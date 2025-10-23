"""Tests for router tools MCP entrypoints."""

import pytest
from unittest.mock import Mock, patch

from triads.tools.router.entrypoint import RouterTools
from triads.tools.shared import ToolResult


class TestRoutePrompt:
    """Tests for route_prompt MCP tool."""

    def test_route_prompt_returns_mcp_compliant_result(self):
        """route_prompt returns ToolResult in MCP format."""
        result = RouterTools.route_prompt("Let's implement OAuth2")

        assert isinstance(result, ToolResult)
        assert result.success is True
        assert len(result.content) == 1
        assert result.content[0]["type"] == "text"
        assert "implementation" in result.content[0]["text"].lower()
        assert "confidence" in result.content[0]["text"].lower()

    def test_route_prompt_with_design_keywords(self):
        """route_prompt correctly routes design-related prompts."""
        result = RouterTools.route_prompt("How should we architect the database?")

        assert result.success is True
        text = result.content[0]["text"]
        assert "design" in text.lower()

    def test_route_prompt_error_returns_proper_format(self):
        """route_prompt returns error in MCP format when routing fails."""
        with patch(
            "triads.tools.router.entrypoint.bootstrap_router_service"
        ) as mock_bootstrap:
            from triads.tools.router.repository import RouterRepositoryError

            mock_service = Mock()
            mock_service.route_prompt.side_effect = RouterRepositoryError(
                "Prompt cannot be empty"
            )
            mock_bootstrap.return_value = mock_service

            result = RouterTools.route_prompt("")

            assert isinstance(result, ToolResult)
            assert result.success is False
            assert result.error is not None
            assert "empty" in result.error.lower()

    def test_route_prompt_includes_confidence_percentage(self):
        """route_prompt formats confidence as percentage."""
        result = RouterTools.route_prompt("Deploy the application")

        assert result.success is True
        text = result.content[0]["text"]
        # Should contain percentage (e.g., "85%")
        assert "%" in text


class TestGetCurrentTriad:
    """Tests for get_current_triad MCP tool."""

    def test_get_current_triad_returns_mcp_compliant_result(self):
        """get_current_triad returns ToolResult in MCP format."""
        result = RouterTools.get_current_triad()

        assert isinstance(result, ToolResult)
        assert result.success is True
        assert len(result.content) == 1
        assert result.content[0]["type"] == "text"

    def test_get_current_triad_shows_none_when_no_active_triad(self):
        """get_current_triad shows 'None' when no triad is active."""
        result = RouterTools.get_current_triad()

        assert result.success is True
        text = result.content[0]["text"]
        assert "none" in text.lower()

    def test_get_current_triad_error_returns_proper_format(self):
        """get_current_triad returns error in MCP format when operation fails."""
        with patch(
            "triads.tools.router.entrypoint.bootstrap_router_service"
        ) as mock_bootstrap:
            mock_service = Mock()
            mock_service.get_current_triad.side_effect = Exception(
                "State file corrupted"
            )
            mock_bootstrap.return_value = mock_service

            result = RouterTools.get_current_triad()

            assert isinstance(result, ToolResult)
            assert result.success is False
            assert result.error is not None

    def test_get_current_triad_includes_session_info(self):
        """get_current_triad includes session ID in output."""
        result = RouterTools.get_current_triad()

        assert result.success is True
        text = result.content[0]["text"]
        assert "session" in text.lower()


class TestToolSignatures:
    """Tests for MCP tool signatures."""

    def test_both_tools_have_proper_signatures(self):
        """Both MCP tools exist with proper signatures."""
        # route_prompt
        assert hasattr(RouterTools, "route_prompt")
        assert callable(RouterTools.route_prompt)

        # get_current_triad
        assert hasattr(RouterTools, "get_current_triad")
        assert callable(RouterTools.get_current_triad)

    def test_route_prompt_accepts_prompt_parameter(self):
        """route_prompt accepts prompt as parameter."""
        # Should not raise
        result = RouterTools.route_prompt("test prompt")
        assert isinstance(result, ToolResult)

    def test_get_current_triad_accepts_no_parameters(self):
        """get_current_triad works with no parameters."""
        # Should not raise
        result = RouterTools.get_current_triad()
        assert isinstance(result, ToolResult)
