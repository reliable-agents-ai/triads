"""Generic workflow validator with schema-driven rules.

This module implements generic, schema-driven workflow validation that works
with ANY workflow type (RFP writing, software development, content creation, etc.).
NO hardcoded triad names - all rules come from WorkflowSchema.

Validates:
- Triad existence (in schema and filesystem)
- Sequential progression
- Conditional requirements (gate triads)
- Enforcement modes (strict, recommended, optional)

Per ADR-GENERIC: Domain-agnostic workflow enforcement
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

# Import domain models from tools/workflow/domain
from triads.tools.workflow.domain import WorkflowInstance

# Import schema and discovery from tools/workflow (moved in Phase 5)
from triads.tools.workflow.schema import WorkflowSchema, WorkflowRule, WorkflowSchemaLoader
from triads.tools.workflow.discovery import TriadDiscovery
from triads.workflow_enforcement.metrics import MetricsResult


@dataclass
class ValidationResult:
    """Result of workflow validation.

    Attributes:
        valid: Whether transition is valid (no violations)
        violations: List of blocking issues
        warnings: List of non-blocking issues
        required_triad: Gate triad that must be completed first (if any)
        skipped_triads: Triads being skipped in this transition
        enforcement_mode: Enforcement mode that applies (from schema)

    Example:
        result = validator.validate_transition(instance, "deployment")
        if not result.valid:
            print(f"Violations: {result.violations}")
            if result.required_triad:
                print(f"Must complete: {result.required_triad}")
    """
    valid: bool
    violations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    required_triad: Optional[str] = None
    skipped_triads: list[str] = field(default_factory=list)
    enforcement_mode: str = "recommended"

    def has_violations(self) -> bool:
        """Check if result has violations.

        Returns:
            True if violations present, False otherwise
        """
        return len(self.violations) > 0

    def has_warnings(self) -> bool:
        """Check if result has warnings.

        Returns:
            True if warnings present, False otherwise
        """
        return len(self.warnings) > 0


class WorkflowValidator:
    """Validates workflow transitions using schema rules.

    Generic validator that works with any workflow by loading rules from
    WorkflowSchema. No hardcoded triad names or domain-specific logic.

    Example:
        schema = WorkflowSchemaLoader().load_schema()
        discovery = TriadDiscovery()
        validator = WorkflowValidator(schema, discovery)

        instance = manager.load_instance("instance-123")
        result = validator.validate_transition(instance, "deployment")

        if not result.valid:
            print(f"Cannot proceed: {result.violations}")
    """

    def __init__(self, schema: WorkflowSchema, discovery: TriadDiscovery):
        """Initialize validator.

        Args:
            schema: Workflow schema with triads and rules
            discovery: Triad discovery for filesystem checks
        """
        self.schema = schema
        self.discovery = discovery

    def validate_transition(
        self,
        instance: WorkflowInstance,
        target_triad: str,
        metrics: Optional[MetricsResult] = None
    ) -> ValidationResult:
        """Validate transition from current state to target triad.

        Checks:
        1. Target triad exists in schema
        2. Target triad exists in filesystem
        3. Sequential progression rules
        4. Conditional requirements (gate triads)

        Args:
            instance: Current workflow instance state
            target_triad: Triad user wants to invoke
            metrics: Optional metrics (for conditional requirements)

        Returns:
            ValidationResult with violations, warnings, and enforcement mode

        Example:
            result = validator.validate_transition(instance, "deployment", metrics)
            if result.valid:
                print("Transition allowed")
            else:
                print(f"Blocked: {result.violations}")
        """
        violations = []
        warnings = []
        skipped_triads = []
        required_triad = None

        # Get enforcement mode for target triad
        enforcement_mode = self._get_enforcement_mode(target_triad)

        # Check if target triad exists in schema
        if not self._triad_in_schema(target_triad):
            violations.append(f"Triad '{target_triad}' not found in workflow schema")
            return ValidationResult(
                valid=False,
                violations=violations,
                warnings=warnings,
                required_triad=required_triad,
                skipped_triads=skipped_triads,
                enforcement_mode=enforcement_mode
            )

        # Check if target triad exists in filesystem
        if not self.discovery.triad_exists(target_triad):
            violations.append(f"Triad '{target_triad}' not found in .claude/agents/ directory")
            return ValidationResult(
                valid=False,
                violations=violations,
                warnings=warnings,
                required_triad=required_triad,
                skipped_triads=skipped_triads,
                enforcement_mode=enforcement_mode
            )

        # Apply workflow rules
        for rule in self.schema.workflow_rules:
            if rule.rule_type == "sequential_progression":
                result = self._check_sequential_progression(instance, target_triad)
                violations.extend(result.get("violations", []))
                warnings.extend(result.get("warnings", []))
                skipped_triads.extend(result.get("skipped", []))

            elif rule.rule_type == "conditional_requirement":
                result = self._check_conditional_requirement(
                    rule, instance, target_triad, metrics
                )
                if result.get("required"):
                    required_triad = result["required_triad"]
                    violations.append(result["message"])

        return ValidationResult(
            valid=len(violations) == 0,
            violations=violations,
            warnings=warnings,
            required_triad=required_triad,
            skipped_triads=skipped_triads,
            enforcement_mode=enforcement_mode
        )

    def _get_enforcement_mode(self, triad_id: str) -> str:
        """Get enforcement mode for specific triad (with overrides).

        Args:
            triad_id: Triad identifier

        Returns:
            Enforcement mode ("strict", "recommended", or "optional")
        """
        # Check per-triad override first
        if triad_id in self.schema.enforcement.per_triad_overrides:
            return self.schema.enforcement.per_triad_overrides[triad_id]

        # Fall back to global mode
        return self.schema.enforcement.mode

    def _triad_in_schema(self, triad_id: str) -> bool:
        """Check if triad exists in schema.

        Args:
            triad_id: Triad identifier

        Returns:
            True if triad in schema, False otherwise
        """
        return any(t.id == triad_id for t in self.schema.triads)

    def _check_sequential_progression(
        self, instance: WorkflowInstance, target_triad: str
    ) -> dict:
        """Check if target triad follows sequential order.

        Compares target triad position with current position to detect:
        - Forward skips (skipping intermediate triads)
        - Backward movement (returning to earlier triad)

        Args:
            instance: Current workflow instance
            target_triad: Target triad to validate

        Returns:
            Dict with violations, warnings, and skipped triads
        """
        violations = []
        warnings = []
        skipped = []

        # Build expected sequence from schema (only required triads)
        triad_sequence = [t.id for t in self.schema.triads if t.required]

        # Find target position
        try:
            target_idx = triad_sequence.index(target_triad)
        except ValueError:
            # Target not in required sequence (optional triad?)
            # Still check all triads for position
            all_sequence = [t.id for t in self.schema.triads]
            try:
                target_idx = all_sequence.index(target_triad)
                triad_sequence = all_sequence  # Use all triads for checking
            except ValueError:
                # Target not in schema at all - should have been caught earlier
                return {"violations": [], "warnings": [], "skipped": []}

        # Find current position
        current_idx = -1
        current_triad = instance.current_triad
        if current_triad:
            try:
                current_idx = triad_sequence.index(current_triad)
            except ValueError:
                current_idx = -1

        # Check for skipped triads
        expected_next_idx = current_idx + 1
        if target_idx > expected_next_idx:
            # Skipping triads
            skipped = triad_sequence[expected_next_idx:target_idx]
            message = f"Sequential progression: skipping {len(skipped)} triad(s): {', '.join(skipped)}"
            warnings.append(message)

        elif target_idx < current_idx:
            # Going backward
            message = f"Sequential progression: moving backward from '{current_triad}' to '{target_triad}'"
            warnings.append(message)

        return {"violations": violations, "warnings": warnings, "skipped": skipped}

    def _check_conditional_requirement(
        self,
        rule: WorkflowRule,
        instance: WorkflowInstance,
        target_triad: str,
        metrics: Optional[MetricsResult]
    ) -> dict:
        """Check if a gate triad is required before target triad.

        Evaluates conditional requirement rules that specify:
        - gate_triad: Required triad (e.g., "garden-tending")
        - before_triad: Triad that requires gate (e.g., "deployment")
        - condition: When gate is required (e.g., significance_threshold)

        Args:
            rule: Conditional requirement rule
            instance: Current workflow instance
            target_triad: Target triad
            metrics: Optional metrics for condition evaluation

        Returns:
            Dict with required flag, required_triad, and message
        """
        gate_triad = rule.gate_triad
        before_triad = rule.before_triad
        condition = rule.condition or {}

        # Rule only applies if target is the "before_triad"
        if target_triad != before_triad:
            return {"required": False}

        # Check if gate already completed
        completed_ids = [
            t.triad_id for t in instance.completed_triads
        ]
        if gate_triad in completed_ids:
            return {"required": False}

        # Evaluate condition
        if not metrics:
            # No metrics provided, can't evaluate - don't require gate
            return {"required": False}

        condition_met = self._evaluate_condition(condition, metrics)

        if condition_met:
            return {
                "required": True,
                "required_triad": gate_triad,
                "message": f"Conditional requirement: '{gate_triad}' required before '{before_triad}' (work is substantial)"
            }

        return {"required": False}

    def _evaluate_condition(self, condition: dict, metrics: MetricsResult) -> bool:
        """Evaluate condition against metrics.

        Condition types:
        - significance_threshold: Check if metrics meet threshold
          - content_created.threshold: Lines/pages/etc threshold
          - components_modified: Number of components threshold
          - complexity: Complexity level threshold

        Args:
            condition: Condition definition from schema
            metrics: Metrics to evaluate

        Returns:
            True if condition met, False otherwise
        """
        condition_type = condition.get("type")

        if condition_type == "significance_threshold":
            metrics_config = condition.get("metrics", {})

            # Check content_created threshold
            if "content_created" in metrics_config:
                threshold = metrics_config["content_created"].get("threshold")
                units = metrics_config["content_created"].get("units")

                # Compare with actual metrics
                if metrics.content_created.get("units") == units:
                    quantity = metrics.content_created.get("quantity", 0)
                    if quantity >= threshold:
                        return True

            # Check components_modified threshold
            if "components_modified" in metrics_config:
                threshold = metrics_config["components_modified"]
                if metrics.components_modified >= threshold:
                    return True

            # Check complexity
            if "complexity" in metrics_config:
                required_complexity = metrics_config["complexity"]
                complexity_order = {"minimal": 0, "moderate": 1, "substantial": 2}
                metric_complexity_level = complexity_order.get(metrics.complexity, 0)
                required_complexity_level = complexity_order.get(required_complexity, 0)
                if metric_complexity_level >= required_complexity_level:
                    return True

        return False
