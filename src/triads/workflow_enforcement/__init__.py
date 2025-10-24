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
    - triads.tools.workflow.metrics (MetricsProvider, MetricsResult, CodeMetricsProvider)
    - triads.tools.workflow.repository (AbstractWorkflowRepository, FileSystemWorkflowRepository)

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
# Import these lazily to avoid circular imports
def __getattr__(name):
    """Lazy import to avoid circular imports."""
    if name == "WorkflowValidator":
        from triads.tools.workflow.validation import WorkflowValidator
        return WorkflowValidator
    elif name == "ValidationResult":
        from triads.tools.workflow.validation import ValidationResult
        return ValidationResult
    elif name == "WorkflowSchemaLoader":
        from triads.tools.workflow.schema import WorkflowSchemaLoader
        return WorkflowSchemaLoader
    elif name == "WorkflowSchema":
        from triads.tools.workflow.schema import WorkflowSchema
        return WorkflowSchema
    elif name == "TriadDiscovery":
        from triads.tools.workflow.discovery import TriadDiscovery
        return TriadDiscovery
    elif name == "TriadInfo":
        from triads.tools.workflow.discovery import TriadInfo
        return TriadInfo
    elif name == "AuditLogger":
        from triads.tools.workflow.audit import AuditLogger
        return AuditLogger
    elif name == "EmergencyBypass":
        from triads.tools.workflow.bypass import EmergencyBypass
        return EmergencyBypass
    elif name == "check_bypass":
        from triads.tools.workflow.bypass import check_bypass
        return check_bypass
    elif name == "GitRunner":
        from triads.tools.workflow.git_utils import GitRunner
        return GitRunner
    elif name == "GitCommandError":
        from triads.tools.workflow.git_utils import GitCommandError
        return GitCommandError
    elif name == "WorkflowEnforcer":
        from triads.tools.workflow.enforcement import WorkflowEnforcer
        return WorkflowEnforcer
    elif name == "EnforcementResult":
        from triads.tools.workflow.enforcement import EnforcementResult
        return EnforcementResult
    elif name == "MetricsProvider":
        from triads.tools.workflow.metrics import MetricsProvider
        return MetricsProvider
    elif name == "MetricsResult":
        from triads.tools.workflow.metrics import MetricsResult
        return MetricsResult
    elif name == "CodeMetricsProvider":
        from triads.tools.workflow.metrics import CodeMetricsProvider
        return CodeMetricsProvider
    elif name == "WorkflowInstanceManager":
        from triads.workflow_enforcement.instance_manager import WorkflowInstanceManager
        return WorkflowInstanceManager
    elif name == "WorkflowInstance":
        from triads.workflow_enforcement.instance_manager import WorkflowInstance
        return WorkflowInstance
    elif name == "WorkflowStateManager":
        from triads.workflow_enforcement.state_manager import WorkflowStateManager
        return WorkflowStateManager
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

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
