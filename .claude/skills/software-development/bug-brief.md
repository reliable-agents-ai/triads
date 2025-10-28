---
name: bug-brief
description: Transform vague bug report into complete BugBrief specification with reproduction steps, expected vs actual behavior, and acceptance criteria. Use when user reports bugs, issues, errors, crashes, broken functionality, failures, exceptions, or not working features. Discovers via keywords - bug, issue, error, crash, broken, fails, not working, exception, stack trace, failure, problem, defect, regression, production issue, incident, glitch, malfunction, doesn't work, freezes, hangs, unresponsive, broken behavior, unexpected behavior, error message, warning, critical, blocker, high priority, cannot, unable to, won't, stopped working, used to work, recently broke
category: brief
domain: software-development
generated_by: upgrade-executor
generated_at: 2025-10-28T17:45:00Z
allowed_tools: ["Grep", "Read", "AskUserQuestion"]
---

# Bug Brief Skill

## Purpose

Transform vague bug report into complete BugBrief specification.

**What users say**: "login is broken", "app crashes when I...", "error message appears", "doesn't work"

**What this skill creates**: Complete bug specification with:
- One-sentence summary
- Reproduction steps
- Expected vs actual behavior
- Acceptance criteria for fix
- Error messages and affected files (if available)

## Keywords for Discovery

bug, issue, error, crash, broken, fails, not working, exception, stack trace, failure, problem, defect, regression, production issue, incident, glitch, malfunction, doesn't work, freezes, hangs, unresponsive, broken behavior, unexpected behavior, error message, warning, critical, blocker, high priority, cannot, unable to, won't, stopped working, used to work, recently broke, threw error, traceback, failed assertion, test failure, integration failure

## When to Invoke This Skill

Invoke when user provides vague bug report like:
- "Login is broken"
- "App crashes when I click submit"
- "Getting an error message"
- "Feature X doesn't work anymore"
- "Users can't access Y"
- "System freezes on startup"
- "Tests are failing"
- "Production incident"

## Skill Procedure

### Step 1: Clarify Input with Questions

Use AskUserQuestion to gather missing information:

**Questions for bug reports**:
1. Can you reproduce this bug consistently? (Yes/No/Sometimes)
2. What were you doing when it happened? (Steps leading to bug)
3. What did you expect to happen? (Expected behavior)
4. What actually happened instead? (Actual behavior)
5. Are there any error messages? (Copy exact error text)
6. What environment? (OS, browser, version, etc.)

---

### Step 2: Gather Context Using Tools

**Use Grep to find relevant code**:
```bash
# Search for error-related code
Grep pattern="login" path=.
Grep pattern="authentication" path=.
Grep pattern="error.*{user_keyword}" path=.
```

**Use Read to examine files**:
```bash
# Read files discovered from Grep
Read file_path="{file_from_grep_results}"
```

**Analyze for**:
- Error handling code
- Related functionality
- Recent changes (if git available)
- Test coverage for affected area

---

### Step 3: Create BugBrief Knowledge Graph Node

Based on gathered information, create structured specification:

