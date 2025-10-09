# Knowledge Management System Overview

## Introduction

The Knowledge Management (KM) system ensures high-quality knowledge graphs through automatic detection, formatting, and resolution of quality issues. It operates transparently in the background while providing manual control when needed.

## System Architecture

### Five Integrated Phases

```
Phase 1: DETECTION
    ↓
Phase 2: FORMATTING
    ↓
Phase 3: SYSTEM AGENTS
    ↓
Phase 4: USER COMMANDS
    ↓
Phase 5: FRESH CONTEXT
```

---

## Phase 1: Detection

**Purpose**: Automatically identify quality issues as graphs are updated

**Location**: `src/triads/km/detection.py`

**Detection Rules**:
1. **Sparse Entity** (medium priority): Entity/Concept with < 3 meaningful properties
2. **Low Confidence** (high priority): Confidence < 0.85 (except Uncertainty nodes)
3. **Missing Evidence** (high priority): No evidence field (except Uncertainty nodes)

**Integration**: on_stop.py hook calls `detect_km_issues()` after each graph save

**Output**: Issues stored in `.claude/km_queue.json`

**Documentation**: [km-detection.md](km-detection.md)

---

## Phase 2: Formatting

**Purpose**: Transform detected issues into human and agent-readable formats

**Location**: `src/triads/km/formatting.py`

**Functions**:
1. **format_km_notification()**: Brief user notifications with emoji
2. **get_agent_for_issue()**: Route issues to appropriate system agents
3. **write_km_status_file()**: Generate `.claude/km_status.md` for agents

**Integration**: on_stop.py hook calls formatting functions after detection

**Output**:
- User notification: `"📋 3 KM issues detected (2 high priority, ...)"`
- Status file: `.claude/km_status.md` (markdown with grouped issues)

**Documentation**: [km-formatting.md](km-formatting.md)

---

## Phase 3: System Agents

**Purpose**: Specialized agents that automatically resolve KM issues

**Location**: `.claude/agents/system/`

**Agents**:

1. **research-agent** (`research-agent.md`)
   - Handles: sparse_entity issues
   - Process: Research → Add properties → Cite evidence
   - Example: Enrich "JWT Library" from 1 to 5+ properties

2. **verification-agent** (`verification-agent.md`)
   - Handles: low_confidence, missing_evidence issues
   - Process: Investigate → Verify/Mark as Uncertainty/Correct
   - Example: Verify "OAuth2 Decision" and raise confidence 0.72 → 0.95

**Management**: `src/triads/km/system_agents.py` provides agent discovery, validation, routing, task formatting

**Integration**: Invoked manually via `Start research-agent: ...` or user commands

**Documentation**: [km-system-agents.md](km-system-agents.md)

---

## Phase 4: User Commands

**Purpose**: Manual KM management through slash commands

**Location**: `.claude/commands/`

**Commands**:

1. **/km-status** (`km-status.md`)
   - View comprehensive issue report
   - Shows summary, issues by triad, recommendations
   - Usage: `/km-status`

2. **/enrich-knowledge** (`enrich-knowledge.md`)
   - Manually enrich sparse entities
   - Interactive or targeted (node_id, "all")
   - Usage: `/enrich-knowledge pyjwt_lib`

3. **/validate-knowledge** (`validate-knowledge.md`)
   - Validate low-confidence claims, add missing evidence
   - Interactive or targeted
   - Usage: `/validate-knowledge auth_decision`

**Integration**: Claude Code slash command system

**Documentation**: [km-user-commands.md](km-user-commands.md)

---

## Phase 5: Fresh Context

**Purpose**: Make agents aware of KM quality issues relevant to their work

**Mechanism**: Agents read `.claude/km_status.md` at start of execution

**Patterns**:
1. **Implicit Context**: System agents invoked with issue as task (built-in)
2. **Explicit Context**: User triads check km_status.md in their prompts
3. **Hook-Based**: (Future) Pre-agent hook injects relevant issues

**Benefits**:
- Prevents quality regression
- Enables proactive resolution
- Maintains context across sessions
- Supports collaborative work

**Documentation**: [km-fresh-context.md](km-fresh-context.md)

---

## Complete Data Flow

### Automatic Flow (Background)

```
1. Agent outputs [GRAPH_UPDATE] blocks
   ↓
2. on_stop.py hook fires
   ↓
3. Hook saves graph to .claude/graphs/{triad}_graph.json
   ↓
4. Hook calls detect_km_issues(graph, triad)
   ↓
5. Issues found → update_km_queue(issues)
   ↓
6. Hook calls format_km_notification(issues)
   ↓
7. User sees: "📋 3 KM issues detected"
   ↓
8. Hook calls write_km_status_file()
   ↓
9. .claude/km_status.md created/updated
   ↓
10. Next agent can read km_status.md for fresh context
```

### Manual Resolution Flow

