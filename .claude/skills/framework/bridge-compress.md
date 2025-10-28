---
name: bridge-compress
description: Compress knowledge graph to top-N most important nodes for agent handoffs and context preservation. Use when handing off to next agent, preparing context summary, reducing graph size, selecting key information, prioritizing critical nodes, compressing knowledge for handoff, preserving essential context, selecting most important findings, bridge agent handoff, context compression needed, reduce knowledge graph, select top nodes, prioritize information, key findings only, essential nodes selection, critical information preservation, handoff preparation, context handoff, compress graph, top N nodes, most important nodes, select key nodes, prioritize nodes, critical nodes only, essential findings, important findings only, compress for handoff, prepare handoff summary, select priority nodes, compress context, reduce context size, preserve critical info, handoff context preparation, compress knowledge base, select significant nodes, priority information only, compress for bridge, handoff compression, context size reduction, select vital nodes, compress graph for handoff, preserve key findings, select crucial nodes, compress to essentials, handoff information selection, reduce graph complexity, select high-priority nodes, compress knowledge for transfer, preserve important context, select critical findings, compress for context transfer, handoff data compression, select essential information, compress graph intelligently, preserve high-confidence nodes, select top findings, compress for agent handoff, reduce information overload, select most relevant nodes, compress context intelligently, preserve decision-critical info, select key decisions, compress to top nodes, handoff context compression, select important conclusions, compress knowledge intelligently.
category: framework
generated_by: triads-generator-template
---

# Bridge Compress

## Purpose

Compress large knowledge graphs to the top-N most important nodes for efficient agent handoffs while preserving all critical context, decisions, and findings. Bridge agents use this skill to prepare focused, high-value context for the next triad.

## Keywords for Discovery

compress, compression, bridge, handoff, top nodes, most important, prioritize, select key information, essential nodes, critical information, context preservation, compress knowledge, reduce context, select top, prioritize information, bridge compression, handoff preparation, context handoff, preserve essential, key findings, important nodes only, compress graph, top N, select priority, critical nodes, vital information, significant findings, compress for handoff, prepare handoff, context summary, reduce graph, select crucial, compress to essentials, handoff summary, priority nodes, compress intelligently, preserve critical, high-confidence nodes, important findings, compress context, reduce complexity, select relevant, handoff data, context compression, essential information, preserve decisions, compress knowledge base, select significant, reduce overload, key decisions, compress efficiently, preserve findings, top findings, agent handoff, context transfer, intelligent compression, preserve context, critical findings, compress graph intelligently, handoff context, reduce size, select vital, compress for transfer, preserve important, decision-critical, compress to top N, context size reduction, select high-priority, knowledge compression, handoff preparation, compress for bridge, select most important, preserve key context

## When to Invoke This Skill

Invoke this skill when:
- Bridge agent preparing handoff to next triad
- Knowledge graph exceeds manageable size (>50 nodes)
- Preparing context summary for user
- Need to focus on highest-value information
- Handing off between workflow phases
- Preserving critical context while reducing noise
- Creating executive summary of findings
- Preparing decision package for stakeholders
- Reducing token usage for context windows
- Focusing attention on most important conclusions
- Creating checkpoint of current understanding
- Preparing compact knowledge transfer
- Filtering low-confidence or superseded nodes
- Preserving decision-critical information only
- Creating focused context for specific task
- Archiving completed work with key findings
- Preparing knowledge for long-term storage
- Creating shareable summary of research
- Reducing complexity for clarity
- Prioritizing findings for action

## Skill Procedure

### Step 1: Load Full Knowledge Graph

```markdown
## Knowledge Graph Loading

**Graph Source**: {path_to_graph_file}

**Full Graph Statistics**:
- **Total nodes**: {count}
- **Node types**: {list_of_types}
- **Confidence range**: {min} - {max}
- **Creation timespan**: {first_timestamp} to {last_timestamp}
- **Creating agents**: {list_of_agents}

**Graph Structure**:
```json
{
  "nodes": [
    {
      "node_id": "finding_001",
      "node_type": "Finding",
      "label": "API rate limit is 100 req/sec",
      "confidence": 0.95,
      "evidence": "...",
      "created_by": "domain-researcher",
      "created_at": "2024-10-27T10:00:00Z",
      "importance": null,  // Will be calculated
      "dependencies": ["decision_002"]
    },
    // ... more nodes
  ],
  "edges": [
    {
      "from": "finding_001",
      "to": "decision_002",
      "relationship": "informs"
    }
  ]
}
```

**Compression Target**: Top-{N} nodes (default: N=20)

**Compression Ratio**: {N}/{total} = {percentage}%
```

