# Skill Templates

Skills are model-invoked functions that Claude Code discovers via LLM analysis of the `description` field. **Keyword optimization is critical** for discoverability.

---

## Directory Structure

```
skills/
├── framework/          # Universal skills (always generated)
│   ├── validate-knowledge.md (✅ Complete template)
│   ├── escalate-uncertainty.md (✅ Complete template)
│   ├── cite-evidence.md (✅ Complete template)
│   ├── validate-assumptions.md (✅ Complete template)
│   ├── multi-method-verify.md (✅ Complete template)
│   └── bridge-compress.md (✅ Complete template)
├── software/           # Software domain skills
│   ├── validate-code.md (⚠️ TODO)
│   ├── pre-commit-review.md (⚠️ TODO)
│   ├── security-scan.md (⚠️ TODO)
│   ├── test-coverage-check.md (⚠️ TODO)
│   └── git-workflow.md (⚠️ TODO)
├── research/           # Research domain skills
│   ├── validate-research.md (⚠️ TODO)
│   ├── validate-citations.md (⚠️ TODO)
│   ├── data-integrity-check.md (⚠️ TODO)
│   ├── peer-review-checklist.md (⚠️ TODO)
│   └── literature-synthesis.md (⚠️ TODO)
├── content/            # Content domain skills
│   └── [skills TBD based on methodology templates]
└── business/           # Business domain skills
    └── [skills TBD based on methodology templates]
```

---

## Skill Template Structure

All skills follow this structure (based on validate-knowledge.md):

```markdown
---
name: {skill-name}
description: {KEYWORD-RICH description with 50-100 keywords for LLM discovery}
category: {framework|software|research|content|business}
generated_by: triads-generator-template
---

# {Skill Title}

## Purpose
{1-2 sentences describing what this skill does}

## Keywords for Discovery
{100+ keywords: synonyms, use cases, problem statements, related terms}

## When to Invoke This Skill
- {Scenario 1}
- {Scenario 2}
- [10-15 specific use cases]

## Skill Procedure

### Step 1: {Action}
{Detailed instructions with code examples}

### Step 2: {Action}
{Detailed instructions}

[5-7 steps total]

## Output Format
{Template showing exact output structure with examples}

## Example Usage
{Concrete scenario showing input → skill invocation → output}

## Integration with Constitutional Principles
{How this skill enforces constitutional principles}
```

---

## Keyword Optimization Strategy

**CRITICAL**: Skills are discovered via LLM analysis of `description` field in YAML frontmatter.

### Description Field Formula

```
description: {primary purpose} {synonym 1} {synonym 2} {use case 1} {use case 2} {problem statement 1} {problem statement 2} {related term 1} {related term 2} [continue 50-100 keywords]
```

### Example (validate-knowledge):
```yaml
description: Validate knowledge graph additions meet confidence thresholds before persisting data. Use when adding nodes to knowledge graph, verifying information accuracy, checking confidence levels, quality control before committing knowledge, ensuring knowledge meets standards, confirming high-confidence facts, validating data integrity, checking knowledge quality, verifying evidence strength, ensuring reliable information, knowledge validation, data validation, confidence check, quality assurance, accuracy verification...
```

**Keyword Categories**:
1. **Primary action verbs**: validate, verify, check, confirm, ensure
2. **Synonyms**: validation, verification, checking, confirmation
3. **Use cases**: "when adding nodes", "before persisting", "quality control"
4. **Problem statements**: "uncertain about accuracy", "need verification"
5. **Related concepts**: confidence, evidence, quality, integrity, reliability
6. **Domain terms**: knowledge graph, nodes, data, information
7. **Quality aspects**: accuracy, standards, thresholds, gates

---

## Framework Skills (Universal - Always Generated)

### 1. validate-knowledge.md (✅ Complete)
**Purpose**: Validate knowledge graph additions meet confidence thresholds

**Keywords**: validate, verify, check, knowledge, confidence, threshold, quality, accuracy, evidence, nodes, graph, validation, verification, quality control, ensure standards, data integrity

**Key Features**:
- Checks confidence ≥ 0.85
- Verifies required fields present
- Validates evidence quality
- Detects conflicts with existing knowledge
- Escalates if validation fails

---

### 2. escalate-uncertainty.md (✅ Complete)
**Purpose**: Handle uncertainty escalation protocol when confidence < 90%

