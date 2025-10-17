"""Tests for workflow schema loader.

Tests cover:
- Loading valid workflow.json schemas
- Schema validation and error handling
- Query interface for schema elements
- Missing optional fields handling
"""

import json
import pytest
from pathlib import Path
from triads.workflow_enforcement.schema_loader import (
    WorkflowSchemaLoader,
    WorkflowSchema,
    TriadDefinition,
    WorkflowRule,
    EnforcementConfig,
    SchemaValidationError,
)


@pytest.fixture
def temp_workflow_dir(tmp_path):
    """Create temporary .claude directory for testing."""
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    return claude_dir


@pytest.fixture
def valid_workflow_schema():
    """Valid workflow schema for testing."""
    return {
        "workflow_name": "software-development",
        "version": "1.0.0",
        "enforcement": {
            "mode": "recommended",
            "per_triad_overrides": {
                "legal-review": "strict"
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
            }
        ],
        "workflow_rules": [
            {
                "rule_type": "sequential_progression",
                "track_deviations": True
            },
            {
                "rule_type": "conditional_requirement",
                "gate_triad": "design",
                "before_triad": "implementation",
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


@pytest.fixture
def minimal_workflow_schema():
    """Minimal valid workflow schema (only required fields)."""
    return {
        "workflow_name": "simple-workflow",
        "version": "1.0.0",
        "triads": [
            {
                "id": "step1",
                "name": "Step 1",
                "type": "task",
                "required": True
            }
        ]
    }


class TestWorkflowSchemaLoader:
    """Test WorkflowSchemaLoader class."""

    def test_load_valid_schema(self, temp_workflow_dir, valid_workflow_schema):
        """Test loading a valid workflow schema."""
        # Write schema to file
        schema_file = temp_workflow_dir / "workflow.json"
        schema_file.write_text(json.dumps(valid_workflow_schema, indent=2))

        # Load schema
        loader = WorkflowSchemaLoader(schema_file)
        schema = loader.load_schema()

        # Verify schema loaded correctly
        assert isinstance(schema, WorkflowSchema)
        assert schema.workflow_name == "software-development"
        assert schema.version == "1.0.0"
        assert len(schema.triads) == 3
        assert len(schema.workflow_rules) == 2

    def test_load_minimal_schema(self, temp_workflow_dir, minimal_workflow_schema):
        """Test loading schema with only required fields."""
        schema_file = temp_workflow_dir / "workflow.json"
        schema_file.write_text(json.dumps(minimal_workflow_schema, indent=2))

        loader = WorkflowSchemaLoader(schema_file)
        schema = loader.load_schema()

        assert schema.workflow_name == "simple-workflow"
        assert schema.version == "1.0.0"
        assert len(schema.triads) == 1
        # Optional fields should have defaults
        assert schema.enforcement.mode == "recommended"  # Default mode
        assert schema.workflow_rules == []  # Empty list if not specified

    def test_load_nonexistent_file(self, temp_workflow_dir):
        """Test loading from nonexistent file raises error."""
        schema_file = temp_workflow_dir / "nonexistent.json"
        loader = WorkflowSchemaLoader(schema_file)

        with pytest.raises(SchemaValidationError, match="Schema file not found"):
            loader.load_schema()

    def test_load_invalid_json(self, temp_workflow_dir):
        """Test loading malformed JSON raises error."""
        schema_file = temp_workflow_dir / "workflow.json"
        schema_file.write_text("{ invalid json }")

        loader = WorkflowSchemaLoader(schema_file)

        with pytest.raises(SchemaValidationError, match="Invalid JSON"):
            loader.load_schema()

    def test_missing_required_field_workflow_name(self, temp_workflow_dir):
        """Test missing required field raises error."""
        schema_file = temp_workflow_dir / "workflow.json"
        schema_file.write_text(json.dumps({
            "version": "1.0.0",
            "triads": []
        }))

        loader = WorkflowSchemaLoader(schema_file)

        with pytest.raises(SchemaValidationError, match="Missing required field: workflow_name"):
            loader.load_schema()

    def test_missing_required_field_triads(self, temp_workflow_dir):
        """Test missing triads field raises error."""
        schema_file = temp_workflow_dir / "workflow.json"
        schema_file.write_text(json.dumps({
            "workflow_name": "test",
            "version": "1.0.0"
        }))

        loader = WorkflowSchemaLoader(schema_file)

        with pytest.raises(SchemaValidationError, match="Missing required field: triads"):
            loader.load_schema()

    def test_invalid_enforcement_mode(self, temp_workflow_dir, valid_workflow_schema):
        """Test invalid enforcement mode raises error."""
        valid_workflow_schema["enforcement"]["mode"] = "invalid_mode"
        schema_file = temp_workflow_dir / "workflow.json"
        schema_file.write_text(json.dumps(valid_workflow_schema))

        loader = WorkflowSchemaLoader(schema_file)

        with pytest.raises(SchemaValidationError, match="Invalid enforcement mode"):
            loader.load_schema()

    def test_empty_triads_list(self, temp_workflow_dir):
        """Test empty triads list raises error."""
        schema_file = temp_workflow_dir / "workflow.json"
        schema_file.write_text(json.dumps({
            "workflow_name": "test",
            "version": "1.0.0",
            "triads": []
        }))

        loader = WorkflowSchemaLoader(schema_file)

        with pytest.raises(SchemaValidationError, match="Triads list cannot be empty"):
            loader.load_schema()

    def test_invalid_triad_missing_id(self, temp_workflow_dir):
        """Test triad missing required id field raises error."""
        schema_file = temp_workflow_dir / "workflow.json"
        schema_file.write_text(json.dumps({
            "workflow_name": "test",
            "version": "1.0.0",
            "triads": [
                {
                    "name": "Test Triad",
                    "type": "task",
                    "required": True
                }
            ]
        }))

        loader = WorkflowSchemaLoader(schema_file)

        with pytest.raises(SchemaValidationError, match="Triad missing required field: id"):
            loader.load_schema()


class TestWorkflowSchemaQueries:
    """Test query interface for workflow schema."""

    def test_get_triad_by_id(self, temp_workflow_dir, valid_workflow_schema):
        """Test retrieving triad by ID."""
        schema_file = temp_workflow_dir / "workflow.json"
        schema_file.write_text(json.dumps(valid_workflow_schema))

        loader = WorkflowSchemaLoader(schema_file)
        schema = loader.load_schema()

        # Get existing triad
        triad = schema.get_triad("design")
        assert triad is not None
        assert triad.id == "design"
        assert triad.name == "Design"
        assert triad.type == "architecture"

        # Get nonexistent triad
        triad = schema.get_triad("nonexistent")
        assert triad is None

    def test_get_triads_by_type(self, temp_workflow_dir, valid_workflow_schema):
        """Test filtering triads by type."""
        schema_file = temp_workflow_dir / "workflow.json"
        schema_file.write_text(json.dumps(valid_workflow_schema))

        loader = WorkflowSchemaLoader(schema_file)
        schema = loader.load_schema()

        # Get research triads
        research_triads = schema.get_triads_by_type("research")
        assert len(research_triads) == 1
        assert research_triads[0].id == "idea-validation"

        # Get nonexistent type
        none_triads = schema.get_triads_by_type("nonexistent")
        assert len(none_triads) == 0

    def test_get_required_triads(self, temp_workflow_dir):
        """Test filtering required triads."""
        schema_data = {
            "workflow_name": "test",
            "version": "1.0.0",
            "triads": [
                {"id": "required1", "name": "Required 1", "type": "task", "required": True},
                {"id": "optional1", "name": "Optional 1", "type": "task", "required": False},
                {"id": "required2", "name": "Required 2", "type": "task", "required": True}
            ]
        }
        schema_file = temp_workflow_dir / "workflow.json"
        schema_file.write_text(json.dumps(schema_data))

        loader = WorkflowSchemaLoader(schema_file)
        schema = loader.load_schema()

        required = schema.get_required_triads()
        assert len(required) == 2
        assert all(t.required for t in required)

    def test_get_enforcement_mode_default(self, temp_workflow_dir, valid_workflow_schema):
        """Test getting enforcement mode with default."""
        schema_file = temp_workflow_dir / "workflow.json"
        schema_file.write_text(json.dumps(valid_workflow_schema))

        loader = WorkflowSchemaLoader(schema_file)
        schema = loader.load_schema()

        # Default mode
        assert schema.get_enforcement_mode("idea-validation") == "recommended"

        # Override mode
        assert schema.get_enforcement_mode("legal-review") == "strict"

    def test_triad_order(self, temp_workflow_dir, valid_workflow_schema):
        """Test triads maintain order from schema."""
        schema_file = temp_workflow_dir / "workflow.json"
        schema_file.write_text(json.dumps(valid_workflow_schema))

        loader = WorkflowSchemaLoader(schema_file)
        schema = loader.load_schema()

        triad_ids = [t.id for t in schema.triads]
        assert triad_ids == ["idea-validation", "design", "implementation"]


class TestEnforcementConfig:
    """Test enforcement configuration handling."""

    def test_default_enforcement_config(self, temp_workflow_dir):
        """Test default enforcement config when not specified."""
        schema_file = temp_workflow_dir / "workflow.json"
        schema_file.write_text(json.dumps({
            "workflow_name": "test",
            "version": "1.0.0",
            "triads": [{"id": "t1", "name": "T1", "type": "task", "required": True}]
        }))

        loader = WorkflowSchemaLoader(schema_file)
        schema = loader.load_schema()

        assert schema.enforcement.mode == "recommended"
        assert schema.enforcement.per_triad_overrides == {}

    def test_per_triad_overrides(self, temp_workflow_dir):
        """Test per-triad enforcement mode overrides."""
        schema_file = temp_workflow_dir / "workflow.json"
        schema_file.write_text(json.dumps({
            "workflow_name": "test",
            "version": "1.0.0",
            "enforcement": {
                "mode": "optional",
                "per_triad_overrides": {
                    "critical": "strict",
                    "important": "recommended"
                }
            },
            "triads": [
                {"id": "critical", "name": "Critical", "type": "task", "required": True},
                {"id": "important", "name": "Important", "type": "task", "required": True},
                {"id": "normal", "name": "Normal", "type": "task", "required": False}
            ]
        }))

        loader = WorkflowSchemaLoader(schema_file)
        schema = loader.load_schema()

        assert schema.get_enforcement_mode("critical") == "strict"
        assert schema.get_enforcement_mode("important") == "recommended"
        assert schema.get_enforcement_mode("normal") == "optional"


class TestWorkflowRules:
    """Test workflow rule parsing."""

    def test_sequential_progression_rule(self, temp_workflow_dir):
        """Test parsing sequential progression rule."""
        schema_file = temp_workflow_dir / "workflow.json"
        schema_file.write_text(json.dumps({
            "workflow_name": "test",
            "version": "1.0.0",
            "triads": [{"id": "t1", "name": "T1", "type": "task", "required": True}],
            "workflow_rules": [
                {
                    "rule_type": "sequential_progression",
                    "track_deviations": True
                }
            ]
        }))

        loader = WorkflowSchemaLoader(schema_file)
        schema = loader.load_schema()

        assert len(schema.workflow_rules) == 1
        rule = schema.workflow_rules[0]
        assert rule.rule_type == "sequential_progression"
        assert rule.track_deviations is True

    def test_conditional_requirement_rule(self, temp_workflow_dir, valid_workflow_schema):
        """Test parsing conditional requirement rule."""
        schema_file = temp_workflow_dir / "workflow.json"
        schema_file.write_text(json.dumps(valid_workflow_schema))

        loader = WorkflowSchemaLoader(schema_file)
        schema = loader.load_schema()

        cond_rules = [r for r in schema.workflow_rules if r.rule_type == "conditional_requirement"]
        assert len(cond_rules) == 1

        rule = cond_rules[0]
        assert rule.gate_triad == "design"
        assert rule.before_triad == "implementation"
        assert rule.bypass_allowed is True
        assert rule.condition["type"] == "significance_threshold"
