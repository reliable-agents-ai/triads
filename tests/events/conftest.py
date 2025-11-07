"""Pytest fixtures for event tests."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from triads.events.models import Event, EventFilters


@pytest.fixture
def sample_event():
    """Create a sample event for testing."""
    return Event(
        subject="agent",
        predicate="completed",
        object_data={
            "agent": "solution-architect",
            "confidence": 0.95,
            "decisions_made": 5,
        },
        workspace_id="workspace-20251030-143022-oauth",
        hook_name="on_stop",
        execution_time_ms=123.45,
    )


@pytest.fixture
def sample_event_no_optional():
    """Create event with only required fields."""
    return Event(
        subject="workspace",
        predicate="created",
        object_data={"workspace_name": "test-workspace"},
    )


@pytest.fixture
def multiple_events():
    """Create multiple events with different timestamps and attributes."""
    base_time = datetime(2025, 10, 30, 14, 0, 0, tzinfo=timezone.utc)

    events = []

    # Agent events
    for i in range(3):
        events.append(
            Event(
                subject="agent",
                predicate="completed",
                object_data={"agent": f"agent-{i}", "confidence": 0.9 + i * 0.01},
                workspace_id="workspace-1",
                timestamp=base_time + timedelta(minutes=i),
            )
        )

    # Triad events
    for i in range(2):
        events.append(
            Event(
                subject="triad",
                predicate="started",
                object_data={"triad": f"triad-{i}"},
                workspace_id="workspace-1",
                timestamp=base_time + timedelta(minutes=10 + i),
            )
        )

    # Different workspace
    events.append(
        Event(
            subject="agent",
            predicate="started",
            object_data={"agent": "research-analyst"},
            workspace_id="workspace-2",
            timestamp=base_time + timedelta(minutes=20),
        )
    )

    # Error event
    events.append(
        Event(
            subject="hook",
            predicate="failed",
            object_data={"hook": "pre_commit"},
            error="Connection timeout",
            workspace_id="workspace-1",
            timestamp=base_time + timedelta(minutes=30),
        )
    )

    return events


@pytest.fixture
def default_filters():
    """Create default EventFilters for testing."""
    return EventFilters()


@pytest.fixture
def workspace_1_filters():
    """Filters for workspace-1."""
    return EventFilters(workspace_id="workspace-1")


@pytest.fixture
def temp_jsonl_file(tmp_path):
    """Temporary JSONL file for testing."""
    return tmp_path / "test_events.jsonl"


@pytest.fixture
def sample_old_format_events():
    """Events in old format (with 'object' field)."""
    return [
        {
            "timestamp": "2025-10-30T22:21:06.960316+00:00",
            "subject": "workspace",
            "predicate": "context_switch_detected",
            "object": {"user_message": "Start new feature", "classification": "NEW_WORK"},
        },
        {
            "timestamp": "2025-10-30T22:25:15.123456+00:00",
            "subject": "agent",
            "predicate": "completed",
            "object": {"agent": "solution-architect", "confidence": 0.95},
        },
        {
            "timestamp": "2025-10-30T22:30:45.789012+00:00",
            "subject": "triad",
            "predicate": "started",
            "object": {"triad": "design", "agents": ["validation-synthesizer", "solution-architect"]},
        },
    ]


@pytest.fixture
def sample_new_format_events():
    """Events in new format (with 'object_data' field)."""
    return [
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "timestamp": "2025-10-30T22:35:00.000000+00:00",
            "subject": "agent",
            "predicate": "completed",
            "object_data": {"agent": "solution-architect", "confidence": 0.98},
            "workspace_id": "workspace-test",
            "hook_name": "on_stop",
            "execution_time_ms": 234.56,
            "error": None,
            "metadata": {"version": "1.0"},
        },
        {
            "id": "223e4567-e89b-12d3-a456-426614174001",
            "timestamp": "2025-10-30T22:40:00.000000+00:00",
            "subject": "triad",
            "predicate": "started",
            "object_data": {"triad": "implementation", "agents": ["design-bridge", "senior-developer"]},
            "workspace_id": "workspace-test",
            "hook_name": "on_start",
            "execution_time_ms": 12.34,
            "error": None,
            "metadata": {},
        },
    ]


@pytest.fixture
def sample_mixed_format_file(tmp_path, sample_old_format_events, sample_new_format_events):
    """Create a JSONL file with mixed old and new format events."""
    import json

    file_path = tmp_path / "mixed_events.jsonl"
    with open(file_path, "w") as f:
        # Write old format events
        for event in sample_old_format_events:
            f.write(json.dumps(event) + "\n")
        # Write new format events
        for event in sample_new_format_events:
            f.write(json.dumps(event) + "\n")
    return file_path
