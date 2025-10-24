"""Repository layer for router tools.

Abstracts access to routing and state management functionality.
"""

import logging
import uuid
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from triads.tools.router.domain import RoutingDecision, RouterState

logger = logging.getLogger(__name__)


class RouterRepositoryError(Exception):
    """Base exception for router repository errors."""
    pass


class AbstractRouterRepository(ABC):
    """Abstract interface for router repositories.

    Defines the contract for accessing routing and state functionality.
    """

    @abstractmethod
    def route_prompt(self, prompt: str) -> RoutingDecision:
        """Route a user prompt to appropriate triad.

        Args:
            prompt: User's input prompt

        Returns:
            RoutingDecision with triad, confidence, method

        Raises:
            RouterRepositoryError: If routing fails
        """
        pass

    @abstractmethod
    def load_state(self) -> RouterState:
        """Load current router state.

        Returns:
            RouterState with current triad and session information
        """
        pass

    @abstractmethod
    def save_state(self, state: RouterState) -> None:
        """Save router state.

        Args:
            state: RouterState to persist
        """
        pass


class InMemoryRouterRepository(AbstractRouterRepository):
    """In-memory router repository for testing.

    Provides simplified routing and state management without
    external dependencies. Used for unit testing.
    """

    def __init__(self):
        """Initialize in-memory repository."""
        self._state: Optional[RouterState] = None
        self._triads = [
            "idea-validation",
            "design",
            "implementation",
            "garden-tending",
            "deployment"
        ]

    def route_prompt(self, prompt: str) -> RoutingDecision:
        """Route prompt using simple keyword matching.

        Args:
            prompt: User's input prompt

        Returns:
            RoutingDecision based on keyword matching

        Raises:
            RouterRepositoryError: If prompt is empty
        """
        if not prompt or not prompt.strip():
            raise RouterRepositoryError("Prompt cannot be empty")

        prompt_lower = prompt.lower()

        # Simple keyword-based routing for testing
        if any(kw in prompt_lower for kw in ["idea", "validate", "research"]):
            return RoutingDecision(
                triad="idea-validation",
                confidence=0.90,
                method="semantic"
            )
        elif any(kw in prompt_lower for kw in ["design", "architect", "should we"]):
            return RoutingDecision(
                triad="design",
                confidence=0.92,
                method="semantic"
            )
        elif any(kw in prompt_lower for kw in ["implement", "build", "create", "write"]):
            return RoutingDecision(
                triad="implementation",
                confidence=0.88,
                method="semantic"
            )
        elif any(kw in prompt_lower for kw in ["refactor", "clean", "improve", "tending"]):
            return RoutingDecision(
                triad="garden-tending",
                confidence=0.85,
                method="semantic"
            )
        elif any(kw in prompt_lower for kw in ["deploy", "release", "publish"]):
            return RoutingDecision(
                triad="deployment",
                confidence=0.87,
                method="semantic"
            )
        else:
            # Default to implementation with lower confidence
            return RoutingDecision(
                triad="implementation",
                confidence=0.70,
                method="semantic"
            )

    def load_state(self) -> RouterState:
        """Load router state from memory.

        Returns:
            RouterState (default state if none exists)
        """
        if self._state is None:
            # Create default state
            self._state = RouterState(
                current_triad=None,
                session_id=str(uuid.uuid4())
            )
        return self._state

    def save_state(self, state: RouterState) -> None:
        """Save router state to memory.

        Args:
            state: RouterState to save
        """
        self._state = state


