---
name: refactor-brief
description: Transform vague refactoring request into complete RefactorBrief specification with scope, code smells, refactoring patterns, and success criteria. Use when user mentions code quality issues, technical debt, cleanup, or improvements needed. Discovers via keywords - refactor, cleanup, improve, simplify, technical debt, code smell, messy, duplicated, complex, hard to understand, difficult to maintain, spaghetti, legacy, consolidate, extract, rename, reorganize, optimize, streamline
category: brief
domain: software-development
generated_by: upgrade-executor
generated_at: 2025-10-28T17:45:00Z
allowed_tools: ["Grep", "Read", "AskUserQuestion", "Bash"]
---

# Refactor Brief Skill

## Purpose

Transform vague refactoring request into complete RefactorBrief specification.

**What users say**: "code is messy", "lots of duplication", "hard to understand", "technical debt"

**What this skill creates**: Complete refactoring specification with:
- Scope definition (files, modules affected)
- Code smells identified
- Refactoring patterns to apply
- Success criteria
- Risk assessment

## Keywords for Discovery

refactor, cleanup, improve, simplify, technical debt, code smell, messy, duplicated, complex, hard to understand, difficult to maintain, spaghetti, legacy, consolidate, extract, rename, reorganize, optimize, streamline, rewrite, restructure, clean up, tidy, maintenance, quality, readability, DRY violation, long method, god class, feature envy, primitive obsession, shotgun surgery

## When to Invoke This Skill

Invoke when user mentions code quality issues like:
- "This code is messy"
- "Lots of duplication in the auth module"
- "Hard to understand what this does"
- "We have technical debt in the API"
- "Code needs cleanup before release"
- "Functions are too long"
- "Classes are doing too much"
- "Need to improve maintainability"

## Skill Procedure

### Step 1: Clarify Input with Questions

Use AskUserQuestion to gather missing information:

