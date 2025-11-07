"""Event sourcing system for triads.

This module provides event sourcing capabilities for capturing and querying
system events in RDF triple format.

Core Classes:
    - Event: Immutable event in subject-predicate-object format
    - EventFilters: Query filters for retrieving events
    - AbstractEventRepository: Base class for event storage
    - InMemoryEventRepository: In-memory implementation for testing/development
    - JSONLEventRepository: JSONL file-based implementation for production

MCP Tools:
    - capture_event(): Capture a new event to repository
    - query_events(): Query events with filters

Example Usage:
    >>> from triads.events import capture_event, query_events
    >>>
    >>> # Capture event
    >>> result = capture_event(
    ...     subject="agent",
    ...     predicate="completed",
    ...     object_data={"agent": "solution-architect", "confidence": 0.95}
    ... )
    >>>
    >>> # Query events
    >>> result = query_events(subject="agent", limit=10)
"""

from triads.events.exceptions import (
    EventQueryError,
    EventStorageError,
    InvalidEventError,
)
from triads.events.jsonl_repository import JSONLEventRepository
from triads.events.memory_repository import InMemoryEventRepository
from triads.events.models import Event, EventFilters
from triads.events.repository import AbstractEventRepository
from triads.events.tools import capture_event, query_events

__all__ = [
    "Event",
    "EventFilters",
    "EventStorageError",
    "EventQueryError",
    "InvalidEventError",
    "AbstractEventRepository",
    "InMemoryEventRepository",
    "JSONLEventRepository",
    "capture_event",
    "query_events",
]
