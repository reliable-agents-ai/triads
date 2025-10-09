# Knowledge Issue Detection

## Overview

The KM detection system automatically identifies quality issues in knowledge graph nodes as they are created or updated.

## Detection Rules

### Sparse Entity (Medium Priority)

**Trigger:** Entity or Concept node with < 3 meaningful properties

**Example:**
```json
{
  "id": "jwt_library",
  "type": "Entity",
  "label": "JWT",
  "properties": {"name": "JWT"}  // Only 1 property - sparse!
}
```

**Action:** Queue for enrichment via research-agent

**Rationale:** Entities should have enough detail to be useful. Sparse entities may indicate incomplete research or need for follow-up.

### Low Confidence (High Priority)

**Trigger:** Confidence < 0.85 (except Uncertainty nodes)

**Example:**
```json
{
  "id": "unverified_claim",
  "type": "Finding",
  "confidence": 0.70  // Below threshold
}
```

**Action:** Queue for verification via verification-agent

**Rationale:** Low confidence facts may propagate errors. They should be verified or marked as Uncertainty.

### Missing Evidence (High Priority)

**Trigger:** No evidence field present (except Uncertainty nodes)

**Example:**
```json
{
  "id": "uncited_fact",
  "type": "Entity",
  "label": "Important finding"
  // Missing: evidence field
}
```

**Action:** Queue for validation - evidence must be added

**Rationale:** Constitutional principle "Evidence-Based Claims" requires all facts to have verifiable evidence.

## Configuration

Detection thresholds can be configured in `src/triads/km/detection.py`:

```python
CONFIDENCE_THRESHOLD = 0.85  # Minimum confidence for facts
SPARSE_PROPERTY_THRESHOLD = 3  # Minimum properties for entities
```

## Queue Format

Issues are stored in `.claude/km_queue.json`:

```json
{
  "issues": [
    {
      "type": "sparse_entity",
      "triad": "discovery",
      "node_id": "jwt_lib",
      "label": "JWT Library",
      "property_count": 1,
      "priority": "medium",
      "detected_at": "2025-10-09T12:00:00Z"
    },
    {
      "type": "low_confidence",
      "triad": "design",
      "node_id": "uncertain_decision",
      "label": "Architecture Choice",
      "confidence": 0.70,
      "priority": "high",
      "detected_at": "2025-10-09T12:05:00Z"
    }
  ],
  "issue_count": 2,
  "updated_at": "2025-10-09T12:05:00Z"
}
```

## Integration

### Automatic Detection (on_stop.py hook)

Detection runs automatically after each knowledge graph update:

1. Agent outputs [GRAPH_UPDATE] blocks
2. Hook saves graph to disk
3. Hook calls `detect_km_issues(graph_data, triad)`
4. If issues found: `update_km_queue(issues)`
5. User sees: "📋 Detected N KM issues (see km_queue.json)"

### Manual Detection

You can also run detection manually:

```python
from triads.km.detection import detect_km_issues

graph_data = load_graph("discovery")
issues = detect_km_issues(graph_data, "discovery")

for issue in issues:
    print(f"{issue['type']}: {issue['label']}")
```

## Testing

Comprehensive test suite in `tests/test_km/test_detection.py`:

- Sparse entity detection
- Low confidence detection
- Missing evidence detection
- Uncertainty nodes ignored
- Multiple issues per node
- Property counting logic
- Queue management (duplicates, preservation)

Run tests:
```bash
uv run pytest tests/test_km/test_detection.py -v
```

## Architecture

### Detection Flow

```
[GRAPH_UPDATE]
    ↓
on_stop.py saves graph
    ↓
detect_km_issues(graph, triad)
    ↓
Check each node:
  - Sparse? (< 3 properties)
  - Low confidence? (< 0.85)
  - Missing evidence?
    ↓
Return issues list
    ↓
update_km_queue(issues)
    ↓
.claude/km_queue.json updated
```

### Property Counting

The system counts "meaningful" properties, excluding metadata:

**Excluded metadata fields:**
- id, type, label, description
- confidence, evidence
- created_by, created_at
- updated_by, updated_at

**Two counting modes:**

1. **Explicit properties dict:**
   ```python
   node = {"id": "x", "properties": {"a": 1, "b": 2}}
   count = 2  # Count properties dict contents
   ```

2. **No properties dict:**
   ```python
   node = {"id": "x", "type": "Entity", "field1": "v1", "field2": "v2"}
   count = 2  # Count non-metadata fields
   ```

## Next Steps

This detection system provides the foundation for:

1. **KM Formatting** (Phase 2) - Format issues for agent/user display
2. **System Agents** (Phase 3) - research-agent and verification-agent
3. **User Commands** (Phase 4) - /enrich-knowledge, /km-status
4. **Fresh Context** (Phase 5) - Inject KM status into agent context

## Related

- [Knowledge Graph Architecture](../research/knowledge/knowledge-graph-architecture.md)
- [Constitutional Knowledge Management](../research/knowledge/constitutional-knowledge-management.md)
