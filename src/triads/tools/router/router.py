"""
Main router orchestrator that coordinates all routing components.

Integrates semantic routing, LLM disambiguation, grace period checks,
and manual selection to provide seamless triad routing.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

from .config import RouterConfig
from ._embedder import RouterEmbedder
from ._grace_period import GracePeriodChecker
from ._llm_disambiguator import LLMDisambiguator
from ._manual_selector import ManualSelector
from ._semantic_router import RoutingDecision, SemanticRouter
from ._state_manager import _RouterStateManager as RouterStateManager
from ._telemetry import TelemetryLogger
from ._timestamp_utils import utc_now_iso
from .domain import RouterState


class TriadRouter:
    """
    Main router orchestrator that coordinates all routing components.

    This is the primary entry point for routing user prompts to triads.
    It orchestrates:
    - Semantic routing (fast, embedding-based)
    - Grace period checks (prevent disruptive re-routing)
    - LLM disambiguation (when semantic routing is uncertain)
    - Manual selection (when LLM fails or is unavailable)
    - Telemetry logging (performance tracking)

    Usage:
        router = TriadRouter()
        result = router.route("Let's validate this idea")
        # result = {
        #     "triad": "idea-validation",
        #     "confidence": 0.92,
        #     "method": "semantic",
        #     "reasoning": "High confidence semantic match (92%)",
        #     "grace_period_active": False,
        #     "latency_ms": 8.5
        # }
    """

    def __init__(
        self,
        config_path: Optional[Path] = None,
        state_path: Optional[Path] = None,
    ):
        """
        Initialize router orchestrator.

        Args:
            config_path: Path to config.json (default: ~/.claude/router/config.json)
            state_path: Path to state file (default: ~/.claude/router_state.json)
        """
        # Load configuration
        self.config = RouterConfig(config_path)

        # Initialize state management
        self.state_manager = RouterStateManager(state_path)

        # Initialize telemetry
        self.telemetry = TelemetryLogger(enabled=self.config.telemetry_enabled)

        # Initialize embedder and semantic router
        self.embedder = RouterEmbedder()
        self.semantic_router = SemanticRouter(self.embedder)

        # Initialize grace period checker
        self.grace_period = GracePeriodChecker(
            self.state_manager,
            grace_turns=self.config.grace_period_turns,
            grace_minutes=self.config.grace_period_minutes,
        )

        # Initialize LLM disambiguator (may not have API key)
        try:
            self.llm_disambiguator = LLMDisambiguator(
                timeout_ms=self.config.llm_timeout_ms
            )
        except ValueError:
            # No API key set, LLM unavailable
            self.llm_disambiguator = None

        # Initialize manual selector
        self.manual_selector = ManualSelector()

    def route(
        self, prompt: str, context: Optional[List[str]] = None
    ) -> Dict:
        """
        Route a user prompt to the appropriate triad.

        This is the main entry point for routing. It:
        1. Checks grace period (stay in current triad if active)
        2. Performs semantic routing (fast, embedding-based)
        3. Falls back to LLM if semantic routing is uncertain
        4. Falls back to manual selection if LLM fails

        Args:
            prompt: User's input prompt
            context: Recent conversation messages (optional, for LLM context)

        Returns:
            Dictionary with:
            - triad: str | None - Selected triad (None if user cancelled)
            - confidence: float - Confidence score (0.0-1.0)
            - method: str - "semantic" | "llm" | "manual" | "grace_period"
            - reasoning: str - Human-readable explanation
            - grace_period_active: bool - Whether grace period is active
            - latency_ms: float - Total routing latency
            - grace_status: dict - Grace period status (if active)
        """
        start_time = time.time()

        # Load current state
        state = self.state_manager.load()

        # Check for explicit bypass (e.g., /switch-triad command)
        should_bypass, bypass_reason = self.grace_period.should_bypass_grace_period(
            prompt, state
        )

        # Check grace period (unless explicitly bypassed)
        if not should_bypass and self.grace_period.is_within_grace_period(state):
            # Stay in current triad
            result = self._handle_grace_period(state, prompt, start_time)
            self._update_state_for_grace_period(state)
            self.state_manager.save(state)
            return result

        # Perform routing
        routing_result = self._perform_routing(prompt, context, start_time)

        # Update state with new triad
        if routing_result["triad"]:
            self.grace_period.reset_grace_period(state, routing_result["triad"])
            self.state_manager.save(state)

        return routing_result

    def _handle_grace_period(
        self, state: RouterState, prompt: str, start_time: float
    ) -> Dict:
        """
        Handle case where grace period is active.

        Stay in current triad and log grace period event.

        Args:
            state: Current router state
            prompt: User prompt (for telemetry)
            start_time: Routing start time

        Returns:
            Routing result dictionary
        """
        latency_ms = (time.time() - start_time) * 1000

        grace_status = self.grace_period.get_grace_period_status(state)

        self.telemetry.log_event(
            "grace_period_active",
            {
                "triad": state.current_triad,
                "turns_remaining": grace_status["turns_remaining"],
                "minutes_remaining": grace_status["minutes_remaining"],
                "reason": grace_status["reason"],
                "latency_ms": latency_ms,
            },
        )

        return {
            "triad": state.current_triad,
            "confidence": 1.0,  # High confidence - staying in current triad
            "method": "grace_period",
            "reasoning": f"Continuing in {state.current_triad} (grace period active)",
            "grace_period_active": True,
            "grace_status": grace_status,
            "latency_ms": latency_ms,
        }

    def _perform_routing(
        self, prompt: str, context: Optional[List[str]], start_time: float
    ) -> Dict:
        """
        Perform actual routing logic.

        Steps:
        1. Semantic routing (fast)
        2. LLM disambiguation (if semantic uncertain)
        3. Manual selection (if LLM fails or unavailable)

        Args:
            prompt: User prompt
            context: Recent conversation messages
            start_time: Routing start time

        Returns:
            Routing result dictionary
        """
        # Step 1: Semantic routing
        semantic_scores = self.semantic_router.route(prompt)
        decision, candidates = self.semantic_router.threshold_check(
            semantic_scores,
            confidence_threshold=self.config.confidence_threshold,
            ambiguity_threshold=self.config.semantic_similarity_threshold,
        )

        # Step 2: High confidence semantic route
        if decision == RoutingDecision.ROUTE_IMMEDIATELY:
            triad, confidence = candidates[0]
            latency_ms = (time.time() - start_time) * 1000

            self.telemetry.log_route_decision(
                prompt_snippet=prompt,
                triad=triad,
                confidence=confidence,
                method="semantic",
                latency_ms=latency_ms,
            )

            return {
                "triad": triad,
                "confidence": confidence,
                "method": "semantic",
                "reasoning": f"High confidence semantic match ({confidence:.0%})",
                "grace_period_active": False,
                "latency_ms": latency_ms,
            }

        # Step 3: LLM disambiguation (if available)
        if (
            self.llm_disambiguator
            and decision == RoutingDecision.LLM_FALLBACK_REQUIRED
        ):
            try:
                triad, confidence, reasoning = (
                    self.llm_disambiguator.disambiguate_with_retry(
                        prompt, candidates, context
                    )
                )
                latency_ms = (time.time() - start_time) * 1000

                self.telemetry.log_route_decision(
                    prompt_snippet=prompt,
                    triad=triad,
                    confidence=confidence,
                    method="llm",
                    latency_ms=latency_ms,
                )

                return {
                    "triad": triad,
                    "confidence": confidence,
                    "method": "llm",
                    "reasoning": reasoning,
                    "grace_period_active": False,
                    "latency_ms": latency_ms,
                }

            except Exception as e:
                # LLM failed, fall back to manual
                print(f"⚠️  LLM disambiguation failed: {e}", file=sys.stderr)
                self.telemetry.log_error(
                    "llm_disambiguation_failure",
                    str(e),
                    {"prompt_snippet": prompt[:50]},
                )

        # Step 4: Manual selection (fallback)
        reason = (
            "llm_failure"
            if self.llm_disambiguator
            else "llm_unavailable"
        )
        triad, selection_reason = self.manual_selector.select_triad(
            prompt, candidates, reason=reason
        )
        latency_ms = (time.time() - start_time) * 1000

        if triad:  # User selected a triad
            self.telemetry.log_route_decision(
                prompt_snippet=prompt,
                triad=triad,
                confidence=1.0,  # Manual selection = 100% confidence
                method="manual",
                latency_ms=latency_ms,
            )

            return {
                "triad": triad,
                "confidence": 1.0,
                "method": "manual",
                "reasoning": f"Manual selection (reason: {selection_reason})",
                "grace_period_active": False,
                "latency_ms": latency_ms,
            }
        else:  # User cancelled
            return {
                "triad": None,
                "confidence": 0.0,
                "method": "cancelled",
                "reasoning": "User cancelled routing",
                "grace_period_active": False,
                "latency_ms": latency_ms,
            }

    def _update_state_for_grace_period(self, state: RouterState) -> None:
        """
        Increment turn count and update activity timestamp.

        Called when grace period is active and we stay in current triad.

        Args:
            state: Router state to update
        """
        state.turn_count += 1
        state.last_activity = utc_now_iso()

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"TriadRouter("
            f"config={self.config}, "
            f"llm_available={self.llm_disambiguator is not None})"
        )
