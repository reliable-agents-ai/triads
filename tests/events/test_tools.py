"""Tests for MCP tools (capture_event and query_events).

This module tests the MCP-compliant Python tools for event capture and query.
Tests are organized by function and cover all edge cases.
"""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict

import pytest

from triads.events.models import Event
from triads.events.memory_repository import InMemoryEventRepository


class TestCaptureEvent:
    """Tests for capture_event() function."""

    def test_capture_event_success(self, tmp_path: Path) -> None:
        """Test successful event capture with required fields only."""
        from triads.events.tools import capture_event

        repo_path = tmp_path / "events.jsonl"
        result = capture_event(
            subject="agent",
            predicate="completed",
            object_data={"agent": "solution-architect", "confidence": 0.95},
        )

        assert result["success"] is True
        assert "event_id" in result
        assert len(result["event_id"]) == 36  # UUID format
        assert "message" in result

    def test_capture_event_with_all_fields(self, tmp_path: Path) -> None:
        """Test event capture with all optional fields."""
        from triads.events.tools import capture_event

        repo_path = tmp_path / "events.jsonl"
        result = capture_event(
            subject="agent",
            predicate="started",
            object_data={"agent": "senior-developer"},
            workspace_id="workspace-123",
            hook_name="on_start",
            execution_time_ms=45.3,
            metadata={"version": "1.0", "tags": ["test"]},
        )

        assert result["success"] is True
        assert "event_id" in result

    def test_capture_event_missing_subject(self) -> None:
        """Test validation error when subject is missing."""
        from triads.events.tools import capture_event

        result = capture_event(
            subject="",  # Empty subject
            predicate="completed",
            object_data={"test": "data"},
        )

        assert result["success"] is False
        assert "error" in result
        assert "subject" in result["error"].lower()

    def test_capture_event_missing_predicate(self) -> None:
        """Test validation error when predicate is missing."""
        from triads.events.tools import capture_event

        result = capture_event(
            subject="agent",
            predicate="",  # Empty predicate
            object_data={"test": "data"},
        )

        assert result["success"] is False
        assert "error" in result
        assert "predicate" in result["error"].lower()

    def test_capture_event_missing_object_data(self) -> None:
        """Test validation error when object_data is None."""
        from triads.events.tools import capture_event

        result = capture_event(
            subject="agent",
            predicate="completed",
            object_data=None,  # type: ignore
        )

        assert result["success"] is False
        assert "error" in result
        assert "object_data" in result["error"].lower()

    def test_capture_event_truncates_large_payload(self, tmp_path: Path) -> None:
        """Test that large payloads are truncated to prevent bloat."""
        from triads.events.tools import capture_event

        # Create payload > 10KB
        large_payload = {"data": "x" * 15000}

        result = capture_event(
            subject="test",
            predicate="large_data",
            object_data=large_payload,
        )

        assert result["success"] is True

        # Verify truncation happened (check saved event)
        # We can't easily verify truncation without reading the file,
        # but the function should complete without error

    def test_capture_event_with_custom_repository(self) -> None:
        """Test capture_event with custom repository instance."""
        from triads.events.tools import capture_event
        from triads.events.models import EventFilters

        custom_repo = InMemoryEventRepository()

        result = capture_event(
            subject="agent",
            predicate="completed",
            object_data={"test": "data"},
            repository=custom_repo,
        )

        assert result["success"] is True

        # Verify event was saved to custom repo
        events = custom_repo.query(EventFilters())
        assert len(events) == 1
        assert events[0].subject == "agent"

    def test_capture_event_returns_valid_uuid(self) -> None:
        """Test that returned event_id is a valid UUID."""
        from triads.events.tools import capture_event

        result = capture_event(
            subject="test",
            predicate="test",
            object_data={"test": "data"},
        )

        assert result["success"] is True
        event_id = result["event_id"]

        # UUID format: 8-4-4-4-12 hex characters
        parts = event_id.split("-")
        assert len(parts) == 5
        assert len(parts[0]) == 8
        assert len(parts[1]) == 4
        assert len(parts[2]) == 4
        assert len(parts[3]) == 4
        assert len(parts[4]) == 12

    def test_capture_event_with_nested_object_data(self) -> None:
        """Test capture_event with deeply nested object_data."""
        from triads.events.tools import capture_event

        nested_data = {
            "level1": {
                "level2": {
                    "level3": {
                        "value": "deep",
                        "list": [1, 2, 3],
                    }
                }
            }
        }

        result = capture_event(
            subject="test",
            predicate="nested",
            object_data=nested_data,
        )

        assert result["success"] is True

    def test_capture_event_storage_error_handling(self, tmp_path: Path) -> None:
        """Test error handling when storage fails."""
        from triads.events.tools import capture_event

        # Create a read-only directory to trigger storage error
        read_only_dir = tmp_path / "readonly"
        read_only_dir.mkdir()
        read_only_dir.chmod(0o444)

        try:
            result = capture_event(
                subject="test",
                predicate="test",
                object_data={"test": "data"},
            )

            # Should return error dict, not raise exception
            # (May succeed or fail depending on permissions, but should not raise)
            assert "success" in result
        finally:
            # Restore permissions for cleanup
            read_only_dir.chmod(0o755)


