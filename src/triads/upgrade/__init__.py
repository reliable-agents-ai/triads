"""Agent upgrade system.

This module provides orchestration for upgrading agent files to new template versions.
It implements a multi-gate safety system: scan → backup → diff → validate → apply.
"""

from .exceptions import (
    AgentNotFoundError,
    InvalidAgentError,
    UpgradeError,
    UpgradeIOError,
    UpgradeSecurityError,
)
from .orchestrator import UpgradeOrchestrator, UpgradeCandidate

__all__ = [
    "UpgradeOrchestrator",
    "UpgradeCandidate",
    "UpgradeError",
    "InvalidAgentError",
    "UpgradeSecurityError",
    "UpgradeIOError",
    "AgentNotFoundError",
]
