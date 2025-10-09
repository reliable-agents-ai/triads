# Knowledge Management Fresh Context

## Overview

Fresh Context is the practice of making agents aware of KM quality issues relevant to their work. This ensures agents don't repeat mistakes, address known uncertainties, and maintain high-quality knowledge graphs.

## How It Works

### Automatic Context via Status File

The KM system creates `.claude/km_status.md` automatically after every graph update (via on_stop.py hook). This file contains:
- All current quality issues
- Grouped by triad and priority
- Agent routing information
- Actionable descriptions

**Agents can read this file** to understand current graph quality.

### Pattern: Agent Self-Awareness

**Best Practice**: Agents should check km_status.md at the start of their execution when working with knowledge graphs.

**Example agent prompt addition:**
```markdown
## Before Starting

1. Check for KM issues relevant to your work:
   - Read `.claude/km_status.md` (if it exists)
   - Note any issues in your triad
   - Avoid repeating known quality problems

2. If you encounter issues mentioned in the status file:
   - Address them as you work
   - Output [GRAPH_UPDATE] blocks to resolve
   - Higher quality > speed
```

---

## Integration Strategies

### Strategy 1: Implicit Context (Recommended)

System agents (research-agent, verification-agent) are **invoked specifically to resolve KM issues**. They receive the issue as part of their task:

```
Start research-agent: Enrich the sparse entity 'PyJWT Library' (pyjwt_lib) in the discovery triad.
```

The agent knows:
- What the problem is (sparse entity)
- Which node to fix (pyjwt_lib)
- What's expected (add 3+ properties)

**No extra context needed** - the task itself provides context.

### Strategy 2: Explicit Context Check

User triads (discovery, design, implementation) can optionally check for KM issues:

**Discovery Agent Example:**
```markdown
---
name: codebase-analyst
triad: discovery
---

# Codebase Analyst

## Your Role
Analyze codebase and document findings in the knowledge graph.

## Before Starting

**Check KM Status:**
1. Read `.claude/km_status.md` if it exists
2. Note any sparse entities or low-confidence nodes in the discovery triad
3. As you analyze, enrich sparse entities you encounter
4. Add strong evidence to avoid low-confidence issues

## Your Process
[Rest of agent prompt...]
```

### Strategy 3: Hook-Based Injection (Future)

A pre-agent hook could inject relevant KM status:

```python
# .claude/hooks/on_agent_start.py (hypothetical)
def inject_km_context(agent_name, agent_triad):
    """Inject KM issues relevant to this agent's triad."""

    status_file = Path(".claude/km_status.md")
    if not status_file.exists():
        return ""

    # Read status
    status = status_file.read_text()

    # Extract issues for this triad
    triad_section = extract_triad_section(status, agent_triad)

    if not triad_section:
        return ""

    # Format for injection
    context = f"""
## KM Status Alert

Your triad ({agent_triad}) has the following quality issues:

{triad_section}

Please address these as you work.
"""

    return context
```

**Status**: Not yet implemented (Claude Code hook system limitations)

---

## Usage Patterns

### Pattern A: System Agent Invocation

**Trigger**: User or automation invokes system agent

**Flow:**
```
1. User runs: /km-status
   Output: "3 sparse entities in discovery triad"

2. User decides to resolve
   User runs: /enrich-knowledge pyjwt_lib

3. Claude expands command:
   "Enrich the sparse entity 'PyJWT Library' (pyjwt_lib)..."

4. Claude acts as research-agent:
   - Researches the entity
   - Outputs [GRAPH_UPDATE]
   - Entity enriched

5. on_stop.py hook:
   - Processes [GRAPH_UPDATE]
   - Updates discovery_graph.json
   - Detects issues (entity now has 5+ properties - resolved!)
   - Updates km_queue.json (removes resolved issue)
   - Regenerates km_status.md

6. Next /km-status shows issue resolved
```

**Context**: Task description itself provides all needed context

### Pattern B: User Triad with KM Awareness

**Trigger**: User invokes triad agent

**Flow:**
```
1. User: "Start Discovery: analyze the authentication system"

2. Discovery agent (codebase-analyst) starts:
   - Checks km_status.md
   - Sees: "JWT Implementation (jwt_impl) - missing evidence"
   - Notes to add evidence for JWT-related findings

3. Agent analyzes codebase:
   - Finds JWT implementation in src/auth/jwt.py
   - Creates node with STRONG evidence:
     [GRAPH_UPDATE]
     type: add_node
     node_id: jwt_implementation_details
     evidence: "Found in src/auth/jwt.py:45-120, uses PyJWT 2.8.0..."
     confidence: 0.95
     [/GRAPH_UPDATE]

4. on_stop.py hook:
   - Processes update
   - Detects no issues (high confidence, strong evidence)
   - km_queue.json stays clean

5. Result: High-quality graph from the start
```

