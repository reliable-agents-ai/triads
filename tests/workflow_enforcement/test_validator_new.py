"""Tests for generic workflow validator (Day 3 - MODULE-005).

Tests cover:
- Validation of transitions between triads
- Sequential progression checking
- Conditional requirement evaluation
- Enforcement mode handling
- Per-triad override support
- Schema-driven validation (no hardcoded triad names)
"""

import pytest
from unittest.mock import Mock
from triads.workflow_enforcement.validator_new import (
    WorkflowValidator,
    ValidationResult,
)
from triads.workflow_enforcement.schema_loader import (
    WorkflowSchema,
    TriadDefinition,
    WorkflowRule,
    EnforcementConfig,
)
from triads.workflow_enforcement.instance_manager import WorkflowInstance
from triads.workflow_enforcement.triad_discovery import TriadDiscovery, TriadInfo
from triads.workflow_enforcement.metrics import MetricsResult


@pytest.fixture
def software_schema():
    """Software development workflow schema."""
    return WorkflowSchema(
        workflow_name="software-development",
        version="1.0.0",
        triads=[
            TriadDefinition(id="idea-validation", name="Idea Validation", type="research", required=True),
            TriadDefinition(id="design", name="Design", type="architecture", required=True),
            TriadDefinition(id="implementation", name="Implementation", type="development", required=True),
            TriadDefinition(id="garden-tending", name="Garden Tending", type="quality", required=False),
            TriadDefinition(id="deployment", name="Deployment", type="release", required=True),
        ],
        enforcement=EnforcementConfig(
            mode="recommended",
            per_triad_overrides={"deployment": "strict"}
        ),
        workflow_rules=[
            WorkflowRule(
                rule_type="sequential_progression",
                track_deviations=True
            ),
            WorkflowRule(
                rule_type="conditional_requirement",
                gate_triad="garden-tending",
                before_triad="deployment",
                condition={
                    "type": "significance_threshold",
                    "metrics": {
                        "content_created": {"threshold": 100, "units": "lines"}
                    }
                },
                bypass_allowed=True
            )
        ]
    )


@pytest.fixture
def mock_discovery():
    """Mock triad discovery with all triads present."""
    discovery = Mock(spec=TriadDiscovery)
    # All triads exist
    discovery.triad_exists.return_value = True
    return discovery


@pytest.fixture
def instance_at_start():
    """Workflow instance at start (no triads completed)."""
    return WorkflowInstance(
        instance_id="test-instance",
        workflow_type="software-development",
        metadata={"started_by": "test@example.com"},
        workflow_progress={
            "current_triad": None,
            "completed_triads": [],
            "skipped_triads": []
        }
    )


@pytest.fixture
def instance_after_idea():
    """Workflow instance after idea-validation completed."""
    return WorkflowInstance(
        instance_id="test-instance",
        workflow_type="software-development",
        metadata={"started_by": "test@example.com"},
        workflow_progress={
            "current_triad": "idea-validation",
            "completed_triads": [
                {"triad_id": "idea-validation", "completed_at": "2025-10-17T10:00:00"}
            ],
            "skipped_triads": []
        }
    )


@pytest.fixture
def instance_after_implementation():
    """Workflow instance after implementation completed."""
    return WorkflowInstance(
        instance_id="test-instance",
        workflow_type="software-development",
        metadata={"started_by": "test@example.com"},
        workflow_progress={
            "current_triad": "implementation",
            "completed_triads": [
                {"triad_id": "idea-validation", "completed_at": "2025-10-17T10:00:00"},
                {"triad_id": "design", "completed_at": "2025-10-17T11:00:00"},
                {"triad_id": "implementation", "completed_at": "2025-10-17T12:00:00"}
            ],
            "skipped_triads": []
        }
    )


@pytest.fixture
def substantial_metrics():
    """Metrics indicating substantial work."""
    return MetricsResult(
        content_created={"type": "code", "quantity": 257, "units": "lines"},
        components_modified=8,
        complexity="substantial",
        raw_data={"loc_added": 257}
    )


@pytest.fixture
def minimal_metrics():
    """Metrics indicating minimal work."""
    return MetricsResult(
        content_created={"type": "code", "quantity": 30, "units": "lines"},
        components_modified=2,
        complexity="minimal",
        raw_data={"loc_added": 30}
    )


