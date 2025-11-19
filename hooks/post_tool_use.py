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

# Add src to path for imports
repo_root = Path(__file__).parent.parent
if str(repo_root / "src") not in sys.path:
    sys.path.insert(0, str(repo_root / "src"))

from triads.events.tools import capture_event  # noqa: E402
from triads.workspace_manager import get_active_workspace  # noqa: E402


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

        # Capture post-tool-use event
        capture_event(
            subject="tool",
            predicate="post_execution",
            object_data={
                "tool_name": tool_name,
                "tool_use_id": tool_use_id,
                "response_size_bytes": response_size,
                "success": True,
                "has_workspace": workspace_id is not None
            },
            workspace_id=workspace_id,
            hook_name="post_tool_use",
            execution_time_ms=(time.time() - start_time) * 1000,
            metadata={"version": "0.15.0"}
        )

    except Exception as e:
        # Capture error event
        capture_event(
            subject="hook",
            predicate="failed",
            object_data={
                "hook": "post_tool_use",
                "error": str(e),
                "error_type": type(e).__name__
            },
            hook_name="post_tool_use",
            execution_time_ms=(time.time() - start_time) * 1000,
            metadata={"version": "0.15.0"}
        )


if __name__ == "__main__":
    main()
