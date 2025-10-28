---
category: business-analysis
domain: business
type: methodology
name: market-research-protocols
description: Market research methodologies including primary and secondary research, survey design, interview protocols, TAM/SAM/SOM analysis, and competitive intelligence
generated_by: triads-generator-template
---

# Market Research Protocols

## Purpose

Define rigorous market research methodologies ensuring reliable, verifiable, and actionable market insights.

---

## Research Types

### Primary Research (Original Data Collection)

**Methods**:
```markdown
**Surveys** (Quantitative):
- Sample size: n ≥30 for statistical significance
- Response rate target: ≥30%
- Confidence level: 95%
- Margin of error: ±5%

**Interviews** (Qualitative):
- Sample size: 10-20 for insights
- Semi-structured format
- 30-60 minute duration
- Record and transcribe

**Focus Groups** (Qualitative):
- 6-10 participants per group
- 90-120 minute sessions
- Professional moderator
- Multiple groups for validation

**Usability Testing** (Product):
- 5-8 users per test
- Task-based scenarios
- Think-aloud protocol
- Video recording
```

### Secondary Research (Existing Data)

**Sources**:
```markdown
**Industry Reports**:
- Gartner, Forrester, IDC
- Cite: "Gartner Magic Quadrant 2024"
- Cost: $1,000-10,000 per report

**Government Data**:
- Census Bureau (census.gov)
- Bureau of Labor Statistics (bls.gov)
- Industry-specific agencies
- Free, public domain

**Financial Reports**:
- Public company 10-Ks, 10-Qs
- EDGAR database (sec.gov)
- Free, publicly filed

**Academic Research**:
- Google Scholar
- University research centers
- Peer-reviewed journals
- Often free or low-cost
```

---

## Survey Design

### Question Types

**Closed-Ended** (Quantitative):
```markdown
**Multiple Choice**:
Q: Which project management tool do you use?
○ Asana
○ Monday.com
○ Jira
○ Trello
○ Other: _______

**Rating Scale** (Likert):
Q: How satisfied are you with your current tool?
1 - Very Dissatisfied
2 - Dissatisfied
3 - Neutral
4 - Satisfied
5 - Very Satisfied

**Yes/No**:
Q: Would you pay for this feature?
○ Yes
○ No
```

**Open-Ended** (Qualitative):
```markdown
Q: What frustrations do you have with your current tool?
[Text box for response]

**Use sparingly**: 2-3 max per survey (reduces completion rate)
```

### Survey Best Practices

```markdown
✅ **Do**:
- Keep survey <10 minutes (completion rate ~80%)
- Start with easy questions
- Use simple language
- Include progress bar
- Mobile-optimized
- Pre-test with 5-10 people

❌ **Don't**:
- Leading questions: "Don't you think...?"
- Double-barreled: "Fast and easy to use?" (two questions)
- Jargon without definition
- Required open-ended questions
- >20 questions total
```

### Sample Size Calculator

```markdown
**Formula**:
n = (Z² × p × (1-p)) / E²

Where:
- Z = Z-score (1.96 for 95% confidence)
- p = Estimated proportion (0.5 for maximum variability)
- E = Margin of error (0.05 for ±5%)

**Example**:
n = (1.96² × 0.5 × 0.5) / 0.05²
n = 384 respondents needed

**Adjust for population**:
If population <20,000, use finite population correction
```

---

## Interview Protocol

### Interview Structure

```markdown
**1. Introduction** (5 min):
- Explain purpose
- Get consent to record
- Ensure confidentiality
- Build rapport

**2. Background Questions** (5-10 min):
- Role, company, industry
- Current solution usage
- Context setting

**3. Problem/Needs Exploration** (20-30 min):
- "Tell me about [pain point]..."
- "Walk me through [process]..."
- "What's challenging about...?"
- Follow-up probes: "Why?" "Can you give an example?"

**4. Solution Validation** (10-15 min):
- Show concept/prototype
- "How would you use this?"
- "What would you change?"

**5. Wrap-Up** (5 min):
- "Anything else to add?"
- Ask for referrals
- Thank you
```

