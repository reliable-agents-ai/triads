"""MCP tool entrypoints for knowledge tools.

Provides 5 MCP-compliant tools for accessing knowledge graphs.
"""

from typing import Optional

from triads.tools.shared import ToolResult
from triads.tools.knowledge.bootstrap import bootstrap_knowledge_service
from triads.tools.knowledge.formatters import (
    format_query_result,
    format_status_result,
    format_node_details,
    format_triad_list,
)


class KnowledgeTools:
    """MCP tool entrypoints for knowledge graph access.

    All methods return ToolResult in MCP-compliant format.
    """

    @staticmethod
    def query_graph(triad: str, query: str, min_confidence: float = 0.0) -> ToolResult:
        """Search knowledge graph by query string.

        MCP Tool: query_graph

        Args:
            triad: Triad name to search
            query: Search query string (case-insensitive)
            min_confidence: Minimum confidence threshold (default: 0.0)

        Returns:
            ToolResult with formatted search results

        Example:
            >>> result = KnowledgeTools.query_graph("design", "OAuth", min_confidence=0.85)
            >>> print(result.content[0]["text"])
        """
        service = bootstrap_knowledge_service()

        try:
            result = service.query_graph(triad, query, min_confidence)
            formatted = format_query_result(result)

            return ToolResult(
                success=True, content=[{"type": "text", "text": formatted}]
            )

        except Exception as e:
            return ToolResult(success=False, content=[], error=str(e))

    @staticmethod
    def get_graph_status(triad: Optional[str] = None) -> ToolResult:
        """Get metadata/health for graphs.

        MCP Tool: get_graph_status

        Args:
            triad: Optional triad name (None = all graphs)

        Returns:
            ToolResult with formatted status information

        Example:
            >>> result = KnowledgeTools.get_graph_status()  # All graphs
            >>> result = KnowledgeTools.get_graph_status(triad="design")  # Single graph
        """
        service = bootstrap_knowledge_service()

        try:
            result = service.get_graph_status(triad)
            formatted = format_status_result(result)

            return ToolResult(
                success=True, content=[{"type": "text", "text": formatted}]
            )

        except Exception as e:
            return ToolResult(success=False, content=[], error=str(e))

    @staticmethod
    def show_node(node_id: str, triad: Optional[str] = None) -> ToolResult:
        """Get detailed node information.

        MCP Tool: show_node

        Args:
            node_id: Node identifier
            triad: Optional triad name (None = search all graphs)

        Returns:
            ToolResult with formatted node details

        Example:
            >>> result = KnowledgeTools.show_node("oauth_decision", triad="design")
        """
        service = bootstrap_knowledge_service()

        try:
            node = service.show_node(node_id, triad)
            formatted = format_node_details(node)

            return ToolResult(
                success=True, content=[{"type": "text", "text": formatted}]
            )

        except Exception as e:
            return ToolResult(success=False, content=[], error=str(e))

    @staticmethod
    def list_triads() -> ToolResult:
        """List all triads with node counts.

        MCP Tool: list_triads

        Returns:
            ToolResult with formatted triad list

        Example:
            >>> result = KnowledgeTools.list_triads()
        """
        service = bootstrap_knowledge_service()

        try:
            triads = service.list_triads()
            formatted = format_triad_list(triads)

            return ToolResult(
                success=True, content=[{"type": "text", "text": formatted}]
            )

        except Exception as e:
            return ToolResult(success=False, content=[], error=str(e))

    @staticmethod
    def get_session_context(project_dir: Optional[str] = None) -> ToolResult:
        """Get full session context (for hooks).

        MCP Tool: get_session_context

        This tool is designed for use in session hooks to provide
        full knowledge graph context to agents.

        Args:
            project_dir: Optional project directory (defaults to current directory)

        Returns:
            ToolResult with formatted session context

        Example:
            >>> result = KnowledgeTools.get_session_context()

        Note:
            Currently returns basic status. Future versions may include
            more context like recent updates, active workflows, etc.
        """
        service = bootstrap_knowledge_service()

        try:
            result = service.get_graph_status(triad=None)  # All graphs
            formatted = format_status_result(result)

            # Prepend context header
            context = "Session Knowledge Context:\n\n" + formatted

            return ToolResult(success=True, content=[{"type": "text", "text": context}])

        except Exception as e:
            return ToolResult(success=False, content=[], error=str(e))
