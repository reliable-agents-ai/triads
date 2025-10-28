---
name: validate-code
category: software
domain: software-development
version: 1.0.0
authority: domain-specific
description: Validate code quality against DRY SOLID Clean Code principles check for code smells duplication complexity violations naming conventions function length class size cyclomatic complexity validate software quality code review automated quality checks detect code smells measure code complexity check DRY violations SOLID principles adherence clean code standards naming convention validation function size limits class complexity metrics validate implementation quality pre-commit quality checks code quality gates quality assurance automated code review static analysis code standards enforcement quality metrics collection code health assessment technical debt detection maintainability checks readability validation code structure analysis quality score calculation validate code before commit check code meets standards ensure code quality compliance software quality validation code inspection automated inspection quality control code hygiene clean codebase standards
---

# Validate Code Quality

**Purpose**: Validate code quality against DRY, SOLID, and Clean Code principles. Detect code smells, measure complexity, check for duplication.

**Domain**: Software Development

**Authority**: Domain-specific standard enforcement

---

## 📋 When to Invoke

**Invoke this skill when**:
- Before committing code (senior-developer)
- During refactoring (pruner)
- After implementing features (senior-developer)
- During code review (any agent)
- When quality gates need verification (test-engineer)

**Keywords that trigger this skill**:
- "validate code quality"
- "check code standards"
- "code smell detection"
- "DRY violations"
- "complexity check"
- "clean code validation"
- "quality gate"

---

## 🎯 Quality Standards (From Methodology)

This skill enforces standards from `@.claude/methodologies/software/code-quality-standards.md`:

### DRY (Don't Repeat Yourself)
**Principle**: Every piece of knowledge should have a single, unambiguous representation.

**Check for**:
- Duplicated code blocks (≥6 lines identical)
- Repeated logic patterns
- Copy-pasted functions with minor variations

**Tools**:
```bash
# Check for duplication
pylint --disable=all --enable=duplicate-code <files>

# Or use radon for Python
radon cc <file> -a  # Complexity
radon mi <file>     # Maintainability index
```

### SOLID Principles

**S - Single Responsibility**:
- Each class/function does ONE thing
- Check: Can you describe it without using "and"?

**O - Open/Closed**:
- Open for extension, closed for modification
- Check: Can add features without changing existing code?

**L - Liskov Substitution**:
- Subclasses substitutable for base classes
- Check: No unexpected behavior when using subclasses

**I - Interface Segregation**:
- No client forced to depend on unused interfaces
- Check: No fat interfaces with many unrelated methods

**D - Dependency Inversion**:
- Depend on abstractions, not concretions
- Check: High-level modules don't import low-level details

### Clean Code Standards

**Function Length**:
- ✅ Target: <20 lines
- ⚠️ Warning: 20-30 lines
- ❌ Violation: >30 lines

**Function Parameters**:
- ✅ Ideal: 0-2 parameters
- ⚠️ Acceptable: 3 parameters
- ❌ Too many: >3 parameters (consider parameter object)

**Cyclomatic Complexity**:
- ✅ Simple: 1-5
- ⚠️ Moderate: 6-10
- ❌ Complex: >10 (refactor needed)

**Naming Conventions**:
- Functions: `verb_noun` (lowercase_with_underscores in Python)
- Classes: `PascalCase`
- Constants: `UPPER_CASE_WITH_UNDERSCORES`
- Private: `_leading_underscore`
- Descriptive, not abbreviated (except common: `i`, `idx`, `tmp`)

---

## 📋 Skill Procedure

### Step 1: Identify Files to Validate

**If specific files provided**:
```yaml
files_to_validate:
  - "{{FILE_PATH_1}}"
  - "{{FILE_PATH_2}}"
```

**If validating all changed files**:
```bash
git diff --name-only --cached | grep "\.py$"
```

---

### Step 2: Run Automated Checks

#### Check 1: Duplication Detection

**Using pylint**:
```bash
pylint --disable=all --enable=duplicate-code <files>
```

