---
name: pre-commit-review
category: software
domain: software-development
version: 1.0.0
authority: domain-specific
description: Pre-commit review run quality checks before commit black formatting flake8 linting mypy type checking isort import sorting code formatting validation linting validation type checking validation automated pre-commit checks code quality gates pre-commit hooks quality assurance before commit validate code before commit automated code review static analysis code standards enforcement quality gates code quality validation pre-commit validation black check flake8 check mypy check isort check formatting check linting check type check import sorting check code style validation automated quality checks quality control before commit code hygiene checks clean code validation standards enforcement automated checks pre-commit tools integration black flake8 mypy isort integration code quality tools quality assurance tools pre-commit quality gates code validation tools automated validation pre-commit workflow quality workflow code quality workflow validate formatting validate linting validate types validate imports ensure code quality before commit check code meets standards quality standards enforcement
---

# Pre-Commit Review

**Purpose**: Run automated quality checks before committing code. Ensures code meets formatting, linting, type checking, and import sorting standards.

**Domain**: Software Development

**Authority**: Domain-specific quality gate enforcement

---

## 📋 When to Invoke

**Invoke this skill when**:
- Before committing code (senior-developer)
- During pre-commit hook execution (automated)
- When validating staged changes (any agent)
- Before creating pull requests (senior-developer)
- After implementing features (senior-developer)

**Keywords that trigger this skill**:
- "pre-commit review"
- "pre-commit checks"
- "run black"
- "run flake8"
- "run mypy"
- "format code"
- "lint code"
- "type check"
- "quality checks"
- "before commit"

---

## 🎯 Quality Standards (From Methodology)

This skill enforces standards from `@.claude/methodologies/software/code-quality-standards.md`:

### Required Tools

1. **black** - Code formatting
   - Opinionated formatter (no config needed)
   - Enforces consistent style
   - Line length: 100 characters

2. **isort** - Import sorting
   - Groups imports: standard library, third-party, first-party
   - Alphabetically sorted within groups
   - Compatible with black

3. **flake8** - Linting
   - Style guide enforcement (PEP 8)
   - Detects code smells
   - Catches common errors

4. **mypy** - Type checking
   - Static type verification
   - Catches type-related bugs
   - Enforces type annotations

---

## 📋 Skill Procedure

### Step 1: Identify Staged Files

**Get list of files to check**:

```bash
# Get staged Python files
git diff --name-only --cached | grep "\.py$"

# Or check specific files
FILES="src/api/routes.py src/core/validator.py"
```

**Record**:
```yaml
pre_commit_scope:
  staged_files: [{{FILE_LIST}}]
  file_count: {{COUNT}}
  change_summary: "{{DESCRIPTION}}"
```

---

### Step 2: Run Black (Formatting)

**Purpose**: Ensure consistent code formatting

**Command**:
```bash
# Check formatting (dry run - doesn't modify)
black --check --diff <files>

# If failures, show what would change:
# - Lines that would be reformatted
# - Diff showing exact changes
```

**Interpreting results**:
- **Exit code 0**: All files formatted correctly ✅
- **Exit code 1**: Files would be reformatted ❌

**Example output**:
```
would reformat src/api/routes.py
--- src/api/routes.py	2024-01-15 10:30:00
+++ src/api/routes.py	2024-01-15 10:30:05
@@ -15,7 +15,7 @@
-def calculate_total(items,tax_rate):
+def calculate_total(items, tax_rate):
     return sum(item.price for item in items) * (1 + tax_rate)

1 file would be reformatted.
```

**Record**:
```yaml
black_check:
  status: "{{PASS|FAIL}}"
  files_checked: {{COUNT}}
  files_needing_format: {{COUNT}}
  issues:
    - file: "{{FILE}}"
      line: {{LINE}}
      issue: "{{DESCRIPTION}}"
```

**Auto-fix available**:
```bash
# Run black to auto-format files
black <files>

# Verify fixes
black --check <files>  # Should now pass
```

---

### Step 3: Run isort (Import Sorting)

**Purpose**: Ensure imports are sorted consistently

**Command**:
```bash
# Check import sorting (dry run)
isort --check --diff <files>

# Show what would change
isort --diff <files>
```

**Expected import order**:
```python
# ✅ CORRECT ORDER
# 1. Standard library imports
import os
import sys
from datetime import datetime

# 2. Third-party imports
import numpy as np
import requests
from flask import Flask

# 3. First-party (local) imports
from myapp.models import User
from myapp.utils import calculate_tax
```

