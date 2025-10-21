"""Graph search and filtering functionality.

This module handles:
- search_knowledge() - Main search function
- Filtering by confidence, node type, triad
- Similarity scoring
- Results ranking

Performance:
- Typical search: < 100ms for 10-100 node graphs
- Case-insensitive substring matching
- Results ranked by relevance (label > description > ID)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from triads.km import config
from triads.km.graph_access.loader import GraphLoader, GraphNotFoundError, InvalidTriadNameError

# Initialize module logger
logger = logging.getLogger(__name__)


# ============================================================================
# Data Classes
# ============================================================================


@dataclass
class SearchResult:
    """A single search result from knowledge graph query."""

    node_id: str
    triad: str
    label: str
    node_type: str
    confidence: float
    matched_field: str  # "label", "description", or "id"
    snippet: str  # Context snippet showing the match
    relevance_score: float  # 0-1, higher = more relevant


# ============================================================================
# GraphSearcher: Search functionality
# ============================================================================


class GraphSearcher:
    """Search functionality for knowledge graphs.

    Provides case-insensitive substring search with filtering by:
    - Triad (search specific graph)
    - Node type (Entity, Concept, Decision, etc.)
    - Minimum confidence threshold

    Results are ranked by relevance:
    - Label matches (highest priority)
    - Description matches (medium priority)
    - ID matches (lowest priority)

    Example:
        searcher = GraphSearcher(loader)
        results = searcher.search(
            "OAuth",
            triad="design",
            node_type="Decision",
            min_confidence=0.85
        )
        for result in results:
            print(f"{result.label} ({result.confidence:.2f})")
    """

    def __init__(self, loader: GraphLoader) -> None:
        """Initialize searcher with graph loader.

        Args:
            loader: GraphLoader instance for accessing graphs
        """
        self.loader = loader

    def search(
        self,
        query: str,
        triad: str | None = None,
        node_type: str | None = None,
        min_confidence: float | None = None,
    ) -> list[SearchResult]:
        """Case-insensitive substring search with filters.

        Searches in node label, description, and ID fields.
        Results are ranked by relevance and sorted.

        Args:
            query: Search query string (case-insensitive)
            triad: Optional triad name to limit search
            node_type: Optional node type filter (Entity, Concept, etc.)
            min_confidence: Optional minimum confidence threshold (0.0-1.0)

        Returns:
            List of SearchResult objects, sorted by relevance (highest first)

        Example:
            # Search all graphs for "OAuth"
            results = searcher.search("OAuth")

            # Search design graph for high-confidence Decisions
            results = searcher.search(
                "auth",
                triad="design",
                node_type="Decision",
                min_confidence=0.85
            )
        """
        query_lower = query.lower()
        results: list[SearchResult] = []

        # Determine which graphs to search
        if triad:
            try:
                graph = self.loader.load_graph(triad)
                if not graph:
                    available = self.loader.list_triads()
                    logger.warning(
                        "Search failed: graph not found",
                        extra={"triad": triad, "available": available}
                    )
                    raise GraphNotFoundError(triad, available)
                graphs_to_search = {triad: graph}
            except InvalidTriadNameError as e:
                available = self.loader.list_triads()
                logger.warning(
                    "Search failed: invalid triad name",
                    extra={"triad": triad, "available": available}
                )
                raise GraphNotFoundError(triad, available) from e
        else:
            graphs_to_search = self.loader.load_all_graphs()

        # Search each graph
        for triad_name, graph in graphs_to_search.items():
            nodes = graph.get("nodes", [])

            for node in nodes:
                # Apply filters
                if node_type and node.get("type") != node_type:
                    continue

                confidence = self._get_confidence(node)
                if min_confidence is not None and confidence < min_confidence:
                    continue

                # Search in fields
                node_id = node.get("id", "")
                label = node.get("label", node_id)
                description = node.get("description", "")

                # Check for matches
                match_info = self._find_best_match(
                    query_lower, node_id, label, description
                )

                if match_info:
                    matched_field, snippet, relevance = match_info
                    results.append(
                        SearchResult(
                            node_id=node_id,
                            triad=triad_name,
                            label=label,
                            node_type=node.get("type", "Unknown"),
                            confidence=confidence,
                            matched_field=matched_field,
                            snippet=snippet,
                            relevance_score=relevance,
                        )
                    )

        # Sort by relevance (highest first), then by confidence
        results.sort(key=lambda r: (-r.relevance_score, -r.confidence))
        return results

    def _get_confidence(self, node: dict[str, Any]) -> float:
        """Extract confidence value from node, handling various formats.

        Args:
            node: Node dictionary

        Returns:
            Confidence value as float (0.0 if missing/invalid)
        """
        conf = node.get("confidence", 0.0)
        try:
            return float(conf)
        except (ValueError, TypeError):
            return 0.0

    def _find_best_match(
        self, query: str, node_id: str, label: str, description: str
    ) -> tuple[str, str, float] | None:
        """Find best match in node fields and return details.

        Args:
            query: Lowercase query string
            node_id: Node ID
            label: Node label
            description: Node description

        Returns:
            Tuple of (field_name, snippet, relevance_score) or None if no match
        """
        # Check label (highest priority)
        if query in label.lower():
            snippet = self._create_snippet(label, query, max_len=config.SEARCH_SNIPPET_LENGTH_LABEL)
            return ("label", snippet, config.RELEVANCE_SCORE_LABEL_MATCH)

        # Check description (medium priority)
        if query in description.lower():
            snippet = self._create_snippet(description, query, max_len=config.SEARCH_SNIPPET_LENGTH_DESCRIPTION)
            return ("description", snippet, config.RELEVANCE_SCORE_DESCRIPTION_MATCH)

        # Check ID (lowest priority)
        if query in node_id.lower():
            snippet = node_id
            return ("id", snippet, config.RELEVANCE_SCORE_ID_MATCH)

        return None

    def _create_snippet(self, text: str, query: str, max_len: int = 100) -> str:
        """Create a context snippet showing the query match.

        Args:
            text: Full text containing the match
            query: Query string (lowercase)
            max_len: Maximum snippet length

        Returns:
            Snippet string with match context
        """
        text_lower = text.lower()
        pos = text_lower.find(query)

        if pos == -1:
            # No match (shouldn't happen, but be safe)
            return text[:max_len] + ("..." if len(text) > max_len else "")

        # Calculate snippet window
        half_window = (max_len - len(query)) // 2
        start = max(0, pos - half_window)
        end = min(len(text), pos + len(query) + half_window)

        snippet = text[start:end]

        # Add ellipsis if truncated
        if start > 0:
            snippet = "..." + snippet
        if end < len(text):
            snippet = snippet + "..."

        return snippet
