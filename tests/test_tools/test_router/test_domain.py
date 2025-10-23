"""Tests for router tools domain models."""

import pytest
from dataclasses import asdict

from triads.tools.router.domain import RoutingDecision, RouterState


class TestRoutingDecision:
    """Tests for RoutingDecision dataclass."""

    def test_routing_decision_creation(self):
        """RoutingDecision can be created with required fields."""
        decision = RoutingDecision(
            triad="implementation",
            confidence=0.92,
            method="semantic"
        )

        assert decision.triad == "implementation"
        assert decision.confidence == 0.92
        assert decision.method == "semantic"

    def test_routing_decision_with_optional_reasoning(self):
        """RoutingDecision supports optional reasoning field."""
        decision = RoutingDecision(
            triad="design",
            confidence=0.85,
            method="llm",
            reasoning="LLM selected design based on architectural keywords"
        )

        assert decision.reasoning == "LLM selected design based on architectural keywords"

    def test_routing_decision_defaults_reasoning_to_none(self):
        """RoutingDecision defaults reasoning to None."""
        decision = RoutingDecision(
            triad="implementation",
            confidence=0.90,
            method="semantic"
        )

        assert decision.reasoning is None

    def test_routing_decision_to_dict(self):
        """RoutingDecision can be converted to dictionary."""
        decision = RoutingDecision(
            triad="garden-tending",
            confidence=0.88,
            method="manual"
        )

        data = asdict(decision)
        assert data["triad"] == "garden-tending"
        assert data["confidence"] == 0.88
        assert data["method"] == "manual"


class TestRouterState:
    """Tests for RouterState dataclass."""

    def test_router_state_creation(self):
        """RouterState can be created with required fields."""
        state = RouterState(
            current_triad="implementation",
            session_id="test-session-123"
        )

        assert state.current_triad == "implementation"
        assert state.session_id == "test-session-123"

    def test_router_state_with_turn_count(self):
        """RouterState tracks turn count."""
        state = RouterState(
            current_triad="design",
            session_id="session-456",
            turn_count=3
        )

        assert state.turn_count == 3

    def test_router_state_defaults_turn_count_to_zero(self):
        """RouterState defaults turn_count to 0."""
        state = RouterState(
            current_triad="implementation",
            session_id="session-789"
        )

        assert state.turn_count == 0

    def test_router_state_with_timestamps(self):
        """RouterState tracks conversation timestamps."""
        state = RouterState(
            current_triad="deployment",
            session_id="session-abc",
            conversation_start="2025-10-23T10:00:00Z",
            last_activity="2025-10-23T10:05:00Z"
        )

        assert state.conversation_start == "2025-10-23T10:00:00Z"
        assert state.last_activity == "2025-10-23T10:05:00Z"

    def test_router_state_to_dict(self):
        """RouterState can be converted to dictionary."""
        state = RouterState(
            current_triad="idea-validation",
            session_id="session-xyz",
            turn_count=2
        )

        data = asdict(state)
        assert data["current_triad"] == "idea-validation"
        assert data["session_id"] == "session-xyz"
        assert data["turn_count"] == 2
