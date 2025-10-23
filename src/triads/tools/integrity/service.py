"""
Service layer for integrity tools.

Coordinates validation and repair operations by orchestrating between
IntegrityChecker and BackupRepository.
"""

from pathlib import Path
from typing import List

from .checker import IntegrityChecker
from .domain import RepairResult, ValidationResult
from .repository import AbstractBackupRepository

import logging

logger = logging.getLogger(__name__)



class IntegrityService:
    """
    Service for graph validation and repair operations.

    Coordinates between IntegrityChecker (validation/repair logic) and
    BackupRepository (backup management).
    """

    def __init__(self, backup_repo: AbstractBackupRepository, graphs_dir: Path | str):
        """
        Initialize integrity service.

        Args:
            backup_repo: Repository for backup operations
            graphs_dir: Directory containing graph files
        """
        self.backup_repo = backup_repo
        self.graphs_dir = Path(graphs_dir)
        self.checker = IntegrityChecker(graphs_dir=self.graphs_dir)

    def check_graph(self, triad: str) -> ValidationResult:
        """
        Validate a single graph.

        Args:
            triad: Name of the triad graph to check

        Returns:
            ValidationResult with detailed validation information
        """
        # Use IntegrityChecker to validate
        km_result = self.checker.check_graph(triad)

        # Convert to our domain model
        return ValidationResult(
            triad=km_result.triad,
            valid=km_result.valid,
            error=km_result.error,
            error_field=km_result.error_field,
            error_count=km_result.error_count,
            file_path=km_result.file_path
        )

    def check_all_graphs(self) -> List[ValidationResult]:
        """
        Validate all graphs in the directory.

        Returns:
            List of ValidationResult objects, one per graph
        """
        # Use IntegrityChecker to validate all
        km_results = self.checker.check_all_graphs()

        # Convert to our domain models
        return [
            ValidationResult(
                triad=km_result.triad,
                valid=km_result.valid,
                error=km_result.error,
                error_field=km_result.error_field,
                error_count=km_result.error_count,
                file_path=km_result.file_path
            )
            for km_result in km_results
        ]

    def repair_graph(self, triad: str, create_backup: bool = True) -> RepairResult:
        """
        Attempt to repair a corrupted graph.

        Args:
            triad: Name of the triad graph to repair
            create_backup: Whether to create a backup before repair (default: True)

        Returns:
            RepairResult with success status and actions taken
        """
        backup_path = None

        # Create backup if requested
        if create_backup:
            backup_path = self.backup_repo.create_backup(triad)

        # Use IntegrityChecker to repair
        km_result = self.checker.repair_graph(triad)

        # Convert to our domain model
        return RepairResult(
            triad=km_result.triad,
            success=km_result.success,
            message=km_result.message,
            actions_taken=km_result.actions_taken,
            backup_created=create_backup and backup_path is not None,
            backup_path=backup_path
        )