### Interview Best Practices

```markdown
✅ **Do**:
- Ask open-ended questions
- Listen more than talk (80/20 rule)
- Probe deeper: "Tell me more..."
- Stay neutral, don't sell
- Record (with permission)
- Take notes

❌ **Don't**:
- Lead the witness: "Isn't this great?"
- Pitch your solution
- Interrupt
- Ask yes/no questions
- Assume understanding
```

### Interview Analysis

```markdown
**Thematic Coding**:
1. Transcribe all interviews
2. Read through, highlight key quotes
3. Code by theme (pain points, needs, behaviors)
4. Count frequency of themes
5. Identify patterns across interviews

**Example Output**:
**Theme 1**: Data silos (mentioned by 15/20 = 75%)
- "Our data is scattered..." (P3, P7, P12)
- "No single source of truth" (P5, P9)

**Theme 2**: Manual processes (mentioned by 12/20 = 60%)
- "Spend 5 hours/week on reports" (P2, P8)
- "Copy-paste between tools" (P4, P11)

**Insight**: Data integration is top pain point (75% mention)
**Source**: Customer interviews (n=20, Oct 2024)
**Confidence**: High (consistent across respondents)
```

---

## TAM/SAM/SOM Analysis

### Definitions

```markdown
**TAM** (Total Addressable Market):
Total revenue if you had 100% market share

**SAM** (Serviceable Available Market):
Portion of TAM you can realistically serve (geography, segment)

**SOM** (Serviceable Obtainable Market):
Portion of SAM you can realistically capture (next 1-3 years)

**Example**:
TAM: All companies globally = $100B
SAM: US mid-market companies = $15B (15% of TAM)
SOM: 2% market share in Year 3 = $300M (2% of SAM)
```

### Calculation Methods

**Top-Down** (Market-based):
```markdown
**TAM Calculation**:
Total # of target companies: 100,000
× Average revenue per customer: $10,000/year
= TAM: $1,000,000,000 ($1B)

**Sources**:
- Company count: "US Census Bureau, NAICS 541511 (2024)"
- ARPU: "Industry benchmark, Gartner 2024"

**SAM Calculation**:
TAM: $1B
× Geographic focus (US only): 30%
× Segment focus (mid-market): 40%
= SAM: $120M

**SOM Calculation**:
SAM: $120M
× Realistic market share Year 3: 2%
= SOM: $2.4M

**Justification**: "Based on competitor analysis, typical new entrant captures 1-3% in first 3 years"
```

**Bottom-Up** (Resource-based):
```markdown
**SOM Calculation**:
Sales reps: 5
× Quota per rep: $500K/year
= Sales capacity: $2.5M/year

**Validate**:
Does bottom-up SOM ($2.5M) align with top-down SOM ($2.4M)?
✅ Yes, within 5% - validates assumptions
```

---

## Competitive Intelligence

### Competitor Analysis Framework

```markdown
**For Each Competitor**:

**1. Company Profile**:
- Founded: [Year]
- Employees: [Count] (LinkedIn estimate)
- Funding: $[Amount] (Crunchbase)
- Revenue: $[Amount] (estimate or public)

**2. Product**:
- Features: [List 5-10 core features]
- Pricing: $[Amount] (public pricing page)
- Technology: [Stack from job postings, BuiltWith]

**3. Go-to-Market**:
- Target customer: [ICP description]
- Sales model: Direct / PLG / Channel
- Marketing: [Top channels from SimilarWeb]

**4. Strengths/Weaknesses**:
- Strengths: [Based on reviews, G2]
- Weaknesses: [Based on reviews, missing features]

**5. Performance**:
- Website traffic: [Monthly visitors, SimilarWeb]
- Growth: [Trending up/down/stable]
- Customer count: [Estimate from case studies]

**Sources Cited**:
- Company website (pricing, features)
- LinkedIn (employee count, job postings)
- Crunchbase (funding)
- G2/Capterra (reviews, ratings)
- SimilarWeb (traffic estimates)
```

