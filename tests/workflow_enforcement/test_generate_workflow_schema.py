"""Tests for workflow schema generator script.

Tests cover:
- Triad discovery from .claude/agents/
- Type inference from triad names
- Schema generation
- File output
"""

import json
import pytest
from pathlib import Path

# Import functions from script
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from generate_workflow_schema import (
    infer_triad_type,
    generate_triad_name,
    generate_workflow_schema,
    save_schema,
)


class TestInferTriadType:
    """Tests for triad type inference."""

    def test_infer_research_types(self):
        """Test research keyword detection."""
        research_ids = [
            "idea-validation",
            "research",
            "discovery",
            "analysis",
            "investigate-problem",
            "rfp-analysis",
            "requirements-study"
        ]

        for triad_id in research_ids:
            assert infer_triad_type(triad_id) == "research", f"Failed for {triad_id}"

    def test_infer_planning_types(self):
        """Test planning keyword detection."""
        planning_ids = [
            "design",
            "architecture",
            "plan",
            "strategy",
            "rfp-strategy",
            "roadmap",
            "blueprint"
        ]

        for triad_id in planning_ids:
            assert infer_triad_type(triad_id) == "planning", f"Failed for {triad_id}"

    def test_infer_execution_types(self):
        """Test execution keyword detection."""
        execution_ids = [
            "implementation",
            "build",
            "create",
            "develop",
            "write-code",
            "coding",
            "rfp-creation"
        ]

        for triad_id in execution_ids:
            assert infer_triad_type(triad_id) == "execution", f"Failed for {triad_id}"

    def test_infer_quality_types(self):
        """Test quality keyword detection."""
        quality_ids = [
            "garden-tending",
            "test",
            "review",
            "quality-check",
            "refactor",
            "cleanup",
            "polish",
            "qa-validation"
        ]

        for triad_id in quality_ids:
            assert infer_triad_type(triad_id) == "quality", f"Failed for {triad_id}"

    def test_infer_release_types(self):
        """Test release keyword detection."""
        release_ids = [
            "deployment",
            "release",
            "publish",
            "ship",
            "delivery",
            "launch",
            "submission",
            "finalize"
        ]

        for triad_id in release_ids:
            assert infer_triad_type(triad_id) == "release", f"Failed for {triad_id}"

    def test_infer_default_type(self):
        """Test default type for unknown keywords."""
        unknown_ids = [
            "unknown-triad",
            "custom-step",
            "random-name"
        ]

        for triad_id in unknown_ids:
            assert infer_triad_type(triad_id) == "execution", f"Failed for {triad_id}"

    def test_case_insensitive(self):
        """Test that inference is case-insensitive."""
        assert infer_triad_type("DESIGN") == "planning"
        assert infer_triad_type("Design") == "planning"
        assert infer_triad_type("design") == "planning"


class TestGenerateTriadName:
    """Tests for triad name generation."""

    def test_basic_name_generation(self):
        """Test basic hyphen-to-space conversion."""
        assert generate_triad_name("idea-validation") == "Idea Validation"
        assert generate_triad_name("garden-tending") == "Garden Tending"
        assert generate_triad_name("design") == "Design"

    def test_underscore_conversion(self):
        """Test underscore conversion."""
        assert generate_triad_name("my_custom_triad") == "My Custom Triad"

    def test_acronym_capitalization(self):
        """Test that acronyms are properly capitalized."""
        assert generate_triad_name("rfp-analysis") == "RFP Analysis"
        assert generate_triad_name("api-design") == "API Design"
        assert generate_triad_name("oauth-implementation") == "OAUTH Implementation"

    def test_mixed_separators(self):
        """Test handling of mixed separators."""
        assert generate_triad_name("api_design-review") == "API Design Review"


