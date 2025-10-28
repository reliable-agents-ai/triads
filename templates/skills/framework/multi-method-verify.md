---
name: multi-method-verify
description: Cross-validate findings using minimum two independent verification methods for reliable conclusions. Use when verifying claims, validating findings, checking accuracy, need corroboration, cross-validate results, verify with multiple methods, independent verification, triangulate findings, cross-check information, verify from different angles, dual verification, multiple verification methods, corroborate findings, validate with two methods, multi-method validation, cross-validation needed, verify independently, check multiple sources, triangulation required, verify multiple ways, cross-reference information, independent validation, verify using different approaches, corroboration needed, multiple source verification, cross-verify findings, validate from multiple perspectives, multi-source validation, verify with different tools, check with multiple approaches, independent cross-validation, verify through multiple channels, multi-method corroboration, validate using multiple techniques, cross-check with different methods, verify across multiple sources, triangulate evidence, multi-method confirmation, validate independently multiple times, verify with varied approaches, cross-validate independently, corroborate with multiple methods, verify using diverse techniques, multi-angle verification, validate through different methods, cross-method validation, verify with independent sources, multi-method quality check, validate using separate methods, cross-validate with different approaches, verify independently twice, corroborate through multiple sources, validate with distinct methods, multi-method evidence check, verify using independent techniques, cross-verify with multiple tools, validate through separate approaches, multi-method accuracy check, verify with different verification methods, cross-validate using multiple sources, corroborate independently, validate with dual methods, multi-method reliability check.
category: framework
generated_by: triads-generator-template
---

# Multi-Method Verification

## Purpose

Enforce the constitutional principle of Multi-Method Verification by requiring ALL knowledge claims, findings, and conclusions to be validated using a minimum of 2 independent verification methods before being accepted as reliable.

## Keywords for Discovery

multi-method, cross-validate, verify multiple ways, two methods, independent verification, cross-check, corroborate, multiple sources, verify independently, dual verification, cross-reference, triangulate, multiple verification methods, verify from different angles, independent validation, cross-validation, verify with multiple tools, check multiple sources, corroboration, triangulation, verify multiple approaches, cross-verify, multi-source validation, verify different techniques, independent cross-validation, verify through multiple channels, multi-method corroboration, validate using multiple techniques, cross-check different methods, verify across multiple sources, triangulate evidence, multi-method confirmation, validate independently multiple times, verify varied approaches, cross-validate independently, corroborate multiple methods, verify diverse techniques, multi-angle verification, validate different methods, cross-method validation, verify independent sources, multi-method quality check, validate separate methods, cross-validate different approaches, verify independently twice, corroborate through sources, validate distinct methods, multi-method evidence check, verify independent techniques, cross-verify multiple tools, validate separate approaches, multi-method accuracy check, verify different verification methods, cross-validate multiple sources, corroborate independently, validate dual methods, multi-method reliability check, verify using two methods, check from multiple angles, validate with different tools, cross-check multiple ways, verify through various methods, corroborate with separate sources, multi-method fact check, validate using independent approaches

## When to Invoke This Skill

Invoke this skill when:
- Validating any factual claim before accepting as knowledge
- Verifying research findings or conclusions
- Checking technical specifications or measurements
- Confirming design decisions or architectural choices
- Validating test results or quality metrics
- Verifying user requirements or business rules
- Confirming bug fixes or root cause analysis
- Validating security vulnerabilities or compliance
- Checking performance benchmarks or metrics
- Confirming statistical results or data analysis
- Verifying external sources or documentation
- Validating assumptions before proceeding
- Checking conflicting information sources
- Confirming high-stakes decisions
- Before adding high-confidence nodes to knowledge graph
- When single method results seem questionable
- Periodic audit of existing knowledge
- Before handoff to next agent or user
- When constitutional compliance requires verification

## Skill Procedure

### Step 1: Identify Claim Requiring Verification

**Extract the claim to verify**:

```markdown
## Claim Identification

**Claim**: {factual statement to verify}

**Source**: {where claim originated}
- Agent output
- User statement
- Documentation
- External source
- Previous knowledge node

**Confidence (single method)**: {percentage}%

**Verification Requirement**:
- **High-stakes claim**: YES / NO
- **Conflicts with existing knowledge**: YES / NO
- **Low initial confidence (<90%)**: YES / NO

**Minimum Methods Required**: 2 (constitutional standard)
**Recommended Methods**: {2-3 based on claim type}
```

