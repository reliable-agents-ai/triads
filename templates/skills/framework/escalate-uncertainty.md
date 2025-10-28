---
name: escalate-uncertainty
description: Handle uncertainty escalation protocol when confidence drops below 90 percent threshold. Use when uncertain about next steps, unclear requirements, ambiguous instructions, low confidence in decision, don't know how to proceed, need clarification from user, uncertain outcome, unclear path forward, ambiguous problem statement, unsure about approach, need guidance, uncertainty threshold exceeded, confidence below threshold, escalation needed, request user input, ask for clarification, uncertainty node creation, document uncertainty, unclear expectations, ambiguous task, need user decision, uncertain requirements, unclear objectives, low confidence situation, escalate to user, uncertainty protocol, unclear next action, ambiguous direction, need confirmation, unsure about solution, require user guidance, escalation procedure, uncertainty management, handle uncertainty, manage ambiguity, resolve uncertainty, clarification needed, user input required, decision needed, guidance required, unclear context, ambiguous scope.
category: framework
generated_by: triads-generator-template
---

# Escalate Uncertainty

## Purpose

Handle the uncertainty escalation protocol when confidence in any decision, knowledge, or action drops below 90%. This skill enforces the constitutional principle of Uncertainty Escalation by ensuring agents never guess when uncertain.

## Keywords for Discovery

uncertainty, uncertain, escalate, escalation, unclear, ambiguous, don't know, unsure, low confidence, need clarification, need guidance, need user input, ask user, request clarification, uncertainty threshold, confidence below 90, confidence below threshold, unclear requirements, ambiguous instructions, unclear next steps, unsure how to proceed, unclear path, ambiguous problem, need confirmation, unclear expectations, uncertain outcome, unclear objectives, ambiguous task, uncertain approach, need decision, require guidance, uncertainty protocol, escalation protocol, handle uncertainty, manage uncertainty, resolve uncertainty, clarification needed, user input needed, decision required, guidance needed, unclear context, ambiguous scope, uncertain direction, unclear solution, need user decision, escalate to user, uncertainty node, document uncertainty, uncertainty management, confidence check, threshold check, low confidence alert

## When to Invoke This Skill

Invoke this skill when:
- Confidence in any decision < 90%
- Requirements are ambiguous or unclear
- Multiple valid approaches exist (unclear which to choose)
- Instructions conflict or are contradictory
- Expected outcome is uncertain
- Next steps are unclear
- User intent is ambiguous
- Information is missing or incomplete
- Assumptions cannot be validated
- High-risk decision requires user confirmation
- Agent doesn't know how to proceed
- Options have equal merit (tie-breaker needed)
- Clarification needed before continuing
- Path forward is not obvious
- Decision has significant consequences

## Skill Procedure

### Step 1: Detect Uncertainty Threshold Violation

Monitor confidence levels throughout agent execution:

```python
def check_confidence_threshold(confidence):
    """Check if confidence meets constitutional requirement."""
    UNCERTAINTY_THRESHOLD = 0.90  # 90%

    if confidence < UNCERTAINTY_THRESHOLD:
        return {
            "threshold_exceeded": True,
            "confidence": confidence,
            "gap": UNCERTAINTY_THRESHOLD - confidence,
            "action": "ESCALATE_IMMEDIATELY"
        }
    else:
        return {
            "threshold_exceeded": False,
            "confidence": confidence,
            "action": "PROCEED"
        }
```

**Confidence Levels**:
- **≥95%**: Proceed with full confidence
- **90-94%**: Proceed with explicit disclosure of confidence level
- **85-89%**: ⚠️ Caution zone - document assumptions, provide reasoning
- **<85%**: ❌ STOP - Uncertainty escalation REQUIRED

### Step 2: Identify Uncertainty Source

Categorize the type of uncertainty:

**Type 1: Requirement Uncertainty**
```markdown
Problem: User request is ambiguous
Example: "Make the system better"
Uncertainty: What aspect? Performance? UX? Security?
Confidence: 60%
```

**Type 2: Technical Uncertainty**
```markdown
Problem: Multiple valid technical approaches
Example: "Which database?" (PostgreSQL vs MySQL vs MongoDB)
Uncertainty: No clear winner, trade-offs exist
Confidence: 70%
```

**Type 3: Decision Uncertainty**
```markdown
Problem: Insufficient information for decision
Example: "Should we refactor now or later?"
Uncertainty: Don't know priorities, timeline constraints
Confidence: 50%
```

**Type 4: Path Uncertainty**
```markdown
Problem: Unclear how to achieve goal
Example: "Fix the performance issue"
Uncertainty: Root cause not identified
Confidence: 65%
```

**Type 5: Scope Uncertainty**
```markdown
Problem: Boundaries not defined
Example: "Update the documentation"
Uncertainty: Which docs? How much detail?
Confidence: 75%
```

