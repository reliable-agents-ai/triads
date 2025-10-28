---
name: cite-evidence
description: Enforce evidence-based claims with proper citations and verifiable sources. Use when making factual claims, stating findings, reporting results, presenting conclusions, documenting decisions, claiming knowledge, asserting facts, need citation, need source, need reference, provide evidence, back up claim, support with proof, cite source, reference material, document evidence, show proof, verifiable evidence, traceable source, evidence chain, substantiate claim, corroborate finding, validate claim with evidence, evidence-based assertion, cited fact, referenced claim, sourced information, documented finding, proven claim, verified statement, evidence documentation, citation required, source needed, reference needed, proof required, evidence backing, substantiation needed, verification source, evidence trail, documentation source.
category: framework
generated_by: triads-generator-template
---

# Cite Evidence

## Purpose

Enforce evidence-based claims by ensuring every factual statement is supported with proper citations and verifiable sources. This skill enforces the constitutional principle of Evidence-Based Claims.

## Keywords for Discovery

cite, citation, evidence, source, reference, proof, cite source, reference material, provide evidence, show proof, back up claim, support with evidence, evidence-based, document evidence, verifiable evidence, traceable source, substantiate, corroborate, validate claim, evidence chain, proof of claim, verified statement, cited fact, sourced information, documented finding, proven claim, citation required, source needed, reference needed, proof required, evidence backing, substantiation, verification source, evidence trail, documentation source, evidence format, proper citation, complete citation, citation standards, reference format, evidence quality, reliable source, credible source, verifiable source, primary source, secondary source, evidence hierarchy, citation completeness, source verification

## When to Invoke This Skill

Invoke this skill when:
- Making any factual claim
- Stating research findings
- Reporting test results
- Documenting decisions
- Claiming knowledge
- Asserting conclusions
- Providing recommendations
- Referencing external sources
- Citing prior work
- Building on existing knowledge
- Adding nodes to knowledge graph
- Creating documentation
- Writing reports
- Finalizing analysis
- Before committing conclusions
- When evidence seems weak or vague

## Skill Procedure

### Step 1: Identify Claims Requiring Evidence

**Claims that REQUIRE citation**:
```markdown
✅ Factual claims:
- "PostgreSQL supports JSON data types"
- "The study found 42% response rate"
- "Python 3.9 introduced dictionary merge operators"

✅ Research findings:
- "Meditation reduced cortisol by 26%"
- "Customer churn rate is 5% monthly"

✅ Technical specifications:
- "API rate limit is 100 requests/second"
- "Maximum file size is 10MB"

✅ Statistical results:
- "Difference was significant (p < 0.001)"
- "Effect size was d = 0.62"

✅ Design decisions:
- "Chose React because team has 4/5 developers with experience"
- "Selected PostgreSQL based on existing production stack"

✅ Historical facts:
- "Feature X was added in version 2.3"
- "Bug Y was reported on 2024-01-15"
```

**Claims that DON'T require citation** (general knowledge or opinion):
```markdown
❌ Opinions:
- "This is a good approach"
- "I recommend option A"

❌ Obvious facts:
- "Computers use binary"
- "HTTP is a protocol"

❌ Self-evident from code:
- "This function returns an integer" (if return type visible)
```

### Step 2: Determine Evidence Format by Domain

**Software Development**:
```markdown
**Code Reference**:
Format: {file_path}:{line_number}
Example: models/user.py:45
Context: "The User model validates email format (models/user.py:45)"

**API Documentation**:
Format: {URL} (accessed {date})
Example: https://docs.python.org/3/library/re.html (accessed 2024-10-27)
Context: "Python's re module supports regex patterns (docs.python.org/3/library/re.html)"

**Test Results**:
Format: Test output or log reference
Example: "pytest output: 47/47 tests passed (test_run_2024-10-27.log)"

**Git History**:
Format: {commit_hash} or {tag}
Example: "Feature added in commit abc1234" or "Released in v2.3.0"

**Library Documentation**:
Format: {library_name} v{version} docs: {URL}
Example: "Django 4.2 docs: https://docs.djangoproject.com/en/4.2/"
```

