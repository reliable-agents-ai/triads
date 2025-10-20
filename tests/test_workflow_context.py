"""Tests for workflow context utilities."""

import json
import os
import tempfile
from pathlib import Path

import pytest

from triads.utils.workflow_context import (
    get_current_instance_id,
    set_current_instance,
    auto_create_instance_if_needed,
    get_or_create_instance,
)
from triads.workflow_enforcement.instance_manager import WorkflowInstanceManager


@pytest.fixture
def temp_workspace():
    """Create temporary workspace with .claude/workflows structure."""
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        workflows_dir = workspace / ".claude" / "workflows"
        workflows_dir.mkdir(parents=True)
        (workflows_dir / "instances").mkdir()
        (workflows_dir / "completed").mkdir()
        (workflows_dir / "abandoned").mkdir()
        yield workspace


def test_get_current_instance_id_none(temp_workspace):
    """Test getting current instance when none exists."""
    instance_id = get_current_instance_id(str(temp_workspace))
    assert instance_id is None


def test_get_current_instance_id_from_env(temp_workspace):
    """Test getting current instance from environment variable."""
    os.environ["TRIADS_WORKFLOW_INSTANCE"] = "test-instance-123"
    try:
        instance_id = get_current_instance_id(str(temp_workspace))
        assert instance_id == "test-instance-123"
    finally:
        del os.environ["TRIADS_WORKFLOW_INSTANCE"]


def test_set_and_get_current_instance(temp_workspace):
    """Test setting and getting current instance."""
    # Create an instance first
    manager = WorkflowInstanceManager(
        base_dir=temp_workspace / ".claude" / "workflows"
    )
    created_id = manager.create_instance(
        workflow_type="software-development",
        title="Test Workflow",
        user="test@example.com"
    )

    # Set it as current
    set_current_instance(created_id, str(temp_workspace))

    # Verify we can get it back
    instance_id = get_current_instance_id(str(temp_workspace))
    assert instance_id == created_id


def test_get_current_instance_from_file(temp_workspace):
    """Test reading current instance from file."""
    # Create an instance
    manager = WorkflowInstanceManager(
        base_dir=temp_workspace / ".claude" / "workflows"
    )
    created_id = manager.create_instance(
        workflow_type="software-development",
        title="Test Workflow",
        user="test@example.com"
    )

    # Manually write current instance file
    current_file = temp_workspace / ".claude" / "workflows" / "current_instance.json"
    with open(current_file, "w") as f:
        json.dump({"instance_id": created_id}, f)

    # Verify we can read it
    instance_id = get_current_instance_id(str(temp_workspace))
    assert instance_id == created_id


def test_get_current_instance_invalid_file_cleared(temp_workspace):
    """Test that invalid current instance file is cleared."""
    # Write current instance file with non-existent instance
    current_file = temp_workspace / ".claude" / "workflows" / "current_instance.json"
    with open(current_file, "w") as f:
        json.dump({"instance_id": "nonexistent-instance"}, f)

    # Verify file exists
    assert current_file.exists()

    # Get current instance (should clear file since instance doesn't exist)
    instance_id = get_current_instance_id(str(temp_workspace))
    assert instance_id is None
    assert not current_file.exists()


def test_get_most_recent_instance(temp_workspace):
    """Test getting most recent instance when no current set."""
    manager = WorkflowInstanceManager(
        base_dir=temp_workspace / ".claude" / "workflows"
    )

    # Create two instances
    id1 = manager.create_instance(
        workflow_type="software-development",
        title="First Workflow",
        user="test@example.com"
    )

    # Wait a moment to ensure different timestamps
    import time
    time.sleep(0.1)

    id2 = manager.create_instance(
        workflow_type="software-development",
        title="Second Workflow",
        user="test@example.com"
    )

    # Get current (should return most recent)
    instance_id = get_current_instance_id(str(temp_workspace))
    assert instance_id == id2


