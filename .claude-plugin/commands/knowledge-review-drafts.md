# Review Draft Knowledge

You are helping the user review **draft** process knowledge that was automatically learned from conversations.

## Your Task

1. **Search for draft knowledge**: Query all knowledge graphs for nodes with `status: "draft"`
2. **Display each draft** with:
   - Node ID
   - Label
   - Priority (CRITICAL, HIGH, MEDIUM, LOW)
   - Process type (checklist, pattern, warning, requirement)
   - Detection method (how it was learned)
   - Content (full checklist/pattern/warning details)
   - Triad where it's stored
   - Created date

3. **Group by priority**: Show CRITICAL first, then HIGH, then MEDIUM, then LOW

4. **For each draft, ask the user**:
   - Is this lesson accurate and useful?
   - Options:
     - ✅ **Promote** (make it active) - Use `/knowledge-promote <node_id>`
     - ❌ **Archive** (false positive) - Use `/knowledge-archive <node_id>`
     - ⏸️  **Keep as draft** (review later) - Do nothing

5. **Show statistics**:
   - Total drafts by priority
   - Breakdown by detection method (user_correction, repeated_mistake, explicit)
   - Breakdown by triad

## Implementation

Use the following approach:

1. **Load all graphs** from `.claude/graphs/`
2. **Filter nodes** where `status == "draft"`
3. **Sort** by priority (CRITICAL → HIGH → MEDIUM → LOW), then by created_at (newest first)
4. **Format output** in a clear, reviewable format

## Example Output

```markdown
# 📋 Draft Knowledge Review

**Total drafts**: 5
- CRITICAL: 2
- HIGH: 1
- MEDIUM: 1
- LOW: 1

---

## 1. [CRITICAL] Remember: marketplace.json

**Node ID**: `process_user_correction_20251017_141530`
**Triad**: deployment
**Learned from**: user_correction
**Created**: 2025-10-17T14:15:30

**Warning**:
- Condition: marketplace.json
- Consequence: User correction: forgot - marketplace.json
- Prevention: Verify before proceeding

**Trigger Conditions**:
- Tools: Write, Edit
- Keywords: marketplace

**Actions**:
- ✅ Promote: `/knowledge-promote process_user_correction_20251017_141530`
- ❌ Archive: `/knowledge-archive process_user_correction_20251017_141530`

---

[Continue for each draft...]
```

## Notes

- Draft lessons are created automatically by the experience learning system
- They start as drafts to prevent false positives
- Once promoted, they become active and will appear in PreToolUse hooks
- Archived lessons are marked with `status: "archived"` and won't be shown again
