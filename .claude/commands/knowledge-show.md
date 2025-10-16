# Knowledge Show Command

Display detailed information about a specific node in the knowledge graph.

## Usage

**Show node from any triad:**
```python
from triads.km.graph_access import show_node
print(show_node("auth_decision"))
```

**Show node from specific triad:**
```python
from triads.km.graph_access import show_node
print(show_node("auth_decision", triad="design"))
```

## Parameters

- **node_id** (required): Node identifier (exact match)
- **triad** (optional): Triad name to search in (if omitted, searches all triads)

## Output Format

```
# OAuth2 Industry Standard

**ID**: `oauth2_research`
**Triad**: default

## Attributes

**Type**: Finding
**Confidence**: 0.95

**Description**:
OAuth2 is widely adopted (GitHub, Google, Microsoft all use it)

**Evidence**:
RFC 6749, GitHub Auth docs, Google OAuth guides

**Created By**: research-agent
**Created**: 2025-10-16T11:10:04.903838

## Additional Properties

**alternatives**: ["OAuth1", "SAML", "OpenID Connect"]

## Relationships

**Outgoing** (2):
- implements → `oauth2_implementation`
- informs → `auth_decision`

**Incoming** (1):
- `oauth2_research_task` → produces
```

The output includes:
- **Attributes**: Core node data (type, confidence, description, evidence)
- **Metadata**: Created by, timestamps
- **Additional Properties**: Custom fields (JSON formatted for complex data)
- **Relationships**: Incoming and outgoing edges with relationship types

## Behavior

### Single Triad Search
When `triad` parameter is specified:
- Searches only that triad's graph
- Returns "not found" if node doesn't exist in that triad
- Faster (doesn't load other graphs)

### All Triads Search
When `triad` parameter is omitted:
- Searches all available triads
- Returns first match found
- Raises error if node exists in multiple triads (see Ambiguous Nodes)

### Ambiguous Nodes
If a node ID exists in multiple triads and you don't specify which:

```
**Ambiguous node ID 'test_entity'**

Found in multiple triads: default, test

Please specify triad:
- show_node('test_entity', triad='default')
- show_node('test_entity', triad='test')
```

## Examples

### View a decision node
```python
# Find decision first
print(search_knowledge("OAuth", node_type="Decision"))

# Then show details
print(show_node("auth_decision", triad="design"))
```

### Explore node relationships
```python
# Show a node
details = show_node("oauth2_research")

# From the output, note related nodes in "Relationships" section
# Then explore those nodes
print(show_node("oauth2_implementation"))
```

### Check node confidence
```python
# Quickly check if a node is well-verified
print(show_node("auth_decision", triad="design"))
# Look for Confidence score (>0.85 is well-verified)
```

## Finding Node IDs

If you don't know the exact node ID:

1. **Use search**: `search_knowledge("partial_name")`
2. **Check status**: `get_status(triad)` to see node counts
3. **Browse by type**: `search_knowledge("", node_type="Decision")`

Node IDs are shown in search results in backticks: `` `node_id` ``

## Tips

1. **Use search first**: Find nodes before showing details
2. **Specify triad**: Faster if you know which triad contains the node
3. **Follow relationships**: Use "Relationships" section to explore connected nodes
4. **Check evidence**: Well-documented nodes have evidence fields
5. **Review confidence**: High confidence (>0.85) = well-verified

## Common Errors

### "Node not found"
- Double-check node ID spelling (case-sensitive)
- Use search: `search_knowledge("partial_id")`
- Check if triad is correct: `get_status(triad)`

### "Ambiguous node ID"
- Node exists in multiple triads
- Specify which triad: `show_node(node_id, triad="design")`
- Or use search to see all: `search_knowledge(node_id)`

### "Graph not found"
- Triad name is incorrect
- Check available triads: `get_status()`
- Remember: use hyphenated names (e.g., `garden-tending`)

## See Also

- `/knowledge-search` - Find nodes before showing details
- `/knowledge-status` - Check available graphs
- `/knowledge-help` - Full command reference