### Step 2: Calculate Node Importance Scores

**Importance Scoring Algorithm**:

Each node receives an importance score (0.0 - 1.0) based on multiple factors:

```python
def calculate_importance(node):
    """Calculate importance score for a node."""

    # Factor 1: Confidence (0.0 - 1.0)
    confidence_score = node['confidence']

    # Factor 2: Node Type Weight
    type_weights = {
        'Decision': 1.0,        # Highest priority
        'ADR': 1.0,             # Architecture Decision Records
        'Finding': 0.9,         # Research findings
        'Conclusion': 0.9,      # Final conclusions
        'Requirement': 0.8,     # User requirements
        'Task': 0.6,            # Action items
        'Question': 0.5,        # Open questions
        'Note': 0.3,            # General notes
        'Uncertainty': 0.7,     # Unresolved uncertainties (important!)
    }
    type_score = type_weights.get(node['node_type'], 0.5)

    # Factor 3: Recency (more recent = more relevant)
    import datetime
    created = datetime.fromisoformat(node['created_at'])
    now = datetime.now()
    age_days = (now - created).days
    recency_score = 1.0 / (1.0 + age_days / 7.0)  # Decay over weeks

    # Factor 4: Dependency Count (more dependencies = more important)
    dependency_count = len(node.get('dependencies', []))
    dependency_score = min(1.0, dependency_count / 5.0)  # Cap at 5 dependencies

    # Factor 5: Evidence Quality (from cite-evidence skill)
    evidence_tier = node.get('evidence_tier', 3)
    evidence_score = (6 - evidence_tier) / 5.0  # Tier 1=1.0, Tier 5=0.2

    # Factor 6: Verification Method (from multi-method-verify skill)
    verification_method = node.get('verification_method', 'single')
    verification_score = 1.0 if 'multi-method' in verification_method else 0.7

    # Weighted combination
    importance = (
        confidence_score * 0.25 +      # 25% confidence
        type_score * 0.25 +            # 25% node type
        recency_score * 0.15 +         # 15% recency
        dependency_score * 0.15 +      # 15% dependencies
        evidence_score * 0.10 +        # 10% evidence quality
        verification_score * 0.10      # 10% verification method
    )

    return round(importance, 3)
```

**Scoring Results**:

```markdown
## Node Importance Scores

| Rank | Node ID | Label | Type | Confidence | Importance | Reason |
|------|---------|-------|------|------------|------------|--------|
| 1 | decision_042 | Use PostgreSQL for DB | Decision | 0.95 | 0.950 | High confidence decision, multi-method verified |
| 2 | finding_038 | API limit 100 req/sec | Finding | 0.95 | 0.912 | Recent, multi-method, Tier 1 evidence |
| 3 | adr_005 | Authentication Strategy | ADR | 0.92 | 0.905 | Critical architecture decision |
| ... | ... | ... | ... | ... | ... | ... |
| 50 | note_017 | Check this later | Note | 0.60 | 0.234 | Low priority note, no verification |

**Distribution**:
- High importance (≥0.8): {count} nodes
- Medium importance (0.5-0.8): {count} nodes
- Low importance (<0.5): {count} nodes
```

### Step 3: Select Top-N Nodes

