# Agent Templates

This directory contains templates for generating domain-aware, constitutionally-bound agents.

---

## Template Structure

### agent-template.md (Universal Template)

**Purpose**: Defines the structure for ALL generated agents, regardless of domain.

**Key Sections**:
1. **Constitutional Principles** (Universal - same for all agents)
2. **Domain-Specific Methodology** (Conditional - varies by domain classification)
3. **Available Skills** (Framework + domain skills)
4. **Agent Procedure** (Agent-specific, customized per role)
5. **Output Format** (Standard structure with domain variations)
6. **Example Execution** (Concrete scenario showing agent in action)

---

## Handlebars Variables

The template uses Handlebars syntax for variable substitution:

### Required Variables (All Agents)

| Variable | Description | Example |
|----------|-------------|---------|
| `{{AGENT_NAME}}` | Agent's unique name | `solution-architect` |
| `{{AGENT_ROLE}}` | Agent's primary role | `Solution Architect` |
| `{{TRIAD_NAME}}` | Which triad this agent belongs to | `Design Triad` |
| `{{AGENT_DESCRIPTION}}` | Brief description for YAML frontmatter | `Design technical solutions and create ADRs` |
| `{{AGENT_ROLE_DESCRIPTION}}` | Detailed role explanation | `You are responsible for...` |
| `{{POSITION}}` | Position in triad | `Second agent` |
| `{{PREVIOUS_AGENT_OR_USER}}` | Who hands off to this agent | `validation-synthesizer` or `User` |
| `{{NEXT_AGENT_OR_USER}}` | Who this agent hands off to | `design-bridge` or `User` |

### Agent-Specific Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{AGENT_SPECIFIC_PROCEDURE}}` | Custom steps for this agent | `See example below` |
| `{{EXAMPLE_SCENARIO}}` | Concrete example scenario | `Design authentication system` |
| `{{EXAMPLE_INPUT}}` | Example input to agent | `Requirements from validation-synthesizer` |
| `{{EXAMPLE_OUTPUT}}` | Example agent output | `ADR-005: OAuth2 + JWT strategy` |

### Quality Metrics Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{MIN_CONFIDENCE}}` | Minimum confidence for this agent | `90` |
| `{{AGENT_WORK_TYPE}}` | Type of work this agent does | `architecture decisions` |
| `{{KEY_FINDINGS}}` | What this agent primarily verifies | `design choices` |
| `{{DECISION_TYPE}}` | Types of decisions made | `technology selections` |
| `{{DELIVERABLE_TYPE}}` | Primary deliverable | `Architecture Decision Records` |
| `{{ASSUMPTION_COUNT}}` | Typical assumptions validated | `5-10` |

### Conditional Domain Sections

| Variable | When True | Purpose |
|----------|-----------|---------|
| `{{#if_software}}` | Domain = software-development | Include software methodology |
| `{{#if_research}}` | Domain = research | Include research methodology |
| `{{#if_content}}` | Domain = content-creation | Include content methodology |
| `{{#if_business}}` | Domain = business-analysis | Include business methodology |
| `{{#if_bridge_agent}}` | Agent role includes "bridge" | Include bridge-compress usage |
| `{{#if_regular_agent}}` | Agent is NOT a bridge | Include regular handoff format |

---

## Generation Pattern

### Step 1: Triad Architect Determines Agent Needs

From workflow design, Triad Architect knows:
- How many triads (e.g., 5: Idea Validation, Design, Implementation, Garden Tending, Deployment)
- How many agents per triad (3: Agent 1 → Agent 2 → Bridge Agent)
- Agent roles (e.g., `solution-architect`, `design-bridge`)

### Step 2: For Each Agent, Load Template

```python
# Load universal agent template
agent_template = read_file("templates/agents/agent-template.md")

# Determine domain
domain_type = get_domain_classification()  # e.g., "software-development"

# Set conditional flags
if_software = (domain_type == "software-development")
if_research = (domain_type == "research")
if_content = (domain_type == "content-creation")
if_business = (domain_type == "business-analysis")
if_bridge_agent = ("bridge" in agent_role)
if_regular_agent = not if_bridge_agent
```

