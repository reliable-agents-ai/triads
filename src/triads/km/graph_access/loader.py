"""Graph loading and caching functionality.

This module handles:
- GraphCache class for caching loaded graphs
- load_graph() for reading graph files
- save_graph() for writing graph files
- Graph file discovery and validation

Security:
- Path traversal protection via strict filename validation
- JSON parsing with error handling
- All graph data treated as plain text (no eval/exec)

Performance:
- Per-session caching (graphs loaded once)
- Lazy loading (load on first access)
- Fast lookups via in-memory cache
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any

# Initialize module logger
logger = logging.getLogger(__name__)


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
                logger.warning(
                    "Path traversal attempt blocked",
                    extra={"triad": triad, "requested_path": str(graph_file)}
                )
                return None
        except (OSError, RuntimeError) as e:
            logger.warning(
                f"Failed to resolve graph path: {type(e).__name__}",
                extra={"triad": triad, "error": str(e)}
            )
            return None

        # Load and parse JSON
        if not graph_file.exists():
            return None

        try:
            with open(graph_file, "r", encoding="utf-8") as f:
                graph_data = json.load(f)

            # Validate basic structure
            if not isinstance(graph_data, dict):
                logger.warning(
                    "Invalid graph structure: expected dict",
                    extra={"triad": triad, "type": type(graph_data).__name__}
                )
                return None

            # Cache and return
            self._cache[triad] = graph_data
            return graph_data

        except (json.JSONDecodeError, OSError, UnicodeDecodeError) as e:
            # Corrupted or unreadable file
            logger.warning(
                f"Failed to load graph: {type(e).__name__}",
                extra={"triad": triad, "error": str(e), "file": str(graph_file)}
            )
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
                logger.debug(
                    "Node search failed: graph not found",
                    extra={"node_id": node_id, "triad": triad}
                )
                return None

            nodes = graph.get("nodes", [])
            for node in nodes:
                if node.get("id") == node_id:
                    return (node, triad)

            logger.debug(
                "Node not found in triad",
                extra={"node_id": node_id, "triad": triad, "nodes_count": len(nodes)}
            )
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
            logger.debug(
                "Node not found in any triad",
                extra={"node_id": node_id, "triads_searched": len(self.list_triads())}
            )
            return None

        if len(found_nodes) > 1:
            # Ambiguous - node exists in multiple triads
            triads = [t for _, t in found_nodes]
            logger.info(
                "Ambiguous node ID: found in multiple triads",
                extra={"node_id": node_id, "triads": triads}
            )
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
