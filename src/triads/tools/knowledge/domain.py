"""Domain models for knowledge tools.

Provides Node, Edge, and KnowledgeGraph domain models with business logic.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Node:
    """Knowledge graph node.

    Represents a node in the knowledge graph with immutable properties.

    Attributes:
        id: Unique node identifier
        label: Human-readable label
        type: Node type (concept, decision, entity, finding, task, workflow, uncertainty)
        confidence: Confidence score (0.0-1.0)
        content: Optional node content/description
        evidence: Optional list of evidence sources
        metadata: Optional metadata dictionary
    """

    id: str
    label: str
    type: str
    confidence: float
    content: Optional[str] = None
    evidence: Optional[list[str]] = None
    metadata: Optional[dict] = None


@dataclass(frozen=True)
class Edge:
    """Knowledge graph edge.

    Represents a directed edge between two nodes.

    Attributes:
        source: Source node ID
        target: Target node ID
        relationship: Relationship type/label
    """

    source: str
    target: str
    relationship: str


@dataclass
class KnowledgeGraph:
    """Knowledge graph domain model with business logic.

    Provides search and validation operations on knowledge graphs.

    Attributes:
        triad: Triad name
        nodes: List of nodes
        edges: List of edges
    """

    triad: str
    nodes: list[Node]
    edges: list[Edge]

    def search(self, query: str, min_confidence: float = 0.0) -> list[Node]:
        """Search nodes by label/content, filter by confidence.

        Case-insensitive substring search in label and content fields.
        Empty query returns all nodes matching confidence filter.

        Args:
            query: Search query string (case-insensitive)
            min_confidence: Minimum confidence threshold (0.0-1.0)

        Returns:
            List of matching nodes, sorted by confidence (highest first)

        Example:
            >>> graph = KnowledgeGraph(triad="design", nodes=[...], edges=[])
            >>> results = graph.search("OAuth", min_confidence=0.85)
            >>> for node in results:
            ...     print(f"{node.label}: {node.confidence}")
        """
        query_lower = query.lower()
        results = []

        for node in self.nodes:
            # Filter by confidence
            if node.confidence < min_confidence:
                continue

            # Empty query = return all (after confidence filter)
            if not query:
                results.append(node)
                continue

            # Search in label and content
            if query_lower in node.label.lower():
                results.append(node)
                continue

            if node.content and query_lower in node.content.lower():
                results.append(node)
                continue

        # Sort by confidence (highest first)
        results.sort(key=lambda n: n.confidence, reverse=True)
        return results

    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate graph structure (edges reference valid nodes).

        Checks that all edges reference nodes that exist in the graph.

        Returns:
            Tuple of (is_valid, error_message)
            - (True, None) if valid
            - (False, error_message) if invalid

        Example:
            >>> graph = KnowledgeGraph(triad="test", nodes=[...], edges=[...])
            >>> is_valid, error = graph.validate()
            >>> if not is_valid:
            ...     print(f"Validation error: {error}")
        """
        logger.debug(
            "Validating graph structure",
            extra={"triad": self.triad, "nodes": len(self.nodes), "edges": len(self.edges)}
        )

        # Build set of node IDs for fast lookup
        node_ids = {node.id for node in self.nodes}

        # Check each edge
        for edge in self.edges:
            if edge.source not in node_ids:
                error_msg = f"Edge source '{edge.source}' does not exist in graph nodes"
                logger.warning(
                    "Graph validation failed: invalid edge source",
                    extra={
                        "triad": self.triad,
                        "edge_source": edge.source,
                        "edge_target": edge.target,
                        "relationship": edge.relationship
                    }
                )
                return (False, error_msg)

            if edge.target not in node_ids:
                error_msg = f"Edge target '{edge.target}' does not exist in graph nodes"
                logger.warning(
                    "Graph validation failed: invalid edge target",
                    extra={
                        "triad": self.triad,
                        "edge_source": edge.source,
                        "edge_target": edge.target,
                        "relationship": edge.relationship
                    }
                )
                return (False, error_msg)

        logger.debug("Graph validation passed", extra={"triad": self.triad})
        return (True, None)
