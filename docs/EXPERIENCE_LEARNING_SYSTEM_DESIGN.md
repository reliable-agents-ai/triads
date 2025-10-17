# Experience-Based Learning System Design

**Version**: 1.0
**Date**: 2025-10-17
**Status**: Design Phase
**Design Bridge Agent**: Architectural evaluation complete

---

## Executive Summary

**Problem**: Knowledge graphs capture history (what was done) but not procedures (how to do things). During v0.7.0-alpha.1 release, we missed updating `marketplace.json` despite having accumulated knowledge. The checklist was created AFTER the mistake, not proactively consulted BEFORE the action.

**Solution**: An experience-based learning system that:
1. **Learns from mistakes** - Automatically captures lessons as process knowledge
2. **Consults experience** - Queries knowledge graphs BEFORE tool execution
3. **Applies lessons proactively** - Injects relevant checklists/warnings into context

**Key Discovery**: PreToolUse hooks are functional and provide the ideal injection point (previously documented as broken).

**Architecture**: Three-component system:
- **Process Knowledge Schema** - Store procedural knowledge in graph Concept nodes
- **Knowledge Query Engine** - Fast relevance-scored lookup (< 100ms)
- **Three-Hook System** - PreToolUse (inject), Stop (learn), SessionStart (display CRITICAL)

**Timeline**: 5 days (validated implementation phasing)

**Risk Level**: Medium (performance-sensitive, but with graceful degradation)

---

## Table of Contents

