"""
Tests for WorkspacePauseHandler.

Tests cover:
- Getting workspace status from state files
- Pausing active workspaces
- Full process flow (active, paused, completed, no workspace)
- Error handling (missing files, JSON errors, exceptions)
- Edge cases (missing state file, invalid status)

Constitutional Principles Applied:
- Quality paramount: >80% coverage target
- Exhaustive testing: All code paths covered
- Security by design: File I/O and error handling tested
- SOLID principles: Tests are focused and independent
"""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add hooks directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'hooks'))

from handlers.workspace_pause_handler import WorkspacePauseHandler


# ==============================================================================
# Fixtures
# ==============================================================================

@pytest.fixture
def temp_workspaces_dir(tmp_path):
    """Create temporary directory for workspaces."""
    workspaces_dir = tmp_path / '.triads' / 'workspaces'
    workspaces_dir.mkdir(parents=True, exist_ok=True)
    return workspaces_dir


@pytest.fixture
def handler(temp_workspaces_dir):
    """Create WorkspacePauseHandler with temporary directory."""
    return WorkspacePauseHandler(workspaces_dir=temp_workspaces_dir)


@pytest.fixture
def create_workspace_state(temp_workspaces_dir):
    """Factory function to create workspace state files."""
    def _create_state(workspace_id: str, status: str = "active"):
        workspace_path = temp_workspaces_dir / workspace_id
        workspace_path.mkdir(exist_ok=True)
        state_file = workspace_path / "state.json"

        state_data = {
            "workspace_id": workspace_id,
            "status": status,
            "created_at": "2025-11-19T12:00:00",
            "updated_at": "2025-11-19T12:00:00"
        }

        with open(state_file, 'w') as f:
            json.dump(state_data, f, indent=2)

        return state_file

    return _create_state


# ==============================================================================
# Get Workspace Status Tests
# ==============================================================================

class TestGetWorkspaceStatus:
    """Tests for get_workspace_status method."""

    def test_get_status_active_workspace(self, handler, create_workspace_state):
        """Test getting status of active workspace."""
        create_workspace_state("test-workspace", "active")

        status = handler.get_workspace_status("test-workspace")

        assert status == "active"

    def test_get_status_paused_workspace(self, handler, create_workspace_state):
        """Test getting status of paused workspace."""
        create_workspace_state("test-workspace", "paused")

        status = handler.get_workspace_status("test-workspace")

        assert status == "paused"

    def test_get_status_completed_workspace(self, handler, create_workspace_state):
        """Test getting status of completed workspace."""
        create_workspace_state("test-workspace", "completed")

        status = handler.get_workspace_status("test-workspace")

        assert status == "completed"

    def test_get_status_missing_state_file(self, handler):
        """Test getting status when state file doesn't exist."""
        status = handler.get_workspace_status("nonexistent-workspace")

        assert status is None

    def test_get_status_invalid_json(self, handler, temp_workspaces_dir):
        """Test handling of invalid JSON in state file."""
        workspace_path = temp_workspaces_dir / "test-workspace"
        workspace_path.mkdir(exist_ok=True)
        state_file = workspace_path / "state.json"

        # Write invalid JSON
        state_file.write_text("{ invalid json }")

        status = handler.get_workspace_status("test-workspace")

        assert status is None

    def test_get_status_missing_status_field(self, handler, temp_workspaces_dir):
        """Test handling of state file without status field."""
        workspace_path = temp_workspaces_dir / "test-workspace"
        workspace_path.mkdir(exist_ok=True)
        state_file = workspace_path / "state.json"

        # Write JSON without status field
        with open(state_file, 'w') as f:
            json.dump({"workspace_id": "test-workspace"}, f)

        status = handler.get_workspace_status("test-workspace")

        assert status == "unknown"  # Default value


# ==============================================================================
# Pause Workspace Tests
# ==============================================================================

class TestPauseWorkspace:
    """Tests for pause_workspace method."""

    @patch('handlers.workspace_pause_handler.mark_workspace_paused')
    def test_pause_workspace_success(self, mock_mark_paused, handler):
        """Test successfully pausing a workspace."""
        mock_mark_paused.return_value = None  # Success (no exception)

        result = handler.pause_workspace("test-workspace")

        assert result is True
        mock_mark_paused.assert_called_once_with("test-workspace", reason="Session ended (auto-pause)")

    @patch('handlers.workspace_pause_handler.mark_workspace_paused')
    def test_pause_workspace_custom_reason(self, mock_mark_paused, handler):
        """Test pausing workspace with custom reason."""
        mock_mark_paused.return_value = None

        result = handler.pause_workspace("test-workspace", reason="Manual pause")

        assert result is True
        mock_mark_paused.assert_called_once_with("test-workspace", reason="Manual pause")

    @patch('handlers.workspace_pause_handler.mark_workspace_paused')
    def test_pause_workspace_failure(self, mock_mark_paused, handler):
        """Test handling of pause failure."""
        mock_mark_paused.side_effect = Exception("Failed to mark as paused")

        result = handler.pause_workspace("test-workspace")

        assert result is False


