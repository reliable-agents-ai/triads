"""JSONL file-based implementation of event repository.

Stores events in JSON Lines format (one JSON object per line) for append-only
persistence. Supports backward compatibility with old sessions.jsonl format.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Union
from uuid import uuid4

from triads.events.exceptions import EventStorageError, InvalidEventError
from triads.events.models import Event, EventFilters
from triads.events.repository import AbstractEventRepository


class JSONLEventRepository(AbstractEventRepository):
    """JSONL file-based implementation of event repository.
    
    Stores events in JSON Lines format (one JSON object per line).
    Supports backward compatibility with old sessions.jsonl format.
    
    Features:
        - Append-only writes (thread-safe for single file)
        - Automatic migration from old format (object -> object_data)
        - Handles corrupt lines gracefully
        - Supports all query/filter operations from AbstractEventRepository
    
    Args:
        file_path: Path to JSONL file
        auto_migrate: If True, automatically migrates old format events (default: True)
    
    Example:
        >>> repo = JSONLEventRepository("events.jsonl")
        >>> event = Event("agent", "completed", {"confidence": 0.95})
        >>> repo.save(event)
    """

    def __init__(self, file_path: Union[str, Path], auto_migrate: bool = True):
        """Initialize repository with file path.
        
        Args:
            file_path: Path to JSONL file
            auto_migrate: If True, automatically migrates old format events
        """
        self._file_path = Path(file_path)
        self._auto_migrate = auto_migrate
        
        # Create parent directories if they don't exist
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create file if it doesn't exist
        if not self._file_path.exists():
            self._file_path.touch()

    def _read_all_events(self) -> List[Event]:
        """Read all events from JSONL file.
        
        Handles:
        - Empty files
        - Corrupt JSON lines (skips gracefully)
        - Old format migration (if auto_migrate=True)
        - Missing required fields (skips gracefully)
        
        Returns:
            List of Event objects
        """
        if not self._file_path.exists():
            return []
        
        content = self._file_path.read_text(encoding="utf-8")
        
        if not content.strip():
            return []
        
        events = []
        
        for line_num, line in enumerate(content.strip().split("\n"), 1):
            try:
                data = json.loads(line)
                
                # Migrate old format if needed
                if self._auto_migrate:
                    data = self._migrate_event_data(data)
                
                # Convert to Event object
                event = self._dict_to_event(data)
                if event:
                    events.append(event)
                    
            except json.JSONDecodeError:
                # Skip corrupt lines gracefully
                continue
            except Exception:
                # Skip any other parsing errors gracefully
                continue
        
        return events

    def _migrate_event_data(self, data: dict) -> dict:
        """Migrate old format event data to new format.
        
        Old format:
            {"timestamp": "...", "subject": "...", "predicate": "...", "object": {...}}
        
        New format:
            {"subject": "...", "predicate": "...", "object_data": {...}, "id": "...", "timestamp": "..."}
        
        Args:
            data: Event data dictionary
        
        Returns:
            Migrated event data dictionary
        """
        migrated = data.copy()
        
        # Convert "object" to "object_data"
        if "object" in migrated and "object_data" not in migrated:
            migrated["object_data"] = migrated.pop("object")
        
        # Generate ID if missing
        if "id" not in migrated:
            migrated["id"] = str(uuid4())
        
        return migrated

    def _dict_to_event(self, data: dict) -> Optional[Event]:
        """Convert dictionary to Event object.
        
        Args:
            data: Event data dictionary
        
        Returns:
            Event object or None if required fields missing
        """
        # Check required fields
        if "subject" not in data or "predicate" not in data:
            return None
        
        if not data.get("predicate"):
            return None
        
        # Ensure object_data exists
        if "object_data" not in data:
            data["object_data"] = {}
        
        try:
            # Parse timestamp if it's a string
            timestamp = data.get("timestamp")
            if isinstance(timestamp, str):
                # Try parsing different ISO 8601 formats
                try:
                    timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                except ValueError:
                    # If parsing fails, use current time
                    timestamp = datetime.now(timezone.utc)
            elif timestamp is None:
                timestamp = datetime.now(timezone.utc)
            
            # Ensure timezone-aware
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)
            
            # Create Event object
            event = Event(
                subject=data["subject"],
                predicate=data["predicate"],
                object_data=data["object_data"],
                id=data.get("id", str(uuid4())),
                timestamp=timestamp,
                workspace_id=data.get("workspace_id"),
                hook_name=data.get("hook_name"),
                execution_time_ms=data.get("execution_time_ms"),
                error=data.get("error"),
                metadata=data.get("metadata", {})
            )
            
            return event
            
        except Exception:
            # If Event creation fails, return None
            return None

    def _event_to_dict(self, event: Event) -> dict:
        """Convert Event object to dictionary for JSON serialization.
        
        Args:
            event: Event object
        
        Returns:
            Dictionary ready for JSON serialization
        """
        data = {
            "subject": event.subject,
            "predicate": event.predicate,
            "object_data": event.object_data,
            "id": event.id,
            "timestamp": event.timestamp.isoformat(),
        }
        
        # Add optional fields if present
        if event.workspace_id is not None:
            data["workspace_id"] = event.workspace_id
        
        if event.hook_name is not None:
            data["hook_name"] = event.hook_name
        
        if event.execution_time_ms is not None:
            data["execution_time_ms"] = event.execution_time_ms
        
        if event.error is not None:
            data["error"] = event.error
        
        if event.metadata:
            data["metadata"] = event.metadata
        
        return data

    def save(self, event: Event) -> str:
        """Save an event to JSONL file.
        
        Args:
            event: Event to save
        
        Returns:
            str: Event ID of saved event
        
        Raises:
            InvalidEventError: If event validation fails
            EventStorageError: If save operation fails
        """
        # Validation
        if event is None:
            raise InvalidEventError("Event cannot be None")
        
        if not event.predicate or event.predicate.strip() == "":
            raise InvalidEventError("Event predicate cannot be empty")
        
        try:
            # Convert to dictionary
            data = self._event_to_dict(event)
            
            # Append to file (atomic operation)
            with open(self._file_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(data) + "\n")
            
            return event.id
            
        except (IOError, OSError) as e:
            raise EventStorageError(f"Failed to save event: {e}")

    def get_by_id(self, event_id: str) -> Optional[Event]:
        """Retrieve a single event by ID.
        
        Args:
            event_id: Unique event identifier
        
        Returns:
            Event if found, None otherwise
        """
        if not event_id:
            return None
        
        # Read all events and search
        events = self._read_all_events()
        
        for event in events:
            if event.id == event_id:
                return event
        
        return None

    def _apply_filters(self, events: List[Event], filters: EventFilters) -> List[Event]:
        """Apply all query filters to a list of events.
        
        Reuses filtering logic from InMemoryEventRepository.
        
        Args:
            events: List of events to filter
            filters: Query filters to apply
        
        Returns:
            Filtered list of events
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
                if (search_lower in e.subject.lower() or
                    search_lower in e.predicate.lower() or
                    (e.error and search_lower in e.error.lower()) or
                    search_lower in str(e.object_data).lower()):
                    filtered.append(e)
            results = filtered

        return results

    def _apply_sorting(self, events: List[Event], filters: EventFilters) -> List[Event]:
        """Apply sorting to a list of events.
        
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
        
        Args:
            filters: Query filters
        
        Returns:
            List of matching events (may be empty)
        """
        # Read all events from file
        events = self._read_all_events()
        
        # Apply filters
        results = self._apply_filters(events, filters)
        
        # Apply sorting
        results = self._apply_sorting(results, filters)
        
        # Apply pagination
        results = self._apply_pagination(results, filters)
        
        return results

    def count(self, filters: EventFilters) -> int:
        """Count events matching filters.
        
        Args:
            filters: Query filters
        
        Returns:
            Number of matching events
        """
        # Read all events from file
        events = self._read_all_events()
        
        # Apply filters only (no sorting or pagination)
        results = self._apply_filters(events, filters)
        
        return len(results)
