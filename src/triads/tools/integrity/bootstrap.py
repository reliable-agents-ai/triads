"""
Bootstrap factory for integrity service.

Creates IntegrityService with production dependencies.
"""

from pathlib import Path

from .repository import FileSystemBackupRepository
from .service import IntegrityService

import logging

logger = logging.getLogger(__name__)



def bootstrap_integrity_service(graphs_dir: Path | str | None = None) -> IntegrityService:
    """
    Create IntegrityService with production dependencies.

    Args:
        graphs_dir: Directory containing graph files (default: .claude/graphs)

    Returns:
        IntegrityService instance with FileSystemBackupRepository
    """
    if graphs_dir is None:
        graphs_dir = Path(".claude/graphs")
    else:
        graphs_dir = Path(graphs_dir)

    # Create filesystem backup repository
    backup_repo = FileSystemBackupRepository(graphs_dir=graphs_dir)

    # Create service
    return IntegrityService(backup_repo=backup_repo, graphs_dir=graphs_dir)