**Research**:
```markdown
**Journal Article**:
Format: Author(s) (Year). Title. Journal, volume(issue), pages. DOI
Example: "Smith, J., et al. (2023). Meditation effects. J. Clin. Psych., 79(3), 234-251. doi:10.1002/jclp.12345"

**Book**:
Format: Author (Year). Title. Publisher.
Example: "Johnson, M. (2024). Data Science Methods. MIT Press."

**Dataset**:
Format: {dataset_name} (n={sample_size}, {source})
Example: "NHANES dataset (n=10,000, CDC)"

**Statistical Output**:
Format: {software} {version} output: {file}
Example: "R 4.3.0 analysis output: analysis_results.txt"
```

**Content Creation**:
```markdown
**Style Guide**:
Format: {guide_name} ({edition/year})
Example: "AP Stylebook (2024 edition)"

**SEO Data**:
Format: {tool_name}: {metric} on {date}
Example: "Google Search Console: 1,245 impressions on 2024-10-15"

**Analytics**:
Format: {platform}: {metric} ({date_range})
Example: "Google Analytics: 15% CTR (Oct 1-27, 2024)"

**Fact-Checking**:
Format: {source} ({verification_date})
Example: "Verified via Snopes.com (2024-10-27)"
```

**Business Analysis**:
```markdown
**Market Report**:
Format: {company} ({year}). {report_title}.
Example: "Gartner (2024). Magic Quadrant for Cloud Databases."

**Financial Data**:
Format: {company} {report_type} ({quarter/year})
Example: "Acme Corp Q3 2024 10-Q filing"

**Industry Statistics**:
Format: {statistic} ({source}, {year})
Example: "$4.2B TAM (Forrester, 2024)"

**Competitive Data**:
Format: {competitor} pricing as of {date}
Example: "Competitor A: $99/month as of 2024-10-15"
```

### Step 3: Validate Citation Completeness

**Required Elements by Format**:

**Code Citation**:
- [ ] File path (absolute or relative from project root)
- [ ] Line number (or range)
- [ ] Optional: Function/class name
- Example: ✅ "models/user.py:45 (User.__init__)"

**Academic Citation**:
- [ ] Author(s) name(s)
- [ ] Publication year
- [ ] Article/book title
- [ ] Journal/publisher name
- [ ] Volume/issue (journals)
- [ ] Page numbers
- [ ] DOI or URL
- Example: ✅ "Smith et al. (2023). Title. Journal, 79(3), 234-251. doi:10.1002/xxx"

**Web Source**:
- [ ] URL (full, not shortened)
- [ ] Website/organization name
- [ ] Access date
- [ ] Page title (if applicable)
- Example: ✅ "PostgreSQL JSON Support (postgresql.org/docs/json, accessed 2024-10-27)"

**Test/Log Reference**:
- [ ] Tool/command used
- [ ] Date/timestamp
- [ ] Result summary
- [ ] Log file location (if applicable)
- Example: ✅ "pytest run (2024-10-27 14:30): 47/47 passed (logs/test_run.log)"

### Step 4: Validate Evidence Quality

**Evidence Hierarchy** (strongest to weakest):

**Tier 1: Direct Observation** (highest quality)
```markdown
✅ Code you read yourself
✅ Tests you ran yourself
✅ Errors you saw yourself
✅ Data you analyzed yourself

Example: "The User model has an email field (confirmed by reading models/user.py:13)"
```

**Tier 2: Official Documentation**
```markdown
✅ Vendor documentation
✅ API specifications
✅ Published standards
✅ Peer-reviewed papers

Example: "PostgreSQL supports JSONB data type (PostgreSQL 16 documentation, Section 8.14)"
```

**Tier 3: Verified Secondary Sources**
```markdown
✅ Established industry sources (Gartner, Forrester)
✅ Reputable publications
✅ Verified datasets
✅ Cited meta-analyses

Example: "Market size is $4.2B (Gartner Magic Quadrant 2024)"
```

**Tier 4: Logical Inference** (from verified facts)
```markdown
⚠️ Conclusions drawn from Tier 1-3 evidence
⚠️ Clearly marked as inference
⚠️ Reasoning chain shown

Example: "Given PostgreSQL supports JSON (docs) and our stack uses PostgreSQL (config.yml:12), we can use JSON data types"
```

**Tier 5: Informed Speculation** (lowest quality)
```markdown
❌ Unverified assumptions
❌ Hearsay
❌ "Common knowledge" without source
❌ Personal opinion presented as fact

Example: ❌ "Everyone knows PostgreSQL is better"
Example: ✅ "I recommend PostgreSQL based on {evidence}, but this is my opinion"
```

