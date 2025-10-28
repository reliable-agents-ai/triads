# Knowledge Graph Node Type Registry

**Version**: 1.0.0
**Purpose**: Define standard node types and their data structures for consistent knowledge graph usage

---

## Overview

This registry defines standard node types used across domains. Each type specifies:
- Required fields in `data.*`
- Optional fields in `data.*`
- Typical `handoff.next_stage`
- Examples and use cases

---

## Brief Node Types

Briefs transform vague input into actionable specifications.

### BugBrief

**Domain**: Software Development
**Purpose**: Transform bug report into executable specification

**Required Fields** (`data.*`):
- `summary`: One-sentence bug description
- `reproduction_steps`: Array of steps to trigger bug
- `expected_behavior`: What should happen
- `actual_behavior`: What actually happens
- `acceptance_criteria`: Array of fix requirements

**Optional Fields** (`data.*`):
- `error_messages`: Array of error text/stack traces
- `affected_files`: Array of file paths with line numbers
- `environment`: Object with OS, browser, dependency versions
- `complexity_estimate`: "SIMPLE" | "MEDIUM" | "COMPLEX"
- `priority`: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW"
- `estimated_effort`: Time estimate string

**Typical Handoff**:
- `next_stage`: "implementation-triad" or "senior-developer"

**Example**:
```yaml
node_type: BugBrief
data:
  summary: "Login returns 500 error with valid credentials"
  reproduction_steps:
    - "Navigate to /login"
    - "Enter valid credentials"
    - "Click submit"
  expected_behavior: "Redirect to dashboard"
  actual_behavior: "500 Internal Server Error"
  acceptance_criteria:
    - "Login works with valid credentials"
    - "No 500 errors"
    - "Tests added"
```

---

### FeatureBrief

**Domain**: Software Development
**Purpose**: Transform feature idea into scoped requirements

**Required Fields** (`data.*`):
- `summary`: One-sentence feature description
- `user_story`: "As a [user], I want [goal], so that [benefit]"
- `problem_statement`: What user pain point this solves
- `acceptance_criteria`: Array of completion requirements

**Optional Fields** (`data.*`):
- `proposed_solution`: High-level approach
- `use_cases`: Array of {scenario, steps, expected_outcome}
- `success_metrics`: Array of {metric, target}
- `dependencies`: Array of other features/systems
- `complexity_estimate`: "SIMPLE" | "MEDIUM" | "COMPLEX"
- `priority`: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW"
- `estimated_effort`: Time estimate string

**Typical Handoff**:
- `next_stage`: "validation-triad" (validate need first) or "design-triad"

**Example**:
```yaml
node_type: FeatureBrief
data:
  summary: "Add dark mode toggle to application settings"
  user_story: "As a user, I want dark mode, so that I can use the app at night"
  problem_statement: "Current bright UI causes eye strain in low-light environments"
  acceptance_criteria:
    - "Toggle in settings page"
    - "Persists across sessions"
    - "All UI elements adapt"
```

---

### RefactorBrief

**Domain**: Software Development
**Purpose**: Transform code quality concern into structured refactoring plan

**Required Fields** (`data.*`):
- `summary`: One-sentence refactoring goal
- `scope`: What code to refactor (files, modules, classes)
- `goal`: What to improve (DRY, SOLID, readability, performance)
- `success_criteria`: Array of completion requirements

**Optional Fields** (`data.*`):
- `code_smells_identified`: Array of {smell, location, severity}
- `refactoring_approach`: Strategy description
- `safe_refactoring_steps`: Array of steps
- `risk_level`: "LOW" | "MEDIUM" | "HIGH"
- `affected_files`: Array of file paths
- `tests_required`: Array of test names

**Typical Handoff**:
- `next_stage`: "garden-tending-triad" or "pruner"

**Example**:
```yaml
node_type: RefactorBrief
data:
  summary: "Extract payment processing logic to separate service"
  scope: "src/orders/checkout.py (300 lines)"
  goal: "Single Responsibility Principle - separate order and payment concerns"
  success_criteria:
    - "PaymentService class created"
    - "Checkout class < 100 lines"
    - "All tests still pass"
```

---

## Research Domain Briefs

### ResearchBrief

**Domain**: Research
**Purpose**: Transform research question into investigation plan

**Required Fields** (`data.*`):
- `summary`: One-sentence research question
- `research_question`: Detailed question to investigate
- `methodology`: How to conduct research
- `expected_outcomes`: What answers are sought

