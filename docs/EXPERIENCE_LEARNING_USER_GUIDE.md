# Experience-Based Learning System - User Guide

## Overview

The **Experience-Based Learning System** enables the triads plugin to learn from mistakes automatically. When you correct Claude or when mistakes repeat, the system extracts lessons and prevents those same mistakes from happening again.

### The Problem It Solves

**Before**: You fix the same mistake multiple times. Claude forgets context between sessions.

**After**: Claude learns from corrections. Mistakes are prevented proactively through automatic knowledge injection.

### How It Works

```
Mistake → Correction → Lesson Extracted → User Reviews → Active → Prevents Future Mistakes
```

## Quick Start

### 1. Use Claude Normally

Just work with Claude Code as usual. The system runs automatically in the background.

### 2. When You Correct Claude

If Claude makes a mistake and you correct it:
```
You: "You forgot to update marketplace.json when bumping the version."
```

The system automatically:
- Detects your correction
- Extracts the lesson
- Creates a draft knowledge node
- Queues it for your review

### 3. Review Draft Lessons

Periodically run:
```
/knowledge-review-drafts
```

This shows all lessons the system has learned:
```markdown
# 📋 Draft Knowledge Review

**Total drafts**: 3
- CRITICAL: 1
- HIGH: 1
- MEDIUM: 1

## 1. [CRITICAL] Remember: marketplace.json

**Node ID**: `process_user_correction_20251017_141530`
**Learned from**: user_correction
**Created**: 2025-10-17T14:15:30

**Warning**:
- Condition: marketplace.json
- Consequence: Version mismatch when bumping versions
- Prevention: Always check marketplace.json during version bumps

**Actions**:
- ✅ Promote: `/knowledge-promote process_user_correction_20251017_141530`
- ❌ Archive: `/knowledge-archive process_user_correction_20251017_141530`
```

### 4. Promote or Archive

For each draft, decide:

**Promote** (make it active):
```
/knowledge-promote process_user_correction_20251017_141530
```

**Archive** (false positive):
```
/knowledge-archive process_user_correction_20251017_141530
```

### 5. See Lessons at Session Start

Next time you start Claude Code, you'll see CRITICAL lessons:

```markdown
================================================================================
# ⚠️  CRITICAL LESSONS LEARNED
================================================================================

## 1. Remember: marketplace.json

**Priority**: CRITICAL
**Type**: warning

**Warning**:
- Condition: marketplace.json
- Consequence: Version mismatch
- Prevention: Always check marketplace.json

**Applies when**: Tools: Write, Edit | Files: **/marketplace.json | Keywords: version

💡 TIP: Review these lessons before starting work.
================================================================================
```

### 6. Lessons Injected Automatically

When you try to perform an action that triggers a lesson, Claude sees it:

```markdown
================================================================================
# 🧠 EXPERIENCE-BASED KNOWLEDGE
================================================================================

Before using **Edit**, consider this learned knowledge:

⚠️ **Remember: marketplace.json**
**Priority**: CRITICAL

[Full warning details...]

**This knowledge was learned from previous experience.**
================================================================================
```

Claude now **prevents the mistake** before it happens!

## Detection Methods

The system learns in three ways:

### 1. User Corrections (Implicit Learning)

The system detects when you correct Claude using phrases like:

- "You forgot X"
- "You missed Y"
- "Why didn't you Z?"
- "You should have A"
- "Don't forget B"
- "Remember to C"

**Example**:
```
You: "You forgot to run tests before committing."
```

**Result**: Creates CRITICAL priority lesson about running tests

### 2. Repeated Mistakes (Implicit Learning)

The system detects patterns indicating repeated mistakes:

- "X again"
- "Another X was missing"
- "X is still missing"
- "Forgot X again"
- "Need to do X again"

**Example**:
```
You: "You need to update marketplace.json again - it's still at the old version."
```

**Result**: Creates HIGH priority lesson about marketplace.json

### 3. Explicit Lessons (Explicit Learning)

You or agents can create structured lessons using `[PROCESS_KNOWLEDGE]` blocks:

```markdown
[PROCESS_KNOWLEDGE]
type: checklist
label: Pre-Deployment Checklist
priority: CRITICAL
process_type: checklist
triad: deployment
trigger_conditions:
  tool_names: ["Write", "Edit"]
  file_patterns: ["**/version*"]
  action_keywords: ["deploy", "release"]
checklist:
  - item: Run full test suite required: true
  - item: Update CHANGELOG.md required: true
  - item: Bump all version files required: true
  - item: Create git tag required: true
[/PROCESS_KNOWLEDGE]
```

**Result**: Creates structured checklist that appears before deployment actions

## Priority Levels

