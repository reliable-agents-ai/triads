# Memory Template Integration Strategy

**User-Level Personalization Compatible with Constitutional Enforcement**

**Version**: 1.0
**Date**: 2025-10-27
**Purpose**: Design how to incorporate Claude Memory Template pattern into triads generation while maintaining constitutional principles

---

## Table of Contents

1. [Overview](#1-overview)
2. [Two-Layer Personalization System](#2-two-layer-personalization-system)
3. [Memory Template Framework](#3-memory-template-framework)
4. [Integration Architecture](#4-integration-architecture)
5. [Component Generation Requirements](#5-component-generation-requirements)
6. [SessionStart Hook Enhancement](#6-sessionstart-hook-enhancement)
7. [Workflow-Specific Templates](#7-workflow-specific-templates)
8. [User Experience](#8-user-experience)
9. [Generation Process](#9-generation-process)

---

## 1. Overview

### The Claude Memory Template Pattern

**Source**: Claude's recommended memory template for optimal AI interaction

**Purpose**: Allow users to define personal preferences, communication style, technical context, and decision-making values

**Key Insight**: Memory templates define **HOW** to work (style, preferences), while constitutional principles define **WHAT** standards to meet (quality, evidence, verification)

**These are COMPLEMENTARY, not conflicting.**

---

### Integration Goal

Create a personalization layer that:
- ✅ Allows user customization of style, tone, domain context
- ✅ Works alongside constitutional principles (doesn't conflict)
- ✅ Auto-loads at session start
- ✅ Supports workflow-specific customization
- ✅ Maintains quality guarantees (evidence, verification, transparency)

---

## 2. Two-Layer Personalization System

### Architecture

```
┌────────────────────────────────────────────────────────────────┐
│ Layer 1: USER PERSONALIZATION (Memory Template)                │
│ - User's identity, preferences, domain                         │
│ - Communication style (tone, voice, length)                    │
│ - Technical stack (languages, frameworks, tools)               │
│ - Individual work patterns                                     │
│ - Decision-making values                                       │
│ - Output format preferences                                    │
└──────────────┬─────────────────────────────────────────────────┘
               │
               ↓ (compatible with, enhances)
┌────────────────────────────────────────────────────────────────┐
│ Layer 2: CONSTITUTIONAL ENFORCEMENT (Triads)                   │
│ - Evidence-based claims (cite all sources)                     │
│ - Uncertainty escalation (confidence <90% = stop)              │
│ - Multi-method verification (≥2 independent sources)           │
│ - Assumption auditing (validate all assumptions)               │
│ - Complete transparency (show all reasoning)                   │
└────────────────────────────────────────────────────────────────┘
```

---

### Layer Responsibilities

#### Layer 1: User Personalization (What You Control)

**Controls**:
- ✅ Communication tone and style
- ✅ Level of detail in explanations
- ✅ Technical stack references
- ✅ Domain-specific terminology
- ✅ Personal decision-making hierarchy
- ✅ Output structure preferences
- ✅ Learning/adaptation patterns

**Does NOT Control**:
- ❌ Evidence requirements (constitutional)
- ❌ Confidence thresholds (constitutional)
- ❌ Verification standards (constitutional)
- ❌ Quality gates (constitutional)

---

#### Layer 2: Constitutional Enforcement (What Triads Control)

**Controls**:
- ✅ Evidence quality (must cite sources)
- ✅ Confidence thresholds (≥85% or escalate)
- ✅ Verification methods (≥2 independent)
- ✅ Reasoning transparency (show all work)
- ✅ Assumption validation (verify all assumptions)
- ✅ Quality gates (validate at triad boundaries)

**Does NOT Control**:
- ❌ Communication style (user preference)
- ❌ Tone and voice (user preference)
- ❌ Technical stack choices (user preference)
- ❌ Domain terminology (user preference)

---

### Example: How Layers Work Together

**Scenario**: User asks "Design an authentication system"

**User's Memory Template Says**:
- "I prefer direct, concise responses"
- "My stack is Python + FastAPI"
- "Prioritize security over features"
- "Medium-depth explanations"

**Constitutional Principles Enforce**:
- "Cite evidence for authentication patterns"
- "Show alternatives considered (OAuth2, JWT, Session)"
- "Confidence ≥85% or escalate uncertainty"
- "Security review (OWASP checks, threat model)"
- "Minimum 2 verification sources"

**Result**:
```markdown
## Authentication System Design

### Recommendation: JWT-based Authentication

**Evidence**:
- FastAPI JWT patterns: https://fastapi.tiangolo.com/tutorial/security/
- OWASP best practices: https://owasp.org/www-project-top-ten/
- Verified in production: internal-docs/auth-patterns.md:45

**Alternatives Considered**:
1. Session-based: Rejected (stateful, scaling issues)
2. OAuth2: Rejected (overkill for internal API)
3. JWT: Selected (stateless, FastAPI native support)

**Security Review**:
- ✅ HTTPS only (no token leakage)
- ✅ Short expiry (15 min access, 7 day refresh)
- ✅ Secure storage (httpOnly cookies)
- ⚠️ CSRF protection needed (verify with security team)

**Confidence**: 90% (strong evidence, proven pattern, one uncertainty)

**Implementation**:
[Python + FastAPI code example - concise, direct]
```

**Analysis**:
- ✅ **Direct, concise** (user preference)
- ✅ **Python + FastAPI** (user stack)
- ✅ **Security prioritized** (user value)
- ✅ **Medium-depth** (user preference)
- ⚖️ **Evidence cited** (constitutional)
- ⚖️ **Alternatives shown** (constitutional)
- ⚖️ **Confidence score** (constitutional)
- ⚖️ **Security review** (constitutional)
- ⚖️ **Uncertainty escalated** (CSRF - 90% confidence, flagged)

**Both layers active, no conflicts.**

---

## 3. Memory Template Framework

### 7-Section Template Structure

Based on Claude's recommended memory template pattern:

#### Section 1: Core Identity and Objective

**Purpose**: Define user's role, domain, and primary focus

**Contents**:
- User's professional role
- Primary projects or domains
- Workflow positioning (technical builder, strategist, researcher)
- Integration with triads workflow system

**Example**:
```markdown
## 1. Core Identity and Objective

I am a full-stack developer using the **Triads Workflow System** for:

- Feature development for SaaS platform (Python + React)
- API design and implementation
- Constitutional TDD development with evidence-based knowledge management

**Workflow Focus**: Implementation and Garden Tending (code quality)
```

---

#### Section 2: Communication and Tone

**Purpose**: Define style, voice, structure preferences

**Contents**:
- Voice and tone (direct, conversational, formal)
- Structure preferences (headings, checklists, paragraphs)
- Clarity standards
- Length preferences (concise, medium, comprehensive)

**Triads Integration**:
- **No hyperbole** (constitutional standard)
- **Evidence-based** (cite sources)
- **Transparent reasoning** (show complete chains)

**Example**:
```markdown
## 2. Communication and Tone

**Style Requirements**:

- **Clarity over cleverness** - Direct, unambiguous language
- **Evidence-based** - Cite sources for all claims (file:line or URL)
- **Transparent reasoning** - Show complete reasoning chains
- **No hyperbole** - Objective assessment (no "amazing", "incredible")
- **Structured output** - Use headings, checklists, clear sections

**Voice**: Professional, peer-level (not explaining basics)

**Length Preference**: Medium-depth (~200-300 words per section)
```

---

#### Section 3: Reasoning Framework

**Purpose**: Problem-solving approach and decision-making process

**Contents**:
- Goal-driven planning structure
- State assessment methods
- Action decomposition approach
- Path planning strategy
- Adaptive execution patterns
- Reflection loop

**Triads Integration**:
- **Constitutional decision-making** (evidence, verification, confidence)
- **Knowledge graph consultation** (check graphs first)
- **Uncertainty escalation** (confidence <90% = stop)
- **TDD methodology** (tests before code)

**Example**:
```markdown
## 3. Reasoning Framework

**Constitutional Problem-Solving Approach**:

When approaching problems in triads system:

1. **Evidence Gathering**
   - Consult knowledge graphs first (`.claude/graphs/*.json`)
   - Gather minimum 2 independent sources
   - Verify assumptions before proceeding
   - Confidence assessment (0.0-1.0 scale)

2. **Constitutional Decision-Making**
   - State current vs. target state explicitly
   - Document all assumptions with validation
   - Show alternatives considered (minimum 2-3)
   - Cite evidence for each decision
   - If confidence <90%: STOP and escalate

3. **Action Execution**
   - Follow RED-GREEN-BLUE TDD cycle (tests before code)
   - Use quality gate skills at phase boundaries
   - Update knowledge graphs with findings
   - Maintain complete transparency

4. **Verification Loop**
   - Minimum 2 verification methods
   - Cross-validate results
   - Document in knowledge graph
   - Run quality checks before committing
```

---

#### Section 4: Technical/Domain Context

**Purpose**: Stack, tools, architecture preferences, constraints

**Contents**:
- Primary languages and tools
- Key frameworks
- Architecture preferences
- Important principles
- Projects worked on
- Domain-specific constraints (performance, scale, compliance)

**Triads Integration**:
- **Quality standards** (coverage ≥80%, security, documentation)
- **Tool preferences** aligned with triad workflows

**Example**:
```markdown
## 4. Technical/Domain Context

**My Stack**:

- Primary languages: Python, TypeScript
- Frameworks: FastAPI, React, PostgreSQL
- Tools: git, pytest, black, mypy, eslint
- Architecture: Modular monolith with service boundaries

**Triads Configuration**:

- Workflow focus: Feature development + refactoring
- Team size: Solo developer with occasional collaboration
- Project scale: Production SaaS platform

**Quality Standards**:

- Test coverage: ≥80% minimum
- Code quality: DRY, functions <20 lines, clear naming
- Security: OWASP Top 10 compliance, no secrets in code
- Documentation: README, CHANGELOG, inline comments for complex logic
```

---

#### Section 5: Philosophical and Value Lens

**Purpose**: Decision framework, trade-off hierarchy, values

**Contents**:
- Decision framework principles
- Trade-off hierarchy (priority order when conflicts arise)
- Core values
- Balance considerations

**Triads Integration**:
- **Constitutional principles** always #1 priority (non-negotiable)
- User values follow constitutional baseline

**Example**:
```markdown
## 5. Philosophical and Value Lens

**Decision Framework**:

When conflicts arise, prioritize in this order:

1. **Constitutional principles** (non-negotiable)
   - Evidence-based claims
   - Confidence ≥85% or escalate
   - Multi-method verification
   - Complete transparency
   - Assumption auditing

2. **Security** (primary value)
   - OWASP compliance
   - Defense in depth
   - No secrets in code

3. **User experience** (secondary value)
   - Performance (<200ms API response)
   - Clear error messages
   - Accessibility

4. **Development speed** (tertiary value)
   - After security and UX are satisfied
   - Simple solutions preferred

**Trade-off Philosophy**:

- **Thoroughness over speed** (constitutional)
- **Working software over perfect code** (but maintain quality gates)
- **Simple solutions over complex** (unless complexity justified by evidence)
```

---

#### Section 6: Output Standards

**Purpose**: Response format, quality expectations, completion criteria

**Contents**:
- Response structure requirements
- Technical solution standards
- Failure mode handling
- Resource cost expectations

**Triads Integration**:
- **Constitutional self-checks** (cite sources, show confidence, verify assumptions)
- **TDD standards** (tests before code)
- **Quality gates** (coverage, security, documentation)

**Example**:
```markdown
## 6. Output Standards

**When responding**:

- ✅ Cite sources (file:line or URL)
- ✅ Show confidence scores (0.0-1.0)
- ✅ Document assumptions explicitly
- ✅ Provide verification methods (≥2)
- ✅ Include reasoning chains
- ✅ Use constitutional self-checks

**For code changes**:

- ✅ Tests BEFORE implementation (TDD)
- ✅ Coverage ≥80% minimum
- ✅ Security review (no secrets, input validation, OWASP checks)
- ✅ Quality checks (DRY, clear naming, <20 line functions)
- ✅ Documentation (README updates, CHANGELOG entries)

**For research/design**:

- ✅ Minimum 2 independent sources
- ✅ Alternatives considered and documented (≥2-3 options)
- ✅ Evidence quality HIGH
- ✅ Confidence ≥85% or uncertainty escalated

**For knowledge additions**:

- ✅ Evidence cited (file:line or URL)
- ✅ Confidence ≥85%
- ✅ Minimum 2 verification methods
- ✅ Provenance (created_by, created_at, source)
```

---

#### Section 7: Learning and Adaptation

**Purpose**: Knowledge management patterns, continuous improvement

**Contents**:
- Knowledge management strategy
- Pattern extraction approach
- Continuous improvement methods
- Gap identification

**Triads Integration**:
- **Knowledge graphs** as primary memory layer
- **Confidence evolution** (update as new evidence emerges)
- **Pattern extraction** (build on previous findings)

**Example**:
```markdown
## 7. Learning and Adaptation

**Knowledge Management**:

- **Knowledge graphs** are the primary memory layer
- Extract patterns from specific problems
- Build on previous findings (check graphs first via Read tool)
- Update confidence as new evidence emerges
- Mark outdated knowledge as deprecated (don't delete - preserve history)

**Continuous Improvement**:

- Identify gaps proactively (what's missing from knowledge graphs?)
- Challenge assumptions from prior sessions (re-verify, don't inherit blindly)
- Refine mental models based on outcomes (reflection after each triad)
- Track recurring issues for systemic fixes (patterns suggest deeper problems)

**Uncertainty Tracking**:

- Maintain Uncertainty nodes in knowledge graph
- Revisit uncertainties as new information emerges
- Convert uncertainties to knowledge when confidence ≥85%
- Escalate persistent uncertainties (may need user input)
```

---

## 4. Integration Architecture

### How Memory Templates Load

```
Session Start
  ↓
hooks/on_session_start.py fires
  ↓
Step 1: Load default memory template
  ├─ Check: .claude/memory-template.md exists?
  ├─ If yes: Load and inject
  └─ If no: Skip (user hasn't customized)
  ↓
Step 2: Load workflow-specific template
  ├─ Detect: Active workflow (from supervisor state)
  ├─ Check: .claude/memory-templates/{workflow-name}.md exists?
  ├─ If yes: Load and inject (overrides default for this workflow)
  └─ If no: Use default only
  ↓
Step 3: Inject constitutional reminder
  ├─ Always inject (non-negotiable)
  └─ Clarify relationship: Memory template + Constitutional principles
  ↓
Result: Personalized + Constitutionally-Enforced Session
```

---

### File Structure

```
.claude/
├── memory-template.md                     # Default user personalization
├── memory-templates/                      # Workflow-specific overrides
│   ├── idea-validation.md                 # Research-focused reasoning
│   ├── design.md                          # Architecture-focused reasoning
│   ├── implementation.md                  # TDD-focused reasoning
│   ├── garden-tending.md                  # Refactoring-focused reasoning
│   └── deployment.md                      # Release-focused reasoning
├── output-styles/
│   └── constitutional.md                  # Constitutional TDD style (Main Claude only)
├── agents/
│   └── {triad}/
│       └── {agent}.md                     # Agents with embedded constitutional sections
├── skills/
│   ├── validate-knowledge.md              # Quality gates
│   ├── validate-research.md
│   ├── validate-implementation.md
│   └── ...
└── hooks/
    ├── on_session_start.py                # Memory template injection (ENHANCED)
    ├── on_pre_experience_injection.py     # Constitutional reminders
    └── on_stop.py                         # Compliance validation
```

---

### SessionStart Hook Enhancement

**File**: `hooks/on_session_start.py`

**Current State**: Basic session initialization

**Enhancement**: Memory template injection

```python
from pathlib import Path
import json

def load_memory_template():
    """Load default user memory template"""
    template_path = Path(".claude/memory-template.md")

    if template_path.exists():
        return template_path.read_text()

    return None


def load_workflow_memory_template(workflow_name):
    """Load workflow-specific memory template"""
    template_path = Path(f".claude/memory-templates/{workflow_name}.md")

    if template_path.exists():
        return template_path.read_text()

    return None


def get_active_workflow():
    """Detect active workflow from supervisor state"""
    # Check supervisor state file
    state_path = Path(".claude/state/supervisor.json")

    if state_path.exists():
        state = json.loads(state_path.read_text())
        return state.get("active_workflow")

    return None


def on_session_start():
    """
    Enhanced session start with memory template injection

    Loads:
    1. Default user memory template (.claude/memory-template.md)
    2. Workflow-specific template if active workflow exists
    3. Constitutional principles reminder

    Returns injection content for Main Claude context
    """

    components = []

    # 1. Load default user memory template
    memory_template = load_memory_template()
    if memory_template:
        components.append(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 USER MEMORY TEMPLATE LOADED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{memory_template}

This template defines YOUR preferences, style, and domain context.
Constitutional principles (evidence, verification, transparency) remain mandatory.
        """)

    # 2. Load workflow-specific template if active workflow
    active_workflow = get_active_workflow()
    if active_workflow:
        workflow_template = load_workflow_memory_template(active_workflow)
        if workflow_template:
            components.append(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔄 WORKFLOW-SPECIFIC TEMPLATE: {active_workflow}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{workflow_template}

This template provides reasoning framework and output standards specific
to the {active_workflow} workflow. It works alongside your default preferences.
            """)

    # 3. Constitutional reminder (ALWAYS inject)
    components.append("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚖️ CONSTITUTIONAL PRINCIPLES ACTIVE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The following principles are enforced across all agents, skills, and hooks:

1. **Evidence-Based Claims**: Cite all sources (file:line or URL)
2. **Uncertainty Escalation**: If confidence <90%, STOP and escalate
3. **Multi-Method Verification**: Use ≥2 independent sources
4. **Complete Transparency**: Show all reasoning chains
5. **Assumption Auditing**: Validate all assumptions

These work alongside your personal preferences above.

**Relationship**:
- Memory Template = HOW you work (style, tone, preferences)
- Constitutional Principles = WHAT standards to meet (quality, evidence, verification)

Both layers are active simultaneously and compatible.
    """)

    return "\n\n".join(components)
```

---

## 5. Component Generation Requirements

### What the Generator MUST Create

When generating a triad system, the generator MUST create memory template infrastructure:

---

#### 1. Default Memory Template (REQUIRED)

**File**: `.claude/memory-template.md`

**Status**: GENERATE THIS

**Contents**: 7-section template with triads-aware defaults

**Template**:

```markdown
# Claude Memory Template - Triads Workflow System

**Copy-Paste Instructions**: Fill in bracketed sections with your specifics, then restart session to activate.

---

## 1. Core Identity and Objective

I am [Your Role] using the **Triads Workflow System** for:

- [Primary project/domain]
- [Secondary project/domain]
- Constitutional TDD development with evidence-based knowledge management

**Workflow Focus**: [Idea Validation / Design / Implementation / Garden Tending / Deployment]

---

## 2. Communication and Tone

**Style Requirements**:

- **Clarity over cleverness** - Direct, unambiguous language
- **Evidence-based** - Cite sources for all claims (file:line or URL)
- **Transparent reasoning** - Show complete reasoning chains
- **No hyperbole** - Objective assessment (no "amazing", "incredible")
- **Structured output** - Use headings, checklists, clear sections

**Voice**: [Professional / Technical / Conversational / Formal]

**Length Preference**: [Concise / Medium-depth / Comprehensive]

---

## 3. Reasoning Framework

**Constitutional Problem-Solving Approach**:

When approaching problems in triads system:

1. **Evidence Gathering**
   - Consult knowledge graphs first (`.claude/graphs/*.json`)
   - Gather minimum 2 independent sources
   - Verify assumptions before proceeding
   - Confidence assessment (0.0-1.0 scale)

2. **Constitutional Decision-Making**
   - State current vs. target state explicitly
   - Document all assumptions with validation
   - Show alternatives considered (minimum 2-3)
   - Cite evidence for each decision
   - If confidence <90%: STOP and escalate

3. **Action Execution**
   - Follow RED-GREEN-BLUE TDD cycle (tests before code)
   - Use quality gate skills at phase boundaries
   - Update knowledge graphs with findings
   - Maintain complete transparency

4. **Verification Loop**
   - Minimum 2 verification methods
   - Cross-validate results
   - Document in knowledge graph
   - Run quality checks before committing

---

## 4. Technical/Domain Context

**My Stack**:

- Primary languages: [e.g., Python, TypeScript, Rust]
- Frameworks: [e.g., FastAPI, React, Django]
- Tools: [e.g., git, pytest, black, mypy]
- Architecture: [e.g., monolithic, microservices, modular]

**Triads Configuration**:

- Workflow focus: [e.g., feature development, research, architecture]
- Team size: [solo / small team / large team]
- Project scale: [prototype / production / enterprise]

**Quality Standards**:

- Test coverage: ≥80% minimum
- Code quality: DRY, functions <20 lines, clear naming
- Security: OWASP Top 10 compliance
- Documentation: README, CHANGELOG, inline comments

---

## 5. Philosophical and Value Lens

**Decision Framework**:

When conflicts arise, prioritize in this order:

1. **Constitutional principles** (non-negotiable)
   - Evidence-based claims
   - Confidence ≥85% or escalate
   - Multi-method verification
   - Complete transparency
   - Assumption auditing

2. **[Your primary value]** (e.g., Security / User experience / Performance)

3. **[Your secondary value]** (e.g., Development speed / Cost / Maintainability)

4. **[Your tertiary value]** (e.g., Innovation / Simplicity)

**Trade-off Philosophy**:

- **Thoroughness over speed** (constitutional)
- **Working software over documentation** (but document key decisions)
- **[Your preference]** (e.g., simple solutions over complex)

---

## 6. Output Standards

**When responding**:

- ✅ Cite sources (file:line or URL)
- ✅ Show confidence scores (0.0-1.0)
- ✅ Document assumptions explicitly
- ✅ Provide verification methods (≥2)
- ✅ Include reasoning chains
- ✅ Use constitutional self-checks

**For code changes**:

- ✅ Tests BEFORE implementation (TDD)
- ✅ Coverage ≥80% minimum
- ✅ Security review (no secrets, input validation, OWASP checks)
- ✅ Quality checks (DRY, clear naming, <20 line functions)
- ✅ Documentation (README updates, CHANGELOG entries)

**For research/design**:

- ✅ Minimum 2 independent sources
- ✅ Alternatives considered and documented (≥2-3 options)
- ✅ Evidence quality HIGH
- ✅ Confidence ≥85% or uncertainty escalated

**For knowledge additions**:

- ✅ Evidence cited (file:line or URL)
- ✅ Confidence ≥85%
- ✅ Minimum 2 verification methods
- ✅ Provenance (created_by, created_at, source)

---

## 7. Learning and Adaptation

**Knowledge Management**:

- **Knowledge graphs** are the primary memory layer
- Extract patterns from specific problems
- Build on previous findings (check graphs first)
- Update confidence as new evidence emerges
- Mark outdated knowledge as deprecated

**Continuous Improvement**:

- Identify gaps proactively
- Challenge assumptions from prior sessions
- Refine mental models based on outcomes
- Track recurring issues for systemic fixes

---

## Customization Preferences

**Areas where I need more depth**:

- [Domain 1]
- [Domain 2]

**Areas where I prefer brevity**:

- [Topic 1]
- [Topic 2]

**Special preferences**:

- [Code comment style]
- [Commit message format]
- [Documentation structure]

**Frequently referenced context**:

- [Project 1: GitHub URL or local path]
- [Documentation site]
- [Team conventions doc]

---

## Integration with Triads System

This memory template works **alongside** constitutional principles enforced by triads:

- **Memory template** = Personal preferences, style, domain context
- **Constitutional principles** = Quality standards (embedded in agents, skills, hooks)

Both layers are active simultaneously and compatible.

**Activation**: This template is auto-loaded at session start via `SessionStart` hook.
```

**User Customization**:
- User fills in bracketed `[sections]` with their specifics
- Template auto-loads on session restart
- User can update anytime (takes effect next session)

---

#### 2. Workflow-Specific Templates (OPTIONAL - GENERATED PER WORKFLOW)

**Directory**: `.claude/memory-templates/`

**Status**: GENERATE ONE PER TRIAD TYPE IN WORKFLOW

**Example**: Implementation Workflow Template

**File**: `.claude/memory-templates/implementation.md`

**Contents**:

```markdown
# Memory Template - Implementation Workflow

**Workflow Type**: Implementation / Development / Coding

**When Active**: During implementation triads (senior-developer, test-engineer)

---

## Reasoning Framework for Implementation

### TDD-First Development (Constitutional Requirement)

**RED → GREEN → BLUE Cycle**:

1. **RED: Write Failing Test**
   - Write test that describes desired behavior
   - Run test to verify it fails
   - Verify failure reason is "feature not implemented" not "test is broken"
   - Document test in reasoning chain

2. **GREEN: Minimal Implementation**
   - Implement simplest code that makes test pass
   - Run specific test to verify it passes
   - Run all tests to verify no regressions
   - Document implementation with reasoning

3. **BLUE: Refactor**
   - Improve code quality without changing behavior
   - Extract long methods, remove duplication, clarify naming
   - Run all tests after each refactoring step
   - Document refactoring with reasoning

### Code Quality Standards

**Before committing**:
- [ ] Tests written BEFORE implementation
- [ ] Coverage ≥80% minimum
- [ ] Edge cases tested (empty, null, boundaries, errors)
- [ ] Code quality: DRY, <20 line functions, clear naming
- [ ] Security: Input validation, no secrets, OWASP checks
- [ ] Documentation: Comments for complex logic, README updated

**If any check fails**: FIX before committing. Quality gates are non-negotiable.

---

## Output Standards for Implementation

**Code Changes**:

Every code change must include:

1. **Tests** (written BEFORE implementation)
   ```python
   # Test file: tests/test_feature.py

   def test_feature_handles_empty_input():
       """Feature should handle empty input gracefully"""
       result = feature("")
       assert result == expected_empty_behavior
   ```

2. **Implementation** (minimal, makes tests pass)
   ```python
   # Implementation file: src/feature.py

   def feature(input_str):
       """Feature description with evidence citation"""
       # Evidence: pattern from src/similar_feature.py:45
       if not input_str:
           return default_value
       return process(input_str)
   ```

3. **Verification** (all tests pass, coverage ≥80%)
   ```bash
   $ pytest tests/test_feature.py -v
   ✅ ALL PASSED

   $ pytest --cov=src/feature
   ✅ Coverage: 85%
   ```

4. **Quality Check** (security, DRY, naming)
   ```markdown
   ✅ No secrets in code
   ✅ Input validation present
   ✅ No duplication
   ✅ Clear naming
   ✅ Functions <20 lines
   ```

---

## Verification Methods for Implementation

**Minimum 2 methods required**:

1. **Automated tests** (pytest, jest, etc.)
2. **Code review** (manual inspection for quality, security)
3. **Static analysis** (mypy, eslint, black)
4. **Coverage report** (pytest-cov, jest --coverage)

**Example**:
```markdown
## Verification

**Method 1: Automated Tests**
- Ran: pytest tests/test_feature.py
- Result: ✅ 12/12 passed
- Evidence: [test output]

**Method 2: Static Analysis**
- Ran: mypy src/feature.py
- Result: ✅ No type errors
- Evidence: [mypy output]

**Cross-Validation**: Tests pass AND types check ✅

**Confidence**: 95% (high coverage, types verified)
```

---

## Common Patterns for Implementation

**Pattern 1: Feature Flag Pattern**
- When: New feature with risk of breaking existing functionality
- Evidence: Used successfully in src/experiments/feature_flags.py:23
- Confidence: 90%

**Pattern 2: Repository Pattern**
- When: Database access layer needs abstraction
- Evidence: Existing pattern in src/repositories/base.py:15
- Confidence: 95%

**Pattern 3: Service Layer**
- When: Business logic needs separation from API handlers
- Evidence: Proven pattern in src/services/auth_service.py:34
- Confidence: 90%

Use these patterns when applicable - cite evidence from codebase.
```

---

## 6. SessionStart Hook Enhancement

**File**: `hooks/on_session_start.py`

**Status**: GENERATE THIS (enhanced version)

**See Section 4: Integration Architecture** for complete implementation.

**Key Enhancement**:
```python
def on_session_start():
    """
    Loads:
    1. Default memory template (.claude/memory-template.md)
    2. Workflow-specific template (if active workflow)
    3. Constitutional reminder (always)

    Result: Personalized + Constitutional session
    """
    # [See full implementation above]
```

---

## 7. Workflow-Specific Templates

### Template Matrix

| Workflow Type | Template File | Focus | Key Patterns |
|---------------|---------------|-------|--------------|
| **Idea Validation** | `idea-validation.md` | Research & Evidence | Multi-source verification, confidence thresholds |
| **Design** | `design.md` | Architecture & ADRs | Alternatives analysis, trade-off documentation |
| **Implementation** | `implementation.md` | TDD & Code Quality | RED-GREEN-BLUE, coverage ≥80% |
| **Garden Tending** | `garden-tending.md` | Refactoring | Safe refactoring rules, regression prevention |
| **Deployment** | `deployment.md` | Release Management | Version bumps, changelog, documentation |

---

### Generation Logic

```python
def generate_workflow_templates(workflow_yaml):
    """
    Generate workflow-specific templates based on triad composition
    """

    templates = []

    # Detect workflow types from triad sequence
    workflow_types = set()

    for triad in workflow_yaml['triad_sequence']:
        triad_type = classify_triad_type(triad['name'])
        workflow_types.add(triad_type)

    # Generate template for each unique workflow type
    for workflow_type in workflow_types:
        template_content = generate_template_for_workflow_type(workflow_type)

        template_path = f".claude/memory-templates/{workflow_type}.md"

        templates.append({
            "path": template_path,
            "content": template_content
        })

    return templates
```

---

## 8. User Experience

### Setup Flow

**Step 1: Installation**
```bash
# User installs triads plugin
claude install triads
```

**Step 2: Generation**
```bash
# User generates workflow (or plugin auto-generates)
/generate-workflow feature-development
```

**Generated Files**:
```
.claude/
├── memory-template.md                    # ← User should customize this
├── memory-templates/
│   ├── implementation.md                 # ← Auto-generated (workflow-specific)
│   └── garden-tending.md
├── output-styles/
│   └── constitutional.md
└── [... other triads components ...]
```

**Step 3: Customization**
```markdown
# User edits .claude/memory-template.md

## 1. Core Identity and Objective

I am a full-stack developer using the **Triads Workflow System** for:

- SaaS platform development (Python + React)
- API design and microservices
- Constitutional TDD development

**Workflow Focus**: Implementation and Garden Tending
```

**Step 4: Activation**
```bash
# User activates output style (optional but recommended)
/output-style constitutional

# Restart session to load memory template
# (Or just start new session - auto-loads via SessionStart hook)
```

**Step 5: Experience**

User asks: "Implement user authentication"

**Response Characteristics**:
- ✅ **Personalized**: Uses user's stack (Python + React), style preferences
- ⚖️ **Constitutional**: Cites evidence, shows alternatives, provides confidence scores
- ✅ **Workflow-Aware**: Follows implementation template (TDD, coverage, quality)

---

### Customization Flow

**User wants to change preferences**:

1. Edit `.claude/memory-template.md`
2. Update preferred sections (tone, stack, values, etc.)
3. Restart session → Changes take effect

**User wants workflow-specific customization**:

1. Edit `.claude/memory-templates/implementation.md` (or other workflow)
2. Customize reasoning framework or output standards for that workflow
3. Restart session → Workflow-specific template used when that workflow is active

---

## 9. Generation Process

### Workflow Analyst Responsibilities

**Enhanced Step 8**: Memory Template Generation

**After** finalizing triad architecture, Workflow Analyst generates:

#### 1. Default Memory Template

**File**: `.claude/memory-template.md`

**Process**:
```python
def generate_default_memory_template(workflow_context):
    """
    Generate default memory template with triads-aware defaults
    """

    template = load_template("memory-template-base.md")

    # Customize based on workflow context
    template = template.replace(
        "[Workflow Focus]",
        infer_primary_workflow_focus(workflow_context)
    )

    return template
```

---

#### 2. Workflow-Specific Templates

**Files**: `.claude/memory-templates/{workflow-type}.md`

**Process**:
```python
def generate_workflow_templates(workflow_yaml):
    """
    Generate templates for each workflow type in the triad sequence
    """

    templates = []

    for triad in workflow_yaml['triad_sequence']:
        triad_type = classify_triad_type(triad['name'])

        if triad_type == "research":
            templates.append(generate_research_template())
        elif triad_type == "implementation":
            templates.append(generate_implementation_template())
        # ... etc

    return deduplicate(templates)
```

---

#### 3. SessionStart Hook Enhancement

**File**: `hooks/on_session_start.py`

**Process**:
```python
# Generate enhanced hook that loads memory templates
def generate_session_start_hook():
    """
    Generate SessionStart hook with memory template injection
    """

    hook_content = load_template("session_start_hook.py")

    # Hook includes:
    # - load_memory_template()
    # - load_workflow_memory_template()
    # - get_active_workflow()
    # - on_session_start() [main function]

    return hook_content
```

---

### Complete Generation Checklist

When generating workflow, create:

**Memory Template Infrastructure**:
- ✅ `.claude/memory-template.md` (default user template)
- ✅ `.claude/memory-templates/{workflow-type}.md` (per workflow type)
- ✅ `hooks/on_session_start.py` (enhanced with template injection)

**Documentation**:
- ✅ `docs/MEMORY_TEMPLATE_GUIDE.md` (how to use memory templates)
- ✅ README section explaining customization

**User Instructions**:
- ✅ Notify user to customize `.claude/memory-template.md`
- ✅ Document restart required for changes to take effect
- ✅ Explain relationship: Memory Template + Constitutional Principles

---

## Summary

### What We're Adding

**1. User Personalization Layer**:
- Memory templates for style, tone, domain context
- 7-section framework (identity, communication, reasoning, technical, values, output, learning)
- Compatible with constitutional enforcement

**2. Workflow-Specific Optimization**:
- Templates per workflow type (research, design, implementation, etc.)
- Specialized reasoning frameworks
- Context-aware output standards

**3. Auto-Loading Infrastructure**:
- SessionStart hook enhancement
- Automatic template injection
- Seamless integration with constitutional principles

---

### Key Benefits

**For Users**:
- ✅ Personalized experience (style, tone, domain)
- ✅ Workflow optimization (reasoning frameworks per workflow)
- ✅ Maintained quality guarantees (constitutional enforcement)
- ✅ Easy customization (edit markdown files, restart session)

**For Triads System**:
- ✅ User adoption (customization increases satisfaction)
- ✅ Flexibility (users adapt system to their needs)
- ✅ Compatibility (no conflicts with constitutional principles)
- ✅ Scalability (workflow-specific templates support diverse domains)

---

### Integration Guarantee

**Memory Template defines**:
- Communication style and tone
- Technical stack references
- Decision-making values
- Output format preferences
- Learning patterns

**Constitutional Principles enforce**:
- Evidence quality (must cite sources)
- Confidence thresholds (≥85% or escalate)
- Verification standards (≥2 methods)
- Reasoning transparency (show all work)
- Assumption validation (verify all assumptions)

**Result**: Personalized experience with quality guarantees - both layers active, zero conflicts.