class TestGenerateWorkflowSchema:
    """Tests for workflow schema generation."""

    @pytest.fixture
    def test_agents_dir(self, tmp_path):
        """Create temporary agents directory with test triads."""
        agents_dir = tmp_path / ".claude" / "agents"
        agents_dir.mkdir(parents=True)

        # Create test triads
        triads = {
            "idea-validation": ["research-analyst.md", "validation-synthesizer.md"],
            "design": ["solution-architect.md", "design-bridge.md"],
            "implementation": ["senior-developer.md", "test-engineer.md"],
            "garden-tending": ["cultivator.md", "pruner.md"],
            "deployment": ["release-manager.md", "documentation-updater.md"]
        }

        for triad_id, agent_files in triads.items():
            triad_dir = agents_dir / triad_id
            triad_dir.mkdir()

            for agent_file in agent_files:
                (triad_dir / agent_file).write_text("# Agent placeholder")

        return agents_dir

    def test_generate_basic_schema(self, test_agents_dir):
        """Test generating basic workflow schema."""
        schema = generate_workflow_schema(
            output_path=None,
            workflow_name="test-workflow",
            agents_dir=test_agents_dir
        )

        # Check structure
        assert "workflow_name" in schema
        assert "version" in schema
        assert "enforcement" in schema
        assert "triads" in schema
        assert "workflow_rules" in schema

        # Check values
        assert schema["workflow_name"] == "test-workflow"
        assert schema["version"] == "1.0.0"
        assert schema["enforcement"]["mode"] == "recommended"
        assert len(schema["triads"]) == 5

    def test_triads_are_sorted(self, test_agents_dir):
        """Test that triads are sorted alphabetically."""
        schema = generate_workflow_schema(
            output_path=None,
            workflow_name="test",
            agents_dir=test_agents_dir
        )

        triad_ids = [t["id"] for t in schema["triads"]]
        assert triad_ids == sorted(triad_ids)

    def test_triad_structure(self, test_agents_dir):
        """Test that each triad has correct structure."""
        schema = generate_workflow_schema(
            output_path=None,
            workflow_name="test",
            agents_dir=test_agents_dir
        )

        for triad in schema["triads"]:
            assert "id" in triad
            assert "name" in triad
            assert "type" in triad
            assert "required" in triad

            # Check types
            assert isinstance(triad["id"], str)
            assert isinstance(triad["name"], str)
            assert isinstance(triad["type"], str)
            assert isinstance(triad["required"], bool)

            # Check type is valid
            assert triad["type"] in ["research", "planning", "execution", "quality", "release"]

    def test_triad_type_inference(self, test_agents_dir):
        """Test that triad types are correctly inferred."""
        schema = generate_workflow_schema(
            output_path=None,
            workflow_name="test",
            agents_dir=test_agents_dir
        )

        triad_types = {t["id"]: t["type"] for t in schema["triads"]}

        assert triad_types["idea-validation"] == "research"
        assert triad_types["design"] == "planning"
        assert triad_types["implementation"] == "execution"
        assert triad_types["garden-tending"] == "quality"
        assert triad_types["deployment"] == "release"

    def test_workflow_rules(self, test_agents_dir):
        """Test that workflow rules are included."""
        schema = generate_workflow_schema(
            output_path=None,
            workflow_name="test",
            agents_dir=test_agents_dir
        )

        assert len(schema["workflow_rules"]) > 0

        # Check sequential progression rule
        sequential_rule = schema["workflow_rules"][0]
        assert sequential_rule["rule_type"] == "sequential_progression"
        assert sequential_rule["track_deviations"] is True

    def test_default_workflow_name(self, test_agents_dir):
        """Test default workflow name inference."""
        schema = generate_workflow_schema(
            output_path=None,
            workflow_name=None,
            agents_dir=test_agents_dir
        )

        # Should use current directory name
        assert schema["workflow_name"] is not None
        assert len(schema["workflow_name"]) > 0

    def test_empty_agents_dir(self, tmp_path):
        """Test handling of empty agents directory."""
        empty_agents_dir = tmp_path / "empty_agents"
        empty_agents_dir.mkdir()

        with pytest.raises(SystemExit) as exc_info:
            generate_workflow_schema(
                output_path=None,
                workflow_name="test",
                agents_dir=empty_agents_dir
            )

        assert exc_info.value.code == 1


class TestConstants:
    """Tests for module constants."""

    def test_constants_defined(self):
        """Test that path constants are properly defined."""
        from scripts.generate_workflow_schema import (
            DEFAULT_WORKFLOW_SCHEMA_PATH,
            DEFAULT_AGENTS_DIR,
            DEFAULT_WORKFLOWS_DIR
        )

        # Verify constants are Path objects
        assert isinstance(DEFAULT_WORKFLOW_SCHEMA_PATH, Path)
        assert isinstance(DEFAULT_AGENTS_DIR, Path)
        assert isinstance(DEFAULT_WORKFLOWS_DIR, Path)

        # Verify expected paths
        assert str(DEFAULT_WORKFLOW_SCHEMA_PATH) == ".claude/workflow.json"
        assert str(DEFAULT_AGENTS_DIR) == ".claude/agents"
        assert str(DEFAULT_WORKFLOWS_DIR) == ".claude/workflows"


