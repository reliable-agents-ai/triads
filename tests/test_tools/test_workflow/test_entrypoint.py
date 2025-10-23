"""Tests for workflow tools MCP entrypoints."""

import pytest
from unittest.mock import Mock, patch

from triads.tools.workflow.entrypoint import WorkflowTools
from triads.tools.shared import ToolResult


@pytest.fixture(autouse=True)
def use_in_memory_repository():
    """Force all tests to use InMemoryWorkflowRepository."""
    with patch("triads.tools.workflow.entrypoint.bootstrap_workflow_service") as mock:
        from triads.tools.workflow.repository import InMemoryWorkflowRepository
        from triads.tools.workflow.service import WorkflowService

        repository = InMemoryWorkflowRepository()
        service = WorkflowService(repository)
        mock.return_value = service
        yield


class TestListWorkflows:
    """Tests for list_workflows MCP tool."""

    def test_list_workflows_returns_mcp_compliant_result(self):
        """list_workflows returns ToolResult in MCP format."""
        result = WorkflowTools.list_workflows()

        assert isinstance(result, ToolResult)
        assert result.success is True
        assert len(result.content) == 1
        assert result.content[0]["type"] == "text"
        assert "workflow instance" in result.content[0]["text"].lower()

    def test_list_workflows_shows_all_instances_by_default(self):
        """list_workflows shows all instances when no filter provided."""
        result = WorkflowTools.list_workflows()

        assert result.success is True
        text = result.content[0]["text"]
        # Should contain sample instances from InMemoryWorkflowRepository
        assert "feature-oauth2" in text or "OAuth2" in text

    def test_list_workflows_with_status_filter(self):
        """list_workflows filters by status when provided."""
        result = WorkflowTools.list_workflows(status="in_progress")

        assert result.success is True
        text = result.content[0]["text"]
        assert "in_progress" in text or "OAuth2" in text  # OAuth2 is in_progress

    def test_list_workflows_with_completed_filter(self):
        """list_workflows shows only completed workflows."""
        result = WorkflowTools.list_workflows(status="completed")

        assert result.success is True
        text = result.content[0]["text"]
        # Should show completed workflow or "found 0"
        assert "workflow instance" in text.lower()

    def test_list_workflows_error_returns_proper_format(self):
        """list_workflows returns error in MCP format when operation fails."""
        with patch(
            "triads.tools.workflow.entrypoint.bootstrap_workflow_service"
        ) as mock_bootstrap:
            from triads.tools.workflow.repository import WorkflowRepositoryError

            mock_service = Mock()
            mock_service.list_workflows.side_effect = WorkflowRepositoryError(
                "Invalid status"
            )
            mock_bootstrap.return_value = mock_service

            result = WorkflowTools.list_workflows(status="invalid")

            assert isinstance(result, ToolResult)
            assert result.success is False
            assert result.error is not None


class TestGetWorkflow:
    """Tests for get_workflow MCP tool."""

    def test_get_workflow_returns_mcp_compliant_result(self):
        """get_workflow returns ToolResult in MCP format."""
        result = WorkflowTools.get_workflow("feature-oauth2-20251023-100523")

        assert isinstance(result, ToolResult)
        assert result.success is True
        assert len(result.content) == 1
        assert result.content[0]["type"] == "text"

    def test_get_workflow_shows_instance_details(self):
        """get_workflow shows detailed instance information."""
        result = WorkflowTools.get_workflow("feature-oauth2-20251023-100523")

        assert result.success is True
        text = result.content[0]["text"]
        assert "OAuth2 Integration" in text
        assert "implementation" in text  # Current triad
        assert "Progress" in text

    def test_get_workflow_shows_completed_triads(self):
        """get_workflow shows completed triads list."""
        result = WorkflowTools.get_workflow("feature-oauth2-20251023-100523")

        assert result.success is True
        text = result.content[0]["text"]
        assert "Completed Triads" in text
        assert "idea-validation" in text or "design" in text

    def test_get_workflow_not_found_returns_error(self):
        """get_workflow returns error for non-existent instance."""
        result = WorkflowTools.get_workflow("nonexistent-instance")

        assert isinstance(result, ToolResult)
        assert result.success is False
        assert result.error is not None
        assert "not found" in result.error.lower()

    def test_get_workflow_error_returns_proper_format(self):
        """get_workflow returns error in MCP format when operation fails."""
        with patch(
            "triads.tools.workflow.entrypoint.bootstrap_workflow_service"
        ) as mock_bootstrap:
            mock_service = Mock()
            mock_service.get_workflow.side_effect = Exception("Database error")
            mock_bootstrap.return_value = mock_service

            result = WorkflowTools.get_workflow("test-instance")

            assert isinstance(result, ToolResult)
            assert result.success is False
            assert result.error is not None


class TestToolSignatures:
    """Tests for MCP tool signatures."""

    def test_both_tools_have_proper_signatures(self):
        """Both MCP tools exist with proper signatures."""
        # list_workflows
        assert hasattr(WorkflowTools, "list_workflows")
        assert callable(WorkflowTools.list_workflows)

        # get_workflow
        assert hasattr(WorkflowTools, "get_workflow")
        assert callable(WorkflowTools.get_workflow)

    def test_list_workflows_accepts_optional_status(self):
        """list_workflows accepts optional status parameter."""
        # Should not raise
        result = WorkflowTools.list_workflows()
        assert isinstance(result, ToolResult)

        result = WorkflowTools.list_workflows(status="in_progress")
        assert isinstance(result, ToolResult)

    def test_get_workflow_accepts_instance_id(self):
        """get_workflow accepts instance_id parameter."""
        # Should not raise (even if not found, should return error ToolResult)
        result = WorkflowTools.get_workflow("test-id")
        assert isinstance(result, ToolResult)
