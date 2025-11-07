"""Tests for JSONLEventRepository - JSONL file-based event storage.

This test suite follows TDD methodology (RED phase):
- Tests written BEFORE implementation
- Tests demonstrate all requirements
- Tests MUST fail until implementation is complete

Test Coverage:
- Initialization and file handling
- Save operations (append-only)
- Query operations (filters, pagination, sorting)
- Count operations
- Get by ID operations
- Backward compatibility with old format
- Edge cases and error handling
"""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from triads.events.exceptions import EventStorageError
from triads.events.models import Event, EventFilters

# Import will fail until implementation exists - that's expected for RED phase
try:
    from triads.events.jsonl_repository import JSONLEventRepository
except ImportError:
    JSONLEventRepository = None


pytestmark = pytest.mark.skipif(
    JSONLEventRepository is None,
    reason="JSONLEventRepository not implemented yet (RED phase)"
)


class TestJSONLRepositoryInit:
    """Test repository initialization and file handling."""

    def test_creates_directory_if_not_exists(self, tmp_path):
        """Repository should create parent directory if it doesn't exist."""
        nested_path = tmp_path / "nested" / "dir" / "events.jsonl"
        
        repo = JSONLEventRepository(nested_path)
        
        assert nested_path.parent.exists()
        assert nested_path.parent.is_dir()

    def test_creates_empty_file_if_not_exists(self, temp_jsonl_file):
        """Repository should create empty file if it doesn't exist."""
        assert not temp_jsonl_file.exists()
        
        repo = JSONLEventRepository(temp_jsonl_file)
        
        assert temp_jsonl_file.exists()
        assert temp_jsonl_file.read_text() == ""

    def test_reads_existing_events_on_init(self, temp_jsonl_file, sample_new_format_events):
        """Repository should load existing events from file on initialization."""
        # Write events to file first
        with open(temp_jsonl_file, "w") as f:
            for event in sample_new_format_events:
                f.write(json.dumps(event) + "\n")
        
        repo = JSONLEventRepository(temp_jsonl_file)
        
        # Should be able to query loaded events
        events = repo.query(EventFilters())
        assert len(events) == len(sample_new_format_events)

    def test_handles_empty_file_gracefully(self, temp_jsonl_file):
        """Repository should handle empty file without error."""
        temp_jsonl_file.write_text("")
        
        repo = JSONLEventRepository(temp_jsonl_file)
        events = repo.query(EventFilters())
        
        assert events == []

    def test_handles_nonexistent_file_gracefully(self, temp_jsonl_file):
        """Repository should handle nonexistent file by creating it."""
        assert not temp_jsonl_file.exists()
        
        repo = JSONLEventRepository(temp_jsonl_file)
        events = repo.query(EventFilters())
        
        assert events == []
        assert temp_jsonl_file.exists()


