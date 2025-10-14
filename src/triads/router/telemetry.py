"""
Telemetry logging for router performance and decisions.

Logs routing decisions, performance metrics, and errors to JSON Lines format.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

from .timestamp_utils import utc_now_iso


class TelemetryLogger:
    """
    Structured telemetry logger for router events.

    Features:
    - JSON Lines format for streaming analysis
    - Automatic log rotation at size limit
    - Privacy-safe prompt snippets (max 50 chars)
    - Configurable enable/disable
    """

    def __init__(
        self,
        log_path: Optional[Path] = None,
        enabled: bool = True,
        max_size_mb: int = 10,
    ):
        """
        Initialize telemetry logger.

        Args:
            log_path: Path to log file. Defaults to ~/.claude/router/logs/routing_telemetry.jsonl
            enabled: Whether telemetry is enabled
            max_size_mb: Maximum log file size before rotation (default: 10MB)
        """
        if log_path is None:
            log_path = (
                Path.home()
                / ".claude"
                / "router"
                / "logs"
                / "routing_telemetry.jsonl"
            )

        self.log_path = Path(log_path)
        self.enabled = enabled
        self.max_size_mb = max_size_mb

        # Create log directory if needed
        if self.enabled:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Log a structured event.

        Args:
            event_type: Type of event (e.g., "route_decision", "error")
            data: Event data dictionary
        """
        if not self.enabled:
            return

        event = {
            "timestamp": utc_now_iso(),
            "event_type": event_type,
            **data,
        }

        # Append to JSON Lines file
        with open(self.log_path, "a") as f:
            f.write(json.dumps(event) + "\n")

        # Check for rotation
        self._check_rotation()

    def log_route_decision(
        self,
        prompt_snippet: str,
        triad: str,
        confidence: float,
        method: str,
        latency_ms: float,
        overridden: bool = False,
    ) -> None:
        """
        Log a routing decision.

        Args:
            prompt_snippet: User prompt (will be truncated to 50 chars for privacy)
            triad: Target triad name
            confidence: Confidence score (0.0-1.0)
            method: Routing method ("semantic", "llm", "manual")
            latency_ms: Routing latency in milliseconds
            overridden: Whether user overrode the suggestion
        """
        self.log_event(
            "route_decision",
            {
                "prompt_snippet": self._safe_snippet(prompt_snippet),
                "triad": triad,
                "confidence": confidence,
                "method": method,
                "latency_ms": latency_ms,
                "overridden": overridden,
            },
        )

    def log_semantic_routing(
        self,
        prompt_snippet: str,
        top_scores: list,
        is_ambiguous: bool,
        latency_ms: float,
    ) -> None:
        """
        Log semantic routing attempt.

        Args:
            prompt_snippet: User prompt (truncated for privacy)
            top_scores: List of (triad, score) tuples
            is_ambiguous: Whether routing was ambiguous
            latency_ms: Semantic routing latency
        """
        self.log_event(
            "semantic_routing",
            {
                "prompt_snippet": self._safe_snippet(prompt_snippet),
                "top_scores": top_scores[:3],  # Top 3 only
                "is_ambiguous": is_ambiguous,
                "latency_ms": latency_ms,
            },
        )

    def log_llm_disambiguation(
        self,
        prompt_snippet: str,
        candidates: list,
        selected_triad: str,
        confidence: float,
        latency_ms: float,
    ) -> None:
        """
        Log LLM disambiguation.

        Args:
            prompt_snippet: User prompt (truncated for privacy)
            candidates: Candidate triads for disambiguation
            selected_triad: LLM's selected triad
            confidence: LLM confidence score
            latency_ms: LLM disambiguation latency
        """
        self.log_event(
            "llm_disambiguation",
            {
                "prompt_snippet": self._safe_snippet(prompt_snippet),
                "candidates": candidates,
                "selected_triad": selected_triad,
                "confidence": confidence,
                "latency_ms": latency_ms,
            },
        )

    def log_grace_period_check(
        self,
        active_triad: str,
        turn_count: int,
        elapsed_minutes: float,
        within_grace: bool,
    ) -> None:
        """
        Log grace period check.

        Args:
            active_triad: Currently active triad
            turn_count: Number of turns since activation
            elapsed_minutes: Minutes since activation
            within_grace: Whether still within grace period
        """
        self.log_event(
            "grace_period_check",
            {
                "active_triad": active_triad,
                "turn_count": turn_count,
                "elapsed_minutes": elapsed_minutes,
                "within_grace": within_grace,
            },
        )

    def log_error(
        self,
        error_type: str,
        error_message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log an error.

        Args:
            error_type: Type of error (e.g., "embedding_failure", "state_corruption")
            error_message: Error description
            context: Additional context dictionary
        """
        data = {
            "error_type": error_type,
            "error_message": error_message,
        }
        if context:
            data["context"] = context

        self.log_event("error", data)

    def _safe_snippet(self, text: str, max_length: int = 50) -> str:
        """
        Create privacy-safe snippet of text.

        Args:
            text: Full text
            max_length: Maximum snippet length (default: 50)

        Returns:
            Truncated text with ellipsis if needed
        """
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."

    def _check_rotation(self) -> None:
        """Check if log rotation is needed and perform it."""
        if not self.log_path.exists():
            return

        # Check size
        size_mb = self.log_path.stat().st_size / (1024 * 1024)
        if size_mb <= self.max_size_mb:
            return

        # Rotate: rename current to .1, keep last 2 rotations
        rotated_1 = self.log_path.with_suffix(".jsonl.1")
        rotated_2 = self.log_path.with_suffix(".jsonl.2")

        # Shift existing rotations
        if rotated_1.exists():
            if rotated_2.exists():
                rotated_2.unlink()
            rotated_1.rename(rotated_2)

        # Rotate current log
        self.log_path.rename(rotated_1)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics from telemetry logs.

        Returns:
            Dictionary with routing statistics
        """
        if not self.enabled or not self.log_path.exists():
            return {}

        stats = {
            "total_events": 0,
            "route_decisions": 0,
            "semantic_routes": 0,
            "llm_routes": 0,
            "manual_routes": 0,
            "avg_latency_ms": 0.0,
            "errors": 0,
        }

        latencies = []

        with open(self.log_path, "r") as f:
            for line in f:
                try:
                    event = json.loads(line)
                    stats["total_events"] += 1

                    if event["event_type"] == "route_decision":
                        stats["route_decisions"] += 1
                        method = event.get("method", "")
                        if method == "semantic":
                            stats["semantic_routes"] += 1
                        elif method == "llm":
                            stats["llm_routes"] += 1
                        elif method == "manual":
                            stats["manual_routes"] += 1

                        latency = event.get("latency_ms")
                        if latency is not None:
                            latencies.append(latency)

                    elif event["event_type"] == "error":
                        stats["errors"] += 1

                except json.JSONDecodeError:
                    continue

        if latencies:
            stats["avg_latency_ms"] = sum(latencies) / len(latencies)

        return stats
