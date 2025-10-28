# Domain Methodology Templates

This directory contains domain-specific methodology templates used by the Generator Triad when creating custom workflows.

---

## Directory Structure

```
methodologies/
├── software/           # Software development methodologies
│   ├── tdd-methodology.md
│   ├── code-quality-standards.md
│   ├── security-protocols.md
│   └── git-workflow.md
├── research/           # Academic/scientific research methodologies
│   ├── research-protocols.md
│   ├── citation-standards.md
│   ├── data-integrity.md
│   └── peer-review-checklist.md
├── content/            # Content creation methodologies (TODO: Complete)
│   ├── editorial-standards.md
│   ├── seo-guidelines.md
│   ├── style-guides.md
│   └── publishing-workflow.md
└── business/           # Business analysis methodologies (TODO: Complete)
    ├── analysis-frameworks.md
    ├── financial-standards.md
    ├── market-research-protocols.md
    └── reporting-standards.md
```

---

## Completed Methodologies

### Software Development Domain (✅ Complete)

1. **TDD Methodology** (tdd-methodology.md)
   - Red-Green-Refactor cycle
   - Test-first development
   - Coverage requirements (≥80%)
   - Quality gates

2. **Code Quality Standards** (code-quality-standards.md)
   - DRY principle
   - SOLID principles
   - Code smells and fixes
   - Static analysis tools (black, flake8, mypy)

3. **Security Protocols** (security-protocols.md)
   - OWASP Top 10
   - Input validation
   - Secrets management
   - Security testing

4. **Git Workflow** (git-workflow.md)
   - Feature branch workflow
   - Conventional commits
   - Pull request process
   - Git hooks

### Research Domain (✅ Complete)

1. **Research Protocols** (research-protocols.md)
   - Scientific method
   - Study design (RCT, observational)
   - Sample size calculation
   - Statistical analysis
   - Reproducibility requirements

2. **Citation Standards** (citation-standards.md)
   - APA, MLA, Chicago formats
   - Reference management (Zotero, Mendeley)
   - Citation integrity
   - Primary vs secondary sources

3. **Data Integrity** (data-integrity.md)
   - FAIR principles
   - Data collection SOPs
   - Quality control (double-entry)
   - Data sharing and archiving

4. **Peer Review Checklist** (peer-review-checklist.md)
   - CONSORT/PRISMA compliance
   - Pre-submission self-review
   - Common reviewer criticisms
   - Response strategies

---

## Pending Methodologies

### Content Creation Domain (⚠️ In Progress)

Templates needed:
1. **Editorial Standards** - Style guides, tone/voice, fact-checking
2. **SEO Guidelines** - Keyword research, meta descriptions, on-page SEO
3. **Style Guides** - AP Stylebook, Chicago Manual, house style
4. **Publishing Workflow** - Editorial calendar, review process, distribution

### Business Analysis Domain (⚠️ In Progress)

Templates needed:
1. **Analysis Frameworks** - Porter's 5 Forces, SWOT, BCG Matrix
2. **Financial Standards** - NPV, IRR, ROI calculations, assumptions
3. **Market Research Protocols** - TAM/SAM/SOM sizing, competitive analysis
4. **Reporting Standards** - Executive summaries, dashboards, KPIs

---

## How Methodologies Are Used

### By Domain Researcher Agent

When classifying a user's domain, Domain Researcher checks if methodology templates exist:

```markdown
Domain classified: software-development
Template availability: EXISTS

Methodologies found:
- TDD (test-driven development)
- Code quality standards (DRY, SOLID)
- Security protocols (OWASP Top 10)
- Git workflow (feature branches, conventional commits)
```

### By Workflow Analyst Agent

When designing triad structure, Workflow Analyst specifies which methodologies apply:

```markdown
Domain: software-development
Methodologies to enforce:
- TDD methodology (via senior-developer agent)
- Code quality (via code-reviewer agent)
- Security protocols (via security-analyst agent)
- Git workflow (via git-workflow skill)
```

