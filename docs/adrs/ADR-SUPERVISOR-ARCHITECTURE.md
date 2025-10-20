# ADR-007: Supervisor-First Multi-Workflow Architecture

**Status**: Approved
**Date**: 2025-10-20
**Decision Makers**: User, Claude (Design Phase)
**Related ADRs**: ADR-006 (Triad Atomicity Principle)

---

## Context

The current triad system uses a single predefined workflow (feature development: idea-validation → design → implementation → garden-tending → deployment). This workflow doesn't fit all problem types:

- **Bug fixing**: Doesn't need idea validation or full design phase
- **Performance optimization**: Needs profiling and measurement triads
- **Refactoring**: Focuses on code quality without new features
- **Investigation**: Research-focused, may not lead to implementation

Additionally, the current interaction model uses "main Claude" for conversational sessions, which:
- Mixes Q&A with work execution
- Creates ambiguity about when to use triads vs. conversation
- Lacks systematic problem classification
- Doesn't learn from past routing decisions

The user's vision: **"I'm working towards an experience where we're predominantly using sub-agents to do work, as opposed to these conversational sessions."**

---

## Decision

We will implement a **Supervisor-first architecture** where:

1. **All user interactions route through a Supervisor Agent**
   - Implemented via `on_user_input` hook (fires on every user message)
   - Supervisor is ALWAYS active from day 1
   - Emergency bypass available via `/direct` command

2. **Supervisor handles dual responsibilities**
   - **Q&A**: Answer informational questions directly (no workflow routing)
   - **Work routing**: Classify problems, suggest workflows, execute triads

3. **Multiple workflow library**
   - Proven workflows for common problem types (bug-fix, performance, feature-dev, refactoring, investigation)
   - Ability to generate new triads for novel problems
   - Variable workflow size: 2-5 triads (6-15 agents)

4. **Workflows compose atomic triads**
   - Triads NEVER decomposed (per ADR-006)
   - Same triads can appear in multiple workflows
   - Sequential execution with context handoffs

5. **Supervisor monitors and learns**
   - Track workflow outcomes
   - Improve routing accuracy over time
   - Record user feedback

---

## Alternatives Considered

### Alternative 1: Gradual Migration
**Approach**: Start with manual workflow invocation, gradually introduce Supervisor

**Rejected because**:
- Creates "two modes" confusion (when to use Supervisor vs. direct?)
- Users never fully adopt new pattern
- Requires maintaining both interaction models
- Delays benefits of systematic problem classification

### Alternative 2: Optional Supervisor Mode
**Approach**: Supervisor is opt-in, users choose when to invoke it

**Rejected because**:
- Same "two modes" problem
- Inconsistent user experience
- Supervisor can't learn effectively (incomplete data)
- Misses opportunity for systematic improvement

### Alternative 3: Decomposable Triads
**Approach**: Pull individual agents from triads, compose flexibly

**Rejected because**:
- Violates user requirement: "triads themselves are atomic, they should not be decomposed"
- Loses internal triad coherence
- Contradicts military organizational patterns (fire team atomicity)
- Increases coordination overhead
- Makes context handoffs unclear

### Alternative 4: Single Large Workflow
**Approach**: One universal workflow that handles all problem types