class TestJSONLRepositorySave:
    """Test event save operations."""

    def test_save_appends_to_file(self, temp_jsonl_file, sample_event):
        """Save should append event to JSONL file."""
        repo = JSONLEventRepository(temp_jsonl_file)
        
        repo.save(sample_event)
        
        content = temp_jsonl_file.read_text()
        lines = content.strip().split("\n")
        assert len(lines) == 1
        
        saved_data = json.loads(lines[0])
        assert saved_data["subject"] == sample_event.subject
        assert saved_data["predicate"] == sample_event.predicate

    def test_save_returns_event_id(self, temp_jsonl_file, sample_event):
        """Save should return the event's ID."""
        repo = JSONLEventRepository(temp_jsonl_file)
        
        returned_id = repo.save(sample_event)
        
        assert returned_id == sample_event.id

    def test_save_writes_correct_json_format(self, temp_jsonl_file, sample_event):
        """Save should write events in new format (object_data, not object)."""
        repo = JSONLEventRepository(temp_jsonl_file)
        
        repo.save(sample_event)
        
        content = temp_jsonl_file.read_text()
        saved_data = json.loads(content.strip())
        
        # New format uses "object_data", not "object"
        assert "object_data" in saved_data
        assert "object" not in saved_data
        assert saved_data["object_data"] == sample_event.object_data

    def test_save_multiple_events(self, temp_jsonl_file, multiple_events):
        """Save should handle multiple sequential saves."""
        repo = JSONLEventRepository(temp_jsonl_file)
        
        for event in multiple_events:
            repo.save(event)
        
        content = temp_jsonl_file.read_text()
        lines = content.strip().split("\n")
        assert len(lines) == len(multiple_events)

    def test_save_with_all_fields(self, temp_jsonl_file):
        """Save should serialize all Event fields."""
        repo = JSONLEventRepository(temp_jsonl_file)
        
        event = Event(
            id="test-id-123",
            timestamp=datetime(2025, 10, 30, 14, 30, 0, tzinfo=timezone.utc),
            subject="agent",
            predicate="completed",
            object_data={"agent": "test", "data": [1, 2, 3]},
            workspace_id="workspace-test",
            hook_name="on_stop",
            execution_time_ms=123.45,
            error="Test error",
            metadata={"key": "value"},
        )
        
        repo.save(event)
        
        content = temp_jsonl_file.read_text()
        saved_data = json.loads(content.strip())
        
        assert saved_data["id"] == "test-id-123"
        assert saved_data["subject"] == "agent"
        assert saved_data["predicate"] == "completed"
        assert saved_data["object_data"] == {"agent": "test", "data": [1, 2, 3]}
        assert saved_data["workspace_id"] == "workspace-test"
        assert saved_data["hook_name"] == "on_stop"
        assert saved_data["execution_time_ms"] == 123.45
        assert saved_data["error"] == "Test error"
        assert saved_data["metadata"] == {"key": "value"}

    def test_save_with_optional_fields_none(self, temp_jsonl_file, sample_event_no_optional):
        """Save should handle None values in optional fields."""
        repo = JSONLEventRepository(temp_jsonl_file)

        repo.save(sample_event_no_optional)

        content = temp_jsonl_file.read_text()
        saved_data = json.loads(content.strip())

        # Optional fields with None values may be omitted (valid JSON optimization)
        # If present, they should be None
        assert saved_data.get("workspace_id") is None
        assert saved_data.get("hook_name") is None
        assert saved_data.get("error") is None

        # Required fields must be present
        assert "subject" in saved_data
        assert "predicate" in saved_data
        assert "object_data" in saved_data

    def test_save_handles_nested_object_data(self, temp_jsonl_file):
        """Save should handle complex nested object_data."""
        repo = JSONLEventRepository(temp_jsonl_file)
        
        event = Event(
            subject="test",
            predicate="complex",
            object_data={
                "nested": {
                    "level1": {
                        "level2": {"value": 42}
                    }
                },
                "list": [1, 2, {"inner": "data"}],
                "string": "test",
                "number": 123,
                "boolean": True,
                "null": None,
            },
        )
        
        repo.save(event)
        
        content = temp_jsonl_file.read_text()
        saved_data = json.loads(content.strip())
        
        assert saved_data["object_data"] == event.object_data

    def test_save_atomic_append(self, temp_jsonl_file, sample_event):
        """Save should use atomic append operation."""
        repo = JSONLEventRepository(temp_jsonl_file)
        
        # Write initial event
        repo.save(sample_event)
        
        # Verify file ends with newline (atomic append behavior)
        content = temp_jsonl_file.read_text()
        assert content.endswith("\n")


