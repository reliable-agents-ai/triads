---
name: git-commit-validate
category: software
domain: software-development
version: 1.0.0
authority: domain-specific
description: Git commit message validation conventional commits format validate commit messages enforce conventional commits standard check commit format commit message standards git commit format validation commit type validation commit scope validation commit description validation breaking change detection commit message quality commit message conventions semantic versioning support automated commit validation commit standards enforcement git workflow validation conventional commits compliance commit format checker commit message linter validate git commits check commit conventions ensure commit standards git commit quality commit message validation tool conventional commit format checker validate commit syntax commit message structure validation atomic commit validation commit best practices enforcement git discipline commit hygiene conventional commits validator semantic commit messages commit type checking commit scope checking commit description checking breaking changes validation commit footer validation commit message format checker git commit standards
---

# Git Commit Message Validation

**Purpose**: Validate commit messages follow conventional commits format. Enforces commit message standards for clarity and semantic versioning.

**Domain**: Software Development

**Authority**: Domain-specific git workflow enforcement

---

## 📋 When to Invoke

**Invoke this skill when**:
- Before committing code (senior-developer)
- During commit-msg git hook (automated)
- When validating commit history (any agent)
- Before creating pull requests (senior-developer)
- During code review (reviewing commit quality)

**Keywords that trigger this skill**:
- "validate commit message"
- "check commit format"
- "conventional commits"
- "commit message validation"
- "git commit check"
- "commit standards"
- "validate git commit"
- "commit format"

---

## 🎯 Conventional Commits Standard (From Methodology)

This skill enforces standards from `@.claude/methodologies/software/git-workflow.md`:

### Commit Message Format

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Required Components

1. **Type** (required): Category of change
2. **Scope** (optional): Area affected
3. **Description** (required): Brief summary

### Valid Types

- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code improvement (no behavior change)
- `perf`: Performance improvement
- `style`: Formatting (no code logic change)
- `test`: Adding/updating tests
- `docs`: Documentation
- `chore`: Maintenance (dependencies, build, etc.)
- `ci`: CI/CD changes

### Format Rules

- **Type**: Lowercase, from valid types list
- **Scope**: Optional, lowercase, alphanumeric with hyphens
- **Description**:
  - Lowercase first letter
  - No period at end
  - Imperative mood ("add" not "added" or "adds")
  - Max 72 characters for first line
- **Body**: Optional, explains WHY (not WHAT)
- **Footer**: Optional, for breaking changes, issue references

---

## 📋 Skill Procedure

### Step 1: Extract Commit Message

**Get commit message to validate**:

```bash
# From most recent commit
git log -1 --pretty=%B

# From commit hash
git log <hash> -1 --pretty=%B

# From staged changes (not yet committed)
# Message provided as input
```

**Record**:
```yaml
commit_validation_input:
  source: "{{git-log|staged|provided}}"
  commit_hash: "{{HASH}}"  # If from log
  message: |
    {{FULL_COMMIT_MESSAGE}}
```

---

### Step 2: Parse Commit Message

**Split into components**:

```yaml
parsed_message:
  first_line: "{{TYPE}}({{SCOPE}}): {{DESCRIPTION}}"
  type: "{{TYPE}}"
  scope: "{{SCOPE|null}}"
  description: "{{DESCRIPTION}}"
  body: "{{BODY|null}}"
  footer: "{{FOOTER|null}}"
```

**Example parsing**:

```
Input: "feat(auth): add password reset functionality"

Parsed:
  type: "feat"
  scope: "auth"
  description: "add password reset functionality"
  body: null
  footer: null
```

---

### Step 3: Validate Type

**Check type is valid**:

```yaml
type_validation:
  provided_type: "{{TYPE}}"
  valid_types:
    - "feat"
    - "fix"
    - "refactor"
    - "perf"
    - "style"
    - "test"
    - "docs"
    - "chore"
    - "ci"
  is_valid: "{{YES|NO}}"
  is_lowercase: "{{YES|NO}}"
```

**Common mistakes**:

```bash
# ❌ INVALID
"Feature: add user auth"  # ❌ Not lowercase
"update: change API"  # ❌ Not a valid type
"FEAT: new feature"  # ❌ Not lowercase

# ✅ VALID
"feat: add user auth"
"fix: correct API bug"
"refactor: extract service layer"
```

