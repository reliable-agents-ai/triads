# Git Workflow

**Authority Level**: DOMAIN-CONDITIONAL (applies to software-development domain)
**Enforcement**: Agents, skills, git-workflow skill, hooks
**Prerequisite**: Constitutional principles + TDD + Code Quality + Security

---

## Workflow Statement

**MANDATE**: Follow feature branch workflow with conventional commits.

**Git discipline is constitutional law for software development.**

---

## Feature Branch Workflow

### The Standard Pattern

```
main (production-ready)
  ↓
feature/user-auth (development)
  ↓
Pull Request → Code Review → Tests Pass → Merge
  ↓
main (with new feature)
```

**Rules**:
- `main` branch is **always** deployable
- All work happens in feature branches
- Branches merge via pull requests
- Tests must pass before merge

---

## Branch Naming Convention

### Pattern

```
<type>/<short-description>
```

### Types

- `feature/` - New features
- `fix/` - Bug fixes
- `refactor/` - Code improvements
- `docs/` - Documentation
- `test/` - Test additions/updates
- `chore/` - Maintenance tasks

### Examples

```bash
# ✅ GOOD
feature/user-authentication
fix/email-validation-bug
refactor/extract-payment-service
docs/api-endpoints
test/add-user-tests
chore/update-dependencies

# ❌ BAD
user-auth  # ❌ No type prefix
feature/implement_the_new_user_authentication_system  # ❌ Too long
fix/bug  # ❌ Not descriptive
my-branch  # ❌ No type, unclear
```

---

## Creating Feature Branches

### Step 1: Start from Latest main

```bash
# Ensure you're on main
git checkout main

# Pull latest changes
git pull origin main

# Verify clean state
git status  # Should show: "nothing to commit, working tree clean"
```

### Step 2: Create Feature Branch

```bash
# Create and switch to feature branch
git checkout -b feature/email-validation

# Verify branch created
git branch  # Should show * feature/email-validation
```

### Step 3: Work on Feature

```bash
# Make changes
# Write tests (TDD RED phase)
# Run tests (verify RED)
# Implement feature (TDD GREEN phase)
# Refactor (TDD REFACTOR phase)
# Run all tests

# Stage changes
git add models/user.py tests/test_user.py

# Commit (see Conventional Commits section)
git commit -m "feat: Add email validation to User model"
```

---

## Conventional Commits

### Format

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code improvement (no behavior change)
- `perf`: Performance improvement
- `style`: Formatting (no code logic change)
- `test`: Adding/updating tests
- `docs`: Documentation
- `chore`: Maintenance (dependencies, build, etc.)
- `ci`: CI/CD changes

### Examples

**Simple commit**:
```bash
git commit -m "feat: Add user email validation"
```

**With scope**:
```bash
git commit -m "feat(auth): Add password reset functionality"
```

**With body**:
```bash
git commit -m "fix(api): Correct timezone handling in date parsing

The previous implementation didn't account for UTC offsets,
causing dates to be off by several hours for international users.

Now using timezone-aware datetime objects throughout."
```

**Breaking change**:
```bash
git commit -m "feat(api): Change authentication to OAuth2

BREAKING CHANGE: API now requires OAuth2 tokens instead of API keys.
Clients must update to use OAuth2 flow."
```

**Multiple changes (use separate commits)**:
```bash
# ❌ BAD - Multiple unrelated changes in one commit
git commit -m "feat: Add email validation and fix payment bug"

# ✅ GOOD - Separate commits
git commit -m "feat: Add email validation to User model"
# [make more changes]
git commit -m "fix(payment): Correct tax calculation for international orders"
```

---

## Commit Best Practices

### Atomic Commits

**Rule**: One logical change per commit.

```bash
# ❌ BAD - Too large
git commit -m "feat: Implement entire user authentication system"
# Includes: registration, login, logout, password reset, email verification

# ✅ GOOD - Atomic
git commit -m "feat(auth): Add user registration endpoint"
git commit -m "feat(auth): Add login with JWT token generation"
git commit -m "feat(auth): Add logout with token invalidation"
git commit -m "feat(auth): Add password reset email flow"
git commit -m "feat(auth): Add email verification"
```

### Commit Message Quality