def test_auto_create_instance_if_needed_creates(temp_workspace):
    """Test auto-creating instance when none exists."""
    instance_id = auto_create_instance_if_needed(
        title="Auto Created",
        user="test@example.com",
        cwd=str(temp_workspace)
    )

    assert instance_id is not None

    # Verify instance was created
    manager = WorkflowInstanceManager(
        base_dir=temp_workspace / ".claude" / "workflows"
    )
    instance = manager.load_instance(instance_id)
    assert instance.metadata["title"] == "Auto Created"
    assert instance.metadata["auto_created"] is True


def test_auto_create_instance_if_needed_returns_existing(temp_workspace):
    """Test that auto-create returns existing instance if one exists."""
    # Create an instance
    manager = WorkflowInstanceManager(
        base_dir=temp_workspace / ".claude" / "workflows"
    )
    existing_id = manager.create_instance(
        workflow_type="software-development",
        title="Existing Workflow",
        user="test@example.com"
    )
    set_current_instance(existing_id, str(temp_workspace))

    # Auto-create should return existing
    instance_id = auto_create_instance_if_needed(cwd=str(temp_workspace))
    assert instance_id == existing_id


def test_get_or_create_instance(temp_workspace):
    """Test convenience function."""
    # First call creates
    id1 = get_or_create_instance(
        title="Test Workflow",
        user="test@example.com",
        cwd=str(temp_workspace)
    )
    assert id1 is not None

    # Second call returns same
    id2 = get_or_create_instance(cwd=str(temp_workspace))
    assert id2 == id1


def test_env_var_priority_over_file(temp_workspace):
    """Test that environment variable takes priority over file."""
    # Create an instance and set as current in file
    manager = WorkflowInstanceManager(
        base_dir=temp_workspace / ".claude" / "workflows"
    )
    file_id = manager.create_instance(
        workflow_type="software-development",
        title="File Instance",
        user="test@example.com"
    )
    set_current_instance(file_id, str(temp_workspace))

    # Set different instance in env var
    os.environ["TRIADS_WORKFLOW_INSTANCE"] = "env-instance-123"
    try:
        instance_id = get_current_instance_id(str(temp_workspace))
        assert instance_id == "env-instance-123"
    finally:
        del os.environ["TRIADS_WORKFLOW_INSTANCE"]


# ============================================================================
# Security Tests (Rule 1: Write tests FIRST)
# ============================================================================

def test_validate_instance_id():
    """Test instance ID validation function."""
    from triads.utils.workflow_context import _validate_instance_id

    # Valid IDs
    assert _validate_instance_id("my-workflow-123")
    assert _validate_instance_id("workflow_name")
    assert _validate_instance_id("test-123_abc")
    assert _validate_instance_id("a" * 255)  # Max length

    # Invalid IDs - path traversal
    assert not _validate_instance_id("../../../etc/passwd")
    assert not _validate_instance_id("my/workflow")
    assert not _validate_instance_id("my\\workflow")
    assert not _validate_instance_id("..test")
    assert not _validate_instance_id("test..")

    # Invalid IDs - special characters
    assert not _validate_instance_id("my workflow")  # space
    assert not _validate_instance_id("my@workflow")  # @
    assert not _validate_instance_id("<script>")     # HTML
    assert not _validate_instance_id("my:workflow")  # colon

    # Invalid IDs - edge cases
    assert not _validate_instance_id("")             # empty
    assert not _validate_instance_id(None)           # None
    assert not _validate_instance_id("a" * 300)      # too long
    assert not _validate_instance_id(123)            # not a string


def test_set_current_instance_path_traversal(temp_workspace):
    """Test that path traversal in instance_id is blocked."""
    with pytest.raises(ValueError, match="Invalid instance_id"):
        set_current_instance("../../../etc/passwd", str(temp_workspace))


