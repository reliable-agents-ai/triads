---
name: check-test-coverage
category: software
domain: software-development
version: 1.0.0
authority: domain-specific
description: Check test coverage verify coverage threshold 80% minimum coverage pytest coverage py.test coverage report coverage analysis test coverage validation ensure adequate testing validate coverage meets standards coverage metrics coverage percentage line coverage branch coverage statement coverage function coverage class coverage module coverage check coverage requirements verify testing adequacy test quality assessment coverage gates coverage validation automated coverage check coverage reporting coverage analysis tool integration pytest-cov coverage.py test coverage enforcement quality gates test completeness validation ensure tests cover code validate test suite completeness check unit test coverage integration test coverage measure test effectiveness coverage thresholds coverage requirements testing standards
---

# Check Test Coverage

**Purpose**: Verify test coverage meets threshold requirements (default ≥80%). Ensure code is adequately tested before deployment.

**Domain**: Software Development

**Authority**: Domain-specific quality gate

---

## 📋 When to Invoke

**Invoke this skill when**:
- After writing tests (test-engineer)
- Before marking implementation complete (test-engineer)
- During quality gate validation (test-engineer)
- Before deployment (release-manager)
- After refactoring (pruner - ensure tests still cover)

**Keywords that trigger this skill**:
- "check test coverage"
- "verify coverage"
- "coverage report"
- "80% coverage"
- "test completeness"
- "coverage threshold"
- "quality gate"

---

## 🎯 Coverage Standards (From Methodology)

This skill enforces standards from `@.claude/methodologies/software/tdd-methodology.md` and `code-quality-standards.md`:

### Coverage Thresholds

**Minimum Requirements**:
- **Overall**: ≥80% line coverage
- **Critical modules**: ≥90% coverage
- **New code**: 100% coverage (no untested new code)

**Coverage Types**:
1. **Line Coverage**: % of lines executed
2. **Branch Coverage**: % of conditional branches taken
3. **Function Coverage**: % of functions called
4. **Statement Coverage**: % of statements executed

### What Must Be Tested

**✅ Must have tests**:
- All public functions/methods
- All API endpoints
- All business logic
- Error handling paths
- Edge cases
- Security-critical code

**⚠️ Optional (but recommended)**:
- Private helper functions (if complex)
- Configuration loading
- Logging statements

**❌ Exclude from coverage**:
- `__init__.py` files (imports only)
- Migrations
- Configuration files
- Test files themselves

---

## 📋 Skill Procedure

### Step 1: Identify Coverage Tool

**Determine which tool to use**:

```yaml
project_type: "{{PYTHON|JAVASCRIPT|TYPESCRIPT|GO|RUST}}"

coverage_tool:
  python: "pytest-cov or coverage.py"
  javascript: "jest --coverage or nyc"
  typescript: "jest --coverage"
  go: "go test -cover"
  rust: "cargo-tarpaulin"
```

**For this project** (Python):
```bash
# Using pytest-cov
pytest --cov=<module> --cov-report=term --cov-report=html
```

---

### Step 2: Run Coverage Analysis

#### Full Project Coverage

```bash
# Run all tests with coverage
pytest --cov=src --cov-report=term-missing --cov-report=html tests/

# Output shows:
# - Overall coverage %
# - Per-file coverage
# - Missing lines
```

**Expected output**:
```
---------- coverage: platform darwin, python 3.11.5 -----------
Name                      Stmts   Miss  Cover   Missing
-------------------------------------------------------
src/api/routes.py           45      3    93%   23-25
src/core/validator.py       30      0   100%
src/models/user.py          50      8    84%   15, 22, 45-48, 67
-------------------------------------------------------
TOTAL                       125     11    91%
```

#### Module-Specific Coverage

```bash
# Check specific module
pytest --cov=src/api --cov-report=term-missing tests/test_api/
```

---

### Step 3: Analyze Coverage Report

#### Parse Coverage Data