**Error messages**:
- Type missing: `❌ Commit message must start with type (feat, fix, refactor, etc.)`
- Type invalid: `❌ Invalid type "{{TYPE}}". Valid types: feat, fix, refactor, perf, style, test, docs, chore, ci`
- Type not lowercase: `❌ Type must be lowercase: "{{TYPE}}" should be "{{type}}"`

---

### Step 4: Validate Scope (if present)

**Check scope format**:

```yaml
scope_validation:
  has_scope: "{{YES|NO}}"
  scope_value: "{{SCOPE|null}}"
  is_lowercase: "{{YES|NO}}"
  is_alphanumeric: "{{YES|NO}}"  # Allow hyphens
  is_wrapped_in_parens: "{{YES|NO}}"
```

**Scope rules**:
- Must be lowercase
- Must be alphanumeric with hyphens allowed
- Must be wrapped in parentheses: `(scope)`
- No spaces or special characters (except hyphens)

**Common mistakes**:

```bash
# ❌ INVALID
"feat(User Auth): add login"  # ❌ Not lowercase, has space
"feat[api]: add endpoint"  # ❌ Wrong brackets
"feat(api_auth): fix bug"  # ❌ Underscore not allowed

# ✅ VALID
"feat(auth): add login"
"fix(api): correct endpoint"
"refactor(user-service): extract logic"
```

**Error messages**:
- Not lowercase: `❌ Scope must be lowercase: "({{SCOPE}})" should be "({{scope}})"`
- Invalid characters: `❌ Scope contains invalid characters. Use only lowercase letters, numbers, and hyphens.`
- Wrong brackets: `❌ Scope must be wrapped in parentheses: (scope)`

---

### Step 5: Validate Description

**Check description format**:

```yaml
description_validation:
  description: "{{DESCRIPTION}}"
  length: {{CHARACTERS}}
  max_length: 72  # First line limit
  within_limit: "{{YES|NO}}"
  starts_lowercase: "{{YES|NO}}"
  ends_with_period: "{{NO|YES}}"  # Should be NO
  uses_imperative_mood: "{{YES|NO|UNSURE}}"
  is_descriptive: "{{YES|NO}}"
```

**Description rules**:
- Max 72 characters for first line
- Start with lowercase letter
- No period at end
- Use imperative mood ("add" not "added" or "adds")
- Be descriptive (not vague)

**Common mistakes**:

```bash
# ❌ INVALID - Length
"feat: Add a new feature that allows users to reset their password via email with a secure token"  # ❌ Too long (>72 chars)

# ❌ INVALID - Capitalization
"feat: Add user authentication"  # ❌ Should start lowercase

# ❌ INVALID - Period
"feat: add user authentication."  # ❌ No period at end

# ❌ INVALID - Past tense
"feat: added user authentication"  # ❌ Use imperative mood

# ❌ INVALID - Vague
"feat: update code"  # ❌ Not descriptive
"fix: fix bug"  # ❌ What bug?
"refactor: changes"  # ❌ What changes?

# ✅ VALID
"feat: add user authentication with JWT tokens"
"fix: correct timezone handling in date parser"
"refactor: extract payment service to separate module"
"perf: add database index on user.email for faster lookups"
```

**Error messages**:
- Too long: `❌ Description too long ({{LENGTH}} chars). Max 72 characters for first line.`
- Starts uppercase: `❌ Description should start with lowercase letter.`
- Ends with period: `❌ Description should not end with a period.`
- Past tense: `⚠️ Consider using imperative mood: "{{IMPERATIVE_FORM}}" instead of "{{PAST_TENSE}}"`
- Vague: `⚠️ Description is vague. Be more specific about what changed.`

---

### Step 6: Validate Body (if present)

**Check body format**:

```yaml
body_validation:
  has_body: "{{YES|NO}}"
  blank_line_after_description: "{{YES|NO}}"  # Required if body present
  explains_why: "{{YES|NO}}"  # Body should explain WHY, not WHAT
  length_reasonable: "{{YES|NO}}"  # No max, but should be concise
```

**Body rules**:
- Must have blank line between description and body
- Should explain WHY, not WHAT
- Use full sentences
- Wrap lines at 72 characters

**Good body examples**:

```bash
# ✅ GOOD - Explains WHY
feat: add email validation to User model

The previous implementation allowed invalid email formats to be saved,
causing downstream errors in the email service. This adds validation
using regex to ensure only valid email formats are accepted.

# ✅ GOOD - Provides context
fix: correct timezone handling in date parser

The previous implementation didn't account for UTC offsets,
causing dates to be off by several hours for international users.
Now using timezone-aware datetime objects throughout.
```

