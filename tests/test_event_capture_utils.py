"""Tests for event_capture_utils module."""

import json
import sys
from pathlib import Path

import pytest

# Add hooks to path
hooks_dir = Path(__file__).parent.parent / "hooks"
sys.path.insert(0, str(hooks_dir))

from event_capture_utils import (
    _check_rate_limit,
    _should_rotate_file,
    capture_hook_error,
    capture_hook_execution,
    safe_capture_event,
)


class TestSafeCaptureEvent:
    """Test safe_capture_event function."""

    def test_capture_event_success(self, temp_events_dir, monkeypatch):
        """Test successful event capture."""
        monkeypatch.setattr("event_capture_utils.EVENTS_FILE", str(temp_events_dir / "events.jsonl"))

        result = safe_capture_event(
            hook_name="test_hook",
            predicate="executed",
            object_data={"status": "success"}
        )

        assert result is True

        events_file = temp_events_dir / "events.jsonl"
        assert events_file.exists()

        with open(events_file, 'r') as f:
            event = json.loads(f.read())

        assert event["hook"] == "test_hook"
        assert event["predicate"] == "executed"
        assert event["object"]["status"] == "success"

    def test_capture_event_invalid_object_data(self):
        """Test event capture with invalid object_data (not dict)."""
        result = safe_capture_event(
            hook_name="test_hook",
            predicate="executed",
            object_data="not a dict"  # Invalid
        )

        assert result is False

    def test_capture_event_with_workspace_id(self, temp_events_dir, monkeypatch):
        """Test event capture with workspace ID."""
        monkeypatch.setattr("event_capture_utils.EVENTS_FILE", str(temp_events_dir / "events.jsonl"))

        result = safe_capture_event(
            hook_name="test_hook",
            predicate="executed",
            object_data={"status": "success"},
            workspace_id="workspace-123"
        )

        assert result is True

        with open(temp_events_dir / "events.jsonl", 'r') as f:
            event = json.loads(f.read())

        assert event["workspace_id"] == "workspace-123"


class TestRateLimiting:
    """Test rate limiting functionality."""

    def test_rate_limit_enforcement(self):
        """Test rate limit is enforced."""
        # First 100 events should pass
        for i in range(100):
            result = _check_rate_limit("test_hook")
            assert result is True

        # 101st event should fail
        result = _check_rate_limit("test_hook")
        assert result is False


class TestFileRotation:
    """Test file rotation functionality."""

    def test_rotation_needed_large_file(self, temp_events_dir):
        """Test rotation is triggered by large file size."""
        events_file = temp_events_dir / "events.jsonl"

        # Create file larger than 10MB
        with open(events_file, 'w') as f:
            f.write("x" * (11 * 1024 * 1024))  # 11MB

        assert _should_rotate_file(events_file) is True

    def test_rotation_needed_many_events(self, temp_events_dir):
        """Test rotation is triggered by event count."""
        events_file = temp_events_dir / "events.jsonl"

        # Create file with >10000 events
        with open(events_file, 'w') as f:
            for i in range(10001):
                f.write('{"event": "test"}\n')

        assert _should_rotate_file(events_file) is True

    def test_rotation_not_needed_small_file(self, temp_events_dir):
        """Test rotation is not triggered for small files."""
        events_file = temp_events_dir / "events.jsonl"

        # Create small file
        with open(events_file, 'w') as f:
            f.write('{"event": "test"}\n')

        assert _should_rotate_file(events_file) is False


class TestCaptureHookExecution:
    """Test capture_hook_execution convenience wrapper."""

    def test_capture_hook_execution(self, temp_events_dir, monkeypatch):
        """Test capture_hook_execution adds execution time."""
        import time

        monkeypatch.setattr("event_capture_utils.EVENTS_FILE", str(temp_events_dir / "events.jsonl"))

        start_time = time.time()
        result = capture_hook_execution(
            "test_hook",
            start_time,
            {"status": "success"}
        )

        assert result is True

        with open(temp_events_dir / "events.jsonl", 'r') as f:
            event = json.loads(f.read())

        assert "execution_time_ms" in event["object"]
        assert event["object"]["execution_time_ms"] >= 0


class TestCaptureHookError:
    """Test capture_hook_error convenience wrapper."""

    def test_capture_hook_error(self, temp_events_dir, monkeypatch):
        """Test capture_hook_error captures exception details."""
        import time

        monkeypatch.setattr("event_capture_utils.EVENTS_FILE", str(temp_events_dir / "events.jsonl"))

        start_time = time.time()
        error = ValueError("Test error")

        result = capture_hook_error(
            "test_hook",
            start_time,
            error
        )

        assert result is True

        with open(temp_events_dir / "events.jsonl", 'r') as f:
            event = json.loads(f.read())

        assert event["predicate"] == "failed"
        assert event["object"]["error_type"] == "ValueError"
        assert event["object"]["error_message"] == "Test error"
