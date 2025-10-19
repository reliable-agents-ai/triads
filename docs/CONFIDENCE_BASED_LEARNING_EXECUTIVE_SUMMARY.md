# Confidence-Based Immediate Learning System - Executive Summary

**Design Status**: Awaiting User Approval
**Created**: 2025-10-19
**Architect**: solution-architect

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✋ DESIGN APPROVAL REQUIRED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Executive Summary

**What we're building**: A confidence-based immediate learning system that acts like human learning - forming hypotheses immediately based on evidence quality, then refining through feedback rather than waiting for approval gates.

**Why this approach**: The current draft/promote workflow breaks the natural learning loop. Research in AI systems (RLHF, Constitutional AI, online learning) shows that evidence-based confidence scores enable immediate learning with automatic self-correction, matching how humans actually learn.

**Timeline**: 6 phases over 6-7 days estimated

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Key Architectural Decisions

### ADR-001: Immediate Learning Based on Confidence

**Decision**: Lessons become active immediately if confidence >= 0.70 (or >= 0.80 for MEDIUM/LOW priority)

**Why**:
- User corrections have 95% confidence - should be trusted immediately
- Current system ignores all lessons until manual review (broken loop)
- Research: RLHF and Constitutional AI learn immediately based on evidence quality

**Alternative Rejected**:
- Keep draft/promote workflow → Rejected: Creates friction, ignores evidence strength
- All lessons active → Rejected: Would inject low-confidence noise

**Confidence Thresholds** (research-informed):
- User correction: 0.95 → active immediately
- Repeated mistake (2+ times): 0.85 → active immediately
- Explicit [PROCESS_KNOWLEDGE] block: 0.90 → active immediately
- Agent inference: 0.65 → needs_validation (optional review)
- Weak suggestion: 0.50 → archived (too weak)

---

### ADR-002: Self-Correction Through Feedback

**Decision**: Automatically detect outcomes and update confidence using Bayesian updating

**Why**:
- Lessons can be wrong - system needs to detect and self-correct
- Research: Online learning continuously refines from feedback
- Asymmetric updates: Failures penalized more than successes rewarded (prevents overconfidence)

**Alternative Rejected**:
- User-triggered only → Rejected: Misses automatic feedback, high friction
- ML-based prediction → Rejected: Overkill, too slow

**Outcome Detection**:
- Lesson injected but mistake still occurred → -40% confidence
- User explicitly contradicts → -60% confidence
- Lesson prevented mistake → +15% confidence
- User confirms lesson → +10% confidence
- Auto-deprecate if confidence < 0.30

---

### ADR-003: Confidence Calculation & Refinement

**Decision**: Evidence-source heuristics for initial confidence, Bayesian multiplicative updates for refinement

**Why**:
- Fast (<10ms) - no ML overhead
- Transparent - clear rules, auditable
- Research-validated - Bayesian updating proven effective

**Alternative Rejected**:
- Fixed scores → Rejected: Can't learn from outcomes
- ML-based → Rejected: Too complex, too slow

**Formula**:
```
Initial confidence = base_by_source + repetition_boost + priority_boost
Update confidence = current * multiplier[outcome]
Multipliers: success=1.15, failure=0.60, contradiction=0.40, confirmation=1.10
Cap: 0.99 max (epistemic humility), 0.10 min (audit trail)
```

---

### ADR-004: Replacing Approval Workflow

**Decision**: Replace mandatory draft/promote with optional validation for uncertain lessons

**Why**:
- High-confidence lessons (0.70+) active immediately - no friction
- Low-confidence lessons (<0.70) flagged for optional review
- Research: RLHF uses human feedback for uncertain cases only

**Alternative Rejected**:
- Keep draft/promote + auto-promote → Rejected: Complexity of dual paths
- No validation (fully automatic) → Rejected: Users want override capability

**New Commands**:
- `/knowledge-review-uncertain` (shows confidence < 0.70 only)
- `/knowledge-validate <id>` (user confirms: +10% confidence)
- `/knowledge-contradict <id> <reason>` (user rejects: -60% confidence)
- `/knowledge-deprecate <id> <reason>` (explicit deprecation)
- `/knowledge-calibration` (check if confidence matches accuracy)

**Removed Commands**:
- `/knowledge-review-drafts` (replaced)
- `/knowledge-promote <id>` (no longer needed - auto-activate)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Implementation Approach

**Phase 1: Add New Fields** (Day 1, 2-3 hours)
- Add confidence, status, outcome tracking fields to schema
- Migration script for existing lessons
- Non-breaking changes