**Common mistakes**:

```bash
# ❌ BAD - No blank line
feat: add feature
This is the body without blank line.

# ❌ BAD - Explains WHAT (obvious from code)
feat: add email validation
Added _is_valid_email method that checks email format.

# ✅ GOOD - Has blank line, explains WHY
feat: add email validation

Email validation prevents invalid formats from causing errors
in downstream email services.
```

**Error messages**:
- No blank line: `❌ Body must be separated from description by blank line.`
- Explains WHAT: `⚠️ Body should explain WHY (not WHAT). What is obvious from the code.`

---

### Step 7: Validate Footer (if present)

**Check footer format**:

```yaml
footer_validation:
  has_footer: "{{YES|NO}}"
  footer_content: "{{FOOTER}}"
  has_breaking_change: "{{YES|NO}}"
  has_issue_reference: "{{YES|NO}}"
  footer_format_valid: "{{YES|NO}}"
```

**Footer patterns**:

1. **Breaking change**:
```
BREAKING CHANGE: <description>
```

2. **Issue reference**:
```
Fixes #123
Closes #456
Resolves #789
```

3. **Multiple footers**:
```
Fixes #123
BREAKING CHANGE: API now requires OAuth2 tokens
```

**Examples**:

```bash
# ✅ GOOD - Breaking change
feat: change authentication to OAuth2

BREAKING CHANGE: API now requires OAuth2 tokens instead of API keys.
Clients must update to use OAuth2 flow.

# ✅ GOOD - Issue reference
fix: correct null pointer in user profile endpoint

Fixes #234

# ✅ GOOD - Multiple footers
feat: add password reset with email verification

Implements password reset flow with secure tokens.

Closes #123
Closes #124
```

**Error messages**:
- Invalid breaking change format: `❌ Breaking change must use format: "BREAKING CHANGE: <description>"`
- Invalid issue reference: `❌ Issue reference must use format: "Fixes #123" or "Closes #123"`

---

### Step 8: Check Atomic Commit

**Verify commit represents ONE logical change**:

```yaml
atomic_check:
  is_atomic: "{{YES|NO|UNSURE}}"
  multiple_changes_detected: "{{YES|NO}}"
  indicators:
    - "{{INDICATOR_1}}"  # e.g., "and" in description
    - "{{INDICATOR_2}}"
```

**Red flags for non-atomic commits**:
- Description contains "and" (e.g., "add feature and fix bug")
- Multiple unrelated types (feat + fix)
- Changes across unrelated modules

**Common mistakes**:

```bash
# ❌ NON-ATOMIC
"feat: add email validation and fix payment bug"  # ❌ Two unrelated changes

# ❌ NON-ATOMIC
"fix: correct API bugs"  # ❌ Plural "bugs" suggests multiple fixes

# ✅ ATOMIC
"feat: add email validation to User model"
"fix: correct timezone handling in date parser"
```

**Error messages**:
- Non-atomic: `⚠️ Commit appears non-atomic. Consider splitting into separate commits.`
- Contains "and": `⚠️ Description contains "and" - this may indicate multiple changes in one commit.`

---

### Step 9: Aggregate Results

```yaml
commit_validation_results:
  timestamp: "{{ISO_8601}}"
  commit_hash: "{{HASH|null}}"
  commit_message: "{{MESSAGE}}"

  type_validation:
    status: "{{PASS|FAIL}}"
    issues: [{{LIST}}]

  scope_validation:
    status: "{{PASS|FAIL|N/A}}"
    issues: [{{LIST}}]

  description_validation:
    status: "{{PASS|FAIL}}"
    issues: [{{LIST}}]

  body_validation:
    status: "{{PASS|FAIL|N/A}}"
    issues: [{{LIST}}]

  footer_validation:
    status: "{{PASS|FAIL|N/A}}"
    issues: [{{LIST}}]

  atomic_check:
    status: "{{PASS|WARN|N/A}}"
    issues: [{{LIST}}]

  overall_status: "{{PASS|FAIL}}"
  is_valid_conventional_commit: "{{YES|NO}}"
```

**Overall status**:
- ✅ **PASS**: All required checks pass (type, description), warnings acceptable
- ❌ **FAIL**: One or more required checks fail

---

### Step 10: Generate Report