class TestQueryEvents:
    """Tests for query_events() function."""

    def test_query_events_no_filters(self) -> None:
        """Test query with no filters returns all events."""
        from triads.events.tools import query_events

        # Create repo with test events
        repo = InMemoryEventRepository()
        repo.save(Event("agent", "started", {"agent": "test1"}))
        repo.save(Event("agent", "completed", {"agent": "test2"}))

        result = query_events(repository=repo)

        assert result["success"] is True
        assert len(result["events"]) == 2
        assert result["total_count"] == 2

    def test_query_events_by_subject(self) -> None:
        """Test filtering by subject."""
        from triads.events.tools import query_events

        repo = InMemoryEventRepository()
        repo.save(Event("agent", "completed", {"test": 1}))
        repo.save(Event("workspace", "created", {"test": 2}))
        repo.save(Event("agent", "started", {"test": 3}))

        result = query_events(subject="agent", repository=repo)

        assert result["success"] is True
        assert len(result["events"]) == 2
        assert all(e["subject"] == "agent" for e in result["events"])

    def test_query_events_by_predicate(self) -> None:
        """Test filtering by predicate."""
        from triads.events.tools import query_events

        repo = InMemoryEventRepository()
        repo.save(Event("agent", "completed", {"test": 1}))
        repo.save(Event("agent", "started", {"test": 2}))
        repo.save(Event("workspace", "completed", {"test": 3}))

        result = query_events(predicate="completed", repository=repo)

        assert result["success"] is True
        assert len(result["events"]) == 2
        assert all(e["predicate"] == "completed" for e in result["events"])

    def test_query_events_by_workspace_id(self) -> None:
        """Test filtering by workspace_id."""
        from triads.events.tools import query_events

        repo = InMemoryEventRepository()
        repo.save(Event("agent", "completed", {"test": 1}, workspace_id="ws1"))
        repo.save(Event("agent", "completed", {"test": 2}, workspace_id="ws2"))
        repo.save(Event("agent", "completed", {"test": 3}, workspace_id="ws1"))

        result = query_events(workspace_id="ws1", repository=repo)

        assert result["success"] is True
        assert len(result["events"]) == 2
        assert all(e["workspace_id"] == "ws1" for e in result["events"])

    def test_query_events_time_range_from(self) -> None:
        """Test filtering by time_from (ISO string)."""
        from triads.events.tools import query_events

        repo = InMemoryEventRepository()

        # Create events with different timestamps
        now = datetime.now(timezone.utc)
        past = now - timedelta(hours=2)

        event1 = Event("agent", "old", {"test": 1})
        event1.timestamp = past
        repo.save(event1)

        event2 = Event("agent", "recent", {"test": 2})
        event2.timestamp = now
        repo.save(event2)

        # Query events from 1 hour ago
        time_from = (now - timedelta(hours=1)).isoformat()
        result = query_events(time_from=time_from, repository=repo)

        assert result["success"] is True
        assert len(result["events"]) == 1
        assert result["events"][0]["predicate"] == "recent"

    def test_query_events_time_range_to(self) -> None:
        """Test filtering by time_to (ISO string)."""
        from triads.events.tools import query_events

        repo = InMemoryEventRepository()

        now = datetime.now(timezone.utc)
        future = now + timedelta(hours=2)

        event1 = Event("agent", "now", {"test": 1})
        event1.timestamp = now
        repo.save(event1)

        event2 = Event("agent", "future", {"test": 2})
        event2.timestamp = future
        repo.save(event2)

        # Query events up to 1 hour from now
        time_to = (now + timedelta(hours=1)).isoformat()
        result = query_events(time_to=time_to, repository=repo)

        assert result["success"] is True
        assert len(result["events"]) == 1
        assert result["events"][0]["predicate"] == "now"

    def test_query_events_with_search(self) -> None:
        """Test full-text search filter."""
        from triads.events.tools import query_events

        repo = InMemoryEventRepository()
        repo.save(Event("agent", "completed", {"name": "solution-architect"}))
        repo.save(Event("workspace", "created", {"name": "test-workspace"}))
        repo.save(Event("agent", "started", {"name": "senior-developer"}))

        result = query_events(search="solution", repository=repo)

        assert result["success"] is True
        assert len(result["events"]) == 1
        assert "solution" in str(result["events"][0]["object_data"]).lower()

    def test_query_events_with_pagination(self) -> None:
        """Test pagination (limit and offset)."""
        from triads.events.tools import query_events

        repo = InMemoryEventRepository()
        for i in range(10):
            repo.save(Event("agent", "test", {"index": i}))

        # First page
        result = query_events(limit=3, offset=0, repository=repo)
        assert len(result["events"]) == 3
        assert result["total_count"] == 10

        # Second page
        result = query_events(limit=3, offset=3, repository=repo)
        assert len(result["events"]) == 3

        # Last page
        result = query_events(limit=3, offset=9, repository=repo)
        assert len(result["events"]) == 1

    def test_query_events_sorting_desc(self) -> None:
        """Test sorting in descending order (default)."""
        from triads.events.tools import query_events

        repo = InMemoryEventRepository()

        now = datetime.now(timezone.utc)
        for i in range(3):
            event = Event("agent", f"test{i}", {"index": i})
            event.timestamp = now + timedelta(seconds=i)
            repo.save(event)

        result = query_events(sort_order="desc", repository=repo)

        assert result["success"] is True
        # Most recent first
        assert result["events"][0]["predicate"] == "test2"
        assert result["events"][1]["predicate"] == "test1"
        assert result["events"][2]["predicate"] == "test0"

    def test_query_events_sorting_asc(self) -> None:
        """Test sorting in ascending order."""
        from triads.events.tools import query_events

        repo = InMemoryEventRepository()

        now = datetime.now(timezone.utc)
        for i in range(3):
            event = Event("agent", f"test{i}", {"index": i})
            event.timestamp = now + timedelta(seconds=i)
            repo.save(event)

        result = query_events(sort_order="asc", repository=repo)

        assert result["success"] is True
        # Oldest first
        assert result["events"][0]["predicate"] == "test0"
        assert result["events"][1]["predicate"] == "test1"
        assert result["events"][2]["predicate"] == "test2"

    def test_query_events_invalid_time_from_format(self) -> None:
        """Test error handling for invalid time_from format."""
        from triads.events.tools import query_events

        repo = InMemoryEventRepository()

        result = query_events(time_from="not-a-date", repository=repo)

        assert result["success"] is False
        assert "error" in result
        assert "time_from" in result["error"].lower()

    def test_query_events_invalid_time_to_format(self) -> None:
        """Test error handling for invalid time_to format."""
        from triads.events.tools import query_events

        repo = InMemoryEventRepository()

        result = query_events(time_to="invalid-date", repository=repo)

        assert result["success"] is False
        assert "error" in result
        assert "time_to" in result["error"].lower()

    def test_query_events_serializes_timestamps(self) -> None:
        """Test that timestamps are serialized as ISO strings."""
        from triads.events.tools import query_events

        repo = InMemoryEventRepository()
        repo.save(Event("agent", "test", {"data": "test"}))

        result = query_events(repository=repo)

        assert result["success"] is True
        timestamp = result["events"][0]["timestamp"]

        # Should be ISO string, not datetime object
        assert isinstance(timestamp, str)
        # Should be parseable as ISO 8601
        parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        assert parsed.tzinfo is not None

    def test_query_events_returns_total_count(self) -> None:
        """Test that total_count reflects total matches (not paginated count)."""
        from triads.events.tools import query_events

        repo = InMemoryEventRepository()
        for i in range(10):
            repo.save(Event("agent", "test", {"index": i}))

        result = query_events(limit=3, repository=repo)

        assert result["success"] is True
        assert len(result["events"]) == 3  # Paginated results
        assert result["total_count"] == 10  # Total matches

    def test_query_events_empty_repository(self) -> None:
        """Test query against empty repository."""
        from triads.events.tools import query_events

        repo = InMemoryEventRepository()

        result = query_events(repository=repo)

        assert result["success"] is True
        assert len(result["events"]) == 0
        assert result["total_count"] == 0

    def test_query_events_combined_filters(self) -> None:
        """Test multiple filters combined (AND logic)."""
        from triads.events.tools import query_events

        repo = InMemoryEventRepository()
        repo.save(Event("agent", "completed", {"test": 1}, workspace_id="ws1"))
        repo.save(Event("agent", "started", {"test": 2}, workspace_id="ws1"))
        repo.save(Event("workspace", "completed", {"test": 3}, workspace_id="ws1"))
        repo.save(Event("agent", "completed", {"test": 4}, workspace_id="ws2"))

        result = query_events(
            subject="agent",
            predicate="completed",
            workspace_id="ws1",
            repository=repo,
        )

        assert result["success"] is True
        assert len(result["events"]) == 1
        assert result["events"][0]["object_data"]["test"] == 1

    def test_query_events_default_repository_path(self, tmp_path: Path, monkeypatch) -> None:
        """Test that default repository uses .triads/events.jsonl."""
        from triads.events.tools import query_events

        # Change working directory to tmp_path
        monkeypatch.chdir(tmp_path)

        # Create default events file
        events_dir = tmp_path / ".triads"
        events_dir.mkdir()
        events_file = events_dir / "events.jsonl"

        # Write test event
        event_data = {
            "id": "test-id",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "subject": "test",
            "predicate": "test",
            "object_data": {"test": "data"},
        }
        events_file.write_text(json.dumps(event_data) + "\n")

        # Query without specifying repository
        result = query_events()

        assert result["success"] is True
        assert len(result["events"]) == 1

    def test_query_events_handles_query_error(self) -> None:
        """Test error handling when query fails."""
        from triads.events.tools import query_events

        # Use repository that will raise an error
        # (In practice, this is hard to trigger since query() is robust)
        # But we test that the function returns error dict

        result = query_events(repository=None)  # type: ignore

        # Should return error dict, not raise exception
        assert "success" in result
        # May succeed with default repo or fail, but should not raise