**Keywords**: uncertainty, escalate, low confidence, unclear, ambiguous, uncertain, need clarification, don't know, unsure, unclear requirements, ambiguous instructions, uncertain outcome, confidence below threshold, escalation protocol, request clarification, ask user, uncertainty threshold, uncertainty node, unclear next steps, ambiguous problem, unsure how to proceed, need guidance

**Key Features**:
- Detects uncertainty threshold violation (confidence < 0.90)
- Creates uncertainty nodes in knowledge graph
- Formats escalation message with options
- Resolves conflicts and documents resolution
- Integrates with all constitutional principles

---

### 3. cite-evidence.md (✅ Complete)
**Purpose**: Enforce evidence-based claims with proper citations

**Keywords**: cite, citation, evidence, source, reference, proof, verify source, document evidence, provide evidence, show proof, back up claim, support with evidence, evidence-based, cite sources, reference material, documentation, proof of claim, verifiable evidence, traceable source, evidence chain, substantiate claim, corroborate, validate claim

**Key Features**:
- Evidence hierarchy (Tier 1-5 from direct observation to speculation)
- Domain-specific citation formats (code, academic, business, content)
- Citation completeness validation
- Evidence quality assessment
- Source accessibility verification

---

### 4. validate-assumptions.md (✅ Complete)
**Purpose**: Audit and validate assumptions before proceeding

**Keywords**: assumptions, validate assumptions, check assumptions, verify assumptions, assumption audit, assumption registry, hidden assumptions, implicit assumptions, unverified assumptions, assumption validation, question assumptions, test assumptions, validate before proceeding, assumption check, assumptions made, assumption documentation, identify assumptions, assumption verification

**Key Features**:
- Assumption registry format with validation status
- Multi-method validation by domain
- Re-validation protocol for inherited assumptions
- Risk assessment if assumption wrong
- Handles invalid assumptions with corrective actions

---

### 5. multi-method-verify.md (✅ Complete)
**Purpose**: Cross-validate findings using ≥2 independent methods

**Keywords**: multi-method, cross-validate, verify multiple ways, two methods, independent verification, cross-check, corroborate, multiple sources, verify independently, dual verification, cross-reference, triangulate, multiple verification methods, verify from different angles, independent validation, cross-validation, verify with multiple tools, check multiple sources, corroboration, triangulation

**Key Features**:
- Minimum 2 independent methods requirement
- Independence criteria validation
- Method selection tables by domain (software, research, content, business)
- Cross-validation protocol with conflict resolution
- Combined confidence scoring

---

### 6. bridge-compress.md (✅ Complete)
**Purpose**: Compress knowledge graph to top-N most important nodes for handoffs

**Keywords**: compress, compression, bridge, handoff, top nodes, most important, prioritize, select key information, essential nodes, critical information, context preservation, compress knowledge, reduce context, select top, prioritize information, bridge compression, handoff preparation, context handoff, preserve essential, key findings, important nodes only

**Key Features**:
- Importance scoring algorithm (6 factors: confidence, type, recency, dependencies, evidence, verification)
- Top-N node selection with validation
- Critical information preservation checks
- Handoff summary generation
- Compression audit trail

---

## Domain-Specific Skills

### Software Development Domain

1. **validate-code.md**
   - Keywords: code quality, DRY, SOLID, clean code, code review, refactor, code smell, maintainability, code standards
   - Checks: DRY violations, SOLID principles, function length, naming conventions

2. **pre-commit-review.md**
   - Keywords: pre-commit, lint, format, type check, quality gates, black, flake8, mypy, isort
   - Checks: black formatting, isort imports, flake8 linting, mypy types

3. **security-scan.md**
   - Keywords: security, OWASP, vulnerabilities, SQL injection, XSS, secrets, credentials, security audit
   - Checks: OWASP Top 10, hardcoded secrets, input validation, injection vulnerabilities

4. **test-coverage-check.md**
   - Keywords: test coverage, unit tests, pytest, coverage report, ≥80%, test suite, quality assurance
   - Checks: Coverage ≥80%, edge cases tested, all paths covered

5. **git-workflow.md**
   - Keywords: git, feature branch, conventional commits, pull request, code review, version control
   - Checks: Branch naming, commit message format, PR template

