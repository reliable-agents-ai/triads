"""Workflow enforcement system for Triad workflows.

This module enforces the requirement for Garden Tending before deployment
when code changes exceed defined thresholds.

Public API (Primary - v0.7+):
    - WorkflowValidator (from validator_new): Schema-driven validation
    - WorkflowEnforcer (from enforcement_new): Schema-driven enforcement
    - WorkflowSchemaLoader: Load workflow schemas
    - WorkflowInstanceManager: Manage workflow instances
    - TriadDiscovery: Discover available triads
    - MetricsProvider: Base class for metrics providers
    - CodeMetricsProvider: Git-based metrics provider
    - GitRunner: Unified git command execution

Legacy API (Deprecated in v0.7, removed in v1.0):
    - validate_deployment(): Main validation function (use WorkflowEnforcer instead)
    - check_bypass(): Check for emergency bypass flags
    - WorkflowStateManager: Manage workflow state (use WorkflowInstanceManager instead)
    - BlockingEnforcement: Block deployment (use WorkflowEnforcer instead)
    - EmergencyBypass: Handle emergency bypass with audit trail
    - AuditLogger: Log bypass events

Example (v0.7+):
    from triads.workflow_enforcement import (
        WorkflowValidator,
        WorkflowEnforcer,
        WorkflowSchemaLoader,
        WorkflowInstanceManager,
        TriadDiscovery,
        CodeMetricsProvider
    )

    # Load schema
    schema_loader = WorkflowSchemaLoader()
    schema = schema_loader.load_schema()

    # Setup enforcement
    discovery = TriadDiscovery()
    instance_manager = WorkflowInstanceManager()
    metrics_provider = CodeMetricsProvider()

    enforcer = WorkflowEnforcer(
        schema_loader=schema_loader,
        instance_manager=instance_manager,
        discovery=discovery,
        metrics_provider=metrics_provider
    )

    # Enforce transition
    result = enforcer.enforce(instance_id="my-workflow", target_triad_id="deployment")
    if not result.allowed:
        print(f"Blocked: {result.message}")
"""

# Primary exports (v0.7+)
from triads.workflow_enforcement.validator_new import WorkflowValidator, ValidationResult
from triads.workflow_enforcement.enforcement_new import WorkflowEnforcer, EnforcementResult
from triads.workflow_enforcement.schema_loader import WorkflowSchemaLoader, WorkflowSchema
from triads.workflow_enforcement.instance_manager import WorkflowInstanceManager, WorkflowInstance
from triads.workflow_enforcement.triad_discovery import TriadDiscovery, TriadInfo
from triads.workflow_enforcement.metrics.base import MetricsProvider, MetricsResult
from triads.workflow_enforcement.metrics.code_metrics import CodeMetricsProvider
from triads.workflow_enforcement.git_utils import GitRunner, GitCommandError

# Legacy exports (deprecated)
from triads.workflow_enforcement.audit import AuditLogger
from triads.workflow_enforcement.bypass import EmergencyBypass, check_bypass
from triads.workflow_enforcement.enforcement import (
    BlockingEnforcement as LegacyBlockingEnforcement,
    validate_deployment,
)
from triads.workflow_enforcement.state_manager import WorkflowStateManager
from triads.workflow_enforcement.validator import WorkflowValidator as LegacyWorkflowValidator

# Maintain backward compatibility
BlockingEnforcement = LegacyBlockingEnforcement

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
    # Legacy exports (deprecated)
    "AuditLogger",
    "BlockingEnforcement",
    "LegacyBlockingEnforcement",
    "LegacyWorkflowValidator",
    "EmergencyBypass",
    "WorkflowStateManager",
    "check_bypass",
    "validate_deployment",
]
