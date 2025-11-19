#!/usr/bin/env python3
"""
PreCompact Hook: Capture compact operation events

This hook runs before Claude Code is about to run a compact operation.
Logs compact trigger and custom instructions for observability.

Hook Type: PreCompact
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
    """Log pre-compact event."""
    start_time = time.time()

    try:
        # Read input from stdin
        input_data = json.load(sys.stdin)

        trigger = input_data.get('trigger', 'unknown')
        custom_instructions = input_data.get('custom_instructions', '')

        # Get active workspace
        workspace_id = get_active_workspace()

        # Capture pre-compact event
        capture_hook_execution(
            hook_name="pre_compact",
            start_time=start_time,
            object_data={
                "trigger": trigger,
                "has_custom_instructions": len(custom_instructions) > 0,
                "has_workspace": workspace_id is not None
            },
            workspace_id=workspace_id,
            predicate="compact_starting"
        )

    except Exception as e:
        # Capture error event
        capture_hook_error(
            hook_name="pre_compact",
            start_time=start_time,
            error=e
        )


if __name__ == "__main__":
    main()
