# Experience-Based Learning Hook Usage Guide

**Status**: Active (Day 2 Complete)
**Version**: 0.7.0-alpha.1+
**Hook**: PreToolUse - on_pre_experience_injection.py

---

## Overview

The PreToolUse hook fires **before every tool execution** and injects relevant procedural knowledge (checklists, patterns, warnings) into the agent's context based on learned experience.

This is a **just-in-time learning system** that helps agents avoid repeating past mistakes.

---

## How It Works

### 1. Hook Fires Before Tool Use

When Claude Code is about to execute a tool (Write, Edit, Bash, etc.), the hook receives:

```json
{
  "tool_name": "Write",
  "tool_input": {"file_path": ".claude-plugin/plugin.json"},
  "cwd": "/Users/dev/project"
}
```

### 2. Query for Relevant Knowledge

The hook queries the ExperienceQueryEngine which:
- Loads all knowledge graphs from `.claude/graphs/`
- Filters to process knowledge nodes (nodes with `process_type`)
- Calculates relevance using structured scoring:
  - Tool name match: 40%
  - File pattern match: 40%
  - Action keywords: 10%
  - Context keywords: 10%
- Applies priority multipliers (CRITICAL = 2.0x, HIGH = 1.5x)
- Returns top 3 most relevant items

### 3. Format and Inject

If relevant knowledge found, the hook formats it and injects into stdout:

```
================================================================================
# 🧠 EXPERIENCE-BASED KNOWLEDGE
================================================================================

Before using **Write**, consider this learned knowledge:

⚠️ **CRITICAL: Version Bump File Checklist**
**Priority**: CRITICAL

**Checklist**:
  □ Update plugin.json version field (.claude-plugin/plugin.json) — 🔴 REQUIRED
  □ Update marketplace.json plugins[].version (.claude-plugin/marketplace.json) — 🔴 REQUIRED
  □ Update pyproject.toml project.version (pyproject.toml) — 🔴 REQUIRED
  □ Add CHANGELOG.md entry (CHANGELOG.md) — 🔴 REQUIRED

**Please verify all required items before proceeding.**

--------------------------------------------------------------------------------

**This knowledge was learned from previous experience.**
================================================================================
```

### 4. Agent Sees Knowledge Before Acting

The injected knowledge appears in the agent's context **before the tool executes**, allowing the agent to:
- Review procedural requirements
- Verify checklist items
- Follow established patterns
- Avoid known pitfalls

---

## When the Hook Fires

### Tools That Trigger Injection

- **Write**: Creating/overwriting files
- **Edit**: Modifying existing files
- **Bash**: Running shell commands
- **Any tool that modifies state**

### Tools That DON'T Trigger (Early Exit)

- **Read**: Reading files (read-only)
- **Grep**: Searching content (read-only)
- **Glob**: Finding files (read-only)

**Why early exit?** Read-only tools don't modify state, so process knowledge about safe modification is irrelevant. Early exit saves performance and avoids context clutter.

---

## Creating Process Knowledge

Process knowledge lives in knowledge graphs (`.claude/graphs/*.json`) as **Concept nodes** with `process_type`.

### Required Fields

```json
{
  "id": "process_unique_id",
  "type": "Concept",
  "label": "Human-readable title",
  "description": "What this process knowledge covers",
  "priority": "CRITICAL|HIGH|MEDIUM|LOW",
  "process_type": "checklist|pattern|warning|requirement",
  "trigger_conditions": {
    "tool_names": ["Write", "Edit"],
    "file_patterns": ["**/plugin.json", "**/*version*"],
    "action_keywords": ["version", "bump", "release"],
    "context_keywords": ["deployment", "publish"],
    "triad_names": ["deployment"]
  },
  "checklist": {
    "items": [
      {"item": "Do this", "required": true, "file": "path/to/file"}
    ]
  }
}
```

### Process Types

#### Checklist
For procedures with multiple steps:

```json
{
  "process_type": "checklist",
  "checklist": {
    "items": [
      {"item": "Update version in X", "required": true, "file": "X"},
      {"item": "Update version in Y", "required": true, "file": "Y"},
      {"item": "Add changelog entry", "required": true, "file": "CHANGELOG.md"}
    ]
  }
}
```