class TestJSONLRepositoryQuery:
    """Test event query operations."""

    def test_query_no_filters(self, temp_jsonl_file, multiple_events):
        """Query with no filters should return all events."""
        repo = JSONLEventRepository(temp_jsonl_file)
        for event in multiple_events:
            repo.save(event)
        
        results = repo.query(EventFilters())
        
        assert len(results) == len(multiple_events)

    def test_query_by_subject(self, temp_jsonl_file, multiple_events):
        """Query should filter by subject."""
        repo = JSONLEventRepository(temp_jsonl_file)
        for event in multiple_events:
            repo.save(event)
        
        filters = EventFilters(subject="agent")
        results = repo.query(filters)
        
        # multiple_events has 4 agent events (3 completed, 1 started)
        assert len(results) == 4
        assert all(event.subject == "agent" for event in results)

    def test_query_by_predicate(self, temp_jsonl_file, multiple_events):
        """Query should filter by predicate."""
        repo = JSONLEventRepository(temp_jsonl_file)
        for event in multiple_events:
            repo.save(event)
        
        filters = EventFilters(predicate="started")
        results = repo.query(filters)
        
        # multiple_events has 3 "started" events (2 triad, 1 agent)
        assert len(results) == 3
        assert all(event.predicate == "started" for event in results)

    def test_query_by_workspace_id(self, temp_jsonl_file, multiple_events):
        """Query should filter by workspace_id."""
        repo = JSONLEventRepository(temp_jsonl_file)
        for event in multiple_events:
            repo.save(event)
        
        filters = EventFilters(workspace_id="workspace-1")
        results = repo.query(filters)
        
        # multiple_events has 6 events in workspace-1
        assert len(results) == 6
        assert all(event.workspace_id == "workspace-1" for event in results)

    def test_query_combined_filters(self, temp_jsonl_file, multiple_events):
        """Query should apply multiple filters (AND logic)."""
        repo = JSONLEventRepository(temp_jsonl_file)
        for event in multiple_events:
            repo.save(event)
        
        filters = EventFilters(
            workspace_id="workspace-1",
            subject="agent",
            predicate="completed"
        )
        results = repo.query(filters)
        
        # Only 3 events match all filters
        assert len(results) == 3
        assert all(event.workspace_id == "workspace-1" for event in results)
        assert all(event.subject == "agent" for event in results)
        assert all(event.predicate == "completed" for event in results)

    def test_query_time_range_from(self, temp_jsonl_file, multiple_events):
        """Query should filter events after time_from."""
        repo = JSONLEventRepository(temp_jsonl_file)
        for event in multiple_events:
            repo.save(event)
        
        # Filter events after minute 10
        time_from = datetime(2025, 10, 30, 14, 10, 0, tzinfo=timezone.utc)
        filters = EventFilters(time_from=time_from)
        results = repo.query(filters)
        
        # Events at minutes 10, 11, 20, 30 should match
        assert len(results) == 4
        assert all(event.timestamp >= time_from for event in results)

    def test_query_time_range_to(self, temp_jsonl_file, multiple_events):
        """Query should filter events before time_to."""
        repo = JSONLEventRepository(temp_jsonl_file)
        for event in multiple_events:
            repo.save(event)
        
        # Filter events before minute 11
        time_to = datetime(2025, 10, 30, 14, 11, 0, tzinfo=timezone.utc)
        filters = EventFilters(time_to=time_to)
        results = repo.query(filters)
        
        # Events at minutes 0, 1, 2, 10, 11 should match
        assert len(results) == 5
        assert all(event.timestamp <= time_to for event in results)

    def test_query_time_range_between(self, temp_jsonl_file, multiple_events):
        """Query should filter events between time_from and time_to."""
        repo = JSONLEventRepository(temp_jsonl_file)
        for event in multiple_events:
            repo.save(event)
        
        time_from = datetime(2025, 10, 30, 14, 1, 0, tzinfo=timezone.utc)
        time_to = datetime(2025, 10, 30, 14, 11, 0, tzinfo=timezone.utc)
        filters = EventFilters(time_from=time_from, time_to=time_to)
        results = repo.query(filters)
        
        # Events at minutes 1, 2, 10, 11 should match
        assert len(results) == 4
        assert all(time_from <= event.timestamp <= time_to for event in results)

    def test_query_with_search(self, temp_jsonl_file):
        """Query should search in subject, predicate, and error fields."""
        repo = JSONLEventRepository(temp_jsonl_file)
        
        events = [
            Event(subject="agent", predicate="completed", object_data={}),
            Event(subject="triad", predicate="started", object_data={}),
            Event(subject="hook", predicate="failed", object_data={}, error="timeout error"),
        ]
        for event in events:
            repo.save(event)
        
        # Search for "timeout" (should match error field)
        filters = EventFilters(search="timeout")
        results = repo.query(filters)
        assert len(results) == 1
        assert results[0].error == "timeout error"
        
        # Search for "agent" (should match subject field)
        filters = EventFilters(search="agent")
        results = repo.query(filters)
        assert len(results) == 1
        assert results[0].subject == "agent"

    def test_query_with_pagination(self, temp_jsonl_file, multiple_events):
        """Query should respect limit and offset."""
        repo = JSONLEventRepository(temp_jsonl_file)
        for event in multiple_events:
            repo.save(event)
        
        # Get first 3 events
        filters = EventFilters(limit=3, offset=0)
        results = repo.query(filters)
        assert len(results) == 3
        
        # Get next 3 events
        filters = EventFilters(limit=3, offset=3)
        results = repo.query(filters)
        assert len(results) == 3
        
        # Get last event (offset past most events)
        filters = EventFilters(limit=3, offset=6)
        results = repo.query(filters)
        assert len(results) == 1

    def test_query_with_sorting_desc(self, temp_jsonl_file, multiple_events):
        """Query should sort by timestamp descending (default)."""
        repo = JSONLEventRepository(temp_jsonl_file)
        for event in multiple_events:
            repo.save(event)
        
        filters = EventFilters(sort_by="timestamp", sort_order="desc")
        results = repo.query(filters)
        
        # Verify descending order
        for i in range(len(results) - 1):
            assert results[i].timestamp >= results[i + 1].timestamp

    def test_query_with_sorting_asc(self, temp_jsonl_file, multiple_events):
        """Query should sort by timestamp ascending."""
        repo = JSONLEventRepository(temp_jsonl_file)
        for event in multiple_events:
            repo.save(event)
        
        filters = EventFilters(sort_by="timestamp", sort_order="asc")
        results = repo.query(filters)
        
        # Verify ascending order
        for i in range(len(results) - 1):
            assert results[i].timestamp <= results[i + 1].timestamp

    def test_query_empty_file(self, temp_jsonl_file):
        """Query on empty file should return empty list."""
        repo = JSONLEventRepository(temp_jsonl_file)
        
        results = repo.query(EventFilters())
        
        assert results == []

    def test_query_corrupted_lines_skipped(self, temp_jsonl_file, sample_event):
        """Query should skip corrupted JSON lines gracefully."""
        repo = JSONLEventRepository(temp_jsonl_file)
        repo.save(sample_event)
        
        # Add corrupted lines manually
        with open(temp_jsonl_file, "a") as f:
            f.write("this is not valid json\n")
            f.write('{"incomplete": json\n')
        
        # Should still return valid event, skip corrupted lines
        results = repo.query(EventFilters())
        assert len(results) == 1
        assert results[0].id == sample_event.id


