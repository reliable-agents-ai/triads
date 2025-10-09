># Knowledge Management User Commands

## Overview

User commands provide manual control over the KM system through slash commands in Claude Code. These commands allow you to inspect, enrich, and validate knowledge graph quality issues interactively.

## Available Commands

### 1. /km-status

**Purpose:** View comprehensive report of current KM issues

**Usage:**
```bash
/km-status
```

**What it does:**
1. Reads `.claude/km_queue.json` and `.claude/km_status.md`
2. Displays organized summary:
   - Total issues and breakdown by priority/triad/type
   - Detailed list of issues grouped by triad
   - Recommendations for resolution
3. Suggests which system agents to invoke

**Example Output:**
```
# Knowledge Management Status Report

## Summary
- Total Issues: 7
- High Priority: 4
- Medium Priority: 3

By Triad:
- discovery: 4 issues
- design: 2 issues
- implementation: 1 issue

## Discovery Triad (4 issues)

### High Priority
⚠️ Authentication Decision (auth_decision_oauth2)
- low_confidence (0.72)
- Agent: verification-agent

...

## Recommendations
1. Start with 4 high-priority issues
2. Run verification-agent for low-confidence nodes
3. Pattern: Discovery triad needs better documentation
```

**When to use:**
- After working on a triad to check for issues
- Before starting new work to understand graph quality
- To monitor KM system health

---

### 2. /enrich-knowledge

**Purpose:** Manually enrich sparse entities with comprehensive information

**Usage:**
```bash
/enrich-knowledge                    # Interactive: shows list
/enrich-knowledge pyjwt_lib          # Enrich specific node by ID
/enrich-knowledge "PyJWT Library"    # Enrich specific node by label
/enrich-knowledge all                # Enrich all sparse entities
```

**What it does:**
1. Loads sparse entity issues from `.claude/km_queue.json`
2. Lets you select which entity to enrich (or specify target)
3. Acts as research-agent:
   - Researches the entity through multiple sources
   - Adds 3+ meaningful properties
   - Cites all evidence
4. Outputs `[GRAPH_UPDATE]` to update the node
5. Verifies enrichment was successful

**Example Flow:**
```
> /enrich-knowledge

Reading .claude/km_queue.json...

Found 3 sparse entities:

1. PyJWT Library (pyjwt_lib) - 1 property
2. Redis Cache (redis_cache) - 2 properties
3. Microservices Pattern (microservices_concept) - 1 property

Which would you like me to enrich? (Enter number or node_id)

> 1

Enriching PyJWT Library...

[Research process shown...]

[GRAPH_UPDATE]
type: update_node
node_id: pyjwt_lib
properties: {
  "version": "2.8.0",
  "purpose": "JWT token encoding/decoding",
  "usage_files": [...],
  ...
}
confidence: 0.95
evidence: [comprehensive citations]
[/GRAPH_UPDATE]

✅ Enrichment complete! PyJWT Library now has 8 properties.
```

**When to use:**
- When you notice sparse entities in your graphs
- After `/km-status` shows sparse_entity issues
- To manually add detail to important concepts/entities

---

### 3. /validate-knowledge

**Purpose:** Validate low-confidence claims and add missing evidence

**Usage:**
```bash
/validate-knowledge                          # Interactive: shows list
/validate-knowledge auth_decision_oauth2      # Validate specific node by ID
/validate-knowledge "Authentication Decision" # Validate specific node by label
/validate-knowledge all                       # Validate all issues
```

**What it does:**
1. Loads validation issues from `.claude/km_queue.json`:
   - Low confidence nodes (< 0.85)
   - Missing evidence nodes
2. Lets you select which to validate (or specify target)
3. Acts as verification-agent:
   - Investigates the claim through multiple sources
   - Either verifies (raises confidence), marks as Uncertainty, or corrects
   - Always adds comprehensive evidence
4. Outputs `[GRAPH_UPDATE]` to update the node
5. Verifies validation was successful

