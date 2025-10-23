"""Repository layer for workflow tools.

Abstracts access to workflow instance functionality.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from triads.tools.workflow.domain import WorkflowInstance, WorkflowStatus, TriadCompletion


class WorkflowRepositoryError(Exception):
    """Base exception for workflow repository errors."""
    pass


class AbstractWorkflowRepository(ABC):
    """Abstract interface for workflow repositories.

    Defines the contract for accessing workflow instance functionality.
    """

    @abstractmethod
    def list_workflows(self, status: Optional[str] = None) -> List[WorkflowInstance]:
        """List workflow instances with optional status filter.

        Args:
            status: Optional status filter ("in_progress", "completed", "abandoned")

        Returns:
            List of WorkflowInstance objects

        Raises:
            WorkflowRepositoryError: If listing fails
        """
        pass

    @abstractmethod
    def get_workflow(self, instance_id: str) -> WorkflowInstance:
        """Get detailed workflow instance information.

        Args:
            instance_id: Instance identifier

        Returns:
            WorkflowInstance with full details

        Raises:
            WorkflowRepositoryError: If instance not found or retrieval fails
        """
        pass


class InMemoryWorkflowRepository(AbstractWorkflowRepository):
    """In-memory workflow repository for testing.

    Provides simplified workflow instance management without
    external dependencies. Used for unit testing.
    """

    def __init__(self):
        """Initialize in-memory repository with sample data."""
        self._instances = {
            "feature-oauth2-20251023-100523": WorkflowInstance(
                instance_id="feature-oauth2-20251023-100523",
                workflow_type="software-development",
                status=WorkflowStatus.IN_PROGRESS,
                title="OAuth2 Integration",
                current_triad="implementation",
                completed_triads=[
                    TriadCompletion(
                        triad_id="idea-validation",
                        completed_at="2025-10-23T09:00:00Z",
                        duration_minutes=30.0
                    ),
                    TriadCompletion(
                        triad_id="design",
                        completed_at="2025-10-23T10:00:00Z",
                        duration_minutes=45.0
                    )
                ],
                started_at="2025-10-23T08:30:00Z"
            ),
            "feature-search-20251022-143000": WorkflowInstance(
                instance_id="feature-search-20251022-143000",
                workflow_type="software-development",
                status=WorkflowStatus.COMPLETED,
                title="Search Feature",
                current_triad=None,  # Completed, no current triad
                completed_triads=[
                    TriadCompletion(
                        triad_id="implementation",
                        completed_at="2025-10-22T15:00:00Z",
                        duration_minutes=60.0
                    ),
                    TriadCompletion(
                        triad_id="garden-tending",
                        completed_at="2025-10-22T16:00:00Z",
                        duration_minutes=30.0
                    )
                ],
                started_at="2025-10-22T14:00:00Z"
            ),
            "experiment-ml-20251020-090000": WorkflowInstance(
                instance_id="experiment-ml-20251020-090000",
                workflow_type="research",
                status=WorkflowStatus.ABANDONED,
                title="ML Experiment",
                current_triad=None,
                completed_triads=[],
                started_at="2025-10-20T09:00:00Z"
            )
        }

    def list_workflows(self, status: Optional[str] = None) -> List[WorkflowInstance]:
        """List workflow instances with optional status filter.

        Args:
            status: Optional status filter

        Returns:
            List of WorkflowInstance objects
        """
        instances = list(self._instances.values())

        if status:
            # Convert string to WorkflowStatus enum
            try:
                status_enum = WorkflowStatus(status)
                instances = [i for i in instances if i.status == status_enum]
            except ValueError:
                raise WorkflowRepositoryError(
                    f"Invalid status '{status}'. Must be one of: in_progress, completed, abandoned"
                )

        return instances

    def get_workflow(self, instance_id: str) -> WorkflowInstance:
        """Get detailed workflow instance information.

        Args:
            instance_id: Instance identifier

        Returns:
            WorkflowInstance with full details

        Raises:
            WorkflowRepositoryError: If instance not found
        """
        if not instance_id or not isinstance(instance_id, str):
            raise WorkflowRepositoryError(
                "Valid instance ID required (must be non-empty string)"
            )

        instance = self._instances.get(instance_id)
        if instance is None:
            raise WorkflowRepositoryError(
                f"Workflow instance not found: {instance_id}"
            )

        return instance
