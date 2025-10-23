"""
Domain models for integrity tools.

Provides ValidationResult and RepairResult for representing the outcomes
of graph validation and repair operations.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import logging

logger = logging.getLogger(__name__)



@dataclass(frozen=True)
class ValidationResult:
    """
    Result of validating a knowledge graph.

    Attributes:
        triad: Name of the triad graph
        valid: Whether the graph passed validation
        error: Error message if validation failed
        error_field: Specific field that caused the error (e.g., "nodes[0].label")
        error_count: Number of errors found
        file_path: Path to the graph file
    """

    triad: str
    valid: bool
    error: Optional[str] = None
    error_field: Optional[str] = None
    error_count: int = 0
    file_path: Optional[Path] = None


@dataclass(frozen=True)
class RepairResult:
    """
    Result of attempting to repair a corrupted graph.

    Attributes:
        triad: Name of the triad graph
        success: Whether the repair succeeded
        message: Human-readable message describing the outcome
        actions_taken: Description of repair actions performed
        backup_created: Whether a backup was created before repair
        backup_path: Path to the backup file if created
    """

    triad: str
    success: bool
    message: str
    actions_taken: Optional[str] = None
    backup_created: bool = False
    backup_path: Optional[Path] = None
