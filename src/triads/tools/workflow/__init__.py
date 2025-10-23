"""Workflow tools for MCP integration.

Provides tools for:
- list_workflows: List all workflow instances
- get_workflow: Get workflow instance details
"""

from .domain import WorkflowInstance, WorkflowStatus, TriadCompletion

__all__ = [
    "WorkflowInstance",
    "WorkflowStatus",
    "TriadCompletion",
]