```yaml
coverage_analysis:
  overall_coverage: {{PERCENTAGE}}%
  total_statements: {{NUMBER}}
  covered_statements: {{NUMBER}}
  missing_statements: {{NUMBER}}

  per_file:
    - file: "{{FILE_PATH}}"
      coverage: {{PERCENTAGE}}%
      statements: {{NUMBER}}
      missing: {{NUMBER}}
      missing_lines: [{{LINE_NUMBERS}}]
      status: "{{PASS|WARNING|FAIL}}"

    - file: "{{FILE_PATH_2}}"
      coverage: {{PERCENTAGE}}%
      statements: {{NUMBER}}
      missing: {{NUMBER}}
      missing_lines: [{{LINE_NUMBERS}}]
      status: "{{STATUS}}"
```

**Status determination**:
- **PASS**: Coverage ≥80% (or ≥90% for critical modules)
- **WARNING**: Coverage 70-79% (borderline, improvements recommended)
- **FAIL**: Coverage <70% (unacceptable, more tests required)

---

### Step 4: Identify Gaps

#### Critical Uncovered Code

**Flag high-priority uncovered lines**:

```yaml
coverage_gaps:
  - file: "{{FILE}}"
    function: "{{FUNCTION_NAME}}"
    lines_missing: [{{LINES}}]
    priority: "{{CRITICAL|HIGH|MEDIUM|LOW}}"
    reason: "{{WHY_CRITICAL}}"
    test_needed: "{{TEST_DESCRIPTION}}"
```

**Priority criteria**:
- **CRITICAL**: Security-sensitive code, error handling, authentication
- **HIGH**: Business logic, API endpoints, data validation
- **MEDIUM**: Helper functions, utilities
- **LOW**: Configuration, logging, trivial getters/setters

**Example**:
```yaml
coverage_gaps:
  - file: "src/api/routes.py"
    function: "authenticate_user"
    lines_missing: [23-25]
    priority: "CRITICAL"
    reason: "Authentication logic must be fully tested"
    test_needed: "Test invalid credentials handling"

  - file: "src/models/user.py"
    function: "validate_email"
    lines_missing: [45-48]
    priority: "HIGH"
    reason: "Email validation is business logic"
    test_needed: "Test edge cases: empty email, invalid format, SQL injection attempt"
```

---

### Step 5: Check Branch Coverage

**Branch coverage** shows if all conditional paths tested:

```bash
# Check branch coverage (if supported)
pytest --cov=src --cov-branch --cov-report=term-missing
```

**Analyze conditionals**:
```yaml
branch_coverage:
  - file: "{{FILE}}"
    line: {{LINE_NUMBER}}
    condition: "{{CODE}}"
    branches_total: {{NUMBER}}
    branches_covered: {{NUMBER}}
    uncovered_paths:
      - "{{PATH_DESCRIPTION}}"
```

**Example**:
```yaml
branch_coverage:
  - file: "src/core/validator.py"
    line: 15
    condition: "if user.is_admin or user.has_permission('edit'):"
    branches_total: 4  # True/True, True/False, False/True, False/False
    branches_covered: 2
    uncovered_paths:
      - "user.is_admin=False and user.has_permission=True"
      - "Both conditions False"
```

---

### Step 6: Validate Against Threshold

**Check if coverage meets requirements**:

```yaml
threshold_validation:
  required_coverage: {{THRESHOLD}}%  # Default 80%
  actual_coverage: {{ACTUAL}}%
  meets_threshold: "{{YES|NO}}"

  per_module_thresholds:
    - module: "{{MODULE}}"
      required: {{PERCENTAGE}}%  # Critical modules may require 90%
      actual: {{PERCENTAGE}}%
      meets_threshold: "{{YES|NO}}"
```

**Result**:
- ✅ **PASS**: All thresholds met
- ❌ **FAIL**: One or more thresholds not met

---

### Step 7: Generate Coverage Report

