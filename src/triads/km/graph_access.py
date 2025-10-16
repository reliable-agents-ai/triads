"""Knowledge graph access utilities for CLI commands.

This module provides lazy-loading graph management, search functionality,
and formatted output for browsing knowledge graphs in Claude Code.

Security:
- Path traversal protection via strict filename validation
- JSON parsing with error handling
- All graph data treated as plain text (no eval/exec)

Performance:
- Per-session caching (graphs loaded once)
- Lazy loading (load on first access)
- Typical search: < 100ms for 10-100 node graphs

Usage:
    # Get status of all graphs
    status = get_status()
    print(status)

    # Search across all graphs
    results = search_knowledge("OAuth", min_confidence=0.85)
    print(results)

    # Show specific node
    node_info = show_node("auth_decision", triad="design")
    print(node_info)
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


# ============================================================================
# Exceptions
# ============================================================================


class AmbiguousNodeError(Exception):
    """Raised when a node ID exists in multiple triads without clarification."""

    def __init__(self, node_id: str, triads: list[str]) -> None:
        self.node_id = node_id
        self.triads = triads
        super().__init__(
            f"Node '{node_id}' found in multiple triads: {', '.join(triads)}. "
            f"Please specify triad parameter."
        )


class GraphNotFoundError(Exception):
    """Raised when a requested graph file doesn't exist."""

    def __init__(self, triad: str, available: list[str]) -> None:
        self.triad = triad
        self.available = available
        available_str = ", ".join(sorted(available)) if available else "none"
        super().__init__(
            f"Graph '{triad}' not found. Available graphs: {available_str}"
        )


class InvalidTriadNameError(Exception):
    """Raised when a triad name contains invalid characters."""

    def __init__(self, triad: str) -> None:
        self.triad = triad
        super().__init__(
            f"Invalid triad name '{triad}'. "
            f"Only alphanumeric characters, underscores, and hyphens are allowed."
        )


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
# GraphLoader: Lazy-loading graph manager with caching
# ============================================================================


