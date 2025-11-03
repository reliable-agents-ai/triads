"""Event and EventFilters models for event sourcing system.

This module defines the core data structures for the event sourcing system:
- Event: Represents a single event in the system (RDF triple format)
- EventFilters: Query filters for retrieving events from repository
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4


@dataclass
class Event:
    """Represents a single event in RDF triple format.

    Events capture what happened in the system using RDF subject-predicate-object
    triples. Each event is immutable and timestamped.

    Required Fields:
        subject: RDF subject (what the event is about)
        predicate: RDF predicate (what action/change occurred)
        object_data: RDF object (detailed event data as dictionary)

    Auto-Generated Fields:
        id: Unique event identifier (UUID)
        timestamp: When the event occurred (UTC)

    Optional Context Fields:
        workspace_id: ID of workspace where event occurred
        hook_name: Name of hook that triggered event
        execution_time_ms: Hook execution time in milliseconds
        error: Error message if event represents a failure
        metadata: Additional arbitrary metadata

    Example:
        >>> event = Event(
        ...     subject="agent",
        ...     predicate="completed",
        ...     object_data={"agent": "solution-architect", "confidence": 0.95}
        ... )
        >>> print(event.id)  # Auto-generated UUID
        >>> print(event.timestamp)  # Auto-generated UTC timestamp
    """

    # RDF triple components (required)
    subject: str
    predicate: str
    object_data: Dict[str, Any]

    # Auto-generated fields
    id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # Optional context fields
    workspace_id: Optional[str] = None
    hook_name: Optional[str] = None
    execution_time_ms: Optional[float] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EventFilters:
    """Query filters for retrieving events from repository.

    All filters use AND logic (all specified filters must match).

    Filter Fields:
        workspace_id: Filter by workspace ID
        subject: Filter by event subject
        predicate: Filter by event predicate
        time_from: Filter events >= this timestamp
        time_to: Filter events <= this timestamp
        search: Full-text search in subject, predicate, error (case-insensitive)

    Pagination:
        limit: Maximum number of results (default: 100)
        offset: Skip this many results (default: 0)

    Sorting:
        sort_by: Field to sort by (default: "timestamp")
        sort_order: "asc" or "desc" (default: "desc")

    Example:
        >>> filters = EventFilters(
        ...     workspace_id="workspace-1",
        ...     subject="agent",
        ...     time_from=datetime(2025, 10, 30, 14, 0, 0, tzinfo=timezone.utc),
        ...     limit=50,
        ...     sort_order="asc"
        ... )
    """

    # Filter fields
    workspace_id: Optional[str] = None
    subject: Optional[str] = None
    predicate: Optional[str] = None
    time_from: Optional[datetime] = None
    time_to: Optional[datetime] = None
    search: Optional[str] = None

    # Pagination
    limit: int = 100
    offset: int = 0

    # Sorting
    sort_by: str = "timestamp"
    sort_order: str = "desc"