**Phase 2: Update Hooks - Confidence Calculation** (Day 1, 3-4 hours)
- Implement confidence calculation in lesson creation
- Update hooks/on_stop.py

**Phase 3: Update Query Engine** (Day 2, 4-5 hours)
- Filter by status (exclude deprecated/archived)
- Weight relevance by confidence
- Performance validation (<100ms)

**Phase 4: Implement Outcome Tracking** (Day 3-4, 8-10 hours)
- Track lesson injections in PreToolUse
- Detect outcomes in Stop hook
- Update confidence based on outcomes
- Auto-deprecation checks

**Phase 5: Add CLI Commands** (Day 5, 6-8 hours)
- Implement new validation commands
- Remove old promote command
- Update command documentation

**Phase 6: Documentation & Testing** (Day 6-7, 8-12 hours)
- End-to-end testing
- Performance benchmarks
- Calibration checks
- User documentation

**Technology Stack**:
- Python 3.10+: Existing codebase language
- Bayesian updating: Simple multiplicative confidence updates (< 10ms)
- Pattern matching: Regex for outcome detection in conversations
- JSON: Store outcome history and confidence metadata in graph nodes

**Dependencies**:
- No new external libraries required
- Uses existing: hooks system, graph storage, experience_query.py
- Backward compatible with existing lessons (migration script)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Security Considerations

**Risk 1: Outcome Detection False Positives**
- **Impact**: Good lessons incorrectly deprecated
- **Mitigation**: Conservative thresholds (need 3 failures OR confidence < 0.30), user can validate to override

**Risk 2: Malicious Confidence Manipulation**
- **Impact**: Bad lessons used with high confidence
- **Mitigation**: Validate bounds on load, calibration monitoring detects anomalies

**Risk 3: Confidence Inflation Attack**
- **Impact**: Overconfident lessons
- **Mitigation**: Cap at 0.99, validation has diminishing returns, calibration checks

**Risk 4: Sensitive Data in Lessons**
- **Impact**: Privacy leak in graph files
- **Mitigation**: Lessons about process not data, review patterns, user can deprecate, graphs in .claude/ (gitignored)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Testing Strategy

**Unit Tests**:
- Confidence calculation (different sources, priorities)
- Status assignment (thresholds)
- Bayesian updates (success/failure/contradiction)
- Deprecation checks
- Performance (<10ms per calculation)

**Integration Tests**:
- Full learning loop (mistake → learn → inject → prevent → refine)
- Self-correction on failure (wrong lesson → auto-deprecate)
- User validation workflow (uncertain → validate → active)
- Performance (outcome detection <100ms)

**Manual Scenarios**:
- Version bump (original use case) end-to-end
- Wrong lesson self-corrects after 3 failures
- User validates uncertain lesson
- User contradicts wrong lesson

**Success Metrics**:
- Immediate learning rate >= 70% (lessons active without review)
- False positive rate <= 15% (active → deprecated within 7 days)
- Calibration deviation <= 10% (confidence matches accuracy)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Approval Checklist

Please confirm:
- [ ] **Architecture makes sense** - Confidence-based immediate learning is the right approach
- [ ] **Key decisions are sound** - ADRs address the draft/promote problem correctly
- [ ] **Approach is appropriately scoped** - Not over-engineered, delivers immediate value
- [ ] **Dependencies are acceptable** - No new libraries, backward compatible
- [ ] **Security requirements are adequate** - Risks identified and mitigated
- [ ] **Research foundation is solid** - RLHF, Bayesian updating, online learning patterns applied correctly
- [ ] **Ready to proceed to implementation** - Design is complete and actionable

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Design Documents

**Full Design Specification**: `docs/CONFIDENCE_BASED_LEARNING_DESIGN.md` (35 pages)
- Complete ADRs with research citations
- Technical specifications (data model, hooks, CLI)
- Implementation plan (6 phases)
- Security analysis
- Testing strategy
- Migration plan

**Research Foundation**:
- RLHF (OpenAI, Anthropic): Trust scores determine updates
- Bayesian updating: Prior + evidence → posterior confidence
- Online learning: Continuous refinement from feedback
- Confidence calibration: Ensure scores match accuracy

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**To proceed**: Reply with "approved" or "looks good"

**To revise**: Provide specific feedback on what needs adjustment

**To see full details**: Read `docs/CONFIDENCE_BASED_LEARNING_DESIGN.md`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
