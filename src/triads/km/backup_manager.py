"""Knowledge graph backup and recovery system.

DEPRECATED: This module has been refactored into triads.tools.knowledge.backup
as part of the DDD architecture consolidation.

New location: triads.tools.knowledge.backup.BackupManager

This module provides backward compatibility. Please update imports to:
    from triads.tools.knowledge.backup import BackupManager
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any

# Import from new location
from triads.tools.knowledge.backup import BackupManager as _NewBackupManager

# Show deprecation warning
warnings.warn(
    "triads.km.backup_manager is deprecated. "
    "Use triads.tools.knowledge.backup instead.",
    DeprecationWarning,
    stacklevel=2
)


# ============================================================================
# Backward Compatibility Alias
# ============================================================================


class BackupManager(_NewBackupManager):
    """Manage backups and recovery for knowledge graphs.

    DEPRECATED: Use BackupManager from triads.tools.knowledge.backup instead.

    This class now inherits from the new BackupManager and delegates all functionality.
    Maintained for backward compatibility only.

    Example:
        # Old (deprecated):
        from triads.km.backup_manager import BackupManager

        # New (preferred):
        from triads.tools.knowledge.backup import BackupManager
    """
    pass