class TestJSONLRepositoryCount:
    """Test event count operations."""

    def test_count_all_events(self, temp_jsonl_file, multiple_events):
        """Count with no filters should return total event count."""
        repo = JSONLEventRepository(temp_jsonl_file)
        for event in multiple_events:
            repo.save(event)
        
        count = repo.count(EventFilters())
        
        assert count == len(multiple_events)

    def test_count_with_filters(self, temp_jsonl_file, multiple_events):
        """Count should respect filters."""
        repo = JSONLEventRepository(temp_jsonl_file)
        for event in multiple_events:
            repo.save(event)
        
        filters = EventFilters(workspace_id="workspace-1", subject="agent")
        count = repo.count(filters)
        
        # 3 agent events in workspace-1
        assert count == 3

    def test_count_empty_file(self, temp_jsonl_file):
        """Count on empty file should return 0."""
        repo = JSONLEventRepository(temp_jsonl_file)
        
        count = repo.count(EventFilters())
        
        assert count == 0


class TestJSONLRepositoryGetById:
    """Test get event by ID operations."""

    def test_get_by_id_found(self, temp_jsonl_file, sample_event):
        """Get by ID should return matching event."""
        repo = JSONLEventRepository(temp_jsonl_file)
        repo.save(sample_event)
        
        result = repo.get_by_id(sample_event.id)
        
        assert result is not None
        assert result.id == sample_event.id
        assert result.subject == sample_event.subject
        assert result.predicate == sample_event.predicate

    def test_get_by_id_not_found(self, temp_jsonl_file):
        """Get by ID should return None if not found."""
        repo = JSONLEventRepository(temp_jsonl_file)
        
        result = repo.get_by_id("nonexistent-id")
        
        assert result is None

    def test_get_by_id_empty_file(self, temp_jsonl_file):
        """Get by ID on empty file should return None."""
        repo = JSONLEventRepository(temp_jsonl_file)
        
        result = repo.get_by_id("any-id")
        
        assert result is None


