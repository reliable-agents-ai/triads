"""Repository layer for router tools.

Abstracts access to routing and state management functionality.
"""

import uuid
from abc import ABC, abstractmethod
from typing import Optional

from triads.tools.router.domain import RoutingDecision, RouterState


class RouterRepositoryError(Exception):
    """Base exception for router repository errors."""
    pass


class AbstractRouterRepository(ABC):
    """Abstract interface for router repositories.

    Defines the contract for accessing routing and state functionality.
    """

    @abstractmethod
    def route_prompt(self, prompt: str) -> RoutingDecision:
        """Route a user prompt to appropriate triad.

        Args:
            prompt: User's input prompt

        Returns:
            RoutingDecision with triad, confidence, method

        Raises:
            RouterRepositoryError: If routing fails
        """
        pass

    @abstractmethod
    def load_state(self) -> RouterState:
        """Load current router state.

        Returns:
            RouterState with current triad and session information
        """
        pass

    @abstractmethod
    def save_state(self, state: RouterState) -> None:
        """Save router state.

        Args:
            state: RouterState to persist
        """
        pass


class InMemoryRouterRepository(AbstractRouterRepository):
    """In-memory router repository for testing.

    Provides simplified routing and state management without
    external dependencies. Used for unit testing.
    """

    def __init__(self):
        """Initialize in-memory repository."""
        self._state: Optional[RouterState] = None
        self._triads = [
            "idea-validation",
            "design",
            "implementation",
            "garden-tending",
            "deployment"
        ]

    def route_prompt(self, prompt: str) -> RoutingDecision:
        """Route prompt using simple keyword matching.

        Args:
            prompt: User's input prompt

        Returns:
            RoutingDecision based on keyword matching

        Raises:
            RouterRepositoryError: If prompt is empty
        """
        if not prompt or not prompt.strip():
            raise RouterRepositoryError("Prompt cannot be empty")

        prompt_lower = prompt.lower()

        # Simple keyword-based routing for testing
        if any(kw in prompt_lower for kw in ["idea", "validate", "research"]):
            return RoutingDecision(
                triad="idea-validation",
                confidence=0.90,
                method="semantic"
            )
        elif any(kw in prompt_lower for kw in ["design", "architect", "should we"]):
            return RoutingDecision(
                triad="design",
                confidence=0.92,
                method="semantic"
            )
        elif any(kw in prompt_lower for kw in ["implement", "build", "create", "write"]):
            return RoutingDecision(
                triad="implementation",
                confidence=0.88,
                method="semantic"
            )
        elif any(kw in prompt_lower for kw in ["refactor", "clean", "improve", "tending"]):
            return RoutingDecision(
                triad="garden-tending",
                confidence=0.85,
                method="semantic"
            )
        elif any(kw in prompt_lower for kw in ["deploy", "release", "publish"]):
            return RoutingDecision(
                triad="deployment",
                confidence=0.87,
                method="semantic"
            )
        else:
            # Default to implementation with lower confidence
            return RoutingDecision(
                triad="implementation",
                confidence=0.70,
                method="semantic"
            )

    def load_state(self) -> RouterState:
        """Load router state from memory.

        Returns:
            RouterState (default state if none exists)
        """
        if self._state is None:
            # Create default state
            self._state = RouterState(
                current_triad=None,
                session_id=str(uuid.uuid4())
            )
        return self._state

    def save_state(self, state: RouterState) -> None:
        """Save router state to memory.

        Args:
            state: RouterState to save
        """
        self._state = state