**Example Flow:**
```
> /validate-knowledge

Reading .claude/km_queue.json...

Found 4 validation issues:

Low Confidence:
1. Authentication Decision (auth_decision_oauth2) - confidence: 0.72
2. Scaling Strategy (scaling_strategy) - confidence: 0.78

Missing Evidence:
3. JWT Implementation (jwt_impl)
4. Performance Claim (performance_improvement)

Which would you like me to validate?

> 1

Validating Authentication Decision...

[Investigation process shown...]

[GRAPH_UPDATE]
type: update_node
node_id: auth_decision_oauth2
confidence: 0.95
evidence: [comprehensive verification from multiple sources]
[/GRAPH_UPDATE]

✅ Validation complete! Confidence raised: 0.72 → 0.95
```

**Possible Outcomes:**

**A. Verified and Strengthened:**
- Confidence raised to 0.85+
- Comprehensive evidence added
- Node remains as-is with stronger backing

**B. Marked as Uncertainty:**
- Cannot be verified
- Converted to Uncertainty node
- Explains why it's uncertain

**C. Corrected:**
- Original claim was incorrect
- Corrected with accurate information
- Uncertainty node documents the error

**When to use:**
- When you notice low-confidence nodes
- After `/km-status` shows validation issues
- To add evidence to important claims
- To verify questionable information

---

## Command Architecture

### How Slash Commands Work

1. **Command File**: `.claude/commands/{command-name}.md`
   - Contains YAML frontmatter with description
   - Contains expanded prompt that Claude receives

2. **User Types**: `/km-status`

3. **Claude Code**: Reads `km-status.md` and treats content as prompt

4. **Claude Executes**: Follows instructions in the command file

5. **Result**: User sees the command output

### Command File Structure

```markdown
---
description: Brief command description (shows in /help)
---

# Command Title

Instructions for Claude on what to do when command is invoked.

Can include:
- Task breakdown
- Output format specifications
- Examples
- Error handling
- Related commands
```

---

## Integration with KM System

### Data Flow

```
User invokes /km-status
    ↓
Reads km_queue.json + km_status.md
    ↓
Displays formatted report
    ↓
User decides to enrich/validate
    ↓
User invokes /enrich-knowledge or /validate-knowledge
    ↓
Research/verification process
    ↓
Outputs [GRAPH_UPDATE]
    ↓
on_stop.py hook processes update
    ↓
Graph updated, issue removed from queue
    ↓
User runs /km-status again to confirm
```

### Relationship to System Agents

**User Commands** are for **manual** intervention:
- You decide when to run them
- Interactive (asks for input)
- Direct control

**System Agents** are for **automatic** resolution:
- Run via `Start research-agent: ...`
- Autonomous (no interaction)
- Can be scheduled/triggered

Both use the same underlying logic (research-agent prompts, verification-agent prompts), but different interaction models.

---

## Best Practices

### When to Use Commands

✅ **Use /km-status**:
- After completing work on a triad
- Before starting new work
- Weekly KM health checks
- When you notice quality issues

✅ **Use /enrich-knowledge**:
- For important sparse entities
- When you have domain knowledge to add
- To bootstrap initial documentation

✅ **Use /validate-knowledge**:
- For critical decisions with low confidence
- When evidence is missing
- To verify questionable claims
- Before making important decisions based on graph info

### Command Workflow

**Typical Flow:**

1. **Check Status**:
   ```
   /km-status
   ```

2. **Prioritize**:
   - Focus on high-priority issues first
   - Group by triad if working on specific area

3. **Resolve Issues**:
   ```
   /validate-knowledge auth_decision_oauth2  # High priority first
   /enrich-knowledge pyjwt_lib              # Then medium
   ```

4. **Verify**:
   ```
   /km-status  # Confirm issues are resolved
   ```

### Tips

**For /enrich-knowledge:**
- Research thoroughly - take time
- Add 5-7 properties (not just 3 minimum)
- Cite specific file:line or URLs
- Focus on actionable properties

