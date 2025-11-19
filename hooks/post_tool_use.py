#!/usr/bin/env python3
"""
PostToolUse Hook: Capture tool execution events after tool completes

This hook runs immediately after a tool completes successfully.
Logs tool name, response, and execution success for observability.

Hook Type: PostToolUse
Configured in: hooks/hooks.json

Security:
- Input validation on all JSON data
- Response size limits (prevent bloat)
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

# Setup import paths using shared utility
from setup_paths import setup_import_paths
setup_import_paths()

from event_capture_utils import safe_capture_event, capture_hook_error  # noqa: E402
from workspace_manager import get_active_workspace  # noqa: E402


def main():
    """Log tool execution event after tool completes."""
    start_time = time.time()

    try:
        # Read input from stdin
        input_data = json.load(sys.stdin)

        tool_name = input_data.get('tool_name', 'unknown')
        tool_input = input_data.get('tool_input', {})
        tool_response = input_data.get('tool_response', {})
        tool_use_id = input_data.get('tool_use_id')

        # Calculate response size (for monitoring)
        response_size = len(json.dumps(tool_response)) if tool_response else 0

        # Get active workspace
        workspace_id = get_active_workspace()

        # Capture post-tool-use event (Note: This is a tool event, not a hook event)
        # Using safe_capture_event directly since subject is "tool" not "hook"
        safe_capture_event(
            hook_name="post_tool_use",
            predicate="tool_executed",
            object_data={
                "tool_name": tool_name,
                "tool_use_id": tool_use_id,
                "response_size_bytes": response_size,
                "success": True,
                "has_workspace": workspace_id is not None,
                "execution_time_ms": (time.time() - start_time) * 1000
            },
            workspace_id=workspace_id
        )

    except Exception as e:
        # Capture error event
        capture_hook_error(
            "post_tool_use",
            start_time,
            e
        )


if __name__ == "__main__":
    main()
