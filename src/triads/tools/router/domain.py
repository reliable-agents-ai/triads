"""Domain models for router tools.

Defines core data structures for routing operations.
"""

from dataclasses import dataclass, field
from typing import Optional


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
    """

    current_triad: Optional[str]
    session_id: str
    turn_count: int = 0
    conversation_start: Optional[str] = None
    last_activity: Optional[str] = None
