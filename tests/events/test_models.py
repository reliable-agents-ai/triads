"""Tests for Event and EventFilters models (RED phase - TDD)."""

from datetime import datetime, timezone
from uuid import UUID

import pytest

from triads.events.models import Event, EventFilters


class TestEvent:
    """Test Event dataclass creation and validation."""

    def test_event_with_all_fields(self, sample_event):
        """Event can be created with all fields."""
        assert sample_event.subject == "agent"
        assert sample_event.predicate == "completed"
        assert sample_event.object_data == {
            "agent": "solution-architect",
            "confidence": 0.95,
            "decisions_made": 5,
        }
        assert sample_event.workspace_id == "workspace-20251030-143022-oauth"
        assert sample_event.hook_name == "on_stop"
        assert sample_event.execution_time_ms == 123.45

    def test_event_with_required_fields_only(self, sample_event_no_optional):
        """Event can be created with only required fields."""
        assert sample_event_no_optional.subject == "workspace"
        assert sample_event_no_optional.predicate == "created"
        assert sample_event_no_optional.object_data == {"workspace_name": "test-workspace"}
        assert sample_event_no_optional.workspace_id is None
        assert sample_event_no_optional.hook_name is None
        assert sample_event_no_optional.execution_time_ms is None
        assert sample_event_no_optional.error is None

    def test_event_id_auto_generated(self, sample_event):
        """Event ID is automatically generated as UUID."""
        assert isinstance(sample_event.id, str)
        # Verify it's a valid UUID
        UUID(sample_event.id)

    def test_event_id_unique(self):
        """Each event gets a unique ID."""
        event1 = Event("subject1", "predicate1", {})
        event2 = Event("subject2", "predicate2", {})
        assert event1.id != event2.id

    def test_event_timestamp_auto_generated(self, sample_event):
        """Event timestamp is automatically generated in UTC."""
        assert isinstance(sample_event.timestamp, datetime)
        assert sample_event.timestamp.tzinfo == timezone.utc

    def test_event_timestamp_is_current(self):
        """Event timestamp is close to current time."""
        before = datetime.now(timezone.utc)
        event = Event("subject", "predicate", {})
        after = datetime.now(timezone.utc)

        assert before <= event.timestamp <= after

    def test_event_with_error(self):
        """Event can include error information."""
        event = Event(
            subject="hook",
            predicate="failed",
            object_data={"hook": "pre_commit"},
            error="Connection timeout",
        )
        assert event.error == "Connection timeout"

    def test_event_metadata_dict(self):
        """Event can include arbitrary metadata."""
        event = Event(
            subject="agent",
            predicate="started",
            object_data={"agent": "research-analyst"},
            metadata={"user_id": "user123", "session_id": "sess456"},
        )
        assert event.metadata == {"user_id": "user123", "session_id": "sess456"}

    def test_event_metadata_defaults_to_empty_dict(self, sample_event):
        """Event metadata defaults to empty dict."""
        assert sample_event.metadata == {}

    def test_event_custom_timestamp(self):
        """Event can be created with custom timestamp."""
        custom_time = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        event = Event(
            subject="test",
            predicate="custom",
            object_data={},
            timestamp=custom_time,
        )
        assert event.timestamp == custom_time

    def test_event_object_data_is_dict(self):
        """Event object_data must be a dictionary."""
        event = Event("subject", "predicate", {"key": "value"})
        assert isinstance(event.object_data, dict)

    def test_event_object_data_can_be_nested(self):
        """Event object_data can contain nested structures."""
        event = Event(
            "subject",
            "predicate",
            {
                "nested": {"level1": {"level2": "value"}},
                "list": [1, 2, 3],
                "mixed": {"items": [{"id": 1}, {"id": 2}]},
            },
        )
        assert event.object_data["nested"]["level1"]["level2"] == "value"
        assert event.object_data["list"] == [1, 2, 3]

    def test_event_string_representation(self, sample_event):
        """Event has useful string representation."""
        event_str = str(sample_event)
        assert "agent" in event_str
        assert "completed" in event_str


class TestEventFilters:
    """Test EventFilters dataclass for querying."""

    def test_filters_default_values(self, default_filters):
        """EventFilters has correct default values."""
        assert default_filters.workspace_id is None
        assert default_filters.subject is None
        assert default_filters.predicate is None
        assert default_filters.time_from is None
        assert default_filters.time_to is None
        assert default_filters.search is None
        assert default_filters.limit == 100
        assert default_filters.offset == 0
        assert default_filters.sort_by == "timestamp"
        assert default_filters.sort_order == "desc"

    def test_filters_with_workspace_id(self, workspace_1_filters):
        """Filters can filter by workspace_id."""
        assert workspace_1_filters.workspace_id == "workspace-1"

    def test_filters_with_subject(self):
        """Filters can filter by subject."""
        filters = EventFilters(subject="agent")
        assert filters.subject == "agent"

    def test_filters_with_predicate(self):
        """Filters can filter by predicate."""
        filters = EventFilters(predicate="completed")
        assert filters.predicate == "completed"

    def test_filters_with_time_range(self):
        """Filters can filter by time range."""
        time_from = datetime(2025, 10, 30, 14, 0, 0, tzinfo=timezone.utc)
        time_to = datetime(2025, 10, 30, 15, 0, 0, tzinfo=timezone.utc)
        filters = EventFilters(time_from=time_from, time_to=time_to)
        assert filters.time_from == time_from
        assert filters.time_to == time_to

    def test_filters_with_search(self):
        """Filters can include full-text search."""
        filters = EventFilters(search="OAuth")
        assert filters.search == "OAuth"

    def test_filters_with_pagination(self):
        """Filters support pagination."""
        filters = EventFilters(limit=50, offset=100)
        assert filters.limit == 50
        assert filters.offset == 100

    def test_filters_with_sorting(self):
        """Filters support sorting configuration."""
        filters = EventFilters(sort_by="subject", sort_order="asc")
        assert filters.sort_by == "subject"
        assert filters.sort_order == "asc"

    def test_filters_all_fields_combined(self):
        """Filters can combine all fields."""
        time_from = datetime(2025, 10, 30, 14, 0, 0, tzinfo=timezone.utc)
        filters = EventFilters(
            workspace_id="workspace-1",
            subject="agent",
            predicate="completed",
            time_from=time_from,
            search="OAuth",
            limit=25,
            offset=50,
            sort_by="timestamp",
            sort_order="asc",
        )
        assert filters.workspace_id == "workspace-1"
        assert filters.subject == "agent"
        assert filters.predicate == "completed"
        assert filters.time_from == time_from
        assert filters.search == "OAuth"
        assert filters.limit == 25
        assert filters.offset == 50
        assert filters.sort_by == "timestamp"
        assert filters.sort_order == "asc"
