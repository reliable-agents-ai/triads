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
