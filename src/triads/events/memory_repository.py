"""In-memory implementation of event repository."""

from typing import List, Optional

from triads.events.exceptions import InvalidEventError
from triads.events.models import Event, EventFilters
from triads.events.repository import AbstractEventRepository


class InMemoryEventRepository(AbstractEventRepository):
    """In-memory implementation of event repository.
    
    Stores events in a Python list. Suitable for testing and development.
    NOT suitable for production (data lost on restart).
    
    Thread-safety: Not thread-safe (use locks if needed in multi-threaded environment)
    """

    def __init__(self):
        """Initialize empty event storage."""
        self._events: List[Event] = []

    def save(self, event: Event) -> str:
        """Save an event to memory.
        
        Args:
            event: Event to save
            
        Returns:
            str: Event ID of saved event
            
        Raises:
            InvalidEventError: If event is None or has empty predicate
        """
        # Validation
        if event is None:
            raise InvalidEventError("Event cannot be None")
        
        if not event.predicate or event.predicate.strip() == "":
            raise InvalidEventError("Event predicate cannot be empty")
        
        # Store event
        self._events.append(event)
        return event.id

    def get_by_id(self, event_id: str) -> Optional[Event]:
        """Retrieve event by ID.
        
        Args:
            event_id: Unique event identifier
            
        Returns:
            Event if found, None otherwise
        """
        if not event_id:
            return None
        
        for event in self._events:
            if event.id == event_id:
                return event
        
        return None

    def _apply_filters(self, events: List[Event], filters: EventFilters) -> List[Event]:
        """Apply all query filters to a list of events.

        Filters are applied in sequence:
        1. workspace_id filter
        2. subject filter
        3. predicate filter
        4. time_from filter (inclusive)
        5. time_to filter (inclusive)
        6. search filter (case-insensitive full-text search)

        Args:
            events: List of events to filter
            filters: Query filters to apply

        Returns:
            Filtered list of events (unsorted, unpaginated)
        """
        results = list(events)

        # Filter by workspace_id
        if filters.workspace_id is not None:
            results = [e for e in results if e.workspace_id == filters.workspace_id]

        # Filter by subject
        if filters.subject is not None:
            results = [e for e in results if e.subject == filters.subject]

        # Filter by predicate
        if filters.predicate is not None:
            results = [e for e in results if e.predicate == filters.predicate]

        # Filter by time range (from)
        if filters.time_from is not None:
            results = [e for e in results if e.timestamp >= filters.time_from]

        # Filter by time range (to)
        if filters.time_to is not None:
            results = [e for e in results if e.timestamp <= filters.time_to]

        # Full-text search filter
        if filters.search is not None:
            search_lower = filters.search.lower()
            filtered = []
            for e in results:
                # Search in subject, predicate, error, object_data
                if (search_lower in e.subject.lower() or
                    search_lower in e.predicate.lower() or
                    (e.error and search_lower in e.error.lower()) or
                    search_lower in str(e.object_data).lower()):
                    filtered.append(e)
            results = filtered

        return results

    def _apply_sorting(self, events: List[Event], filters: EventFilters) -> List[Event]:
        """Apply sorting to a list of events.

        Sorts by the field specified in filters.sort_by with the order
        specified in filters.sort_order. Falls back to timestamp sorting
        if the specified field doesn't exist.

        Args:
            events: List of events to sort
            filters: Query filters containing sort_by and sort_order

        Returns:
            Sorted list of events
        """
        reverse = (filters.sort_order == "desc")
        try:
            return sorted(events, key=lambda e: getattr(e, filters.sort_by), reverse=reverse)
        except AttributeError:
            # Invalid sort field - fall back to timestamp
            return sorted(events, key=lambda e: e.timestamp, reverse=reverse)

    def _apply_pagination(self, events: List[Event], filters: EventFilters) -> List[Event]:
        """Apply pagination to a list of events.

        Extracts a slice of events based on filters.offset and filters.limit.
        Returns empty list if offset is beyond the end of the list.

        Args:
            events: List of events to paginate
            filters: Query filters containing offset and limit

        Returns:
            Paginated slice of events
        """
        start = filters.offset
        end = start + filters.limit
        return events[start:end]

    def query(self, filters: EventFilters) -> List[Event]:
        """Query events with filters.

        Applies filters in sequence:
        1. workspace_id, subject, predicate, time range, search filters
        2. Sorting by specified field
        3. Pagination (offset + limit)

        Args:
            filters: Query filters

        Returns:
            List of matching events (may be empty)
        """
        # Apply filters
        results = self._apply_filters(self._events, filters)

        # Apply sorting
        results = self._apply_sorting(results, filters)

        # Apply pagination
        results = self._apply_pagination(results, filters)

        return results

    def count(self, filters: EventFilters) -> int:
        """Count events matching filters.

        Applies same filters as query() but without sorting or pagination.

        Args:
            filters: Query filters

        Returns:
            Number of matching events
        """
        # Apply filters only (no sorting or pagination for count)
        results = self._apply_filters(self._events, filters)
        return len(results)
