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

# Add src to path for imports
repo_root = Path(__file__).parent.parent
if str(repo_root / "src") not in sys.path:
    sys.path.insert(0, str(repo_root / "src"))

from triads.events.tools import capture_event  # noqa: E402
from triads.workspace_manager import get_active_workspace  # noqa: E402


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
        capture_event(
            subject="agent",
            predicate="subagent_completed",
            object_data={
                "stop_hook_active": stop_hook_active,
                "has_workspace": workspace_id is not None
            },
            workspace_id=workspace_id,
            hook_name="subagent_stop",
            execution_time_ms=(time.time() - start_time) * 1000,
            metadata={"version": "0.15.0"}
        )

    except Exception as e:
        # Capture error event
        capture_event(
            subject="hook",
            predicate="failed",
            object_data={
                "hook": "subagent_stop",
                "error": str(e),
                "error_type": type(e).__name__
            },
            hook_name="subagent_stop",
            execution_time_ms=(time.time() - start_time) * 1000,
            metadata={"version": "0.15.0"}
        )


if __name__ == "__main__":
    main()
