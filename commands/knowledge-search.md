# Knowledge Search Command

Search across knowledge graphs with optional filters.

## Usage

**Basic search:**
```python
from triads.km.graph_access import search_knowledge
print(search_knowledge("OAuth"))
```

**Search with filters:**
```python
from triads.km.graph_access import search_knowledge

# Search only design graph
print(search_knowledge("auth", triad="design"))

# Filter by node type
print(search_knowledge("OAuth", node_type="Decision"))

# High confidence only
print(search_knowledge("security", min_confidence=0.85))

# Combine all filters
print(search_knowledge(
    "authentication",
    triad="design",
    node_type="Decision",
    min_confidence=0.90
))
```

## Parameters

- **query** (required): Search string (case-insensitive)
- **triad** (optional): Limit search to specific triad graph
- **node_type** (optional): Filter by type (Entity, Concept, Decision, Finding, Uncertainty)
- **min_confidence** (optional): Minimum confidence score (0.0-1.0)

## Search Behavior

### Fields Searched
1. **Label** (highest priority) - Node's human-readable name
2. **Description** (medium priority) - Detailed description
3. **ID** (lowest priority) - Node identifier

### Result Ranking
Results are sorted by:
1. **Relevance** (label match > description match > ID match)
2. **Confidence** (higher confidence first)

### Matching
- Case-insensitive substring matching
- Matches anywhere in the field (not just beginning)
- All filters must match (AND logic)

## Output Format

```
# Search Results: 'OAuth'

Found: 2 nodes

## default (2 results)

### OAuth2 Industry Standard (`oauth2_research`)
**Type**: Finding | **Confidence**: 0.95 | **Match**: label
> OAuth2 Industry Standard

### Python OAuth2 Libraries (`oauth2_libraries`)
**Type**: Entity | **Confidence**: 0.90 | **Match**: label
> Python OAuth2 Libraries
```

Results are grouped by triad, showing:
- Node label and ID
- Node type and confidence
- Which field matched (label/description/id)
- Context snippet with the match

## Examples

### Find all authentication-related nodes
```python
print(search_knowledge("auth"))
```

### Find decisions about OAuth
```python
print(search_knowledge("OAuth", node_type="Decision"))
```

### Find high-confidence findings in design graph
```python
print(search_knowledge("", triad="design", node_type="Finding", min_confidence=0.90))
```

### Search for a partial node ID
```python
print(search_knowledge("auth_dec"))  # Finds "auth_decision"
```

## Tips

1. **Start broad**: Use short terms, then narrow with filters
2. **Try variations**: "auth" vs "authentication" vs "OAuth"
3. **Check snippets**: Snippets show where and how the match occurred
4. **Use node type**: Filter by Decision to find ADRs
5. **Confidence filter**: Use `min_confidence=0.85` for verified nodes only

## No Results?

If you get no results:
- Try shorter, more general terms
- Remove filters (especially node_type and min_confidence)
- Check graph exists: `get_status(triad)` if you specified a triad
- Use empty query to list all: `search_knowledge("", triad="design")`

## See Also

- `/knowledge-show` - View detailed node information
- `/knowledge-status` - Check available graphs
- `/knowledge-help` - Full command reference
