# Knowledge Issue Formatting

## Overview

The KM formatting system transforms detected quality issues into human-readable and agent-readable formats.

## Formatting Functions

### format_km_notification()

**Purpose:** Create brief user notifications about detected issues

**Signature:**
```python
def format_km_notification(issues: list[dict[str, Any]]) -> str | None
```

**Behavior:**
- Returns `None` if issue list is empty
- For single issue: "📋 1 KM issue detected (sparse entity)"
- For multiple issues: Groups by priority and type

**Examples:**

```python
# Single issue
issues = [{"type": "sparse_entity", "priority": "medium", "node_id": "x"}]
notification = format_km_notification(issues)
# => "📋 1 KM issue detected (sparse entity)"

# Multiple issues with high priority
issues = [
    {"type": "low_confidence", "priority": "high", "node_id": "a"},
    {"type": "low_confidence", "priority": "high", "node_id": "b"},
    {"type": "sparse_entity", "priority": "medium", "node_id": "c"},
]
notification = format_km_notification(issues)
# => "📋 3 KM issues detected (2 high priority, 2 low confidence, 1 sparse entity)"
```

**Integration:** Called by `on_stop.py` hook after detecting issues

---

### get_agent_for_issue()

**Purpose:** Route issues to appropriate system agents

**Signature:**
```python
def get_agent_for_issue(issue: dict[str, Any]) -> str
```

**Routing Table:**

| Issue Type | System Agent |
|------------|--------------|
| `sparse_entity` | `research-agent` |
| `low_confidence` | `verification-agent` |
| `missing_evidence` | `verification-agent` |

**Raises:** `ValueError` if issue type is unknown

**Examples:**

```python
issue = {"type": "sparse_entity", "node_id": "x"}
agent = get_agent_for_issue(issue)
# => "research-agent"

issue = {"type": "low_confidence", "node_id": "y"}
agent = get_agent_for_issue(issue)
# => "verification-agent"
```

**Future Extensions:**

To add new issue types and agents:

```python
# In src/triads/km/formatting.py
ISSUE_TO_AGENT = {
    "sparse_entity": "research-agent",
    "low_confidence": "verification-agent",
    "missing_evidence": "verification-agent",
    "outdated_info": "refresh-agent",  # New type
}
```

---

### write_km_status_file()

**Purpose:** Create agent-readable status file from issue queue

**Signature:**
```python
def write_km_status_file() -> None
```

**Behavior:**
- Reads from `.claude/km_queue.json`
- Writes to `.claude/km_status.md`
- If no issues: Removes status file
- Groups issues by triad and priority
- Includes agent routing information

**Output Format:**

```markdown
# Knowledge Management Status

## Summary

**Total issues**: 5
- ⚠️  **3 high priority**
- 📋 2 medium priority

---

## Discovery Triad (3 issues)

### ⚠️  High Priority

- ⚠️ **Low Confidence Finding** (`uncertain_claim`) (confidence: 0.72) → `verification-agent`
- ❗ **Missing Evidence** (`uncited_entity`) (no evidence) → `verification-agent`

### 📋 Medium Priority

- 🔍 **JWT Library** (`jwt_lib`) (1 properties) → `research-agent`

## Design Triad (2 issues)

### ⚠️  High Priority

- ⚠️ **Uncertain Decision** (`decision_oauth`) (confidence: 0.80) → `verification-agent`

### 📋 Medium Priority

- 🔍 **Sparse Concept** (`auth_pattern`) (2 properties) → `research-agent`
```

**Issue Formatting:**

Each issue includes:
- **Priority emoji**: ⚠️ (high) or 📋 (medium)
- **Type emoji**:
  - 🔍 sparse_entity
  - ⚠️ low_confidence
  - ❗ missing_evidence
- **Label and node_id**: Human + machine readable
- **Type-specific details**:
  - Property count for sparse entities
  - Confidence score for low confidence
  - "no evidence" for missing evidence
- **Agent routing**: Which agent handles this issue

**Integration:** Called by `on_stop.py` hook after all graphs are updated

---

## Configuration

### File Paths

```python
# In src/triads/km/formatting.py
QUEUE_FILE = Path(".claude/km_queue.json")   # Input
STATUS_FILE = Path(".claude/km_status.md")   # Output
```

### Agent Routing

```python
ISSUE_TO_AGENT = {
    "sparse_entity": "research-agent",
    "low_confidence": "verification-agent",
    "missing_evidence": "verification-agent",
}
```

---

## Integration Flow

```
[GRAPH_UPDATE]
    ↓
on_stop.py saves graph
    ↓
detect_km_issues(graph, triad)
    ↓
update_km_queue(issues)
    ↓
format_km_notification(issues)  ← NEW
    ↓
Print notification to user
    ↓
(After all triads processed)
    ↓
write_km_status_file()  ← NEW
    ↓
.claude/km_status.md created
    ↓
Agents can read status via Fresh Context hook
```

