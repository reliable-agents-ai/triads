"""
Tests for Supervisor core functionality.

Phase 1: Basic structure and hook integration
"""

import pytest
from pathlib import Path

from triads.supervisor.core import (
    load_supervisor_prompt,
    build_supervisor_context,
    invoke_supervisor,
    classify_problem_type,
    suggest_workflow,
    execute_workflow,
    record_routing_outcome,
)


class TestSupervisorCore:
    """Test Supervisor core functions (Phase 1)."""

    def test_load_supervisor_prompt(self):
        """Test loading supervisor agent definition."""
        # Should load the supervisor.md file
        prompt = load_supervisor_prompt()

        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "Supervisor Agent" in prompt
        assert "Triage" in prompt
        assert "ADR-007" in prompt or "Supervisor-First" in prompt

    def test_build_supervisor_context_empty(self):
        """Test building context with no inputs."""
        context = build_supervisor_context()

        assert isinstance(context, str)
        assert "Workflow Library" in context or "workflows" in context.lower()

    def test_build_supervisor_context_with_workflows(self):
        """Test building context with workflow list."""
        workflows = [
            {"name": "Bug Fix", "description": "Fix bugs systematically"},
            {"name": "Feature Dev", "description": "Develop new features"},
        ]

        context = build_supervisor_context(workflows=workflows)

        assert isinstance(context, str)
        assert "Bug Fix" in context
        assert "Feature Dev" in context

    def test_invoke_supervisor_not_implemented(self):
        """Test that direct invocation raises NotImplementedError in Phase 1."""
        with pytest.raises(NotImplementedError, match="Phase 1"):
            invoke_supervisor("test message")

    def test_classify_problem_type_not_implemented(self):
        """Test that classification raises NotImplementedError in Phase 1."""
        with pytest.raises(NotImplementedError, match="Phase 3"):
            classify_problem_type("There's a bug in the router")

    def test_suggest_workflow_not_implemented(self):
        """Test that workflow suggestion raises NotImplementedError in Phase 1."""
        with pytest.raises(NotImplementedError, match="Phase 2"):
            suggest_workflow("bug")

    def test_execute_workflow_not_implemented(self):
        """Test that workflow execution raises NotImplementedError in Phase 1."""
        workflow = {"name": "Bug Fix", "triads": []}
        with pytest.raises(NotImplementedError, match="Phase 4"):
            execute_workflow(workflow, "test problem")

    def test_record_routing_outcome_not_implemented(self):
        """Test that outcome recording raises NotImplementedError in Phase 1."""
        with pytest.raises(NotImplementedError, match="Phase 5"):
            record_routing_outcome(
                message="test",
                classification={"type": "bug"},
                workflow_used="bug-fix",
                user_accepted=True
            )
