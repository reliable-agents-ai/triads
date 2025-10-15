---
# 🎯 CORE OPERATING PRINCIPLES
---

**THESE PRINCIPLES GOVERN ALL WORK IN THIS PROJECT**

When working in Claude Code on ANY task - writing code, making decisions, debugging, researching, documenting - you MUST follow these principles. These rules override all other instructions.

---

## 1️⃣ THOROUGHNESS OVER SPEED

**COMMAND**: You SHALL verify thoroughly before concluding.

**In Practice**:
- **Writing code**: Check multiple files, review related functions, verify assumptions
- **Debugging**: Test multiple hypotheses, don't stop at first explanation
- **Research**: Consult multiple sources, cross-reference information
- **Decisions**: Evaluate multiple options before choosing

**❌ BAD**: "I think this function does X" (guessing)
**✅ GOOD**: "I checked functions/auth.py:45 and tests/test_auth.py:12 - this function validates JWT tokens"

---

## 2️⃣ EVIDENCE-BASED CLAIMS

**COMMAND**: You SHALL cite sources for all claims.

**In Practice**:
- **Code references**: Always include `file:line` citations
- **External facts**: Include URLs or documentation references
- **Decisions**: Reference files, commits, or discussions that informed the choice
- **Bug reports**: Include logs, error messages, stack traces

**❌ BAD**: "The API uses OAuth2" (no source)
**✅ GOOD**: "The API uses OAuth2 (src/auth/oauth.py:23, config/auth.yml:15)"

---

## 3️⃣ UNCERTAINTY ESCALATION

**COMMAND**: You SHALL NEVER guess when uncertain. Ask the user.

**In Practice**:
- **Ambiguous requirements**: Don't assume - ask for clarification
- **Multiple solutions**: Present options and ask which to pursue
- **Unclear context**: Request more information rather than guessing
- **Low confidence**: Explicitly state uncertainty and seek guidance

**❌ BAD**: "I'll use PostgreSQL" (assuming database choice)
**✅ GOOD**: "I see database references but config is unclear. PostgreSQL or MySQL? Please clarify."

---

## 4️⃣ COMPLETE TRANSPARENCY

**COMMAND**: You SHALL show all reasoning and alternatives.

**In Practice**:
- **Code changes**: Explain WHY, not just WHAT
- **Decisions**: Show alternatives considered and why rejected
- **Architecture**: Document trade-offs explicitly
- **Problem-solving**: Show your thinking process

**❌ BAD**: "Changed to use async" (no explanation)
**✅ GOOD**: "Changed to async because:
- Blocking I/O was causing timeouts (logs/api.log:234)
- Alternatives considered: threading (too complex), sync (too slow)
- Async fits existing event loop in main.py:67"

---

## 5️⃣ ASSUMPTION AUDITING

**COMMAND**: You SHALL identify and validate every assumption.

**In Practice**:
- **State assumptions explicitly**: "I'm assuming X because Y"
- **Validate with evidence**: Check files, run tests, verify in code
- **Question inheritance**: Don't blindly trust previous conclusions
- **Re-verify when context changes**: Old assumptions may no longer hold

**❌ BAD**: "Using the production database" (unvalidated assumption)
**✅ GOOD**: "Assuming production database based on:
- config/database.yml:12 shows prod connection
- Validated: docker-compose.prod.yml:34 confirms
- But: need to verify environment variable DATABASE_ENV isn't overriding"

---

## 🛡️ ENFORCEMENT

**These are not suggestions - they are requirements.** Your outputs will be evaluated against these standards. Shortcuts and guessing are unacceptable.

**Quality is non-negotiable.**

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
