"""Tests for router tools repository layer."""

import pytest
from pathlib import Path

from triads.tools.router.domain import RoutingDecision, RouterState
from triads.tools.router.repository import (
    AbstractRouterRepository,
    InMemoryRouterRepository,
    RouterRepositoryError,
)


class TestInMemoryRouterRepository:
    """Tests for in-memory router repository."""

    def test_repository_creation(self):
        """InMemoryRouterRepository can be created."""
        repo = InMemoryRouterRepository()
        assert isinstance(repo, AbstractRouterRepository)

    def test_load_state_returns_default_when_empty(self):
        """load_state returns default state when no state exists."""
        repo = InMemoryRouterRepository()
        state = repo.load_state()

        assert isinstance(state, RouterState)
        assert state.current_triad is None
        assert state.session_id is not None  # Has generated session ID

    def test_save_and_load_state(self):
        """save_state and load_state work together."""
        repo = InMemoryRouterRepository()

        state = RouterState(
            current_triad="implementation",
            session_id="test-session-123",
            turn_count=5
        )

        repo.save_state(state)
        loaded = repo.load_state()

        assert loaded.current_triad == "implementation"
        assert loaded.session_id == "test-session-123"
        assert loaded.turn_count == 5

    def test_route_prompt_success(self):
        """route_prompt returns routing decision."""
        repo = InMemoryRouterRepository()

        # Set up mock routing result
        decision = RoutingDecision(
            triad="design",
            confidence=0.92,
            method="semantic"
        )

        # For in-memory, we simulate routing by directly returning decision
        # (Real implementation will wrap TriadRouter.route())
        result = repo.route_prompt("How should we architect this?")

        assert isinstance(result, RoutingDecision)
        assert result.triad in ["design", "implementation", "idea-validation", "garden-tending", "deployment"]
        assert 0.0 <= result.confidence <= 1.0
        assert result.method in ["semantic", "llm", "manual", "grace_period"]

    def test_route_prompt_with_empty_string_raises_error(self):
        """route_prompt raises error for empty prompt."""
        repo = InMemoryRouterRepository()

        with pytest.raises(RouterRepositoryError, match="Prompt cannot be empty"):
            repo.route_prompt("")

    def test_route_prompt_with_whitespace_only_raises_error(self):
        """route_prompt raises error for whitespace-only prompt."""
        repo = InMemoryRouterRepository()

        with pytest.raises(RouterRepositoryError, match="Prompt cannot be empty"):
            repo.route_prompt("   \n  \t  ")

    def test_state_persistence_across_operations(self):
        """State persists across multiple operations."""
        repo = InMemoryRouterRepository()

        # Save initial state
        state1 = RouterState(
            current_triad="design",
            session_id="session-abc",
            turn_count=2
        )
        repo.save_state(state1)

        # Route a prompt (doesn't affect state in in-memory version)
        repo.route_prompt("Let's implement OAuth")

        # State should still be accessible
        loaded = repo.load_state()
        assert loaded.current_triad == "design"
        assert loaded.turn_count == 2

    def test_updating_state(self):
        """State can be updated by saving new version."""
        repo = InMemoryRouterRepository()

        # Initial state
        state = RouterState(
            current_triad="implementation",
            session_id="session-xyz",
            turn_count=3
        )
        repo.save_state(state)

        # Update state
        state.turn_count = 4
        state.last_activity = "2025-10-23T10:30:00Z"
        repo.save_state(state)

        # Load and verify
        loaded = repo.load_state()
        assert loaded.turn_count == 4
        assert loaded.last_activity == "2025-10-23T10:30:00Z"


class TestAbstractRouterRepository:
    """Tests for abstract repository interface."""

    def test_cannot_instantiate_abstract_repository(self):
        """AbstractRouterRepository cannot be instantiated directly."""
        with pytest.raises(TypeError):
            AbstractRouterRepository()

    def test_abstract_methods_defined(self):
        """Abstract repository defines required methods."""
        assert hasattr(AbstractRouterRepository, 'route_prompt')
        assert hasattr(AbstractRouterRepository, 'load_state')
        assert hasattr(AbstractRouterRepository, 'save_state')
