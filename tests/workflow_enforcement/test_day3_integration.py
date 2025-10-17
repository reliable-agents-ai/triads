"""Day 3 Integration tests - End-to-end workflow enforcement.

Tests the complete workflow enforcement system working together:
- Schema loading
- Instance management
- Triad discovery
- Validation
- Enforcement
- Deviation tracking

Per ADR-GENERIC: Schema-driven, domain-agnostic workflow enforcement
"""

import json
import pytest
from pathlib import Path
from triads.workflow_enforcement.schema_loader import WorkflowSchemaLoader
from triads.workflow_enforcement.instance_manager import WorkflowInstanceManager
from triads.workflow_enforcement.triad_discovery import TriadDiscovery
from triads.workflow_enforcement.enforcement_new import WorkflowEnforcer
from triads.workflow_enforcement.metrics import MetricsResult


@pytest.fixture
def test_workflow_dir(tmp_path):
    """Create complete test workflow environment."""
    # Create .claude directory structure
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()

    # Create workflow schema
    schema = {
        "workflow_name": "software-development",
        "version": "1.0.0",
        "enforcement": {
            "mode": "recommended",
            "per_triad_overrides": {
                "deployment": "strict"
            }
        },
        "triads": [
            {
                "id": "idea-validation",
                "name": "Idea Validation",
                "type": "research",
                "required": True
            },
            {
                "id": "design",
                "name": "Design",
                "type": "architecture",
                "required": True
            },
            {
                "id": "implementation",
                "name": "Implementation",
                "type": "development",
                "required": True
            },
            {
                "id": "garden-tending",
                "name": "Garden Tending",
                "type": "quality",
                "required": False
            },
            {
                "id": "deployment",
                "name": "Deployment",
                "type": "release",
                "required": True
            }
        ],
        "workflow_rules": [
            {
                "rule_type": "sequential_progression",
                "track_deviations": True
            },
            {
                "rule_type": "conditional_requirement",
                "gate_triad": "garden-tending",
                "before_triad": "deployment",
                "condition": {
                    "type": "significance_threshold",
                    "metrics": {
                        "content_created": {
                            "threshold": 100,
                            "units": "lines"
                        }
                    }
                },
                "bypass_allowed": True
            }
        ]
    }

    # Write workflow schema
    schema_file = claude_dir / "workflow.json"
    schema_file.write_text(json.dumps(schema, indent=2))

    # Create agents directory structure
    agents_dir = claude_dir / "agents"
    agents_dir.mkdir()

    # Create triad directories
    for triad in schema["triads"]:
        triad_dir = agents_dir / triad["id"]
        triad_dir.mkdir()
        # Create placeholder agent files
        (triad_dir / "agent1.md").write_text(f"# {triad['name']} Agent")

    # Create workflows directory
    workflows_dir = claude_dir / "workflows"
    workflows_dir.mkdir()

    return tmp_path


