# Standard Output Protocol

**Version**: 1.0.0
**Authority**: Universal (applies to all skills and agents)
**Purpose**: Standardize handoffs between skills/agents using knowledge graph as communication bus

---

## Overview

All skills and agents communicate through a standardized protocol:

1. **Do work** (research, analysis, transformation, implementation)
2. **Store results** in knowledge graph node (full data)
3. **Return OUTPUT envelope** with node reference (lightweight handoff)
4. **Downstream loads** node by reference and proceeds

**Benefits**:
- ✅ Single source of truth (no data duplication)
- ✅ Lightweight handoffs (node IDs, not full payloads)
- ✅ Traceability built-in (graph lineage)
- ✅ Context compression works naturally (bridge agents compress nodes)
- ✅ Backward references easy (trace provenance)

---

## OUTPUT Envelope Structure

### Required for ALL Skills and Agents

```yaml
OUTPUT:
  # Metadata (universal)
  _meta:
    output_type: "{{brief|specification|implementation|review|analysis}}"
    created_by: "{{skill-name or agent-name}}"
    domain: "{{software-development|research|content|business|custom}}"
    timestamp: "{{ISO 8601 format}}"
    confidence: {{0.0-1.0}}  # How confident in the output

  # Handoff information (universal)
  _handoff:
    next_stage: "{{triad-name|agent-name|user}}"
    graph_node: "{{node_id}}"  # Reference to knowledge graph node
    required_fields: [{{list of fields next stage needs from node.data.*}}]
    optional_fields: [{{list of fields next stage may use from node.data.*}}]

    # Optional: For non-graph data (use sparingly)
    inline_data: {{small-data-if-needed}}
```

### Example: Bug Brief Skill Output

```yaml
OUTPUT:
  _meta:
    output_type: "brief"
    created_by: "bug-brief"
    domain: "software-development"
    timestamp: "2025-10-28T10:30:45Z"
    confidence: 0.95

  _handoff:
    next_stage: "implementation-triad"
    graph_node: "bug_login_500_20251028_103045"
    required_fields: ["summary", "reproduction_steps", "acceptance_criteria"]
    optional_fields: ["error_messages", "affected_files", "environment"]
```

---

## Knowledge Graph Node Structure

### Required for ALL Outputs

```yaml
[GRAPH_UPDATE]
type: add_node
node_id: {{unique_id}}  # Format: {type}_{topic}_{timestamp}
node_type: {{NodeType}}  # See node-types.md for registry

# Standard metadata (ALL nodes)
metadata:
  created_by: "{{skill-name or agent-name}}"
  created_at: "{{ISO 8601 timestamp}}"
  domain: "{{domain}}"
  confidence: {{0.0-1.0}}
  output_type: "{{brief|specification|implementation|review|analysis}}"

# Domain-specific data (flexible structure per node type)
data:
  # Content structure varies by node_type
  # See node-types.md for specific structures
  {{domain_specific_fields}}

# Handoff metadata (how downstream consumes this)
handoff:
  ready_for_next: {{true|false}}
  next_stage: "{{triad-name|agent-name}}"
  required_fields: [{{fields in data.* that next stage needs}}]
  optional_fields: [{{fields in data.* that next stage may use}}]

# Traceability (automatically tracked by graph system)
lineage:
  created_from_node: "{{upstream_node_id}}"  # If derived from another node
  consumed_by_nodes: []  # Populated when other nodes reference this
[/GRAPH_UPDATE]
```

### Example: Bug Brief Node

```yaml
[GRAPH_UPDATE]
type: add_node
node_id: bug_login_500_20251028_103045
node_type: BugBrief

metadata:
  created_by: "bug-brief"
  created_at: "2025-10-28T10:30:45Z"
  domain: "software-development"
  confidence: 0.95
  output_type: "brief"

data:
  summary: "Login form returns 500 error with valid credentials"
  reproduction_steps:
    - "Navigate to /login"
    - "Enter username: test@example.com"
    - "Enter password: valid_password"
    - "Click 'Login' button"
    - "Observe 500 Internal Server Error"
  expected_behavior: "User redirected to dashboard"
  actual_behavior: "500 error, NullPointerException in logs"
  error_messages:
    - "NullPointerException at login.py:45"
    - "AttributeError: 'NoneType' object has no attribute 'email'"
  affected_files:
    - "src/auth/login.py:45"
    - "src/models/user.py:23"
  environment:
    os: "macOS 14.0"
    browser: "Chrome 120"
    dependencies: "Flask 2.3.0, SQLAlchemy 2.0.0"
  acceptance_criteria:
    - "Login works with valid credentials"
    - "500 error no longer occurs"
    - "Test added: test_login_with_valid_credentials()"
    - "No regressions in logout or registration"
  complexity_estimate: "SIMPLE"
  priority: "HIGH"
  estimated_effort: "1-2 hours"

handoff:
  ready_for_next: true
  next_stage: "implementation-triad"
  required_fields: ["summary", "reproduction_steps", "acceptance_criteria"]
  optional_fields: ["error_messages", "affected_files", "environment"]

lineage:
  created_from_node: null  # First node in chain
  consumed_by_nodes: []  # Will be populated when senior-developer loads this
[/GRAPH_UPDATE]
```