**Displays as**:
```
⚠️ **CRITICAL: Title**
**Priority**: CRITICAL

**Checklist**:
  □ Update version in X (X) — 🔴 REQUIRED
  □ Update version in Y (Y) — 🔴 REQUIRED
  □ Add changelog entry (CHANGELOG.md) — 🔴 REQUIRED
```

#### Pattern
For when/then guidance:

```json
{
  "process_type": "pattern",
  "pattern": {
    "when": "Modifying authentication code",
    "then": "Run security test suite and check for token leaks",
    "example": "pytest tests/security/ && grep -r 'token' logs/"
  }
}
```

**Displays as**:
```
ℹ️ **HIGH: Title**

**When**: Modifying authentication code
**Then**: Run security test suite and check for token leaks
**Example**: pytest tests/security/ && grep -r 'token' logs/
```

#### Warning
For risks and mitigation:

```json
{
  "process_type": "warning",
  "warning": {
    "risk": "Pushing to main without tests can break production",
    "mitigation": "Always run full test suite before pushing to main",
    "consequence": "Production outage, rollback required"
  }
}
```

**Displays as**:
```
⚠️ **HIGH WARNING: Title**

**Risk**: Pushing to main without tests can break production
**Mitigation**: Always run full test suite before pushing to main
**Consequence**: Production outage, rollback required
```

#### Requirement
For must-do rules:

```json
{
  "process_type": "requirement",
  "requirement": {
    "must": "All API endpoints must have rate limiting",
    "rationale": "Prevents DoS attacks and ensures fair usage"
  }
}
```

**Displays as**:
```
ℹ️ **MEDIUM REQUIREMENT: Title**

**Must**: All API endpoints must have rate limiting
**Rationale**: Prevents DoS attacks and ensures fair usage
```

---

## Trigger Conditions

Control when knowledge gets injected via `trigger_conditions`:

### Tool Names
```json
"tool_names": ["Write", "Edit"]
```
- Exact tool name match (40% relevance)
- Use `["*"]` to match any tool (20% relevance)

### File Patterns
```json
"file_patterns": ["**/plugin.json", "**/*version*", "**/CHANGELOG.md"]
```
- Glob patterns matched against file paths
- `**` matches any directory depth
- `*` matches any characters except `/`
- 40% relevance if matched

### Action Keywords
```json
"action_keywords": ["version", "bump", "release", "deploy"]
```
- Matched against tool input (lowercased)
- 10% relevance if any keyword found
- Good for detecting intent

### Context Keywords
```json
"context_keywords": ["deployment", "publish", "production"]
```
- Matched against description and tool input
- 10% relevance if any keyword found
- Good for domain context

### Triad Names
```json
"triad_names": ["deployment", "design"]
```
- Organizational hint (which triad this applies to)
- Not used for relevance scoring (yet)

---

## Priority Levels

Priority affects both display and relevance scoring:

| Priority | Multiplier | Display | When to Use |
|----------|-----------|---------|-------------|
| **CRITICAL** | 2.0x | Red ⚠️, === borders, ALL CAPS | Mission-critical procedures, data loss risks, security issues |
| **HIGH** | 1.5x | Yellow ⚠️, --- borders | Important but not critical, best practices |
| **MEDIUM** | 1.0x | Blue ℹ️, --- borders | Standard procedures, helpful reminders |
| **LOW** | 0.5x | Gray ℹ️, no borders | Nice-to-know info, minor optimizations |

**Example**: A CRITICAL item with 0.2 base relevance gets boosted to 0.4 (above 0.4 threshold), so it gets injected. A LOW item with 0.2 base relevance drops to 0.1 (below threshold), so it's filtered out.

**Use CRITICAL sparingly** - only for things that can cause data loss, security issues, or break production.

---

## Relevance Threshold

**Current threshold**: 0.4 (after priority multiplier)

This means:
- CRITICAL items need only 0.2 base relevance (0.2 * 2.0 = 0.4)
- HIGH items need 0.27 base relevance (0.27 * 1.5 = 0.4)
- MEDIUM items need 0.4 base relevance (0.4 * 1.0 = 0.4)
- LOW items need 0.8 base relevance (0.8 * 0.5 = 0.4)

