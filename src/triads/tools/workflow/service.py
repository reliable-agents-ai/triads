"""Service layer for workflow tools.

Provides business logic for workflow instance operations.
"""

from typing import List, Optional

from triads.tools.workflow.domain import WorkflowInstance
from triads.tools.workflow.repository import AbstractWorkflowRepository

import logging

logger = logging.getLogger(__name__)



class WorkflowService:
    """Service for workflow operations.

    Orchestrates workflow instance management through repository layer.
    """

    def __init__(self, repository: AbstractWorkflowRepository):
        """Initialize workflow service.

        Args:
            repository: Workflow repository for data access
        """
        self.repository = repository

    def list_workflows(self, status: Optional[str] = None) -> List[WorkflowInstance]:
        """List workflow instances with optional status filter.

        Args:
            status: Optional status filter ("in_progress", "completed", "abandoned")

        Returns:
            List of WorkflowInstance objects

        Raises:
            WorkflowRepositoryError: If listing fails
        """
        return self.repository.list_workflows(status)

    def get_workflow(self, instance_id: str) -> WorkflowInstance:
        """Get detailed workflow instance information.

        Args:
            instance_id: Instance identifier

        Returns:
            WorkflowInstance with full details

        Raises:
            WorkflowRepositoryError: If instance not found
        """
        return self.repository.get_workflow(instance_id)
