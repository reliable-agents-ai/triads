"""Tests for generator tools domain models."""

import pytest
from dataclasses import asdict

from triads.tools.generator.domain import AgentDefinition, WorkflowTemplate


class TestAgentDefinition:
    """Tests for AgentDefinition dataclass."""

    def test_agent_definition_creation(self):
        """AgentDefinition can be created with required fields."""
        agent = AgentDefinition(
            name="investigator",
            role="Lead investigator who analyzes issues",
            tools=["Read", "Grep", "Bash"],
            content="---\nname: investigator\n...",
            triad_id="debugging"
        )

        assert agent.name == "investigator"
        assert agent.role == "Lead investigator who analyzes issues"
        assert agent.tools == ["Read", "Grep", "Bash"]
        assert "name: investigator" in agent.content
        assert agent.triad_id == "debugging"

    def test_agent_definition_defaults_tools_to_empty_list(self):
        """AgentDefinition defaults tools to empty list."""
        agent = AgentDefinition(
            name="coordinator",
            role="Coordinator",
            content="---\nname: coordinator\n...",
            triad_id="coordination"
        )

        assert agent.tools == []

    def test_agent_definition_to_dict(self):
        """AgentDefinition can be converted to dictionary."""
        agent = AgentDefinition(
            name="fixer",
            role="Fixes bugs",
            tools=["Edit", "Bash"],
            content="agent content",
            triad_id="debugging"
        )

        data = asdict(agent)
        assert data["name"] == "fixer"
        assert data["role"] == "Fixes bugs"
        assert data["tools"] == ["Edit", "Bash"]
        assert data["triad_id"] == "debugging"


class TestWorkflowTemplate:
    """Tests for WorkflowTemplate dataclass."""

    def test_workflow_template_creation(self):
        """WorkflowTemplate can be created with required fields."""
        template = WorkflowTemplate(
            workflow_type="debugging",
            domain="Software Debugging",
            triads=["debugging", "verification"]
        )

        assert template.workflow_type == "debugging"
        assert template.domain == "Software Debugging"
        assert template.triads == ["debugging", "verification"]

    def test_workflow_template_with_description(self):
        """WorkflowTemplate supports optional description."""
        template = WorkflowTemplate(
            workflow_type="debugging",
            domain="Software Debugging",
            triads=["debugging"],
            description="Systematic debugging workflow"
        )

        assert template.description == "Systematic debugging workflow"

    def test_workflow_template_defaults_description_to_none(self):
        """WorkflowTemplate defaults description to None."""
        template = WorkflowTemplate(
            workflow_type="debugging",
            domain="Software",
            triads=["debugging"]
        )

        assert template.description is None

    def test_workflow_template_to_dict(self):
        """WorkflowTemplate can be converted to dictionary."""
        template = WorkflowTemplate(
            workflow_type="debugging",
            domain="Software",
            triads=["debugging", "verification"]
        )

        data = asdict(template)
        assert data["workflow_type"] == "debugging"
        assert data["domain"] == "Software"
        assert data["triads"] == ["debugging", "verification"]
