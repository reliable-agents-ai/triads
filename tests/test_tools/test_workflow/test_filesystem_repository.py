"""Tests for FileSystemWorkflowRepository.

Tests the filesystem-based workflow repository implementation.
"""

import json
import pytest
from pathlib import Path
from triads.tools.workflow.repository import (
    FileSystemWorkflowRepository,
    WorkflowRepositoryError,
)
from triads.tools.workflow.domain import WorkflowStatus


@pytest.fixture
def temp_workflow_dir(tmp_path):
    """Create temporary workflow directory structure."""
    base_dir = tmp_path / "workflows"
    instances_dir = base_dir / "instances"
    completed_dir = base_dir / "completed"
    abandoned_dir = base_dir / "abandoned"

    instances_dir.mkdir(parents=True)
    completed_dir.mkdir(parents=True)
    abandoned_dir.mkdir(parents=True)

    # Create sample instance files
    instance_data = {
        "instance_id": "test-instance-001",
        "workflow_type": "software-development",
        "metadata": {
            "title": "Test Feature",
            "started_by": "test@example.com",
            "started_at": "2025-10-23T10:00:00Z",
            "status": "in_progress"
        },
        "workflow_progress": {
            "current_triad": "implementation",
            "completed_triads": [
                {
                    "triad_id": "design",
                    "completed_at": "2025-10-23T09:00:00Z",
                    "duration_minutes": 30.0
                }
            ],
            "skipped_triads": []
        },
        "workflow_deviations": [
            {
                "type": "skip_forward",
                "from_triad": "idea-validation",
                "to_triad": "design",
                "reason": "Already validated",
                "timestamp": "2025-10-23T08:30:00Z",
                "user": "test@example.com",
                "skipped": ["idea-validation"]
            }
        ],
        "significance_metrics": {
            "lines_added": 100,
            "lines_deleted": 20
        }
    }

    # Write instance file
    with open(instances_dir / "test-instance-001.json", "w") as f:
        json.dump(instance_data, f)

    # Create completed instance
    completed_data = {
        **instance_data,
        "instance_id": "test-completed-002",
        "metadata": {
            **instance_data["metadata"],
            "status": "completed",
            "completed_at": "2025-10-23T12:00:00Z"
        }
    }
    with open(completed_dir / "test-completed-002.json", "w") as f:
        json.dump(completed_data, f)

    return base_dir


