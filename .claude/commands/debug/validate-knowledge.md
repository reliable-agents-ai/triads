---
description: Validate low-confidence claims and add missing evidence
---

# Validate Knowledge Command

You are manually validating questionable information in the knowledge graph system.

## Your Task

1. **Load KM Queue**: Read `.claude/km_queue.json` to find validation issues:
   - low_confidence nodes (confidence < 0.85)
   - missing_evidence nodes (no evidence field)
2. **Select Target**: Either:
   - Use node specified by user (if they provided node_id or label)
   - Show user the list and ask which to validate
3. **Investigate and Verify**: Act as the verification-agent
4. **Output [GRAPH_UPDATE]**: Either strengthen, mark as Uncertainty, or correct

## Process

### Step 1: Load and Display Validation Issues

```
Reading .claude/km_queue.json...

Found 4 validation issues:

**Low Confidence (2):**

1. **Authentication Decision** (`auth_decision_oauth2`) in discovery triad
   - Current confidence: 0.72
   - Issue: Decision lacks strong evidence

2. **Scaling Strategy** (`scaling_strategy`) in design triad
   - Current confidence: 0.78
   - Issue: Strategy needs verification

**Missing Evidence (2):**

3. **JWT Implementation** (`jwt_impl`) in discovery triad
   - Issue: No citation for implementation details

4. **Performance Claim** (`performance_improvement`) in implementation triad
   - Issue: "API is 3x faster" claim lacks benchmarks

Which would you like me to validate? (Enter number or node_id, or "all")
```

### Step 2: Investigate

Follow verification-agent guidelines (see `.claude/agents/system/verification-agent.md`):

1. **Understand the Claim**: Read current node info, understand what's being claimed
2. **Gather Evidence**: Use multiple verification strategies:
   - **Code Verification**: Grep + Read actual implementation
   - **Documentation Verification**: Search docs, standards, authoritative sources
   - **Testing Verification**: Check test suites, run tests if safe
   - **Historical Verification**: Git history, commits, PRs
3. **Assess Quality**:
   - Strong evidence: 0.90-0.95 confidence
   - Good evidence: 0.85-0.90 confidence
   - Weak evidence: < 0.85 (convert to Uncertainty)
   - No evidence: Convert to Uncertainty
   - Incorrect: Correct the claim

### Step 3: Output [GRAPH_UPDATE]

Choose one of three approaches:

**Option A: Verify and Strengthen**
```
[GRAPH_UPDATE]
type: update_node
node_id: {node_id}
confidence: 0.90
evidence: {comprehensive_evidence_with_multiple_sources}
{additional_properties_if_found}
[/GRAPH_UPDATE]
```

**Option B: Mark as Uncertainty**
```
[GRAPH_UPDATE]
type: update_node
node_id: {node_id}
node_type: Uncertainty
label: {clarify_what_is_uncertain}
description: {explain_why_unverifiable}
confidence: 1.0
[/GRAPH_UPDATE]
```

**Option C: Correct Incorrect Information**
```
[GRAPH_UPDATE]
type: update_node
node_id: {node_id}
label: {corrected_label}
description: {corrected_description}
confidence: 0.95
evidence: {sources_for_correction}
note: Original claim was incorrect. Updated based on verification.
[/GRAPH_UPDATE]

[GRAPH_UPDATE]
type: add_node
node_id: {node_id}_original_claim
node_type: Uncertainty
label: Original claim: {original_claim}
description: This was incorrect and has been corrected
confidence: 1.0
[/GRAPH_UPDATE]

[GRAPH_UPDATE]
type: add_edge
source: {node_id}
target: {node_id}_original_claim
edge_type: replaces
rationale: Verification revealed original claim was incorrect
[/GRAPH_UPDATE]
```

### Step 4: Verify Validation

After outputting [GRAPH_UPDATE]:
- Confirm confidence is ≥ 0.85 OR node is marked as Uncertainty
- Verify evidence is comprehensive with specific citations
- Note resolution will be reflected in km_queue.json on next update

## Example 1: Verifying Low Confidence Claim

