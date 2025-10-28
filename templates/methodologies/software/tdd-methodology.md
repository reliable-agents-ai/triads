# Test-Driven Development (TDD) Methodology

**Authority Level**: DOMAIN-CONDITIONAL (applies to software-development domain)
**Enforcement**: Agents, skills, hooks in software development workflows
**Prerequisite**: Constitutional principles (evidence, verification, transparency)

---

## Methodology Statement

**MANDATE**: Write tests before implementation. Follow red-green-refactor cycle.

**TDD is required for all code changes in software development workflows.**

---

## The TDD Cycle

### Red-Green-Refactor Pattern

```
RED → GREEN → REFACTOR → COMMIT
 ↓      ↓        ↓         ↓
TEST   CODE    CLEAN    RECORD
```

Every code change follows this cycle. No exceptions.

---

## Phase 1: RED (Write Failing Test)

### Objective
Create a test that fails for the right reason.

### Constitutional Requirements
- [ ] Test MUST be written before implementation
- [ ] Test MUST fail when run (verify red state)
- [ ] Failure reason MUST be verified correct
- [ ] Test MUST cover edge cases, not just happy path
- [ ] Evidence MUST be provided (test output captured)

### Procedure

**Step 1: Write Test for Desired Behavior**
```python
# tests/test_user.py
def test_email_validation_rejects_invalid_format():
    """Invalid email format should raise ValueError."""
    with pytest.raises(ValueError, match="Invalid email"):
        User(email="not-an-email")
```

**Step 2: Run Test to Verify Failure**
```bash
pytest tests/test_user.py::test_email_validation_rejects_invalid_format -v
```

**Step 3: Verify Failure Reason**
Check that test fails because feature not implemented, NOT because test is broken.

**Expected failure**: `User does not validate email format`
**NOT acceptable**: `SyntaxError` or `ImportError` (test is broken)

**Step 4: Document Red State**
```markdown
## RED Phase Evidence

Test: test_email_validation_rejects_invalid_format
File: tests/test_user.py:45
Result: ❌ FAILED (expected)
Reason: User class does not validate email format

Output:
```
FAILED - DID NOT RAISE ValueError
```

Confidence: 100% (test fails for correct reason)
```

### Edge Cases Requirement

Every RED phase MUST include edge cases:

**Happy Path** (insufficient alone):
```python
def test_valid_email_accepted():
    user = User(email="valid@example.com")
    assert user.email == "valid@example.com"
```

**Edge Cases** (required):
```python
def test_email_without_at_sign_rejected():
    with pytest.raises(ValueError):
        User(email="invalid-email")

def test_email_without_domain_rejected():
    with pytest.raises(ValueError):
        User(email="user@")

def test_empty_email_rejected():
    with pytest.raises(ValueError):
        User(email="")

def test_email_with_special_chars_accepted():
    user = User(email="user+tag@example.co.uk")
    assert user.email == "user+tag@example.co.uk"
```

---

## Phase 2: GREEN (Make Test Pass)

### Objective
Implement the simplest code that makes the test pass.

### Constitutional Requirements
- [ ] Implementation MUST be minimal (no gold-plating)
- [ ] Test MUST pass when run (verify green state)
- [ ] All tests MUST still pass (regression check)
- [ ] Evidence MUST be provided (test output captured)
- [ ] No shortcuts that compromise correctness

### Procedure

**Step 1: Implement Minimal Solution**
```python
# models/user.py
import re

class User:
    def __init__(self, email):
        # Minimal implementation - just enough to pass tests
        if not email or '@' not in email or not email.split('@')[1]:
            raise ValueError("Invalid email")
        self.email = email
```

**Reasoning**: This is minimal but correct. Don't add unnecessary features (YAGNI principle).

**Step 2: Run Specific Test**
```bash
pytest tests/test_user.py::test_email_validation_rejects_invalid_format -v
```

**Expected**: ✅ PASSED

**Step 3: Run All Tests (Regression Check)**
```bash
pytest tests/test_user.py -v
```

**Expected**: ✅ ALL PASSED