class GraphLoader:
    """Lazy-loading graph manager with per-session caching.

    Provides secure, efficient access to knowledge graphs stored as
    NetworkX JSON files in .claude/graphs/ directory.

    Security:
        - Validates all triad names (alphanumeric + _- only)
        - Prevents path traversal attacks
        - Safe JSON parsing with error handling

    Performance:
        - Per-session caching (load once, reuse)
        - Lazy loading (only load when needed)
        - Fast lookups via in-memory cache

    Example:
        loader = GraphLoader()
        triads = loader.list_triads()  # ['design', 'implementation']
        graph = loader.load_graph('design')  # Load with caching
        node, triad = loader.get_node('auth_decision')  # Find node
    """

    def __init__(self, graphs_dir: Path | None = None) -> None:
        """Initialize loader with optional custom graphs directory.

        Args:
            graphs_dir: Path to graphs directory. Defaults to .claude/graphs/
        """
        self._cache: dict[str, dict[str, Any]] = {}
        self._graphs_dir = graphs_dir or Path(".claude/graphs")

    def list_triads(self) -> list[str]:
        """Return sorted list of available triad names from *_graph.json files.

        Scans the graphs directory for files matching *_graph.json pattern
        and extracts the triad name (prefix before _graph.json).

        Returns:
            Sorted list of triad names (e.g., ['design', 'implementation'])

        Example:
            loader = GraphLoader()
            triads = loader.list_triads()
            # ['deployment', 'design', 'implementation']
        """
        if not self._graphs_dir.exists():
            return []

        triads = []
        for path in self._graphs_dir.glob("*_graph.json"):
            # Extract triad name from filename (e.g., "design_graph.json" -> "design")
            triad_name = path.stem.replace("_graph", "")
            # Skip invalid names (e.g., template files)
            if self._is_valid_triad_name(triad_name):
                triads.append(triad_name)

        return sorted(triads)

    def load_graph(self, triad: str) -> dict[str, Any] | None:
        """Load single graph with caching. Return None if not found.

        Security:
            - Validates triad name (no path traversal)
            - Safe JSON parsing with error handling

        Args:
            triad: Triad name (e.g., 'design', 'implementation')

        Returns:
            Graph data dictionary, or None if not found or invalid

        Raises:
            InvalidTriadNameError: If triad name contains invalid characters

        Example:
            graph = loader.load_graph('design')
            if graph:
                nodes = graph.get('nodes', [])
        """
        # Security: Validate triad name
        if not self._is_valid_triad_name(triad):
            raise InvalidTriadNameError(triad)

        # Check cache first
        if triad in self._cache:
            return self._cache[triad]

        # Construct safe path
        graph_file = self._graphs_dir / f"{triad}_graph.json"

        # Security: Verify resolved path is still under graphs directory
        try:
            resolved = graph_file.resolve()
            graphs_resolved = self._graphs_dir.resolve()
            if not str(resolved).startswith(str(graphs_resolved)):
                # Path traversal attempt detected
                return None
        except (OSError, RuntimeError):
            return None

        # Load and parse JSON
        if not graph_file.exists():
            return None

        try:
            with open(graph_file, "r", encoding="utf-8") as f:
                graph_data = json.load(f)

            # Validate basic structure
            if not isinstance(graph_data, dict):
                return None

            # Cache and return
            self._cache[triad] = graph_data
            return graph_data

        except (json.JSONDecodeError, OSError, UnicodeDecodeError):
            # Corrupted or unreadable file
            return None

    def load_all_graphs(self) -> dict[str, dict[str, Any]]:
        """Load all graphs (lazy, cached). Return {triad_name: graph_data}.

        Returns:
            Dictionary mapping triad names to their graph data.
            Empty dict if no graphs found.

        Example:
            all_graphs = loader.load_all_graphs()
            for triad, graph in all_graphs.items():
                print(f"{triad}: {len(graph.get('nodes', []))} nodes")
        """
        graphs = {}
        for triad in self.list_triads():
            graph = self.load_graph(triad)
            if graph:
                graphs[triad] = graph
        return graphs

    def get_node(
        self, node_id: str, triad: str | None = None
    ) -> tuple[dict[str, Any], str] | None:
        """Find node by ID. Return (node_data, triad_name) or None.

        If triad is specified, searches only that graph.
        Otherwise searches all graphs.

        Args:
            node_id: Node identifier to find
            triad: Optional triad name to limit search

        Returns:
            Tuple of (node_dict, triad_name) if found, None otherwise

        Raises:
            AmbiguousNodeError: If node exists in multiple triads without
                clarification

        Example:
            # Search specific triad
            node, triad = loader.get_node('auth_decision', triad='design')

            # Search all triads
            try:
                node, triad = loader.get_node('auth_decision')
            except AmbiguousNodeError as e:
                print(f"Found in: {e.triads}")
        """
        if triad:
            # Search specific triad only
            graph = self.load_graph(triad)
            if not graph:
                return None

            nodes = graph.get("nodes", [])
            for node in nodes:
                if node.get("id") == node_id:
                    return (node, triad)
            return None

        # Search all triads
        found_nodes: list[tuple[dict[str, Any], str]] = []

        for triad_name in self.list_triads():
            graph = self.load_graph(triad_name)
            if not graph:
                continue

            nodes = graph.get("nodes", [])
            for node in nodes:
                if node.get("id") == node_id:
                    found_nodes.append((node, triad_name))

        if not found_nodes:
            return None

        if len(found_nodes) > 1:
            # Ambiguous - node exists in multiple triads
            triads = [t for _, t in found_nodes]
            raise AmbiguousNodeError(node_id, triads)

        return found_nodes[0]

    def _is_valid_triad_name(self, triad: str) -> bool:
        """Validate triad name contains only safe characters.

        Security: Prevents path traversal and injection attacks.

        Args:
            triad: Triad name to validate

        Returns:
            True if name is valid, False otherwise
        """
        # Only allow alphanumeric, underscore, and hyphen
        # No dots (.), slashes (/, \), or other special characters
        pattern = r"^[a-zA-Z0-9_-]+$"
        return bool(re.match(pattern, triad))


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
                    raise GraphNotFoundError(triad, available)
                graphs_to_search = {triad: graph}
            except InvalidTriadNameError:
                available = self.loader.list_triads()
                raise GraphNotFoundError(triad, available)
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
            snippet = self._create_snippet(label, query, max_len=100)
            return ("label", snippet, 1.0)

        # Check description (medium priority)
        if query in description.lower():
            snippet = self._create_snippet(description, query, max_len=150)
            return ("description", snippet, 0.7)

        # Check ID (lowest priority)
        if query in node_id.lower():
            snippet = node_id
            return ("id", snippet, 0.5)

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


