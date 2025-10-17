# Experience-Based Learning System - Implementation Guide

**For**: Implementation Triad (Senior Developer, Test Engineer)
**Design Complete**: 2025-10-17
**Start Implementation**: After user approval

---

## Quick Start

### Prerequisites

1. **Read**:
   - `docs/EXPERIENCE_LEARNING_DESIGN_SUMMARY.md` (5 min)
   - `docs/EXPERIENCE_LEARNING_SYSTEM_DESIGN.md` - ADR-001 through ADR-005 (20 min)

2. **Verify**:
   - PreToolUse hook is functional: `cat .claude/hooks/pre_tool_use_test.log`
   - Existing hooks work: `hooks/on_stop.py`, `hooks/session_start.py`
   - Knowledge graph system operational: `ls .claude/graphs/*.json`

3. **Setup**:
   ```bash
   git checkout -b feature/experience-learning-system
   mkdir -p tests/km/
   ```

### Day-by-Day Checklist

Copy this checklist and track progress:

#### Day 1: Query Engine + Relevance Scoring

- [ ] Create `src/triads/km/experience_query.py`
- [ ] Implement `ExperienceQueryEngine` class
- [ ] Implement `calculate_tool_match_score()`
- [ ] Implement `calculate_file_match_score()`
- [ ] Implement `calculate_keyword_match_score()`
- [ ] Implement `calculate_context_match_score()`
- [ ] Implement `format_for_injection()`
- [ ] Write unit tests for all functions
- [ ] Run benchmarks (target: P95 < 100ms)
- [ ] Verify: `pytest tests/km/test_experience_query.py -v`

#### Day 2: PreToolUse Hook Implementation

- [ ] Create `hooks/pre_experience_injection.py`
- [ ] Implement `main()` with error handling
- [ ] Add early exit for irrelevant tools
- [ ] Integrate `ExperienceQueryEngine`
- [ ] Implement `extract_recent_messages()`
- [ ] Update `hooks/hooks.json` to register hook
- [ ] Test with real PreToolUse input
- [ ] Verify injection into context
- [ ] Performance check: < 100ms
- [ ] Verify: Run Claude Code session, check `.claude/hooks/` logs

#### Day 3: Stop Hook Lesson Extraction

- [ ] Extend `hooks/on_stop.py`
- [ ] Implement `extract_process_knowledge_blocks()`
- [ ] Implement `parse_nested_structure()`
- [ ] Implement `create_process_knowledge_node()`
- [ ] Integrate into existing Stop hook flow
- [ ] Test with conversation containing [PROCESS_KNOWLEDGE] blocks
- [ ] Verify nodes added to graphs
- [ ] Check draft status set correctly
- [ ] Verify: Add test block to conversation, check deployment_graph.json

#### Day 4: SessionStart Enhancement

- [ ] Extend `hooks/session_start.py`
- [ ] Add CRITICAL process knowledge section
- [ ] Add draft lessons summary
- [ ] Format for readability
- [ ] Test with CRITICAL nodes in graph
- [ ] Test with no CRITICAL nodes
- [ ] Verify display at session start
- [ ] Verify: Start new session, check output

#### Day 5: End-to-End Testing and Documentation

- [ ] Run full learning loop test
- [ ] Run version bump scenario test
- [ ] Run performance benchmarks
- [ ] Run error handling tests
- [ ] Create `docs/EXPERIENCE_LEARNING_SYSTEM.md`
- [ ] Update `README.md`
- [ ] Update `CHANGELOG.md`
- [ ] Create example [PROCESS_KNOWLEDGE] blocks
- [ ] Implement `/knowledge-review-drafts` CLI command
- [ ] Implement `/knowledge-promote` CLI command
- [ ] Implement `/knowledge-archive` CLI command
- [ ] Final validation checklist
- [ ] Clean up debug code
- [ ] Update version to 0.8.0

---

## Critical Design Decisions

### 1. PreToolUse Hook MUST Be Fast (< 100ms)

**Why**: Fires before every tool use. Slow hook = bad UX.

**How to achieve**:
- Cache graphs in memory (load once per session)
- Early exit on irrelevant tools: `if tool_name not in ["Write", "Edit", "Bash", "NotebookEdit"]: return []`
- Fast path if no process knowledge exists
- Use simple string matching (no regex in hot path)
- Log slow queries to stderr for monitoring

**Test continuously**: Add timing wrapper, log any query > 100ms.

### 2. Hook MUST NEVER Block Tool Execution

**Why**: Crash in hook would break all work.

**How to achieve**:
```python
def main():
    try:
        # All hook logic
        ...
    except Exception as e:
        # Log but NEVER re-raise
        print(f"⚠️ Experience injection error: {e}", file=sys.stderr)
    finally:
        # ALWAYS exit 0
        sys.exit(0)
```