### Step 3: Document Uncertainty in Knowledge Graph

Create an Uncertainty node to track the issue:

```markdown
[GRAPH_UPDATE]
type: add_node
node_id: uncertainty_{unique_id}_{timestamp}
node_type: Uncertainty
label: {Brief description of uncertainty}
description: {Detailed explanation}
confidence: {current_confidence}
threshold_violated: 0.90
gap: {0.90 - current_confidence}
uncertainty_type: {requirement|technical|decision|path|scope}
context: {What was being attempted}
options_considered: [{list of alternatives}]
information_needed: {What would resolve uncertainty}
impact: {Consequences if wrong decision made}
escalated_at: {timestamp}
escalated_by: {agent_name}
status: pending_user_response
[/GRAPH_UPDATE]
```

### Step 4: Format Escalation Message

```markdown
❌ UNCERTAINTY THRESHOLD EXCEEDED

**Current Task**: {what you were trying to accomplish}

**Confidence Level**: {percentage}% (threshold: ≥90%)
**Uncertainty Gap**: {gap}%

**Uncertainty Type**: {type}

**Context**:
{Explain what led to this uncertainty}

**The Problem**:
{Clear statement of what is unclear/ambiguous}

**Options Considered**:
1. **Option A**: {description}
   - Pros: {advantages}
   - Cons: {disadvantages}
   - Confidence if chosen: {percentage}%

2. **Option B**: {description}
   - Pros: {advantages}
   - Cons: {disadvantages}
   - Confidence if chosen: {percentage}%

[3. Option C if applicable...]

**Information Needed to Proceed**:
{Specific questions that would resolve uncertainty}

**Impact if Wrong**:
- Best case: {minor negative outcome}
- Worst case: {major negative outcome}

**Request**: {Specific question or decision needed from user}

**I cannot proceed until this uncertainty is resolved.**
```

### Step 5: Present to User

Use clear, actionable format:

```markdown
## ⚠️ Escalation Required

I need your guidance to proceed. My confidence in the next step is {X}%, which is below the constitutional threshold of 90%.

**What I'm trying to do**:
{Goal in plain language}

**What's unclear**:
{The ambiguity/uncertainty}

**Options I've considered**:

### Option 1: {Name}
{Description}
- **Pros**: {benefit 1}, {benefit 2}
- **Cons**: {drawback 1}, {drawback 2}
- **When to choose**: {scenario}

### Option 2: {Name}
{Description}
- **Pros**: {benefit 1}, {benefit 2}
- **Cons**: {drawback 1}, {drawback 2}
- **When to choose**: {scenario}

**My recommendation** (if any): {Option X because...}
**My confidence in recommendation**: {percentage}%

**Question for you**: {Specific, answerable question}

---

Which option should I pursue, or is there a different approach you'd prefer?
```

### Step 6: Await Resolution

```markdown
## Resolution Tracking

**Status**: ⏸️ Paused - Awaiting user response

**What happens next**:
1. User provides clarification/decision
2. Update uncertainty node with resolution
3. Document decision rationale
4. Resume work with ≥90% confidence

**Uncertainty Node ID**: uncertainty_{id}
**Escalated**: {timestamp}
**Expected Resolution**: When user responds
```

### Step 7: Document Resolution

Once user responds:

```markdown
[GRAPH_UPDATE]
type: update_node
node_id: uncertainty_{id}
status: resolved
resolution: {user's decision}
resolved_at: {timestamp}
resolved_by: user
new_confidence: {updated_confidence}
rationale: {why this resolves uncertainty}
next_steps: {what to do now}
[/GRAPH_UPDATE]
```

## Output Format

```markdown
❌ UNCERTAINTY THRESHOLD EXCEEDED

**Confidence**: {XX}% (required: ≥90%)
**Uncertainty Type**: {requirement|technical|decision|path|scope}

---

**Task**: {what you were attempting}

**Problem**: {what is unclear}

**Options Considered**:
1. {Option A} - Confidence if chosen: {XX}%
2. {Option B} - Confidence if chosen: {XX}%

**Information Needed**:
{Specific questions}

**Impact if Wrong**:
- Best case: {minor impact}
- Worst case: {major impact}

---

**REQUEST**: {Specific question for user}

⏸️ Work paused until uncertainty resolved.

**Uncertainty Node**: uncertainty_{id} created in knowledge graph
```

## Example Usage

**Scenario 1: Ambiguous Requirements**

**Agent internal state**:
```
Task: "Improve the API"
Confidence: 65%
Reason: "Improve" is vague - performance? Security? Documentation?
```

