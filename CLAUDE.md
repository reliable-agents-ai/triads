---
# 🎯 CORE OPERATING PRINCIPLES
---

**THESE PRINCIPLES GOVERN ALL WORK IN THIS PROJECT**

When working in Claude Code on ANY task - writing code, making decisions, debugging, researching, documenting - you MUST follow these principles. These rules override all other instructions.

---

## Constitutional Principles (Universal - ABSOLUTE Authority)

The following constitutional principles are imported from separate files for maintainability and reusability. These principles apply to ALL work in this project and CANNOT be overridden.

@.claude/constitutional/evidence-based-claims.md
@.claude/constitutional/uncertainty-escalation.md
@.claude/constitutional/multi-method-verification.md
@.claude/constitutional/complete-transparency.md
@.claude/constitutional/assumption-auditing.md
@.claude/constitutional/communication-standards.md

**Authority**: ABSOLUTE - Cannot be overridden by any other instruction

---

## Domain-Specific Methodology (Software Development)

This project is a software development project. The following methodologies define quality standards for software development work:

@.claude/methodologies/software/tdd-methodology.md
@.claude/methodologies/software/code-quality-standards.md
@.claude/methodologies/software/security-protocols.md
@.claude/methodologies/software/git-workflow.md

**Authority**: HIGH - Domain-specific standards that apply to all software development tasks

---

## Framework Skills (Keyword-Discoverable)

The following framework skills enforce constitutional principles and are keyword-discoverable for agent invocation:

**Available Skills**:
- `validate-knowledge` - Validate knowledge graph additions meet confidence thresholds
- `escalate-uncertainty` - Escalate when confidence < 90%
- `cite-evidence` - Ensure all claims have verifiable evidence
- `validate-assumptions` - Identify and validate assumptions before proceeding
- `multi-method-verify` - Verify with ≥2 independent methods
- `bridge-compress` - Compress knowledge graph to top-N nodes for handoffs

**Location**: `.claude/skills/framework/`

Skills are discovered by keyword matching in their `description` fields (50-100+ keywords each).

---

---
# ⚡ TRIAD ROUTING SYSTEM
---

**CRITICAL DIRECTIVE**: This project uses a 5-triad workflow. When user describes work (not questions), suggest the appropriate triad.

## Routing Table

| User Intent | Suggest This Command |
|-------------|---------------------|
| **New feature idea** | `Start Idea Validation: [idea description]` |
| **"How should we architect..."** | `Start Design: [feature to design]` |
| **"Let's build/implement..."** | `Start Implementation: [feature to build]` |
| **"Code is messy/needs refactoring"** | `Start Garden Tending: [scope to improve]` |
| **"Ready to release/deploy"** | `Start Deployment: v[version]` |

## Triads Explained

### 1. Idea Validation
- **Purpose**: Research ideas, validate community need, prioritize features
- **When**: User has new feature idea, wants to validate problem-solution fit
- **Agents**: research-analyst → community-researcher → validation-synthesizer

### 2. Design
- **Purpose**: Create architecture, make decisions, write ADRs
- **When**: Designing solutions, evaluating approaches, documenting decisions
- **Agents**: validation-synthesizer → solution-architect → design-bridge
- **⚠️ HITL Gate**: User MUST approve design before proceeding to Implementation

### 3. Implementation
- **Purpose**: Write code, create tests, ensure quality
- **When**: Building approved features, writing implementation code
- **Agents**: design-bridge → senior-developer → test-engineer

### 4. Garden Tending
- **Purpose**: Refactor, reduce debt, improve quality
- **When**: Code needs cleanup, after features, before releases, when debt accumulates
- **Agents**: cultivator → pruner → gardener-bridge
- **Philosophy**: Cultivate growth, prune redundancy, preserve working systems

### 5. Deployment
- **Purpose**: Create releases, update docs, publish packages
- **When**: Ready to release, need changelog updates, package publishing
- **Agents**: gardener-bridge → release-manager → documentation-updater

## Routing Examples

**User**: "I'm thinking about adding AI-powered code suggestions"
**You**: "This sounds like **Idea Validation** work - we should research demand and feasibility. Would you like me to `Start Idea Validation: AI-powered code suggestions`?"

**User**: "How should we structure the plugin system?"
**You**: "This is **Design** work - we need to architect the solution. Would you like me to `Start Design: Plugin system architecture`?"

**User**: "What's the difference between a bridge agent and regular agent?"
**You**: [Answer the question - this is Q&A, NOT a work request. Don't suggest routing.]

**User**: "Let's build the OAuth2 integration"
**You**: "This sounds like **Implementation** work. Would you like me to `Start Implementation: OAuth2 integration`?"

**User**: "The router code has lots of duplication"
**You**: "This is **Garden Tending** work - refactoring to improve quality. Would you like me to `Start Garden Tending: Router code consolidation`?"

**User**: "Is there any maintenance work needed?"
**You**: "This sounds like **Garden Tending** work - scanning for quality improvements. Would you like me to `Start Garden Tending: Codebase maintenance scan`?"

**User**: "We're ready to release v0.3.0"
**You**: "This is **Deployment** work. Would you like me to `Start Deployment: v0.3.0`?"

## Critical Rules

1. **Suggest, don't auto-execute**: Always ask for confirmation before invoking a triad
2. **Work vs. Questions**: Only suggest routing for work requests, not information questions
3. **Context matters**: If deep in conversation about specific code, routing may interrupt flow - use judgment
4. **Explicit commands**: When user types exact "Start TriadName: ..." syntax, invoke immediately without asking

---

---
# 📊 KNOWLEDGE MANAGEMENT
---

**For detailed knowledge graph principles, see**: [docs/KM_PRINCIPLES.md](docs/KM_PRINCIPLES.md)

## Quick Reference

- **Minimum confidence**: 85% (< 85% → create Uncertainty node and escalate)
- **Verification methods**: Use minimum 2 methods for every knowledge addition
- **Provenance required**: Every node must include source, timestamp, evidence, created_by
- **Graph updates**: Use `[GRAPH_UPDATE]` blocks in agent outputs

---

---
# 📚 DETAILED DOCUMENTATION
---

For comprehensive guides, see:

- **[Claude Code Integration Guide](docs/CLAUDE_CODE_INTEGRATION_GUIDE.md)** - How to use triad generator with Claude Code
- **[Usage Guide](docs/USAGE.md)** - Working with generated triads
- **[Architecture](docs/ARCHITECTURE.md)** - System design and components
- **[Installation](docs/INSTALLATION.md)** - Setup instructions
- **[Claude Code Official Docs](https://docs.claude.com/en/docs/claude-code)** - Claude Code reference

---