```markdown
## Commit Message Validation Report

**Commit**: {{HASH|"Staged changes"}}
**Timestamp**: {{TIMESTAMP}}

---

### Commit Message

```
{{FULL_COMMIT_MESSAGE}}
```

---

### Validation Summary

**Status**: {{✅ PASS | ❌ FAIL}}

| Component | Status | Issues |
|-----------|--------|--------|
| Type | {{✅|❌}} | {{COUNT}} |
| Scope | {{✅|❌|N/A}} | {{COUNT}} |
| Description | {{✅|❌}} | {{COUNT}} |
| Body | {{✅|❌|⚠️|N/A}} | {{COUNT}} |
| Footer | {{✅|❌|N/A}} | {{COUNT}} |
| Atomic | {{✅|⚠️|N/A}} | {{COUNT}} |

---

### Detailed Results

{{#if type_fail}}
#### ❌ Type Validation

{{TYPE_ISSUES_LIST}}
{{/if}}

{{#if scope_fail}}
#### ❌ Scope Validation

{{SCOPE_ISSUES_LIST}}
{{/if}}

{{#if description_fail}}
#### ❌ Description Validation

{{DESCRIPTION_ISSUES_LIST}}
{{/if}}

{{#if body_warn}}
#### ⚠️ Body Recommendations

{{BODY_WARNINGS_LIST}}
{{/if}}

{{#if footer_fail}}
#### ❌ Footer Validation

{{FOOTER_ISSUES_LIST}}
{{/if}}

{{#if atomic_warn}}
#### ⚠️ Atomic Commit Check

{{ATOMIC_WARNINGS_LIST}}
{{/if}}

---

### Recommendations

{{#if pass}}
✅ **Commit message is valid**

Follows conventional commits format. Ready to commit.
{{/if}}

{{#if fail}}
❌ **Commit message is invalid**

**Required fixes**:
{{REQUIRED_FIXES_LIST}}

**Suggested format**:
```
{{SUGGESTED_CORRECTED_MESSAGE}}
```

**Re-run validation after fixing.**
{{/if}}

{{#if warnings_only}}
⚠️ **Commit message is valid but has warnings**

Message meets minimum standards but could be improved:
{{IMPROVEMENT_SUGGESTIONS}}

Warnings don't block commits but addressing them improves commit quality.
{{/if}}
```

---

## 🔗 Integration with Constitutional Principles

This skill enforces:
- ✅ **Evidence-based**: Git history provides evidence of changes
- ✅ **Complete transparency**: Commit messages document WHY, not just WHAT
- ✅ **Communication standards**: Clear, unambiguous commit messages
- ✅ **No hazing**: Commit format is accessible and well-documented

---

## 📊 Output Format

```yaml
commit_validation:
  timestamp: "{{ISO_8601}}"
  commit_message: "{{MESSAGE}}"

  validation_results:
    type: "{{PASS|FAIL}}"
    scope: "{{PASS|FAIL|N/A}}"
    description: "{{PASS|FAIL}}"
    body: "{{PASS|WARN|N/A}}"
    footer: "{{PASS|FAIL|N/A}}"
    atomic: "{{PASS|WARN|N/A}}"

  overall_status: "{{PASS|FAIL}}"
  is_valid: "{{YES|NO}}"
  ready_to_commit: "{{YES|NO}}"

  issues: [{{LIST}}]
  warnings: [{{LIST}}]
  suggestions: [{{LIST}}]
```

---

## 💡 Usage Examples

### Example 1: Valid Commit Message

**senior-developer validating commit**:
```
Validating commit message: "feat(auth): add password reset functionality"

Using git-commit-validate skill...

Result: ✅ PASS
- Type: ✅ "feat" (valid)
- Scope: ✅ "auth" (valid)
- Description: ✅ "add password reset functionality" (72 chars, imperative mood)
- Body: N/A
- Footer: N/A
- Atomic: ✅ Single logical change

Commit message is valid. Ready to commit.
```

### Example 2: Invalid Type

**senior-developer validating commit**:
```
Validating commit message: "update: change API endpoint"

Using git-commit-validate skill...

Result: ❌ FAIL
- Type: ❌ "update" is not a valid type
  Valid types: feat, fix, refactor, perf, style, test, docs, chore, ci

Suggested fix:
"refactor: change API endpoint"
or
"feat: change API endpoint" (if adds new functionality)

Re-run validation after fixing.
```

### Example 3: Description Too Long