class TestFileSystemWorkflowRepository:
    """Tests for FileSystemWorkflowRepository."""

    def test_list_workflows_returns_all_instances(self, temp_workflow_dir):
        """list_workflows returns all instances from all directories."""
        repo = FileSystemWorkflowRepository(base_dir=temp_workflow_dir)
        instances = repo.list_workflows()

        assert len(instances) == 2
        instance_ids = {inst.instance_id for inst in instances}
        assert "test-instance-001" in instance_ids
        assert "test-completed-002" in instance_ids

    def test_list_workflows_filters_by_status(self, temp_workflow_dir):
        """list_workflows filters by status correctly."""
        repo = FileSystemWorkflowRepository(base_dir=temp_workflow_dir)

        # Filter for in_progress
        in_progress = repo.list_workflows(status="in_progress")
        assert len(in_progress) == 1
        assert in_progress[0].instance_id == "test-instance-001"
        assert in_progress[0].status == WorkflowStatus.IN_PROGRESS

        # Filter for completed
        completed = repo.list_workflows(status="completed")
        assert len(completed) == 1
        assert completed[0].instance_id == "test-completed-002"
        assert completed[0].status == WorkflowStatus.COMPLETED

    def test_list_workflows_raises_error_for_invalid_status(self, temp_workflow_dir):
        """list_workflows raises error for invalid status."""
        repo = FileSystemWorkflowRepository(base_dir=temp_workflow_dir)

        with pytest.raises(WorkflowRepositoryError) as exc_info:
            repo.list_workflows(status="invalid_status")

        assert "Invalid status" in str(exc_info.value)

    def test_get_workflow_returns_instance_with_full_details(self, temp_workflow_dir):
        """get_workflow returns instance with all details populated."""
        repo = FileSystemWorkflowRepository(base_dir=temp_workflow_dir)
        instance = repo.get_workflow("test-instance-001")

        assert instance.instance_id == "test-instance-001"
        assert instance.workflow_type == "software-development"
        assert instance.title == "Test Feature"
        assert instance.status == WorkflowStatus.IN_PROGRESS
        assert instance.current_triad == "implementation"
        assert instance.started_by == "test@example.com"
        assert instance.started_at == "2025-10-23T10:00:00Z"

    def test_get_workflow_parses_completed_triads(self, temp_workflow_dir):
        """get_workflow correctly parses completed triads."""
        repo = FileSystemWorkflowRepository(base_dir=temp_workflow_dir)
        instance = repo.get_workflow("test-instance-001")

        assert len(instance.completed_triads) == 1
        completion = instance.completed_triads[0]
        assert completion.triad_id == "design"
        assert completion.completed_at == "2025-10-23T09:00:00Z"
        assert completion.duration_minutes == 30.0

    def test_get_workflow_parses_deviations(self, temp_workflow_dir):
        """get_workflow correctly parses workflow deviations."""
        repo = FileSystemWorkflowRepository(base_dir=temp_workflow_dir)
        instance = repo.get_workflow("test-instance-001")

        assert len(instance.workflow_deviations) == 1
        deviation = instance.workflow_deviations[0]
        assert deviation.deviation_type == "skip_forward"
        assert deviation.from_triad == "idea-validation"
        assert deviation.to_triad == "design"
        assert deviation.reason == "Already validated"
        assert "idea-validation" in deviation.skipped

    def test_get_workflow_parses_significance_metrics(self, temp_workflow_dir):
        """get_workflow correctly parses significance metrics."""
        repo = FileSystemWorkflowRepository(base_dir=temp_workflow_dir)
        instance = repo.get_workflow("test-instance-001")

        assert instance.significance_metrics["lines_added"] == 100
        assert instance.significance_metrics["lines_deleted"] == 20

    def test_get_workflow_raises_error_for_invalid_instance_id(self, temp_workflow_dir):
        """get_workflow raises error for path traversal attempt."""
        repo = FileSystemWorkflowRepository(base_dir=temp_workflow_dir)

        # Try path traversal
        with pytest.raises(WorkflowRepositoryError) as exc_info:
            repo.get_workflow("../../etc/passwd")

        assert "Invalid instance ID format" in str(exc_info.value)

    def test_get_workflow_raises_error_for_nonexistent_instance(self, temp_workflow_dir):
        """get_workflow raises error for nonexistent instance."""
        repo = FileSystemWorkflowRepository(base_dir=temp_workflow_dir)

        with pytest.raises(WorkflowRepositoryError) as exc_info:
            repo.get_workflow("nonexistent-instance")

        assert "not found" in str(exc_info.value)

    def test_repository_handles_missing_directories_gracefully(self, tmp_path):
        """Repository handles missing directories without crashing."""
        repo = FileSystemWorkflowRepository(base_dir=tmp_path / "nonexistent")

        # Should return empty list, not crash
        instances = repo.list_workflows()
        assert instances == []

    def test_repository_skips_malformed_json_files(self, temp_workflow_dir):
        """Repository skips malformed JSON files gracefully."""
        # Create malformed JSON file
        instances_dir = temp_workflow_dir / "instances"
        with open(instances_dir / "malformed.json", "w") as f:
            f.write("{invalid json")

        repo = FileSystemWorkflowRepository(base_dir=temp_workflow_dir)
        instances = repo.list_workflows()

        # Should still get the valid instances
        assert len(instances) == 2
        assert all(inst.instance_id != "malformed" for inst in instances)
