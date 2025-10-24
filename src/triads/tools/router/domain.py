"""Domain models for router tools.

Defines core data structures for routing operations.
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Optional

import logging

logger = logging.getLogger(__name__)



@dataclass
class RoutingDecision:
    """Routing decision result.

    Represents the output of routing a user prompt to a triad.

    Attributes:
        triad: Selected triad name
        confidence: Confidence score (0.0-1.0)
        method: Routing method used ("semantic", "llm", "manual", "grace_period")
        reasoning: Optional human-readable explanation of routing decision
    """

    triad: str
    confidence: float
    method: str
    reasoning: Optional[str] = None


@dataclass
class RouterState:
    """Router state information.

    Represents the current state of the router including active triad,
    conversation tracking, and grace period information.

    Attributes:
        current_triad: Currently active triad name (None if no active triad)
        session_id: Unique session identifier
        turn_count: Number of turns since triad activation
        conversation_start: ISO 8601 timestamp when conversation started
        last_activity: ISO 8601 timestamp of last routing activity
        training_mode: Whether training mode is active
        training_confirmations: Count of training mode confirmations
    """

    current_triad: Optional[str]
    session_id: str
    turn_count: int = 0
    conversation_start: Optional[str] = None
    last_activity: Optional[str] = None
    training_mode: bool = False
    training_confirmations: int = 0

    def is_within_grace_period(
        self, grace_turns: int = 5, grace_minutes: int = 8
    ) -> bool:
        """
        Check if current state is within grace period.

        Grace period is satisfied if EITHER:
        - turn_count < grace_turns OR
        - time since last_activity < grace_minutes

        Args:
            grace_turns: Maximum turns before grace period expires (default: 5)
            grace_minutes: Maximum minutes before grace period expires (default: 8)

        Returns:
            True if within grace period, False otherwise
        """
        from ._timestamp_utils import utc_now_aware

        if not self.current_triad or not self.conversation_start:
            return False

        # Check turn count
        if self.turn_count < grace_turns:
            return True

        # Check time elapsed since last activity
        if self.last_activity:
            try:
                last_active = datetime.fromisoformat(
                    self.last_activity.replace("Z", "+00:00")
                )
                now = utc_now_aware()
                elapsed_minutes = (now - last_active).total_seconds() / 60

                if elapsed_minutes < grace_minutes:
                    return True
            except (ValueError, AttributeError):
                # Invalid timestamp - default to expired
                pass

        return False

    def update_activity(self) -> None:
        """Update activity timestamp and increment turn count."""
        from ._timestamp_utils import utc_now_iso

        self.last_activity = utc_now_iso()
        self.turn_count += 1

    def to_dict(self) -> dict:
        """
        Convert state to JSON-serializable dictionary.

        Returns:
            Dictionary representation of RouterState
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "RouterState":
        """
        Create RouterState from dictionary.

        Handles missing fields gracefully by using defaults from dataclass.

        Args:
            data: Dictionary with state fields

        Returns:
            RouterState instance
        """
        # Filter to only known fields to handle schema evolution
        valid_fields = {k: v for k, v in data.items() if k in cls.__annotations__}
        return cls(**valid_fields)