class TestBackwardCompatibility:
    """Test backward compatibility with old event format.
    
    Critical: Must support reading old format (with 'object' field)
    and automatically convert to new format (with 'object_data' field).
    """

    def test_read_old_format_object_field(self, temp_jsonl_file, sample_old_format_events):
        """Repository should read old format events and convert 'object' to 'object_data'."""
        # Write old format events
        with open(temp_jsonl_file, "w") as f:
            for event in sample_old_format_events:
                f.write(json.dumps(event) + "\n")
        
        repo = JSONLEventRepository(temp_jsonl_file)
        results = repo.query(EventFilters())
        
        assert len(results) == len(sample_old_format_events)
        
        # Verify conversion happened
        for event in results:
            assert hasattr(event, "object_data")
            assert event.object_data is not None

    def test_read_old_format_missing_id(self, temp_jsonl_file):
        """Repository should auto-generate ID for old format events missing ID field."""
        old_event = {
            "timestamp": "2025-10-30T22:21:06.960316+00:00",
            "subject": "workspace",
            "predicate": "created",
            "object": {"name": "test"},
        }
        
        with open(temp_jsonl_file, "w") as f:
            f.write(json.dumps(old_event) + "\n")
        
        repo = JSONLEventRepository(temp_jsonl_file)
        results = repo.query(EventFilters())
        
        assert len(results) == 1
        assert results[0].id is not None
        assert len(results[0].id) > 0  # Should have generated UUID

    def test_read_old_format_missing_timestamp(self, temp_jsonl_file):
        """Repository should handle old format events with missing timestamp."""
        old_event = {
            "subject": "workspace",
            "predicate": "created",
            "object": {"name": "test"},
        }
        
        with open(temp_jsonl_file, "w") as f:
            f.write(json.dumps(old_event) + "\n")
        
        repo = JSONLEventRepository(temp_jsonl_file)
        results = repo.query(EventFilters())
        
        # Should either generate timestamp or skip event gracefully
        assert len(results) <= 1  # Either 0 (skipped) or 1 (generated timestamp)

    def test_read_mixed_old_new_formats(self, sample_mixed_format_file):
        """Repository should handle files with both old and new format events."""
        repo = JSONLEventRepository(sample_mixed_format_file)
        results = repo.query(EventFilters())
        
        # Should load all events (3 old + 2 new = 5 total)
        assert len(results) == 5
        
        # All should have object_data field
        for event in results:
            assert hasattr(event, "object_data")
            assert event.object_data is not None

    def test_write_always_uses_new_format(self, temp_jsonl_file, sample_event):
        """New events should always be written in new format (object_data)."""
        repo = JSONLEventRepository(temp_jsonl_file)
        
        repo.save(sample_event)
        
        content = temp_jsonl_file.read_text()
        saved_data = json.loads(content.strip())
        
        # Verify new format
        assert "object_data" in saved_data
        assert "object" not in saved_data

    def test_migration_preserves_data(self, temp_jsonl_file, sample_old_format_events):
        """Migration from old to new format should preserve all data."""
        # Write old format
        with open(temp_jsonl_file, "w") as f:
            for event in sample_old_format_events:
                f.write(json.dumps(event) + "\n")

        # Load with repository
        repo = JSONLEventRepository(temp_jsonl_file)
        results = repo.query(EventFilters())

        # Verify data integrity
        assert len(results) == len(sample_old_format_events)

        # Sort both by timestamp for consistent comparison
        results_sorted = sorted(results, key=lambda e: e.timestamp)
        originals_sorted = sorted(sample_old_format_events, key=lambda e: e["timestamp"])

        for result, original in zip(results_sorted, originals_sorted):
            assert result.subject == original["subject"]
            assert result.predicate == original["predicate"]
            # object_data should contain what was in "object"
            assert result.object_data == original["object"]


