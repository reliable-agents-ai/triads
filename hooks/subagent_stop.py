#!/usr/bin/env python3
"""
SubagentStop Hook: Capture subagent completion events

This hook runs when a Claude Code subagent (Task tool call) has finished responding.
Logs subagent execution completion for observability.

Hook Type: SubagentStop
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
    """Log subagent completion event."""
    start_time = time.time()

    try:
        # Read input from stdin
        input_data = json.load(sys.stdin)

        stop_hook_active = input_data.get('stop_hook_active', False)

        # Get active workspace
        workspace_id = get_active_workspace()

        # Capture subagent stop event
        capture_hook_execution(
            hook_name="subagent_stop",
            start_time=start_time,
            object_data={
                "stop_hook_active": stop_hook_active,
                "has_workspace": workspace_id is not None
            },
            workspace_id=workspace_id,
            predicate="subagent_completed"
        )

    except Exception as e:
        # Capture error event
        capture_hook_error(
            hook_name="subagent_stop",
            start_time=start_time,
            error=e
        )


if __name__ == "__main__":
    main()
