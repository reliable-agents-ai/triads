# Triad System Workflow Guide

**For: Open Source Meta-AI Development**

This guide explains how to use your custom 5-triad system for evolving the Triad Generator project.

---

## Table of Contents

1. [Overview](#overview)
2. [The 5 Triads](#the-5-triads)
3. [How to Invoke Triads](#how-to-invoke-triads)
4. [Complete Workflow Examples](#complete-workflow-examples)
5. [Knowledge Graphs](#knowledge-graphs)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

---

## Overview

Your system consists of **5 triads** (15 agents total) that guide work from idea through deployment:

```
┌──────────────────────────────────────────────────────────────────┐
│                       IDEA VALIDATION                             │
│  Research Analyst → Community Researcher → Validation Synthesizer │
└────────────────────────────┬─────────────────────────────────────┘
                             ↓ (bridge)
┌──────────────────────────────────────────────────────────────────┐
│                    DESIGN & ARCHITECTURE                          │
│  Validation Synthesizer → Solution Architect → Design Bridge      │
└────────────────────────────┬─────────────────────────────────────┘
                             ↓ (bridge)
┌──────────────────────────────────────────────────────────────────┐
│                       IMPLEMENTATION                              │
│       Design Bridge → Senior Developer → Test Engineer            │
└────────────────────────────┬─────────────────────────────────────┘
                             ↓
┌──────────────────────────────────────────────────────────────────┐
│                      GARDEN TENDING                               │
│        Cultivator → Pruner → Gardener Bridge                      │
│                           ↓           ↓                           │
│                  (to Deployment)  (feedback to Design)            │
└────────────────────────────┬─────────────────────────────────────┘
                             ↓ (bridge)
┌──────────────────────────────────────────────────────────────────┐
│                   DEPLOYMENT & RELEASE                            │
│  Gardener Bridge → Release Manager → Documentation Updater        │
└──────────────────────────────────────────────────────────────────┘
```

---

## The 5 Triads

### 1. Idea Validation Triad

**Purpose**: Research ideas, validate with community, determine priority

**Agents**:
- **Research Analyst**: Web research, industry patterns, technical feasibility
- **Community Researcher**: User feedback, priority assessment, demand validation
- **Validation Synthesizer** (bridge): Compress into actionable requirements

**When to use**:
- New feature ideas
- Enhancement proposals
- Before starting design

**Output**: Validated requirements (PROCEED/DEFER/REJECT)

---

### 2. Design & Architecture Triad

**Purpose**: Design solutions, make architectural decisions, create specifications

**Agents**:
- **Validation Synthesizer** (bridge): Load validated requirements
- **Solution Architect**: Create ADRs, design specifications, implementation plans
- **Design Bridge** (bridge): Compress into implementation roadmap

**When to use**:
- After idea validation (PROCEED)
- Before implementing features
- When architectural decisions needed

**Output**: ADRs, technical specifications, implementation tasks

---

### 3. Implementation Triad

**Purpose**: Code features, write tests, verify quality

**Agents**:
- **Design Bridge** (bridge): Load implementation roadmap
- **Senior Developer**: Write code following ADRs, safe refactoring
- **Test Engineer**: Verify acceptance criteria, quality gate

**When to use**:
- After design phase
- When implementing features
- Following ADRs and specs

**Output**: Working code, passing tests, quality sign-off

---

### 4. Garden Tending Triad

**Purpose**: Continuous improvement, refactoring, technical debt management

**Agents**:
- **Cultivator**: Identify beneficial patterns, unification opportunities
- **Pruner**: Remove redundancy, safe refactoring, simplify complexity
- **Gardener Bridge** (bridge): Assess deployment readiness + feedback to Design

**When to use**:
- After major features
- Before releases
- When technical debt accumulates
- Spontaneously when finding issues

**Output**: Quality improvements, deployment readiness, design feedback

---

### 5. Deployment & Release Triad

**Purpose**: Create releases, update documentation, deploy to production

**Agents**:
- **Gardener Bridge** (bridge): Load deployment readiness
- **Release Manager**: Version, release notes, git tags, publish
- **Documentation Updater**: Update README, CHANGELOG, docs

**When to use**:
- After garden tending approves deployment
- When ready to release version
- After quality improvements

**Output**: Published release, updated documentation

---

## How to Invoke Triads

### Command Format

```
Start {Triad Name}: {task description}
```

### Examples

```bash
# Idea Validation
Start Idea Validation: Add ability to pause/resume triads mid-execution

# Design & Architecture
Start Design: Interactive graph visualization feature

# Implementation
Start Implementation: Graph viewer per ADR-001 and ADR-002

# Garden Tending
Start Garden Tending: Scope - entire codebase

# Deployment & Release
Start Deployment: v0.0.7
```

---

## Complete Workflow Examples

### Example 1: New Feature from Idea to Deployment

**Scenario**: User wants to add interactive graph visualization

**Step 1: Idea Validation**

```
> Start Idea Validation: Interactive graph visualization for knowledge graphs
```

**What happens**:
1. **Research Analyst**: Searches for visualization tools (Cytoscape.js, D3.js, vis.js)
2. **Community Researcher**: Validates user need (users complain JSON inspection is tedious)
3. **Validation Synthesizer**: Creates requirement → PROCEED (Priority: HIGH)

**Output**: `.claude/graphs/idea-validation_graph.json` with validated requirement

---

**Step 2: Design & Architecture**

```
> Start Design: Interactive graph visualization per validated requirement
```

**What happens**:
1. **Validation Synthesizer**: Loads requirement from bridge context
2. **Solution Architect**: Creates 3 ADRs (separate HTML+JSON, vis.js library, query parameter)
3. **Design Bridge**: Creates implementation roadmap with 10 tasks

**Output**: `.claude/graphs/design_graph.json` with ADRs and tasks

---

**Step 3: Implementation**

```
> Start Implementation: Graph visualization per design specifications
```

**What happens**:
1. **Design Bridge**: Loads ADRs and tasks
2. **Senior Developer**: Implements HTML, JS, CSS following ADRs
3. **Test Engineer**: Verifies acceptance criteria, security tests → APPROVE

**Output**: `.claude/graphs/implementation_graph.json` + working code

---

**Step 4: Garden Tending** (optional but recommended)

```
> Start Garden Tending: Scope - visualization feature
```

**What happens**:
1. **Cultivator**: Identifies "dynamic loading pattern" worth expanding
2. **Pruner**: Unifies graph loading (3 implementations → 1 GraphLoader)
3. **Gardener Bridge**: Deployment readiness READY + feedback to Design

**Output**:
- `.claude/graphs/garden-tending_graph.json`
- `.claude/graphs/bridge_garden_to_deployment.json` (forward)
- `.claude/graphs/feedback_garden_to_design.json` (feedback)

---

**Step 5: Deployment & Release**

```
> Start Deployment: v0.0.7
```

**What happens**:
1. **Gardener Bridge**: Loads deployment readiness (READY)
2. **Release Manager**: Creates v0.0.7 tag, release notes, publishes
3. **Documentation Updater**: Updates CHANGELOG, README, API docs

**Output**:
- `.claude/graphs/deployment_graph.json`
- Git tag: `v0.0.7`
- Published release

---

### Example 2: Quick Bug Fix (Skip Some Triads)

**Scenario**: Bug found, needs immediate fix

**Path**: Implementation → Deployment (skip Idea, Design if trivial)

```bash
# If bug fix is straightforward:
> Start Implementation: Fix division by zero in confidence calculation

# After fix:
> Start Deployment: v0.0.7-hotfix
```

**When to skip**:
- Bug fixes (obvious solution)
- Typos, documentation updates
- Hotfixes

**When NOT to skip**:
- Architectural changes
- New features
- Security vulnerabilities (need design review)

---

### Example 3: Garden Tending Without New Features

**Scenario**: Code quality improvement, no new features

```bash
> Start Garden Tending: Scope - entire codebase
```

**Use cases**:
- Before major releases
- After several feature additions
- When technical debt accumulates
- Proactive refactoring

**Output**: Quality improvements ready for deployment

---

## Knowledge Graphs

Each triad builds a knowledge graph in `.claude/graphs/`:

### Graph Files

```
.claude/graphs/
├── idea-validation_graph.json       # Validation decisions
├── design_graph.json                 # ADRs, specifications
├── implementation_graph.json         # Code implementations
├── garden-tending_graph.json         # Quality improvements
├── deployment_graph.json             # Releases
├── bridge_idea_to_design.json        # Context: Idea → Design
├── bridge_design_to_implementation.json  # Context: Design → Implementation
├── bridge_garden_to_deployment.json      # Context: Garden → Deployment
└── feedback_garden_to_design.json        # Feedback: Garden → Design
```

### Viewing Graphs

**Option 1: JSON inspection**

```bash
cat .claude/graphs/generator_graph.json | python3 -m json.tool
```

**Option 2: Interactive visualization** (if implemented)

```bash
open .claude/visualization/graph-viewer.html?graph=generator_graph.json
```

### Node Types

- **Entity**: Things (files, components, requirements)
- **Concept**: Ideas (patterns, principles, designs)
- **Decision**: Choices (ADRs, priority assessments, approvals)
- **Task**: Work items (implementation tasks)
- **Finding**: Discoveries (research findings, test results)
- **Uncertainty**: Known unknowns (items needing resolution)

### Graph Updates

Agents add nodes using `[GRAPH_UPDATE]` blocks:

```markdown
[GRAPH_UPDATE]
type: add_node
node_id: unique_id
node_type: Entity | Concept | Decision | Task | Finding | Uncertainty
label: Display name
description: Detailed description
confidence: 0.85-1.0
evidence: Citations, file:line references
created_by: agent-name
[/GRAPH_UPDATE]
```

---

## Best Practices

### 1. Start with Validation

**Don't skip Idea Validation** unless the need is obvious:
- ✅ GOOD: "Start Idea Validation: Add pause/resume feature"
- ❌ BAD: "Start Implementation: Add pause/resume" (no validation, no design)

**Why**: Prevents wasted effort on low-priority or unwanted features

---

### 2. Respect ADRs

**Follow architectural decisions** from Design phase:
- If ADR says "use vis.js", use vis.js (or update ADR with rationale)
- Don't silently deviate from design

**Why**: Design made decisions for reasons - document changes if needed

---

### 3. Safe Refactoring Rules (CRITICAL)

When Garden Tending involves refactoring, **follow these rules strictly**:

1. **Never refactor without tests**: Write tests first
2. **Make it work before making it better**: Fix bugs before improving
3. **One change at a time**: Incremental commits
4. **Verify after each change**: Run tests continuously
5. **Commit before and after**: Easy rollback

**Why**: Prevents breaking working code

---

### 4. Garden Tending is Not Optional

**Invoke Garden Tending**:
- After major features
- Before releases
- When debt accumulates

**Don't wait** for perfect time - technical debt compounds

**Why**: Maintains code quality, prevents accumulation

---

### 5. Knowledge Graph Hygiene

**Review graphs periodically**:

```bash
# Check for uncertainties
cat .claude/graphs/*.json | jq '.nodes[] | select(.type=="Uncertainty")'

# Check graph sizes
du -sh .claude/graphs/*.json
```

**Clean up old graphs** (if very large):
- Archive old versions
- Prune low-confidence nodes
- Consolidate related nodes

**Why**: Keeps context manageable for bridge agents

---

## Troubleshooting

### Issue: Triad doesn't start

**Symptom**: Command `Start Idea Validation: ...` doesn't work

**Solutions**:
1. Check command format: `Start {Triad Name}: {description}`
2. Verify agent files exist: `ls .claude/agents/idea-validation/`
3. Check for syntax errors in agent markdown files

---

### Issue: Bridge agent loses context

**Symptom**: Design agent doesn't have requirements from Validation

**Solutions**:
1. Check bridge file exists: `ls .claude/graphs/bridge_idea_to_design.json`
2. Verify on_bridge_transition.py hook ran
3. Check compression preserved critical nodes (top-20)

---

### Issue: Tests failing after Garden Tending

**Symptom**: Pruner refactored code, tests now fail

**Solution**:
1. **Revert immediately**: `git checkout HEAD~1` (rollback to before refactoring)
2. **Review safe refactoring rules**: Pruner should have caught this
3. **Fix tests or code**: Make tests pass before proceeding

**Prevention**: Follow Rule 4 (verify after each change)

---

### Issue: Deployment blocked

**Symptom**: Garden Tending says NOT READY for deployment

**Solutions**:
1. Review issues: Check `garden-tending_graph.json` for issues_found
2. Fix blockers: Address critical bugs, failing tests, security issues
3. Re-run Garden Tending after fixes
4. Only deploy when Gardener Bridge approves (READY)

---

### Issue: Design feedback not applied

**Symptom**: Same mistakes repeated in new features

**Solutions**:
1. Review feedback graph: `cat .claude/graphs/feedback_garden_to_design.json`
2. Before next Design phase: Check feedback for patterns
3. Solution Architect should reference feedback in ADRs

**Why feedback exists**: Continuous improvement loop

---

## Advanced Usage

### Partial Triad Invocation

Invoke specific agent:

```
> Run agent: research-analyst from idea-validation triad
> Task: Research pause/resume patterns
```

(If Claude Code supports this - check documentation)

---

### Custom Scopes

Garden Tending with focused scope:

```
> Start Garden Tending: Scope - .claude/hooks/ only
```

Focuses cultivation/pruning on specific directory

---

### Emergency Hotfix Path

Critical bug, skip validation and design:

```
> Start Implementation: HOTFIX - Fix critical security vulnerability in file loader
> Start Deployment: v0.0.7-hotfix
```

**Use sparingly** - only for emergencies

---

## Quick Reference

### When to Use Each Triad

| Triad | Use When... | Skip If... |
|-------|-------------|------------|
| **Idea Validation** | New features, enhancements | Bug fixes, typos |
| **Design & Architecture** | Complex features, architectural changes | Trivial changes |
| **Implementation** | Building features, writing code | (Never skip) |
| **Garden Tending** | Before releases, after features, debt accumulation | No refactoring needed |
| **Deployment** | Ready to release | Not deployment-ready |

### Command Cheat Sheet

```bash
# Idea Validation
Start Idea Validation: [idea description]

# Design
Start Design: [feature from validated idea]

# Implementation
Start Implementation: [feature from design]

# Garden Tending
Start Garden Tending: [scope]

# Deployment
Start Deployment: v[X.Y.Z]
```

### Knowledge Graph Locations

```bash
.claude/graphs/idea-validation_graph.json
.claude/graphs/design_graph.json
.claude/graphs/implementation_graph.json
.claude/graphs/garden-tending_graph.json
.claude/graphs/deployment_graph.json

# Bridge contexts
.claude/graphs/bridge_*.json

# Feedback (unique to Garden Tending)
.claude/graphs/feedback_garden_to_design.json
```

---

## Next Steps

1. **Try your first workflow**: Pick a feature and go Idea → Design → Implementation → Garden Tending → Deployment
2. **Review knowledge graphs**: Check `.claude/graphs/*.json` after each triad
3. **Iterate**: Use feedback from Garden Tending to improve future designs
4. **Customize agents**: Edit agent markdown files to match your workflow preferences

---

**Questions?** Refer to individual agent files in `.claude/agents/` for detailed guidance on each agent's behavior.

Happy building! 🎯
