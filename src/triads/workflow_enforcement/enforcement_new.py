"""Workflow enforcement engine with orchestration logic.

This module orchestrates the entire enforcement workflow:
1. Load workflow instance
2. Validate transition using WorkflowValidator
3. Apply enforcement mode logic (strict/recommended/optional)
4. Record deviations
5. Generate user messages

Works with ANY workflow - no hardcoded triad names.

Per ADR-GENERIC: Domain-agnostic workflow enforcement
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from triads.workflow_enforcement.schema_loader import WorkflowSchemaLoader, WorkflowSchema
from triads.workflow_enforcement.instance_manager import WorkflowInstanceManager, WorkflowInstance
from triads.workflow_enforcement.triad_discovery import TriadDiscovery
from triads.workflow_enforcement.validator_new import WorkflowValidator, ValidationResult
from triads.workflow_enforcement.metrics import MetricsProvider


@dataclass
class EnforcementResult:
    """Result of enforcement check.

    Attributes:
        allowed: Can proceed with target triad?
        message: Message to show user
        requires_reason: Does user need to provide --reason?
        validation_result: Underlying validation details

    Example:
        result = enforcer.enforce(instance_id, "deployment")
        if result.is_blocked():
            print(result.message)
    """
    allowed: bool
    message: str
    requires_reason: bool
    validation_result: ValidationResult

    def is_blocked(self) -> bool:
        """Check if transition is blocked.

        Returns:
            True if not allowed, False otherwise
        """
        return not self.allowed


class WorkflowEnforcer:
    """Orchestrates workflow enforcement.

    Coordinates schema loading, validation, enforcement mode application,
    and deviation tracking. Generic orchestrator that works with any workflow.

    Example:
        schema_loader = WorkflowSchemaLoader()
        instance_manager = WorkflowInstanceManager()
        discovery = TriadDiscovery()
        metrics_provider = CodeMetricsProvider()

        enforcer = WorkflowEnforcer(
            schema_loader,
            instance_manager,
            discovery,
            metrics_provider
        )

        result = enforcer.enforce("instance-123", "deployment")
        if result.allowed:
            print("Proceed with deployment")
        else:
            print(result.message)
    """

    def __init__(
        self,
        schema_loader: WorkflowSchemaLoader,
        instance_manager: WorkflowInstanceManager,
        discovery: TriadDiscovery,
        metrics_provider: Optional[MetricsProvider] = None
    ):
        """Initialize enforcer.

        Args:
            schema_loader: Schema loader instance
            instance_manager: Instance manager instance
            discovery: Triad discovery instance
            metrics_provider: Optional metrics provider
        """
        self.schema_loader = schema_loader
        self.instance_manager = instance_manager
        self.discovery = discovery
        self.metrics_provider = metrics_provider
        self.schema = schema_loader.load_schema()
        self.validator = WorkflowValidator(self.schema, discovery)

    def enforce(
        self,
        instance_id: str,
        target_triad: str,
        skip_reason: Optional[str] = None,
        force_skip: bool = False
    ) -> EnforcementResult:
        """Enforce workflow rules for target triad invocation.

        Args:
            instance_id: Workflow instance ID
            target_triad: Triad to invoke
            skip_reason: Reason for skipping steps (if applicable)
            force_skip: Emergency override (requires justification)

        Returns:
            EnforcementResult indicating if allowed and what message to show

        Example:
            result = enforcer.enforce("instance-123", "deployment")
            if not result.allowed:
                print(f"Blocked: {result.message}")
        """
        # Load instance
        instance = self.instance_manager.load_instance(instance_id)

        # Calculate metrics (if provider available)
        metrics = None
        if self.metrics_provider:
            try:
                metrics = self.metrics_provider.calculate_metrics({})
            except Exception:
                # Graceful degradation: proceed without metrics
                pass

        # Validate transition
        validation = self.validator.validate_transition(instance, target_triad, metrics)

        # Apply enforcement mode logic
        return self._apply_enforcement_mode(
            instance, target_triad, validation, skip_reason, force_skip
        )

    def _apply_enforcement_mode(
        self,
        instance: WorkflowInstance,
        target_triad: str,
        validation: ValidationResult,
        skip_reason: Optional[str],
        force_skip: bool
    ) -> EnforcementResult:
        """Apply enforcement mode logic (strict/recommended/optional).

        Args:
            instance: Workflow instance
            target_triad: Target triad
            validation: Validation result
            skip_reason: Optional skip reason
            force_skip: Force skip flag

        Returns:
            EnforcementResult
        """
        mode = validation.enforcement_mode

        # Check if there are any issues (violations or warnings)
        has_issues = validation.has_violations() or validation.has_warnings() or validation.required_triad is not None

        if not has_issues:
            # No violations or warnings, proceed
            return EnforcementResult(
                allowed=True,
                message=f"✓ Proceeding with {target_triad}",
                requires_reason=False,
                validation_result=validation
            )

        # Handle violations/warnings based on mode
        if mode == "strict":
            return self._apply_strict_mode(validation, force_skip, skip_reason, instance, target_triad)
        elif mode == "recommended":
            return self._apply_recommended_mode(
                instance, target_triad, validation, skip_reason
            )
        elif mode == "optional":
            return self._apply_optional_mode(
                instance, target_triad, validation, skip_reason
            )
        else:
            # Unknown mode, default to recommended
            return self._apply_recommended_mode(
                instance, target_triad, validation, skip_reason
            )

    def _apply_strict_mode(
        self,
        validation: ValidationResult,
        force_skip: bool,
        skip_reason: Optional[str],
        instance: WorkflowInstance,
        target_triad: str
    ) -> EnforcementResult:
        """Strict mode: Block deviations, require emergency override.

        Args:
            validation: Validation result
            force_skip: Force skip flag
            skip_reason: Skip reason
            instance: Workflow instance
            target_triad: Target triad

        Returns:
            EnforcementResult
        """
        if force_skip:
            if not skip_reason or len(skip_reason) < 20:
                return EnforcementResult(
                    allowed=False,
                    message="🛑 CRITICAL: Emergency override requires detailed justification (min 20 chars)",
                    requires_reason=True,
                    validation_result=validation
                )
            # Allow with override - record deviation
            self._record_deviation(instance, target_triad, validation, skip_reason)
            return EnforcementResult(
                allowed=True,
                message=f"⚠️  EMERGENCY OVERRIDE: {skip_reason}\n(Audit logged)",
                requires_reason=False,
                validation_result=validation
            )

        # Build blocking message
        message = "🛑 CRITICAL: Cannot proceed\n"
        message += f"Enforcement mode: STRICT\n\n"
        for violation in validation.violations:
            message += f"  • {violation}\n"
        if validation.required_triad:
            message += f"\nRequired: Complete '{validation.required_triad}' first\n"
        message += f"\nEmergency override: --force-skip --reason '...'"

        return EnforcementResult(
            allowed=False,
            message=message,
            requires_reason=False,
            validation_result=validation
        )

    def _apply_recommended_mode(
        self,
        instance: WorkflowInstance,
        target_triad: str,
        validation: ValidationResult,
        skip_reason: Optional[str]
    ) -> EnforcementResult:
        """Recommended mode: Warn about deviations, allow skip with reason.

        Args:
            instance: Workflow instance
            target_triad: Target triad
            validation: Validation result
            skip_reason: Skip reason

        Returns:
            EnforcementResult
        """
        if skip_reason:
            # User provided reason, record and allow
            self._record_deviation(instance, target_triad, validation, skip_reason)
            return EnforcementResult(
                allowed=True,
                message=f"⚠️  Deviation recorded: {skip_reason}\n✓ Proceeding with {target_triad}",
                requires_reason=False,
                validation_result=validation
            )

        # Build warning message requesting reason
        message = f"⚠️  RECOMMENDED: Review workflow before proceeding\n"
        message += f"Enforcement mode: RECOMMENDED\n\n"
        for warning in validation.warnings:
            message += f"  • {warning}\n"
        for violation in validation.violations:
            message += f"  • {violation}\n"
        if validation.required_triad:
            message += f"\nRecommended: Complete '{validation.required_triad}' first\n"

        message += f"\nOptions:\n"
        message += f"  1. Follow workflow: Start {validation.required_triad or 'previous step'}\n"
        message += f"  2. Skip with reason: --skip --reason '...'\n"

        return EnforcementResult(
            allowed=False,
            message=message,
            requires_reason=True,
            validation_result=validation
        )

    def _apply_optional_mode(
        self,
        instance: WorkflowInstance,
        target_triad: str,
        validation: ValidationResult,
        skip_reason: Optional[str]
    ) -> EnforcementResult:
        """Optional mode: Log deviations, minimal friction.

        Args:
            instance: Workflow instance
            target_triad: Target triad
            validation: Validation result
            skip_reason: Skip reason

        Returns:
            EnforcementResult
        """
        # Record deviation (even without reason)
        reason = skip_reason or "No reason provided"
        self._record_deviation(instance, target_triad, validation, reason)

        message = f"ℹ️  Deviation logged"
        if validation.skipped_triads:
            message += f": Skipped {', '.join(validation.skipped_triads)}"
        message += f"\n✓ Proceeding with {target_triad}"

        return EnforcementResult(
            allowed=True,
            message=message,
            requires_reason=False,
            validation_result=validation
        )

    def _record_deviation(
        self,
        instance: WorkflowInstance,
        target_triad: str,
        validation: ValidationResult,
        reason: str
    ) -> None:
        """Record deviation in instance file.

        Args:
            instance: Workflow instance
            target_triad: Target triad
            validation: Validation result
            reason: Deviation reason
        """
        deviation = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": self._classify_deviation(instance, target_triad, validation),
            "from_triad": instance.workflow_progress.get("current_triad"),
            "to_triad": target_triad,
            "skipped": validation.skipped_triads,
            "reason": reason,
            "enforcement_mode": validation.enforcement_mode,
            "user": instance.metadata.get("started_by", "unknown")
        }

        self.instance_manager.add_deviation(instance.instance_id, deviation)

    def _classify_deviation(
        self, instance: WorkflowInstance, target_triad: str, validation: ValidationResult
    ) -> str:
        """Classify deviation type.

        Args:
            instance: Workflow instance
            target_triad: Target triad
            validation: Validation result

        Returns:
            Deviation type ("skip_forward", "skip_backward", "gate_skip", "unknown")
        """
        if validation.skipped_triads:
            return "skip_forward"

        # Check if going backward
        triad_sequence = [t.id for t in self.schema.triads]
        current_triad = instance.workflow_progress.get("current_triad")

        try:
            current_idx = triad_sequence.index(current_triad) if current_triad else -1
            target_idx = triad_sequence.index(target_triad)
            if target_idx < current_idx:
                return "skip_backward"
        except ValueError:
            pass

        if validation.required_triad:
            return "gate_skip"

        return "unknown"