```markdown
## Top-N Selection

**Selection Criteria**: Top {N} nodes by importance score

**Selected Nodes**: {N} nodes

### Top {N} Most Important Nodes

**Rank 1: {node_id}** (Importance: {score})
- **Type**: {node_type}
- **Label**: {label}
- **Confidence**: {confidence}
- **Why Important**: {explanation}

**Rank 2: {node_id}** (Importance: {score})
- **Type**: {node_type}
- **Label**: {label}
- **Confidence**: {confidence}
- **Why Important**: {explanation}

[Continue for all N nodes...]

---

### Nodes Excluded: {total - N}

**High-importance nodes excluded** (importance ≥0.7 but not in top-N):
- {node_id}: {label} (importance: {score}) - {reason_for_exclusion}

**Medium/Low importance nodes excluded**: {count}
- These nodes have importance <0.7 and are safely omitted from handoff

---

### Coverage Analysis

**Node Types Represented**:
- Decisions: {count}/{total_decisions} ({percentage}%)
- ADRs: {count}/{total_adrs} ({percentage}%)
- Findings: {count}/{total_findings} ({percentage}%)
- Requirements: {count}/{total_requirements} ({percentage}%)
- Uncertainties: {count}/{total_uncertainties} ({percentage}%)

**Confidence Distribution in Top-N**:
- High (≥0.9): {count} nodes
- Medium (0.8-0.9): {count} nodes
- Lower (<0.8): {count} nodes

**Evidence Quality in Top-N**:
- Tier 1 (Direct Observation): {count}
- Tier 2 (Official Docs): {count}
- Tier 3 (Secondary Sources): {count}
- Tier 4 (Inference): {count}
- Tier 5 (Speculation): {count}

**Verification Status in Top-N**:
- Multi-method verified: {count}
- Single method: {count}
- Unverified: {count}
```

### Step 4: Validate Critical Information Preserved

**Critical Information Checklist**:

```markdown
## Critical Information Validation

**Mandatory Preservation** (must be in top-N):

✅ / ❌ **All Decisions**: {count} decisions total, {count} in top-N
  - Missing decisions (if any): {list}

✅ / ❌ **All ADRs**: {count} ADRs total, {count} in top-N
  - Missing ADRs (if any): {list}

✅ / ❌ **All High-Confidence Findings** (≥0.95): {count} total, {count} in top-N
  - Missing findings (if any): {list}

✅ / ❌ **All Requirements**: {count} requirements total, {count} in top-N
  - Missing requirements (if any): {list}

✅ / ❌ **All Unresolved Uncertainties**: {count} uncertainties total, {count} in top-N
  - Missing uncertainties (if any): {list}

✅ / ❌ **All Multi-Method Verified Nodes** (confidence ≥0.9): {count} total, {count} in top-N
  - Missing verified nodes (if any): {list}

---

**If ANY critical information missing**:

⚠️ **CRITICAL INFORMATION NOT IN TOP-N**

**Problem**: {describe what's missing}

**Solution**: Increase N or manually include critical nodes

**Action Taken**:
- Increased N from {old_N} to {new_N}, OR
- Manually added {count} critical nodes to compressed graph

**Validation**: ✅ All critical information now preserved
```

**Example - Critical Information Check**:

```markdown
## Critical Information Validation

**Mandatory Preservation** (must be in top-N):

✅ **All Decisions**: 8 decisions total, 8 in top-20 (100%)

✅ **All ADRs**: 3 ADRs total, 3 in top-20 (100%)

❌ **All High-Confidence Findings** (≥0.95): 12 findings total, 10 in top-20 (83%)
  - **Missing**: finding_031 "TDD improves quality" (conf: 0.96, importance: 0.78, rank: 22)
  - **Missing**: finding_039 "Dark mode 15% usage" (conf: 0.95, importance: 0.76, rank: 24)

✅ **All Requirements**: 5 requirements total, 5 in top-20 (100%)

✅ **All Unresolved Uncertainties**: 2 uncertainties total, 2 in top-20 (100%)

✅ **All Multi-Method Verified**: 15 nodes total, 14 in top-20 (93%)

---

⚠️ **CRITICAL INFORMATION NOT IN TOP-N**

**Problem**: 2 high-confidence findings (≥0.95) not in top-20

**Solution**: Manually include these findings in compressed graph

**Action Taken**:
- Manually added finding_031 and finding_039 to compressed graph
- New compressed size: 22 nodes (instead of 20)

**Validation**: ✅ All critical information now preserved (100% of high-confidence findings)
```

### Step 5: Create Compressed Graph Structure