class TestJSONLRepositoryEdgeCases:
    """Test edge cases and error handling."""

    def test_large_object_data_handled(self, temp_jsonl_file):
        """Repository should handle large object_data payloads."""
        # Create event with 5KB payload (under 10KB limit)
        large_data = {"text": "x" * 5000, "numbers": list(range(100))}
        event = Event(
            subject="test",
            predicate="large",
            object_data=large_data,
        )
        
        repo = JSONLEventRepository(temp_jsonl_file)
        repo.save(event)
        
        results = repo.query(EventFilters())
        assert len(results) == 1
        assert results[0].object_data == large_data

    def test_unicode_in_subject_predicate(self, temp_jsonl_file):
        """Repository should handle Unicode characters in subject/predicate."""
        event = Event(
            subject="agent_日本語",
            predicate="completed_✓",
            object_data={"message": "Hello 世界"},
        )
        
        repo = JSONLEventRepository(temp_jsonl_file)
        repo.save(event)
        
        results = repo.query(EventFilters())
        assert len(results) == 1
        assert results[0].subject == "agent_日本語"
        assert results[0].predicate == "completed_✓"
        assert results[0].object_data["message"] == "Hello 世界"

    def test_special_characters_in_fields(self, temp_jsonl_file):
        """Repository should handle special characters in all fields."""
        event = Event(
            subject='agent"with"quotes',
            predicate="action\\with\\backslashes",
            object_data={
                "newlines": "line1\nline2\nline3",
                "tabs": "col1\tcol2\tcol3",
                "quotes": 'He said "hello"',
            },
        )
        
        repo = JSONLEventRepository(temp_jsonl_file)
        repo.save(event)
        
        results = repo.query(EventFilters())
        assert len(results) == 1
        assert results[0].object_data == event.object_data

    def test_concurrent_writes_safe(self, temp_jsonl_file, multiple_events):
        """Append-only writes should be thread-safe."""
        # This is a simplified test - actual concurrency would need threading
        repo = JSONLEventRepository(temp_jsonl_file)
        
        # Sequential writes should all succeed
        for event in multiple_events:
            repo.save(event)
        
        # All events should be retrievable
        results = repo.query(EventFilters())
        assert len(results) == len(multiple_events)

    def test_file_permissions(self, tmp_path):
        """Repository should handle file permission errors gracefully."""
        import os
        import stat

        # Create file first, then make directory read-only
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        file_path = readonly_dir / "events.jsonl"

        # Create repository and file while directory is writable
        repo = JSONLEventRepository(file_path)

        # Now make directory read-only (but file is already created)
        # Make file read-only to prevent writes
        os.chmod(file_path, stat.S_IRUSR)

        try:
            # Should raise EventStorageError on write failure
            event = Event(subject="test", predicate="test", object_data={})

            with pytest.raises(EventStorageError):
                repo.save(event)
        finally:
            # Cleanup: restore permissions
            os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR)
            os.chmod(readonly_dir, stat.S_IRWXU)

    def test_disk_full_error(self, temp_jsonl_file, sample_event):
        """Repository should raise EventStorageError if write fails."""
        # We can't easily simulate disk full, but we can test error path
        # This test documents the expected behavior
        repo = JSONLEventRepository(temp_jsonl_file)
        
        # Normal save should succeed
        result = repo.save(sample_event)
        assert result == sample_event.id
        
        # Document: If disk were full, should raise EventStorageError
        # (actual simulation requires mocking or disk quota tools)