**Step 4: Document Green State**
```markdown
## GREEN Phase Evidence

Implementation: User.__init__ email validation
File: models/user.py:15
Result: ✅ Specific test PASSED
Result: ✅ All tests PASSED (47 total)

Output:
```
test_email_validation_rejects_invalid_format PASSED
test_email_without_at_sign_rejected PASSED
test_email_without_domain_rejected PASSED
test_empty_email_rejected PASSED
test_email_with_special_chars_accepted PASSED
==================== 47 passed in 2.45s ====================
```

Confidence: 100% (all tests green)
```

### Anti-Patterns to Avoid

❌ **Gold-plating**: Adding features not covered by tests
```python
# DON'T DO THIS in GREEN phase
class User:
    def __init__(self, email):
        if not self._validate_email(email):
            raise ValueError("Invalid email")
        self.email = email
        self.email_verified = False  # ❌ Not in requirements
        self.verification_token = generate_token()  # ❌ Not tested
```

✅ **Minimal implementation**: Only what tests require
```python
# DO THIS in GREEN phase
class User:
    def __init__(self, email):
        if not email or '@' not in email or not email.split('@')[1]:
            raise ValueError("Invalid email")
        self.email = email  # ✅ Just enough
```

---

## Phase 3: REFACTOR (Improve Code Quality)

### Objective
Improve code quality without changing behavior.

### Constitutional Requirements
- [ ] Refactoring MUST maintain all passing tests
- [ ] Tests MUST pass after each refactoring step
- [ ] Code quality MUST improve (DRY, Clean Code, SOLID)
- [ ] No temporary scaffolding left behind
- [ ] Evidence MUST be provided for each refactoring

### Refactoring Checklist

**Code Smells to Fix**:
- [ ] Long methods (>20 lines) → Extract functions
- [ ] Magic numbers/strings → Named constants
- [ ] Unclear variable names → Descriptive names
- [ ] Code duplication → DRY principle
- [ ] Complex conditionals → Guard clauses or extraction
- [ ] Temporary bridges/wrappers → Remove after migration

**SOLID Principles**:
- [ ] Single Responsibility: Each function does one thing
- [ ] Open/Closed: Open for extension, closed for modification
- [ ] Liskov Substitution: Subtypes must be substitutable
- [ ] Interface Segregation: Many specific interfaces > one general
- [ ] Dependency Inversion: Depend on abstractions, not concretions

### Refactoring Example

**Before** (works but has code smells):
```python
class User:
    def __init__(self, email):
        if not email or '@' not in email or not email.split('@')[1]:
            raise ValueError("Invalid email")
        self.email = email
```

**Refactoring 1: Extract email validation logic**
```python
EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

class User:
    def __init__(self, email):
        if not self._is_valid_email(email):
            raise ValueError(f"Invalid email: {email}")
        self.email = email

    @staticmethod
    def _is_valid_email(email):
        """Validate email format using regex."""
        return re.match(EMAIL_REGEX, email) is not None
```

**Run tests**: ✅ All pass

**Refactoring 2: Improve error message**
```python
class User:
    def __init__(self, email):
        if not self._is_valid_email(email):
            raise ValueError(
                f"Invalid email format: '{email}'. "
                f"Expected format: user@domain.com"
            )
        self.email = email
```

**Run tests**: ✅ All pass (pytest.raises matches substring)

**Document Refactoring**:
```markdown
## REFACTOR Phase Evidence

Refactoring 1: Extract email validation to method
- Reason: Single Responsibility Principle
- Result: ✅ All tests pass

Refactoring 2: Add descriptive error message
- Reason: Better debugging experience
- Result: ✅ All tests pass

Refactoring 3: Extract regex to module constant
- Reason: DRY (reusable), no magic strings
- Result: ✅ All tests pass

Final state: Clean, maintainable, all tests green
Confidence: 100%
```

---

## Phase 4: COMMIT (Record Work)

### Objective
Record work with proper git commit.

### Constitutional Requirements
- [ ] Commit message follows conventional commits format
- [ ] Commit includes only related changes (atomic)
- [ ] Commit message explains WHAT and WHY
- [ ] Evidence shows commit created successfully
- [ ] Working directory clean after commit

