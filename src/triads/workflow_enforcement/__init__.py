"""Deprecated: Use triads.tools.workflow instead.

This module provides backward compatibility for code that imports from
triads.workflow_enforcement. Core workflow functionality has been moved to
triads.tools.workflow with a proper 4-layer DDD architecture.

DEPRECATION NOTICE (v0.10.0):
    This module will be removed in v0.11.0. Please migrate to:
    - triads.tools.workflow.validation (WorkflowValidator)
    - triads.tools.workflow.enforcement (WorkflowEnforcer)
    - triads.tools.workflow.schema (WorkflowSchemaLoader)
    - triads.tools.workflow.discovery (TriadDiscovery)
    - triads.tools.workflow.audit (AuditLogger)
    - triads.tools.workflow.bypass (EmergencyBypass)
    - triads.tools.workflow.git_utils (GitRunner)

Migration Guide:
    OLD: from triads.workflow_enforcement.validator_new import WorkflowValidator
    NEW: from triads.tools.workflow.validation import WorkflowValidator

    OLD: from triads.workflow_enforcement.schema_loader import WorkflowSchemaLoader
    NEW: from triads.tools.workflow.schema import WorkflowSchemaLoader

    OLD: from triads.workflow_enforcement.triad_discovery import TriadDiscovery
    NEW: from triads.tools.workflow.discovery import TriadDiscovery

See docs/PHASE_9_REFACTOR.md for complete migration guide.
"""

import warnings

warnings.warn(
    "triads.workflow_enforcement is deprecated and will be removed in v0.11.0. "
    "Use triads.tools.workflow instead. "
    "See docs/PHASE_9_REFACTOR.md for migration guide.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export from new locations (moved to tools/workflow in v0.10.0)
from triads.tools.workflow.validation import WorkflowValidator, ValidationResult
from triads.tools.workflow.schema import WorkflowSchemaLoader, WorkflowSchema
from triads.tools.workflow.discovery import TriadDiscovery, TriadInfo
from triads.tools.workflow.audit import AuditLogger
from triads.tools.workflow.bypass import EmergencyBypass, check_bypass
from triads.tools.workflow.git_utils import GitRunner, GitCommandError

# Still in old location (enforcement_new uses old modules)
from triads.workflow_enforcement.enforcement_new import WorkflowEnforcer, EnforcementResult
from triads.workflow_enforcement.instance_manager import WorkflowInstanceManager, WorkflowInstance
from triads.workflow_enforcement.state_manager import WorkflowStateManager
from triads.workflow_enforcement.metrics.base import MetricsProvider, MetricsResult
from triads.workflow_enforcement.metrics.code_metrics import CodeMetricsProvider

__all__ = [
    # Primary exports (v0.7+)
    "WorkflowValidator",
    "ValidationResult",
    "WorkflowEnforcer",
    "EnforcementResult",
    "WorkflowSchemaLoader",
    "WorkflowSchema",
    "WorkflowInstanceManager",
    "WorkflowInstance",
    "TriadDiscovery",
    "TriadInfo",
    "MetricsProvider",
    "MetricsResult",
    "CodeMetricsProvider",
    "GitRunner",
    "GitCommandError",
    # Legacy exports (still supported - for audit, bypass, state)
    "AuditLogger",
    "EmergencyBypass",
    "WorkflowStateManager",
    "check_bypass",
]
