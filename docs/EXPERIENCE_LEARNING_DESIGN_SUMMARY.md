# Experience-Based Learning System - Design Summary

**Status**: Design Complete, Ready for Implementation
**Date**: 2025-10-17
**Design Bridge Agent**: Validation Complete

---

## Executive Summary

**Problem Solved**: Knowledge graphs capture history (what was done) but not procedures (how to do things). The marketplace.json mistake in v0.7.0-alpha.1 demonstrates this gap - we had accumulated knowledge but didn't proactively consult it.

**Solution**: Three-component experience-based learning system that learns from mistakes, stores procedural knowledge, and injects it BEFORE actions.

**Timeline**: 5 days (validated with dependency analysis)

**Risk Level**: Medium-Low (comprehensive mitigations in place)

**Innovation**: Leverages newly-verified PreToolUse hooks for proactive knowledge injection.

---

## Architecture at a Glance

### Three Components

1. **Process Knowledge Schema** (ADR-002)
   - Store in existing Concept nodes (backward compatible)
   - Four types: checklist, pattern, warning, requirement
   - Structured trigger conditions enable fast matching
   - Four priority levels: CRITICAL, HIGH, MEDIUM, LOW

2. **Knowledge Query Engine** (ADR-003)
   - Fast relevance-scored lookup (< 100ms target)
   - Matches tool + file + keywords
   - Priority multiplier (2.0x for CRITICAL)
   - Top-3 results to prevent clutter

3. **Three-Hook System** (ADR-001)
   - **PreToolUse**: Query and inject BEFORE tool execution (primary)
   - **Stop**: Extract lessons from [PROCESS_KNOWLEDGE] blocks (learning)
   - **SessionStart**: Display CRITICAL items at session start (awareness)

### Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│  1. LEARNING (Stop Hook)                                    │
│  User corrects mistake → [PROCESS_KNOWLEDGE] block created  │
│  → Stop hook extracts → Add to graph as draft node          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  2. STORAGE (Knowledge Graphs)                              │
│  Process knowledge stored in deployment_graph.json          │
│  Schema: trigger_conditions + process_type + priority       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  3. DISPLAY (SessionStart Hook)                             │
│  CRITICAL items shown at session start for awareness        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  4. INJECTION (PreToolUse Hook)                             │
│  Before Write to plugin.json → Query graphs                 │
│  → Match trigger_conditions → Calculate relevance           │
│  → Apply priority multiplier → Return top-3                 │
│  → Inject formatted checklist into context                  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  5. PREVENTION                                              │
│  Agent sees checklist BEFORE action → Follows all steps     │
│  → Marketplace.json updated → Mistake prevented             │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Decisions and Rationale

### ADR-001: PreToolUse Hook Selection

**Decision**: Use PreToolUse as PRIMARY injection hook (with SessionStart + Stop support)

**Why**:
- ✅ Perfect timing: Inject EXACTLY before action (e.g., before Write to version file)
- ✅ High precision: Can filter by tool_name + file_path + parameters
- ✅ Maximum coverage: Catches all file operations, git commands, deployments
- ✅ Proven functional: Test logs confirm PreToolUse works reliably
- ✅ Graceful degradation: SessionStart shows CRITICAL items even if PreToolUse fails

**Trade-offs**:
- ⚠️ Performance-sensitive: Fires frequently, must be < 100ms
- ⚠️ Complexity: Three hooks to maintain

