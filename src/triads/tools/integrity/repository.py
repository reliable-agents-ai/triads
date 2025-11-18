"""
Repository layer for integrity tools.

Provides AbstractBackupRepository interface and implementations:
- InMemoryBackupRepository: For testing
- FileSystemBackupRepository: Wraps BackupManager for production use
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from triads.tools.knowledge.backup import BackupManager

import logging

logger = logging.getLogger(__name__)



class AbstractBackupRepository(ABC):
    """
    Abstract interface for backup operations.

    Defines the contract for backup repositories that manage graph backups.
    """

    @abstractmethod
    def create_backup(self, triad: str) -> Path:
        """
        Create a backup of the specified triad graph.

        Args:
            triad: Name of the triad graph

        Returns:
            Path to the created backup file
        """
        pass

    @abstractmethod
    def list_backups(self, triad: str) -> List[str]:
        """
        List all backups for the specified triad graph.

        Args:
            triad: Name of the triad graph

        Returns:
            List of backup filenames, sorted newest first
        """
        pass

    @abstractmethod
    def restore_backup(self, triad: str, backup_name: str | Path) -> bool:
        """
        Restore a graph from a backup.

        Args:
            triad: Name of the triad graph
            backup_name: Backup filename or path to restore from

        Returns:
            True if restore succeeded, False otherwise
        """
        pass


class InMemoryBackupRepository(AbstractBackupRepository):
    """
    In-memory backup repository for testing.

    Simulates backup operations without touching the filesystem.
    """

    def __init__(self):
        """Initialize in-memory backup storage."""
        self.backups: dict[str, List[Path]] = {}
        self._backup_counter = 0

    def create_backup(self, triad: str) -> Path:
        """
        Create a simulated backup in memory.

        Args:
            triad: Name of the triad graph

        Returns:
            Simulated path to backup file
        """
        # Generate unique backup path
        backup_path = Path(f"/fake/backups/{triad}_graph_{self._backup_counter}.json.backup")
        self._backup_counter += 1

        # Store in memory
        if triad not in self.backups:
            self.backups[triad] = []
        self.backups[triad].append(backup_path)

        return backup_path

    def list_backups(self, triad: str) -> List[str]:
        """
        List all simulated backups for a triad.

        Args:
            triad: Name of the triad graph

        Returns:
            List of backup paths as strings
        """
        if triad not in self.backups:
            return []
        return [str(path) for path in self.backups[triad]]

    def restore_backup(self, triad: str, backup_name: str | Path) -> bool:
        """
        Simulate restoring a backup.

        Args:
            triad: Name of the triad graph
            backup_name: Backup filename or path

        Returns:
            True if backup exists, False otherwise
        """
        if triad not in self.backups:
            return False

        # Check if backup exists
        backup_path = Path(backup_name)
        return backup_path in self.backups[triad]


class FileSystemBackupRepository(AbstractBackupRepository):
    """
    Filesystem backup repository that wraps BackupManager.

    Delegates all backup operations to the existing BackupManager.
    """

    def __init__(self, graphs_dir: Path | str):
        """
        Initialize filesystem backup repository.

        Args:
            graphs_dir: Directory containing graph files
        """
        self.graphs_dir = Path(graphs_dir)
        self.backup_manager = BackupManager(graphs_dir=self.graphs_dir)

    def create_backup(self, triad: str) -> Path | None:
        """
        Create a backup using BackupManager.

        Args:
            triad: Name of the triad graph

        Returns:
            Path to created backup file, or None if source doesn't exist
        """
        return self.backup_manager.create_backup(triad)

    def list_backups(self, triad: str) -> List[str]:
        """
        List backups using BackupManager.

        Args:
            triad: Name of the triad graph

        Returns:
            List of backup filenames, sorted newest first
        """
        return self.backup_manager.list_backups(triad)

    def restore_backup(self, triad: str, backup_name: str | Path) -> bool:
        """
        Restore backup using BackupManager.

        Args:
            triad: Name of the triad graph
            backup_name: Backup filename or path to restore from

        Returns:
            True if restore succeeded, False otherwise
        """
        # Convert Path to string if needed
        if isinstance(backup_name, Path):
            backup_name = backup_name.name

        return self.backup_manager.restore_backup(triad, backup_name)
