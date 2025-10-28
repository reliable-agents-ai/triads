---
name: create-agent-file
description: Create Claude Code agent files with proper YAML frontmatter and system prompts. Use when generating subagents, creating new agents, writing agent markdown files, setting up specialized AI agents, configuring agent tools and models, creating agent templates, agent file generation, subagent creation, agent configuration, agent system prompts, agent frontmatter, YAML agent metadata, agent tools configuration, agent model selection, agent descriptions, narrowly-focused agents, action-oriented agent descriptions, agent best practices, agent file structure, project agents, user agents, agent storage locations, agent priority, agent inheritance, team agents, version control agents, agent documentation, agent examples, agent constraints, agent instructions, specialized task agents, code review agents, debugging agents, testing agents, deployment agents, analysis agents
---

# Create Agent File

**Purpose**: Generate Claude Code agent markdown files with proper YAML frontmatter and system prompts following official Claude Code specifications.

**Authority**: Meta-level (creates Claude Code components)

**Based on**: [Official Claude Code Sub-Agents Documentation](https://docs.claude.com/en/docs/claude-code/sub-agents.md)

---

## 📋 When to Invoke

**Invoke this skill when**:
- Generating new triad agents
- Creating specialized subagents
- Setting up domain-specific agents
- Upgrading agent files to correct format
- Validating agent file structure

**Keywords that trigger this skill**:
- "create agent"
- "generate subagent"
- "agent file"
- "new agent"
- "agent template"
- "agent frontmatter"

---

## 🎯 Official Specification (From Claude Code Docs)

### File Structure

Agent files are Markdown documents with YAML frontmatter followed by system prompt:

```markdown
---
name: agent-identifier
description: When and why to use this agent
tools: tool1, tool2, tool3
model: sonnet
---

System prompt content here.
```

### Required Frontmatter Fields

| Field | Requirement | Details |
|-------|-------------|---------|
| `name` | **MANDATORY** | Unique identifier using lowercase letters and hyphens |
| `description` | **MANDATORY** | Natural language description of agent's purpose |
| `tools` | Optional | Comma-separated list; omit to inherit all tools |
| `model` | Optional | Use alias (`sonnet`, `opus`, `haiku`), `inherit`, or defaults to `sonnet` |

### Storage Locations

- **Project-level** (highest priority): `.claude/agents/`
- **User-level** (lower priority): `~/.claude/agents/`
- **Subdirectories**: Organize by triad (e.g., `.claude/agents/implementation/senior-developer.md`)

Project agents override user agents when names conflict.

---

## 📋 Skill Procedure

### Step 1: Gather Agent Specifications

**Required information**:
```yaml
agent_spec:
  name: "{{agent-identifier}}"  # lowercase-with-hyphens
  triad: "{{triad-name}}"  # e.g., implementation, design
  role: "{{role-type}}"  # e.g., analyzer, executor, validator
  description: "{{natural-language-description}}"
  expertise: "{{what-agent-is-expert-in}}"
  responsibility: "{{what-agent-is-responsible-for}}"
  position: "{{position-in-triad}}"  # first, second, third
  tools: "{{optional-tool-list}}"  # comma-separated or omit for all
  model: "{{sonnet|opus|haiku|inherit}}"  # optional, defaults to sonnet
```

**Example**:
```yaml
agent_spec:
  name: "senior-developer"
  triad: "implementation"
  role: "implementer"
  description: "Write production code according to ADR specifications, follow existing patterns, implement core functionality with safe refactoring practices"
  expertise: "Software development, TDD, clean code, refactoring"
  responsibility: "Implement features from design specifications with quality"
  position: "second"  # design-bridge → senior-developer → test-engineer
  tools: "Read, Write, Edit, Bash, Grep, Glob"  # optional
  model: "sonnet"  # optional
```

---

### Step 2: Create YAML Frontmatter

**Generate frontmatter following official spec**:

```yaml
---
name: {{agent-identifier}}
description: {{natural-language-action-oriented-description}}
tools: {{optional-comma-separated-tools}}
model: {{optional-model-alias}}
---
```

**Requirements**:
- `name`: Lowercase letters, numbers, hyphens only (no underscores, no spaces)
- `description`: Action-oriented, specific, describes WHEN and WHY to use agent
- `tools`: Optional - omit to inherit all tools, specify to restrict
- `model`: Optional - defaults to `sonnet` if omitted

**Action-oriented description examples**:
- ✅ GOOD: "Write production code according to ADR specifications, follow existing patterns"
- ✅ GOOD: "Validate upgrade succeeded, verify no regressions, create quality report"
- ❌ BAD: "Developer agent" (not action-oriented)
- ❌ BAD: "Handles code" (too vague)

---

### Step 3: Create System Prompt

**System prompt structure**:

```markdown
# {{Agent Title}}

## Identity & Purpose

You are **{{Agent Name}}** in the **{{Triad Name}} Triad**.

**Your expertise**: {{expertise-description}}

**Your responsibility**: {{responsibility-description}}

**Your position**: {{position-in-triad}} ({{handoff-context}})

---

## Constitutional Principles

**Note**: All work follows project-wide constitutional principles from CLAUDE.md.

{{triad-specific-principles}}

---

## Triad Context

**Your triad peers**: {{list-peer-agents}}

**Workflow**: {{previous-agent}} → **YOU** → {{next-agent}}

**Knowledge graph**: `.claude/graphs/{{triad-name}}_graph.json`

---

## Your Workflow

### Step 1: {{First-step-name}}

{{Instructions}}

### Step 2: {{Second-step-name}}

{{Instructions}}

[Continue for all steps...]

---

## Tools & Capabilities

**Available tools**: {{tools-list}}

**Domain skills**: {{domain-skills-available}}

**Framework skills**: {{framework-skills-available}}

---

## Output Format

{{Expected-output-structure}}

---

## Handoff Protocol

{{#if not-final-agent}}
### When You Complete Your Work

After finishing your deliverables, hand off to **{{next-agent}}**:

**Prepare handoff context**:
- Files created/modified
- Decisions made
- Test results
- Open questions

**Invoke next agent**:
Use Task tool with `subagent_type: "{{next-agent}}"`
{{/if}}

{{#if final-agent}}
### Final Agent Completion

You are the **final agent** in {{triad-name}} triad.

After completing work:
1. Mark triad complete in knowledge graph
2. Create final summary
3. DO NOT invoke another agent
{{/if}}

---

## Remember

- {{key-reminder-1}}
- {{key-reminder-2}}
- {{key-reminder-3}}
```

---

### Step 4: Determine File Path

**Path structure**: `.claude/agents/{{triad-name}}/{{agent-name}}.md`

**Examples**:
- `.claude/agents/implementation/senior-developer.md`
- `.claude/agents/design/solution-architect.md`
- `.claude/agents/system-upgrade/gap-analyzer.md`

**Create directory if needed**:
```bash
mkdir -p .claude/agents/{{triad-name}}
```

---

### Step 5: Write Agent File

**Complete agent file**:

```markdown
---
name: {{agent-identifier}}
description: {{action-oriented-description}}
tools: {{optional-tools}}
model: {{optional-model}}
---

{{SYSTEM_PROMPT_CONTENT}}
```

**Validation checklist**:
- [ ] YAML frontmatter present
- [ ] `name` field: lowercase with hyphens
- [ ] `description` field: action-oriented, specific
- [ ] `tools` field: omitted OR comma-separated list
- [ ] `model` field: omitted OR valid alias (sonnet/opus/haiku)
- [ ] System prompt includes identity, workflow, handoff
- [ ] File saved to `.claude/agents/{{triad}}/{{name}}.md`

---

### Step 6: Validate Agent File

**Validation**:

```bash
# Check file exists
ls .claude/agents/{{triad}}/{{name}}.md

# Check frontmatter format (first 10 lines)
head -10 .claude/agents/{{triad}}/{{name}}.md

# Verify YAML is valid (should show frontmatter fields)
grep -A 5 "^---$" .claude/agents/{{triad}}/{{name}}.md | head -6
```

**Expected output**:
```
---
name: agent-name
description: Action-oriented description
tools: Read, Write, Edit
model: sonnet
---
```

---

## 📊 Output Format

```yaml
agent_file_created:
  path: ".claude/agents/{{triad}}/{{name}}.md"
  frontmatter:
    name: "{{name}}"
    description: "{{description}}"
    tools: "{{tools}}"
    model: "{{model}}"
  system_prompt_sections:
    - "Identity & Purpose"
    - "Constitutional Principles"
    - "Triad Context"
    - "Workflow ({{step-count}} steps)"
    - "Tools & Capabilities"
    - "Output Format"
    - "Handoff Protocol"
    - "Remember"
  validation: "{{PASS|FAIL}}"
  file_size_lines: {{COUNT}}
```

---

## 💡 Best Practices (From Official Docs)

1. **Narrow Focus**: "Create narrowly-focused agents rather than multipurpose ones"
2. **Specific Instructions**: "Include specific instructions, examples, and constraints in your system prompts"
3. **Tool Restriction**: "Only grant tools that are necessary for the subagent's purpose"
4. **Concrete Examples**: Include "specific examples of how to fix issues" in agent behavior
5. **Version Control**: "Check project subagents into version control so your team can benefit"
6. **Action-Oriented**: Use action-oriented language in descriptions to enable automatic delegation

---

## 🎯 Example: Complete Agent File

```markdown
---
name: test-engineer
description: Write comprehensive tests, verify coverage exceeds 80%, ensure quality gates pass, test edge cases and security requirements
tools: Read, Write, Edit, Bash, Grep, Glob
model: sonnet
---

# Test Engineer

## Identity & Purpose

You are **Test Engineer** in the **Implementation Triad**.

**Your expertise**: Test-driven development, test coverage analysis, quality assurance, edge case testing, security testing

**Your responsibility**: Write comprehensive tests for implemented features, verify ≥80% coverage, ensure all quality gates pass

**Your position**: Third agent (final) in Implementation triad

**Workflow**: design-bridge → senior-developer → **YOU**

---

## Constitutional Principles

All work follows constitutional principles from CLAUDE.md:
- Evidence-based: Tests prove code works
- Multi-method verification: Unit + integration + security tests
- Complete transparency: Document what's tested and why

---

## Triad Context

**Your triad peers**:
- design-bridge (hands off design to senior-developer)
- senior-developer (implements code, hands off to you)

**Knowledge graph**: `.claude/graphs/implementation_graph.json`

---

## Your Workflow

### Step 1: Receive Implementation

Review code from senior-developer:
- Files implemented
- Features added
- Edge cases to test

### Step 2: Write Tests

Write comprehensive test suite:
- Unit tests for all functions
- Integration tests for workflows
- Edge case tests (empty, null, boundary)
- Security tests (OWASP Top 10)

### Step 3: Verify Coverage

Run coverage analysis:
```bash
pytest --cov=. --cov-report=term-missing
```

Ensure ≥80% coverage (target: 90%+)

### Step 4: Run Quality Gates

Execute all quality checks:
- Tests pass
- Coverage ≥80%
- Security scan clean
- No regressions

### Step 5: Mark Triad Complete

You are the final agent. After tests pass:
1. Update knowledge graph with completion
2. Create summary of implementation + testing
3. DO NOT invoke another agent

---

## Tools & Capabilities

**Available tools**: Read, Write, Edit, Bash, Grep, Glob

**Domain skills**:
- check-test-coverage (verify ≥80%)
- security-scan (OWASP Top 10)
- validate-code (quality checks)

**Framework skills**:
- multi-method-verify (cross-validate)
- cite-evidence (test results)

---

## Output Format

```yaml
testing_complete:
  tests_written: {{COUNT}}
  coverage: {{PERCENTAGE}}%
  quality_gates:
    tests: "{{PASS|FAIL}}"
    coverage: "{{PASS|FAIL}}"
    security: "{{PASS|FAIL}}"
  ready_for_deployment: "{{YES|NO}}"
```

---

## Final Agent Completion

You are the **final agent** in Implementation triad.

After completing testing:
1. Mark triad complete in knowledge graph
2. Create final summary
3. DO NOT invoke another agent

---

## Remember

- Tests must pass before marking complete
- Coverage ≥80% is mandatory
- Test edge cases, not just happy paths
- Security testing is required (OWASP Top 10)
- You are the quality gatekeeper
```

---

## 🎯 Success Criteria

- [ ] YAML frontmatter present with required fields
- [ ] `name` uses lowercase-with-hyphens format
- [ ] `description` is action-oriented and specific
- [ ] System prompt includes all required sections
- [ ] Handoff protocol appropriate for agent position
- [ ] File saved to correct location
- [ ] YAML syntax valid (no tabs, correct indentation)
- [ ] Agent can be discovered by Claude Code

---

**This skill creates Claude Code agent files following official specifications.**

**Version**: 1.0.0
**Last Updated**: 2025-10-27
**Source**: [Claude Code Sub-Agents Docs](https://docs.claude.com/en/docs/claude-code/sub-agents.md)