**Step 1: Load**
```
Found low-confidence node: Authentication Decision (auth_decision_oauth2)
Current state:
- Type: Decision
- Label: Use OAuth2 with GitHub provider
- Confidence: 0.72 (below 0.85 threshold)
- Evidence: "Discussed in team meeting"
- Triad: discovery
```

**Step 2: Investigate**
```
Let me verify this OAuth2 decision...

1. Checking configuration files:
   - Found config/oauth.yml with GitHub OAuth settings
   - client_id and callback_url configured

2. Checking implementation:
   - src/auth/oauth.py implements OAuth2 flow
   - Uses authlib library (pyproject.toml:28)

3. Checking git history:
   - Commit a1b2c3d "Add GitHub OAuth integration" (2024-09-15)
   - PR #245 has detailed discussion and approval

4. Checking tests:
   - tests/test_oauth.py has comprehensive OAuth flow tests
   - All tests passing

Decision is well-documented and implemented. Can raise confidence to 0.95.
```

**Step 3: Output Update**
```
[GRAPH_UPDATE]
type: update_node
node_id: auth_decision_oauth2
confidence: 0.95
evidence: OAuth2 with GitHub provider confirmed. Configuration in config/oauth.yml:5-12 specifies client_id and callback_url. Implementation in src/auth/oauth.py:1-150 uses authlib 1.2.0 (pyproject.toml:28). Decision made in commit a1b2c3d (2024-09-15) with PR #245 discussion. Verified by passing tests in tests/test_oauth.py::test_github_oauth_flow. Integration documented in docs/authentication.md:45-60.
properties: {
  "decision_date": "2024-09-15",
  "commit": "a1b2c3d",
  "pr_number": "#245",
  "implementation_status": "complete",
  "test_coverage": "comprehensive"
}
[/GRAPH_UPDATE]
```

**Step 4: Verify**
```
✅ Validation complete!

Authentication Decision:
- Confidence raised: 0.72 → 0.95
- Evidence: Comprehensive with 5 sources cited
- Added 5 additional properties
- Status: Verified

The node will be removed from km_queue.json on next graph update.
```

## Example 2: Converting to Uncertainty

**Step 1: Load**
```
Found low-confidence node: Scaling Strategy (scaling_strategy)
Current state:
- Type: Concept
- Label: Horizontal scaling with Kubernetes
- Confidence: 0.78
- Evidence: "Mentioned as future plan"
- Triad: design
```

**Step 2: Investigate**
```
Let me verify this scaling strategy...

1. Checking for Kubernetes configuration:
   - No kubernetes/ directory
   - No deployment.yml or k8s configs found
   - grep "kubernetes" returns no results

2. Checking docs:
   - No mention in docs/deployment.md
   - No mention in docs/architecture.md

3. Checking git history:
   - Found discussion in PR #198 (closed without merge)
   - Suggestion was made but not approved

4. Current deployment:
   - Uses simple docker-compose (docker-compose.yml exists)
   - Single-server deployment

Strategy was discussed but never implemented or decided. Should be Uncertainty.
```

**Step 3: Output Update**
```
[GRAPH_UPDATE]
type: update_node
node_id: scaling_strategy
node_type: Uncertainty
label: Kubernetes scaling strategy status unclear
description: Kubernetes was mentioned as a potential scaling strategy in PR #198, but no configuration exists, no decision was made, and current deployment uses docker-compose on single server. Unclear if this is still planned, abandoned, or under consideration.
confidence: 1.0
[/GRAPH_UPDATE]
```

**Step 4: Verify**
```
✅ Validation complete!

Scaling Strategy:
- Converted to: Uncertainty node
- Rationale: No evidence of implementation or decision
- Current deployment: docker-compose (single server)
- Status: Needs decision

The node is now properly marked as uncertain rather than falsely confident.
```

## Example 3: Correcting Incorrect Information

**Step 1: Load**
```
Found missing-evidence node: Performance Claim (performance_improvement)
Current state:
- Type: Finding
- Label: API is 3x faster after optimization
- Evidence: (missing)
- Triad: implementation
```