**senior-developer validating commit**:
```
Validating commit message: "feat: Add a new feature that allows users to reset their password via email with a secure token and verification"

Using git-commit-validate skill...

Result: ❌ FAIL
- Type: ✅ "feat" (valid)
- Description: ❌ Too long (115 chars, max 72)
  ❌ Starts with uppercase (should be lowercase)

Suggested fix:
"feat: add password reset via email with secure token

Implements password reset flow allowing users to receive
a secure token via email for password verification."

Re-run validation after fixing.
```

### Example 4: Non-Atomic Commit

**senior-developer validating commit**:
```
Validating commit message: "feat: add email validation and fix payment bug"

Using git-commit-validate skill...

Result: ⚠️ PASS with warnings
- Type: ✅ "feat" (valid)
- Description: ✅ Valid format
- Atomic: ⚠️ Description contains "and" - may indicate multiple changes

Recommendation:
Consider splitting into two commits:
1. "feat: add email validation to User model"
2. "fix: correct tax calculation in payment processor"

This improves git history clarity and makes changes easier to revert individually.
```

### Example 5: Breaking Change

**senior-developer validating commit**:
```
Validating commit message:
"feat(api): change authentication to OAuth2

BREAKING CHANGE: API now requires OAuth2 tokens instead of API keys.
Clients must update to use OAuth2 flow."

Using git-commit-validate skill...

Result: ✅ PASS
- Type: ✅ "feat" (valid)
- Scope: ✅ "api" (valid)
- Description: ✅ "change authentication to OAuth2"
- Body: N/A
- Footer: ✅ Breaking change properly documented
- Atomic: ✅ Single logical change

Breaking change detected: Will trigger major version bump in semantic versioning.

Commit message is valid. Ready to commit.
```

---

## 🎯 Success Criteria

- [ ] Commit message extracted successfully
- [ ] Type validated against allowed types
- [ ] Scope validated (if present)
- [ ] Description validated (length, format, mood)
- [ ] Body validated (if present)
- [ ] Footer validated (if present)
- [ ] Atomic commit check performed
- [ ] Clear PASS/FAIL status determined
- [ ] Specific issues identified with line numbers
- [ ] Corrected message suggested (if invalid)

---

## 🔧 Git Hook Integration

### commit-msg Hook

**File**: `.git/hooks/commit-msg`

```bash
#!/bin/bash

COMMIT_MSG_FILE=$1
COMMIT_MSG=$(cat "$COMMIT_MSG_FILE")

echo "Validating commit message..."

# Conventional commit regex
CONVENTIONAL_COMMIT_REGEX="^(feat|fix|refactor|perf|style|test|docs|chore|ci)(\([a-z0-9-]+\))?: [a-z].{1,71}$"

if ! echo "$COMMIT_MSG" | head -1 | grep -qE "$CONVENTIONAL_COMMIT_REGEX"; then
    echo "❌ Commit message does not follow conventional commits format."
    echo ""
    echo "Format: <type>(<scope>): <description>"
    echo ""
    echo "Valid types: feat, fix, refactor, perf, style, test, docs, chore, ci"
    echo ""
    echo "Example: feat(auth): add password reset functionality"
    echo ""
    exit 1
fi

echo "✅ Commit message is valid"
exit 0
```

**Make executable**:
```bash
chmod +x .git/hooks/commit-msg
```

**Now validates automatically on every commit**:
```bash
$ git commit -m "update: fix bug"
Validating commit message...
❌ Commit message does not follow conventional commits format.

Format: <type>(<scope>): <description>

Valid types: feat, fix, refactor, perf, style, test, docs, chore, ci

Example: feat(auth): add password reset functionality

$ git commit -m "fix: correct bug in user validation"
Validating commit message...
✅ Commit message is valid
[main abc1234] fix: correct bug in user validation
```

---

## 📚 Conventional Commits Reference

### Quick Reference Card

```
feat: A new feature
fix: A bug fix
refactor: Code change that neither fixes a bug nor adds a feature
perf: Code change that improves performance
style: Changes that don't affect code meaning (whitespace, formatting)
test: Adding or updating tests
docs: Documentation only changes
chore: Changes to build process or auxiliary tools
ci: Changes to CI configuration files and scripts

Format: <type>(<scope>): <description>

Example: feat(api): add user authentication endpoint

Breaking changes:
feat(api): change auth to OAuth2

BREAKING CHANGE: API now requires OAuth2 tokens.
```

---

**This skill ensures commit messages follow conventional commits standard for clear, semantic git history.**

**Version**: 1.0.0
**Last Updated**: 2025-10-27
