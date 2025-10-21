"""Knowledge graph access utilities for CLI commands.

This package provides lazy-loading graph management, search functionality,
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
    from triads.km.graph_access import get_status
    status = get_status()
    print(status)

    # Search across all graphs
    from triads.km.graph_access import search_knowledge
    results = search_knowledge("OAuth", min_confidence=0.85)
    print(results)

    # Show specific node
    from triads.km.graph_access import show_node
    node_info = show_node("auth_decision", triad="design")
    print(node_info)
"""

# Import exceptions from loader
from triads.km.graph_access.loader import (
    AmbiguousNodeError,
    GraphLoader,
    GraphNotFoundError,
    InvalidTriadNameError,
)

# Import formatter
from triads.km.graph_access.formatter import GraphFormatter

# Import searcher and data classes
from triads.km.graph_access.searcher import GraphSearcher, SearchResult

# Import convenience functions and expose singleton instances for testing
from triads.km.graph_access import commands
from triads.km.graph_access.commands import (
    _get_loader,
    _get_searcher,
    get_help,
    get_status,
    search_knowledge,
    show_node,
)

# Expose singleton instances for testing (backward compatibility)
# Tests need to access _loader and _searcher to reset them between test runs
def __getattr__(name):
    """Provide backward-compatible access to singleton instances in commands module."""
    if name == "_loader":
        return commands._loader
    elif name == "_searcher":
        return commands._searcher
    elif name == "_formatter":
        return commands._formatter
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

def __setattr__(name, value):
    """Allow tests to reset singleton instances."""
    if name == "_loader":
        commands._loader = value
    elif name == "_searcher":
        commands._searcher = value
    elif name == "_formatter":
        commands._formatter = value
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    # Exceptions
    "AmbiguousNodeError",
    "GraphNotFoundError",
    "InvalidTriadNameError",
    # Classes
    "GraphLoader",
    "GraphSearcher",
    "GraphFormatter",
    # Data classes
    "SearchResult",
    # Convenience functions (CLI commands)
    "get_status",
    "search_knowledge",
    "show_node",
    "get_help",
]