**Expected output**:
- ✅ No duplication found
- ❌ Similar lines in N files

**Record**:
```yaml
duplication_check:
  tool: "pylint"
  result: "{{PASS|FAIL}}"
  duplications_found: {{COUNT}}
  details: |
    {{DUPLICATION_REPORT}}
```

#### Check 2: Complexity Measurement

**Using radon**:
```bash
# Cyclomatic complexity
radon cc <file> -a -s

# Maintainability index
radon mi <file> -s
```

**Interpret results**:
- **A-B**: Excellent (complexity 1-10)
- **C**: Moderate (complexity 11-20) - ⚠️ Warning
- **D-F**: High (complexity >20) - ❌ Refactor needed

**Record**:
```yaml
complexity_check:
  tool: "radon"
  average_complexity: {{NUMBER}}
  grade: "{{A|B|C|D|F}}"
  functions_over_threshold: {{COUNT}}
  flagged_functions:
    - function: "{{FUNCTION_NAME}}"
      complexity: {{NUMBER}}
      location: "{{FILE}}:{{LINE}}"
```

#### Check 3: Linting (Style + Basic Smells)

**Using flake8**:
```bash
flake8 <files> --max-line-length=100
```

**Common issues caught**:
- Long lines
- Unused imports
- Unused variables
- Indentation errors
- Whitespace issues

**Record**:
```yaml
linting_check:
  tool: "flake8"
  result: "{{PASS|FAIL}}"
  violations: {{COUNT}}
  critical_violations:
    - "{{VIOLATION_1}}"
    - "{{VIOLATION_2}}"
```

---

### Step 3: Manual Code Review

**For each file, check**:

#### Naming Quality
```yaml
naming_review:
  - file: "{{FILE}}"
    issues:
      - type: "unclear_function_name"
        location: "{{FILE}}:{{LINE}}"
        current: "{{BAD_NAME}}"
        suggestion: "{{BETTER_NAME}}"
        reason: "{{WHY_BETTER}}"
```

**Examples**:
- ❌ `def process(data):` → ✅ `def calculate_user_statistics(user_data):`
- ❌ `class Manager:` → ✅ `class UserAccountManager:`
- ❌ `x = getData()` → ✅ `user_profile = fetch_user_profile(user_id)`

#### Function Length Check
```yaml
function_length_review:
  - function: "{{FUNCTION_NAME}}"
    location: "{{FILE}}:{{LINE}}"
    length: {{LINES}}
    status: "{{OK|WARNING|VIOLATION}}"
    recommendation: "{{REFACTOR_SUGGESTION}}"
```

**If >20 lines**:
- Suggest: Extract method
- Identify: What can be pulled into separate functions
- Propose: New function names

#### Single Responsibility Check
```yaml
srp_review:
  - entity: "{{CLASS_OR_FUNCTION}}"
    location: "{{FILE}}:{{LINE}}"
    responsibilities: [{{LIST}}]
    violation: "{{YES|NO}}"
    recommendation: "{{SPLIT_SUGGESTION}}"
```

**Test**: Can you describe it without "and"?
- ❌ "This function validates input **and** saves to database"
- ✅ "This function validates input" + separate "save_to_database()"

---

### Step 4: Calculate Quality Score

**Scoring**:
```yaml
quality_score:
  duplication: "{{PASS=25|FAIL=0}}"
  complexity: "{{GRADE_A_B=25|GRADE_C=15|GRADE_D_F=0}}"
  linting: "{{PASS=25|FAIL=0}}"
  manual_review: "{{GOOD=25|ISSUES=10|MAJOR_ISSUES=0}}"

  total: {{SUM}} / 100
  grade: "{{A|B|C|D|F}}"
```

**Grade interpretation**:
- **A (90-100)**: Excellent quality, ready to commit
- **B (80-89)**: Good quality, minor issues acceptable
- **C (70-79)**: Acceptable, but improvements recommended
- **D (60-69)**: Poor quality, refactoring needed
- **F (<60)**: Failing quality standards, DO NOT COMMIT