### CRITICAL

- **When**: User corrections, deployment context, security issues
- **Where shown**: SessionStart + PreToolUse hooks
- **Impact**: Must be reviewed and fixed immediately

**Examples**:
- User said "you forgot X"
- Deployment-related mistakes
- Security vulnerabilities

### HIGH

- **When**: Repeated mistakes, security-related, performance issues
- **Where shown**: PreToolUse hooks
- **Impact**: Should be addressed soon

**Examples**:
- Mistake happened multiple times
- Security best practices
- Performance optimizations

### MEDIUM

- **When**: Code quality, refactoring suggestions
- **Where shown**: PreToolUse hooks
- **Impact**: Good to fix when convenient

**Examples**:
- Code organization
- Refactoring opportunities
- Documentation improvements

### LOW

- **When**: Uncertain or low-confidence detections
- **Where shown**: Draft review only (not injected)
- **Impact**: Review to determine if accurate

**Examples**:
- Ambiguous corrections
- Possible false positives
- Nice-to-have improvements

## Process Types

### Checklist

Multiple items to verify before proceeding:

```markdown
**Checklist**:
  □ Update plugin.json version field — 🔴 REQUIRED
  □ Update marketplace.json version — 🔴 REQUIRED
  □ Update pyproject.toml version — 🔴 REQUIRED
  □ Add CHANGELOG entry — 🟡 Optional
```

### Warning

Condition → Consequence → Prevention pattern:

```markdown
**Warning**:
- Condition: Bumping version without updating all files
- Consequence: Version mismatch in marketplace
- Prevention: Check all version files before committing
```

### Pattern

When → Then → Rationale pattern:

```markdown
**Pattern**:
- When: Making a breaking API change
- Then: Bump major version number
- Rationale: Semantic versioning convention for breaking changes
```

### Requirement

Must/should statements:

```markdown
**Requirement**:
- Must run tests before deploying
- Should update documentation when adding features
```

## CLI Commands

### `/knowledge-review-drafts`

**Purpose**: Review all draft lessons learned by the system

**Usage**:
```
/knowledge-review-drafts
```

**Output**: Shows all drafts grouped by priority with promote/archive actions

**When to use**:
- After a session where you corrected mistakes
- Periodically to review accumulated lessons
- Before a release to ensure quality lessons

### `/knowledge-promote <node_id>`

**Purpose**: Activate a draft lesson

**Usage**:
```
/knowledge-promote process_user_correction_20251017_141530
```

**Effect**:
- Changes status from "draft" to "active"
- Lesson will appear at SessionStart (if CRITICAL)
- Lesson will be injected by PreToolUse hooks
- Prevents the mistake from happening again

**When to use**:
- After reviewing a draft and confirming it's accurate
- When you want the system to prevent this mistake

### `/knowledge-archive <node_id>`

**Purpose**: Archive a false positive or irrelevant lesson

**Usage**:
```
/knowledge-archive process_repeated_mistake_20251017_141830
```

**Effect**:
- Changes status from "draft" to "archived"
- Lesson won't appear in reviews
- Lesson won't be injected by hooks
- Kept in graph for audit trail

**When to use**:
- When a detected lesson is incorrect (false positive)
- When a lesson is no longer relevant
- When you don't want this lesson active

## Best Practices

### 1. Review Drafts Regularly

Run `/knowledge-review-drafts` after sessions where you:
- Corrected Claude multiple times
- Noticed repeated mistakes
- Want to capture lessons learned

### 2. Be Specific When Correcting

Instead of:
```
You: "This is wrong."
```

Use:
```
You: "You forgot to update marketplace.json when bumping the version."
```

The system extracts better lessons from specific corrections.

### 3. Promote Accurate Lessons Quickly

High-quality lessons become more valuable when promoted:
- They prevent future mistakes immediately
- They guide Claude in next session
- They improve system intelligence over time

### 4. Archive False Positives

Don't leave bad drafts in the queue:
- Archive obvious false positives quickly
- This keeps your draft review clean
- Prevents confusion later

### 5. Use Explicit Lessons for Complex Knowledge

For complex checklists or patterns, create explicit `[PROCESS_KNOWLEDGE]` blocks:
- More structured than implicit learning
- Can include detailed trigger conditions
- Can specify required vs optional items

## Troubleshooting

### "I corrected Claude but no draft was created"

**Possible causes**:
1. Correction phrase didn't match detection patterns
2. Stop hook didn't fire
3. Lesson was extracted but merged with existing

**Solutions**:
- Use explicit correction phrases ("you forgot X")
- Check `.claude/graphs/*_graph.json` for draft nodes
- Run `/knowledge-review-drafts` to see all drafts