**Interpreting results**:
- **Exit code 0**: All imports sorted correctly ✅
- **Exit code 1**: Imports need sorting ❌

**Example output**:
```
ERROR: src/api/routes.py Imports are incorrectly sorted and/or formatted.
--- src/api/routes.py:before	2024-01-15 10:30:00
+++ src/api/routes.py:after	2024-01-15 10:30:05
@@ -1,5 +1,5 @@
-from myapp.models import User
 import os
+from myapp.models import User
```

**Record**:
```yaml
isort_check:
  status: "{{PASS|FAIL}}"
  files_checked: {{COUNT}}
  files_needing_sort: {{COUNT}}
  issues:
    - file: "{{FILE}}"
      issue: "Imports incorrectly sorted"
```

**Auto-fix available**:
```bash
# Run isort to auto-sort imports
isort <files>

# Verify fixes
isort --check <files>  # Should now pass
```

---

### Step 4: Run Flake8 (Linting)

**Purpose**: Detect style violations and code smells

**Command**:
```bash
# Run flake8
flake8 <files> --max-line-length=100 --show-source
```

**Common violations detected**:
- E501: Line too long (>100 characters)
- E302: Expected 2 blank lines, found 1
- E231: Missing whitespace after ','
- F401: Module imported but unused
- F841: Local variable assigned but never used
- E722: Do not use bare 'except'
- E711: Comparison to None should be 'if cond is None:'

**Interpreting results**:
- **Exit code 0**: No linting errors ✅
- **Exit code 1**: Linting errors found ❌

**Example output**:
```
src/api/routes.py:15:80: E501 line too long (105 > 100 characters)
def calculate_total_with_tax_and_shipping(items, tax_rate, shipping_cost, discount_code=None):
                                                                            ^

src/api/routes.py:23:5: F841 local variable 'unused_var' is assigned to but never used
    unused_var = calculate_subtotal(items)
    ^

src/core/validator.py:45:9: E722 do not use bare 'except:'
        except:
        ^
```

**Record**:
```yaml
flake8_check:
  status: "{{PASS|FAIL}}"
  files_checked: {{COUNT}}
  total_violations: {{COUNT}}
  violations_by_type:
    E501: {{COUNT}}  # Line too long
    F841: {{COUNT}}  # Unused variable
    E722: {{COUNT}}  # Bare except
  critical_violations:
    - file: "{{FILE}}"
      line: {{LINE}}
      code: "{{ERROR_CODE}}"
      message: "{{MESSAGE}}"
      severity: "{{ERROR|WARNING}}"
```