# ============================================================================
# GraphFormatter: Markdown output formatting
# ============================================================================


class GraphFormatter:
    """Markdown formatters for command output.

    Provides consistent, readable formatting for all knowledge graph
    CLI command outputs.

    Example:
        formatter = GraphFormatter()
        status = formatter.format_status(graphs)
        print(status)
    """

    @staticmethod
    def format_status(
        graphs: dict[str, dict[str, Any]], triad: str | None = None
    ) -> str:
        """Format /knowledge-status output as markdown table.

        Args:
            graphs: Dictionary of {triad_name: graph_data}
            triad: Optional triad name for single-triad view

        Returns:
            Markdown formatted status report

        Example:
            status = formatter.format_status(all_graphs)
            # Returns table with Triad | Nodes | Edges | Types | Avg Confidence
        """
        if not graphs:
            return "**No knowledge graphs found**\n\nNo graphs exist in `.claude/graphs/` directory."

        # Filter to single triad if specified
        if triad:
            if triad not in graphs:
                available = ", ".join(sorted(graphs.keys()))
                return f"**Graph '{triad}' not found**\n\nAvailable graphs: {available}"
            graphs = {triad: graphs[triad]}

        # Calculate summary statistics
        total_nodes = sum(len(g.get("nodes", [])) for g in graphs.values())
        total_edges = sum(len(g.get("links", [])) for g in graphs.values())

        lines = ["# Knowledge Graph Status\n"]
        lines.append(f"**Graphs**: {len(graphs)}")
        lines.append(f"**Total Nodes**: {total_nodes}")
        lines.append(f"**Total Edges**: {total_edges}\n")

        # Table header
        lines.append("| Triad | Nodes | Edges | Types | Avg Confidence |")
        lines.append("|-------|-------|-------|-------|----------------|")

        # Table rows
        for triad_name in sorted(graphs.keys()):
            graph = graphs[triad_name]
            nodes = graph.get("nodes", [])
            edges = graph.get("links", [])

            # Count node types
            types = set(n.get("type", "Unknown") for n in nodes)
            type_count = len(types)

            # Calculate average confidence
            confidences = []
            for node in nodes:
                try:
                    conf = float(node.get("confidence", 0))
                    confidences.append(conf)
                except (ValueError, TypeError):
                    pass

            avg_conf = sum(confidences) / len(confidences) if confidences else 0.0

            lines.append(
                f"| {triad_name} | {len(nodes)} | {len(edges)} | "
                f"{type_count} | {avg_conf:.2f} |"
            )

        # Add node type breakdown if single triad
        if triad and len(graphs) == 1:
            lines.append("\n## Node Type Breakdown\n")
            graph = list(graphs.values())[0]
            nodes = graph.get("nodes", [])

            # Count by type
            type_counts: dict[str, int] = {}
            for node in nodes:
                node_type = node.get("type", "Unknown")
                type_counts[node_type] = type_counts.get(node_type, 0) + 1

            for node_type in sorted(type_counts.keys()):
                count = type_counts[node_type]
                lines.append(f"- **{node_type}**: {count}")

        return "\n".join(lines)

    @staticmethod
    def format_search_results(
        results: list[SearchResult], query: str
    ) -> str:
        """Format /knowledge-search output.

        Args:
            results: List of SearchResult objects
            query: Original search query

        Returns:
            Markdown formatted search results

        Example:
            output = formatter.format_search_results(results, "OAuth")
        """
        if not results:
            return (
                f"**No results found for: '{query}'**\n\n"
                f"**Suggestions:**\n"
                f"- Try a broader search term\n"
                f"- Check available triads with `/knowledge-status`\n"
                f"- Search without filters (triad, type, confidence)\n"
            )

        lines = [f"# Search Results: '{query}'\n"]
        lines.append(f"**Found**: {len(results)} nodes\n")

        # Group by triad
        by_triad: dict[str, list[SearchResult]] = {}
        for result in results:
            if result.triad not in by_triad:
                by_triad[result.triad] = []
            by_triad[result.triad].append(result)

        # Format each triad's results
        for triad_name in sorted(by_triad.keys()):
            triad_results = by_triad[triad_name]
            lines.append(f"## {triad_name} ({len(triad_results)} results)\n")

            for result in triad_results:
                # Node header
                lines.append(
                    f"### {result.label} (`{result.node_id}`)\n"
                )

                # Metadata
                lines.append(
                    f"**Type**: {result.node_type} | "
                    f"**Confidence**: {result.confidence:.2f} | "
                    f"**Match**: {result.matched_field}\n"
                )

                # Snippet
                lines.append(f"> {result.snippet}\n")

        return "\n".join(lines)

    @staticmethod
    def format_node_details(
        node: dict[str, Any], triad: str, graph: dict[str, Any]
    ) -> str:
        """Format /knowledge-show output.

        Args:
            node: Node dictionary
            triad: Triad name
            graph: Full graph data (for relationships)

        Returns:
            Markdown formatted node details

        Example:
            details = formatter.format_node_details(node, 'design', graph)
        """
        node_id = node.get("id", "Unknown")
        label = node.get("label", node_id)

        lines = [f"# {label}\n"]
        lines.append(f"**ID**: `{node_id}`")
        lines.append(f"**Triad**: {triad}\n")

        # Core attributes
        lines.append("## Attributes\n")

        # Type and confidence
        lines.append(f"**Type**: {node.get('type', 'Unknown')}")

        confidence = node.get("confidence", 0)
        try:
            conf_value = float(confidence)
            lines.append(f"**Confidence**: {conf_value:.2f}")
        except (ValueError, TypeError):
            lines.append(f"**Confidence**: {confidence}")

        # Description
        description = node.get("description")
        if description:
            lines.append(f"\n**Description**:\n{description}\n")

        # Evidence
        evidence = node.get("evidence")
        if evidence:
            lines.append(f"**Evidence**:\n{evidence}\n")

        # Created/Updated
        created_by = node.get("created_by")
        if created_by:
            lines.append(f"**Created By**: {created_by}")

        created_at = node.get("created_at")
        if created_at:
            lines.append(f"**Created**: {created_at}")

        updated_at = node.get("updated_at")
        if updated_at:
            lines.append(f"**Updated**: {updated_at}")

        # Additional properties (exclude standard ones)
        standard_keys = {
            "id",
            "label",
            "type",
            "description",
            "confidence",
            "evidence",
            "created_by",
            "created_at",
            "updated_at",
        }

        additional = {k: v for k, v in node.items() if k not in standard_keys}
        if additional:
            lines.append("\n## Additional Properties\n")
            for key, value in sorted(additional.items()):
                # Format value
                if isinstance(value, (list, dict)):
                    value_str = json.dumps(value, indent=2)
                    lines.append(f"**{key}**:\n```json\n{value_str}\n```")
                else:
                    lines.append(f"**{key}**: {value}")

        # Relationships (edges)
        edges = graph.get("links", [])
        outgoing = [e for e in edges if e.get("source") == node_id]
        incoming = [e for e in edges if e.get("target") == node_id]

        if outgoing or incoming:
            lines.append("\n## Relationships\n")

        if outgoing:
            lines.append(f"**Outgoing** ({len(outgoing)}):")
            for edge in outgoing:
                target = edge.get("target", "Unknown")
                rel_type = edge.get("key", "relates_to")
                lines.append(f"- {rel_type} → `{target}`")

        if incoming:
            lines.append(f"\n**Incoming** ({len(incoming)}):")
            for edge in incoming:
                source = edge.get("source", "Unknown")
                rel_type = edge.get("key", "relates_to")
                lines.append(f"- `{source}` → {rel_type}")

        return "\n".join(lines)