```markdown
[GRAPH_UPDATE]
type: add_node
node_id: bug_brief_{sanitized_summary}_{timestamp}
node_type: BugBrief

metadata:
  created_by: bug-brief-skill
  created_at: {ISO 8601 timestamp}
  confidence: {0.85-1.0 based on information completeness}
  domain: software-development
  output_type: "brief"

data:
  summary: "{One-sentence bug description}"

  reproduction_steps:
    - "{Step 1}"
    - "{Step 2}"
    - "{Step 3}"
    - "Expected: {what should happen}"
    - "Actual: {what actually happens}"

  expected_behavior: "{What the user expected}"
  actual_behavior: "{What actually occurred}"

  acceptance_criteria:
    - "Bug no longer occurs when following reproduction steps"
    - "{Specific fix validation criterion 1}"
    - "{Specific fix validation criterion 2}"

  error_messages:
    - "{Error text 1}"
    - "{Error text 2}"

  affected_files:
    - "{file_path:line_number}"
    - "{file_path:line_number}"

  environment:
    os: "{operating system}"
    browser: "{browser + version}"
    app_version: "{version}"
    other: "{relevant environment details}"

  severity: "{CRITICAL|HIGH|MEDIUM|LOW based on impact}"
  reproducibility: "{ALWAYS|SOMETIMES|ONCE}"

handoff:
  ready_for_next: true
  next_stage: "implementation-triad"
  required_fields: ["summary", "reproduction_steps", "expected_behavior", "actual_behavior", "acceptance_criteria"]
  optional_fields: ["error_messages", "affected_files", "environment", "severity", "reproducibility"]

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
    created_by: "bug-brief"
    domain: "software-development"
    timestamp: "{ISO 8601}"
    confidence: {0.85-1.0}

  _handoff:
    next_stage: "implementation-triad"
    graph_node: "bug_brief_{sanitized_summary}_{timestamp}"
    required_fields: ["summary", "reproduction_steps", "expected_behavior", "actual_behavior", "acceptance_criteria"]
    optional_fields: ["error_messages", "affected_files", "environment"]
```

---

## Output Format

Returns:
- **Knowledge graph node** with complete bug specification (stored in graph)
- **Standard OUTPUT envelope** with node reference (lightweight handoff)

**User sees**:
```markdown
✅ Created BugBrief specification: bug_brief_login_broken_20251028_173045

**Summary**: Login form fails to authenticate valid credentials

**Reproduction Steps**:
1. Navigate to /login
2. Enter valid username and password
3. Click "Submit"
Expected: Redirect to dashboard
Actual: Error "Invalid credentials" appears

**Acceptance Criteria**:
- Valid credentials authenticate successfully
- Error only appears for actual invalid credentials
- Dashboard loads after successful login

**Next Stage**: implementation-triad

View full specification in knowledge graph: bug_brief_login_broken_20251028_173045
```

---

## Example Usage

**User Input**: "login is broken"

**Skill Process**:
1. ✅ Keyword match: "broken" triggers bug-brief skill
2. ✅ Asked clarifying questions via AskUserQuestion
   - User provided: reproduction steps, expected vs actual, no error message visible
3. ✅ Searched codebase with Grep for "login" and "authentication"
   - Found: src/auth/login.py, src/auth/validators.py
4. ✅ Read relevant files with Read tool
   - Discovered: Password validation logic in validators.py:45
5. ✅ Created BugBrief knowledge graph node with complete specification
6. ✅ Returned OUTPUT envelope with node reference

**Output**: Complete bug specification ready for implementation triad

---

## Integration with Standard Output Protocol

This skill follows the standard output protocol (`.claude/protocols/standard-output.md`):
- Creates knowledge graph node (full data storage)
- Returns OUTPUT envelope (lightweight handoff)
- Downstream agents load node by reference

**Node structure** follows `.claude/protocols/node-types.md` → BugBrief definition.

---

## Why This Skill Matters

**Before**:
- User: "login is broken"
- Developer: "Can you provide more details?"
- [Multiple back-and-forth messages]
- [Developer manually searches code]
- [Finally enough context to start fixing]

**After**:
- User: "login is broken"
- bug-brief skill activates automatically
- Asks structured questions once
- Gathers code context automatically
- Creates complete specification
- Implementation triad receives structured input and fixes bug immediately

**Time saved**: ~15-20 minutes per bug report
**Context quality**: Systematic and complete

---

## Constitutional Integration

This skill enforces constitutional principles:

- **Evidence-Based Claims**: All findings cite code locations, error messages, environment details
- **Multi-Method Verification**: Uses Grep (search) + Read (inspection) + AskUserQuestion (clarification)
- **Complete Transparency**: Shows complete reasoning chain from vague input → structured brief
- **Uncertainty Escalation**: If confidence < 85%, flags missing information and requests clarification
- **Assumption Auditing**: Documents assumptions (e.g., "Assuming production environment" if not specified)

**This skill is the software development manifestation of brief transformation.**