```markdown
## Compressed Knowledge Graph

**Compression Summary**:
- **Original size**: {total} nodes
- **Compressed size**: {N} nodes
- **Compression ratio**: {percentage}%
- **Critical info preserved**: ✅ 100%

**Compressed Graph**:

```json
{
  "metadata": {
    "compressed_at": "2024-10-27T22:45:00Z",
    "compressed_by": "bridge-compress-skill",
    "original_node_count": 87,
    "compressed_node_count": 20,
    "compression_ratio": "23%",
    "selection_method": "importance_score_top_N",
    "critical_info_preserved": true
  },
  "nodes": [
    {
      "node_id": "decision_042",
      "node_type": "Decision",
      "label": "Use PostgreSQL for database",
      "description": "...",
      "confidence": 0.95,
      "importance": 0.950,
      "rank": 1,
      "evidence": "...",
      "created_by": "solution-architect",
      "created_at": "2024-10-27T15:00:00Z",
      "verification_method": "multi-method",
      "evidence_tier": 1
    },
    // ... 19 more nodes
  ],
  "edges": [
    // Only edges between nodes in compressed graph
  ],
  "excluded_nodes": {
    "count": 67,
    "summary": "Excluded 67 low-importance nodes (importance <0.75)"
  }
}
```

**Node Type Distribution** (compressed graph):
- Decisions: {count}
- ADRs: {count}
- Findings: {count}
- Requirements: {count}
- Uncertainties: {count}
- Tasks: {count}
- Other: {count}
```

### Step 6: Generate Handoff Summary

```markdown
## Handoff Summary for {Next Agent/Triad}

**Context**: Compressed knowledge from {Current Triad} → {Next Triad}

**Compression**: {total} nodes → {N} nodes ({percentage}% preserved)

---

### 🎯 Key Decisions ({count})

**Decision 1**: {label}
- **Rationale**: {brief explanation}
- **Confidence**: {percentage}%
- **Source**: {node_id}

**Decision 2**: {label}
- **Rationale**: {brief explanation}
- **Confidence**: {percentage}%
- **Source**: {node_id}

[Continue for all decisions...]

---

### 📋 Architecture Decision Records ({count})

**ADR-001**: {title}
- **Context**: {brief context}
- **Decision**: {what was decided}
- **Consequences**: {key consequences}
- **Source**: {node_id}

[Continue for all ADRs...]

---

### 🔍 Critical Findings ({count})

**Finding 1**: {label}
- **Summary**: {brief summary}
- **Evidence**: {evidence_tier}, {verification_method}
- **Confidence**: {percentage}%
- **Source**: {node_id}

[Continue for all findings...]

---

### 📌 Requirements ({count})

**Requirement 1**: {label}
- **Description**: {brief description}
- **Source**: {node_id}

[Continue for all requirements...]

---

### ⚠️ Unresolved Uncertainties ({count})

**Uncertainty 1**: {label}
- **Issue**: {what is uncertain}
- **Resolution Needed**: {what would resolve it}
- **Impact**: {consequences if not resolved}
- **Source**: {node_id}

[Continue for all uncertainties...]

---

### 📊 Quality Metrics

**Confidence Summary**:
- Average confidence: {average}%
- High confidence (≥90%): {count} nodes
- Medium confidence (80-89%): {count} nodes

**Evidence Quality**:
- Tier 1 (Direct Observation): {count} nodes
- Multi-method verified: {count} nodes

**Completeness**:
- All decisions preserved: ✅
- All ADRs preserved: ✅
- All requirements preserved: ✅
- All high-confidence findings: ✅

---

### 🎯 Recommended Next Actions

Based on compressed knowledge, the next agent should:

1. {Recommended action 1 based on decisions}
2. {Recommended action 2 based on findings}
3. {Resolve uncertainty: description}
4. {Implement requirement: description}

---

### 📎 Full Graph Reference

**Original graph location**: {path_to_full_graph}
**Compressed graph location**: {path_to_compressed_graph}

**If you need excluded nodes**: Refer to original graph for complete context
```

### Step 7: Document Compression Audit Trail

```markdown
## Compression Audit Trail

**Compression Event**:
- **Date**: {timestamp}
- **Compressor**: bridge-compress-skill
- **Triggering Agent**: {agent_name}
- **Reason**: {handoff|size_limit|context_reduction}

**Compression Parameters**:
- **Original size**: {total} nodes
- **Target size**: {N} nodes
- **Selection method**: importance_score_top_N
- **Importance weights**: confidence 25%, type 25%, recency 15%, dependencies 15%, evidence 10%, verification 10%

**Quality Assurance**:
- Critical information preserved: ✅ YES / ❌ NO
- All decisions included: ✅ YES / ❌ NO
- All ADRs included: ✅ YES / ❌ NO
- All uncertainties included: ✅ YES / ❌ NO
- High-confidence findings (≥95%): {percentage}% included

**Excluded Nodes Breakdown**:
- Low importance (<0.5): {count} nodes
- Medium importance (0.5-0.7): {count} nodes
- Superseded nodes: {count} nodes
- Duplicate information: {count} nodes

**Validation**:
- Compression validated by: {validator}
- Validation status: ✅ APPROVED / ⚠️ WARNINGS / ❌ REJECTED
- Warnings (if any): {list_of_warnings}

**Archive**:
- Full graph archived at: {path}
- Compressed graph saved at: {path}
- Audit log saved at: {path}
```