# ============================================================================
# Convenience Functions (for CLI commands)
# ============================================================================

# Singleton instances for caching across calls
_loader: GraphLoader | None = None
_searcher: GraphSearcher | None = None
_formatter: GraphFormatter = GraphFormatter()


def _get_loader() -> GraphLoader:
    """Get or create singleton GraphLoader instance."""
    global _loader
    if _loader is None:
        _loader = GraphLoader()
    return _loader


def _get_searcher() -> GraphSearcher:
    """Get or create singleton GraphSearcher instance."""
    global _searcher
    if _searcher is None:
        _searcher = GraphSearcher(_get_loader())
    return _searcher


def get_status(triad: str | None = None) -> str:
    """Get knowledge graph status (for /knowledge-status command).

    Args:
        triad: Optional triad name for single-triad view

    Returns:
        Markdown formatted status report

    Example:
        # All graphs
        print(get_status())

        # Single triad
        print(get_status('design'))
    """
    loader = _get_loader()

    if triad:
        try:
            graph = loader.load_graph(triad)
            if not graph:
                available = loader.list_triads()
                available_str = ", ".join(sorted(available)) if available else "none"
                return (
                    f"**Graph '{triad}' not found**\n\n"
                    f"Available graphs: {available_str}"
                )
            graphs = {triad: graph}
        except InvalidTriadNameError:
            available = loader.list_triads()
            available_str = ", ".join(sorted(available)) if available else "none"
            return (
                f"**Invalid triad name '{triad}'**\n\n"
                f"Only alphanumeric characters, underscores, and hyphens allowed.\n"
                f"Available graphs: {available_str}"
            )
    else:
        graphs = loader.load_all_graphs()

    return _formatter.format_status(graphs, triad)


