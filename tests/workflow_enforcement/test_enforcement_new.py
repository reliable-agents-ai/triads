"""Tests for workflow enforcement engine (Day 3 - MODULE-006).

Tests cover:
- Enforcement orchestration
- Enforcement mode application (strict, recommended, optional)
- Deviation recording
- User message generation
- Force skip handling
- Graceful degradation (no metrics)
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from triads.workflow_enforcement.enforcement_new import (
    WorkflowEnforcer,
    EnforcementResult,
)
from triads.workflow_enforcement.validator_new import ValidationResult
from triads.workflow_enforcement.schema_loader import (
    WorkflowSchema,
    TriadDefinition,
    WorkflowRule,
    EnforcementConfig,
    WorkflowSchemaLoader,
)
from triads.workflow_enforcement.instance_manager import (
    WorkflowInstance,
    WorkflowInstanceManager,
)
from triads.workflow_enforcement.triad_discovery import TriadDiscovery
from triads.workflow_enforcement.metrics import MetricsProvider, MetricsResult


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
def mock_schema_loader(software_schema):
    """Mock schema loader."""
    loader = Mock(spec=WorkflowSchemaLoader)
    loader.load_schema.return_value = software_schema
    return loader


@pytest.fixture
def mock_instance_manager():
    """Mock instance manager."""
    manager = Mock(spec=WorkflowInstanceManager)
    return manager


@pytest.fixture
def mock_discovery():
    """Mock triad discovery."""
    discovery = Mock(spec=TriadDiscovery)
    discovery.triad_exists.return_value = True
    return discovery


@pytest.fixture
def mock_metrics_provider():
    """Mock metrics provider."""
    provider = Mock(spec=MetricsProvider)
    provider.calculate_metrics.return_value = MetricsResult(
        content_created={"type": "code", "quantity": 50, "units": "lines"},
        components_modified=2,
        complexity="minimal",
        raw_data={}
    )
    return provider


@pytest.fixture
def instance_at_start():
    """Instance at start."""
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
def instance_after_implementation():
    """Instance after implementation."""
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


class TestWorkflowEnforcer:
    """Test WorkflowEnforcer class."""

    def test_enforce_valid_transition(self, mock_schema_loader, mock_instance_manager,
                                      mock_discovery, instance_at_start):
        """Test enforcing valid transition (should allow)."""
        mock_instance_manager.load_instance.return_value = instance_at_start

        enforcer = WorkflowEnforcer(
            mock_schema_loader,
            mock_instance_manager,
            mock_discovery,
            None
        )

        result = enforcer.enforce("test-instance", "idea-validation")

        assert result.allowed is True
        assert "✓" in result.message
        assert result.requires_reason is False

    def test_enforce_invalid_transition_strict_mode(self, mock_schema_loader, mock_instance_manager,
                                                     mock_discovery, instance_at_start):
        """Test enforcing invalid transition in strict mode (should block)."""
        mock_instance_manager.load_instance.return_value = instance_at_start

        enforcer = WorkflowEnforcer(
            mock_schema_loader,
            mock_instance_manager,
            mock_discovery,
            None
        )

        # Try to skip to deployment (strict mode)
        result = enforcer.enforce("test-instance", "deployment")

        assert result.allowed is False
        assert "🛑 CRITICAL" in result.message
        assert "STRICT" in result.message
        assert result.requires_reason is False  # Strict doesn't ask for reason, just blocks

    def test_enforce_invalid_transition_recommended_mode(self, mock_schema_loader, mock_instance_manager,
                                                          mock_discovery, instance_at_start):
        """Test enforcing invalid transition in recommended mode (should request reason)."""
        mock_instance_manager.load_instance.return_value = instance_at_start

        enforcer = WorkflowEnforcer(
            mock_schema_loader,
            mock_instance_manager,
            mock_discovery,
            None
        )

        # Try first triad (idea-validation) - should allow
        result = enforcer.enforce("test-instance", "idea-validation")
        assert result.allowed is True

        # Try skipping to implementation from start (skips idea + design)
        result = enforcer.enforce("test-instance", "implementation")

        assert result.allowed is False
        assert "⚠️  RECOMMENDED" in result.message
        assert "--skip --reason" in result.message
        assert result.requires_reason is True

    def test_enforce_invalid_transition_optional_mode(self, mock_instance_manager, mock_discovery, instance_at_start):
        """Test enforcing invalid transition in optional mode (should allow with log)."""
        # Create schema with optional enforcement
        optional_schema = WorkflowSchema(
            workflow_name="test",
            version="1.0.0",
            triads=[
                TriadDefinition(id="step1", name="Step 1", type="task", required=True),
                TriadDefinition(id="step2", name="Step 2", type="task", required=True),
            ],
            enforcement=EnforcementConfig(mode="optional"),
            workflow_rules=[
                WorkflowRule(rule_type="sequential_progression", track_deviations=True)
            ]
        )

        mock_schema_loader = Mock(spec=WorkflowSchemaLoader)
        mock_schema_loader.load_schema.return_value = optional_schema
        mock_instance_manager.load_instance.return_value = instance_at_start

        enforcer = WorkflowEnforcer(
            mock_schema_loader,
            mock_instance_manager,
            mock_discovery,
            None
        )

        # Try skipping step1
        result = enforcer.enforce("test-instance", "step2")

        assert result.allowed is True
        assert "ℹ️  Deviation logged" in result.message
        assert result.requires_reason is False

    def test_enforce_strict_with_force_skip(self, mock_schema_loader, mock_instance_manager,
                                            mock_discovery, instance_at_start):
        """Test force skip in strict mode with valid justification."""
        mock_instance_manager.load_instance.return_value = instance_at_start

        enforcer = WorkflowEnforcer(
            mock_schema_loader,
            mock_instance_manager,
            mock_discovery,
            None
        )

        # Force skip with valid reason
        result = enforcer.enforce(
            "test-instance",
            "deployment",
            skip_reason="Emergency production hotfix for critical bug #1234",
            force_skip=True
        )

        assert result.allowed is True
        assert "⚠️  EMERGENCY OVERRIDE" in result.message
        assert "Audit logged" in result.message

    def test_enforce_strict_force_skip_insufficient_reason(self, mock_schema_loader, mock_instance_manager,
                                                           mock_discovery, instance_at_start):
        """Test force skip in strict mode with insufficient justification."""
        mock_instance_manager.load_instance.return_value = instance_at_start

        enforcer = WorkflowEnforcer(
            mock_schema_loader,
            mock_instance_manager,
            mock_discovery,
            None
        )

        # Force skip with short reason
        result = enforcer.enforce(
            "test-instance",
            "deployment",
            skip_reason="hotfix",
            force_skip=True
        )

        assert result.allowed is False
        assert "requires detailed justification" in result.message
        assert "(min 20 chars)" in result.message

    def test_enforce_recommended_with_reason(self, mock_schema_loader, mock_instance_manager,
                                             mock_discovery, instance_at_start):
        """Test skipping in recommended mode with valid reason."""
        mock_instance_manager.load_instance.return_value = instance_at_start

        enforcer = WorkflowEnforcer(
            mock_schema_loader,
            mock_instance_manager,
            mock_discovery,
            None
        )

        # Skip with reason
        result = enforcer.enforce(
            "test-instance",
            "implementation",
            skip_reason="Design completed in Figma"
        )

        assert result.allowed is True
        assert "⚠️  Deviation recorded" in result.message
        assert "Design completed in Figma" in result.message

    def test_enforce_recommended_without_reason(self, mock_schema_loader, mock_instance_manager,
                                                mock_discovery, instance_at_start):
        """Test skipping in recommended mode without reason (should request it)."""
        mock_instance_manager.load_instance.return_value = instance_at_start

        enforcer = WorkflowEnforcer(
            mock_schema_loader,
            mock_instance_manager,
            mock_discovery,
            None
        )

        # Skip without reason
        result = enforcer.enforce("test-instance", "implementation")

        assert result.allowed is False
        assert result.requires_reason is True
        assert "--skip --reason" in result.message

    def test_enforce_optional_logs_deviation(self, mock_instance_manager, mock_discovery, instance_at_start):
        """Test that optional mode logs deviations even without reason."""
        optional_schema = WorkflowSchema(
            workflow_name="test",
            version="1.0.0",
            triads=[
                TriadDefinition(id="step1", name="Step 1", type="task", required=True),
                TriadDefinition(id="step2", name="Step 2", type="task", required=True),
            ],
            enforcement=EnforcementConfig(mode="optional"),
            workflow_rules=[
                WorkflowRule(rule_type="sequential_progression", track_deviations=True)
            ]
        )

        mock_schema_loader = Mock(spec=WorkflowSchemaLoader)
        mock_schema_loader.load_schema.return_value = optional_schema
        mock_instance_manager.load_instance.return_value = instance_at_start

        enforcer = WorkflowEnforcer(
            mock_schema_loader,
            mock_instance_manager,
            mock_discovery,
            None
        )

        result = enforcer.enforce("test-instance", "step2")

        # Should call add_deviation
        assert mock_instance_manager.add_deviation.called

    def test_enforce_records_deviation(self, mock_schema_loader, mock_instance_manager,
                                       mock_discovery, instance_at_start):
        """Test that deviations are recorded with all metadata."""
        mock_instance_manager.load_instance.return_value = instance_at_start

        enforcer = WorkflowEnforcer(
            mock_schema_loader,
            mock_instance_manager,
            mock_discovery,
            None
        )

        # Skip with reason
        result = enforcer.enforce(
            "test-instance",
            "implementation",
            skip_reason="Design completed externally"
        )

        # Verify add_deviation was called
        assert mock_instance_manager.add_deviation.called
        call_args = mock_instance_manager.add_deviation.call_args

        # Check deviation structure
        deviation = call_args[0][1]
        assert deviation["type"] == "skip_forward"
        assert deviation["reason"] == "Design completed externally"
        assert "timestamp" in deviation
        assert deviation["user"] == "test@example.com"

    def test_enforce_with_metrics(self, mock_schema_loader, mock_instance_manager,
                                  mock_discovery, instance_after_implementation):
        """Test enforcement with metrics provider."""
        mock_instance_manager.load_instance.return_value = instance_after_implementation

        # Mock metrics provider with substantial work
        mock_metrics = Mock(spec=MetricsProvider)
        mock_metrics.calculate_metrics.return_value = MetricsResult(
            content_created={"type": "code", "quantity": 257, "units": "lines"},
            components_modified=8,
            complexity="substantial",
            raw_data={}
        )

        enforcer = WorkflowEnforcer(
            mock_schema_loader,
            mock_instance_manager,
            mock_discovery,
            mock_metrics
        )

        # Try to deploy (should require garden-tending)
        result = enforcer.enforce("test-instance", "deployment")

        assert result.allowed is False
        assert "garden-tending" in result.message.lower()

    def test_enforce_without_metrics(self, mock_schema_loader, mock_instance_manager,
                                     mock_discovery, instance_after_implementation):
        """Test enforcement without metrics provider (graceful degradation)."""
        mock_instance_manager.load_instance.return_value = instance_after_implementation

        enforcer = WorkflowEnforcer(
            mock_schema_loader,
            mock_instance_manager,
            mock_discovery,
            None  # No metrics provider
        )

        # Should proceed without metrics (no gate required, garden-tending is optional)
        result = enforcer.enforce("test-instance", "deployment")

        # Deployment after implementation should be valid (garden-tending is optional)
        # No metrics = no gate requirement
        assert result.allowed is True

    def test_enforce_gate_required(self, mock_schema_loader, mock_instance_manager,
                                   mock_discovery, instance_after_implementation):
        """Test enforcement when gate triad is required."""
        mock_instance_manager.load_instance.return_value = instance_after_implementation

        # Metrics provider with substantial work
        mock_metrics = Mock(spec=MetricsProvider)
        mock_metrics.calculate_metrics.return_value = MetricsResult(
            content_created={"type": "code", "quantity": 150, "units": "lines"},
            components_modified=10,
            complexity="substantial",
            raw_data={}
        )

        enforcer = WorkflowEnforcer(
            mock_schema_loader,
            mock_instance_manager,
            mock_discovery,
            mock_metrics
        )

        result = enforcer.enforce("test-instance", "deployment")

        assert result.allowed is False
        assert "garden-tending" in result.validation_result.required_triad

    def test_classify_deviation_skip_forward(self, mock_schema_loader, mock_instance_manager,
                                             mock_discovery, instance_at_start):
        """Test deviation classification for skip forward."""
        mock_instance_manager.load_instance.return_value = instance_at_start

        enforcer = WorkflowEnforcer(
            mock_schema_loader,
            mock_instance_manager,
            mock_discovery,
            None
        )

        result = enforcer.enforce(
            "test-instance",
            "implementation",
            skip_reason="Design done elsewhere"
        )

        # Check deviation type
        deviation = mock_instance_manager.add_deviation.call_args[0][1]
        assert deviation["type"] == "skip_forward"

    def test_classify_deviation_skip_backward(self, mock_schema_loader, mock_instance_manager,
                                               mock_discovery, instance_after_implementation):
        """Test deviation classification for skip backward."""
        mock_instance_manager.load_instance.return_value = instance_after_implementation

        enforcer = WorkflowEnforcer(
            mock_schema_loader,
            mock_instance_manager,
            mock_discovery,
            None
        )

        result = enforcer.enforce(
            "test-instance",
            "design",
            skip_reason="Need to revise design"
        )

        # Check deviation type
        deviation = mock_instance_manager.add_deviation.call_args[0][1]
        assert deviation["type"] == "skip_backward"

    def test_classify_deviation_gate_skip(self, mock_schema_loader, mock_instance_manager,
                                          mock_discovery, instance_after_implementation):
        """Test deviation classification for gate skip."""
        mock_instance_manager.load_instance.return_value = instance_after_implementation

        # Metrics indicating gate required
        mock_metrics = Mock(spec=MetricsProvider)
        mock_metrics.calculate_metrics.return_value = MetricsResult(
            content_created={"type": "code", "quantity": 200, "units": "lines"},
            components_modified=10,
            complexity="substantial",
            raw_data={}
        )

        enforcer = WorkflowEnforcer(
            mock_schema_loader,
            mock_instance_manager,
            mock_discovery,
            mock_metrics
        )

        # Force skip gate requirement with valid reason
        result = enforcer.enforce(
            "test-instance",
            "deployment",
            skip_reason="Emergency hotfix required for critical production bug",
            force_skip=True
        )

        # Should allow with force skip and record deviation
        assert result.allowed is True

        # Check deviation was recorded
        assert mock_instance_manager.add_deviation.called
        deviation = mock_instance_manager.add_deviation.call_args[0][1]
        assert deviation["type"] == "gate_skip"
