"""Backup and recovery for knowledge graphs.

Provides automatic backup before writes and auto-restore on failure.
Moved from triads.km.backup_manager as part of DDD refactoring.
"""

from __future__ import annotations

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class BackupManager:
    """Manage backups and recovery for knowledge graphs.

    Features:
        - Auto-backup before writes
        - Timestamped backup files
        - Rotation (keep last N backups)
        - Auto-restore on failure

    Example:
        backup_mgr = BackupManager(graphs_dir=Path(".claude/graphs"), max_backups=5)
        backups = backup_mgr.list_backups("design")
        backup_mgr.restore_backup("design", backups[0])
    """

    def __init__(self, graphs_dir: Path | str, max_backups: int = 5) -> None:
        """Initialize backup manager.

        Args:
            graphs_dir: Directory containing graph files
            max_backups: Maximum number of backups to keep per graph
        """
        self.graphs_dir = Path(graphs_dir)
        self.max_backups = max_backups
        self.backups_dir = self.graphs_dir / "backups"
        self._config_file = self.backups_dir / ".backup_config.json"

        # Save config
        self._save_config()

    def _save_config(self) -> None:
        """Save backup configuration to file."""
        try:
            self.backups_dir.mkdir(parents=True, exist_ok=True)
            with open(self._config_file, "w", encoding="utf-8") as f:
                json.dump({"max_backups": self.max_backups}, f)
        except (OSError, IOError) as e:
            logger.warning(
                f"Failed to save backup config: {type(e).__name__}",
                extra={"error": str(e)}
            )

    @staticmethod
    def load_config(graphs_dir: Path | str) -> int:
        """Load max_backups configuration from directory.

        Args:
            graphs_dir: Directory containing graph files

        Returns:
            Configured max_backups value, or default (5) if not found
        """
        config_file = Path(graphs_dir) / "backups" / ".backup_config.json"
        if config_file.exists():
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    return config.get("max_backups", 5)
            except (json.JSONDecodeError, OSError, IOError):
                pass
        return 5

    def _get_graph_file(self, triad: str) -> Path:
        """Get path to graph file for a triad.

        Args:
            triad: Triad name

        Returns:
            Path to graph file
        """
        return self.graphs_dir / f"{triad}_graph.json"

    def create_backup(self, triad: str) -> Path | None:
        """Create a timestamped backup of a graph file.

        Creates backup in .claude/graphs/backups/ with format:
        {triad}_graph_YYYYMMDD_HHMMSS_microseconds.json.backup

        Args:
            triad: Triad name

        Returns:
            Path to created backup file, or None if source doesn't exist
        """
        graph_file = self._get_graph_file(triad)

        if not graph_file.exists():
            logger.debug(
                "Skipping backup: source file doesn't exist (first save)",
                extra={"triad": triad, "file": str(graph_file)}
            )
            return None

        self.backups_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        backup_name = f"{triad}_graph_{timestamp}.json.backup"
        backup_path = self.backups_dir / backup_name

        try:
            shutil.copy2(graph_file, backup_path)
            logger.info(
                "Created backup",
                extra={"triad": triad, "backup": backup_name}
            )
            return backup_path

        except (OSError, IOError) as e:
            logger.error(
                f"Failed to create backup: {type(e).__name__}",
                extra={"triad": triad, "error": str(e)}
            )
            return None

    def list_backups(self, triad: str) -> list[str]:
        """List all backups for a triad graph.

        Args:
            triad: Triad name

        Returns:
            List of backup filenames, sorted newest first
        """
        if not self.backups_dir.exists():
            return []

        pattern = f"{triad}_graph_*.json.backup"
        backup_files = sorted(
            self.backups_dir.glob(pattern),
            key=lambda p: p.name,
            reverse=True
        )

        return [f.name for f in backup_files]

    def load_backup(self, triad: str, backup_name: str) -> dict[str, Any]:
        """Load a specific backup.

        Args:
            triad: Triad name
            backup_name: Backup filename

        Returns:
            Graph data from backup

        Raises:
            FileNotFoundError: If backup doesn't exist
            json.JSONDecodeError: If backup is corrupted
        """
        backup_path = self.backups_dir / backup_name

        if not backup_path.exists():
            raise FileNotFoundError(f"Backup not found: {backup_name}")

        try:
            with open(backup_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(
                "Corrupted backup file",
                extra={"triad": triad, "backup": backup_name, "error": str(e)}
            )
            raise

    def restore_backup(self, triad: str, backup_name: str) -> bool:
        """Restore a graph from a backup.

        Args:
            triad: Triad name
            backup_name: Backup filename to restore from

        Returns:
            True on success, False on failure
        """
        try:
            backup_data = self.load_backup(triad, backup_name)

            graph_file = self._get_graph_file(triad)
            with open(graph_file, "w", encoding="utf-8") as f:
                json.dump(backup_data, f, indent=2)

            logger.info(
                "Restored graph from backup",
                extra={"triad": triad, "backup": backup_name}
            )
            return True

        except (FileNotFoundError, json.JSONDecodeError, OSError, IOError) as e:
            logger.error(
                f"Failed to restore backup: {type(e).__name__}",
                extra={"triad": triad, "backup": backup_name, "error": str(e)}
            )
            return False

    def restore_latest(self, triad: str) -> bool:
        """Restore from the latest backup.

        Args:
            triad: Triad name

        Returns:
            True on success, False on failure or no backups
        """
        backups = self.list_backups(triad)
        if not backups:
            logger.warning(
                "No backups available to restore",
                extra={"triad": triad}
            )
            return False

        latest_backup = backups[0]
        return self.restore_backup(triad, latest_backup)

    def prune_backups(self, triad: str, keep: int) -> None:
        """Prune old backups, keeping only newest N.

        Args:
            triad: Triad name
            keep: Number of backups to keep
        """
        backups = self.list_backups(triad)

        if len(backups) > keep:
            to_delete = backups[keep:]
            for backup_name in to_delete:
                backup_path = self.backups_dir / backup_name
                try:
                    backup_path.unlink()
                    logger.debug(
                        "Deleted old backup",
                        extra={"triad": triad, "backup": backup_name}
                    )
                except OSError as e:
                    logger.warning(
                        f"Failed to delete backup: {type(e).__name__}",
                        extra={"triad": triad, "backup": backup_name, "error": str(e)}
                    )

    def get_backup_info(self, triad: str, backup_name: str) -> dict[str, Any]:
        """Get metadata about a backup.

        Args:
            triad: Triad name
            backup_name: Backup filename

        Returns:
            Dictionary with timestamp, size_bytes, nodes_count, etc.
        """
        backup_path = self.backups_dir / backup_name

        if not backup_path.exists():
            raise FileNotFoundError(f"Backup not found: {backup_name}")

        parts = backup_name.replace(".json.backup", "").split("_")
        if len(parts) >= 3:
            date_part = parts[-2]
            time_part = parts[-1]
            timestamp = f"{date_part}_{time_part}"
        else:
            timestamp = "unknown"

        size_bytes = backup_path.stat().st_size

        try:
            backup_data = self.load_backup(triad, backup_name)
            nodes_count = len(backup_data.get("nodes", []))
        except (json.JSONDecodeError, OSError):
            nodes_count = None

        return {
            "timestamp": timestamp,
            "size_bytes": size_bytes,
            "nodes_count": nodes_count,
            "path": str(backup_path),
        }