### Conventional Commit Format

```
<type>: <concise description>

<optional body explaining WHY>

Evidence:
- Tests: <count> passing
- Coverage: <percentage>%
- Quality: All checks passed
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code improvement without behavior change
- `perf`: Performance improvement
- `style`: Formatting, no code change
- `test`: Adding/updating tests
- `docs`: Documentation only
- `chore`: Maintenance tasks

### Commit Procedure

**Step 1: Stage Changes**
```bash
git add models/user.py tests/test_user.py
```

**Step 2: Verify Staged Changes**
```bash
git diff --cached
```

**Step 3: Create Commit**
```bash
git commit -m "feat: Add email validation to User model

Implements email format validation using regex pattern.
Validates: non-empty, contains @, has domain, has TLD.

Evidence:
- Tests: 47/47 passing
- Coverage: 100% of validation logic
- Quality: All checks passed (black, flake8, mypy)
- Refactoring: Extracted validation method, improved error messages"
```

**Step 4: Verify Commit**
```bash
git log -1 --oneline
git status
```

**Expected**: Clean working tree

---

## TDD Quality Gates

### Pre-Implementation Checklist

Before writing any production code:
- [ ] RED phase complete (failing test exists)
- [ ] Test fails for correct reason (not broken test)
- [ ] Edge cases included in test suite
- [ ] Test is focused (tests one behavior)

### Pre-Commit Checklist

Before committing any code:
- [ ] GREEN phase complete (all tests pass)
- [ ] REFACTOR phase complete (code is clean)
- [ ] No code smells remain
- [ ] Test coverage ≥80% for new code
- [ ] All quality checks pass (linting, typing, formatting)
- [ ] No console.log, debugger, or debug prints remain
- [ ] Commit message follows conventional commits

### Coverage Requirements

**Minimum**: 80% line coverage for new code
**Target**: 90%+ line coverage
**Critical paths**: 100% coverage (authentication, payment, security)

**Check coverage**:
```bash
pytest --cov=models --cov-report=term-missing tests/
```

**Coverage report**:
```
Name                Stmts   Miss  Cover   Missing
-------------------------------------------------
models/user.py         15      0   100%
models/auth.py         42      3    93%   23-25
-------------------------------------------------
TOTAL                  57      3    95%
```

---

## Integration with Constitutional Principles

### Evidence-Based Claims
TDD provides built-in evidence: passing tests prove behavior.

```markdown
Claim: "User email validation works correctly"
Evidence:
- test_email_validation_rejects_invalid_format: ✅ PASSED
- test_email_without_at_sign_rejected: ✅ PASSED
- test_email_without_domain_rejected: ✅ PASSED
- test_empty_email_rejected: ✅ PASSED
- Coverage: 100% of validation logic
Confidence: 100%
```

### Multi-Method Verification
TDD uses multiple verification methods:
1. **Unit tests**: Behavior verification
2. **Coverage analysis**: Completeness verification
3. **Static analysis**: Code quality verification (mypy, flake8)
4. **Manual code review**: Logic verification

### Complete Transparency
TDD requires showing all work:
- RED phase: Document failing test
- GREEN phase: Document implementation
- REFACTOR phase: Document improvements
- COMMIT phase: Record in git history

---

## TDD Anti-Patterns

### ❌ Testing Implementation Details
```python
# BAD - tests internal implementation
def test_email_validation_uses_regex():
    user = User(email="test@example.com")
    assert hasattr(user, '_is_valid_email')  # ❌ Implementation detail
```

### ✅ Testing Behavior
```python
# GOOD - tests external behavior
def test_email_validation_rejects_invalid_format():
    with pytest.raises(ValueError):
        User(email="invalid")  # ✅ Public behavior