**Test**: Inject exceptions, verify tool still executes.

### 3. CRITICAL Items Must Have 100% Recall

**Why**: Missing CRITICAL checklist defeats purpose.

**How to achieve**:
- Priority multiplier: `CRITICAL: 2.0x`
- CRITICAL needs only 0.4 base relevance to pass 0.7 threshold
- SessionStart shows CRITICAL items as redundant layer
- Write tests: "CRITICAL node + matching tool → MUST inject"

**Test**: Version bump scenario with CRITICAL checklist.

### 4. Auto-Add Lessons as Draft (Not Manual Confirmation)

**Why**: Can't block Stop hook for user input.

**How to achieve**:
- Set `status: "draft"` on all auto-extracted nodes
- User reviews later with `/knowledge-review-drafts`
- User can edit/delete directly in graph JSON

**Behavior**: All lessons immediately usable, user can refine later.

---

## Code Structure

### New Files to Create

```
src/triads/km/
├── experience_query.py    # ExperienceQueryEngine (Day 1)
└── process_knowledge.py   # ProcessKnowledge dataclass (Day 1)

hooks/
└── pre_experience_injection.py  # PreToolUse hook (Day 2)

tests/km/
├── test_experience_query.py     # Query engine tests (Day 1)
├── test_process_knowledge.py    # Schema tests (Day 1)
└── test_integration_experience.py  # End-to-end tests (Day 5)
```

### Files to Extend

```
hooks/
├── on_stop.py           # Add process knowledge extraction (Day 3)
└── session_start.py     # Add CRITICAL display (Day 4)

src/triads/km/
└── graph_access.py      # Add CLI commands (Day 5)
```

---

## Schema Reference (Quick)

### Process Knowledge Node Structure

```json
{
  "id": "process_{purpose}_{timestamp}",
  "type": "Concept",
  "label": "Human-readable title",
  "description": "What this process knowledge is about",
  "confidence": 1.0,
  "evidence": "Where this lesson came from",
  "created_by": "lesson-extractor",
  "created_at": "ISO timestamp",
  "status": "draft",

  "process_type": "checklist|pattern|warning|requirement",
  "priority": "CRITICAL|HIGH|MEDIUM|LOW",

  "trigger_conditions": {
    "tool_names": ["Write", "Edit"],
    "file_patterns": ["**/plugin.json"],
    "action_keywords": ["version bump"],
    "context_keywords": ["deployment"],
    "triad_names": ["deployment"]
  },

  "checklist": {  // If process_type = checklist
    "title": "Checklist Title",
    "items": ["Item 1", "Item 2"],
    "format": "checkbox"
  }
}
```

### Relevance Formula

```python
base_relevance = (
    tool_match * 0.40 +      # Tool name exact match (0 or 1)
    file_match * 0.40 +      # File pattern match (0 or 1)
    keyword_match * 0.10 +   # Action keywords (0-1)
    context_match * 0.10     # Context keywords (0-1)
)

final_score = base_relevance * priority_multiplier

priority_multiplier = {
    "CRITICAL": 2.0,
    "HIGH": 1.5,
    "MEDIUM": 1.0,
    "LOW": 0.5
}

# Inject if final_score >= 0.7
# Return top 3 results
```

---

## Test Strategy

### Unit Tests (Day 1)

**File**: `tests/km/test_experience_query.py`

**Test Cases**:
- `test_tool_match_score()`: Exact match vs no match
- `test_file_match_score()`: fnmatch patterns
- `test_keyword_match_score()`: Case-insensitive substring
- `test_relevance_calculation()`: Full formula with examples
- `test_priority_multiplier()`: 2.0x for CRITICAL
- `test_threshold_filtering()`: 0.7 minimum
- `test_top_n_limiting()`: Max 3 results
- `test_format_for_injection()`: Each process_type and priority

**Run**: `pytest tests/km/test_experience_query.py -v`

### Integration Tests (Day 2)

**File**: `tests/km/test_integration_experience.py`

**Test Cases**:
- `test_pretooluse_hook_fires()`: Hook receives input
- `test_early_exit_on_read()`: Read tool skipped
- `test_injection_on_write()`: Write to relevant file → inject
- `test_performance_benchmark()`: Latency < 100ms
- `test_error_handling()`: Malformed input doesn't crash

**Run**: `pytest tests/km/test_integration_experience.py -v`

### End-to-End Tests (Day 5)

**Scenario**: Full learning loop

