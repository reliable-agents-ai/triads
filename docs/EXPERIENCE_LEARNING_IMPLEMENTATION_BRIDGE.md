# Experience Learning System - Implementation Bridge

**Design Bridge Agent Handoff**
**Date**: 2025-10-17
**Status**: Design Approved ✅ - Ready for Implementation
**Target Version**: 0.8.0

---

## Executive Summary

**What to Build**: Experience-based learning system that learns from mistakes, stores procedural knowledge, and injects it BEFORE actions to prevent repeated mistakes.

**Why It Matters**: The marketplace.json mistake (v0.7.0-alpha.1) happened because we created a checklist AFTER the mistake instead of consulting it BEFORE. This system closes that loop.

**Key Innovation**: PreToolUse hooks (newly verified as functional) enable perfect-timing injection - knowledge appears exactly when needed, not too early or too late.

**Timeline**: 5 days (validated with dependency analysis)

**Risk Level**: MEDIUM-LOW (performance-sensitive but comprehensive mitigations in place)

---

## Critical Architectural Decisions (Top 5 ADRs)

### ADR-001: PreToolUse Hook as Primary Injection Point ⭐ CRITICAL

**Decision**: Use PreToolUse hook (with SessionStart + Stop support) for experience injection

**Why This Matters**:
- **Perfect timing**: Inject knowledge EXACTLY before action (e.g., before Writing version file)
- **High precision**: Can filter by tool_name + file_path + parameters
- **Proven functional**: Test logs confirm PreToolUse works reliably
- **Maximum coverage**: Catches all file modifications, git commands, deployments

**Implementation Impact**:
- Hook MUST complete < 100ms (fires frequently)
- Hook MUST NEVER block tool execution (exit 0 always)
- Early exit on irrelevant tools (Read, Glob, Grep)
- Performance monitoring essential

**Critical Code Pattern**:
```python
def main():
    try:
        # All hook logic
        ...
    except Exception as e:
        print(f"⚠️ Error: {e}", file=sys.stderr)
    finally:
        sys.exit(0)  # ALWAYS exit 0, never block
```

**Alternatives Rejected**:
- SessionStart only: Wrong timing (too early, not action-specific)
- UserPromptSubmit: No tool context, can't see file paths
- LLM-based relevance: Too slow (500-2000ms per call)

---

### ADR-002: Process Knowledge Schema ⭐ CRITICAL

**Decision**: Use Concept nodes with structured trigger_conditions and typed process knowledge

**Schema Structure**:
```json
{
  "id": "process_{purpose}_{timestamp}",
  "type": "Concept",
  "label": "Version Bump File Checklist",
  "description": "Checklist of all files to update during version bump",
  "confidence": 1.0,
  "evidence": "Missed marketplace.json in v0.7.0-alpha.1",
  "created_by": "lesson-extractor",
  "created_at": "ISO timestamp",
  "status": "draft",

  "process_type": "checklist|pattern|warning|requirement",
  "priority": "CRITICAL|HIGH|MEDIUM|LOW",

  "trigger_conditions": {
    "tool_names": ["Write", "Edit"],
    "file_patterns": ["**/plugin.json", "**/*version*"],
    "action_keywords": ["version bump", "release"],
    "context_keywords": ["deployment"],
    "triad_names": ["deployment"]
  },

  "checklist": {
    "title": "Version Bump Complete Checklist",
    "items": [
      "pyproject.toml",
      "plugin.json",
      "marketplace.json",
      "CHANGELOG.md"
    ]
  }
}
```

**Why Structured trigger_conditions**:
- Enables FAST matching (< 100ms) vs LLM inference (500-2000ms)
- Deterministic: same input always matches same knowledge
- Queryable: can filter by tool, file pattern, keywords

**Four Process Types**:
1. **checklist**: Step-by-step procedures (most common)
2. **pattern**: "When X, do Y" guidance
3. **warning**: Risks to be aware of
4. **requirement**: Hard constraints that must be met

**Backward Compatible**: Uses existing Concept node type, no schema migration needed

---

### ADR-003: Relevance Scoring Algorithm ⭐ CRITICAL

