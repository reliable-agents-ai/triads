"""Tests for router tools service layer."""

import pytest

from triads.tools.router.domain import RoutingDecision, RouterState
from triads.tools.router.repository import InMemoryRouterRepository
from triads.tools.router.service import RouterService


class TestRouterService:
    """Tests for RouterService."""

    @pytest.fixture
    def service(self):
        """Create service with in-memory repository."""
        repo = InMemoryRouterRepository()
        return RouterService(repo)

    def test_route_prompt_returns_decision(self, service):
        """route_prompt returns RoutingDecision."""
        result = service.route_prompt("Let's implement OAuth2")

        assert isinstance(result, RoutingDecision)
        assert result.triad == "implementation"
        assert result.confidence > 0.8
        assert result.method == "semantic"

    def test_route_prompt_with_design_keywords(self, service):
        """route_prompt identifies design prompts."""
        result = service.route_prompt("How should we architect the database?")

        assert result.triad == "design"
        assert result.confidence > 0.8

    def test_get_current_triad_returns_none_when_no_state(self, service):
        """get_current_triad returns None when no active triad."""
        result = service.get_current_triad()

        assert isinstance(result, RouterState)
        assert result.current_triad is None

    def test_get_current_triad_returns_active_triad(self, service):
        """get_current_triad returns active triad when set."""
        # Set up state
        state = RouterState(
            current_triad="implementation",
            session_id="test-session",
            turn_count=3
        )
        service.repository.save_state(state)

        # Get current triad
        result = service.get_current_triad()

        assert result.current_triad == "implementation"
        assert result.turn_count == 3

    def test_route_prompt_validates_input(self, service):
        """route_prompt validates prompt input."""
        from triads.tools.router.repository import RouterRepositoryError

        with pytest.raises(RouterRepositoryError):
            service.route_prompt("")

    def test_service_uses_provided_repository(self):
        """Service uses the repository provided at initialization."""
        repo = InMemoryRouterRepository()
        service = RouterService(repo)

        assert service.repository is repo
