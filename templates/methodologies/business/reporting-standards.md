---
category: business-analysis
domain: business
type: methodology
name: reporting-standards
description: Business reporting standards including executive summaries, data visualization, presentation design, stakeholder communication, and report formatting requirements
generated_by: triads-generator-template
---

# Reporting Standards

## Purpose

Define standards for clear, actionable, and professional business reporting that communicates insights effectively to stakeholders.

---

## Report Structure

### Standard Report Template

```markdown
# [Report Title]

**Date**: [YYYY-MM-DD]
**Author**: [Name, Title]
**Audience**: [Executive / Board / Team]
**Status**: [Draft / Final]

---

## Executive Summary (1 page max)

**Purpose**: [Why this report exists]

**Key Findings**:
1. [Finding 1] - [Impact]
2. [Finding 2] - [Impact]
3. [Finding 3] - [Impact]

**Recommendations**:
1. [Action 1] - [Expected outcome]
2. [Action 2] - [Expected outcome]

**Bottom Line**: [1-2 sentence conclusion]

---

## Situation / Background

**Context**: [What's happening, why it matters]
**Scope**: [What this report covers]
**Methodology**: [How analysis was conducted]

---

## Analysis

### Finding 1: [Title]
**Data**: [Evidence with source]
**Implication**: [What this means]
**Supporting Visual**: [Chart/table reference]

### Finding 2: [Title]
[Same structure]

---

## Recommendations

### Recommendation 1: [Action]
**Rationale**: [Why do this]
**Expected Impact**: [Outcome]
**Resources Required**: [Time, budget, people]
**Timeline**: [When to implement]
**Risk**: [What could go wrong]

---

## Conclusion

[Summary of key points and next steps]

---

## Appendix

- Detailed calculations
- Data tables
- Methodology details
- Additional charts
```

---

## Executive Summary Standards

### Purpose

**One-page summary** that busy executives can read in 2-3 minutes.

### Structure

```markdown
## Executive Summary

**Situation**: [1 sentence: What's happening]

**Complication**: [1 sentence: Why it's a problem]

**Resolution**: [1 sentence: What we recommend]

**Key Findings** (3-5 bullets):
• [Finding]: [Evidence] → [Implication]
• [Finding]: [Evidence] → [Implication]

**Recommendations** (3 max):
1. **[Action]**: [Expected outcome]
2. **[Action]**: [Expected outcome]

**Financial Impact**: [Revenue/cost implication]

**Timeline**: [When to act]

**Decision Required**: [What stakeholders must decide]
```

### Best Practices

```markdown
✅ **Do**:
- Start with bottom line (conclusion first)
- Use bullets, not paragraphs
- Include only critical information
- Make recommendations specific and actionable
- State financial impact clearly

❌ **Don't**:
- Include background/details (save for body)
- Use jargon without definition
- Present options without recommendation
- Exceed 1 page
```

---

## Data Visualization

### Chart Selection

**Choose chart type based on data**:

```markdown
**Comparison** (compare values):
→ Bar chart (horizontal bars for long labels)
→ Column chart (vertical bars for time series)

**Trend Over Time**:
→ Line chart (continuous data)
→ Column chart (discrete periods)

**Part-to-Whole** (show composition):
→ Pie chart (if 2-5 categories, totals 100%)
→ Stacked bar chart (if multiple segments)

**Distribution** (show data spread):
→ Histogram (frequency distribution)
→ Box plot (quartiles, outliers)

**Relationship** (correlation):
→ Scatter plot (two variables)
→ Bubble chart (three variables)

**Geographic**:
→ Map with color coding (regional data)
```

### Chart Design Principles

```markdown
✅ **Do**:
- **Clear title**: "Q3 Revenue by Region" not "Chart 1"
- **Axis labels**: Always label X and Y axes with units
- **Data labels**: Include values on bars/points
- **Legend**: Place near chart, define all colors
- **Source**: Cite data source below chart
- **Simplify**: Remove gridlines, 3D effects, unnecessary decoration

❌ **Don't**:
- Use 3D charts (distort perception)
- Use >6 colors (hard to distinguish)
- Truncate Y-axis (misleading)
- Use pie charts for >5 slices
- Clutter with excessive labels
```

