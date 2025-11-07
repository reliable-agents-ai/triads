"""MCP-compliant Python tools for event capture and query.

This module provides two primary functions for working with events:
- capture_event(): Capture a new event and save to repository
- query_events(): Query events with filters, pagination, and sorting

Both functions return dictionary results (never raise exceptions) for
MCP tool compatibility.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from triads.event_logger import truncate_large_payloads
from triads.events.exceptions import EventQueryError, EventStorageError, InvalidEventError
from triads.events.jsonl_repository import JSONLEventRepository
from triads.events.models import Event, EventFilters
from triads.events.repository import AbstractEventRepository

# Constants
MAX_PAYLOAD_SIZE = 10000


def capture_event(
    subject: str,
    predicate: str,
    object_data: Optional[Dict[str, Any]],
    workspace_id: Optional[str] = None,
    hook_name: Optional[str] = None,
    execution_time_ms: Optional[float] = None,
    metadata: Optional[Dict[str, Any]] = None,
    repository: Optional[AbstractEventRepository] = None,
) -> Dict[str, Any]:
    """Capture a new event and save to repository.

    This function validates inputs, creates an Event instance, truncates
    large payloads, and persists to the repository. Returns a dictionary
    result (never raises exceptions).

    Args:
        subject: RDF subject (what the event is about), e.g., "agent", "workspace"
        predicate: RDF predicate (what action occurred), e.g., "completed", "started"
        object_data: RDF object (event payload as dictionary)
        workspace_id: Optional workspace identifier
        hook_name: Optional name of hook that triggered event
        execution_time_ms: Optional hook execution time in milliseconds
        metadata: Optional additional metadata
        repository: Optional custom repository (default: JSONLEventRepository at .triads/events.jsonl)

    Returns:
        Dictionary with keys:
        - success: bool (True if saved, False if error)
        - event_id: str (UUID of saved event, if success=True)
        - message: str (success message or error description)
        - error: str (error details, if success=False)

    Example:
        >>> result = capture_event(
        ...     subject="agent",
        ...     predicate="completed",
        ...     object_data={"agent": "solution-architect", "confidence": 0.95}
        ... )
        >>> if result["success"]:
        ...     print(f"Event saved: {result['event_id']}")
        ... else:
        ...     print(f"Error: {result['error']}")
    """
    try:
        # Validate required fields
        if not subject or not isinstance(subject, str) or subject.strip() == "":
            return {
                "success": False,
                "error": "Validation error: 'subject' is required and cannot be empty",
                "message": "Event capture failed",
            }

        if not predicate or not isinstance(predicate, str) or predicate.strip() == "":
            return {
                "success": False,
                "error": "Validation error: 'predicate' is required and cannot be empty",
                "message": "Event capture failed",
            }

        if object_data is None:
            return {
                "success": False,
                "error": "Validation error: 'object_data' is required and cannot be None",
                "message": "Event capture failed",
            }

        if not isinstance(object_data, dict):
            return {
                "success": False,
                "error": "Validation error: 'object_data' must be a dictionary",
                "message": "Event capture failed",
            }

        # Truncate large payloads to prevent bloat
        truncated_data = truncate_large_payloads(object_data, max_size=MAX_PAYLOAD_SIZE)

        # Create Event instance
        event = Event(
            subject=subject.strip(),
            predicate=predicate.strip(),
            object_data=truncated_data,
            workspace_id=workspace_id,
            hook_name=hook_name,
            execution_time_ms=execution_time_ms,
            metadata=metadata or {},
        )

        # Get or create default repository
        if repository is None:
            repository = _get_default_repository()

        # Save to repository
        event_id = repository.save(event)

        return {
            "success": True,
            "event_id": event_id,
            "message": f"Event captured successfully: {subject}.{predicate}",
        }

    except InvalidEventError as e:
        return {
            "success": False,
            "error": f"Validation error: {str(e)}",
            "message": "Event capture failed",
        }

    except EventStorageError as e:
        return {
            "success": False,
            "error": f"Storage error: {str(e)}",
            "message": "Event capture failed",
        }

    except Exception as e:
        # Catch-all for unexpected errors
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "message": "Event capture failed",
        }


def query_events(
    workspace_id: Optional[str] = None,
    subject: Optional[str] = None,
    predicate: Optional[str] = None,
    time_from: Optional[str] = None,
    time_to: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    sort_by: str = "timestamp",
    sort_order: str = "desc",
    repository: Optional[AbstractEventRepository] = None,
) -> Dict[str, Any]:
    """Query events with filters, pagination, and sorting.

    This function parses ISO 8601 time strings, creates EventFilters,
    queries the repository, and serializes results. Returns a dictionary
    result (never raises exceptions).

    Args:
        workspace_id: Filter by workspace ID (optional)
        subject: Filter by event subject (optional)
        predicate: Filter by event predicate (optional)
        time_from: Filter events >= this timestamp (ISO 8601 string, optional)
        time_to: Filter events <= this timestamp (ISO 8601 string, optional)
        search: Full-text search in subject/predicate/error/object_data (optional)
        limit: Maximum number of results (default: 100)
        offset: Skip this many results (default: 0)
        sort_by: Field to sort by (default: "timestamp")
        sort_order: "asc" or "desc" (default: "desc")
        repository: Optional custom repository (default: JSONLEventRepository at .triads/events.jsonl)

    Returns:
        Dictionary with keys:
        - success: bool (True if query succeeded, False if error)
        - events: List[Dict] (list of event dictionaries, if success=True)
        - total_count: int (total matching events before pagination, if success=True)
        - message: str (success message or error description)
        - error: str (error details, if success=False)

    Example:
        >>> result = query_events(
        ...     subject="agent",
        ...     predicate="completed",
        ...     limit=10
        ... )
        >>> if result["success"]:
        ...     print(f"Found {result['total_count']} events")
        ...     for event in result["events"]:
        ...         print(f"  {event['timestamp']}: {event['subject']}.{event['predicate']}")
        ... else:
        ...     print(f"Error: {result['error']}")
    """
    try:
        # Parse time filters
        time_from_dt = _parse_iso_timestamp(time_from, "time_from")
        if isinstance(time_from_dt, dict):  # Error dict
            return time_from_dt

        time_to_dt = _parse_iso_timestamp(time_to, "time_to")
        if isinstance(time_to_dt, dict):  # Error dict
            return time_to_dt

        # Create EventFilters instance
        filters = EventFilters(
            workspace_id=workspace_id,
            subject=subject,
            predicate=predicate,
            time_from=time_from_dt,
            time_to=time_to_dt,
            search=search,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        # Get or create default repository
        if repository is None:
            repository = _get_default_repository()

        # Query events from repository
        events = repository.query(filters)

        # Get total count (without pagination)
        total_count = repository.count(filters)

        # Serialize events to dictionaries
        serialized_events = [_serialize_event(event) for event in events]

        return {
            "success": True,
            "events": serialized_events,
            "total_count": total_count,
            "message": f"Found {total_count} matching events",
        }

    except EventQueryError as e:
        return {
            "success": False,
            "error": f"Query error: {str(e)}",
            "message": "Query failed",
        }

    except Exception as e:
        # Catch-all for unexpected errors
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "message": "Query failed",
        }


def _get_default_repository() -> JSONLEventRepository:
    """Get default event repository instance.

    Returns:
        JSONLEventRepository configured with default path (.triads/events.jsonl)

    Note:
        Path is computed dynamically based on current working directory.
    """
    default_path = Path.cwd() / ".triads" / "events.jsonl"
    return JSONLEventRepository(default_path)


def _parse_iso_timestamp(
    timestamp_str: Optional[str], field_name: str
) -> Optional[datetime] | Dict[str, Any]:
    """Parse ISO 8601 timestamp string to datetime object.

    Args:
        timestamp_str: ISO 8601 formatted timestamp string (or None)
        field_name: Name of field (for error messages)

    Returns:
        datetime object (timezone-aware) if valid, None if input is None,
        or error dictionary if parsing fails

    Example:
        >>> dt = _parse_iso_timestamp("2025-10-30T14:30:22Z", "time_from")
        >>> isinstance(dt, datetime)
        True
    """
    if timestamp_str is None:
        return None

    try:
        # Parse ISO 8601 format (replace Z with +00:00 for fromisoformat)
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))

        # Ensure timezone-aware
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        return dt

    except (ValueError, AttributeError) as e:
        # Return error dictionary
        return {
            "success": False,
            "error": f"Invalid {field_name} format: {str(e)}. Expected ISO 8601 format.",
            "message": "Query failed",
        }


def _serialize_event(event: Event) -> Dict[str, Any]:
    """Convert Event object to dictionary with ISO timestamp.

    Args:
        event: Event object to serialize

    Returns:
        Dictionary representation of event with timestamp as ISO string

    Example:
        >>> event = Event("agent", "completed", {"confidence": 0.95})
        >>> serialized = _serialize_event(event)
        >>> print(serialized["timestamp"])  # ISO 8601 string
        "2025-10-30T14:30:22.123456+00:00"
    """
    data = {
        "id": event.id,
        "timestamp": event.timestamp.isoformat(),
        "subject": event.subject,
        "predicate": event.predicate,
        "object_data": event.object_data,
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