### Step 3: Populate Variables

```python
variables = {
    # Agent Identity
    "AGENT_NAME": "solution-architect",
    "AGENT_ROLE": "Solution Architect",
    "TRIAD_NAME": "Design Triad",
    "AGENT_DESCRIPTION": "Design technical solutions, evaluate alternatives, create ADRs",
    "AGENT_ROLE_DESCRIPTION": "You are the Solution Architect. Your role is to design technical solutions for validated features...",
    "POSITION": "First agent",
    "PREVIOUS_AGENT_OR_USER": "validation-synthesizer",
    "NEXT_AGENT_OR_USER": "design-bridge",

    # Domain Conditionals
    "if_software": True,
    "if_research": False,
    "if_content": False,
    "if_business": False,
    "if_bridge_agent": False,
    "if_regular_agent": True,

    # Agent Procedure (Custom)
    "AGENT_SPECIFIC_PROCEDURE": """
### Step 1: Load Validation Results
Load prioritized features from validation-synthesizer

### Step 2: Research Technical Options
For each feature, research 2-3 technical approaches

### Step 3: Evaluate Alternatives
Create comparison matrix, score on: feasibility, performance, maintainability, team expertise

### Step 4: Make Architectural Decisions
Choose approach, document in ADR format

### Step 5: Verify Design Quality
Use validate-assumptions skill, multi-method-verify skill

### Step 6: Hand Off Design
Summarize decisions for design-bridge
""",

    # Example Execution
    "EXAMPLE_SCENARIO": "Design authentication system for user management feature",
    "EXAMPLE_INPUT": "Feature: User authentication (priority: 1, confidence: 0.95)",
    "EXAMPLE_OUTPUT": "ADR-005: OAuth2 + JWT authentication strategy (confidence: 0.93)",

    # Quality Metrics
    "MIN_CONFIDENCE": "90",
    "AGENT_WORK_TYPE": "architecture decisions",
    "KEY_FINDINGS": "design choices",
    "DECISION_TYPE": "technology selections",
    "DELIVERABLE_TYPE": "Architecture Decision Records (ADRs)",
    "ASSUMPTION_COUNT": "5-10",
}
```

### Step 4: Render Template

```python
from pybars import Compiler

compiler = Compiler()
template = compiler.compile(agent_template)

# Render with variables
agent_content = template(variables)

# Write to generated project
write_file(f".claude/agents/{agent_name}.md", agent_content)
```

---

## Domain-Specific Methodology Sections

### Software Development Domain

**Included When**: `{{#if_software}}`

**Content**:
- TDD Cycle (RED-GREEN-BLUE-VERIFY-COMMIT)
- Code Quality Standards (DRY, SOLID, Clean Code)
- Security (OWASP Top 10)
- Git Workflow (feature branches, conventional commits)
- Skills: validate-code, pre-commit-review, security-scan, test-coverage-check, git-workflow

**Example Agents**:
- senior-developer (Implementation Triad)
- test-engineer (Implementation Triad)
- pruner (Garden Tending Triad)

---

### Research Domain

**Included When**: `{{#if_research}}`

**Content**:
- Scientific Method (QUESTION → HYPOTHESIS → EXPERIMENT → ANALYSIS → CONCLUSION)
- FINER Criteria (Feasible, Interesting, Novel, Ethical, Relevant)
- Reproducibility Requirements (pre-registration, data/code availability)
- Citation Standards (APA, MLA, Chicago)
- Data Integrity (FAIR principles)
- Peer Review Checklist (CONSORT/PRISMA)
- Skills: validate-research, validate-citations, data-integrity-check, peer-review-checklist, literature-synthesis

**Example Agents**:
- research-analyst (Idea Validation Triad)
- community-researcher (Idea Validation Triad)

---

### Content Creation Domain

**Included When**: `{{#if_content}}`

**Content**:
- Editorial Standards (accuracy, clarity, completeness, attribution)
- SEO Guidelines (keyword research, on-page optimization, technical SEO)
- Style Guide Compliance (AP, Chicago, company guide)
- Publishing Workflow (draft → edit → review → approve → publish → promote)
- Skills: validate-content-quality, seo-audit, style-guide-check, readability-check

