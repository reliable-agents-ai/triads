#!/usr/bin/env python3
"""
Notification Hook: Capture notification events

This hook runs when Claude Code sends notifications.
Logs notification type and message for observability.

Hook Type: Notification
Configured in: hooks/hooks.json

Security:
- Input validation on all JSON data
- Safe error handling (never crashes)

Quality:
- Single Responsibility: Only event logging
- Zero bloat: Minimal code
- SOLID compliant
"""

import json
import sys
import time
from pathlib import Path

# Use shared path setup utility (eliminates duplication)
from setup_paths import setup_import_paths
setup_import_paths()

# Use shared event capture (eliminates duplication, adds security)
from event_capture_utils import capture_hook_execution, capture_hook_error  # noqa: E402
from workspace_manager import get_active_workspace  # noqa: E402


def main():
    """Log notification event."""
    start_time = time.time()

    try:
        # Read input from stdin
        input_data = json.load(sys.stdin)

        message = input_data.get('message', '')
        notification_type = input_data.get('notification_type', 'info')

        # Get active workspace
        workspace_id = get_active_workspace()

        # Capture notification event
        capture_hook_execution(
            hook_name="notification",
            start_time=start_time,
            object_data={
                "notification_type": notification_type,
                "message_length": len(message),
                "has_workspace": workspace_id is not None
            },
            workspace_id=workspace_id,
            predicate="notification_sent"
        )

    except Exception as e:
        # Capture error event
        capture_hook_error(
            hook_name="notification",
            start_time=start_time,
            error=e
        )


if __name__ == "__main__":
    main()
