"""Unit tests for BlockingEnforcement.

Tests cover:
- Blocking behavior (returns False, exits)
- Allowing deployment when GT complete
- Error message formatting
- allow_force parameter
- State integration
- Metrics integration
"""

import sys
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest

from triads.workflow_enforcement.enforcement import (
    BlockingEnforcement,
    validate_deployment,
)
from triads.workflow_enforcement.state_manager import WorkflowStateManager
from triads.workflow_enforcement.validator import WorkflowValidator


@pytest.fixture
def mock_state_manager():
    """Create mock WorkflowStateManager."""
    manager = MagicMock(spec=WorkflowStateManager)
    manager.load_state.return_value = {
        "session_id": "test",
        "completed_triads": [],
        "current_phase": None,
        "last_transition": None,
        "metadata": {},
    }
    return manager


@pytest.fixture
def mock_validator():
    """Create mock WorkflowValidator."""
    validator = MagicMock(spec=WorkflowValidator)
    validator.calculate_metrics.return_value = {
        "loc_changed": 50,
        "files_changed": 3,
        "has_new_features": False,
        "git_available": True,
    }
    validator.requires_garden_tending.return_value = False
    return validator


@pytest.fixture
def enforcement(mock_state_manager, mock_validator):
    """Create BlockingEnforcement instance with mocks."""
    return BlockingEnforcement(mock_state_manager, mock_validator)


class TestValidationPass:
    """Test cases where validation passes."""

    def test_pass_no_implementation_yet(self, enforcement, mock_state_manager):
        """Test validation passes when implementation not started."""
        mock_state_manager.load_state.return_value = {"completed_triads": []}

        result = enforcement.validate_or_block(allow_force=True)

        assert result is True

    def test_pass_garden_tending_completed(self, enforcement, mock_state_manager):
        """Test validation passes when GT completed."""
        mock_state_manager.load_state.return_value = {
            "completed_triads": ["implementation", "garden-tending"]
        }

        result = enforcement.validate_or_block(allow_force=True)

        assert result is True

    def test_pass_low_metrics(self, enforcement, mock_state_manager, mock_validator):
        """Test validation passes when metrics don't trigger GT."""
        mock_state_manager.load_state.return_value = {
            "completed_triads": ["implementation"]
        }
        mock_validator.requires_garden_tending.return_value = False

        result = enforcement.validate_or_block(allow_force=True)

        assert result is True

    def test_pass_only_design_completed(self, enforcement, mock_state_manager):
        """Test validation passes with only design completed."""
        mock_state_manager.load_state.return_value = {
            "completed_triads": ["idea-validation", "design"]
        }

        result = enforcement.validate_or_block(allow_force=True)

        assert result is True


class TestValidationBlock:
    """Test cases where validation blocks."""

    def test_block_high_loc(self, enforcement, mock_state_manager, mock_validator):
        """Test blocking when LOC exceeds threshold."""
        mock_state_manager.load_state.return_value = {
            "completed_triads": ["implementation"]
        }
        mock_validator.calculate_metrics.return_value = {
            "loc_changed": 150,
            "files_changed": 3,
            "has_new_features": False,
        }
        mock_validator.requires_garden_tending.return_value = True

        result = enforcement.validate_or_block(allow_force=True)

        assert result is False

    def test_block_high_files(self, enforcement, mock_state_manager, mock_validator):
        """Test blocking when files exceed threshold."""
        mock_state_manager.load_state.return_value = {
            "completed_triads": ["implementation"]
        }
        mock_validator.calculate_metrics.return_value = {
            "loc_changed": 50,
            "files_changed": 8,
            "has_new_features": False,
        }
        mock_validator.requires_garden_tending.return_value = True

        result = enforcement.validate_or_block(allow_force=True)

        assert result is False

    def test_block_new_features(self, enforcement, mock_state_manager, mock_validator):
        """Test blocking when new features detected."""
        mock_state_manager.load_state.return_value = {
            "completed_triads": ["implementation"]
        }
        mock_validator.calculate_metrics.return_value = {
            "loc_changed": 50,
            "files_changed": 3,
            "has_new_features": True,
        }
        mock_validator.requires_garden_tending.return_value = True

        result = enforcement.validate_or_block(allow_force=True)

        assert result is False

    def test_block_exits_without_allow_force(
        self, enforcement, mock_state_manager, mock_validator
    ):
        """Test that blocking exits program without allow_force."""
        mock_state_manager.load_state.return_value = {
            "completed_triads": ["implementation"]
        }
        mock_validator.requires_garden_tending.return_value = True

        with pytest.raises(SystemExit) as exc_info:
            enforcement.validate_or_block(allow_force=False)

        assert exc_info.value.code == 1