class FileSystemRouterRepository(AbstractRouterRepository):
    """File system-based router repository.

    PHASE 2 REFACTOR: Contains actual routing implementation (NO WRAPPER).

    Implements routing logic with:
    - Grace period checking (prevent mid-conversation re-routing)
    - Semantic routing (embedding-based, fast)
    - LLM disambiguation (when semantic is uncertain)
    - Manual selection fallback (ultimate failsafe)

    Architecture:
    - Uses actual migrated components from tools.router._*
    - NO imports from triads.router (eliminated wrapper pattern)
    """

    def __init__(
        self,
        config_path: Optional[Path] = None,
        state_path: Optional[Path] = None
    ):
        """Initialize file system repository with actual components.

        Args:
            config_path: Path to router config.json (default: ~/.claude/router/config.json)
            state_path: Path to router state file (default: ~/.claude/router_state.json)
        """
        # Import migrated components (NOT from triads.router)
        from .config import RouterConfig
        from ._state_manager import _RouterStateManager
        from ._embedder import RouterEmbedder
        from ._semantic_router import SemanticRouter, RoutingDecision as SemanticDecision
        from ._grace_period import GracePeriodChecker
        from ._telemetry import TelemetryLogger

        # Load configuration
        self.config = RouterConfig(config_path)

        # Initialize state management
        self.state_manager = _RouterStateManager(state_path)

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
            from ._llm_disambiguator import LLMDisambiguator
            self.llm_disambiguator = LLMDisambiguator(
                timeout_ms=self.config.llm_timeout_ms
            )
        except ValueError:
            # No API key set, LLM unavailable
            self.llm_disambiguator = None

        # Initialize manual selector
        from ._manual_selector import ManualSelector
        self.manual_selector = ManualSelector()

        # Store SemanticDecision enum for threshold checking
        self._SemanticDecision = SemanticDecision

    def route_prompt(self, prompt: str) -> RoutingDecision:
        """Route prompt using actual implementation (NO DELEGATION).

        Implements full routing cascade:
        1. Grace period check (stay in current triad if active)
        2. Semantic routing (fast, embedding-based)
        3. LLM disambiguation (if semantic uncertain)
        4. Manual selection (if LLM fails/unavailable)

        Args:
            prompt: User's input prompt

        Returns:
            RoutingDecision with triad, confidence, method

        Raises:
            RouterRepositoryError: If routing fails or prompt is empty
        """
        if not prompt or not prompt.strip():
            raise RouterRepositoryError("Prompt cannot be empty")

        try:
            import time
            start_time = time.time()

            # Load current state
            state = self.state_manager.load()

            # Check for bypass conditions
            should_bypass, bypass_reason = self.grace_period.should_bypass_grace_period(
                prompt, state
            )

            # Check grace period (unless explicitly bypassed)
            if not should_bypass and self.grace_period.is_within_grace_period(state):
                # Stay in current triad during grace period
                latency_ms = (time.time() - start_time) * 1000

                self.telemetry.log_event(
                    "grace_period_active",
                    {
                        "triad": state.current_triad,
                        "latency_ms": latency_ms,
                    },
                )

                return RoutingDecision(
                    triad=state.current_triad,
                    confidence=1.0,
                    method="grace_period",
                    reasoning=f"Continuing in {state.current_triad} (grace period active)"
                )

            # Perform routing (semantic → LLM → manual cascade)
            result = self._perform_routing(prompt, start_time)

            # Update state with new triad
            if result.triad:
                self.grace_period.reset_grace_period(state, result.triad)
                self.state_manager.save(state)

            return result

        except Exception as e:
            logger.error(f"Routing failed: {e}")
            raise RouterRepositoryError(f"Routing failed: {e}") from e

    def _perform_routing(self, prompt: str, start_time: float) -> RoutingDecision:
        """Perform actual routing logic (semantic → LLM → manual).

        Args:
            prompt: User prompt
            start_time: Routing start time (for latency tracking)

        Returns:
            RoutingDecision
        """
        import time

        # Step 1: Semantic routing
        semantic_scores = self.semantic_router.route(prompt)
        decision, candidates = self.semantic_router.threshold_check(
            semantic_scores,
            confidence_threshold=self.config.confidence_threshold,
            ambiguity_threshold=self.config.semantic_similarity_threshold,
        )

        # Step 2: High confidence semantic route
        if decision == self._SemanticDecision.ROUTE_IMMEDIATELY:
            triad, confidence = candidates[0]
            latency_ms = (time.time() - start_time) * 1000

            self.telemetry.log_route_decision(
                prompt_snippet=prompt[:50],
                triad=triad,
                confidence=confidence,
                method="semantic",
                latency_ms=latency_ms,
            )

            return RoutingDecision(
                triad=triad,
                confidence=confidence,
                method="semantic",
                reasoning=f"High confidence semantic match ({confidence:.0%})"
            )

        # Step 3: LLM disambiguation (if available)
        if (
            self.llm_disambiguator
            and decision == self._SemanticDecision.LLM_FALLBACK_REQUIRED
        ):
            try:
                triad, confidence, reasoning = (
                    self.llm_disambiguator.disambiguate_with_retry(
                        prompt=prompt,
                        candidates=candidates,
                        context=None,
                    )
                )

                latency_ms = (time.time() - start_time) * 1000

                self.telemetry.log_route_decision(
                    prompt_snippet=prompt[:50],
                    triad=triad,
                    confidence=confidence,
                    method="llm",
                    latency_ms=latency_ms,
                )

                return RoutingDecision(
                    triad=triad,
                    confidence=confidence,
                    method="llm",
                    reasoning=reasoning
                )

            except Exception as llm_error:
                logger.warning(f"LLM disambiguation failed: {llm_error}, falling back to manual")

        # Step 4: Manual selection fallback
        selected_triad = self.manual_selector.select(prompt, candidates[:3])
        latency_ms = (time.time() - start_time) * 1000

        self.telemetry.log_route_decision(
            prompt_snippet=prompt[:50],
            triad=selected_triad,
            confidence=1.0,  # User explicitly selected
            method="manual",
            latency_ms=latency_ms,
        )

        return RoutingDecision(
            triad=selected_triad,
            confidence=1.0,
            method="manual",
            reasoning="User selected manually"
        )

    def load_state(self) -> RouterState:
        """Load router state from file system.

        Returns:
            RouterState with current triad and session information
        """
        # Load state using _RouterStateManager (already returns domain model)
        return self.state_manager.load()

    def save_state(self, state: RouterState) -> None:
        """Save router state to file system.

        Args:
            state: RouterState to persist
        """
        # Save using _RouterStateManager (accepts domain model)
        self.state_manager.save(state)