```bash
# ❌ BAD
git commit -m "fix bug"  # ❌ Not descriptive
git commit -m "WIP"  # ❌ Work in progress shouldn't be committed
git commit -m "asdfasdf"  # ❌ Nonsense
git commit -m "Fixed the thing"  # ❌ What thing?

# ✅ GOOD
git commit -m "fix(api): Correct null pointer in user profile endpoint"
git commit -m "refactor(db): Extract query logic to repository pattern"
git commit -m "perf(search): Add database index on user.email for faster lookups"
```

### When to Commit

**Commit after**:
- RED-GREEN-REFACTOR cycle complete
- All tests pass
- Code quality checks pass
- Feature is self-contained

**Don't commit**:
- Broken code
- Failing tests
- Debug/console.log statements
- Commented-out code

---

## Pull Request Workflow

### Step 1: Push Feature Branch

```bash
# Push branch to remote
git push origin feature/email-validation

# Or first time (set upstream)
git push -u origin feature/email-validation
```

### Step 2: Create Pull Request

**Via GitHub CLI**:
```bash
gh pr create --title "feat: Add email validation to User model" --body "$(cat <<'EOF'
## Summary
- Added email validation to User model
- Validates email format using regex
- Rejects invalid formats (no @, no domain, empty)

## Changes
- models/user.py: Added _is_valid_email method
- tests/test_user.py: Added 4 validation tests

## Testing
- ✅ All 4 new tests passing
- ✅ All 47 existing tests passing
- ✅ Coverage: 100% of validation logic

## Checklist
- [x] Tests written and passing
- [x] Code quality checks passed (black, flake8, mypy)
- [x] Documentation updated
- [x] No breaking changes
EOF
)"
```

**Via GitHub Web UI**:
1. Navigate to repository
2. Click "Pull requests" → "New pull request"
3. Select base: `main`, compare: `feature/email-validation`
4. Fill in template (see below)

### Pull Request Template

```markdown
## Summary
<!-- Brief description of changes -->

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Changes Made
<!-- List specific changes -->
- File 1: What changed
- File 2: What changed

## Testing
<!-- Describe testing performed -->
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed
- [ ] All tests passing

## Quality Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Code comments added for complex logic
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests provide adequate coverage (≥80%)

## Screenshots (if applicable)
<!-- Add screenshots for UI changes -->

## Related Issues
<!-- Link to issues: Fixes #123, Closes #456 -->
```

### Step 3: Code Review

**Reviewer checklist**:
- [ ] Code follows conventions
- [ ] Logic is sound
- [ ] Tests are comprehensive
- [ ] No security vulnerabilities
- [ ] Documentation is clear
- [ ] No unnecessary complexity

**Review feedback format**:
```markdown
**Approve**: LGTM! Ready to merge.

**Request Changes**:
- models/user.py:45 - Consider extracting regex to constant
- tests/test_user.py:23 - Add test for special characters in email

**Comment**:
- Nice use of guard clauses here! Very readable.
```

### Step 4: Address Feedback

```bash
# Make requested changes
# Commit changes
git commit -m "refactor: Extract email regex to module constant"

# Push updates
git push origin feature/email-validation
```

### Step 5: Merge PR

**Squash and Merge** (preferred for feature branches):
```bash
# GitHub will squash all commits into one
# Resulting commit message:
feat: Add email validation to User model (#123)

- Added email validation to User model
- Validates email format using regex
- Rejects invalid formats
```

**After merge**:
```bash
# Switch to main
git checkout main

# Pull merged changes
git pull origin main

# Delete feature branch
git branch -d feature/email-validation
git push origin --delete feature/email-validation
```

---

## Git Workflow Patterns

### Keeping Feature Branch Updated

**Rebase onto main** (preferred):
```bash
# On feature branch
git checkout feature/email-validation

# Fetch latest main
git fetch origin main

# Rebase onto main
git rebase origin/main

# If conflicts, resolve and continue
git rebase --continue

# Force push (required after rebase)
git push --force-with-lease origin feature/email-validation
```

**Merge main into feature** (alternative):
```bash
# On feature branch
git checkout feature/email-validation

# Merge main
git merge origin/main

# Resolve conflicts if any
git push origin feature/email-validation
```

### Undoing Mistakes

**Uncommit last commit** (keep changes):
```bash
git reset --soft HEAD~1
```

