"""
Tests for integrity tools service layer.

Tests IntegrityService which coordinates validation and repair operations.
"""

from pathlib import Path
from unittest.mock import MagicMock, Mock

import pytest

from triads.km.integrity_checker import ValidationResult as KMValidationResult
from triads.km.integrity_checker import RepairResult as KMRepairResult
from triads.tools.integrity.domain import RepairResult, ValidationResult
from triads.tools.integrity.repository import InMemoryBackupRepository
from triads.tools.integrity.service import IntegrityService


@pytest.fixture
def mock_checker():
    """Mock IntegrityChecker for testing."""
    checker = Mock()
    return checker


@pytest.fixture
def in_memory_repo():
    """In-memory backup repository for testing."""
    return InMemoryBackupRepository()


@pytest.fixture
def service_with_mocks(mock_checker, in_memory_repo):
    """IntegrityService with mocked dependencies."""
    service = IntegrityService(backup_repo=in_memory_repo, graphs_dir=Path("/fake"))
    service.checker = mock_checker  # Replace real checker with mock
    return service


class TestIntegrityServiceCheckGraph:
    """Test check_graph functionality."""

    def test_check_graph_valid(self, service_with_mocks, mock_checker):
        """Valid graph returns ValidationResult with valid=True."""
        # Mock checker to return valid result
        mock_checker.check_graph.return_value = KMValidationResult(
            triad="design",
            valid=True,
            error=None,
            error_count=0,
            file_path=Path(".claude/graphs/design_graph.json")
        )

        result = service_with_mocks.check_graph("design")

        assert isinstance(result, ValidationResult)
        assert result.triad == "design"
        assert result.valid is True
        assert result.error is None
        assert result.error_count == 0
        mock_checker.check_graph.assert_called_once_with("design")

    def test_check_graph_invalid_with_errors(self, service_with_mocks, mock_checker):
        """Invalid graph returns ValidationResult with error details."""
        # Mock checker to return invalid result
        mock_checker.check_graph.return_value = KMValidationResult(
            triad="implementation",
            valid=False,
            error="Missing required field 'label'",
            error_field="nodes[0].label",
            error_count=1,
            file_path=Path(".claude/graphs/implementation_graph.json")
        )

        result = service_with_mocks.check_graph("implementation")

        assert isinstance(result, ValidationResult)
        assert result.triad == "implementation"
        assert result.valid is False
        assert result.error == "Missing required field 'label'"
        assert result.error_field == "nodes[0].label"
        assert result.error_count == 1


class TestIntegrityServiceCheckAllGraphs:
    """Test check_all_graphs functionality."""

    def test_check_all_graphs_returns_all_results(self, service_with_mocks, mock_checker):
        """check_all_graphs returns ValidationResult for each graph."""
        # Mock checker to return multiple results
        mock_checker.check_all_graphs.return_value = [
            KMValidationResult(
                triad="design",
                valid=True,
                error=None,
                error_count=0,
                file_path=Path(".claude/graphs/design_graph.json")
            ),
            KMValidationResult(
                triad="implementation",
                valid=False,
                error="Invalid edge",
                error_count=1,
                file_path=Path(".claude/graphs/implementation_graph.json")
            ),
        ]

        results = service_with_mocks.check_all_graphs()

        assert len(results) == 2
        assert all(isinstance(r, ValidationResult) for r in results)
        assert results[0].triad == "design"
        assert results[0].valid is True
        assert results[1].triad == "implementation"
        assert results[1].valid is False
        mock_checker.check_all_graphs.assert_called_once()

    def test_check_all_graphs_empty(self, service_with_mocks, mock_checker):
        """check_all_graphs returns empty list when no graphs exist."""
        mock_checker.check_all_graphs.return_value = []

        results = service_with_mocks.check_all_graphs()

        assert results == []


class TestIntegrityServiceRepairGraph:
    """Test repair_graph functionality."""

    def test_repair_graph_creates_backup_by_default(self, service_with_mocks, mock_checker, in_memory_repo):
        """repair_graph creates backup by default before repair."""
        # Mock successful repair
        mock_checker.repair_graph.return_value = KMRepairResult(
            triad="design",
            success=True,
            message="Successfully repaired graph",
            actions_taken="Removed 2 invalid edges",
            backup_created=False  # IntegrityChecker doesn't track our backup
        )

        result = service_with_mocks.repair_graph("design", create_backup=True)

        assert isinstance(result, RepairResult)
        assert result.triad == "design"
        assert result.success is True
        assert result.backup_created is True  # Our service created backup
        assert result.backup_path is not None
        assert "design" in str(result.backup_path)

        # Verify backup was created in repo
        backups = in_memory_repo.list_backups("design")
        assert len(backups) == 1

    def test_repair_graph_skip_backup_when_requested(self, service_with_mocks, mock_checker, in_memory_repo):
        """repair_graph skips backup when create_backup=False."""
        # Mock successful repair
        mock_checker.repair_graph.return_value = KMRepairResult(
            triad="design",
            success=True,
            message="Successfully repaired graph",
            actions_taken="Removed 2 invalid edges",
            backup_created=False
        )

        result = service_with_mocks.repair_graph("design", create_backup=False)

        assert result.backup_created is False
        assert result.backup_path is None

        # Verify no backup in repo
        backups = in_memory_repo.list_backups("design")
        assert len(backups) == 0

    def test_repair_graph_failure_propagates(self, service_with_mocks, mock_checker):
        """repair_graph returns failure result when repair fails."""
        # Mock failed repair
        mock_checker.repair_graph.return_value = KMRepairResult(
            triad="implementation",
            success=False,
            message="Cannot repair: Missing required field 'id'",
            actions_taken=None,
            backup_created=False
        )

        result = service_with_mocks.repair_graph("implementation")

        assert result.success is False
        assert "Cannot repair" in result.message
        assert result.actions_taken is None

    def test_repair_graph_includes_actions_taken(self, service_with_mocks, mock_checker):
        """repair_graph includes actions_taken from IntegrityChecker."""
        # Mock repair with actions
        mock_checker.repair_graph.return_value = KMRepairResult(
            triad="design",
            success=True,
            message="Successfully repaired graph",
            actions_taken="Removed 3 invalid edges; Removed 1 node with invalid confidence",
            backup_created=False
        )

        result = service_with_mocks.repair_graph("design", create_backup=False)

        assert result.success is True
        assert result.actions_taken == "Removed 3 invalid edges; Removed 1 node with invalid confidence"
