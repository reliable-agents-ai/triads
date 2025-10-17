"""Tests for workflow instance manager.

Tests cover:
- Instance CRUD operations
- Instance lifecycle (create, update, complete, abandon)
- Concurrent-safe operations (file locking)
- Deviation tracking
- Triad completion tracking
- Significance metrics recording
"""

import json
import pytest
import time
from pathlib import Path
from datetime import datetime
from triads.workflow_enforcement.instance_manager import (
    WorkflowInstanceManager,
    WorkflowInstance,
    InstanceNotFoundError,
    InstanceValidationError,
)


@pytest.fixture
def temp_workflow_dir(tmp_path):
    """Create temporary .claude/workflows directory for testing."""
    workflows_dir = tmp_path / ".claude" / "workflows"
    workflows_dir.mkdir(parents=True)
    (workflows_dir / "instances").mkdir()
    (workflows_dir / "completed").mkdir()
    (workflows_dir / "abandoned").mkdir()
    return workflows_dir


@pytest.fixture
def instance_manager(temp_workflow_dir):
    """Create instance manager with test directory."""
    return WorkflowInstanceManager(base_dir=temp_workflow_dir)


class TestInstanceCreation:
    """Test workflow instance creation."""

    def test_create_instance_basic(self, instance_manager):
        """Test creating a basic workflow instance."""
        instance_id = instance_manager.create_instance(
            workflow_type="software-development",
            title="OAuth2 Integration",
            user="test@example.com"
        )

        # Verify instance ID format (slug-timestamp)
        assert instance_id.startswith("oauth2-integration-")
        assert len(instance_id.split("-")) >= 3  # slug + timestamp parts

        # Verify instance file created
        instance = instance_manager.load_instance(instance_id)
        assert instance.instance_id == instance_id
        assert instance.workflow_type == "software-development"
        assert instance.metadata["title"] == "OAuth2 Integration"
        assert instance.metadata["started_by"] == "test@example.com"
        assert instance.metadata["status"] == "in_progress"

    def test_create_instance_generates_unique_ids(self, instance_manager):
        """Test that concurrent instances get unique IDs."""
        id1 = instance_manager.create_instance("test", "Test", "user@example.com")
        time.sleep(0.01)  # Small delay to ensure different timestamp
        id2 = instance_manager.create_instance("test", "Test", "user@example.com")

        assert id1 != id2

    def test_create_instance_slug_generation(self, instance_manager):
        """Test slug generation from titles."""
        # Simple title
        id1 = instance_manager.create_instance("test", "Simple Title", "user@example.com")
        assert "simple-title-" in id1

        # Title with special characters
        id2 = instance_manager.create_instance("test", "OAuth2 & JWT Integration!", "user@example.com")
        assert "oauth2-jwt-integration-" in id2

        # Title with multiple spaces
        id3 = instance_manager.create_instance("test", "Too   Many    Spaces", "user@example.com")
        assert "too-many-spaces-" in id3

    def test_create_instance_invalid_workflow_type(self, instance_manager):
        """Test creating instance with invalid workflow type."""
        with pytest.raises(InstanceValidationError, match="Invalid workflow_type"):
            instance_manager.create_instance("", "Test", "user@example.com")

    def test_create_instance_invalid_title(self, instance_manager):
        """Test creating instance with invalid title."""
        with pytest.raises(InstanceValidationError, match="Invalid title"):
            instance_manager.create_instance("test", "", "user@example.com")

    def test_create_instance_invalid_user(self, instance_manager):
        """Test creating instance with invalid user."""
        with pytest.raises(InstanceValidationError, match="Invalid user"):
            instance_manager.create_instance("test", "Test", "")


class TestInstanceLoading:
    """Test loading workflow instances."""

    def test_load_existing_instance(self, instance_manager):
        """Test loading an existing instance."""
        # Create instance
        instance_id = instance_manager.create_instance("test", "Test", "user@example.com")

        # Load instance
        instance = instance_manager.load_instance(instance_id)

        assert instance.instance_id == instance_id
        assert instance.workflow_type == "test"
        assert instance.metadata["title"] == "Test"

    def test_load_nonexistent_instance(self, instance_manager):
        """Test loading nonexistent instance raises error."""
        with pytest.raises(InstanceNotFoundError, match="Instance not found"):
            instance_manager.load_instance("nonexistent-instance-123")

    def test_load_instance_invalid_json(self, instance_manager, temp_workflow_dir):
        """Test loading instance with corrupted JSON."""
        # Create corrupted file
        instance_file = temp_workflow_dir / "instances" / "corrupted-123.json"
        instance_file.write_text("{ invalid json }")

        with pytest.raises(InstanceValidationError, match="Invalid JSON"):
            instance_manager.load_instance("corrupted-123")