def search_knowledge(
    query: str,
    triad: str | None = None,
    node_type: str | None = None,
    min_confidence: float | None = None,
) -> str:
    """Search knowledge graphs (for /knowledge-search command).

    Args:
        query: Search query string
        triad: Optional triad name to limit search
        node_type: Optional node type filter
        min_confidence: Optional minimum confidence (0.0-1.0)

    Returns:
        Markdown formatted search results

    Example:
        # Basic search
        print(search_knowledge("OAuth"))

        # Filtered search
        print(search_knowledge(
            "auth",
            triad="design",
            node_type="Decision",
            min_confidence=0.85
        ))
    """
    searcher = _get_searcher()

    try:
        results = searcher.search(query, triad, node_type, min_confidence)
        return _formatter.format_search_results(results, query)
    except GraphNotFoundError as e:
        available_str = ", ".join(sorted(e.available)) if e.available else "none"
        return (
            f"**Graph '{e.triad}' not found**\n\n" f"Available graphs: {available_str}"
        )
    except InvalidTriadNameError as e:
        loader = _get_loader()
        available = loader.list_triads()
        available_str = ", ".join(sorted(available)) if available else "none"
        return (
            f"**Invalid triad name '{e.triad}'**\n\n"
            f"Only alphanumeric characters, underscores, and hyphens allowed.\n"
            f"Available graphs: {available_str}"
        )