```

### ❌ Writing Tests After Code
This defeats the purpose of TDD. Tests must come first.

### ❌ Skipping Refactor Phase
Leaving code messy because "tests pass" creates technical debt.

### ❌ Not Running All Tests
Only running new test misses regressions. Always run full suite.

---

## TDD Enforcement Mechanisms

### Layer 1: Skills
- `pre-commit-review` skill runs quality checks
- `test-coverage-check` skill verifies ≥80% coverage
- `validate-code` skill checks for code smells

### Layer 2: Hooks
- `on_stop.py` verifies tests pass before allowing commit
- Pre-commit hooks run black, isort, flake8, mypy

### Layer 3: Agents
- Agents have TDD methodology embedded in prompts
- Senior Developer writes tests first by design
- Test Engineer validates coverage requirements

### Layer 4: Git Workflow
- Feature branches require tests
- PRs blocked until tests pass
- CI/CD runs full test suite

---

## TDD Workflow Example

### Scenario: Add User Authentication

**RED Phase**:
```python
# tests/test_auth.py
def test_authenticate_with_valid_credentials():
    user = User(email="test@example.com", password="secret123")
    assert user.authenticate("secret123") is True

def test_authenticate_with_invalid_credentials():
    user = User(email="test@example.com", password="secret123")
    assert user.authenticate("wrong") is False

def test_password_is_hashed_not_stored_plaintext():
    user = User(email="test@example.com", password="secret123")
    assert user.password != "secret123"  # Must be hashed
```

Run: `pytest tests/test_auth.py -v`
Result: ❌ FAILED (User has no authenticate method)

**GREEN Phase**:
```python
# models/user.py
import bcrypt

class User:
    def __init__(self, email, password=None):
        if not self._is_valid_email(email):
            raise ValueError(f"Invalid email: {email}")
        self.email = email
        if password:
            self.password = bcrypt.hashpw(
                password.encode('utf-8'),
                bcrypt.gensalt()
            )

    def authenticate(self, password):
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password
        )
```

Run: `pytest tests/test_auth.py -v`
Result: ✅ ALL PASSED

**REFACTOR Phase**:
```python
# Extract password hashing to separate concern
class User:
    def __init__(self, email, password=None):
        if not self._is_valid_email(email):
            raise ValueError(f"Invalid email: {email}")
        self.email = email
        if password:
            self.password = self._hash_password(password)

    @staticmethod
    def _hash_password(password):
        """Hash password using bcrypt."""
        return bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        )

    def authenticate(self, password):
        """Verify password against stored hash."""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password
        )
```

Run: `pytest tests/test_auth.py -v`
Result: ✅ ALL PASSED

**COMMIT Phase**:
```bash
git add models/user.py tests/test_auth.py
git commit -m "feat: Add password authentication to User model

Implements bcrypt password hashing and authentication.
Passwords stored as hashes, never plaintext.

Evidence:
- Tests: 3/3 new tests passing, 50 total passing
- Coverage: 100% of auth logic
- Security: OWASP compliant (bcrypt hashing)
- Quality: All checks passed"
```

---

## TDD Checklist

Before claiming any code change complete:

- [ ] **RED**: Wrote failing test first
- [ ] **RED**: Test fails for correct reason
- [ ] **RED**: Edge cases included
- [ ] **GREEN**: Minimal implementation
- [ ] **GREEN**: Specific test passes
- [ ] **GREEN**: All tests pass (no regressions)
- [ ] **REFACTOR**: Code is clean (no smells)
- [ ] **REFACTOR**: SOLID principles followed
- [ ] **REFACTOR**: Tests still green after refactoring
- [ ] **COMMIT**: Conventional commit message
- [ ] **COMMIT**: Atomic commit (related changes only)
- [ ] **Coverage**: ≥80% line coverage
- [ ] **Quality**: black, isort, flake8, mypy pass

**If ANY box is unchecked, work is NOT complete.**

---

## Constitutional Reminder

**TDD is the software development manifestation of constitutional principles**:
- Evidence-Based Claims → Tests prove behavior
- Multi-Method Verification → Tests + coverage + static analysis
- Complete Transparency → RED-GREEN-REFACTOR documented
- Thoroughness Over Speed → Write tests first, no shortcuts

**TDD is not optional in software development workflows. It is constitutional law for code changes.**
