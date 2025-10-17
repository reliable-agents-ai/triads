"""Unit tests for WorkflowValidator.

Tests cover:
- calculate_metrics with mock git diff output
- Enforcement rules (all combinations)
- Transition validation (valid sequences)
- get_required_phase logic
- Graceful degradation when git unavailable
"""

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from triads.workflow_enforcement.validator import (
    FILES_THRESHOLD,
    LOC_THRESHOLD,
    VALID_TRANSITIONS,
    WorkflowValidator,
)


@pytest.fixture
def validator():
    """Create WorkflowValidator instance."""
    return WorkflowValidator()


class TestCalculateMetrics:
    """Test metrics calculation from git diff."""

    @patch("subprocess.run")
    def test_metrics_with_git_available(self, mock_run, validator):
        """Test metrics calculation when git is available."""
        # Mock git rev-parse (git available)
        mock_rev_parse = MagicMock()
        mock_rev_parse.returncode = 0

        # Mock git diff output
        mock_diff = MagicMock()
        mock_diff.returncode = 0
        mock_diff.stdout = "10\t5\tsrc/file1.py\n20\t10\tsrc/file2.py\n"

        # Mock git name-status (no new files)
        mock_status = MagicMock()
        mock_status.returncode = 0
        mock_status.stdout = "M\tsrc/file1.py"

        mock_run.side_effect = [mock_rev_parse, mock_diff, mock_status, mock_status]

        metrics = validator.calculate_metrics()

        assert metrics["git_available"] is True
        assert metrics["loc_changed"] == 45  # 10+5+20+10
        assert metrics["files_changed"] == 2
        assert metrics["has_new_features"] is False

    @patch("subprocess.run")
    def test_metrics_git_not_available(self, mock_run, validator):
        """Test metrics when git is not available."""
        mock_run.side_effect = FileNotFoundError("git not found")

        metrics = validator.calculate_metrics()

        assert metrics["git_available"] is False
        assert metrics["loc_changed"] == 0
        assert metrics["files_changed"] == 0
        assert metrics["has_new_features"] is False

    @patch("subprocess.run")
    def test_metrics_not_git_repo(self, mock_run, validator):
        """Test metrics when not in a git repository."""
        mock_result = MagicMock()
        mock_result.returncode = 1  # Not a git repo

        mock_run.return_value = mock_result

        metrics = validator.calculate_metrics()

        assert metrics["git_available"] is False

    @patch("subprocess.run")
    def test_metrics_with_new_feature(self, mock_run, validator):
        """Test detection of new features."""
        # Mock git rev-parse
        mock_rev_parse = MagicMock()
        mock_rev_parse.returncode = 0

        # Mock git diff with new file in src/
        mock_diff = MagicMock()
        mock_diff.returncode = 0
        mock_diff.stdout = "50\t0\tsrc/new_feature.py\n"

        # Mock git name-status showing new file
        mock_status = MagicMock()
        mock_status.returncode = 0
        mock_status.stdout = "A\tsrc/new_feature.py"

        mock_run.side_effect = [mock_rev_parse, mock_diff, mock_status]

        metrics = validator.calculate_metrics()

        assert metrics["has_new_features"] is True
        assert metrics["loc_changed"] == 50
        assert metrics["files_changed"] == 1

    @patch("subprocess.run")
    def test_metrics_binary_files_skipped(self, mock_run, validator):
        """Test binary files are skipped in metrics."""
        mock_rev_parse = MagicMock()
        mock_rev_parse.returncode = 0

        # Binary files marked with "-"
        mock_diff = MagicMock()
        mock_diff.returncode = 0
        mock_diff.stdout = "-\t-\timage.png\n10\t5\tfile.py\n"

        mock_status = MagicMock()
        mock_status.returncode = 0
        mock_status.stdout = "M\tfile.py"

        mock_run.side_effect = [mock_rev_parse, mock_diff, mock_status]

        metrics = validator.calculate_metrics()

        assert metrics["loc_changed"] == 15  # Only file.py counted
        assert metrics["files_changed"] == 1

    @patch("subprocess.run")
    def test_metrics_empty_diff(self, mock_run, validator):
        """Test metrics with empty git diff."""
        mock_rev_parse = MagicMock()
        mock_rev_parse.returncode = 0

        mock_diff = MagicMock()
        mock_diff.returncode = 0
        mock_diff.stdout = ""

        mock_run.side_effect = [mock_rev_parse, mock_diff]

        metrics = validator.calculate_metrics()

        assert metrics["loc_changed"] == 0
        assert metrics["files_changed"] == 0

    @patch("subprocess.run")
    def test_metrics_custom_base_ref(self, mock_run, validator):
        """Test metrics with custom base reference."""
        mock_rev_parse = MagicMock()
        mock_rev_parse.returncode = 0

        mock_diff = MagicMock()
        mock_diff.returncode = 0
        mock_diff.stdout = "10\t5\tfile.py\n"

        mock_status = MagicMock()
        mock_status.returncode = 0
        mock_status.stdout = "M\tfile.py"

        mock_run.side_effect = [mock_rev_parse, mock_diff, mock_status]

        validator.calculate_metrics(base_ref="origin/main")

        # Verify git diff was called with correct base_ref
        assert mock_run.call_args_list[1][0][0] == [
            "git",
            "diff",
            "--numstat",
            "origin/main",
            "HEAD",
        ]

    @patch("subprocess.run")
    def test_metrics_timeout_handling(self, mock_run, validator):
        """Test graceful handling of git timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired("git", 5)

        metrics = validator.calculate_metrics()

        assert metrics["git_available"] is False
        assert metrics["loc_changed"] == 0

    @patch("subprocess.run")
    def test_metrics_invalid_numstat_format(self, mock_run, validator):
        """Test handling of invalid numstat format."""
        mock_rev_parse = MagicMock()
        mock_rev_parse.returncode = 0

        mock_diff = MagicMock()
        mock_diff.returncode = 0
        # Invalid format (missing tabs, non-numeric values)
        mock_diff.stdout = "invalid\nnotanumber\t5\tfile.py\n10\t5\tvalid.py\n"

        mock_status = MagicMock()
        mock_status.returncode = 0
        mock_status.stdout = "M\tvalid.py"

        mock_run.side_effect = [mock_rev_parse, mock_diff, mock_status]

        metrics = validator.calculate_metrics()

        # Should only count valid line
        assert metrics["loc_changed"] == 15  # 10+5 from valid.py
        assert metrics["files_changed"] == 1


class TestRequiresGardenTending:
    """Test Garden Tending requirement logic."""

    def test_requires_gt_high_loc(self, validator):
        """Test GT required when LOC exceeds threshold."""
        metrics = {"loc_changed": 150, "files_changed": 2, "has_new_features": False}

        assert validator.requires_garden_tending(metrics) is True

    def test_requires_gt_exact_threshold_loc(self, validator):
        """Test GT not required at exact LOC threshold."""
        metrics = {"loc_changed": 100, "files_changed": 2, "has_new_features": False}

        assert validator.requires_garden_tending(metrics) is False

    def test_requires_gt_just_over_threshold_loc(self, validator):
        """Test GT required just over LOC threshold."""
        metrics = {"loc_changed": 101, "files_changed": 2, "has_new_features": False}

        assert validator.requires_garden_tending(metrics) is True

    def test_requires_gt_high_files(self, validator):
        """Test GT required when files exceed threshold."""
        metrics = {"loc_changed": 50, "files_changed": 8, "has_new_features": False}

        assert validator.requires_garden_tending(metrics) is True

    def test_requires_gt_exact_threshold_files(self, validator):
        """Test GT not required at exact files threshold."""
        metrics = {"loc_changed": 50, "files_changed": 5, "has_new_features": False}

        assert validator.requires_garden_tending(metrics) is False

    def test_requires_gt_just_over_threshold_files(self, validator):
        """Test GT required just over files threshold."""
        metrics = {"loc_changed": 50, "files_changed": 6, "has_new_features": False}

        assert validator.requires_garden_tending(metrics) is True

    def test_requires_gt_new_features(self, validator):
        """Test GT required when new features added."""
        metrics = {"loc_changed": 50, "files_changed": 2, "has_new_features": True}

        assert validator.requires_garden_tending(metrics) is True

    def test_requires_gt_all_triggers(self, validator):
        """Test GT required when all triggers activated."""
        metrics = {"loc_changed": 200, "files_changed": 10, "has_new_features": True}

        assert validator.requires_garden_tending(metrics) is True

    def test_requires_gt_no_triggers(self, validator):
        """Test GT not required when no triggers activated."""
        metrics = {"loc_changed": 50, "files_changed": 3, "has_new_features": False}

        assert validator.requires_garden_tending(metrics) is False

    def test_requires_gt_zero_changes(self, validator):
        """Test GT not required with zero changes."""
        metrics = {"loc_changed": 0, "files_changed": 0, "has_new_features": False}

        assert validator.requires_garden_tending(metrics) is False

    def test_requires_gt_flag_override_require(self, validator):
        """Test require_garden_tending flag overrides metrics."""
        metrics = {"loc_changed": 0, "files_changed": 0, "has_new_features": False}
        flags = {"require_garden_tending": True}

        assert validator.requires_garden_tending(metrics, flags) is True

    def test_requires_gt_flag_override_skip(self, validator):
        """Test skip_garden_tending flag overrides metrics."""
        metrics = {"loc_changed": 200, "files_changed": 10, "has_new_features": True}
        flags = {"skip_garden_tending": True}

        assert validator.requires_garden_tending(metrics, flags) is False

    def test_requires_gt_flags_conflict(self, validator):
        """Test behavior when both flags set (require takes precedence)."""
        metrics = {"loc_changed": 50, "files_changed": 3, "has_new_features": False}
        flags = {"require_garden_tending": True, "skip_garden_tending": True}

        # require_garden_tending is checked first
        assert validator.requires_garden_tending(metrics, flags) is True

    def test_requires_gt_missing_metrics_keys(self, validator):
        """Test handling of missing metrics keys."""
        metrics = {}  # Empty metrics

        assert validator.requires_garden_tending(metrics) is False


class TestIsValidTransition:
    """Test workflow transition validation."""

    def test_valid_transition_from_none(self, validator):
        """Test valid transition from None (workflow start)."""
        assert validator.is_valid_transition(None, "idea-validation") is True

    def test_invalid_transition_from_none(self, validator):
        """Test invalid transition from None."""
        assert validator.is_valid_transition(None, "design") is False
        assert validator.is_valid_transition(None, "implementation") is False

    def test_valid_transition_idea_to_design(self, validator):
        """Test valid transition from idea-validation to design."""
        assert validator.is_valid_transition("idea-validation", "design") is True

    def test_invalid_transition_idea_to_implementation(self, validator):
        """Test invalid transition from idea-validation to implementation."""
        assert validator.is_valid_transition("idea-validation", "implementation") is False

    def test_valid_transition_design_to_implementation(self, validator):
        """Test valid transition from design to implementation."""
        assert validator.is_valid_transition("design", "implementation") is True

    def test_invalid_transition_design_to_deployment(self, validator):
        """Test invalid transition from design to deployment."""
        assert validator.is_valid_transition("design", "deployment") is False

    def test_valid_transition_implementation_to_gt(self, validator):
        """Test valid transition from implementation to garden-tending."""
        assert validator.is_valid_transition("implementation", "garden-tending") is True

    def test_valid_transition_implementation_to_deployment(self, validator):
        """Test valid transition from implementation to deployment (skip GT)."""
        assert validator.is_valid_transition("implementation", "deployment") is True

    def test_valid_transition_gt_to_deployment(self, validator):
        """Test valid transition from garden-tending to deployment."""
        assert validator.is_valid_transition("garden-tending", "deployment") is True

    def test_invalid_transition_deployment_to_any(self, validator):
        """Test no valid transitions from deployment (end of workflow)."""
        assert validator.is_valid_transition("deployment", "idea-validation") is False
        assert validator.is_valid_transition("deployment", "design") is False

    def test_invalid_transition_unknown_phase(self, validator):
        """Test invalid transition from unknown phase."""
        assert validator.is_valid_transition("unknown-phase", "design") is False

    def test_all_valid_transitions(self, validator):
        """Test all explicitly valid transitions."""
        valid_pairs = [
            (None, "idea-validation"),
            ("idea-validation", "design"),
            ("design", "implementation"),
            ("implementation", "garden-tending"),
            ("implementation", "deployment"),
            ("garden-tending", "deployment"),
        ]

        for from_phase, to_phase in valid_pairs:
            assert (
                validator.is_valid_transition(from_phase, to_phase) is True
            ), f"Expected {from_phase} -> {to_phase} to be valid"


class TestGetRequiredPhase:
    """Test next required phase detection."""

    def test_required_phase_from_none(self, validator):
        """Test next phase from None is idea-validation."""
        next_phase = validator.get_required_phase(None)
        assert next_phase == "idea-validation"

    def test_required_phase_from_idea_validation(self, validator):
        """Test next phase from idea-validation is design."""
        next_phase = validator.get_required_phase("idea-validation")
        assert next_phase == "design"

    def test_required_phase_from_design(self, validator):
        """Test next phase from design is implementation."""
        next_phase = validator.get_required_phase("design")
        assert next_phase == "implementation"

    def test_required_phase_from_implementation(self, validator):
        """Test next phase from implementation (returns first valid)."""
        next_phase = validator.get_required_phase("implementation")
        # Should return first valid (alphabetically sorted)
        assert next_phase in ["deployment", "garden-tending"]

    def test_required_phase_from_garden_tending(self, validator):
        """Test next phase from garden-tending is deployment."""
        next_phase = validator.get_required_phase("garden-tending")
        assert next_phase == "deployment"

    def test_required_phase_from_deployment(self, validator):
        """Test next phase from deployment is None (end)."""
        next_phase = validator.get_required_phase("deployment")
        assert next_phase is None

    def test_required_phase_unknown_phase(self, validator):
        """Test unknown phase returns None."""
        next_phase = validator.get_required_phase("unknown-phase")
        assert next_phase is None


class TestThresholdsConfiguration:
    """Test threshold configuration constants."""

    def test_loc_threshold_value(self):
        """Test LOC threshold is set correctly."""
        assert LOC_THRESHOLD == 100

    def test_files_threshold_value(self):
        """Test files threshold is set correctly."""
        assert FILES_THRESHOLD == 5

    def test_valid_transitions_structure(self):
        """Test VALID_TRANSITIONS has expected structure."""
        assert isinstance(VALID_TRANSITIONS, dict)
        assert None in VALID_TRANSITIONS
        assert "deployment" in VALID_TRANSITIONS
        assert VALID_TRANSITIONS["deployment"] == set()


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_metrics_with_none_values(self, validator):
        """Test handling of None values in metrics."""
        metrics = {"loc_changed": None, "files_changed": None, "has_new_features": None}

        # Should not crash - uses .get() with defaults
        result = validator.requires_garden_tending(metrics)
        assert result is False

    def test_metrics_with_negative_values(self, validator):
        """Test handling of negative values."""
        metrics = {"loc_changed": -10, "files_changed": -5, "has_new_features": False}

        # Should not trigger (negative < threshold)
        assert validator.requires_garden_tending(metrics) is False

    @patch("subprocess.run")
    def test_metrics_subprocess_error(self, mock_run, validator):
        """Test handling of subprocess errors."""
        mock_run.side_effect = subprocess.SubprocessError("Command failed")

        metrics = validator.calculate_metrics()

        # Should return safe defaults
        assert metrics["git_available"] is False
        assert metrics["loc_changed"] == 0