**Context**: Agent proactively checked km_status.md

### Pattern C: Bridge Agent Context Handoff

**Trigger**: Bridge agent transitions between triads

**Flow:**
```
1. Discovery triad completes:
   - knowledge-synthesizer (bridge) prepares handoff
   - Notices in km_status.md: "2 sparse entities in discovery"
   - Notes in handoff summary:
     "WARNING: PyJWT entity is sparse, recommend enrichment"

2. Design triad begins:
   - Receives compressed context from bridge
   - Sees warning about PyJWT
   - Either enriches PyJWT or marks as needing enrichment
   - Proceeds with design knowing the limitation

3. Result: Quality issues don't propagate silently
```

**Context**: Bridge agent checked km_status.md before handoff

---

## Implementation Guide

### For Agent Authors

**Add KM awareness to your agent:**

1. **Add KM check to agent prompt:**
```markdown
## Initialization

Before starting your main task:

1. **Check KM Status** (if working with knowledge graphs):
   ```
   Read .claude/km_status.md
   ```

2. **Note relevant issues**:
   - Issues in your triad
   - Issues related to your work
   - Known uncertainties

3. **Address issues as you work**:
   - Add strong evidence to avoid low-confidence issues
   - Enrich entities with 3+ properties
   - Cite all sources

## Your Main Task
[Rest of prompt...]
```

2. **Example in action:**

```markdown
# Codebase Analyst

## Initialization

1. Check `.claude/km_status.md` for discovery triad issues
2. Note sparse entities and low-confidence nodes
3. Plan to address them during analysis

## Process

When analyzing codebase:
- If you encounter a sparse entity, enrich it
- If you find evidence for low-confidence nodes, add it
- Always cite file:line for code-related findings

Example:
```
[GRAPH_UPDATE]
type: update_node
node_id: jwt_lib
properties: {
  "file_path": "src/auth/jwt.py",
  "line_range": "45-120",
  "purpose": "JWT token generation and validation"
}
confidence: 0.95
evidence: Found in src/auth/jwt.py:45-120...
[/GRAPH_UPDATE]
```
```

### For Users

**Check KM status regularly:**

```bash
# After work session
/km-status

# Before starting new work
/km-status

# Weekly
/km-status
```

**Address high-priority issues:**

```bash
/validate-knowledge all   # Fix high-priority first
/enrich-knowledge all     # Then medium-priority
```

---

## File Structure

### .claude/km_status.md

**Purpose**: Human and agent-readable status file

**Format**:
```markdown
# Knowledge Management Status

## Summary
- Total issues: 5
- High priority: 2
- Medium priority: 3

## Discovery Triad (3 issues)

### High Priority
⚠️ **Low Confidence Node** (node_id)
- confidence: 0.72
- Agent: verification-agent

### Medium Priority
🔍 **Sparse Entity** (node_id)
- property_count: 1
- Agent: research-agent

[... more triads ...]
```

**Generated by**: on_stop.py hook after each graph update

**Read by**: Agents, users via /km-status command

---

## Benefits of Fresh Context

### 1. Prevents Quality Regression

**Without Fresh Context:**
```
Discovery finds: "JWT library"
- Adds node with just name
- Low quality

Design references JWT:
- Doesn't realize it's sparse
- Adds more low-quality nodes

Implementation uses JWT:
- Still doesn't know details
- Makes assumptions

Result: Cascade of low-quality information
```

**With Fresh Context:**
```
Discovery finds: "JWT library"
- Adds node
- Hook detects sparse entity

Design starts:
- Reads km_status.md
- Sees "JWT library is sparse"
- Either enriches it or notes limitation

Result: Quality issues caught early
```

### 2. Enables Proactive Resolution

Agents can resolve issues **as they work** rather than needing separate resolution steps:

```
Codebase Analyst analyzing auth system:
- Reads km_status.md
- Sees "JWT implementation - missing evidence"
- While analyzing JWT code, adds comprehensive evidence
- Issue resolved inline
```

### 3. Maintains Context Across Sessions

**Between Sessions:**
```
Session 1:
- Discovery phase work
- Some sparse entities created

[Time passes]

Session 2:
- User runs /km-status
- Sees issues from Session 1
- Resolves before continuing

Result: Quality doesn't degrade over time
```

