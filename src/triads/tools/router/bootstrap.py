"""Bootstrap utilities for router tools.

Provides factory functions for creating service instances with
appropriate repositories.
"""

from triads.tools.router.repository import InMemoryRouterRepository
from triads.tools.router.service import RouterService


def bootstrap_router_service() -> RouterService:
    """Create RouterService with appropriate repository.

    For now, uses InMemoryRouterRepository. In the future, this will
    be extended to use FileSystemRouterRepository that wraps the
    actual TriadRouter and RouterStateManager.

    Returns:
        RouterService configured for testing
    """
    repository = InMemoryRouterRepository()
    return RouterService(repository)
