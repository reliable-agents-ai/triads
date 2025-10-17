# Knowledge Graph CLI Commands

Browse and search knowledge graphs stored in `.claude/graphs/`.

## Commands

### `/knowledge-status [triad]`
Show status of knowledge graphs.

**Usage:**
```python
from triads.km.graph_access import get_status

# All graphs
print(get_status())

# Single triad
print(get_status('design'))
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
from triads.km.graph_access import search_knowledge

# Basic search
print(search_knowledge("OAuth"))

# With filters
print(search_knowledge(
    "auth",
    triad="design",           # Search only design graph
    node_type="Decision",     # Filter by type
    min_confidence=0.85       # High confidence only
))
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
from triads.km.graph_access import show_node

# Search all triads
print(show_node("auth_decision"))

# Search specific triad
print(show_node("auth_decision", triad="design"))
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
from triads.km.graph_access import get_help
print(get_help())
```

---

## Examples

### Find all OAuth-related decisions
```python
from triads.km.graph_access import search_knowledge
print(search_knowledge("OAuth", node_type="Decision"))
```

### Check design graph status
```python
from triads.km.graph_access import get_status
print(get_status("design"))
```

### View specific node details
```python
from triads.km.graph_access import show_node
print(show_node("auth_decision", triad="design"))
```

### Find low-confidence nodes
```python
from triads.km.graph_access import search_knowledge
# Search for nodes that need verification (sorted by confidence)
print(search_knowledge("", min_confidence=0.0))
```

---

## Node Types

Knowledge graphs contain different types of nodes:

- **Entity**: Concrete things (libraries, tools, systems)
- **Concept**: Abstract ideas or principles
- **Decision**: Architectural or design decisions (see ADRs)
- **Finding**: Research results or discoveries
- **Uncertainty**: Known unknowns requiring investigation

---

## Troubleshooting

### "Graph not found"
- Check available graphs: `get_status()`
- Verify triad name spelling
- Remember: triad names are lowercase with hyphens (e.g., `garden-tending`)

### "Node not found"
- Use search first: `search_knowledge("partial_id")`
- Check if node exists: `get_status(triad)`
- Node IDs are unique within a triad but may not be unique across triads

### "Ambiguous node ID"
- Node exists in multiple triads
- Specify triad: `show_node(node_id, triad="design")`
- Use search to see all occurrences: `search_knowledge(node_id)`

### No search results
- Try broader search terms
- Remove filters (triad, type, confidence)
- Check graph has content: `get_status()`
- Search is case-insensitive substring match

---

## Tips

1. **Start with status**: See what graphs exist and their size
2. **Search broadly**: Use short, common terms (e.g., "auth" not "authentication")
3. **Filter progressively**: Add filters to narrow results
4. **Use context snippets**: Match snippets show where query appears
5. **Follow relationships**: Node details show related nodes (edges)
6. **Confidence matters**: High confidence (>0.85) nodes are well-verified

---

## Architecture

Knowledge graphs are stored as NetworkX JSON files in `.claude/graphs/`:
- Format: `{triad}_graph.json` (e.g., `design_graph.json`)
- Structure: Nodes (entities) and Links (relationships)
- Updated: Agents add nodes during execution

For implementation details, see: `src/triads/km/graph_access.py`