**Decision**: Structured scoring with tool (40%) + file (40%) + keywords (20%)

**Formula**:
```python
base_relevance = (
    tool_match * 0.40 +      # Exact tool name match
    file_match * 0.40 +      # Glob pattern match
    keyword_match * 0.10 +   # Action keywords
    context_match * 0.10     # Context keywords
)

final_score = base_relevance * priority_multiplier

priority_multiplier = {
    "CRITICAL": 2.0,   # Double the score
    "HIGH": 1.5,
    "MEDIUM": 1.0,
    "LOW": 0.5
}

# Inject if final_score >= 0.7
```

**Why These Weights**:
- Tool + file = 80%: High signal (Write to plugin.json very different from Read README.md)
- Keywords = 20%: Medium signal (user intent but might be vague)
- Priority multiplier AFTER base score ensures CRITICAL items never lost

**CRITICAL Safety Guarantee**:
- CRITICAL items need only 0.4 base relevance to inject
- 0.4 * 2.0 = 0.8 > 0.7 threshold ✅
- Achieves 100% recall for CRITICAL process knowledge

**Performance Target**: < 100ms (P95) via:
- Early exit on irrelevant tools
- Lazy graph loading (cache in memory)
- Fast path if no process knowledge exists
- Simple string matching (no regex in hot path)

**Alternatives Rejected**:
- LLM-based: Too slow (500-2000ms)
- Embeddings: Heavy dependency (500MB+), 50-200ms inference
- Simple keywords: Not precise enough (high false positives)

---

### ADR-004: Lesson Extraction Mechanism ⭐ HIGH

**Decision**: Pattern-based extraction in Stop hook with auto-add as draft

**Detection Patterns** (priority order):
1. **[PROCESS_KNOWLEDGE] blocks** (highest trust - use directly)
2. User correction patterns: "you forgot", "you missed"
3. Explicit lesson statements: "lesson learned:", "important:"
4. Repeated mistakes: Same correction 2+ times

**Inference Algorithms**:

```python
def infer_priority(correction_type, impact_level, repetition_count):
    if repetition_count >= 2:
        return "CRITICAL"  # Repeated mistakes always critical

    if correction_type == "user_correction":
        if impact_level == "production":  # deploy, release, security
            return "CRITICAL"
        elif impact_level == "quality":  # tests, bugs
            return "HIGH"
        else:
            return "MEDIUM"

    # ... see ADR-004 for full logic
```

**Auto-Add as Draft**:
- Set `status: "draft"` on all auto-extracted nodes
- User reviews later with `/knowledge-review-drafts` CLI command
- Can edit/delete directly in graph JSON
- Lessons immediately usable, refined later

**Why Pattern-Based** (not LLM-based):
- Fast: < 50ms vs 2-10 seconds for LLM inference
- Stop hook must not delay session end
- Can upgrade to LLM batch processing later (async)

---

### ADR-005: Priority System ⭐ HIGH

**Decision**: Four levels (CRITICAL, HIGH, MEDIUM, LOW) with clear semantics

| Priority | Definition | Multiplier | Display | Recall Target |
|----------|-----------|-----------|---------|---------------|
| CRITICAL | Production-breaking, data loss, security | 2.0x | SessionStart + PreToolUse | 100% |
| HIGH | Quality impact, prevents bugs | 1.5x | PreToolUse | 90% |
| MEDIUM | Nice-to-have, improves workflow | 1.0x | PreToolUse if relevant | 50% |
| LOW | Informational, rarely needed | 0.5x | Rarely | 10% |

**Assignment Rules**:
- Repeated mistake (2+) → CRITICAL
- User correction + production impact → CRITICAL
- User correction + quality impact → HIGH
- Explicit lesson + production → HIGH
- Proactive suggestion → MEDIUM

**Display Formatting**:
- CRITICAL: Red ⚠️, `====` borders, all caps
- HIGH: Yellow ⚠️, `----` borders
- MEDIUM: Blue ℹ️, `----` borders
- LOW: Gray ℹ️, no borders

