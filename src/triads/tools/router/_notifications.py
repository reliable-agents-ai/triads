"""
User-facing notifications for routing decisions.

Formats routing results into clear, informative messages for users.
"""

from typing import Dict


class NotificationBuilder:
    """
    Builds user-facing routing notifications.

    Formats routing results from TriadRouter into clear, contextual
    notifications that help users understand routing decisions.
    """

    def format_routing_notification(self, routing_result: Dict) -> str:
        """
        Format routing result as user-friendly notification.

        Args:
            routing_result: Dictionary from TriadRouter.route() with keys:
                - triad: str | None
                - confidence: float
                - method: "semantic" | "llm" | "manual" | "grace_period" | "cancelled"
                - reasoning: str
                - grace_period_active: bool
                - grace_status: dict (optional, if grace period active)

        Returns:
            Formatted notification string ready for display
        """
        method = routing_result["method"]
        triad = routing_result["triad"]
        confidence = routing_result["confidence"]
        reasoning = routing_result.get("reasoning", "")

        if method == "cancelled":
            return "❌ Routing cancelled. Staying in current triad."

        if method == "grace_period":
            grace_status = routing_result.get("grace_status", {})
            return self._format_grace_period_notification(triad, grace_status)

        if method == "semantic":
            return self._format_semantic_notification(triad, confidence)

        if method == "llm":
            return self._format_llm_notification(
                triad, confidence, reasoning
            )

        if method == "manual":
            return self._format_manual_notification(triad)

        # Fallback for unknown methods
        return f"🔀 Routing to {triad}"

    def _format_grace_period_notification(
        self, triad: str, grace_status: Dict
    ) -> str:
        """
        Format grace period continuation notification.

        Shows concise status of why we're staying in current triad.

        Args:
            triad: Active triad name
            grace_status: Dict with turns_remaining, minutes_remaining, reason

        Returns:
            Formatted notification
        """
        turns_remaining = grace_status.get("turns_remaining", 0)
        minutes_remaining = grace_status.get("minutes_remaining", 0)
        reason = grace_status.get("reason", "unknown")

        if reason == "both":
            status = f"turn {5 - turns_remaining}/5, {minutes_remaining:.0f} min remaining"
        elif reason == "turns":
            status = f"turn {5 - turns_remaining}/5"
        elif reason == "time":
            status = f"{minutes_remaining:.0f} min remaining"
        else:
            status = "active"

        return f"💬 Continuing in {triad} ({status})"

    def _format_semantic_notification(
        self, triad: str, confidence: float
    ) -> str:
        """
        Format semantic routing notification.

        High confidence routes get simple notification.
        Medium confidence routes show score for transparency.

        Args:
            triad: Selected triad name
            confidence: Confidence score (0.0-1.0)

        Returns:
            Formatted notification
        """
        if confidence >= 0.85:
            # High confidence - simple notification
            return f"🔀 Routing to {triad}"
        else:
            # Medium confidence - show score
            return f"🔀 Routing to {triad} (confidence: {confidence:.0%})"

    def _format_llm_notification(
        self, triad: str, confidence: float, reasoning: str
    ) -> str:
        """
        Format LLM disambiguation notification.

        Shows reasoning to help users understand LLM's decision.

        Args:
            triad: Selected triad name
            confidence: LLM confidence score
            reasoning: LLM's reasoning text

        Returns:
            Formatted notification with reasoning snippet
        """
        # Show reasoning for LLM routes (more interesting)
        reason_snippet = (
            reasoning[:60] + "..." if len(reasoning) > 60 else reasoning
        )
        return f"🔀 Routing to {triad}\n   💡 {reason_snippet}"

    def _format_manual_notification(self, triad: str) -> str:
        """
        Format manual selection notification.

        Simple confirmation message for manual selections.

        Args:
            triad: Manually selected triad name

        Returns:
            Formatted notification
        """
        return f"✅ You selected {triad}"

    def format_override_hint(self) -> str:
        """
        Format override command hint.

        Shows users how to manually override routing decisions.

        Returns:
            Formatted hint text
        """
        return "   💡 Override: /switch-triad [name] or type 'c' to cancel"

    def format_grace_period_summary(self, grace_status: Dict) -> str:
        """
        Format detailed grace period summary.

        For status command or verbose output.

        Args:
            grace_status: Dict with active, turns_remaining, minutes_remaining, reason

        Returns:
            Formatted multi-line summary
        """
        if not grace_status.get("active"):
            return "Grace Period: 🔴 Inactive (routing will occur on next prompt)"

        turns_remaining = grace_status["turns_remaining"]
        minutes_remaining = grace_status["minutes_remaining"]
        reason = grace_status["reason"]

        lines = ["Grace Period: 🟢 Active"]

        if reason in ["turns", "both"]:
            lines.append(f"  Turns Remaining: {turns_remaining}/5")

        if reason in ["time", "both"]:
            lines.append(f"  Time Remaining: {minutes_remaining:.1f} minutes")

        return "\n".join(lines)

    def format_routing_stats(self, stats: Dict) -> str:
        """
        Format routing statistics from telemetry.

        Args:
            stats: Statistics dict from TelemetryLogger.get_stats()

        Returns:
            Formatted multi-line statistics summary
        """
        if not stats:
            return "ℹ️  No routing statistics available."

        total = stats.get("route_decisions", 0)
        if total == 0:
            return "ℹ️  No routing decisions recorded yet."

        semantic = stats.get("semantic_routes", 0)
        llm = stats.get("llm_routes", 0)
        manual = stats.get("manual_routes", 0)
        avg_latency = stats.get("avg_latency_ms", 0.0)

        lines = [
            "📊 Router Statistics",
            "=" * 50,
            "",
            f"Total Routes: {total}",
            "",
            "Method Breakdown:",
        ]

        if semantic > 0:
            pct = (semantic / total) * 100
            lines.append(f"  Semantic:    {semantic:3d} ({pct:.1f}%)")

        if llm > 0:
            pct = (llm / total) * 100
            lines.append(f"  LLM:         {llm:3d} ({pct:.1f}%)")

        if manual > 0:
            pct = (manual / total) * 100
            lines.append(f"  Manual:      {manual:3d} ({pct:.1f}%)")

        lines.append("")
        lines.append(f"Average Latency: {avg_latency:.1f}ms")

        return "\n".join(lines)