def test_set_current_instance_invalid_chars(temp_workspace):
    """Test that special characters are rejected."""
    invalid_ids = [
        "my/workflow",   # Forward slash
        "my\\workflow",  # Backslash
        "my workflow",   # Space
        "<script>",      # HTML
        "test:123",      # Colon
    ]
    for invalid_id in invalid_ids:
        with pytest.raises(ValueError, match="Invalid instance_id"):
            set_current_instance(invalid_id, str(temp_workspace))


def test_get_current_instance_env_var_path_traversal(temp_workspace):
    """Test that env var with path traversal is rejected."""
    os.environ["TRIADS_WORKFLOW_INSTANCE"] = "../../../etc/passwd"
    try:
        instance_id = get_current_instance_id(str(temp_workspace))
        # Should return None (rejected and fell through to other methods)
        assert instance_id != "../../../etc/passwd"
        assert instance_id is None  # No other instances exist
    finally:
        del os.environ["TRIADS_WORKFLOW_INSTANCE"]


def test_get_current_instance_env_var_invalid_chars(temp_workspace):
    """Test that env var with invalid characters is rejected."""
    test_cases = [
        "my/workflow",
        "my\\workflow",
        "my workflow",
        "<script>alert('xss')</script>",
    ]

    for invalid_id in test_cases:
        os.environ["TRIADS_WORKFLOW_INSTANCE"] = invalid_id
        try:
            instance_id = get_current_instance_id(str(temp_workspace))
            assert instance_id != invalid_id
            assert instance_id is None
        finally:
            del os.environ["TRIADS_WORKFLOW_INSTANCE"]


# ============================================================================
# Concurrency Tests (Rule 1: Write tests FIRST)
# ============================================================================

def test_concurrent_set_current_instance(temp_workspace):
    """Test that concurrent writes don't corrupt file."""
    import threading

    # Create some instances first
    manager = WorkflowInstanceManager(
        base_dir=temp_workspace / ".claude" / "workflows"
    )
    instance_ids = [
        manager.create_instance(
            workflow_type="software-development",
            title=f"Test {i}",
            user="test@example.com"
        )
        for i in range(5)
    ]

    errors = []

    def writer(instance_id):
        try:
            for _ in range(20):
                set_current_instance(instance_id, str(temp_workspace))
        except Exception as e:
            errors.append(e)

    threads = [
        threading.Thread(target=writer, args=(iid,))
        for iid in instance_ids
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # No errors should occur
    assert len(errors) == 0

    # Verify file is not corrupt - should be valid JSON with valid instance_id
    instance_id = get_current_instance_id(str(temp_workspace))
    assert instance_id is not None
    assert instance_id in instance_ids


def test_concurrent_read_write_current_instance(temp_workspace):
    """Test concurrent readers and writers don't cause corruption."""
    import threading
    import time

    # Create instances
    manager = WorkflowInstanceManager(
        base_dir=temp_workspace / ".claude" / "workflows"
    )
    instance_ids = [
        manager.create_instance(
            workflow_type="software-development",
            title=f"Test {i}",
            user="test@example.com"
        )
        for i in range(3)
    ]

    errors = []
    read_results = []

    def writer(instance_id):
        try:
            for _ in range(10):
                set_current_instance(instance_id, str(temp_workspace))
                time.sleep(0.001)
        except Exception as e:
            errors.append(("writer", e))

    def reader():
        try:
            for _ in range(30):
                result = get_current_instance_id(str(temp_workspace))
                if result is not None:
                    read_results.append(result)
                time.sleep(0.001)
        except Exception as e:
            errors.append(("reader", e))

    # Start writers and readers
    threads = []
    for iid in instance_ids:
        threads.append(threading.Thread(target=writer, args=(iid,)))
    for _ in range(3):
        threads.append(threading.Thread(target=reader))

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # No errors should occur
    assert len(errors) == 0, f"Errors occurred: {errors}"

    # All reads should return valid instance IDs
    assert len(read_results) > 0
    for result in read_results:
        assert result in instance_ids
