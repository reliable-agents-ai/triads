"""Tests for InMemoryEventRepository (RED phase - TDD)."""

from datetime import datetime, timedelta, timezone

import pytest

from triads.events.exceptions import EventQueryError, EventStorageError, InvalidEventError
from triads.events.memory_repository import InMemoryEventRepository
from triads.events.models import Event, EventFilters


class TestInMemoryRepositorySave:
    """Test saving events to repository."""

    def test_save_returns_event_id(self, sample_event):
        """save() returns event ID."""
        repo = InMemoryEventRepository()
        event_id = repo.save(sample_event)
        assert event_id == sample_event.id

    def test_save_stores_event(self, sample_event):
        """save() stores event in repository."""
        repo = InMemoryEventRepository()
        repo.save(sample_event)
        
        retrieved = repo.get_by_id(sample_event.id)
        assert retrieved is not None
        assert retrieved.id == sample_event.id

    def test_save_multiple_events(self, multiple_events):
        """save() can store multiple events."""
        repo = InMemoryEventRepository()
        
        for event in multiple_events:
            repo.save(event)
        
        # Verify all events stored
        assert repo.count(EventFilters()) == len(multiple_events)

    def test_save_invalid_event_raises_error(self):
        """save() raises InvalidEventError for None event."""
        repo = InMemoryEventRepository()
        
        with pytest.raises(InvalidEventError):
            repo.save(None)

    def test_save_event_with_missing_required_field_raises_error(self):
        """save() validates required fields."""
        repo = InMemoryEventRepository()
        
        # Create event with missing predicate (should fail)
        with pytest.raises(InvalidEventError):
            event = Event(subject="test", predicate="", object_data={})
            repo.save(event)


class TestInMemoryRepositoryGetById:
    """Test retrieving single event by ID."""

    def test_get_by_id_returns_event(self, sample_event):
        """get_by_id() returns event when found."""
        repo = InMemoryEventRepository()
        repo.save(sample_event)
        
        retrieved = repo.get_by_id(sample_event.id)
        assert retrieved is not None
        assert retrieved.id == sample_event.id
        assert retrieved.subject == sample_event.subject

    def test_get_by_id_returns_none_when_not_found(self):
        """get_by_id() returns None when event not found."""
        repo = InMemoryEventRepository()
        
        retrieved = repo.get_by_id("nonexistent-id")
        assert retrieved is None

    def test_get_by_id_with_empty_string_returns_none(self):
        """get_by_id() handles empty string ID."""
        repo = InMemoryEventRepository()
        
        retrieved = repo.get_by_id("")
        assert retrieved is None


