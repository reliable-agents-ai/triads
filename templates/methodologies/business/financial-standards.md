---
category: business-analysis
domain: business
type: methodology
name: financial-standards
description: Financial analysis standards including GAAP/IFRS compliance, financial modeling, valuation methods, sensitivity analysis, and financial reporting requirements
generated_by: triads-generator-template
---

# Financial Standards

## Purpose

Define financial analysis standards ensuring accurate, compliant, and verifiable financial calculations, projections, and reporting.

---

## Core Financial Principles

### 1. GAAP/IFRS Compliance

**Generally Accepted Accounting Principles** (US):
```markdown
**Revenue Recognition**: When to recognize revenue
**Expense Matching**: Match expenses to related revenue
**Historical Cost**: Record at acquisition cost
**Conservatism**: Don't overstate assets/income
**Consistency**: Use same methods year-over-year
**Full Disclosure**: Provide all material information
```

**International Financial Reporting Standards** (Global):
```markdown
Similar principles, some differences in:
- Revenue recognition timing
- Asset valuation methods
- Lease accounting
- Inventory valuation
```

**Compliance Requirement**:
```markdown
✅ State which standard used: "All figures per GAAP"
✅ Cite specific standards: "ASC 606 (Revenue Recognition)"
✅ Note deviations: If any non-GAAP metrics, clearly label
```

---

## Financial Statement Analysis

### Income Statement (P&L)

**Key Metrics**:
```markdown
**Revenue**:
- Total Revenue = All income from operations
- YoY Growth % = (Current - Prior) / Prior × 100

**Profitability**:
- Gross Profit = Revenue - COGS
- Gross Margin % = Gross Profit / Revenue × 100
- Operating Income (EBIT) = Gross Profit - Operating Expenses
- Operating Margin % = EBIT / Revenue × 100
- Net Income = EBIT - Interest - Taxes
- Net Margin % = Net Income / Revenue × 100
```

**Example Calculation**:
```markdown
Revenue: $10,000,000
COGS: $4,000,000
→ Gross Profit: $6,000,000
→ Gross Margin: 60%

Operating Expenses: $3,500,000
→ Operating Income: $2,500,000
→ Operating Margin: 25%

Interest: $200,000
Taxes: $600,000
→ Net Income: $1,700,000
→ Net Margin: 17%

**Source**: Company 10-K filing (2024), Page 45
**Confidence**: 100% (audited financials)
```

### Balance Sheet

**Key Metrics**:
```markdown
**Liquidity**:
- Current Ratio = Current Assets / Current Liabilities
  - >1.0 = Can cover short-term obligations
- Quick Ratio = (Current Assets - Inventory) / Current Liabilities
  - >1.0 = Can cover without selling inventory

**Leverage**:
- Debt-to-Equity = Total Debt / Total Equity
  - <1.0 = Conservative, >2.0 = Aggressive
- Debt-to-Assets = Total Debt / Total Assets
  - Lower = less leveraged

**Efficiency**:
- Asset Turnover = Revenue / Total Assets
  - Higher = more efficient use of assets
```

### Cash Flow Statement

**Key Metrics**:
```markdown
**Cash from Operations (CFO)**: Core business cash generation
**Cash from Investing (CFI)**: CapEx, acquisitions (usually negative)
**Cash from Financing (CFF)**: Debt, equity, dividends

**Free Cash Flow (FCF)**:
FCF = CFO - CapEx
- Positive FCF = Can fund growth without external capital
- FCF Margin % = FCF / Revenue × 100

**Burn Rate** (for startups):
Monthly Burn = Monthly Cash Outflow - Monthly Cash Inflow
Runway (months) = Cash Balance / Monthly Burn
```

---

## Financial Modeling

### Projection Methods

**Top-Down (Market-Based)**:
```markdown
TAM (Total Addressable Market): $10B
× Market Share Assumption: 2%
= Revenue Potential: $200M

**Requirements**:
- Cite TAM source: "Gartner 2024 Market Report"
- Justify market share: "Based on competitor analysis"
- Show calculation steps
- Provide confidence level: 70% ± 30%
```

**Bottom-Up (Unit Economics)**:
```markdown
Customer Acquisition:
  Sales Reps: 10
  × Quota per Rep: $1M/year
  = Sales Capacity: $10M/year

Customer Retention:
  Existing Revenue: $5M
  × Retention Rate: 95%
  = Retained Revenue: $4.75M

Total Projected Revenue: $14.75M

**Requirements**:
- Document each assumption
- Cite industry benchmarks
- Show sensitivity to key variables
```

### Sensitivity Analysis

**Purpose**: Test how changes in assumptions affect outcomes

