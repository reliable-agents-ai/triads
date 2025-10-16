# Knowledge Status Command

View the status of all knowledge graphs or a specific triad graph.

## Usage

**View all graphs:**
```python
from triads.km.graph_access import get_status
print(get_status())
```

**View specific triad:**
```python
from triads.km.graph_access import get_status
print(get_status('design'))
```

## Output

Shows a summary table with:
- **Triad**: Name of the triad graph
- **Nodes**: Number of nodes in the graph
- **Edges**: Number of edges (relationships)
- **Types**: Count of distinct node types
- **Avg Confidence**: Average confidence score

For single triad view, also shows node type breakdown.

## Example

```
# Knowledge Graph Status

Graphs: 5
Total Nodes: 157
Total Edges: 34

| Triad | Nodes | Edges | Types | Avg Confidence |
|-------|-------|-------|-------|----------------|
| design | 65 | 0 | 4 | 0.93 |
| implementation | 23 | 0 | 4 | 0.99 |
...
```

## See Also

- `/knowledge-search` - Search across graphs
- `/knowledge-show` - View node details
- `/knowledge-help` - Full command reference
