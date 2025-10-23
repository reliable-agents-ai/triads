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

from triads.km.schema_validator import ValidationError, validate_graph
from triads.utils.file_operations import atomic_write_json

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

    def __init__(self, graphs_dir: Path | None = None, max_backups: int = 5) -> None:
        """Initialize loader with optional custom graphs directory.

        Args:
            graphs_dir: Path to graphs directory. Defaults to .claude/graphs/
            max_backups: Maximum number of backups to keep per graph (default: 5)
        """
        self._cache: dict[str, dict[str, Any]] = {}
        self._graphs_dir = graphs_dir or Path(".claude/graphs")
        self._max_backups = max_backups

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

    def load_graph(self, triad: str, auto_restore: bool = False) -> dict[str, Any] | None:
        """Load single graph with caching. Return None if not found.

        Security:
            - Validates triad name (no path traversal)
            - Safe JSON parsing with error handling
            - Optional auto-restore from backup on corruption

        Args:
            triad: Triad name (e.g., 'design', 'implementation')
            auto_restore: If True, automatically restore from backup on corruption

        Returns:
            Graph data dictionary, or None if not found or invalid

        Raises:
            InvalidTriadNameError: If triad name contains invalid characters
            Exception: If auto_restore=True but no backup exists

        Example:
            graph = loader.load_graph('design')
            if graph:
                nodes = graph.get('nodes', [])

            # With auto-restore
            graph = loader.load_graph('design', auto_restore=True)
        """
        # Import BackupManager here to avoid circular imports
        from triads.km.backup_manager import BackupManager

        # Security: Validate triad name
        if not self._is_valid_triad_name(triad):
            raise InvalidTriadNameError(triad)

        # Check cache first
        if triad in self._cache:
            return self._cache[triad]

        # Construct safe path
        graph_file = self._graphs_dir / f"{triad}_graph.json"

        # Security: Verify resolved path is still under graphs directory
        if not self._validate_graph_path(graph_file, triad, "load"):
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

            # Try auto-restore if requested
            if auto_restore:
                backup_mgr = BackupManager(graphs_dir=self._graphs_dir)
                backups = backup_mgr.list_backups(triad)

                if not backups:
                    raise Exception(
                        f"Corrupted graph file with no backup available: {graph_file.name}"
                    )

                logger.info(
                    "Attempting auto-restore from backup",
                    extra={"triad": triad, "backup": backups[0]}
                )

                if backup_mgr.restore_latest(triad):
                    # Clear cache and retry load
                    if triad in self._cache:
                        del self._cache[triad]
                    # Recursive call without auto_restore to prevent infinite loop
                    return self.load_graph(triad, auto_restore=False)
                else:
                    raise Exception(f"Failed to restore from backup: {triad}")

            # P0: USER-VISIBLE ERROR MESSAGES (v0.8.0-alpha.7)
            # Print to stderr for immediate user feedback with actionable fix steps
            import sys

            if isinstance(e, json.JSONDecodeError):
                print(
                    f"\n⚠️  Corrupted Knowledge Graph Detected:\n"
                    f"   File: {graph_file.name}\n"
                    f"   Error: {e.msg} at line {e.lineno}, column {e.colno}\n"
                    f"\n"
                    f"   EMERGENCY BYPASS (if hook is blocking fixes):\n"
                    f"   export TRIADS_NO_BLOCK=1\n"
                    f"   # Then restart Claude Code\n"
                    f"\n"
                    f"   To fix the corrupted graph:\n"
                    f"   1. Validate JSON: python3 -m json.tool {graph_file}\n"
                    f"   2. Or delete to regenerate: rm {graph_file}\n"
                    f"\n"
                    f"   Hook will continue with other valid graphs.\n",
                    file=sys.stderr
                )
            elif isinstance(e, (OSError, UnicodeDecodeError)):
                print(
                    f"\n⚠️  Failed to Read Knowledge Graph:\n"
                    f"   File: {graph_file.name}\n"
                    f"   Error: {type(e).__name__}: {str(e)}\n"
                    f"\n"
                    f"   Check file permissions and encoding.\n"
                    f"   Hook will continue with other valid graphs.\n",
                    file=sys.stderr
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

    def save_graph(self, triad: str, graph_data: dict[str, Any], max_backups: int | None = None) -> bool:
        """Save graph data using atomic file operations with locking.

        Uses atomic_write_json to prevent corruption from concurrent writes
        and crashes during write operations. Creates backup before write.

        Security:
            - Validates triad name (no path traversal)
            - Uses atomic writes with file locking
            - Auto-backup before writes
            - Auto-restore on failure

        Args:
            triad: Triad name (e.g., 'design', 'implementation')
            graph_data: Graph data dictionary to save

        Returns:
            True on success, False on failure

        Raises:
            InvalidTriadNameError: If triad name contains invalid characters

        Example:
            graph_data = {"nodes": [], "edges": []}
            success = loader.save_graph('design', graph_data)
            if success:
                print("Graph saved successfully")
        """
        # Import BackupManager here to avoid circular imports
        from triads.km.backup_manager import BackupManager

        # Security: Validate triad name
        if not self._is_valid_triad_name(triad):
            raise InvalidTriadNameError(triad)

        # Construct safe path
        graph_file = self._graphs_dir / f"{triad}_graph.json"

        # Security: Verify resolved path is still under graphs directory
        if not self._validate_graph_path(graph_file, triad, "save"):
            return False

        # Validate graph schema before saving
        try:
            validate_graph(graph_data)
        except ValidationError as e:
            logger.error(
                f"Graph validation failed: {e.message}",
                extra={
                    "triad": triad,
                    "field": e.field,
                    "error": e.message,
                },
            )
            return False

        # Create backup before write (if file exists)
        # Use parameter if provided, else load from config, else use instance default
        if max_backups is not None:
            effective_max = max_backups
        else:
            effective_max = BackupManager.load_config(self._graphs_dir)

        backup_mgr = BackupManager(graphs_dir=self._graphs_dir, max_backups=effective_max)
        backup_created = backup_mgr.create_backup(triad)

        # Save using atomic write with file locking
        try:
            atomic_write_json(graph_file, graph_data, lock=True, indent=2)
            # Update cache with new data
            self._cache[triad] = graph_data

            # Prune old backups after successful write
            if backup_created:
                backup_mgr.prune_backups(triad, keep=effective_max)

            return True

        except (OSError, IOError) as e:
            logger.error(
                f"Failed to save graph: {type(e).__name__}",
                extra={
                    "triad": triad,
                    "error": str(e),
                    "file": str(graph_file),
                },
            )

            # Try to restore from backup on failure
            if backup_created:
                logger.info(
                    "Attempting to restore from backup after write failure",
                    extra={"triad": triad}
                )
                backup_mgr.restore_latest(triad)

            return False

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

    def _validate_graph_path(
        self, graph_file: Path, triad: str, operation: str
    ) -> bool:
        """Validate graph file path to prevent path traversal attacks.

        Security: Ensures resolved path stays within graphs directory.

        Args:
            graph_file: Path to validate
            triad: Triad name for logging context
            operation: Operation name for logging ("load" or "save")

        Returns:
            True if path is valid and safe, False otherwise
        """
        try:
            resolved = graph_file.resolve()
            graphs_resolved = self._graphs_dir.resolve()
            if not str(resolved).startswith(str(graphs_resolved)):
                # Path traversal attempt detected
                logger.warning(
                    f"Path traversal attempt blocked during {operation}",
                    extra={
                        "triad": triad,
                        "requested_path": str(graph_file),
                        "operation": operation,
                    },
                )
                return False
        except (OSError, RuntimeError) as e:
            logger.warning(
                f"Failed to resolve graph path during {operation}: {type(e).__name__}",
                extra={"triad": triad, "error": str(e), "operation": operation},
            )
            return False

        return True

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
