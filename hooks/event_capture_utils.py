"""
Event capture utilities for hooks.

Provides secure event capture with:
- Rate limiting (prevents DoS)
- Automatic file rotation (prevents unbounded growth)
- Fail-safe execution (never crashes hooks)
- Input validation (size limits enforced)

All functions return gracefully rather than raising exceptions.
This ensures hooks never crash and never block tool execution.

Usage:
    from event_capture_utils import capture_hook_execution, capture_hook_error

    start_time = time.time()
    try:
        # Hook logic here
        capture_hook_execution("hook_name", start_time, {"status": "success"})
    except Exception as e:
        capture_hook_error("hook_name", start_time, e)
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from constants import (
    EVENTS_FILE,
    MAX_EVENT_FILE_SIZE_MB,
    MAX_EVENTS_PER_FILE,
    EVENT_RATE_LIMIT_PER_MINUTE,
    PLUGIN_VERSION
)

# Rate limiting: Track event counts per hook per minute
_rate_limit_state = {}


def _check_rate_limit(hook_name: str) -> bool:
    """
    Check if hook has exceeded rate limit.

    Args:
        hook_name: Name of the hook

    Returns:
        bool: True if under limit, False if exceeded
    """
    current_minute = int(time.time() / 60)

    # Initialize state for this hook if needed
    if hook_name not in _rate_limit_state:
        _rate_limit_state[hook_name] = {"minute": current_minute, "count": 0}

    state = _rate_limit_state[hook_name]

    # Reset count if we're in a new minute
    if state["minute"] != current_minute:
        state["minute"] = current_minute
        state["count"] = 0

    # Check if under limit
    if state["count"] >= EVENT_RATE_LIMIT_PER_MINUTE:
        return False

    # Increment count
    state["count"] += 1
    return True


def _should_rotate_file(events_file: Path) -> bool:
    """
    Check if events file should be rotated.

    Rotation triggers:
    1. File size exceeds MAX_EVENT_FILE_SIZE_MB
    2. File has more than MAX_EVENTS_PER_FILE events

    Args:
        events_file: Path to events file

    Returns:
        bool: True if rotation needed
    """
    if not events_file.exists():
        return False

    # Check file size
    file_size_mb = events_file.stat().st_size / (1024 * 1024)
    if file_size_mb >= MAX_EVENT_FILE_SIZE_MB:
        return True

    # Check event count
    try:
        with open(events_file, 'r') as f:
            event_count = sum(1 for _ in f)
        if event_count >= MAX_EVENTS_PER_FILE:
            return True
    except Exception:
        # If we can't count events, don't rotate
        pass

    return False


def _rotate_file(events_file: Path) -> None:
    """
    Rotate events file by renaming with timestamp.

    Creates: events.jsonl.backup_20251119_152300

    Args:
        events_file: Path to events file
    """
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = events_file.with_suffix(f'.jsonl.backup_{timestamp}')
        events_file.rename(backup_file)
        print(f"ℹ️  Rotated events file to: {backup_file.name}", file=sys.stderr)
    except Exception as e:
        print(f"⚠️  Failed to rotate events file: {e}", file=sys.stderr)


def safe_capture_event(
    hook_name: str,
    predicate: str,
    object_data: Dict,
    workspace_id: Optional[str] = None
) -> bool:
    """
    Safely capture event with rate limiting, rotation, fail-safe handling.

    Security features:
    - Rate limiting: Max EVENT_RATE_LIMIT_PER_MINUTE events per hook
    - File rotation: Automatic at MAX_EVENT_FILE_SIZE_MB or MAX_EVENTS_PER_FILE
    - Input validation: object_data must be a dict
    - Fail-safe: Never raises exceptions

    Args:
        hook_name: Name of the hook (e.g., "session_start")
        predicate: Event predicate (e.g., "executed", "failed")
        object_data: Event-specific data (must be JSON-serializable dict)
        workspace_id: Optional workspace ID

    Returns:
        bool: True if event captured successfully, False otherwise

    Example:
        success = safe_capture_event(
            hook_name="session_start",
            predicate="executed",
            object_data={"source": "normal_session"},
            workspace_id="my-workspace"
        )
    """
    try:
        # Validate object_data is a dict
        if not isinstance(object_data, dict):
            print(f"⚠️  object_data must be a dict, got {type(object_data)}", file=sys.stderr)
            return False

        # Check rate limit
        if not _check_rate_limit(hook_name):
            print(f"⚠️  Rate limit exceeded for {hook_name} (max {EVENT_RATE_LIMIT_PER_MINUTE}/min)", file=sys.stderr)

            # Log to security audit log
            try:
                from security_audit import log_rate_limit_violation
                log_rate_limit_violation({
                    "hook": hook_name,
                    "limit_per_minute": EVENT_RATE_LIMIT_PER_MINUTE,
                    "action": "event_dropped"
                })
            except ImportError:
                pass  # Security audit module not available

            return False

        # Prepare events file
        events_file = Path(EVENTS_FILE)
        events_file.parent.mkdir(parents=True, exist_ok=True)

        # Check if rotation needed
        if _should_rotate_file(events_file):
            _rotate_file(events_file)

        # Build event
        event = {
            "timestamp": datetime.now().isoformat(),
            "hook": hook_name,
            "subject": "hook",
            "predicate": predicate,
            "object": object_data,
            "metadata": {
                "version": PLUGIN_VERSION
            }
        }

        # Add workspace_id if provided
        if workspace_id:
            event["workspace_id"] = workspace_id

        # Append event to file (JSONL format)
        with open(events_file, 'a') as f:
            f.write(json.dumps(event) + '\n')

        return True

    except Exception as e:
        # Fail silently - never crash hooks
        print(f"⚠️  Failed to capture event: {e}", file=sys.stderr)
        return False


def capture_hook_execution(
    hook_name: str,
    start_time: float,
    object_data: Dict,
    workspace_id: Optional[str] = None,
    predicate: str = "executed"
) -> bool:
    """
    Convenience wrapper with automatic timing calculation.

    Automatically calculates execution_time_ms from start_time
    and adds it to object_data.

    Args:
        hook_name: Name of the hook
        start_time: Start time from time.time()
        object_data: Event-specific data
        workspace_id: Optional workspace ID
        predicate: Event predicate (default: "executed")

    Returns:
        bool: True if event captured successfully

    Example:
        start_time = time.time()
        # ... hook logic ...
        capture_hook_execution(
            "session_start",
            start_time,
            {"source": "normal_session"}
        )
    """
    # Calculate execution time
    execution_time_ms = (time.time() - start_time) * 1000

    # Add execution time to object_data
    enhanced_data = {
        **object_data,
        "execution_time_ms": execution_time_ms
    }

    return safe_capture_event(
        hook_name=hook_name,
        predicate=predicate,
        object_data=enhanced_data,
        workspace_id=workspace_id
    )


def capture_hook_error(
    hook_name: str,
    start_time: float,
    error: Exception,
    workspace_id: Optional[str] = None
) -> bool:
    """
    Convenience wrapper for error events.

    Captures error type, message, and execution time.

    Args:
        hook_name: Name of the hook
        start_time: Start time from time.time()
        error: Exception that was raised
        workspace_id: Optional workspace ID

    Returns:
        bool: True if event captured successfully

    Example:
        start_time = time.time()
        try:
            # ... hook logic ...
        except Exception as e:
            capture_hook_error("session_start", start_time, e)
    """
    # Calculate execution time
    execution_time_ms = (time.time() - start_time) * 1000

    # Build error data
    error_data = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "execution_time_ms": execution_time_ms
    }

    return safe_capture_event(
        hook_name=hook_name,
        predicate="failed",
        object_data=error_data,
        workspace_id=workspace_id
    )