```python
def test_full_learning_loop():
    """Test: User correction → Lesson extracted → Knowledge injected → Mistake prevented."""

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
      file_patterns: ["**/plugin.json"]
    checklist:
      items:
        - plugin.json
        - marketplace.json
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
    # (In real usage, agent sees checklist and updates both files)
```

**Run**: `pytest tests/km/test_integration_experience.py::test_full_learning_loop -v`

### Performance Benchmarks (Day 1, Day 5)

**File**: `tests/km/test_performance.py`

```python
def test_query_performance():
    """Benchmark query engine performance."""
    import time

    # Load graphs (100, 300, 500 nodes)
    graphs = create_test_graphs([100, 300, 500])

    for node_count in [100, 300, 500]:
        graph = graphs[node_count]

        # Run 100 queries
        latencies = []
        for _ in range(100):
            start = time.perf_counter()
            results = query_engine.query_relevant_knowledge(
                tool_name="Write",
                tool_input={"file_path": "/path/to/plugin.json"}
            )
            latencies.append((time.perf_counter() - start) * 1000)

        # Calculate percentiles
        p50 = percentile(latencies, 50)
        p95 = percentile(latencies, 95)
        p99 = percentile(latencies, 99)

        print(f"Graph size: {node_count} nodes")
        print(f"  P50: {p50:.1f}ms")
        print(f"  P95: {p95:.1f}ms")
        print(f"  P99: {p99:.1f}ms")

        # Assert targets
        assert p50 < 30, f"P50 latency {p50}ms exceeds 30ms target"
        assert p95 < 100, f"P95 latency {p95}ms exceeds 100ms target"
        assert p99 < 150, f"P99 latency {p99}ms exceeds 150ms target"
```

**Run**: `pytest tests/km/test_performance.py -v`

---

## Common Issues and Solutions

### Issue 1: PreToolUse Hook Not Firing

**Symptoms**: No injection, no logs in `.claude/hooks/pre_tool_use_test.log`

**Debug**:
1. Check `hooks/hooks.json`: Verify PreToolUse hook registered
2. Check hook script permissions: `chmod +x hooks/pre_experience_injection.py`
3. Check Python path: Verify shebang `#!/usr/bin/env python3`
4. Test manually: `echo '{"tool_name":"Write","tool_input":{}}' | python3 hooks/pre_experience_injection.py`

**Solution**: Usually permissions or JSON syntax error.

### Issue 2: Query Too Slow (> 100ms)

**Symptoms**: Latency warnings in stderr

**Debug**:
1. Check graph size: How many nodes? How many process knowledge nodes?
2. Profile hot functions: Add timing wrappers
3. Check caching: Is graph loaded every time?

**Solution**:
- Add aggressive caching: Load graphs once, reuse
- Early exit: Skip irrelevant tools before query
- Optimize patterns: Use fnmatch (fast) not regex

### Issue 3: False Positives (Irrelevant Injection)

**Symptoms**: Knowledge injected when not relevant

**Debug**:
1. Check relevance scores: Log final_score for each match
2. Check trigger_conditions: Are patterns too broad?
3. Check threshold: Is 0.7 too low?

**Solution**:
- Tighten trigger_conditions: More specific file patterns
- Raise threshold: Try 0.75 or 0.8
- Lower priority: Change from CRITICAL to HIGH

### Issue 4: False Negatives (Missing CRITICAL)

**Symptoms**: CRITICAL checklist not injected when expected

**Debug**:
1. Check trigger_conditions: Do tool_names and file_patterns match?
2. Check priority: Is it actually CRITICAL (2.0x multiplier)?
3. Check base relevance: Is it at least 0.4?

**Solution**:
- Broaden trigger_conditions: Add more file patterns
- Verify priority: Ensure CRITICAL set correctly
- Check threshold: 0.7 might be too high if base relevance < 0.4

### Issue 5: Stop Hook Not Extracting Lessons

**Symptoms**: [PROCESS_KNOWLEDGE] block in conversation, but no node added

**Debug**:
1. Check block syntax: Properly formatted?
2. Check Stop hook logs: Any parsing errors?
3. Check graph file: Was it saved correctly?

**Solution**:
- Validate block structure: Use JSON schema validator
- Add debug logging: Print parsed blocks to stderr
- Check file permissions: Can Stop hook write to graph?

---

## Testing Checklist (Day 5)

Before considering implementation complete:

### Functional Tests

- [ ] CRITICAL process knowledge injected before Write to version file
- [ ] [PROCESS_KNOWLEDGE] blocks parsed and nodes created
- [ ] Draft status set on auto-extracted lessons
- [ ] CRITICAL knowledge displayed at SessionStart
- [ ] Draft lessons count shown at SessionStart
- [ ] User can disable with `DISABLE_EXPERIENCE_INJECTION=1`
- [ ] User can review drafts with `/knowledge-review-drafts`
- [ ] User can promote drafts with `/knowledge-promote <node_id>`
- [ ] User can archive nodes with `/knowledge-archive <node_id>`