**Why Four Levels** (not 3 or 5):
- 3 levels: Not enough granularity ("Normal" too broad)
- 5+ levels: Decision paralysis, unclear semantics
- 4 levels: Production → Quality → Style → Info spectrum

---

## Implementation Roadmap (5 Days)

### Day 1: Query Engine + Relevance Scoring ⭐ CRITICAL PATH

**Goal**: Build core query engine with relevance algorithm

**Tasks**:
1. Create `src/triads/km/experience_query.py` - ExperienceQueryEngine class
2. Implement relevance scoring (tool, file, keywords)
3. Add formatting logic (each process_type + priority)
4. Write unit tests (all scoring functions)
5. Run benchmarks (target: P95 < 100ms)

**Deliverables**:
- ✅ Query engine working and tested
- ✅ Performance targets met
- ✅ All tests passing

**Blockers**: None (can start immediately)

---

### Day 2: PreToolUse Hook Implementation ⭐ CRITICAL PATH

**Goal**: Integrate query engine into PreToolUse hook

**Dependencies**: Day 1 complete

**Tasks**:
1. Create `hooks/pre_experience_injection.py`
2. Implement main() with error handling (ALWAYS exit 0)
3. Add early exit for irrelevant tools
4. Integrate ExperienceQueryEngine
5. Extract recent messages from transcript (for keyword matching)
6. Update `hooks/hooks.json` to register hook
7. End-to-end testing

**Deliverables**:
- ✅ PreToolUse hook fires before tool execution
- ✅ Knowledge injected into context
- ✅ Performance < 100ms
- ✅ Error handling prevents tool blocking

**Blockers**: Requires Day 1 query engine

---

### Day 3: Stop Hook Lesson Extraction ⭐ CRITICAL PATH

**Goal**: Auto-extract lessons from conversation

**Dependencies**: Day 1-2 complete (so extracted lessons can be tested with injection)

**Tasks**:
1. Extend `hooks/on_stop.py` with [PROCESS_KNOWLEDGE] parsing
2. Implement `extract_process_knowledge_blocks()`
3. Implement `create_process_knowledge_node()` (sets status: draft)
4. Integrate into existing Stop hook flow
5. Test with conversation containing [PROCESS_KNOWLEDGE] blocks
6. (Optional) Pattern-based detection (user corrections)

**Deliverables**:
- ✅ [PROCESS_KNOWLEDGE] blocks parsed
- ✅ Nodes added to graphs with draft status
- ✅ Evidence preserved

**Blockers**: Requires Day 1 query engine (to test extracted lessons work)

---

### Day 4: SessionStart Enhancement + CLI Commands

**Goal**: Display CRITICAL items at session start, add review workflow

**Dependencies**: Day 3 complete (draft lessons exist)

**Tasks**:
1. Extend `hooks/session_start.py` with CRITICAL process knowledge section
2. Add draft lessons summary
3. Implement `/knowledge-review-drafts` CLI command
4. Implement `/knowledge-promote <node_id>` CLI command
5. Implement `/knowledge-archive <node_id>` CLI command
6. Integration testing

**Deliverables**:
- ✅ CRITICAL items shown at session start
- ✅ Draft count displayed
- ✅ CLI commands functional

**Blockers**: Requires Day 3 (draft lessons to review)

---

### Day 5: End-to-End Testing + Documentation

**Goal**: Validate full system, create user docs

**Dependencies**: Day 1-4 complete

**Tasks**:
1. Full learning loop test (correction → extraction → injection → prevention)
2. Version bump scenario test (marketplace.json mistake prevented)
3. Performance benchmarks (all graphs sizes)
4. Error handling tests (hook crashes, malformed input)
5. Create user documentation (`docs/EXPERIENCE_LEARNING_SYSTEM.md`)
6. Update `README.md` and `CHANGELOG.md`
7. Clean up debug code, finalize

**Deliverables**:
- ✅ All integration tests passing
- ✅ Documentation complete
- ✅ Ready for v0.8.0 release

**Blockers**: Requires Day 1-4 complete

---

## Critical Implementation Details

### Performance Requirements (NON-NEGOTIABLE)

