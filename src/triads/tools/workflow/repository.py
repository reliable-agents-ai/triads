"""Repository layer for workflow tools.

Abstracts access to workflow instance functionality.
"""

import json
import logging
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

from triads.tools.workflow.domain import (
    WorkflowInstance,
    WorkflowStatus,
    TriadCompletion,
    WorkflowDeviation,
)
from triads.utils.file_operations import atomic_read_json

logger = logging.getLogger(__name__)


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
                started_at="2025-10-23T08:30:00Z",
                started_by="test@example.com"
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
                started_at="2025-10-22T14:00:00Z",
                completed_at="2025-10-22T16:30:00Z",
                started_by="test@example.com"
            ),
            "experiment-ml-20251020-090000": WorkflowInstance(
                instance_id="experiment-ml-20251020-090000",
                workflow_type="research",
                status=WorkflowStatus.ABANDONED,
                title="ML Experiment",
                current_triad=None,
                completed_triads=[],
                started_at="2025-10-20T09:00:00Z",
                abandoned_at="2025-10-20T11:00:00Z",
                started_by="test@example.com"
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


class FileSystemWorkflowRepository(AbstractWorkflowRepository):
    """File system-based workflow repository.

    Reads workflow instances from .claude/workflows/ directory structure.
    Implements the repository pattern using actual filesystem persistence.
    """

    def __init__(self, base_dir: Optional[Path] = None):
        """Initialize filesystem repository.

        Args:
            base_dir: Base directory for workflows (default: .claude/workflows)
        """
        if base_dir is None:
            base_dir = Path(".claude/workflows")
        self.base_dir = Path(base_dir)

        # Instance directories
        self.instances_dir = self.base_dir / "instances"
        self.completed_dir = self.base_dir / "completed"
        self.abandoned_dir = self.base_dir / "abandoned"

    def list_workflows(self, status: Optional[str] = None) -> List[WorkflowInstance]:
        """List workflow instances with optional status filter.

        Args:
            status: Optional status filter ("in_progress", "completed", "abandoned")

        Returns:
            List of WorkflowInstance objects

        Raises:
            WorkflowRepositoryError: If status is invalid
        """
        instances = []

        # Determine which directories to search
        if status == "in_progress":
            directories = [self.instances_dir]
        elif status == "completed":
            directories = [self.completed_dir]
        elif status == "abandoned":
            directories = [self.abandoned_dir]
        elif status is None:
            directories = [self.instances_dir, self.completed_dir, self.abandoned_dir]
        else:
            raise WorkflowRepositoryError(
                f"Invalid status: {status}. "
                f"Must be one of: in_progress, completed, abandoned, or None"
            )

        # Collect instances from directories
        for directory in directories:
            if not directory.exists():
                continue

            for instance_file in directory.glob("*.json"):
                try:
                    data = atomic_read_json(instance_file)
                    instance = self._parse_instance(data)
                    instances.append(instance)

                except Exception:
                    # Skip malformed files
                    continue

        # Sort by started_at (most recent first)
        instances.sort(
            key=lambda x: x.started_at if x.started_at else "",
            reverse=True
        )

        return instances

    def get_workflow(self, instance_id: str) -> WorkflowInstance:
        """Get detailed workflow instance information.

        Args:
            instance_id: Instance identifier

        Returns:
            WorkflowInstance with full details

        Raises:
            WorkflowRepositoryError: If instance not found or invalid
        """
        # Security: Validate instance_id to prevent path traversal
        if not self._is_valid_instance_id(instance_id):
            raise WorkflowRepositoryError(
                f"Invalid instance ID format: {instance_id}. "
                f"Instance IDs must be alphanumeric with hyphens only."
            )

        # Try each directory
        for directory in [self.instances_dir, self.completed_dir, self.abandoned_dir]:
            instance_file = directory / f"{instance_id}.json"

            if instance_file.exists():
                try:
                    # Read JSON directly to catch parse errors
                    with open(instance_file, "r") as f:
                        data = json.load(f)

                    # Validate required fields
                    if "instance_id" not in data or "workflow_type" not in data:
                        raise WorkflowRepositoryError(
                            f"Instance file missing required fields: {instance_file}"
                        )

                    return self._parse_instance(data)

                except json.JSONDecodeError as e:
                    raise WorkflowRepositoryError(
                        f"Invalid JSON in instance file: {instance_file}. Error: {e}"
                    )
                except WorkflowRepositoryError:
                    raise
                except Exception as e:
                    raise WorkflowRepositoryError(
                        f"Error loading instance file: {instance_file}. Error: {e}"
                    )

        # Not found in any directory
        raise WorkflowRepositoryError(
            f"Workflow instance not found: {instance_id}. "
            f"Searched in: instances, completed, abandoned"
        )

    def _parse_instance(self, data: Dict[str, Any]) -> WorkflowInstance:
        """Parse instance data from JSON into WorkflowInstance domain object.

        Args:
            data: Raw JSON data

        Returns:
            WorkflowInstance domain object
        """
        # Parse metadata
        metadata = data.get("metadata", {})
        status_str = metadata.get("status", "in_progress")

        # Convert status string to enum
        try:
            status = WorkflowStatus(status_str)
        except ValueError:
            status = WorkflowStatus.IN_PROGRESS

        # Parse workflow progress
        progress = data.get("workflow_progress", {})

        # Parse completed triads
        completed_triads = []
        for completion in progress.get("completed_triads", []):
            completed_triads.append(
                TriadCompletion(
                    triad_id=completion.get("triad_id", ""),
                    completed_at=completion.get("completed_at", ""),
                    duration_minutes=completion.get("duration_minutes", 0.0),
                )
            )

        # Parse skipped triads (already in dict format)
        skipped_triads = progress.get("skipped_triads", [])

        # Parse deviations
        deviations = []
        for dev in data.get("workflow_deviations", []):
            deviations.append(
                WorkflowDeviation(
                    deviation_type=dev.get("type", "unknown"),
                    from_triad=dev.get("from_triad"),
                    to_triad=dev.get("to_triad", ""),
                    reason=dev.get("reason", ""),
                    timestamp=dev.get("timestamp", ""),
                    user=dev.get("user"),
                    skipped=dev.get("skipped", []),
                )
            )

        return WorkflowInstance(
            instance_id=data["instance_id"],
            workflow_type=data["workflow_type"],
            status=status,
            title=metadata.get("title", "Untitled"),
            current_triad=progress.get("current_triad"),
            completed_triads=completed_triads,
            skipped_triads=skipped_triads,
            started_at=metadata.get("started_at"),
            completed_at=metadata.get("completed_at"),
            abandoned_at=metadata.get("abandoned_at"),
            started_by=metadata.get("started_by"),
            workflow_deviations=deviations,
            significance_metrics=data.get("significance_metrics", {}),
            metadata=metadata,
        )

    def _is_valid_instance_id(self, instance_id: str) -> bool:
        """Validate instance ID format (security check).

        Args:
            instance_id: Instance ID to validate

        Returns:
            True if valid, False otherwise
        """
        # Only allow alphanumeric and hyphens
        return bool(re.match(r"^[a-z0-9\-]+$", instance_id))