### Example - Good Chart

```
Title: Q3 2024 Revenue Growth by Region

 Revenue
 ($M)
   15 ├─────────────────┐
      │      ████████   │ 14.2
   10 │      █     █    │
      │ ████ █ ███ █ ██ │ 8.5  9.8  7.2
    5 │ █  █ █ █ █ █ █  │
      │ █  █ █ █ █ █ █  │
    0 └─┴──┴─┴─┴─┴─┴─┴──┘
        NA  EMEA APAC LATAM

Legend: ██ Q3 2024
Source: Company financials (internal), Oct 2024
```

### Dashboard Design

```markdown
**Layout**:
┌─────────────────────────────────────┐
│  KPI 1     KPI 2     KPI 3     KPI 4│ ← Top metrics (4-6 max)
├─────────────────────────────────────┤
│                                     │
│     Primary Chart (Trend)           │ ← Most important visual
│                                     │
├──────────────────┬──────────────────┤
│  Supporting      │  Supporting      │
│  Chart 1         │  Chart 2         │ ← Detail/breakdown
├──────────────────┴──────────────────┤
│  Table with details                 │ ← Raw data (optional)
└─────────────────────────────────────┘

**Principles**:
- Most important info top-left (F-pattern reading)
- Limit to 6-8 visualizations max
- Consistent color scheme throughout
- Clear section labels
```

---

## Table Standards

### Table Design

```markdown
✅ **Good Table**:
| Product | Q3 Revenue | Growth YoY | Market Share |
|---------|------------|------------|--------------|
| Product A | $12.5M | +15% | 8.2% |
| Product B | $8.3M | +22% | 5.4% |
| Product C | $5.1M | -3% | 3.3% |
| **Total** | **$25.9M** | **+12%** | **17.0%** |

**Source**: Company financials, Q3 2024

**Features**:
- Clear headers with units
- Right-align numbers
- Left-align text
- Bold totals/key rows
- Alternating row shading (optional)
- Source citation
```

### Large Tables

```markdown
**If >10 rows**:
- Add summary row at top
- Group by category
- Use color coding for thresholds
- Consider chart instead

**If >5 columns**:
- Prioritize most important columns
- Move detail to appendix
- Consider splitting into multiple tables
```

---

## Writing Standards

### Clarity Principles

```markdown
✅ **Write Clearly**:
- **Active voice**: "The team achieved targets" not "Targets were achieved"
- **Concrete**: "$2.5M increase" not "significant growth"
- **Simple words**: "Use" not "utilize", "Help" not "facilitate"
- **Short sentences**: Average ≤20 words
- **Consistent terms**: "Customer" throughout, not "customer/client/user"

**Before** (unclear):
"It is recommended that consideration be given to the implementation of a comprehensive strategy focused on the enhancement of customer retention metrics."

**After** (clear):
"Recommendation: Implement customer retention strategy to increase retention from 85% to 95%."
```

### Number Formatting

```markdown
**Consistency**:
- Decimals: 1 decimal place for percentages (15.5%), 2 for currency ($12.45M)
- Large numbers: Use M/B (millions/billions) for readability
  - $1.5M not $1,500,000
  - $2.3B not $2,300,000,000
- Percentages: Include % symbol (15% not 15)
- Ranges: Use en dash (10–15% not 10-15%)

**Rounding**:
- Be consistent throughout document
- Note precision: "All figures rounded to nearest $100K"
```

### Bullet Points

```markdown
✅ **Effective Bullets**:
- Start with strong verb
- Parallel structure (all verbs or all nouns)
- 1-2 lines each
- 3-7 bullets per list
- Sub-bullets for detail

**Example**:
• Increased revenue 15% ($2.5M → $2.9M)
• Reduced churn from 12% to 8%
• Expanded to 3 new markets (UK, DE, FR)

**Parallel structure** (all verb phrases):
• Analyze market trends
• Identify opportunities
• Develop recommendations
```

