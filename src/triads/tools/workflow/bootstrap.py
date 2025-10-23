"""Bootstrap utilities for workflow tools.

Provides factory functions for creating service instances with
appropriate repositories.
"""

from pathlib import Path
from typing import Optional

from triads.tools.workflow.repository import (
    FileSystemWorkflowRepository,
    InMemoryWorkflowRepository,
)
from triads.tools.workflow.service import WorkflowService


def bootstrap_workflow_service(
    use_filesystem: bool = True,
    base_dir: Optional[Path] = None
) -> WorkflowService:
    """Create WorkflowService with appropriate repository.

    Args:
        use_filesystem: If True, use filesystem repository (default).
                       If False, use in-memory repository (for testing).
        base_dir: Base directory for filesystem repository (default: .claude/workflows)

    Returns:
        WorkflowService configured with requested repository
    """
    if use_filesystem:
        repository = FileSystemWorkflowRepository(base_dir=base_dir)
    else:
        repository = InMemoryWorkflowRepository()

    return WorkflowService(repository)
