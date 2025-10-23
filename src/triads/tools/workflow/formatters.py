"""Formatters for workflow tool output.

Converts domain models to human-readable text formats for MCP tools.
"""

from typing import List

from triads.tools.workflow.domain import WorkflowInstance


def format_workflow_list(instances: List[WorkflowInstance]) -> str:
    """Format workflow instance list as human-readable text.

    Args:
        instances: List of WorkflowInstance objects to format

    Returns:
        Formatted string with workflow list

    Example:
        >>> instances = [WorkflowInstance(...), WorkflowInstance(...)]
        >>> print(format_workflow_list(instances))
        Found 2 workflow instance(s):

        feature-oauth2-20251023-100523
          Title: OAuth2 Integration
          Status: in_progress
          Started: 2025-10-23T08:30:00Z
          Current: implementation
    """
    if not instances:
        return "No workflow instances found."

    lines = [f"Found {len(instances)} workflow instance(s):\n"]

    for inst in instances:
        lines.append(f"{inst.instance_id}")
        lines.append(f"  Title: {inst.title}")
        lines.append(f"  Status: {inst.status.value}")
        if inst.started_at:
            lines.append(f"  Started: {inst.started_at}")
        current = inst.current_triad or "Not started"
        lines.append(f"  Current: {current}")
        lines.append("")

    return "\n".join(lines)


def format_workflow_details(instance: WorkflowInstance) -> str:
    """Format workflow instance details as human-readable text.

    Args:
        instance: WorkflowInstance to format

    Returns:
        Formatted string with detailed workflow information

    Example:
        >>> instance = WorkflowInstance(...)
        >>> print(format_workflow_details(instance))
        Workflow Instance: feature-oauth2-20251023-100523

        Title: OAuth2 Integration
        Type: software-development
        Status: in_progress
        Started at: 2025-10-23T08:30:00Z

        Progress:
          Current triad: implementation
          Completed: 2 triad(s)
    """
    lines = [
        f"Workflow Instance: {instance.instance_id}\n",
        f"Title: {instance.title}",
        f"Type: {instance.workflow_type}",
        f"Status: {instance.status.value}",
    ]

    if instance.started_at:
        lines.append(f"Started at: {instance.started_at}")

    lines.append("\nProgress:")
    current = instance.current_triad or "Not started"
    lines.append(f"  Current triad: {current}")
    lines.append(f"  Completed: {len(instance.completed_triads)} triad(s)")

    # Completed triads details
    if instance.completed_triads:
        lines.append("\nCompleted Triads:")
        for completion in instance.completed_triads:
            lines.append(
                f"  ✓ {completion.triad_id} ({completion.duration_minutes:.1f} minutes)"
            )

    return "\n".join(lines)
