---
name: validate-assumptions
description: Audit and validate all assumptions before proceeding with work. Use when making assumptions, taking something for granted, assuming facts without verification, implicit assumptions, hidden assumptions, unverified assumptions, inherited assumptions from previous agents, assumption validation needed, question assumptions, test assumptions, verify assumptions, assumption audit, assumption check, validate before proceeding, assumptions made, assumption documentation, identify assumptions, assumption registry, assumption verification, check what you're assuming, verify taken for granted, validate implicit knowledge, check inherited facts, re-verify previous conclusions, assumption analysis, assumption testing, validate base premises, check foundational assumptions, verify starting assumptions, assumption quality check, ensure valid assumptions, assumption evidence check, validate assumption evidence, cross-check assumptions, verify assumption validity, assumption risk assessment, check assumption impact.
category: framework
generated_by: triads-generator-template
---

# Validate Assumptions

## Purpose

Identify, document, and validate EVERY assumption before proceeding with work. This skill enforces the constitutional principle of Assumption Auditing by ensuring no unvalidated assumptions slip through.

## Keywords for Discovery

assumptions, validate assumptions, check assumptions, verify assumptions, audit assumptions, assumption validation, assumption audit, assumption check, question assumptions, test assumptions, identify assumptions, document assumptions, assumption registry, hidden assumptions, implicit assumptions, unverified assumptions, inherited assumptions, assumption verification, assumptions made, validate before proceeding, assumption documentation, assumption analysis, assumption testing, check what assuming, verify taken for granted, validate implicit knowledge, check inherited facts, re-verify previous conclusions, assumption evidence, validate base premises, foundational assumptions, starting assumptions, assumption quality, valid assumptions, assumption impact, assumption risk, cross-check assumptions, assumption validity, assumption source, validate inherited, re-validate assumptions, assumption completeness

## When to Invoke This Skill

