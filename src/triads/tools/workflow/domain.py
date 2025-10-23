"""Domain models for workflow tools.

Defines core data structures for workflow instance operations.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class WorkflowStatus(Enum):
    """Workflow instance status."""

    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


@dataclass
class TriadCompletion:
    """Information about a completed triad.

    Attributes:
        triad_id: Triad identifier
        completed_at: ISO 8601 timestamp when triad was completed
        duration_minutes: Duration in minutes
    """

    triad_id: str
    completed_at: str
    duration_minutes: float


@dataclass
class WorkflowInstance:
    """Workflow instance information.

    Represents a workflow instance with progress tracking,
    completed triads, and metadata.

    Attributes:
        instance_id: Unique instance identifier
        workflow_type: Type of workflow (e.g., "software-development")
        status: Current status (in_progress, completed, abandoned)
        title: Human-readable title
        current_triad: Currently active triad (None if not started)
        completed_triads: List of completed triads
        started_at: ISO 8601 timestamp when workflow started
    """

    instance_id: str
    workflow_type: str
    status: WorkflowStatus
    title: str
    current_triad: Optional[str] = None
    completed_triads: List[TriadCompletion] = field(default_factory=list)
    started_at: Optional[str] = None