class TestInMemoryRepositoryQuery:
    """Test querying events with filters."""

    def test_query_no_filters_returns_all(self, multiple_events):
        """query() with no filters returns all events."""
        repo = InMemoryEventRepository()
        for event in multiple_events:
            repo.save(event)
        
        results = repo.query(EventFilters())
        assert len(results) == len(multiple_events)

    def test_query_by_workspace_id(self, multiple_events):
        """query() filters by workspace_id."""
        repo = InMemoryEventRepository()
        for event in multiple_events:
            repo.save(event)
        
        filters = EventFilters(workspace_id="workspace-1")
        results = repo.query(filters)
        
        # Should get all events from workspace-1 (6 events)
        assert len(results) == 6
        assert all(e.workspace_id == "workspace-1" for e in results)

    def test_query_by_subject(self, multiple_events):
        """query() filters by subject."""
        repo = InMemoryEventRepository()
        for event in multiple_events:
            repo.save(event)
        
        filters = EventFilters(subject="agent")
        results = repo.query(filters)
        
        # Should get all agent events (4 events)
        assert len(results) == 4
        assert all(e.subject == "agent" for e in results)

    def test_query_by_predicate(self, multiple_events):
        """query() filters by predicate."""
        repo = InMemoryEventRepository()
        for event in multiple_events:
            repo.save(event)
        
        filters = EventFilters(predicate="completed")
        results = repo.query(filters)
        
        # Should get all completed events (3 events)
        assert len(results) == 3
        assert all(e.predicate == "completed" for e in results)

    def test_query_combined_filters(self, multiple_events):
        """query() combines multiple filters with AND logic."""
        repo = InMemoryEventRepository()
        for event in multiple_events:
            repo.save(event)
        
        filters = EventFilters(
            workspace_id="workspace-1",
            subject="agent",
            predicate="completed"
        )
        results = repo.query(filters)
        
        # Should get agent completed events from workspace-1 (3 events)
        assert len(results) == 3
        assert all(
            e.workspace_id == "workspace-1" 
            and e.subject == "agent" 
            and e.predicate == "completed" 
            for e in results
        )

    def test_query_time_range_from(self, multiple_events):
        """query() filters by time_from."""
        repo = InMemoryEventRepository()
        for event in multiple_events:
            repo.save(event)
        
        # Query events after 15 minutes
        time_from = datetime(2025, 10, 30, 14, 15, 0, tzinfo=timezone.utc)
        filters = EventFilters(time_from=time_from)
        results = repo.query(filters)
        
        # Should get events after minute 15
        assert len(results) == 2
        assert all(e.timestamp >= time_from for e in results)

    def test_query_time_range_to(self, multiple_events):
        """query() filters by time_to."""
        repo = InMemoryEventRepository()
        for event in multiple_events:
            repo.save(event)
        
        # Query events before 15 minutes
        time_to = datetime(2025, 10, 30, 14, 15, 0, tzinfo=timezone.utc)
        filters = EventFilters(time_to=time_to)
        results = repo.query(filters)
        
        # Should get events before minute 15
        assert len(results) == 5
        assert all(e.timestamp <= time_to for e in results)

    def test_query_time_range_between(self, multiple_events):
        """query() filters by time range (time_from AND time_to)."""
        repo = InMemoryEventRepository()
        for event in multiple_events:
            repo.save(event)
        
        # Query events between 5 and 15 minutes
        time_from = datetime(2025, 10, 30, 14, 5, 0, tzinfo=timezone.utc)
        time_to = datetime(2025, 10, 30, 14, 15, 0, tzinfo=timezone.utc)
        filters = EventFilters(time_from=time_from, time_to=time_to)
        results = repo.query(filters)
        
        # Should get events in range
        assert len(results) == 2
        assert all(time_from <= e.timestamp <= time_to for e in results)

    def test_query_full_text_search(self, multiple_events):
        """query() supports full-text search in object_data."""
        repo = InMemoryEventRepository()
        for event in multiple_events:
            repo.save(event)
        
        filters = EventFilters(search="agent-1")
        results = repo.query(filters)
        
        # Should find event with "agent-1" in object_data
        assert len(results) == 1
        assert "agent-1" in str(results[0].object_data)

    def test_query_full_text_search_case_insensitive(self):
        """query() search is case-insensitive."""
        repo = InMemoryEventRepository()
        event = Event(
            "test",
            "test",
            {"message": "OAuth Authentication"},
        )
        repo.save(event)
        
        # Search with lowercase should find uppercase content
        filters = EventFilters(search="oauth")
        results = repo.query(filters)
        
        assert len(results) == 1

    def test_query_full_text_search_in_error(self):
        """query() searches in error field too."""
        repo = InMemoryEventRepository()
        event = Event(
            "hook",
            "failed",
            {"hook": "pre_commit"},
            error="Connection timeout error"
        )
        repo.save(event)
        
        filters = EventFilters(search="timeout")
        results = repo.query(filters)
        
        assert len(results) == 1

    def test_query_pagination_limit(self, multiple_events):
        """query() respects limit for pagination."""
        repo = InMemoryEventRepository()
        for event in multiple_events:
            repo.save(event)
        
        filters = EventFilters(limit=3)
        results = repo.query(filters)
        
        assert len(results) == 3

    def test_query_pagination_offset(self, multiple_events):
        """query() respects offset for pagination."""
        repo = InMemoryEventRepository()
        for event in multiple_events:
            repo.save(event)
        
        # Get first 3
        first_page = repo.query(EventFilters(limit=3, offset=0, sort_by="timestamp", sort_order="asc"))
        
        # Get next 3
        second_page = repo.query(EventFilters(limit=3, offset=3, sort_by="timestamp", sort_order="asc"))
        
        # Should be different events
        first_ids = {e.id for e in first_page}
        second_ids = {e.id for e in second_page}
        assert first_ids.isdisjoint(second_ids)

    def test_query_pagination_offset_beyond_results(self, multiple_events):
        """query() with offset beyond results returns empty list."""
        repo = InMemoryEventRepository()
        for event in multiple_events:
            repo.save(event)
        
        filters = EventFilters(offset=1000)
        results = repo.query(filters)
        
        assert len(results) == 0

    def test_query_sort_by_timestamp_desc(self, multiple_events):
        """query() sorts by timestamp descending (default)."""
        repo = InMemoryEventRepository()
        for event in multiple_events:
            repo.save(event)
        
        filters = EventFilters(sort_by="timestamp", sort_order="desc")
        results = repo.query(filters)
        
        # Verify descending order (newest first)
        timestamps = [e.timestamp for e in results]
        assert timestamps == sorted(timestamps, reverse=True)

    def test_query_sort_by_timestamp_asc(self, multiple_events):
        """query() sorts by timestamp ascending."""
        repo = InMemoryEventRepository()
        for event in multiple_events:
            repo.save(event)
        
        filters = EventFilters(sort_by="timestamp", sort_order="asc")
        results = repo.query(filters)
        
        # Verify ascending order (oldest first)
        timestamps = [e.timestamp for e in results]
        assert timestamps == sorted(timestamps)

    def test_query_sort_by_subject(self, multiple_events):
        """query() sorts by subject."""
        repo = InMemoryEventRepository()
        for event in multiple_events:
            repo.save(event)
        
        filters = EventFilters(sort_by="subject", sort_order="asc")
        results = repo.query(filters)
        
        # Verify sorted by subject
        subjects = [e.subject for e in results]
        assert subjects == sorted(subjects)

    def test_query_empty_repository_returns_empty_list(self):
        """query() on empty repository returns empty list."""
        repo = InMemoryEventRepository()
        
        results = repo.query(EventFilters())
        assert results == []

    def test_query_no_matches_returns_empty_list(self, multiple_events):
        """query() with no matches returns empty list."""
        repo = InMemoryEventRepository()
        for event in multiple_events:
            repo.save(event)
        
        filters = EventFilters(subject="nonexistent")
        results = repo.query(filters)
        
        assert results == []