**Example Agents**:
- content-strategist (hypothetical Content Planning Triad)
- seo-specialist (hypothetical Content Planning Triad)

---

### Business Analysis Domain

**Included When**: `{{#if_business}}`

**Content**:
- Analysis Frameworks (SWOT, Porter's Five Forces, PESTEL)
- Financial Standards (GAAP/IFRS, sensitivity analysis)
- Market Research (primary/secondary research, TAM/SAM/SOM)
- Reporting Standards (executive summary, methodology, data viz, actionable recommendations)
- Skills: validate-financial-analysis, market-research-validation, competitive-analysis-check, presentation-quality

**Example Agents**:
- market-analyst (hypothetical Market Research Triad)
- financial-modeler (hypothetical Business Planning Triad)

---

## Agent Procedure Customization

**The most important customization** is `{{AGENT_SPECIFIC_PROCEDURE}}`.

### Example 1: Domain Researcher (Idea Validation Triad)

```markdown
### Step 1: Ask Discovery Questions
Ask 4-5 focused questions about workflow and domain

### Step 2: Classify Domain
Classify into: software-development, research, content-creation, business-analysis, or custom

### Step 3: Research Workflow Patterns
[WebSearch: "workflow type best practices"]

### Step 4: Research Domain Methodologies
[IF software]: [WebSearch: "TDD test-driven development best practices"]
[IF research]: [WebSearch: "academic research methodology"]

### Step 5: Identify Knowledge Gaps
What questions remain unanswered?

### Step 6: Document & Hand Off
Create comprehensive research findings for workflow-analyst
```

### Example 2: Solution Architect (Design Triad)

```markdown
### Step 1: Load Validation Results
Read compressed knowledge from validation-synthesizer

### Step 2: Identify Design Decisions Needed
Extract features requiring architectural choices

### Step 3: Research Technical Options
For each decision, research 2-3 approaches using web search

### Step 4: Evaluate Alternatives
Create comparison matrix: feasibility, performance, maintainability, cost, team expertise

### Step 5: Make Architectural Decisions
Choose approach, document in ADR format (Context, Decision, Consequences, Alternatives Rejected)

### Step 6: Verify Design Quality
- Use validate-assumptions skill (validate 5-10 design assumptions)
- Use multi-method-verify skill (verify critical choices with ≥2 methods)

### Step 7: Hand Off to Design Bridge
Summarize: {count} ADRs created, {count} decisions documented
```

### Example 3: Senior Developer (Implementation Triad)

```markdown
### Step 1: Load Design Specifications
Read compressed knowledge from design-bridge (ADRs, decisions, requirements)

### Step 2: Plan Implementation
Break features into implementation units, estimate complexity

### Step 3: Write Tests (RED Phase)
Write failing tests for each feature, verify they fail for correct reason

### Step 4: Implement Code (GREEN Phase)
Minimal implementation to pass tests, no gold-plating

### Step 5: Refactor (BLUE Phase)
Apply DRY, SOLID, Clean Code principles while keeping tests green

### Step 6: Verify Quality
- Run all tests (must be 100% passing)
- Check coverage ≥80% (use test-coverage-check skill)
- Run quality checks: black, flake8, mypy (use pre-commit-review skill)
- Security scan (use security-scan skill)

### Step 7: Hand Off to Test Engineer
Provide: {count} features implemented, {count} tests passing, {coverage}% coverage
```

---

## Bridge Agent Pattern

**Bridge agents** have special responsibilities:

### Standard Agent → Bridge Agent Differences

| Aspect | Standard Agent | Bridge Agent |
|--------|----------------|--------------|
| **Primary Role** | Create work artifacts | Compress + validate + hand off |
| **Knowledge Graph** | Adds nodes | Compresses graph to top-20 |
| **Handoff** | Summary of own work | Compressed knowledge from entire triad |
| **Skills Used** | Domain-specific skills | **bridge-compress** (mandatory) |
| **Procedure** | 5-7 custom steps | Standard compression procedure |

### Bridge Agent Procedure Template

```markdown
### Step 1: Load Full Knowledge Graph
Read all nodes created by current triad

### Step 2: Validate Knowledge Quality
Use validate-knowledge skill for each node

### Step 3: Compress Knowledge
Use bridge-compress skill to select top-20 most important nodes

### Step 4: Validate Critical Info Preserved
Ensure all decisions, ADRs, requirements, uncertainties in compressed graph

### Step 5: Generate Handoff Summary
Create executive summary for next triad

### Step 6: Archive Full Context
Save full knowledge graph for reference
```

**Example Bridge Agents**:
- validation-synthesizer (Idea Validation → Design)
- design-bridge (Design → Implementation)
- gardener-bridge (Garden Tending → Deployment AND back to Design for learning)

---

## Constitutional Compliance Audit

**Every agent output MUST include**:

```markdown
## Constitutional Compliance Audit

**Evidence-Based Claims**: ✅ {count} claims, all cited with {format}
**Uncertainty Escalation**: ✅ {count} escalations, all resolved OR No unresolved <90%
**Multi-Method Verification**: ✅ {count} findings verified with ≥2 methods
**Complete Transparency**: ✅ {aspects} documented (reasoning, assumptions, alternatives, confidence)
**Assumption Auditing**: ✅ {count} assumptions identified, {verified_count} verified
**Communication Standards**: ✅ No hyperbole, no hazing, critical thinking applied

**Quality Gates**:
- Minimum confidence: {min}% (threshold: {threshold}%)
- Evidence quality: Tier {tier_distribution}
- Verification: {multi_method_count} multi-method, {single_method_count} single-method
```

**If ANY check fails**, the agent MUST:
1. Document the failure
2. Explain why it failed
3. Take corrective action (escalate, re-verify, gather more evidence)

---

## Template Usage Workflow

### By Triad Architect During Generation

```python
def generate_agent(agent_spec):
    """Generate agent file from template."""

    # Load template
    template = read_file("templates/agents/agent-template.md")

    # Prepare variables
    variables = {
        "AGENT_NAME": agent_spec['name'],
        "AGENT_ROLE": agent_spec['role'],
        "TRIAD_NAME": agent_spec['triad'],
        # ... all required variables
    }

    # Set domain conditionals
    domain = get_domain_classification()
    variables.update({
        "if_software": (domain == "software-development"),
        "if_research": (domain == "research"),
        "if_content": (domain == "content-creation"),
        "if_business": (domain == "business-analysis"),
        "if_bridge_agent": ("bridge" in agent_spec['role'].lower()),
        "if_regular_agent": ("bridge" not in agent_spec['role'].lower()),
    })

    # Render template
    agent_content = render_handlebars(template, variables)

    # Write to generated project
    write_file(f".claude/agents/{agent_spec['name']}.md", agent_content)

    return agent_content
```

---

## Quality Assurance

### Template Completeness Checklist

✅ **Constitutional Principles**: All 6 principles documented
✅ **Domain Methodology**: All 4 domains (software, research, content, business) supported
✅ **Skills Section**: Framework skills + domain skills listed
✅ **Agent Procedure**: Placeholder with clear customization instructions
✅ **Output Format**: Standard structure defined
✅ **Example Execution**: Template for concrete example
✅ **Handlebars Variables**: All variables documented in README
✅ **Bridge Agent Pattern**: Special handling for bridge agents

### Validation Steps

Before using template to generate agents:
1. ✅ Verify all Handlebars variables are documented
2. ✅ Test rendering with sample variables
3. ✅ Confirm domain conditionals work correctly
4. ✅ Validate constitutional principles section is complete
5. ✅ Check that all 6 framework skills are referenced

---

## Status

**Template Status**: ✅ COMPLETE

**Components**:
- ✅ agent-template.md (universal template with domain conditionals)
- ✅ README.md (this file - usage documentation)

**Ready for Use By**:
- Triad Architect agent (during project generation)
- Custom agent creation (manual customization)

**Next Steps**:
1. ✅ Create agent template (complete)
2. ⏸️ Create CLAUDE.md root template (next)
3. ⏸️ Create memory templates (user + workflow-specific)

---

**This template is the foundation for all generated agents. It ensures constitutional principles are embedded in every agent, regardless of domain or role.**