### By Triad Architect Agent

When generating files, Triad Architect:

**IF template_availability == "exists"**:
- Copies methodology files from `templates/methodologies/{domain}/`
- Imports them in generated CLAUDE.md via @import syntax
- Generates domain-specific skills that reference methodologies

**IF template_availability == "needs_creation"**:
- Uses Domain Researcher's methodology research findings
- Generates custom methodology files
- Creates custom skills based on discovered quality standards

---

## Methodology Template Standards

All methodology templates follow this structure:

```markdown
# [Methodology Name]

**Authority Level**: DOMAIN-CONDITIONAL (applies to [domain] domain)
**Enforcement**: [agents, skills, hooks that enforce this]
**Prerequisite**: Constitutional principles + [other methodologies]

---

## [Methodology] Statement

**MANDATE**: [What must be done]

**[Quality aspect] is constitutional law for [domain] workflows.**

---

## [Main Sections]

[Detailed methodology content organized by phases/principles]

---

## [Domain] Quality Checklist

Before claiming [work type] complete:

- [ ] [Quality criterion 1]
- [ ] [Quality criterion 2]
- [ ] [Quality criterion 3]
...

**If ANY box is unchecked, [work type] is NOT complete.**

---

## Constitutional Integration

[Methodology name] enforces constitutional principles:

- **Evidence-Based Claims**: [How this methodology provides evidence]
- **Multi-Method Verification**: [How multiple methods verify quality]
- **Complete Transparency**: [How transparency is maintained]
- **[Other principles]**: [Integration]

**[Quality aspect] is not optional. It is constitutional law for [domain] workflows.**
```

---

## Integration with Constitutional Principles

**Universal Constitutional Principles** (always apply):
- Evidence-based claims
- Uncertainty escalation
- Multi-method verification
- Complete transparency
- Assumption auditing
- Communication standards

**Domain Methodologies** (conditional):
- Software: TDD, code quality, security, git workflow
- Research: Research protocols, citations, data integrity, peer review
- Content: Editorial, SEO, style, publishing
- Business: Analysis, financial, market research, reporting

**Hierarchy**:
```
Constitutional Principles (ABSOLUTE)
    ↓
Domain Methodologies (CONDITIONAL on domain)
    ↓
Project-Specific Standards (team/organization preferences)
```

---

## For Contributors

To add a new methodology template:

1. Create markdown file in appropriate domain directory
2. Follow template structure above
3. Include comprehensive examples
4. Provide checklists for quality gates
5. Integrate with constitutional principles
6. Update this README.md

To add a new domain:

1. Create directory: `templates/methodologies/{domain}/`
2. Research domain-specific quality standards
3. Create 3-5 methodology files covering main quality aspects
4. Update Domain Researcher agent to recognize new domain
5. Update Workflow Analyst to specify domain skills
6. Update Triad Architect to handle new domain templates

---

## Status Summary

| Domain | Files | Status | Completeness |
|--------|-------|--------|--------------|
| Software | 4/4 | ✅ Complete | 100% |
| Research | 4/4 | ✅ Complete | 100% |
| Content | 0/4 | ⚠️ Pending | 0% |
| Business | 0/4 | ⚠️ Pending | 0% |

**Total**: 8/16 methodology files complete (50%)

**Priority**: Content and business domain templates needed for full domain coverage.

---

## Next Steps

1. ✅ Complete software methodology templates (4 files)
2. ✅ Complete research methodology templates (4 files)
3. ⚠️ Complete content methodology templates (4 files) - IN PROGRESS
4. ⚠️ Complete business methodology templates (4 files) - PENDING
5. ⏸️ Create skill templates that reference these methodologies
6. ⏸️ Test Generator Triad with all domains

---

**Note**: While content and business templates are pending, the Generator Triad can still function by using the "needs_creation" path - generating custom methodologies from Domain Researcher's web research findings. However, having pre-made templates is more efficient and ensures consistent quality standards.