## Output Format

```markdown
## Bridge Compression Report

**Original Graph**: {total} nodes
**Compressed Graph**: {N} nodes ({percentage}% compression)

---

### Top-{N} Most Important Nodes

**Rank 1**: {node_id} - {label} (Importance: {score})
**Rank 2**: {node_id} - {label} (Importance: {score})
...
**Rank {N}**: {node_id} - {label} (Importance: {score})

---

### Critical Information Preserved

✅ Decisions: {count}/{total} (100%)
✅ ADRs: {count}/{total} (100%)
✅ Requirements: {count}/{total} (100%)
✅ High-confidence findings: {count}/{total} ({percentage}%)
✅ Uncertainties: {count}/{total} (100%)

---

### Handoff Summary

**Key Decisions**: {list}
**Critical Findings**: {list}
**Unresolved Uncertainties**: {list}
**Recommended Actions**: {list}

---

### Compressed Graph

```json
{compressed_graph_json}
```

---

### Audit Trail

- Compressed at: {timestamp}
- Compressed by: bridge-compress-skill
- Original graph: {path}
- Compressed graph: {path}
- Validation: ✅ APPROVED
```

## Example Usage

**Scenario**: Design Bridge handing off to Implementation Triad

**Input**:
```markdown
Full knowledge graph: 87 nodes (42 findings, 18 decisions, 8 ADRs, 12 requirements, 7 uncertainties)
Handoff: Design Triad → Implementation Triad
Target: Top-20 nodes for implementation context
```

**Skill Invocation**:

