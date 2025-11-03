"""Event sourcing system for triads.

This module provides event sourcing capabilities for capturing and querying
system events in RDF triple format.

Core Classes:
    - Event: Immutable event in subject-predicate-object format
    - EventFilters: Query filters for retrieving events
    - AbstractEventRepository: Base class for event storage
    - InMemoryEventRepository: In-memory implementation for testing/development

Example Usage:
    >>> from triads.events import Event, EventFilters, InMemoryEventRepository
    >>> 
    >>> # Create repository
    >>> repo = InMemoryEventRepository()
    >>> 
    >>> # Create and save event
    >>> event = Event(
    ...     subject="agent",
    ...     predicate="completed",
    ...     object_data={"agent": "solution-architect", "confidence": 0.95}
    ... )
    >>> repo.save(event)
    >>> 
    >>> # Query events
    >>> filters = EventFilters(subject="agent", limit=10)
    >>> events = repo.query(filters)
"""

from triads.events.exceptions import (
    EventQueryError,
    EventStorageError,
    InvalidEventError,
)
from triads.events.memory_repository import InMemoryEventRepository
from triads.events.models import Event, EventFilters
from triads.events.repository import AbstractEventRepository

__all__ = [
    "Event",
    "EventFilters",
    "EventStorageError",
    "EventQueryError",
    "InvalidEventError",
    "AbstractEventRepository",
    "InMemoryEventRepository",
]
