"""Workflow schema loader with validation.

This module loads and validates workflow.json schemas that define:
- Workflow triads (steps in the workflow)
- Enforcement rules (sequential, conditional)
- Enforcement modes (strict, recommended, optional)

The schema loader is GENERIC - it works with any workflow type (RFP writing,
software development, content creation, etc.). No hardcoded triad names.

Per ADR-GENERIC: Schema-driven, domain-agnostic workflow enforcement
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import logging

logger = logging.getLogger(__name__)



class SchemaValidationError(Exception):
    """Raised when workflow schema validation fails."""
    pass


@dataclass
class TriadDefinition:
    """Definition of a triad in the workflow.

    Attributes:
        id: Unique triad identifier (e.g., "idea-validation", "rfp-analysis")
        name: Human-readable name (e.g., "Idea Validation", "RFP Analysis")
        type: Triad type (e.g., "research", "development", "review")
        required: Whether this triad is required in the workflow
        metadata: Optional additional metadata
    """
    id: str
    name: str
    type: str
    required: bool
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowRule:
    """Definition of a workflow enforcement rule.

    Attributes:
        rule_type: Type of rule ("sequential_progression", "conditional_requirement")
        track_deviations: Whether to track deviations from this rule
        gate_triad: For conditional rules, the required triad
        before_triad: For conditional rules, the triad that requires the gate
        condition: Condition definition (e.g., significance threshold)
        bypass_allowed: Whether bypass is allowed for this rule
        metadata: Optional additional metadata
    """
    rule_type: str
    track_deviations: bool = True
    gate_triad: str | None = None
    before_triad: str | None = None
    condition: dict[str, Any] | None = None
    bypass_allowed: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EnforcementConfig:
    """Enforcement configuration for workflow.

    Attributes:
        mode: Default enforcement mode ("strict", "recommended", "optional")
        per_triad_overrides: Per-triad enforcement mode overrides
    """
    mode: str = "recommended"
    per_triad_overrides: dict[str, str] = field(default_factory=dict)


@dataclass
class WorkflowSchema:
    """Complete workflow schema.

    Attributes:
        workflow_name: Unique workflow identifier (e.g., "software-development", "rfp-writing")
        version: Schema version (semantic versioning)
        triads: List of triad definitions (in order)
        enforcement: Enforcement configuration
        workflow_rules: List of workflow rules
        metadata: Optional additional metadata
    """
    workflow_name: str
    version: str
    triads: list[TriadDefinition]
    enforcement: EnforcementConfig
    workflow_rules: list[WorkflowRule] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def get_triad(self, triad_id: str) -> TriadDefinition | None:
        """Get triad definition by ID.

        Args:
            triad_id: Triad identifier

        Returns:
            TriadDefinition if found, None otherwise

        Example:
            triad = schema.get_triad("design")
            if triad:
                print(f"Found: {triad.name}")
        """
        for triad in self.triads:
            if triad.id == triad_id:
                return triad
        return None

    def get_triads_by_type(self, triad_type: str) -> list[TriadDefinition]:
        """Get all triads of a specific type.

        Args:
            triad_type: Triad type to filter by

        Returns:
            List of matching triads

        Example:
            research_triads = schema.get_triads_by_type("research")
        """
        return [t for t in self.triads if t.type == triad_type]

    def get_required_triads(self) -> list[TriadDefinition]:
        """Get all required triads.

        Returns:
            List of required triads

        Example:
            required = schema.get_required_triads()
            print(f"Must complete {len(required)} triads")
        """
        return [t for t in self.triads if t.required]

    def get_enforcement_mode(self, triad_id: str) -> str:
        """Get enforcement mode for a triad (with override support).

        Args:
            triad_id: Triad identifier

        Returns:
            Enforcement mode ("strict", "recommended", or "optional")

        Example:
            mode = schema.get_enforcement_mode("legal-review")
            if mode == "strict":
                print("This triad cannot be skipped")
        """
        # Check for per-triad override
        if triad_id in self.enforcement.per_triad_overrides:
            return self.enforcement.per_triad_overrides[triad_id]

        # Return default mode
        return self.enforcement.mode

    def get_triad_index(self, triad_id: str) -> int | None:
        """Get index of triad in workflow order.

        Args:
            triad_id: Triad identifier

        Returns:
            Index (0-based) if found, None otherwise

        Example:
            idx = schema.get_triad_index("implementation")
            if idx is not None:
                print(f"Implementation is step {idx + 1}")
        """
        for idx, triad in enumerate(self.triads):
            if triad.id == triad_id:
                return idx
        return None


class WorkflowSchemaLoader:
    """Loads and validates workflow schemas from JSON files.

    Example:
        loader = WorkflowSchemaLoader(".claude/workflow.json")
        schema = loader.load_schema()
        print(f"Loaded workflow: {schema.workflow_name}")
    """

    # Valid enforcement modes
    VALID_MODES = {"strict", "recommended", "optional"}

    # Valid rule types
    VALID_RULE_TYPES = {"sequential_progression", "conditional_requirement"}

    def __init__(self, schema_file: Path | str | None = None):
        """Initialize schema loader.

        Args:
            schema_file: Path to workflow.json (default: .claude/workflow.json)
        """
        if schema_file is None:
            schema_file = Path(".claude/workflow.json")
        self.schema_file = Path(schema_file)

    def load_schema(self) -> WorkflowSchema:
        """Load and validate workflow schema.

        Returns:
            Validated WorkflowSchema instance

        Raises:
            SchemaValidationError: If schema is invalid

        Example:
            loader = WorkflowSchemaLoader()
            try:
                schema = loader.load_schema()
                print(f"Loaded {len(schema.triads)} triads")
            except SchemaValidationError as e:
                print(f"Invalid schema: {e}")
        """
        # Check file exists
        if not self.schema_file.exists():
            raise SchemaValidationError(
                f"Schema file not found: {self.schema_file}\n"
                f"Expected: .claude/workflow.json"
            )

        # Parse JSON
        try:
            with open(self.schema_file, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise SchemaValidationError(
                f"Invalid JSON in schema file: {e}\n"
                f"File: {self.schema_file}"
            )

        # Validate and parse schema
        return self._parse_schema(data)

    def _parse_schema(self, data: dict[str, Any]) -> WorkflowSchema:
        """Parse and validate schema data.

        Args:
            data: Parsed JSON data

        Returns:
            Validated WorkflowSchema

        Raises:
            SchemaValidationError: If validation fails
        """
        # Check required top-level fields
        self._require_field(data, "workflow_name")
        self._require_field(data, "version")
        self._require_field(data, "triads")

        # Parse triads
        triads = self._parse_triads(data["triads"])

        # Parse enforcement config (with defaults)
        enforcement = self._parse_enforcement(data.get("enforcement", {}))

        # Parse workflow rules (optional)
        workflow_rules = self._parse_rules(data.get("workflow_rules", []))

        # Build schema
        return WorkflowSchema(
            workflow_name=data["workflow_name"],
            version=data["version"],
            triads=triads,
            enforcement=enforcement,
            workflow_rules=workflow_rules,
            metadata=data.get("metadata", {})
        )

    def _parse_triads(self, triads_data: list[dict[str, Any]]) -> list[TriadDefinition]:
        """Parse triads list.

        Args:
            triads_data: List of triad definitions

        Returns:
            List of TriadDefinition instances

        Raises:
            SchemaValidationError: If validation fails
        """
        if not isinstance(triads_data, list):
            raise SchemaValidationError("Triads must be a list")

        if len(triads_data) == 0:
            raise SchemaValidationError(
                "Triads list cannot be empty. "
                "Workflow must have at least one triad."
            )

        triads = []
        for idx, triad_data in enumerate(triads_data):
            try:
                triad = self._parse_triad(triad_data)
                triads.append(triad)
            except SchemaValidationError as e:
                raise SchemaValidationError(
                    f"Error in triad {idx}: {e}"
                )

        return triads

    def _parse_triad(self, triad_data: dict[str, Any]) -> TriadDefinition:
        """Parse single triad definition.

        Args:
            triad_data: Triad data dictionary

        Returns:
            TriadDefinition instance

        Raises:
            SchemaValidationError: If validation fails
        """
        # Check required fields
        self._require_field(triad_data, "id", "Triad")
        self._require_field(triad_data, "name", "Triad")
        self._require_field(triad_data, "type", "Triad")
        self._require_field(triad_data, "required", "Triad")

        return TriadDefinition(
            id=triad_data["id"],
            name=triad_data["name"],
            type=triad_data["type"],
            required=triad_data["required"],
            metadata=triad_data.get("metadata", {})
        )

    def _parse_enforcement(self, enforcement_data: dict[str, Any]) -> EnforcementConfig:
        """Parse enforcement configuration.

        Args:
            enforcement_data: Enforcement config data

        Returns:
            EnforcementConfig instance

        Raises:
            SchemaValidationError: If validation fails
        """
        # Get mode (default: recommended)
        mode = enforcement_data.get("mode", "recommended")

        # Validate mode
        if mode not in self.VALID_MODES:
            raise SchemaValidationError(
                f"Invalid enforcement mode: {mode}\n"
                f"Must be one of: {', '.join(sorted(self.VALID_MODES))}"
            )

        # Get overrides (default: empty dict)
        overrides = enforcement_data.get("per_triad_overrides", {})

        # Validate override modes
        for triad_id, override_mode in overrides.items():
            if override_mode not in self.VALID_MODES:
                raise SchemaValidationError(
                    f"Invalid enforcement mode for triad '{triad_id}': {override_mode}\n"
                    f"Must be one of: {', '.join(sorted(self.VALID_MODES))}"
                )

        return EnforcementConfig(
            mode=mode,
            per_triad_overrides=overrides
        )

    def _parse_rules(self, rules_data: list[dict[str, Any]]) -> list[WorkflowRule]:
        """Parse workflow rules.

        Args:
            rules_data: List of rule definitions

        Returns:
            List of WorkflowRule instances

        Raises:
            SchemaValidationError: If validation fails
        """
        if not isinstance(rules_data, list):
            raise SchemaValidationError("Workflow rules must be a list")

        rules = []
        for idx, rule_data in enumerate(rules_data):
            try:
                rule = self._parse_rule(rule_data)
                rules.append(rule)
            except SchemaValidationError as e:
                raise SchemaValidationError(
                    f"Error in rule {idx}: {e}"
                )

        return rules

    def _parse_rule(self, rule_data: dict[str, Any]) -> WorkflowRule:
        """Parse single workflow rule.

        Args:
            rule_data: Rule data dictionary

        Returns:
            WorkflowRule instance

        Raises:
            SchemaValidationError: If validation fails
        """
        # Check required field
        self._require_field(rule_data, "rule_type", "Rule")

        rule_type = rule_data["rule_type"]

        # Validate rule type
        if rule_type not in self.VALID_RULE_TYPES:
            raise SchemaValidationError(
                f"Invalid rule type: {rule_type}\n"
                f"Must be one of: {', '.join(sorted(self.VALID_RULE_TYPES))}"
            )

        # Build rule
        return WorkflowRule(
            rule_type=rule_type,
            track_deviations=rule_data.get("track_deviations", True),
            gate_triad=rule_data.get("gate_triad"),
            before_triad=rule_data.get("before_triad"),
            condition=rule_data.get("condition"),
            bypass_allowed=rule_data.get("bypass_allowed", False),
            metadata=rule_data.get("metadata", {})
        )

    def _require_field(self, data: dict[str, Any], field: str, context: str = "") -> None:
        """Check that required field exists in data.

        Args:
            data: Data dictionary
            field: Required field name
            context: Context for error message (e.g., "Triad")

        Raises:
            SchemaValidationError: If field is missing
        """
        if field not in data:
            prefix = f"{context} missing" if context else "Missing"
            raise SchemaValidationError(
                f"{prefix} required field: {field}"
            )
