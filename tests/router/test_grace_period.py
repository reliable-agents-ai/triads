"""Tests for grace period enforcement."""

import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from triads.tools.router._grace_period import GracePeriodChecker
from triads.tools.router._state_manager import _RouterStateManager as RouterStateManager
from triads.tools.router.domain import RouterState


class TestGracePeriodChecker:
    """Test grace period enforcement logic."""

    @pytest.fixture
    def state_manager(self):
        """Create state manager with temporary file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "router_state.json"
            yield RouterStateManager(state_path=state_path)

    @pytest.fixture
    def checker(self, state_manager):
        """Create grace period checker."""
        return GracePeriodChecker(
            state_manager=state_manager,
            grace_turns=5,
            grace_minutes=8,
        )

    def test_init_custom_thresholds(self, state_manager):
        """Test initialization with custom thresholds."""
        checker = GracePeriodChecker(
            state_manager=state_manager,
            grace_turns=10,
            grace_minutes=15,
        )

        assert checker.grace_turns == 10
        assert checker.grace_minutes == 15

    def test_is_within_grace_period_no_current_triad(self, checker):
        """Test grace period returns False when no active triad."""
        state = RouterState(session_id="test-123")

        assert not checker.is_within_grace_period(state)

    def test_is_within_grace_period_by_turns(self, checker):
        """Test grace period satisfied by turn count."""
        state = RouterState(
            session_id="test-123",
            current_triad="design",
            turn_count=3,
            last_activity=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        )

        assert checker.is_within_grace_period(state)

    def test_is_within_grace_period_turns_at_threshold(self, checker):
        """Test grace period when turn count equals threshold."""
        state = RouterState(
            session_id="test-123",
            current_triad="design",
            turn_count=5,  # Equal to grace_turns
            last_activity=(
                datetime.now(timezone.utc) - timedelta(minutes=10)
            ).isoformat().replace("+00:00", "Z"),
        )

        # Should be False - turns >= grace_turns and time expired
        assert not checker.is_within_grace_period(state)

    def test_is_within_grace_period_by_time(self, checker):
        """Test grace period satisfied by time."""
        state = RouterState(
            session_id="test-123",
            current_triad="design",
            turn_count=10,  # Turns exceeded
            last_activity=(datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat().replace("+00:00", "Z"),
        )

        # Should be True - time is within grace_minutes
        assert checker.is_within_grace_period(state)

    def test_is_within_grace_period_time_at_threshold(self, checker):
        """Test grace period when time equals threshold."""
        state = RouterState(
            session_id="test-123",
            current_triad="design",
            turn_count=10,
            last_activity=(datetime.now(timezone.utc) - timedelta(minutes=8)).isoformat()
            + "Z",
        )

        # Should be False - time >= grace_minutes and turns exceeded
        # Note: Depending on exact timing, this might be flaky
        # We check both are expired
        assert not checker.is_within_grace_period(state)

    def test_is_within_grace_period_both_exceeded(self, checker):
        """Test grace period when both turn and time exceeded."""
        state = RouterState(
            session_id="test-123",
            current_triad="design",
            turn_count=10,
            last_activity=(
                datetime.now(timezone.utc) - timedelta(minutes=15)
            ).isoformat()
            + "Z",
        )

        assert not checker.is_within_grace_period(state)

    def test_is_within_grace_period_invalid_timestamp(self, checker):
        """Test grace period with invalid timestamp."""
        state = RouterState(
            session_id="test-123",
            current_triad="design",
            turn_count=10,
            last_activity="invalid-timestamp",
        )

        # Invalid timestamp should be treated as expired
        assert not checker.is_within_grace_period(state)

    def test_get_grace_period_status_no_current_triad(self, checker):
        """Test status with no active triad."""
        state = RouterState(session_id="test-123")

        status = checker.get_grace_period_status(state)

        assert not status["active"]
        assert status["reason"] == "none"

    def test_get_grace_period_status_turns_active(self, checker):
        """Test status when turns are active."""
        state = RouterState(
            session_id="test-123",
            current_triad="design",
            turn_count=3,
            last_activity=(
                datetime.now(timezone.utc) - timedelta(minutes=10)
            ).isoformat()
            + "Z",
        )

        status = checker.get_grace_period_status(state)

        assert status["active"]
        assert status["turns_remaining"] == 2  # 5 - 3
        assert status["minutes_remaining"] == 0.0  # Time expired
        assert status["reason"] == "turns"

    def test_get_grace_period_status_time_active(self, checker):
        """Test status when time is active."""
        state = RouterState(
            session_id="test-123",
            current_triad="design",
            turn_count=10,
            last_activity=(datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat().replace("+00:00", "Z"),
        )

        status = checker.get_grace_period_status(state)

        assert status["active"]
        assert status["turns_remaining"] == 0
        assert status["minutes_remaining"] > 0
        assert status["minutes_remaining"] <= 3  # ~3 minutes remaining
        assert status["reason"] == "time"

    def test_get_grace_period_status_both_active(self, checker):
        """Test status when both turn and time are active."""
        state = RouterState(
            session_id="test-123",
            current_triad="design",
            turn_count=3,
            last_activity=(datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat().replace("+00:00", "Z"),
        )

        status = checker.get_grace_period_status(state)

        assert status["active"]
        assert status["turns_remaining"] > 0
        assert status["minutes_remaining"] > 0
        assert status["reason"] == "both"

    def test_get_grace_period_status_neither_active(self, checker):
        """Test status when neither turn nor time are active."""
        state = RouterState(
            session_id="test-123",
            current_triad="design",
            turn_count=10,
            last_activity=(
                datetime.now(timezone.utc) - timedelta(minutes=15)
            ).isoformat()
            + "Z",
        )

        status = checker.get_grace_period_status(state)

        assert not status["active"]
        assert status["turns_remaining"] == 0
        assert status["minutes_remaining"] == 0
        assert status["reason"] == "none"

    def test_should_bypass_grace_period_explicit_command(self, checker):
        """Test bypass with explicit /switch-triad command."""
        state = RouterState(session_id="test-123", current_triad="design")

        should_bypass, reason = checker.should_bypass_grace_period(
            "/switch-triad implementation", state
        )

        assert should_bypass
        assert reason == "explicit_switch_command"

    def test_should_bypass_grace_period_lets_switch_to(self, checker):
        """Test bypass with 'let's switch to' phrase."""
        state = RouterState(session_id="test-123", current_triad="design")

        should_bypass, reason = checker.should_bypass_grace_period(
            "Let's switch to implementation now", state
        )

        assert should_bypass
        assert reason == "explicit_transition_phrase"

    def test_should_bypass_grace_period_lets_move_to(self, checker):
        """Test bypass with 'let's move to' phrase."""
        state = RouterState(session_id="test-123", current_triad="design")

        should_bypass, reason = checker.should_bypass_grace_period(
            "Now let's move to deployment", state
        )

        assert should_bypass
        assert reason == "explicit_transition_phrase"

    def test_should_bypass_grace_period_now_lets(self, checker):
        """Test bypass with 'now let's' phrase."""
        state = RouterState(session_id="test-123", current_triad="design")

        should_bypass, reason = checker.should_bypass_grace_period(
            "Great! Now let's build it", state
        )

        assert should_bypass
        assert reason == "explicit_transition_phrase"

    def test_should_bypass_grace_period_can_we_switch(self, checker):
        """Test bypass with 'can we switch to' phrase."""
        state = RouterState(session_id="test-123", current_triad="design")

        should_bypass, reason = checker.should_bypass_grace_period(
            "Can we switch to implementation?", state
        )

        assert should_bypass
        assert reason == "explicit_transition_phrase"

    def test_should_bypass_grace_period_i_want_to_switch(self, checker):
        """Test bypass with 'i want to switch to' phrase."""
        state = RouterState(session_id="test-123", current_triad="design")

        should_bypass, reason = checker.should_bypass_grace_period(
            "I want to switch to deployment", state
        )

        assert should_bypass
        assert reason == "explicit_transition_phrase"

    def test_should_bypass_grace_period_and_then(self, checker):
        """Test bypass with 'and then' multi-intent."""
        state = RouterState(session_id="test-123", current_triad="design")

        should_bypass, reason = checker.should_bypass_grace_period(
            "Let's finalize the design and then start coding", state
        )

        assert should_bypass
        assert reason == "multi_intent_detected"

    def test_should_bypass_grace_period_then(self, checker):
        """Test bypass with 'then' multi-intent."""
        state = RouterState(session_id="test-123", current_triad="design")

        should_bypass, reason = checker.should_bypass_grace_period(
            "Complete the ADR then implement it", state
        )

        assert should_bypass
        assert reason == "multi_intent_detected"

    def test_should_bypass_grace_period_normal_prompt(self, checker):
        """Test no bypass for normal prompt."""
        state = RouterState(session_id="test-123", current_triad="design")

        should_bypass, reason = checker.should_bypass_grace_period(
            "What should we consider in the design?", state
        )

        assert not should_bypass
        assert reason == "normal_prompt"

    def test_should_bypass_grace_period_case_insensitive(self, checker):
        """Test bypass detection is case insensitive."""
        state = RouterState(session_id="test-123", current_triad="design")

        should_bypass, reason = checker.should_bypass_grace_period(
            "LET'S SWITCH TO IMPLEMENTATION", state
        )

        assert should_bypass
        assert reason == "explicit_transition_phrase"

    def test_reset_grace_period(self, checker):
        """Test resetting grace period for new triad."""
        state = RouterState(
            session_id="test-123",
            current_triad="design",
            turn_count=10,
            last_activity="2024-01-01T10:00:00Z",
            conversation_start="2024-01-01T09:00:00Z",
        )

        new_state = checker.reset_grace_period(state, "implementation")

        assert new_state.current_triad == "implementation"
        assert new_state.turn_count == 1
        # Check timestamps are recent (within last second)
        assert new_state.last_activity is not None
        assert new_state.conversation_start is not None

        last_activity_dt = datetime.fromisoformat(
            new_state.last_activity.replace("Z", "+00:00")
        )
        conversation_start_dt = datetime.fromisoformat(
            new_state.conversation_start.replace("Z", "+00:00")
        )

        now = datetime.now(last_activity_dt.tzinfo)
        assert (now - last_activity_dt).total_seconds() < 2
        assert (now - conversation_start_dt).total_seconds() < 2

    def test_reset_grace_period_updates_all_fields(self, checker):
        """Test reset updates all relevant fields."""
        state = RouterState(
            session_id="test-123",
            current_triad="design",
            turn_count=10,
        )

        new_state = checker.reset_grace_period(state, "deployment")

        assert new_state.current_triad == "deployment"
        assert new_state.turn_count == 1
        assert new_state.last_activity == new_state.conversation_start
        assert new_state.session_id == "test-123"  # Unchanged
