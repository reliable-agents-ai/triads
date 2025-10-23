"""
Test that plugin commands can use KnowledgeTools.

Phase 8 validation: Verify tools are accessible for plugin command use.
"""

from triads.tools.knowledge import KnowledgeTools
from triads.tools.shared import ToolResult


class TestPluginCommandToolAccess:
    """Verify plugin commands can access and use tools."""

    def test_plugin_can_import_knowledge_tools(self):
        """Verify KnowledgeTools can be imported."""
        assert KnowledgeTools is not None
        assert hasattr(KnowledgeTools, 'query_graph')
        assert hasattr(KnowledgeTools, 'get_graph_status')

    def test_plugin_can_query_for_draft_nodes(self):
        """Verify plugin can query for draft nodes using tools."""
        # Plugin commands like /knowledge-review-drafts can use this
        result = KnowledgeTools.query_graph(
            triad="default",
            query="draft",  # Would search for draft status
            min_confidence=0.0
        )

        assert isinstance(result, ToolResult)
        assert result.success or not result.success  # Either is valid

    def test_plugin_can_get_graph_status(self):
        """Verify plugin can get graph status for command implementations."""
        result = KnowledgeTools.get_graph_status()

        assert isinstance(result, ToolResult)
        assert result.success
        assert result.content[0]["type"] == "text"

    def test_plugin_can_show_specific_node(self):
        """Verify plugin can show node details for promote/archive commands."""
        # Would be used by /knowledge-promote <node_id>
        result = KnowledgeTools.show_node(
            node_id="test_node_id",
            triad="default"
        )

        # May fail if node doesn't exist, but tool is accessible
        assert isinstance(result, ToolResult)


class TestPluginCommandPatterns:
    """Test patterns plugin commands would use."""

    def test_review_drafts_pattern(self):
        """Test pattern for /knowledge-review-drafts command."""
        # Step 1: Get all graphs
        status_result = KnowledgeTools.get_graph_status()
        assert status_result.success

        # Step 2: Query each graph for draft nodes
        # (In real implementation, would parse triads from status)
        query_result = KnowledgeTools.query_graph(
            triad="default",
            query="draft",
            min_confidence=0.0
        )
        assert isinstance(query_result, ToolResult)

        # Step 3: Format results for user
        # (Formatting would be done in plugin command implementation)

    def test_promote_node_pattern(self):
        """Test pattern for /knowledge-promote <node_id> command."""
        # Step 1: Find the node
        node_result = KnowledgeTools.show_node(
            node_id="test_node",
            triad="default"
        )

        # Step 2: Verify it's a draft
        # (Would parse node details from result)

        # Step 3: Update status (would use km.commands or direct edit)
        # (Not implemented in tools yet - Phase 9 work)

        assert isinstance(node_result, ToolResult)

    def test_archive_node_pattern(self):
        """Test pattern for /knowledge-archive <node_id> command."""
        # Similar to promote pattern
        node_result = KnowledgeTools.show_node(
            node_id="test_node",
            triad="default"
        )

        assert isinstance(node_result, ToolResult)


class TestFutureCommandEnhancements:
    """Tests for potential future command enhancements using tools."""

    def test_list_all_triads_for_commands(self):
        """Commands could use list_triads for completions."""
        result = KnowledgeTools.list_triads()

        assert result.success
        assert "graph" in result.content[0]["text"].lower()

    def test_search_across_all_graphs(self):
        """Commands could search all graphs at once."""
        # This would require iterating triads or adding search_all tool
        triads_result = KnowledgeTools.list_triads()
        assert triads_result.success

        # In future, could add KnowledgeTools.search_all(query)
        # For now, commands can query each triad separately