# ==============================================================================
# Process Flow Tests
# ==============================================================================

class TestProcess:
    """Tests for process method (full flow)."""

    @patch('handlers.workspace_pause_handler.get_active_workspace')
    @patch('handlers.workspace_pause_handler.mark_workspace_paused')
    def test_process_active_workspace(self, mock_mark_paused, mock_get_active, handler, create_workspace_state):
        """Test processing when workspace is active."""
        mock_get_active.return_value = "test-workspace"
        mock_mark_paused.return_value = None
        create_workspace_state("test-workspace", "active")

        result = handler.process()

        assert result['workspace_id'] == "test-workspace"
        assert result['paused'] is True
        assert result['status'] == "active"
        assert "Session ended" in result['reason']
        mock_mark_paused.assert_called_once()

    @patch('handlers.workspace_pause_handler.get_active_workspace')
    def test_process_no_active_workspace(self, mock_get_active, handler):
        """Test processing when no active workspace exists."""
        mock_get_active.return_value = None

        result = handler.process()

        assert result['workspace_id'] is None
        assert result['paused'] is False
        assert result['reason'] == 'No active workspace'

    @patch('handlers.workspace_pause_handler.get_active_workspace')
    def test_process_paused_workspace(self, mock_get_active, handler, create_workspace_state):
        """Test processing when workspace is already paused."""
        mock_get_active.return_value = "test-workspace"
        create_workspace_state("test-workspace", "paused")

        result = handler.process()

        assert result['workspace_id'] == "test-workspace"
        assert result['paused'] is False
        assert result['status'] == "paused"
        assert "already paused" in result['reason']

    @patch('handlers.workspace_pause_handler.get_active_workspace')
    def test_process_completed_workspace(self, mock_get_active, handler, create_workspace_state):
        """Test processing when workspace is completed."""
        mock_get_active.return_value = "test-workspace"
        create_workspace_state("test-workspace", "completed")

        result = handler.process()

        assert result['workspace_id'] == "test-workspace"
        assert result['paused'] is False
        assert result['status'] == "completed"
        assert "already completed" in result['reason']

    @patch('handlers.workspace_pause_handler.get_active_workspace')
    def test_process_missing_state_file(self, mock_get_active, handler):
        """Test processing when workspace has no state file."""
        mock_get_active.return_value = "test-workspace"

        result = handler.process()

        assert result['workspace_id'] == "test-workspace"
        assert result['paused'] is False
        assert result['status'] is None
        assert "No state file" in result['reason']

    @patch('handlers.workspace_pause_handler.get_active_workspace')
    @patch('handlers.workspace_pause_handler.mark_workspace_paused')
    def test_process_pause_failure(self, mock_mark_paused, mock_get_active, handler, create_workspace_state):
        """Test processing when pause operation fails."""
        mock_get_active.return_value = "test-workspace"
        mock_mark_paused.side_effect = Exception("Pause failed")
        create_workspace_state("test-workspace", "active")

        result = handler.process()

        assert result['workspace_id'] == "test-workspace"
        assert result['paused'] is False
        assert result['reason'] == "Failed to pause"

    @patch('handlers.workspace_pause_handler.get_active_workspace')
    def test_process_exception_handling(self, mock_get_active, handler):
        """Test that process handles exceptions gracefully."""
        mock_get_active.side_effect = Exception("Unexpected error")

        result = handler.process()

        assert result['workspace_id'] is None
        assert result['paused'] is False
        assert 'error' in result
        assert "Unexpected error" in result['error']


# ==============================================================================
# Edge Cases and Error Handling
# ==============================================================================

