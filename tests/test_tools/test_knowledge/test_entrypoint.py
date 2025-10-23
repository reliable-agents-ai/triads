"""Tests for knowledge tools MCP entrypoints."""

import pytest
from unittest.mock import Mock, patch

from triads.tools.knowledge.entrypoint import KnowledgeTools
from triads.tools.shared import ToolResult


class TestQueryGraph:
    """Tests for query_graph MCP tool."""

    def test_query_graph_returns_mcp_compliant_result(self, seeded_repo):
        """query_graph returns ToolResult in MCP format."""
        with patch(
            "triads.tools.knowledge.entrypoint.bootstrap_knowledge_service"
        ) as mock_bootstrap:
            from triads.tools.knowledge.service import KnowledgeService

            mock_bootstrap.return_value = KnowledgeService(seeded_repo)

            result = KnowledgeTools.query_graph(
                triad="design", query="OAuth", min_confidence=0.0
            )

            assert isinstance(result, ToolResult)
            assert result.success is True
            assert len(result.content) == 1
            assert result.content[0]["type"] == "text"
            assert "oauth_decision" in result.content[0]["text"]

    def test_query_graph_error_returns_proper_format(self):
        """query_graph returns error in MCP format when graph not found."""
        with patch(
            "triads.tools.knowledge.entrypoint.bootstrap_knowledge_service"
        ) as mock_bootstrap:
            from triads.tools.knowledge.repository import GraphNotFoundError

            mock_service = Mock()
            mock_service.query_graph.side_effect = GraphNotFoundError(
                "missing", ["design"]
            )
            mock_bootstrap.return_value = mock_service

            result = KnowledgeTools.query_graph(
                triad="missing", query="test", min_confidence=0.0
            )

            assert isinstance(result, ToolResult)
            assert result.success is False
            assert result.error is not None
            assert "missing" in result.error


class TestGetGraphStatus:
    """Tests for get_graph_status MCP tool."""

    def test_get_graph_status_all_graphs(self, seeded_repo):
        """get_graph_status returns all graphs when triad=None."""
        with patch(
            "triads.tools.knowledge.entrypoint.bootstrap_knowledge_service"
        ) as mock_bootstrap:
            from triads.tools.knowledge.service import KnowledgeService

            mock_bootstrap.return_value = KnowledgeService(seeded_repo)

            result = KnowledgeTools.get_graph_status(triad=None)

            assert isinstance(result, ToolResult)
            assert result.success is True
            assert "design" in result.content[0]["text"]
            assert "implementation" in result.content[0]["text"]

    def test_get_graph_status_single_graph(self, seeded_repo):
        """get_graph_status returns single graph when triad specified."""
        with patch(
            "triads.tools.knowledge.entrypoint.bootstrap_knowledge_service"
        ) as mock_bootstrap:
            from triads.tools.knowledge.service import KnowledgeService

            mock_bootstrap.return_value = KnowledgeService(seeded_repo)

            result = KnowledgeTools.get_graph_status(triad="design")

            assert isinstance(result, ToolResult)
            assert result.success is True
            text = result.content[0]["text"]
            assert "design" in text
            assert "Nodes: 3" in text


class TestShowNode:
    """Tests for show_node MCP tool."""

    def test_show_node_found(self, seeded_repo):
        """show_node returns node details when found."""
        with patch(
            "triads.tools.knowledge.entrypoint.bootstrap_knowledge_service"
        ) as mock_bootstrap:
            from triads.tools.knowledge.service import KnowledgeService

            mock_bootstrap.return_value = KnowledgeService(seeded_repo)

            result = KnowledgeTools.show_node(node_id="oauth_decision", triad="design")

            assert isinstance(result, ToolResult)
            assert result.success is True
            text = result.content[0]["text"]
            assert "oauth_decision" in text
            assert "OAuth2 Authentication Decision" in text

    def test_show_node_not_found(self, seeded_repo):
        """show_node returns not found message when node doesn't exist."""
        with patch(
            "triads.tools.knowledge.entrypoint.bootstrap_knowledge_service"
        ) as mock_bootstrap:
            from triads.tools.knowledge.service import KnowledgeService

            mock_bootstrap.return_value = KnowledgeService(seeded_repo)

            result = KnowledgeTools.show_node(node_id="nonexistent", triad="design")

            assert isinstance(result, ToolResult)
            assert result.success is True  # Still successful, just not found
            assert "not found" in result.content[0]["text"].lower()


class TestListTriads:
    """Tests for list_triads MCP tool."""

    def test_list_triads_returns_formatted_list(self, seeded_repo):
        """list_triads returns formatted list of triads."""
        with patch(
            "triads.tools.knowledge.entrypoint.bootstrap_knowledge_service"
        ) as mock_bootstrap:
            from triads.tools.knowledge.service import KnowledgeService

            mock_bootstrap.return_value = KnowledgeService(seeded_repo)

            result = KnowledgeTools.list_triads()

            assert isinstance(result, ToolResult)
            assert result.success is True
            text = result.content[0]["text"]
            assert "design" in text
            assert "implementation" in text
            assert "3 nodes" in text  # design has 3 nodes


class TestToolSignatures:
    """Tests for MCP tool signatures."""

    def test_all_5_tools_have_proper_signatures(self):
        """All 5 MCP tools exist with proper signatures."""
        # query_graph
        assert hasattr(KnowledgeTools, "query_graph")
        assert callable(KnowledgeTools.query_graph)

        # get_graph_status
        assert hasattr(KnowledgeTools, "get_graph_status")
        assert callable(KnowledgeTools.get_graph_status)

        # show_node
        assert hasattr(KnowledgeTools, "show_node")
        assert callable(KnowledgeTools.show_node)

        # list_triads
        assert hasattr(KnowledgeTools, "list_triads")
        assert callable(KnowledgeTools.list_triads)

        # get_session_context
        assert hasattr(KnowledgeTools, "get_session_context")
        assert callable(KnowledgeTools.get_session_context)