**Manual fixes required** (flake8 doesn't auto-fix):
- E501: Break long lines
- F401: Remove unused imports
- F841: Remove unused variables or use them
- E722: Specify exception type: `except ValueError:`

---

### Step 5: Run mypy (Type Checking)

**Purpose**: Verify type annotations and catch type-related bugs

**Command**:
```bash
# Run mypy
mypy <files> --strict
```

**Common issues detected**:
- Missing type annotations
- Type mismatches (e.g., passing `str` where `int` expected)
- Missing return type annotations
- `Any` type used (too permissive)
- Optional type not handled (`None` not checked)

**Interpreting results**:
- **Exit code 0**: No type errors ✅
- **Exit code 1**: Type errors found ❌

**Example output**:
```
src/api/routes.py:15: error: Function is missing a return type annotation  [no-untyped-def]
def calculate_total(items, tax_rate):
^

src/api/routes.py:23: error: Argument 1 to "calculate_tax" has incompatible type "str"; expected "float"  [arg-type]
    tax = calculate_tax("0.08", subtotal)
                        ^

src/core/validator.py:45: error: Incompatible return value type (got "None", expected "str")  [return-value]
    return None
    ^
```

**Record**:
```yaml
mypy_check:
  status: "{{PASS|FAIL}}"
  files_checked: {{COUNT}}
  total_errors: {{COUNT}}
  errors_by_type:
    no-untyped-def: {{COUNT}}
    arg-type: {{COUNT}}
    return-value: {{COUNT}}
  critical_errors:
    - file: "{{FILE}}"
      line: {{LINE}}
      error_code: "{{CODE}}"
      message: "{{MESSAGE}}"
      severity: "{{ERROR|NOTE}}"
```

**Fixes required**:
```python
# ❌ Before (mypy error)
def calculate_total(items, tax_rate):
    return sum(item.price for item in items) * (1 + tax_rate)

# ✅ After (mypy clean)
def calculate_total(items: List[Item], tax_rate: float) -> float:
    return sum(item.price for item in items) * (1 + tax_rate)
```

---

### Step 6: Aggregate Results

**Combine all check results**:

```yaml
pre_commit_review_results:
  timestamp: "{{ISO_8601}}"
  files_checked: {{COUNT}}

  black:
    status: "{{PASS|FAIL}}"
    files_needing_format: {{COUNT}}

  isort:
    status: "{{PASS|FAIL}}"
    files_needing_sort: {{COUNT}}

  flake8:
    status: "{{PASS|FAIL}}"
    total_violations: {{COUNT}}

  mypy:
    status: "{{PASS|FAIL}}"
    total_errors: {{COUNT}}

  overall_status: "{{PASS|FAIL}}"
  ready_to_commit: "{{YES|NO}}"
```

**Overall status determination**:
- ✅ **PASS**: All 4 checks pass (black, isort, flake8, mypy)
- ❌ **FAIL**: One or more checks failed

---

### Step 7: Generate Report

```markdown
## Pre-Commit Review Report

**Files Checked**: {{COUNT}}
**Timestamp**: {{TIMESTAMP}}

---

### Summary

**Overall Status**: {{✅ PASS | ❌ FAIL}}

| Check | Status | Issues |
|-------|--------|--------|
| Black (Formatting) | {{✅|❌}} | {{COUNT}} files need formatting |
| isort (Imports) | {{✅|❌}} | {{COUNT}} files need sorting |
| Flake8 (Linting) | {{✅|❌}} | {{COUNT}} violations |
| mypy (Types) | {{✅|❌}} | {{COUNT}} type errors |

---

### Black (Formatting)

{{#if black_pass}}
✅ All files formatted correctly
{{/if}}

{{#if black_fail}}
❌ {{COUNT}} files need formatting:

{{FILES_LIST}}

**Auto-fix available**:
```bash
black {{FILES}}
```
{{/if}}

---

### isort (Import Sorting)

{{#if isort_pass}}
✅ All imports sorted correctly
{{/if}}

{{#if isort_fail}}
❌ {{COUNT}} files have unsorted imports:

{{FILES_LIST}}

**Auto-fix available**:
```bash
isort {{FILES}}
```
{{/if}}

---

### Flake8 (Linting)

{{#if flake8_pass}}
✅ No linting violations
{{/if}}

{{#if flake8_fail}}
❌ {{COUNT}} linting violations found:

**Critical violations**:
{{CRITICAL_VIOLATIONS_LIST}}

**All violations**:
{{ALL_VIOLATIONS_LIST}}

**Manual fixes required** (flake8 doesn't auto-fix)
{{/if}}

---

### mypy (Type Checking)

{{#if mypy_pass}}
✅ No type errors
{{/if}}

{{#if mypy_fail}}
❌ {{COUNT}} type errors found:

**Critical errors**:
{{CRITICAL_ERRORS_LIST}}

**All errors**:
{{ALL_ERRORS_LIST}}

**Manual fixes required** - Add type annotations
{{/if}}

---

### Recommendations

{{#if pass}}
✅ **Ready to commit**

All quality checks passed. Code meets standards.
{{/if}}

{{#if fail}}
❌ **NOT ready to commit**

**Required actions**:

1. **Auto-fixable issues**:
{{#if black_fail}}
   - Run `black {{FILES}}` to fix formatting
{{/if}}
{{#if isort_fail}}
   - Run `isort {{FILES}}` to fix import sorting
{{/if}}

2. **Manual fixes required**:
{{#if flake8_fail}}
   - Fix {{COUNT}} flake8 violations (see details above)
{{/if}}
{{#if mypy_fail}}
   - Fix {{COUNT}} mypy type errors (see details above)
{{/if}}

**After fixes, re-run pre-commit review before committing.**
{{/if}}
```

---

## 🔗 Integration with Constitutional Principles

This skill enforces:
- ✅ **Evidence-based**: Reports include specific file:line citations
- ✅ **Complete transparency**: Shows exact violations and how to fix them
- ✅ **Thoroughness**: Runs 4 independent quality checks
- ✅ **Multi-method verification**: Uses multiple tools (black, isort, flake8, mypy) to catch different issue types

---

## 📊 Output Format

```yaml
pre_commit_review:
  timestamp: "{{ISO_8601}}"
  files_checked: {{COUNT}}

  checks:
    black:
      status: "{{PASS|FAIL}}"
      files_needing_format: {{COUNT}}
      auto_fixable: true

    isort:
      status: "{{PASS|FAIL}}"
      files_needing_sort: {{COUNT}}
      auto_fixable: true

    flake8:
      status: "{{PASS|FAIL}}"
      violations: {{COUNT}}
      auto_fixable: false

    mypy:
      status: "{{PASS|FAIL}}"
      errors: {{COUNT}}
      auto_fixable: false

  overall_status: "{{PASS|FAIL}}"
  ready_to_commit: "{{YES|NO}}"

  auto_fix_command: "black {{FILES}} && isort {{FILES}}"
```

---

## 💡 Usage Examples

### Example 1: All Checks Pass

**senior-developer before commit**:
```
I'm ready to commit my changes to src/api/routes.py and src/core/validator.py.

Running pre-commit review...

Using pre-commit-review skill...

Result: ✅ PASS
- Black: ✅ Formatting correct
- isort: ✅ Imports sorted
- Flake8: ✅ No violations
- mypy: ✅ No type errors

Ready to commit.
```

### Example 2: Formatting Issues (Auto-Fixable)

**senior-developer before commit**:
```
Running pre-commit checks on staged files...

Using pre-commit-review skill...

Result: ❌ FAIL
- Black: ❌ 2 files need formatting
  - src/api/routes.py (spacing issues)
  - src/core/validator.py (line length)
- isort: ✅ Imports sorted
- Flake8: ✅ No violations
- mypy: ✅ No type errors

Auto-fixing formatting issues:
$ black src/api/routes.py src/core/validator.py
reformatted src/api/routes.py
reformatted src/core/validator.py
All done! ✨ 🍰 ✨

Re-running pre-commit review...

Result: ✅ PASS
Ready to commit.
```

### Example 3: Type Errors (Manual Fix Required)

**senior-developer before commit**:
```
Running pre-commit checks...

Using pre-commit-review skill...

Result: ❌ FAIL
- Black: ✅ Formatting correct
- isort: ✅ Imports sorted
- Flake8: ✅ No violations
- mypy: ❌ 3 type errors
  - src/api/routes.py:15: Function is missing return type annotation
  - src/api/routes.py:23: Incompatible type (str vs float)
  - src/core/validator.py:45: Incompatible return value

Manual fixes required:

1. Add return type to calculate_total() (routes.py:15)
2. Fix type mismatch: convert tax_rate string to float (routes.py:23)
3. Fix return type in validate_email() (validator.py:45)

After fixing these type errors, re-run pre-commit review.
```

---

## 🎯 Success Criteria

- [ ] All staged files identified
- [ ] Black check completed (formatting validation)
- [ ] isort check completed (import sorting validation)
- [ ] Flake8 check completed (linting validation)
- [ ] mypy check completed (type checking validation)
- [ ] Results aggregated and reported
- [ ] Clear PASS/FAIL status determined
- [ ] Auto-fix commands provided (if applicable)
- [ ] Manual fix guidance provided (if needed)

---

## 🔧 Configuration

### pyproject.toml

**Recommended configuration**:

```toml
[tool.black]
line-length = 100
target-version = ['py39']
include = '\.pyi?$'
exclude = '''
/(
    \.git
  | \.mypy_cache
  | \.venv
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
line_length = 100
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_any_unimported = false
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
check_untyped_defs = true
strict_equality = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
```

### .flake8

```ini
[flake8]
max-line-length = 100
extend-ignore = E203, W503
exclude =
    .git,
    __pycache__,
    .venv,
    build,
    dist
per-file-ignores =
    __init__.py:F401
```

---

## 🚀 Integration with Git Hooks

### .pre-commit-config.yaml

**Optional**: Use pre-commit framework for automatic enforcement:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.1.0
    hooks:
      - id: black
        language_version: python3.9

  - repo: https://github.com/pycqa/isort
    rev: 5.13.0
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: ["--max-line-length=100"]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

**Install hooks**:
```bash
pip install pre-commit
pre-commit install
```

**Now checks run automatically on `git commit`**:
```bash
$ git commit -m "feat: add new feature"
black....................................................................Passed
isort....................................................................Passed
flake8...................................................................Passed
mypy.....................................................................Passed
[main abc1234] feat: add new feature
```

---

**This skill ensures code meets quality standards before committing.**

**Version**: 1.0.0
**Last Updated**: 2025-10-27
