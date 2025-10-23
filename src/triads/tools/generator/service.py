"""Service layer for generator tools.

Provides business logic for agent generation operations.
"""

from typing import List

from triads.tools.generator.domain import AgentDefinition
from triads.tools.generator.repository import AbstractGeneratorRepository

import logging

logger = logging.getLogger(__name__)



class GeneratorService:
    """Service for generator operations.

    Orchestrates agent generation through repository layer.
    """

    def __init__(self, repository: AbstractGeneratorRepository):
        """Initialize generator service.

        Args:
            repository: Generator repository for data access
        """
        self.repository = repository

    def generate_agents(self, workflow_type: str, domain: str) -> List[AgentDefinition]:
        """Generate agent definitions for a workflow.

        Args:
            workflow_type: Type of workflow (e.g., "debugging")
            domain: Domain description for context

        Returns:
            List of AgentDefinition objects

        Raises:
            GeneratorRepositoryError: If generation fails
        """
        return self.repository.generate_agents(workflow_type, domain)
