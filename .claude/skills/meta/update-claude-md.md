---
name: update-claude-md
description: Update CLAUDE.md memory file with @import syntax and recursive imports. Use when updating project memory, configuring CLAUDE.md, adding @import statements, managing memory hierarchy, organizing constitutional principles, configuring domain methodologies, setting up framework skills, memory file updates, CLAUDE.md structure, import syntax, recursive imports, memory organization, project instructions, user instructions, memory templates, memory best practices, memory validation, import depth limits, memory hierarchy, enterprise memory, project memory, user memory, local memory, memory precedence, memory architecture, memory patterns, memory documentation
---

# Update CLAUDE.md Memory File

**Purpose**: Update CLAUDE.md with proper @import syntax and memory hierarchy following official Claude Code specifications.

**Authority**: Meta-level (manages Claude Code memory system)

**Based on**: [Official Claude Code Memory Documentation](https://docs.claude.com/en/docs/claude-code/memory.md)

---

## 📋 When to Invoke

**Invoke this skill when**:
- Updating project memory (CLAUDE.md)
- Adding @import statements
- Organizing constitutional principles
- Configuring domain methodologies
- Restructuring memory hierarchy
- Validating import syntax

**Keywords that trigger this skill**:
- "update CLAUDE.md"
- "add @import"
- "memory file"
- "project instructions"
- "@import syntax"

---

## 🎯 Official Specification (From Claude Code Docs)

### What is CLAUDE.md?

CLAUDE.md is the project memory file that provides persistent instructions to Claude. It supports:
- **@import syntax**: Include other markdown files
- **Recursive imports**: Imported files can import others (max depth 5)
- **Memory hierarchy**: Enterprise → Project → User → Local

### Import Syntax

```markdown
@path/to/file.md
@.claude/constitutional/evidence-based-claims.md
@../shared/standards.md
```

**Rules**:
- Each @import must be on its own line
- Paths can be relative or absolute
- Imported files are inserted at import location
- Max import depth: 5 levels
- Circular imports prevented

### Memory Hierarchy

```
Enterprise memory (org-wide)
  ↓ overrides ↓
Project memory (.claude/CLAUDE.md)
  ↓ overrides ↓
User memory (~/.claude/CLAUDE.md)
  ↓ overrides ↓
Local memory (conversation-specific)
```

**Precedence**: Enterprise > Project > User > Local

### File Location

**Project-level**: `.claude/CLAUDE.md` or `CLAUDE.md` (root)

**Best practice**: Use `.claude/CLAUDE.md` for organization

---

## 📋 Skill Procedure

### Step 1: Understand Current CLAUDE.md Structure

**Read existing file**:
```bash
cat .claude/CLAUDE.md
# or
cat CLAUDE.md
```

**Analyze**:
- Current sections present
- Existing @imports
- Inline content vs imported content
- Organization structure

---

### Step 2: Determine What to Import

**Constitutional principles** (should be imported):
```markdown
@.claude/constitutional/evidence-based-claims.md
@.claude/constitutional/uncertainty-escalation.md
@.claude/constitutional/multi-method-verification.md
@.claude/constitutional/complete-transparency.md
@.claude/constitutional/assumption-auditing.md
@.claude/constitutional/communication-standards.md
```

**Domain methodologies** (should be imported):
```markdown
# Software development domain
@.claude/methodologies/software/tdd-methodology.md
@.claude/methodologies/software/code-quality-standards.md
@.claude/methodologies/software/security-protocols.md
@.claude/methodologies/software/git-workflow.md
```

**Framework skills reference** (list, not full content):
```markdown
Available framework skills:
- validate-knowledge
- escalate-uncertainty
- cite-evidence
[...]
```

**Domain skills reference** (list, not full content):
```markdown
Available domain skills:
- validate-code (software)
- check-test-coverage (software)
[...]
```

**What NOT to import**:
- Skill files themselves (too large, discovered via keywords)
- Agent files (registered separately)
- Hook files (registered separately)
- Data files (not instructions)

---

### Step 3: Design CLAUDE.md Structure

**Recommended structure**:

```markdown
---
# 🎯 CORE OPERATING PRINCIPLES
---

**THESE PRINCIPLES GOVERN ALL WORK IN THIS PROJECT**

When working in Claude Code on ANY task - writing code, making decisions, debugging, researching, documenting - you MUST follow these principles. These rules override all other instructions.

---

## Constitutional Principles (Universal - ABSOLUTE Authority)

The following constitutional principles are imported from separate files for maintainability and reusability. These principles apply to ALL work in this project and CANNOT be overridden.

@.claude/constitutional/evidence-based-claims.md
@.claude/constitutional/uncertainty-escalation.md
@.claude/constitutional/multi-method-verification.md
@.claude/constitutional/complete-transparency.md
@.claude/constitutional/assumption-auditing.md
@.claude/constitutional/communication-standards.md

**Authority**: ABSOLUTE - Cannot be overridden by any other instruction

---

## Domain-Specific Methodology ({{Domain Name}})

This project is a {{domain}} project. The following methodologies define quality standards for {{domain}} work:

@.claude/methodologies/{{domain}}/{{methodology-1}}.md
@.claude/methodologies/{{domain}}/{{methodology-2}}.md
@.claude/methodologies/{{domain}}/{{methodology-3}}.md

**Authority**: HIGH - Domain-specific standards that apply to all {{domain}} tasks

---

## Framework Skills (Keyword-Discoverable)

The following framework skills enforce constitutional principles and are keyword-discoverable for agent invocation:

**Available Skills**:
- `skill-name-1` - Description
- `skill-name-2` - Description
[...]

**Location**: `.claude/skills/framework/`

Skills are discovered by keyword matching in their `description` fields (50-100+ keywords each).

---

## Domain Skills (Keyword-Discoverable)

The following domain-specific skills provide {{domain}} capabilities:

**Available Skills**:
- `domain-skill-1` - Description
- `domain-skill-2` - Description
[...]

**Location**: `.claude/skills/{{domain}}/`

---

## {{Additional Sections}}

[Project-specific instructions that don't fit above categories]

---

---
# 📚 DETAILED DOCUMENTATION
---

For comprehensive guides, see:

- **[Guide 1](docs/guide1.md)** - Description
- **[Guide 2](docs/guide2.md)** - Description
[...]

---
```

---

### Step 4: Create Import Files

**If constitutional principles don't exist yet**, create them first:

```bash
mkdir -p .claude/constitutional
```

Then create each principle file (see examples below).

**If domain methodologies don't exist yet**, create them:

```bash
mkdir -p .claude/methodologies/{{domain}}
```

Then create each methodology file.

---

### Step 5: Update CLAUDE.md with Imports

**Replace inline content with @imports**:

**Before** (inline content):
```markdown
# Constitutional Principles

## Evidence-Based Claims

Every factual claim MUST be supported by verifiable evidence.

[... 500 lines of content ...]
```

**After** (@import):
```markdown
## Constitutional Principles (Universal - ABSOLUTE Authority)

@.claude/constitutional/evidence-based-claims.md
@.claude/constitutional/uncertainty-escalation.md
[...]
```

**Benefits**:
- CLAUDE.md stays concise (~200 lines instead of 5,000)
- Principles are reusable across projects
- Updates propagate to all projects importing them
- Clear separation of concerns
- Easier to maintain

---

### Step 6: Validate Import Syntax

**Check for common errors**:

```bash
# Check @imports are on own lines
grep -n '@' .claude/CLAUDE.md

# Verify imported files exist
grep '^@' .claude/CLAUDE.md | sed 's/@//' | while read file; do
  if [ ! -f "$file" ]; then
    echo "ERROR: File not found: $file"
  fi
done

# Check for circular imports (manual inspection)
# A imports B, B imports A = circular (not allowed)
```

**Valid @import**:
```markdown
@.claude/constitutional/evidence-based-claims.md
```

**Invalid @import**:
```markdown
@ .claude/constitutional/evidence-based-claims.md  # ❌ Space after @
@.claude/constitutional/evidence-based-claims.md (optional)  # ❌ Text after path
```

---

### Step 7: Test Memory Loading

**Verify imports load correctly**:

1. Start new Claude Code session
2. Check that imported content is active
3. Verify no import errors in logs
4. Test that principles are being followed

**Indicators memory is working**:
- Agent follows constitutional principles
- Domain methodologies are applied
- Skills are discoverable
- No "I don't see any instructions" messages

---

## 📊 Output Format

```yaml
claude_md_updated:
  path: ".claude/CLAUDE.md"
  total_lines: {{COUNT}}
  imports_count: {{COUNT}}
  imports:
    - path: "{{import-path}}"
      exists: "{{YES|NO}}"
      depth: {{LEVEL}}
    [...]
  sections:
    - "Constitutional Principles"
    - "Domain Methodologies"
    - "Framework Skills"
    [...]
  validation: "{{PASS|FAIL}}"
  circular_imports: "{{NONE|DETECTED}}"
  max_import_depth: {{NUMBER}}/5
```

---

## 💡 CLAUDE.md Examples

### Example 1: Software Development Project

**File**: `.claude/CLAUDE.md`

```markdown
---
# 🎯 CORE OPERATING PRINCIPLES
---

**THESE PRINCIPLES GOVERN ALL WORK IN THIS PROJECT**

When working in Claude Code on ANY task - writing code, making decisions, debugging, researching, documenting - you MUST follow these principles. These rules override all other instructions.

---

## Constitutional Principles (Universal - ABSOLUTE Authority)

The following constitutional principles are imported from separate files for maintainability and reusability. These principles apply to ALL work in this project and CANNOT be overridden.

@.claude/constitutional/evidence-based-claims.md
@.claude/constitutional/uncertainty-escalation.md
@.claude/constitutional/multi-method-verification.md
@.claude/constitutional/complete-transparency.md
@.claude/constitutional/assumption-auditing.md
@.claude/constitutional/communication-standards.md

**Authority**: ABSOLUTE - Cannot be overridden by any other instruction

---

## Domain-Specific Methodology (Software Development)

This project is a software development project. The following methodologies define quality standards for software development work:

@.claude/methodologies/software/tdd-methodology.md
@.claude/methodologies/software/code-quality-standards.md
@.claude/methodologies/software/security-protocols.md
@.claude/methodologies/software/git-workflow.md

**Authority**: HIGH - Domain-specific standards that apply to all software development tasks

---

## Framework Skills (Keyword-Discoverable)

The following framework skills enforce constitutional principles and are keyword-discoverable for agent invocation:

**Available Skills**:
- `validate-knowledge` - Validate knowledge graph additions meet confidence thresholds
- `escalate-uncertainty` - Escalate when confidence < 90%
- `cite-evidence` - Ensure all claims have verifiable evidence
- `validate-assumptions` - Identify and validate assumptions before proceeding
- `multi-method-verify` - Verify with ≥2 independent methods
- `bridge-compress` - Compress knowledge graph to top-N nodes for handoffs

**Location**: `.claude/skills/framework/`

Skills are discovered by keyword matching in their `description` fields (50-100+ keywords each).

---

## Domain Skills (Keyword-Discoverable)

The following software development skills provide code quality capabilities:

**Available Skills**:
- `validate-code` - Code quality validation (DRY, SOLID, Clean Code)
- `check-test-coverage` - Verify test coverage ≥80%
- `security-scan` - OWASP Top 10 vulnerability scanning
- `pre-commit-review` - Automated quality checks before commits
- `git-commit-validate` - Validate conventional commits format

**Location**: `.claude/skills/software/`

---

## Triad Workflows

This project uses a 5-triad workflow for structured development:

1. **Idea Validation** - Research ideas, validate community need
2. **Design** - Create architecture, make decisions, write ADRs
3. **Implementation** - Write code, create tests, ensure quality
4. **Garden Tending** - Refactor, reduce debt, improve quality
5. **Deployment** - Create releases, update docs, publish

**Routing**: Agent suggests appropriate triad based on user intent.

---

---
# 📚 DETAILED DOCUMENTATION
---

For comprehensive guides, see:

- **[Architecture](docs/ARCHITECTURE.md)** - System design and components
- **[Usage Guide](docs/USAGE.md)** - Working with generated triads
- **[Installation](docs/INSTALLATION.md)** - Setup instructions
- **[Claude Code Docs](https://docs.claude.com/en/docs/claude-code)** - Official reference

---
```

**Result**: ~80 lines in CLAUDE.md, ~6,000+ lines in imported files

---

### Example 2: Research Project

**File**: `.claude/CLAUDE.md`

```markdown
---
# 🎯 CORE OPERATING PRINCIPLES
---

**THESE PRINCIPLES GOVERN ALL RESEARCH WORK**

---

## Constitutional Principles (Universal - ABSOLUTE Authority)

@.claude/constitutional/evidence-based-claims.md
@.claude/constitutional/uncertainty-escalation.md
@.claude/constitutional/multi-method-verification.md
@.claude/constitutional/complete-transparency.md
@.claude/constitutional/assumption-auditing.md
@.claude/constitutional/communication-standards.md

**Authority**: ABSOLUTE - Cannot be overridden

---

## Domain-Specific Methodology (Research)

This is a research project. The following methodologies define research standards:

@.claude/methodologies/research/literature-review.md
@.claude/methodologies/research/statistical-analysis.md
@.claude/methodologies/research/data-collection.md
@.claude/methodologies/research/academic-writing.md

**Authority**: HIGH - Research standards that apply to all work

---

## Framework Skills

**Available Skills**:
- `validate-knowledge` - Validate research findings meet confidence thresholds
- `cite-evidence` - Ensure all claims have academic citations
- `multi-method-verify` - Cross-validate findings with ≥2 methods

**Location**: `.claude/skills/framework/`

---

## Domain Skills (Research)

**Available Skills**:
- `literature-search` - Search academic databases (PubMed, Google Scholar)
- `statistical-test` - Run statistical tests with proper validation
- `citation-format` - Format citations (APA, MLA, Chicago)
- `data-visualization` - Create publication-quality figures

**Location**: `.claude/skills/research/`

---

## Research Workflow

1. **Literature Review** - Search, evaluate, synthesize papers
2. **Study Design** - Create research protocol, IRB submission
3. **Data Collection** - Gather data following protocol
4. **Analysis** - Statistical analysis, visualization
5. **Writing** - Draft manuscript, revisions, submission

---

---
# 📚 DOCUMENTATION
---

- **[Research Protocol](docs/protocol.md)**
- **[Data Dictionary](docs/data-dictionary.md)**
- **[Analysis Plan](docs/analysis-plan.md)**

---
```

---

### Example 3: Content Creation Project

**File**: `.claude/CLAUDE.md`

```markdown
---
# 🎯 CORE OPERATING PRINCIPLES
---

**THESE PRINCIPLES GOVERN ALL CONTENT CREATION WORK**

---

## Constitutional Principles (Universal - ABSOLUTE Authority)

@.claude/constitutional/evidence-based-claims.md
@.claude/constitutional/uncertainty-escalation.md
@.claude/constitutional/multi-method-verification.md
@.claude/constitutional/complete-transparency.md
@.claude/constitutional/assumption-auditing.md
@.claude/constitutional/communication-standards.md

**Authority**: ABSOLUTE - Cannot be overridden

---

## Domain-Specific Methodology (Content Creation)

This is a content creation project. The following methodologies define content standards:

@.claude/methodologies/content/writing-standards.md
@.claude/methodologies/content/seo-optimization.md
@.claude/methodologies/content/readability-guidelines.md
@.claude/methodologies/content/fact-checking.md

**Authority**: HIGH - Content standards that apply to all work

---

## Framework Skills

**Available Skills**:
- `validate-knowledge` - Validate content claims
- `cite-evidence` - Ensure factual claims are cited
- `multi-method-verify` - Cross-verify facts with ≥2 sources

**Location**: `.claude/skills/framework/`

---

## Domain Skills (Content)

**Available Skills**:
- `readability-check` - Check Flesch-Kincaid score, grade level
- `seo-optimize` - Optimize for keywords, meta descriptions
- `fact-check` - Verify claims against authoritative sources
- `plagiarism-check` - Check for duplicate content

**Location**: `.claude/skills/content/`

---

## Content Workflow

1. **Research** - Gather facts, verify sources
2. **Outline** - Structure content, create headings
3. **Draft** - Write initial version
4. **Optimize** - SEO, readability, clarity
5. **Review** - Fact-check, edit, polish
6. **Publish** - Format, schedule, distribute

---

---
# 📚 STYLE GUIDES
---

- **[Brand Voice](docs/brand-voice.md)**
- **[AP Stylebook](docs/ap-style.md)**
- **[SEO Guidelines](docs/seo.md)**

---
```

---

## 🎯 Import Best Practices

### 1. Progressive Disclosure

**Load only what's needed**:

```markdown
# ✅ GOOD - List skills, don't import full files
Available skills:
- validate-code
- check-test-coverage
[...]

# ❌ BAD - Importing huge skill files
@.claude/skills/software/validate-code.md  # 900 lines loaded always
```

**Why**: Skills are discovered by keywords, full content loaded only when invoked

---

### 2. Clear Authority Hierarchy

**Document precedence**:

```markdown
## Constitutional Principles
**Authority**: ABSOLUTE

## Domain Methodologies
**Authority**: HIGH

## Project Guidelines
**Authority**: MEDIUM
```

**Why**: Resolves conflicts when instructions disagree

---

### 3. Modular Organization

**Separate concerns**:

```
.claude/
├── constitutional/        # Universal principles
├── methodologies/        # Domain-specific standards
│   ├── software/
│   ├── research/
│   └── content/
├── skills/              # Capabilities
│   ├── framework/       # Constitutional enforcement
│   └── {{domain}}/      # Domain-specific
└── CLAUDE.md            # Main memory file
```

**Why**: Reusable across projects, easier to maintain

---

### 4. Avoid Circular Imports

**❌ BAD - Circular import**:
```markdown
# File A
@file-b.md

# File B
@file-a.md  # ❌ Circular!
```

**✅ GOOD - Hierarchical**:
```markdown
# CLAUDE.md
@constitutional/principles.md

# constitutional/principles.md
# (no imports back to CLAUDE.md)
```

---

### 5. Document Import Purpose

**Add comments**:

```markdown
## Constitutional Principles (Universal - ABSOLUTE Authority)

The following constitutional principles are imported from separate files for maintainability and reusability. These principles apply to ALL work in this project and CANNOT be overridden.

@.claude/constitutional/evidence-based-claims.md
[...]
```

**Why**: Explains why imports exist, what they provide

---

### 6. Validate Imports Regularly

**Check for broken imports**:

```bash
#!/bin/bash
# validate-imports.sh

echo "Validating CLAUDE.md imports..."

grep '^@' .claude/CLAUDE.md | sed 's/@//' | while read file; do
  if [ -f "$file" ]; then
    echo "✅ $file"
  else
    echo "❌ MISSING: $file"
  fi
done
```

**Run regularly**: On commit, in CI/CD

---

## 🎯 Import Depth Example

```markdown
# Level 1: CLAUDE.md
@.claude/constitutional/evidence-based-claims.md

# Level 2: evidence-based-claims.md
@.claude/constitutional/shared/verification-protocol.md

# Level 3: verification-protocol.md
@.claude/constitutional/shared/confidence-calculation.md

# Level 4: confidence-calculation.md
@.claude/constitutional/shared/evidence-types.md

# Level 5: evidence-types.md
@.claude/constitutional/shared/source-authority.md

# Level 6: source-authority.md (MAX DEPTH REACHED)
# ❌ Cannot import further - 5 level limit
```

**Max depth**: 5 levels to prevent performance issues

---

## 🎯 Memory Hierarchy Example

### Enterprise Memory (Organization-wide)

**File**: (Managed by org admin, not in project)

```markdown
# Acme Corp Engineering Standards

All projects must follow:
@acme-corp/standards/code-quality.md
@acme-corp/standards/security.md
@acme-corp/standards/compliance.md
```

### Project Memory

**File**: `.claude/CLAUDE.md`

```markdown
# Project-specific standards

@.claude/constitutional/evidence-based-claims.md
@.claude/methodologies/software/tdd-methodology.md

# Project-specific overrides
## Deployment Process

Our deployment process differs from company standard:
[custom instructions]
```

### User Memory

**File**: `~/.claude/CLAUDE.md`

```markdown
# Personal preferences

I prefer:
- Concise responses
- Python examples over pseudocode
- Explicit type annotations
```

### Precedence in Action

```
User asks: "How should I format code?"

1. Check Enterprise memory: "Use Acme Corp style guide"
2. Check Project memory: "Follow TDD methodology" (overrides enterprise)
3. Check User memory: "Use type annotations" (adds to project)
4. Apply all in order: Project TDD + User type annotations
```

---

## 🎯 Success Criteria

- [ ] CLAUDE.md file exists at `.claude/CLAUDE.md`
- [ ] All @imports on separate lines
- [ ] Imported files exist and are readable
- [ ] No circular imports
- [ ] Import depth ≤5 levels
- [ ] Clear section headers
- [ ] Authority levels documented
- [ ] Skills listed (not fully imported)
- [ ] Validation script passes
- [ ] Memory loads successfully in Claude Code

---

**This skill updates CLAUDE.md with proper @import syntax following official specifications.**

**Version**: 1.0.0
**Last Updated**: 2025-10-27
**Source**: [Claude Code Memory Docs](https://docs.claude.com/en/docs/claude-code/memory.md)