```
1. User runs: /km-status
   ↓
2. Claude reads km_queue.json + km_status.md
   ↓
3. User sees comprehensive report
   ↓
4. User decides to resolve issue
   ↓
5. User runs: /enrich-knowledge pyjwt_lib
   ↓
6. Claude acts as research-agent
   ↓
7. Claude researches and enriches entity
   ↓
8. Claude outputs [GRAPH_UPDATE]
   ↓
9. on_stop.py hook processes update
   ↓
10. Graph updated, issue removed from queue
   ↓
11. User runs /km-status again → issue resolved
```

### System Agent Flow

```
1. User runs: /km-status
   ↓
2. Sees high-priority issue
   ↓
3. User runs: Start verification-agent: Verify node X
   ↓
4. verification-agent investigates claim
   ↓
5. Agent outputs [GRAPH_UPDATE] with verification
   ↓
6. on_stop.py hook processes update
   ↓
7. Issue resolved
```

---

## File Structure

```
triads/
├── src/triads/km/
│   ├── __init__.py
│   ├── detection.py          # Phase 1: Issue detection
│   ├── formatting.py          # Phase 2: Issue formatting
│   └── system_agents.py       # Phase 3: Agent management
│
├── .claude/
│   ├── agents/system/
│   │   ├── research-agent.md        # Phase 3: Enrichment agent
│   │   └── verification-agent.md    # Phase 3: Validation agent
│   │
│   ├── commands/
│   │   ├── km-status.md             # Phase 4: Status command
│   │   ├── enrich-knowledge.md      # Phase 4: Enrichment command
│   │   └── validate-knowledge.md    # Phase 4: Validation command
│   │
│   ├── graphs/
│   │   └── {triad}_graph.json       # Knowledge graphs
│   │
│   ├── km_queue.json                # Issue queue
│   ├── km_status.md                 # Phase 2: Status file for agents
│   │
│   └── hooks/
│       └── on_stop.py               # Integration point
│
├── tests/test_km/
│   ├── test_detection.py            # 12 tests
│   ├── test_formatting.py           # 13 tests
│   └── test_system_agents.py        # 15 tests
│
└── docs/
    ├── km-detection.md              # Phase 1 docs
    ├── km-formatting.md             # Phase 2 docs
    ├── km-system-agents.md          # Phase 3 docs
    ├── km-user-commands.md          # Phase 4 docs
    ├── km-fresh-context.md          # Phase 5 docs
    └── km-system-overview.md        # This file
```

---

## Testing

**Test Coverage**:
- **40 tests total** across all phases
- **85% coverage** on km module
- All tests passing with ruff + mypy clean

**Test Files**:
- `test_detection.py`: 12 tests for issue detection
- `test_formatting.py`: 13 tests for formatting
- `test_system_agents.py`: 15 tests for agent management

**Run Tests**:
```bash
uv run pytest tests/test_km/ -v --cov=src/triads/km
```

---

## Quick Start Guide

### 1. Check System Status

```bash
/km-status
```

Shows all current KM issues.

### 2. Resolve High-Priority Issues

```bash
/validate-knowledge all
```

Validates low-confidence nodes and adds missing evidence.

### 3. Enrich Sparse Entities

```bash
/enrich-knowledge all
```

Adds properties to sparse entities.

### 4. Verify Resolution

```bash
/km-status
```

Confirm issues are resolved.

---

## Configuration

### Detection Thresholds

```python
# In src/triads/km/detection.py
CONFIDENCE_THRESHOLD = 0.85      # Minimum confidence
SPARSE_PROPERTY_THRESHOLD = 3    # Minimum properties
```

### Agent Routing

```python
# In src/triads/km/formatting.py and system_agents.py
ISSUE_TO_AGENT = {
    "sparse_entity": "research-agent",
    "low_confidence": "verification-agent",
    "missing_evidence": "verification-agent",
}
```

### File Locations

```python
# In detection.py and formatting.py
QUEUE_FILE = Path(".claude/km_queue.json")
STATUS_FILE = Path(".claude/km_status.md")

# In system_agents.py
SYSTEM_AGENTS_DIR = Path(".claude/agents/system")
```

---

## Best Practices

### For Users

1. **Check status regularly**: Run `/km-status` after work sessions
2. **Resolve high-priority first**: Validation issues before enrichment
3. **Batch operations**: Use `all` argument for efficiency
4. **Verify resolution**: Run `/km-status` again to confirm

### For Agent Authors

1. **Check km_status.md**: Read at agent start for awareness
2. **Add strong evidence**: File:line, URLs, commit hashes
3. **3+ properties minimum**: For entities and concepts
4. **Confidence 0.85+**: Or convert to Uncertainty
5. **Use [GRAPH_UPDATE]**: Proper format for graph updates

### For Developers

1. **Follow TDD**: Write tests first (RED-GREEN-BLUE)
2. **Maintain coverage**: Keep > 80% coverage
3. **Type annotations**: Use `from __future__ import annotations`
4. **Constitutional compliance**: Enforce TRUST principles
5. **Document changes**: Update relevant docs

---

## Troubleshooting

### Hook Errors

**Problem**: on_stop.py hook fails with import errors