**Optional Fields** (`data.*`):
- `hypothesis`: If applicable
- `data_sources`: Where to look
- `success_metrics`: How to measure success
- `timeline`: Time estimate

**Typical Handoff**:
- `next_stage`: "research-analyst"

---

### HypothesisBrief

**Domain**: Research
**Purpose**: Transform vague hypothesis into testable prediction

**Required Fields** (`data.*`):
- `summary`: One-sentence hypothesis
- `hypothesis_statement`: "If [condition], then [outcome], because [reasoning]"
- `test_methodology`: How to test
- `success_criteria`: What confirms/refutes hypothesis

**Optional Fields** (`data.*`):
- `variables`: Independent/dependent variables
- `control_conditions`: What to control for
- `expected_results`: Predicted outcomes

**Typical Handoff**:
- `next_stage`: "research-analyst"

---

## Content Domain Briefs

### ArticleBrief

**Domain**: Content Creation
**Purpose**: Transform topic idea into article outline

**Required Fields** (`data.*`):
- `summary`: One-sentence article topic
- `target_audience`: Who this is for
- `key_points`: Array of main points to cover
- `tone`: "formal" | "casual" | "technical" | "conversational"

**Optional Fields** (`data.*`):
- `word_count_target`: Number
- `keywords_seo`: Array of SEO keywords
- `outline`: Structured outline
- `references`: Sources to cite

**Typical Handoff**:
- `next_stage`: "content-writer"

---

### EditBrief

**Domain**: Content Creation
**Purpose**: Transform edit request into structured edit plan

**Required Fields** (`data.*`):
- `summary`: What to edit
- `edit_type`: "grammar" | "style" | "structure" | "fact-check"
- `target_content`: Reference to content to edit
- `success_criteria`: When edit is complete

**Optional Fields** (`data.*`):
- `style_guide`: Which style guide to follow
- `specific_issues`: Array of known issues
- `priority`: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW"

**Typical Handoff**:
- `next_stage`: "editor"

---

## Specification Node Types

### ADR (Architecture Decision Record)

**Domain**: Software Development
**Purpose**: Document architecture decisions

**Required Fields** (`data.*`):
- `title`: Decision name
- `context`: Background and problem
- `decision`: What was decided
- `rationale`: Why this decision

**Optional Fields** (`data.*`):
- `alternatives_considered`: Array of {option, pros, cons, why_rejected}
- `consequences`: Expected impact
- `status`: "proposed" | "accepted" | "superseded"

**Typical Handoff**:
- `next_stage`: "design-bridge" (for compression)

---

### Specification

**Domain**: Software Development
**Purpose**: Technical specification for implementation

**Required Fields** (`data.*`):
- `component_name`: What's being specified
- `purpose`: What it does
- `interfaces`: APIs, contracts, signatures

**Optional Fields** (`data.*`):
- `data_model`: Schema, database structure
- `dependencies`: Other components needed
- `constraints`: Technical limitations
- `test_strategy`: How to test

**Typical Handoff**:
- `next_stage`: "design-bridge" or "senior-developer"

---

## Implementation Node Types

### Implementation

**Domain**: Software Development
**Purpose**: Document code changes made

**Required Fields** (`data.*`):
- `summary`: What was implemented
- `code_changes`: Description of changes
- `files_modified`: Array of file paths

**Optional Fields** (`data.*`):
- `tests_added`: Array of test names
- `documentation_updated`: Array of doc files
- `breaking_changes`: Boolean and description
- `migration_required`: Boolean and guide

**Typical Handoff**:
- `next_stage`: "test-engineer"

---

### TestResults

**Domain**: Software Development
**Purpose**: Document test execution results

**Required Fields** (`data.*`):
- `test_suite`: Which tests ran
- `tests_passed`: Number
- `tests_failed`: Number
- `coverage_percentage`: Number (0-100)

**Optional Fields** (`data.*`):
- `failed_tests`: Array of {test_name, error, reason}
- `coverage_gaps`: Array of {file, missing_lines}
- `recommendations`: What to fix

**Typical Handoff**:
- `next_stage`: "senior-developer" (if failures) or "gardener-bridge" (if success)

---

## Review Node Types

### Review

**Domain**: Software Development, Content, Research
**Purpose**: Document review findings

