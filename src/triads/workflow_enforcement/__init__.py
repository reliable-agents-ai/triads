"""Workflow enforcement system for Triad workflows.

This module enforces the requirement for Garden Tending before deployment
when code changes exceed defined thresholds.

Public API:
    - validate_deployment(): Main validation function (call from release-manager)
    - check_bypass(): Check for emergency bypass flags
    - WorkflowStateManager: Manage workflow state
    - WorkflowValidator: Calculate metrics and validate transitions
    - BlockingEnforcement: Block deployment if requirements not met
    - EmergencyBypass: Handle emergency bypass with audit trail
    - AuditLogger: Log bypass events

Example:
    # In release-manager agent
    from triads.workflow_enforcement import validate_deployment, check_bypass

    # Check for bypass first
    if not check_bypass():
        # Normal validation
        validate_deployment()

    # Proceed with deployment...
"""

from triads.workflow_enforcement.audit import AuditLogger
from triads.workflow_enforcement.bypass import EmergencyBypass, check_bypass
from triads.workflow_enforcement.enforcement import (
    BlockingEnforcement,
    validate_deployment,
)
from triads.workflow_enforcement.state_manager import WorkflowStateManager
from triads.workflow_enforcement.validator import WorkflowValidator

__all__ = [
    "AuditLogger",
    "BlockingEnforcement",
    "EmergencyBypass",
    "WorkflowStateManager",
    "WorkflowValidator",
    "check_bypass",
    "validate_deployment",
]