### "Lesson appears at wrong times"

**Cause**: Trigger conditions too broad

**Solution**:
1. Archive the lesson: `/knowledge-archive <node_id>`
2. Manually edit the graph JSON to fix trigger_conditions
3. Or let it stay archived and create a better explicit lesson

### "Too many drafts to review"

**Cause**: System is learning too much

**Solutions**:
- Review and promote/archive in batches
- Focus on CRITICAL and HIGH priority first
- Archive LOW priority drafts that aren't useful

### "SessionStart is slow"

**Cause**: Too many CRITICAL lessons

**Solutions**:
- Archive or downgrade some CRITICAL lessons
- Only keep the most important lessons at CRITICAL
- The system only shows top 5, so this is rare

### "PreToolUse not injecting lessons"

**Possible causes**:
1. Lesson is still draft (not promoted)
2. Trigger conditions don't match the action
3. PreToolUse hook not installed

**Solutions**:
- Check lesson status: should be "active"
- Review trigger_conditions in graph JSON
- Verify hook installed: `~/.claude/plugins/marketplaces/triads-marketplace/hooks/`

## Technical Details

### Where Lessons Are Stored

All lessons are stored in knowledge graphs:

```
.claude/graphs/
  ├── deployment_graph.json   # Deployment-related lessons
  ├── implementation_graph.json  # Implementation lessons
  └── default_graph.json      # General lessons
```

Each lesson is a Concept node with:
```json
{
  "id": "process_user_correction_20251017_141530",
  "type": "Concept",
  "label": "Remember: marketplace.json",
  "priority": "CRITICAL",
  "process_type": "warning",
  "status": "draft",  # or "active" or "archived"
  "trigger_conditions": {
    "tool_names": ["Write", "Edit"],
    "file_patterns": ["**/marketplace.json"],
    "action_keywords": ["version", "bump"]
  },
  "warning": {
    "condition": "...",
    "consequence": "...",
    "prevention": "..."
  }
}
```

### Hook Execution Flow

1. **SessionStart**: Displays CRITICAL lessons (if any)
2. **PreToolUse**: Before each tool, checks for relevant lessons
3. **Work happens**: Claude uses tools with lesson context
4. **Stop**: Analyzes conversation, extracts new lessons

### Performance

- **Query speed**: 0.1ms P95 (1000x better than 100ms target)
- **Hook overhead**: < 2ms per tool use
- **Extraction time**: < 1s even on large conversations
- **SessionStart impact**: Negligible (only if CRITICAL lessons exist)

## Advanced Usage

### Manual Lesson Creation

Create lessons manually by adding nodes to graphs:

1. Open `.claude/graphs/deployment_graph.json`
2. Add a Concept node with process_type
3. Include trigger_conditions
4. Set status to "active" (or "draft" for review)
5. Save the file

### Editing Lessons

Lessons can be edited manually:

1. Open the graph JSON file
2. Find the node by ID
3. Edit fields (label, priority, trigger_conditions, content)
4. Save the file

Changes take effect immediately.

### Sharing Lessons

Export lessons to share with team:

1. Copy the Concept node from your graph
2. Send the JSON to a teammate
3. They add it to their graph
4. Lesson is now shared!

### Lesson Templates

Create templates for common lesson types:

```json
{
  "type": "Concept",
  "process_type": "checklist",
  "priority": "HIGH",
  "status": "active",
  "trigger_conditions": {
    "tool_names": ["Write"],
    "file_patterns": ["**/*.py"],
    "action_keywords": ["test"]
  },
  "checklist": [
    {"item": "Write unit tests", "required": true},
    {"item": "Write integration tests", "required": false}
  ]
}
```

## FAQ

**Q: Will the system learn bad lessons?**
A: That's why lessons start as drafts. You must review and promote them.

**Q: Can I disable the system?**
A: Yes, remove the PreToolUse and Stop hooks from hooks.json.

**Q: How many lessons can the system handle?**
A: Thousands. The query engine is highly optimized (< 1ms queries).

**Q: What if I disagree with a lesson?**
A: Archive it with `/knowledge-archive <node_id>`.

**Q: Can I see what lessons Claude sees?**
A: Yes, the PreToolUse injection is visible in the conversation.

**Q: How do I reset the system?**
A: Delete draft/active lessons from graph JSON files.

**Q: Does this work with custom triads?**
A: Yes! Lessons are stored per-triad automatically.

## Support

For issues or questions:
- GitHub Issues: https://github.com/reliable-agents-ai/triads/issues
- Documentation: See `/docs` directory
- Demo: Run `python tests/test_km/demo_experience_flow.py`

---

**The system learns from your corrections to help prevent future mistakes. Happy learning!** 🎓