### Competitive Positioning Map

```markdown
**2x2 Matrix Example**:

         High Features
              │
              │  Competitor C
              │     ●
              │              Competitor A
              │                   ●
Low Price ────┼──────────────────── High Price
              │
              │        ● You
              │
              │  Competitor B
              │     ●
              │
         Low Features

**Analysis**:
- Competitor A: Premium, feature-rich
- Competitor B: Budget, basic
- Competitor C: Mid-market leader
- You: Mid-price, selective features (focused positioning)

**Source**: Feature comparison (public data, Oct 2024), Pricing (websites)
```

---

## Data Quality Standards

### Source Evaluation

```markdown
✅ **High Quality**:
- Primary research (own surveys, interviews)
- Government data (Census, BLS)
- Audited financial reports (10-K)
- Peer-reviewed research
- Industry reports (Gartner, Forrester)

⚠️ **Medium Quality**:
- Company estimates (Crunchbase)
- Review sites (G2, Capterra)
- Traffic estimates (SimilarWeb)
- Job postings (LinkedIn)

❌ **Low Quality**:
- Unverified blogs
- Social media claims
- Press releases (marketing)
- Anonymous sources
```

### Sample Size Requirements

```markdown
**Quantitative (Surveys)**:
- Minimum: n=30 (basic statistical validity)
- Recommended: n=100+ (5% margin of error)
- Ideal: n=384+ (95% confidence, ±5% error)

**Qualitative (Interviews)**:
- Minimum: 5 interviews (initial patterns)
- Recommended: 10-15 (saturation)
- Maximum: 20-30 (diminishing returns)
```

---

## Reporting Standards

### Research Report Structure

```markdown
# Market Research Report: [Topic]

**Date**: [YYYY-MM-DD]
**Analyst**: [Name]
**Methods**: [Survey n=X / Interviews n=Y / Secondary]

## Executive Summary
- **Market Size**: TAM $XB, SAM $YM, SOM $ZM
- **Key Finding 1**: [Insight]
- **Key Finding 2**: [Insight]
- **Recommendation**: [Action]

## Methodology
- **Primary Research**: [Description]
  - Survey: n=[X], response rate [Y]%, margin of error ±[Z]%
  - Interviews: n=[X], [Profile]
- **Secondary Research**: [Sources]
- **Analysis Period**: [Date range]

## Market Sizing
### TAM Analysis
[Calculation with sources]
**Confidence**: [High/Medium/Low]

### SAM Analysis
[Calculation]

### SOM Analysis
[Calculation]

## Findings
### Finding 1: [Title]
**Evidence**: [Data]
**Source**: [Citation]
**Significance**: [Why it matters]

[Continue for all findings]

## Competitive Landscape
[Competitor analysis]

## Recommendations
1. **Priority 1**: [Action]
   - **Rationale**: [Why]
   - **Expected Impact**: [Outcome]

## Appendix
- Survey instrument
- Interview guide
- Data tables
- Calculations
```

---

## Integration with Constitutional Principles

**Evidence-Based Claims**:
- All market sizing cited with sources
- Survey data includes sample size, methodology
- Competitor data sourced from verifiable channels

**Multi-Method Verification**:
- Cross-validate with multiple sources
- Use primary + secondary research
- Triangulate estimates (top-down + bottom-up)

**Complete Transparency**:
- Document all assumptions
- Show calculations
- Provide confidence levels

**Assumption Auditing**:
- Validate market size assumptions
- Test sensitivity of estimates
- Question inherited market data

---

**These protocols ensure market research is rigorous, reliable, and actionable.**
