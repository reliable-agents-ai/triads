"""Tests for workflow tools domain models."""

import pytest
from dataclasses import asdict
from datetime import datetime

from triads.tools.workflow.domain import WorkflowInstance, WorkflowStatus, TriadCompletion


class TestWorkflowStatus:
    """Tests for WorkflowStatus enum."""

    def test_workflow_status_has_expected_values(self):
        """WorkflowStatus enum has all expected status values."""
        assert WorkflowStatus.IN_PROGRESS.value == "in_progress"
        assert WorkflowStatus.COMPLETED.value == "completed"
        assert WorkflowStatus.ABANDONED.value == "abandoned"

    def test_workflow_status_can_be_compared(self):
        """WorkflowStatus values can be compared."""
        assert WorkflowStatus.IN_PROGRESS == WorkflowStatus.IN_PROGRESS
        assert WorkflowStatus.IN_PROGRESS != WorkflowStatus.COMPLETED


class TestTriadCompletion:
    """Tests for TriadCompletion dataclass."""

    def test_triad_completion_creation(self):
        """TriadCompletion can be created with required fields."""
        completion = TriadCompletion(
            triad_id="implementation",
            completed_at="2025-10-23T10:00:00Z",
            duration_minutes=45.5
        )

        assert completion.triad_id == "implementation"
        assert completion.completed_at == "2025-10-23T10:00:00Z"
        assert completion.duration_minutes == 45.5

    def test_triad_completion_to_dict(self):
        """TriadCompletion can be converted to dictionary."""
        completion = TriadCompletion(
            triad_id="design",
            completed_at="2025-10-23T09:00:00Z",
            duration_minutes=30.0
        )

        data = asdict(completion)
        assert data["triad_id"] == "design"
        assert data["completed_at"] == "2025-10-23T09:00:00Z"
        assert data["duration_minutes"] == 30.0


class TestWorkflowInstance:
    """Tests for WorkflowInstance dataclass."""

    def test_workflow_instance_creation(self):
        """WorkflowInstance can be created with required fields."""
        instance = WorkflowInstance(
            instance_id="feature-oauth2-20251023-100523",
            workflow_type="software-development",
            status=WorkflowStatus.IN_PROGRESS,
            title="OAuth2 Integration"
        )

        assert instance.instance_id == "feature-oauth2-20251023-100523"
        assert instance.workflow_type == "software-development"
        assert instance.status == WorkflowStatus.IN_PROGRESS
        assert instance.title == "OAuth2 Integration"

    def test_workflow_instance_with_current_triad(self):
        """WorkflowInstance tracks current triad."""
        instance = WorkflowInstance(
            instance_id="test-instance",
            workflow_type="software-development",
            status=WorkflowStatus.IN_PROGRESS,
            title="Test Workflow",
            current_triad="implementation"
        )

        assert instance.current_triad == "implementation"

    def test_workflow_instance_defaults_current_triad_to_none(self):
        """WorkflowInstance defaults current_triad to None."""
        instance = WorkflowInstance(
            instance_id="test-instance",
            workflow_type="software-development",
            status=WorkflowStatus.IN_PROGRESS,
            title="Test Workflow"
        )

        assert instance.current_triad is None

    def test_workflow_instance_with_completed_triads(self):
        """WorkflowInstance tracks completed triads."""
        completed = [
            TriadCompletion(
                triad_id="idea-validation",
                completed_at="2025-10-23T09:00:00Z",
                duration_minutes=30.0
            ),
            TriadCompletion(
                triad_id="design",
                completed_at="2025-10-23T10:00:00Z",
                duration_minutes=45.0
            )
        ]

        instance = WorkflowInstance(
            instance_id="test-instance",
            workflow_type="software-development",
            status=WorkflowStatus.IN_PROGRESS,
            title="Test Workflow",
            completed_triads=completed
        )

        assert len(instance.completed_triads) == 2
        assert instance.completed_triads[0].triad_id == "idea-validation"
        assert instance.completed_triads[1].triad_id == "design"

    def test_workflow_instance_defaults_completed_triads_to_empty_list(self):
        """WorkflowInstance defaults completed_triads to empty list."""
        instance = WorkflowInstance(
            instance_id="test-instance",
            workflow_type="software-development",
            status=WorkflowStatus.IN_PROGRESS,
            title="Test Workflow"
        )

        assert instance.completed_triads == []

    def test_workflow_instance_with_timestamps(self):
        """WorkflowInstance tracks start timestamp."""
        instance = WorkflowInstance(
            instance_id="test-instance",
            workflow_type="software-development",
            status=WorkflowStatus.COMPLETED,
            title="Test Workflow",
            started_at="2025-10-23T08:00:00Z"
        )

        assert instance.started_at == "2025-10-23T08:00:00Z"

    def test_workflow_instance_to_dict(self):
        """WorkflowInstance can be converted to dictionary."""
        instance = WorkflowInstance(
            instance_id="test-instance",
            workflow_type="software-development",
            status=WorkflowStatus.IN_PROGRESS,
            title="Test Workflow",
            current_triad="implementation"
        )

        data = asdict(instance)
        assert data["instance_id"] == "test-instance"
        assert data["status"] == WorkflowStatus.IN_PROGRESS
        assert data["current_triad"] == "implementation"