class TestWorkflowValidator:
    """Test WorkflowValidator class."""

    def test_validate_valid_first_triad(self, software_schema, mock_discovery, instance_at_start):
        """Test validating first triad in workflow (should be valid)."""
        validator = WorkflowValidator(software_schema, mock_discovery)

        result = validator.validate_transition(instance_at_start, "idea-validation")

        assert result.valid is True
        assert len(result.violations) == 0
        assert len(result.warnings) == 0
        assert result.enforcement_mode == "recommended"

    def test_validate_valid_sequential_transition(self, software_schema, mock_discovery, instance_after_idea):
        """Test validating sequential progression (idea → design)."""
        validator = WorkflowValidator(software_schema, mock_discovery)

        result = validator.validate_transition(instance_after_idea, "design")

        assert result.valid is True
        assert len(result.violations) == 0
        assert len(result.warnings) == 0

    def test_validate_triad_not_in_schema(self, software_schema, mock_discovery, instance_at_start):
        """Test validating triad not defined in schema."""
        validator = WorkflowValidator(software_schema, mock_discovery)

        result = validator.validate_transition(instance_at_start, "unknown-triad")

        assert result.valid is False
        assert len(result.violations) == 1
        assert "not found in workflow schema" in result.violations[0]

    def test_validate_triad_not_in_filesystem(self, software_schema, instance_at_start):
        """Test validating triad not present in filesystem."""
        # Mock discovery that says triad doesn't exist
        discovery = Mock(spec=TriadDiscovery)
        discovery.triad_exists.return_value = False

        validator = WorkflowValidator(software_schema, discovery)
        result = validator.validate_transition(instance_at_start, "idea-validation")

        assert result.valid is False
        assert len(result.violations) == 1
        assert "not found in .claude/agents/" in result.violations[0]

    def test_validate_skip_one_triad(self, software_schema, mock_discovery, instance_after_idea):
        """Test skipping one triad (idea → implementation, skipping design)."""
        validator = WorkflowValidator(software_schema, mock_discovery)

        result = validator.validate_transition(instance_after_idea, "implementation")

        # Should generate warning (not violation) about skipping design
        assert len(result.warnings) > 0
        assert "skipping" in result.warnings[0].lower()
        assert "design" in result.skipped_triads

    def test_validate_skip_multiple_triads(self, software_schema, mock_discovery, instance_at_start):
        """Test skipping multiple triads (start → deployment, skipping 3 required triads)."""
        validator = WorkflowValidator(software_schema, mock_discovery)

        result = validator.validate_transition(instance_at_start, "deployment")

        # Should warn about skipping multiple triads
        # Note: garden-tending is optional (required=False), so only 3 required triads are skipped
        assert len(result.warnings) > 0
        assert len(result.skipped_triads) == 3  # idea, design, impl (garden-tending is optional)
        assert "idea-validation" in result.skipped_triads
        assert "design" in result.skipped_triads
        assert "implementation" in result.skipped_triads

    def test_validate_backward_movement(self, software_schema, mock_discovery, instance_after_implementation):
        """Test moving backward in workflow (implementation → design)."""
        validator = WorkflowValidator(software_schema, mock_discovery)

        result = validator.validate_transition(instance_after_implementation, "design")

        # Should generate warning about backward movement
        assert len(result.warnings) > 0
        assert "backward" in result.warnings[0].lower()

    def test_validate_conditional_requirement_met(self, software_schema, mock_discovery,
                                                   instance_after_implementation, substantial_metrics):
        """Test conditional requirement when condition is met (requires gate)."""
        validator = WorkflowValidator(software_schema, mock_discovery)

        result = validator.validate_transition(
            instance_after_implementation,
            "deployment",
            metrics=substantial_metrics
        )

        # Garden tending required because work is substantial
        assert result.valid is False
        assert result.required_triad == "garden-tending"
        assert len(result.violations) > 0
        assert "garden-tending" in result.violations[0].lower()

    def test_validate_conditional_requirement_not_met(self, software_schema, mock_discovery,
                                                       instance_after_implementation, minimal_metrics):
        """Test conditional requirement when condition not met (gate not required)."""
        validator = WorkflowValidator(software_schema, mock_discovery)

        result = validator.validate_transition(
            instance_after_implementation,
            "deployment",
            metrics=minimal_metrics
        )

        # Garden tending NOT required because work is minimal
        assert result.required_triad is None
        # Only warnings about skipping (not violations)
        assert len(result.violations) == 0

    def test_validate_conditional_requirement_gate_completed(self, software_schema, mock_discovery, substantial_metrics):
        """Test conditional requirement when gate already completed."""
        # Instance with garden-tending already done
        instance = WorkflowInstance(
            instance_id="test-instance",
            workflow_type="software-development",
            metadata={"started_by": "test@example.com"},
            workflow_progress={
                "current_triad": "garden-tending",
                "completed_triads": [
                    {"triad_id": "idea-validation", "completed_at": "2025-10-17T10:00:00"},
                    {"triad_id": "design", "completed_at": "2025-10-17T11:00:00"},
                    {"triad_id": "implementation", "completed_at": "2025-10-17T12:00:00"},
                    {"triad_id": "garden-tending", "completed_at": "2025-10-17T13:00:00"}
                ],
                "skipped_triads": []
            }
        )

        validator = WorkflowValidator(software_schema, mock_discovery)
        result = validator.validate_transition(instance, "deployment", metrics=substantial_metrics)

        # Should be valid - gate already completed
        assert result.required_triad is None
        assert len(result.violations) == 0

    def test_validate_enforcement_mode_strict(self, software_schema, mock_discovery, instance_after_implementation):
        """Test enforcement mode for strict triad (deployment has strict override)."""
        validator = WorkflowValidator(software_schema, mock_discovery)

        result = validator.validate_transition(instance_after_implementation, "deployment")

        # Deployment has strict override in schema
        assert result.enforcement_mode == "strict"

    def test_validate_enforcement_mode_recommended(self, software_schema, mock_discovery, instance_after_idea):
        """Test enforcement mode for recommended triad (default mode)."""
        validator = WorkflowValidator(software_schema, mock_discovery)

        result = validator.validate_transition(instance_after_idea, "design")

        # Design has no override, uses default
        assert result.enforcement_mode == "recommended"

    def test_validate_enforcement_mode_optional(self, mock_discovery, instance_at_start):
        """Test enforcement mode for optional mode workflow."""
        # Create schema with optional mode
        optional_schema = WorkflowSchema(
            workflow_name="test",
            version="1.0.0",
            triads=[
                TriadDefinition(id="step1", name="Step 1", type="task", required=True),
                TriadDefinition(id="step2", name="Step 2", type="task", required=True),
            ],
            enforcement=EnforcementConfig(mode="optional"),
            workflow_rules=[]
        )

        validator = WorkflowValidator(optional_schema, mock_discovery)
        result = validator.validate_transition(instance_at_start, "step1")

        assert result.enforcement_mode == "optional"

    def test_validate_per_triad_override(self, software_schema, mock_discovery, instance_at_start):
        """Test per-triad enforcement override."""
        validator = WorkflowValidator(software_schema, mock_discovery)

        # Deployment has strict override
        result = validator.validate_transition(instance_at_start, "deployment")
        assert result.enforcement_mode == "strict"

        # Design uses default mode
        result = validator.validate_transition(instance_at_start, "design")
        assert result.enforcement_mode == "recommended"

    def test_evaluate_condition_content_created(self, software_schema, mock_discovery,
                                                 instance_after_implementation):
        """Test condition evaluation based on content_created threshold."""
        validator = WorkflowValidator(software_schema, mock_discovery)

        # Metrics meeting threshold (100+ lines)
        high_metrics = MetricsResult(
            content_created={"type": "code", "quantity": 150, "units": "lines"},
            components_modified=5,
            complexity="substantial",
            raw_data={}
        )

        result = validator.validate_transition(
            instance_after_implementation,
            "deployment",
            metrics=high_metrics
        )

        assert result.required_triad == "garden-tending"

        # Metrics below threshold (<100 lines)
        low_metrics = MetricsResult(
            content_created={"type": "code", "quantity": 50, "units": "lines"},
            components_modified=2,
            complexity="minimal",
            raw_data={}
        )

        result = validator.validate_transition(
            instance_after_implementation,
            "deployment",
            metrics=low_metrics
        )

        assert result.required_triad is None

    def test_evaluate_condition_components_modified(self, mock_discovery):
        """Test condition evaluation based on components_modified threshold."""
        # Schema with components_modified condition
        schema = WorkflowSchema(
            workflow_name="test",
            version="1.0.0",
            triads=[
                TriadDefinition(id="step1", name="Step 1", type="task", required=True),
                TriadDefinition(id="gate", name="Gate", type="quality", required=False),
                TriadDefinition(id="step2", name="Step 2", type="task", required=True),
            ],
            enforcement=EnforcementConfig(mode="recommended"),
            workflow_rules=[
                WorkflowRule(
                    rule_type="conditional_requirement",
                    gate_triad="gate",
                    before_triad="step2",
                    condition={
                        "type": "significance_threshold",
                        "metrics": {"components_modified": 5}
                    }
                )
            ]
        )

        instance = WorkflowInstance(
            instance_id="test",
            workflow_type="test",
            workflow_progress={
                "current_triad": "step1",
                "completed_triads": [{"triad_id": "step1", "completed_at": "2025-10-17"}]
            }
        )

        validator = WorkflowValidator(schema, mock_discovery)

        # Many components modified
        high_metrics = MetricsResult(
            content_created={"type": "code", "quantity": 50, "units": "lines"},
            components_modified=10,
            complexity="moderate",
            raw_data={}
        )

        result = validator.validate_transition(instance, "step2", metrics=high_metrics)
        assert result.required_triad == "gate"

        # Few components modified
        low_metrics = MetricsResult(
            content_created={"type": "code", "quantity": 50, "units": "lines"},
            components_modified=2,
            complexity="minimal",
            raw_data={}
        )

        result = validator.validate_transition(instance, "step2", metrics=low_metrics)
        assert result.required_triad is None

    def test_evaluate_condition_complexity(self, mock_discovery):
        """Test condition evaluation based on complexity threshold."""
        # Schema with complexity condition
        schema = WorkflowSchema(
            workflow_name="test",
            version="1.0.0",
            triads=[
                TriadDefinition(id="step1", name="Step 1", type="task", required=True),
                TriadDefinition(id="gate", name="Gate", type="quality", required=False),
                TriadDefinition(id="step2", name="Step 2", type="task", required=True),
            ],
            enforcement=EnforcementConfig(mode="recommended"),
            workflow_rules=[
                WorkflowRule(
                    rule_type="conditional_requirement",
                    gate_triad="gate",
                    before_triad="step2",
                    condition={
                        "type": "significance_threshold",
                        "metrics": {"complexity": "moderate"}
                    }
                )
            ]
        )

        instance = WorkflowInstance(
            instance_id="test",
            workflow_type="test",
            workflow_progress={
                "current_triad": "step1",
                "completed_triads": [{"triad_id": "step1", "completed_at": "2025-10-17"}]
            }
        )

        validator = WorkflowValidator(schema, mock_discovery)

        # Substantial complexity (meets threshold)
        high_metrics = MetricsResult(
            content_created={"type": "code", "quantity": 50, "units": "lines"},
            components_modified=2,
            complexity="substantial",
            raw_data={}
        )

        result = validator.validate_transition(instance, "step2", metrics=high_metrics)
        assert result.required_triad == "gate"

        # Minimal complexity (below threshold)
        low_metrics = MetricsResult(
            content_created={"type": "code", "quantity": 50, "units": "lines"},
            components_modified=2,
            complexity="minimal",
            raw_data={}
        )

        result = validator.validate_transition(instance, "step2", metrics=low_metrics)
        assert result.required_triad is None

    def test_sequential_progression_optional_triad(self, software_schema, mock_discovery, instance_after_idea):
        """Test sequential progression with optional triad (garden-tending)."""
        validator = WorkflowValidator(software_schema, mock_discovery)

        # Skipping optional garden-tending
        result = validator.validate_transition(instance_after_idea, "deployment")

        # Should skip multiple triads including optional one
        assert len(result.skipped_triads) > 0

    def test_no_metrics_provided(self, software_schema, mock_discovery, instance_after_implementation):
        """Test validation when no metrics provided (graceful degradation)."""
        validator = WorkflowValidator(software_schema, mock_discovery)

        # No metrics provided
        result = validator.validate_transition(instance_after_implementation, "deployment", metrics=None)

        # Should not require gate if metrics unavailable
        assert result.required_triad is None
        # Should still check sequential progression
        # Note: garden-tending is optional (required=False), so it's not in the required sequence
        # When checking deployment after implementation, no required triads are skipped
        assert len(result.skipped_triads) == 0  # No required triads skipped (garden-tending is optional)