class TestErrorMessages:
    """Test error message formatting."""

    def test_block_message_high_loc(
        self, enforcement, mock_state_manager, mock_validator
    ):
        """Test error message shows LOC when threshold exceeded."""
        mock_state_manager.load_state.return_value = {
            "completed_triads": ["implementation"]
        }
        mock_validator.calculate_metrics.return_value = {
            "loc_changed": 150,
            "files_changed": 3,
            "has_new_features": False,
        }
        mock_validator.requires_garden_tending.return_value = True

        # Capture stdout
        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            enforcement.validate_or_block(allow_force=True)

        output = captured_output.getvalue()
        assert "Garden Tending Required" in output
        assert "150 lines changed" in output
        assert "threshold: 100" in output

    def test_block_message_high_files(
        self, enforcement, mock_state_manager, mock_validator
    ):
        """Test error message shows files when threshold exceeded."""
        mock_state_manager.load_state.return_value = {
            "completed_triads": ["implementation"]
        }
        mock_validator.calculate_metrics.return_value = {
            "loc_changed": 50,
            "files_changed": 8,
            "has_new_features": False,
        }
        mock_validator.requires_garden_tending.return_value = True

        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            enforcement.validate_or_block(allow_force=True)

        output = captured_output.getvalue()
        assert "8 files changed" in output
        assert "threshold: 5" in output

    def test_block_message_new_features(
        self, enforcement, mock_state_manager, mock_validator
    ):
        """Test error message shows new features."""
        mock_state_manager.load_state.return_value = {
            "completed_triads": ["implementation"]
        }
        mock_validator.calculate_metrics.return_value = {
            "loc_changed": 50,
            "files_changed": 3,
            "has_new_features": True,
        }
        mock_validator.requires_garden_tending.return_value = True

        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            enforcement.validate_or_block(allow_force=True)

        output = captured_output.getvalue()
        assert "New features detected" in output

    def test_block_message_all_triggers(
        self, enforcement, mock_state_manager, mock_validator
    ):
        """Test error message shows all triggered rules."""
        mock_state_manager.load_state.return_value = {
            "completed_triads": ["implementation"]
        }
        mock_validator.calculate_metrics.return_value = {
            "loc_changed": 200,
            "files_changed": 10,
            "has_new_features": True,
        }
        mock_validator.requires_garden_tending.return_value = True

        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            enforcement.validate_or_block(allow_force=True)

        output = captured_output.getvalue()
        assert "200 lines changed" in output
        assert "10 files changed" in output
        assert "New features detected" in output

    def test_block_message_includes_bypass_instructions(
        self, enforcement, mock_state_manager, mock_validator
    ):
        """Test error message includes bypass instructions."""
        mock_state_manager.load_state.return_value = {
            "completed_triads": ["implementation"]
        }
        mock_validator.requires_garden_tending.return_value = True

        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            enforcement.validate_or_block(allow_force=True)

        output = captured_output.getvalue()
        assert "--force-deploy" in output
        assert "--justification" in output


class TestStateIntegration:
    """Test integration with state manager."""

    def test_loads_state_on_validation(
        self, enforcement, mock_state_manager, mock_validator
    ):
        """Test that validate_or_block loads state."""
        enforcement.validate_or_block(allow_force=True)

        mock_state_manager.load_state.assert_called_once()

    def test_checks_completed_triads(
        self, enforcement, mock_state_manager, mock_validator
    ):
        """Test that validation checks completed triads."""
        mock_state_manager.load_state.return_value = {
            "completed_triads": ["idea-validation", "design", "implementation"]
        }
        mock_validator.requires_garden_tending.return_value = True

        enforcement.validate_or_block(allow_force=True)

        # Should calculate metrics since implementation is done
        mock_validator.calculate_metrics.assert_called_once()

    def test_skips_metrics_if_no_implementation(
        self, enforcement, mock_state_manager, mock_validator
    ):
        """Test that metrics aren't calculated if no implementation."""
        mock_state_manager.load_state.return_value = {"completed_triads": ["design"]}

        enforcement.validate_or_block(allow_force=True)

        # Should not calculate metrics
        mock_validator.calculate_metrics.assert_not_called()