```markdown
## Bridge Compression Report

**Original Graph**: 87 nodes
**Compressed Graph**: 22 nodes (25% compression)

---

### Top-22 Most Important Nodes

**Rank 1**: adr_005 - Authentication Strategy: OAuth2 + JWT (Importance: 0.975)
**Rank 2**: decision_042 - Use PostgreSQL for database (Importance: 0.950)
**Rank 3**: decision_038 - React for frontend framework (Importance: 0.945)
**Rank 4**: requirement_012 - Must support 10,000 concurrent users (Importance: 0.920)
**Rank 5**: finding_051 - API rate limit 100 req/sec (dev), 1000 (prod) (Importance: 0.912)
**Rank 6**: adr_008 - Microservices architecture pattern (Importance: 0.905)
**Rank 7**: decision_045 - Redis for session storage (Importance: 0.895)
**Rank 8**: uncertainty_023 - Unresolved: Email service provider (Importance: 0.875)
**Rank 9**: requirement_008 - GDPR compliance required (Importance: 0.870)
**Rank 10**: finding_047 - TDD improves code quality 40% (Importance: 0.865)
**Rank 11**: adr_009 - RESTful API design (Importance: 0.860)
**Rank 12**: decision_049 - Docker for containerization (Importance: 0.855)
**Rank 13**: finding_052 - Dark mode usage only 15% (Importance: 0.850)
**Rank 14**: requirement_015 - ISO 27001 security standards (Importance: 0.845)
**Rank 15**: decision_051 - GitHub Actions for CI/CD (Importance: 0.840)
**Rank 16**: finding_048 - Response time must be <200ms (Importance: 0.835)
**Rank 17**: requirement_018 - Support mobile browsers (Importance: 0.830)
**Rank 18**: decision_052 - pytest for testing framework (Importance: 0.825)
**Rank 19**: finding_053 - Code coverage target ≥80% (Importance: 0.820)
**Rank 20**: uncertainty_025 - Unresolved: Deployment strategy (cloud provider) (Importance: 0.815)
**Rank 21**: finding_031 - TDD reduces bugs by 60% (Importance: 0.780) [manually included - high confidence]
**Rank 22**: finding_039 - User analytics show 85% light mode (Importance: 0.760) [manually included - high confidence]

---

### Critical Information Preserved

✅ **Decisions**: 8/8 (100%)
  - All architectural and technology decisions included

✅ **ADRs**: 3/3 (100%)
  - All Architecture Decision Records included

✅ **Requirements**: 12/12 (100%)
  - All functional and non-functional requirements included

✅ **High-confidence findings** (≥0.95): 12/12 (100%)
  - All verified findings included (2 manually added to ensure 100%)

✅ **Uncertainties**: 2/2 (100%)
  - All unresolved uncertainties flagged for attention

**Validation**: ✅ All critical information preserved

---

### Handoff Summary for Implementation Triad

**Context**: Design work complete → Ready for implementation

**Compression**: 87 nodes → 22 nodes (top 25% by importance)

---

#### 🎯 Key Decisions (8)

**Decision 1**: Use PostgreSQL for database
- **Rationale**: Team expertise (4/5 developers), production experience, JSONB support
- **Confidence**: 95%
- **Source**: decision_042

**Decision 2**: React for frontend framework
- **Rationale**: Team knowledge, component reusability, ecosystem
- **Confidence**: 94%
- **Source**: decision_038

**Decision 3**: Redis for session storage
- **Rationale**: Performance (in-memory), scalability, pub/sub support
- **Confidence**: 89%
- **Source**: decision_045

[Continue for all 8 decisions...]

---

#### 📋 Architecture Decision Records (3)

**ADR-005**: OAuth2 + JWT Authentication Strategy
- **Context**: Need secure, scalable authentication
- **Decision**: OAuth2 for third-party auth, JWT for session tokens
- **Consequences**: Must implement token refresh, key rotation
- **Alternatives Rejected**: Session cookies (doesn't scale), Basic Auth (insecure)
- **Source**: adr_005

**ADR-008**: Microservices Architecture Pattern
- **Context**: Need independent deployment, scaling
- **Decision**: Split into 5 services: auth, user, content, analytics, notification
- **Consequences**: Increased complexity, but better scalability
- **Source**: adr_008

**ADR-009**: RESTful API Design
- **Context**: Need standard API interface
- **Decision**: REST with JSON, versioned endpoints (/v1/)
- **Consequences**: Clear contracts, easy to document
- **Source**: adr_009

---

#### 🔍 Critical Findings (12)

**Finding 1**: API rate limit 100 req/sec (dev), 1000 req/sec (prod)
- **Summary**: Production has 10x higher limit via config override
- **Evidence**: Tier 1 (code + config + runtime), multi-method verified
- **Confidence**: 95%
- **Implication**: Implement rate limiting middleware with env-based config
- **Source**: finding_051

**Finding 2**: TDD improves code quality by 40%
- **Summary**: Meta-analysis of 18 studies shows significant quality improvement
- **Evidence**: Tier 2 (peer-reviewed research), multi-method verified
- **Confidence**: 96%
- **Implication**: Use TDD methodology for all implementation
- **Source**: finding_047

**Finding 3**: Dark mode usage only 15% of users
- **Summary**: Analytics show 85% prefer light mode
- **Evidence**: Tier 1 (analytics data), multi-method verified
- **Confidence**: 95%
- **Implication**: Prioritize light mode, dark mode is nice-to-have
- **Source**: finding_052

[Continue for all 12 findings...]

---

#### 📌 Requirements (12)

**Requirement 1**: Must support 10,000 concurrent users
- **Type**: Performance
- **Priority**: Must-have
- **Verification**: Load testing required
- **Source**: requirement_012

**Requirement 2**: GDPR compliance required
- **Type**: Legal/Compliance
- **Priority**: Must-have
- **Implications**: Data anonymization, right to deletion, consent tracking
- **Source**: requirement_008

**Requirement 3**: ISO 27001 security standards
- **Type**: Security/Compliance
- **Priority**: Must-have
- **Implications**: Access controls, audit logs, encryption
- **Source**: requirement_015

[Continue for all 12 requirements...]

---

#### ⚠️ Unresolved Uncertainties (2)

**Uncertainty 1**: Email service provider
- **Issue**: SendGrid vs AWS SES vs Mailgun undecided
- **Resolution Needed**: Cost analysis + deliverability comparison
- **Impact**: Cannot implement email notifications until resolved
- **Recommendation**: Research and decide before sprint planning
- **Source**: uncertainty_023

**Uncertainty 2**: Deployment strategy (cloud provider)
- **Issue**: AWS vs GCP vs Azure undecided
- **Resolution Needed**: Cost modeling + team expertise assessment
- **Impact**: Cannot finalize infrastructure-as-code until resolved
- **Recommendation**: Resolve in first implementation sprint
- **Source**: uncertainty_025

---

#### 📊 Quality Metrics

**Confidence Summary**:
- Average confidence: 91%
- High confidence (≥90%): 18/22 nodes (82%)
- Medium confidence (80-89%): 4/22 nodes (18%)

**Evidence Quality**:
- Tier 1 (Direct Observation): 8 nodes (36%)
- Tier 2 (Official Docs): 10 nodes (45%)
- Multi-method verified: 16 nodes (73%)

**Completeness**:
- All decisions preserved: ✅ 8/8 (100%)
- All ADRs preserved: ✅ 3/3 (100%)
- All requirements preserved: ✅ 12/12 (100%)
- All high-confidence findings: ✅ 12/12 (100%)
- All uncertainties preserved: ✅ 2/2 (100%)

---

#### 🎯 Recommended Next Actions

Based on compressed knowledge, the Implementation Triad should:

1. **Resolve Uncertainties First**:
   - Research email providers (uncertainty_023)
   - Decide on cloud provider (uncertainty_025)

2. **Set Up Infrastructure**:
   - Implement PostgreSQL database (decision_042)
   - Configure Redis session store (decision_045)
   - Set up Docker containers (decision_049)

3. **Implement Core Architecture**:
   - Follow microservices pattern (adr_008)
   - Implement OAuth2 + JWT auth (adr_005)
   - Build RESTful API (adr_009)

4. **Follow Quality Standards**:
   - Use TDD methodology (finding_047, finding_031)
   - Target ≥80% code coverage (finding_053)
   - Ensure <200ms response time (finding_048)

5. **Meet Requirements**:
   - Implement GDPR compliance (requirement_008)
   - Follow ISO 27001 standards (requirement_015)
   - Support 10K concurrent users (requirement_012)

6. **Deprioritize**:
   - Dark mode (nice-to-have, only 15% usage) (finding_052, finding_039)

---

### 📎 Full Graph Reference

**Original graph location**: `.claude/graphs/design_graph.json`
**Compressed graph location**: `.claude/graphs/design_compressed_for_implementation.json`

**Excluded Nodes**: 65 nodes (details in original graph)
- Low-priority notes: 23 nodes
- Superseded findings: 12 nodes
- Medium-confidence findings (<80%): 18 nodes
- Exploratory questions (resolved): 12 nodes

**If you need excluded context**: Refer to original graph for complete design exploration history

---

### Compressed Graph

```json
{
  "metadata": {
    "compressed_at": "2024-10-27T22:45:00Z",
    "compressed_by": "design-bridge",
    "original_node_count": 87,
    "compressed_node_count": 22,
    "compression_ratio": "25%",
    "selection_method": "importance_score_top_N",
    "critical_info_preserved": true,
    "handoff_to": "implementation-triad"
  },
  "nodes": [
    {
      "node_id": "adr_005",
      "node_type": "ADR",
      "label": "Authentication Strategy: OAuth2 + JWT",
      "importance": 0.975,
      "rank": 1,
      "confidence": 0.95,
      "evidence_tier": 1,
      "verification_method": "multi-method"
    },
    // ... 21 more nodes
  ]
}
```
```

## Integration with Constitutional Principles

**Complete Transparency**:
- Documents full compression algorithm and scoring weights
- Shows all nodes considered with importance scores
- Explains why nodes included or excluded
- Provides audit trail for compression decisions

**Evidence-Based Claims**:
- Importance scores based on measurable factors (confidence, evidence tier, verification method)
- Objective ranking algorithm, not subjective selection
- All scoring factors documented and verifiable

**Assumption Auditing**:
- Documents assumptions about what constitutes "important" (scoring weights)
- Validates that critical information types are preserved
- Questions whether excluded nodes might be needed

**Multi-Method Verification**:
- Uses multiple scoring factors (6 factors) for importance calculation
- Cross-validates that critical nodes are included
- Validates preservation using multiple criteria

**Uncertainty Escalation**:
- Always preserves Uncertainty nodes (high type weight 0.7)
- Flags when critical information might be missing
- Escalates if compression would lose important context

---

**This skill is critical for bridge agents. Use it to create focused, high-value handoffs between workflow phases.**
