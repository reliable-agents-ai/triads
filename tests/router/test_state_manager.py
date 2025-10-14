"""Tests for router state management."""

import time
from datetime import datetime, timedelta

import pytest

from src.triads.router.state_manager import RouterState, RouterStateManager


class TestRouterState:
    """Test RouterState dataclass."""

    def test_default_state(self):
        """Test default state creation."""
        state = RouterState(session_id="test-123")

        assert state.session_id == "test-123"
        assert state.active_triad is None
        assert state.conversation_start is None
        assert state.turn_count == 0
        assert state.last_activity is None
        assert state.pending_intents == []
        assert state.training_mode_confirmations == 0

    def test_to_json(self):
        """Test JSON serialization."""
        state = RouterState(
            session_id="test-123",
            active_triad="design",
            turn_count=5,
            pending_intents=["research", "code"],
        )

        json_data = state.to_json()

        assert json_data["session_id"] == "test-123"
        assert json_data["active_triad"] == "design"
        assert json_data["turn_count"] == 5
        assert json_data["pending_intents"] == ["research", "code"]

    def test_from_json(self):
        """Test JSON deserialization."""
        data = {
            "session_id": "test-456",
            "active_triad": "implementation",
            "turn_count": 3,
            "pending_intents": ["debug"],
        }

        state = RouterState.from_json(data)

        assert state.session_id == "test-456"
        assert state.active_triad == "implementation"
        assert state.turn_count == 3
        assert state.pending_intents == ["debug"]

    def test_from_json_missing_fields(self):
        """Test JSON deserialization with missing fields uses defaults."""
        data = {"session_id": "test-789"}

        state = RouterState.from_json(data)

        assert state.session_id == "test-789"
        assert state.active_triad is None
        assert state.turn_count == 0
        assert state.pending_intents == []

    def test_from_json_extra_fields(self):
        """Test JSON deserialization ignores unknown fields."""
        data = {
            "session_id": "test-999",
            "unknown_field": "should be ignored",
            "another_unknown": 123,
        }

        state = RouterState.from_json(data)

        assert state.session_id == "test-999"
        assert not hasattr(state, "unknown_field")

    def test_is_within_grace_period_no_active_triad(self):
        """Test grace period check with no active triad."""
        state = RouterState(session_id="test")

        assert not state.is_within_grace_period()

    def test_is_within_grace_period_by_turns(self):
        """Test grace period satisfied by turn count."""
        state = RouterState(
            session_id="test",
            active_triad="design",
            conversation_start=datetime.utcnow().isoformat() + "Z",
            turn_count=3,
        )

        assert state.is_within_grace_period(grace_turns=5, grace_minutes=8)

    def test_is_within_grace_period_turns_exceeded(self):
        """Test grace period when turns exceeded but time is within limit."""
        # Start time 2 minutes ago
        start = datetime.utcnow() - timedelta(minutes=2)
        state = RouterState(
            session_id="test",
            active_triad="design",
            conversation_start=start.isoformat() + "Z",
            turn_count=10,  # Exceeds grace_turns
        )

        # Should still be within grace period due to time
        assert state.is_within_grace_period(grace_turns=5, grace_minutes=8)

    def test_is_within_grace_period_both_exceeded(self):
        """Test grace period when both turns and time exceeded."""
        # Start time 10 minutes ago
        start = datetime.utcnow() - timedelta(minutes=10)
        state = RouterState(
            session_id="test",
            active_triad="design",
            conversation_start=start.isoformat() + "Z",
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
        assert state.active_triad is None

    def test_save_and_load(self, temp_state_path):
        """Test basic save and load cycle."""
        manager = RouterStateManager(state_path=temp_state_path)

        # Create and save state
        state = RouterState(
            session_id="test-session",
            active_triad="implementation",
            turn_count=7,
        )
        manager.save(state)

        # Load and verify
        loaded = manager.load()
        assert loaded.session_id == "test-session"
        assert loaded.active_triad == "implementation"
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
        assert state.active_triad is None

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
        before = datetime.utcnow()

        updated = manager.update_activity(state)

        after = datetime.utcnow()

        # Verify timestamp is recent
        activity_time = datetime.fromisoformat(
            updated.last_activity.replace("Z", "+00:00")
        )
        before_with_tz = before.replace(tzinfo=activity_time.tzinfo)
        after_with_tz = after.replace(tzinfo=activity_time.tzinfo)
        assert before_with_tz <= activity_time <= after_with_tz

    def test_activate_triad(self, temp_state_path):
        """Test triad activation."""
        manager = RouterStateManager(state_path=temp_state_path)

        state = RouterState(session_id="test")
        activated = manager.activate_triad(state, "design")

        assert activated.active_triad == "design"
        assert activated.turn_count == 0
        assert activated.conversation_start is not None
        assert activated.last_activity is not None

    def test_increment_turn(self, temp_state_path):
        """Test turn counter increment."""
        manager = RouterStateManager(state_path=temp_state_path)

        state = RouterState(session_id="test", turn_count=5)
        incremented = manager.increment_turn(state)

        assert incremented.turn_count == 6
        assert incremented.last_activity is not None

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