class TestInstanceUpdates:
    """Test updating workflow instances."""

    def test_update_instance_metadata(self, instance_manager):
        """Test updating instance metadata."""
        instance_id = instance_manager.create_instance("test", "Test", "user@example.com")

        # Update metadata
        instance_manager.update_instance(instance_id, {
            "metadata": {"custom_field": "custom_value"}
        })

        # Verify update
        instance = instance_manager.load_instance(instance_id)
        assert instance.metadata["custom_field"] == "custom_value"
        # Original fields should still exist
        assert instance.metadata["title"] == "Test"

    def test_update_instance_metrics(self, instance_manager):
        """Test updating significance metrics."""
        instance_id = instance_manager.create_instance("test", "Test", "user@example.com")

        # Update metrics
        instance_manager.update_instance(instance_id, {
            "significance_metrics": {
                "content_created": {"type": "code", "quantity": 257, "units": "lines"},
                "complexity": "substantial"
            }
        })

        # Verify update
        instance = instance_manager.load_instance(instance_id)
        assert instance.significance_metrics["content_created"]["quantity"] == 257
        assert instance.significance_metrics["complexity"] == "substantial"


class TestTriadCompletion:
    """Test triad completion tracking."""

    def test_mark_triad_completed(self, instance_manager):
        """Test marking a triad as completed."""
        instance_id = instance_manager.create_instance("test", "Test", "user@example.com")

        # Mark triad completed
        instance_manager.mark_triad_completed(instance_id, "idea-validation")

        # Verify completion recorded
        instance = instance_manager.load_instance(instance_id)
        assert len(instance.workflow_progress["completed_triads"]) == 1

        completed = instance.workflow_progress["completed_triads"][0]
        assert completed["triad_id"] == "idea-validation"
        assert "completed_at" in completed
        assert "duration_minutes" in completed

        # Current triad should be updated
        assert instance.workflow_progress["current_triad"] == "idea-validation"

    def test_mark_multiple_triads_completed(self, instance_manager):
        """Test marking multiple triads as completed."""
        instance_id = instance_manager.create_instance("test", "Test", "user@example.com")

        # Mark triads completed
        instance_manager.mark_triad_completed(instance_id, "idea-validation")
        time.sleep(0.01)
        instance_manager.mark_triad_completed(instance_id, "design")
        time.sleep(0.01)
        instance_manager.mark_triad_completed(instance_id, "implementation")

        # Verify all completions recorded
        instance = instance_manager.load_instance(instance_id)
        completed_ids = [t["triad_id"] for t in instance.workflow_progress["completed_triads"]]
        assert completed_ids == ["idea-validation", "design", "implementation"]

        # Current triad should be latest
        assert instance.workflow_progress["current_triad"] == "implementation"

    def test_mark_triad_completed_duplicate(self, instance_manager):
        """Test marking same triad completed twice (should not duplicate)."""
        instance_id = instance_manager.create_instance("test", "Test", "user@example.com")

        # Mark triad completed twice
        instance_manager.mark_triad_completed(instance_id, "design")
        instance_manager.mark_triad_completed(instance_id, "design")

        # Should only appear once
        instance = instance_manager.load_instance(instance_id)
        completed_ids = [t["triad_id"] for t in instance.workflow_progress["completed_triads"]]
        assert completed_ids.count("design") == 1


class TestSkippedTriads:
    """Test skipped triad tracking."""

    def test_mark_triad_skipped(self, instance_manager):
        """Test marking a triad as skipped."""
        instance_id = instance_manager.create_instance("test", "Test", "user@example.com")

        # Skip triad
        instance_manager.mark_triad_skipped(instance_id, "design", "Design in Figma")

        # Verify skip recorded
        instance = instance_manager.load_instance(instance_id)
        assert len(instance.workflow_progress["skipped_triads"]) == 1

        skipped = instance.workflow_progress["skipped_triads"][0]
        assert skipped["triad_id"] == "design"
        assert skipped["reason"] == "Design in Figma"
        assert "skipped_at" in skipped


class TestDeviations:
    """Test deviation tracking."""

    def test_add_deviation_skip_forward(self, instance_manager):
        """Test recording skip forward deviation."""
        instance_id = instance_manager.create_instance("test", "Test", "user@example.com")

        # Record deviation
        instance_manager.add_deviation(instance_id, {
            "type": "skip_forward",
            "from_triad": "idea-validation",
            "to_triad": "implementation",
            "skipped": ["design"],
            "reason": "Design completed in Figma",
            "user": "user@example.com"
        })

        # Verify deviation recorded
        instance = instance_manager.load_instance(instance_id)
        assert len(instance.workflow_deviations) == 1

        deviation = instance.workflow_deviations[0]
        assert deviation["type"] == "skip_forward"
        assert deviation["skipped"] == ["design"]
        assert "timestamp" in deviation

    def test_add_multiple_deviations(self, instance_manager):
        """Test recording multiple deviations."""
        instance_id = instance_manager.create_instance("test", "Test", "user@example.com")

        # Record multiple deviations
        instance_manager.add_deviation(instance_id, {
            "type": "skip_forward",
            "reason": "Reason 1"
        })

        instance_manager.add_deviation(instance_id, {
            "type": "skip_backward",
            "reason": "Reason 2"
        })

        # Verify both recorded
        instance = instance_manager.load_instance(instance_id)
        assert len(instance.workflow_deviations) == 2