---

## Testing

Comprehensive test suite in `tests/test_km/test_formatting.py`:

**Notification Tests:**
- `test_format_km_notification_empty`: Empty list returns None
- `test_format_km_notification_single_issue`: Single issue formatting
- `test_format_km_notification_multiple_issues`: Grouping by type/priority
- `test_format_km_notification_with_emoji`: Visual clarity with emojis

**Agent Routing Tests:**
- `test_get_agent_for_issue_sparse_entity`: Research agent routing
- `test_get_agent_for_issue_low_confidence`: Verification agent routing
- `test_get_agent_for_issue_missing_evidence`: Verification agent routing
- `test_get_agent_for_issue_unknown_type`: Error handling

**Status File Tests:**
- `test_write_km_status_file_empty_queue`: No file if empty
- `test_write_km_status_file_with_issues`: Full markdown generation
- `test_write_km_status_file_includes_agent_routing`: Agent info included
- `test_write_km_status_file_markdown_formatting`: Proper markdown structure
- `test_write_km_status_file_groups_by_priority`: High priority first

Run tests:
```bash
uv run pytest tests/test_km/test_formatting.py -v
```

---

## Usage Examples

### Manual Notification

```python
from triads.km.formatting import format_km_notification
from triads.km.detection import detect_km_issues

# Detect issues in a graph
graph_data = load_graph("discovery")
issues = detect_km_issues(graph_data, "discovery")

# Format notification
notification = format_km_notification(issues)
if notification:
    print(notification)
```

### Manual Status File Generation

```python
from triads.km.formatting import write_km_status_file

# Generate status file from current queue
write_km_status_file()

# Read it
with open(".claude/km_status.md", "r") as f:
    print(f.read())
```

### Agent Routing Logic

```python
from triads.km.formatting import get_agent_for_issue, write_km_status_file

# After writing status file, route issues to agents
import json
with open(".claude/km_queue.json", "r") as f:
    queue = json.load(f)

for issue in queue["issues"]:
    agent = get_agent_for_issue(issue)
    print(f"Issue {issue['node_id']} → {agent}")
```

---

## Architecture

### Separation of Concerns

**Detection** (`detection.py`):
- Scans graphs for quality issues
- Returns structured issue data
- Maintains queue on disk

**Formatting** (`formatting.py`):
- Transforms issues for display
- Routes to appropriate agents
- Generates status files

**Why separate?**
- Detection is pure logic (testable)
- Formatting is presentation (changeable)
- Agents can read status without re-detecting

### Data Flow

```
Graph → Detection → Queue (JSON) → Formatting → Status (Markdown)
                                              ↓
                                         Notification (String)
```

---

## Future Enhancements

### 1. Priority-based Notifications

```python
# Only notify user about high priority issues
high_priority = [i for i in issues if i["priority"] == "high"]
if high_priority:
    notification = format_km_notification(high_priority)
```

### 2. Slack/Discord Webhooks

```python
def send_webhook_notification(issues):
    """Send KM issues to external channel."""
    notification = format_km_notification(issues)
    if notification:
        requests.post(WEBHOOK_URL, json={"text": notification})
```

### 3. HTML Status Dashboard

```python
def write_km_status_html():
    """Generate interactive HTML status page."""
    # Similar to write_km_status_file but with charts, filters
```

### 4. Agent Performance Tracking

```python
# Track which agents resolve issues fastest
{
    "research-agent": {"assigned": 10, "resolved": 8, "avg_time": "2h"},
    "verification-agent": {"assigned": 5, "resolved": 5, "avg_time": "30m"}
}
```

---

## Related

- [Detection System](km-detection.md) - How issues are detected
- [System Agents](km-system-agents.md) - Agents that resolve issues (Phase 3)
- [User Commands](km-user-commands.md) - Manual issue management (Phase 4)

---

## Implementation Notes

### Type Safety

Full type annotations for mypy:
```python
def format_km_notification(issues: list[dict[str, Any]]) -> str | None
def get_agent_for_issue(issue: dict[str, Any]) -> str
def write_km_status_file() -> None
```

### Error Handling

- `get_agent_for_issue()` raises `ValueError` for unknown types
- `write_km_status_file()` silently succeeds if queue is empty
- Hook integration wraps calls in try/except

### Performance

- Status file generation is O(n) where n = issue count
- Grouping uses `defaultdict` for efficiency
- File I/O is atomic (write then rename)

### Testing Strategy

- Unit tests for each function
- Integration test with mock queue file
- Tests use `tmp_path` and `monkeypatch` for isolation
- 96% coverage on formatting.py