class TestSaveSchema:
    """Tests for schema file saving."""

    def test_save_creates_file(self, tmp_path):
        """Test that save creates the file."""
        output_path = tmp_path / "workflow.json"

        schema = {
            "workflow_name": "test",
            "version": "1.0.0",
            "triads": []
        }

        save_schema(schema, output_path)

        assert output_path.exists()
        assert output_path.is_file()

    def test_save_creates_parent_directories(self, tmp_path):
        """Test that save creates parent directories if needed."""
        output_path = tmp_path / "nested" / "path" / "workflow.json"

        schema = {"workflow_name": "test"}

        save_schema(schema, output_path)

        assert output_path.exists()
        assert output_path.parent.exists()

    def test_save_valid_json(self, tmp_path):
        """Test that saved file contains valid JSON."""
        output_path = tmp_path / "workflow.json"

        schema = {
            "workflow_name": "test",
            "version": "1.0.0",
            "triads": [
                {"id": "test-triad", "name": "Test Triad", "type": "execution", "required": True}
            ]
        }

        save_schema(schema, output_path)

        # Load and verify
        with open(output_path) as f:
            loaded = json.load(f)

        assert loaded == schema

    def test_save_formatting(self, tmp_path):
        """Test that saved file has proper formatting."""
        output_path = tmp_path / "workflow.json"

        schema = {"workflow_name": "test", "triads": []}

        save_schema(schema, output_path)

        content = output_path.read_text()

        # Should have indentation
        assert "  " in content
        # Should have trailing newline
        assert content.endswith("\n")


class TestIntegration:
    """Integration tests for full workflow."""

    def test_full_generation_workflow(self, tmp_path):
        """Test complete workflow from triads to file."""
        # Create agents directory
        agents_dir = tmp_path / ".claude" / "agents"
        agents_dir.mkdir(parents=True)

        # Create triads
        for triad_id in ["research", "design", "implementation"]:
            triad_dir = agents_dir / triad_id
            triad_dir.mkdir()
            (triad_dir / "agent.md").write_text("# Agent")

        # Generate schema
        output_path = tmp_path / "workflow.json"

        schema = generate_workflow_schema(
            output_path=output_path,
            workflow_name="test-workflow",
            agents_dir=agents_dir
        )

        # Save schema
        save_schema(schema, output_path)

        # Verify file exists and is valid
        assert output_path.exists()

        with open(output_path) as f:
            loaded = json.load(f)

        assert loaded["workflow_name"] == "test-workflow"
        assert len(loaded["triads"]) == 3

    def test_real_project_structure(self, tmp_path):
        """Test with realistic project structure."""
        # Simulate real triads project
        agents_dir = tmp_path / ".claude" / "agents"
        agents_dir.mkdir(parents=True)

        triads_structure = {
            "idea-validation": ["research-analyst.md", "community-researcher.md", "validation-synthesizer.md"],
            "design": ["solution-architect.md", "design-bridge.md"],
            "implementation": ["senior-developer.md", "test-engineer.md"],
            "garden-tending": ["cultivator.md", "pruner.md", "gardener-bridge.md"],
            "deployment": ["release-manager.md", "documentation-updater.md"]
        }

        for triad_id, agents in triads_structure.items():
            triad_dir = agents_dir / triad_id
            triad_dir.mkdir()

            for agent in agents:
                (triad_dir / agent).write_text(f"# {agent}")

        # Generate
        schema = generate_workflow_schema(
            output_path=None,
            workflow_name="software-development",
            agents_dir=agents_dir
        )

        # Verify
        assert schema["workflow_name"] == "software-development"
        assert len(schema["triads"]) == 5

        # Check types
        triad_types = {t["id"]: t["type"] for t in schema["triads"]}
        assert triad_types["idea-validation"] == "research"
        assert triad_types["design"] == "planning"
        assert triad_types["implementation"] == "execution"
        assert triad_types["garden-tending"] == "quality"
        assert triad_types["deployment"] == "release"