**Skill Invocation**:
```markdown
❌ UNCERTAINTY THRESHOLD EXCEEDED

**Confidence**: 65% (required: ≥90%)
**Uncertainty Type**: Requirement Uncertainty

---

**Task**: Improve the API

**Problem**: The term "improve" is ambiguous. There are multiple aspects of the API that could be improved, each requiring different approaches and effort levels.

**Options Considered**:

1. **Performance Optimization**
   - Add caching layer
   - Optimize database queries
   - Add pagination to large result sets
   - Confidence if chosen: 85%

2. **Security Hardening**
   - Add rate limiting
   - Implement input validation
   - Add authentication to public endpoints
   - Confidence if chosen: 80%

3. **Documentation Enhancement**
   - Add OpenAPI/Swagger spec
   - Write usage examples
   - Document all error codes
   - Confidence if chosen: 90%

4. **Developer Experience**
   - Add SDK in multiple languages
   - Improve error messages
   - Add request/response examples
   - Confidence if chosen: 75%

**Information Needed**:
- What specific problem are users experiencing with the current API?
- Which improvement would provide the most value?
- What is the priority: speed, security, usability, or documentation?

**Impact if Wrong**:
- Best case: Deliver improvement, but not the most needed one
- Worst case: Spend 2 weeks on wrong improvement, actual problem persists

---

**REQUEST**: Which aspect of the API should I focus on improving?

⏸️ Work paused until uncertainty resolved.

**Uncertainty Node**: uncertainty_api_improvement_20241027 created
```

**User Response**:
```
Users are complaining about slow response times on the /users endpoint. Focus on performance optimization.
```

**Resolution**:
```markdown
✅ Uncertainty Resolved

**User Decision**: Performance optimization for /users endpoint
**Updated Confidence**: 95%

**Rationale**:
- Clear, specific target: /users endpoint
- Measurable goal: improve response time
- User-driven priority: complaints about slowness

**Next Steps**:
1. Profile /users endpoint to identify bottleneck
2. Implement optimization (likely N+1 query issue)
3. Measure improvement with benchmarks

Proceeding with performance optimization...

[GRAPH_UPDATE]
type: update_node
node_id: uncertainty_api_improvement_20241027
status: resolved
resolution: "Performance optimization for /users endpoint"
resolved_at: 2024-10-27T22:15:00Z
resolved_by: user
new_confidence: 0.95
next_steps: "Profile endpoint, optimize queries, benchmark"
[/GRAPH_UPDATE]
```

---

**Scenario 2: Technical Decision with Trade-offs**

**Agent internal state**:
```
Task: Choose database for new feature
Confidence: 70%
Reason: PostgreSQL and MySQL both viable, equal trade-offs
```

**Skill Invocation**:
```markdown
❌ UNCERTAINTY THRESHOLD EXCEEDED

**Confidence**: 70% (required: ≥90%)
**Uncertainty Type**: Technical Uncertainty

---

**Task**: Select database for user notification feature

**Problem**: Both PostgreSQL and MySQL meet requirements. Trade-offs are balanced, no clear winner without knowing your priorities.

**Options Considered**:

1. **PostgreSQL**
   - Pros:
     - Team expertise (80% know PostgreSQL)
     - Already in production stack
     - Better JSON support for flexible notification schema
     - Strong ACID guarantees
   - Cons:
     - Slightly more resource-intensive
     - More complex than MySQL
   - Confidence if chosen: 85%

2. **MySQL**
   - Pros:
     - Simpler, easier to maintain
     - Lighter resource usage
     - Faster for simple queries
   - Cons:
     - Only 20% of team knows MySQL
     - Not currently in stack (new dependency)
     - Weaker JSON support
   - Confidence if chosen: 70%

**Information Needed**:
- Is team expertise a priority? (favors PostgreSQL)
- Is resource efficiency critical? (favors MySQL)
- Do we want to add a new database to our stack?

**Impact if Wrong**:
- Best case: Both work, but suboptimal team velocity
- Worst case: Team struggles with unfamiliar database, migration needed later

---

**REQUEST**: Should I prioritize team expertise (PostgreSQL) or resource efficiency (MySQL)? Or is there another factor I should consider?

⏸️ Work paused until uncertainty resolved.

**Uncertainty Node**: uncertainty_database_choice_20241027 created
```

## Integration with Constitutional Principles

**Uncertainty Escalation** (direct enforcement):
- Detects confidence < 90%
- Immediately stops execution
- Escalates to user with clear options
- Resumes only after resolution

**Evidence-Based Claims**:
- Documents uncertainty with specific confidence score
- Provides evidence for why confidence is low
- Lists concrete options with pros/cons

**Complete Transparency**:
- Shows all options considered
- Explains why each option scored as it did
- States impact if wrong decision made
- Documents full reasoning chain

**Assumption Auditing**:
- Identifies unvalidated assumptions causing uncertainty
- Makes assumptions explicit in escalation message
- Requests validation from user

**Multi-Method Verification**:
- Would use multiple methods if confidence were higher
- Escalates when methods conflict or are insufficient

---

**This skill is critical for maintaining constitutional integrity. Use it whenever confidence drops below 90%. Never guess when uncertain.**