class TestInMemoryRepositoryCount:
    """Test counting events with filters."""

    def test_count_no_filters(self, multiple_events):
        """count() with no filters counts all events."""
        repo = InMemoryEventRepository()
        for event in multiple_events:
            repo.save(event)
        
        total = repo.count(EventFilters())
        assert total == len(multiple_events)

    def test_count_with_workspace_filter(self, multiple_events):
        """count() respects workspace_id filter."""
        repo = InMemoryEventRepository()
        for event in multiple_events:
            repo.save(event)
        
        filters = EventFilters(workspace_id="workspace-1")
        count = repo.count(filters)
        
        assert count == 6

    def test_count_with_subject_filter(self, multiple_events):
        """count() respects subject filter."""
        repo = InMemoryEventRepository()
        for event in multiple_events:
            repo.save(event)
        
        filters = EventFilters(subject="agent")
        count = repo.count(filters)
        
        assert count == 4

    def test_count_combined_filters(self, multiple_events):
        """count() combines multiple filters."""
        repo = InMemoryEventRepository()
        for event in multiple_events:
            repo.save(event)
        
        filters = EventFilters(
            workspace_id="workspace-1",
            subject="agent"
        )
        count = repo.count(filters)
        
        assert count == 3

    def test_count_with_time_range(self, multiple_events):
        """count() respects time range filters."""
        repo = InMemoryEventRepository()
        for event in multiple_events:
            repo.save(event)
        
        time_from = datetime(2025, 10, 30, 14, 15, 0, tzinfo=timezone.utc)
        filters = EventFilters(time_from=time_from)
        count = repo.count(filters)
        
        assert count == 2

    def test_count_with_search(self):
        """count() respects search filter."""
        repo = InMemoryEventRepository()
        event1 = Event("test", "test", {"message": "OAuth"})
        event2 = Event("test", "test", {"message": "JWT"})
        repo.save(event1)
        repo.save(event2)
        
        filters = EventFilters(search="OAuth")
        count = repo.count(filters)
        
        assert count == 1

    def test_count_empty_repository(self):
        """count() on empty repository returns 0."""
        repo = InMemoryEventRepository()
        
        count = repo.count(EventFilters())
        assert count == 0

    def test_count_no_matches(self, multiple_events):
        """count() with no matches returns 0."""
        repo = InMemoryEventRepository()
        for event in multiple_events:
            repo.save(event)
        
        filters = EventFilters(subject="nonexistent")
        count = repo.count(filters)
        
        assert count == 0


class TestInMemoryRepositoryEdgeCases:
    """Test edge cases and error handling."""

    def test_repository_isolation(self):
        """Different repository instances are isolated."""
        repo1 = InMemoryEventRepository()
        repo2 = InMemoryEventRepository()
        
        event1 = Event("test1", "test1", {})
        repo1.save(event1)
        
        # repo2 should not see repo1's events
        assert repo2.count(EventFilters()) == 0

    def test_query_pagination_boundary_conditions(self):
        """query() handles edge cases in pagination."""
        repo = InMemoryEventRepository()
        
        # Create 5 events
        for i in range(5):
            repo.save(Event(f"subject-{i}", "test", {}))
        
        # Limit larger than total
        results = repo.query(EventFilters(limit=100))
        assert len(results) == 5
        
        # Offset at boundary
        results = repo.query(EventFilters(offset=5))
        assert len(results) == 0
        
        # Offset just before boundary
        results = repo.query(EventFilters(offset=4, limit=10))
        assert len(results) == 1

    def test_query_with_invalid_sort_field(self):
        """query() handles invalid sort_by field gracefully."""
        repo = InMemoryEventRepository()
        event = Event("test", "test", {})
        repo.save(event)
        
        # Should not raise error, fall back to timestamp
        filters = EventFilters(sort_by="nonexistent_field")
        results = repo.query(filters)
        
        assert len(results) == 1

    def test_save_and_retrieve_event_with_all_optional_fields(self):
        """Repository handles events with all optional fields."""
        repo = InMemoryEventRepository()
        
        event = Event(
            subject="hook",
            predicate="executed",
            object_data={"hook": "on_stop"},
            workspace_id="workspace-123",
            hook_name="on_stop",
            execution_time_ms=45.67,
            error="Some error",
            metadata={"key": "value"}
        )
        repo.save(event)
        
        retrieved = repo.get_by_id(event.id)
        assert retrieved.workspace_id == "workspace-123"
        assert retrieved.hook_name == "on_stop"
        assert retrieved.execution_time_ms == 45.67
        assert retrieved.error == "Some error"
        assert retrieved.metadata == {"key": "value"}