**Step 2: Investigate**
```
Let me verify this performance claim...

1. Checking for benchmarks:
   - No benchmarks/ directory
   - No performance tests found
   - grep "benchmark" returns no results

2. Checking git history:
   - Commit b2c3d4e "Optimize database queries"
   - But commit message doesn't mention 3x improvement
   - No performance measurements in commit

3. Checking actual performance:
   - Looking at optimization: Added database index
   - Typical improvement from indexing: 20-50% not 3x

4. Checking tests:
   - tests/test_performance.py exists
   - Latest run shows ~40% improvement, not 3x

Claim of "3x faster" is incorrect. Actual improvement is ~40%.
```

**Step 3: Output Update**
```
[GRAPH_UPDATE]
type: update_node
node_id: performance_improvement
label: API query performance improved by ~40%
description: Database query optimization through indexing improved performance by approximately 40%, as measured by tests/test_performance.py
confidence: 0.95
evidence: Optimization implemented in commit b2c3d4e added index on users.email field. Performance tests in tests/test_performance.py show average query time reduced from 150ms to 90ms (40% improvement). Verified by running tests on 2025-10-09. Original claim of "3x faster" was incorrect.
properties: {
  "optimization_type": "database_indexing",
  "commit": "b2c3d4e",
  "before_avg_ms": 150,
  "after_avg_ms": 90,
  "improvement_percent": 40,
  "test_file": "tests/test_performance.py"
}
note: Original claim of 3x improvement was incorrect. Actual improvement is 40% based on test measurements.
[/GRAPH_UPDATE]

[GRAPH_UPDATE]
type: add_node
node_id: performance_improvement_original_claim
node_type: Uncertainty
label: Original performance claim was inaccurate
description: Initial claim stated "3x faster" but testing shows 40% improvement. Cause: Estimate made without benchmarking. Now corrected with actual measurements.
confidence: 1.0
[/GRAPH_UPDATE]

[GRAPH_UPDATE]
type: add_edge
source: performance_improvement
target: performance_improvement_original_claim
edge_type: corrects
rationale: Verification revealed original estimate was incorrect. Updated with actual benchmark data.
[/GRAPH_UPDATE]
```

**Step 4: Verify**
```
✅ Validation complete!

Performance Claim:
- Corrected: "3x faster" → "40% improvement"
- Evidence: Added benchmark data from tests
- Confidence: 0.95 (verified with measurements)
- Added: Uncertainty node documenting the error
- Status: Corrected and verified

The node now accurately reflects reality with proper evidence.
```

## Constitutional Compliance

### R - Require Evidence
Every validation must result in comprehensive evidence or conversion to Uncertainty.

### T - Thorough over Fast
Take time to verify through multiple sources. Don't rush.

### R - Respect Uncertainty
If you cannot verify, convert to Uncertainty - don't fake evidence.

### T - Test Assumptions
Challenge the original claim. Don't assume it's correct.

## Verification Strategies

### For Code Claims
1. Grep for mentioned code
2. Read actual implementation
3. Check usage patterns
4. Run tests if available

### For Decision Claims
1. Check git history (commits, PRs)
2. Search documentation
3. Look for configuration files
4. Verify implementation exists

### For Performance Claims
1. Find benchmark/test code
2. Check git history for measurements
3. Look for monitoring data
4. Run tests if safe

### For Concept Claims
1. Search authoritative sources (RFCs, official docs)
2. Cross-reference with implementation
3. Check if concept is actually used

## User Arguments

If user provides specific target:
```
/validate-knowledge auth_decision_oauth2
/validate-knowledge "Authentication Decision"
/validate-knowledge all
```

## Error Handling

- **No validation issues found**: Report "No low-confidence or missing-evidence nodes in queue."
- **Node not found**: "Node '{id}' not found in queue. Available: [list]"
- **Cannot verify**: Convert to Uncertainty node

## Related Commands

- `/km-status` - View all KM issues
- `/enrich-knowledge` - Enrich sparse entities

Begin validation now. If no target specified, load and display the list.
