"""Tests for router state management."""

import time
from datetime import datetime, timedelta, timezone

import pytest

from triads.tools.router._state_manager import _RouterStateManager as RouterStateManager
from triads.tools.router.domain import RouterState


class TestRouterState:
    """Test RouterState dataclass."""

    def test_default_state(self):
        """Test default state creation."""
        state = RouterState(session_id="test-123")

        assert state.session_id == "test-123"
        assert state.current_triad is None
        assert state.conversation_start is None
        assert state.turn_count == 0
        assert state.last_activity is None
        assert state.training_mode is False
        assert state.training_confirmations == 0

    def test_to_json(self):
        """Test JSON serialization."""
        state = RouterState(
            session_id="test-123",
            current_triad="design",
            turn_count=5,
        )

        json_data = state.to_dict()

        assert json_data["session_id"] == "test-123"
        assert json_data["current_triad"] == "design"
        assert json_data["turn_count"] == 5

    def test_from_json(self):
        """Test JSON deserialization."""
        data = {
            "session_id": "test-456",
            "current_triad": "implementation",
            "turn_count": 3,
        }

        state = RouterState.from_dict(data)

        assert state.session_id == "test-456"
        assert state.current_triad == "implementation"
        assert state.turn_count == 3

    def test_from_json_missing_fields(self):
        """Test JSON deserialization with missing fields uses defaults."""
        data = {"session_id": "test-789"}

        state = RouterState.from_dict(data)

        assert state.session_id == "test-789"
        assert state.current_triad is None
        assert state.turn_count == 0

    def test_from_json_extra_fields(self):
        """Test JSON deserialization ignores unknown fields."""
        data = {
            "session_id": "test-999",
            "unknown_field": "should be ignored",
            "another_unknown": 123,
        }

        state = RouterState.from_dict(data)

        assert state.session_id == "test-999"
        assert not hasattr(state, "unknown_field")

    def test_is_within_grace_period_no_current_triad(self):
        """Test grace period check with no active triad."""
        state = RouterState(session_id="test")

        assert not state.is_within_grace_period()

    def test_is_within_grace_period_by_turns(self):
        """Test grace period satisfied by turn count."""
        state = RouterState(
            session_id="test",
            current_triad="design",
            conversation_start=datetime.now(timezone.utc).isoformat() + "Z",
            turn_count=3,
        )

        assert state.is_within_grace_period(grace_turns=5, grace_minutes=8)

    def test_is_within_grace_period_turns_exceeded(self):
        """Test grace period when turns exceeded but time is within limit."""
        # Last activity 2 minutes ago
        last = datetime.now(timezone.utc) - timedelta(minutes=2)
        state = RouterState(
            session_id="test",
            current_triad="design",
            conversation_start=datetime.now(timezone.utc).isoformat() + "Z",
            last_activity=last.isoformat().replace("+00:00", "Z"),
            turn_count=10,  # Exceeds grace_turns
        )

        # Should still be within grace period due to time
        assert state.is_within_grace_period(grace_turns=5, grace_minutes=8)

    def test_is_within_grace_period_both_exceeded(self):
        """Test grace period when both turns and time exceeded."""
        # Last activity 10 minutes ago
        last = datetime.now(timezone.utc) - timedelta(minutes=10)
        state = RouterState(
            session_id="test",
            current_triad="design",
            conversation_start=datetime.now(timezone.utc).isoformat() + "Z",
            last_activity=last.isoformat().replace("+00:00", "Z"),
            turn_count=10,  # Exceeds grace_turns
        )

        # Should be outside grace period
        assert not state.is_within_grace_period(grace_turns=5, grace_minutes=8)


