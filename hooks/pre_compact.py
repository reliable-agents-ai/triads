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

# Add src to path for imports
repo_root = Path(__file__).parent.parent
if str(repo_root / "src") not in sys.path:
    sys.path.insert(0, str(repo_root / "src"))

from triads.events.tools import capture_event  # noqa: E402
from triads.workspace_manager import get_active_workspace  # noqa: E402


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
        capture_event(
            subject="system",
            predicate="compact_starting",
            object_data={
                "trigger": trigger,
                "has_custom_instructions": len(custom_instructions) > 0,
                "has_workspace": workspace_id is not None
            },
            workspace_id=workspace_id,
            hook_name="pre_compact",
            execution_time_ms=(time.time() - start_time) * 1000,
            metadata={"version": "0.15.0"}
        )

    except Exception as e:
        # Capture error event
        capture_event(
            subject="hook",
            predicate="failed",
            object_data={
                "hook": "pre_compact",
                "error": str(e),
                "error_type": type(e).__name__
            },
            hook_name="pre_compact",
            execution_time_ms=(time.time() - start_time) * 1000,
            metadata={"version": "0.15.0"}
        )


if __name__ == "__main__":
    main()
