#

 ---
name: validate-knowledge
description: Validate knowledge graph additions meet confidence thresholds before persisting data. Use when adding nodes to knowledge graph, verifying information accuracy, checking confidence levels, quality control before committing knowledge, ensuring knowledge meets standards, confirming high-confidence facts, validating data integrity, checking knowledge quality, verifying evidence strength, ensuring reliable information, knowledge validation, data validation, confidence check, quality assurance, accuracy verification, information verification, fact checking knowledge base, validate before commit, ensure quality standards, check reliability, verify before adding, knowledge quality control, data quality check.
category: framework
generated_by: triads-generator-template
---

# Validate Knowledge

## Purpose

Validate that knowledge graph additions meet minimum confidence thresholds and include required evidence before persisting to the graph.

This skill enforces the constitutional principle of Evidence-Based Claims by ensuring all knowledge has verifiable evidence and meets quality standards.

## Keywords for Discovery

validate knowledge, verify knowledge, check knowledge, confirm knowledge, knowledge validation, validate nodes, verify nodes, check nodes, quality control knowledge, knowledge quality, confidence threshold, confidence check, minimum confidence, validate before adding, check before persist, quality assurance knowledge, ensure accuracy, verify accuracy, check accuracy, accuracy validation, evidence validation, verify evidence, check evidence, evidence quality, knowledge integrity, data integrity check, validate graph additions, verify graph data, knowledge graph validation, fact validation, fact verification, validate information, verify information, check information quality, information accuracy, reliable knowledge, trustworthy data, quality standards knowledge, meet standards, pass quality gates, validation protocol, verification protocol

## When to Invoke This Skill

Invoke this skill when:
- Adding new nodes to knowledge graph
- Agent proposes knowledge with confidence < 90%
- Verifying knowledge quality before handoff to next agent
- Quality control checkpoint in workflow
- Bridge agent compressing knowledge (validate before compression)
- Final verification before completing triad work
- Any time knowledge accuracy is uncertain
- Before making decisions based on knowledge
- When knowledge conflicts with existing nodes
- Periodic knowledge graph audits

## Skill Procedure

### Step 1: Extract Knowledge Addition Request

From agent output, identify knowledge addition:

```markdown
[GRAPH_UPDATE]
type: add_node
node_id: finding_cortisol_reduction
node_type: Finding
label: Cortisol Reduction from Meditation
description: Meditation reduced cortisol by 26%
confidence: 0.75
evidence: Meta-analysis showed d=0.62 effect size
source: Smith et al., 2023
[/GRAPH_UPDATE]
```

### Step 2: Check Confidence Threshold

**Minimum Threshold**: 85% (0.85)

```python
confidence = float(node_data['confidence'])

if confidence < 0.85:
    print(f"❌ VALIDATION FAILED: Confidence {confidence} below threshold 0.85")
    return "ESCALATE"  # Trigger uncertainty escalation
else:
    print(f"✅ Confidence check passed: {confidence} >= 0.85")
```

### Step 3: Verify Required Fields Present

Required fields for all nodes:
- `node_id`: Unique identifier
- `node_type`: Classification (Finding, Decision, Task, etc.)
- `label`: Human-readable description
- `confidence`: Numeric 0.0-1.0
- `evidence`: Source of information
- `created_by`: Agent name

```python
required_fields = ['node_id', 'node_type', 'label', 'confidence', 'evidence', 'created_by']

missing_fields = []
for field in required_fields:
    if field not in node_data or not node_data[field]:
        missing_fields.append(field)

if missing_fields:
    print(f"❌ VALIDATION FAILED: Missing required fields: {missing_fields}")
    return "REJECT"
else:
    print(f"✅ All required fields present")
```

### Step 4: Validate Evidence Quality

Evidence must be specific and verifiable:

**Good Evidence** (✅):
- File path + line number: `models/user.py:45`
- URL with date accessed: `https://example.com/study (accessed 2024-01-15)`
- Paper citation: `Smith et al., 2023, Journal of X, 79(3), 234-251`
- Test results: `pytest output: 47/47 tests passed`

**Bad Evidence** (❌):
- Vague: "From research"
- Unverifiable: "I think this is correct"
- Missing source: "It's commonly known that..."

```python
evidence = node_data['evidence']

# Check evidence is not empty or vague
vague_patterns = ['i think', 'probably', 'maybe', 'seems like', 'appears to']
if any(pattern in evidence.lower() for pattern in vague_patterns):
    print(f"❌ VALIDATION FAILED: Evidence is vague: '{evidence}'")
    return "REJECT"

# Check evidence has specificity (contains numbers, URLs, or citations)
has_specificity = any(char.isdigit() for char in evidence) or 'http' in evidence.lower() or '(' in evidence
if not has_specificity:
    print(f"⚠️  WARNING: Evidence may lack specificity: '{evidence}'")
    # Don't reject, but flag for review

print(f"✅ Evidence quality acceptable")
```

### Step 5: Check for Conflicts with Existing Knowledge

```python
# Load existing knowledge graph
existing_nodes = load_graph('.claude/graphs/{triad_name}_graph.json')

# Check if similar node exists with different conclusion
for existing_node in existing_nodes:
    if similar_topic(node_data['label'], existing_node['label']):
        if contradicts(node_data['description'], existing_node['description']):
            print(f"⚠️  CONFLICT DETECTED:")
            print(f"   New: {node_data['label']} (confidence: {node_data['confidence']})")
            print(f"   Existing: {existing_node['label']} (confidence: {existing_node['confidence']})")
            print(f"   Action: Higher confidence node takes precedence")

            if node_data['confidence'] > existing_node['confidence']:
                print(f"   → New node has higher confidence, will replace existing")
            else:
                print(f"   → Existing node has higher confidence, reject new node")
                return "REJECT"
```