class TestMetricsIntegration:
    """Test integration with validator."""

    def test_calculates_metrics_when_needed(
        self, enforcement, mock_state_manager, mock_validator
    ):
        """Test metrics calculated when implementation done."""
        mock_state_manager.load_state.return_value = {
            "completed_triads": ["implementation"]
        }
        mock_validator.requires_garden_tending.return_value = False

        enforcement.validate_or_block(allow_force=True)

        mock_validator.calculate_metrics.assert_called_once()

    def test_passes_metrics_to_requires_gt(
        self, enforcement, mock_state_manager, mock_validator
    ):
        """Test metrics passed to requires_garden_tending."""
        mock_state_manager.load_state.return_value = {
            "completed_triads": ["implementation"]
        }
        test_metrics = {
            "loc_changed": 150,
            "files_changed": 8,
            "has_new_features": True,
        }
        mock_validator.calculate_metrics.return_value = test_metrics

        enforcement.validate_or_block(allow_force=True)

        mock_validator.requires_garden_tending.assert_called_once_with(test_metrics)


class TestValidateDeploymentFunction:
    """Test validate_deployment convenience function."""

    @patch("triads.workflow_enforcement.enforcement.BlockingEnforcement")
    def test_validate_deployment_creates_enforcement(self, mock_enforcement_class):
        """Test validate_deployment creates BlockingEnforcement."""
        mock_enforcement = MagicMock()
        mock_enforcement.validate_or_block.return_value = True
        mock_enforcement_class.return_value = mock_enforcement

        result = validate_deployment()

        mock_enforcement_class.assert_called_once()
        mock_enforcement.validate_or_block.assert_called_once()
        assert result is True

    @patch("triads.workflow_enforcement.enforcement.BlockingEnforcement")
    def test_validate_deployment_exits_on_failure(self, mock_enforcement_class):
        """Test validate_deployment exits on validation failure."""
        mock_enforcement = MagicMock()
        mock_enforcement.validate_or_block.side_effect = SystemExit(1)
        mock_enforcement_class.return_value = mock_enforcement

        with pytest.raises(SystemExit) as exc_info:
            validate_deployment()

        assert exc_info.value.code == 1


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_missing_completed_triads_key(
        self, enforcement, mock_state_manager, mock_validator
    ):
        """Test handling of state without completed_triads key."""
        mock_state_manager.load_state.return_value = {}

        result = enforcement.validate_or_block(allow_force=True)

        # Should pass (default to empty list)
        assert result is True

    def test_none_completed_triads(
        self, enforcement, mock_state_manager, mock_validator
    ):
        """Test handling of None completed_triads."""
        mock_state_manager.load_state.return_value = {"completed_triads": None}

        result = enforcement.validate_or_block(allow_force=True)

        # Should pass (None treated as empty)
        assert result is True

    def test_empty_metrics(self, enforcement, mock_state_manager, mock_validator):
        """Test handling of empty metrics dictionary."""
        mock_state_manager.load_state.return_value = {
            "completed_triads": ["implementation"]
        }
        mock_validator.calculate_metrics.return_value = {}
        mock_validator.requires_garden_tending.return_value = False

        result = enforcement.validate_or_block(allow_force=True)

        assert result is True

    def test_metrics_calculation_fails(
        self, enforcement, mock_state_manager, mock_validator
    ):
        """Test handling when metrics calculation raises exception."""
        mock_state_manager.load_state.return_value = {
            "completed_triads": ["implementation"]
        }
        mock_validator.calculate_metrics.side_effect = Exception("Git failed")

        with pytest.raises(Exception):
            enforcement.validate_or_block(allow_force=True)

    def test_duplicate_triads_in_completed(
        self, enforcement, mock_state_manager, mock_validator
    ):
        """Test handling of duplicate triads in completed list."""
        mock_state_manager.load_state.return_value = {
            "completed_triads": ["implementation", "implementation", "garden-tending"]
        }

        result = enforcement.validate_or_block(allow_force=True)

        # Should still pass (garden-tending is in list)
        assert result is True