**Base relevance calculation**:
- Tool match: +0.4
- File match: +0.4
- Action keyword match: +0.1
- Context keyword match: +0.1
- **Total possible**: 1.0

**Example (Version Bump Checklist)**:
- Tool: Write → +0.4 (exact match)
- File: plugin.json matches `**/plugin.json` → +0.4 (pattern match)
- Base: 0.8
- Priority: CRITICAL (2.0x) → 0.8 * 2.0 = **1.6** (well above 0.4 threshold!)

---

## Top 3 Limit

The hook injects **at most 3 items** per tool use to avoid context pollution.

**Why 3?**
- More than 3 overwhelms the agent
- Top 3 covers most important knowledge
- Context window is precious

**Sorting**:
1. Priority first (CRITICAL → HIGH → MEDIUM → LOW)
2. Relevance score second (higher → lower)

So you'll always see the most critical, most relevant items first.

---

## Performance

### Current Metrics

- **Query engine**: ~0.1ms P95 (1000x better than 100ms target!)
- **Hook total**: < 200ms including subprocess overhead
- **Actual hook logic**: ~1-2ms (formatting + query)
- **Subprocess overhead**: ~10-20ms (unavoidable)

### Optimization Tips

1. **Keep graphs small**: Fewer nodes = faster queries
2. **Cache is automatic**: First query loads graphs, subsequent queries use cache
3. **Early exit helps**: Hook doesn't query for Read/Grep/Glob
4. **Simple patterns**: Complex regex in `file_patterns` slows matching

---

## Error Handling

The hook **NEVER blocks tool execution**:

```python
try:
    # ... query and inject logic ...
except Exception as e:
    print(f"Experience injection error: {e}", file=sys.stderr)
finally:
    sys.exit(0)  # ALWAYS exit successfully
```

**What happens on errors**:
- Error logged to stderr
- No knowledge injected (empty stdout)
- Tool executes normally

**Possible errors**:
- Invalid JSON in graph files → logged, tool continues
- Missing graph directory → logged, tool continues
- Query engine crash → logged, tool continues

**Tool execution is sacred** - hook failures must never prevent tools from running.

---

## Testing

### Manual Test

```bash
echo '{
  "tool_name": "Write",
  "tool_input": {"file_path": ".claude-plugin/plugin.json"},
  "cwd": "/Users/dev/project"
}' | python3 hooks/on_pre_experience_injection.py
```

Should output the Version Bump Checklist.

### Test with Different Tool

```bash
echo '{
  "tool_name": "Bash",
  "tool_input": {"command": "ls -la"},
  "cwd": "/Users/dev/project"
}' | python3 hooks/on_pre_experience_injection.py
```

Should output nothing (no relevant knowledge for Bash).

### Verify Hook is Active

In a Claude Code session:
1. Try to Write to `.claude-plugin/plugin.json`
2. Before tool executes, you should see Version Bump Checklist appear
3. Checklist should mention marketplace.json (the critical lesson!)

---

## Troubleshooting

### Hook Not Firing

**Check**:
1. Is hook installed? `ls ~/.claude/plugins/marketplaces/triads-marketplace/hooks/`
2. Is hooks.json correct? `cat ~/.claude/plugins/marketplaces/triads-marketplace/hooks/hooks.json`
3. Check stderr: `tail -f ~/.claude/logs/*.log | grep experience`

### No Knowledge Injected

**Check**:
1. Does graph exist? `ls .claude/graphs/*.json`
2. Does node have `process_type`? `grep process_type .claude/graphs/*.json`
3. Does node have `trigger_conditions`? `grep trigger_conditions .claude/graphs/*.json`
4. Manual test: Run hook directly with mock input (see Testing section)

### Wrong Knowledge Injected

**Check**:
1. Relevance scoring: Add debug output to show scores
2. Trigger conditions: Verify tool/file/keywords match
3. Priority: CRITICAL items have 2.0x boost, might override relevance

### Hook Slow

**Check**:
1. Graph size: `wc -l .claude/graphs/*.json` (should be < 1000 lines each)
2. Query time: Add timing output to hook
3. Subprocess overhead: Expected ~10-20ms

---

## Best Practices

### Writing Process Knowledge

1. **Be specific with trigger_conditions**
   - Don't use `["*"]` for tool_names unless truly universal
   - Use precise file patterns (e.g., `**/plugin.json` not `**/*.json`)
   - Include action keywords that indicate intent

