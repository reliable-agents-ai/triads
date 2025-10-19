# Confidence-Based Immediate Learning System - Design Specification

**Version**: 1.0.0
**Status**: Design Review
**Created**: 2025-10-19
**Author**: solution-architect

---

## Executive Summary

**What we're building**: A confidence-based immediate learning system that learns like humans do - forming hypotheses immediately based on evidence quality, then refining through feedback rather than waiting for external approval.

**Why this approach**: The current draft/promote workflow breaks the natural learning loop. Humans don't wait for approval to learn lessons - they assess confidence based on evidence strength, act on that confidence, and refine understanding through outcomes. AI systems (RLHF, Constitutional AI, online learning) follow the same pattern.

**Timeline**: 3-4 phases over 5-7 days estimated

---

## Problem Statement

### Current System (Broken Learning Loop)

```
User corrects mistake → System creates lesson with status="draft" → Lesson ignored by query engine
                                                                   ↓
User must manually review → /knowledge-promote <id> → Lesson becomes "active" → Lesson used

Problems:
1. Lessons never used until manually promoted (friction)
2. High-confidence lessons (user corrections) treated same as low-confidence (guesses)
3. No automatic refinement based on outcomes
4. Breaks natural learning: "form hypothesis → test → refine"
```

### Desired System (Natural Learning Loop)

```
Evidence → Calculate confidence → Learn immediately (if confident) → Monitor outcomes → Refine confidence
    ↓                                      ↓                              ↓
User correction (95%)             Inject into context            Prevented mistake (+10%)
Repeated pattern (85%)            Use with appropriate weight    Mistake still occurred (-40%)
Explicit block (90%)              Trust proportional to confidence  User contradicted (-60%)
Agent guess (65%)                 Optional validation available    User confirmed (+15%)
```

---

## Research Foundation

### AI Self-Correction Patterns

**1. Reinforcement Learning from Human Feedback (RLHF)**

**Pattern**: Systems learn from human feedback without requiring approval for every update
- **OpenAI GPT models**: Update based on feedback quality, not approval gates
- **Anthropic Constitutional AI**: Self-critique and refinement without external validation
- **Key insight**: Trust scores determine update magnitude, not binary approve/reject

**Application to our system**:
- User corrections = highest trust score → immediate learning
- Repeated patterns = medium-high trust → immediate but lower weight
- System inferences = lower trust → learn but flag for validation

**2. Bayesian Confidence Updating**

**Pattern**: Start with prior confidence, update based on evidence
- **Formula**: `P(H|E) = P(E|H) * P(H) / P(E)`
- **In practice**: Strong evidence (user correction) → high posterior confidence
- **Refinement**: Each outcome updates confidence (success +10-15%, failure -40-60%)

**Application to our system**:
```python
# Initial confidence based on evidence source
if source == "user_correction":
    confidence = 0.95  # Very strong evidence
elif source == "repeated_mistake" and count >= 2:
    confidence = 0.85  # Strong evidence
elif source == "process_knowledge_block":
    confidence = 0.90  # Explicit, structured
else:
    confidence = 0.65  # Weak evidence, needs validation

# Update after outcome
if lesson_prevented_mistake:
    confidence = min(0.99, confidence * 1.15)  # Cap at 0.99
elif mistake_despite_lesson:
    confidence *= 0.60  # Significant penalty
elif user_confirmed:
    confidence = min(0.99, confidence * 1.10)
elif user_contradicted:
    confidence *= 0.40  # Strong penalty
```

**3. Online Learning & Contradiction Detection**

**Pattern**: Continuous learning from stream of data with self-correction
- **Concept drift detection**: Recognize when learned patterns become invalid
- **Contradiction signals**: New evidence conflicts with existing belief
- **Graceful degradation**: Low-confidence items deprecate automatically

**Application to our system**:
- Monitor lesson usage: Was it injected? Did mistake still occur?
- Detect contradictions: User says opposite of lesson, or repeats mistake after injection
- Auto-deprecate: If confidence drops below threshold (0.30), mark deprecated

**4. Confidence Calibration**

**Pattern**: Ensure confidence scores reflect actual reliability
- **Well-calibrated**: 85% confidence → 85% accuracy in practice
- **Monitoring**: Track precision/recall per confidence band
- **Adjustment**: Recalibrate if confidence != accuracy

**Application to our system**:
```python
# Track accuracy by confidence band
confidence_bands = {
    "0.90-1.00": {"injected": 15, "effective": 14, "accuracy": 93%},
    "0.80-0.90": {"injected": 20, "effective": 17, "accuracy": 85%},
    "0.70-0.80": {"injected": 10, "effective": 7, "accuracy": 70%},
    "below_0.70": {"flagged_for_review": 5}
}

# If band accuracy < confidence, recalibrate downward
```

---

## Architectural Decision Records

### ADR-001: Immediate Learning Based on Confidence

**Status**: Proposed

**Context**:
Current system creates all lessons with `status: "draft"` and requires manual promotion. This breaks the learning loop and creates friction. Research shows AI systems (RLHF, Constitutional AI) learn immediately based on evidence quality.

**Decision**:
Lessons become `status: "active"` immediately based on confidence score and priority. No draft status for high-confidence lessons.

**Confidence Thresholds** (research-informed):

| Source | Initial Confidence | Status | Rationale |
|--------|-------------------|--------|-----------|
| User correction | 0.95 | active | Strongest signal (human identified error) |
| Repeated mistake (2+ occurrences) | 0.85 | active | Pattern confirmed by repetition |
| Explicit [PROCESS_KNOWLEDGE] block | 0.90 | active | Structured, intentional documentation |
| CRITICAL priority (deployment context) | 0.95 | active | High-stakes context increases confidence |
| Agent inference | 0.65 | needs_validation | Weak signal, flag for review |
| Suggestion without evidence | 0.50 | needs_validation | Very weak, manual review required |

**Status Assignment Logic**:
```python
def assign_status(confidence: float, priority: str) -> str:
    """
    Assign lesson status based on confidence and priority.

    Rules (research-informed):
    - confidence >= 0.80 → active (learn immediately)
    - 0.70 <= confidence < 0.80 AND priority in [CRITICAL, HIGH] → active
    - confidence < 0.70 → needs_validation (flag for optional review)
    - confidence < 0.50 → archived (too weak to learn)
    """
    if confidence >= 0.80:
        return "active"
    elif confidence >= 0.70 and priority in ["CRITICAL", "HIGH"]:
        return "active"  # Lower bar for important contexts
    elif confidence >= 0.50:
        return "needs_validation"
    else:
        return "archived"  # Too weak to be useful
```

**Alternatives Considered**:

1. **Keep draft/promote workflow** (current)
   - **Rejected**: Breaks learning loop, high friction, ignores evidence quality
   - Research: RLHF doesn't gate every update on human approval

2. **All lessons active immediately**
   - **Rejected**: Would inject low-confidence noise
   - Research: Confidence calibration requires varying trust levels

3. **Hybrid: Confidence-based activation** (chosen)
   - **Advantages**: Matches human learning, respects evidence strength, allows refinement
   - **Research support**: Bayesian updating, RLHF, online learning all use this pattern

**Consequences**:

**Pros**:
- Natural learning loop: form hypothesis → test → refine
- High-confidence lessons used immediately (no friction)
- Trust proportional to evidence quality
- Automatic refinement based on outcomes

**Cons**:
- Risk of acting on wrong lessons (mitigated by confidence thresholds)
- Need monitoring to detect bad lessons (added failure tracking)
- Complexity in confidence calculation (worth the benefit)

**Implementation Impact**:
- Remove `status: "draft"` from high-confidence lessons (hooks/on_stop.py:828)
- Add confidence calculation logic
- Update query engine to weight by confidence
- Add outcome tracking for refinement

**Research Citations**:
- OpenAI RLHF (Ouyang et al., 2022): Trust scores determine update magnitude
- Anthropic Constitutional AI (Bai et al., 2022): Self-refinement without approval gates
- Bayesian updating: Prior + evidence → posterior confidence
- Online learning: Continuous refinement from feedback stream

---

### ADR-002: Self-Correction Through Feedback

**Status**: Proposed