**Method**:
```markdown
Base Case: $10M revenue
Best Case (+20%): $12M revenue
Worst Case (-20%): $8M revenue

**Key Variables**:
- Market growth: ±5%
- Win rate: ±10%
- Pricing: ±15%
- Churn: ±5%

**Present as table**:
| Scenario | Revenue | Assumptions |
|----------|---------|-------------|
| Best | $12M | Market +15%, Win rate +10% |
| Base | $10M | Current assumptions |
| Worst | $8M | Market -10%, Churn +5% |

**Confidence Ranges**:
- 90% confidence: $8M - $12M range
- 50% confidence: $9.5M - $10.5M range
```

### Scenario Planning

**Three-Scenario Model**:
```markdown
**Bull Case** (30% probability):
- Best assumptions
- Everything goes right
- Revenue: $15M

**Base Case** (50% probability):
- Realistic assumptions
- Expected outcome
- Revenue: $10M

**Bear Case** (20% probability):
- Conservative assumptions
- Challenges materialize
- Revenue: $6M

**Probability-Weighted**:
= (0.30 × $15M) + (0.50 × $10M) + (0.20 × $6M)
= $4.5M + $5M + $1.2M
= $10.7M expected value
```

---

## Valuation Methods

### DCF (Discounted Cash Flow)

**Formula**:
```markdown
Company Value = Σ (FCF / (1 + WACC)^year) + Terminal Value

Where:
- FCF = Free Cash Flow (projected for 5-10 years)
- WACC = Weighted Average Cost of Capital
- Terminal Value = FCF_final × (1 + growth) / (WACC - growth)

**Example**:
Year 1 FCF: $1M, WACC: 12%, Growth: 3%
PV = $1M / 1.12 = $0.89M
[Continue for years 2-5]
Terminal Value = $1.3M × 1.03 / (0.12 - 0.03) = $14.9M
Company Value = Sum of PVs + Terminal Value

**Cite Assumptions**:
- WACC: "Industry average 12% per Damodaran 2024"
- Growth: "Conservative vs market 5% per IBISWorld"
```

### Comparable Company Analysis

**Method**:
```markdown
Find 3-5 similar public companies
Calculate multiples:
- EV/Revenue
- EV/EBITDA
- P/E ratio

Apply median multiple to your company:
Median EV/Revenue = 5.0x
Your Revenue = $10M
→ Implied Valuation = $50M

**Requirements**:
- Document comparables selection criteria
- Show multiple calculation
- Cite data sources (Yahoo Finance, CapIQ)
- Explain adjustments for differences
```

---

## Financial Reporting Standards

### Report Structure

```markdown
# Financial Analysis: [Company Name]

**Date**: [YYYY-MM-DD]
**Period**: [Q1 2024 / FY 2024]
**Standard**: GAAP / IFRS
**Analyst**: [Name]

## Executive Summary
- Revenue: $X (+Y% YoY)
- Profitability: Net margin Z%
- Cash position: $W
- Key takeaway: [1-2 sentences]

## Detailed Analysis

### Revenue Analysis
[Breakdown by segment, YoY comparison]
**Source**: [10-K page X]

### Profitability Analysis
[Margins, trends, drivers]
**Source**: [10-K page Y]

### Cash Flow Analysis
[CFO, FCF, burn rate if applicable]
**Source**: [Cash flow statement]

### Balance Sheet Health
[Liquidity, leverage ratios]
**Source**: [Balance sheet]

## Projections
[Forward-looking estimates with scenarios]
**Methodology**: [Top-down / Bottom-up / Hybrid]
**Confidence**: [Range]

## Assumptions
1. Assumption: [Statement]
   - Source: [Data source]
   - Sensitivity: [Impact if wrong by ±X%]

## Risk Factors
- Risk 1: [Description + mitigation]
- Risk 2: [Description + mitigation]

## Conclusion
[Overall assessment with confidence level]
```

### Citation Requirements

```markdown
✅ **For All Figures**:
- Source document: "Company 10-K (FY 2024)"
- Specific page: "Page 45, Revenue table"
- Date accessed: "Accessed 2024-10-27"
- Calculation shown: "Gross Margin = $6M / $10M = 60%"

❌ **Prohibited**:
- "Approximately $10M" (be exact)
- "Around 60%" (be precise)
- "Source: internet" (be specific)
- Undocumented assumptions
```

---

## Integration with Constitutional Principles

**Evidence-Based Claims**:
- All figures cited from audited financials
- Calculations shown step-by-step
- Assumptions explicitly stated

**Multi-Method Verification**:
- Cross-check with multiple sources
- Use multiple valuation methods
- Triangulate estimates

**Complete Transparency**:
- Show all calculations
- Document all assumptions
- Provide confidence ranges

**Assumption Auditing**:
- List every assumption
- Validate with industry data
- Test sensitivity

---

**These financial standards ensure accurate, compliant, and verifiable financial analysis.**
