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

# Add src to path for imports
repo_root = Path(__file__).parent.parent
if str(repo_root / "src") not in sys.path:
    sys.path.insert(0, str(repo_root / "src"))

from triads.events.tools import capture_event  # noqa: E402
from triads.workspace_manager import get_active_workspace  # noqa: E402


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
        capture_event(
            subject="system",
            predicate="notification_sent",
            object_data={
                "notification_type": notification_type,
                "message_length": len(message),
                "has_workspace": workspace_id is not None
            },
            workspace_id=workspace_id,
            hook_name="notification",
            execution_time_ms=(time.time() - start_time) * 1000,
            metadata={"version": "0.15.0"}
        )

    except Exception as e:
        # Capture error event
        capture_event(
            subject="hook",
            predicate="failed",
            object_data={
                "hook": "notification",
                "error": str(e),
                "error_type": type(e).__name__
            },
            hook_name="notification",
            execution_time_ms=(time.time() - start_time) * 1000,
            metadata={"version": "0.15.0"}
        )


if __name__ == "__main__":
    main()