2. **Use appropriate priority**
   - CRITICAL: Data loss, security, production breaks
   - HIGH: Important best practices, common mistakes
   - MEDIUM: Standard procedures, helpful reminders
   - LOW: Nice-to-know, optimizations

3. **Keep checklists concise**
   - 3-5 items max
   - Mark truly required items as `"required": true`
   - Include file references for clarity

4. **Test your knowledge nodes**
   - Manual test with mock hook input
   - Verify relevance scoring works as expected
   - Check formatting looks good

### Organizing Knowledge

1. **One graph per triad** (deployment_graph.json, design_graph.json, etc.)
2. **Group related knowledge** (all version bumping in one node)
3. **Use consistent node IDs** (`process_{topic}_{date}`)
4. **Update existing nodes** rather than creating duplicates

---

## Examples

### Example 1: Version Bump Checklist (Existing)

**Location**: `.claude/graphs/deployment_graph.json`

**Triggers on**:
- Write or Edit to plugin.json, marketplace.json, pyproject.toml
- Keywords: version, bump, release, update

**Result**: Shows checklist before modifying version files

### Example 2: Git Commit Checklist (Hypothetical)

```json
{
  "id": "process_git_commit_checklist_2025-10-17",
  "type": "Concept",
  "label": "Pre-Commit Checklist",
  "description": "Checklist to verify before creating git commits",
  "priority": "HIGH",
  "process_type": "checklist",
  "trigger_conditions": {
    "tool_names": ["Bash"],
    "file_patterns": ["**/*"],
    "action_keywords": ["git commit", "commit -m"],
    "context_keywords": ["commit", "git"]
  },
  "checklist": {
    "items": [
      {"item": "Run test suite", "required": true, "file": "pytest"},
      {"item": "Run linter", "required": true, "file": "ruff check"},
      {"item": "Check for debug statements", "required": true, "file": "grep -r 'console.log\\|debugger'"},
      {"item": "Verify commit message follows conventions", "required": false}
    ]
  }
}
```

**Would trigger**: Before `git commit -m "..."`

### Example 3: API Security Pattern (Hypothetical)

```json
{
  "id": "process_api_security_pattern_2025-10-17",
  "type": "Concept",
  "label": "API Security Pattern",
  "description": "Security checks when modifying API endpoints",
  "priority": "CRITICAL",
  "process_type": "pattern",
  "trigger_conditions": {
    "tool_names": ["Write", "Edit"],
    "file_patterns": ["**/api/**/*.py", "**/routes/**/*.py"],
    "action_keywords": ["endpoint", "route", "api"],
    "context_keywords": ["authentication", "authorization", "security"]
  },
  "pattern": {
    "when": "Creating or modifying API endpoints",
    "then": "Ensure authentication middleware, rate limiting, and input validation are present",
    "example": "@require_auth\\n@rate_limit(calls=100, period=60)\\n@validate_input(schema)"
  }
}
```

**Would trigger**: Before modifying files in `api/` or `routes/` directories

---

## Future Enhancements (Day 3+)

Day 3 will add **lesson extraction** to the Stop hook:
- Detect failed operations (test failures, git hook failures)
- Extract lessons from failure patterns
- Automatically create new process knowledge nodes
- Close the learning loop!

This will enable the system to **learn from mistakes automatically** without manual knowledge creation.

---

## Summary

The experience-based learning hook provides **just-in-time procedural knowledge** to help agents avoid repeating past mistakes:

✅ **Fires before every tool use** (except read-only tools)
✅ **Queries for relevant knowledge** (priority-weighted relevance scoring)
✅ **Injects top 3 items** (avoids context pollution)
✅ **NEVER blocks tools** (always exits 0, even on errors)
✅ **Fast** (< 2ms hook logic, ~0.1ms query)
✅ **Extensible** (create new knowledge nodes in graphs)

**Current use case**: Version Bump Checklist ensures marketplace.json is never forgotten again!

**File**: `hooks/on_pre_experience_injection.py`
**Config**: `hooks/hooks.json`
**Tests**: `tests/test_km/test_pre_tool_use_hook.py` (19 passing)
**Status**: Active ✅
