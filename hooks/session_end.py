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

# Add src to path for imports
repo_root = Path(__file__).parent.parent
if str(repo_root / "src") not in sys.path:
    sys.path.insert(0, str(repo_root / "src"))

from triads.events.tools import capture_event  # noqa: E402
from triads.workspace_manager import get_active_workspace  # noqa: E402


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
        capture_event(
            subject="session",
            predicate="ended",
            object_data={
                "reason": reason,
                "has_workspace": workspace_id is not None
            },
            workspace_id=workspace_id,
            hook_name="session_end",
            execution_time_ms=(time.time() - start_time) * 1000,
            metadata={"version": "0.15.0"}
        )

    except Exception as e:
        # Capture error event
        capture_event(
            subject="hook",
            predicate="failed",
            object_data={
                "hook": "session_end",
                "error": str(e),
                "error_type": type(e).__name__
            },
            hook_name="session_end",
            execution_time_ms=(time.time() - start_time) * 1000,
            metadata={"version": "0.15.0"}
        )


if __name__ == "__main__":
    main()
