"""Graph loading and caching functionality.

DEPRECATED: This module has been refactored into triads.tools.knowledge.repository
as part of the DDD architecture consolidation.

New location: triads.tools.knowledge.repository.FileSystemGraphRepository

This module provides backward compatibility shims. Please update imports to:
    from triads.tools.knowledge.repository import FileSystemGraphRepository

All functionality has been preserved:
- Graph caching
- Atomic writes with backup
- Security validations (path traversal, input validation)
- Auto-restore from backup
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any

# Import from new location
from triads.tools.knowledge.repository import (
    FileSystemGraphRepository as _NewFileSystemGraphRepository,
    GraphNotFoundError as _GraphNotFoundError,
    InvalidTriadNameError as _InvalidTriadNameError,
    AmbiguousNodeError as _AmbiguousNodeError,
)

# Import utilities for backward compatibility (tests may mock these)
from triads.utils.file_operations import atomic_write_json

# Show deprecation warning
warnings.warn(
    "triads.km.graph_access.loader is deprecated. "
    "Use triads.tools.knowledge.repository instead.",
    DeprecationWarning,
    stacklevel=2
)


# ============================================================================
# Backward Compatibility Aliases for Exceptions
# ============================================================================

# Alias old exception names to new location
AmbiguousNodeError = _AmbiguousNodeError
GraphNotFoundError = _GraphNotFoundError
InvalidTriadNameError = _InvalidTriadNameError


# ============================================================================
# GraphLoader: Backward Compatibility Wrapper
# ============================================================================


class GraphLoader(_NewFileSystemGraphRepository):
    """Lazy-loading graph manager with per-session caching.

    DEPRECATED: Use FileSystemGraphRepository from triads.tools.knowledge.repository instead.

    This class now inherits from FileSystemGraphRepository and delegates all functionality.
    Maintained for backward compatibility only.

    Example:
        # Old (deprecated):
        from triads.km.graph_access.loader import GraphLoader
        loader = GraphLoader()

        # New (preferred):
        from triads.tools.knowledge.repository import FileSystemGraphRepository
        repo = FileSystemGraphRepository()
    """

    def __init__(self, graphs_dir: Path | None = None, max_backups: int = 5) -> None:
        """Initialize loader with optional custom graphs directory.

        Args:
            graphs_dir: Path to graphs directory. Defaults to .claude/graphs/
            max_backups: Maximum number of backups to keep per graph (default: 5)
        """
        # Initialize parent (FileSystemGraphRepository)
        super().__init__(graphs_dir=graphs_dir, max_backups=max_backups)

        # Maintain backward compatibility for _graphs_dir attribute
        self._graphs_dir = self.graphs_dir

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
