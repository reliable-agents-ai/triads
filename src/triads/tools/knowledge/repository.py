"""Repository layer for knowledge tools.

Provides AbstractGraphRepository interface and two implementations:
- InMemoryGraphRepository: For testing with seeded data
- FileSystemGraphRepository: Production, wraps km.graph_access
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict

from triads.tools.knowledge.domain import Node, Edge, KnowledgeGraph


class GraphNotFoundError(Exception):
    """Raised when requested graph doesn't exist."""

    def __init__(self, triad: str, available: list[str]) -> None:
        self.triad = triad
        self.available = available
        available_str = ", ".join(sorted(available)) if available else "none"
        super().__init__(
            f"Graph '{triad}' not found. Available graphs: {available_str}"
        )


class AbstractGraphRepository(ABC):
    """Abstract repository for knowledge graphs.

    Provides interface for loading and listing graphs.
    """

    @abstractmethod
    def get(self, triad: str) -> KnowledgeGraph:
        """Get graph by triad name.

        Args:
            triad: Triad name

        Returns:
            KnowledgeGraph instance

        Raises:
            GraphNotFoundError: If graph doesn't exist
        """
        pass

    @abstractmethod
    def list_all(self) -> list[KnowledgeGraph]:
        """List all available graphs.

        Returns:
            List of KnowledgeGraph instances
        """
        pass


class InMemoryGraphRepository(AbstractGraphRepository):
    """In-memory graph repository for testing.

    Can be seeded with test data via constructor.

    Example:
        >>> graphs = {"design": KnowledgeGraph(...)}
        >>> repo = InMemoryGraphRepository(graphs)
        >>> graph = repo.get("design")
    """

    def __init__(self, graphs: Dict[str, KnowledgeGraph] | None = None) -> None:
        """Initialize repository with optional seed data.

        Args:
            graphs: Dictionary mapping triad names to KnowledgeGraph instances
        """
        self.graphs = graphs or {}

    def get(self, triad: str) -> KnowledgeGraph:
        """Get graph by triad name.

        Args:
            triad: Triad name

        Returns:
            KnowledgeGraph instance

        Raises:
            GraphNotFoundError: If graph doesn't exist
        """
        if triad not in self.graphs:
            available = list(self.graphs.keys())
            raise GraphNotFoundError(triad, available)

        return self.graphs[triad]

    def list_all(self) -> list[KnowledgeGraph]:
        """List all available graphs.

        Returns:
            List of KnowledgeGraph instances
        """
        return list(self.graphs.values())


class FileSystemGraphRepository(AbstractGraphRepository):
    """File system graph repository.

    Wraps existing triads.km.graph_access.GraphLoader to provide
    domain model interface.

    Example:
        >>> from pathlib import Path
        >>> repo = FileSystemGraphRepository(Path(".claude/graphs"))
        >>> graph = repo.get("design")
    """

    def __init__(self, graphs_dir: Path | None = None) -> None:
        """Initialize repository with graphs directory.

        Args:
            graphs_dir: Path to graphs directory (defaults to .claude/graphs)
        """
        # Import here to avoid circular imports
        from triads.km.graph_access.loader import GraphLoader

        self.graphs_dir = graphs_dir or Path(".claude/graphs")
        self._loader = GraphLoader(graphs_dir=self.graphs_dir)

    def get(self, triad: str) -> KnowledgeGraph:
        """Get graph by triad name.

        Args:
            triad: Triad name

        Returns:
            KnowledgeGraph domain model

        Raises:
            GraphNotFoundError: If graph doesn't exist
        """
        # Load using existing GraphLoader
        graph_data = self._loader.load_graph(triad)

        if graph_data is None:
            available = self._loader.list_triads()
            raise GraphNotFoundError(triad, available)

        # Transform to domain model
        return self._to_domain(triad, graph_data)

    def list_all(self) -> list[KnowledgeGraph]:
        """List all available graphs.

        Returns:
            List of KnowledgeGraph domain models
        """
        graphs = []

        for triad in self._loader.list_triads():
            graph_data = self._loader.load_graph(triad)
            if graph_data:
                graphs.append(self._to_domain(triad, graph_data))

        return graphs

    def _to_domain(self, triad: str, data: dict) -> KnowledgeGraph:
        """Transform graph data from JSON format to domain model.

        Args:
            triad: Triad name
            data: Graph data from GraphLoader (NetworkX JSON format)

        Returns:
            KnowledgeGraph domain model
        """
        # Transform nodes
        nodes = []
        for node_data in data.get("nodes", []):
            node = Node(
                id=node_data.get("id", ""),
                label=node_data.get("label", node_data.get("id", "")),
                type=node_data.get("type", "Unknown"),
                confidence=float(node_data.get("confidence", 0.0)),
                content=node_data.get("content") or node_data.get("description"),
                evidence=node_data.get("evidence"),
                metadata={
                    k: v
                    for k, v in node_data.items()
                    if k not in ["id", "label", "type", "confidence", "content", "description", "evidence"]
                },
            )
            nodes.append(node)

        # Transform edges
        edges = []
        for edge_data in data.get("links", []) or data.get("edges", []):
            edge = Edge(
                source=edge_data.get("source", ""),
                target=edge_data.get("target", ""),
                relationship=edge_data.get("key", "") or edge_data.get("relationship", ""),
            )
            edges.append(edge)

        return KnowledgeGraph(triad=triad, nodes=nodes, edges=edges)
