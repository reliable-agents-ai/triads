"""Domain models for workflow tools.

Defines core data structures for workflow instance operations.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

import logging

logger = logging.getLogger(__name__)



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
class WorkflowDeviation:
    """Information about a workflow deviation.

    Attributes:
        deviation_type: Type of deviation (e.g., "skip_forward", "skip_backward")
        from_triad: Source triad
        to_triad: Target triad
        reason: Reason for deviation
        timestamp: ISO 8601 timestamp when deviation occurred
        user: User who authorized deviation
        skipped: List of skipped triad IDs
    """

    deviation_type: str
    from_triad: Optional[str]
    to_triad: str
    reason: str
    timestamp: str
    user: Optional[str] = None
    skipped: List[str] = field(default_factory=list)


@dataclass
class WorkflowInstance:
    """Workflow instance information.

    Represents a workflow instance with progress tracking,
    completed triads, metadata, deviations, and metrics.

    Attributes:
        instance_id: Unique instance identifier
        workflow_type: Type of workflow (e.g., "software-development")
        status: Current status (in_progress, completed, abandoned)
        title: Human-readable title
        current_triad: Currently active triad (None if not started)
        completed_triads: List of completed triads
        skipped_triads: List of skipped triads with reasons
        started_at: ISO 8601 timestamp when workflow started
        completed_at: ISO 8601 timestamp when workflow completed (if completed)
        abandoned_at: ISO 8601 timestamp when workflow abandoned (if abandoned)
        started_by: User who started the workflow
        workflow_deviations: List of deviations from workflow rules
        significance_metrics: Metrics for significance evaluation
        metadata: Additional metadata
    """

    instance_id: str
    workflow_type: str
    status: WorkflowStatus
    title: str
    current_triad: Optional[str] = None
    completed_triads: List[TriadCompletion] = field(default_factory=list)
    skipped_triads: List[Dict[str, Any]] = field(default_factory=list)
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    abandoned_at: Optional[str] = None
    started_by: Optional[str] = None
    workflow_deviations: List[WorkflowDeviation] = field(default_factory=list)
    significance_metrics: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
