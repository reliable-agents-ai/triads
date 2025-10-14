# The Complete Guide to Claude Code Sub-Agents

**Master specialized AI agents with persistent context and knowledge graphs**

*Based on real-world implementation of a 5-triad system for OSS development*

---

## Table of Contents

1. [What Are Claude Code Sub-Agents?](#what-are-claude-code-sub-agents)
2. [Why Use Sub-Agents?](#why-use-sub-agents)
3. [Sub-Agent Configuration](#sub-agent-configuration)
4. [Agent Organization Patterns](#agent-organization-patterns)
5. [Invoking Sub-Agents](#invoking-sub-agents)
6. [The Triad Pattern](#the-triad-pattern)
7. [Bridge Agents](#bridge-agents)
8. [Real-World Example: 5-Triad OSS Development System](#real-world-example-5-triad-oss-development-system)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

---

## What Are Claude Code Sub-Agents?

**Sub-agents** are specialized AI agents with their own:
- **Identity** (name and purpose)
- **Context window** (separate from main conversation)
- **Tool access** (specific capabilities)
- **Prompt** (detailed instructions for their role)

Think of them as team members, each with expertise in a specific domain.

### How Sub-Agents Work

```
┌─────────────────────────────────────────┐
│  User invokes sub-agent                  │
│  "Start Design: OAuth2 integration"      │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  Claude Code loads agent definition      │
│  from .claude/agents/{name}.md           │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  Agent runs with dedicated context       │
│  (separate from main conversation)       │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  Agent produces output                   │
│  (updates knowledge graphs, files, etc.) │
└─────────────────────────────────────────┘
```

**Key difference from regular prompts**: Sub-agents have:
- Persistent identity across sessions
- Separate context (doesn't pollute main conversation)
- Specialized tool access
- Can be invoked by name or automatically

---

## Why Use Sub-Agents?

### Specialization Over Generalization

**Without sub-agents**:
```
You: Write OAuth2 code, make it secure, test it, document it,
     and make sure it follows our coding standards.

Claude: [Attempts all tasks, context gets mixed, quality varies]
```

**With sub-agents**:
```
You: Start Design: OAuth2 integration
Solution Architect: [Creates detailed ADR with security considerations]

You: Start Implementation: OAuth2 per design
Senior Developer: [Writes code following ADR]
Test Engineer: [Writes comprehensive tests]

You: Start Garden Tending: OAuth2 feature
Pruner: [Refactors for clarity and removes redundancy]
```

### Benefits

**1. Context Separation**
- Each agent has clean context focused on their role
- No context pollution between phases
- Main conversation stays focused on high-level coordination

**2. Reusability**
- Define once, use repeatedly
- Share agents across projects
- Build a library of specialized agents

**3. Quality Through Specialization**
- Each agent is an expert in their domain
- Detailed prompts for specific tasks
- Better outputs than generic "do everything" prompts

**4. Workflow Automation**
- Chain agents together (triads, pipelines)
- Bridge agents preserve context between phases
- Knowledge graphs persist information across sessions

---

## Sub-Agent Configuration

### Required Frontmatter

Sub-agents are defined in Markdown files with YAML frontmatter:

**Location**: `.claude/agents/{name}.md`

**Required fields**:
```yaml
---
name: agent-name
description: Natural language description of what this agent does
---
```

**Optional fields**:
```yaml
---
name: agent-name
description: What this agent does
tools: Read, Write, Edit, Grep, Glob, Bash, WebSearch  # CSV format
model: sonnet  # or opus, haiku, inherit
---
```

### Example: Simple Agent

```markdown
---
name: code-reviewer
description: Expert code reviewer checking for bugs, security issues, and style violations
tools: Read, Grep, Glob
---

# Code Reviewer

## Role

You are an expert code reviewer. Your job is to:
1. Read code files
2. Identify bugs, security issues, style violations
3. Provide actionable feedback with specific line numbers

## Process

1. **Use Read tool** to examine files
2. **Use Grep** to search for patterns (SQL injection risks, etc.)
3. **Report findings** with file:line citations

## Output Format

```markdown
## Code Review Results

### Critical Issues
- **file.py:42**: SQL injection vulnerability - use parameterized queries

### Style Issues
- **file.py:15**: Line too long (120 chars, limit 100)
```

Your reviews should be thorough, specific, and actionable.
```

### Example: Complex Agent with Custom Fields

```markdown
---
name: solution-architect
description: Design technical solutions, evaluate alternatives, create ADRs
triad: design
is_bridge: false
tools: Read, Grep, Glob, Write
model: sonnet
---

# Solution Architect

[Detailed prompt with examples, constitutional principles, etc.]
```

**Custom fields** (like `triad`, `is_bridge`) are preserved but not used by Claude Code directly - they're for your organization.

---

## Agent Organization Patterns

### Flat Structure

**Simple projects**:
```
.claude/agents/
├── code-reviewer.md
├── test-writer.md
├── doc-updater.md
└── release-manager.md
```

**Usage**: Direct invocation by name
```
Invoke code-reviewer to review src/auth.py
```

### Hierarchical Structure

**Complex projects with workflows**:
```
.claude/agents/
├── idea-validation/
│   ├── research-analyst.md
│   ├── community-researcher.md
│   └── validation-synthesizer.md
│
├── design/
│   ├── solution-architect.md
│   └── design-bridge.md
│
├── implementation/
│   ├── senior-developer.md
│   └── test-engineer.md
│
└── deployment/
    ├── release-manager.md
    └── documentation-updater.md
```

**Usage**: Workflow-based invocation
```
Start Idea Validation: Add OAuth2 support
Start Design: OAuth2 integration per validated requirements
Start Implementation: OAuth2 per design specifications
```

### Hybrid Structure

```
.claude/agents/
├── core/                    # General-purpose agents
│   ├── code-reviewer.md
│   └── doc-updater.md
│
├── workflow/                # Workflow-specific agents
│   ├── discovery/
│   ├── design/
│   └── implementation/
│
└── system/                  # Meta-agents (quality, monitoring)
    ├── research-agent.md
    └── verification-agent.md
```

---

## Invoking Sub-Agents

### Explicit Invocation

**Direct call**:
```
Invoke {agent-name} to {task}
```

**Examples**:
```
Invoke code-reviewer to review src/auth.py
Invoke test-writer to add tests for OAuth2 module
Invoke release-manager to create v1.2.0 release
```

### Workflow Invocation

**Triad-based**:
```
Start {Triad}: {task description}
```

**Examples**:
```
Start Idea Validation: Add graph visualization
Start Design: Graph visualization per validated requirements
Start Implementation: Visualization dashboard per design
```

### Automatic Invocation

Agents can be configured to trigger automatically based on:
- File patterns (e.g., test-writer on `.py` file changes)
- Keywords (e.g., security-analyzer on "security review")
- Hooks (e.g., pre-commit, post-tool-use)

*(Configured via hooks or MCP - see Hooks Guide for details)*

---

## The Triad Pattern

### What is a Triad?

A **triad** is a group of 3 agents working together on a phase of work:
1. **Agent A**: Gathers information
2. **Agent B**: Processes and refines
3. **Agent C** (Bridge): Synthesizes and prepares handoff to next triad

**Why 3?**
- Simmel's sociological research: Groups of 3 are optimal
- Provides mediation, tie-breaking, and accountability
- Avoids single point of failure (1 agent) or decision gridlock (2 agents)

### Triad Structure

```
┌─────────────────────────────────────────────────┐
│              Triad: Design Phase                 │
│                                                  │
│  ┌─────────────┐   ┌─────────────┐             │
│  │  Agent 1    │──▶│  Agent 2    │             │
│  │  (Gather)   │   │  (Refine)   │             │
│  └─────────────┘   └──────┬──────┘             │
│                            │                     │
│                            ▼                     │
│                     ┌─────────────┐             │
│                     │  Agent 3    │ ────────┐   │
│                     │  (Bridge)   │         │   │
│                     └─────────────┘         │   │
└─────────────────────────────────────────────┼───┘
                                              │
                                              │ (Context compressed)
                                              ▼
                                    ┌───────────────────┐
                                    │  Next Triad       │
                                    └───────────────────┘
```

### Example Triad: Implementation

**Triad Members**:
```markdown
1. Design Bridge (bridge from previous triad)
   - Loads design specifications
   - Presents ADR to development team

2. Senior Developer
   - Writes production code
   - Follows design patterns
   - Implements core functionality

3. Test Engineer
   - Writes comprehensive tests
   - Verifies coverage >80%
   - Ensures quality gates pass
```

**Sequential Execution**:
```
Start Implementation: OAuth2 integration

→ Design Bridge loads ADR from Design triad
→ Senior Developer writes code per ADR
→ Test Engineer writes and runs tests
→ Knowledge graph updated with implementation details
```

---

## Bridge Agents

### What Are Bridge Agents?

**Bridge agents** are special agents that:
1. **Belong to two triads** (source and target)
2. **Compress context** from source triad (top-20 most important items)
3. **Hand off context** to target triad
4. **Preserve information** across phase boundaries

### Why Bridges?

**Problem**: Context loss between phases
```
Design Phase:
- Created detailed ADR
- Security considerations documented
- 50+ design decisions made

Implementation Phase (without bridge):
- "What was the security requirement again?"
- "Why did we choose approach X?"
- Lost context, re-doing design work
```

**Solution**: Bridge agents
```
Design Phase → Design Bridge Agent
                ↓
                Compresses top-20 critical nodes:
                - ADR document
                - Security requirements
                - File modification plan
                - Key design rationale
                ↓
Implementation Phase receives compressed context
- Has everything needed to implement
- No re-work, no context loss
```

### Bridge Agent Structure

```yaml
---
name: design-bridge
description: Validate design completeness, compress design decisions and ADRs, and bridge context to Implementation triad
triad: design
is_bridge: true
bridge_connects: "Design & Architecture → Implementation"
---

# Design Bridge (Bridge Agent)

## Role

You are a bridge agent connecting Design & Architecture to Implementation.

## Responsibilities

1. **Validate completeness**:
   - ADR present and complete
   - Security addressed
   - Test strategy defined

2. **Compress context**:
   - Select top-20 nodes from Design graph
   - Priority: ADR (1.0), Security (0.9), Files to modify (0.9)
   - Save to `.claude/graphs/bridge_design_to_implementation.json`

3. **Prepare handoff**:
   - Summarize key decisions for Implementation team
   - Highlight critical requirements
   - Flag any uncertainties

## Context Compression

Use this formula to score node importance:
```
importance = (
    confidence * 0.3 +
    node_degree * 0.3 +
    recency * 0.2 +
    type_priority * 0.2
)
```

Keep top-20 nodes + their 1-hop neighbors.
```

### Bridge Flow Example

**Full Workflow**:
```
1. Idea Validation Triad
   Agent 1: Research Analyst
   Agent 2: Community Researcher
   Agent 3: Validation Synthesizer (BRIDGE)
            ↓ [compresses: validated requirements, priority score]

2. Design & Architecture Triad
   Agent 1: Validation Synthesizer (receives compressed context)
   Agent 2: Solution Architect
   Agent 3: Design Bridge (BRIDGE)
            ↓ [compresses: ADR, security, implementation plan]

3. Implementation Triad
   Agent 1: Design Bridge (receives compressed context)
   Agent 2: Senior Developer
   Agent 3: Test Engineer
```

---

## Real-World Example: 5-Triad OSS Development System

### System Overview

This example shows a complete OSS development workflow using triads and bridge agents.

**5 Triads**:
1. Idea Validation
2. Design & Architecture
3. Implementation
4. Garden Tending (quality improvement)
5. Deployment & Release

### Triad 1: Idea Validation

**Purpose**: Research and validate feature ideas before starting work

**Agents**:
```markdown
# research-analyst.md
---
name: research-analyst
description: Research ideas by gathering evidence from web research, codebase analysis, and industry best practices
tools: WebSearch, WebFetch, Read, Grep, Glob
---

Searches for:
- Similar implementations in other projects
- Industry best practices
- Technical feasibility
- Existing patterns in codebase

# community-researcher.md
---
name: community-researcher
description: Assess community need and gather user feedback by analyzing GitHub issues, discussions, and comparable projects
tools: WebSearch, WebFetch, Read, Bash
---

Analyzes:
- GitHub issues and discussions
- User requests and upvotes
- Comparable projects
- Community interest level

# validation-synthesizer.md (BRIDGE)
---
name: validation-synthesizer
description: Synthesize research findings, calculate priority scores, make PROCEED/DEFER/REJECT decisions, and bridge context to Design triad
is_bridge: true
---

Decides:
- PROCEED (high priority, implement now)
- DEFER (good idea, later)
- REJECT (not aligned with goals)

Calculates: priority = (impact × feasibility) / effort
Compresses: Top-20 nodes → Design triad
```

**Usage**:
```
Start Idea Validation: Add visual graph explorer

→ Research Analyst: Finds similar projects, technical approaches
→ Community Researcher: Checks user demand, community interest
→ Validation Synthesizer: Calculates priority score, decides PROCEED
→ Compressed context saved for Design triad
```

### Triad 2: Design & Architecture

**Purpose**: Create detailed technical design with ADRs

**Agents**:
```markdown
# solution-architect.md
---
name: solution-architect
description: Design technical solutions, evaluate alternatives, create ADRs (Architecture Decision Records), and plan implementation approach
tools: Read, Grep, Glob, Write
---

Creates:
- Architecture Decision Record (ADR)
- File modification plan
- Security considerations
- Test strategy

Evaluates:
- 2-3 alternative approaches
- Trade-offs for each
- Why chosen approach is optimal

# design-bridge.md (BRIDGE)
---
name: design-bridge
description: Validate design completeness, compress design decisions and ADRs, and bridge context to Implementation triad
is_bridge: true
---

Validates:
- ADR complete
- Security addressed
- Test strategy defined

Compresses: ADR + implementation plan → Implementation triad
```

**Usage**:
```
Start Design: Visual graph explorer per validated requirements

→ Validation Synthesizer (from Idea Validation): Loads requirements
→ Solution Architect: Creates ADR with 3 alternatives, security notes
→ Design Bridge: Validates completeness, compresses design
→ Compressed context saved for Implementation triad
```

### Triad 3: Implementation

**Purpose**: Write code and tests

**Agents**:
```markdown
# senior-developer.md
---
name: senior-developer
description: Write production code according to ADR specifications, follow existing patterns, implement core functionality with safe refactoring practices
tools: Read, Write, Edit, Grep, Glob, Bash
---

Implements:
- Code per ADR specifications
- Following existing patterns (uses Grep to find)
- Safe refactoring (5 rules: tests first, one change at a time, verify continuously, commit incrementally)

# test-engineer.md
---
name: test-engineer
description: Write comprehensive tests, verify coverage >80%, ensure quality gates pass, test edge cases and security requirements
tools: Read, Write, Edit, Bash, Grep, Glob
---

Tests:
- Unit tests for core logic
- Integration tests for APIs
- Edge cases (empty input, boundaries)
- Security tests (per ADR security requirements)
- Coverage >80% for new code
```

**Usage**:
```
Start Implementation: Graph explorer per design

→ Design Bridge (from Design): Loads ADR and implementation plan
→ Senior Developer: Writes code following ADR
→ Test Engineer: Writes tests, verifies coverage
→ Implementation complete, ready for Garden Tending
```

### Triad 4: Garden Tending (Unique)

**Purpose**: Continuous improvement, refactoring, debt management

**Philosophy**: Cultivate, Prune, Preserve, Weed

**Agents**:
```markdown
# cultivator.md
---
name: cultivator
description: Identify growth opportunities, beneficial patterns, and consolidation opportunities to improve code quality
tools: Read, Grep, Glob, Bash
---

Cultivates:
- New patterns worth expanding
- Consolidation opportunities (duplicate code)
- Single source of truth improvements

# pruner.md
---
name: pruner
description: Remove redundancy, simplify complexity, eliminate duplicate code following 5 Safe Refactoring Rules
tools: Read, Edit, Grep, Glob, Bash
---

Prunes:
- Redundant code
- Unnecessary complexity
- Duplicate implementations

Weeds:
- Confusing naming
- Circular dependencies
- Hidden behaviors

Safe Refactoring Rules:
1. Never refactor without tests
2. Make it work before making it better
3. One change at a time
4. Verify after each change
5. Commit before and after

# gardener-bridge.md (UNIQUE DUAL-OUTPUT BRIDGE)
---
name: gardener-bridge
description: Unique dual-output bridge - forward quality-checked code to Deployment AND feed improvement patterns back to Design for continuous learning
is_bridge: true
bridge_connects: "Garden Tending → Deployment (forward) + Design (feedback)"
---

Dual output:
1. Forward to Deployment: Quality-checked code, test results
2. Feedback to Design: Improvement patterns discovered, lessons learned

Creates:
- `.claude/graphs/bridge_garden_to_deployment.json` (forward)
- `.claude/graphs/feedback_garden_to_design.json` (feedback loop!)
```

**Usage**:
```
Start Garden Tending: post-feature cleanup for graph explorer

→ Cultivator: Identifies consolidation opportunities
→ Pruner: Refactors safely (tests first, one change at a time)
→ Gardener Bridge:
   - Approves for deployment
   - Sends improvement patterns back to Design triad for future use
```

**Unique Feature**: Gardener Bridge creates a **feedback loop** - lessons from implementation inform future designs!

### Triad 5: Deployment & Release

**Purpose**: Release to production, update docs

**Agents**:
```markdown
# release-manager.md
---
name: release-manager
description: Create GitHub releases, write changelogs, bump versions, verify installation, tag commits
tools: Read, Write, Edit, Bash, Grep, Glob
---

Releases:
- Bump version in all files
- Write user-facing changelog
- Create GitHub release with `gh release create`
- Tag commit and push
- Verify installation in clean environment

# documentation-updater.md
---
name: documentation-updater
description: Update README, installation guides, CHANGELOG, ensure docs match new version, verify links work
tools: Read, Write, Edit, Grep, Glob
---

Updates:
- README with new version and features
- CHANGELOG with release notes
- Installation guides if needed
- Verifies links still work (curl -I)
```

**Usage**:
```
Start Deployment: v1.5.0

→ Gardener Bridge (from Garden Tending): Loads quality-checked code
→ Release Manager: Creates GitHub release, bumps version
→ Documentation Updater: Updates docs and changelog
→ Release complete!
```

### Complete Feature Workflow

```bash
# 1. Validate idea
Start Idea Validation: Add graph visualization dashboard

# Output: PROCEED (priority: 8.5/10)
# Bridge: Compressed requirements → Design triad

# 2. Design solution
Start Design: Graph visualization per validated requirements

# Output: ADR created with 3 alternatives, security considerations
# Bridge: Compressed design → Implementation triad

# 3. Implement
Start Implementation: Visualization dashboard per design

# Output: Code written, tests passing (coverage: 87%)
# Flows to: Garden Tending

# 4. Quality improvement
Start Garden Tending: post-feature cleanup for visualization

# Output:
#  - Forward: Deployment-ready code
#  - Feedback: "Consider D3.js abstraction for future visualizations"

# 5. Deploy
Start Deployment: v1.5.0

# Output: GitHub release created, docs updated
# Complete!
```

### Knowledge Graph Integration

Each triad maintains its own knowledge graph:

```
.claude/graphs/
├── idea-validation_graph.json     # Requirements, research findings
├── design_graph.json               # ADRs, design decisions
├── implementation_graph.json       # Code changes, test results
├── garden-tending_graph.json       # Quality improvements
├── deployment_graph.json           # Release metadata
│
└── bridge_*.json                   # Compressed context handoffs
    ├── bridge_idea_to_design.json
    ├── bridge_design_to_implementation.json
    ├── bridge_garden_to_deployment.json
    └── feedback_garden_to_design.json  # Unique feedback loop!
```

Agents update graphs using `[GRAPH_UPDATE]` blocks in their output.

---

## Best Practices

### 1. Clear Agent Identity

**❌ Bad**:
```yaml
---
name: helper
description: Helps with stuff
---
```

**✅ Good**:
```yaml
---
name: security-auditor
description: Review code for security vulnerabilities including SQL injection, XSS, authentication bypass, and insecure dependencies
tools: Read, Grep, Bash
---
```

### 2. Specific Tool Assignment

**❌ Bad**:
```yaml
tools: Read, Write, Edit, Bash, WebSearch, Grep, Glob  # Everything
```

**✅ Good**:
```yaml
# For analyst agent
tools: Read, WebSearch, Grep  # Read-only, research focus

# For developer agent
tools: Read, Write, Edit, Bash  # Code modification

# For bridge agent
tools: # None - synthesis only
```

### 3. Detailed Prompts with Examples

**❌ Bad**:
```markdown
You are a code reviewer. Review code.
```

**✅ Good**:
```markdown
# Code Reviewer

## Role
Expert code reviewer checking for bugs, security, and style.

## Process
1. Use Read tool to examine files
2. Use Grep to search for patterns
3. Report findings with file:line citations

## Example Output

### Critical Issues
- **auth.py:42**: SQL injection - use parameterized queries
  ```python
  # Bad
  query = f"SELECT * FROM users WHERE id = {user_id}"

  # Good
  query = "SELECT * FROM users WHERE id = ?"
  cursor.execute(query, (user_id,))
  ```

### Style Issues
- **utils.py:15**: Line too long (120 chars, limit 100)
```

### 4. Constitutional Principles

Embed quality standards in agent prompts:

```markdown
## Constitutional Principles

This agent follows TRUST framework:

**T**horoughness: Research 2+ sources before making claims
**R**equire evidence: All claims must cite file:line or URLs
**U**ncertainty escalation: If confidence < 85%, create Uncertainty node
**S**how all work: Document reasoning and alternatives
**T**est assumptions: Validate before proceeding
```

### 5. Knowledge Graph Integration

Have agents update persistent memory:

```markdown
## Knowledge Graph Updates

After completing work, output:

\`\`\`markdown
[GRAPH_UPDATE]
type: add_node
node_id: security_audit_auth_module
node_type: Finding
label: Security Audit Results - Auth Module
description: Found 2 critical issues, 3 warnings
issues: ["SQL injection in login", "Weak password hashing"]
confidence: 0.95
evidence: "auth.py:42, auth.py:67"
created_by: security-auditor
[/GRAPH_UPDATE]
\`\`\`
```

### 6. Progressive Disclosure

Start simple, add complexity as needed:

**Phase 1: Basic agent**
```yaml
---
name: code-reviewer
description: Review code for bugs and style issues
tools: Read, Grep
---
```

**Phase 2: Add structure**
Organize into triads, add bridges

**Phase 3: Add quality**
Knowledge graphs, constitutional principles, feedback loops

---

## Troubleshooting

### Agents Not Appearing

**Symptom**: Agent defined but not showing in Claude Code

**Checks**:
```bash
# 1. Verify file location
ls .claude/agents/*.md

# 2. Check frontmatter format
cat .claude/agents/my-agent.md
# Must have:
# name: agent-name
# description: What it does

# 3. Verify YAML syntax
python3 << 'EOF'
import yaml
with open('.claude/agents/my-agent.md') as f:
    content = f.read()
    frontmatter = content.split('---')[1]
    print(yaml.safe_load(frontmatter))
EOF

# 4. Restart Claude Code
# Agents are loaded at startup
```

**Common Issues**:
- ❌ `role:` instead of `name:`
- ❌ Missing `description:`
- ❌ Tools in array format `[Read, Write]` instead of CSV `Read, Write`
- ❌ Invalid YAML (indentation errors)

### Agent Not Receiving Context

**Symptom**: Agent seems to lack information from previous agents

**Solutions**:

1. **Use bridge agents**:
```markdown
# Bridge agent loads context from previous triad
# See Bridge Agents section above
```

2. **Use knowledge graphs**:
```markdown
# Agents write to graphs, next agent reads
[GRAPH_UPDATE]
type: add_node
node_id: oauth2_design
node_type: Decision
label: OAuth2 ADR
description: Detailed design with security considerations
[/GRAPH_UPDATE]
```

3. **Explicit handoff in prompts**:
```markdown
## Context from Previous Agent

The Design Bridge has prepared the following context:
- ADR for OAuth2 integration
- Security requirements: JWT with RS256
- Files to modify: src/auth/oauth.py, tests/test_oauth.py
```

### Agent Producing Poor Quality Output

**Symptom**: Agent output is generic, lacks detail, or misses requirements

**Solutions**:

1. **Add specific examples** in agent prompt
2. **Include constitutional checkpoints**:
```markdown
## Pre-Output Checklist

Before producing output, verify:
- [ ] All claims have evidence (file:line or URLs)
- [ ] Confidence score calculated (formula shown)
- [ ] Alternatives considered (min 2)
- [ ] Assumptions documented and validated
```

3. **Use quality hooks**:
```json
{
  "hooks": {
    "Stop": [{
      "hooks": [{
        "type": "command",
        "command": "python3 .claude/hooks/validate_output.py"
      }]
    }]
  }
}
```

4. **Refine agent prompt iteratively**:
   - Start with basic version
   - Review agent output
   - Add specific examples of good/bad output
   - Add constraints and requirements
   - Test again

### Bridge Agent Not Compressing Context

**Symptom**: Next triad seems to have too much or too little context

**Solutions**:

1. **Check compression logic**:
```python
# In bridge agent prompt, specify formula:
importance = (
    confidence * 0.3 +
    node_degree * 0.3 +
    recency * 0.2 +
    type_priority * 0.2
)

# Keep top-20 nodes
```

2. **Adjust priority weights**:
```python
# If losing critical info, increase type_priority weight
type_priority_weight = 0.4  # Was 0.2

# If too much detail, increase recency weight
recency_weight = 0.3  # Was 0.2
```

3. **Verify bridge file creation**:
```bash
ls .claude/graphs/bridge_*.json
cat .claude/graphs/bridge_design_to_implementation.json
```

### Circular Dependencies Between Agents

**Symptom**: Agent A calls Agent B calls Agent A → infinite loop

**Solution**: Design with directed flow:
```
Triad 1 → Bridge → Triad 2 → Bridge → Triad 3

✅ Good: Linear flow
❌ Bad: Triad 2 calling back to Triad 1
```

Exception: Feedback loops (like Gardener Bridge) should:
- Be asynchronous (don't block current flow)
- Go to staging area for next session
- Not trigger immediate re-execution

---

## Further Reading

- **[Hooks Guide](./CLAUDE_CODE_HOOKS_GUIDE.md)** - Automate agent invocation
- **[Usage Guide](./USAGE.md)** - Using the Triad Generator
- **[Architecture](./ARCHITECTURE.md)** - System design details
- **[Claude Code Docs](https://docs.claude.com/en/docs/claude-code/sub-agents)** - Official documentation

---

## Real-World Resources

**Example System**: This project uses the 5-triad system documented above.

**View agents**:
```bash
ls .claude/agents/*/
cat .claude/agents/garden-tending/pruner.md
```

**View workflow**:
```bash
cat .claude/WORKFLOW.md
```

**View configuration**:
```bash
cat .claude/settings.json
```

**Try it**:
```bash
Start Idea Validation: [your feature idea]
```

---

**Questions? Issues?**

- [GitHub Issues](https://github.com/reliable-agents-ai/triads/issues)
- [GitHub Discussions](https://github.com/reliable-agents-ai/triads/discussions)
- [Claude Code Community](https://claude.ai/community)