### Performance Tests

- [ ] P50 latency < 30ms (100 node graph)
- [ ] P95 latency < 100ms (500 node graph)
- [ ] P99 latency < 150ms (500 node graph)
- [ ] Early exit on Read tool < 1ms
- [ ] No process knowledge fast path < 5ms

### Error Handling Tests

- [ ] Malformed PreToolUse input doesn't crash
- [ ] Missing graph file doesn't crash
- [ ] Corrupted graph JSON doesn't crash
- [ ] Exception in query engine doesn't block tool
- [ ] Timeout (> 200ms) logged but doesn't crash

### Integration Tests

- [ ] Full learning loop works (correction → extraction → injection → prevention)
- [ ] Version bump scenario prevents marketplace.json mistake
- [ ] Multiple process knowledge items ranked correctly
- [ ] Priority multiplier works (CRITICAL surfaces with low relevance)
- [ ] Threshold filtering works (LOW priority filtered out)

### Backward Compatibility Tests

- [ ] Existing graphs without process knowledge still work
- [ ] Old Concept nodes unaffected
- [ ] SessionStart still shows graph summaries
- [ ] Stop hook still processes [GRAPH_UPDATE] blocks

---

## Success Metrics (Post-Implementation)

Track these metrics in first 2 weeks:

### Performance Metrics

- **PreToolUse latency distribution** (P50, P95, P99)
  - Target: P95 < 100ms
  - Alert if: P95 > 150ms

- **Injection frequency**
  - How often does PreToolUse inject knowledge?
  - Target: 5-10% of tool executions

- **False positive rate**
  - User feedback: Was injection helpful?
  - Target: < 10% "not helpful"

### Functional Metrics

- **CRITICAL recall rate**
  - Did CRITICAL items get injected when relevant?
  - Target: 100%

- **Lessons learned**
  - How many [PROCESS_KNOWLEDGE] blocks extracted?
  - Target: 1-2 per session (if mistakes occur)

- **Draft review rate**
  - How many draft lessons promoted to active?
  - Target: > 50%

### User Experience Metrics

- **System usage**
  - Is `DISABLE_EXPERIENCE_INJECTION=1` set?
  - Target: < 5% users disable

- **Manual edits**
  - Are users editing process knowledge nodes?
  - Target: Shows engagement

- **Mistake recurrence**
  - Are same mistakes repeated?
  - Target: 0 repeated mistakes for CRITICAL items

---

## Post-Implementation Tasks

### Week 1-2: Monitoring

- [ ] Add logging for all injection events
- [ ] Track latency distribution
- [ ] Collect user feedback (helpful/not-helpful)
- [ ] Monitor false positive rate
- [ ] Check for repeated mistakes

### Week 3-4: Tuning

- [ ] Adjust relevance threshold if needed (0.7 → 0.75?)
- [ ] Tweak priority multipliers if imbalanced
- [ ] Refine trigger conditions based on usage
- [ ] Add common patterns to default knowledge

### Future Enhancements (v0.9.0+)

- [ ] LLM-based lesson extraction (async batch job)
- [ ] Semantic search with embeddings (optional)
- [ ] Web UI for process knowledge management
- [ ] Post-action validation (did user follow checklist?)
- [ ] Cross-session learning (repeated mistakes across users)

---

## Questions? Issues?

### During Implementation

- **Design questions**: Refer to ADRs in `docs/EXPERIENCE_LEARNING_SYSTEM_DESIGN.md`
- **Clarifications**: Ask Design Bridge agent or user
- **Blockers**: Document in implementation log, escalate if needed

### Testing Issues

- **Failing tests**: Check test fixtures, verify test data
- **Performance issues**: Profile slow functions, optimize hot paths
- **Integration issues**: Check hook registration, verify graph structure

### Documentation

- **User-facing**: Write clear examples and use cases
- **Developer-facing**: Document internal APIs and design decisions
- **Troubleshooting**: Add common issues to docs

---

## Ready to Start?

1. **Read design docs** (30 min total)
2. **Set up branch and tests** (30 min)
3. **Start Day 1**: Build query engine
4. **Follow roadmap** day by day
5. **Run tests continuously**
6. **Benchmark performance** daily
7. **Document as you go**

**Target completion**: 5 days

**Good luck!** 🚀

---

**For questions or blockers**: Refer to `docs/EXPERIENCE_LEARNING_SYSTEM_DESIGN.md` (full design with all ADRs)