### Research Domain

1. **validate-research.md**
   - Keywords: research methodology, statistical validity, experimental design, hypothesis testing, reproducibility
   - Checks: Study design, sample size, statistical assumptions, reproducibility

2. **validate-citations.md**
   - Keywords: citations, references, APA, MLA, Chicago, bibliography, citation format, academic writing
   - Checks: Citation completeness, format consistency, DOI presence

3. **data-integrity-check.md**
   - Keywords: data integrity, FAIR principles, reproducibility, data quality, data documentation
   - Checks: FAIR compliance, codebook completeness, data quality

4. **peer-review-checklist.md**
   - Keywords: peer review, CONSORT, PRISMA, publication standards, manuscript review
   - Checks: Reporting guidelines, completeness, methodology rigor

5. **literature-synthesis.md**
   - Keywords: literature review, systematic review, meta-analysis, evidence synthesis, research integration
   - Checks: Search strategy, inclusion criteria, synthesis quality

---

## How Skills Are Used

### By Agents (Automatic Invocation)

Agents can invoke skills directly in their procedures:

```markdown
## Step 3: Validate Knowledge Addition

Before adding to knowledge graph, invoke validate-knowledge skill:

[Agent thinks: I should validate this knowledge before adding it]
[Agent uses Skill tool to invoke validate-knowledge]

Result: ✅ APPROVED - Confidence 0.92, all checks passed
Proceeding with knowledge addition...
```

### By Users (Manual Invocation)

Users can directly invoke skills:

```
User: Please use the validate-knowledge skill to check this finding
```

### Skill Discovery

Claude Code discovers skills via LLM analysis of `description` field:

```yaml
# When user says: "Can you validate this knowledge?"
# LLM analyzes all skill descriptions
# Finds match: validate-knowledge (keywords: "validate", "knowledge")
# Invokes skill automatically
```

---

## Skill Generation Priority

**Critical Path** (needed for system to function):
1. ✅ validate-knowledge (Complete)
2. ✅ escalate-uncertainty (Complete)
3. ✅ validate-assumptions (Complete)

**High Priority** (enforce core principles):
4. ✅ cite-evidence (Complete)
5. ✅ multi-method-verify (Complete)
6. ✅ bridge-compress (Complete)

**Domain-Specific** (conditional on domain):
- Software skills (if software-development domain)
- Research skills (if research domain)
- Content skills (if content-creation domain)
- Business skills (if business-analysis domain)

---

## Skill Template Usage by Triad Architect

### If template_availability == "exists":

```python
# Load skill template
skill_template = read_file(f"templates/skills/{category}/{skill_name}.md")

# Customize for generated project
skill_content = skill_template.format(
    project_name=workflow_info['name'],
    domain=domain_type,
    # ... other customizations
)

# Write to generated project
write_file(f".claude/skills/{category}/{skill_name}.md", skill_content)
```

### If template_availability == "needs_creation":

```python
# Generate skill from methodology research
skill_content = generate_custom_skill(
    skill_name=skill_name,
    domain=domain_type,
    methodology_research=methodology_research,
    quality_standards=quality_standards
)

write_file(f".claude/skills/custom/{skill_name}.md", skill_content)
```

---

## Status Summary

| Category | Skills | Complete | Pending |
|----------|--------|----------|---------|
| Framework | 6 | 6 | 0 |
| Software | 5 | 0 | 5 |
| Research | 5 | 0 | 5 |
| Content | TBD | 0 | TBD |
| Business | TBD | 0 | TBD |

**Total**: 6/6 framework skill templates complete ✅

**Critical Path Complete**: All 6 framework skills (universal - always generated) are complete! These enforce constitutional principles across all domains.

**Next Steps**:
1. ✅ Complete validate-knowledge template
2. ✅ Complete escalate-uncertainty template
3. ✅ Complete validate-assumptions template
4. ✅ Complete cite-evidence template
5. ✅ Complete multi-method-verify template
6. ✅ Complete bridge-compress template
7. ⏸️ Create domain-specific skill templates (software, research, content, business)

---

**Pattern Established**: With all 6 framework skills complete, the pattern is fully established. The Triad Architect can follow this pattern to:
- **Copy framework skills** (exists) for all generated projects
- **Generate domain-specific skills** from methodology research OR copy from templates when created
