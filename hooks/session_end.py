#!/usr/bin/env python3
"""
SessionEnd Hook: Capture session end events

This hook runs when a Claude Code session ends.
Logs session termination reason for observability and analytics.

Hook Type: SessionEnd
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
    """Log session end event."""
    start_time = time.time()

    try:
        # Read input from stdin
        input_data = json.load(sys.stdin)

        reason = input_data.get('reason', 'unknown')

        # Get active workspace
        workspace_id = get_active_workspace()

        # Capture session end event
        capture_hook_execution(
            hook_name="session_end",
            start_time=start_time,
            object_data={
                "reason": reason,
                "has_workspace": workspace_id is not None
            },
            workspace_id=workspace_id,
            predicate="ended"
        )

    except Exception as e:
        # Capture error event
        capture_hook_error(
            hook_name="session_end",
            start_time=start_time,
            error=e
        )


if __name__ == "__main__":
    main()