---

## Presentation Standards

### Slide Design

```markdown
**Slide Structure**:
┌─────────────────────────────────────┐
│ Slide Title (Headline, not label)  │ ← Message, not topic
├─────────────────────────────────────┤
│                                     │
│  • Key point 1                      │ ← 3-5 bullets OR
│  • Key point 2                      │   one visual
│  • Key point 3                      │
│                                     │
│  [OR Single Chart/Visual]           │
│                                     │
├─────────────────────────────────────┤
│ Source: Company data, Oct 2024    │ ← Citation
└─────────────────────────────────────┘

**6-Second Rule**: Audience should grasp the point in 6 seconds

**Font Sizes**:
- Title: 28-32pt
- Body: 18-24pt
- Source: 12-14pt
```

### Slide Content Limits

```markdown
✅ **One message per slide**:
- Slide title = the message
- Body supports the message

❌ **Too much**:
- >7 bullets per slide
- >20 words per bullet
- Multiple charts per slide
- Paragraphs of text

**Example Titles**:
❌ "Revenue Analysis" (topic, not message)
✅ "Revenue Grew 15% YoY, Beating Plan by $500K" (message)
```

---

## Stakeholder Communication

### Audience Adaptation

```markdown
**Executive Audience**:
- Focus: Bottom line, decisions needed
- Length: 1-page exec summary + 5-10 slides
- Detail: High-level, strategic
- Format: Visual, concise

**Technical Audience**:
- Focus: Methodology, details
- Length: Full report with appendices
- Detail: In-depth, technical
- Format: Tables, detailed analysis

**General Audience**:
- Focus: Key insights, implications
- Length: 2-3 page summary
- Detail: Moderate, explained
- Format: Balance of visual and text
```

### Recommendation Framework

**Always Include**:
```markdown
**Recommendation**: [Specific action]

**Rationale**: [Why this action]
- Supporting point 1
- Supporting point 2

**Expected Outcome**: [Measurable result]
- Metric 1: Current → Target
- Metric 2: Current → Target

**Resources Required**:
- Budget: $[amount]
- Timeline: [duration]
- People: [headcount/roles]

**Risks**:
- Risk 1: [Mitigation]
- Risk 2: [Mitigation]

**Alternatives Considered**:
- Option B: [Why not chosen]
- Option C: [Why not chosen]

**Next Steps**:
1. [Action 1] - [Owner] - [Date]
2. [Action 2] - [Owner] - [Date]
```

---

## Quality Checklist

### Before Sharing

```markdown
Content:
- [ ] Executive summary 1 page or less
- [ ] Key findings clearly stated with evidence
- [ ] Recommendations specific and actionable
- [ ] All claims sourced/cited
- [ ] Assumptions documented
- [ ] Confidence levels provided for estimates

Design:
- [ ] Charts clear and labeled
- [ ] Tables formatted consistently
- [ ] Color scheme consistent throughout
- [ ] No chart junk (3D, excessive decoration)
- [ ] Source cited on every visual

Writing:
- [ ] Active voice used
- [ ] Jargon defined
- [ ] Numbers formatted consistently
- [ ] Spelling and grammar correct
- [ ] Appropriate length for audience

Accessibility:
- [ ] High contrast (readable when printed B&W)
- [ ] Alt text for images (if digital)
- [ ] Font size ≥12pt
- [ ] Color not only way to convey information
```

---

## Integration with Constitutional Principles

**Evidence-Based Claims**:
- All statements supported by data
- Sources cited for every claim
- Calculations shown in appendix

**Complete Transparency**:
- Methodology documented
- Assumptions listed
- Limitations acknowledged
- Confidence levels provided

**Communication Standards**:
- Clear, no jargon (unless defined)
- No hyperbole (specific numbers)
- Accessible to intended audience

**Assumption Auditing**:
- All assumptions explicitly stated
- Sensitivity analysis for key assumptions
- Alternative scenarios presented

---

**These reporting standards ensure professional, clear, and actionable business communications.**