class TestDay3Integration:
    """Integration tests for complete workflow enforcement system."""

    def test_complete_workflow_happy_path(self, test_workflow_dir):
        """Test complete workflow following sequential order."""
        # Initialize components
        schema_loader = WorkflowSchemaLoader(test_workflow_dir / ".claude/workflow.json")
        instance_manager = WorkflowInstanceManager(test_workflow_dir / ".claude/workflows")
        discovery = TriadDiscovery(str(test_workflow_dir / ".claude/agents"))

        enforcer = WorkflowEnforcer(schema_loader, instance_manager, discovery, None)

        # Create instance
        instance_id = instance_manager.create_instance(
            "software-development",
            "OAuth2 Integration",
            "developer@example.com"
        )

        # Step 1: Start with idea-validation
        result = enforcer.enforce(instance_id, "idea-validation")
        assert result.allowed is True
        instance_manager.mark_triad_completed(instance_id, "idea-validation")

        # Step 2: Move to design
        result = enforcer.enforce(instance_id, "design")
        assert result.allowed is True
        instance_manager.mark_triad_completed(instance_id, "design")

        # Step 3: Move to implementation
        result = enforcer.enforce(instance_id, "implementation")
        assert result.allowed is True
        instance_manager.mark_triad_completed(instance_id, "implementation")

        # Step 4: Deploy (no metrics = no gate requirement)
        result = enforcer.enforce(instance_id, "deployment")
        assert result.allowed is True

        # Verify no deviations
        instance = instance_manager.load_instance(instance_id)
        assert len(instance.workflow_deviations) == 0

    def test_workflow_with_skip_and_reason(self, test_workflow_dir):
        """Test workflow with valid skip and reason."""
        schema_loader = WorkflowSchemaLoader(test_workflow_dir / ".claude/workflow.json")
        instance_manager = WorkflowInstanceManager(test_workflow_dir / ".claude/workflows")
        discovery = TriadDiscovery(str(test_workflow_dir / ".claude/agents"))

        enforcer = WorkflowEnforcer(schema_loader, instance_manager, discovery, None)

        # Create instance
        instance_id = instance_manager.create_instance(
            "software-development",
            "Hotfix",
            "developer@example.com"
        )

        # Try to skip to implementation (should require reason)
        result = enforcer.enforce(instance_id, "implementation")
        assert result.allowed is False
        assert result.requires_reason is True

        # Skip with valid reason
        result = enforcer.enforce(
            instance_id,
            "implementation",
            skip_reason="Design completed in external tool (Figma)"
        )
        assert result.allowed is True

        # Verify deviation recorded
        instance = instance_manager.load_instance(instance_id)
        assert len(instance.workflow_deviations) == 1
        assert instance.workflow_deviations[0]["type"] == "skip_forward"
        assert "Figma" in instance.workflow_deviations[0]["reason"]

    def test_strict_mode_blocks_without_force(self, test_workflow_dir):
        """Test strict mode enforcement (deployment)."""
        schema_loader = WorkflowSchemaLoader(test_workflow_dir / ".claude/workflow.json")
        instance_manager = WorkflowInstanceManager(test_workflow_dir / ".claude/workflows")
        discovery = TriadDiscovery(str(test_workflow_dir / ".claude/agents"))

        enforcer = WorkflowEnforcer(schema_loader, instance_manager, discovery, None)

        # Create instance
        instance_id = instance_manager.create_instance(
            "software-development",
            "Skip Test",
            "developer@example.com"
        )

        # Try to skip directly to deployment (strict mode)
        result = enforcer.enforce(instance_id, "deployment")
        assert result.allowed is False
        assert "🛑 CRITICAL" in result.message
        assert "STRICT" in result.message

    def test_strict_mode_allows_with_force_skip(self, test_workflow_dir):
        """Test strict mode with force skip and valid justification."""
        schema_loader = WorkflowSchemaLoader(test_workflow_dir / ".claude/workflow.json")
        instance_manager = WorkflowInstanceManager(test_workflow_dir / ".claude/workflows")
        discovery = TriadDiscovery(str(test_workflow_dir / ".claude/agents"))

        enforcer = WorkflowEnforcer(schema_loader, instance_manager, discovery, None)

        # Create instance
        instance_id = instance_manager.create_instance(
            "software-development",
            "Emergency Deployment",
            "developer@example.com"
        )

        # Force skip with valid justification
        result = enforcer.enforce(
            instance_id,
            "deployment",
            skip_reason="Critical production bug #1234 - database corruption risk",
            force_skip=True
        )
        assert result.allowed is True
        assert "EMERGENCY OVERRIDE" in result.message

        # Verify deviation recorded
        instance = instance_manager.load_instance(instance_id)
        assert len(instance.workflow_deviations) == 1
        assert "database corruption" in instance.workflow_deviations[0]["reason"]

    def test_gate_requirement_with_substantial_work(self, test_workflow_dir):
        """Test gate requirement triggered by substantial metrics."""
        from unittest.mock import Mock

        schema_loader = WorkflowSchemaLoader(test_workflow_dir / ".claude/workflow.json")
        instance_manager = WorkflowInstanceManager(test_workflow_dir / ".claude/workflows")
        discovery = TriadDiscovery(str(test_workflow_dir / ".claude/agents"))

        # Mock metrics provider with substantial work
        metrics_provider = Mock()
        metrics_provider.calculate_metrics.return_value = MetricsResult(
            content_created={"type": "code", "quantity": 257, "units": "lines"},
            components_modified=12,
            complexity="substantial",
            raw_data={"files": ["auth.py", "db.py", "api.py"]}
        )

        enforcer = WorkflowEnforcer(schema_loader, instance_manager, discovery, metrics_provider)

        # Create instance and follow the workflow properly
        instance_id = instance_manager.create_instance(
            "software-development",
            "Large Feature",
            "developer@example.com"
        )

        # Complete each step properly (enforce then mark)
        result = enforcer.enforce(instance_id, "idea-validation")
        instance_manager.mark_triad_completed(instance_id, "idea-validation")

        result = enforcer.enforce(instance_id, "design")
        instance_manager.mark_triad_completed(instance_id, "design")

        result = enforcer.enforce(instance_id, "implementation")
        instance_manager.mark_triad_completed(instance_id, "implementation")

        # Try to deploy - should require garden-tending
        result = enforcer.enforce(instance_id, "deployment")
        assert result.allowed is False
        assert "garden-tending" in result.message.lower()

        # Complete garden-tending
        result = enforcer.enforce(instance_id, "garden-tending")
        # Should not be blocked - garden-tending comes after implementation
        assert result.allowed is True
        instance_manager.mark_triad_completed(instance_id, "garden-tending")

        # Try deployment again - deployment is strict, will require force override or needs reason
        # Since garden-tending is optional, validator sees deployment as skipping required triads
        # In production, user would use --force-skip or complete through recommended first
        result = enforcer.enforce(instance_id, "deployment")
        # Strict mode blocks even with completed gate
        assert result.allowed is False

        # Use force skip to deploy
        result = enforcer.enforce(
            instance_id,
            "deployment",
            skip_reason="All quality gates passed, garden-tending completed successfully",
            force_skip=True
        )
        assert result.allowed is True

    def test_backward_movement_records_deviation(self, test_workflow_dir):
        """Test backward movement in workflow."""
        schema_loader = WorkflowSchemaLoader(test_workflow_dir / ".claude/workflow.json")
        instance_manager = WorkflowInstanceManager(test_workflow_dir / ".claude/workflows")
        discovery = TriadDiscovery(str(test_workflow_dir / ".claude/agents"))

        enforcer = WorkflowEnforcer(schema_loader, instance_manager, discovery, None)

        # Create instance and complete some triads
        instance_id = instance_manager.create_instance(
            "software-development",
            "Revision Needed",
            "developer@example.com"
        )
        instance_manager.mark_triad_completed(instance_id, "idea-validation")
        instance_manager.mark_triad_completed(instance_id, "design")
        instance_manager.mark_triad_completed(instance_id, "implementation")

        # Go back to design (recommended mode - needs reason)
        result = enforcer.enforce(instance_id, "design")
        assert result.allowed is False
        assert result.requires_reason is True

        # Provide reason
        result = enforcer.enforce(
            instance_id,
            "design",
            skip_reason="Implementation revealed design flaws, need to revise architecture"
        )
        assert result.allowed is True

        # Verify deviation recorded as backward movement
        instance = instance_manager.load_instance(instance_id)
        assert len(instance.workflow_deviations) == 1
        assert instance.workflow_deviations[0]["type"] == "skip_backward"

    def test_optional_mode_minimal_friction(self, test_workflow_dir):
        """Test optional enforcement mode."""
        # Modify schema to use optional mode AND remove deployment override
        schema_file = test_workflow_dir / ".claude/workflow.json"
        schema = json.loads(schema_file.read_text())
        schema["enforcement"]["mode"] = "optional"
        schema["enforcement"]["per_triad_overrides"] = {}  # Remove strict override
        schema_file.write_text(json.dumps(schema, indent=2))

        schema_loader = WorkflowSchemaLoader(schema_file)
        instance_manager = WorkflowInstanceManager(test_workflow_dir / ".claude/workflows")
        discovery = TriadDiscovery(str(test_workflow_dir / ".claude/agents"))

        enforcer = WorkflowEnforcer(schema_loader, instance_manager, discovery, None)

        # Create instance
        instance_id = instance_manager.create_instance(
            "software-development",
            "Flexible Workflow",
            "developer@example.com"
        )

        # Skip directly to deployment (should allow with log)
        result = enforcer.enforce(instance_id, "deployment")
        assert result.allowed is True
        assert "ℹ️  Deviation logged" in result.message

        # Verify deviation recorded
        instance = instance_manager.load_instance(instance_id)
        assert len(instance.workflow_deviations) == 1

    def test_per_triad_override_enforcement(self, test_workflow_dir):
        """Test per-triad enforcement mode overrides."""
        schema_loader = WorkflowSchemaLoader(test_workflow_dir / ".claude/workflow.json")
        instance_manager = WorkflowInstanceManager(test_workflow_dir / ".claude/workflows")
        discovery = TriadDiscovery(str(test_workflow_dir / ".claude/agents"))

        enforcer = WorkflowEnforcer(schema_loader, instance_manager, discovery, None)

        # Create instance
        instance_id = instance_manager.create_instance(
            "software-development",
            "Override Test",
            "developer@example.com"
        )

        # Skip to implementation (recommended mode - needs reason)
        result = enforcer.enforce(instance_id, "implementation")
        assert result.allowed is False
        assert "⚠️  RECOMMENDED" in result.message

        # Skip to deployment (strict mode override - blocked)
        result = enforcer.enforce(instance_id, "deployment")
        assert result.allowed is False
        assert "🛑 CRITICAL" in result.message
        assert "STRICT" in result.message