**Required Fields** (`data.*`):
- `reviewed_item`: What was reviewed
- `review_type`: "code" | "content" | "research" | "design"
- `findings`: Array of issues found
- `overall_status`: "approved" | "changes_requested" | "rejected"

**Optional Fields** (`data.*`):
- `severity_breakdown`: {critical, high, medium, low counts}
- `recommendations`: What to improve
- `positive_notes`: What was good

**Typical Handoff**:
- `next_stage`: Original creator (if changes needed) or next stage (if approved)

---

## Bridge Node Types

### DesignSummary

**Domain**: Software Development
**Purpose**: Compressed summary of Design triad outputs

**Required Fields** (`data.*`):
- `key_decisions`: Top 5 ADRs summarized
- `architecture_overview`: High-level description
- `implementation_guidance`: How to proceed

**Optional Fields** (`data.*`):
- `critical_components`: Array of components
- `interfaces`: API definitions
- `constraints`: Technical constraints
- `_references.detailed_adrs`: Array of ADR node IDs for deep dive

**Typical Handoff**:
- `next_stage`: "implementation-triad"

**Special**: Created by bridge agents, references multiple upstream nodes in `lineage.created_from_nodes`

---

### ValidationSummary

**Domain**: Research, Software Development
**Purpose**: Compressed summary of Validation triad outputs

**Required Fields** (`data.*`):
- `validation_result`: "PROCEED" | "DEFER" | "REJECT"
- `priority_score`: Number (0-100)
- `key_findings`: Top 3-5 findings
- `recommendation`: What to do next

**Optional Fields** (`data.*`):
- `community_need`: Evidence of demand
- `competitive_analysis`: How this compares
- `risk_assessment`: What could go wrong
- `_references.detailed_research`: Array of research node IDs

**Typical Handoff**:
- `next_stage`: "design-triad" (if PROCEED) or "user" (if DEFER/REJECT)

---

## Special Node Types

### Uncertainty

**Domain**: Universal
**Purpose**: Escalate when confidence < 90%

**Required Fields** (`data.*`):
- `uncertainty_source`: What is unclear
- `question`: Specific question needing answer
- `context`: Why this matters

**Optional Fields** (`data.*`):
- `options`: Array of possible choices with impacts
- `evidence_collected`: What's known so far
- `impact_if_unresolved`: Consequences

**Typical Handoff**:
- `next_stage`: "user"
- `handoff.ready_for_next`: false (blocked)

---

### Approval

**Domain**: Universal
**Purpose**: Record user approval at HITL gates

**Required Fields** (`data.*`):
- `approved_item`: What was approved
- `approval_status`: "approved" | "rejected" | "changes_requested"
- `timestamp`: When approved

**Optional Fields** (`data.*`):
- `comments`: User feedback
- `conditions`: Any conditions on approval

**Typical Handoff**:
- `next_stage`: Next stage in workflow

---

## Domain-Specific Extensions

### Adding Custom Node Types

For custom domains, create node types following this template:

```yaml
node_type: {{CustomType}}
domain: {{custom-domain}}
purpose: {{What this represents}}

# Required fields
data:
  {{field1}}: {{description}}
  {{field2}}: {{description}}

# Optional fields
data_optional:
  {{field3}}: {{description}}

# Typical handoff
handoff:
  next_stage: "{{typical-next-stage}}"
```

**Register custom types** in this file for team consistency.

---

## Node Type Naming Conventions

- **PascalCase**: Node types use PascalCase (e.g., BugBrief, FeatureBrief)
- **Descriptive**: Name describes purpose (not just generic "Input" or "Output")
- **Domain suffix optional**: Add domain suffix if ambiguous (e.g., ResearchBrief vs ArticleBrief)

---

## Version History

- **1.0.0** (2025-10-28): Initial node type registry
  - Software development types: BugBrief, FeatureBrief, RefactorBrief, ADR, Specification, Implementation, TestResults
  - Research types: ResearchBrief, HypothesisBrief
  - Content types: ArticleBrief, EditBrief
  - Bridge types: DesignSummary, ValidationSummary
  - Universal types: Uncertainty, Approval, Review

---

## Related Documentation

- **Standard Output Protocol**: `.claude/protocols/standard-output.md`
- **Knowledge Management Principles**: `docs/KM_PRINCIPLES.md`

---

**When creating new node types, add them to this registry for team visibility and consistency.**