Invoke this skill when:
- Starting new work (audit initial assumptions)
- Receiving handoff from previous agent (re-validate inherited assumptions)
- Making design decisions (identify underlying assumptions)
- Before committing to an approach (verify assumptions hold)
- Encountering unexpected results (question original assumptions)
- User provides requirements (validate understood assumptions)
- Multiple assumptions compound (audit assumption chain)
- High-risk decisions (verify critical assumptions)
- Conflicting information (test competing assumptions)
- Domain knowledge applied (validate domain assumptions)
- "Common knowledge" invoked (verify it's actually true)
- Time pressure exists (don't skip assumption validation)
- Template/pattern used (validate context matches)

## Skill Procedure

### Step 1: Identify ALL Assumptions

**Ask relentlessly**:
- What am I taking for granted?
- What facts haven't I verified?
- What "obviousness" am I assuming?
- What did previous agents assume that I'm inheriting?
- What domain knowledge am I applying without verification?

**Common Hidden Assumptions by Domain**:

**Software Development**:
```markdown
❌ Assumed: "Users have internet connection"
✅ Question: What about offline scenarios?

❌ Assumed: "Database is always available"
✅ Question: What about outages or maintenance windows?

❌ Assumed: "Input will be valid UTF-8"
✅ Question: What about other encodings or binary data?

❌ Assumed: "Function will return in < 1 second"
✅ Question: What if external API is slow?
```

**Research**:
```markdown
❌ Assumed: "Sample is representative of population"
✅ Question: Is there selection bias?

❌ Assumed: "Measurements are accurate"
✅ Question: What about instrument error or calibration?

❌ Assumed: "Variables are independent"
✅ Question: Could there be confounding factors?
```

**Content Creation**:
```markdown
❌ Assumed: "Audience reads English"
✅ Question: Do we need localization?

❌ Assumed: "Readers have background knowledge"
✅ Question: Should we explain fundamentals?

❌ Assumed: "SEO rules are stable"
✅ Question: Has Google's algorithm changed?
```

**Business Analysis**:
```markdown
❌ Assumed: "Market size remains constant"
✅ Question: Is market growing or declining?

❌ Assumed: "Competitors won't respond"
✅ Question: What if they match our price?

❌ Assumed: "Costs scale linearly"
✅ Question: Are there economies of scale?
```

### Step 2: Document Each Assumption in Registry

**Assumption Registry Format**:

```markdown
## Assumptions Made

### Assumption 1: {Clear statement of assumption}

**Source**: {Where this assumption came from}
- [ ] Inherited from previous agent
- [ ] Stated in requirements
- [ ] Industry standard practice
- [ ] Personal inference
- [ ] Domain knowledge
- [ ] Template/pattern assumption

**Type**: {Classification}
- [ ] Data assumption (about inputs/outputs)
- [ ] Behavioral assumption (about users/systems)
- [ ] Environmental assumption (about context)
- [ ] Temporal assumption (about timing/sequence)
- [ ] Technical assumption (about technology/tools)

**Validation Status**:
- [ ] ✅ VERIFIED - {how verified, evidence source}
- [ ] ⚠️ UNVERIFIED - {why not verified yet}
- [ ] ❌ INVALID - {why assumption is wrong}
- [ ] 🔄 PARTIALLY VERIFIED - {what's verified, what's not}

**Evidence** (if verified):
- Method 1: {verification method} → Result: {finding}
- Method 2: {verification method} → Result: {finding}
- Cross-validation: {do methods agree?}

**Risk if Wrong**: {Impact if this assumption is invalid}
- Best case: {minor impact}
- Worst case: {major impact}
- Likelihood of being wrong: {low|medium|high}

**Mitigation** (if unverified or risky):
- Plan A: {how to validate}
- Plan B: {fallback if assumption wrong}
- Monitoring: {how to detect if assumption breaks}

---

[Repeat for Assumption 2, 3, etc...]
```

### Step 3: Validate Assumptions (Multi-Method)

**Validation Methods by Type**:

**Method 1: Code Inspection** (for software):
```python
# Assumption: API returns JSON format
# Validation: Read API handler code

# File: api/handler.py:34
response_headers = {'Content-Type': 'application/json'}

# Status: ✅ VERIFIED - API sets JSON content type
```

**Method 2: Runtime Testing**:
```python
# Assumption: Function handles empty input
# Validation: Test with empty input

result = process_data([])  # Empty list
# Result: ValueError: Input cannot be empty

# Status: ❌ INVALID - Assumption was wrong, function doesn't handle empty input
```

**Method 3: Documentation Check**:
```markdown
Assumption: Rate limit is 1000 requests/second
Validation: Check API documentation

docs/api-limits.md:12
> API rate limit: 100 requests/second per IP address

Status: ❌ INVALID - Assumption was 10x too high (100, not 1000)
```

**Method 4: Data Analysis**:
```python
# Assumption: Data is normally distributed
# Validation: Shapiro-Wilk test

from scipy import stats
statistic, p_value = stats.shapiro(data)
# p_value = 0.03 (< 0.05 threshold)

# Status: ❌ INVALID - Data is NOT normally distributed
```

**Method 5: User/Stakeholder Verification**:
```markdown
Assumption: Users prefer dark mode
Validation: Ask user directly

User response: "Actually, analytics show only 15% use dark mode. Light mode is more popular."

Status: ❌ INVALID - Assumption contradicted by data
```

### Step 4: Handle Invalid Assumptions

When assumption validation fails:

```markdown
❌ INVALID ASSUMPTION DETECTED

**Assumption**: {what you assumed}
**Reality**: {what's actually true}
**Discrepancy**: {how different}

**Validation Method**: {how you discovered it was wrong}
**Evidence**: {proof that assumption is invalid}

**Impact Analysis**:
- **Decisions based on this assumption**: {list}
- **Work products affected**: {list}
- **Downstream dependencies**: {what else depends on this}

**Corrective Actions**:
1. Revise assumption to match reality
2. Re-evaluate decisions based on corrected assumption
3. Update affected work products
4. Notify downstream agents/processes
5. Document lesson learned

**Lessons Learned**:
- **Why assumption was wrong**: {root cause}
- **How to avoid in future**: {prevention}

**Updated Plan**: {what to do now with correct information}
```

**Example**:
```markdown
❌ INVALID ASSUMPTION DETECTED

**Assumption**: API rate limit is 1000 requests/second
**Reality**: API rate limit is 100 requests/second
**Discrepancy**: 10x difference

**Validation Method**: Documentation check (docs/api-limits.md:12)
**Evidence**: "API rate limit: 100 requests/second per IP address"

**Impact Analysis**:
- **Decisions**: Designed system for 1000 req/sec throughput
- **Work products**: Load balancer configured for 1000 req/sec
- **Downstream**: Performance SLA promises 500 req/sec (impossible with 100 limit)

**Corrective Actions**:
1. Update assumption: Rate limit is 100 req/sec (not 1000)
2. Re-architect for 100 req/sec constraint
   - Option A: Request batching to reduce API calls
   - Option B: Horizontal scaling with multiple IPs
3. Update load balancer config
4. Renegotiate SLA to realistic level (50 req/sec = 50% of limit)
5. Add documentation warning about rate limit

**Lessons Learned**:
- **Why wrong**: Remembered documentation from old API version
- **Prevention**: Always verify limits in current documentation, don't rely on memory

**Updated Plan**: Implement request batching to reduce API calls by 60%, allowing 40 req/sec with margin for bursts
```

### Step 5: Re-Validate Inherited Assumptions

**CRITICAL**: Never trust inherited assumptions without verification.

**Re-Validation Protocol**:
```markdown
## Inherited Assumption Re-Validation

**Assumption**: {inherited assumption}
**Source**: {previous agent who made assumption}
**Original Evidence**: {what evidence they had}
**Original Confidence**: {their confidence level}

**Independent Re-Validation**:

**Method 1**: {independent verification approach}
- Result: {finding}
- Agreement with original?: {yes|no|partial}

**Method 2**: {different verification approach}
- Result: {finding}
- Agreement with original?: {yes|no|partial}

**Cross-Validation**:
- Methods agree?: {yes|no}
- Agrees with original?: {yes|no}

**Re-Validation Result**:
- [ ] ✅ CONFIRMED - Independent verification supports assumption
- [ ] ❌ REFUTED - Independent verification contradicts assumption
- [ ] 🔄 PARTIALLY TRUE - Assumption holds with limitations

**Action**:
- **If CONFIRMED**: Proceed with assumption, document re-validation
- **If REFUTED**: Escalate to correct upstream, revise plan
- **If PARTIALLY TRUE**: Document limitations, proceed with caution
```

**Example**:
```markdown
## Inherited Assumption Re-Validation

**Assumption**: "Users prefer dark mode"
**Source**: Domain Researcher (from user interviews)
**Original Evidence**: "3 users mentioned dark mode in interviews"
**Original Confidence**: 75%

**Independent Re-Validation**:

**Method 1**: Analytics data analysis
- Checked: Last 90 days of user preferences
- Result: 15% of users enable dark mode, 85% use light mode
- Agreement with original?: ❌ NO - Contradicts assumption

**Method 2**: User survey
- Surveyed: 500 active users
- Result: Dark mode ranked #7 out of 10 requested features
- Agreement with original?: ❌ NO - Low priority

**Cross-Validation**:
- Methods agree?: ✅ YES - Both show low dark mode demand
- Agrees with original?: ❌ NO - Refutes original assumption

**Re-Validation Result**:
🔄 PARTIALLY TRUE - **Some** users want dark mode, but not majority

**Corrected Assumption**:
"A minority (15%) of users prefer dark mode. Dark mode is nice-to-have, not must-have."

**Action**:
- Notify Domain Researcher that assumption was overstated
- Downgrade dark mode priority (below features with broader appeal)
- Proceed with lower priority
- Document corrected understanding in knowledge graph

[GRAPH_UPDATE]
type: update_node
node_id: finding_user_preference_darkmode
label: Dark Mode User Preference (Corrected)
description: "15% of users prefer dark mode (not majority)"
confidence: 0.95
evidence: "Analytics (n=10,000 users, 90 days) + Survey (n=500)"
validation_method: "Multi-method (analytics + survey)"
original_assumption: "Most users prefer dark mode"
correction: "Minority (15%) prefer dark mode"
corrected_by: validate-assumptions-skill
[/GRAPH_UPDATE]
```

## Output Format

```markdown
## Assumption Validation Report

**Assumptions Identified**: {count}
**Assumptions Validated**: {count}
**Assumptions Invalid**: {count}
**Assumptions Unverified**: {count}

---

### Assumption Registry

{For each assumption:}

**Assumption {N}**: {statement}
- **Source**: {where it came from}
- **Type**: {data|behavioral|environmental|temporal|technical}
- **Status**: ✅ VERIFIED | ⚠️ UNVERIFIED | ❌ INVALID | 🔄 PARTIAL
- **Evidence**: {verification evidence}
- **Risk if wrong**: {impact}
- **Mitigation**: {how to handle if wrong}

---

### Validation Summary

✅ **Safe to proceed with**: {count} verified assumptions
⚠️ **Proceed with caution**: {count} unverified assumptions
❌ **BLOCKED**: {count} invalid assumptions requiring correction

**Next Steps**:
{If all verified}: Proceed with work
{If unverified}: {mitigation plan}
{If invalid}: {corrective actions}
```

## Example Usage

**Scenario**: Implementing email validation feature

**Skill Invocation**:

```markdown
## Assumption Validation Report

**Assumptions Identified**: 5
**Assumptions Validated**: 4
**Assumptions Invalid**: 1

---

### Assumption Registry

**Assumption 1**: User model has email field
- **Source**: Inherited from previous agent
- **Type**: Data assumption
- **Status**: ✅ VERIFIED
- **Evidence**:
  - Method 1: Code inspection (models/user.py:13) - Field exists
  - Method 2: Database schema - Column present
- **Risk if wrong**: Cannot add validation to non-existent field
- **Validation**: Both methods confirm field exists

**Assumption 2**: Email format validation is missing
- **Source**: Task requirements
- **Type**: Technical assumption
- **Status**: ✅ VERIFIED
- **Evidence**:
  - Method 1: Code inspection - Field is plain `str`, no validators
  - Method 2: Test suite - No validation tests present
- **Risk if wrong**: Duplicate work if validation exists
- **Validation**: Confirmed no existing validation

**Assumption 3**: bcrypt is available for password hashing
- **Source**: Security best practices
- **Type**: Technical assumption
- **Status**: ✅ VERIFIED
- **Evidence**:
  - Method 1: requirements.txt:15 - bcrypt==4.0.1
  - Method 2: Import test - `import bcrypt` succeeds
- **Risk if wrong**: Cannot implement secure password storage
- **Validation**: Library installed and importable

**Assumption 4**: Email field can store 255 characters
- **Source**: Personal inference (common email max length)
- **Type**: Data assumption
- **Status**: ❌ INVALID
- **Evidence**:
  - Method 1: Database schema - Column is VARCHAR(100)
  - Method 2: RFC 5321 - Max email length is 320 characters
- **Discrepancy**: Database only allows 100 chars, should be at least 320
- **Risk**: Valid emails may be rejected
- **Corrective Action**: Expand column to VARCHAR(320)

**Assumption 5**: All users have email addresses
- **Source**: Domain assumption
- **Type**: Data assumption
- **Status**: ⚠️ UNVERIFIED
- **Evidence**: Not yet verified
- **Risk if wrong**: Validation might break for users without email
- **Mitigation**: Make email optional, validate only if present
- **Action**: Ask user to confirm email is required field

---

### Validation Summary

✅ **Safe to proceed with**: 3 verified assumptions
⚠️ **Proceed with caution**: 1 unverified assumption (email required?)
❌ **BLOCKED**: 1 invalid assumption (database column too small)

**Next Steps**:
1. ❌ Expand database column: VARCHAR(100) → VARCHAR(320)
2. ⚠️ Clarify with user: Is email a required field?
3. ✅ Once corrected, implement email validation
```

## Integration with Constitutional Principles

**Assumption Auditing** (direct enforcement):
- Identifies ALL assumptions (explicit and hidden)
- Documents each in registry format
- Validates using multiple methods
- Re-validates inherited assumptions

**Evidence-Based Claims**:
- Every assumption requires evidence to be "verified"
- Multiple validation methods required
- Sources must be specific and verifiable

**Multi-Method Verification**:
- Uses ≥2 independent methods per assumption
- Cross-validates results
- Flags conflicts for resolution

**Uncertainty Escalation**:
- Unvalidated assumptions → Lower confidence
- Invalid assumptions → STOP and escalate
- High-risk assumptions → Require user confirmation

**Complete Transparency**:
- Full assumption registry visible
- Validation methods documented
- Evidence shown for all claims
- Risk assessment explicit

---

**This skill is critical for preventing failures due to invalid assumptions. Use it at the start of every task and when receiving handoffs from other agents.**
