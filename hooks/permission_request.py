#!/usr/bin/env python3
"""
PermissionRequest Hook: Capture permission dialog events

This hook runs when user sees permission dialog for tool execution.
Logs permission requests for security auditing and compliance.

Hook Type: PermissionRequest
Configured in: hooks/hooks.json

Security:
- Audit trail for all permission requests
- No sensitive data logging
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
    """Log permission request event."""
    start_time = time.time()

    try:
        # Read input from stdin
        input_data = json.load(sys.stdin)

        tool_name = input_data.get('tool_name', 'unknown')
        tool_use_id = input_data.get('tool_use_id')

        # Get active workspace
        workspace_id = get_active_workspace()

        # Capture permission request event (security audit trail)
        capture_hook_execution(
            hook_name="permission_request",
            start_time=start_time,
            object_data={
                "tool_name": tool_name,
                "tool_use_id": tool_use_id,
                "has_workspace": workspace_id is not None,
                "security_event": True
            },
            workspace_id=workspace_id,
            predicate="permission_requested"
        )

    except Exception as e:
        # Capture error event
        capture_hook_error(
            hook_name="permission_request",
            start_time=start_time,
            error=e
        )


if __name__ == "__main__":
    main()