**Examples of Claims Requiring Verification**:

```markdown
✅ **Software Development**:
- "The API rate limit is 100 requests/second"
- "All tests pass with 95% coverage"
- "The database supports ACID transactions"

✅ **Research**:
- "Meditation reduces cortisol by 26%"
- "Sample size provides 80% statistical power"
- "Data follows normal distribution"

✅ **Business**:
- "Market size is $4.2B TAM"
- "Competitor A charges $99/month"
- "Customer churn rate is 5% monthly"

✅ **Content**:
- "Article has 1,245 impressions"
- "Keyword difficulty score is 45"
- "Reading level is grade 8"
```

### Step 2: Select Independent Verification Methods

**Independence Criteria**:

Two methods are **independent** if they:
1. Use different data sources
2. Use different tools/techniques
3. Use different assumptions
4. Could fail independently (one passing doesn't guarantee the other passes)

**❌ NOT Independent** (avoid these pairs):
```markdown
- Reading file + reading same file again
- Running test once + running same test again
- Checking documentation page 1 + checking same page again
- One person's opinion + same person's rephrased opinion
```

**✅ Independent** (use these pairs):
```markdown
- Reading code + running tests
- Documentation + runtime verification
- Static analysis + dynamic testing
- Primary source + secondary source
- Automated tool + manual inspection
- Quantitative analysis + qualitative analysis
```

**Verification Methods by Domain**:

#### Software Development

| Method | Description | Use For |
|--------|-------------|---------|
| **Code Inspection** | Read source code directly | API behavior, logic, structure |
| **Runtime Testing** | Execute code with test cases | Actual behavior, edge cases |
| **Documentation Check** | Official docs, API specs | Specifications, contracts |
| **Static Analysis** | Tools: mypy, flake8, pylint | Type errors, code smells |
| **Dynamic Analysis** | Profiling, debugging, logging | Performance, runtime behavior |
| **Git History** | Commits, blame, tags | When feature added, who changed |
| **Dependency Check** | requirements.txt, package.json | Library versions, availability |
| **Configuration Review** | Config files, env vars | Settings, limits, thresholds |

#### Research

| Method | Description | Use For |
|--------|-------------|---------|
| **Literature Review** | Published papers, meta-analyses | Scientific consensus, prior findings |
| **Statistical Analysis** | Calculate statistics from raw data | Effect sizes, significance, power |
| **Data Visualization** | Plot distributions, relationships | Patterns, outliers, assumptions |
| **Replication Analysis** | Re-run analysis with same data | Reproducibility, correctness |
| **Peer Review** | Expert evaluation | Methodology quality, validity |
| **Pre-registration Check** | Compare to registered protocol | Protocol adherence, p-hacking |
| **Methodological Assessment** | Evaluate study design | Internal validity, confounds |
| **Data Quality Check** | Missing data, outliers, errors | Data integrity, reliability |

#### Content Creation

| Method | Description | Use For |
|--------|-------------|---------|
| **Analytics Tools** | Google Analytics, Search Console | Traffic, engagement, rankings |
| **SEO Tools** | Ahrefs, SEMrush, Moz | Keyword metrics, competition |
| **Readability Tools** | Hemingway, Grammarly | Reading level, clarity |
| **Style Guide Check** | AP, Chicago, company guide | Style compliance, consistency |
| **Fact-Checking Sources** | Snopes, fact-check.org | Accuracy, misinformation |
| **Plagiarism Tools** | Turnitin, Copyscape | Originality, duplication |
| **User Testing** | Surveys, interviews, feedback | User perception, usability |
| **Competitive Analysis** | Analyze competitor content | Market positioning, gaps |

#### Business Analysis

| Method | Description | Use For |
|--------|-------------|---------|
| **Market Research Reports** | Gartner, Forrester, IDC | Market size, trends, forecasts |
| **Financial Analysis** | 10-K, 10-Q, earnings calls | Company financials, growth |
| **Competitive Intelligence** | Pricing pages, product demos | Feature comparison, positioning |
| **Customer Data** | CRM, surveys, interviews | Customer needs, pain points |
| **Industry Statistics** | Trade associations, government | Industry benchmarks, standards |
| **SWOT Analysis** | Strengths, weaknesses, opportunities, threats | Strategic assessment |
| **Porter's Five Forces** | Competitive dynamics framework | Industry attractiveness |
| **Financial Modeling** | Build model from assumptions | Projections, scenarios, valuation |

### Step 3: Execute Verification Method 1

```markdown
## Verification Method 1: {method_name}

**Method Type**: {code_inspection | runtime_testing | documentation | etc.}

**Independence**: Primary method (first verification)

**Execution**:
{Detailed steps of how verification was performed}

**Evidence Collected**:
```
{Raw output, screenshots, logs, data}
```

**Finding**: {what this method revealed}

**Result**:
- ✅ SUPPORTS claim
- ❌ REFUTES claim
- 🔄 PARTIALLY SUPPORTS (with caveats)
- ⚠️ INCONCLUSIVE (method failed or insufficient data)

**Confidence (Method 1 alone)**: {percentage}%

**Limitations**:
- {what this method cannot verify}
- {assumptions this method relies on}
- {potential sources of error}
```

**Example - Software Development**:

```markdown
## Verification Method 1: Code Inspection

**Method Type**: Code Inspection

**Independence**: Primary method

**Execution**:
1. Located API rate limiting code
2. Read file: api/middleware/rate_limiter.py
3. Found RateLimiter class configuration

**Evidence Collected**:
```python
# api/middleware/rate_limiter.py:15-20
class RateLimiter:
    def __init__(self):
        self.max_requests = 100  # requests per second
        self.window = 1.0  # seconds
```

**Finding**: Code shows max_requests = 100 per 1.0 second window

**Result**: ✅ SUPPORTS claim ("API rate limit is 100 requests/second")

**Confidence (Method 1 alone)**: 85%

**Limitations**:
- Only verifies code configuration, not actual runtime behavior
- Doesn't verify if config is overridden by environment variables
- Doesn't confirm if middleware is actually enabled
```

### Step 4: Execute Verification Method 2 (Independent)

```markdown
## Verification Method 2: {method_name}

**Method Type**: {different_from_method_1}

**Independence**: ✅ Verified independent from Method 1
- Different data source: {yes|no} - {explanation}
- Different technique: {yes|no} - {explanation}
- Different assumptions: {yes|no} - {explanation}
- Can fail independently: {yes|no} - {explanation}

**Execution**:
{Detailed steps}

**Evidence Collected**:
```
{Raw output}
```

**Finding**: {what this method revealed}

**Result**:
- ✅ SUPPORTS claim
- ❌ REFUTES claim
- 🔄 PARTIALLY SUPPORTS
- ⚠️ INCONCLUSIVE

**Confidence (Method 2 alone)**: {percentage}%

**Limitations**:
- {what this method cannot verify}
```

**Example - Software Development (continued)**:

```markdown
## Verification Method 2: Documentation Check

**Method Type**: Documentation Check

**Independence**: ✅ Verified independent from Method 1
- Different data source: YES (API docs vs source code)
- Different technique: YES (reading docs vs reading code)
- Different assumptions: YES (docs could be outdated, code is ground truth)
- Can fail independently: YES (docs could be wrong while code is correct, or vice versa)

**Execution**:
1. Checked API documentation
2. Located rate limiting section
3. Read official API docs at docs/api-limits.md

**Evidence Collected**:
```markdown
# docs/api-limits.md:12-15

## Rate Limits

All API endpoints are rate-limited to **100 requests per second** per IP address.

Exceeding this limit returns HTTP 429 (Too Many Requests).
```

**Finding**: Documentation states 100 requests/second limit

**Result**: ✅ SUPPORTS claim

**Confidence (Method 2 alone)**: 90%

**Limitations**:
- Documentation could be outdated
- Doesn't verify actual runtime enforcement
```

### Step 5: Cross-Validate Results

```markdown
## Cross-Validation

**Methods Used**:
1. {Method 1}: {result}
2. {Method 2}: {result}

**Agreement Analysis**:

| Aspect | Method 1 | Method 2 | Agreement |
|--------|----------|----------|-----------|
| {aspect_1} | {finding} | {finding} | ✅ / ❌ |
| {aspect_2} | {finding} | {finding} | ✅ / ❌ |

**Overall Agreement**: {percentage}%

**Cross-Validation Result**:

[IF both methods SUPPORT]:
✅ **VERIFIED** - Claim supported by 2 independent methods

[IF both methods REFUTE]:
❌ **REFUTED** - Claim contradicted by 2 independent methods

[IF methods CONFLICT]:
⚠️ **CONFLICT DETECTED** - Methods disagree
- Method 1 says: {finding}
- Method 2 says: {finding}
- Discrepancy: {explanation}
- **Action Required**: Execute Method 3 to resolve conflict

[IF one INCONCLUSIVE]:
🔄 **PARTIAL VERIFICATION** - Only 1 method successful
- **Action Required**: Execute alternative Method 2

**Combined Confidence**:
- Method 1 alone: {conf_1}%
- Method 2 alone: {conf_2}%
- **Cross-validated confidence**: {combined}%

Formula: Combined = (conf_1 + conf_2) / 2 + bonus
- Bonus: +10% if both methods agree
- Penalty: -20% if methods conflict
```

**Example - Cross-Validation**:

```markdown
## Cross-Validation

**Methods Used**:
1. Code Inspection: ✅ SUPPORTS (100 req/sec in code)
2. Documentation: ✅ SUPPORTS (100 req/sec in docs)

**Agreement Analysis**:

| Aspect | Method 1 (Code) | Method 2 (Docs) | Agreement |
|--------|-----------------|-----------------|-----------|
| Rate limit value | 100 req/sec | 100 req/sec | ✅ |
| Time window | 1.0 seconds | per second | ✅ |
| Scope | per instance | per IP address | ⚠️ Partial |

**Overall Agreement**: 90%

**Cross-Validation Result**:
✅ **VERIFIED** - Claim "API rate limit is 100 requests/second" supported by 2 independent methods

**Combined Confidence**:
- Method 1 alone: 85%
- Method 2 alone: 90%
- Agreement bonus: +10%
- **Cross-validated confidence**: 95%

**Minor Discrepancy Noted**:
Code doesn't specify "per IP address", but docs do. This is a documentation detail, not a contradiction of the core claim (100 req/sec limit).
```

### Step 6: Handle Conflicts (If Methods Disagree)

**Conflict Resolution Protocol**:

```markdown
## Conflict Resolution

⚠️ **METHODS DISAGREE**

**Method 1**: {method_name} → {result}
**Method 2**: {method_name} → {result}

**Conflict Analysis**:
- **What they agree on**: {commonalities}
- **What they disagree on**: {differences}
- **Possible reasons for conflict**:
  1. {reason 1: e.g., outdated documentation}
  2. {reason 2: e.g., environment-specific behavior}
  3. {reason 3: e.g., method limitations}

**Resolution Strategy**:

**Option A: Execute Tie-Breaker Method 3**
- Method 3: {choose third independent method}
- Rationale: {why this method will resolve conflict}

**Option B: Deeper Investigation**
- Investigate: {specific aspect causing conflict}
- Approach: {how to investigate}

**Option C: Escalate Uncertainty**
- If conflict cannot be resolved with available methods
- Create uncertainty node
- Request user guidance

**Action Taken**: {which option chosen and why}
```

**Example - Conflict Resolution**:

```markdown
## Conflict Resolution

⚠️ **METHODS DISAGREE**

**Method 1**: Code Inspection → Rate limit is 100 req/sec
**Method 2**: Production Logs → Actual limit appears to be 1000 req/sec

**Conflict Analysis**:
- **Agree on**: Rate limiting exists
- **Disagree on**: Actual limit value (100 vs 1000)

**Possible Reasons**:
1. Code configuration is overridden by environment variable
2. Different limit for production vs development
3. Load balancer has separate limit layer

**Resolution Strategy**: Option A - Execute Method 3

**Method 3: Configuration File Check**

Checked production environment config:
```yaml
# config/production.yml:23
rate_limit:
  max_requests: 1000  # Override for production
  window: 1.0
```

**Finding**: Production environment overrides code default (100) with config value (1000)

**Resolution**:
- **Code default**: 100 req/sec (correct for development)
- **Production override**: 1000 req/sec (correct for production)
- **Revised claim**: "API rate limit is 100 requests/second in development, 1000 in production"

**Combined Confidence**: 95% (all 3 methods now agree with clarified claim)
```

### Step 7: Document Verification Outcome

```markdown
## Multi-Method Verification Report

**Claim Verified**: {original claim}

**Verification Status**: ✅ VERIFIED | ❌ REFUTED | 🔄 REVISED | ⚠️ INCONCLUSIVE

**Methods Used**: {count} methods (minimum 2 required ✅)

---

### Method Summary

**Method 1: {name}**
- Type: {type}
- Result: {support|refute|partial|inconclusive}
- Confidence: {percentage}%
- Evidence: {brief summary}

**Method 2: {name}**
- Type: {type}
- Result: {support|refute|partial|inconclusive}
- Confidence: {percentage}%
- Evidence: {brief summary}

[Method 3 if conflict resolution needed]

---

### Cross-Validation

**Agreement**: {percentage}%
**Conflicts**: {count} conflicts {resolved|unresolved}

**Combined Confidence**: {final_percentage}%

---

### Final Conclusion

[IF VERIFIED]:
✅ **CLAIM VERIFIED**

The claim "{original_claim}" is **verified** with {final_confidence}% confidence based on {count} independent verification methods.

**Evidence Quality**: {Tier 1|2|3|4|5} (from cite-evidence skill)

**Safe to use for**:
- Adding to knowledge graph with high confidence
- Making decisions based on this claim
- Citing as verified fact

[IF REFUTED]:
❌ **CLAIM REFUTED**

The claim "{original_claim}" is **refuted** by {count} independent methods.

**Actual finding**: {what is actually true}

**Correction needed**: {how to correct claim}

[IF REVISED]:
🔄 **CLAIM REVISED**

The original claim "{original_claim}" required revision.

**Revised claim**: {corrected statement}
**Confidence in revised claim**: {percentage}%

[IF INCONCLUSIVE]:
⚠️ **INCONCLUSIVE**

Verification methods could not conclusively verify or refute the claim.

**Reason**: {why inconclusive}
**Recommendation**: {escalate|get more data|use different methods}

---

### Knowledge Graph Update

[IF VERIFIED or REVISED]:
```
[GRAPH_UPDATE]
type: add_node
node_id: verified_{claim_id}
node_type: VerifiedFinding
label: {claim or revised_claim}
confidence: {final_confidence}
verification_method: multi-method ({count} methods)
methods_used: [{method1}, {method2}, ...]
cross_validation_score: {agreement_percentage}
evidence_tier: {1-5}
created_by: multi-method-verify-skill
[/GRAPH_UPDATE]
```

[IF REFUTED]:
```
[GRAPH_UPDATE]
type: add_node
node_id: refuted_{claim_id}
node_type: RefutedClaim
label: Refuted: {original_claim}
actual_finding: {what_is_true}
refutation_method: multi-method ({count} methods)
methods_used: [{method1}, {method2}, ...]
created_by: multi-method-verify-skill
[/GRAPH_UPDATE]
```
```

## Output Format

```markdown
## Multi-Method Verification Report

**Claim**: "{claim_statement}"

**Status**: ✅ VERIFIED | ❌ REFUTED | 🔄 REVISED | ⚠️ INCONCLUSIVE

**Methods**: {count} independent methods

---

### Method 1: {name}
- **Type**: {method_type}
- **Result**: ✅ Supports | ❌ Refutes | 🔄 Partial
- **Confidence**: {XX}%
- **Evidence**: {summary}

### Method 2: {name}
- **Type**: {method_type}
- **Result**: ✅ Supports | ❌ Refutes | 🔄 Partial
- **Confidence**: {XX}%
- **Evidence**: {summary}

---

### Cross-Validation
- **Agreement**: {XX}%
- **Conflicts**: {count} {resolved|unresolved}
- **Combined Confidence**: {XX}%

---

### Conclusion

{Final determination with reasoning}

**Final Confidence**: {XX}%
**Evidence Tier**: {1-5}
**Safe for**: {use cases}

---

### Knowledge Graph
```
[GRAPH_UPDATE]
{node_specification}
[/GRAPH_UPDATE]
```
```

## Example Usage

**Scenario**: Verifying API rate limit claim

**Input Claim**:
```markdown
"The API rate limit is 100 requests per second"
Source: API documentation
Initial Confidence: 75% (single source)
```

**Skill Invocation**:

```markdown
## Multi-Method Verification Report

**Claim**: "The API rate limit is 100 requests per second"

**Status**: ✅ VERIFIED (with minor clarification)

**Methods**: 3 independent methods (conflict resolution required)

---

### Method 1: Code Inspection
- **Type**: Static Analysis
- **Result**: ✅ Supports
- **Confidence**: 85%
- **Evidence**:
  ```python
  # api/middleware/rate_limiter.py:15
  self.max_requests = 100  # per second
  ```
  Code clearly sets limit to 100 req/sec

### Method 2: Documentation Check
- **Type**: Official Documentation
- **Result**: ✅ Supports
- **Confidence**: 90%
- **Evidence**:
  ```markdown
  # docs/api-limits.md:12
  Rate limited to 100 requests per second per IP
  ```
  Documentation confirms 100 req/sec limit

### Method 3: Runtime Testing (Conflict Resolution)
- **Type**: Dynamic Analysis
- **Result**: 🔄 Partial (production differs)
- **Confidence**: 95%
- **Evidence**:
  ```bash
  # Production config override
  # config/production.yml:23
  rate_limit:
    max_requests: 1000
  ```
  Production environment overrides to 1000 req/sec

---

### Cross-Validation
- **Agreement**: 90% (all methods agree limit exists, differ on value by environment)
- **Conflicts**: 1 resolved (production vs development)
- **Combined Confidence**: 95%

---

### Conclusion

✅ **CLAIM REVISED FOR CLARITY**

The original claim "API rate limit is 100 requests per second" is **verified with clarification**.

**Revised claim**: "API rate limit is 100 requests/second (development), 1000 requests/second (production)"

**Verification summary**:
- Code default: 100 req/sec ✅
- Documentation: 100 req/sec ✅
- Production config: 1000 req/sec (override) ✅

All three methods agree when environment context is included.

**Final Confidence**: 95%
**Evidence Tier**: Tier 1 (Direct Observation - code + runtime + config)
**Safe for**: High-confidence knowledge addition, design decisions, documentation

---

### Knowledge Graph
```
[GRAPH_UPDATE]
type: add_node
node_id: verified_api_rate_limit_20241027
node_type: VerifiedFinding
label: API Rate Limit (Environment-Specific)
description: "API rate limit is 100 req/sec (dev), 1000 req/sec (prod)"
confidence: 0.95
verification_method: "multi-method (3 independent)"
methods_used: ["code_inspection", "documentation_check", "runtime_testing"]
cross_validation_score: 0.90
evidence_tier: 1
environments:
  development: 100
  production: 1000
source_code: "api/middleware/rate_limiter.py:15"
documentation: "docs/api-limits.md:12"
production_config: "config/production.yml:23"
created_by: multi-method-verify-skill
verified_at: 2024-10-27T22:30:00Z
[/GRAPH_UPDATE]
```
```

## Integration with Constitutional Principles

**Multi-Method Verification** (direct enforcement):
- Requires minimum 2 independent verification methods
- Validates independence criteria explicitly
- Cross-validates results and detects conflicts
- Resolves conflicts with tie-breaker methods
- Rejects claims verified by only 1 method

**Evidence-Based Claims**:
- Every method must provide specific, verifiable evidence
- Evidence quality assessed using cite-evidence skill
- Multiple evidence sources increase reliability
- Tier 1 evidence (direct observation) prioritized

**Uncertainty Escalation**:
- Escalates when methods conflict and cannot be resolved
- Escalates when confidence remains <90% after verification
- Creates uncertainty nodes for unresolvable conflicts

**Complete Transparency**:
- Documents all verification methods attempted
- Shows complete reasoning for method selection
- Explains conflicts and how resolved
- Full evidence trail for all claims

**Assumption Auditing**:
- Identifies assumptions each method relies on
- Validates that methods use different assumptions (independence)
- Documents limitations of each method
- Re-validates inherited claims with new methods

---

**This skill is critical for ensuring reliability of all knowledge. Use it before adding any high-confidence knowledge to the graph.**