---

## Downstream Consumption Pattern

### Standard Loading Procedure

```python
# 1. Agent receives OUTPUT envelope
handoff = receive_input()

# 2. Extract node reference
node_id = handoff._handoff.graph_node

# 3. Load node from knowledge graph
node = graph.load_node(node_id)

# 4. Validate required fields present
required_fields = handoff._handoff.required_fields
for field in required_fields:
    if field not in node.data:
        raise ValueError(f"Missing required field: {field}")

# 5. Extract data for processing
summary = node.data.summary
reproduction_steps = node.data.reproduction_steps
acceptance_criteria = node.data.acceptance_criteria

# 6. Optional: Load optional fields if needed
if "error_messages" in node.data:
    error_messages = node.data.error_messages

# 7. Proceed with work
process_bug_fix(summary, reproduction_steps, acceptance_criteria)

# 8. Create own output node
[GRAPH_UPDATE]
type: add_node
node_id: implementation_bug_fix_20251028_113045
node_type: Implementation
# ... (follows same structure)
[/GRAPH_UPDATE]

# 9. Return OUTPUT envelope with new node reference
OUTPUT:
  _meta:
    output_type: "implementation"
    created_by: "senior-developer"
    confidence: 0.92
  _handoff:
    next_stage: "test-engineer"
    graph_node: "implementation_bug_fix_20251028_113045"
    required_fields: ["code_changes", "files_modified"]
```

### Validation Checklist

Before loading node:
- [ ] OUTPUT envelope contains `_handoff.graph_node`
- [ ] Node ID is valid (not empty, not null)

After loading node:
- [ ] Node exists in graph
- [ ] All `required_fields` present in `node.data.*`
- [ ] Node confidence ≥ 0.85 (or meets threshold for domain)
- [ ] `node.handoff.ready_for_next` == true

---

## Bridge Agent Pattern (Context Compression)

Bridge agents compress multiple upstream nodes into summary node.

### Example: Design Bridge

```yaml
# 1. Load multiple upstream nodes
adrs = graph.load_nodes_by_type("ADR")
specifications = graph.load_nodes_by_type("Specification")

# 2. Compress into summary node
[GRAPH_UPDATE]
type: add_node
node_id: design_summary_20251028_120000
node_type: DesignSummary

metadata:
  created_by: "design-bridge"
  confidence: 0.95

data:
  key_decisions: [{{top 5 ADRs summarized}}]
  architecture_overview: "{{high-level description}}"
  critical_components: [{{list}}]
  interfaces: [{{API definitions}}]
  constraints: [{{technical constraints}}]
  implementation_guidance: "{{how to proceed}}"

handoff:
  ready_for_next: true
  next_stage: "implementation-triad"
  required_fields: ["key_decisions", "architecture_overview", "implementation_guidance"]
  optional_fields: ["critical_components", "interfaces"]

lineage:
  created_from_nodes: [{{all ADR and Spec node IDs}}]  # ← References all source nodes
  consumed_by_nodes: []

# Optional: Include direct references to detailed nodes
_references:
  detailed_adrs: [{{ADR node IDs}}]
  detailed_specifications: [{{Spec node IDs}}]
[/GRAPH_UPDATE]

# 3. Return OUTPUT envelope with compressed node
OUTPUT:
  _meta:
    output_type: "specification"
    created_by: "design-bridge"
    confidence: 0.95
  _handoff:
    next_stage: "implementation-triad"
    graph_node: "design_summary_20251028_120000"  # ← Compressed summary
    required_fields: ["key_decisions", "architecture_overview"]

    # Optional: Provide references to detailed nodes if needed
    detail_nodes:
      adrs: [{{ADR node IDs}}]
      specifications: [{{Spec node IDs}}]
```

**Downstream agent receives**:
- Compressed summary node (lightweight, essential context)
- Optional references to detailed nodes (if deep dive needed)

---

## Node ID Format

### Standard Convention

```
{type}_{topic}_{timestamp}
```

**Examples**:
- `bug_login_500_20251028_103045`
- `feature_darkmode_20251028_110000`
- `refactor_auth_module_20251028_113000`
- `specification_api_architecture_20251028_120000`
- `implementation_bug_fix_20251028_140000`