**PreToolUse Hook Latency**:
- P50: < 30ms
- P95: < 100ms ⭐ PRIMARY TARGET
- P99: < 150ms

**How to Achieve**:
1. **Early exit**: Skip irrelevant tools immediately
   ```python
   RELEVANT_TOOLS = {"Write", "Edit", "NotebookEdit", "Bash"}
   if tool_name not in RELEVANT_TOOLS:
       return []  # < 1ms
   ```

2. **Lazy graph loading**: Load once, cache for session
   ```python
   if not self._cache:
       self._cache = self._load_all_graphs()  # 10-30ms once
   ```

3. **Fast path**: No process knowledge → exit immediately
   ```python
   if not process_nodes:
       return []  # < 5ms
   ```

4. **Simple matching**: fnmatch + substring (no regex)
   ```python
   # Fast
   fnmatch.fnmatch(file_path, pattern)
   keyword in text.lower()

   # Slow - DON'T USE
   re.search(r'complex.*regex', text)
   ```

5. **Monitor continuously**:
   ```python
   if elapsed_ms > 100:
       print(f"⚠️ Slow query: {elapsed_ms:.1f}ms", file=sys.stderr)
   ```

---

### Error Handling (NON-NEGOTIABLE)

**Golden Rule**: Hook MUST NEVER block tool execution

**Pattern**:
```python
def main():
    try:
        # All hook logic
        input_data = json.load(sys.stdin)
        tool_name = input_data.get("tool_name")

        # Early exits
        if tool_name not in RELEVANT_TOOLS:
            sys.exit(0)

        # Query and inject
        engine = ExperienceQueryEngine()
        results = engine.query_relevant_knowledge(...)

        # Output
        for result in results:
            print(result.formatted_text)

    except Exception as e:
        # Log but NEVER re-raise
        print(f"⚠️ Experience injection error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)

    finally:
        # ALWAYS exit 0 (success)
        sys.exit(0)
```

**Test**: Inject exceptions at every point, verify tool still executes

---

### CRITICAL Recall Guarantee (NON-NEGOTIABLE)

**Requirement**: 100% recall for CRITICAL process knowledge

**How to Achieve**:
1. **Priority multiplier**: 2.0x for CRITICAL
   - CRITICAL needs only 0.4 base relevance to pass 0.7 threshold
   - Even if file doesn't match perfectly, CRITICAL still injects

2. **SessionStart redundancy**: Show CRITICAL items at session start
   - Even if PreToolUse fails/misses, user sees it upfront
   - Layered defense

3. **Testing**:
   ```python
   def test_critical_recall():
       """CRITICAL items MUST inject when relevant."""
       # Given: CRITICAL node matching tool + file
       # When: PreToolUse fires
       # Then: MUST inject (100% recall)

       assert "Version Bump Checklist" in injected_context
   ```

**Never Compromise On**: Missing CRITICAL item = failure

---

## File Structure (What to Create)

### New Files

```
src/triads/km/
├── experience_query.py      # ExperienceQueryEngine (Day 1)
└── process_knowledge.py     # ProcessKnowledge dataclass (Day 1)

hooks/
└── pre_experience_injection.py  # PreToolUse hook (Day 2)

tests/km/
├── test_experience_query.py     # Query engine tests (Day 1)
├── test_process_knowledge.py    # Schema tests (Day 1)
└── test_integration_experience.py  # End-to-end tests (Day 5)

docs/
└── EXPERIENCE_LEARNING_SYSTEM.md  # User documentation (Day 5)
```

### Files to Extend

```
hooks/
├── on_stop.py           # Add [PROCESS_KNOWLEDGE] parsing (Day 3)
├── session_start.py     # Add CRITICAL display (Day 4)
└── hooks.json           # Register PreToolUse hook (Day 2)

src/triads/km/
└── graph_access.py      # Add CLI commands (Day 4)

README.md                # Mention new feature (Day 5)
CHANGELOG.md             # v0.8.0 section (Day 5)
```

---

## Testing Strategy

### Unit Tests (Day 1)

**File**: `tests/km/test_experience_query.py`