class TestRouterStateManager:
    """Test RouterStateManager file operations."""

    @pytest.fixture
    def temp_state_path(self, tmp_path):
        """Create temporary state file path."""
        return tmp_path / "test_router_state.json"

    def test_load_nonexistent_file(self, temp_state_path):
        """Test loading when state file doesn't exist."""
        manager = RouterStateManager(state_path=temp_state_path)

        state = manager.load()

        assert state.session_id  # Should have generated UUID
        assert state.current_triad is None

    def test_save_and_load(self, temp_state_path):
        """Test basic save and load cycle."""
        manager = RouterStateManager(state_path=temp_state_path)

        # Create and save state
        state = RouterState(
            session_id="test-session",
            current_triad="implementation",
            turn_count=7,
        )
        manager.save(state)

        # Load and verify
        loaded = manager.load()
        assert loaded.session_id == "test-session"
        assert loaded.current_triad == "implementation"
        assert loaded.turn_count == 7

    def test_save_creates_directory(self, tmp_path):
        """Test that save creates parent directory if needed."""
        nested_path = tmp_path / "nested" / "dir" / "state.json"
        manager = RouterStateManager(state_path=nested_path)

        state = RouterState(session_id="test")
        manager.save(state)

        assert nested_path.exists()
        assert nested_path.parent.exists()

    def test_load_corrupted_json(self, temp_state_path):
        """Test loading corrupted JSON resets to default."""
        # Write corrupted JSON
        temp_state_path.write_text("{ invalid json }")

        manager = RouterStateManager(state_path=temp_state_path)
        state = manager.load()

        # Should get default state
        assert state.session_id  # New UUID generated
        assert state.current_triad is None

    def test_reset(self, temp_state_path):
        """Test state reset deletes file."""
        manager = RouterStateManager(state_path=temp_state_path)

        # Create state
        state = RouterState(session_id="test")
        manager.save(state)
        assert temp_state_path.exists()

        # Reset
        manager.reset()
        assert not temp_state_path.exists()

    def test_update_activity(self, temp_state_path):
        """Test activity timestamp update."""
        manager = RouterStateManager(state_path=temp_state_path)

        state = RouterState(session_id="test")
        before = datetime.now(timezone.utc)

        # update_activity is now a domain method on RouterState
        state.update_activity()

        after = datetime.now(timezone.utc)

        # Verify timestamp is recent
        activity_time = datetime.fromisoformat(
            state.last_activity.replace("Z", "+00:00")
        )
        assert before <= activity_time <= after

    def test_activate_triad(self, temp_state_path):
        """Test triad activation."""
        from triads.tools.router._timestamp_utils import utc_now_iso

        manager = RouterStateManager(state_path=temp_state_path)

        # Triad activation is now handled in service/repository layer
        # Create state with activated triad
        state = RouterState(
            session_id="test",
            current_triad="design",
            turn_count=0,
            conversation_start=utc_now_iso(),
            last_activity=utc_now_iso()
        )

        # Save and verify persistence
        manager.save(state)
        loaded = manager.load()

        assert loaded.current_triad == "design"
        assert loaded.turn_count == 0
        assert loaded.conversation_start is not None
        assert loaded.last_activity is not None

    def test_increment_turn(self, temp_state_path):
        """Test turn counter increment."""
        manager = RouterStateManager(state_path=temp_state_path)

        state = RouterState(session_id="test", turn_count=5)

        # Turn increment is handled by update_activity() domain method
        state.update_activity()

        assert state.turn_count == 6
        assert state.last_activity is not None

    def test_concurrent_access(self, temp_state_path):
        """Test concurrent read/write doesn't corrupt state."""
        import threading

        manager = RouterStateManager(state_path=temp_state_path)
        errors = []

        def writer():
            """Write state multiple times."""
            try:
                for i in range(10):
                    state = RouterState(session_id=f"writer-{i}", turn_count=i)
                    manager.save(state)
                    time.sleep(0.001)
            except Exception as e:
                errors.append(e)

        def reader():
            """Read state multiple times."""
            try:
                for _ in range(10):
                    state = manager.load()
                    assert state.session_id is not None
                    time.sleep(0.001)
            except Exception as e:
                errors.append(e)

        # Run concurrent operations with threading (simpler than multiprocessing)
        writer_thread = threading.Thread(target=writer)
        reader_thread = threading.Thread(target=reader)

        writer_thread.start()
        reader_thread.start()

        writer_thread.join(timeout=5)
        reader_thread.join(timeout=5)

        # Verify no errors occurred
        assert not errors, f"Concurrent access errors: {errors}"

        # Verify final state is valid
        final_state = manager.load()
        assert final_state.session_id is not None
