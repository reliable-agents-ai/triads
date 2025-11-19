#!/usr/bin/env python3
"""
PreToolUse Hook: Capture tool execution events before tool runs

This hook runs after Claude creates tool parameters and before processing the tool call.
Logs tool name, parameters, and execution context for observability.

Hook Type: PreToolUse
Configured in: hooks/hooks.json

Security:
- Input validation on all JSON data
- No sensitive parameter logging (credentials filtered)
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


def sanitize_tool_input(tool_input):
    """
    Remove sensitive data from tool parameters.

    Filters: passwords, tokens, api_keys, credentials
    """
    if not isinstance(tool_input, dict):
        return tool_input

    sensitive_keys = {'password', 'token', 'api_key', 'secret', 'credential', 'auth'}
    sanitized = {}

    for key, value in tool_input.items():
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            sanitized[key] = "[REDACTED]"
        elif isinstance(value, dict):
            sanitized[key] = sanitize_tool_input(value)
        else:
            sanitized[key] = value

    return sanitized


def main():
    """Log tool execution event before tool runs."""
    start_time = time.time()

    try:
        # Read input from stdin
        input_data = json.load(sys.stdin)

        tool_name = input_data.get('tool_name', 'unknown')
        tool_input = input_data.get('tool_input', {})
        tool_use_id = input_data.get('tool_use_id')

        # Sanitize tool input (remove sensitive data)
        sanitized_input = sanitize_tool_input(tool_input)

        # Get active workspace
        workspace_id = get_active_workspace()

        # Capture pre-tool-use event
        capture_event(
            subject="tool",
            predicate="pre_execution",
            object_data={
                "tool_name": tool_name,
                "tool_input_keys": list(sanitized_input.keys()) if isinstance(sanitized_input, dict) else None,
                "tool_use_id": tool_use_id,
                "has_workspace": workspace_id is not None
            },
            workspace_id=workspace_id,
            hook_name="pre_tool_use",
            execution_time_ms=(time.time() - start_time) * 1000,
            metadata={"version": "0.15.0"}
        )

    except Exception as e:
        # Capture error event
        capture_event(
            subject="hook",
            predicate="failed",
            object_data={
                "hook": "pre_tool_use",
                "error": str(e),
                "error_type": type(e).__name__
            },
            hook_name="pre_tool_use",
            execution_time_ms=(time.time() - start_time) * 1000,
            metadata={"version": "0.15.0"}
        )


if __name__ == "__main__":
    main()
