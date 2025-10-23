"""Bootstrap utilities for workflow tools.

Provides factory functions for creating service instances with
appropriate repositories.
"""

from triads.tools.workflow.repository import InMemoryWorkflowRepository
from triads.tools.workflow.service import WorkflowService


def bootstrap_workflow_service() -> WorkflowService:
    """Create WorkflowService with appropriate repository.

    For now, uses InMemoryWorkflowRepository. In the future, this will
    be extended to use FileSystemWorkflowRepository that wraps the
    actual workflow_enforcement CLI functions.

    Returns:
        WorkflowService configured for testing
    """
    repository = InMemoryWorkflowRepository()
    return WorkflowService(repository)