**Questions for refactoring requests**:
1. What area needs refactoring? (Module, file, function)
2. What specific problems exist? (Duplication, complexity, unclear names)
3. What triggered this? (Bug, new feature blocked, code review feedback)
4. Are there tests? (Coverage level)
5. What's the timeline? (When needed by)
6. Are there constraints? (Can't break existing API, must maintain compatibility)

---

### Step 2: Gather Context Using Tools

**Use Grep to find code smells**:
```bash
# Search for duplication patterns
Grep pattern="{suspected_duplicate_code}" path=.

# Find long functions (heuristic: many line breaks)
Grep pattern="^def.*:" path=. -A 50 | grep -c "^$"

# Find TODO/FIXME comments indicating debt
Grep pattern="TODO|FIXME|HACK|XXX" path=.
```

**Use Read to examine code quality**:
```bash
# Read files with suspected issues
Read file_path="{file_from_grep}"
```

**Use Bash to analyze metrics**:
```bash
# Count lines per function (complexity indicator)
# Run linting tools
flake8 {module} --select=C901  # Cyclomatic complexity
pylint {module} --disable=all --enable=R  # Refactoring suggestions

# Check test coverage
pytest --cov={module} --cov-report=term-missing
```

**Analyze for**:
- Code smells (duplication, long methods, god classes)
- Complexity metrics (cyclomatic complexity, nesting depth)
- Test coverage gaps
- Dependencies between components
- Recent changes (git blame for problem areas)

---

### Step 3: Create RefactorBrief Knowledge Graph Node

Based on gathered information, create structured specification:

```markdown
[GRAPH_UPDATE]
type: add_node
node_id: refactor_brief_{sanitized_name}_{timestamp}
node_type: RefactorBrief

metadata:
  created_by: refactor-brief-skill
  created_at: {ISO 8601 timestamp}
  confidence: {0.85-1.0 based on information completeness}
  domain: software-development
  output_type: "brief"

data:
  refactoring_name: "{Refactoring name}"
  summary: "{One-sentence refactoring description}"

  scope:
    files:
      - "{file_path_1}"
      - "{file_path_2}"
    modules:
      - "{module_name_1}"
      - "{module_name_2}"
    functions:
      - "{module.function_name}"
    lines_of_code: {approximate LOC affected}

  trigger:
    reason: "{Why refactoring now: bug, feature blocked, review feedback}"
    priority: "{HIGH|MEDIUM|LOW}"
    blocking: "{What this blocks if not done}"

  code_smells_identified:
    - smell: "Long Method"
      location: "{file:line}"
      description: "{function_name} is 150 lines (>20 recommended)"
      severity: "HIGH"
    - smell: "Duplicated Code"
      location: "{file1:line} and {file2:line}"
      description: "Same validation logic in 3 places"
      severity: "MEDIUM"
    - smell: "God Class"
      location: "{file:class_name}"
      description: "UserManager has 25 methods, multiple responsibilities"
      severity: "HIGH"

  refactoring_patterns:
    - pattern: "Extract Method"
      applies_to: "{file:function}"
      rationale: "Break 150-line function into focused sub-functions"
      estimated_effort: "{hours}"
    - pattern: "Extract Class"
      applies_to: "{file:class}"
      rationale: "Split UserManager into UserRepository, UserValidator, UserNotifier"
      estimated_effort: "{hours}"
    - pattern: "Replace Magic Numbers with Named Constants"
      applies_to: "{file:function}"
      rationale: "Clarify intent of numeric literals"
      estimated_effort: "{hours}"

  acceptance_criteria:
    - "All existing tests still pass"
    - "Test coverage maintained or improved (≥{current}%)"
    - "Code complexity reduced: cyclomatic complexity <10 per function"
    - "No code duplication (DRY violations eliminated)"
    - "Function length <20 lines"
    - "Class length <300 lines"
    - "Clear, descriptive names for all variables/functions/classes"
    - "No new bugs introduced (regression testing)"

  current_state:
    test_coverage: "{percentage}%"
    cyclomatic_complexity:
      - function: "{name}"
        complexity: {score}
    duplication: "{percentage}% code duplication detected"
    technical_debt_ratio: "{hours of debt / hours of development}"

  target_state:
    test_coverage: "{target percentage}%"
    cyclomatic_complexity: "All functions <10"
    duplication: "<3% code duplication"
    technical_debt_ratio: "Reduced by {percentage}%"

  risks:
    - risk: "Breaking existing functionality"
      mitigation: "Run full test suite after each refactoring step"
    - risk: "Introducing new bugs"
      mitigation: "Small, incremental changes with frequent testing"
    - risk: "Merge conflicts if others working in same area"
      mitigation: "Communicate with team, coordinate timing"

  constraints:
    - "Must maintain backward compatibility (public API unchanged)"
    - "No changes to database schema"
    - "Must complete before {deadline}"
    - "Cannot break existing integrations"

  dependencies:
    - "Tests must exist before refactoring"
    - "Code review approval required"
    - "Feature freeze during refactoring"

  refactoring_strategy:
    approach: "Incremental (small, testable steps)"
    order:
      - step: 1
        action: "Add tests for existing behavior (if missing)"
        verification: "All tests pass"
      - step: 2
        action: "Extract duplicated code to shared function"
        verification: "Tests still pass, duplication reduced"
      - step: 3
        action: "Break long methods into smaller functions"
        verification: "Tests still pass, complexity reduced"
      - step: 4
        action: "Split god class into focused classes"
        verification: "Tests still pass, SRP satisfied"
      - step: 5
        action: "Rename unclear variables/functions"
        verification: "Tests still pass, readability improved"

handoff:
  ready_for_next: true
  next_stage: "implementation-triad"
  required_fields: ["refactoring_name", "scope", "code_smells_identified", "refactoring_patterns", "acceptance_criteria"]
  optional_fields: ["current_state", "target_state", "risks", "constraints", "refactoring_strategy"]

lineage:
  created_from_node: null
  consumed_by_nodes: []
[/GRAPH_UPDATE]
```

---

### Step 4: Return Standard OUTPUT Envelope

Return lightweight handoff with node reference:

```markdown
OUTPUT:
  _meta:
    output_type: "brief"
    created_by: "refactor-brief"
    domain: "software-development"
    timestamp: "{ISO 8601}"
    confidence: {0.85-1.0}

  _handoff:
    next_stage: "implementation-triad"
    graph_node: "refactor_brief_{sanitized_name}_{timestamp}"
    required_fields: ["refactoring_name", "scope", "code_smells_identified", "refactoring_patterns", "acceptance_criteria"]
    optional_fields: ["current_state", "target_state", "risks"]
```

---

## Output Format

Returns:
- **Knowledge graph node** with complete refactoring specification (stored in graph)
- **Standard OUTPUT envelope** with node reference (lightweight handoff)

**User sees**:
```markdown
✅ Created RefactorBrief specification: refactor_brief_auth_module_cleanup_20251028_173045

**Refactoring**: Auth Module Cleanup

**Scope**:
- Files: auth/login.py, auth/validators.py, auth/user_manager.py
- Lines affected: ~450 LOC

**Code Smells Identified**:
- Long Method: login.py::authenticate() is 120 lines (HIGH)
- Duplicated Code: Email validation duplicated in 3 places (MEDIUM)
- God Class: UserManager has 18 methods (HIGH)

**Refactoring Patterns**:
- Extract Method: Break authenticate() into sub-functions
- Extract Class: Split UserManager → UserRepository, UserValidator, NotificationService
- Replace Magic Numbers: Convert hardcoded values to named constants

**Acceptance Criteria**:
- All 47 existing tests pass
- Coverage maintained at 87%
- Cyclomatic complexity <10 per function
- No code duplication

**Strategy**: Incremental refactoring over 5 steps with testing after each

**Next Stage**: implementation-triad

View full specification in knowledge graph: refactor_brief_auth_module_cleanup_20251028_173045
```

---

## Example Usage

**User Input**: "auth module code is messy"

**Skill Process**:
1. ✅ Keyword match: "messy" triggers refactor-brief skill
2. ✅ Asked clarifying questions via AskUserQuestion
   - Scope: auth module (login, validators, user_manager)
   - Problems: Long functions, duplication, god class
   - Trigger: Code review flagged issues
   - Tests: 87% coverage exists
   - Timeline: Before next release (2 weeks)
3. ✅ Searched codebase with Grep for code smells
   - Found: authenticate() function 120 lines
   - Found: Email validation duplicated in 3 files
   - Found: UserManager class has 18 methods
4. ✅ Ran complexity analysis with Bash
   - Cyclomatic complexity: authenticate() = 15 (high)
   - Code duplication: 12% in auth module
5. ✅ Read affected files with Read tool
   - Confirmed: Multiple responsibilities in UserManager
   - Identified: Magic numbers for token expiry
6. ✅ Created RefactorBrief knowledge graph node with complete specification
7. ✅ Returned OUTPUT envelope with node reference

**Output**: Complete refactoring specification ready for implementation triad

---

## Integration with Standard Output Protocol

This skill follows the standard output protocol (`.claude/protocols/standard-output.md`):
- Creates knowledge graph node (full data storage)
- Returns OUTPUT envelope (lightweight handoff)
- Downstream agents load node by reference

**Node structure** follows `.claude/protocols/node-types.md` → RefactorBrief definition.

---

## Why This Skill Matters

**Before**:
- User: "auth code is messy"
- Developer: "Where? What's messy? How should I fix it?"
- [Developer manually scans code]
- [Finds some issues, misses others]
- [Refactors without clear goals]
- [Breaks tests, introduces bugs]
- [Reverts changes, time wasted]

**After**:
- User: "auth code is messy"
- refactor-brief skill activates automatically
- Analyzes code with metrics (complexity, duplication)
- Identifies specific code smells with locations
- Proposes refactoring patterns with rationale
- Defines clear acceptance criteria
- Creates incremental strategy
- Implementation triad executes safely with tests

**Time saved**: ~1-2 weeks of analysis and false starts
**Quality improvement**: Systematic refactoring prevents bugs

---

## Code Smells Reference

Common code smells this skill identifies:

**Method-Level Smells**:
- Long Method (>20 lines)
- Too Many Parameters (>3-4 params)
- Complex Conditionals (nested if/else)
- Magic Numbers/Strings
- Dead Code

**Class-Level Smells**:
- God Class (too many responsibilities)
- Feature Envy (uses another class's data more than own)
- Data Clump (same group of data repeated)
- Primitive Obsession (should be object)

**Code Organization Smells**:
- Duplicated Code (DRY violation)
- Shotgun Surgery (one change requires many file edits)
- Divergent Change (one class changes for many reasons)
- Parallel Inheritance (adding subclass requires another subclass)

---

## Refactoring Patterns Reference

Common refactoring patterns this skill recommends:

**Composing Methods**:
- Extract Method
- Inline Method
- Extract Variable
- Replace Temp with Query

**Moving Features**:
- Move Method
- Move Field
- Extract Class
- Inline Class

**Organizing Data**:
- Replace Magic Number with Named Constant
- Encapsulate Field
- Replace Data Value with Object

**Simplifying Conditionals**:
- Decompose Conditional
- Consolidate Conditional Expression
- Replace Nested Conditional with Guard Clauses

**SOLID Principles**:
- Single Responsibility Principle (split god classes)
- Open/Closed Principle (extract interfaces)
- Dependency Inversion (depend on abstractions)

---

## Refactoring Safety Protocol

All refactoring follows this safety protocol:

1. **Verify tests exist** (if not, write them first)
2. **Run tests** (establish green baseline)
3. **Make small change** (one refactoring at a time)
4. **Run tests** (verify still green)
5. **Commit** (atomic refactoring commits)
6. **Repeat** (incremental progress)

**If tests fail**: Revert immediately, understand why, fix approach.

**Never**:
- ❌ Refactor without tests
- ❌ Make multiple changes at once
- ❌ Commit broken tests
- ❌ Skip running tests

---

## Constitutional Integration

This skill enforces constitutional principles:

- **Evidence-Based Claims**: All code smells cite metrics (complexity scores, LOC, duplication %)
- **Multi-Method Verification**: Uses Grep (search) + Read (inspection) + Bash (metrics analysis)
- **Complete Transparency**: Shows complete analysis from vague input → code smells → refactoring patterns
- **Uncertainty Escalation**: If confidence < 85%, flags missing tests or unclear scope
- **Assumption Auditing**: Documents assumptions (e.g., "Assuming tests exist" verified by coverage check)
- **No Hyperbole**: Uses objective metrics, not subjective "bad code"
- **Critical Thinking**: Evaluates multiple refactoring patterns, chooses based on cost/benefit

**This skill transforms vague quality concerns into systematic improvement plans with constitutional rigor.**
