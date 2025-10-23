"""Service layer for knowledge tools.

Provides business logic for MCP tools.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from triads.tools.knowledge.domain import Node, KnowledgeGraph
from triads.tools.knowledge.repository import AbstractGraphRepository


@dataclass
class QueryResult:
    """Result of a query_graph operation.

    Attributes:
        nodes: List of matching nodes
        total: Total number of matches
    """

    nodes: list[Node]
    total: int


@dataclass
class StatusResult:
    """Result of a get_graph_status operation.

    Attributes:
        graphs: List of knowledge graphs
    """

    graphs: list[KnowledgeGraph]


class KnowledgeService:
    """Service layer for knowledge tools.

    Provides business logic for querying, retrieving status,
    and displaying node information from knowledge graphs.

    Example:
        >>> from triads.tools.knowledge.repository import InMemoryGraphRepository
        >>> repo = InMemoryGraphRepository(graphs={...})
        >>> service = KnowledgeService(repo)
        >>> result = service.query_graph("design", "OAuth", min_confidence=0.85)
    """

    def __init__(self, graph_repo: AbstractGraphRepository) -> None:
        """Initialize service with graph repository.

        Args:
            graph_repo: Repository for accessing knowledge graphs
        """
        self.graph_repo = graph_repo

    def query_graph(
        self, triad: str, query: str, min_confidence: float = 0.0
    ) -> QueryResult:
        """Query knowledge graph by search string and confidence.

        Searches specified graph for nodes matching query string,
        filtered by minimum confidence threshold.

        Args:
            triad: Triad name to search
            query: Search query string (case-insensitive)
            min_confidence: Minimum confidence threshold (0.0-1.0)

        Returns:
            QueryResult with matching nodes

        Raises:
            GraphNotFoundError: If graph doesn't exist

        Example:
            >>> result = service.query_graph("design", "OAuth", min_confidence=0.85)
            >>> for node in result.nodes:
            ...     print(f"{node.label}: {node.confidence}")
        """
        graph = self.graph_repo.get(triad)
        nodes = graph.search(query, min_confidence)
        return QueryResult(nodes=nodes, total=len(nodes))

    def get_graph_status(self, triad: Optional[str] = None) -> StatusResult:
        """Get metadata/health for graphs.

        If triad is specified, returns status for that graph only.
        Otherwise returns status for all graphs.

        Args:
            triad: Optional triad name (None = all graphs)

        Returns:
            StatusResult with list of graphs

        Raises:
            GraphNotFoundError: If specified graph doesn't exist

        Example:
            >>> # Get status for all graphs
            >>> result = service.get_graph_status()
            >>> for graph in result.graphs:
            ...     print(f"{graph.triad}: {len(graph.nodes)} nodes")
            >>>
            >>> # Get status for single graph
            >>> result = service.get_graph_status(triad="design")
        """
        if triad:
            # Single graph
            graph = self.graph_repo.get(triad)
            return StatusResult(graphs=[graph])
        else:
            # All graphs
            graphs = self.graph_repo.list_all()
            return StatusResult(graphs=graphs)

    def show_node(self, node_id: str, triad: Optional[str] = None) -> Optional[Node]:
        """Get detailed node information.

        If triad is specified, searches only that graph.
        Otherwise searches all graphs for the node.

        Args:
            node_id: Node identifier
            triad: Optional triad name (None = search all)

        Returns:
            Node if found, None otherwise

        Example:
            >>> # Search specific graph
            >>> node = service.show_node("oauth_decision", triad="design")
            >>>
            >>> # Search all graphs
            >>> node = service.show_node("oauth_decision")
        """
        if triad:
            # Search specific graph
            graph = self.graph_repo.get(triad)
            for node in graph.nodes:
                if node.id == node_id:
                    return node
            return None
        else:
            # Search all graphs
            graphs = self.graph_repo.list_all()
            for graph in graphs:
                for node in graph.nodes:
                    if node.id == node_id:
                        return node
            return None

    def list_triads(self) -> list[dict]:
        """List all triads with node counts.

        Returns:
            List of dicts with "name" and "node_count" keys

        Example:
            >>> triads = service.list_triads()
            >>> for triad in triads:
            ...     print(f"{triad['name']}: {triad['node_count']} nodes")
        """
        graphs = self.graph_repo.list_all()
        return [
            {"name": graph.triad, "node_count": len(graph.nodes)} for graph in graphs
        ]