def show_node(node_id: str, triad: str | None = None) -> str:
    """Show detailed node information (for /knowledge-show command).

    Args:
        node_id: Node identifier
        triad: Optional triad name to limit search

    Returns:
        Markdown formatted node details

    Example:
        # Search all triads
        print(show_node("auth_decision"))

        # Search specific triad
        print(show_node("auth_decision", triad="design"))
    """
    loader = _get_loader()

    try:
        result = loader.get_node(node_id, triad)
        if not result:
            if triad:
                return f"**Node '{node_id}' not found in '{triad}' graph**"
            else:
                available = loader.list_triads()
                available_str = ", ".join(sorted(available)) if available else "none"
                return (
                    f"**Node '{node_id}' not found**\n\n"
                    f"Available triads: {available_str}\n"
                    f"Use `/knowledge-search {node_id}` to search"
                )

        node, triad_name = result
        graph = loader.load_graph(triad_name)
        if not graph:
            return f"**Error loading graph '{triad_name}'**"

        return _formatter.format_node_details(node, triad_name, graph)

    except AmbiguousNodeError as e:
        triads_str = ", ".join(sorted(e.triads))
        return (
            f"**Ambiguous node ID '{e.node_id}'**\n\n"
            f"Found in multiple triads: {triads_str}\n\n"
            f"Please specify triad:\n"
            + "\n".join(f"- `show_node('{node_id}', triad='{t}')`" for t in e.triads)
        )
    except InvalidTriadNameError as e:
        loader = _get_loader()
        available = loader.list_triads()
        available_str = ", ".join(sorted(available)) if available else "none"
        return (
            f"**Invalid triad name '{e.triad}'**\n\n"
            f"Only alphanumeric characters, underscores, and hyphens allowed.\n"
            f"Available graphs: {available_str}"
        )


def get_help() -> str:
    """Get help information (for /knowledge-help command).

    Returns:
        Markdown formatted help text
    """
    return """# Knowledge Graph CLI Commands

Browse and search knowledge graphs stored in `.claude/graphs/`.

## Commands

### `/knowledge-status [triad]`
Show status of knowledge graphs.

**Usage:**
```python
# All graphs
get_status()

# Single triad
get_status('design')
```

**Output:**
- Graph count and statistics
- Table: Triad | Nodes | Edges | Types | Avg Confidence
- Node type breakdown (single triad view)

---

### `/knowledge-search <query> [options]`
Search across knowledge graphs.

**Usage:**
```python
# Basic search
search_knowledge("OAuth")

# With filters
search_knowledge(
    "auth",
    triad="design",           # Search only design graph
    node_type="Decision",     # Filter by type
    min_confidence=0.85       # High confidence only
)
```

**Search Fields:**
- Node labels (highest priority)
- Descriptions (medium priority)
- Node IDs (lowest priority)

**Output:**
- Results grouped by triad
- Match snippets with context
- Metadata (type, confidence, matched field)

---

### `/knowledge-show <node_id> [triad]`
Show detailed node information.

**Usage:**
```python
# Search all triads
show_node("auth_decision")

# Search specific triad
show_node("auth_decision", triad="design")
```

**Output:**
- All node attributes
- Relationships (incoming/outgoing edges)
- Additional properties (JSON formatted)

---

### `/knowledge-help`
Show this help message.

**Usage:**
```python
get_help()
```

---

## Examples

### Find all OAuth-related decisions
```python
search_knowledge("OAuth", node_type="Decision")
```

### Check design graph status
```python
get_status("design")
```

### View specific node details
```python
show_node("auth_decision", triad="design")
```

### Find low-confidence nodes
```python
# Search for nodes that need verification
search_knowledge("", min_confidence=0.0)  # All nodes, sorted by confidence
```

---

## Troubleshooting

**"Graph not found"**
- Check available graphs: `get_status()`
- Verify triad name spelling

**"Node not found"**
- Use search first: `search_knowledge("partial_id")`
- Check if node exists: `get_status(triad)`

**"Ambiguous node ID"**
- Node exists in multiple triads
- Specify triad: `show_node(node_id, triad="design")`

**No search results**
- Try broader search terms
- Remove filters (triad, type, confidence)
- Check graph has content: `get_status()`

---

## Tips

1. **Start with status**: See what graphs exist
2. **Search broadly**: Use short, common terms
3. **Filter progressively**: Add filters to narrow results
4. **Use context snippets**: Match snippets show where query appears
5. **Follow relationships**: Node details show related nodes

---

For more information, see: `docs/km-access-commands.md`
"""
