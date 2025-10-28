---
name: create-skill-file
description: Create Claude Code skill files with keyword-rich descriptions for LLM discovery. Use when generating skills, creating reusable tasks, writing skill markdown, setting up skill directories, configuring skill tools, skill templates, skill creation, skill file generation, skill configuration, skill descriptions, keyword optimization, skill discovery, LLM activation, skill frontmatter, YAML skill metadata, allowed tools, skill procedures, progressive disclosure, skill reference files, skill scripts, skill supporting files, focused skills, single capability skills, skill best practices, skill file structure, project skills, user skills, skill storage locations, skill documentation, skill examples, skill version history, narrowly-focused skills, skill activation patterns
---

# Create Skill File

**Purpose**: Generate Claude Code skill files with keyword-rich descriptions optimized for LLM discovery following official Claude Code specifications.

**Authority**: Meta-level (creates Claude Code components)

**Based on**: [Official Claude Code Skills Documentation](https://docs.claude.com/en/docs/claude-code/skills.md)

---

## 📋 When to Invoke

**Invoke this skill when**:
- Generating new domain skills
- Creating framework skills
- Setting up reusable task definitions
- Optimizing skill keyword discovery
- Validating skill file structure

**Keywords that trigger this skill**:
- "create skill"
- "generate skill"
- "skill file"
- "new skill"
- "skill template"
- "keyword optimization"

---

## 🎯 Official Specification (From Claude Code Docs)

### Frontmatter Requirements

Skills require YAML frontmatter with **two mandatory fields**:

| Field | Requirement | Details |
|-------|-------------|---------|
| `name` | **MANDATORY** | Lowercase letters, numbers, hyphens only (max 64 characters) |
| `description` | **MANDATORY** | Brief description (max 1024 characters) - CRITICAL for discovery |
| `allowed-tools` | Optional | Restrict which tools Claude can use when skill is active |

### Description Field for Discovery (CRITICAL)

**The description is critical for keyword activation.** It should articulate both the skill's functionality and contextual triggers.

**Best practices**:
- Include specific terms users mention (file formats, operations)
- Be explicit about when to use the skill
- Include synonyms and related keywords
- Mention file extensions if relevant

**Example (good)**:
```yaml
description: Analyze Excel spreadsheets, generate pivot tables, create charts. Use when working with Excel files, spreadsheets, or .xlsx files.
```

**Example (bad)**:
```yaml
description: Helps with data
```

Vague descriptions impair discovery. Instead of "Helps with data," specify the data type, operations, and when Claude should activate the skill.

### File Structure

Each skill consists of a directory containing `SKILL.md` (required) plus optional supporting files:

```
skill-name/
├── SKILL.md           # Required: Main skill definition
├── reference.md       # Optional: Additional context
├── scripts/           # Optional: Helper scripts
└── templates/         # Optional: Template files
```

Claude loads supplementary files only when needed, using **progressive disclosure** for context efficiency.

### Storage Locations

- **Project skills**: `.claude/skills/` (shared with team)
- **User skills**: `~/.claude/skills/` (personal use)
- **Subdirectories**: Organize by category (e.g., `.claude/skills/software/validate-code.md`)

---

## 📋 Skill Procedure

### Step 1: Gather Skill Specifications

**Required information**:
```yaml
skill_spec:
  name: "{{skill-identifier}}"  # lowercase-with-hyphens, max 64 chars
  category: "{{framework|software|research|content|business|meta}}"
  domain: "{{domain-type}}"  # e.g., software-development, research
  description_short: "{{1-sentence-purpose}}"

  # Keyword optimization (CRITICAL)
  primary_keywords: [{{list-main-keywords}}]
  synonyms: [{{list-synonyms}}]
  use_cases: [{{when-to-invoke}}]
  file_extensions: [{{if-applicable}}]  # e.g., .xlsx, .py, .md

  # Functionality
  purpose: "{{what-skill-does}}"
  when_to_invoke: [{{scenario-list}}]
  procedure_steps: [{{step-by-step}}]
  output_format: "{{expected-output}}"

  # Optional
  allowed_tools: [{{tool-list}}]  # omit to allow all
  reference_files: [{{additional-docs}}]
  scripts: [{{helper-scripts}}]
  templates: [{{template-files}}]
```

**Example**:
```yaml
skill_spec:
  name: "validate-code"
  category: "software"
  domain: "software-development"
  description_short: "Validate code quality against DRY, SOLID, Clean Code principles"

  primary_keywords:
    - "validate code"
    - "code quality"
    - "DRY principle"
    - "SOLID principles"
    - "Clean Code"

  synonyms:
    - "check code quality"
    - "code review"
    - "quality check"
    - "code validation"

  use_cases:
    - "before commit"
    - "during code review"
    - "quality gates"
    - "refactoring"

  file_extensions:
    - ".py"
    - ".js"
    - ".ts"

  allowed_tools:
    - "Read"
    - "Bash"
    - "Grep"
```

---

### Step 2: Create Keyword-Rich Description

**Description format** (max 1024 characters):

```
{{Primary-purpose}}. {{Key-capabilities}}. Use when {{trigger-scenarios}}. {{File-types-or-operations}}. {{Related-keywords}}.
```

**Keyword optimization strategy**:

1. **Primary keywords first** (what the skill does)
2. **Synonyms** (alternative ways to say it)
3. **Use cases** (when to invoke)
4. **File types** (if applicable)
5. **Related operations** (associated tasks)

**Example (validate-code skill)**:
```yaml
description: Validate code quality against DRY SOLID Clean Code principles check for code smells duplication complexity violations naming conventions function length class size cyclomatic complexity validate software quality code review automated quality checks detect code smells measure code complexity check DRY violations SOLID principles adherence clean code standards code maintainability code readability refactoring opportunities technical debt detection code metrics quality scoring linting static analysis code patterns best practices programming standards software craftsmanship
```

**Character count**: ~500 characters (within 1024 limit)

**Keywords included**: 50+ keywords covering:
- Core concepts (DRY, SOLID, Clean Code)
- Operations (validate, check, detect, measure)
- Use cases (code review, quality checks)
- Related terms (maintainability, readability, refactoring)

---

### Step 3: Create YAML Frontmatter

```yaml
---
name: {{skill-identifier}}
description: {{keyword-rich-description-max-1024-chars}}
allowed-tools: {{optional-comma-separated-tools}}
---
```

**Requirements**:
- `name`: Lowercase, numbers, hyphens only (max 64 chars)
- `description`: Max 1024 characters, keyword-optimized
- `allowed-tools`: Optional - omit to allow all tools

**Validation**:
- No tabs in YAML (use spaces)
- Correct indentation
- No special characters in name (except hyphens)

---

### Step 4: Create Skill Content

**Standard skill structure**:

```markdown
---
name: {{skill-name}}
description: {{keyword-rich-description}}
allowed-tools: {{optional-tools}}
---

# {{Skill Title}}

**Purpose**: {{What this skill does}}

**Domain**: {{Domain type}}

**Authority**: {{authority-level}}

---

## 📋 When to Invoke

**Invoke this skill when**:
- {{Scenario 1}}
- {{Scenario 2}}
- {{Scenario 3}}

**Keywords that trigger this skill**:
- "{{keyword1}}"
- "{{keyword2}}"
- "{{keyword3}}"

---

## 🎯 {{Methodology/Standards}} (From Methodology)

This skill enforces standards from `@.claude/{{methodology-path}}`:

{{Standards content}}

---

## 📋 Skill Procedure

### Step 1: {{First-step-name}}

**Purpose**: {{What this step does}}

**Actions**:
{{Instructions}}

**Example**:
{{Concrete example}}

---

### Step 2: {{Second-step-name}}

**Purpose**: {{What this step does}}

**Actions**:
{{Instructions}}

**Example**:
{{Concrete example}}

---

[Continue for all steps...]

---

## 📊 Output Format

```yaml
{{skill_name}}_output:
  field1: "{{VALUE}}"
  field2: {{COUNT}}
  field3:
    - "{{ITEM}}"
  status: "{{PASS|FAIL}}"
```

---

## 💡 Usage Examples

### Example 1: {{Scenario-name}}

**Context**: {{Setup}}

**Invocation**: {{How skill is triggered}}

**Result**:
{{Expected output}}

---

### Example 2: {{Scenario-name}}

[Continue for multiple examples...]

---

## 🎯 Success Criteria

- [ ] {{Criterion 1}}
- [ ] {{Criterion 2}}
- [ ] {{Criterion 3}}

---

## 🔗 Integration with Constitutional Principles

This skill enforces:
- ✅ {{Principle 1}}: {{How enforced}}
- ✅ {{Principle 2}}: {{How enforced}}

---

## 📚 Related Skills

- **{{related-skill-1}}** - {{When to use instead}}
- **{{related-skill-2}}** - {{When to use instead}}

---

**This skill {{purpose-summary}}.**

**Version**: {{version}}
**Last Updated**: {{date}}
**Source**: {{methodology-reference}}
```

---

### Step 5: Create Skill Directory Structure

**For simple skills** (single file):
```bash
# Create skill file directly
mkdir -p .claude/skills/{{category}}
```

**For complex skills** (with supporting files):
```bash
# Create skill directory
mkdir -p .claude/skills/{{category}}/{{skill-name}}
mkdir -p .claude/skills/{{category}}/{{skill-name}}/scripts
mkdir -p .claude/skills/{{category}}/{{skill-name}}/templates

# Files:
# - SKILL.md (required)
# - reference.md (optional)
# - scripts/*.sh or *.py (optional)
# - templates/*.template (optional)
```

**Progressive disclosure**: Claude loads reference files and scripts only when needed, keeping initial context efficient.

---

### Step 6: Write Skill File

**Simple skill** (single file):
```bash
# Path: .claude/skills/{{category}}/{{skill-name}}.md
```

**Complex skill** (directory with SKILL.md):
```bash
# Path: .claude/skills/{{category}}/{{skill-name}}/SKILL.md
```

**Validation checklist**:
- [ ] YAML frontmatter present
- [ ] `name`: lowercase-with-hyphens, max 64 chars
- [ ] `description`: max 1024 chars, keyword-rich
- [ ] `allowed-tools`: omitted OR comma-separated list
- [ ] Content includes: Purpose, When to Invoke, Procedure, Output, Examples
- [ ] No tabs in YAML (spaces only)
- [ ] Correct indentation

---

### Step 7: Optimize Keyword Discovery

**Keyword optimization checklist**:

```yaml
keyword_analysis:
  primary_action_verbs: [{{validate, check, analyze, generate}}]
  domain_terms: [{{code, quality, DRY, SOLID}}]
  use_case_triggers: [{{before commit, code review}}]
  file_extensions: [{{.py, .js}}]
  synonyms: [{{alternative-terms}}]
  related_operations: [{{associated-tasks}}]

  total_keywords: {{COUNT}}
  target: 50+
  coverage: "{{GOOD|NEEDS_MORE}}"
```

**Test keyword coverage**:
- Include 50-100+ keywords in description
- Cover multiple ways users might describe the task
- Include file extensions if file-type specific
- Add operation verbs (validate, check, analyze, generate)
- Include domain terminology

---

### Step 8: Validate Skill File

**Validation**:

```bash
# Check file exists
ls .claude/skills/{{category}}/{{skill-name}}.md
# OR for complex skills:
ls .claude/skills/{{category}}/{{skill-name}}/SKILL.md

# Check frontmatter format
head -10 .claude/skills/{{category}}/{{skill-name}}.md

# Verify YAML is valid
grep -A 3 "^---$" .claude/skills/{{category}}/{{skill-name}}.md | head -4

# Count description length
grep "description:" .claude/skills/{{category}}/{{skill-name}}.md | wc -c
```

**Expected output**:
```
---
name: skill-name
description: Keyword-rich description under 1024 characters...
allowed-tools: Read, Bash, Grep
---
```

**Description length**: <1024 characters

---

## 📊 Output Format

```yaml
skill_file_created:
  path: ".claude/skills/{{category}}/{{skill-name}}.md"
  frontmatter:
    name: "{{name}}"
    description_length: {{COUNT}}
    keywords_count: {{COUNT}}
    allowed_tools: "{{tools}}"

  structure:
    has_purpose: true
    has_when_to_invoke: true
    has_procedure: true
    has_output_format: true
    has_examples: true
    step_count: {{COUNT}}

  keyword_optimization:
    primary_keywords: {{COUNT}}
    synonyms: {{COUNT}}
    use_cases: {{COUNT}}
    total_keywords: {{COUNT}}
    target: 50+
    quality: "{{EXCELLENT|GOOD|NEEDS_IMPROVEMENT}}"

  validation: "{{PASS|FAIL}}"
  file_size_lines: {{COUNT}}
```

---

## 💡 Best Practices (From Official Docs)

1. **Narrow Focus**: "Keep Skills focused on single capabilities rather than broad domains"
2. **Keyword Optimization**: Include specific terms users mention, file formats, operations
3. **Test Activation**: "Test with team members to validate activation patterns"
4. **Version History**: "Document version history within markdown content"
5. **Progressive Disclosure**: Use reference files and scripts for additional context (loaded on-demand)
6. **YAML Validation**: "Verify YAML syntax (no tabs, correct indentation)"
7. **Team Sharing**: Store project skills in `.claude/skills/` for version control
8. **Avoid Vague Descriptions**: Be specific about data types, operations, and triggers

---

## 🎯 Example: Complete Skill File

```markdown
---
name: check-test-coverage
description: Verify test coverage meets threshold check coverage ≥80% verify coverage thresholds test coverage analysis coverage reports coverage metrics line coverage branch coverage function coverage statement coverage pytest coverage pytest-cov coverage.py coverage validation quality gates coverage requirements ensure adequate testing test suite completeness missing coverage gaps untested code coverage enforcement testing standards TDD compliance test quality assurance coverage thresholds coverage percentage coverage analysis coverage reporting coverage gaps detection
---

# Check Test Coverage

**Purpose**: Verify test coverage meets or exceeds threshold (≥80% overall, ≥90% for critical modules).

**Domain**: Software Development

**Authority**: Domain-specific TDD methodology enforcement

---

## 📋 When to Invoke

**Invoke this skill when**:
- Before committing code (test-engineer)
- During pre-commit checks (automated)
- Before creating pull requests
- Validating quality gates
- After writing new tests

**Keywords that trigger this skill**:
- "check test coverage"
- "verify coverage"
- "coverage threshold"
- "test coverage report"
- "coverage analysis"

---

## 🎯 TDD Methodology Standards (From Methodology)

This skill enforces standards from `@.claude/methodologies/software/tdd-methodology.md`:

### Coverage Thresholds

- **Overall coverage**: ≥80% (minimum)
- **Critical modules**: ≥90% (authentication, payment, security)
- **New code**: 100% (target)

### Coverage Types

- Line coverage (% lines executed)
- Branch coverage (% conditional branches taken)
- Function coverage (% functions called)
- Statement coverage (% statements executed)

---

## 📋 Skill Procedure

### Step 1: Run Coverage Analysis

**Command**:
```bash
pytest --cov=. --cov-report=term-missing --cov-report=html tests/
```

**Captures**:
- Overall coverage percentage
- Per-file coverage breakdown
- Missing lines (not covered by tests)

**Example output**:
```
Name                    Stmts   Miss  Cover   Missing
-----------------------------------------------------
src/api/routes.py          45      2    96%   23-24
src/core/validator.py      32      8    75%   12-15, 34-37
-----------------------------------------------------
TOTAL                     234     18    92%
```

---

### Step 2: Parse Coverage Results

**Extract metrics**:
```yaml
coverage_analysis:
  overall_coverage: 92%
  threshold: 80%
  meets_threshold: YES

  per_file:
    - file: "src/api/routes.py"
      coverage: 96%
      status: PASS

    - file: "src/core/validator.py"
      coverage: 75%
      status: FAIL
      missing_lines: [12-15, 34-37]
      priority: HIGH
```

---

### Step 3: Identify Coverage Gaps

**For files below threshold**:
```yaml
coverage_gaps:
  - file: "src/core/validator.py"
    current_coverage: 75%
    target_coverage: 80%
    gap: 5%
    missing_lines: [12-15, 34-37]
    priority: HIGH
    reason: "Core validation logic must be tested"

  recommended_tests:
    - "Test empty input validation (line 12-13)"
    - "Test invalid format handling (line 14-15)"
    - "Test edge case: null values (line 34-37)"
```

---

### Step 4: Generate Coverage Report

**Format**:
```markdown
## Test Coverage Report

**Overall Coverage**: 92%
**Threshold**: 80%
**Status**: ✅ PASS

### Coverage by File

| File | Coverage | Status | Missing Lines |
|------|----------|--------|---------------|
| src/api/routes.py | 96% | ✅ | 23-24 |
| src/core/validator.py | 75% | ❌ | 12-15, 34-37 |

### Coverage Gaps

**FAIL**: src/core/validator.py (75% < 80%)
- Missing: Lines 12-15 (empty input validation)
- Missing: Lines 34-37 (null value handling)
- Priority: HIGH (core validation logic)

**Recommendations**:
1. Add test for empty input: `test_validator_empty_input()`
2. Add test for null values: `test_validator_null_handling()`

After adding these tests, re-run coverage analysis.
```

---

## 📊 Output Format

```yaml
coverage_check:
  overall_coverage: {{PERCENTAGE}}%
  threshold: 80%
  meets_threshold: "{{YES|NO}}"

  files_analyzed: {{COUNT}}
  files_passing: {{COUNT}}
  files_failing: {{COUNT}}

  coverage_gaps:
    - file: "{{FILE}}"
      coverage: {{PERCENTAGE}}%
      missing_lines: [{{LINES}}]
      priority: "{{CRITICAL|HIGH|MEDIUM}}"

  recommendations: [{{LIST}}]
  ready_to_commit: "{{YES|NO}}"
```

---

## 💡 Usage Examples

### Example 1: All Coverage Passes

**test-engineer before commit**:
```
Checking test coverage...

Using check-test-coverage skill...

Result: ✅ PASS
- Overall: 92% (threshold: 80%)
- All files above threshold
- Ready to commit
```

### Example 2: Coverage Gap Detected

**test-engineer before commit**:
```
Checking test coverage...

Using check-test-coverage skill...

Result: ❌ FAIL
- Overall: 87% (above 80% but file gaps exist)
- src/core/validator.py: 75% (below 80%)
  Missing: Lines 12-15, 34-37

Recommendations:
1. Add test_validator_empty_input()
2. Add test_validator_null_handling()

Not ready to commit until gaps filled.
```

---

## 🎯 Success Criteria

- [ ] Coverage analysis completed
- [ ] Overall coverage ≥80%
- [ ] Critical modules ≥90%
- [ ] Coverage gaps identified
- [ ] Recommendations provided
- [ ] Clear PASS/FAIL status

---

## 🔗 Integration with Constitutional Principles

This skill enforces:
- ✅ **Evidence-based**: Tests prove code works (coverage shows what's proven)
- ✅ **Thoroughness**: ≥80% threshold ensures comprehensive testing
- ✅ **Multi-method verification**: Multiple coverage types (line, branch, function)

---

**This skill ensures test coverage meets quality standards.**

**Version**: 1.0.0
**Last Updated**: 2025-10-27
**Source**: @.claude/methodologies/software/tdd-methodology.md
```

---

## 🎯 Success Criteria

- [ ] YAML frontmatter present with required fields
- [ ] `name` uses lowercase-with-hyphens (max 64 chars)
- [ ] `description` is keyword-rich (50-100+ keywords, max 1024 chars)
- [ ] Content includes all required sections
- [ ] Examples are concrete and actionable
- [ ] File saved to correct location
- [ ] YAML syntax valid (no tabs, correct indentation)
- [ ] Skill can be discovered by Claude via keywords

---

**This skill creates Claude Code skill files with optimized keyword discovery.**

**Version**: 1.0.0
**Last Updated**: 2025-10-27
**Source**: [Claude Code Skills Docs](https://docs.claude.com/en/docs/claude-code/skills.md)
