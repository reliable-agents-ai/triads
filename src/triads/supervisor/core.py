"""
Supervisor core invocation logic.

This module provides the core functionality for invoking the Supervisor agent
and managing workflow routing.

Phase 1: Basic structure and invocation pattern
Future phases: Classification, execution monitoring, learning
"""

from pathlib import Path
from typing import Optional, Dict, Any


def invoke_supervisor(message: str, context: Optional[Dict[str, Any]] = None) -> str:
    """
    Invoke Supervisor Agent with user message.

    Note: In Phase 1, the Supervisor is primarily implemented via the
    UserPromptSubmit hook which injects instructions. This function provides
    a programmatic interface for future phases and testing.

    Args:
        message: User's message
        context: Session context (optional)

    Returns:
        str: Supervisor's response

    Raises:
        NotImplementedError: Direct invocation not yet implemented in Phase 1
    """
    raise NotImplementedError(
        "Direct Supervisor invocation not yet implemented in Phase 1. "
        "Supervisor logic is injected via UserPromptSubmit hook. "
        "This function will be implemented in Phase 3 for programmatic routing."
    )


def load_supervisor_prompt() -> str:
    """
    Load Supervisor agent definition from .claude/agents/supervisor/supervisor.md

    Returns:
        str: Supervisor agent prompt

    Raises:
        FileNotFoundError: If supervisor.md doesn't exist
    """
    supervisor_md = Path(".claude/agents/supervisor/supervisor.md")

    if not supervisor_md.exists():
        raise FileNotFoundError(
            f"Supervisor agent definition not found at {supervisor_md}. "
            "Ensure .claude/agents/supervisor/supervisor.md exists."
        )

    return supervisor_md.read_text()


def build_supervisor_context(
    context: Optional[Dict[str, Any]] = None,
    workflows: Optional[list] = None
) -> str:
    """
    Build full context for Supervisor agent.

    Combines:
    - Session context (knowledge graphs, current state)
    - Workflow library
    - Classification guidelines

    Args:
        context: Session context dictionary
        workflows: List of available workflows

    Returns:
        str: Formatted context for Supervisor

    Note: Phase 1 implementation - basic structure only
    """
    context = context or {}
    workflows = workflows or []

    output = []

    # Session context
    if context:
        output.append("## Session Context\n")
        # TODO: Format session context (Phase 2)
        output.append("(Session context formatting not yet implemented)")
        output.append("")

    # Workflow library
    if workflows:
        output.append("## Available Workflows\n")
        for workflow in workflows:
            output.append(f"- {workflow.get('name', 'Unknown')}: {workflow.get('description', '')}")
        output.append("")
    else:
        output.append("## Workflow Library\n")
        output.append("(Workflow library not yet created - will be implemented in Phase 2)")
        output.append("")

    return "\n".join(output)


def classify_problem_type(message: str) -> Dict[str, Any]:
    """
    Classify user message into problem type.

    Args:
        message: User's message

    Returns:
        dict: Classification result with:
            - problem_type: str (bug, feature, performance, etc.)
            - confidence: float (0.0-1.0)
            - indicators: list of str (keywords that triggered classification)
            - suggested_workflow: str (workflow name)

    Note: Phase 1 - Placeholder for Phase 3 implementation
    """
    raise NotImplementedError(
        "Automated problem classification not yet implemented. "
        "Will be added in Phase 3 with semantic routing and LLM fallback."
    )


def suggest_workflow(problem_type: str) -> Optional[Dict[str, Any]]:
    """
    Suggest appropriate workflow for problem type.

    Args:
        problem_type: Classified problem type

    Returns:
        dict: Workflow definition or None if not found

    Note: Phase 1 - Placeholder for Phase 2 implementation
    """
    raise NotImplementedError(
        "Workflow suggestion not yet implemented. "
        "Will be added in Phase 2 with workflow library."
    )


def execute_workflow(workflow: Dict[str, Any], problem: str) -> Dict[str, Any]:
    """
    Execute workflow for given problem.

    Args:
        workflow: Workflow definition
        problem: Problem description

    Returns:
        dict: Workflow execution results

    Note: Phase 1 - Placeholder for Phase 4 implementation
    """
    raise NotImplementedError(
        "Workflow execution not yet implemented. "
        "Will be added in Phase 4 with execution monitoring."
    )


def record_routing_outcome(
    message: str,
    classification: Dict[str, Any],
    workflow_used: str,
    user_accepted: bool,
    outcome: Optional[str] = None,
    feedback: Optional[str] = None
) -> None:
    """
    Record routing outcome for learning.

    Args:
        message: Original user message
        classification: Classification result
        workflow_used: Workflow that was used
        user_accepted: Whether user accepted the routing
        outcome: Workflow outcome (success/failure)
        feedback: User feedback (optional)

    Note: Phase 1 - Placeholder for Phase 5 implementation
    """
    raise NotImplementedError(
        "Routing outcome recording not yet implemented. "
        "Will be added in Phase 5 with learning system."
    )


# Phase 1 exports - mostly placeholders for future phases
__all__ = [
    "invoke_supervisor",
    "load_supervisor_prompt",
    "build_supervisor_context",
    "classify_problem_type",
    "suggest_workflow",
    "execute_workflow",
    "record_routing_outcome",
]