**Critical Test Cases**:
- `test_tool_match_score()`: Exact match vs no match
- `test_file_match_score()`: fnmatch patterns work
- `test_keyword_match_score()`: Case-insensitive substring
- `test_relevance_calculation()`: Full formula with examples
- `test_priority_multiplier()`: 2.0x for CRITICAL
- `test_threshold_filtering()`: 0.7 minimum applied
- `test_top_n_limiting()`: Max 3 results
- `test_critical_recall()`: CRITICAL always injects when relevant ⭐

**Run**: `pytest tests/km/test_experience_query.py -v`

---

### Integration Tests (Day 2)

**File**: `tests/km/test_integration_experience.py`

**Critical Test Cases**:
- `test_pretooluse_hook_fires()`: Hook receives input
- `test_early_exit_on_read()`: Read tool skipped (< 1ms)
- `test_injection_on_write()`: Write to version file → inject
- `test_performance_benchmark()`: Latency < 100ms ⭐
- `test_error_handling()`: Malformed input doesn't crash ⭐

**Run**: `pytest tests/km/test_integration_experience.py -v`

---

### End-to-End Test (Day 5) ⭐ CRITICAL

**Scenario**: Full learning loop (prevents marketplace.json mistake)

```python
def test_full_learning_loop():
    """
    Test: User correction → Lesson extracted → Knowledge injected → Mistake prevented

    This is THE test that validates the entire system.
    """

    # 1. Simulate user correction in conversation
    conversation = """
    User: You forgot to update marketplace.json
    Assistant: You're right, let me add:
    [PROCESS_KNOWLEDGE]
    type: checklist
    priority: CRITICAL
    label: Version Bump File Checklist
    trigger_conditions:
      tool_names: [Write, Edit]
      file_patterns: ["**/plugin.json", "**/*version*"]
    checklist:
      items:
        - pyproject.toml
        - plugin.json
        - marketplace.json
        - CHANGELOG.md
    [/PROCESS_KNOWLEDGE]
    """

    # 2. Run Stop hook → Extract lesson
    result = run_stop_hook(conversation)
    assert "Created: Version Bump File Checklist (CRITICAL)" in result

    # 3. Load graph → Verify node added
    graph = load_graph('deployment')
    node = find_node_by_label(graph, 'Version Bump File Checklist')
    assert node is not None
    assert node['priority'] == 'CRITICAL'
    assert node['status'] == 'draft'

    # 4. Simulate Write to plugin.json
    pretooluse_input = {
        "tool_name": "Write",
        "tool_input": {"file_path": "/path/to/plugin.json"}
    }

    # 5. Run PreToolUse hook → Check injection
    output = run_pretooluse_hook(pretooluse_input)
    assert "Version Bump File Checklist" in output
    assert "marketplace.json" in output
    assert "CRITICAL CHECKLIST" in output

    # 6. Verify mistake prevented
    # In real usage: Agent sees checklist → Updates all files → No mistake
```

**This Test MUST Pass**: It's the whole point of the system

---

## Success Metrics (Post-Implementation)

### Performance Metrics

- **PreToolUse latency**: P95 < 100ms ✅
- **Injection frequency**: 5-10% of tool executions (not too frequent)
- **False positive rate**: < 10% ("not helpful" feedback)

### Functional Metrics

- **CRITICAL recall**: 100% (never miss CRITICAL items) ⭐
- **Lessons learned**: 1-2 per session (if mistakes occur)
- **Draft review rate**: > 50% promoted to active

### User Experience Metrics

- **System usage**: < 5% users disable (DISABLE_EXPERIENCE_INJECTION=1)
- **Manual edits**: Shows engagement
- **Mistake recurrence**: 0 repeated for CRITICAL items ⭐

---

## Common Issues and Solutions

### Issue 1: PreToolUse Hook Not Firing

**Symptoms**: No injection, no logs

**Debug**:
1. Check `hooks/hooks.json`: Hook registered?
2. Check permissions: `chmod +x hooks/pre_experience_injection.py`
3. Check Python path: Shebang `#!/usr/bin/env python3`
4. Test manually: `echo '{"tool_name":"Write","tool_input":{}}' | python3 hooks/pre_experience_injection.py`

