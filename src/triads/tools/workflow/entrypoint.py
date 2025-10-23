"""MCP tool entrypoints for workflow tools.

Provides 2 MCP-compliant tools for workflow instance management.
"""

from typing import Optional

from triads.tools.shared import ToolResult
from triads.tools.workflow.bootstrap import bootstrap_workflow_service
from triads.tools.workflow.formatters import format_workflow_list, format_workflow_details


class WorkflowTools:
    """MCP tool entrypoints for workflow operations.

    All methods return ToolResult in MCP-compliant format.
    """

    @staticmethod
    def list_workflows(status: Optional[str] = None) -> ToolResult:
        """List all workflow instances with optional status filter.

        MCP Tool: list_workflows

        Lists all workflow instances in the project, optionally filtered
        by status (in_progress, completed, abandoned).

        Args:
            status: Optional status filter

        Returns:
            ToolResult with formatted workflow list

        Example:
            >>> result = WorkflowTools.list_workflows()
            >>> print(result.content[0]["text"])
            Found 3 workflow instance(s):

            feature-oauth2-20251023-100523
              Title: OAuth2 Integration
              Status: in_progress
              ...

            >>> result = WorkflowTools.list_workflows(status="completed")
        """
        service = bootstrap_workflow_service()

        try:
            instances = service.list_workflows(status)
            formatted = format_workflow_list(instances)

            return ToolResult(
                success=True, content=[{"type": "text", "text": formatted}]
            )

        except Exception as e:
            return ToolResult(success=False, content=[], error=str(e))

    @staticmethod
    def get_workflow(instance_id: str) -> ToolResult:
        """Get detailed information about a workflow instance.

        MCP Tool: get_workflow

        Retrieves full details about a specific workflow instance including
        progress, completed triads, and metadata.

        Args:
            instance_id: Instance identifier

        Returns:
            ToolResult with formatted workflow details

        Example:
            >>> result = WorkflowTools.get_workflow("feature-oauth2-20251023-100523")
            >>> print(result.content[0]["text"])
            Workflow Instance: feature-oauth2-20251023-100523

            Title: OAuth2 Integration
            Type: software-development
            Status: in_progress
            ...
        """
        service = bootstrap_workflow_service()

        try:
            instance = service.get_workflow(instance_id)
            formatted = format_workflow_details(instance)

            return ToolResult(
                success=True, content=[{"type": "text", "text": formatted}]
            )

        except Exception as e:
            return ToolResult(success=False, content=[], error=str(e))