**For /validate-knowledge:**
- Use multiple verification strategies
- If uncertain, mark as Uncertainty (don't guess)
- Correct errors openly (add Uncertainty node documenting mistake)
- Explain your verification process in evidence field

**For all commands:**
- Read the command file prompts to understand expectations
- Follow constitutional principles (Evidence, Thorough, Uncertainty)
- Output clear [GRAPH_UPDATE] blocks
- Verify your work before finishing

---

## Examples

### Example 1: Full Enrichment Workflow

```bash
# Check what needs enrichment
> /km-status

Output: 3 sparse entities found

# Enrich interactively
> /enrich-knowledge

Claude shows list, you select pyjwt_lib

[Claude researches...]

[GRAPH_UPDATE block output...]

✅ PyJWT Library enriched

# Verify resolution
> /km-status

Output: 2 sparse entities remaining (pyjwt_lib resolved)
```

### Example 2: Batch Validation

```bash
# Check validation issues
> /km-status

Output: 4 low-confidence nodes

# Validate all at once
> /validate-knowledge all

[Claude processes each node sequentially...]

Node 1: ✅ Verified (confidence 0.72 → 0.95)
Node 2: ⚠️  Marked as Uncertainty (unverifiable)
Node 3: ✅ Verified (confidence 0.80 → 0.90)
Node 4: 🔧 Corrected (incorrect claim fixed)

# Verify resolution
> /km-status

Output: All validation issues resolved
```

### Example 3: Targeted Fix

```bash
# You notice a specific issue
> /validate-knowledge auth_decision_oauth2

[Claude verifies the specific node...]

✅ Validation complete

# Continue working
(No need to run /km-status if you only fixed one specific issue)
```

---

## Testing Commands

### Manual Testing

1. **Create test issue**:
```bash
echo '{
  "issues": [{
    "type": "sparse_entity",
    "triad": "test",
    "node_id": "test_entity",
    "label": "Test Entity",
    "property_count": 1,
    "priority": "medium"
  }]
}' > .claude/km_queue.json
```

2. **Run command**:
```bash
/km-status
# Should show 1 issue

/enrich-knowledge test_entity
# Should enrich the entity
```

3. **Verify**:
```bash
cat .claude/km_queue.json
# Should be empty or issue removed
```

---

## Troubleshooting

### Command Not Found

**Problem**: `/km-status` returns "Unknown command"

**Solution**:
```bash
# Check command file exists
ls .claude/commands/km-status.md

# If missing, create it
# See command file examples in this doc
```

### No Issues Found

**Problem**: Commands report "No issues found" but you know there are issues

**Solution**:
```bash
# Check queue file exists and has issues
cat .claude/km_queue.json

# If empty, create a graph update to trigger detection
# (Make a change, hook will detect issues)
```

### Updates Not Saving

**Problem**: [GRAPH_UPDATE] output but graph not updating

**Solution**:
```bash
# Check on_stop.py hook is configured
cat .claude/settings.json | grep on_stop

# Check hook runs without errors
python3 .claude/hooks/on_stop.py <<< 'test'

# Verify sys.path includes src/ for imports
```

### Command Hangs

**Problem**: Command runs indefinitely

**Solution**:
- Commands may wait for user input
- Check if you need to respond to a prompt
- Press Ctrl+C to cancel if needed
- Re-run with specific target: `/enrich-knowledge node_id`

---

## Future Enhancements

### 1. Automated Command Scheduling

```bash
# Run KM maintenance daily
/km-status && /enrich-knowledge all && /validate-knowledge all
```

### 2. Batch Operations with Filters

```bash
/enrich-knowledge --triad=discovery
/validate-knowledge --priority=high
```

### 3. Command Chaining

```bash
/km-resolve-all  # Runs enrich + validate + status in sequence
```

### 4. Export Reports

```bash
/km-status --export=json
/km-status --export=html
```

---

## Related Documentation

- [Detection System](km-detection.md) - How issues are detected
- [Formatting System](km-formatting.md) - How issues are formatted
- [System Agents](km-system-agents.md) - Automated resolution
- [Fresh Context](km-fresh-context.md) - Agent context injection (Phase 5)

---

## Command Files

All command files located in `.claude/commands/`:
- `km-status.md` - Status reporting
- `enrich-knowledge.md` - Entity enrichment
- `validate-knowledge.md` - Claim validation

To customize, edit the markdown files directly.