### 4. Supports Collaborative Work

**Multiple Users:**
```
User A:
- Works on discovery triad
- Leaves some sparse entities

User B:
- Starts design triad
- Reads km_status.md
- Sees User A's sparse entities
- Can address them or note dependencies

Result: Team stays coordinated on quality
```

---

## Best Practices

### DO ✅

✅ **Check km_status.md at agent start**
```markdown
## Initialization
1. Read `.claude/km_status.md` for current issues
2. Note issues relevant to your triad/task
```

✅ **Address issues inline as you work**
```
If analyzing JWT and it's marked sparse:
- Add properties while analyzing
- Output [GRAPH_UPDATE]
- Resolve issue immediately
```

✅ **Add strong evidence from the start**
```
Always cite:
- File paths with line numbers
- URLs for web sources
- Commit hashes for decisions
```

✅ **Run /km-status regularly**
```bash
# After work
/km-status

# Before work
/km-status
```

✅ **Resolve high-priority issues first**
```
Priority order:
1. Missing evidence (high)
2. Low confidence (high)
3. Sparse entities (medium)
```

### DON'T ❌

❌ **Don't ignore km_status.md**
```
If agent sees issues but ignores them:
- Quality degrades
- Issues accumulate
- Harder to fix later
```

❌ **Don't assume issues are someone else's problem**
```
If you encounter a sparse entity:
- Enrich it if you have information
- Or mark what you don't know as Uncertainty
```

❌ **Don't create nodes that will trigger issues**
```
Bad:
- Sparse entities (< 3 properties)
- Low confidence (< 0.85) without converting to Uncertainty
- Missing evidence

Good:
- 5+ properties
- 0.90+ confidence
- Comprehensive evidence citations
```

---

## Testing Fresh Context

### Manual Test

1. **Create test issue:**
```bash
echo '{
  "issues": [{
    "type": "sparse_entity",
    "triad": "discovery",
    "node_id": "test_entity",
    "label": "Test Entity",
    "property_count": 1,
    "priority": "medium"
  }]
}' > .claude/km_queue.json
```

2. **Generate status file:**
```python
from triads.km.formatting import write_km_status_file
write_km_status_file()
```

3. **View status:**
```bash
cat .claude/km_status.md
```

4. **Test agent awareness:**
```
Start discovery: Analyze something related to test_entity

Agent should:
- Read km_status.md
- See test_entity is sparse
- Enrich it during work
```

5. **Verify resolution:**
```bash
/km-status  # Should show issue resolved
```

---

## Future Enhancements

### 1. Automatic Context Injection

**Hook that injects KM status into agent prompts:**
```python
# on_agent_start.py
def inject_context(agent_name, triad):
    issues = get_triad_issues(triad)
    if issues:
        return f"NOTE: {len(issues)} KM issues in your triad. See details in km_status.md"
    return ""
```

### 2. Priority-Based Alerts

**Only inject high-priority issues:**
```python
high_priority = [i for i in issues if i['priority'] == 'high']
if high_priority:
    return f"⚠️  {len(high_priority)} HIGH PRIORITY issues require immediate attention"
```

### 3. Smart Context Filtering

**Only inject relevant issues:**
```python
if agent_name == "codebase-analyst":
    # Only show code-related sparse entities
    return filter_issues(issues, type="sparse_entity", category="code")
```

### 4. Context Size Limits

**Avoid overwhelming agents:**
```python
MAX_CONTEXT_SIZE = 500  # characters

if len(context) > MAX_CONTEXT_SIZE:
    # Summarize instead of full details
    return f"{len(issues)} KM issues found. Run /km-status for details."
```

---

## Related Documentation

- [Detection System](km-detection.md) - How issues are detected
- [Formatting System](km-formatting.md) - How issues are formatted
- [System Agents](km-system-agents.md) - Automated resolution
- [User Commands](km-user-commands.md) - Manual management

---

## Summary

**Fresh Context** ensures agents work with awareness of knowledge graph quality:

1. **Automatic**: on_stop.py generates km_status.md after every update
2. **Available**: Agents can read km_status.md to check for issues
3. **Actionable**: Issues include node_id, description, agent routing
4. **Effective**: Prevents quality regression, enables proactive resolution

**Simple Pattern**:
```
1. Agent starts
2. Reads .claude/km_status.md
3. Notes relevant issues
4. Addresses issues as work progresses
5. Outputs [GRAPH_UPDATE] blocks
6. Hook updates graphs and regenerates status
7. Next agent sees updated status
```

**Result**: High-quality knowledge graphs maintained automatically.
