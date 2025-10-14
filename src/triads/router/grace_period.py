"""
Grace period enforcement to prevent re-routing mid-conversation.

Tracks turn count and time since triad activation to prevent disruptive
re-routing during active work sessions.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

from .state_manager import RouterState, RouterStateManager
from .timestamp_utils import utc_now_aware, utc_now_iso


class GracePeriodChecker:
    """Checks if routing should be skipped due to active grace period."""

    def __init__(
        self,
        state_manager: RouterStateManager,
        grace_turns: int = 5,
        grace_minutes: int = 8,
    ):
        """
        Initialize grace period checker.

        Args:
            state_manager: RouterStateManager instance
            grace_turns: Number of turns before grace period expires (default: 5)
            grace_minutes: Minutes before grace period expires (default: 8)
        """
        self.state_manager = state_manager
        self.grace_turns = grace_turns
        self.grace_minutes = grace_minutes

    def is_within_grace_period(self, state: RouterState) -> bool:
        """
        Check if grace period is active.

        Grace period is active if:
        - (turn_count < grace_turns) OR (time_since_last_activity < grace_minutes)

        Returns True if should stay in current triad (no re-routing).

        Args:
            state: Current router state

        Returns:
            True if within grace period, False otherwise
        """
        # No active triad = no grace period
        if not state.active_triad:
            return False

        # Check turn-based grace period (strictly less than)
        if state.turn_count < self.grace_turns:
            return True

        # Check time-based grace period
        if state.last_activity:
            try:
                last_activity_dt = datetime.fromisoformat(
                    state.last_activity.replace("Z", "+00:00")
                )
                # Use timezone-aware datetime for comparison
                now = utc_now_aware()
                time_since = now - last_activity_dt
                if time_since < timedelta(minutes=self.grace_minutes):
                    return True
            except (ValueError, AttributeError):
                # Invalid timestamp - treat as expired
                return False

        return False

    def get_grace_period_status(self, state: RouterState) -> dict:
        """
        Get detailed grace period status for notifications.

        Args:
            state: Current router state

        Returns:
            Dictionary with:
            - active: bool - Whether grace period is active
            - turns_remaining: int - Turns until expiration
            - minutes_remaining: float - Minutes until expiration
            - reason: str - Which threshold is active ("turns", "time", "both", "none")
        """
        if not state.active_triad:
            return {"active": False, "reason": "none"}

        turns_remaining = max(0, self.grace_turns - state.turn_count)

        minutes_remaining = 0.0
        if state.last_activity:
            try:
                last_activity_dt = datetime.fromisoformat(
                    state.last_activity.replace("Z", "+00:00")
                )
                now = utc_now_aware()
                time_since = now - last_activity_dt
                minutes_remaining = max(
                    0, self.grace_minutes - time_since.total_seconds() / 60
                )
            except (ValueError, AttributeError):
                minutes_remaining = 0.0

        # Determine which threshold is active
        turn_active = turns_remaining > 0
        time_active = minutes_remaining > 0

        if turn_active and time_active:
            reason = "both"
        elif turn_active:
            reason = "turns"
        elif time_active:
            reason = "time"
        else:
            reason = "none"

        return {
            "active": turn_active or time_active,
            "turns_remaining": turns_remaining,
            "minutes_remaining": minutes_remaining,
            "reason": reason,
        }

    def should_bypass_grace_period(
        self, prompt: str, state: RouterState
    ) -> Tuple[bool, str]:
        """
        Check if prompt explicitly requests triad switch, bypassing grace period.

        Detects:
        - Explicit switch commands (/switch-triad)
        - Strong transition phrases ("let's switch to", "let's move to")
        - Multi-intent detection ("do X and then Y")

        Args:
            prompt: User's input prompt
            state: Current router state

        Returns:
            Tuple of (should_bypass, reason)
            - should_bypass: True if should bypass grace period
            - reason: Why bypass was triggered
        """
        prompt_lower = prompt.lower().strip()

        # Explicit switch commands
        if prompt_lower.startswith("/switch-triad"):
            return (True, "explicit_switch_command")

        # Strong transition phrases
        strong_transitions = [
            "let's switch to",
            "let's move to",
            "now let's",
            "can we switch to",
            "i want to switch to",
        ]

        for phrase in strong_transitions:
            if phrase in prompt_lower:
                return (True, "explicit_transition_phrase")

        # Multi-intent detection (simplified - LLM can do more sophisticated detection)
        if " and then " in prompt_lower or " then " in prompt_lower:
            return (True, "multi_intent_detected")

        return (False, "normal_prompt")

    def reset_grace_period(
        self, state: RouterState, new_triad: str
    ) -> RouterState:
        """
        Reset grace period counters when switching triads.

        This is called after routing to a new triad.

        Args:
            state: Current router state
            new_triad: Name of new triad being activated

        Returns:
            Updated router state with reset counters
        """
        # Set timestamp once to ensure consistency
        now_timestamp = utc_now_iso()

        state.active_triad = new_triad
        state.turn_count = 1  # Reset to 1 (this prompt is turn 1)
        state.last_activity = now_timestamp
        state.conversation_start = now_timestamp

        return state