class TestInstanceLifecycle:
    """Test instance lifecycle transitions."""

    def test_complete_instance(self, instance_manager, temp_workflow_dir):
        """Test completing an instance moves it to completed directory."""
        instance_id = instance_manager.create_instance("test", "Test", "user@example.com")

        # Complete instance
        instance_manager.complete_instance(instance_id)

        # Verify moved to completed directory
        completed_file = temp_workflow_dir / "completed" / f"{instance_id}.json"
        assert completed_file.exists()

        # Original file should be gone
        instance_file = temp_workflow_dir / "instances" / f"{instance_id}.json"
        assert not instance_file.exists()

        # Load from completed
        instance = instance_manager.load_instance(instance_id)
        assert instance.metadata["status"] == "completed"
        assert "completed_at" in instance.metadata

    def test_abandon_instance(self, instance_manager, temp_workflow_dir):
        """Test abandoning an instance moves it to abandoned directory."""
        instance_id = instance_manager.create_instance("test", "Test", "user@example.com")

        # Abandon instance
        instance_manager.abandon_instance(instance_id, "No longer needed")

        # Verify moved to abandoned directory
        abandoned_file = temp_workflow_dir / "abandoned" / f"{instance_id}.json"
        assert abandoned_file.exists()

        # Original file should be gone
        instance_file = temp_workflow_dir / "instances" / f"{instance_id}.json"
        assert not instance_file.exists()

        # Load from abandoned
        instance = instance_manager.load_instance(instance_id)
        assert instance.metadata["status"] == "abandoned"
        assert instance.metadata["abandon_reason"] == "No longer needed"
        assert "abandoned_at" in instance.metadata


class TestInstanceListing:
    """Test listing instances."""

    def test_list_all_instances(self, instance_manager):
        """Test listing all instances."""
        # Create multiple instances
        id1 = instance_manager.create_instance("test", "Test 1", "user@example.com")
        id2 = instance_manager.create_instance("test", "Test 2", "user@example.com")
        id3 = instance_manager.create_instance("test", "Test 3", "user@example.com")

        # List all
        instances = instance_manager.list_instances()
        assert len(instances) >= 3
        instance_ids = [i["instance_id"] for i in instances]
        assert id1 in instance_ids
        assert id2 in instance_ids
        assert id3 in instance_ids

    def test_list_instances_by_status(self, instance_manager):
        """Test filtering instances by status."""
        # Create instances with different statuses
        id1 = instance_manager.create_instance("test", "In Progress", "user@example.com")
        id2 = instance_manager.create_instance("test", "To Complete", "user@example.com")
        instance_manager.complete_instance(id2)
        id3 = instance_manager.create_instance("test", "To Abandon", "user@example.com")
        instance_manager.abandon_instance(id3, "Test")

        # List in_progress
        in_progress = instance_manager.list_instances(status="in_progress")
        assert len(in_progress) >= 1
        assert any(i["instance_id"] == id1 for i in in_progress)
        assert not any(i["instance_id"] == id2 for i in in_progress)

        # List completed
        completed = instance_manager.list_instances(status="completed")
        assert any(i["instance_id"] == id2 for i in completed)

        # List abandoned
        abandoned = instance_manager.list_instances(status="abandoned")
        assert any(i["instance_id"] == id3 for i in abandoned)

    def test_list_instances_empty(self, instance_manager):
        """Test listing instances when none exist."""
        instances = instance_manager.list_instances()
        assert instances == []


class TestConcurrentSafety:
    """Test concurrent-safe operations."""

    def test_concurrent_instance_creation(self, instance_manager):
        """Test that concurrent creates don't collide."""
        # This is a basic test - real concurrency testing would use threads
        ids = []
        for i in range(5):
            instance_id = instance_manager.create_instance(
                "test",
                f"Test {i}",
                "user@example.com"
            )
            ids.append(instance_id)

        # All IDs should be unique
        assert len(ids) == len(set(ids))

        # All instances should be loadable
        for instance_id in ids:
            instance = instance_manager.load_instance(instance_id)
            assert instance.instance_id == instance_id

    def test_atomic_updates(self, instance_manager):
        """Test that updates are atomic."""
        instance_id = instance_manager.create_instance("test", "Test", "user@example.com")

        # Perform multiple updates
        for i in range(5):
            instance_manager.update_instance(instance_id, {
                "metadata": {"counter": i}
            })

        # Final state should be consistent
        instance = instance_manager.load_instance(instance_id)
        assert instance.metadata["counter"] == 4


class TestSecurityValidation:
    """Test security validation."""

    def test_path_traversal_prevention_in_instance_id(self, instance_manager):
        """Test that instance IDs with path traversal are rejected."""
        # Try to create instance with dangerous characters
        with pytest.raises(InstanceNotFoundError):
            # load_instance should reject path traversal attempts
            instance_manager.load_instance("../../etc/passwd")

    def test_slug_sanitization(self, instance_manager):
        """Test that dangerous characters are sanitized in slugs."""
        # Create instance with dangerous title
        instance_id = instance_manager.create_instance(
            "test",
            "../../../etc/passwd",
            "user@example.com"
        )

        # Slug should be sanitized
        assert "../" not in instance_id
        assert "etc-passwd-" in instance_id