### Step 6: Validation Decision

```python
def validate_knowledge_addition(node_data):
    """Validate knowledge addition meets quality standards."""

    # Step 2: Confidence threshold
    if node_data['confidence'] < 0.85:
        return {
            "status": "ESCALATE",
            "reason": f"Confidence {node_data['confidence']} below threshold 0.85",
            "action": "Create uncertainty node, request clarification"
        }

    # Step 3: Required fields
    required_fields = ['node_id', 'node_type', 'label', 'confidence', 'evidence', 'created_by']
    missing = [f for f in required_fields if f not in node_data or not node_data[f]]
    if missing:
        return {
            "status": "REJECT",
            "reason": f"Missing required fields: {missing}",
            "action": "Agent must provide all required fields"
        }

    # Step 4: Evidence quality
    evidence = node_data['evidence']
    vague_patterns = ['i think', 'probably', 'maybe', 'seems like', 'appears to']
    if any(p in evidence.lower() for p in vague_patterns):
        return {
            "status": "REJECT",
            "reason": f"Evidence is vague: '{evidence}'",
            "action": "Provide specific, verifiable evidence"
        }

    # Step 5: Conflict check (simplified)
    # [Would check against existing graph]

    # All checks passed
    return {
        "status": "APPROVED",
        "reason": "All validation checks passed",
        "action": "Proceed with knowledge addition"
    }
```

## Output Format

```markdown
## Knowledge Validation Result

**Node ID**: {node_id}
**Label**: {label}

**Validation Status**: ✅ APPROVED | ⚠️ ESCALATE | ❌ REJECTED

**Checks Performed**:
- Confidence threshold (≥0.85): ✅ PASSED ({confidence})
- Required fields: ✅ PASSED (all present)
- Evidence quality: ✅ PASSED (specific and verifiable)
- Conflict check: ✅ PASSED (no conflicts detected)

**Recommendation**: {APPROVE | ESCALATE | REJECT}

[IF APPROVED]:
✅ Knowledge addition meets quality standards. Proceed with graph update.

[IF ESCALATE]:
⚠️ Confidence below threshold. Create uncertainty node:
```
[GRAPH_UPDATE]
type: add_node
node_id: uncertainty_{original_node_id}
node_type: Uncertainty
label: Uncertain: {original_label}
confidence: {confidence}
reason: Confidence below 0.85 threshold
resolution_needed: {what needs clarification}
[/GRAPH_UPDATE]
```

[IF REJECTED]:
❌ Knowledge addition rejected. Reason: {reason}
Action required: {action}
```

## Example Usage

**Scenario**: Agent proposes knowledge with low confidence

**Input**:
```markdown
[GRAPH_UPDATE]
type: add_node
node_id: finding_user_preference
label: Users prefer dark mode
description: Most users want dark mode feature
confidence: 0.70
evidence: 3 users mentioned it in interviews
created_by: domain-researcher
[/GRAPH_UPDATE]
```

**Skill Invocation**:
```
User: Please invoke the validate-knowledge skill to check this addition
```

**Skill Output**:
```markdown
## Knowledge Validation Result

**Node ID**: finding_user_preference
**Label**: Users prefer dark mode

**Validation Status**: ⚠️ ESCALATE

**Checks Performed**:
- Confidence threshold (≥0.85): ❌ FAILED (0.70 < 0.85)
- Required fields: ✅ PASSED (all present)
- Evidence quality: ⚠️  WARNING (small sample: only 3 users)
- Conflict check: ✅ PASSED

**Recommendation**: ESCALATE

⚠️ Confidence below threshold. This knowledge requires verification before adding.

**Suggested Actions**:
1. Gather more evidence (survey larger sample)
2. Cross-reference with analytics data
3. Check industry research on dark mode preferences

**Create Uncertainty Node**:
```
[GRAPH_UPDATE]
type: add_node
node_id: uncertainty_user_preference_darkmode
node_type: Uncertainty
label: Uncertain: User Dark Mode Preference
confidence: 0.70
reason: Sample size too small (n=3), confidence below 0.85 threshold
evidence_needed: "Survey ≥30 users OR analytics data showing dark mode usage"
resolution_method: "Conduct user survey or analyze existing usage data"
created_by: validate-knowledge-skill
[/GRAPH_UPDATE]
```
```

## Integration with Constitutional Principles

**Evidence-Based Claims**:
- Requires specific, verifiable evidence
- Rejects vague or unsubstantiated claims
- Enforces minimum evidence quality

**Uncertainty Escalation**:
- Automatically escalates when confidence < 85%
- Creates uncertainty nodes for tracking
- Suggests resolution methods

**Multi-Method Verification**:
- Checks multiple quality dimensions (confidence, evidence, conflicts)
- Cross-references with existing knowledge
- Requires corroboration for high-impact decisions

**Complete Transparency**:
- Documents validation decision and reasoning
- Explains why knowledge approved/rejected
- Provides clear action items for rejected knowledge

---

**This skill is critical for maintaining knowledge graph integrity. Use it liberally before any knowledge addition.**
