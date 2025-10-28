# Keyword Optimization Strategy for Skills & Subagents

**SEO/SEM Approach to Maximizing Discoverability**

**Version**: 1.0
**Date**: 2025-10-27
**Purpose**: Optimize skill and subagent descriptions with keyword-rich content to maximize Claude's autonomous discovery

---

## Table of Contents

1. [Discovery Mechanism](#1-discovery-mechanism)
2. [Keyword Strategy Framework](#2-keyword-strategy-framework)
3. [Skills Keyword Optimization](#3-skills-keyword-optimization)
4. [Subagent Keyword Optimization](#4-subagent-keyword-optimization)
5. [Framework Skills (Always Generated)](#5-framework-skills-always-generated)
6. [Triad-Specific Skills (Generated Per Triad)](#6-triad-specific-skills-generated-per-triad)
7. [Keyword Research Process](#7-keyword-research-process)
8. [Testing & Validation](#8-testing--validation)

---

## 1. Discovery Mechanism

### How Skills Are Discovered

**From Claude Code Documentation**:
> "Claude autonomously decides when to use them based on your request and the Skill's description."

**Critical Field**: `description` in YAML frontmatter

**Discovery Process**:
```
User Message
  ↓
Claude's language model analyzes message
  ↓
Matches message intent against skill descriptions
  ↓
Selects most relevant skill(s)
  ↓
Invokes skill
```

**Key Insight**: Description is parsed by LLM - need **semantic keyword coverage**, not just exact matches.

---

### How Subagents Are Discovered

**From Supervisor Logic**:
- Hook-injected (automatic)
- Task tool invocation (manual)
- Description helps supervisor route correctly

**Critical Fields**:
- `description` in YAML frontmatter
- Body content (role, responsibilities, when invoked)

---

## 2. Keyword Strategy Framework

### SEO/SEM Principles Applied

#### 1. Broad Match Keywords (High Volume, Lower Precision)

**Purpose**: Capture wide range of user intents

**Example**: "validate", "check", "verify", "test", "review"

**When to use**: Primary capabilities that apply broadly

---

#### 2. Phrase Match Keywords (Medium Volume, Medium Precision)

**Purpose**: Capture specific scenarios

**Example**: "validate research outputs", "check code quality", "verify test coverage"

**When to use**: Common user phrasing patterns

---

#### 3. Exact Match Keywords (Low Volume, High Precision)

**Purpose**: Capture precise intents

**Example**: "validate knowledge graph additions for evidence and confidence"

**When to use**: Specific technical operations

---

#### 4. Long-Tail Keywords (Very Specific, High Intent)

**Purpose**: Capture detailed scenarios

**Example**: "before saving knowledge to graph check confidence threshold is above 85%"

**When to use**: Complex multi-step operations

---

#### 5. Synonym Clusters (Coverage)

**Purpose**: Cover different ways users express same intent

**Example**:
- validate = verify = check = confirm = ensure = audit = review
- code = implementation = source = program
- test = spec = unit test = integration test

**When to use**: Every description should include synonym clusters

---

#### 6. Action Verbs (Trigger Words)

**Purpose**: Match user action requests

**Example**: validate, check, verify, test, review, audit, analyze, examine, inspect, assess, evaluate

**When to use**: Start of description, in "when to use" section

---

#### 7. Context Keywords (Domain Terms)

**Purpose**: Match specific work contexts

**Example**: research, implementation, deployment, design, refactoring, debugging

**When to use**: Domain-specific skills

---

#### 8. Negative Keywords (Exclusions)

**Purpose**: Prevent irrelevant invocations

**Example**: "Do NOT use for simple questions or information requests"

**When to use**: When skill has narrow scope

---

### Description Template Structure

```markdown
---
name: skill-name
description: |
  [ACTION VERB] [PRIMARY CAPABILITY] [CONTEXT].

  Use when [TRIGGER PHRASE 1], [TRIGGER PHRASE 2], or [TRIGGER PHRASE 3].

  Capabilities: [SYNONYM CLUSTER 1], [SYNONYM CLUSTER 2], [SYNONYM CLUSTER 3].

  Handles: [SPECIFIC SCENARIO 1], [SPECIFIC SCENARIO 2], [LONG-TAIL SCENARIO].

  Keywords: [KEYWORD 1], [KEYWORD 2], [KEYWORD 3], [KEYWORD 4], [KEYWORD 5].
allowed-tools: Read, Grep, Bash
---
```

**Character Budget**: ~500-800 characters (2-3 sentences max)
- Front-load critical keywords
- Include synonyms naturally
- Add trigger phrases
- End with explicit keyword list

---

## 3. Skills Keyword Optimization

### Example: Research Validation Skill

**❌ Poor (Vague, Low Coverage)**:
```yaml
description: Validates research quality
```

**❌ Better (Specific, But Limited)**:
```yaml
description: Validate research outputs for evidence and confidence before proceeding to next triad
```

**✅ Optimal (Keyword-Rich, Broad Coverage)**:
```yaml
description: |
  Validate, verify, and audit research outputs for evidence quality, source citations,
  confidence thresholds, and multi-method verification. Use when research analyst,
  community researcher, or any research agent completes work and before progressing
  to design or implementation phases. Checks include: evidence citations (URLs, file:line),
  confidence scores (≥85% threshold), verification methods (minimum 2 independent sources),
  reasoning transparency (complete chains), and assumption validation. Ensures research
  meets constitutional principles. Keywords: validate research, check evidence, verify sources,
  audit confidence, review findings, assess quality, confirm citations, inspect methodology,
  evaluate research quality, research quality gate, evidence-based validation.
```

**Keyword Analysis**:
- **Action verbs** (11): validate, verify, audit, checks, ensures, confirm, inspect, evaluate, assess, review, progressing
- **Synonym clusters**: validate/verify/audit/check, research/findings, evidence/citations/sources
- **Trigger phrases**: "research analyst completes", "before progressing to", "when research"
- **Context keywords**: research, design, implementation, constitutional principles
- **Technical terms**: confidence threshold, evidence citations, verification methods, reasoning transparency
- **Long-tail**: "research outputs for evidence quality, source citations, confidence thresholds"
- **Explicit keywords list**: Last sentence provides direct keyword matching

**Coverage**: Captures ~20+ different ways users might request research validation

---

### Example: Implementation Validation Skill

**✅ Optimal**:
```yaml
description: |
  Validate, verify, and quality-check code implementation, test coverage, security,
  and documentation before deployment. Use when senior developer, test engineer, or
  implementation agent completes coding work. Checks TDD compliance (tests before code),
  code coverage (≥80%), edge cases (empty input, boundaries, errors), code quality
  (DRY, functions <20 lines, clear naming), security (input validation, no secrets,
  SQL injection prevention, XSS protection), and documentation (comments, README, CHANGELOG).
  Blocks deployment on violations. Keywords: validate code, check tests, verify coverage,
  audit security, review quality, test validation, code review, implementation gate,
  quality assurance, TDD verification, security audit, deployment readiness.
```

**Keyword Analysis**:
- **Action verbs** (10): validate, verify, check, blocks, audit, review, deployment, protection
- **Synonym clusters**: validate/verify/check, code/implementation, test/coverage, security/protection
- **Trigger phrases**: "senior developer completes", "test engineer completes", "before deployment"
- **Context keywords**: implementation, deployment, TDD, security, quality
- **Technical terms**: code coverage, edge cases, DRY, SQL injection, XSS, CHANGELOG
- **Explicit keywords**: 12 direct keywords in last sentence

---

## 4. Subagent Keyword Optimization

### Example: Research Analyst Agent

**❌ Poor**:
```yaml
description: Research ideas by gathering evidence
```

**✅ Optimal**:
```yaml
description: |
  Research, investigate, and analyze ideas, features, enhancements, and technical solutions
  by gathering evidence from multiple sources: web research, codebase analysis, documentation,
  technical papers, blog posts, GitHub repositories, and industry best practices. Use for
  idea validation, feature discovery, technology research, feasibility analysis, competitive
  research, pattern discovery, and industry trend analysis. Validates ideas before design phase.
  Keywords: research ideas, investigate features, analyze solutions, gather evidence, web search,
  codebase analysis, feasibility study, industry patterns, competitive analysis, technology research.
```

**Keyword Analysis**:
- **Action verbs** (8): research, investigate, analyze, gathering, validates
- **Synonym clusters**: research/investigate/analyze, ideas/features/solutions, evidence/sources
- **Trigger phrases**: "idea validation", "feature discovery", "before design phase"
- **Context keywords**: web research, codebase, documentation, GitHub, industry
- **Use cases**: 7 specific scenarios (idea validation, feature discovery, etc.)
- **Source types**: web, codebase, docs, papers, blogs, GitHub, best practices

---

## 5. Framework Skills (Always Generated)

These skills are **ALWAYS generated** regardless of triad composition - they enforce constitutional principles across all workflows.

### 5.1 Validate Knowledge Skill

**File**: `.claude/skills/validate-knowledge.md`

**Purpose**: Constitutional gate for ALL knowledge graph additions

**Keyword-Optimized Description**:
```yaml
---
name: validate-knowledge
description: |
  Validate, verify, and audit knowledge graph additions for evidence quality, confidence
  thresholds, verification methods, and provenance before saving to graph. Use when ANY
  agent creates [GRAPH_UPDATE] blocks, adds nodes, creates edges, or updates knowledge.
  Mandatory validation for: evidence citations (file:line or URL), confidence scores
  (≥85% or marked as Uncertainty), verification methods (minimum 2 independent), provenance
  (created_by, created_at, source fields), and node types (Concept, Decision, Finding, etc.).
  Blocks knowledge save on violations. Constitutional enforcement for all knowledge additions.
  Keywords: validate knowledge, check graph updates, verify evidence, audit confidence,
  knowledge integrity, graph validation, evidence quality, confidence threshold,
  multi-method verification, provenance check, knowledge quality gate, constitutional compliance.
allowed-tools: Read
---
```

**Why Always Generated**: Knowledge graphs are core to triads - every system needs knowledge integrity enforcement.

**Trigger Coverage**:
- "[GRAPH_UPDATE]" in any agent output
- "add node", "create edge", "update knowledge"
- "save to graph", "knowledge addition"
- "graph update", "knowledge graph"

---

### 5.2 Pre-Commit Review Skill

**File**: `.claude/skills/pre-commit-review.md`

**Purpose**: Constitutional TDD enforcement before git commits

**Keyword-Optimized Description**:
```yaml
---
name: pre-commit-review
description: |
  Review, validate, and check code changes before git commit, ensuring TDD compliance,
  test coverage, code quality, and no secrets in code. Use before git commit, git add,
  committing changes, or when ready to commit. Verifies: tests written BEFORE implementation
  (RED-GREEN-BLUE cycle), test coverage ≥80%, all tests passing, no TODO/FIXME without tickets,
  no secrets (.env excluded, no API keys in code), no debugging code (console.log, debugger),
  code quality (DRY, clear naming, functions <20 lines), and commit message quality
  (conventional commits format). Blocks commit on violations.
  Keywords: pre-commit, commit review, validate commit, check before commit, git validation,
  TDD verification, test coverage check, secret detection, code quality review, commit gate,
  ready to commit, commit quality, pre-commit hook, git safety.
allowed-tools: Read, Bash, Grep
---
```

**Why Always Generated**: Git commits are universal - all projects need commit quality gates.

**Trigger Coverage**:
- "git commit", "commit changes", "ready to commit"
- "before commit", "pre-commit", "commit review"
- "check commit", "validate commit"

---

### 5.3 Uncertainty Escalation Skill

**File**: `.claude/skills/escalate-uncertainty.md`

**Purpose**: Constitutional principle enforcement when confidence <90%

**Keyword-Optimized Description**:
```yaml
---
name: escalate-uncertainty
description: |
  Detect, identify, and escalate uncertainty when agent confidence drops below 90%,
  preventing low-confidence claims from becoming facts. Use when agent is unsure, uncertain,
  lacks information, confidence is low, multiple interpretations exist, or ambiguity detected.
  Creates Uncertainty nodes in knowledge graph with: uncertainty source description,
  questions needing answers, confidence assessment (0.0-1.0), required information list,
  and impact analysis. Blocks progression until uncertainty resolved. Constitutional principle:
  Never guess when uncertain - escalate immediately.
  Keywords: escalate uncertainty, detect ambiguity, low confidence, unsure, uncertain,
  lack information, create uncertainty node, confidence below threshold, ambiguity handling,
  uncertainty gate, question escalation, need clarification, confidence assessment.
allowed-tools: Write
---
```

**Why Always Generated**: Uncertainty escalation is constitutional principle - applies to all agents.

**Trigger Coverage**:
- "unsure", "uncertain", "not sure", "don't know"
- "low confidence", "confidence below", "ambiguous"
- "multiple interpretations", "unclear", "confusing"

---

### 5.4 Evidence Citation Skill

**File**: `.claude/skills/cite-evidence.md`

**Purpose**: Constitutional principle enforcement for evidence-based claims

**Keyword-Optimized Description**:
```yaml
---
name: cite-evidence
description: |
  Validate, verify, and ensure all factual claims have cited evidence (URLs, file:line,
  documentation references) before agent completes work. Use when agent makes claims,
  states facts, reports findings, or presents conclusions. Checks: every claim has source
  citation, sources are verifiable (can be checked independently), minimum 2 independent
  sources for key findings, URLs are complete and accessible, file:line references are
  accurate, and no unsupported assertions. Blocks output submission with uncited claims.
  Constitutional principle: Evidence-based claims only.
  Keywords: cite evidence, validate sources, verify citations, check references,
  evidence-based, source validation, citation check, factual claims, reference verification,
  evidence quality, source credibility, citation requirement, evidence gate.
allowed-tools: Read, WebFetch
---
```

**Why Always Generated**: Evidence-based claims are constitutional principle - universal requirement.

---

### 5.5 Assumption Validation Skill

**File**: `.claude/skills/validate-assumptions.md`

**Purpose**: Constitutional principle for assumption auditing

**Keyword-Optimized Description**:
```yaml
---
name: validate-assumptions
description: |
  Identify, document, and validate all assumptions before agent proceeds with work,
  preventing unvalidated assumptions from becoming hidden dependencies. Use when agent
  makes assumptions, inherits beliefs, relies on prior knowledge, or builds on existing work.
  Creates assumption registry with: assumption statement, validation method used, validation
  status (verified/unverified/invalid), risk if assumption wrong, and evidence supporting
  assumption. Blocks progression on unvalidated assumptions. Constitutional principle:
  Question and validate every assumption.
  Keywords: validate assumptions, check assumptions, identify assumptions, assumption audit,
  verify beliefs, hidden assumptions, assumption registry, validate dependencies,
  question assumptions, assumption validation, inherited assumptions, assumption check.
allowed-tools: Read, Grep, WebSearch
---
```

**Why Always Generated**: Assumption auditing is constitutional principle - applies universally.

---

## 6. Triad-Specific Skills (Generated Per Triad)

These skills are generated **BASED ON** the triads in the workflow - each triad type gets corresponding validation skill.

### Skill Generation Matrix

| Triad Type | Generated Skill | Purpose |
|------------|----------------|---------|
| **Research/Investigation** | `validate-research.md` | Validate evidence, sources, confidence |
| **Design/Architecture** | `validate-design.md` | Validate ADRs, alternatives, security |
| **Implementation/Development** | `validate-implementation.md` | Validate tests, coverage, quality |
| **Garden Tending/Refactoring** | `validate-refactoring.md` | Validate safe refactoring, no regressions |
| **Deployment/Release** | `validate-deployment.md` | Validate version bumps, changelog, docs |
| **Testing/QA** | `validate-testing.md` | Validate test quality, edge cases |
| **Security/Audit** | `validate-security.md` | Validate OWASP checks, vulnerabilities |
| **Performance/Optimization** | `validate-performance.md` | Validate benchmarks, profiling |

### Generation Logic

```python
def generate_skills_for_workflow(workflow_yaml):
    """Generate framework skills + triad-specific skills"""

    skills = []

    # 1. ALWAYS generate framework skills (constitutional)
    skills.extend([
        generate_skill("validate-knowledge"),
        generate_skill("pre-commit-review"),
        generate_skill("escalate-uncertainty"),
        generate_skill("cite-evidence"),
        generate_skill("validate-assumptions")
    ])

    # 2. Generate triad-specific skills based on workflow
    triads = workflow_yaml['triad_sequence']

    for triad in triads:
        triad_type = classify_triad_type(triad['name'])

        if triad_type == "research":
            skills.append(generate_skill("validate-research"))
        elif triad_type == "design":
            skills.append(generate_skill("validate-design"))
        elif triad_type == "implementation":
            skills.append(generate_skill("validate-implementation"))
        elif triad_type == "refactoring":
            skills.append(generate_skill("validate-refactoring"))
        elif triad_type == "deployment":
            skills.append(generate_skill("validate-deployment"))
        # ... etc

    return deduplicate(skills)
```

---

### 6.1 Validate Research Skill

**Generated When**: Workflow contains research/investigation/discovery/analysis triads

**Keyword-Optimized Description**:
```yaml
---
name: validate-research
description: |
  Validate, verify, and audit research outputs for evidence quality, source citations,
  confidence thresholds, multi-method verification, and reasoning transparency before
  progressing to design or implementation. Use when research analyst, community researcher,
  domain researcher, or investigation agent completes research work. Validates: evidence
  citations (URLs or file:line), source authority (recent, credible), minimum 2 independent
  sources, confidence ≥85% or marked as Uncertainty, verification methods documented,
  reasoning chain complete, alternatives considered, and assumptions validated. Blocks
  progression on violations. Quality gate for research phase.
  Keywords: validate research, research validation, check evidence, verify sources,
  research quality, audit findings, evidence quality gate, source verification,
  confidence check, research review, investigation validation, analysis quality,
  research gate, feasibility validation.
allowed-tools: Read, Grep
---
```

**Trigger Keywords** (25+):
- validate research, check research, verify research, audit research, review research
- research validation, research quality, research gate, research review
- validate findings, check evidence, verify sources, audit sources
- investigation validation, analysis quality, feasibility check
- evidence quality, source verification, confidence check
- before design, before implementation, research complete

---

### 6.2 Validate Design Skill

**Generated When**: Workflow contains design/architecture/planning triads

**Keyword-Optimized Description**:
```yaml
---
name: validate-design
description: |
  Validate, verify, and audit design outputs including ADRs (Architecture Decision Records),
  security considerations, alternatives analysis, and implementation plans before coding.
  Use when solution architect, design bridge, system designer, or architecture agent completes
  design work. Validates: ADR complete (problem, decision, alternatives, consequences),
  security addressed (OWASP considerations, auth/authz, data protection), minimum 2-3
  alternatives evaluated with trade-offs, implementation approach defined, test strategy
  included, file modification plan present, and rollback strategy documented. Blocks
  implementation on incomplete design. Quality gate for design phase.
  Keywords: validate design, design validation, check ADR, verify architecture,
  design review, architecture validation, ADR quality, security review, design gate,
  solution validation, architecture review, design quality, planning validation,
  design completeness, architecture gate.
allowed-tools: Read
---
```

**Trigger Keywords** (25+):
- validate design, check design, verify design, audit design, review design
- design validation, design quality, design gate, design review
- validate ADR, check architecture, verify solution, audit plan
- architecture validation, solution review, planning quality
- security review, alternatives check, trade-off analysis
- before implementation, before coding, design complete

---

### 6.3 Validate Implementation Skill

**Generated When**: Workflow contains implementation/development/coding triads

**Keyword-Optimized Description**:
```yaml
---
name: validate-implementation
description: |
  Validate, verify, and quality-check code implementation, test coverage, security,
  code quality, and documentation before deployment or merging. Use when senior developer,
  test engineer, coder, programmer, or implementation agent completes coding work.
  Validates: TDD compliance (tests before code, RED-GREEN-BLUE), test coverage ≥80%,
  all tests passing, edge cases tested (empty, null, boundaries, errors), code quality
  (DRY, functions <20 lines, clear naming, type annotations), security (input validation,
  no secrets, SQL injection prevention, XSS protection), and documentation (comments,
  README, CHANGELOG). Blocks deployment on violations. Quality gate for implementation.
  Keywords: validate code, code validation, check tests, verify coverage, implementation review,
  code quality, test validation, security audit, code review, quality assurance,
  TDD verification, deployment readiness, implementation gate, code gate.
allowed-tools: Read, Bash, Grep
---
```

**Trigger Keywords** (30+):
- validate code, check code, verify code, audit code, review code
- code validation, code quality, code review, code gate
- validate implementation, check implementation, implementation review
- test coverage, test validation, TDD check, tests passing
- security audit, security review, vulnerability check
- code quality, quality assurance, QA, quality gate
- before deployment, before merge, ready to deploy

---

### 6.4 Validate Deployment Skill

**Generated When**: Workflow contains deployment/release/publishing triads

**Keyword-Optimized Description**:
```yaml
---
name: validate-deployment
description: |
  Validate, verify, and check deployment readiness including version bumps, changelog updates,
  documentation accuracy, and release artifacts before publishing or deploying. Use when
  release manager, deployment agent, publisher, or deployment engineer prepares release.
  Validates: version bumped in ALL files (package.json, pyproject.toml, plugin.json, etc.),
  CHANGELOG updated with release notes, README reflects new version, documentation links work,
  tests passing in CI, build succeeds, release artifacts created, git tag applied, and
  rollback plan documented. Blocks deployment on missing items. Quality gate for releases.
  Keywords: validate deployment, deployment validation, check release, verify version,
  release readiness, deployment gate, version check, changelog validation, deployment review,
  release validation, publish check, version bump, deployment quality, release gate.
allowed-tools: Read, Bash, Grep
---
```

**Trigger Keywords** (25+):
- validate deployment, check deployment, verify deployment, audit deployment
- deployment validation, deployment readiness, deployment gate
- validate release, check release, verify release, release validation
- version check, version bump, version validation
- changelog check, changelog validation, release notes
- before publish, before deploy, ready to deploy, ready to release

---

## 7. Keyword Research Process

### For Each New Skill

**Step 1: Identify Primary Action**
- What is the skill doing? (validate, check, verify, audit, etc.)

**Step 2: List Synonym Variants** (Target: 5-10 synonyms)
- validate = verify = check = confirm = ensure = audit = review = inspect = assess = evaluate

**Step 3: Identify Context Keywords** (Target: 5-10 contexts)
- research, design, implementation, deployment, testing, security, quality, etc.

**Step 4: List User Trigger Phrases** (Target: 10-20 phrases)
- "before moving to next phase"
- "when research completes"
- "ready to deploy"
- "check quality"
- etc.

**Step 5: Add Technical Terms** (Target: 10-15 terms)
- Domain-specific: ADR, TDD, coverage, CI/CD, etc.
- Operation-specific: commit, merge, deploy, release, etc.

**Step 6: Create Long-Tail Scenarios** (Target: 3-5 scenarios)
- "validate research outputs for evidence quality and confidence thresholds before design phase"

**Step 7: Compile Explicit Keyword List** (Target: 10-15 keywords)
- End description with "Keywords: keyword1, keyword2, keyword3, ..."

---

### Keyword Density Target

**Optimal Description Structure**:
```
Total length: 500-800 characters
Keyword density: 15-25% (75-200 characters of pure keywords)
Unique keywords: 20-30 distinct terms
Synonym coverage: 3-5 variants per concept
Trigger phrases: 5-10 phrases
```

**Example Breakdown**:
```yaml
description: |
  Validate, verify, and audit [3 synonyms] research outputs [context] for evidence quality
  [technical term], source citations [technical term], confidence thresholds [technical term],
  and multi-method verification [technical term] before progressing to design [trigger phrase].
  Use when research analyst [context], community researcher [context], or investigation agent
  [context] completes work [trigger phrase]. Keywords: validate research, research validation,
  check evidence, verify sources [explicit keywords].
```

**Keyword Count**: 25+ keywords/phrases in 150 words

---

## 8. Testing & Validation

### Keyword Coverage Testing

**Method**: Test if skill discovered for various phrasings

**Test Cases for "validate-research" Skill**:

```python
test_phrases = [
    # Direct matches
    "validate the research",
    "check research quality",
    "verify research outputs",

    # Synonym variants
    "audit the research findings",
    "review research evidence",
    "confirm research sources",

    # Trigger phrases
    "research analyst completed work",
    "before moving to design",
    "ready to proceed from research",

    # Technical terms
    "check confidence threshold",
    "verify evidence citations",
    "multi-method verification needed",

    # Long-tail
    "validate research outputs for evidence quality before design phase",

    # Natural language variants
    "is the research good enough to move forward?",
    "should we validate what the researcher found?",
    "check if research meets quality standards"
]

for phrase in test_phrases:
    result = invoke_skill_matching(phrase, available_skills)
    assert "validate-research" in result.matched_skills
```

**Success Criteria**: ≥90% of test phrases correctly match intended skill

---

### A/B Testing Descriptions

**Test**: Compare skill invocation rates for different description variants

**Variant A** (Minimal keywords):
```yaml
description: Validate research quality before design
```

**Variant B** (Moderate keywords):
```yaml
description: Validate and verify research outputs for quality, evidence, and
confidence before progressing to design phase. Use when research completes.
```

**Variant C** (Optimized keywords):
```yaml
description: Validate, verify, and audit research outputs for evidence quality,
source citations, confidence thresholds, and multi-method verification before
progressing to design or implementation. Use when research analyst, community
researcher, or investigation agent completes work. Keywords: validate research,
check evidence, verify sources, audit confidence, research quality gate.
```

**Measure**:
- Invocation accuracy (correct skill for user intent)
- Invocation frequency (how often discovered)
- False positive rate (invoked when shouldn't be)

**Target**: Variant C should have 2-3x higher discovery rate than Variant A

---

## Summary

### Key Principles

1. **Front-Load Keywords**: Most important keywords in first 50 characters
2. **Synonym Coverage**: 3-5 variants per core concept
3. **Trigger Phrases**: 5-10 explicit "use when" phrases
4. **Technical Terms**: 10-15 domain-specific terms
5. **Long-Tail Scenarios**: 3-5 detailed use cases
6. **Explicit Keyword List**: End with "Keywords: ..." list
7. **Natural Language**: Keywords embedded naturally, not stuffed

### Skill Generation Requirements

**Framework Skills** (Always Generate):
- ✅ validate-knowledge.md (5 keywords clusters, 20+ terms)
- ✅ pre-commit-review.md (5 keyword clusters, 20+ terms)
- ✅ escalate-uncertainty.md (5 keyword clusters, 15+ terms)
- ✅ cite-evidence.md (5 keyword clusters, 15+ terms)
- ✅ validate-assumptions.md (5 keyword clusters, 15+ terms)

**Triad-Specific Skills** (Generate Per Workflow):
- ✅ validate-research.md (if research triads present)
- ✅ validate-design.md (if design triads present)
- ✅ validate-implementation.md (if implementation triads present)
- ✅ validate-deployment.md (if deployment triads present)
- ✅ validate-{custom}.md (for custom triad types)

**Each Skill Must Have**:
- ✅ 500-800 character description
- ✅ 20-30 unique keywords
- ✅ 5-10 trigger phrases
- ✅ 3-5 synonym clusters
- ✅ Explicit keyword list at end
- ✅ Natural language flow (not keyword stuffing)

### Subagent Description Requirements

**Each Subagent Must Have**:
- ✅ 300-600 character description
- ✅ 15-25 unique keywords
- ✅ 3-5 trigger phrases
- ✅ 3-4 synonym clusters
- ✅ Explicit use cases (5-7 scenarios)
- ✅ "When to invoke" section with triggers

**Example Length Comparison**:
- ❌ Poor: 20 characters ("Validates research")
- ⚠️ Okay: 100 characters ("Validate research outputs for quality")
- ✅ Good: 300 characters (includes synonyms, triggers)
- ✅ Optimal: 500-800 characters (full keyword optimization)

This keyword strategy ensures skills and subagents are **discoverable by Claude's language model** across a wide range of user phrasings, maximizing autonomous invocation accuracy.