**Alternatives Rejected**:
- SessionStart only: Wrong timing (too early)
- UserPromptSubmit: No tool context (can't see file paths)
- LLM-based relevance: Too slow (500-2000ms)

### ADR-002: Process Knowledge Schema

**Decision**: Use Concept nodes with structured trigger_conditions and typed process knowledge

**Why**:
- ✅ Backward compatible: Uses existing Concept node type
- ✅ Queryable: Structured trigger_conditions enable fast matching (< 100ms)
- ✅ Expressive: Four process types (checklist, pattern, warning, requirement)
- ✅ Human-readable: JSON structure is clear and editable

**Schema**:
```json
{
  "type": "Concept",
  "process_type": "checklist|pattern|warning|requirement",
  "priority": "CRITICAL|HIGH|MEDIUM|LOW",
  "trigger_conditions": {
    "tool_names": ["Write", "Edit"],
    "file_patterns": ["**/plugin.json", "**/*version*"],
    "action_keywords": ["version bump", "release"],
    "context_keywords": ["deployment"],
    "triad_names": ["deployment"]
  },
  "checklist": {...},  // Type-specific content
  "pattern": {...},
  "warning": {...},
  "requirement": {...}
}
```

**Alternatives Rejected**:
- New "Process" node type: Breaking change, not needed
- Separate files: Fragments knowledge, no relationships
- Flat string fields: Not queryable, too slow

### ADR-003: Relevance Algorithm

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

# Priority multipliers
CRITICAL: 2.0x
HIGH: 1.5x
MEDIUM: 1.0x
LOW: 0.5x

# Threshold: 0.7 minimum
```

**Why**:
- ✅ Fast: Simple string/pattern matching (< 100ms achievable)
- ✅ Precise: Tool + file matching provides high signal
- ✅ Priority-aware: CRITICAL items need only 0.4 base relevance (2.0 * 0.4 = 0.8 > 0.7)
- ✅ Deterministic: Same input always produces same ranking

**Performance Targets**:
- P50: < 30ms
- P95: < 100ms
- P99: < 150ms

**Alternatives Rejected**:
- LLM-based: Too slow (500-2000ms per query)
- Embeddings: Heavy dependency (500MB+), 50-200ms per query
- Simple keywords: Not precise enough (high false positives)

### ADR-004: Lesson Extraction

**Decision**: Pattern-based extraction in Stop hook with auto-add as draft

**Detection Patterns**:
1. **Explicit [PROCESS_KNOWLEDGE] blocks** (highest trust)
2. User correction patterns: "you forgot", "you missed"
3. Explicit lesson statements: "lesson learned:", "important:"
4. Repeated mistakes: Same correction 2+ times

**Inference Algorithms**:
- **Priority**: User correction + high impact → CRITICAL
- **Trigger conditions**: Extract file paths, tools, keywords from context
- **Process type**: Multiple steps → checklist, "when X do Y" → pattern, risk → warning

**Status**: Auto-add with `status: "draft"` for user review

**Why**:
- ✅ Automatic: Lessons captured without manual work
- ✅ Safe: Draft status allows review before trust
- ✅ Fast: Pattern matching < 50ms
- ✅ Incremental: System gets smarter over time

**Alternatives Rejected**:
- Manual only: High friction, lessons forgotten (defeats purpose)
- LLM-based: Too slow for Stop hook (2-10 seconds)
- Conversation replay: Very slow and expensive (30+ seconds)

### ADR-005: Priority System

**Decision**: Four priority levels with clear semantics and behavior rules

**Levels**:

| Priority | Definition | Multiplier | Display | Recall Target |
|----------|-----------|-----------|---------|---------------|
| CRITICAL | Production-breaking, data loss, security | 2.0x | SessionStart + PreToolUse | 100% |
| HIGH | Quality impact, prevents bugs | 1.5x | PreToolUse | 90% |
| MEDIUM | Nice-to-have, improves workflow | 1.0x | PreToolUse (if relevant) | 50% |
| LOW | Informational, rarely needed | 0.5x | Rarely | 10% |

**Assignment Rules**:
- Repeated mistake (2+) → CRITICAL
- User correction + production impact → CRITICAL
- User correction + quality impact → HIGH
- Explicit lesson + production → HIGH
- Proactive suggestion → MEDIUM

**Why**:
- ✅ Clear semantics: Each level implies specific behavior
- ✅ Safety: CRITICAL 2.0x multiplier ensures never missed
- ✅ Balance: High-priority surfaces, low-priority filtered
- ✅ Actionable: Priority affects ranking AND display

**Alternatives Rejected**:
- Three levels: Not enough granularity
- Numeric scale (1-10): Ambiguous semantics
- No priority: Can't guarantee CRITICAL recall

---

## Risk Analysis Summary

| Risk | Likelihood | Impact | Severity | Mitigation |
|------|-----------|--------|----------|------------|
| PreToolUse performance > 100ms | Medium | High | HIGH | Caching, early exit, benchmarking, disable flag |
| False positives | Medium | Medium | MEDIUM | Conservative threshold (0.7), top-3 limit, feedback |
| False negatives (CRITICAL) | Low | Critical | HIGH | 2.0x multiplier, SessionStart redundancy, 100% recall tests |
| Hook crash | Low | Critical | HIGH | try/except, exit 0 always, timeout protection |
| Incorrect lesson inference | Medium | Low | LOW | Draft status, user review, manual edit |
| Graph pollution | Medium | Low | LOW | Periodic cleanup, draft expiry, user delete |

**Overall Risk Level**: **MEDIUM-LOW** (comprehensive mitigations in place)

**Recommendation**: PROCEED WITH IMPLEMENTATION

---

## Implementation Roadmap (5 Days)

### Day 1: Query Engine + Relevance Scoring
- Build `ExperienceQueryEngine` with relevance algorithm
- Implement component scores (tool, file, keywords)
- Add formatting logic
- Benchmark and optimize (< 100ms target)

### Day 2: PreToolUse Hook Implementation
- Create `pre_experience_injection.py` hook
- Integrate query engine
- Add recent messages extraction
- End-to-end testing

### Day 3: Stop Hook Lesson Extraction
- Add [PROCESS_KNOWLEDGE] block parsing
- Create process knowledge nodes
- Integrate into Stop hook
- (Optional) Pattern-based detection

### Day 4: SessionStart Enhancement
- Display CRITICAL process knowledge at session start
- Add draft lessons summary
- Testing and validation

### Day 5: End-to-End Testing and Documentation
- Integration testing (full learning loop)
- Documentation (user guide, examples, API docs)
- CLI commands (/knowledge-review-drafts, /knowledge-promote)
- Final validation and cleanup

**Dependencies**:
```
Day 0 (Prep) → Day 1 (Query Engine) → Day 2 (PreToolUse) →
Day 3 (Stop Hook) → Day 4 (SessionStart) → Day 5 (Testing & Docs)
```

**Critical Path**: Linear (each day depends on previous)

**Parallelization**: Limited (Day 5 docs/CLI can overlap)

---

## Success Criteria

### Functional Requirements

| Requirement | Target | Verification Method |
|------------|--------|---------------------|
| CRITICAL process knowledge injected before relevant tools | 100% recall | Test with version bump scenario |
| Lessons automatically extracted from [PROCESS_KNOWLEDGE] blocks | Parse success rate | Stop hook unit tests |
| Process knowledge displayed at SessionStart | All CRITICAL shown | SessionStart integration test |
| Draft lessons reviewable and editable | CLI commands work | Manual testing |
| User can disable system | Environment variable | Set DISABLE_EXPERIENCE_INJECTION=1 |

### Non-Functional Requirements

| Requirement | Target | Verification Method |
|------------|--------|---------------------|
| PreToolUse hook latency | < 100ms (P95) | Performance benchmarks |
| CRITICAL recall rate | 100% | Integration tests with CRITICAL nodes |
| False positive rate | < 10% | User feedback tracking |
| Graceful degradation | Never block tools | Error injection tests |
| Backward compatible | Existing graphs work | Load old graphs |

### User Experience

| Requirement | Target | Verification Method |
|------------|--------|---------------------|
| Clear, readable formatting | High readability | User feedback |
| Non-intrusive | Only when relevant | Injection event logs |
| Helpful | Prevents repeated mistakes | Measure mistake recurrence rate |
| Controllable | User can disable/edit | Test disable flag + manual edits |

---

## Validation of Initial Implementation Plan

**User's Proposed Plan**:
- Day 1: Query engine + relevance scoring
- Day 2: PreToolUse hook implementation
- Day 3: Stop hook lesson extraction
- Day 4: SessionStart enhancement
- Day 5: End-to-end testing

**Design Bridge Evaluation**: **✅ VALIDATED**

**Rationale**:
- ✅ Correct sequencing: Query engine must come first (Day 2-4 depend on it)
- ✅ Reasonable time estimates: Tasks sized appropriately for complexity
- ✅ Clear dependencies: Each day builds on previous
- ✅ Testing included: Day 5 validates entire system

**Enhancements Made**:
- ✅ Added Day 0 preparation (branch setup, test infrastructure)
- ✅ Broke down each day into specific tasks with hours
- ✅ Added dependency graph showing critical path
- ✅ Identified parallelization opportunities (Day 5 docs/CLI)
- ✅ Added fallback plans for each risk

**Missing Dependencies Identified**: None critical. Plan is sound.

---

## Component Specifications (Ready for Implementation)

### 1. ExperienceQueryEngine

**File**: `src/triads/km/experience_query.py`

**API**:
```python
class ExperienceQueryEngine:
    def query_relevant_knowledge(
        tool_name: str,
        tool_input: dict,
        recent_messages: list[str] | None = None,
        min_relevance: float = 0.7,
        max_results: int = 3
    ) -> list[ProcessKnowledge]
```

**Performance**: < 100ms (P95)

### 2. PreToolUse Hook

**File**: `hooks/pre_experience_injection.py`

**Behavior**:
- Read stdin for tool context
- Early exit on irrelevant tools (Read, Glob, Grep)
- Query ExperienceQueryEngine
- Output formatted knowledge to stdout
- Log performance to stderr
- ALWAYS exit 0 (never block)

### 3. Stop Hook Enhancement

**File**: `hooks/on_stop.py` (extend existing)

**New Function**: `extract_process_knowledge_blocks(text: str) -> list[dict]`

**Behavior**:
- Parse [PROCESS_KNOWLEDGE]...[/PROCESS_KNOWLEDGE] blocks
- Create process knowledge nodes with draft status
- Add to appropriate graph (deployment, implementation, etc.)
- Log to stderr

### 4. SessionStart Hook Enhancement

**File**: `hooks/session_start.py` (extend existing)

**New Section**: Display CRITICAL process knowledge

**Behavior**:
- Load CRITICAL nodes from all graphs
- Format and display (top 5 only)
- Show draft lessons count

### 5. CLI Commands

**Commands**:
- `/knowledge-review-drafts`: List all draft process knowledge
- `/knowledge-promote <node_id>`: Change status draft → active
- `/knowledge-archive <node_id>`: Change status to archived

**Implementation**: Extend `src/triads/km/graph_access.py`

---

## What's Next?

**For User**: Review and approve this design

**For Implementation Triad**:
1. Read full design document: `docs/EXPERIENCE_LEARNING_SYSTEM_DESIGN.md`
2. Start with Day 1: Build ExperienceQueryEngine
3. Follow 5-day roadmap exactly (dependencies are critical)
4. Consult ADRs for detailed design decisions
5. Run benchmarks continuously (performance target < 100ms)

**For Deployment Triad** (after implementation):
1. Test with real version bump scenario
2. Verify marketplace.json mistake prevented
3. Document in changelog as v0.8.0 feature
4. Update marketplace.json to list new capabilities

---

## Key Files

| Document | Purpose |
|----------|---------|
| `docs/EXPERIENCE_LEARNING_SYSTEM_DESIGN.md` | Complete design with all 5 ADRs + implementation roadmap (15,000+ words) |
| `docs/EXPERIENCE_LEARNING_DESIGN_SUMMARY.md` | This file - executive summary |
| `.claude/graphs/deployment_graph.json` | Example process knowledge node (version bump checklist) |
| `hooks/pre_experience_injection.py` | To be created - PreToolUse hook |
| `src/triads/km/experience_query.py` | To be created - Query engine |

---

## Questions for User (Before Implementation)

1. **Scope Confirmation**: Is 5-day timeline acceptable? Can defer pattern-based detection (Day 3 Task 3.4) to v0.9.0 if needed?

2. **Priority on MVP**: Focus on explicit [PROCESS_KNOWLEDGE] blocks first (highest trust), add pattern detection later?

3. **Performance vs Features**: If PreToolUse < 100ms is hard, prefer:
   - A) Reduce features (top-1 instead of top-3, skip keywords)
   - B) Accept 150ms latency

4. **Draft Review Workflow**: Auto-add with draft status acceptable? Or prefer manual confirmation?

**Recommend**: Keep as-is. Design is solid, roadmap is achievable, mitigations are comprehensive.

---

## Design Bridge Sign-Off

**Status**: ✅ **DESIGN APPROVED FOR IMPLEMENTATION**

**Confidence**: 95% (5% risk from performance unknowns, mitigated with fallbacks)

**Readiness**:
- ✅ All ADRs complete with alternatives evaluation
- ✅ Risk analysis comprehensive with mitigations
- ✅ Implementation roadmap validated with dependencies
- ✅ Component specifications ready for coding
- ✅ Success metrics defined and measurable
- ✅ Testing strategy clear

**Recommendation**: **PROCEED TO IMPLEMENTATION TRIAD**

---

**Ready for user approval.**
