"""CLI command functions for graph access.

This module handles:
- get_status() - Graph status info
- search_knowledge() - Search across graphs
- show_node() - Display node details
- get_help() - Help documentation
- CLI convenience functions (singleton instances)
"""

from __future__ import annotations

from triads.km.graph_access.formatter import GraphFormatter
from triads.km.graph_access.loader import (
    AmbiguousNodeError,
    GraphLoader,
    InvalidTriadNameError,
)
from triads.km.graph_access.searcher import GraphNotFoundError, GraphSearcher

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