**Solution**: Usually permissions or JSON syntax error

---

### Issue 2: Query Too Slow (> 100ms)

**Symptoms**: Latency warnings in stderr

**Debug**:
1. Check graph size: How many nodes? How many process knowledge nodes?
2. Profile hot functions: Add timing wrappers
3. Check caching: Is graph loaded every time?

**Solution**:
- Add aggressive caching
- Early exit on irrelevant tools
- Optimize hot paths (remove regex, use fnmatch)

---

### Issue 3: False Negatives (CRITICAL Item Missed)

**Symptoms**: CRITICAL checklist not injected when expected ⚠️ HIGH SEVERITY

**Debug**:
1. Check trigger_conditions: Do tool_names and file_patterns match?
2. Check priority: Is it actually CRITICAL (2.0x multiplier)?
3. Check base relevance: Log the calculated score
4. Check threshold: Is 0.7 too high?

**Solution**:
- Broaden trigger_conditions (add more file patterns)
- Verify priority is CRITICAL
- If base relevance < 0.4, fix trigger conditions (CRITICAL needs 0.4 minimum)

**This is a FAILURE** - must fix immediately

---

## Design References

**Full Design Docs**:
- `/Users/iainnb/Documents/repos/triads/docs/EXPERIENCE_LEARNING_SYSTEM_DESIGN.md` (15,000+ words, all ADRs)
- `/Users/iainnb/Documents/repos/triads/docs/EXPERIENCE_LEARNING_DESIGN_SUMMARY.md` (Executive summary)
- `/Users/iainnb/Documents/repos/triads/docs/EXPERIENCE_LEARNING_IMPLEMENTATION_GUIDE.md` (This file's companion)

**Example Process Knowledge**:
- `.claude/graphs/deployment_graph.json` - Version bump checklist node (already exists)

**Existing Hooks**:
- `hooks/on_stop.py` (lines 530-699) - [GRAPH_UPDATE] parsing to extend
- `hooks/session_start.py` (lines 304-401) - Graph summaries to extend

**PreToolUse Test Logs**:
- `.claude/hooks/pre_tool_use_test.log` - Confirms hook functional

---

## For Senior Developer

### Start Here

1. **Read** (30 min):
   - This document (implementation bridge)
   - ADR-001, ADR-002, ADR-003 in full design doc

2. **Setup** (30 min):
   ```bash
   git checkout -b feature/experience-learning-system
   mkdir -p tests/km/
   mkdir -p src/triads/km/
   ```

3. **Day 1 - Build Query Engine**:
   - Create `experience_query.py`
   - Implement relevance scoring (formula above)
   - Write tests (CRITICAL recall test essential)
   - Benchmark (< 100ms target)

4. **Day 2 - Build PreToolUse Hook**:
   - Create `pre_experience_injection.py`
   - ALWAYS exit 0 (never block tools)
   - Early exit on Read/Glob/Grep
   - Test end-to-end

5. **Day 3-5 - Complete System**:
   - Follow roadmap day by day
   - Test continuously
   - Document as you go

### Questions? Blockers?

- **Design questions**: Refer to ADRs in full design doc
- **Clarifications**: Ask Design Bridge agent or user
- **Performance issues**: Profile, optimize hot paths
- **Test failures**: Check test fixtures, verify expectations

---

## Critical Reminders

1. **Performance**: < 100ms (P95) is non-negotiable
2. **Error handling**: ALWAYS exit 0, never block tools
3. **CRITICAL recall**: 100% is non-negotiable
4. **Testing**: End-to-end test MUST pass (marketplace.json scenario)
5. **Documentation**: Write as you go, not at the end

---

## Ready to Start?

✅ Design approved by user
✅ All ADRs validated
✅ Implementation roadmap validated
✅ Risks identified and mitigated
✅ Success criteria clear

**Target completion**: 5 days

**For questions**: Refer to full design doc or ask

**Good luck!** 🚀

---

**Handoff complete from Design Bridge to Senior Developer.**