**Reject Weak Evidence**:
```markdown
❌ "From research" - Too vague
❌ "I think this is correct" - Opinion, not evidence
❌ "It's commonly known" - Verify with source
❌ "Someone told me" - Hearsay, verify independently
❌ "Probably" or "seems like" - Speculation, get evidence
```

### Step 5: Format Citation Properly

**In-Text Citation Formats**:

**Software Development**:
```markdown
The User model validates email format (models/user.py:45) using regex patterns.

PostgreSQL supports JSON data types (PostgreSQL 16 docs, Section 8.14.1, postgresql.org/docs/16/datatype-json.html).

All tests passed (pytest run 2024-10-27: 47/47, logs/test_run.log).
```

**Research (APA Style)**:
```markdown
Meditation significantly reduced cortisol levels (Smith et al., 2023).

Smith et al. (2023) found that mindfulness meditation reduced cortisol by 26% compared to control (p < 0.001, d = 0.62).

Reference:
Smith, J. D., Johnson, M. K., & Williams, R. L. (2023). Effects of mindfulness on anxiety reduction. Journal of Clinical Psychology, 79(3), 234-251. https://doi.org/10.1002/jclp.12345
```

**Business Analysis**:
```markdown
The cloud database market is projected at $4.2B TAM (Gartner, 2024) with 12% CAGR (Forrester Q3 2024).

Competitor A charges $99/month (pricing page as of 2024-10-15), while Competitor B charges $129/month (pricing page as of 2024-10-15).
```

**Content/SEO**:
```markdown
The article achieved 1,245 impressions with 15.2% CTR (Google Search Console, Oct 1-27, 2024).

AP Stylebook (2024) recommends using Oxford comma in lists for clarity.
```

### Step 6: Verify Sources Are Accessible

**Check that sources can be verified**:

**URLs**:
```markdown
✅ Check URL is accessible (returns HTTP 200)
✅ Check URL is not behind paywall (or note if it is)
✅ Check URL is stable (not temporary link)
✅ Archive important URLs (archive.org)

Example:
Source: https://postgresql.org/docs/16/datatype-json.html
Status: ✅ Accessible, public, stable
Archived: https://web.archive.org/web/*/postgresql.org/docs/16/datatype-json.html
```

**Files**:
```markdown
✅ File exists in repository
✅ Line number is accurate
✅ Content matches claim

Example:
Citation: models/user.py:45
Verification:
- File exists: ✅
- Line 45 contains: `if not self._is_valid_email(email):` ✅
- Supports claim about email validation: ✅
```

**Papers/Books**:
```markdown
✅ DOI resolves
✅ Paper is published (not just preprint)
✅ Citation is accurate (authors, year, pages)

Example:
DOI: https://doi.org/10.1002/jclp.12345
Resolves to: ✅ Smith et al. (2023) JCLP article
Peer-reviewed: ✅
Citation accurate: ✅
```

## Output Format

```markdown
## Citation Validation Report

**Claims Analyzed**: {count}
**Claims Cited**: {count}
**Citations Complete**: {count}
**Citations Incomplete**: {count}
**Weak Evidence**: {count}

---

### Claim-by-Claim Analysis

**Claim 1**: "{statement}"
- **Citation**: {citation}
- **Evidence Quality**: Tier {1-5} ({quality_level})
- **Completeness**: ✅ Complete | ⚠️ Incomplete | ❌ Missing
- **Accessibility**: ✅ Verifiable | ⚠️ Restricted | ❌ Broken
- **Status**: ✅ APPROVED | ⚠️ NEEDS IMPROVEMENT | ❌ REJECTED

**Claim 2**: "{statement}"
[... repeat for all claims ...]

---

### Summary

✅ **Approved**: {count} claims with complete, high-quality citations
⚠️ **Needs Improvement**: {count} claims with incomplete citations
❌ **Rejected**: {count} claims with no evidence or weak evidence

**Next Steps**:
{If all approved}: Proceed with confidence
{If needs improvement}: {specific improvements needed}
{If rejected}: {must provide evidence or remove claims}
```

## Example Usage

**Scenario**: Validating technical design document