**Discard last commit** (lose changes):
```bash
git reset --hard HEAD~1
```

**Amend last commit**:
```bash
# Fix mistake
git add file.py

# Amend (don't do this if already pushed!)
git commit --amend --no-edit
```

**Revert a commit** (safe for pushed commits):
```bash
git revert <commit-hash>
```

---

## Git Hooks

### Pre-Commit Hook

**File**: `.git/hooks/pre-commit`

```bash
#!/bin/bash

echo "Running pre-commit checks..."

# Run tests
pytest
if [ $? -ne 0 ]; then
    echo "❌ Tests failed. Commit aborted."
    exit 1
fi

# Run black
black --check .
if [ $? -ne 0 ]; then
    echo "❌ Black formatting check failed. Run: black ."
    exit 1
fi

# Run flake8
flake8 .
if [ $? -ne 0 ]; then
    echo "❌ Flake8 linting failed."
    exit 1
fi

# Run mypy
mypy .
if [ $? -ne 0 ]; then
    echo "❌ Mypy type checking failed."
    exit 1
fi

echo "✅ All pre-commit checks passed!"
exit 0
```

**Make executable**:
```bash
chmod +x .git/hooks/pre-commit
```

### Pre-Push Hook

**File**: `.git/hooks/pre-push`

```bash
#!/bin/bash

echo "Running pre-push checks..."

# Run full test suite
pytest --cov=. --cov-report=term-missing
if [ $? -ne 0 ]; then
    echo "❌ Tests failed. Push aborted."
    exit 1
fi

# Check coverage
coverage report --fail-under=80
if [ $? -ne 0 ]; then
    echo "❌ Coverage below 80%. Push aborted."
    exit 1
fi

echo "✅ All pre-push checks passed!"
exit 0
```

---

## Git Configuration

### User Config

```bash
# Set name and email
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Set default branch name
git config --global init.defaultBranch main

# Set default editor
git config --global core.editor "vim"

# Enable auto-correction
git config --global help.autocorrect 20

# Colorize output
git config --global color.ui auto
```

### Aliases

```bash
# Useful aliases
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.unstage 'reset HEAD --'
git config --global alias.last 'log -1 HEAD'
git config --global alias.visual 'log --oneline --graph --decorate --all'
```

---

## .gitignore

**Essential patterns**:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
*.egg-info/
dist/
build/

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Environment
.env
.env.local
.env.*.local

# OS
.DS_Store
Thumbs.db

# Secrets
*.pem
*.key
credentials.json
secrets.yaml

# Logs
*.log
logs/

# Databases
*.db
*.sqlite
*.sqlite3
```

---

## CI/CD Integration

### GitHub Actions Example

**File**: `.github/workflows/ci.yml`

```yaml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt

    - name: Run black
      run: black --check .

    - name: Run flake8
      run: flake8 .

    - name: Run mypy
      run: mypy .

    - name: Run tests with coverage
      run: |
        pytest --cov=. --cov-report=xml --cov-report=term-missing

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: true

    - name: Check coverage threshold
      run: coverage report --fail-under=80
```

---

## Git Workflow Checklist

Before creating a pull request:

- [ ] Branch name follows convention (`type/description`)
- [ ] Commits are atomic (one logical change each)
- [ ] Commit messages follow conventional commits
- [ ] All tests pass
- [ ] Code quality checks pass (black, flake8, mypy)
- [ ] Coverage ≥80%
- [ ] No debug/console.log statements
- [ ] No secrets hardcoded
- [ ] PR template filled out
- [ ] Ready for code review

Before merging:

- [ ] Code review approved
- [ ] CI/CD pipeline green
- [ ] Conflicts resolved
- [ ] Branch up to date with main
- [ ] Tests still passing after rebase/merge

After merging:

- [ ] Local main updated
- [ ] Feature branch deleted (local and remote)
- [ ] Related issues closed

**If ANY box is unchecked, workflow is incomplete.**

---

## Constitutional Integration

Git workflow enforces constitutional principles:

- **Evidence-Based**: Git history provides evidence of all changes
- **Thoroughness**: PR checklist ensures nothing skipped
- **Transparency**: Commit messages document WHY, not just WHAT
- **No Ambiguity**: Conventional commits provide clear change types

**Git discipline is not optional. It is constitutional law for software development.**
