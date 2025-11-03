"""Abstract base class for event repository."""

from abc import ABC, abstractmethod
from typing import List, Optional

from triads.events.models import Event, EventFilters


class AbstractEventRepository(ABC):
    """Abstract base class for event repository implementations.
    
    Defines the interface that all event repositories must implement.
    Repositories are responsible for persisting and querying events.
    
    Implementations:
        - InMemoryEventRepository: In-memory storage (testing, development)
        - FileEventRepository: File-based storage (simple persistence)
        - DatabaseEventRepository: Database storage (production)
    """

    @abstractmethod
    def save(self, event: Event) -> str:
        """Save an event to the repository.
        
        Args:
            event: Event to save
            
        Returns:
            str: Event ID of saved event
            
        Raises:
            InvalidEventError: If event validation fails
            EventStorageError: If save operation fails
        """
        pass

    @abstractmethod
    def get_by_id(self, event_id: str) -> Optional[Event]:
        """Retrieve a single event by ID.
        
        Args:
            event_id: Unique event identifier
            
        Returns:
            Event if found, None otherwise
        """
        pass

    @abstractmethod
    def query(self, filters: EventFilters) -> List[Event]:
        """Query events with filters.
        
        Args:
            filters: Query filters (workspace_id, subject, predicate, time range, etc.)
            
        Returns:
            List of matching events (may be empty)
            
        Raises:
            EventQueryError: If query operation fails
        """
        pass

    @abstractmethod
    def count(self, filters: EventFilters) -> int:
        """Count events matching filters.
        
        Args:
            filters: Query filters (same as query())
            
        Returns:
            Number of matching events
            
        Raises:
            EventQueryError: If count operation fails
        """
        pass