```markdown
## Test Coverage Report

**Project**: {{PROJECT_NAME}}
**Timestamp**: {{TIMESTAMP}}
**Coverage Tool**: {{TOOL}}

---

### Overall Coverage

**Total**: {{PERCENTAGE}}% ({{COVERED}}/{{TOTAL}} statements)

**Threshold**: {{THRESHOLD}}%
**Status**: {{✅ PASS | ❌ FAIL}}

---

### Per-File Coverage

| File | Coverage | Status |
|------|----------|--------|
| {{FILE_1}} | {{PERCENTAGE}}% | {{✅|⚠️|❌}} |
| {{FILE_2}} | {{PERCENTAGE}}% | {{✅|⚠️|❌}} |

---

### Coverage Gaps

{{#if gaps}}
**Critical Gaps** ({{COUNT}}):
{{CRITICAL_GAPS_LIST}}

**High Priority Gaps** ({{COUNT}}):
{{HIGH_PRIORITY_GAPS_LIST}}

**Medium Priority Gaps** ({{COUNT}}):
{{MEDIUM_PRIORITY_GAPS_LIST}}
{{/if}}

{{#if no_gaps}}
✅ No significant coverage gaps found
{{/if}}

---

### Branch Coverage

**Branch Coverage**: {{PERCENTAGE}}%

{{#if uncovered_branches}}
**Uncovered Branches** ({{COUNT}}):
{{UNCOVERED_BRANCHES_LIST}}
{{/if}}

---

### Recommendations

{{#if pass}}
✅ **Coverage meets standards**

No action required. Continue maintaining high test coverage.
{{/if}}

{{#if fail}}
❌ **Coverage below threshold**

**Required actions**:
1. {{ACTION_1}}
2. {{ACTION_2}}

**Tests to write**:
{{TESTS_NEEDED_LIST}}

**Cannot proceed to deployment until coverage ≥{{THRESHOLD}}%**
{{/if}}

{{#if warning}}
⚠️ **Coverage acceptable but borderline**

**Recommended improvements**:
{{IMPROVEMENT_LIST}}
{{/if}}

---

### HTML Report

Detailed coverage report available at: `htmlcov/index.html`

Open with: `open htmlcov/index.html` (macOS) or `xdg-open htmlcov/index.html` (Linux)
```

---

## 🔗 Integration with Constitutional Principles

This skill enforces:
- ✅ **Evidence-based**: Provides specific line numbers for gaps
- ✅ **Complete transparency**: Shows exactly what's tested and what's not
- ✅ **Thoroughness**: Checks line, branch, and function coverage

---

## 📊 Output Format

```yaml
test_coverage_check:
  timestamp: "{{ISO_8601}}"
  tool: "{{TOOL_NAME}}"

  overall:
    coverage_percentage: {{NUMBER}}
    threshold: {{NUMBER}}
    meets_threshold: "{{YES|NO}}"

  line_coverage: {{PERCENTAGE}}%
  branch_coverage: {{PERCENTAGE}}%
  function_coverage: {{PERCENTAGE}}%

  gaps:
    critical: {{COUNT}}
    high: {{COUNT}}
    medium: {{COUNT}}
    low: {{COUNT}}

  status: "{{PASS|WARNING|FAIL}}"
  ready_for_deployment: "{{YES|NO}}"
```

---

## 💡 Usage Examples

### Example 1: After Writing Tests

**test-engineer**:
```
I've written tests for the new authentication module. Checking coverage...

Using check-test-coverage skill...

Result:
- Overall: 92% ✅
- src/auth/login.py: 95%
- src/auth/validate.py: 88%

Exceeds 80% threshold. Ready for implementation complete.
```

### Example 2: Coverage Below Threshold

**test-engineer**:
```
Checking coverage after implementation...

Using check-test-coverage skill...

Result:
- Overall: 72% ❌
- src/api/routes.py: 65% (15 lines uncovered)

FAIL: Below 80% threshold.

Critical gaps:
- authenticate_user() function (lines 23-25) - NO TESTS
- validate_input() error handling (lines 45-48) - NOT COVERED

Required: Write tests for critical authentication and validation paths.
Cannot proceed to deployment.
```

### Example 3: After Refactoring

**pruner**:
```
Refactored UserManager class. Verifying tests still cover code...

Using check-test-coverage skill...

Result:
- Overall: 89% ✅ (was 87% before refactoring)
- src/models/user.py: 89%

Coverage maintained after refactoring. Tests still comprehensive.
```

---

## 🎯 Success Criteria

- [ ] Coverage tool executed successfully
- [ ] Overall coverage percentage calculated
- [ ] Per-file coverage analyzed
- [ ] Coverage gaps identified with priority
- [ ] Branch coverage checked (if supported)
- [ ] Threshold validation completed
- [ ] Clear PASS/FAIL status determined

---

**This skill ensures adequate test coverage before code is deployed.**

**Version**: 1.0.0
**Last Updated**: 2025-10-27
