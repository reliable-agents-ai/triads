"""Bootstrap utilities for router tools.

Provides factory functions for creating service instances with
appropriate repositories.
"""

from pathlib import Path
from typing import Optional

from triads.tools.router.repository import (
    FileSystemRouterRepository,
    InMemoryRouterRepository,
)
from triads.tools.router.service import RouterService


def bootstrap_router_service(
    use_filesystem: Optional[bool] = None,
    config_path: Optional[Path] = None,
    state_path: Optional[Path] = None,
) -> RouterService:
    """Create RouterService with appropriate repository.

    Args:
        use_filesystem: If True, use FileSystemRouterRepository (production).
                       If False, use InMemoryRouterRepository (testing).
                       If None (default), auto-detect based on config file existence.
        config_path: Path to router config.json (only used if use_filesystem=True)
        state_path: Path to router state file (only used if use_filesystem=True)

    Returns:
        RouterService configured with specified repository
    """
    # Auto-detect mode if not specified
    if use_filesystem is None:
        # Check if router config exists to determine mode
        from triads.router.router_paths import DEFAULT_PATHS

        default_config = config_path if config_path else DEFAULT_PATHS.config_file
        use_filesystem = Path(default_config).exists()

    if use_filesystem:
        repository = FileSystemRouterRepository(
            config_path=config_path, state_path=state_path
        )
    else:
        repository = InMemoryRouterRepository()

    return RouterService(repository)
