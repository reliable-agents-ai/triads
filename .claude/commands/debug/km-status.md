---
description: View current knowledge management issues
---

# Knowledge Management Status

You are displaying the current state of the Knowledge Management (KM) system.

## Your Task

1. **Check for KM queue file**: Read `.claude/km_queue.json`
2. **Check for KM status file**: Read `.claude/km_status.md`
3. **Display comprehensive status**

## Output Format

Provide a clear, organized report:

### Summary

- Total issues detected
- Breakdown by priority (high/medium)
- Breakdown by triad
- Breakdown by issue type

### Issues by Triad

Group issues by their triad and show:
- Node ID and label
- Issue type
- Priority
- Relevant details (property count, confidence, etc.)
- Which system agent handles it

### Recommendations

Based on the issues, suggest:
- Which issues to tackle first (high priority)
- Whether to invoke system agents automatically
- Any patterns you notice (e.g., "Many sparse entities in discovery triad")

## Example Output

```
# Knowledge Management Status Report

## Summary
- **Total Issues**: 7
- **High Priority**: 4 (2 low confidence, 2 missing evidence)
- **Medium Priority**: 3 (3 sparse entities)

**By Triad:**
- discovery: 4 issues
- design: 2 issues
- implementation: 1 issue

**By Type:**
- sparse_entity: 3 (handled by research-agent)
- low_confidence: 2 (handled by verification-agent)
- missing_evidence: 2 (handled by verification-agent)

---

## Discovery Triad (4 issues)

### High Priority

⚠️ **Authentication Decision** (`auth_decision_oauth2`)
- Type: low_confidence
- Current confidence: 0.72
- Agent: verification-agent
- Issue: Decision needs verification and stronger evidence

❗ **JWT Implementation** (`jwt_impl`)
- Type: missing_evidence
- Agent: verification-agent
- Issue: No citation for how JWT is implemented

### Medium Priority

🔍 **PyJWT Library** (`pyjwt_lib`)
- Type: sparse_entity
- Properties: 1 (needs at least 3)
- Agent: research-agent
- Issue: Needs enrichment with version, capabilities, usage patterns

🔍 **Redis Cache** (`redis_cache`)
- Type: sparse_entity
- Properties: 2
- Agent: research-agent

---

## Design Triad (2 issues)

### High Priority

⚠️ **Scaling Strategy** (`scaling_strategy`)
- Type: low_confidence
- Confidence: 0.78
- Agent: verification-agent

### Medium Priority

🔍 **Microservices Pattern** (`microservices_concept`)
- Type: sparse_entity
- Properties: 1
- Agent: research-agent

---

## Implementation Triad (1 issue)

### High Priority

❗ **Performance Claim** (`performance_improvement`)
- Type: missing_evidence
- Agent: verification-agent
- Issue: Claim that "API is 3x faster" lacks benchmarks

---

## Recommendations

1. **Start with High Priority Issues**: 4 issues need immediate attention
   - 2 low confidence nodes should be verified
   - 2 nodes missing evidence need citations

2. **Consider System Agents**:
   - Run verification-agent for the 4 high-priority issues
   - Run research-agent for the 3 sparse entities

3. **Pattern Noticed**: Discovery triad has the most issues (4/7)
   - Suggests initial research phase needs more thorough documentation
   - Consider slowing down discovery phase to add better evidence

4. **Invoke Agents**: Would you like me to start resolving these? I can:
   - `Start verification-agent: Verify the low-confidence node 'Authentication Decision'...`
   - `Start research-agent: Enrich the sparse entity 'PyJWT Library'...`
```

## Important Notes

- If no km_queue.json exists, report "No KM issues detected"
- If km_status.md exists but is empty, report "Status file exists but no issues"
- Show file paths so user can manually inspect: `.claude/km_queue.json`, `.claude/km_status.md`
- Do NOT fabricate issues - only report what's actually in the files
- If files don't exist or are empty, that's good news!

Begin your status report now.
