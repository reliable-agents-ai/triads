"""Bootstrap utilities for generator tools.

Provides factory functions for creating service instances with
appropriate repositories.
"""

from triads.tools.generator.repository import InMemoryGeneratorRepository
from triads.tools.generator.service import GeneratorService

import logging

logger = logging.getLogger(__name__)



def bootstrap_generator_service() -> GeneratorService:
    """Create GeneratorService with appropriate repository.

    For now, uses InMemoryGeneratorRepository. In the future, this will
    be extended to use a repository that wraps the actual generator modules.

    Returns:
        GeneratorService configured for testing
    """
    repository = InMemoryGeneratorRepository()
    return GeneratorService(repository)
