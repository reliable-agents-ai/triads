"""
Workspace Pause Handler: Auto-pause active workspaces on session end.

Checks for active workspaces and marks them as paused when a session ends.
Ensures workspace state persists between sessions for proper resumption.

Single Responsibility: Workspace lifecycle management only.

Usage:
    handler = WorkspacePauseHandler()
    result = handler.process()
    # result = {"workspace_id": "...", "paused": True, "reason": "..."}
"""

import json
import sys
from pathlib import Path
from typing import Dict, Optional

from setup_paths import setup_import_paths
setup_import_paths()

from triads.workspace_manager import (  # noqa: E402
    get_active_workspace,
    mark_workspace_paused
)


class WorkspacePauseHandler:
    """Handler for workspace auto-pause on session end."""

    def __init__(self, workspaces_dir: Path = None):
        """
        Initialize workspace pause handler.

        Args:
            workspaces_dir: Directory for workspaces (default: .triads/workspaces/)
        """
        self.workspaces_dir = workspaces_dir or Path('.triads/workspaces')

    def get_workspace_status(self, workspace_id: str) -> Optional[str]:
        """
        Get current status of a workspace.

        Args:
            workspace_id: Workspace identifier

        Returns:
            Status string ("active", "paused", "completed", etc.) or None if error
        """
        workspace_path = self.workspaces_dir / workspace_id
        state_file = workspace_path / "state.json"

        if not state_file.exists():
            return None

        try:
            with open(state_file, 'r') as f:
                state = json.load(f)
            return state.get('status', 'unknown')
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️  Could not read workspace state: {e}", file=sys.stderr)
            return None

    def pause_workspace(self, workspace_id: str, reason: str = "Session ended (auto-pause)") -> bool:
        """
        Pause an active workspace.

        Args:
            workspace_id: Workspace identifier
            reason: Reason for pausing

        Returns:
            bool: True if workspace was paused, False otherwise
        """
        try:
            mark_workspace_paused(workspace_id, reason=reason)
            print(f"⏸️  Auto-paused workspace: {workspace_id}", file=sys.stderr)
            print(f"   Workspace will resume automatically on next session start", file=sys.stderr)
            return True
        except Exception as e:
            print(f"❌ Error pausing workspace {workspace_id}: {e}", file=sys.stderr)
            return False

    def process(self) -> Dict:
        """
        Main entry point: check for active workspace and pause if needed.

        Process flow:
        1. Get active workspace ID
        2. Check workspace status
        3. If status is "active", pause workspace
        4. Return results

        This operation is non-critical and fails gracefully:
        - If no active workspace: return {"paused": False, "reason": "No active workspace"}
        - If workspace already paused/completed: return {"paused": False, "reason": "Already paused/completed"}
        - If pause fails: return {"paused": False, "error": "..."}

        Returns:
            dict: Processing results
                - workspace_id: Workspace ID (if found)
                - paused: True if workspace was paused
                - status: Workspace status before pause
                - reason: Reason for pause or why not paused
                - error: Error message if pause failed
        """
        try:
            # Get active workspace
            active_workspace = get_active_workspace()

            if not active_workspace:
                print("ℹ️  No active workspace (nothing to pause)", file=sys.stderr)
                return {
                    'workspace_id': None,
                    'paused': False,
                    'reason': 'No active workspace'
                }

            # Get workspace status
            current_status = self.get_workspace_status(active_workspace)

            if current_status is None:
                print(f"ℹ️  No state file for workspace {active_workspace}", file=sys.stderr)
                return {
                    'workspace_id': active_workspace,
                    'paused': False,
                    'status': None,
                    'reason': 'No state file found'
                }

            if current_status != 'active':
                print(
                    f"ℹ️  Workspace {active_workspace} status: {current_status} (no pause needed)",
                    file=sys.stderr
                )
                return {
                    'workspace_id': active_workspace,
                    'paused': False,
                    'status': current_status,
                    'reason': f'Workspace already {current_status}'
                }

            # Pause active workspace
            pause_reason = "Session ended (auto-pause)"
            paused = self.pause_workspace(active_workspace, reason=pause_reason)

            return {
                'workspace_id': active_workspace,
                'paused': paused,
                'status': current_status,
                'reason': pause_reason if paused else 'Failed to pause'
            }

        except Exception as e:
            # Non-critical feature - log error but don't crash
            print(f"⚠️  Workspace auto-pause check failed: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)

            return {
                'workspace_id': None,
                'paused': False,
                'error': str(e)
            }
