---
name: create-command-file
description: Create Claude Code slash commands with argument handling and tool restrictions. Use when generating slash commands, creating custom commands, writing command files, setting up /command syntax, command arguments, command descriptions, allowed-tools configuration, command templates, command file generation, command best practices, command examples, command validation, command testing, slash command creation, user commands, command handlers, command scripts, command parameters, argument parsing, command documentation, command frontmatter, YAML command metadata, command storage, project commands, user-level commands, command discovery, command invocation, command workflows, command patterns, command architecture
---

# Create Slash Command File

**Purpose**: Generate Claude Code slash command files with proper frontmatter and argument handling following official Claude Code specifications.

**Authority**: Meta-level (creates Claude Code components)

**Based on**: [Official Claude Code Slash Commands Documentation](https://docs.claude.com/en/docs/claude-code/slash-commands.md)

---

## 📋 When to Invoke

**Invoke this skill when**:
- Generating custom slash commands
- Creating user workflows
- Setting up command shortcuts
- Implementing command handlers
- Configuring command arguments
- Creating command templates

**Keywords that trigger this skill**:
- "create command"
- "generate slash command"
- "command file"
- "slash command"
- "/command"
- "custom command"

---

## 🎯 Official Specification (From Claude Code Docs)

### What Are Slash Commands?

Slash commands are user-defined shortcuts that expand to full prompts when typed. They enable:
- **Workflow shortcuts** (e.g., `/review-pr` expands to full code review prompt)
- **Template invocation** (e.g., `/test-feature` loads test generation instructions)
- **Argument handling** (e.g., `/analyze-file myfile.py`)
- **Tool restrictions** (limit which tools command can use)

### Command File Structure

```markdown
---
allowed-tools: tool1, tool2, tool3  # Optional: restrict tools
argument-hint: <description>  # Optional: shown in autocomplete
description: What the command does  # Optional but recommended
model: sonnet|opus|haiku  # Optional: model to use
---

The prompt that gets expanded when command is invoked.

Arguments can be accessed via $ARGUMENTS, $1, $2, etc.
```

### Storage Locations

- **User-level** (highest priority): `~/.claude/commands/`
- **Project-level** (lower priority): `.claude/commands/`

User commands override project commands when names conflict.

---

## 📋 Skill Procedure

### Step 1: Gather Command Specifications

**Required information**:
```yaml
command_spec:
  name: "{{command-name}}"  # What user types (without /)
  description: "{{what-command-does}}"
  prompt: "{{expanded-prompt-text}}"
  arguments: "{{expected-arguments}}"  # Optional
  argument_hint: "{{hint-shown-in-autocomplete}}"  # Optional
  allowed_tools: "{{tool-list}}"  # Optional: restrict tools
  model: "{{sonnet|opus|haiku}}"  # Optional
  level: "{{project|user}}"  # Where to store
```

**Example**:
```yaml
command_spec:
  name: "review-pr"
  description: "Perform comprehensive code review of PR changes"
  prompt: "Review the pull request changes with focus on: code quality, security, tests, documentation"
  arguments: "PR number (optional)"
  argument_hint: "<pr-number>"
  allowed_tools: "Read, Grep, Bash"
  model: "sonnet"
  level: "project"
```

---

### Step 2: Create Command Frontmatter

**Generate frontmatter following official spec**:

```yaml
---
allowed-tools: {{optional-tool-list}}
argument-hint: {{optional-hint}}
description: {{optional-description}}
model: {{optional-model}}
---
```

**Field details**:

**allowed-tools** (optional):
- Comma-separated list of tools command can use
- If omitted, command has access to all tools
- Use to restrict command capabilities

```yaml
# Restrict to read-only tools
allowed-tools: Read, Grep, Glob

# Restrict to file operations
allowed-tools: Read, Write, Edit

# Restrict to code execution
allowed-tools: Bash
```

**argument-hint** (optional):
- Shown in autocomplete dropdown
- Helps users understand expected arguments
- Format: `<arg1> <arg2>` or `[optional-arg]`

```yaml
argument-hint: <pr-number>
argument-hint: <file-path>
argument-hint: <feature-name> [scope]
```

**description** (optional):
- Shown in autocomplete dropdown
- Brief explanation of what command does
- Max ~100 characters for readability

```yaml
description: Review pull request changes for quality and security
description: Generate tests for specified file
description: Analyze codebase structure and generate report
```

**model** (optional):
- Which model to use for this command
- Values: `sonnet`, `opus`, `haiku`
- If omitted, uses default model

```yaml
model: sonnet  # Balanced performance/cost
model: opus    # Most capable, slowest
model: haiku   # Fastest, cheapest
```

---

### Step 3: Create Command Prompt

**Prompt structure**:

```markdown
---
[frontmatter]
---

Your prompt text here.

You can use:
- $ARGUMENTS: All arguments as single string
- $1, $2, $3, etc.: Individual arguments
- Bash commands: `ls`, `cat`, etc.
- File references: @file.md syntax
```

**Argument access**:

```bash
# $ARGUMENTS = all arguments as string
/my-command arg1 arg2 arg3
# $ARGUMENTS = "arg1 arg2 arg3"

# $1, $2, $3 = individual arguments
/my-command arg1 arg2 arg3
# $1 = "arg1"
# $2 = "arg2"
# $3 = "arg3"
```

**Example with arguments**:
```markdown
---
argument-hint: <file-path>
description: Analyze Python file for code quality issues
---

Analyze the Python file at `$1` for:

1. Code quality (DRY, SOLID, Clean Code)
2. Security vulnerabilities (OWASP Top 10)
3. Test coverage gaps
4. Documentation completeness

Provide specific line numbers and actionable recommendations.
```

**Example with Bash commands**:
```markdown
---
description: Generate project structure report
---

Generate a comprehensive project structure report:

\`\`\`bash
# Count total lines of code
find . -name "*.py" | xargs wc -l | tail -1

# List largest files
find . -name "*.py" -exec wc -l {} + | sort -rn | head -10

# Count total files by type
find . -type f | sed 's/.*\.//' | sort | uniq -c | sort -rn
\`\`\`

Analyze the output and summarize:
- Total lines of code
- 10 largest files
- File type distribution
```

**Example with file references**:
```markdown
---
description: Review code against project standards
---

Review the code following these standards:

@.claude/methodologies/software/code-quality-standards.md
@.claude/methodologies/software/security-protocols.md

Check for:
1. Compliance with coding standards
2. Security vulnerabilities
3. Missing tests
4. Documentation gaps
```

---

### Step 4: Determine Storage Location

**Path structure**:

**Project-level** (recommended for team commands):
```
.claude/commands/<command-name>.md
```

**User-level** (personal commands):
```
~/.claude/commands/<command-name>.md
```

**Examples**:
```
# Project commands (team-shared)
.claude/commands/review-pr.md
.claude/commands/test-feature.md
.claude/commands/generate-docs.md

# User commands (personal)
~/.claude/commands/my-workflow.md
~/.claude/commands/debug-helper.md
```

**When to use each**:
- **Project-level**: Team workflows, project-specific standards
- **User-level**: Personal shortcuts, custom workflows

---

### Step 5: Write Command File

**Complete command file**:

```markdown
---
allowed-tools: {{optional-tools}}
argument-hint: {{optional-hint}}
description: {{optional-description}}
model: {{optional-model}}
---

{{PROMPT_CONTENT}}
```

**Example 1: Simple command (no arguments)**:

**File**: `.claude/commands/status.md`

```markdown
---
description: Show project status summary
---

Provide a comprehensive project status summary:

1. **Git status**: Show current branch, uncommitted changes
2. **Build status**: Run tests and report results
3. **Code quality**: Run linters and report issues
4. **Dependencies**: Check for outdated packages

Format as structured report with clear sections.
```

**Example 2: Command with arguments**:

**File**: `.claude/commands/analyze-file.md`

```markdown
---
argument-hint: <file-path>
description: Analyze file for quality issues
allowed-tools: Read, Bash
model: sonnet
---

Analyze the file at `$1` for:

## Code Quality
- DRY violations
- SOLID principle violations
- Code smells
- Complexity issues

## Security
- OWASP Top 10 vulnerabilities
- Hardcoded secrets
- Injection risks

## Testing
- Missing test coverage
- Edge cases not tested

## Documentation
- Missing docstrings
- Unclear variable names
- Complex logic without comments

Provide specific line numbers and actionable recommendations.
```

**Example 3: Command with Bash execution**:

**File**: `.claude/commands/check-deps.md`

```markdown
---
description: Check for outdated dependencies
allowed-tools: Bash
---

Check for outdated dependencies:

\`\`\`bash
# Python
pip list --outdated

# JavaScript
npm outdated

# Show security vulnerabilities
pip-audit
npm audit
\`\`\`

Analyze the output and provide:
1. List of outdated packages with current and latest versions
2. Security vulnerabilities found
3. Recommended update priority (critical, high, medium, low)
4. Breaking change warnings
```

**Example 4: Command with file references**:

**File**: `.claude/commands/review-code.md`

```markdown
---
argument-hint: <file-path>
description: Review code against project standards
allowed-tools: Read, Grep
---

Review `$1` against project standards:

@.claude/methodologies/software/code-quality-standards.md
@.claude/methodologies/software/security-protocols.md
@.claude/methodologies/software/tdd-methodology.md

**Checklist**:

## Code Quality
- [ ] DRY: No duplication
- [ ] SOLID: Single responsibility
- [ ] Clean Code: Clear names, <20 line functions
- [ ] No code smells

## Security
- [ ] No SQL injection risks
- [ ] No hardcoded secrets
- [ ] Input validation present
- [ ] OWASP Top 10 compliance

## Testing
- [ ] Tests present
- [ ] Coverage ≥80%
- [ ] Edge cases covered

Provide line-by-line feedback with specific recommendations.
```

---

### Step 6: Validate Command File

**Validation**:

```bash
# Check file exists
ls .claude/commands/review-pr.md

# Check frontmatter (first 10 lines)
head -10 .claude/commands/review-pr.md

# Verify YAML syntax
# (frontmatter should be valid YAML between --- markers)
```

**Expected structure**:
```
---
[valid YAML frontmatter]
---

[prompt content]
```

---

### Step 7: Test Command

**Test invocation**:

```bash
# Test command without arguments
/status

# Test command with arguments
/analyze-file src/main.py

# Test command with multiple arguments
/review-code models/user.py security
```

**Verify**:
- Command expands to full prompt
- Arguments substituted correctly ($1, $2, etc.)
- Bash commands execute if present
- File references load correctly
- Tool restrictions enforced

---

## 📊 Output Format

```yaml
command_file_created:
  name: "{{command-name}}"
  path: ".claude/commands/{{command-name}}.md"
  frontmatter:
    allowed_tools: "{{tools}}"
    argument_hint: "{{hint}}"
    description: "{{description}}"
    model: "{{model}}"
  prompt_length_lines: {{COUNT}}
  has_arguments: "{{YES|NO}}"
  has_bash_commands: "{{YES|NO}}"
  has_file_references: "{{YES|NO}}"
  validation: "{{PASS|FAIL}}"
```

---

## 💡 Command Examples

### Example 1: Code Review Command

**File**: `.claude/commands/review-pr.md`

```markdown
---
argument-hint: <pr-number>
description: Comprehensive code review of pull request changes
allowed-tools: Read, Bash, Grep
model: sonnet
---

Perform comprehensive code review of PR #$1:

\`\`\`bash
# Get PR diff
gh pr diff $1

# Get PR description
gh pr view $1

# Check test coverage
pytest --cov=. --cov-report=term-missing
\`\`\`

Review against standards:
@.claude/methodologies/software/code-quality-standards.md
@.claude/methodologies/software/security-protocols.md

**Review checklist**:

## Code Quality
- [ ] DRY: No duplication
- [ ] SOLID principles followed
- [ ] Clean code: Functions <20 lines
- [ ] Clear variable names
- [ ] No code smells

## Security
- [ ] No injection vulnerabilities
- [ ] Input validation present
- [ ] No hardcoded secrets
- [ ] OWASP Top 10 compliant

## Testing
- [ ] Tests added for new features
- [ ] Tests updated for changes
- [ ] Coverage ≥80%
- [ ] Edge cases covered

## Documentation
- [ ] Docstrings present
- [ ] README updated
- [ ] CHANGELOG updated
- [ ] Breaking changes documented

Provide line-by-line feedback with:
- Issue description
- Severity (critical, high, medium, low)
- Recommended fix
- File and line number
```

---

### Example 2: Test Generation Command

**File**: `.claude/commands/test-feature.md`

```markdown
---
argument-hint: <file-path>
description: Generate comprehensive tests for specified file
allowed-tools: Read, Write
model: sonnet
---

Generate comprehensive tests for `$1`:

1. **Read existing implementation**:
   - Understand function signatures
   - Identify public API
   - Note edge cases

2. **Generate tests**:
   - Unit tests for all public functions
   - Edge case tests (empty, null, boundary)
   - Error handling tests
   - Integration tests if needed

3. **Follow TDD methodology**:
   @.claude/methodologies/software/tdd-methodology.md

4. **Ensure coverage**:
   - Target ≥90% line coverage
   - Cover all branches
   - Test error paths

5. **Write to test file**:
   - Naming: `test_<filename>.py`
   - Location: `tests/` directory
   - Format: pytest style

Include:
- Fixtures for common setup
- Parameterized tests for multiple inputs
- Mock external dependencies
- Clear test names describing what's tested
```

---

### Example 3: Documentation Command

**File**: `.claude/commands/generate-docs.md`

```markdown
---
description: Generate API documentation from code
allowed-tools: Read, Write, Bash
model: sonnet
---

Generate comprehensive API documentation:

\`\`\`bash
# Find all Python files
find . -name "*.py" -not -path "./tests/*" -not -path "./venv/*"
\`\`\`

For each public module:

1. **Extract API surface**:
   - Public classes
   - Public functions
   - Class methods
   - Function signatures

2. **Generate documentation**:
   - Module description
   - Class documentation
   - Function documentation
   - Parameter descriptions
   - Return value descriptions
   - Examples

3. **Write to docs/**:
   - One file per module
   - Markdown format
   - Cross-references between modules

4. **Generate index**:
   - docs/README.md with table of contents
   - Alphabetical listing
   - Category grouping

Format using standard docstring style:
@.claude/methodologies/software/code-quality-standards.md
```

---

### Example 4: Security Audit Command

**File**: `.claude/commands/security-audit.md`

```markdown
---
description: Run comprehensive security audit
allowed-tools: Bash, Read, Write
model: sonnet
---

Run comprehensive security audit:

\`\`\`bash
# Python security scanning
bandit -r . -f json -o bandit-report.json

# Dependency vulnerability scanning
pip-audit --format=json > pip-audit-report.json

# Check for secrets
trufflehog filesystem . --json > secrets-report.json
\`\`\`

Analyze against OWASP Top 10:
@.claude/methodologies/software/security-protocols.md

**Audit report**:

## 1. Broken Access Control
- [ ] Authorization checks present
- [ ] No direct object references
- [ ] Default deny

## 2. Cryptographic Failures
- [ ] Passwords hashed with bcrypt
- [ ] No hardcoded secrets
- [ ] HTTPS enforced

## 3. Injection
- [ ] Parameterized queries
- [ ] Input validation
- [ ] No command injection

## 4. Insecure Design
- [ ] Rate limiting present
- [ ] File upload limits
- [ ] Strong password requirements

## 5. Security Misconfiguration
- [ ] Debug mode off
- [ ] Security headers configured
- [ ] No default credentials

## 6. Vulnerable Components
- [ ] Dependencies up to date
- [ ] No known vulnerabilities
- [ ] Regular updates scheduled

## 7. Authentication Failures
- [ ] Multi-factor authentication
- [ ] Session timeout
- [ ] Strong password policy

## 8. Data Integrity Failures
- [ ] No pickle deserialization
- [ ] Code signing
- [ ] Integrity checks

## 9. Logging Failures
- [ ] Security events logged
- [ ] No sensitive data in logs
- [ ] Log monitoring enabled

## 10. Server-Side Request Forgery
- [ ] URL validation
- [ ] Block internal IPs
- [ ] Network segmentation

**Summary**:
- Total vulnerabilities: {{count}}
- Critical: {{count}}
- High: {{count}}
- Medium: {{count}}
- Low: {{count}}

**Remediation plan**: Prioritized list of fixes
```

---

### Example 5: Refactoring Command

**File**: `.claude/commands/refactor.md`

```markdown
---
argument-hint: <file-path>
description: Refactor code to improve quality
allowed-tools: Read, Edit, Bash
model: sonnet
---

Refactor `$1` to improve code quality:

## Step 1: Analyze Current State

Read file and identify:
- Code duplication (DRY violations)
- Long functions (>20 lines)
- Complex logic (cyclomatic complexity)
- Code smells
- SOLID violations

## Step 2: Create Tests (if missing)

\`\`\`bash
pytest --cov=$1 --cov-report=term-missing
\`\`\`

If coverage <80%, add tests before refactoring.

## Step 3: Refactor

Apply improvements:
1. **Extract methods**: Long functions → small, focused functions
2. **Remove duplication**: DRY principle
3. **Simplify conditionals**: Guard clauses, early returns
4. **Improve names**: Descriptive variable/function names
5. **Extract constants**: Replace magic numbers

Follow:
@.claude/methodologies/software/code-quality-standards.md

## Step 4: Verify Tests Still Pass

\`\`\`bash
pytest tests/test_$(basename $1)
\`\`\`

## Step 5: Run Quality Checks

\`\`\`bash
black --check $1
flake8 $1
mypy $1
\`\`\`

## Step 6: Document Changes

Create refactoring summary:
- What was changed
- Why (code smell addressed)
- Before/after comparison
- Test verification
```

---

### Example 6: Workflow Command

**File**: `.claude/commands/feature-complete.md`

```markdown
---
description: Mark feature complete with full checklist
allowed-tools: Read, Bash, Write
model: sonnet
---

Feature completion checklist:

## 1. Code Implementation

- [ ] Feature implemented
- [ ] Code follows standards (@.claude/methodologies/software/code-quality-standards.md)
- [ ] No code smells
- [ ] DRY, SOLID principles followed

## 2. Testing

\`\`\`bash
# Run tests
pytest --cov=. --cov-report=term-missing

# Check coverage
coverage report --fail-under=80
\`\`\`

- [ ] Unit tests present
- [ ] Integration tests present
- [ ] Coverage ≥80%
- [ ] Edge cases tested
- [ ] All tests passing

## 3. Security

\`\`\`bash
# Security scan
bandit -r .
pip-audit
\`\`\`

- [ ] No security vulnerabilities
- [ ] OWASP Top 10 compliant
- [ ] No hardcoded secrets
- [ ] Input validation present

## 4. Documentation

- [ ] Docstrings added
- [ ] README updated
- [ ] CHANGELOG updated
- [ ] API docs generated

## 5. Code Review

- [ ] Self-review completed
- [ ] Peer review requested
- [ ] Feedback addressed

## 6. Git

\`\`\`bash
# Verify clean state
git status

# Create PR
gh pr create --title "feat: ..." --body "..."
\`\`\`

- [ ] Commits follow conventional commits
- [ ] Branch up to date with main
- [ ] Pull request created
- [ ] CI/CD passing

If ALL checkboxes checked: ✅ Feature complete
If ANY unchecked: ❌ Feature incomplete - complete remaining items
```

---

## 🎯 Command Best Practices

1. **Clear descriptions**: Help users understand what command does

2. **Argument hints**: Show expected arguments in autocomplete

3. **Tool restrictions**: Limit tools to minimum needed (security)

4. **Reference standards**: Use @import for consistency

5. **Structured output**: Checklists, reports, clear sections

6. **Error handling**: Validate arguments, provide helpful errors

7. **Documentation**: Comment complex commands, explain purpose

8. **Testing**: Test commands with various arguments

9. **Version control**: Check project commands into git

10. **User-level for personal**: Keep personal workflows in ~/.claude/

---

## 🎯 Common Command Patterns

### Pattern 1: File Analysis

```markdown
---
argument-hint: <file-path>
---

Analyze `$1` for:
- [Analysis criteria]

Read file, run tools, generate report.
```

### Pattern 2: Batch Processing

```markdown
---
description: Process all files matching pattern
---

\`\`\`bash
find . -name "*.py" | while read file; do
  # Process each file
done
\`\`\`
```

### Pattern 3: Checklist Workflow

```markdown
---
description: Complete workflow with validation
---

## Step 1: [Task]
- [ ] Subtask 1
- [ ] Subtask 2

## Step 2: [Task]
[...]

Verify all checkboxes before proceeding.
```

### Pattern 4: Report Generation

```markdown
---
description: Generate structured report
---

\`\`\`bash
# Collect data
[commands]
\`\`\`

## Summary
[Key findings]

## Details
[Detailed analysis]

## Recommendations
[Action items]
```

---

## 🎯 Success Criteria

- [ ] Frontmatter present (if using optional fields)
- [ ] YAML syntax valid
- [ ] Description clear and concise
- [ ] Arguments documented in hint
- [ ] Prompt is actionable
- [ ] File saved to correct location
- [ ] Command tested with arguments
- [ ] Tool restrictions appropriate
- [ ] References load correctly
- [ ] Command discoverable via autocomplete

---

**This skill creates Claude Code slash commands following official specifications.**

**Version**: 1.0.0
**Last Updated**: 2025-10-27
**Source**: [Claude Code Slash Commands Docs](https://docs.claude.com/en/docs/claude-code/slash-commands.md)