**Input Claims**:
```markdown
1. "PostgreSQL supports JSON data types"
2. "The API rate limit is 1000 requests/second"
3. "Users prefer dark mode"
4. "React is the best frontend framework"
5. "All tests passed"
```

**Skill Output**:
```markdown
## Citation Validation Report

**Claims Analyzed**: 5
**Claims Cited**: 3
**Citations Complete**: 2
**Citations Incomplete**: 1
**Weak Evidence**: 2

---

### Claim-by-Claim Analysis

**Claim 1**: "PostgreSQL supports JSON data types"
- **Citation**: "PostgreSQL 16 documentation, Section 8.14.1"
- **Full Reference**: https://postgresql.org/docs/16/datatype-json.html
- **Evidence Quality**: Tier 2 (Official Documentation)
- **Completeness**: ✅ Complete
- **Accessibility**: ✅ Verifiable (URL works, public)
- **Status**: ✅ APPROVED

**Claim 2**: "The API rate limit is 1000 requests/second"
- **Citation**: None provided
- **Evidence Quality**: Tier 5 (Unverified)
- **Completeness**: ❌ Missing
- **Status**: ❌ REJECTED - Must verify actual rate limit
- **Action Required**: Check API documentation or configuration files

**Claim 3**: "Users prefer dark mode"
- **Citation**: "3 users mentioned it in interviews"
- **Evidence Quality**: Tier 4 (Weak inference from small sample)
- **Completeness**: ⚠️ Incomplete (sample size too small)
- **Status**: ⚠️ NEEDS IMPROVEMENT
- **Action Required**: Provide larger sample or analytics data

**Claim 4**: "React is the best frontend framework"
- **Citation**: None (opinion)
- **Evidence Quality**: Tier 5 (Subjective opinion)
- **Completeness**: ❌ Missing (opinion presented as fact)
- **Status**: ❌ REJECTED
- **Action Required**: Either:
  - Remove "best" and provide objective criteria
  - Rephrase as recommendation: "I recommend React because {evidence}"

**Claim 5**: "All tests passed"
- **Citation**: "pytest run 2024-10-27"
- **Full Reference**: "pytest: 47/47 passed (logs/test_run_20241027.log)"
- **Evidence Quality**: Tier 1 (Direct Observation)
- **Completeness**: ⚠️ Incomplete (missing log file reference)
- **Accessibility**: ✅ Verifiable (log file exists)
- **Status**: ⚠️ NEEDS IMPROVEMENT
- **Improvement**: Add log file path to citation

---

### Summary

✅ **Approved**: 1 claim (Claim 1)
⚠️ **Needs Improvement**: 2 claims (Claims 3, 5)
❌ **Rejected**: 2 claims (Claims 2, 4)

**Next Steps**:
1. Claim 2: Verify API rate limit (check docs/api-limits.md or config files)
2. Claim 3: Supplement with analytics data or larger survey
3. Claim 4: Rephrase as recommendation with objective criteria
4. Claim 5: Add complete log file reference

**Revised Document** (with improvements):
1. ✅ "PostgreSQL supports JSON data types (PostgreSQL 16 docs, Section 8.14.1)"
2. "The API rate limit is 100 requests/second (docs/api-limits.md:12)" [CORRECTED after verification]
3. "15% of users prefer dark mode (Analytics Oct 2024, n=10,000)" [IMPROVED with data]
4. "I recommend React because 4/5 team members have experience with it (team survey 2024-10)" [REPHRASED as recommendation]
5. "All 47 tests passed (pytest 2024-10-27, logs/test_run_20241027.log)" [IMPROVED with complete reference]
```

## Integration with Constitutional Principles

**Evidence-Based Claims** (direct enforcement):
- Requires evidence for all factual claims
- Validates citation completeness
- Checks evidence quality
- Rejects unsupported claims

**Multi-Method Verification**:
- Verifies sources are accessible
- Cross-checks citations against original sources
- Validates evidence hierarchy

**Complete Transparency**:
- Shows full citations
- Documents evidence quality tier
- Explains why claims approved/rejected
- Provides specific improvement actions

**Assumption Auditing**:
- Identifies claims based on unverified assumptions
- Requires validation before accepting as fact
- Flags weak evidence for verification

---

**This skill is critical for maintaining intellectual rigor. Use it before finalizing any document, report, or knowledge addition.**
