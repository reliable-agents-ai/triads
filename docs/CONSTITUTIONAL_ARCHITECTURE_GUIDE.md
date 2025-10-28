# Constitutional Architecture Guide
**Triads Project - Claude Code Component Usage & Constitutional Enforcement**

**Version**: 1.0
**Date**: 2025-10-27
**Purpose**: Reference guide for understanding how constitutional principles are enforced across Claude Code components

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Component Overview](#2-component-overview)
3. [Constitutional Enforcement Layers](#3-constitutional-enforcement-layers)
4. [Instruction Language Standards](#4-instruction-language-standards)
5. [Component Decision Tree](#5-component-decision-tree)
6. [Component Reference](#6-component-reference)
7. [Constitutional Patterns](#7-constitutional-patterns)
8. [Implementation Checklist](#8-implementation-checklist)
9. [Examples & Use Cases](#9-examples--use-cases)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Executive Summary

### The Problem

AI agents can create low-quality knowledge if not constitutionally governed:
- Unverified claims without evidence
- Low-confidence assertions (<85%) treated as facts
- Single-source verification (needs ≥2 methods)
- Hidden assumptions not validated
- Missing reasoning chains

### The Solution

**Multi-layer constitutional architecture** using Claude Code components:

```
Output Style (Main Claude personality)
    ↓
Subagent Prompts (constitutional enforcement at source)
    ↓
Skills (workflow quality gates)
    ↓
Knowledge Integrity Triad (mandatory validation)
    ↓
Hooks (system-level interception)
```

### Key Principle

**Defense in Depth**: Multiple layers ensure constitutional compliance even if one layer fails.

---

## 2. Component Overview

### Claude Code Components Available

| Component | File Location | Scope | Invocation | Authority |
|-----------|--------------|-------|------------|-----------|
| **Output Styles** | `.claude/output-styles/` | Main Claude only | Always active | HIGHEST (system prompt) |
| **Project Instructions** | `CLAUDE.md` | All agents (if read) | Manual reading | HIGH (project rules) |
| **Subagents** | `.claude/agents/` | Individual agent | Main Claude delegates | HIGH (agent prompt) |
| **Skills** | `.claude/skills/` | Main Claude only | Model-invoked | MEDIUM (discretionary) |
| **Hooks** | `.claude/hooks/` | System-wide | Automatic | HIGHEST (system-level) |
| **Workflows** | `.claude/workflows/` | Workflow sequences | User/Supervisor trigger | MEDIUM (orchestration) |

---

## 3. Constitutional Enforcement Layers

### Layer 1: Output Style (Main Claude Behavior)

**File**: `.claude/output-styles/constitutional.md`

**What It Enforces**:
- ACCA Framework (Accurate, Clear, Complete, Actionable)
- Communication standards (No Hyperbole, No Hazing, Critical Thinking)
- Core constitutional principles (Thoroughness, Evidence, Uncertainty, Transparency, Assumption Auditing)
- RED-GREEN-BLUE TDD methodology
- Reasoning framework (State Assessment, Action Decomposition, Path Planning, Adaptive Execution, Reflection)
- Trade-off hierarchy (Correctness > Security > Maintainability > Performance > Speed)
- Git workflow discipline

**Who It Applies To**: Main Claude (the Claude Code instance responding to user)

**Authority Level**: ABSOLUTE (system prompt modification)

**When It's Active**: Always (whenever output style is selected)

**Limitations**:
- ❌ Does NOT propagate to subagents invoked via Task tool
- ❌ Does NOT affect plugin agents or external agents
- ❌ Only applies to Main Claude's responses

**Use When**:
- Defining how Main Claude communicates with user
- Establishing Main Claude's working methodology (TDD, reasoning framework)
- Setting Main Claude's personality and standards

**Configuration**:
```bash
# User selects via command
/output-style constitutional

# Or in .claude/settings.local.json
{
  "output-style": "constitutional"
}
```

---

### Layer 2: Project Instructions (Universal Principles)

**File**: `CLAUDE.md`

**What It Enforces**:
- Core operating principles (apply to ALL work)
- Triad routing rules
- Knowledge management principles
- Workflow expectations
- Team coding standards

**Who It Applies To**:
- Main Claude (always reads CLAUDE.md)
- Subagents (if explicitly instructed to read in their prompt)
- All team members working on project

**Authority Level**: HIGH (project-level mandate)

**When It's Active**: When agents read CLAUDE.md content

**Limitations**:
- ⚠️ Requires agents to explicitly read the file
- ⚠️ Not automatically enforced (depends on agent compliance)
- ⚠️ Can be accidentally ignored if agent doesn't consult

**Use When**:
- Defining principles that apply across ALL triads
- Documenting team standards and conventions
- Providing context about project structure
- Explaining workflow routing rules

**Current CLAUDE.md Structure**:
```markdown
# ⚡ CORE OPERATING PRINCIPLES
1. Thoroughness Over Speed
2. Evidence-Based Claims
3. Uncertainty Escalation
4. Complete Transparency
5. Assumption Auditing

# ⚡ TRIAD ROUTING SYSTEM
[Routing table for workflows]

# 📊 KNOWLEDGE MANAGEMENT
[Knowledge graph principles]

# 📚 DETAILED DOCUMENTATION
[Links to architecture, usage, installation docs]
```

---

### Layer 3: Subagent Prompts (Constitutional Enforcement at Source)

**Files**: `.claude/agents/{triad}/{agent-name}.md`

**What It Enforces**:
- Constitutional principles embedded in agent's system prompt
- Evidence-based claims (cite sources)
- Uncertainty escalation (stop if <90% confidence)
- Multi-method verification (≥2 verification methods)
- Complete transparency (show reasoning)
- Assumption auditing (validate all assumptions)
- Knowledge graph protocol (query before work, update after)
- Agent-specific responsibilities

**Who It Applies To**: Individual subagent (isolated context)

**Authority Level**: HIGH (agent system prompt)

**When It's Active**: When Main Claude invokes subagent via Task tool

**Limitations**:
- ✅ DOES enforce constitutional principles in agent's work
- ✅ Agent cannot bypass (encoded in system prompt)
- ⚠️ Requires prompt to include constitutional section
- ⚠️ Main Claude must still validate output (double-check)

**Use When**:
- Creating new triad agents
- Ensuring agents produce constitutionally-compliant outputs
- Embedding mandatory protocols agents must follow
- Restricting tool usage for security

**Example Structure**:
```markdown
---
name: research-analyst
triad: idea-validation
tools: WebSearch, WebFetch, Read, Grep, Glob
---

# Research Analyst

## ⚖️ CONSTITUTIONAL PRINCIPLES (MANDATORY)

[Evidence-Based Claims protocol]
[Uncertainty Escalation protocol]
[Multi-Method Verification protocol]
[Complete Transparency protocol]
[Assumption Auditing protocol]

## 🧠 Knowledge Graph Protocol

[Query before work, update after]

## Responsibilities

[Agent-specific tasks]
```

**Template**: `.claude/templates/constitutional-agent-template.md` (to be created)

---

### Layer 4: Skills (Workflow Quality Gates)

**Files**: `.claude/skills/{skill-name}/SKILL.md`

**What It Enforces**:
- Workflow-specific validation at checkpoints
- Quality gates at triad boundaries
- Validation checklists for specific outputs
- Tool restriction for security-sensitive workflows

**Who It Applies To**: Main Claude only

**Authority Level**: MEDIUM (model-invoked, discretionary)

**When It's Active**: When Main Claude determines skill is contextually relevant

**Limitations**:
- ❌ NOT mandatory (Claude decides when to use)
- ❌ Does NOT apply to subagents
- ❌ Can be skipped if model doesn't recognize context
- ⚠️ Should NOT be relied upon for critical enforcement

**Use When**:
- Providing validation checklists for Main Claude
- Creating reusable quality gate templates
- Restricting tool usage in specific workflows
- Sharing validation protocols across team (git-sharable)

**Skill Structure**:
```markdown
---
name: validate-research
description: Quality gate for idea-validation triad outputs. Use when research-analyst or community-researcher complete work to ensure evidence quality, source citations, and confidence thresholds.
allowed-tools: Read, Grep
---

# Research Validation Skill

## When to Use
After research-analyst or community-researcher completes work.

## Validation Checklist
- [ ] Sources cited (URLs, file:line)
- [ ] Evidence quality assessed
- [ ] Confidence ≥85% or escalated
- [ ] ≥2 verification methods used
- [ ] Reasoning chain complete

## Decision
✅ PASS: Proceed to next triad
❌ FAIL: Request rework with specific gaps
```

**Example Skills**:
- `validate-research` - After idea-validation triad
- `validate-design` - After design triad (ADR completeness)
- `validate-implementation` - After implementation triad (code quality)
- `validate-knowledge` - When reviewing [GRAPH_UPDATE] blocks

---

### Layer 5: Knowledge Integrity Triad (Mandatory Validation)

**Files**:
- `.claude/agents/knowledge-integrity/integrity-cultivator.md`
- `.claude/agents/knowledge-integrity/integrity-pruner.md`
- `.claude/agents/knowledge-integrity/integrity-bridge.md`
- `hooks/agent_output_validator.py`

**What It Enforces**:
- MANDATORY validation of ALL [GRAPH_UPDATE] blocks
- Constitutional compliance before knowledge graph save
- Evidence completeness (provenance required)
- Confidence threshold (≥85% required)
- Multi-method verification (≥2 methods required)
- Redundancy detection (duplicate entities)
- Contradiction detection (conflicting facts)

**Who It Applies To**: ALL agents creating knowledge graph updates

**Authority Level**: HIGHEST (hook-triggered, cannot bypass)

**When It's Active**: Automatically when [GRAPH_UPDATE] detected in any agent output

**Limitations**:
- ✅ Guaranteed activation (hook-based)
- ✅ Applies to all agents
- ✅ Blocks saves if validation fails
- ⚠️ Adds latency (multi-agent validation pipeline)

**Use When**:
- Enforcing constitutional compliance on knowledge additions
- Preventing low-quality knowledge from entering graph
- Detecting and resolving knowledge conflicts
- Maintaining knowledge graph integrity

**Flow**:
```
ANY agent creates [GRAPH_UPDATE]
  ↓
hooks/agent_output_validator.py detects block
  ↓
Hook invokes knowledge-integrity triad:
  1. integrity-cultivator: Assess quality (evidence, confidence, verification)
  2. integrity-pruner: Check redundancy (duplicates, contradictions)
  3. integrity-bridge: Approve/Reject with rationale
  ↓
If APPROVED: Save to knowledge graph
If REJECTED: Escalate to user with specific violations
```

---

### Layer 6: Hooks (System-Level Interception)

**Files**:
- `hooks/user_prompt_submit.py` (Supervisor orchestration)
- `hooks/agent_output_validator.py` (Knowledge validation)

**What It Enforces**:
- Work request detection and workflow routing
- Orchestrator instruction injection
- [GRAPH_UPDATE] detection and validation triggering
- Mandatory quality gates (cannot be bypassed)

**Who It Applies To**: Entire Claude Code session (system-level)

**Authority Level**: HIGHEST (runs before Claude sees message / after agent outputs)

**When It's Active**: Automatically on every user message / agent output

**Limitations**:
- ✅ Cannot be bypassed (system-level)
- ✅ Applies to all messages/outputs
- ⚠️ Complex to debug (runs invisibly)
- ⚠️ Performance impact if hooks are slow

**Use When**:
- Mandatory enforcement (cannot rely on agent compliance)
- System-wide interception needed
- Workflow orchestration
- Automatic quality gate triggering

**Current Hooks**:

**1. user_prompt_submit.py** (Supervisor):
```python
def process_user_message(user_message: str) -> str:
    """Detect work requests and inject orchestrator instructions"""

    # Detect work vs Q&A
    work_type = detect_work_request(user_message)

    if work_type:
        # Inject orchestrator instructions for triad execution
        return inject_orchestrator_instructions(work_type, user_message)

    # Q&A mode - no orchestration needed
    return user_message
```

**2. agent_output_validator.py** (Knowledge Governance):
```python
def validate_knowledge_additions(agent_output: str) -> str:
    """Detect [GRAPH_UPDATE] blocks and inject validation step"""

    graph_updates = detect_graph_updates(agent_output)

    if not graph_updates:
        return agent_output  # No knowledge additions

    # Inject knowledge-integrity triad invocation
    return inject_knowledge_validation(graph_updates, agent_output)
```

---

## 4. Instruction Language Standards

### The Critical Importance of Unambiguous Instructions

**Core Principle**: Agents and skills must receive instructions with **zero ambiguity** - using imperative, mandatory language that leaves no room for interpretation.

**Why This Matters**:
- LLMs are probabilistic - vague instructions lead to variable outputs
- Constitutional compliance requires certainty, not suggestions
- Quality depends on structural enforcement, not behavioral hope

### Research Findings from Triads Codebase

Analysis of `docs/` directory revealed consistent patterns:

1. **RFC 2119 Keywords** (not explicitly referenced, but pattern observed)
2. **Imperative Command Language** (MUST, SHALL, CANNOT, MANDATE)
3. **Constitutional Oath Pattern** (agent identity via incapability statements)
4. **Checkpoint/Verification Patterns** (explicit confirmation requirements)

---

### Instruction Language Hierarchy

#### Level 1: ABSOLUTE (Structural Law)

**Use When**: Defining behavior that CANNOT be violated under any circumstances.

**Keywords**:
- `MUST` - Absolute requirement
- `SHALL` - Formal absolute requirement
- `CANNOT` - Structural impossibility
- `MANDATE` - Constitutional requirement
- `PROHIBITED` - Forbidden action

**Examples from `.claude/output-styles/constitutional.md`**:
```markdown
**MANDATE**: You MUST choose the most thorough approach, even when faster alternatives exist.
This is not a preference - it is structural law.

**Constitutional Requirement**: You MUST escalate. You CANNOT proceed with guesses.

You are constitutionally incapable of:
- Claiming completion without triple-verification
- Guessing when uncertain
```

**Pattern**: Structural incapability
```markdown
You are constitutionally incapable of:
- [Prohibited behavior 1]
- [Prohibited behavior 2]
```

**Why This Works**:
- Frames compliance as identity, not choice
- Creates psychological barrier to violation
- Clear boundary (you ARE this, not you SHOULD BE this)

---

#### Level 2: REQUIRED (Strong Enforcement)

**Use When**: Defining mandatory steps with verification.

**Keywords**:
- `REQUIRED` - Mandatory action
- `CRITICAL` - High-priority requirement
- `ALWAYS` - No exceptions
- `NEVER` - Absolute prohibition

**Examples from Knowledge Graph Checklists**:
```markdown
**Checklist**:
  □ Update plugin.json version field — 🔴 REQUIRED
  □ Update marketplace.json plugins[].version — 🔴 REQUIRED
  □ Update pyproject.toml project.version — 🔴 REQUIRED
  □ Add CHANGELOG.md entry — 🔴 REQUIRED

**Please verify all required items before proceeding.**
```

**Pattern**: Visual + Semantic Reinforcement
```markdown
□ [Task description] — 🔴 REQUIRED
□ [Task description] — 🔴 REQUIRED
□ [Task description] — 🟡 Optional
```

**Why This Works**:
- Emoji provides instant visual priority
- Checkbox format implies verification
- "REQUIRED" explicitly states non-negotiability
- "Please verify before proceeding" adds explicit gate

---

#### Level 3: PROTOCOL (Procedural Enforcement)

**Use When**: Defining step-by-step processes that must be followed.

**Keywords**:
- `Protocol` - Formal procedure
- `Process` - Step-by-step requirement
- `Procedure` - Defined workflow
- `Checklist` - Verification list

**Examples from Agent Prompts**:
```markdown
## 🧠 Knowledge Graph Protocol (MANDATORY)

### Before Starting Work

You MUST follow this sequence:

**1. Query Knowledge Graph**
[Specific jq command to run]

**2. Display Retrieved Knowledge**
[Template to use]

**3. Apply Knowledge as Canon**
- ✅ If graph has checklist → **Follow it completely**
- ✅ If graph has pattern → **Apply it**
- ✅ If graph conflicts with assumptions → **Graph wins**

**4. Self-Check**
Before proceeding:
- [ ] Did I query the knowledge graph?
- [ ] Did I display findings to the user?
- [ ] Do I understand which patterns/checklists apply?
- [ ] Am I prepared to follow them as mandatory guidance?

**If any answer is NO**: Complete that step before proceeding.
```

**Pattern**: Numbered Steps + Self-Check + Blocking Condition
```markdown
## [Protocol Name] (MANDATORY)

### Before [Action]

You MUST follow this sequence:

**1. [Step Name]**
[Specific command or action]

**2. [Step Name]**
[Specific command or action]

**N. Self-Check**
Before proceeding:
- [ ] [Verification 1]
- [ ] [Verification 2]

**If any answer is NO**: [Blocking instruction]
```

**Why This Works**:
- Numbered steps provide clear sequence
- Self-check creates internal accountability
- Blocking condition prevents skipping
- "(MANDATORY)" in header reinforces non-negotiability

---

#### Level 4: CONDITIONAL (If-Then Enforcement)

**Use When**: Defining behavior based on conditions.

**Keywords**:
- `If [condition] then [action]`
- `When [trigger] → [response]`
- `On [event] → [action]`

**Examples from Trigger Conditions**:
```json
{
  "trigger_conditions": {
    "tool_names": ["Write", "Edit"],
    "file_patterns": ["**/plugin.json", "**/marketplace.json"],
    "action_keywords": ["version", "bump", "release"],
    "context_keywords": ["deployment", "publish"]
  }
}
```

**Pattern**: Structured Condition Matching
```markdown
## Trigger Conditions

**When ALL of these match**:
- Tool: [tool name list]
- File: [glob patterns]
- Action keyword: [keyword list]
- Context: [context keyword list]

**Then**:
- [Action 1]
- [Action 2]
```

**Why This Works**:
- Explicit boolean logic (ALL, ANY, NONE)
- Machine-parseable structure
- Clear trigger → response mapping

---

#### Level 5: GUIDANCE (Recommendation, Non-Binding)

**Use When**: Providing best practices that aren't strictly enforced.

**Keywords**:
- `SHOULD` - Recommendation
- `RECOMMENDED` - Best practice
- `CONSIDER` - Optional improvement
- `MAY` - Permissible option

**Examples from Documentation**:
```markdown
**RECOMMENDED**:
- Start with basic version
- Add complexity iteratively
- Test after each addition

**CONSIDER**:
- Using compression for large backups
- Adding age-based cleanup
```

**Pattern**: Clearly Marked Recommendations
```markdown
**RECOMMENDED**: [Best practice]
**CONSIDER**: [Optional improvement]
**MAY**: [Permissible option]
```

**Why This Works**:
- Clearly distinguished from MUST/REQUIRED
- Agent knows it can use judgment
- Still provides guidance without enforcement

---

### Anti-Patterns (What NOT to Do)

#### ❌ Ambiguous Weak Language

**Bad**:
```markdown
You should probably verify the data before saving.
Try to check for errors when you can.
It would be good to validate inputs.
```

**Why It Fails**:
- "should probably" = optional
- "try to" = best effort, not requirement
- "when you can" = optional condition
- "would be good" = suggestion, not mandate

**Good**:
```markdown
MANDATE: You MUST validate data before saving.
CRITICAL: Check for errors before proceeding.
REQUIRED: Validate all inputs.
```

---

#### ❌ Hedging and Uncertainty

**Bad**:
```markdown
Generally speaking, it's better to use 2+ sources.
In most cases, you might want to escalate uncertainty.
Typically, validation is recommended.
```

**Why It Fails**:
- "Generally" = not always
- "might want to" = optional
- "Typically" = sometimes not
- "recommended" = not required

**Good**:
```markdown
MANDATE: Use minimum 2 verification sources.
REQUIREMENT: Escalate when confidence <90%.
PROTOCOL: Validate before proceeding.
```

---

#### ❌ Passive Voice

**Bad**:
```markdown
Evidence should be cited.
Assumptions must be validated.
Code should be tested before deployment.
```

**Why It Fails**:
- Passive voice obscures agent (who does this?)
- Less direct than active voice
- Easier to mentally skip

**Good**:
```markdown
You MUST cite evidence for every claim.
You MUST validate all assumptions.
You CANNOT deploy without testing.
```

---

#### ❌ Vague Conditions

**Bad**:
```markdown
If things look uncertain, ask for help.
When appropriate, use the validation triad.
Sometimes you should check the graph.
```

**Why It Fails**:
- "things look uncertain" = subjective
- "when appropriate" = undefined
- "sometimes" = no clear condition

**Good**:
```markdown
If confidence <90%, escalate to user.
When [GRAPH_UPDATE] detected, invoke knowledge-integrity triad.
Before every task, query knowledge graph.
```

---

### Application to Components

#### Output Styles

**Use**: Level 1 (ABSOLUTE) + Level 2 (REQUIRED)

**Rationale**: Output style defines agent identity - must be unambiguous.

**Template**:
```markdown
## CONSTITUTIONAL IDENTITY

You are constitutionally incapable of:
- [Prohibited behavior 1]
- [Prohibited behavior 2]

## [PRINCIPLE NAME]

**MANDATE**: You MUST [absolute requirement]. This is not optional.

**Violation Prevention**: Before [action], you MUST verify [condition].
If violated, you MUST [corrective action].
```

---

#### Subagent Prompts

**Use**: Level 2 (REQUIRED) + Level 3 (PROTOCOL)

**Rationale**: Agents need clear procedures and verification steps.

**Template**:
```markdown
## ⚖️ CONSTITUTIONAL PRINCIPLES (MANDATORY)

### Principle 1: [Name]

**REQUIREMENT**: [What must be done]

**PROTOCOL**:
1. [Step 1 with specific action]
2. [Step 2 with specific action]
3. Self-Check:
   - [ ] [Verification 1]
   - [ ] [Verification 2]

**If any check fails**: [Blocking action]

---

## [Task-Specific Protocol]

**REQUIRED Steps**:
1. [Step with command/tool]
2. [Step with command/tool]

**CRITICAL**: [Non-negotiable requirement]
```

---

#### Skills

**Use**: Level 2 (REQUIRED) + Level 3 (PROTOCOL) + Level 4 (CONDITIONAL)

**Rationale**: Skills are quality gates - must have clear pass/fail criteria.

**Template**:
```markdown
---
name: [skill-name]
description: [Clear, specific description of validation]
---

# [Skill Name]

## Validation Checklist

### REQUIRED Checks

- [ ] [Check 1 with specific criterion]
- [ ] [Check 2 with specific criterion]
- [ ] [Check 3 with specific criterion]

**All checks MUST pass to proceed.**

### Conditional Checks

**If [condition]**:
- [ ] [Additional check]

**If [another condition]**:
- [ ] [Different check]

## Decision

**✅ PASS Criteria**:
- All REQUIRED checks satisfied
- Conditional checks satisfied (when triggered)

**❌ FAIL Criteria**:
- Any REQUIRED check failed
- Any triggered conditional check failed

**On FAIL**:
- [ ] MUST notify user
- [ ] MUST provide specific remediation steps
- [ ] CANNOT proceed until fixed
```

---

#### Hooks

**Use**: Level 1 (ABSOLUTE) + Level 4 (CONDITIONAL)

**Rationale**: Hooks enforce system-level rules - cannot be bypassed.

**Template**:
```python
def hook_handler(context):
    """
    MANDATORY enforcement hook

    This hook CANNOT be bypassed. All enforcement is non-negotiable.
    """

    # Detect condition
    if detect_condition(context):
        # ABSOLUTE requirement
        validation_result = mandatory_validation(context)

        if not validation_result.passed:
            # BLOCKING error
            raise BlockingError(
                "CRITICAL: Validation failed. CANNOT proceed.\n"
                f"Reason: {validation_result.reason}\n"
                f"Required action: {validation_result.remediation}"
            )

    # If condition not met, pass through
    return context
```

**Pattern**: Detect → Validate → Block on Failure

---

### Checklist for Writing Instructions

When writing instructions for agents/skills, verify:

**□ Language Clarity**
- [ ] Used imperative mood ("You MUST" not "You should")
- [ ] Active voice ("You validate X" not "X should be validated")
- [ ] No hedging ("MUST" not "might want to")
- [ ] No ambiguity ("confidence <90%" not "when uncertain")

**□ Enforcement Level**
- [ ] Chosen appropriate level (ABSOLUTE, REQUIRED, PROTOCOL, CONDITIONAL, GUIDANCE)
- [ ] Used keywords from that level
- [ ] Avoided mixing levels (don't use "MUST" and "consider" for same instruction)

**□ Verification**
- [ ] Included self-check or verification step
- [ ] Specified what happens on failure
- [ ] Provided blocking condition (if ABSOLUTE/REQUIRED)

**□ Specificity**
- [ ] Concrete actions (not vague verbs like "ensure" or "handle")
- [ ] Measurable criteria (numbers, file paths, tool names)
- [ ] Clear conditions (if/then statements with specific triggers)

**□ Structure**
- [ ] Used visual hierarchy (headers, lists, bold, emojis)
- [ ] Numbered steps for sequences
- [ ] Checkboxes for verification lists
- [ ] Code blocks for commands

---

### Real-World Example: Evolution of Instruction Clarity

**Initial Version (Weak)**:
```markdown
Agents should generally try to validate their knowledge before adding to the graph.
It would be good to check sources and make sure confidence is reasonable.
```

**Problems**:
- "should generally" = optional
- "try to" = best effort
- "would be good" = suggestion
- "reasonable" = undefined

**Revised Version (Strong)**:
```markdown
## Knowledge Validation Protocol (MANDATORY)

Before adding knowledge to graph, you MUST:

1. **Validate Evidence**
   - REQUIRED: Cite minimum 2 independent sources
   - Sources MUST be verifiable (file:line or URL)

2. **Assess Confidence**
   - Calculate confidence score (0.0-1.0)
   - If confidence <0.90, STOP and escalate to user
   - If confidence ≥0.90, proceed with explicit disclosure

3. **Self-Check**
   - [ ] Have I cited ≥2 sources?
   - [ ] Is my confidence ≥90% OR have I escalated?
   - [ ] Have I shown complete reasoning chain?

**If any check fails**: DO NOT add knowledge. Escalate or gather more evidence.

**Constitutional Requirement**: You CANNOT add knowledge without completing this protocol.
```

**Improvements**:
- Level 1 (ABSOLUTE): "CANNOT add knowledge without protocol"
- Level 2 (REQUIRED): "MUST cite minimum 2 sources"
- Level 3 (PROTOCOL): Numbered steps + self-check
- Level 4 (CONDITIONAL): "If confidence <0.90, STOP"
- Specific criteria: "≥2 sources", "confidence ≥0.90"
- Clear blocking condition: "DO NOT add knowledge"

---

### Summary: Instruction Writing Principles

1. **Be Imperative**: Command, don't suggest
2. **Be Absolute**: MUST/CANNOT, not should/might
3. **Be Specific**: Numbers, names, paths, not vague terms
4. **Be Structured**: Steps, checks, blocks, visual hierarchy
5. **Be Verified**: Self-checks, blocking conditions, explicit gates
6. **Be Consistent**: Use same level keywords throughout a section

**Golden Rule**: If an agent can interpret your instruction two different ways, you've failed. There must be **zero ambiguity**.

---

## 5. Component Decision Tree

### When to Use Each Component

```
┌─────────────────────────────────────────────────────────┐
│ Question: What do you need to enforce?                  │
└──────────────┬──────────────────────────────────────────┘
               │
               ├─ Main Claude's communication style?
               │  → USE: Output Style (.claude/output-styles/constitutional.md)
               │
               ├─ Project-wide principles for all work?
               │  → USE: CLAUDE.md (Core Operating Principles)
               │
               ├─ Individual agent's mandatory protocols?
               │  → USE: Subagent Prompt (⚖️ CONSTITUTIONAL PRINCIPLES section)
               │
               ├─ Workflow-specific validation checklist?
               │  → USE: Skill (.claude/skills/validate-{workflow}/)
               │
               ├─ Mandatory knowledge graph validation?
               │  → USE: Knowledge Integrity Triad + Hook
               │
               └─ System-wide automatic enforcement?
                  → USE: Hook (hooks/agent_output_validator.py)
```

### Decision Matrix

| Need | Output Style | CLAUDE.md | Subagent | Skill | Triad+Hook |
|------|--------------|-----------|----------|-------|------------|
| **Main Claude behavior** | ✅ PRIMARY | ⚠️ Reference | ❌ | ❌ | ❌ |
| **Agent behavior** | ❌ | ⚠️ Optional | ✅ PRIMARY | ❌ | ❌ |
| **Workflow checkpoint** | ❌ | ❌ | ❌ | ✅ PRIMARY | ⚠️ Backup |
| **Knowledge validation** | ❌ | ⚠️ Principles | ⚠️ At source | ⚠️ Optional | ✅ MANDATORY |
| **Cannot be bypassed** | ✅ | ❌ | ✅ | ❌ | ✅ |
| **Applies to all agents** | ❌ | ⚠️ If read | ❌ (per-agent) | ❌ | ✅ |
| **Git-sharable** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Team coordination** | ⚠️ | ✅ | ✅ | ✅ | ✅ |

---

## 5. Component Reference

### 5.1 Output Styles

**Purpose**: Define Main Claude's personality, communication style, and working methodology.

**When to Create**:
- Establishing Main Claude's behavior standards
- Defining TDD methodology
- Setting reasoning framework
- Specifying git workflow discipline

**When NOT to Create**:
- Agent-specific protocols (use subagent prompts)
- Workflow-specific validation (use skills)
- Mandatory enforcement (use hooks)

**File Structure**:
```
.claude/output-styles/
└── constitutional.md
    ├── YAML frontmatter (name, description)
    └── Markdown content (constitutional principles, TDD, reasoning framework)
```

**How to Activate**:
```bash
/output-style constitutional
```

**Key Sections in constitutional.md**:
1. Constitutional Identity
2. ACCA Framework
3. Communication Standards
4. Core Constitutional Principles (5 principles)
5. Reasoning Framework (5-step process)
6. Trade-off Hierarchy
7. Instruction Authority Hierarchy
8. RED-GREEN-BLUE TDD Methodology
9. Constitutional Self-Monitoring

**Documentation**: https://docs.claude.com/en/docs/claude-code/output-styles

---

### 5.2 Project Instructions (CLAUDE.md)

**Purpose**: Document project-wide principles, routing rules, and team standards.

**When to Update**:
- Adding new core operating principle
- Changing triad routing logic
- Documenting team conventions
- Updating knowledge management approach

**When NOT to Update**:
- Main Claude personality (use output style)
- Agent-specific protocols (use subagent prompts)
- Workflow validation (use skills)

**File Structure**:
```
CLAUDE.md
├── ⚡ CORE OPERATING PRINCIPLES
├── ⚡ TRIAD ROUTING SYSTEM
├── 📊 KNOWLEDGE MANAGEMENT
└── 📚 DETAILED DOCUMENTATION
```

**Current Sections**:

**1. Core Operating Principles**:
- Thoroughness Over Speed
- Evidence-Based Claims
- Uncertainty Escalation
- Complete Transparency
- Assumption Auditing

**2. Triad Routing System**:
- Routing table (user intent → triad)
- Examples of routing
- Critical rules

**3. Knowledge Management**:
- Minimum confidence (85%)
- Verification methods (≥2)
- Provenance required
- Graph update protocol

**4. Detailed Documentation**:
- Links to architecture docs
- Usage guides
- Installation instructions

**How Agents Access**:
```bash
# In subagent prompt, instruct agent to read:
"Before starting work, read CLAUDE.md to understand core operating principles."

# Or in agent responsibilities:
"1. Read CLAUDE.md for constitutional principles
 2. Apply principles to your work
 3. Document compliance in output"
```

---

### 5.3 Subagent Prompts

**Purpose**: Embed constitutional principles and protocols directly in agent system prompts.

**When to Create**:
- Adding new triad agent
- Ensuring agent produces constitutional outputs
- Embedding mandatory protocols
- Restricting tool usage for security

**When NOT to Create**:
- Main Claude behavior (use output style)
- Optional validation (use skills)
- System-wide enforcement (use hooks)

**File Structure**:
```
.claude/agents/
├── {triad}/
│   ├── {agent-name}.md
│   │   ├── YAML frontmatter (name, triad, tools, description)
│   │   ├── ⚖️ CONSTITUTIONAL PRINCIPLES
│   │   ├── 🧠 Knowledge Graph Protocol
│   │   ├── Responsibilities
│   │   └── Output Format
│   └── ...
└── templates/
    └── constitutional-agent-template.md
```

**YAML Frontmatter Fields**:
```yaml
---
name: agent-name                    # Unique identifier (lowercase, hyphens)
triad: triad-name                   # Which triad (idea-validation, design, etc.)
role: gatherer|validator|bridge     # Agent role in triad
template_version: 0.8.0             # Template version used
description: "Brief description"    # When/why to invoke this agent
tools: Read, Grep, Glob            # Allowed tools (optional, restricts access)
---
```

**Constitutional Section Structure**:
```markdown
## ⚖️ CONSTITUTIONAL PRINCIPLES (MANDATORY)

You are constitutionally bound by immutable behavioral principles.

### Principle 1: Evidence-Based Claims
[Protocol for citing sources, verification methods, confidence]

### Principle 2: Uncertainty Escalation
[Protocol for escalating when confidence <90%]

### Principle 3: Multi-Method Verification
[Protocol for using ≥2 verification methods]

### Principle 4: Complete Transparency
[Protocol for showing reasoning, assumptions, alternatives]

### Principle 5: Assumption Auditing
[Protocol for identifying and validating assumptions]

---

## Constitutional Self-Check

Before submitting output:
- [ ] Every claim has cited evidence
- [ ] Confidence ≥90% or escalated
- [ ] ≥2 verification methods used
- [ ] Complete reasoning shown
- [ ] All assumptions validated
- [ ] Knowledge graph consulted
```

**Template Location**: `.claude/templates/constitutional-agent-template.md` (to be created)

**How to Create Agent from Template**:
```bash
# Copy template
cp .claude/templates/constitutional-agent-template.md \
   .claude/agents/{triad}/{agent-name}.md

# Replace placeholders
# {AGENT_NAME} → actual-agent-name
# {TRIAD_NAME} → idea-validation | design | implementation | garden-tending | deployment
# {ROLE} → gatherer | validator | bridge
# {DESCRIPTION} → What this agent does
# {ALLOWED_TOOLS} → Read, Grep, Glob, WebSearch, etc.
```

---

### 5.4 Skills

**Purpose**: Provide workflow-specific validation checklists and quality gates for Main Claude.

**When to Create**:
- Workflow checkpoint validation
- Reusable quality gate templates
- Tool-restricted workflows
- Team-sharable validation protocols

**When NOT to Create**:
- Mandatory enforcement (use hooks + triad)
- Agent-specific protocols (use subagent prompts)
- Main Claude personality (use output style)

**File Structure**:
```
.claude/skills/
└── {skill-name}/
    ├── SKILL.md (required)
    │   ├── YAML frontmatter
    │   └── Markdown instructions
    ├── reference.md (optional)
    ├── examples.md (optional)
    └── templates/ (optional)
```

**YAML Frontmatter**:
```yaml
---
name: skill-name                    # lowercase, hyphens only (max 64 chars)
description: "When to use this"    # Critical for discovery (max 1024 chars)
allowed-tools: Read, Grep          # Optional: restrict tools when skill active
---
```

**Skill Pattern for Validation**:
```markdown
---
name: validate-research
description: Quality gate for idea-validation triad. Use after research-analyst or community-researcher complete work to validate evidence, sources, and confidence.
allowed-tools: Read, Grep
---

# Research Validation Skill

## Purpose
Validate research findings meet constitutional standards before proceeding.

## When to Use
After research-analyst or community-researcher completes work, BEFORE proceeding to design triad.

## Validation Checklist

### 1. Evidence Quality
- [ ] Every claim has specific source (URL or file:line)
- [ ] Sources are authoritative and recent
- [ ] Evidence directly supports claims

### 2. Confidence Assessment
- [ ] Explicit confidence score provided
- [ ] Confidence ≥85% OR uncertainty escalated
- [ ] Justification for confidence level included

### 3. Multi-Method Verification
- [ ] ≥2 verification methods used per key finding
- [ ] Methods are independent (not same source)
- [ ] Methods documented explicitly

### 4. Reasoning Transparency
- [ ] Complete reasoning chain from evidence to conclusion
- [ ] Assumptions identified and validated
- [ ] Alternatives considered and documented

### 5. Knowledge Graph Integration
- [ ] Knowledge graph consulted before work
- [ ] Relevant past decisions referenced
- [ ] [GRAPH_UPDATE] blocks included with proper provenance

## Decision

✅ **PASS**: All checklist items verified → Proceed to next triad
❌ **FAIL**: Violations found → Request rework with specific gaps identified

## Output Format

```
## Research Validation Results

### Evidence Quality: ✅ PASS / ❌ FAIL
[Assessment details]

### Confidence Assessment: ✅ PASS / ❌ FAIL
[Assessment details]

### Multi-Method Verification: ✅ PASS / ❌ FAIL
[Assessment details]

### Reasoning Transparency: ✅ PASS / ❌ FAIL
[Assessment details]

### Knowledge Graph Integration: ✅ PASS / ❌ FAIL
[Assessment details]

---

### OVERALL DECISION: ✅ PASS / ❌ FAIL

[If FAIL, specific remediation steps required]
```
```

**How Skills Activate**:
```
Main Claude receives research-analyst output
  ↓
Model evaluates: "Should I validate this?"
  ↓
Searches skill descriptions for "validate", "research", "quality gate"
  ↓
Finds validate-research skill (description matches context)
  ↓
Loads SKILL.md and applies checklist
  ↓
Main Claude uses checklist to validate output
  ↓
Decision: Pass (proceed) or Fail (request rework)
```

**Limitations**:
- ⚠️ Activation is discretionary (model decides)
- ⚠️ Only available to Main Claude (not subagents)
- ⚠️ Cannot intercept or block operations (guidance only)

**Documentation**: https://docs.claude.com/en/docs/claude-code/skills

---

### 5.5 Knowledge Integrity Triad

**Purpose**: Mandatory validation of ALL knowledge graph additions with constitutional compliance enforcement.

**When to Use**:
- Enforcing constitutional standards on knowledge
- Preventing low-quality knowledge from entering graph
- Detecting duplicates, contradictions, orphans
- Maintaining knowledge graph integrity

**When NOT to Use**:
- Workflow validation (use skills)
- Main Claude behavior (use output style)
- Project-wide principles (use CLAUDE.md)

**File Structure**:
```
.claude/agents/knowledge-integrity/
├── integrity-cultivator.md    # Assess quality (evidence, confidence, verification)
├── integrity-pruner.md        # Check redundancy (duplicates, contradictions)
└── integrity-bridge.md        # Approve/Reject with rationale

hooks/
└── agent_output_validator.py  # Detects [GRAPH_UPDATE], invokes triad
```

**Architecture**:

**1. Hook Detection** (`hooks/agent_output_validator.py`):
```python
def validate_knowledge_additions(agent_output: str) -> str:
    """Detect [GRAPH_UPDATE] blocks in any agent output"""

    graph_updates = detect_graph_updates(agent_output)

    if not graph_updates:
        return agent_output  # No knowledge additions

    # Inject mandatory validation step
    validation_instructions = f"""

    ================================================================================
    # 🛡️ CONSTITUTIONAL CHECKPOINT: KNOWLEDGE INTEGRITY VALIDATION
    ================================================================================

    The previous agent proposed {len(graph_updates)} knowledge graph updates.

    Before these updates are saved, you MUST validate constitutional compliance.

    ## GOVERNANCE PROTOCOL

    1. INVOKE: knowledge-integrity triad via Task tool
       - Pass: graph_updates={graph_updates}
       - Wait for validation result

    2. CHECK RESULT:
       - If APPROVED: Proceed with saving knowledge
       - If REJECTED: Escalate to user with specific violations

    3. ONLY SAVE knowledge if integrity triad approves

    This is NON-NEGOTIABLE constitutional enforcement.
    """

    return agent_output + validation_instructions
```

**2. Triad Agents**:

**integrity-cultivator.md**:
```markdown
## Role
Assess constitutional quality of proposed knowledge additions.

## Validation Checks

### 1. Evidence-Based Claims
- Every [GRAPH_UPDATE] must include provenance field
- Provenance must cite specific source (URL, file:line, documentation)
- Evidence must be verifiable

### 2. Confidence Threshold
- Every node must have confidence score
- Confidence must be ≥85%
- If confidence <85%, update must include escalation justification

### 3. Multi-Method Verification
- Every node must document verification_methods field
- Minimum 2 verification methods required
- Methods must be independent (different sources/approaches)

### 4. Complete Transparency
- Reasoning chain must be included
- Assumptions must be documented
- Alternatives considered must be listed

## Output Format
```
## Quality Assessment

[For each graph update:]

Update: {node_id}
- Evidence: ✅ PASS / ❌ FAIL {assessment}
- Confidence: ✅ PASS / ❌ FAIL {score}% (threshold: 85%)
- Verification: ✅ PASS / ❌ FAIL {method_count} methods (min: 2)
- Transparency: ✅ PASS / ❌ FAIL {reasoning_chain_present}

Overall: ✅ PASS / ❌ FAIL
```
```

**integrity-pruner.md**:
```markdown
## Role
Detect redundancy and contradictions in knowledge graph.

## Checks

### 1. Duplicate Detection
- Check if entity already exists (same name/label)
- Check if relationship already exists (same source/target/type)
- Flag near-duplicates (high similarity)

### 2. Contradiction Detection
- Check if new fact contradicts existing fact
- Check temporal conflicts (e.g., person in two places simultaneously)
- Flag confidence conflicts (high-confidence vs low-confidence on same fact)

### 3. Orphan Detection
- Check if new nodes have relationships
- Flag isolated entities
- Suggest connections to existing graph

## Output Format
```
## Redundancy Assessment

Duplicates Found: {count}
- {node_id}: Duplicate of {existing_node_id} (similarity: {score})

Contradictions Found: {count}
- {conflict_description}

Orphans: {count}
- {node_id}: No relationships defined

Overall: ✅ NO ISSUES / ⚠️ REVIEW REQUIRED / ❌ BLOCKING ISSUES
```
```

**integrity-bridge.md**:
```markdown
## Role
Synthesize assessments and make final APPROVE/REJECT decision.

## Decision Protocol

1. Review cultivator assessment (quality)
2. Review pruner assessment (redundancy)
3. Make decision:
   - ✅ APPROVE: All checks passed OR minor issues acceptable
   - ⚠️ APPROVE WITH WARNINGS: Issues noted but not blocking
   - ❌ REJECT: Blocking violations found

4. Provide rationale and remediation if rejected

## Output Format
```
## Knowledge Integrity Decision

### Cultivator Assessment Summary
[Quality check results]

### Pruner Assessment Summary
[Redundancy check results]

### DECISION: ✅ APPROVED / ⚠️ APPROVED WITH WARNINGS / ❌ REJECTED

### Rationale
[Why this decision was made]

### Remediation (if rejected)
[Specific steps to fix violations]

### [HANDOFF_REQUEST] (if approved)
next_action: save_to_knowledge_graph
approved_updates: {list of node_ids}
```
```

**3. Flow Example**:
```
research-analyst creates finding
  ↓
Adds [GRAPH_UPDATE] block:
  [GRAPH_UPDATE]
  node_id: finding_docker_benefits
  label: Docker Benefits Research
  confidence: 0.98
  provenance: {source: "https://docker.com/docs", evidence: "..."}
  verification_methods: ["web_research", "codebase_analysis"]
  [/GRAPH_UPDATE]
  ↓
Hook detects [GRAPH_UPDATE] in output
  ↓
Hook injects validation instructions
  ↓
Main Claude invokes knowledge-integrity triad:

  1. integrity-cultivator checks:
     - Evidence: ✅ PASS (provenance includes source)
     - Confidence: ✅ PASS (98% ≥ 85%)
     - Verification: ✅ PASS (2 methods)
     - Transparency: ✅ PASS (reasoning documented)

  2. integrity-pruner checks:
     - Duplicates: ✅ NONE (Docker entity new)
     - Contradictions: ✅ NONE
     - Orphans: ⚠️ WARNING (no relationships yet)

  3. integrity-bridge decides:
     - Decision: ✅ APPROVED WITH WARNINGS
     - Rationale: "Quality checks passed, orphan acceptable for new research"
     - Action: Save to knowledge graph
  ↓
Knowledge saved to .claude/graphs/idea-validation_graph.json
```

---

### 5.6 Hooks

**Purpose**: System-level interception for mandatory enforcement that cannot be bypassed.

**When to Use**:
- Mandatory quality gates
- Automatic workflow orchestration
- [GRAPH_UPDATE] detection and validation
- System-wide enforcement (cannot rely on agent compliance)

**When NOT to Use**:
- Optional validation (use skills)
- Agent-specific protocols (use subagent prompts)
- User-facing configuration (use CLAUDE.md)

**File Structure**:
```
hooks/
├── user_prompt_submit.py          # Runs BEFORE Claude sees message
│   └── Supervisor orchestration
└── agent_output_validator.py      # Runs AFTER agent outputs
    └── Knowledge validation
```

**Hook Lifecycle**:

**1. user_prompt_submit.py** (Pre-Processing):
```
User sends message
  ↓
Hook runs (BEFORE Claude sees it)
  ↓
Detect work vs Q&A
  ↓
If work: Inject orchestrator instructions
  ↓
Claude receives modified message
  ↓
Claude acts on instructions
```

**2. agent_output_validator.py** (Post-Processing):
```
Agent completes work
  ↓
Agent returns output
  ↓
Hook runs (BEFORE Main Claude sees it)
  ↓
Detect [GRAPH_UPDATE] blocks
  ↓
If found: Inject validation instructions
  ↓
Main Claude receives modified output
  ↓
Main Claude invokes knowledge-integrity triad
```

**Hook Implementation Pattern**:
```python
# hooks/agent_output_validator.py

def validate_knowledge_additions(agent_output: str) -> str:
    """
    Mandatory knowledge validation hook.

    Runs AFTER every agent output to detect and validate
    [GRAPH_UPDATE] blocks before knowledge is saved.
    """

    # 1. Detect knowledge additions
    graph_updates = detect_graph_updates(agent_output)

    if not graph_updates:
        # No knowledge additions, pass through
        return agent_output

    # 2. Inject MANDATORY validation step
    validation_instructions = generate_validation_instructions(graph_updates)

    # 3. Return modified output with validation requirement
    return agent_output + validation_instructions

def detect_graph_updates(text: str) -> List[dict]:
    """Extract [GRAPH_UPDATE] blocks from text"""
    pattern = r'\[GRAPH_UPDATE\](.*?)\[/GRAPH_UPDATE\]'
    matches = re.findall(pattern, text, re.DOTALL)
    return [parse_graph_update(m) for m in matches]

def generate_validation_instructions(updates: List[dict]) -> str:
    """Generate validation instructions for Main Claude"""
    return f"""

    ================================================================================
    # 🛡️ CONSTITUTIONAL CHECKPOINT: KNOWLEDGE INTEGRITY VALIDATION
    ================================================================================

    DETECTED: {len(updates)} knowledge graph update(s)

    MANDATORY PROTOCOL:

    1. INVOKE knowledge-integrity triad (via Task tool)
       - Validation required before save
       - Pass: graph_updates={updates}

    2. WAIT for triad approval:
       - ✅ APPROVED → Save to knowledge graph
       - ❌ REJECTED → Escalate to user with violations

    3. DO NOT SAVE knowledge without triad approval

    This enforcement is NON-NEGOTIABLE.
    """
```

**Configuration**:
```json
// .claude/settings.json

{
  "hooks": {
    "user_prompt_submit": {
      "path": "hooks/user_prompt_submit.py",
      "function": "process_user_message",
      "description": "Supervisor orchestration"
    },
    "agent_output_validator": {
      "path": "hooks/agent_output_validator.py",
      "function": "validate_knowledge_additions",
      "description": "Knowledge integrity validation"
    }
  }
}
```

**Limitations**:
- ⚠️ Complex to debug (runs invisibly)
- ⚠️ Performance impact if slow
- ⚠️ Must be stateless (no persistence between invocations)
- ⚠️ Errors can block workflow

**Documentation**: Internal (no official Claude Code docs on hooks yet)

---

## 6. Constitutional Patterns

### Pattern 1: Defense in Depth

**Principle**: Multiple layers ensure constitutional compliance even if one layer fails.

**Implementation**:
```
Layer 1 (Prevention): Subagent prompt with constitutional principles
  ↓ Agent creates output following principles

Layer 2 (Detection): Main Claude reviews output with skill
  ↓ Main Claude validates using checklist

Layer 3 (Enforcement): Hook detects [GRAPH_UPDATE]
  ↓ Invokes knowledge-integrity triad

Layer 4 (Verification): Triad validates and approves/rejects
  ↓ Only compliant knowledge saved
```

**Why This Works**:
- Layer 1 fails → Layer 2 catches
- Layer 2 discretionary → Layer 3 mandatory
- Layer 3 triggers → Layer 4 validates
- All layers fail → Knowledge not saved (fail-safe)

---

### Pattern 2: Constitutional Agent Template

**Principle**: All agents share constitutional foundation, specialize in domain.

**Implementation**:
```markdown
# Every agent starts with:

## ⚖️ CONSTITUTIONAL PRINCIPLES (MANDATORY)
[Universal constitutional section - identical across all agents]

## 🧠 {TRIAD} Knowledge Graph Protocol
[Triad-specific protocol - shared within triad]

## Responsibilities
[Agent-specific tasks - unique to this agent]
```

**Why This Works**:
- Constitutional principles universal (prevent drift)
- Triad protocols shared (consistent within workflow)
- Responsibilities specialized (agent expertise)

**Template**: `.claude/templates/constitutional-agent-template.md`

---

### Pattern 3: Hook-Triggered Quality Gates

**Principle**: Automatic enforcement via system hooks, not agent compliance.

**Implementation**:
```python
# Hook pattern
def hook_function(input_or_output: str) -> str:
    """Intercept and inject enforcement instructions"""

    # 1. Detect trigger condition
    if not should_enforce(input_or_output):
        return input_or_output  # Pass through

    # 2. Inject mandatory instructions
    enforcement = generate_enforcement_instructions()

    # 3. Return modified with enforcement
    return input_or_output + enforcement
```

**Why This Works**:
- Hooks run automatically (can't be forgotten)
- Hooks are system-level (can't be bypassed)
- Hooks inject instructions (Main Claude must follow)
- Hooks are stateless (repeatable, testable)

---

### Pattern 4: Skill-Based Discretionary Guidance

**Principle**: Skills provide optional validation when Main Claude recognizes context.

**Implementation**:
```markdown
# Skill description optimized for discovery:
description: "Quality gate for {workflow} triad. Use when {agent} completes work to validate {standards}."

# Skill provides checklist
## Validation Checklist
- [ ] Standard 1
- [ ] Standard 2
...

# Main Claude decides when to use
Main Claude: "Research complete. Let me validate using validate-research skill."
```

**Why This Works**:
- Skills discoverable (model finds when relevant)
- Skills optional (doesn't block workflow)
- Skills reusable (git-sharable)
- Skills lightweight (no enforcement overhead)

---

### Pattern 5: Escalation Over Guessing

**Principle**: Agents escalate uncertainty instead of guessing and creating low-confidence knowledge.

**Implementation in Subagent Prompt**:
```markdown
### Principle 2: Uncertainty Escalation

**Threshold Protocol**:
- 95-100%: Proceed with full documentation
- 90-94%: Proceed with explicit confidence disclosure
- <90%: STOP and escalate

**Escalation Format**:
```
❌ UNCERTAINTY THRESHOLD EXCEEDED

Current Confidence: {percentage}%
Uncertainty Source: {what is unclear}

REQUEST: Please clarify {specific question} before I proceed.
```

**Constitutional Requirement**: You MUST escalate. You CANNOT proceed with guesses.
```

**Why This Works**:
- Prevents low-quality knowledge at source
- Explicit confidence thresholds (no ambiguity)
- Escalation template (easy for agent to use)
- Constitutional mandate (agent cannot bypass)

---

## 7. Implementation Checklist

### Phase 1: Foundation (Main Claude)

- [x] **Output Style Created**: `.claude/output-styles/constitutional.md` exists
- [x] **Output Style Active**: `/output-style constitutional` selected
- [x] **CLAUDE.md Updated**: Core operating principles documented
- [ ] **CLAUDE.md Enhanced**: Add constitutional principles section (if missing)

**Verification**:
```bash
# Check output style exists
ls .claude/output-styles/constitutional.md

# Check output style active
cat .claude/settings.local.json | grep "output-style"

# Check CLAUDE.md has principles
grep "CORE OPERATING PRINCIPLES" CLAUDE.md
```

---

### Phase 2: Agent Constitutional Prompts

- [ ] **Template Created**: `.claude/templates/constitutional-agent-template.md`
- [ ] **All Agents Updated**: 18+ agents include constitutional section

**Agents to Update**:
```
Idea Validation Triad:
- [ ] research-analyst.md
- [ ] community-researcher.md
- [ ] validation-synthesizer.md

Design Triad:
- [ ] solution-architect.md
- [ ] design-bridge.md

Implementation Triad:
- [ ] senior-developer.md
- [ ] test-engineer.md

Garden Tending Triad:
- [ ] cultivator.md
- [ ] pruner.md
- [ ] gardener-bridge.md

Deployment Triad:
- [ ] release-manager.md
- [ ] documentation-updater.md

System Agents:
- [ ] verification-agent.md
- [ ] research-agent.md

Supervisor:
- [ ] supervisor.md (reference constitutional principles)
```

**Verification**:
```bash
# Check template exists
ls .claude/templates/constitutional-agent-template.md

# Count agents with constitutional section
grep -r "⚖️ CONSTITUTIONAL PRINCIPLES" .claude/agents/ | wc -l
# Should be 18+ (all agents)

# Check specific agent
grep "CONSTITUTIONAL PRINCIPLES" .claude/agents/idea-validation/research-analyst.md
```

---

### Phase 3: Workflow Validation Skills

- [ ] **validate-research skill**: `.claude/skills/validate-research/SKILL.md`
- [ ] **validate-design skill**: `.claude/skills/validate-design/SKILL.md`
- [ ] **validate-implementation skill**: `.claude/skills/validate-implementation/SKILL.md`
- [ ] **validate-knowledge skill**: `.claude/skills/validate-knowledge/SKILL.md`

**Verification**:
```bash
# List all skills
ls .claude/skills/

# Check validate-research exists
cat .claude/skills/validate-research/SKILL.md | grep "name: validate-research"

# Check skill descriptions optimized for discovery
grep "description:" .claude/skills/*/SKILL.md
```

---

### Phase 4: Knowledge Integrity Triad

- [ ] **integrity-cultivator.md**: `.claude/agents/knowledge-integrity/integrity-cultivator.md`
- [ ] **integrity-pruner.md**: `.claude/agents/knowledge-integrity/integrity-pruner.md`
- [ ] **integrity-bridge.md**: `.claude/agents/knowledge-integrity/integrity-bridge.md`
- [ ] **Hook Created**: `hooks/agent_output_validator.py`
- [ ] **Hook Registered**: Entry in `.claude/settings.json`

**Verification**:
```bash
# Check triad agents exist
ls .claude/agents/knowledge-integrity/

# Check hook exists
ls hooks/agent_output_validator.py

# Check hook registered
cat .claude/settings.json | grep "agent_output_validator"
```

---

### Phase 5: Testing & Validation

- [ ] **Test Output Style**: Main Claude follows constitutional principles
- [ ] **Test Agent Prompts**: Subagents escalate when confidence <90%
- [ ] **Test Skills**: Main Claude uses validate-* skills at checkpoints
- [ ] **Test Triad**: Knowledge integrity triad validates [GRAPH_UPDATE]
- [ ] **Test Hook**: Hook detects [GRAPH_UPDATE] and triggers validation

**Test Scripts**:
```bash
# Test 1: Output style active
# Expected: Main Claude shows constitutional compliance audit

# Test 2: Agent escalation
# Create test that forces low confidence
# Expected: Agent escalates with uncertainty format

# Test 3: Skill activation
# Complete research, Main Claude should validate
# Expected: validate-research skill used

# Test 4: Triad validation
# Create [GRAPH_UPDATE] with low confidence
# Expected: Triad rejects and provides remediation

# Test 5: Hook interception
# Any [GRAPH_UPDATE] in agent output
# Expected: Hook injects validation instructions
```

---

## 8. Examples & Use Cases

### Example 1: Research Validation Flow

**Scenario**: User requests "Research Docker benefits for containerization"

**Flow**:

**1. Supervisor Detects Work** (Hook: user_prompt_submit.py):
```
User: "Research Docker benefits"
  ↓
Hook detects work request (not Q&A)
  ↓
Hook injects orchestrator instructions for idea-validation triad
  ↓
Main Claude invokes research-analyst
```

**2. research-analyst Researches** (Constitutional Prompt):
```
research-analyst prompt includes:
  ⚖️ CONSTITUTIONAL PRINCIPLES
  - Evidence-Based Claims: Cite sources
  - Uncertainty Escalation: Stop if <90% confidence
  - Multi-Method Verification: Use ≥2 methods
  ↓
Agent conducts research:
  - Method 1: Web search (docker.com/docs)
  - Method 2: Codebase analysis (existing Docker usage)
  ↓
Agent creates finding with 98% confidence
  ↓
Agent includes [GRAPH_UPDATE]:
    node_id: finding_docker_benefits
    confidence: 0.98
    provenance: {source: "https://docker.com/docs", evidence: "..."}
    verification_methods: ["web_research", "codebase_analysis"]
  ↓
Agent returns output to Main Claude
```

**3. Main Claude Validates** (Skill: validate-research):
```
Main Claude receives research-analyst output
  ↓
Main Claude: "Let me validate this research"
  ↓
Loads validate-research skill
  ↓
Applies checklist:
  - [ ] Sources cited? ✅ Yes (docker.com/docs)
  - [ ] Confidence ≥85%? ✅ Yes (98%)
  - [ ] ≥2 methods? ✅ Yes (web + codebase)
  - [ ] Reasoning shown? ✅ Yes
  ↓
Main Claude: ✅ PASS - Proceed to community-researcher
```

**4. Hook Detects Knowledge** (Hook: agent_output_validator.py):
```
research-analyst output contains [GRAPH_UPDATE]
  ↓
Hook intercepts output
  ↓
Hook injects validation instructions:
  "MANDATORY: Invoke knowledge-integrity triad before saving"
  ↓
Main Claude receives modified output with validation requirement
```

**5. Knowledge Integrity Triad Validates**:
```
Main Claude invokes knowledge-integrity triad
  ↓
integrity-cultivator checks quality:
  - Evidence: ✅ PASS (source cited)
  - Confidence: ✅ PASS (98% ≥ 85%)
  - Verification: ✅ PASS (2 methods)
  ↓
integrity-pruner checks redundancy:
  - Duplicates: ✅ NONE
  - Contradictions: ✅ NONE
  ↓
integrity-bridge approves:
  - Decision: ✅ APPROVED
  - Rationale: "All constitutional checks passed"
  ↓
Knowledge saved to .claude/graphs/idea-validation_graph.json
```

**Result**: High-quality knowledge with constitutional guarantees at every layer.

---

### Example 2: Low-Confidence Escalation

**Scenario**: research-analyst encounters ambiguous information

**Flow**:

**1. Agent Researches** (Constitutional Prompt):
```
research-analyst researching "GraphQL vs REST for our API"
  ↓
Agent finds conflicting information:
  - Source 1: "GraphQL is better for flexibility"
  - Source 2: "REST is simpler for basic APIs"
  ↓
Agent calculates confidence: 72% (below 90% threshold)
  ↓
Agent's constitutional prompt triggers escalation:
  "MANDATE: When confidence <90%, STOP and escalate"
  ↓
Agent returns escalation (NOT a low-confidence finding):
```

**2. Agent Output**:
```markdown
❌ UNCERTAINTY THRESHOLD EXCEEDED

Task: Determine whether GraphQL or REST is better for our API

Current Confidence: 72%

Uncertainty Source: Conflicting information from authoritative sources
- docker.com recommends GraphQL for complex queries
- AWS best practices recommend REST for simple CRUD
- Our use case falls in between (moderate complexity)

Impact: Choosing wrong architecture could require significant rework

Options:
1. GraphQL: Better flexibility, steeper learning curve
2. REST: Simpler, more established tooling
3. Hybrid: REST for CRUD, GraphQL for complex queries

REQUEST: Please clarify API complexity requirements before I proceed.

Specific Questions:
- How complex are the expected queries? (simple CRUD vs nested relationships)
- Is team familiar with GraphQL?
- Is real-time data subscription needed?
```

**3. Main Claude Receives Escalation**:
```
Main Claude sees uncertainty escalation (not a finding)
  ↓
Main Claude presents to user:
  "research-analyst encountered uncertainty (72% confidence).
   Please provide clarification on API complexity requirements."
  ↓
User clarifies: "Simple CRUD, team not familiar with GraphQL"
  ↓
Main Claude passes clarification back to research-analyst
  ↓
research-analyst completes research with 95% confidence:
  "Recommendation: REST - matches use case, team expertise, simplicity"
```

**Result**: Low-confidence knowledge prevented at source, user clarification obtained, high-confidence conclusion reached.

---

### Example 3: Knowledge Integrity Rejection

**Scenario**: Agent creates knowledge with insufficient evidence

**Flow**:

**1. Agent Creates Knowledge** (Violates Constitutional Principles):
```
community-researcher creates finding:
  [GRAPH_UPDATE]
  node_id: finding_community_prefers_graphql
  label: "Community Prefers GraphQL"
  confidence: 0.88
  provenance: {source: "Stack Overflow discussion", evidence: "One user said GraphQL is better"}
  verification_methods: ["web_search"]
  [/GRAPH_UPDATE]
```

**Problems**:
- ❌ Single verification method (requires ≥2)
- ❌ Weak evidence (one user opinion)
- ❌ Confidence too high for evidence quality

**2. Hook Detects** (agent_output_validator.py):
```
Hook detects [GRAPH_UPDATE]
  ↓
Hook injects validation instructions
  ↓
Main Claude invokes knowledge-integrity triad
```

**3. Triad Validates**:
```
integrity-cultivator assesses:
  - Evidence: ❌ FAIL (single user opinion is not authoritative)
  - Confidence: ⚠️ WARNING (88% for weak evidence is too high)
  - Verification: ❌ FAIL (only 1 method, requires ≥2)

integrity-pruner checks:
  - Duplicates: ✅ NONE
  - Contradictions: ✅ NONE

integrity-bridge decides:
  - Decision: ❌ REJECTED
  - Rationale: "Insufficient evidence and verification for confidence level"
```

**4. Bridge Output**:
```markdown
## Knowledge Integrity Decision: ❌ REJECTED

### Violations Found:

1. **Evidence Quality: INSUFFICIENT**
   - Current: Single Stack Overflow user opinion
   - Required: Authoritative source (official surveys, multiple sources)

2. **Verification Methods: INSUFFICIENT**
   - Current: 1 method (web_search only)
   - Required: Minimum 2 independent methods

3. **Confidence Mismatch**
   - Current confidence: 88%
   - Evidence supports: ~60% (opinion-based)

### Remediation Required:

Before this knowledge can be saved:

1. **Add Second Verification Method**:
   - Survey official GraphQL vs REST usage statistics
   - Analyze GitHub trends data
   - Review industry reports

2. **Strengthen Evidence**:
   - Find authoritative sources (State of JS survey, Stack Overflow trends)
   - Multiple data points, not single opinions

3. **Adjust Confidence**:
   - Lower to 60-70% for current evidence quality
   - OR strengthen evidence to justify 88%

### Next Steps:

Main Claude should request community-researcher to:
1. Conduct additional verification using second method
2. Find authoritative community preference data
3. Resubmit with strengthened evidence
```

**5. Main Claude Escalates to User**:
```
Main Claude: "Knowledge integrity validation FAILED.
              community-researcher's finding rejected due to:
              - Insufficient evidence (1 user opinion)
              - Single verification method (requires ≥2)

              Options:
              1. Request rework with additional verification
              2. Lower confidence to match evidence (~60%)
              3. Skip this finding and proceed

              What would you like to do?"

User: "Request rework"

Main Claude: "community-researcher, please conduct additional research
              using a second verification method and find authoritative
              community preference data (surveys, trend reports)."
```

**Result**: Low-quality knowledge blocked, specific remediation provided, agent can fix and resubmit.

---

## 9. Troubleshooting

### Issue 1: Output Style Not Applying

**Symptoms**:
- Main Claude doesn't follow constitutional principles
- No constitutional compliance audit in responses
- TDD methodology not followed

**Diagnosis**:
```bash
# Check output style file exists
ls .claude/output-styles/constitutional.md
# Should exist

# Check output style selected
cat .claude/settings.local.json | grep "output-style"
# Should show: "output-style": "constitutional"

# Check output style format
head -20 .claude/output-styles/constitutional.md
# Should show YAML frontmatter with name, description
```

**Solutions**:

1. **Output style not selected**:
```bash
/output-style constitutional
```

2. **Output style file malformed**:
```yaml
# First 3 lines must be:
---
name: Constitutional TDD
description: Constitutional software development agent...
---
```

3. **Session restart required**:
```bash
# Restart Claude Code session
# Output styles load at session start
```

---

### Issue 2: Agents Not Following Constitutional Principles

**Symptoms**:
- Agents create low-confidence knowledge (<85%)
- Agents don't cite sources
- Agents don't show reasoning chains
- Agents don't escalate uncertainty

**Diagnosis**:
```bash
# Check agent file has constitutional section
grep "⚖️ CONSTITUTIONAL PRINCIPLES" .claude/agents/{triad}/{agent}.md
# Should find section

# Check agent tools restricted
grep "tools:" .claude/agents/{triad}/{agent}.md
# Should show allowed tools only
```

**Solutions**:

1. **Agent missing constitutional section**:
```bash
# Copy from template
cp .claude/templates/constitutional-agent-template.md \
   .claude/agents/{triad}/{agent}.md

# Or add section manually (see Section 5.3)
```

2. **Constitutional section not mandatory**:
```markdown
# Make sure section header says "MANDATORY"
## ⚖️ CONSTITUTIONAL PRINCIPLES (MANDATORY)

# Not just:
## Constitutional Principles
```

3. **Agent ignoring principles**:
```markdown
# Add constitutional self-check at end of prompt:

## Constitutional Self-Check

Before submitting output, verify:
- [ ] Every claim has cited evidence
- [ ] Confidence ≥90% or escalated
- [ ] ≥2 verification methods used
- [ ] Complete reasoning shown
- [ ] All assumptions validated

**If ANY checkbox is unchecked, complete that requirement before proceeding.**
```

---

### Issue 3: Skills Not Activating

**Symptoms**:
- Main Claude doesn't use validate-* skills
- Skills never mentioned in responses
- Validation checklists not applied

**Diagnosis**:
```bash
# Check skill file exists
ls .claude/skills/validate-research/SKILL.md
# Should exist

# Check skill description
grep "description:" .claude/skills/validate-research/SKILL.md
# Should be specific and include keywords like "quality gate", "validate", "research"

# Check skill name
grep "name:" .claude/skills/validate-research/SKILL.md
# Should be lowercase, hyphens only
```

**Solutions**:

1. **Skill description too vague**:
```yaml
# Bad (vague):
description: "Validates research"

# Good (specific with context keywords):
description: "Quality gate for idea-validation triad. Use when research-analyst or community-researcher complete work to validate evidence quality, source citations, and confidence thresholds."
```

2. **Skill name format invalid**:
```yaml
# Bad:
name: Validate Research  # uppercase, spaces
name: validate_research  # underscores

# Good:
name: validate-research  # lowercase, hyphens
```

3. **Skills are discretionary**:
```markdown
# Remember: Skills are model-invoked (discretionary)
# Don't rely on skills for mandatory enforcement
# Use knowledge-integrity triad + hook for mandatory validation
```

---

### Issue 4: Hook Not Intercepting

**Symptoms**:
- [GRAPH_UPDATE] blocks not validated
- knowledge-integrity triad never invoked
- Knowledge saved without validation

**Diagnosis**:
```bash
# Check hook file exists
ls hooks/agent_output_validator.py
# Should exist

# Check hook registered
cat .claude/settings.json | grep "agent_output_validator"
# Should show hook entry

# Check hook function signature
grep "def validate_knowledge_additions" hooks/agent_output_validator.py
# Should exist with correct signature
```

**Solutions**:

1. **Hook not registered**:
```json
// Add to .claude/settings.json
{
  "hooks": {
    "agent_output_validator": {
      "path": "hooks/agent_output_validator.py",
      "function": "validate_knowledge_additions",
      "description": "Knowledge integrity validation"
    }
  }
}
```

2. **Hook function signature wrong**:
```python
# Correct signature:
def validate_knowledge_additions(agent_output: str) -> str:
    """Hook function - receives output, returns modified output"""
    ...
    return modified_output

# Not:
def validate_knowledge_additions():  # Missing parameter
def validate_knowledge_additions(output):  # Wrong parameter name
```

3. **Hook not detecting [GRAPH_UPDATE]**:
```python
# Check regex pattern
pattern = r'\[GRAPH_UPDATE\](.*?)\[/GRAPH_UPDATE\]'
matches = re.findall(pattern, agent_output, re.DOTALL)

# re.DOTALL flag required for multiline matching
```

---

### Issue 5: Triad Validation Not Blocking Bad Knowledge

**Symptoms**:
- Low-confidence knowledge saved despite <85%
- Knowledge without evidence saved
- Triad approves everything

**Diagnosis**:
```bash
# Check triad agents exist
ls .claude/agents/knowledge-integrity/
# Should show: integrity-cultivator.md, integrity-pruner.md, integrity-bridge.md

# Check cultivator has validation checks
grep "Confidence Threshold" .claude/agents/knowledge-integrity/integrity-cultivator.md
# Should find section with ≥85% requirement

# Check bridge has decision logic
grep "APPROVE\|REJECT" .claude/agents/knowledge-integrity/integrity-bridge.md
# Should find decision protocol
```

**Solutions**:

1. **Triad too lenient**:
```markdown
# In integrity-cultivator.md, make thresholds explicit:

### 2. Confidence Threshold
- Every node must have confidence score
- Confidence must be ≥85%
- If confidence <85%, update must be REJECTED OR include escalation justification

**MANDATE**: No exceptions to 85% threshold without explicit escalation.
```

2. **Bridge auto-approves**:
```markdown
# In integrity-bridge.md, make rejection criteria clear:

## Decision Protocol

### REJECTION Criteria (ANY of these = REJECT):
- Confidence <85% without escalation justification
- Missing provenance (no source cited)
- Single verification method (requires ≥2)
- Missing reasoning chain
- Contradicts existing high-confidence knowledge

**MANDATE**: If ANY rejection criterion is met, decision MUST be REJECT.
```

3. **Main Claude ignores rejection**:
```markdown
# In hook validation instructions, emphasize non-negotiable:

3. DO NOT SAVE knowledge without triad approval

**This enforcement is NON-NEGOTIABLE. REJECTED knowledge must be escalated to user for rework.**
```

---

## Appendix A: File Locations Quick Reference

```
triads/
├── .claude/
│   ├── output-styles/
│   │   └── constitutional.md                    # Layer 1: Main Claude behavior
│   │
│   ├── agents/
│   │   ├── idea-validation/
│   │   │   ├── research-analyst.md              # Layer 3: Agent prompts
│   │   │   ├── community-researcher.md
│   │   │   └── validation-synthesizer.md
│   │   ├── design/
│   │   │   ├── solution-architect.md
│   │   │   └── design-bridge.md
│   │   ├── implementation/
│   │   │   ├── senior-developer.md
│   │   │   └── test-engineer.md
│   │   ├── garden-tending/
│   │   │   ├── cultivator.md
│   │   │   ├── pruner.md
│   │   │   └── gardener-bridge.md
│   │   ├── deployment/
│   │   │   ├── release-manager.md
│   │   │   └── documentation-updater.md
│   │   ├── knowledge-integrity/                 # Layer 5: Mandatory validation
│   │   │   ├── integrity-cultivator.md
│   │   │   ├── integrity-pruner.md
│   │   │   └── integrity-bridge.md
│   │   └── supervisor/
│   │       └── supervisor.md
│   │
│   ├── skills/                                   # Layer 4: Quality gates
│   │   ├── validate-research/
│   │   │   └── SKILL.md
│   │   ├── validate-design/
│   │   │   └── SKILL.md
│   │   ├── validate-implementation/
│   │   │   └── SKILL.md
│   │   └── validate-knowledge/
│   │       └── SKILL.md
│   │
│   ├── templates/
│   │   └── constitutional-agent-template.md     # Template for agents
│   │
│   └── settings.json                            # Hook registration
│
├── hooks/                                        # Layer 6: System enforcement
│   ├── user_prompt_submit.py
│   └── agent_output_validator.py
│
├── CLAUDE.md                                     # Layer 2: Universal principles
│
└── docs/
    └── CONSTITUTIONAL_ARCHITECTURE_GUIDE.md     # This document
```

---

## Appendix B: Constitutional Principles Reference

### The 5 Core Principles

**1. Thoroughness Over Speed**
- Always take the hard road, never shortcuts
- Use multiple verification methods
- Check edge cases, not just happy paths
- Validate ALL assumptions

**2. Evidence-Based Claims**
- Triple-verify everything before stating facts
- Cite specific sources: URLs, file:line, documentation
- Show step-by-step reasoning
- Distinguish facts from inferences

**3. Uncertainty Escalation**
- Never guess when uncertain - escalate immediately
- 95-100%: Proceed with documentation
- 90-94%: Proceed with disclosure
- <90%: STOP and escalate

**4. Complete Transparency**
- Show all work, reasoning, and assumptions
- List all sources consulted
- Provide alternatives considered
- Include confidence levels

**5. Assumption Auditing**
- Question and validate every assumption
- Re-verify inherited assumptions
- Never trust "facts" without verification
- Document validation procedures

---

## Appendix C: Decision Quick Reference

| Question | Answer |
|----------|--------|
| How do I make Main Claude follow constitutional principles? | Use Output Style (`.claude/output-styles/constitutional.md`) |
| How do I make agents follow constitutional principles? | Embed in agent prompts (⚖️ CONSTITUTIONAL PRINCIPLES section) |
| How do I validate at workflow checkpoints? | Create skills (`.claude/skills/validate-{workflow}/`) |
| How do I enforce knowledge graph quality? | Knowledge Integrity Triad + Hook (mandatory) |
| How do I share standards across team? | CLAUDE.md + git-commit agents and skills |
| How do I prevent bypassing quality gates? | Hooks (system-level, automatic) |
| How do I know what component to use? | See Section 4: Component Decision Tree |

---

## Appendix D: Version History

**Version 1.0** (2025-10-27)
- Initial comprehensive guide
- Covers all 6 layers of constitutional architecture
- Includes decision trees, examples, troubleshooting
- References all Claude Code components

---

**END OF GUIDE**

For questions or clarifications, consult:
- Claude Code Documentation: https://docs.claude.com/en/docs/claude-code
- Project CLAUDE.md: Core operating principles
- This guide: Component-specific reference