**Context**:
Once lessons are learned, the system needs to detect when they're wrong and correct them. Current system has no feedback mechanism - lessons remain active even if ineffective.

**Decision**:
Implement automatic self-correction through outcome monitoring and Bayesian confidence updating.

**Contradiction Detection Methods**:

1. **Lesson injected but mistake still occurred**
   - **Signal strength**: Strong (lesson clearly didn't work)
   - **Confidence impact**: -40% (multiply by 0.60)
   - **Detection**: Track injected lessons in PreToolUse, check if same mistake pattern appears in Stop hook

2. **User explicitly contradicts lesson**
   - **Signal strength**: Very strong (human overriding)
   - **Confidence impact**: -60% (multiply by 0.40)
   - **Detection**: Pattern match: "that's wrong", "actually [opposite]", "ignore that lesson"

3. **Lesson successfully prevented mistake**
   - **Signal strength**: Medium (positive reinforcement)
   - **Confidence impact**: +15% (multiply by 1.15, cap at 0.99)
   - **Detection**: Lesson injected + expected mistake pattern did NOT occur

4. **User confirms lesson**
   - **Signal strength**: Medium (validation)
   - **Confidence impact**: +10% (multiply by 1.10, cap at 0.99)
   - **Detection**: Pattern match: "yes", "correct", "that's right", "/knowledge-validate <id>"

**Confidence Update Formula** (Bayesian-inspired):

```python
def update_confidence(
    current_confidence: float,
    outcome: str,  # "success", "failure", "contradiction", "confirmation"
) -> float:
    """
    Update confidence based on outcome (Bayesian updating pattern).

    Research basis:
    - Success: Modest increase (evidence confirms hypothesis)
    - Failure: Significant decrease (evidence contradicts hypothesis)
    - Contradiction: Strong decrease (human override signal)
    - Confirmation: Modest increase (human validation)

    Asymmetry rationale (research-informed):
    - Negative evidence should outweigh positive (prevent overconfidence)
    - Human feedback (contradiction/confirmation) stronger than outcomes
    """
    multipliers = {
        "success": 1.15,       # +15% (lesson worked)
        "confirmation": 1.10,  # +10% (human validated)
        "failure": 0.60,       # -40% (lesson didn't work)
        "contradiction": 0.40, # -60% (human rejected)
    }

    new_confidence = current_confidence * multipliers[outcome]

    # Cap at 0.99 (never 100% certain - epistemic humility)
    # Floor at 0.10 (keep for audit trail, but effectively deprecated)
    return max(0.10, min(0.99, new_confidence))
```

**Deprecation Criteria**:

```python
def check_deprecation(lesson: dict) -> bool:
    """
    Determine if lesson should be deprecated.

    Rules (research-informed):
    - confidence < 0.30 → deprecated (too unreliable)
    - failure_count >= 3 AND success_count == 0 → deprecated (consistently wrong)
    - user_contradictions >= 2 → deprecated (human rejected multiple times)
    """
    if lesson["confidence"] < 0.30:
        return True

    if lesson["failure_count"] >= 3 and lesson["success_count"] == 0:
        return True

    if lesson.get("contradiction_count", 0) >= 2:
        return True

    return False
```

**Alternatives Considered**:

1. **User-triggered correction only**
   - **Rejected**: Misses automatic feedback signals (failures), high friction
   - Research: Online learning shows value of automatic feedback

2. **ML-based effectiveness prediction**
   - **Rejected**: Overkill, requires training data, adds latency
   - Research: Simple Bayesian updating effective for small-scale learning

3. **Automatic outcome monitoring + Bayesian updating** (chosen)
   - **Advantages**: Low latency, transparent, matches research patterns
   - **Research support**: RLHF reward modeling, Bayesian online learning

**Consequences**:

**Pros**:
- Self-healing: Bad lessons automatically deprecate
- Continuous improvement: Good lessons strengthen over time
- Low friction: No manual intervention needed for most cases
- Transparent: Simple confidence math, auditable

**Cons**:
- Outcome detection not 100% accurate (might miss subtle failures)
- Requires tracking infrastructure (lesson injection logs, outcome matching)
- Risk of premature deprecation (mitigated by thresholds)

**Implementation Impact**:
- Add `success_count`, `failure_count`, `contradiction_count` fields
- Track lesson injections in PreToolUse hook
- Match outcomes in Stop hook
- Update confidence after each outcome
- Check deprecation criteria
- Store deprecation reason for audit

**Research Citations**:
- RLHF reward modeling: Automatic feedback from outcomes
- Bayesian online learning: Continuous probability updates
- Contradiction detection (NLP): "X but actually Y" patterns
- Epistemic humility: Never 100% certain (Kahneman, "Thinking Fast and Slow")

---

### ADR-003: Confidence Calculation & Refinement

**Status**: Proposed

**Context**:
Need systematic way to calculate initial confidence based on evidence source, then refine based on outcomes. Must be fast (<10ms), transparent, and well-calibrated.

**Decision**:
Use evidence-source heuristics for initial confidence, Bayesian multiplicative updates for refinement, periodic calibration checks.

**Initial Confidence Calculation**:

```python
def calculate_initial_confidence(
    source: str,
    priority: str,
    repetition_count: int = 1,
    context: dict = None
) -> float:
    """
    Calculate initial confidence based on evidence source and context.

    Research basis:
    - Stronger evidence (user correction) → higher confidence
    - Repetition confirms pattern → confidence boost
    - High-stakes context (CRITICAL) → confidence boost
    - Weak evidence (agent guess) → lower confidence

    Returns: float in range [0.50, 0.95]
    """
    # Base confidence from source
    base_confidences = {
        "user_correction": 0.95,        # Strongest signal
        "repeated_mistake": 0.75,       # Will be boosted by repetition
        "process_knowledge_block": 0.90, # Explicit, structured
        "agent_inference": 0.65,        # Weak signal
        "suggestion": 0.50,             # Very weak
    }

    confidence = base_confidences.get(source, 0.60)

    # Boost for repetition (research: repeated patterns more reliable)
    if source == "repeated_mistake" and repetition_count >= 2:
        repetition_boost = min(0.15, (repetition_count - 1) * 0.05)
        confidence += repetition_boost

    # Boost for CRITICAL priority (high-stakes context)
    if priority == "CRITICAL":
        confidence = min(0.95, confidence * 1.05)

    # Penalty for conflicting evidence (if provided in context)
    if context and context.get("conflicting_evidence"):
        confidence *= 0.85

    # Ensure bounds [0.50, 0.95]
    return max(0.50, min(0.95, confidence))
```

**Refinement Through Outcomes**:

```python
def refine_confidence(lesson: dict, outcome_history: list) -> float:
    """
    Refine confidence based on historical outcomes.

    Research basis: Bayesian updating with asymmetric evidence weighting
    - Failures penalized more than successes rewarded (prevent overconfidence)
    - Recent outcomes weighted more than old (recency bias)
    - Contradictions strongest signal (human feedback > automated)

    Args:
        lesson: Lesson dictionary with current confidence
        outcome_history: List of outcomes (most recent first)

    Returns: Updated confidence
    """
    current_confidence = lesson["confidence"]

    # Weight recent outcomes more (exponential decay)
    for i, outcome in enumerate(outcome_history[:10]):  # Last 10 outcomes
        weight = 0.9 ** i  # 1.0, 0.9, 0.81, 0.73, ...

        if outcome == "success":
            current_confidence *= (1 + 0.15 * weight)
        elif outcome == "failure":
            current_confidence *= (1 - 0.40 * weight)
        elif outcome == "contradiction":
            current_confidence *= (1 - 0.60 * weight)
        elif outcome == "confirmation":
            current_confidence *= (1 + 0.10 * weight)

    # Ensure bounds [0.10, 0.99]
    return max(0.10, min(0.99, current_confidence))
```

**Calibration Monitoring**:

```python
def check_calibration(lessons: list) -> dict:
    """
    Check if confidence scores are well-calibrated.

    Research basis: Confidence should match accuracy
    - 90% confidence lessons should be correct 90% of time
    - Significant deviation → recalibration needed

    Returns: Calibration report with adjustment recommendations
    """
    bands = {
        "0.90-1.00": {"total": 0, "successful": 0},
        "0.80-0.90": {"total": 0, "successful": 0},
        "0.70-0.80": {"total": 0, "successful": 0},
        "0.60-0.70": {"total": 0, "successful": 0},
    }

    for lesson in lessons:
        conf = lesson["confidence"]
        success_rate = lesson["success_count"] / max(1, lesson["success_count"] + lesson["failure_count"])

        if conf >= 0.90:
            band = "0.90-1.00"
        elif conf >= 0.80:
            band = "0.80-0.90"
        elif conf >= 0.70:
            band = "0.70-0.80"
        else:
            band = "0.60-0.70"

        bands[band]["total"] += 1
        if success_rate > 0.5:  # Majority success = "successful"
            bands[band]["successful"] += 1

    # Calculate accuracy per band
    report = {}
    for band, data in bands.items():
        if data["total"] > 0:
            accuracy = data["successful"] / data["total"]
            expected = float(band.split("-")[0])
            deviation = abs(accuracy - expected)

            report[band] = {
                "accuracy": accuracy,
                "expected": expected,
                "deviation": deviation,
                "needs_recalibration": deviation > 0.15  # >15% deviation
            }

    return report
```

**Alternatives Considered**:

1. **Fixed confidence scores**
   - **Rejected**: Doesn't learn from outcomes, can't self-correct
   - Research: Static confidence leads to overconfidence (Dunning-Kruger)

2. **ML-based confidence prediction**
   - **Rejected**: Requires training data, complex, slow
   - Research: Simple heuristics + Bayesian updating often outperform ML in low-data regimes

3. **Evidence-source heuristics + Bayesian refinement** (chosen)
   - **Advantages**: Fast (<10ms), transparent, well-calibrated, research-validated
   - **Research support**: Bayesian updating, calibration monitoring, RLHF

**Consequences**:

**Pros**:
- Fast: Heuristics + simple math = <10ms
- Transparent: Clear rules, auditable
- Self-calibrating: Monitors and adjusts
- Research-validated: Bayesian updating proven effective

**Cons**:
- Heuristics may need tuning based on real usage
- Calibration requires sufficient data (20+ lessons per band)
- Doesn't capture complex interactions (trade-off for speed)

**Implementation Impact**:
- Calculate confidence in `create_process_knowledge_node()`
- Update confidence in Stop hook after outcome detection
- Add calibration check command (`/knowledge-calibration`)
- Store outcome history (last 10 outcomes per lesson)

**Research Citations**:
- Bayesian updating: Cox's theorem, probability as extended logic
- Confidence calibration: Brier scores, proper scoring rules
- Recency weighting: Exponential decay in time series analysis
- Asymmetric updating: Kahneman & Tversky, loss aversion

---

### ADR-004: Replacing Approval Workflow

**Status**: Proposed

**Context**:
Current workflow requires manual review of all drafts (`/knowledge-review-drafts`) and promotion (`/knowledge-promote <id>`). This creates friction and doesn't align with confidence-based learning.

**Decision**:
Replace draft/promote workflow with optional validation workflow. High-confidence lessons active immediately, low-confidence lessons flagged for optional review.

**New Status Values**:

```python
STATUS_VALUES = {
    "active": "Lesson in use, confidence >= 0.70 (or >= 0.80 for MEDIUM/LOW priority)",
    "needs_validation": "Confidence < 0.70, flagged for optional review",
    "deprecated": "Confidence < 0.30 or failed criteria, kept for audit",
    "archived": "User explicitly archived, not shown in reviews"
}
```

**New CLI Commands**:

| Command | Purpose | Effect |
|---------|---------|--------|
| `/knowledge-review-uncertain` | Show lessons with `needs_validation` status | Display lessons with confidence < 0.70 for optional review |
| `/knowledge-validate <id>` | User confirms lesson is correct | Increase confidence by +10%, change status to `active` if crosses threshold |
| `/knowledge-contradict <id> <reason>` | User says lesson is wrong | Decrease confidence by -60%, add reason to deprecation notes |
| `/knowledge-deprecate <id> <reason>` | Explicitly deprecate lesson | Change status to `deprecated`, store reason |
| `/knowledge-calibration` | Check calibration of confidence scores | Show accuracy by confidence band, suggest recalibration if needed |

**Removed Commands**:

- `/knowledge-review-drafts` (replaced by `/knowledge-review-uncertain`)
- `/knowledge-promote <id>` (no longer needed - lessons activate automatically)
- `/knowledge-archive <id>` (use `/knowledge-deprecate` instead for clarity)

**Workflow Comparison**:

**Old (Draft/Promote)**:
```
1. Mistake happens
2. System creates lesson with status="draft"
3. Lesson ignored until manually promoted
4. User runs /knowledge-review-drafts
5. User runs /knowledge-promote <id>
6. Lesson becomes active
7. Lesson used in next session

Problems: Steps 3-5 create friction, break learning loop
```

**New (Confidence-Based)**:
```
1. Mistake happens
2. System calculates confidence based on evidence
3. If confidence >= 0.70: status="active", lesson used immediately
   If confidence < 0.70: status="needs_validation", flagged for optional review
4. Optional: User runs /knowledge-review-uncertain (only low-confidence lessons)
5. Optional: User runs /knowledge-validate <id> or /knowledge-contradict <id>
6. System automatically refines confidence based on outcomes
7. If confidence drops < 0.30: auto-deprecate

Benefits: Immediate learning, optional validation, automatic refinement
```

**Alternatives Considered**:

1. **Keep draft/promote, add auto-promote for high-confidence**
   - **Rejected**: Complexity of maintaining two paths, still has friction for medium-confidence lessons
   - Research: RLHF doesn't use dual-track approval

2. **No validation commands (fully automatic)**
   - **Rejected**: Users want ability to override bad lessons quickly
   - Research: Human-in-the-loop improves calibration (RLHF, Constitutional AI)

3. **Optional validation for uncertain lessons** (chosen)
   - **Advantages**: Best of both worlds - automatic for high-confidence, user control for uncertain
   - **Research support**: RLHF uses human feedback for uncertain cases

**Consequences**:

**Pros**:
- Immediate learning for high-confidence lessons
- Reduced friction (no mandatory review)
- Optional validation for uncertain cases
- User control retained (contradict/deprecate)
- Automatic refinement reduces manual work

**Cons**:
- Risk of acting on wrong lessons (mitigated by confidence thresholds and auto-deprecation)
- Users might not review uncertain lessons (acceptable - better than draft limbo)
- Command changes require user re-learning (worth it for better UX)

**Implementation Impact**:
- Update `/knowledge-review-drafts` to `/knowledge-review-uncertain`
- Add `/knowledge-validate`, `/knowledge-contradict`, `/knowledge-deprecate`, `/knowledge-calibration` commands
- Remove `/knowledge-promote` (no longer applicable)
- Update hooks/on_stop.py to assign status based on confidence
- Update experience_query.py to filter by status (exclude deprecated/archived)

**Migration Strategy**:

```python
def migrate_existing_lessons():
    """
    Migrate existing draft lessons to new status system.

    Rules:
    - CRITICAL priority + draft → calculate confidence, likely active
    - HIGH priority + draft → calculate confidence, likely active
    - MEDIUM/LOW priority + draft → needs_validation
    - User-promoted active lessons → keep active, set confidence=0.95
    """
    for lesson in get_all_lessons():
        if lesson["status"] == "active":
            # User explicitly promoted, trust that
            lesson["confidence"] = 0.95
            # Keep status="active"

        elif lesson["status"] == "draft":
            # Calculate confidence from source
            confidence = calculate_initial_confidence(
                source=lesson.get("detection_method", "unknown"),
                priority=lesson.get("priority", "MEDIUM"),
                repetition_count=lesson.get("repetition_count", 1)
            )
            lesson["confidence"] = confidence

            # Assign new status
            lesson["status"] = assign_status(confidence, lesson["priority"])

        elif lesson["status"] == "archived":
            # Keep archived, set confidence=0.10
            lesson["confidence"] = 0.10
            lesson["status"] = "deprecated"
```

**Research Citations**:
- RLHF human-in-the-loop: Feedback for uncertain predictions
- Constitutional AI: Optional human critique for refinement
- Active learning: Query human for most uncertain examples
- Confidence-based triggering: Only escalate uncertain cases

---

## Technical Specification

### Data Model Changes

**New Fields** (add to all process knowledge nodes):

```python
{
  "id": "process_user_correction_20251019_143022",
  "type": "Concept",
  "label": "Remember: marketplace.json when bumping version",
  "description": "User correction: forgot - marketplace.json",
  "process_type": "warning",
  "priority": "CRITICAL",

  # === NEW FIELDS ===

  # Confidence & Status
  "confidence": 0.95,  # float [0.0, 1.0], required
  "status": "active",  # "active" | "needs_validation" | "deprecated" | "archived"

  # Evidence & Source
  "source": "user_correction",  # "user_correction" | "repeated_mistake" | "process_knowledge_block" | "agent_inference"
  "detection_method": "user_correction",  # Legacy field, kept for compatibility
  "repetition_count": 1,  # How many times this pattern occurred

  # Outcome Tracking
  "success_count": 0,  # Times lesson prevented mistake
  "failure_count": 0,  # Times mistake occurred despite lesson
  "confirmation_count": 0,  # Times user validated lesson
  "contradiction_count": 0,  # Times user contradicted lesson

  # Usage Tracking
  "injection_count": 0,  # Times lesson was injected into context
  "last_injected_at": null,  # ISO timestamp or null
  "last_outcome": null,  # "success" | "failure" | "confirmation" | "contradiction" | null
  "outcome_history": [],  # Last 10 outcomes ["success", "failure", ...]

  # Deprecation
  "deprecated_at": null,  # ISO timestamp or null
  "deprecated_reason": null,  # String or null
  "deprecation_automatic": false,  # true if auto-deprecated, false if user-triggered

  # Metadata (existing)
  "created_by": "experience-learning-system",
  "created_at": "2025-10-19T14:30:22.000000",
  "updated_at": "2025-10-19T14:30:22.000000",  # NEW: Track updates
  "evidence": "Learned from conversation at 2025-10-19T14:30:22"
}
```

**Field Validation**:

```python
def validate_process_knowledge_node(node: dict) -> list[str]:
    """
    Validate process knowledge node has all required fields.

    Returns: List of validation errors (empty if valid)
    """
    errors = []

    # Required fields
    required = ["id", "type", "confidence", "status", "source", "created_at"]
    for field in required:
        if field not in node:
            errors.append(f"Missing required field: {field}")

    # Confidence bounds
    if "confidence" in node:
        if not (0.0 <= node["confidence"] <= 1.0):
            errors.append(f"confidence must be in [0.0, 1.0], got {node['confidence']}")

    # Valid status
    valid_statuses = ["active", "needs_validation", "deprecated", "archived"]
    if "status" in node:
        if node["status"] not in valid_statuses:
            errors.append(f"status must be one of {valid_statuses}, got {node['status']}")

    # Valid source
    valid_sources = ["user_correction", "repeated_mistake", "process_knowledge_block", "agent_inference", "suggestion"]
    if "source" in node:
        if node["source"] not in valid_sources:
            errors.append(f"source must be one of {valid_sources}, got {node['source']}")

    # Count fields non-negative
    count_fields = ["success_count", "failure_count", "confirmation_count", "contradiction_count", "injection_count"]
    for field in count_fields:
        if field in node and node[field] < 0:
            errors.append(f"{field} must be non-negative, got {node[field]}")

    return errors
```

### Query Engine Changes

**Filter by Status** (add to `_load_process_knowledge`):

```python
def _load_process_knowledge(self) -> dict[str, list[dict[str, Any]]]:
    """Load all process knowledge nodes from all graphs.

    NEW: Filter by status (only active and needs_validation lessons used).
    Exclude deprecated and archived lessons.

    Returns:
        Dictionary mapping triad_name to list of process knowledge nodes.
    """
    all_graphs = self._loader.load_all_graphs()
    process_knowledge: dict[str, list[dict[str, Any]]] = {}

    for triad_name, graph in all_graphs.items():
        nodes = graph.get("nodes", [])

        # Filter to process knowledge nodes (Concept type with process_type)
        # NEW: Also filter by status (exclude deprecated/archived)
        process_nodes = [
            node for node in nodes
            if node.get("type") == "Concept"
            and "process_type" in node
            and node.get("status") in ["active", "needs_validation"]  # NEW
        ]

        if process_nodes:
            process_knowledge[triad_name] = process_nodes

    logger.debug(
        f"Loaded {sum(len(nodes) for nodes in process_knowledge.values())} "
        f"process knowledge nodes from {len(process_knowledge)} triads"
    )

    return process_knowledge
```

**Weight by Confidence** (add to `_calculate_relevance`):

```python
def _calculate_relevance(
    self,
    node: dict[str, Any],
    tool_name: str,
    file_path: str,
    tool_input_str: str,
) -> float:
    """Calculate relevance score for a process knowledge node.

    NEW: Multiply final score by confidence to weight uncertain lessons lower.

    Uses structured scoring algorithm:
    - Tool name match: 40% (exact) or 20% (wildcard)
    - File pattern match: 40%
    - Action keywords: 10%
    - Context keywords: 10%
    - Priority multiplier: CRITICAL=2.0x, HIGH=1.5x, MEDIUM=1.0x, LOW=0.5x
    - Confidence multiplier: NEW - weight by confidence

    Returns:
        Relevance score (0-1+, can exceed 1.0 with CRITICAL multiplier).
    """
    # ... existing scoring logic ...
    base_score = calculate_base_score(...)  # 0.0 to 1.0

    # Apply priority multiplier (existing)
    priority = node.get("priority", "MEDIUM")
    priority_multiplier = PRIORITY_MULTIPLIERS.get(priority, 1.0)
    score_with_priority = base_score * priority_multiplier

    # NEW: Apply confidence multiplier
    confidence = node.get("confidence", 0.80)  # Default 0.80 for backward compat
    final_score = score_with_priority * confidence

    return final_score
```

### Hook Changes

**Stop Hook** (hooks/on_stop.py - lesson creation):

```python
def create_process_knowledge_node(lesson_data, conversation_text):
    """
    Create a Process Concept node from lesson data.

    NEW: Calculate confidence, assign status based on confidence.

    Args:
        lesson_data: Lesson dictionary
        conversation_text: Full conversation text

    Returns:
        Node dictionary ready for graph insertion
    """
    # ... existing logic ...

    # NEW: Calculate confidence
    confidence = calculate_initial_confidence(
        source=lesson_data.get('type', 'unknown'),
        priority=priority,
        repetition_count=lesson_data.get('repetition_count', 1),
        context=lesson_data
    )

    # NEW: Assign status based on confidence
    status = assign_status(confidence, priority)

    # Build node
    node = {
        'id': node_id,
        'type': 'Concept',
        'label': lesson_data.get('label', f"Lesson: {lesson_data.get('missed_item', 'Unknown')}"),
        'description': lesson_data.get('description', ''),
        'confidence': confidence,  # NEW
        'status': status,  # NEW (was always "draft")
        'priority': priority,
        'process_type': lesson_data.get('process_type', 'warning'),
        'source': lesson_data.get('type', 'unknown'),  # NEW
        'detection_method': lesson_data.get('type', 'explicit'),  # Legacy
        'created_by': 'experience-learning-system',
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),  # NEW
        'evidence': f"Learned from conversation at {datetime.now().isoformat()}",

        # NEW: Initialize tracking fields
        'success_count': 0,
        'failure_count': 0,
        'confirmation_count': 0,
        'contradiction_count': 0,
        'injection_count': 0,
        'last_injected_at': None,
        'last_outcome': None,
        'outcome_history': [],
        'deprecated_at': None,
        'deprecated_reason': None,
        'deprecation_automatic': False,
    }

    # ... rest of existing logic ...

    return node
```

**PreToolUse Hook** (hooks/on_pre_experience_injection.py - track injections):

```python
def inject_relevant_knowledge(tool_name, tool_input, cwd):
    """
    Inject relevant process knowledge before tool execution.

    NEW: Track which lessons are injected (for outcome monitoring).
    """
    # ... existing query logic ...

    results = engine.query_for_tool_use(tool_name, tool_input, cwd)

    if not results:
        return

    # NEW: Log injected lessons for outcome tracking
    injected_lessons = []
    for item in results:
        injected_lessons.append({
            "lesson_id": item.node_id,
            "triad": item.triad,
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool_name,
            "file_path": tool_input.get("file_path", ""),
        })

    # Store in session file for Stop hook to read
    session_file = Path(".claude/km/.current_session_injections.json")
    session_file.parent.mkdir(parents=True, exist_ok=True)

    if session_file.exists():
        with open(session_file, 'r') as f:
            existing = json.load(f)
    else:
        existing = []

    existing.extend(injected_lessons)

    with open(session_file, 'w') as f:
        json.dump(existing, f, indent=2)

    # ... existing injection logic ...
```

**Stop Hook** (hooks/on_stop.py - outcome detection):

```python
def detect_lesson_outcomes(conversation_text, injected_lessons):
    """
    Detect outcomes for lessons that were injected this session.

    NEW: Match injected lessons to outcomes (success/failure/contradiction/confirmation).

    Args:
        conversation_text: Full conversation text
        injected_lessons: List of lessons injected this session

    Returns:
        Dictionary mapping lesson_id to outcome
    """
    outcomes = {}

    for injection in injected_lessons:
        lesson_id = injection["lesson_id"]

        # Load lesson to check what mistake it prevents
        lesson = load_lesson_by_id(lesson_id, injection["triad"])
        if not lesson:
            continue

        missed_item = lesson.get("missed_item") or lesson.get("label", "")

        # Check for user contradiction
        contradiction_patterns = [
            r"that's\s+wrong",
            r"actually\s+(?:it|you)\s+should",
            r"ignore\s+that\s+lesson",
            r"that\s+lesson\s+is\s+incorrect",
        ]

        for pattern in contradiction_patterns:
            if re.search(pattern, conversation_text, re.IGNORECASE):
                outcomes[lesson_id] = "contradiction"
                break

        if lesson_id in outcomes:
            continue

        # Check for user confirmation
        confirmation_patterns = [
            r"yes,?\s+that's\s+correct",
            r"good\s+catch",
            r"thanks?\s+for\s+(?:the\s+)?reminder",
            r"/knowledge-validate\s+" + re.escape(lesson_id),
        ]

        for pattern in confirmation_patterns:
            if re.search(pattern, conversation_text, re.IGNORECASE):
                outcomes[lesson_id] = "confirmation"
                break

        if lesson_id in outcomes:
            continue

        # Check if mistake still occurred (failure)
        if missed_item and missed_item.lower() in conversation_text.lower():
            # Check if it's in user correction context
            correction_context = re.search(
                rf"(?:you\s+forgot|you\s+missed|still\s+missing).*{re.escape(missed_item)}",
                conversation_text,
                re.IGNORECASE
            )
            if correction_context:
                outcomes[lesson_id] = "failure"
                continue

        # Default: assume success (lesson was injected, mistake didn't occur)
        outcomes[lesson_id] = "success"

    return outcomes


def update_lessons_with_outcomes(outcomes):
    """
    Update lesson confidence and counts based on detected outcomes.

    NEW: Apply Bayesian confidence updates, check deprecation criteria.
    """
    for lesson_id, outcome in outcomes.items():
        # Find lesson in graphs
        lesson, triad = find_lesson_by_id(lesson_id)
        if not lesson:
            continue

        # Update counts
        if outcome == "success":
            lesson["success_count"] += 1
        elif outcome == "failure":
            lesson["failure_count"] += 1
        elif outcome == "confirmation":
            lesson["confirmation_count"] += 1
        elif outcome == "contradiction":
            lesson["contradiction_count"] += 1

        # Update confidence
        old_confidence = lesson["confidence"]
        lesson["confidence"] = update_confidence(old_confidence, outcome)

        # Update outcome history
        lesson["outcome_history"] = ([outcome] + lesson.get("outcome_history", []))[:10]
        lesson["last_outcome"] = outcome
        lesson["updated_at"] = datetime.now().isoformat()

        # Check deprecation criteria
        if check_deprecation(lesson):
            lesson["status"] = "deprecated"
            lesson["deprecated_at"] = datetime.now().isoformat()
            lesson["deprecation_automatic"] = True
            lesson["deprecated_reason"] = f"Automatic deprecation: confidence={lesson['confidence']:.2f}, success={lesson['success_count']}, failure={lesson['failure_count']}"

        # Save updated lesson back to graph
        save_lesson(lesson, triad)

        # Log outcome
        logger.info(
            f"Lesson {lesson_id}: {outcome} → confidence {old_confidence:.2f} → {lesson['confidence']:.2f}"
        )
```

### CLI Commands

**1. `/knowledge-review-uncertain`**

Purpose: Review lessons with low confidence (<0.70) that need validation

```markdown
# Review Uncertain Knowledge

You are helping the user review **uncertain** process knowledge (confidence < 0.70) that may need validation.

## Your Task

1. **Search for uncertain knowledge**: Query all knowledge graphs for nodes with `status: "needs_validation"`
2. **Display each uncertain lesson** with:
   - Node ID
   - Label
   - Confidence score (with explanation)
   - Priority (CRITICAL, HIGH, MEDIUM, LOW)
   - Process type (checklist, pattern, warning, requirement)
   - Source (how it was learned)
   - Success/failure counts (if any)
   - Content (full details)
   - Triad where it's stored
   - Created date

3. **Group by confidence**: Show lowest confidence first (most uncertain)

4. **For each uncertain lesson, ask the user**:
   - Is this lesson correct and useful?
   - Options:
     - ✅ **Validate** (increase confidence, may activate) - Use `/knowledge-validate <node_id>`
     - ❌ **Contradict** (decrease confidence, may deprecate) - Use `/knowledge-contradict <node_id> <reason>`
     - 🗑️ **Deprecate** (explicitly mark as wrong) - Use `/knowledge-deprecate <node_id> <reason>`
     - ⏸️  **Keep as uncertain** (wait for more evidence) - Do nothing

5. **Show statistics**:
   - Total uncertain lessons by confidence band
   - Breakdown by source
   - Breakdown by triad

## Implementation

Use the following approach:

1. **Load all graphs** from `.claude/graphs/`
2. **Filter nodes** where `status == "needs_validation"`
3. **Sort** by confidence (lowest first), then by created_at (newest first)
4. **Format output** in a clear, reviewable format

## Example Output

```markdown
# 🔍 Uncertain Knowledge Review

**Total uncertain lessons**: 3
- Very uncertain (< 0.60): 1
- Uncertain (0.60-0.69): 2

---

## 1. [HIGH] Pattern: Version bump sequence

**Node ID**: `process_agent_inference_20251019_120000`
**Confidence**: 0.55 (uncertain - agent inference)
**Triad**: deployment
**Source**: agent_inference
**Created**: 2025-10-19T12:00:00
**Outcomes**: 0 success, 1 failure, 0 confirmation, 0 contradiction

**Pattern**:
When bumping version:
1. Update version in setup.py
2. Update version in pyproject.toml
3. Update CHANGELOG.md
4. Update marketplace.json

**Why uncertain**: Inferred by agent without explicit confirmation. Failed once.

**Actions**:
- ✅ Validate: `/knowledge-validate process_agent_inference_20251019_120000` (if correct)
- ❌ Contradict: `/knowledge-contradict process_agent_inference_20251019_120000 "marketplace.json not always needed"` (if wrong)
- 🗑️ Deprecate: `/knowledge-deprecate process_agent_inference_20251019_120000 "Incorrect pattern"`

---

[Continue for each uncertain lesson...]
```

## Notes

- Uncertain lessons are NOT used by default (low confidence)
- Validating increases confidence, may activate if crosses threshold
- Contradicting decreases confidence, may auto-deprecate
- These reviews are OPTIONAL - system works without them
- Purpose: Refine confidence for better calibration
```

**2. `/knowledge-validate <node_id>`**

Purpose: User confirms lesson is correct (increase confidence)

```markdown
# Validate Knowledge

You are helping the user **validate** (confirm correctness of) a process knowledge lesson.

## Your Task

1. **Find the lesson** by node_id across all graphs
2. **Display current state**:
   - Label
   - Confidence (before validation)
   - Status
   - Content
3. **Update the lesson**:
   - Increase confidence by +10% (multiply by 1.10)
   - Cap at 0.99 (never 100% certain)
   - Increment confirmation_count
   - Add "confirmation" to outcome_history
   - Update updated_at timestamp
   - If new confidence >= 0.70 AND status == "needs_validation", change to "active"
4. **Save changes** to graph
5. **Report result**:
   - Old confidence → new confidence
   - Old status → new status (if changed)
   - Effect on lesson usage

## Example Output

```markdown
# ✅ Knowledge Validated

**Lesson**: Remember: marketplace.json when bumping version
**Node ID**: `process_user_correction_20251019_143022`
**Triad**: deployment

**Confidence updated**:
- Before: 0.65 (uncertain)
- After: 0.72 (validated) ✓

**Status changed**:
- Before: needs_validation
- After: active ✅

**Effect**: This lesson is now **active** and will be injected before relevant tool uses.

**Outcome history**: [confirmation]
**Confirmation count**: 1
```

## Implementation

```python
def validate_knowledge(node_id: str):
    # Find lesson
    lesson, triad = find_lesson_by_id(node_id)

    # Update confidence
    old_conf = lesson["confidence"]
    lesson["confidence"] = min(0.99, old_conf * 1.10)

    # Update counts
    lesson["confirmation_count"] += 1
    lesson["outcome_history"] = (["confirmation"] + lesson.get("outcome_history", []))[:10]
    lesson["last_outcome"] = "confirmation"
    lesson["updated_at"] = datetime.now().isoformat()

    # Check if should activate
    old_status = lesson["status"]
    if lesson["confidence"] >= 0.70 and old_status == "needs_validation":
        lesson["status"] = "active"

    # Save
    save_lesson(lesson, triad)

    # Report
    print(f"Confidence: {old_conf:.2f} → {lesson['confidence']:.2f}")
    if old_status != lesson["status"]:
        print(f"Status: {old_status} → {lesson['status']}")
```
```

**3. `/knowledge-contradict <node_id> <reason>`**

Purpose: User says lesson is wrong (decrease confidence)

```markdown
# Contradict Knowledge

You are helping the user **contradict** (mark as incorrect) a process knowledge lesson.

## Your Task

1. **Find the lesson** by node_id across all graphs
2. **Display current state**
3. **Update the lesson**:
   - Decrease confidence by -60% (multiply by 0.40)
   - Floor at 0.10 (keep for audit)
   - Increment contradiction_count
   - Add "contradiction" to outcome_history
   - Add reason to notes
   - Update updated_at timestamp
   - If new confidence < 0.30, auto-deprecate
4. **Save changes** to graph
5. **Report result**

## Example Output

```markdown
# ❌ Knowledge Contradicted

**Lesson**: Pattern: Always update all four files when bumping version
**Node ID**: `process_agent_inference_20251019_120000`
**Triad**: deployment

**Confidence updated**:
- Before: 0.65
- After: 0.26 ⚠️

**Status changed**:
- Before: needs_validation
- After: deprecated (automatic - confidence too low)

**Reason**: "marketplace.json not always needed - only for plugin marketplace releases"

**Effect**: This lesson is now **deprecated** and will NOT be used.

**Outcome history**: [contradiction, success]
**Contradiction count**: 1
```

## Implementation

```python
def contradict_knowledge(node_id: str, reason: str):
    # Find lesson
    lesson, triad = find_lesson_by_id(node_id)

    # Update confidence
    old_conf = lesson["confidence"]
    lesson["confidence"] = max(0.10, old_conf * 0.40)

    # Update counts
    lesson["contradiction_count"] += 1
    lesson["outcome_history"] = (["contradiction"] + lesson.get("outcome_history", []))[:10]
    lesson["last_outcome"] = "contradiction"
    lesson["updated_at"] = datetime.now().isoformat()

    # Add reason
    if "contradiction_reasons" not in lesson:
        lesson["contradiction_reasons"] = []
    lesson["contradiction_reasons"].append({
        "reason": reason,
        "timestamp": datetime.now().isoformat()
    })

    # Check if should deprecate
    old_status = lesson["status"]
    if lesson["confidence"] < 0.30:
        lesson["status"] = "deprecated"
        lesson["deprecated_at"] = datetime.now().isoformat()
        lesson["deprecation_automatic"] = True
        lesson["deprecated_reason"] = f"User contradiction: {reason}"

    # Save
    save_lesson(lesson, triad)

    # Report
    print(f"Confidence: {old_conf:.2f} → {lesson['confidence']:.2f}")
    if old_status != lesson["status"]:
        print(f"Status: {old_status} → {lesson['status']} (automatic)")
```
```

**4. `/knowledge-deprecate <node_id> <reason>`**

Purpose: Explicitly deprecate a lesson

```markdown
# Deprecate Knowledge

Explicitly mark a lesson as deprecated (wrong or no longer relevant).

Similar to contradict, but explicitly sets status to "deprecated" regardless of confidence.

Use this when you want to remove a lesson from use without necessarily lowering its confidence score (e.g., requirements changed, lesson no longer applies).
```

**5. `/knowledge-calibration`**

Purpose: Check calibration of confidence scores

```markdown
# Check Confidence Calibration

Display calibration report showing if confidence scores match actual accuracy.

## Output

```markdown
# 📊 Confidence Calibration Report

**Total lessons analyzed**: 45

## Calibration by Confidence Band

### Band: 0.90-1.00 (Very High Confidence)
- **Expected accuracy**: 90-100%
- **Actual accuracy**: 92% (23/25 successful)
- **Status**: ✅ Well-calibrated (deviation: 2%)

### Band: 0.80-0.90 (High Confidence)
- **Expected accuracy**: 80-90%
- **Actual accuracy**: 75% (12/16 successful)
- **Status**: ⚠️ Underperforming (deviation: 8%)
- **Recommendation**: Monitor - may need recalibration if trend continues

### Band: 0.70-0.80 (Medium Confidence)
- **Expected accuracy**: 70-80%
- **Actual accuracy**: 83% (5/6 successful)
- **Status**: ✅ Well-calibrated (deviation: 5%)

### Band: 0.60-0.70 (Low Confidence)
- **Expected accuracy**: 60-70%
- **Actual accuracy**: 50% (1/2 successful)
- **Status**: ⚠️ Insufficient data (only 2 lessons)

## Overall Calibration

**Mean absolute deviation**: 5.0%
**Status**: ✅ Well-calibrated overall

**Recommendation**: No immediate recalibration needed. Continue monitoring 0.80-0.90 band.
```
```

---

## Migration Plan

### Phase 1: Add New Fields (Non-Breaking)

**Goal**: Add new fields to schema without breaking existing functionality

**Tasks**:
1. Add field definitions to data model documentation
2. Update `create_process_knowledge_node()` to initialize new fields
3. Update query engine to handle missing fields gracefully (backward compat)
4. Write migration script to add fields to existing nodes

**Migration Script**:

```python
def migrate_add_new_fields():
    """
    Add new fields to existing process knowledge nodes.

    Preserves existing data, adds defaults for new fields.
    """
    graphs_dir = Path(".claude/graphs")

    for graph_file in graphs_dir.glob("*_graph.json"):
        with open(graph_file, 'r') as f:
            graph = json.load(f)

        modified = False

        for node in graph.get("nodes", []):
            # Only update process knowledge nodes
            if node.get("type") != "Concept" or "process_type" not in node:
                continue

            # Add new fields if missing
            if "confidence" not in node:
                # Infer from existing data
                node["confidence"] = infer_confidence_from_existing(node)
                modified = True

            if "status" not in node:
                node["status"] = infer_status_from_existing(node)
                modified = True

            if "source" not in node:
                node["source"] = node.get("detection_method", "unknown")
                modified = True

            # Initialize tracking fields
            for field in ["success_count", "failure_count", "confirmation_count", "contradiction_count", "injection_count"]:
                if field not in node:
                    node[field] = 0
                    modified = True

            for field in ["last_injected_at", "last_outcome", "deprecated_at", "deprecated_reason"]:
                if field not in node:
                    node[field] = None
                    modified = True

            if "outcome_history" not in node:
                node["outcome_history"] = []
                modified = True

            if "deprecation_automatic" not in node:
                node["deprecation_automatic"] = False
                modified = True

            if "updated_at" not in node:
                node["updated_at"] = node.get("created_at", datetime.now().isoformat())
                modified = True

        # Save if modified
        if modified:
            with open(graph_file, 'w') as f:
                json.dump(graph, f, indent=2)

            print(f"✓ Migrated {graph_file.name}")


def infer_confidence_from_existing(node: dict) -> float:
    """Infer confidence for existing node based on available data."""
    # If user promoted to active, assume high confidence
    if node.get("status") == "active":
        return 0.95

    # If draft, calculate from source
    source = node.get("detection_method", "unknown")
    priority = node.get("priority", "MEDIUM")

    return calculate_initial_confidence(source, priority)


def infer_status_from_existing(node: dict) -> str:
    """Infer status for existing node."""
    existing_status = node.get("status")

    if existing_status == "active":
        return "active"  # Keep active
    elif existing_status == "archived":
        return "deprecated"  # Rename to deprecated
    elif existing_status == "draft":
        # Calculate confidence, assign new status
        confidence = node.get("confidence", 0.70)
        priority = node.get("priority", "MEDIUM")
        return assign_status(confidence, priority)
    else:
        return "needs_validation"  # Conservative default
```

**Timeline**: Day 1 (2-3 hours)

**Risk**: Low - adds fields, doesn't remove anything

### Phase 2: Update Hooks (Confidence Calculation)

**Goal**: Start calculating confidence for new lessons

**Tasks**:
1. Update `create_process_knowledge_node()` in hooks/on_stop.py
2. Implement `calculate_initial_confidence()`
3. Implement `assign_status()`
4. Test with sample lessons

**Timeline**: Day 1 (3-4 hours)

**Risk**: Low - only affects new lessons

### Phase 3: Update Query Engine (Confidence Weighting)

**Goal**: Use confidence in relevance scoring

**Tasks**:
1. Update `_load_process_knowledge()` to filter by status
2. Update `_calculate_relevance()` to multiply by confidence
3. Test query performance (<100ms)
4. Add logging for confidence impact

**Timeline**: Day 2 (4-5 hours)

**Risk**: Medium - affects all queries, needs performance validation

### Phase 4: Implement Outcome Tracking

**Goal**: Detect outcomes and update confidence

**Tasks**:
1. Update PreToolUse hook to log injections
2. Implement `detect_lesson_outcomes()` in Stop hook
3. Implement `update_lessons_with_outcomes()`
4. Implement deprecation checks
5. Test full feedback loop

**Timeline**: Day 3-4 (8-10 hours)

**Risk**: Medium - complex outcome detection, potential false positives

### Phase 5: Add CLI Commands

**Goal**: Provide user validation interface

**Tasks**:
1. Rename `/knowledge-review-drafts` to `/knowledge-review-uncertain`
2. Implement `/knowledge-validate`
3. Implement `/knowledge-contradict`
4. Implement `/knowledge-deprecate`
5. Implement `/knowledge-calibration`
6. Remove `/knowledge-promote` (no longer needed)

**Timeline**: Day 5 (6-8 hours)

**Risk**: Low - CLI commands, low impact if buggy

### Phase 6: Documentation & Testing

**Goal**: Document new system, validate end-to-end

**Tasks**:
1. Update user guide
2. Update technical documentation
3. Create migration guide
4. End-to-end testing
5. Performance benchmarks
6. Calibration checks

**Timeline**: Day 6-7 (8-12 hours)

**Risk**: Low - documentation and validation

---

## Security Considerations

### Risks

**1. Malicious Confidence Manipulation**

**Risk**: User could manually edit graph JSON to set wrong confidence scores
- **Severity**: Medium
- **Likelihood**: Low (requires direct file access)
- **Impact**: Bad lessons used with high confidence

**Mitigation**:
- Validate confidence bounds [0.0, 1.0] on load
- Log confidence changes with timestamps
- Calibration monitoring would detect anomalies

**2. Outcome Detection False Positives**

**Risk**: System incorrectly detects "failure" when lesson actually worked
- **Severity**: Medium
- **Likelihood**: Medium (pattern matching imperfect)
- **Impact**: Good lessons incorrectly deprecated

**Mitigation**:
- Conservative deprecation thresholds (confidence < 0.30)
- Require multiple failures before deprecation
- User can validate to override
- Audit trail preserved (deprecated lessons kept)

**3. Confidence Inflation Attack**

**Risk**: User repeatedly validates lessons to artificially boost confidence
- **Severity**: Low
- **Likelihood**: Low (why would user do this?)
- **Impact**: Overconfident lessons

**Mitigation**:
- Cap confidence at 0.99 (never 100%)
- Validation has diminishing returns (+10% of current)
- Calibration monitoring would detect if confidence > accuracy

**4. Privacy: Sensitive Information in Lessons**

**Risk**: Lessons might capture sensitive data from conversations
- **Severity**: Medium
- **Likelihood**: Low (lessons are about process, not data)
- **Impact**: Sensitive data leaked in graph files

**Mitigation**:
- Review lesson extraction patterns (avoid capturing data)
- Document that lessons should be about process, not specific values
- User can archive lessons with sensitive info
- Graph files already in `.claude/` (typically gitignored)

### Implementation

```python
def validate_confidence_on_load(node: dict) -> dict:
    """Validate and sanitize confidence score."""
    conf = node.get("confidence", 0.70)

    # Enforce bounds
    if not isinstance(conf, (int, float)):
        logger.warning(f"Invalid confidence type for {node['id']}: {type(conf)}")
        conf = 0.70

    if conf < 0.0 or conf > 1.0:
        logger.warning(f"Confidence out of bounds for {node['id']}: {conf}")
        conf = max(0.0, min(1.0, conf))

    node["confidence"] = conf
    return node
```

---

## Testing Strategy

### Unit Tests

**1. Confidence Calculation**

```python
def test_calculate_initial_confidence():
    """Test confidence calculation for different sources."""
    # User correction → high confidence
    assert calculate_initial_confidence("user_correction", "CRITICAL") == 0.95

    # Repeated mistake (2+) → medium-high
    assert calculate_initial_confidence("repeated_mistake", "HIGH", repetition_count=2) >= 0.80

    # Agent inference → low
    assert calculate_initial_confidence("agent_inference", "MEDIUM") == 0.65

    # CRITICAL priority boost
    assert calculate_initial_confidence("suggestion", "CRITICAL") > calculate_initial_confidence("suggestion", "MEDIUM")
```

**2. Status Assignment**

```python
def test_assign_status():
    """Test status assignment based on confidence."""
    # High confidence → active
    assert assign_status(0.85, "MEDIUM") == "active"

    # Medium confidence + CRITICAL → active (lower bar)
    assert assign_status(0.72, "CRITICAL") == "active"

    # Low confidence → needs_validation
    assert assign_status(0.65, "MEDIUM") == "needs_validation"

    # Very low → archived
    assert assign_status(0.45, "LOW") == "archived"
```

**3. Confidence Updating**

```python
def test_update_confidence():
    """Test Bayesian confidence updates."""
    # Success increases
    assert update_confidence(0.80, "success") > 0.80

    # Failure decreases (more than success increases)
    success_delta = update_confidence(0.80, "success") - 0.80
    failure_delta = 0.80 - update_confidence(0.80, "failure")
    assert failure_delta > success_delta  # Asymmetric

    # Contradiction strongest penalty
    assert update_confidence(0.80, "contradiction") < update_confidence(0.80, "failure")

    # Cap at 0.99
    assert update_confidence(0.95, "success") <= 0.99
```

**4. Deprecation Checks**

```python
def test_check_deprecation():
    """Test deprecation criteria."""
    # Low confidence
    assert check_deprecation({"confidence": 0.25, "failure_count": 0, "success_count": 0})

    # Consistent failures
    assert check_deprecation({"confidence": 0.70, "failure_count": 3, "success_count": 0})

    # Multiple contradictions
    assert check_deprecation({"confidence": 0.70, "failure_count": 0, "contradiction_count": 2})

    # Healthy lesson
    assert not check_deprecation({"confidence": 0.80, "failure_count": 1, "success_count": 5})
```

### Integration Tests

**1. Full Learning Loop**

```python
def test_full_learning_loop():
    """Test: mistake → learn → inject → prevent → refine."""
    # 1. User correction creates high-confidence lesson
    conversation = "You forgot to update marketplace.json when bumping version."
    lessons = extract_lessons_from_conversation(conversation, [])

    assert len(lessons) == 1
    lesson = lessons[0]
    assert lesson["confidence"] >= 0.90
    assert lesson["status"] == "active"

    # 2. Lesson injected on next Write to version file
    engine = ExperienceQueryEngine()
    results = engine.query_for_tool_use(
        tool_name="Write",
        tool_input={"file_path": "setup.py", "content": "version = '1.0.1'"},
        cwd="/project"
    )

    assert len(results) > 0
    assert any("marketplace.json" in r.formatted_text for r in results)

    # 3. Mistake prevented (no correction in next conversation)
    conversation2 = "I bumped the version in setup.py and marketplace.json."
    outcomes = detect_lesson_outcomes(conversation2, [{"lesson_id": lesson["id"]}])

    assert outcomes[lesson["id"]] == "success"

    # 4. Confidence increased
    updated_lesson = update_lessons_with_outcomes({lesson["id"]: "success"})
    assert updated_lesson["confidence"] > lesson["confidence"]
```

**2. Self-Correction on Failure**

```python
def test_self_correction_on_failure():
    """Test: wrong lesson → failure → confidence decreases → deprecates."""
    # 1. Create medium-confidence lesson
    lesson = create_process_knowledge_node({
        "type": "agent_inference",
        "label": "Always run tests before commit",
        "description": "Pattern inferred from agent",
        "process_type": "pattern",
        "priority": "MEDIUM"
    }, "")

    assert 0.60 <= lesson["confidence"] <= 0.70
    assert lesson["status"] in ["active", "needs_validation"]

    # 2. Failure detected multiple times
    for _ in range(3):
        lesson = update_lesson_with_outcome(lesson, "failure")

    # 3. Confidence should be very low
    assert lesson["confidence"] < 0.30

    # 4. Auto-deprecated
    assert lesson["status"] == "deprecated"
    assert lesson["deprecation_automatic"] == True
```

**3. User Validation Workflow**

```python
def test_user_validation_workflow():
    """Test: uncertain lesson → user validates → becomes active."""
    # 1. Create uncertain lesson
    lesson = create_process_knowledge_node({
        "type": "agent_inference",
        "label": "Pattern: XYZ",
        "priority": "MEDIUM"
    }, "")

    assert lesson["confidence"] < 0.70
    assert lesson["status"] == "needs_validation"

    # 2. User validates
    updated_lesson = validate_knowledge(lesson["id"])

    # 3. Confidence increased
    assert updated_lesson["confidence"] > lesson["confidence"]

    # 4. Status changed to active (if crossed threshold)
    if updated_lesson["confidence"] >= 0.70:
        assert updated_lesson["status"] == "active"
```

### Performance Tests

**1. Confidence Calculation Speed**

```python
def test_confidence_calculation_performance():
    """Ensure confidence calculation is fast (<10ms)."""
    import time

    start = time.perf_counter()

    for _ in range(1000):
        calculate_initial_confidence("user_correction", "CRITICAL")

    elapsed_ms = (time.perf_counter() - start) * 1000
    avg_ms = elapsed_ms / 1000

    assert avg_ms < 0.01  # <0.01ms per calculation
```

**2. Outcome Detection Performance**

```python
def test_outcome_detection_performance():
    """Ensure outcome detection completes in <100ms."""
    import time

    conversation = "..." * 1000  # Large conversation
    injections = [{"lesson_id": f"lesson_{i}", "triad": "test"} for i in range(10)]

    start = time.perf_counter()
    outcomes = detect_lesson_outcomes(conversation, injections)
    elapsed_ms = (time.perf_counter() - start) * 1000

    assert elapsed_ms < 100  # <100ms total
```

### Manual Testing Scenarios

**Scenario 1: Version Bump (Original Use Case)**

1. User bumps version, forgets marketplace.json
2. User corrects: "You forgot marketplace.json"
3. Verify: Lesson created with confidence >= 0.90, status "active"
4. Next version bump: Write to setup.py
5. Verify: Lesson injected before Write
6. User updates marketplace.json correctly
7. Verify: Outcome detected as "success", confidence increased

**Scenario 2: Wrong Lesson Self-Corrects**

1. Agent infers pattern (medium confidence)
2. Lesson injected
3. User still makes "mistake" (pattern was wrong)
4. Verify: Outcome "failure", confidence decreased
5. Repeat 2 more times
6. Verify: Lesson auto-deprecated (confidence < 0.30)

**Scenario 3: User Validation**

1. Uncertain lesson created (confidence 0.65)
2. Run `/knowledge-review-uncertain`
3. Verify: Lesson shown with low confidence explanation
4. Run `/knowledge-validate <id>`
5. Verify: Confidence increased to ~0.72, status changed to "active"

**Scenario 4: User Contradiction**

1. Active lesson exists (confidence 0.85)
2. User says "That lesson is wrong, actually..."
3. Verify: Outcome "contradiction", confidence decreased to ~0.34
4. Verify: Auto-deprecated (confidence < 0.30)

---

## Success Metrics

### Primary Metrics

**1. Immediate Learning Rate**

**Definition**: Percentage of lessons that become active immediately (without manual review)

**Target**: >= 70% of lessons active immediately

**Measurement**:
```python
immediate_active = count(lessons where status == "active" on creation)
total_lessons = count(all lessons created)
rate = immediate_active / total_lessons
```

**Success Criterion**: rate >= 0.70

**2. False Positive Rate**

**Definition**: Percentage of active lessons that get deprecated within 7 days

**Target**: <= 15% false positive rate

**Measurement**:
```python
false_positives = count(lessons where status changed active → deprecated within 7 days)
total_active = count(lessons that became active)
rate = false_positives / total_active
```

**Success Criterion**: rate <= 0.15

**3. Confidence Calibration**

**Definition**: Mean absolute deviation between confidence scores and actual accuracy

**Target**: <= 10% deviation

**Measurement**:
```python
for each confidence band:
    expected_accuracy = midpoint of band (e.g., 0.85 for 0.80-0.90)
    actual_accuracy = success_count / (success_count + failure_count)
    deviation = abs(expected_accuracy - actual_accuracy)

mean_deviation = average(all deviations)
```

**Success Criterion**: mean_deviation <= 0.10

### Secondary Metrics

**4. User Review Burden**

**Definition**: Percentage of lessons requiring manual review

**Target**: <= 30% need review (inverse of immediate learning rate)

**Measurement**: count(lessons with status "needs_validation") / total_lessons

**5. Self-Correction Rate**

**Definition**: Percentage of bad lessons that auto-deprecate (vs requiring user intervention)

**Target**: >= 80% auto-deprecated

**Measurement**: count(deprecated_automatic == true) / count(all deprecated)

**6. Lesson Refinement Activity**

**Definition**: Average number of confidence updates per lesson

**Target**: >= 2.0 updates per lesson (shows active refinement)

**Measurement**: sum(all outcome_history lengths) / count(lessons)

---

## For Design Bridge

**Pass forward to Implementation**:
- ADR documents (all 4 ADRs with research citations)
- Technical specification (complete data model, hook changes, CLI commands)
- Implementation plan (6 phases with timelines and risks)
- Security considerations (4 risks with mitigations)
- Testing strategy (unit, integration, performance, manual scenarios)
- Migration plan (backward-compatible, phased rollout)
- Success metrics (3 primary, 3 secondary with measurement formulas)

**Key decisions preserved**:
- Immediate learning based on confidence thresholds (research-informed)
- Bayesian confidence updating with outcome monitoring
- Self-correction through automatic deprecation
- Optional validation workflow (not required approval)

**Implementation can start with**:
- Phase 1: Add new fields (non-breaking migration)
- Reference: Bayesian updating formulas, RLHF patterns
- Validation: Test confidence calculation with unit tests

---