---

### Step 5: Generate Report

```markdown
## Code Quality Validation Report

**Files Validated**: {{COUNT}}
**Timestamp**: {{TIMESTAMP}}

---

### Automated Checks

**Duplication**: {{PASS ✅ | FAIL ❌}}
{{DETAILS}}

**Complexity**: Grade {{A|B|C|D|F}}
- Average complexity: {{NUMBER}}
- Functions over threshold: {{COUNT}}
{{FLAGGED_FUNCTIONS}}

**Linting**: {{PASS ✅ | FAIL ❌}}
- Violations: {{COUNT}}
{{CRITICAL_VIOLATIONS}}

---

### Manual Review Findings

**Naming Issues**: {{COUNT}}
{{NAMING_ISSUES_LIST}}

**Function Length Violations**: {{COUNT}}
{{FUNCTION_LENGTH_ISSUES}}

**SRP Violations**: {{COUNT}}
{{SRP_ISSUES}}

---

### Quality Score

**Total**: {{SCORE}} / 100
**Grade**: {{GRADE}}

{{#if grade_A_or_B}}
✅ **Code meets quality standards** - Ready to commit
{{/if}}

{{#if grade_C}}
⚠️ **Code is acceptable but has issues** - Consider refactoring:
{{IMPROVEMENT_LIST}}
{{/if}}

{{#if grade_D_or_F}}
❌ **Code fails quality standards** - DO NOT COMMIT

**Required fixes**:
{{REQUIRED_FIXES}}

**Recommendation**: Refactor before proceeding.
{{/if}}

---

### Recommendations

1. **{{RECOMMENDATION_1}}**
2. **{{RECOMMENDATION_2}}**
3. **{{RECOMMENDATION_3}}**
```

---

## 🔗 Integration with Constitutional Principles

This skill enforces:
- ✅ **Evidence-based claims**: Reports include specific file:line citations
- ✅ **Complete transparency**: Full reasoning for each violation
- ✅ **Thoroughness**: Multiple verification methods (automated + manual)

---

## 📊 Output Format

```yaml
code_quality_validation:
  files_validated: {{COUNT}}
  timestamp: "{{ISO_8601}}"

  automated_checks:
    duplication: "{{PASS|FAIL}}"
    complexity_grade: "{{A|B|C|D|F}}"
    linting: "{{PASS|FAIL}}"

  manual_review:
    naming_issues: {{COUNT}}
    length_violations: {{COUNT}}
    srp_violations: {{COUNT}}

  quality_score: {{NUMBER}} / 100
  grade: "{{A|B|C|D|F}}"
  ready_to_commit: "{{YES|NO}}"

  recommendations: [{{LIST}}]
```

---

## 💡 Usage Examples

### Example 1: Pre-Commit Validation

**senior-developer before commit**:
```
I need to validate code quality before committing these changes:
- src/api/routes.py
- src/core/validator.py

Using validate-code skill...

[Runs automated checks + manual review]

Result: Grade B (85/100)
- ✅ No duplication
- ✅ Low complexity
- ⚠️ 2 functions >20 lines (refactor recommended)

Ready to commit with minor improvements recommended.
```

### Example 2: Refactoring Validation

**pruner after refactoring**:
```
I've refactored the UserManager class. Validating code quality...

Using validate-code skill...

Result: Grade A (92/100)
- ✅ No duplication (was 15%, now 0%)
- ✅ Complexity reduced (was D, now B)
- ✅ All functions <15 lines
- ✅ Clear naming

Refactoring successful - quality improved significantly.
```

---

## 🎯 Success Criteria

- [ ] All automated checks run successfully
- [ ] Manual review completed for key aspects
- [ ] Quality score calculated with evidence
- [ ] Grade assigned (A/B/C/D/F)
- [ ] Recommendations provided if issues found
- [ ] Report includes file:line citations

---

**This skill ensures consistent code quality standards across all software development work.**

**Version**: 1.0.0
**Last Updated**: 2025-10-27