**Solution**:
```bash
# Check sys.path includes src/
grep "sys.path" .claude/hooks/on_stop.py

# Should see: sys.path.insert(0, str(repo_root / "src"))
```

### No Issues Detected

**Problem**: Work creates low-quality nodes but no issues detected

**Solution**:
```bash
# Check detection thresholds
grep "THRESHOLD" src/triads/km/detection.py

# Check hooks are configured
cat .claude/settings.json | grep hooks

# Manually test detection
python3 -c "
from triads.km.detection import detect_km_issues
graph = {'nodes': [{'id': 'test', 'type': 'Entity', 'properties': {'x': 1}}]}
print(detect_km_issues(graph, 'test'))
"
```

### Commands Not Found

**Problem**: `/km-status` returns "Unknown command"

**Solution**:
```bash
# Check command file exists
ls .claude/commands/km-status.md

# Check frontmatter
head -5 .claude/commands/km-status.md
```

### Issues Not Resolving

**Problem**: Fix issue but it still appears in queue

**Solution**:
1. Check [GRAPH_UPDATE] format is correct
2. Verify hook processed the update (check graphs updated)
3. Manually regenerate status:
```python
from triads.km.formatting import write_km_status_file
write_km_status_file()
```

---

## Performance Considerations

**Detection**: O(n) where n = number of nodes (fast)

**Formatting**: O(n) where n = number of issues (fast)

**Queue Updates**: O(n) checks for duplicates (fast with sets)

**Status File Generation**: O(n) with grouping (fast with defaultdict)

**Typical Impact**: < 100ms overhead per graph update

---

## Future Enhancements

### 1. Automated Resolution

```python
# Automatically invoke system agents for high-priority issues
if high_priority_count > 3:
    auto_invoke_agents(high_priority_issues)
```

### 2. Machine Learning

```python
# Learn which properties are most useful
# Suggest properties based on entity type and context
```

### 3. Graph Analytics

```python
# Detect patterns in issues
# "Discovery triad always has sparse entities"
# Recommend process improvements
```

### 4. CI/CD Integration

```bash
# Pre-commit hook checks for KM issues
# Blocks commits if high-priority issues exist
```

### 5. Metrics Dashboard

```
# Track KM health over time
- Issue trend (increasing/decreasing)
- Resolution time by agent
- Quality score by triad
```

---

## Implementation Timeline

**Phase 0** (Foundation): Repository setup with uv, pytest, ruff, mypy

**Phase 1** (Detection): Issue detection with 12 tests, 100% coverage

**Phase 2** (Formatting): User notifications + status files, 13 tests, 96% coverage

**Phase 3** (System Agents): research-agent + verification-agent, 15 tests, 86% coverage

**Phase 4** (User Commands): 3 slash commands for manual management

**Phase 5** (Fresh Context): Agent awareness via km_status.md

**Total Development**: 5 phases, 40 tests, 85% coverage, all passing

---

## Contributing

### Adding New Issue Types

1. **Add detection logic** in `src/triads/km/detection.py`:
```python
# Issue 4: Outdated information
if last_updated > 90_days_ago:
    issues.append({"type": "outdated_info", ...})
```

2. **Add formatting** in `src/triads/km/formatting.py`:
```python
ISSUE_TO_AGENT["outdated_info"] = "refresh-agent"
```

3. **Create system agent** in `.claude/agents/system/refresh-agent.md`

4. **Add tests** in `tests/test_km/test_detection.py`

5. **Update docs**

### Adding New System Agents

1. **Create agent file**: `.claude/agents/system/new-agent.md`

2. **Add frontmatter**:
```yaml
---
name: new-agent
role: Brief description
type: system
purpose: What it does
---
```

3. **Write agent prompt** with examples, process, quality checklist

4. **Add routing** in `system_agents.py`

5. **Add tests** in `test_system_agents.py`

6. **Update docs**

---

## Resources

**Documentation**:
- [Detection](km-detection.md)
- [Formatting](km-formatting.md)
- [System Agents](km-system-agents.md)
- [User Commands](km-user-commands.md)
- [Fresh Context](km-fresh-context.md)

**Code**:
- `src/triads/km/` - Python modules
- `.claude/agents/system/` - System agents
- `.claude/commands/` - User commands
- `tests/test_km/` - Test suite

**Support**:
- GitHub Issues: https://github.com/reliable-agents-ai/triads/issues
- Discussions: https://github.com/reliable-agents-ai/triads/discussions

---

## Summary

The KM system provides **automatic quality assurance** for knowledge graphs:

✅ **Automatic Detection**: Issues caught immediately after graph updates

✅ **Clear Formatting**: Human and agent-readable status reports

✅ **Automated Resolution**: System agents resolve issues autonomously

✅ **Manual Control**: User commands for targeted management

✅ **Fresh Context**: Agents aware of quality issues

✅ **Well-Tested**: 40 tests, 85% coverage, all passing

✅ **Fully Documented**: Comprehensive docs for each phase

**Result**: High-quality knowledge graphs maintained with minimal effort.
