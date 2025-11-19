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

# Add src to path for imports
repo_root = Path(__file__).parent.parent
if str(repo_root / "src") not in sys.path:
    sys.path.insert(0, str(repo_root / "src"))

from triads.events.tools import capture_event  # noqa: E402
from triads.workspace_manager import get_active_workspace  # noqa: E402


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
        capture_event(
            subject="security",
            predicate="permission_requested",
            object_data={
                "tool_name": tool_name,
                "tool_use_id": tool_use_id,
                "has_workspace": workspace_id is not None
            },
            workspace_id=workspace_id,
            hook_name="permission_request",
            execution_time_ms=(time.time() - start_time) * 1000,
            metadata={"version": "0.15.0", "security_event": True}
        )

    except Exception as e:
        # Capture error event
        capture_event(
            subject="hook",
            predicate="failed",
            object_data={
                "hook": "permission_request",
                "error": str(e),
                "error_type": type(e).__name__
            },
            hook_name="permission_request",
            execution_time_ms=(time.time() - start_time) * 1000,
            metadata={"version": "0.15.0"}
        )


if __name__ == "__main__":
    main()
