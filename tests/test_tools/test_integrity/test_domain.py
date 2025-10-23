"""
Tests for integrity tools domain models.

Tests ValidationResult and RepairResult domain objects.
"""

from pathlib import Path

import pytest

from triads.tools.integrity.domain import RepairResult, ValidationResult


class TestValidationResult:
    """Test ValidationResult domain model."""

    def test_validation_result_valid_graph(self):
        """Valid graph has no error and valid=True."""
        result = ValidationResult(
            triad="design",
            valid=True,
            error=None,
            error_field=None,
            error_count=0,
            file_path=Path(".claude/graphs/design_graph.json")
        )

        assert result.triad == "design"
        assert result.valid is True
        assert result.error is None
        assert result.error_field is None
        assert result.error_count == 0
        assert result.file_path == Path(".claude/graphs/design_graph.json")

    def test_validation_result_invalid_graph_with_error(self):
        """Invalid graph has error message and valid=False."""
        result = ValidationResult(
            triad="implementation",
            valid=False,
            error="Missing required field 'label' in node 0",
            error_field="nodes[0].label",
            error_count=1,
            file_path=Path(".claude/graphs/implementation_graph.json")
        )

        assert result.triad == "implementation"
        assert result.valid is False
        assert result.error == "Missing required field 'label' in node 0"
        assert result.error_field == "nodes[0].label"
        assert result.error_count == 1

    def test_validation_result_has_triad_and_file_path(self):
        """ValidationResult tracks triad name and file path."""
        result = ValidationResult(
            triad="generator",
            valid=True,
            file_path=Path("/custom/path/generator_graph.json")
        )

        assert result.triad == "generator"
        assert result.file_path == Path("/custom/path/generator_graph.json")

    def test_validation_result_defaults(self):
        """ValidationResult has sensible defaults for optional fields."""
        result = ValidationResult(triad="test", valid=True)

        assert result.error is None
        assert result.error_field is None
        assert result.error_count == 0
        assert result.file_path is None


class TestRepairResult:
    """Test RepairResult domain model."""

    def test_repair_result_success(self):
        """Successful repair has success=True and message."""
        result = RepairResult(
            triad="design",
            success=True,
            message="Successfully repaired graph",
            actions_taken="Removed 3 invalid edges",
            backup_created=True,
            backup_path=Path(".claude/graphs/backups/design_graph_20250101_120000.json.backup")
        )

        assert result.triad == "design"
        assert result.success is True
        assert result.message == "Successfully repaired graph"
        assert result.actions_taken == "Removed 3 invalid edges"
        assert result.backup_created is True
        assert result.backup_path.name == "design_graph_20250101_120000.json.backup"

    def test_repair_result_failure_with_message(self):
        """Failed repair has success=False and error message."""
        result = RepairResult(
            triad="implementation",
            success=False,
            message="Cannot repair: Missing required field 'id' in node",
            actions_taken=None,
            backup_created=False,
            backup_path=None
        )

        assert result.triad == "implementation"
        assert result.success is False
        assert "Cannot repair" in result.message
        assert result.actions_taken is None
        assert result.backup_created is False
        assert result.backup_path is None

    def test_repair_result_tracks_backup_creation(self):
        """RepairResult tracks whether backup was created."""
        # With backup
        with_backup = RepairResult(
            triad="test",
            success=True,
            message="Repaired",
            backup_created=True,
            backup_path=Path("/path/to/backup.json.backup")
        )
        assert with_backup.backup_created is True
        assert with_backup.backup_path is not None

        # Without backup
        without_backup = RepairResult(
            triad="test",
            success=True,
            message="Repaired",
            backup_created=False,
            backup_path=None
        )
        assert without_backup.backup_created is False
        assert without_backup.backup_path is None

    def test_repair_result_defaults(self):
        """RepairResult has sensible defaults for optional fields."""
        result = RepairResult(
            triad="test",
            success=True,
            message="OK"
        )

        assert result.actions_taken is None
        assert result.backup_created is False
        assert result.backup_path is None
