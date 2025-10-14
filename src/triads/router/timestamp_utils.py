"""
Timestamp utilities for router components.

Provides centralized, consistent timestamp generation to prevent
naive/aware datetime mixing bugs across the router system.
"""
from datetime import datetime, timezone


def utc_now_iso() -> str:
    """
    Generate current UTC timestamp in ISO 8601 format with 'Z' suffix.

    Returns consistent timezone-aware timestamps across all router components.
    Format: "2025-10-14T10:30:00.123456Z"

    Returns:
        ISO 8601 formatted UTC timestamp string with 'Z' suffix

    Example:
        >>> timestamp = utc_now_iso()
        >>> timestamp.endswith('Z')
        True
        >>> 'T' in timestamp
        True
    """
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def utc_now_aware() -> datetime:
    """
    Get current UTC time as timezone-aware datetime object.

    Returns:
        Timezone-aware datetime object in UTC

    Example:
        >>> dt = utc_now_aware()
        >>> dt.tzinfo is not None
        True
    """
    return datetime.now(timezone.utc)