**Rejected because**:
- Inefficient (bug fix doesn't need idea validation)
- Fixed workflow can't adapt to problem diversity
- Doesn't match military task organization doctrine
- Creates unnecessary overhead for simple problems

---

## Rationale

### 1. Military Organizational Patterns

Research into military organizations (documented in `MILITARY_ORGANIZATIONAL_PATTERNS.md`) reveals battle-tested principles:

**Squad Organization (9 soldiers)**:
- 2 fire teams (4 each) + 1 squad leader
- Fire teams are atomic (never decomposed)
- Squad leader coordinates but doesn't execute
- **Maps to**: 3 triads + Supervisor

**Task Organization Doctrine**:
- Intact units composed for mission-specific needs
- Same units used in different task organizations
- Units never decomposed into individuals
- **Maps to**: Workflows compose intact triads

**Optimal Team Size (9-12)**:
- Below 9: insufficient diversity
- Above 12: coordination overhead
- 9-12: proven sweet spot
- **Maps to**: 2-5 triads per workflow

### 2. Separation of Concerns

**Supervisor responsibilities**:
- Problem classification
- Workflow routing
- Execution monitoring
- Learning and improvement
- Q&A handling

**Triad responsibilities**:
- Execute specific work
- Internal coordination
- Produce outputs
- Hand off to next triad

**Benefits**:
- Clear authority boundaries
- Supervisor can optimize routing without changing triads
- Triads can improve without changing routing logic
- Easier testing and validation

### 3. Proven Patterns + Flexibility

**Workflow library approach**:
- Common problems use proven workflows (fast, reliable)
- Novel problems can generate new triads (flexible)
- Workflows evolve based on usage patterns
- Matches military "tried and tested" + adaptation

**Evidence**:
- Military uses doctrine (proven patterns) + field adaptation
- Software uses design patterns + custom solutions
- User explicitly requested: "there needs to be...established examples, much like in the military, things that are tried and tested"

### 4. Learning System

**Supervisor learns over time**:
- Records problem classification → workflow selection
- Tracks workflow outcomes (success/failure)
- Captures user feedback
- Improves routing accuracy

**Benefits**:
- System gets smarter with use
- Reduces misrouting
- Identifies gaps in workflow library
- Enables continuous improvement

### 5. Agent-First Paradigm

**Current state**: Conversational Claude with occasional triad invocation
**Target state**: Supervisor routes to triads, conversation is rare

**User's explicit goal**: "predominantly using sub-agents to do work"

**Immediate activation ensures**:
- Day 1 adoption
- No ambiguity about interaction model
- Users build habits around new pattern
- System gathers learning data immediately

---

## Consequences

### Positive

1. **Problem-Appropriate Workflows**
   - Bug fixes use 3-triad workflow (fast)
   - Features use 4-triad workflow (comprehensive)
   - Investigation uses 2-triad workflow (focused)

2. **Systematic Problem Classification**
   - Consistent routing logic
   - Pattern matching on problem indicators
   - LLM fallback for ambiguous cases
   - Manual selection for uncertain routing

3. **Clear Interaction Model**
   - All user input → Supervisor
   - Supervisor → triages Q&A vs. work
   - Work → routes to appropriate workflow
   - Emergency bypass available (`/direct`)

4. **Continuous Improvement**
   - System learns from outcomes
   - Routing accuracy improves
   - Workflow library evolves
   - User feedback drives optimization

5. **Scalability**
   - Add new workflows without changing core system
   - Triads reusable across workflows
   - Supervisor logic separate from execution
   - Clear extension points

### Negative

1. **Complexity Increase**
   - New hook to maintain (`on_user_input`)
   - Workflow library to curate
   - Supervisor logic to develop
   - More moving parts

   **Mitigation**: Comprehensive testing, clear documentation, phased implementation

2. **Supervisor Dependency**
   - All interactions funnel through Supervisor
   - Supervisor failure blocks all work
   - Single point of failure

   **Mitigation**:
   - Emergency bypass (`/direct`)
   - Fallback to passthrough on error
   - Robust error handling
   - Extensive testing

3. **Initial Learning Period**
   - Supervisor starts with zero training data
   - Early routing may be imperfect
   - Users need to learn new interaction model

   **Mitigation**:
   - Training mode with confirmations
   - Graduation after 10+ successful interactions
   - Clear feedback when routing uncertain
   - Documentation and examples

4. **Workflow Maintenance**
   - Library needs curation
   - Proven patterns must be validated
   - New problem types require new workflows

   **Mitigation**:
   - Start with 5 proven workflows
   - Add based on demand
   - User feedback drives additions
   - Document workflow design principles

### Neutral

1. **User Interaction Changes**
   - Users don't directly invoke triads anymore
   - Supervisor suggests, user confirms
   - More structured interaction

2. **Triad Design Implications**
   - Triads must be reusable across workflows
   - Can't be overly specialized
   - Must have clear inputs/outputs

---

## Implementation Plan

See full plan in session context. High-level phases:

### Phase 0: Research Documentation (Current)
- ✅ Document military organizational patterns
- ✅ Create knowledge graph nodes
- ✅ Create ADR (this document)

### Phase 1: Supervisor Agent Core (Week 1-2)
- Create `on_user_input` hook
- Create Supervisor agent definition
- Implement invocation logic

### Phase 2: Workflow Library (Week 3)
- Define workflow schema
- Create 5 proven workflows
- Implement workflow loader

### Phase 3: Problem Classification (Week 4)
- Implement classifier
- Create workflow suggester
- Add LLM fallback

### Phase 4: Execution Monitoring (Week 5)
- Create workflow executor
- Implement progress tracking
- Add context handoff logic

### Phase 5: Learning System (Week 6)
- Implement outcome recording
- Create feedback collection
- Build routing improvement logic

### Phase 6: Triad Library Expansion (Week 7-8)
- Create specialized triads
- Standardize context handoffs
- Document triad design patterns

### Phase 7: Testing & Documentation (Week 9)
- Comprehensive testing
- User documentation
- Migration guide

**Total**: ~9 weeks, ~152 hours

---

## Validation Criteria

This decision will be considered successful when:

1. **Adoption**
   - ✅ >80% of work requests route through Supervisor
   - ✅ Users understand when to use `/direct` bypass
   - ✅ Fewer "how do I..." questions about interaction model

2. **Accuracy**
   - ✅ >90% of workflow routing accepted by users (after training period)
   - ✅ <10% misrouting requiring manual correction
   - ✅ Routing confidence scores > 0.8 for common problems

3. **Efficiency**
   - ✅ Bug fixes complete faster (3 triads vs. 5 triads)
   - ✅ Investigations don't trigger unnecessary implementation
   - ✅ Users report less friction in problem → solution flow

4. **Learning**
   - ✅ Routing accuracy improves over 30-day period
   - ✅ System identifies gaps in workflow library
   - ✅ User feedback incorporated into routing logic

5. **Reliability**
   - ✅ Supervisor uptime >99%
   - ✅ Fallback mechanisms work on Supervisor failure
   - ✅ `/direct` bypass functions as emergency escape

---

## Risks and Mitigations

### Risk 1: Supervisor Becomes Bottleneck
**Probability**: Medium
**Impact**: High

**Indicators**:
- Supervisor routing takes >5 seconds
- Users frequently use `/direct` bypass
- Complaints about interaction speed

**Mitigations**:
- Optimize classifier (cache embeddings)
- Async LLM calls with timeout
- Profile and optimize hot paths
- Consider local LLM for classification

### Risk 2: Workflow Library Becomes Stale
**Probability**: Medium
**Impact**: Medium

**Indicators**:
- Users frequently request custom triads
- Proven workflows no longer match common problems
- Low workflow reuse rate

**Mitigations**:
- Regular library review (quarterly)
- Track workflow usage metrics
- User feedback drives updates
- Document workflow design patterns

### Risk 3: Triads Too Specialized for Reuse
**Probability**: Low
**Impact**: Medium

**Indicators**:
- Triads used in only 1 workflow
- Frequent need for new triads
- Similar triads with slight variations

**Mitigations**:
- Design review for new triads
- Refactor to increase generality
- Document reuse patterns
- Consolidation during Garden Tending

### Risk 4: Users Bypass Supervisor Frequently
**Probability**: Low
**Impact**: High

**Indicators**:
- >30% interactions use `/direct`
- Users report Supervisor as "annoying"
- Supervisor suggestions rejected frequently

**Mitigations**:
- Improve routing accuracy
- Reduce confirmation friction (training graduation)
- Better Q&A vs. work detection
- User research to understand pain points

---

## Related Documents

- **MILITARY_ORGANIZATIONAL_PATTERNS.md**: Research findings that informed this decision
- **ADR-006: Triad Atomicity Principle**: Foundation for workflow composition approach
- **SUPERVISOR.md** (to be created): Supervisor agent definition and behavior
- **WORKFLOWS.md** (to be created): Workflow library documentation
- **INTERACTION_MODEL.md** (to be created): User interaction guide

---

## Open Questions

### Resolved
- ✅ Should Supervisor be optional? **NO - immediate activation**
- ✅ How many workflows in initial library? **5 proven patterns**
- ✅ Can triads be decomposed? **NO - atomic principle**
- ✅ Sequential or parallel triad execution? **Sequential only**
- ✅ Who classifies problems? **Supervisor suggests, user confirms**

### Unresolved
- ⏳ What's the graduation criteria for training mode? **Proposed: 10 successful interactions**
- ⏳ How to handle workflow generation for novel problems? **Phase 6 implementation**
- ⏳ Should Supervisor use local or cloud LLM? **TBD based on performance testing**
- ⏳ Context handoff format standardization? **To be defined in Phase 6**

---

## Approval

**User Approval**: 2025-10-20 (selected Option A: Immediate implementation)
**Design Phase**: Completed
**Implementation Phase**: In Progress (Phase 0 Documentation)

---

## Document History

- **2025-10-20**: Initial ADR created (Phase 0 of Supervisor implementation)
- User approved implementation plan via ExitPlanMode
- Knowledge graph nodes created (design_graph.json)
- Military research documented (MILITARY_ORGANIZATIONAL_PATTERNS.md)

---

**Next Steps**: Begin Phase 1 implementation - create `on_user_input` hook and Supervisor agent definition.