class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_workspace_with_special_characters(self, handler, create_workspace_state):
        """Test handling workspace IDs with special characters."""
        workspace_id = "test-workspace-v2.1_final"
        create_workspace_state(workspace_id, "active")

        status = handler.get_workspace_status(workspace_id)

        assert status == "active"

    def test_workspace_with_unicode(self, handler, temp_workspaces_dir):
        """Test handling workspace IDs with unicode characters."""
        workspace_id = "test-café-résumé"
        workspace_path = temp_workspaces_dir / workspace_id
        workspace_path.mkdir(exist_ok=True)
        state_file = workspace_path / "state.json"

        with open(state_file, 'w') as f:
            json.dump({"workspace_id": workspace_id, "status": "active"}, f)

        status = handler.get_workspace_status(workspace_id)

        assert status == "active"

    def test_empty_state_file(self, handler, temp_workspaces_dir):
        """Test handling of empty state file."""
        workspace_path = temp_workspaces_dir / "test-workspace"
        workspace_path.mkdir(exist_ok=True)
        state_file = workspace_path / "state.json"

        # Write empty file
        state_file.write_text("")

        status = handler.get_workspace_status("test-workspace")

        assert status is None

    def test_corrupted_state_file(self, handler, temp_workspaces_dir):
        """Test handling of corrupted state file."""
        workspace_path = temp_workspaces_dir / "test-workspace"
        workspace_path.mkdir(exist_ok=True)
        state_file = workspace_path / "state.json"

        # Write binary garbage
        state_file.write_bytes(b'\x00\x01\x02\x03\x04\x05')

        status = handler.get_workspace_status("test-workspace")

        assert status is None

    @patch('handlers.workspace_pause_handler.get_active_workspace')
    @patch('handlers.workspace_pause_handler.mark_workspace_paused')
    def test_multiple_process_calls(self, mock_mark_paused, mock_get_active, handler, create_workspace_state):
        """Test calling process multiple times."""
        mock_get_active.return_value = "test-workspace"
        mock_mark_paused.return_value = None
        create_workspace_state("test-workspace", "active")

        # First call should pause
        result1 = handler.process()
        assert result1['paused'] is True

        # Update status to paused
        state_file = handler.workspaces_dir / "test-workspace" / "state.json"
        with open(state_file, 'r') as f:
            state = json.load(f)
        state['status'] = 'paused'
        with open(state_file, 'w') as f:
            json.dump(state, f)

        # Second call should not pause (already paused)
        result2 = handler.process()
        assert result2['paused'] is False
        assert "already paused" in result2['reason']

    def test_state_file_permissions_error(self, handler, temp_workspaces_dir):
        """Test handling of permission errors when reading state file."""
        workspace_path = temp_workspaces_dir / "test-workspace"
        workspace_path.mkdir(exist_ok=True)
        state_file = workspace_path / "state.json"

        with open(state_file, 'w') as f:
            json.dump({"workspace_id": "test-workspace", "status": "active"}, f)

        # Make file unreadable (on Unix-like systems)
        import os
        if os.name != 'nt':  # Skip on Windows
            state_file.chmod(0o000)

            status = handler.get_workspace_status("test-workspace")

            # Should return None due to permission error
            assert status is None

            # Restore permissions for cleanup
            state_file.chmod(0o644)

    @patch('handlers.workspace_pause_handler.mark_workspace_paused')
    @patch('handlers.workspace_pause_handler.get_active_workspace')
    def test_various_workspace_statuses(self, mock_get_active, mock_mark_paused, handler, create_workspace_state):
        """Test handling of various workspace status values."""
        mock_mark_paused.return_value = None  # Mock the pause function

        test_statuses = [
            "active",
            "paused",
            "completed",
            "failed",
            "cancelled",
            "pending",
            "unknown"
        ]

        for test_status in test_statuses:
            workspace_id = f"workspace-{test_status}"
            mock_get_active.return_value = workspace_id
            create_workspace_state(workspace_id, test_status)

            result = handler.process()

            assert result['workspace_id'] == workspace_id
            assert result['status'] == test_status

            # Only active workspaces should be paused
            if test_status == "active":
                assert result['paused'] is True
            else:
                assert result['paused'] is False

    @patch('handlers.workspace_pause_handler.get_active_workspace')
    @patch('handlers.workspace_pause_handler.mark_workspace_paused')
    def test_pause_reason_propagation(self, mock_mark_paused, mock_get_active, handler, create_workspace_state):
        """Test that pause reason is correctly propagated."""
        mock_get_active.return_value = "test-workspace"
        mock_mark_paused.return_value = None
        create_workspace_state("test-workspace", "active")

        result = handler.process()

        assert result['paused'] is True
        assert result['reason'] == "Session ended (auto-pause)"

        # Verify the reason was passed to mark_workspace_paused
        mock_mark_paused.assert_called_once()
        call_args = mock_mark_paused.call_args
        assert call_args[1]['reason'] == "Session ended (auto-pause)"

    def test_handler_initialization_with_custom_dir(self, tmp_path):
        """Test handler initialization with custom workspaces directory."""
        custom_dir = tmp_path / 'custom' / 'workspaces'
        handler = WorkspacePauseHandler(workspaces_dir=custom_dir)

        assert handler.workspaces_dir == custom_dir

    def test_handler_initialization_default_dir(self):
        """Test handler initialization with default directory."""
        handler = WorkspacePauseHandler()

        assert handler.workspaces_dir == Path('.triads/workspaces')
