"""Service layer for router tools.

Provides business logic for routing and state management operations.
"""

from triads.tools.router.domain import RoutingDecision, RouterState
from triads.tools.router.repository import AbstractRouterRepository


class RouterService:
    """Service for router operations.

    Orchestrates routing and state management through repository layer.
    """

    def __init__(self, repository: AbstractRouterRepository):
        """Initialize router service.

        Args:
            repository: Router repository for data access
        """
        self.repository = repository

    def route_prompt(self, prompt: str) -> RoutingDecision:
        """Route a user prompt to appropriate triad.

        Args:
            prompt: User's input prompt

        Returns:
            RoutingDecision with triad, confidence, and method

        Raises:
            RouterRepositoryError: If routing fails or prompt is invalid
        """
        return self.repository.route_prompt(prompt)

    def get_current_triad(self) -> RouterState:
        """Get current router state including active triad.

        Returns:
            RouterState with current triad and session information
        """
        return self.repository.load_state()