**Type**: Node type (lowercase)
**Topic**: Brief description (lowercase, underscores)
**Timestamp**: YYYYMMDDTHHmmss format

### Uniqueness Guarantee

Timestamp ensures uniqueness even if same type + topic occur multiple times.

---

## Special Cases

### HITL (Human-in-the-Loop) Gates

When user approval needed:

```yaml
OUTPUT:
  _meta:
    output_type: "specification"
    created_by: "solution-architect"
    confidence: 0.90
  _handoff:
    next_stage: "user"  # ← Goes to user, not next agent
    graph_node: "adrs_summary_20251028_120000"
    required_fields: ["key_decisions", "implementation_plan"]

    # Indicate HITL gate
    approval_required: true
    approval_question: "Do you approve this architecture design?"
```

After user approval:
```yaml
OUTPUT:
  _meta:
    output_type: "approval"
    created_by: "user"
    confidence: 1.0
  _handoff:
    next_stage: "implementation-triad"
    graph_node: "adrs_summary_20251028_120000"  # ← Same node, user approved
    required_fields: ["key_decisions", "implementation_plan"]
    approval_status: "approved"
```

### Uncertainty Escalation

When confidence < 90%:

```yaml
[GRAPH_UPDATE]
type: add_node
node_id: uncertainty_darkmode_priority_20251028_103000
node_type: Uncertainty

metadata:
  created_by: "feature-brief"
  confidence: 0.75  # Below threshold

data:
  uncertainty_source: "Feature priority unclear"
  question: "Is dark mode P0 or P1? Affects resource allocation"
  options:
    - option: "P0 (Critical)"
      impact: "Dedicate 2 developers for 1 week"
    - option: "P1 (High)"
      impact: "1 developer over 2 weeks"
  context: "User survey shows 40% want dark mode, but unclear urgency"

handoff:
  ready_for_next: false  # ← Blocked until resolved
  next_stage: "user"
  required_fields: ["resolution"]
[/GRAPH_UPDATE]

OUTPUT:
  _meta:
    output_type: "uncertainty"
    created_by: "feature-brief"
    confidence: 0.75
  _handoff:
    next_stage: "user"
    graph_node: "uncertainty_darkmode_priority_20251028_103000"
    required_fields: ["resolution"]
    escalation_reason: "Confidence below 90% threshold"
```

---

## Integration with Constitutional Principles

**Evidence-Based Claims**:
- All nodes require evidence (stored in `data.*`)
- Confidence scores indicate certainty
- Lineage tracks provenance (where data came from)

**Multi-Method Verification**:
- Multiple nodes can reference same topic (different perspectives)
- Bridge agents compress multiple nodes (cross-validation)
- Confidence increases when multiple sources agree

**Complete Transparency**:
- Full reasoning chain in knowledge graph
- Lineage shows: A → created → B → consumed_by → C
- Every decision traceable

**Uncertainty Escalation**:
- Confidence < 90% → create Uncertainty node
- Automatically escalates to user
- Blocks downstream until resolved

**Thoroughness**:
- Required fields ensure completeness
- Validation checks prevent missing data
- Bridge agents ensure no information loss

---

## Examples by Domain

### Software Development

**Node Types**: BugBrief, FeatureBrief, RefactorBrief, ADR, Specification, Implementation, TestResults, Review

**Workflow**:
```
bug-brief → BugBrief node → senior-developer → Implementation node → test-engineer → TestResults node
```

### Research

**Node Types**: ResearchBrief, HypothesisBrief, ExperimentBrief, DataAnalysis, Findings, Report

**Workflow**:
```
research-brief → ResearchBrief node → research-analyst → Findings node → validation-synthesizer → Report node
```

### Content Creation

**Node Types**: ArticleBrief, EditBrief, SEOBrief, DraftContent, EditedContent, PublishedContent

**Workflow**:
```
article-brief → ArticleBrief node → content-writer → DraftContent node → editor → EditedContent node
```

---

## Version History

- **1.0.0** (2025-10-28): Initial standard output protocol
  - OUTPUT envelope structure defined
  - Knowledge graph node structure defined
  - Consumption pattern documented
  - Bridge agent pattern documented

---

## Related Documentation

- **Node Type Registry**: `.claude/protocols/node-types.md`
- **Knowledge Management Principles**: `docs/KM_PRINCIPLES.md`
- **Brief Skills Guide**: `docs/BRIEF_SKILLS_GUIDE.md` (coming soon)

---

**This protocol is mandatory for all skills and agents. Violations prevent proper handoffs and break traceability.**