1. [ADR-001: Hook Selection for Experience Injection](#adr-001-hook-selection-for-experience-injection)
2. [ADR-002: Process Knowledge Schema Design](#adr-002-process-knowledge-schema-design)
3. [ADR-003: Knowledge Query and Relevance Algorithm](#adr-003-knowledge-query-and-relevance-algorithm)
4. [ADR-004: Lesson Extraction and Learning Mechanism](#adr-004-lesson-extraction-and-learning-mechanism)
5. [ADR-005: Process Knowledge Priority System](#adr-005-process-knowledge-priority-system)
6. [Risk Analysis](#risk-analysis)
7. [Implementation Roadmap](#implementation-roadmap)
8. [Component Specifications](#component-specifications)
9. [Testing Strategy](#testing-strategy)
10. [Success Metrics](#success-metrics)

---

# ADR-001: Hook Selection for Experience Injection

**Status**: Accepted
**Date**: 2025-10-17
**Deciders**: Design Bridge Agent
**Consulted**: PreToolUse test logs, hooks/on_stop.py, hooks/session_start.py

## Context and Problem Statement

We need to inject relevant process knowledge (checklists, warnings, patterns) into agent context BEFORE actions that could benefit from experience. The question is: which Claude Code hook(s) should we use?

**Options**:
1. PreToolUse - Fires before every tool execution
2. SessionStart - Fires once at session start
3. UserPromptSubmit - Fires after each user message
4. Stop - Fires after Claude's response (not for injection)

## Decision Drivers

- **Timing**: Knowledge must be injected BEFORE the action occurs
- **Precision**: Only inject when relevant (not clutter every action)
- **Performance**: Hook must complete < 100ms (P95)
- **Coverage**: Must catch file modifications, git operations, deployments
- **Reliability**: Hook must be stable and not block tool execution

## Considered Options

### Option 1: PreToolUse Hook (SELECTED)

**How it works**:
- Fires before EVERY tool execution (Read, Write, Edit, Bash, etc.)
- Receives: `tool_name`, `tool_input`, `session_id`, `cwd`, `permission_mode`
- Output to stdout → injected as additional context for tool execution

**Pros**:
- ✅ **Perfect timing**: Inject exactly before action (e.g., before Write to version file)
- ✅ **High precision**: Can filter by tool_name + file patterns + parameters
- ✅ **Maximum coverage**: Catches all file operations, git commands, test runs
- ✅ **Proven functional**: Verified via test logs (.claude/hooks/pre_tool_use_test.log)
- ✅ **Rich context**: Full tool parameters available for relevance matching

**Cons**:
- ⚠️ **Performance-sensitive**: Fires FREQUENTLY (every tool use)
- ⚠️ **Latency critical**: < 100ms requirement to avoid UX impact
- ⚠️ **Potential noise**: Must filter aggressively to prevent clutter

**Relevance Example**:
```json
{
  "tool_name": "Write",
  "tool_input": {
    "file_path": "/path/to/plugin.json"
  }
}
```

Query would match:
- `tool_names: ["Write", "Edit"]`
- `file_patterns: ["**/plugin.json", "**/*version*"]`
- Inject: "Version Bump File Checklist" (CRITICAL priority)

### Option 2: SessionStart Hook

**How it works**:
- Fires ONCE when session starts
- No per-action context
- Currently used for routing directives + graph summaries

**Pros**:
- ✅ **No performance impact**: Fires only once
- ✅ **Already implemented**: Existing infrastructure
- ✅ **Good for general awareness**: Show CRITICAL items upfront

**Cons**:
- ❌ **Wrong timing**: Too early, not before specific actions
- ❌ **No precision**: Can't filter by tool or file
- ❌ **Easy to miss**: Large context dump at start, not when relevant
- ❌ **No refresh**: Knowledge added mid-session won't appear

**Verdict**: **Complementary, not primary**. Use for CRITICAL priority warnings, but not action-specific injection.

### Option 3: UserPromptSubmit Hook

**How it works**:
- Fires after user submits message, before Claude processes
- Receives user message content
- Could inject based on keywords in prompt

**Pros**:
- ✅ **Contextual**: Based on user's stated intent
- ✅ **Less frequent**: Only on user messages (not every tool)

**Cons**:
- ❌ **Wrong timing**: Fires before planning, not before execution
- ❌ **No tool context**: Can't see file paths, tool names
- ❌ **Keyword matching limited**: "bump version" might not appear in prompt
- ❌ **Not action-bound**: User might ask "how to deploy?" but not actually deploy

**Verdict**: **Rejected**. Too early and too vague.

### Option 4: Multiple Hook Strategy

**Hybrid approach**:
- **PreToolUse**: Primary injection (action-specific, high precision)
- **SessionStart**: Secondary display (CRITICAL priority items only)
- **Stop**: Learning (extract lessons, create process knowledge)

**Pros**:
- ✅ **Best of both**: Precision + awareness
- ✅ **Graceful degradation**: If PreToolUse fails, SessionStart still shows CRITICAL
- ✅ **Complete lifecycle**: Learn (Stop), Store (graph), Display (SessionStart), Apply (PreToolUse)

**Cons**:
- ⚠️ **Complexity**: Three hooks to maintain
- ⚠️ **Potential redundancy**: Same knowledge shown twice

**Mitigation**:
- SessionStart: ONLY show CRITICAL priority (< 5 items expected)
- PreToolUse: Show CRITICAL + HIGH + MEDIUM (filtered by relevance)
- Deduplication: PreToolUse can check if already shown in session

## Decision Outcome

**Chosen option**: **"Multiple Hook Strategy" (PreToolUse + SessionStart + Stop)**

### Primary Hook: PreToolUse

**Decision**: Use PreToolUse as PRIMARY injection hook for experience-based learning.

**Rationale**:
1. **Timing is critical**: The marketplace.json mistake demonstrates we need knowledge EXACTLY before the action
2. **Context is available**: File paths, tool names enable precise relevance matching
3. **Performance is achievable**: Target < 100ms via:
   - Lazy graph loading (cache in memory)
   - Fast string matching (no regex for hot path)
   - Early exit on irrelevant tools (skip Read, skip AskUserQuestion)
   - Top-3 results only (not full result set)
4. **Hook is functional**: Test logs confirm PreToolUse works reliably
5. **Graceful degradation**: Hook failure doesn't block tool execution (exit 0 always)

### Supporting Hook: SessionStart

**Decision**: Enhance existing SessionStart to show CRITICAL priority process knowledge.

**Rationale**:
1. **Awareness**: User sees critical procedures at session start
2. **Low cost**: Runs once, no performance impact
3. **Already exists**: SessionStart infrastructure in place
4. **Redundancy is acceptable**: CRITICAL items worth showing twice

### Learning Hook: Stop

**Decision**: Extend existing Stop hook to detect and extract lessons from conversation.

**Rationale**:
1. **Already captures graph updates**: Stop hook scans for [GRAPH_UPDATE] blocks
2. **Natural fit**: Lessons learned are captured as process knowledge nodes
3. **Human-in-loop**: User can confirm/reject learned lessons via review

## Consequences

### Positive

- **Maximum precision**: Process knowledge injected exactly when needed
- **Minimal clutter**: Relevance scoring filters out irrelevant knowledge
- **Complete learning loop**: Detect lessons → Store as process knowledge → Query on relevant actions → Prevent repeated mistakes
- **Layered redundancy**: CRITICAL items shown at SessionStart AND PreToolUse

### Negative

- **Performance risk**: PreToolUse fires frequently, must be FAST (< 100ms target)
- **Increased complexity**: Three hooks to maintain instead of one
- **Potential for noise**: Over-injection if relevance threshold too low

### Mitigation Strategies

**Performance**:
- Cache graphs in memory (singleton pattern)
- Skip irrelevant tools early (whitelist: Write, Edit, Bash, NotebookEdit)
- Fast path for no process knowledge (exit immediately if no Concept nodes with process_type)
- Benchmark continuously (log slow queries > 100ms to stderr)

**Complexity**:
- Shared utility library (`src/triads/km/experience_query.py`)
- Comprehensive tests for query engine
- Clear separation: PreToolUse = query, Stop = learn, SessionStart = display

**Noise**:
- Conservative relevance threshold (0.7 minimum)
- Top-3 results max
- Priority-weighted ranking (CRITICAL > HIGH > MEDIUM > LOW)
- User can disable via environment variable: `DISABLE_EXPERIENCE_INJECTION=1`

## Validation

**Test Case 1: Version Bump Scenario**

```bash
# Tool execution
tool_name: "Write"
tool_input: {
  "file_path": "/path/to/pyproject.toml",
  "content": "version = \"0.8.0\"..."
}

# Expected behavior
PreToolUse hook fires → queries graphs → matches:
  - Node: "Version Bump File Checklist" (CRITICAL)
  - Relevance: 0.95 (matches file_pattern "*version*", tool "Write")

→ Injects before Write:
"""
⚠️ CRITICAL PROCESS KNOWLEDGE

Version Bump File Checklist:
- [ ] pyproject.toml (version field)
- [ ] plugin.json (version field)
- [ ] marketplace.json (current_version)
- [ ] CHANGELOG.md (new section)
"""

→ Agent sees checklist BEFORE writing file
→ Remembers to update ALL version files
→ Mistake prevented
```

**Test Case 2: Irrelevant Tool (Read)**

```bash
# Tool execution
tool_name: "Read"
tool_input: {
  "file_path": "/path/to/README.md"
}

# Expected behavior
PreToolUse hook fires → early exit (Read not in whitelist) → < 1ms
No injection (reading doesn't need process knowledge)
```

**Test Case 3: No Process Knowledge**

```bash
# New project, no process knowledge nodes yet
PreToolUse hook fires → queries graphs → no Concept nodes with process_type
→ Early exit → < 5ms
```

## References

- Test logs: `/Users/iainnb/Documents/repos/triads/.claude/hooks/pre_tool_use_test.log`
- Existing Stop hook: `hooks/on_stop.py` (lines 530-699)
- Existing SessionStart hook: `hooks/session_start.py` (lines 304-401)
- Deployment graph with process knowledge: `.claude/graphs/deployment_graph.json` (node: process_version_bump_checklist_2025-10-17)

---

# ADR-002: Process Knowledge Schema Design

**Status**: Accepted
**Date**: 2025-10-17
**Deciders**: Design Bridge Agent

## Context and Problem Statement

We need a schema to represent procedural knowledge (how to do things) that can:
1. Be stored in existing knowledge graphs (no new node types)
2. Support different knowledge types (checklists, patterns, warnings, requirements)
3. Enable precise relevance matching (tool names, file patterns, keywords)
4. Be human-readable and editable
5. Be automatically generated from conversation analysis

## Decision Drivers

- **Backward compatibility**: Must work with existing graph structure
- **Expressiveness**: Must capture diverse procedural knowledge
- **Queryability**: Must support fast relevance matching
- **Simplicity**: Must be easy for LLMs to generate and humans to understand
- **Flexibility**: Must handle future knowledge types without schema changes

## Schema Design

### Core Node Structure

**Node Type**: `Concept` (existing type, no new type needed)

**Required Fields** (standard graph fields):
```json
{
  "id": "process_{domain}_{purpose}_{timestamp}",
  "type": "Concept",
  "label": "{Human-readable title}",
  "description": "{What this process knowledge is about}",
  "confidence": 1.0,
  "evidence": "{Where this lesson came from}",
  "created_by": "{agent or 'claude-code-session'}",
  "created_at": "{ISO timestamp}"
}
```

**Process Knowledge Extensions** (optional fields for Concept nodes):
```json
{
  "process_type": "checklist|pattern|warning|requirement",
  "priority": "CRITICAL|HIGH|MEDIUM|LOW",

  "trigger_conditions": {
    "tool_names": ["Write", "Edit", "Bash"],
    "file_patterns": ["**/plugin.json", "**/*version*"],
    "action_keywords": ["version bump", "release", "deploy"],
    "context_keywords": ["deployment", "migration"],
    "triad_names": ["deployment", "garden-tending"]
  },

  // Type-specific content (only one populated based on process_type)
  "checklist": {
    "title": "Version Bump Complete Checklist",
    "items": [
      "pyproject.toml (version field)",
      "plugin.json (version field)",
      "marketplace.json (current_version)",
      "CHANGELOG.md (new version section)"
    ],
    "format": "checkbox|numbered|bulleted"
  },

  "pattern": {
    "situation": "When deploying a new release",
    "action": "Always update marketplace.json after updating plugin.json",
    "rationale": "Marketplace.json is consumed by marketplace, must stay in sync",
    "example": "See v0.7.0-alpha.1 release where this was missed"
  },

  "warning": {
    "risk": "Forgetting to update marketplace.json causes marketplace to show old version",
    "severity": "high",
    "detection": "User report or marketplace listing check",
    "mitigation": "Use Version Bump Checklist before every release"
  },

  "requirement": {
    "constraint": "All version numbers must be updated atomically",
    "rationale": "Prevents version mismatch between components",
    "validation": "grep -r 'version.*0.7.0' to verify all updated"
  }
}
```

### Trigger Conditions Explained

**Purpose**: Enable fast, precise relevance matching in PreToolUse hook

**Fields**:

1. **`tool_names`** (list of strings):
   - Which Claude Code tools trigger this knowledge?
   - Examples: `["Write", "Edit", "NotebookEdit"]`, `["Bash"]`
   - Matching: Exact match against `tool_name` from PreToolUse input
   - Use case: "Version Bump Checklist" triggers on Write/Edit only

2. **`file_patterns`** (list of glob patterns):
   - Which file paths trigger this knowledge?
   - Examples: `["**/plugin.json"]`, `["**/*version*"]`, `["**/tests/**/*.py"]`
   - Matching: fnmatch.fnmatch(file_path, pattern)
   - Use case: "Plugin Schema Validation" triggers on any plugin.json file

3. **`action_keywords`** (list of strings):
   - Which action descriptions trigger this knowledge?
   - Examples: `["version bump", "release", "deploy", "migrate"]`
   - Matching: Case-insensitive substring in conversation context
   - Use case: "Deployment Checklist" triggers when user says "ready to release"

4. **`context_keywords`** (list of strings):
   - Which conversation topics trigger this knowledge?
   - Examples: `["deployment", "refactoring", "security", "performance"]`
   - Matching: Case-insensitive substring in recent messages
   - Use case: "Security Best Practices" triggers in security discussions

5. **`triad_names`** (list of strings):
   - Which triads use this knowledge?
   - Examples: `["deployment"]`, `["garden-tending", "implementation"]`
   - Matching: Exact match against current active triad
   - Use case: "Deployment-specific patterns" only trigger in deployment triad

**Matching Strategy** (see ADR-003):
- ALL conditions are OR-ed (any match counts)
- Relevance score increases with number of matches
- Priority weight applied after relevance calculation

### Process Types

#### 1. Checklist

**When to use**: Step-by-step procedures that must be completed in order

**Structure**:
```json
{
  "process_type": "checklist",
  "checklist": {
    "title": "Database Migration Checklist",
    "items": [
      "Backup production database",
      "Test migration on staging",
      "Schedule maintenance window",
      "Run migration script",
      "Verify data integrity",
      "Update API contracts",
      "Notify dependent services"
    ],
    "format": "checkbox"
  }
}
```

**Display Format** (injected into context):
```
DATABASE MIGRATION CHECKLIST

Before proceeding, verify:
- [ ] Backup production database
- [ ] Test migration on staging
- [ ] Schedule maintenance window
- [ ] Run migration script
- [ ] Verify data integrity
- [ ] Update API contracts
- [ ] Notify dependent services
```

#### 2. Pattern

**When to use**: "When X, do Y" procedural guidance

**Structure**:
```json
{
  "process_type": "pattern",
  "pattern": {
    "situation": "When refactoring code",
    "action": "Always run full test suite before committing",
    "rationale": "Prevents regressions from propagating",
    "example": "v0.6.0 refactoring broke import detection due to skipped tests"
  }
}
```

**Display Format**:
```
PATTERN: Code Refactoring

When: Refactoring code
Do: Always run full test suite before committing
Why: Prevents regressions from propagating

Example: v0.6.0 refactoring broke import detection due to skipped tests
```

#### 3. Warning

**When to use**: Risks to be aware of during specific actions

**Structure**:
```json
{
  "process_type": "warning",
  "warning": {
    "risk": "Editing agent prompts without testing breaks agent behavior",
    "severity": "high",
    "detection": "Agent produces incorrect outputs or fails to invoke",
    "mitigation": "Test agent with sample inputs after every prompt change"
  }
}
```

**Display Format**:
```
⚠️ WARNING: Agent Prompt Editing

Risk: Editing agent prompts without testing breaks agent behavior
Severity: HIGH
How to detect: Agent produces incorrect outputs or fails to invoke
Mitigation: Test agent with sample inputs after every prompt change
```

#### 4. Requirement

**When to use**: Hard constraints that must be satisfied

**Structure**:
```json
{
  "process_type": "requirement",
  "requirement": {
    "constraint": "All public APIs must have docstrings with examples",
    "rationale": "Enables auto-generated documentation and Claude Code assistance",
    "validation": "ruff check --select D (docstring checks)"
  }
}
```

**Display Format**:
```
REQUIREMENT: API Documentation

Constraint: All public APIs must have docstrings with examples
Why: Enables auto-generated documentation and Claude Code assistance
Verify with: ruff check --select D (docstring checks)
```

## Considered Alternatives

### Alternative 1: New Node Type "Process"

**Idea**: Create a new node type specifically for process knowledge

**Pros**:
- ✅ Clear semantic distinction
- ✅ Could have Process-specific fields in graph schema

**Cons**:
- ❌ **Breaking change**: Requires graph schema migration
- ❌ **Complexity**: Need to update all graph access code
- ❌ **Overkill**: Concept nodes already support arbitrary properties
- ❌ **Not backward compatible**: Old graphs wouldn't have Process nodes

**Verdict**: **Rejected**. Concept nodes are flexible enough, no need for new type.

### Alternative 2: Separate Process Knowledge Files

**Idea**: Store process knowledge outside graphs (e.g., `.claude/procedures/*.json`)

**Pros**:
- ✅ Easier to edit manually (separate files)
- ✅ No graph pollution with meta-knowledge

**Cons**:
- ❌ **Fragmentation**: Knowledge split across graph + files
- ❌ **No relationships**: Can't link process to entities/decisions via edges
- ❌ **No history**: Graphs track when/who created knowledge
- ❌ **Extra loading**: Query engine needs to load graphs AND files

**Verdict**: **Rejected**. Graphs are the single source of truth for knowledge.

### Alternative 3: Flat String Fields (No Structured trigger_conditions)

**Idea**: Store trigger conditions as plain text description

```json
{
  "when_to_apply": "Use this when writing to version-related files during deployment"
}
```

**Pros**:
- ✅ Simpler schema
- ✅ More flexible (natural language)

**Cons**:
- ❌ **Not queryable**: Can't efficiently match tool_name or file_path
- ❌ **Ambiguous**: "version-related files" requires NLP to interpret
- ❌ **Performance**: Would need LLM inference for every match (too slow)
- ❌ **Not deterministic**: Same input might match differently

**Verdict**: **Rejected**. Structured trigger conditions enable fast, deterministic matching.

## Decision Outcome

**Chosen option**: **Concept nodes with structured trigger_conditions and typed process knowledge**

### Rationale

1. **Backward compatible**: Uses existing Concept node type
2. **Queryable**: Structured trigger_conditions enable fast matching (< 100ms)
3. **Expressive**: Four process types cover diverse procedural knowledge
4. **Flexible**: Can add new process types without schema changes
5. **Human-readable**: JSON structure is clear and editable
6. **LLM-friendly**: Stop hook can generate these structures from conversation

### Example: Version Bump Checklist (Complete Node)

```json
{
  "id": "process_version_bump_checklist_2025-10-17",
  "type": "Concept",
  "label": "Version Bump File Checklist",
  "description": "Complete checklist of ALL files that must be updated when bumping version. This is procedural knowledge that should be consulted before every release.",
  "confidence": 1.0,
  "evidence": "Missed marketplace.json in v0.7.0-alpha.1 initial release (caught by user)",
  "created_by": "claude-code-session",
  "created_at": "2025-10-17T12:14:08.181048",

  "process_type": "checklist",
  "priority": "CRITICAL",

  "trigger_conditions": {
    "tool_names": ["Write", "Edit"],
    "file_patterns": [
      "**/pyproject.toml",
      "**/plugin.json",
      "**/marketplace.json",
      "**/*version*"
    ],
    "action_keywords": ["version bump", "release", "deploy", "update version"],
    "context_keywords": ["deployment", "release"],
    "triad_names": ["deployment"]
  },

  "checklist": {
    "title": "Version Bump Complete Checklist",
    "items": [
      "pyproject.toml (version field in [project] section)",
      "plugin.json (version field in root object)",
      "marketplace.json (current_version field)",
      "CHANGELOG.md (add new version section with changes)"
    ],
    "format": "checkbox"
  }
}
```

## Consequences

### Positive

- **Fast querying**: Structured trigger_conditions enable O(n) scan of process knowledge nodes (n = small)
- **Clear semantics**: Four process types cover common patterns
- **No migration needed**: Existing graphs work, new knowledge added incrementally
- **LLM generation**: Stop hook can create these nodes from conversation
- **Human editable**: Users can manually add/edit process knowledge in graphs

### Negative

- **Schema complexity**: More fields than simple string-based approach
- **Potential redundancy**: Same knowledge might be captured multiple ways
- **Maintenance**: Trigger conditions might become stale if file patterns change

### Mitigation

**Complexity**: Provide JSON schema + validation + examples in docs
**Redundancy**: Periodic review of process knowledge nodes for duplicates
**Maintenance**: Link process knowledge to specific versions/decisions, mark as deprecated when outdated

## Validation

See ADR-003 for query engine validation and test cases.

## References

- Existing graph structure: `.claude/graphs/deployment_graph.json`
- Graph access utilities: `src/triads/km/graph_access.py`
- Knowledge detection: `src/triads/km/detection.py`

---

# ADR-003: Knowledge Query and Relevance Algorithm

**Status**: Accepted
**Date**: 2025-10-17
**Deciders**: Design Bridge Agent

## Context and Problem Statement

The PreToolUse hook must query knowledge graphs and find relevant process knowledge in < 100ms. We need a relevance algorithm that:
1. Matches tool context against trigger conditions
2. Calculates relevance scores (0-1)
3. Ranks by priority + relevance
4. Returns top N results
5. Achieves < 100ms latency (P95)

## Decision Drivers

- **Performance**: Must complete < 100ms on typical graphs (100-500 nodes)
- **Precision**: High relevance items should match, low relevance should not
- **Priority-aware**: CRITICAL items must surface even with lower relevance
- **Deterministic**: Same input always produces same ranking
- **Simple**: No ML models, embeddings, or external dependencies

## Relevance Scoring Algorithm

### Input Context (from PreToolUse)

```python
{
    "tool_name": "Write",
    "tool_input": {
        "file_path": "/path/to/plugin.json",
        "content": "..."  # (optional, usually not needed for matching)
    },
    "session_id": "...",
    "cwd": "/Users/iainnb/Documents/repos/triads",
    "permission_mode": "bypassPermissions"
}
```

### Scoring Formula

```python
relevance_score = (
    tool_match_score * 0.40 +      # Tool name exact match
    file_match_score * 0.40 +      # File pattern match
    keyword_match_score * 0.10 +   # Action keywords (from recent conversation)
    context_match_score * 0.10     # Context keywords (from recent conversation)
)

final_score = relevance_score * priority_multiplier

# Priority multipliers
priority_multiplier = {
    "CRITICAL": 2.0,   # Double the relevance score
    "HIGH": 1.5,
    "MEDIUM": 1.0,
    "LOW": 0.5
}
```

### Component Scores (0-1)

#### 1. Tool Match Score (0 or 1)

```python
def calculate_tool_match_score(tool_name: str, trigger_conditions: dict) -> float:
    """Exact match on tool name."""
    tool_names = trigger_conditions.get("tool_names", [])

    if not tool_names:
        # No tool restriction → matches all tools
        return 0.5  # Neutral score

    if tool_name in tool_names:
        return 1.0  # Exact match

    return 0.0  # No match
```

**Rationale**: Tool name is high signal (e.g., "Write" vs "Read" is very different)

#### 2. File Match Score (0 or 1)

```python
import fnmatch

def calculate_file_match_score(file_path: str, trigger_conditions: dict) -> float:
    """Glob pattern match on file path."""
    file_patterns = trigger_conditions.get("file_patterns", [])

    if not file_patterns:
        # No file restriction → matches all files
        return 0.5  # Neutral score

    for pattern in file_patterns:
        if fnmatch.fnmatch(file_path, pattern):
            return 1.0  # Pattern match

    return 0.0  # No match
```

**Rationale**: File path is high signal (e.g., "plugin.json" vs "README.md" is very different)

#### 3. Keyword Match Score (0-1, fractional)

```python
def calculate_keyword_match_score(
    recent_messages: list[str],  # Last 5 user + assistant messages
    trigger_conditions: dict
) -> float:
    """Case-insensitive substring match on action keywords."""
    action_keywords = trigger_conditions.get("action_keywords", [])
    context_keywords = trigger_conditions.get("context_keywords", [])

    if not action_keywords:
        return 0.5  # Neutral score

    # Combine all recent text
    full_text = " ".join(recent_messages).lower()

    # Count matches
    matches = sum(1 for keyword in action_keywords if keyword.lower() in full_text)

    if matches == 0:
        return 0.0

    # Fractional score: matches / total keywords
    return min(1.0, matches / len(action_keywords))
```

**Rationale**: Keywords provide context but are lower signal than tool/file

#### 4. Context Match Score (same as keyword match)

```python
def calculate_context_match_score(
    recent_messages: list[str],
    trigger_conditions: dict
) -> float:
    """Case-insensitive substring match on context keywords."""
    context_keywords = trigger_conditions.get("context_keywords", [])

    if not context_keywords:
        return 0.5  # Neutral score

    full_text = " ".join(recent_messages).lower()
    matches = sum(1 for keyword in context_keywords if keyword.lower() in full_text)

    if matches == 0:
        return 0.0

    return min(1.0, matches / len(context_keywords))
```

### Relevance Threshold

**Minimum relevance score**: 0.7 (after priority multiplier)

**Rationale**:
- 0.7 requires strong tool + file match OR keyword boost
- CRITICAL items with 0.4 base relevance → 0.8 final (passes threshold)
- LOW priority items need 0.9 base relevance → 0.45 final (fails threshold)

**Examples**:

| Base Relevance | Priority | Final Score | Injected? |
|----------------|----------|-------------|-----------|
| 0.8 | CRITICAL | 1.6 | ✅ Yes |
| 0.5 | CRITICAL | 1.0 | ✅ Yes |
| 0.4 | CRITICAL | 0.8 | ✅ Yes |
| 0.3 | CRITICAL | 0.6 | ❌ No |
| 0.9 | HIGH | 1.35 | ✅ Yes |
| 0.5 | HIGH | 0.75 | ✅ Yes |
| 0.4 | HIGH | 0.6 | ❌ No |
| 0.8 | MEDIUM | 0.8 | ✅ Yes |
| 0.6 | MEDIUM | 0.6 | ❌ No |
| 1.0 | LOW | 0.5 | ❌ No |

### Result Ranking and Limits

```python
# Sort by final_score (descending)
ranked_results = sorted(results, key=lambda r: r.final_score, reverse=True)

# Apply threshold
filtered_results = [r for r in ranked_results if r.final_score >= 0.7]

# Limit to top N
top_results = filtered_results[:3]  # Max 3 injected per tool use
```

**Rationale**: Top-3 limit prevents context clutter, forces high relevance

## Query Engine Design

### Component: ExperienceQueryEngine

**Location**: `src/triads/km/experience_query.py`

**API**:

```python
class ExperienceQueryEngine:
    """Query knowledge graphs for relevant process knowledge."""

    def __init__(self, graphs_dir: Path = Path(".claude/graphs")):
        self._cache: dict[str, dict] = {}  # {triad_name: graph_data}
        self._graphs_dir = graphs_dir

    def query_relevant_knowledge(
        self,
        tool_name: str,
        tool_input: dict,
        recent_messages: list[str] | None = None,
        min_relevance: float = 0.7,
        max_results: int = 3
    ) -> list[ProcessKnowledge]:
        """
        Query graphs for relevant process knowledge.

        Args:
            tool_name: Name of tool being used (e.g., "Write")
            tool_input: Tool parameters (e.g., {"file_path": "..."})
            recent_messages: Last N conversation messages (for keyword matching)
            min_relevance: Minimum relevance score (default 0.7)
            max_results: Maximum results to return (default 3)

        Returns:
            List of ProcessKnowledge objects, ranked by relevance

        Performance:
            - Target: < 100ms (P95)
            - Typical: 20-50ms for 100-500 node graphs
        """
        pass

    def _load_graphs_lazy(self) -> dict[str, dict]:
        """Load all graphs into cache (lazy, once per session)."""
        pass

    def _extract_process_nodes(self, graphs: dict[str, dict]) -> list[dict]:
        """Extract Concept nodes with process_type field."""
        pass

    def _calculate_relevance(
        self,
        node: dict,
        tool_name: str,
        tool_input: dict,
        recent_messages: list[str]
    ) -> float:
        """Calculate relevance score for a process knowledge node."""
        pass

    def _format_for_injection(self, node: dict) -> str:
        """Format process knowledge for context injection."""
        pass
```

**ProcessKnowledge Data Class**:

```python
@dataclass
class ProcessKnowledge:
    """Relevant process knowledge with metadata."""

    node_id: str
    triad: str
    label: str
    process_type: str  # checklist, pattern, warning, requirement
    priority: str  # CRITICAL, HIGH, MEDIUM, LOW
    relevance_score: float  # Base relevance (0-1)
    final_score: float  # After priority multiplier
    formatted_text: str  # Ready for injection into context

    # Metadata for debugging
    matched_on: list[str]  # ["tool", "file", "keyword"]
    trigger_conditions: dict
```

### Performance Optimizations

#### 1. Early Exit Conditions

```python
# Skip irrelevant tools entirely
RELEVANT_TOOLS = {"Write", "Edit", "NotebookEdit", "Bash"}

if tool_name not in RELEVANT_TOOLS:
    return []  # < 1ms
```

**Rationale**: Read, Glob, Grep don't modify state, don't need process knowledge

#### 2. Lazy Graph Loading

```python
# Load once, cache for session
if not self._cache:
    self._cache = self._load_all_graphs()  # ~10-30ms once
```

**Rationale**: Graphs don't change mid-session, load once

#### 3. Fast Path for No Process Knowledge

```python
process_nodes = self._extract_process_nodes(self._cache)

if not process_nodes:
    return []  # < 5ms if no process knowledge exists
```

**Rationale**: New projects have no process knowledge yet

#### 4. Simple String Matching (No Regex)

```python
# Use fnmatch (compiled internally) for file patterns
# Use 'in' for keyword matching (O(n) substring search)
# No regex compilation in hot path
```

**Rationale**: fnmatch and substring search are fast enough, regex adds overhead

### Benchmarking and Monitoring

**Log slow queries** (in PreToolUse hook):

```python
import time

start = time.perf_counter()
results = query_engine.query_relevant_knowledge(...)
elapsed_ms = (time.perf_counter() - start) * 1000

if elapsed_ms > 100:
    print(f"⚠️ Slow experience query: {elapsed_ms:.1f}ms", file=sys.stderr)
```

**Success Metrics**:
- P50 latency: < 30ms
- P95 latency: < 100ms
- P99 latency: < 150ms

## Considered Alternatives

### Alternative 1: LLM-based Relevance

**Idea**: Use Claude to determine relevance for each process knowledge node

```python
# For each node
prompt = f"Is this process knowledge relevant to tool {tool_name} on file {file_path}? Yes/No: {node}"
relevance = llm.complete(prompt)
```

**Pros**:
- ✅ **Semantic understanding**: Could understand nuanced relevance
- ✅ **Flexible**: No need to design scoring algorithm

**Cons**:
- ❌ **Too slow**: 500-2000ms per LLM call, would need one per node
- ❌ **Expensive**: API costs for every tool use
- ❌ **Non-deterministic**: Same input might produce different relevance
- ❌ **Requires network**: LLM API might be unavailable

**Verdict**: **Rejected**. Too slow and expensive for PreToolUse hot path.

### Alternative 2: Embedding-based Semantic Search

**Idea**: Use sentence transformers to embed process knowledge + queries, find nearest neighbors

```python
# Preprocessing (once)
embeddings = model.encode([node['description'] for node in process_nodes])

# Query time
query_embedding = model.encode(f"{tool_name} {file_path}")
similarities = cosine_similarity(query_embedding, embeddings)
```

**Pros**:
- ✅ **Semantic matching**: Understands "version update" ≈ "release"
- ✅ **Handles typos**: Fuzzy matching

**Cons**:
- ❌ **Dependency**: Requires sentence-transformers library (heavy, 500MB+)
- ❌ **Slow**: Model inference 50-200ms per query on CPU
- ❌ **Preprocessing**: Need to re-embed when graph changes
- ❌ **Overkill**: Structured trigger conditions already precise

**Verdict**: **Rejected**. Too heavy for the problem. Structured matching is faster and precise enough.

### Alternative 3: Simple Keyword Matching Only

**Idea**: Just match keywords in description field, no structured trigger conditions

```python
# For each node
if any(keyword in node['description'].lower() for keyword in ['version', 'release']):
    results.append(node)
```

**Pros**:
- ✅ **Simple**: Minimal code
- ✅ **Fast**: O(n) string scan

**Cons**:
- ❌ **Imprecise**: Can't distinguish tool types or file paths
- ❌ **High false positives**: "version" in description != version bump action
- ❌ **No priority**: All results equal weight

**Verdict**: **Rejected**. Not precise enough for < 10% false positive rate goal.

## Decision Outcome

**Chosen option**: **Structured relevance scoring with tool + file + keyword matching**

### Rationale

1. **Performance**: Simple string/pattern matching achieves < 100ms target
2. **Precision**: Tool + file matching provides high signal
3. **Priority-aware**: Multiplier ensures CRITICAL items surface
4. **Deterministic**: Same input always produces same ranking
5. **No dependencies**: Pure Python, fnmatch from stdlib

### Scoring Weights Justification

| Component | Weight | Rationale |
|-----------|--------|-----------|
| Tool match | 40% | High signal: tool type fundamentally different (Write vs Read) |
| File match | 40% | High signal: file path indicates intent (version file vs doc file) |
| Action keywords | 10% | Medium signal: user intent but might be vague |
| Context keywords | 10% | Low signal: general topic, not specific action |

**Total**: 100% (before priority multiplier)

**Priority multiplier applied AFTER** base score ensures CRITICAL items never lost.

## Consequences

### Positive

- **Fast**: < 100ms target achievable with simple matching
- **Precise**: Low false positive rate (< 10% expected)
- **Complete**: 100% recall for CRITICAL items (via priority boost)
- **Simple**: No ML, embeddings, or external dependencies
- **Debuggable**: Scores are explainable (matched on tool + file)

### Negative

- **Manual tuning**: Weights (40/40/10/10) might need adjustment based on usage
- **No semantic understanding**: "deploy" ≠ "release" (but can add to keywords)
- **Pattern maintenance**: File patterns need updates if project structure changes

### Mitigation

**Tuning**: Log relevance scores to stderr, adjust weights if too many false positives/negatives
**Semantics**: Use synonym lists in keyword matching (deploy|release|ship)
**Maintenance**: Process knowledge nodes linked to decisions/versions, mark as deprecated when stale

## Validation

### Test Case 1: High Relevance (Should Inject)

```python
# Input
tool_name = "Write"
tool_input = {"file_path": "/path/to/plugin.json"}
recent_messages = ["Let's bump the version to 0.8.0 and release"]

# Process node
{
  "process_type": "checklist",
  "priority": "CRITICAL",
  "trigger_conditions": {
    "tool_names": ["Write", "Edit"],
    "file_patterns": ["**/plugin.json"],
    "action_keywords": ["version bump", "release"]
  }
}

# Calculation
tool_match = 1.0     # "Write" in ["Write", "Edit"]
file_match = 1.0     # "plugin.json" matches "**/plugin.json"
keyword_match = 1.0  # "version bump" and "release" both in recent_messages
context_match = 0.5  # No context_keywords

base_relevance = 1.0*0.4 + 1.0*0.4 + 1.0*0.1 + 0.5*0.1 = 0.95
final_score = 0.95 * 2.0 (CRITICAL) = 1.9

# Result: ✅ INJECT (final_score 1.9 >> 0.7 threshold)
```

### Test Case 2: Medium Relevance (Should NOT Inject)

```python
# Input
tool_name = "Write"
tool_input = {"file_path": "/path/to/README.md"}
recent_messages = ["Update the documentation"]

# Process node (same as above)

# Calculation
tool_match = 1.0     # "Write" matches
file_match = 0.0     # "README.md" doesn't match "**/plugin.json"
keyword_match = 0.0  # No keywords match
context_match = 0.5  # Neutral

base_relevance = 1.0*0.4 + 0.0*0.4 + 0.0*0.1 + 0.5*0.1 = 0.45
final_score = 0.45 * 2.0 (CRITICAL) = 0.9

# Result: ✅ INJECT (final_score 0.9 > 0.7 threshold)
# Note: CRITICAL boost saves it, but borderline
```

### Test Case 3: Low Relevance (Should NOT Inject)

```python
# Input
tool_name = "Read"
tool_input = {"file_path": "/path/to/plugin.json"}

# Process node (same as above)

# Calculation
tool_match = 0.0     # "Read" not in ["Write", "Edit"]
file_match = 1.0     # File matches but irrelevant for Read
keyword_match = 0.5  # Neutral
context_match = 0.5  # Neutral

base_relevance = 0.0*0.4 + 1.0*0.4 + 0.5*0.1 + 0.5*0.1 = 0.5
final_score = 0.5 * 2.0 (CRITICAL) = 1.0

# Result: ✅ Would inject, BUT early exit on Read tool prevents query
# Optimization: Read skipped in RELEVANT_TOOLS whitelist
```

### Test Case 4: Priority Impact

```python
# Same input as Test Case 2, but priority = LOW

base_relevance = 0.45
final_score = 0.45 * 0.5 (LOW) = 0.225

# Result: ❌ DO NOT INJECT (final_score 0.225 < 0.7 threshold)
# Priority multiplier correctly filters low-priority borderline matches
```

## Performance Benchmarks (Expected)

| Scenario | Graph Size | Process Nodes | Latency (P95) |
|----------|-----------|---------------|---------------|
| No process knowledge | 500 nodes | 0 | < 5ms |
| Small project | 100 nodes | 5 | < 20ms |
| Medium project | 300 nodes | 15 | < 50ms |
| Large project | 500 nodes | 30 | < 100ms |
| Read tool (early exit) | 500 nodes | 30 | < 1ms |

**Bottleneck**: Loading graphs from disk (first query only, then cached)

## References

- Graph access utilities: `src/triads/km/graph_access.py`
- fnmatch documentation: https://docs.python.org/3/library/fnmatch.html
- PreToolUse hook test logs showing tool_input structure

---

# ADR-004: Lesson Extraction and Learning Mechanism

**Status**: Accepted
**Date**: 2025-10-17
**Deciders**: Design Bridge Agent

## Context and Problem Statement

The system must learn from mistakes and conversations by:
1. Detecting lessons learned during sessions
2. Extracting them as structured process knowledge nodes
3. Inferring appropriate priority levels
4. Inferring relevant trigger conditions
5. Adding them to knowledge graphs automatically

This happens in the **Stop hook** after Claude finishes responding.

## Decision Drivers

- **Automation**: Minimize manual process knowledge creation
- **Accuracy**: Generated nodes must have correct structure and trigger conditions
- **Safety**: Avoid creating low-quality or incorrect process knowledge
- **Human-in-loop**: User should review/approve before committing to graph
- **Learning from mistakes**: System should detect when things went wrong

## Lesson Detection Patterns

### Pattern 1: User Correction

**Signal**: User points out a mistake

```
User: "You forgot to update marketplace.json in the version bump"
Assistant: "You're right, I missed that. Let me add it now."
```

**Detection** (in Stop hook):
```python
# Scan conversation for correction patterns
correction_patterns = [
    r"you forgot",
    r"you missed",
    r"you didn't",
    r"but you also need",
    r"don't forget",
    r"remember to",
    r"make sure you"
]

if any(re.search(pattern, message, re.IGNORECASE) for pattern in correction_patterns):
    # Potential lesson detected
```

**Generated Process Knowledge**:
- **Priority**: CRITICAL (user had to intervene)
- **Type**: checklist or warning (depending on context)
- **Evidence**: Link to conversation timestamp
- **Trigger conditions**: Infer from files mentioned in correction

### Pattern 2: Explicit Lesson Statement

**Signal**: Claude or user explicitly states a lesson

```
Assistant: "Lesson learned: Always update marketplace.json when bumping plugin version"
```

**Detection**:
```python
lesson_patterns = [
    r"lesson learned:",
    r"note for future:",
    r"important:",
    r"remember that",
    r"going forward",
    r"from now on"
]
```

**Generated Process Knowledge**:
- **Priority**: HIGH (explicitly stated)
- **Type**: pattern (situation → action)
- **Evidence**: Exact quote from conversation

### Pattern 3: [PROCESS_KNOWLEDGE] Block

**Signal**: Claude explicitly outputs structured process knowledge

```markdown
[PROCESS_KNOWLEDGE]
type: checklist
priority: CRITICAL
label: Version Bump File Checklist
trigger_conditions:
  tool_names: [Write, Edit]
  file_patterns: ["**/plugin.json", "**/*version*"]
checklist:
  title: Complete Version Bump
  items:
    - pyproject.toml
    - plugin.json
    - marketplace.json
    - CHANGELOG.md
[/PROCESS_KNOWLEDGE]
```

**Detection**: Parse structured block (similar to existing [GRAPH_UPDATE] parsing)

**Generated Process Knowledge**: Use provided structure directly (highest trust)

### Pattern 4: Repeated Mistakes

**Signal**: Same mistake occurs multiple times across sessions

```python
# Check graph history
similar_corrections = [
    node for node in graph['nodes']
    if node.get('type') == 'Concept'
    and 'correction' in node.get('tags', [])
    and similar_topic(node['description'], current_correction)
]

if len(similar_corrections) >= 2:
    # Repeated mistake → upgrade priority to CRITICAL
```

**Generated Process Knowledge**:
- **Priority**: CRITICAL (repeated mistake)
- **Type**: warning (risk of repeating)
- **Evidence**: Link to all related correction nodes

## Inference Algorithms

### Inferring Priority

```python
def infer_priority(
    context: str,
    correction_type: str,
    repetition_count: int,
    user_explicit: bool
) -> str:
    """
    Infer priority level for process knowledge.

    Rules:
    1. User correction + high impact → CRITICAL
    2. User correction + medium impact → HIGH
    3. Explicit lesson statement → HIGH
    4. Repeated mistake (2+) → CRITICAL
    5. Repeated mistake (1) → HIGH
    6. Proactive suggestion → MEDIUM
    7. Optional improvement → LOW
    """

    if repetition_count >= 2:
        return "CRITICAL"  # Repeated mistakes are critical

    if user_explicit and correction_type == "correction":
        # User had to correct us
        if high_impact(context):
            return "CRITICAL"  # e.g., deployment, security, data loss
        else:
            return "HIGH"      # e.g., code quality, tests

    if correction_type == "explicit_lesson":
        return "HIGH"  # Claude explicitly noted importance

    if correction_type == "proactive_suggestion":
        return "MEDIUM"  # Claude suggested improvement

    return "LOW"  # Default for optional improvements

def high_impact(context: str) -> bool:
    """Check if context indicates high impact."""
    high_impact_keywords = [
        "deploy", "release", "production", "security",
        "data loss", "breaking change", "migration",
        "version", "publish"
    ]
    return any(keyword in context.lower() for keyword in high_impact_keywords)
```

### Inferring Trigger Conditions

```python
def infer_trigger_conditions(
    conversation: list[dict],
    correction_context: str
) -> dict:
    """
    Infer trigger conditions from conversation context.

    Strategy:
    1. Extract file paths mentioned → file_patterns
    2. Extract tool names mentioned → tool_names
    3. Extract action verbs → action_keywords
    4. Extract domain topics → context_keywords
    5. Detect current triad → triad_names
    """

    trigger_conditions = {
        "tool_names": [],
        "file_patterns": [],
        "action_keywords": [],
        "context_keywords": [],
        "triad_names": []
    }

    # Extract file paths
    file_paths = extract_file_references(conversation)
    trigger_conditions["file_patterns"] = [
        generalize_file_path(path) for path in file_paths
    ]

    # Extract tools from [TOOL_USE] blocks in conversation
    tools = extract_tool_uses(conversation)
    trigger_conditions["tool_names"] = list(set(tools))

    # Extract action keywords
    action_verbs = ["update", "create", "modify", "deploy", "bump", "release"]
    for verb in action_verbs:
        if verb in correction_context.lower():
            trigger_conditions["action_keywords"].append(verb)

    # Extract domain keywords
    trigger_conditions["context_keywords"] = extract_domain_keywords(correction_context)

    # Detect current triad (if in triad workflow)
    current_triad = detect_current_triad()
    if current_triad:
        trigger_conditions["triad_names"] = [current_triad]

    return trigger_conditions

def generalize_file_path(path: str) -> str:
    """
    Convert specific path to glob pattern.

    Examples:
        "/path/to/plugin.json" → "**/plugin.json"
        "/path/to/pyproject.toml" → "**/pyproject.toml"
        "/path/to/src/module_v2.py" → "**/*version*.py" (if version-related)
    """
    filename = os.path.basename(path)

    # Common generalization patterns
    if "version" in filename.lower():
        return f"**/*version*{os.path.splitext(filename)[1]}"

    # Default: match filename anywhere
    return f"**/{filename}"
```

### Inferring Process Type

```python
def infer_process_type(correction_text: str, context: str) -> str:
    """
    Infer which process type fits the lesson.

    Rules:
    1. Multiple steps mentioned → checklist
    2. "When X, do Y" structure → pattern
    3. Risk/danger mentioned → warning
    4. Must/requirement language → requirement
    """

    # Checklist indicators
    if any(indicator in correction_text.lower() for indicator in [
        "also need", "don't forget", "all files", "complete",
        "both", "and", "also update"
    ]):
        return "checklist"

    # Pattern indicators
    if any(indicator in correction_text.lower() for indicator in [
        "when", "always", "whenever", "after", "before"
    ]):
        return "pattern"

    # Warning indicators
    if any(indicator in correction_text.lower() for indicator in [
        "risk", "danger", "careful", "could", "might", "warning"
    ]):
        return "warning"

    # Requirement indicators
    if any(indicator in correction_text.lower() for indicator in [
        "must", "required", "constraint", "cannot", "should not"
    ]):
        return "requirement"

    # Default to pattern (most flexible)
    return "pattern"
```

## Stop Hook Integration

### Existing Stop Hook Behavior

Currently (from hooks/on_stop.py):
1. Receives conversation transcript
2. Scans for [GRAPH_UPDATE] blocks
3. Parses and applies updates to graphs
4. Validates pre-flight checks
5. Detects KM issues

### New Behavior: Lesson Extraction

**Add to Stop hook** (after existing graph update logic):

```python
# After applying [GRAPH_UPDATE] blocks

# Extract lessons from conversation
lessons = extract_lessons_from_conversation(conversation_text)

if lessons:
    print(f"\n📚 Detected {len(lessons)} potential lesson(s)", file=sys.stderr)

    # Create process knowledge nodes
    for lesson in lessons:
        # Infer fields
        priority = infer_priority(
            lesson['context'],
            lesson['type'],
            lesson['repetition_count'],
            lesson['user_explicit']
        )

        trigger_conditions = infer_trigger_conditions(
            conversation,
            lesson['context']
        )

        process_type = infer_process_type(lesson['text'], lesson['context'])

        # Create node
        node = create_process_knowledge_node(
            label=lesson['title'],
            description=lesson['description'],
            priority=priority,
            process_type=process_type,
            trigger_conditions=trigger_conditions,
            evidence=lesson['evidence'],
            created_by="lesson-extractor"
        )

        # Add to appropriate graph (deployment, implementation, etc.)
        target_triad = lesson.get('triad', 'default')
        graph_data = load_graph(target_triad)
        graph_data['nodes'].append(node)
        save_graph(graph_data, target_triad)

        print(f"  ✓ Created: {lesson['title']} ({priority})", file=sys.stderr)
```

### Human-in-Loop Review

**Option 1: Immediate Confirmation** (interactive)

```python
# Show learned lesson to user
print(f"\n{'='*80}\n", file=sys.stderr)
print(f"📚 LESSON LEARNED\n", file=sys.stderr)
print(f"Title: {lesson['title']}", file=sys.stderr)
print(f"Priority: {priority}", file=sys.stderr)
print(f"Type: {process_type}", file=sys.stderr)
print(f"\nAdd to knowledge graph? (y/n): ", file=sys.stderr, end='')

# Note: Stop hooks can't block for user input in Claude Code
# This approach doesn't work
```

**Verdict**: ❌ Not feasible. Stop hooks can't prompt user interactively.

**Option 2: Staged Commit** (deferred review)

```python
# Save to pending lessons file
pending_file = Path('.claude/pending_lessons.json')
pending_lessons = load_or_create(pending_file)
pending_lessons.append({
    'lesson': lesson,
    'priority': priority,
    'process_type': process_type,
    'trigger_conditions': trigger_conditions,
    'detected_at': datetime.now().isoformat(),
    'session_id': session_id
})
save(pending_file, pending_lessons)

print(f"  → Saved to pending_lessons.json (review before commit)", file=sys.stderr)
```

**Verdict**: ✅ Feasible, but extra step for user.

**Option 3: Auto-Add with Review Command** (recommended)

```python
# Automatically add to graph with 'draft' status
node['status'] = 'draft'  # Mark as unreviewed
node['reviewed_by'] = None

graph_data['nodes'].append(node)
save_graph(graph_data, target_triad)

print(f"  ✓ Added as DRAFT: {lesson['title']} ({priority})", file=sys.stderr)
print(f"  Review with: /knowledge-show {node['id']}", file=sys.stderr)
```

**Verdict**: ✅ **RECOMMENDED**. Lessons immediately usable, user can review/edit/delete later.

## Considered Alternatives

### Alternative 1: Manual Process Knowledge Creation Only

**Idea**: No automatic extraction, users manually create process knowledge

**Pros**:
- ✅ **100% accuracy**: User writes exactly what they mean
- ✅ **No false positives**: No incorrect lessons added

**Cons**:
- ❌ **High friction**: User must remember to document lessons
- ❌ **Incomplete**: Lessons will be forgotten (like marketplace.json was)
- ❌ **Defeats purpose**: System doesn't learn automatically

**Verdict**: **Rejected**. The whole point is automatic learning from mistakes.

### Alternative 2: LLM-based Lesson Extraction

**Idea**: Use Claude to analyze conversation and extract lessons

```python
# After session
prompt = f"""
Analyze this conversation and extract any lessons learned:

{conversation_text}

Output lessons in JSON format with title, description, priority, trigger conditions.
"""

lessons = claude.complete(prompt)
```

**Pros**:
- ✅ **Semantic understanding**: Better than regex patterns
- ✅ **Contextual**: Can understand nuanced lessons
- ✅ **Flexible**: Handles diverse lesson types

**Cons**:
- ❌ **Slow**: LLM inference takes 2-10 seconds
- ❌ **Expensive**: API cost for every session
- ❌ **Requires network**: Might fail if offline
- ❌ **Stop hook timing**: Stop hooks should be fast

**Verdict**: **Rejected** for Stop hook. Could be used for **async batch processing** instead (future enhancement).

### Alternative 3: Conversation Replay with Fresh Claude

**Idea**: At end of session, replay conversation to fresh Claude and ask "what did you learn?"

**Pros**:
- ✅ **Self-awareness**: Claude can reflect on its own mistakes
- ✅ **Comprehensive**: Can analyze entire session holistically

**Cons**:
- ❌ **Very slow**: Full conversation replay + analysis = 30+ seconds
- ❌ **Very expensive**: Processes entire conversation twice
- ❌ **Stop hook constraint**: Way too slow for Stop hook

**Verdict**: **Rejected** for Stop hook. Could be **async batch job** (future enhancement).

## Decision Outcome

**Chosen option**: **Pattern-based lesson extraction in Stop hook with auto-add as draft**

### Implementation Strategy

**Phase 1** (MVP):
1. Detect explicit [PROCESS_KNOWLEDGE] blocks in conversation (highest trust)
2. Parse structured blocks into process knowledge nodes
3. Auto-add to graph with status='draft'
4. Log to stderr for user awareness

**Phase 2** (Pattern Detection):
1. Add user correction pattern detection (regex)
2. Add explicit lesson statement detection
3. Infer priority, type, trigger conditions using rule-based algorithms
4. Auto-add as draft with lower confidence (0.8 instead of 1.0)

**Phase 3** (Advanced):
1. Detect repeated mistakes across sessions
2. Async LLM-based lesson extraction (batch job, not in Stop hook)
3. User review UI (CLI command or web interface)

### Rationale

1. **Start simple**: Explicit [PROCESS_KNOWLEDGE] blocks have high precision
2. **Incremental complexity**: Add pattern detection after MVP works
3. **Human-in-loop via draft status**: Auto-add but mark for review
4. **Async for expensive operations**: Keep Stop hook fast (< 100ms)

## Consequences

### Positive

- **Automatic learning**: Lessons captured without manual work
- **Incremental improvement**: System gets smarter over time
- **Fail-safe**: Draft status allows review before trust
- **Fast Stop hook**: Pattern matching is fast enough (< 50ms expected)

### Negative

- **False positives**: Some detected "lessons" might be irrelevant
- **Inference errors**: Priority/trigger conditions might be wrong
- **Clutter**: Too many draft lessons could pollute graphs

### Mitigation

**False positives**: Draft status + user can delete invalid lessons
**Inference errors**: User can edit nodes directly in graph JSON
**Clutter**: Periodic cleanup job to archive old draft lessons

## Validation

### Test Case 1: Explicit [PROCESS_KNOWLEDGE] Block

**Input** (in conversation):
```markdown
I should have remembered to update marketplace.json. Let me document this:

[PROCESS_KNOWLEDGE]
type: checklist
priority: CRITICAL
label: Version Bump File Checklist
trigger_conditions:
  tool_names: [Write, Edit]
  file_patterns: ["**/plugin.json", "**/*version*"]
checklist:
  title: Complete Version Bump
  items:
    - pyproject.toml (version field)
    - plugin.json (version field)
    - marketplace.json (current_version)
    - CHANGELOG.md (new version section)
[/PROCESS_KNOWLEDGE]
```

**Output** (Stop hook):
```json
{
  "id": "process_version_bump_checklist_2025-10-17T13:00:00",
  "type": "Concept",
  "label": "Version Bump File Checklist",
  "description": "Complete checklist of ALL files that must be updated when bumping version.",
  "confidence": 1.0,
  "evidence": "Explicit [PROCESS_KNOWLEDGE] block in session {session_id}",
  "created_by": "lesson-extractor",
  "created_at": "2025-10-17T13:00:00.000000",
  "status": "draft",

  "process_type": "checklist",
  "priority": "CRITICAL",
  "trigger_conditions": {
    "tool_names": ["Write", "Edit"],
    "file_patterns": ["**/plugin.json", "**/*version*"]
  },
  "checklist": {
    "title": "Complete Version Bump",
    "items": [
      "pyproject.toml (version field)",
      "plugin.json (version field)",
      "marketplace.json (current_version)",
      "CHANGELOG.md (new version section)"
    ],
    "format": "checkbox"
  }
}
```

**Verification**: ✅ Node added to deployment_graph.json

### Test Case 2: User Correction Pattern

**Input** (in conversation):
```
User: "You forgot to update marketplace.json when you bumped the version in plugin.json"
Assistant: "You're absolutely right, my apologies. Let me add that now."
```

**Output** (Stop hook):
```json
{
  "id": "process_marketplace_json_sync_2025-10-17T13:05:00",
  "type": "Concept",
  "label": "Marketplace.json Version Sync",
  "description": "When updating plugin.json version, must also update marketplace.json current_version field",
  "confidence": 0.85,
  "evidence": "User correction in session {session_id}: 'You forgot to update marketplace.json'",
  "created_by": "lesson-extractor",
  "created_at": "2025-10-17T13:05:00.000000",
  "status": "draft",

  "process_type": "pattern",  // Inferred from "when...must"
  "priority": "CRITICAL",     // Inferred from user correction + deployment context
  "trigger_conditions": {
    "tool_names": ["Write", "Edit"],  // Inferred from tools used in context
    "file_patterns": ["**/plugin.json", "**/marketplace.json"],  // Extracted from conversation
    "action_keywords": ["version bump", "update version"],  // Inferred from context
    "context_keywords": ["deployment", "release"]  // Inferred from domain
  },
  "pattern": {
    "situation": "When updating plugin.json version",
    "action": "Always update marketplace.json current_version field",
    "rationale": "Marketplace.json must stay in sync with plugin.json for marketplace listing",
    "example": "Session {session_id} - forgot marketplace.json during version bump"
  }
}
```

**Verification**: ✅ Node added with inferred fields, marked as draft for review

## References

- Existing Stop hook: `hooks/on_stop.py`
- Graph update parsing: `extract_graph_updates_from_text()` (lines 113-155)
- Deployment graph with process knowledge: `.claude/graphs/deployment_graph.json`

---

# ADR-005: Process Knowledge Priority System

**Status**: Accepted
**Date**: 2025-10-17
**Deciders**: Design Bridge Agent

## Context and Problem Statement

Process knowledge must be prioritized to ensure:
1. CRITICAL items are NEVER missed (100% recall)
2. LOW priority items don't clutter context (< 10% false positive rate)
3. Priority levels have clear, actionable semantics
4. Priority affects both ranking AND display behavior

## Decision Drivers

- **Safety**: CRITICAL mistakes must be prevented
- **Usability**: Priorities must be intuitive to users and LLMs
- **Performance**: Priority must affect query ranking
- **Flexibility**: Support different severity levels
- **Actionability**: Each priority should imply specific behavior

## Priority Levels

### CRITICAL - "Production-Breaking"

**Definition**: Must be followed to prevent production incidents, data loss, security issues, or blocking bugs.

**Examples**:
- Version bump complete checklist (marketplace.json)
- Database migration safety procedures
- Security validation requirements
- Breaking change deployment protocols

**Behavior**:
- **Relevance multiplier**: 2.0x (doubles relevance score)
- **Display location**: SessionStart + PreToolUse injection
- **Formatting**: Red ⚠️ prefix, all caps title
- **Recall requirement**: 100% (never miss CRITICAL items)

**When to assign CRITICAL**:
- User had to intervene to prevent/fix issue
- Issue affects production, users, or data integrity
- Repeated mistake (2+ occurrences)
- Explicitly marked as critical by user

### HIGH - "Quality-Impact"

**Definition**: Should be followed to maintain code quality, prevent bugs, or ensure best practices.

**Examples**:
- Test coverage requirements
- Code review checklists
- Refactoring safety patterns
- Documentation standards

**Behavior**:
- **Relevance multiplier**: 1.5x
- **Display location**: PreToolUse injection only
- **Formatting**: Yellow ⚠️ prefix
- **Recall requirement**: 90% (occasionally missing is acceptable)

**When to assign HIGH**:
- User mentioned as important
- Explicitly stated as lesson learned
- Quality/testing related
- First-time mistake correction

### MEDIUM - "Nice-to-Have"

**Definition**: Suggested practices that improve workflow but aren't essential.

**Examples**:
- Code style preferences
- Optimization suggestions
- Organization patterns
- Helpful tips

**Behavior**:
- **Relevance multiplier**: 1.0x (no boost)
- **Display location**: PreToolUse injection if highly relevant
- **Formatting**: Blue ℹ️ prefix
- **Recall requirement**: 50% (can be missed often)

**When to assign MEDIUM**:
- Proactive suggestions (not corrections)
- Style/preference recommendations
- Optional improvements
- Context-dependent practices

### LOW - "Informational"

**Definition**: Background information or rarely-needed context.

**Examples**:
- Historical notes
- Deprecated patterns (for reference)
- Edge case warnings
- Project trivia

**Behavior**:
- **Relevance multiplier**: 0.5x (penalized)
- **Display location**: Rarely injected (needs very high base relevance)
- **Formatting**: Gray ℹ️ prefix
- **Recall requirement**: 10% (mostly filtered out)

**When to assign LOW**:
- Optional context
- Rarely relevant
- Historical documentation
- Superseded by better practices

## Priority Assignment Rules

### Automatic Inference (Lesson Extraction)

```python
def infer_priority(
    correction_type: str,     # "user_correction", "explicit_lesson", "suggestion"
    impact_level: str,        # "production", "quality", "style", "info"
    repetition_count: int,    # How many times seen before
    user_explicit: bool       # User said "critical" or "important"
) -> str:
    """
    Infer priority from context.

    Decision tree:
    1. repetition_count >= 2 → CRITICAL (repeated mistakes are critical)
    2. user_explicit + "critical" keyword → CRITICAL
    3. correction_type == "user_correction":
       - impact_level == "production" → CRITICAL
       - impact_level == "quality" → HIGH
       - else → MEDIUM
    4. correction_type == "explicit_lesson":
       - impact_level == "production" → HIGH
       - else → MEDIUM
    5. correction_type == "suggestion" → MEDIUM
    6. else → LOW
    """

    # Repeated mistakes always CRITICAL
    if repetition_count >= 2:
        return "CRITICAL"

    # User explicitly marked as critical
    if user_explicit:
        return "CRITICAL"

    # User had to correct us
    if correction_type == "user_correction":
        if impact_level == "production":
            return "CRITICAL"
        elif impact_level == "quality":
            return "HIGH"
        else:
            return "MEDIUM"

    # Claude explicitly noted a lesson
    if correction_type == "explicit_lesson":
        if impact_level == "production":
            return "HIGH"
        else:
            return "MEDIUM"

    # Proactive suggestion
    if correction_type == "suggestion":
        return "MEDIUM"

    # Default
    return "LOW"

def classify_impact_level(context: str) -> str:
    """Classify impact from context keywords."""
    production_keywords = [
        "deploy", "release", "production", "publish",
        "security", "data loss", "breaking", "critical",
        "users affected", "downtime", "rollback"
    ]

    quality_keywords = [
        "test", "bug", "error", "exception", "crash",
        "refactor", "code quality", "lint", "type check",
        "coverage", "regression"
    ]

    style_keywords = [
        "style", "format", "naming", "organize",
        "readability", "comment", "documentation"
    ]

    context_lower = context.lower()

    if any(keyword in context_lower for keyword in production_keywords):
        return "production"
    elif any(keyword in context_lower for keyword in quality_keywords):
        return "quality"
    elif any(keyword in context_lower for keyword in style_keywords):
        return "style"
    else:
        return "info"
```

### Manual Override

Users can edit priority directly in graph JSON:

```bash
# Edit deployment_graph.json
{
  "id": "process_some_checklist",
  "priority": "HIGH"  # User changes from "MEDIUM" to "HIGH"
}
```

**Use case**: User realizes a MEDIUM priority item is actually CRITICAL after using it.

## Priority Impact on Query System

### Relevance Multiplier

```python
priority_multipliers = {
    "CRITICAL": 2.0,   # Double the relevance
    "HIGH": 1.5,       # 50% boost
    "MEDIUM": 1.0,     # No change
    "LOW": 0.5         # Penalized
}

final_score = base_relevance * priority_multipliers[priority]
```

**Effect on threshold** (0.7 minimum):

| Base Relevance | CRITICAL | HIGH | MEDIUM | LOW |
|----------------|----------|------|--------|-----|
| 0.4 | 0.8 ✅ | 0.6 ❌ | 0.4 ❌ | 0.2 ❌ |
| 0.5 | 1.0 ✅ | 0.75 ✅ | 0.5 ❌ | 0.25 ❌ |
| 0.6 | 1.2 ✅ | 0.9 ✅ | 0.6 ❌ | 0.3 ❌ |
| 0.7 | 1.4 ✅ | 1.05 ✅ | 0.7 ✅ | 0.35 ❌ |
| 0.8 | 1.6 ✅ | 1.2 ✅ | 0.8 ✅ | 0.4 ❌ |

**Key insight**: CRITICAL items need only 0.4 base relevance to inject (2.0 * 0.4 = 0.8 > 0.7)

### Display Formatting

```python
def format_for_injection(node: dict) -> str:
    """Format process knowledge based on priority."""
    priority = node.get('priority', 'MEDIUM')
    process_type = node.get('process_type')

    if priority == "CRITICAL":
        header = f"⚠️ CRITICAL {process_type.upper()}"
        border = "=" * 80
    elif priority == "HIGH":
        header = f"⚠️ HIGH PRIORITY {process_type.upper()}"
        border = "-" * 80
    elif priority == "MEDIUM":
        header = f"ℹ️ {process_type.title()}"
        border = "-" * 80
    else:  # LOW
        header = f"ℹ️ Note: {process_type.title()}"
        border = ""

    # Format content based on process_type
    content = format_process_content(node)

    if border:
        return f"\n{border}\n{header}\n{border}\n\n{content}\n\n{border}\n"
    else:
        return f"\n{header}\n{content}\n"
```

**Example outputs**:

**CRITICAL**:
```
================================================================================
⚠️ CRITICAL CHECKLIST
================================================================================

Version Bump Complete Checklist

Before proceeding, verify:
- [ ] pyproject.toml (version field)
- [ ] plugin.json (version field)
- [ ] marketplace.json (current_version)
- [ ] CHANGELOG.md (new version section)

================================================================================
```

**HIGH**:
```
--------------------------------------------------------------------------------
⚠️ HIGH PRIORITY PATTERN
--------------------------------------------------------------------------------

Code Refactoring Safety

When: Refactoring code
Do: Always run full test suite before committing
Why: Prevents regressions from propagating

--------------------------------------------------------------------------------
```

**MEDIUM**:
```
--------------------------------------------------------------------------------
ℹ️ Pattern
--------------------------------------------------------------------------------

Commit Message Format

When: Writing commit messages
Do: Use conventional commits format (type: description)
Why: Enables automatic changelog generation
```

**LOW**:
```
ℹ️ Note: Historical Context

This pattern was used before v0.5.0 but is now deprecated.
See new pattern: [link]
```

## Considered Alternatives

### Alternative 1: Three Levels Only (Critical/Normal/Low)

**Idea**: Simplify to 3 levels

**Pros**:
- ✅ Simpler to understand
- ✅ Easier to assign

**Cons**:
- ❌ **Not enough granularity**: "Normal" too broad (quality vs style very different)
- ❌ **Binary thinking**: Forces everything into extremes

**Verdict**: **Rejected**. Four levels provide better granularity without excessive complexity.

### Alternative 2: Numeric Scale (1-10)

**Idea**: Priority as number 1-10

**Pros**:
- ✅ Fine-grained control
- ✅ Easy arithmetic

**Cons**:
- ❌ **Ambiguous semantics**: What's the difference between 6 and 7?
- ❌ **Decision paralysis**: Too many choices
- ❌ **Not actionable**: Number doesn't imply behavior

**Verdict**: **Rejected**. Named levels are clearer.

### Alternative 3: No Priority (Relevance Only)

**Idea**: Just use base relevance, no priority field

**Pros**:
- ✅ Simpler schema
- ✅ One less field to maintain

**Cons**:
- ❌ **Can't guarantee CRITICAL recall**: High relevance != high importance
- ❌ **No user control**: Can't manually boost priority
- ❌ **Misses context**: Version bump might have low relevance if keywords don't match, but it's still critical

**Verdict**: **Rejected**. Priority is essential for safety-critical process knowledge.

## Decision Outcome

**Chosen option**: **Four priority levels (CRITICAL, HIGH, MEDIUM, LOW) with semantic definitions and behavior rules**

### Rationale

1. **Clear semantics**: Each level has specific meaning and behavior
2. **Safety guarantee**: CRITICAL items have 2.0x multiplier → 100% recall achievable
3. **Flexibility**: Four levels cover production→quality→style→info spectrum
4. **Actionable**: Priority implies display format, frequency, emphasis
5. **User-friendly**: Easy to understand and assign

## Consequences

### Positive

- **Safety**: CRITICAL items never missed (2.0x boost)
- **Clarity**: Priorities have clear, actionable meanings
- **Control**: Users can manually override priorities
- **Balance**: High-priority items surface, low-priority filtered out

### Negative

- **Subjectivity**: Priority assignment has some judgment involved
- **Calibration**: Might need to adjust multipliers based on real-world usage
- **Potential over-use**: Users might mark everything CRITICAL

### Mitigation

**Subjectivity**: Provide clear decision tree for automatic inference
**Calibration**: Log priority distribution, adjust multipliers if imbalanced
**Over-use**: Documentation emphasizes "only production-breaking" for CRITICAL

## Validation

### Test Case 1: CRITICAL Recall

**Scenario**: Version bump with low keyword relevance

```python
# Process knowledge
{
  "priority": "CRITICAL",
  "trigger_conditions": {
    "file_patterns": ["**/plugin.json"]
  }
}

# Tool use
tool_name = "Write"
tool_input = {"file_path": "/path/to/plugin.json"}
recent_messages = []  # No keywords

# Calculation
base_relevance = 0.4  # Tool match only (0.4 * 1.0 + 0 keywords)
final_score = 0.4 * 2.0 (CRITICAL) = 0.8

# Result: ✅ INJECT (0.8 > 0.7 threshold)
# CRITICAL priority saves low-relevance match
```

### Test Case 2: LOW Priority Filtered

**Scenario**: Historical note with high relevance

```python
# Process knowledge
{
  "priority": "LOW",
  "trigger_conditions": {
    "file_patterns": ["**/config.json"],
    "action_keywords": ["configure", "setup"]
  }
}

# Tool use
tool_name = "Write"
tool_input = {"file_path": "/path/to/config.json"}
recent_messages = ["Let's configure the settings"]

# Calculation
base_relevance = 0.9  # Tool + file + keywords match
final_score = 0.9 * 0.5 (LOW) = 0.45

# Result: ❌ DO NOT INJECT (0.45 < 0.7 threshold)
# LOW priority correctly filters borderline matches
```

### Test Case 3: Priority Distribution Goal

**Expected distribution** (across all process knowledge nodes):

| Priority | Percentage | Count (if 20 total) |
|----------|-----------|---------------------|
| CRITICAL | 10-20% | 2-4 nodes |
| HIGH | 30-40% | 6-8 nodes |
| MEDIUM | 30-40% | 6-8 nodes |
| LOW | 10-20% | 2-4 nodes |

**Monitoring**: Log priority distribution weekly, flag if > 50% CRITICAL (over-use).

## References

- ADR-003 for relevance formula
- ADR-004 for priority inference algorithm
- Deployment graph example: `.claude/graphs/deployment_graph.json` (node with priority="CRITICAL")

---

# Risk Analysis

## Risk Assessment Matrix

| Risk | Likelihood | Impact | Severity | Mitigation |
|------|-----------|--------|----------|------------|
| PreToolUse hook performance > 100ms | Medium | High | **HIGH** | Aggressive caching, early exit, benchmarking, disable flag |
| False positives (irrelevant injection) | Medium | Medium | **MEDIUM** | Conservative threshold (0.7), top-3 limit, user feedback loop |
| False negatives (missing CRITICAL) | Low | Critical | **HIGH** | 2.0x priority multiplier, SessionStart redundancy, 100% recall tests |
| Hook crash blocks tool execution | Low | Critical | **HIGH** | Graceful error handling, exit 0 always, try/except all hook code |
| Incorrect lesson inference | Medium | Low | **LOW** | Draft status, user review, manual edit capability |
| Graph pollution with noise | Medium | Low | **LOW** | Periodic cleanup, draft expiry, user can delete nodes |
| Trigger condition staleness | Low | Low | **LOW** | Link to versions, mark deprecated, periodic review |

## Detailed Risk Analysis

### Risk 1: PreToolUse Hook Performance > 100ms

**Description**: If PreToolUse hook takes > 100ms, user experiences noticeable lag before every tool execution.

**Likelihood**: Medium (depends on graph size and query efficiency)

**Impact**: High (degrades UX, users will disable feature)

**Mitigation Strategies**:

1. **Aggressive caching**:
   ```python
   # Load graphs once per session, cache in memory
   _graph_cache = {}

   if not _graph_cache:
       _graph_cache = load_all_graphs()  # 10-30ms once
   ```

2. **Early exit conditions**:
   ```python
   # Skip irrelevant tools
   if tool_name not in RELEVANT_TOOLS:
       return []  # < 1ms

   # Skip if no process knowledge exists
   if not _process_nodes_cache:
       return []  # < 5ms
   ```

3. **Benchmarking and monitoring**:
   ```python
   import time
   start = time.perf_counter()
   results = query_engine.query_relevant_knowledge(...)
   elapsed_ms = (time.perf_counter() - start) * 1000

   if elapsed_ms > 100:
       print(f"⚠️ Slow query: {elapsed_ms:.1f}ms", file=sys.stderr)
   ```

4. **Disable flag**:
   ```bash
   export DISABLE_EXPERIENCE_INJECTION=1
   ```

5. **Performance tests**:
   - Benchmark on graph sizes: 100, 300, 500 nodes
   - Target: P95 < 100ms, P50 < 30ms
   - Fail build if P95 > 150ms

**Residual Risk**: LOW (mitigations are comprehensive)

### Risk 2: False Positives (Irrelevant Injection)

**Description**: Process knowledge injected when not relevant, cluttering context.

**Likelihood**: Medium (depends on trigger condition precision)

**Impact**: Medium (annoying but not harmful, users might disable)

**Mitigation Strategies**:

1. **Conservative threshold**:
   - 0.7 minimum relevance (tested to balance recall vs precision)
   - Prefer false negatives over false positives for non-CRITICAL

2. **Top-3 limit**:
   - Maximum 3 process knowledge items per tool use
   - Forces only highest relevance

3. **User feedback loop**:
   ```python
   # In PreToolUse output
   print("💬 Was this helpful? Reply with '/feedback {node_id} helpful|not-helpful'")
   ```

4. **Monitoring**:
   - Log injection events (node_id, tool_name, relevance_score)
   - Track user feedback
   - Adjust threshold if false positive rate > 10%

5. **Trigger condition refinement**:
   - Use file_patterns + tool_names (high signal)
   - Use keywords sparingly (lower signal)

**Residual Risk**: LOW (threshold tunable based on feedback)

### Risk 3: False Negatives (Missing CRITICAL Items)

**Description**: CRITICAL process knowledge not injected when needed, mistake repeated.

**Likelihood**: Low (2.0x multiplier + SessionStart redundancy)

**Impact**: Critical (defeats purpose of system)

**Mitigation Strategies**:

1. **Priority multiplier (2.0x for CRITICAL)**:
   - CRITICAL items need only 0.4 base relevance to pass 0.7 threshold
   - Ensures CRITICAL always surfaces unless truly irrelevant

2. **SessionStart redundancy**:
   - CRITICAL items shown at session start regardless of relevance
   - User sees warning upfront

3. **100% recall tests**:
   ```python
   def test_critical_recall():
       """Verify CRITICAL items always injected when tool+file match."""
       # Given: CRITICAL checklist for plugin.json
       # When: Writing to plugin.json
       # Then: Checklist MUST be injected
   ```

4. **Monitoring and alerting**:
   - Log when CRITICAL items exist but not injected
   - Alert if pattern detected (e.g., same file written without injection)

5. **Post-action validation** (future enhancement):
   - After tool completes, check if CRITICAL checklist was followed
   - Prompt user if items unchecked

**Residual Risk**: VERY LOW (multiple redundant layers)

### Risk 4: Hook Crash Blocks Tool Execution

**Description**: Exception in PreToolUse hook prevents tool from executing.

**Likelihood**: Low (with proper error handling)

**Impact**: Critical (blocks all work, users very frustrated)

**Mitigation Strategies**:

1. **Graceful error handling**:
   ```python
   def main():
       try:
           results = query_engine.query_relevant_knowledge(...)
           for result in results:
               print(result.formatted_text)
       except Exception as e:
           # Log error but don't block tool
           print(f"⚠️ Experience query failed: {e}", file=sys.stderr)
           # DO NOT RE-RAISE
       finally:
           # ALWAYS exit 0 (success)
           sys.exit(0)
   ```

2. **Input validation**:
   ```python
   # Validate stdin JSON before processing
   try:
       input_data = json.load(sys.stdin)
   except json.JSONDecodeError:
       print("⚠️ Invalid hook input", file=sys.stderr)
       sys.exit(0)  # Exit gracefully
   ```

3. **Timeout protection**:
   ```python
   import signal

   def timeout_handler(signum, frame):
       raise TimeoutError("Query exceeded 200ms")

   signal.alarm(0.2)  # 200ms timeout
   try:
       results = query_engine.query_relevant_knowledge(...)
   except TimeoutError:
       print("⚠️ Query timeout", file=sys.stderr)
   finally:
       signal.alarm(0)  # Cancel alarm
   ```

4. **Extensive testing**:
   - Test with malformed input
   - Test with missing graphs
   - Test with corrupted graph JSON
   - Test with empty graphs

**Residual Risk**: VERY LOW (multiple layers of protection)

### Risk 5: Incorrect Lesson Inference

**Description**: Stop hook extracts incorrect lessons (wrong priority, wrong trigger conditions).

**Likelihood**: Medium (inference algorithm has heuristics)

**Impact**: Low (draft status allows review and deletion)

**Mitigation Strategies**:

1. **Draft status**:
   - All auto-extracted lessons marked `status: "draft"`
   - User can review, edit, or delete

2. **User review command**:
   ```bash
   /knowledge-show {node_id}  # Review draft lesson
   ```

3. **Manual edit capability**:
   - User can edit graph JSON directly
   - Or use CLI to update fields

4. **Conservative inference**:
   - Prefer lower priority if ambiguous
   - Prefer broader trigger conditions if uncertain

5. **Evidence tracing**:
   - Every node includes `evidence` field linking to conversation
   - User can verify context

**Residual Risk**: VERY LOW (user has full control)

### Risk 6: Graph Pollution with Noise

**Description**: Too many low-quality draft lessons accumulate in graphs.

**Likelihood**: Medium (depends on inference accuracy)

**Impact**: Low (can be cleaned up, doesn't affect functionality)

**Mitigation Strategies**:

1. **Periodic cleanup job**:
   ```bash
   # Monthly cron job
   python -m triads.km.cleanup --archive-drafts --older-than=30d
   ```

2. **Draft expiry**:
   - After 30 days, draft lessons auto-archived unless promoted to active

3. **User can delete**:
   - Simple CLI command to delete node by ID

4. **Review prompts**:
   - SessionStart shows count of draft lessons: "5 draft lessons pending review"

5. **Quality scoring** (future):
   - Track if lesson was ever injected
   - Archive lessons never used after 90 days

**Residual Risk**: VERY LOW (cleanup is easy)

### Risk 7: Trigger Condition Staleness

**Description**: File patterns or tool names change, trigger conditions no longer match.

**Likelihood**: Low (file structure usually stable)

**Impact**: Low (false negatives, but not harmful)

**Mitigation Strategies**:

1. **Version linking**:
   ```json
   {
     "valid_from": "v0.7.0",
     "valid_until": "v1.0.0",
     "superseded_by": "process_new_pattern_2025-11-01"
   }
   ```

2. **Deprecation marking**:
   - Mark nodes as deprecated when patterns change
   - Still queryable but shown with warning

3. **Periodic review**:
   - Quarterly review of CRITICAL process knowledge
   - Verify trigger conditions still accurate

4. **Trigger condition testing**:
   ```python
   def test_trigger_conditions():
       """Verify trigger conditions match current project structure."""
       # Test that file patterns match actual files in repo
   ```

**Residual Risk**: VERY LOW (graceful degradation)

## Overall Risk Level

**System Risk Level**: **MEDIUM-LOW**

**Rationale**:
- Two HIGH risks (performance, false negatives) have comprehensive mitigations
- Most risks are LOW impact or LOW likelihood
- Multiple redundant safety layers (SessionStart, draft status, graceful errors)
- User has full control (disable flag, manual edit, delete nodes)

**Recommendation**: **PROCEED WITH IMPLEMENTATION**

Risks are acceptable given:
- High value of feature (prevent repeated mistakes)
- Comprehensive mitigations in place
- Graceful degradation strategies
- User control and visibility

---

# Implementation Roadmap

## Timeline: 5 Days

**Validated phasing with dependency analysis**

## Phase 0: Preparation (Pre-Day 1)

**Duration**: 1 hour

**Tasks**:
1. Create implementation branch: `feature/experience-learning-system`
2. Set up test infrastructure
3. Create benchmark suite

**Deliverables**:
- Branch ready
- Test fixtures prepared
- Benchmarking harness ready

## Day 1: Query Engine + Relevance Scoring

**Goal**: Build and test core query engine with relevance algorithm

**Tasks**:

### Task 1.1: Create ExperienceQueryEngine (3 hours)

**File**: `src/triads/km/experience_query.py`

**Implementation**:
```python
class ExperienceQueryEngine:
    def __init__(self, graphs_dir: Path = Path(".claude/graphs")):
        self._cache: dict[str, dict] = {}
        self._process_nodes_cache: list[dict] | None = None
        self._graphs_dir = graphs_dir

    def query_relevant_knowledge(
        self,
        tool_name: str,
        tool_input: dict,
        recent_messages: list[str] | None = None,
        min_relevance: float = 0.7,
        max_results: int = 3
    ) -> list[ProcessKnowledge]:
        # Implementation per ADR-003
        pass
```

**Tests**:
- Test relevance calculation (tool + file + keywords)
- Test priority multiplier
- Test threshold filtering
- Test top-N limiting

**Acceptance Criteria**:
- All tests pass
- Relevance scores match hand-calculated examples
- Performance: < 50ms for 100-node graph

### Task 1.2: Implement Relevance Scoring (2 hours)

**Functions**:
- `calculate_tool_match_score()`
- `calculate_file_match_score()`
- `calculate_keyword_match_score()`
- `calculate_context_match_score()`

**Tests**:
- Test each component score function
- Test with edge cases (no patterns, no keywords)
- Test fnmatch patterns

**Acceptance Criteria**:
- Component scores correct
- Pattern matching works (fnmatch)

### Task 1.3: Add Formatting Logic (1 hour)

**Function**: `format_for_injection(node: dict) -> str`

**Tests**:
- Test formatting for each process_type (checklist, pattern, warning, requirement)
- Test formatting for each priority (CRITICAL, HIGH, MEDIUM, LOW)
- Verify output is readable

**Acceptance Criteria**:
- Formatted output matches design specs (ADR-002)
- Priority affects formatting (borders, prefixes)

### Task 1.4: Benchmark and Optimize (1 hour)

**Tests**:
- Benchmark on 100, 300, 500 node graphs
- Profile slow functions
- Optimize if needed

**Acceptance Criteria**:
- P50 < 30ms
- P95 < 100ms
- P99 < 150ms

**Deliverables** (Day 1):
- ✅ `experience_query.py` implemented
- ✅ All tests passing
- ✅ Performance benchmarks met

## Day 2: PreToolUse Hook Implementation

**Goal**: Integrate query engine into PreToolUse hook

**Dependencies**: Day 1 complete (query engine working)

### Task 2.1: Create pre_experience_injection.py (2 hours)

**File**: `hooks/pre_experience_injection.py`

**Implementation**:
```python
#!/usr/bin/env python3
"""
PreToolUse Hook: Experience-Based Learning Injection

Queries knowledge graphs for relevant process knowledge and injects
into context before tool execution.
"""

import json
import sys
import time
from pathlib import Path

# Add KM module to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from triads.km.experience_query import ExperienceQueryEngine

def main():
    try:
        # Parse input
        input_data = json.load(sys.stdin)
        tool_name = input_data.get("tool_name")
        tool_input = input_data.get("tool_input", {})

        # Early exit for irrelevant tools
        RELEVANT_TOOLS = {"Write", "Edit", "NotebookEdit", "Bash"}
        if tool_name not in RELEVANT_TOOLS:
            sys.exit(0)

        # Query for relevant knowledge
        start = time.perf_counter()
        engine = ExperienceQueryEngine()
        results = engine.query_relevant_knowledge(
            tool_name=tool_name,
            tool_input=tool_input,
            recent_messages=None,  # TODO: Extract from transcript
            min_relevance=0.7,
            max_results=3
        )
        elapsed_ms = (time.perf_counter() - start) * 1000

        # Log performance
        if elapsed_ms > 100:
            print(f"⚠️ Slow experience query: {elapsed_ms:.1f}ms", file=sys.stderr)

        # Output formatted knowledge
        if results:
            print(f"\n📚 EXPERIENCE-BASED GUIDANCE ({len(results)} items)\n", file=sys.stderr)
            for result in results:
                print(result.formatted_text)
                print(f"  [Relevance: {result.final_score:.2f}, From: {result.triad}]", file=sys.stderr)

    except Exception as e:
        # NEVER block tool execution
        print(f"⚠️ Experience injection error: {e}", file=sys.stderr)
    finally:
        # ALWAYS exit 0
        sys.exit(0)

if __name__ == "__main__":
    main()
```

**Tests**:
- Test with real PreToolUse input
- Test early exit on Read tool
- Test error handling (malformed input)
- Test graceful degradation (missing graphs)

**Acceptance Criteria**:
- Hook receives input and queries engine
- Formatted output injected into context
- Errors logged but don't block tool
- Performance < 100ms (P95)

### Task 2.2: Update hooks.json (30 minutes)

**File**: `hooks/hooks.json`

**Change**:
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/pre_experience_injection.py"
          }
        ]
      }
    ]
  }
}
```

**Note**: Remove or comment out test hook

**Tests**:
- Verify hook fires on tool execution
- Verify output injected into context
- Check PreToolUse log file

**Acceptance Criteria**:
- Hook configured correctly
- Fires before every tool use

### Task 2.3: Add Recent Messages Extraction (2 hours)

**Enhancement**: Extract last 5 messages from transcript for keyword matching

**Implementation**:
```python
def extract_recent_messages(transcript_path: str, limit: int = 5) -> list[str]:
    """Extract recent messages from transcript for keyword matching."""
    if not Path(transcript_path).exists():
        return []

    with open(transcript_path, 'r') as f:
        lines = f.readlines()

    messages = []
    for line in lines[-20:]:  # Last 20 lines should cover last 5 messages
        try:
            entry = json.loads(line)
            content = entry.get('content', '')
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and 'text' in item:
                        messages.append(item['text'])
            elif isinstance(content, str):
                messages.append(content)
        except json.JSONDecodeError:
            continue

    return messages[-limit:]
```

**Tests**:
- Test with real transcript files
- Test with empty transcript
- Test JSON parsing

**Acceptance Criteria**:
- Recent messages extracted correctly
- Keyword matching uses recent context

### Task 2.4: End-to-End Testing (1.5 hours)

**Scenarios**:
1. Write to plugin.json → Version Bump Checklist injected
2. Write to README.md → No injection (not relevant)
3. Read file → Early exit, no query
4. Bash with "deploy" keyword → Deployment patterns injected

**Tests**:
- Integration tests with real graphs
- Verify formatting in context
- Verify performance in real session

**Acceptance Criteria**:
- All scenarios pass
- User sees formatted guidance before tool execution
- No false positives, no false negatives for test cases

**Deliverables** (Day 2):
- ✅ PreToolUse hook working
- ✅ Knowledge injected before tool execution
- ✅ End-to-end tests passing

## Day 3: Stop Hook Lesson Extraction

**Goal**: Automatically extract lessons from conversation and create process knowledge nodes

**Dependencies**: Day 1-2 complete (query engine + PreToolUse working)

### Task 3.1: Add [PROCESS_KNOWLEDGE] Block Parsing (2 hours)

**File**: `hooks/on_stop.py` (extend existing)

**Implementation**:
```python
def extract_process_knowledge_blocks(text: str) -> list[dict]:
    """Extract [PROCESS_KNOWLEDGE]...[/PROCESS_KNOWLEDGE] blocks."""
    pattern = r'\[PROCESS_KNOWLEDGE\](.*?)\[/PROCESS_KNOWLEDGE\]'
    matches = re.findall(pattern, text, re.DOTALL)

    blocks = []
    for match in matches:
        block = {}
        for line in match.strip().split('\n'):
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()

                # Parse nested structures
                if key in ['trigger_conditions', 'checklist', 'pattern', 'warning', 'requirement']:
                    # Parse as YAML-like structure
                    block[key] = parse_nested_structure(value)
                else:
                    block[key] = value

        blocks.append(block)

    return blocks
```

**Tests**:
- Test parsing explicit [PROCESS_KNOWLEDGE] blocks
- Test with nested structures (checklist items, trigger conditions)
- Test with missing fields

**Acceptance Criteria**:
- Blocks parsed correctly
- Nested structures preserved
- Handles malformed blocks gracefully

### Task 3.2: Create Process Knowledge Nodes (2 hours)

**Function**: `create_process_knowledge_node(block: dict) -> dict`

**Implementation**:
```python
def create_process_knowledge_node(
    block: dict,
    created_by: str = "lesson-extractor"
) -> dict:
    """Create a process knowledge node from extracted block."""
    node_id = f"process_{block.get('label', 'unknown').replace(' ', '_')}_{datetime.now().strftime('%Y-%m-%d')}"

    node = {
        "id": node_id,
        "type": "Concept",
        "label": block.get('label', 'Untitled Process Knowledge'),
        "description": block.get('description', ''),
        "confidence": block.get('confidence', 1.0),
        "evidence": block.get('evidence', 'Explicit [PROCESS_KNOWLEDGE] block'),
        "created_by": created_by,
        "created_at": datetime.now().isoformat(),
        "status": "draft",  # Mark for review

        "process_type": block.get('type', 'pattern'),
        "priority": block.get('priority', 'MEDIUM'),
        "trigger_conditions": block.get('trigger_conditions', {})
    }

    # Add type-specific content
    if node['process_type'] == 'checklist':
        node['checklist'] = block.get('checklist', {})
    elif node['process_type'] == 'pattern':
        node['pattern'] = block.get('pattern', {})
    elif node['process_type'] == 'warning':
        node['warning'] = block.get('warning', {})
    elif node['process_type'] == 'requirement':
        node['requirement'] = block.get('requirement', {})

    return node
```

**Tests**:
- Test node creation for each process_type
- Test with missing fields (use defaults)
- Verify node structure matches schema (ADR-002)

**Acceptance Criteria**:
- Nodes created with correct structure
- Draft status set
- Evidence preserved

### Task 3.3: Integrate into Stop Hook (1 hour)

**File**: `hooks/on_stop.py`

**Integration Point**: After existing [GRAPH_UPDATE] processing

```python
# After graph updates processed

# Extract process knowledge
process_blocks = extract_process_knowledge_blocks(conversation_text)

if process_blocks:
    print(f"\n📚 Detected {len(process_blocks)} process knowledge block(s)", file=sys.stderr)

    for block in process_blocks:
        # Create node
        node = create_process_knowledge_node(block)

        # Determine target triad
        target_triad = block.get('triad', 'default')

        # Add to graph
        graph_data = load_graph(target_triad)
        graph_data['nodes'].append(node)
        save_graph(graph_data, target_triad)

        print(f"  ✓ Created: {node['label']} ({node['priority']}) [DRAFT]", file=sys.stderr)
        print(f"    Review with: /knowledge-show {node['id']}", file=sys.stderr)
```

**Tests**:
- Test with conversation containing [PROCESS_KNOWLEDGE] blocks
- Verify nodes added to correct graph
- Verify draft status
- Check stderr output

**Acceptance Criteria**:
- Blocks detected and parsed
- Nodes added to graphs
- User notified in stderr

### Task 3.4: Add Pattern-Based Detection (Phase 2 - Optional for MVP) (2 hours)

**Patterns to detect**:
- User correction: "you forgot", "you missed"
- Explicit lesson: "lesson learned:", "important:"
- Repeated mistake: Check graph for similar corrections

**Implementation**: See ADR-004 for algorithms

**Tests**:
- Test each pattern detector
- Test priority inference
- Test trigger condition inference

**Acceptance Criteria**:
- Patterns detected with high precision
- Inferred fields reasonable
- False positive rate < 20%

**Deliverables** (Day 3):
- ✅ Stop hook extracts [PROCESS_KNOWLEDGE] blocks
- ✅ Process knowledge nodes created and added to graphs
- ✅ User notified of learned lessons
- ✅ (Optional) Pattern-based detection working

## Day 4: SessionStart Enhancement

**Goal**: Display CRITICAL priority process knowledge at session start

**Dependencies**: Day 1-3 complete (full system working)

### Task 4.1: Add Process Knowledge to SessionStart (2 hours)

**File**: `hooks/session_start.py`

**Enhancement**: After existing graph summaries, add CRITICAL process knowledge section

**Implementation**:
```python
# After displaying graph summaries

# Load CRITICAL process knowledge
critical_knowledge = []
for triad_name in list_triads():
    graph = load_graph(triad_name)
    if not graph:
        continue

    for node in graph.get('nodes', []):
        if node.get('type') == 'Concept' and node.get('process_type'):
            if node.get('priority') == 'CRITICAL' and node.get('status') != 'archived':
                critical_knowledge.append({
                    'node': node,
                    'triad': triad_name
                })

if critical_knowledge:
    output.append("=" * 80)
    output.append("# ⚠️ CRITICAL PROCESS KNOWLEDGE")
    output.append("=" * 80)
    output.append("")
    output.append("**The following procedures are CRITICAL. Failure to follow them has caused production issues.**")
    output.append("")

    for item in critical_knowledge[:5]:  # Top 5 only
        node = item['node']
        output.append(f"## {node.get('label')}")
        output.append(f"**Triad**: {item['triad']}")
        output.append(f"**Type**: {node.get('process_type')}")
        output.append("")

        # Format based on type
        if node.get('process_type') == 'checklist':
            checklist = node.get('checklist', {})
            output.append(f"**{checklist.get('title', 'Checklist')}**:")
            for item in checklist.get('items', []):
                output.append(f"- [ ] {item}")
        elif node.get('process_type') == 'pattern':
            pattern = node.get('pattern', {})
            output.append(f"**When**: {pattern.get('situation', 'N/A')}")
            output.append(f"**Do**: {pattern.get('action', 'N/A')}")
        # ... other types

        output.append("")
        output.append("-" * 80)
        output.append("")
```

**Tests**:
- Test with CRITICAL nodes in graph
- Test with no CRITICAL nodes
- Verify formatting
- Check limit (top 5)

**Acceptance Criteria**:
- CRITICAL knowledge displayed at session start
- Formatting clear and readable
- Limited to top 5 (not overwhelming)

### Task 4.2: Add Draft Lessons Summary (1 hour)

**Enhancement**: Show count of draft lessons pending review

**Implementation**:
```python
# After CRITICAL process knowledge

# Count draft lessons
draft_count = 0
for triad_name in list_triads():
    graph = load_graph(triad_name)
    if not graph:
        continue
    draft_count += sum(
        1 for node in graph.get('nodes', [])
        if node.get('type') == 'Concept'
        and node.get('process_type')
        and node.get('status') == 'draft'
    )

if draft_count > 0:
    output.append(f"📚 **{draft_count} draft lesson(s) pending review**")
    output.append(f"   Review with: `/knowledge-search` or `/knowledge-status`")
    output.append("")
```

**Tests**:
- Test with draft lessons
- Test with no drafts
- Verify count accuracy

**Acceptance Criteria**:
- Draft count displayed
- User aware of pending reviews

### Task 4.3: Testing and Validation (1 hour)

**Scenarios**:
- Session with CRITICAL knowledge → displayed
- Session with no CRITICAL knowledge → not displayed
- Session with draft lessons → count shown

**Acceptance Criteria**:
- All scenarios work
- Output clear and helpful

**Deliverables** (Day 4):
- ✅ SessionStart displays CRITICAL process knowledge
- ✅ Draft lessons summary shown
- ✅ User aware of important procedures at session start

## Day 5: End-to-End Testing and Documentation

**Goal**: Validate full system, document, and prepare for release

**Dependencies**: Day 1-4 complete (full system implemented)

### Task 5.1: Integration Testing (2 hours)

**Test Scenarios**:

1. **Full Learning Loop**:
   - User corrects mistake
   - Claude creates [PROCESS_KNOWLEDGE] block
   - Stop hook extracts and adds to graph
   - Next session: CRITICAL knowledge shown at SessionStart
   - Relevant action: PreToolUse injects knowledge
   - Mistake prevented

2. **Version Bump Scenario** (real-world test):
   - Add version bump checklist to deployment graph
   - Start new session
   - Attempt to write to plugin.json
   - Verify checklist injected before Write
   - Complete all items
   - Verify marketplace.json updated

3. **Performance Test**:
   - Graph with 30 process knowledge nodes
   - Measure PreToolUse latency (P50, P95, P99)
   - Verify < 100ms target met

4. **Error Handling Test**:
   - Malformed graph JSON
   - Missing trigger_conditions field
   - Hook crash simulation
   - Verify graceful degradation

**Acceptance Criteria**:
- All scenarios pass
- No regressions
- Performance targets met
- Errors handled gracefully

### Task 5.2: Documentation (2 hours)

**Files to create/update**:

1. **docs/EXPERIENCE_LEARNING_SYSTEM.md**:
   - Overview of system
   - How to use [PROCESS_KNOWLEDGE] blocks
   - How to review draft lessons
   - How to disable (DISABLE_EXPERIENCE_INJECTION=1)

2. **README.md** (update):
   - Add section on experience-based learning
   - Link to docs

3. **CHANGELOG.md**:
   - Add v0.8.0 entry
   - List new features

4. **Examples**:
   - Example [PROCESS_KNOWLEDGE] block
   - Example version bump checklist
   - Example deployment pattern

**Acceptance Criteria**:
- Documentation complete and clear
- Examples runnable
- User can understand system from docs

### Task 5.3: User Guide and CLI Commands (1 hour)

**CLI Enhancements**:

1. `/knowledge-review-drafts`:
   - List all draft process knowledge
   - Show details
   - Prompt to promote/delete

2. `/knowledge-promote <node_id>`:
   - Change status from draft → active
   - Set reviewed_by

3. `/knowledge-archive <node_id>`:
   - Change status to archived
   - Remove from active queries

**Implementation**: Extend `src/triads/km/graph_access.py`

**Acceptance Criteria**:
- Commands work
- User can manage process knowledge

### Task 5.4: Final Validation and Cleanup (1 hour)

**Tasks**:
- Remove test hooks
- Clean up debug logging
- Verify all tests pass
- Run linters/formatters
- Update version to 0.8.0

**Checklist**:
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Performance benchmarks met
- [ ] Documentation complete
- [ ] No debug code in production
- [ ] Version bumped to 0.8.0

**Deliverables** (Day 5):
- ✅ Full system tested end-to-end
- ✅ Documentation complete
- ✅ CLI commands working
- ✅ Ready for release

---

## Dependency Graph

```
Day 0 (Prep)
    ↓
Day 1 (Query Engine)
    ↓
Day 2 (PreToolUse Hook) → Depends on: Day 1
    ↓
Day 3 (Stop Hook) → Depends on: Day 1, 2
    ↓
Day 4 (SessionStart) → Depends on: Day 1, 2, 3
    ↓
Day 5 (Testing & Docs) → Depends on: Day 1, 2, 3, 4
```

**Critical Path**: Day 1 → Day 2 → Day 3 → Day 4 → Day 5

**Parallelization Opportunities**:
- Day 2 Task 2.3 (recent messages) can be done in parallel with Task 2.1
- Day 3 Task 3.4 (pattern detection) can be done after MVP if time runs short
- Day 5 Task 5.2 (docs) and Task 5.3 (CLI) can overlap

---

## Risk Mitigation During Implementation

### If Day 1 Performance < Target

**Fallback**:
- Reduce process knowledge limit to top-1 instead of top-3
- Skip keyword matching (only tool + file)
- Add more aggressive early exits

**Timeline Impact**: +0.5 days (optimization)

### If PreToolUse Hook Unstable

**Fallback**:
- Disable PreToolUse, use SessionStart only
- Reduces functionality but preserves learning

**Timeline Impact**: No change (fallback is simpler)

### If Lesson Extraction Too Noisy

**Fallback**:
- Phase 1: Only explicit [PROCESS_KNOWLEDGE] blocks
- Phase 2: Pattern detection deferred to future release

**Timeline Impact**: No change (Phase 1 is MVP)

---

## Success Criteria (Overall)

### Functional Requirements

- ✅ CRITICAL process knowledge injected before relevant tools
- ✅ Lessons automatically extracted from [PROCESS_KNOWLEDGE] blocks
- ✅ Process knowledge displayed at SessionStart
- ✅ Draft lessons reviewable and editable
- ✅ User can disable system (environment variable)

### Non-Functional Requirements

- ✅ PreToolUse hook latency < 100ms (P95)
- ✅ 100% recall for CRITICAL items (never miss)
- ✅ < 10% false positive rate (rarely inject irrelevant)
- ✅ Graceful degradation on errors (never block tools)
- ✅ Backward compatible (existing graphs work)

### User Experience

- ✅ Clear, readable formatting
- ✅ Non-intrusive (only when relevant)
- ✅ Helpful (prevents repeated mistakes)
- ✅ Controllable (user can disable/edit)

---

## Post-Implementation

### Monitoring (Week 1-2)

- Log all injection events (node_id, tool_name, relevance_score)
- Track user feedback (helpful/not-helpful)
- Measure performance (latency distribution)
- Count false positives/negatives

### Tuning (Week 3-4)

- Adjust relevance threshold if needed
- Tweak priority multipliers
- Refine trigger conditions based on usage
- Add common patterns to defaults

### Future Enhancements (v0.9.0+)

- LLM-based lesson extraction (async batch job)
- Semantic search with embeddings (optional)
- Web UI for process knowledge management
- Post-action validation (did user follow checklist?)
- Cross-session learning (repeated mistakes across users)

---

**Design Complete. Ready for Implementation Triad.**
