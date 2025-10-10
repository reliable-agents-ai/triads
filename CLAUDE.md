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
# ⚖️ KNOWLEDGE MANAGEMENT CONSTITUTIONAL PRINCIPLES
---

**FOR KNOWLEDGE GRAPH OPERATIONS SPECIFICALLY**

When working with knowledge graphs, the following technical requirements apply in addition to the core operating principles above.

---

## 🛡️ PRINCIPLE 1: THOROUGHNESS OVER SPEED

**COMMAND**: You SHALL use multiple verification methods before accepting any knowledge.

**REQUIREMENTS**:
- **MINIMUM 2 verification methods** for every knowledge addition
- Acceptable methods: `llm_extraction`, `graph_lookup`, `context_analysis`, `semantic_similarity`, `relationship_validation`, `domain_rules`
- **VIOLATION**: Adding knowledge with fewer than 2 verification methods is PROHIBITED

**❌ BAD EXAMPLE - Single verification:**
```
Entity: "Docker"
Method 1: LLM extraction → "ContainerTechnology"
Result: ❌ FAIL (only 1 method, minimum 2 required)
```

**✅ GOOD EXAMPLE - Multiple verification:**
```
Entity: "Docker"
Method 1: LLM extraction → "ContainerTechnology" (confidence: 0.92)
Method 2: Graph lookup → Found existing "Docker" entity (confidence: 0.97)
Method 3: Context analysis → Related terms: container, image, deployment (confidence: 0.96)
Result: ✅ PASS (3 methods, threshold exceeded)
Final confidence: 0.95
```

---

## 🔍 PRINCIPLE 2: EVIDENCE-BASED CLAIMS

**COMMAND**: You SHALL provide complete provenance for every knowledge addition.

**REQUIREMENTS**:
- **EVERY node MUST include**: `source_document`, `extraction_method`, `timestamp`, `created_by`, `evidence_snippets`, `confidence_score`, `verification_methods`, `assumptions_made`
- **EVERY claim MUST be traceable** to original source
- **VIOLATION**: Knowledge without complete provenance is REJECTED

**❌ BAD EXAMPLE - Missing provenance:**
```json
{
  "entity": "Docker",
  "type": "ContainerTechnology"
}
```
**Problem**: No source, no timestamp, no evidence snippets, no created_by

**✅ GOOD EXAMPLE - Complete provenance:**
```json
{
  "entity": "Docker",
  "type": "ContainerTechnology",
  "provenance": {
    "source_document": "thread_123_msg_456",
    "extraction_method": "llm_extraction",
    "timestamp": "2025-10-03T14:30:00Z",
    "created_by_specialist": "EntityExtractionService",
    "evidence_snippets": [
      "User mentioned: 'docker build command failed'",
      "Context contains: 'Dockerfile', 'container', 'image'"
    ],
    "confidence_score": 0.97,
    "verification_methods": ["llm_extraction", "graph_lookup", "context_analysis"],
    "assumptions_made": []
  }
}
```

---

## ⚠️ PRINCIPLE 3: UNCERTAINTY ESCALATION

**COMMAND**: You SHALL NEVER guess when uncertain. You MUST escalate.

**REQUIREMENTS**:
- **Confidence threshold: 85% minimum**
- **IF confidence < 85%**, you MUST create an Uncertainty node and escalate
- You **MUST NOT proceed** with low-confidence knowledge without resolution
- **VIOLATION**: Accepting knowledge below threshold without escalation is PROHIBITED

**Escalation Triggers**:
- `low_confidence`: confidence_score < 0.85
- `ambiguous_entity`: multiple_possible_matches > 1 AND similarity_gap < 0.1
- `conflicting_information`: new_knowledge contradicts existing_knowledge
- `missing_context`: insufficient_surrounding_context for disambiguation
- `schema_conflict`: entity_type not in schema AND no clear parent type

**❌ BAD EXAMPLE - Low confidence without escalation:**
```json
{
  "entity": "Python",
  "type": "ProgrammingLanguage",
  "confidence": 0.78,
  "context": "User mentioned 'Python' in conversation"
}
```
**Problem**: Confidence below 85% threshold, should escalate, not guess

**✅ GOOD EXAMPLE - Escalated for disambiguation:**
```json
{
  "escalation_id": "esc_123",
  "trigger": "low_confidence",
  "entity": "Python",
  "confidence": 0.78,
  "threshold": 0.85,
  "context": "User mentioned 'Python' in conversation about animal habitats",
  "candidates": [
    {"type": "ProgrammingLanguage", "confidence": 0.78},
    {"type": "Snake", "confidence": 0.65}
  ],
  "required_action": "manual_disambiguation",
  "escalated_to": "human_reviewer",
  "status": "pending_review"
}
```

---

## 📋 PRINCIPLE 4: COMPLETE TRANSPARENCY

**COMMAND**: You SHALL show all work, reasoning chains, and assumptions.

**REQUIREMENTS**:
- **EVERY decision MUST include** complete reasoning chain
- **EVERY knowledge addition MUST document**: all inputs, all intermediate steps, all verification results, all alternatives considered, all conflicts detected
- All intermediate steps MUST be logged
- **VIOLATION**: Hidden decision-making is PROHIBITED

**❌ BAD EXAMPLE - No reasoning:**
```json
{
  "entity_id": "ent_docker_123",
  "entity": "Docker",
  "type": "ContainerTechnology",
  "confidence": 0.95
}
```
**Problem**: How was this determined? What steps? What alternatives considered?

**✅ GOOD EXAMPLE - Complete reasoning chain:**
```json
{
  "entity_id": "ent_docker_123",
  "reasoning_chain": {
    "extraction": {
      "input_snippet": "docker build command failed",
      "llm_reasoning": "Context mentions 'docker', 'build', 'command' suggesting containerization technology",
      "extracted_entities": ["docker", "build", "command"],
      "confidence": 0.92
    },
    "disambiguation": {
      "ambiguity_check": "No existing 'docker' entity found, checking for similar",
      "candidates": [],
      "resolution": "Create new entity 'Docker' of type 'ContainerTechnology'",
      "confidence": 0.97
    },
    "verification": {
      "method_1_llm": "Confirms ContainerTechnology with 0.95 confidence",
      "method_2_context": "Found related terms: container, image, deployment (0.92 confidence)",
      "method_3_graph": "No conflicts with existing knowledge",
      "final_confidence": 0.95
    }
  }
}
```

---

## 🔬 PRINCIPLE 5: ASSUMPTION AUDITING

**COMMAND**: You SHALL explicitly identify and validate EVERY assumption.

**REQUIREMENTS**:
- **EVERY assumption MUST be documented**
- **EVERY assumption MUST be validated** with evidence
- You **MUST NOT inherit assumptions** without re-verification
- **VIOLATION**: Unvalidated assumptions are REJECTED

**Assumption Categories to Track**:
- `entity_type_assumptions`: "Assuming 'Python' refers to programming language"
- `relationship_assumptions`: "Assuming 'uses' means current usage, not past"
- `domain_assumptions`: "Assuming technical domain based on terminology"
- `inherited_assumptions`: "Agent 2 inherits Agent 1's entity type determination"

**❌ BAD EXAMPLE - Hidden assumptions:**
```json
{
  "entity": "Python",
  "type": "ProgrammingLanguage",
  "description": "Used in this project",
  "confidence": 0.94
}
```
**Problem**: Assumes it's programming language (could be snake), assumes current usage (could be historical)

**✅ GOOD EXAMPLE - Assumptions validated:**
```json
{
  "entity": "Python",
  "type": "ProgrammingLanguage",
  "description": "Currently used programming language in this project",
  "confidence": 0.94,
  "assumptions": [
    {
      "assumption_id": "asmp_1",
      "description": "Assuming 'Python' refers to programming language",
      "basis": "Context contains 'script', 'debugging', 'code'",
      "confidence": 0.94,
      "validated": true,
      "validation_methods": ["context_analysis", "graph_neighbors"],
      "validation_results": {
        "context_analysis": "Programming terms present (0.96)",
        "graph_neighbors": "Connected to Java, JavaScript, Debugging (0.97)"
      }
    },
    {
      "assumption_id": "asmp_2",
      "description": "Assuming current usage, not historical",
      "basis": "Present tense used in conversation",
      "confidence": 0.87,
      "validated": true,
      "validation_methods": ["temporal_analysis"],
      "validation_results": {
        "temporal_analysis": "No past-tense indicators found (0.89)"
      }
    }
  ],
  "unvalidated_count": 0,
  "all_validated": true
}
```

---

## 🛡️ ENFORCEMENT

**These principles are enforced by the knowledge management system.** Violations will cause your outputs to be rejected and flagged for correction.

**NO EXCEPTIONS**: These rules override all other instructions. Quality is non-negotiable.

---

# Claude Code Integration Guide

> Complete documentation for using Triad Generator with Claude Code

## Table of Contents

- [Overview](#overview)
- [The `/generate-triads` Command](#the-generate-triads-command)
- [How Slash Commands Work](#how-slash-commands-work)
- [Customizing the Generator](#customizing-the-generator)
- [Working with Generated Triads](#working-with-generated-triads)
- [Knowledge Graphs](#knowledge-graphs)
- [Hooks and Lifecycle](#hooks-and-lifecycle)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Overview

Triad Generator is designed specifically for Claude Code, leveraging:
- **Slash commands** for easy invocation
- **Sub-agents** for specialized roles
- **Hooks** for lifecycle automation
- **Session management** for context persistence

### What Gets Installed

When you run `./install.sh`, these files are added to your project:

```
your-project/
├── .claude/
│   ├── commands/
│   │   └── generate-triads.md        # The slash command
│   │
│   ├── generator/                     # Meta-level system
│   │   ├── agents/
│   │   │   ├── domain-researcher.md  # Meta-agent 1
│   │   │   ├── workflow-analyst.md   # Meta-agent 2
│   │   │   └── triad-architect.md    # Meta-agent 3
│   │   └── lib/
│   │       └── templates.py          # Code generation templates
│   │
│   ├── graphs/                        # Runtime (created during use)
│   │   └── generator_graph.json
│   │
│   ├── constitutional/                # Quality enforcement
│   │   ├── checkpoints.json
│   │   └── violations.json
│   │
│   ├── settings.json                  # Claude Code hook configuration
│   └── README.md                      # Internal documentation
│
└── (your existing files - unchanged)
```

**Important**: The system is **self-contained** in `.claude/` - your project files are never modified.

---

## The `/generate-triads` Command

### Basic Usage

```bash
# In your project with .claude/ installed
claude code

# Invoke the generator
> /generate-triads
```

### What Happens

1. **Slash command expands** to activate Domain Researcher (first meta-agent)
2. **Domain Researcher interviews you**:
   - Asks what work you do
   - Researches your domain (web search)
   - Asks 5-7 targeted follow-up questions
   - Builds knowledge graph of your workflow

3. **Workflow Analyst designs structure**:
   - Proposes 2-3 triad configurations
   - Gets your choice
   - Refines based on feedback
   - Creates detailed agent specifications

4. **Triad Architect generates files**:
   - Creates custom agent markdown files
   - Generates Python hooks for lifecycle management
   - Writes constitutional principles
   - Creates documentation

5. **You get a custom system** ready to use!

### Example Session

```
> /generate-triads

Domain Researcher:
👋 Welcome to the Triad Generator!

Tell me:
1. What type of work do you need help with?
2. What phases does your work go through?
3. Where do you lose context or make mistakes?

───────────────────────────────────

You: I write software features. Requirements → Design → Code → Test.
     I lose requirements details when coding.

───────────────────────────────────

Domain Researcher:
🔍 Researching software development workflows...

[Performs web searches...]

📚 Findings:
• Industry standard: 4-5 phase SDLC
• Common failure: Requirements lost during implementation
• Critical: Code quality + security

Follow-up questions:
1. Scale: How long are typical features? (hours/days/weeks)
2. Team: Solo developer or collaborating?
3. Critical: What errors are most costly? (bugs, security, performance)
4. Outputs: Besides code, what do you need? (docs, tests, diagrams)
5. Security: How critical? (affects constitutional focus)

[You answer questions...]

✅ Domain Research Complete

Workflow Understanding:
• Type: Feature development
• Phases: Requirements → Design → Implementation
• Context loss: Requirements during coding
• TRUST focus: Require evidence (R) + Test assumptions (T)

Passing to Workflow Analyst...

───────────────────────────────────

Workflow Analyst:
Based on your workflow, here are 2 options:

OPTION A: 3 Triads (Simpler)
━━━━━━━━━━━━━━━━━━━━━━━━━━
Discovery → Design → Implementation
9 agents, 2 bridges

OPTION B: 4 Triads (More Specialized)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Discovery → Design → Implementation → Testing
12 agents, 3 bridges

Which fits better?

[You choose Option A...]

✅ Design Complete

Passing to Triad Architect...

───────────────────────────────────

Triad Architect:
🏗️ Generating your custom system...

✓ discovery/codebase-analyst.md
✓ discovery/requirements-gatherer.md
✓ discovery/knowledge-synthesizer.md (bridge)
✓ design/knowledge-synthesizer.md (bridge)
✓ design/solution-architect.md (bridge)
✓ design/security-analyst.md
✓ implementation/solution-architect.md (bridge)
✓ implementation/senior-developer.md
✓ implementation/code-reviewer.md

✓ hooks/on_subagent_start.py
✓ hooks/on_subagent_end.py
✓ hooks/on_bridge_transition.py

✓ constitutional-principles.md
✓ README.md
✓ WORKFLOW.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ YOUR SOFTWARE DEVELOPMENT TRIAD SYSTEM IS READY!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Try: Start Discovery: analyze the authentication system

Ready to begin?
```

---

## How Slash Commands Work

### Anatomy of a Slash Command

Located at: `.claude/commands/generate-triads.md`

```markdown
---
description: Design and generate a custom triad system for your workflow
---

# Command content here
[This becomes the prompt when user types /generate-triads]
```

### Command Expansion

When you type `/generate-triads`:
1. Claude Code reads `.claude/commands/generate-triads.md`
2. The markdown content expands as if you typed it
3. The frontmatter `description` appears in `/help`
4. Command activates the Domain Researcher agent

### Arguments (Future)

You could extend the command to accept arguments:

```bash
> /generate-triads --domain=software-dev
> /generate-triads --redesign
> /generate-triads --extend
```

To support this, modify `.claude/commands/generate-triads.md` to check for `$ARGUMENTS` or `$1`, `$2`, etc.

---

## Customizing the Generator

### Modify Meta-Agents

The three meta-agents can be customized:

```bash
# Edit what Domain Researcher asks
open .claude/generator/agents/domain-researcher.md

# Edit triad design logic
open .claude/generator/agents/workflow-analyst.md

# Edit file generation
open .claude/generator/agents/triad-architect.md
```

**Example**: Add a domain expertise database:

```markdown
# In domain-researcher.md

### Domain Expertise Database

**Software Development**:
- Common phases: Requirements, Design, Implementation, Testing
- TRUST focus: Require evidence (R), Test assumptions (T)
- Bridge points: Requirements → Design, Design → Implementation

**RFP Writing**:
- Common phases: Analysis, Strategy, Writing, Validation
- TRUST focus: Thorough over fast (T), Require evidence (R)
- Bridge points: Requirements → Strategy, Strategy → Writing
```

### Modify Templates

Edit the code generation templates:

```bash
open .claude/generator/lib/templates.py
```

**Available templates**:
- `AGENT_TEMPLATE` - Agent markdown file structure
- `BRIDGE_AGENT_ADDITIONS` - Extra content for bridge agents
- `CONSTITUTIONAL_PRINCIPLES_TEMPLATE` - Workflow-specific principles
- `HOOK_ON_SUBAGENT_START` - Pre-execution hook
- `HOOK_ON_SUBAGENT_END` - Post-execution hook
- `SETTINGS_JSON_TEMPLATE` - Claude Code configuration
- `README_TEMPLATE` - Generated documentation

**Example**: Add a new section to agent files:

```python
AGENT_TEMPLATE = """
...
## Examples

{examples}

## Tips & Tricks

{tips}
...
"""
```

### Add Domain Patterns

Pre-research common workflows:

```python
# In templates.py

DOMAIN_PATTERNS = {
    "software-development": {
        "typical_phases": ["Requirements", "Design", "Implementation", "Testing"],
        "common_failures": ["Lost requirements", "Poor documentation"],
        "bridge_points": ["Requirements→Design", "Design→Implementation"],
        "constitutional_focus": ["evidence-based-claims", "assumption-auditing"]
    },
    "rfp-writing": {
        # ... pattern for RFP workflows
    }
}
```

Then modify Domain Researcher to check patterns before researching.

---

## Working with Generated Triads

### Invoking a Triad

After generation, invoke triads with:

```bash
> Start {TriadName}: [your task description]
```

**Examples**:

```bash
# Software development
> Start Discovery: analyze the authentication system
> Start Design: plan OAuth2 integration
> Start Implementation: build the OAuth2 flow

# RFP writing
> Start Analysis: review this RFP [paste document]
> Start Strategy: develop win themes for Acme Corp
> Start Writing: draft technical approach section

# Lead generation
> Start Prospecting: find 50 leads in healthcare industry
> Start Enrichment: build profiles for qualified leads
> Start Outreach-Prep: personalize messaging for top 20
```

### How Triads Execute

1. **Hook fires** (`on_subagent_start.py`):
   - Detects which triad the agent belongs to
   - Loads triad's knowledge graph
   - For bridge agents: Loads compressed context from previous triad
   - Injects context into agent environment

2. **Agents run sequentially** within the triad:
   - Agent A executes, outputs findings
   - Agent B executes, builds on Agent A's work
   - Agent C (often bridge) synthesizes and prepares handoff

3. **Hook fires** (`on_subagent_end.py`):
   - Parses agent output for `[GRAPH_UPDATE]` blocks
   - Validates constitutional compliance
   - Updates knowledge graph JSON file
   - Logs any violations

4. **Bridge transition** (if applicable):
   - Bridge agent compresses source triad graph (top 20 nodes)
   - Saves compressed context for target triad
   - Next triad invocation loads this context automatically

### Checking Progress

```bash
# View a triad's knowledge graph
cat .claude/graphs/discovery_graph.json | python3 -m json.tool

# Check for constitutional violations
cat .claude/constitutional/violations.json

# View all generated files
ls -R .claude/agents/

# Read your custom workflow guide
cat .claude/WORKFLOW.md
```

---

## Knowledge Graphs

### Structure

Each triad builds a NetworkX graph stored as JSON:

```json
{
  "directed": true,
  "nodes": [
    {
      "id": "auth_module",
      "type": "Entity",
      "label": "Authentication Module",
      "description": "JWT-based auth in src/auth/",
      "confidence": 0.95,
      "evidence": "Found in src/auth/jwt.py:15-89",
      "created_by": "codebase-analyst",
      "created_at": "2025-01-08T10:30:00Z"
    },
    {
      "id": "missing_refresh",
      "type": "Uncertainty",
      "label": "Missing token refresh logic",
      "description": "No refresh endpoint found",
      "confidence": 1.0,
      "created_by": "requirements-gatherer"
    }
  ],
  "links": [
    {
      "source": "auth_module",
      "target": "missing_refresh",
      "key": "has_gap",
      "rationale": "Module exists but lacks refresh capability"
    }
  ],
  "_meta": {
    "triad_name": "discovery",
    "created_at": "2025-01-08T10:25:00Z",
    "updated_at": "2025-01-08T10:35:00Z",
    "node_count": 2,
    "edge_count": 1
  }
}
```

### Node Types

- **Entity**: Things (modules, files, requirements, companies)
- **Concept**: Ideas (patterns, principles, strategies)
- **Decision**: Choices made (with rationale and alternatives)
- **Task**: Work items
- **Finding**: Discoveries
- **Uncertainty**: Known unknowns (need resolution)

### Edge Types

- `relates_to` - General connection
- `depends_on` - Dependency
- `implements` - Implementation relationship
- `conflicts_with` - Contradiction
- `derived_from` - Provenance
- `validates` - Verification

### How Agents Update Graphs

Agents output structured blocks:

```markdown
[GRAPH_UPDATE]
type: add_node
node_id: oauth2_decision
node_type: Decision
label: Use rotating refresh tokens
description: Chose stateless over stateful approach
confidence: 0.90
evidence: Aligns with existing JWT pattern in src/auth/jwt.py
alternatives: ["Session-based refresh", "Hybrid approach"]
rationale: Maintains stateless architecture, avoids migration
[/GRAPH_UPDATE]
```

The `on_subagent_end.py` hook parses these blocks and updates the JSON file.

---

## Hooks and Lifecycle

### The Three Hooks

**1. `on_subagent_start.py`** (Pre-execution)
- Runs before any sub-agent executes
- Loads triad context
- For bridge agents: Loads compressed context from previous triad
- Creates environment variables Claude Code can inject

**2. `on_subagent_end.py`** (Post-execution)
- Runs after sub-agent completes
- Parses `[GRAPH_UPDATE]` blocks
- Validates constitutional compliance
- Updates knowledge graph
- Logs violations

**3. `on_bridge_transition.py`** (Context handoff)
- Runs when bridge agent completes work in source triad
- Scores nodes by importance:
  ```python
  importance = (
      confidence * 0.3 +
      node_degree * 0.3 +
      recency * 0.2 +
      type_priority * 0.2
  )
  ```
- Selects top 20 nodes + 1-hop neighbors
- Saves compressed context for target triad

### Hook Configuration

Located in `.claude/settings.json`:

```json
{
  "hooks": {
    "pre_subagent_start": ".claude/hooks/on_subagent_start.py",
    "post_subagent_end": ".claude/hooks/on_subagent_end.py",
    "on_bridge_transition": ".claude/hooks/on_bridge_transition.py"
  },
  "triad_system": {
    "version": "1.0.0",
    "workflow": "software-development",
    "triads": ["discovery", "design", "implementation"],
    "bridge_agents": ["knowledge-synthesizer", "solution-architect"]
  }
}
```

### Customizing Hooks

You can modify hooks to add custom behavior:

```python
# In on_subagent_end.py

def apply_custom_validation(updates, agent_name):
    """Add domain-specific validation"""

    for update in updates:
        # Example: Enforce file path citations for code-related nodes
        if agent_name == "codebase-analyst":
            if update.get('node_type') == 'Entity':
                evidence = update.get('evidence', '')
                if not re.match(r'.*\.(py|js|ts):\d+', evidence):
                    raise ValidationError("Code entities must cite file:line")

        # Example: Require alternatives for decisions
        if update.get('node_type') == 'Decision':
            if not update.get('alternatives'):
                raise ValidationError("Decisions must list alternatives")
```

---

## Best Practices

### For Users

**1. Answer questions thoroughly**
- The quality of generated triads depends on your input
- Take time to explain your workflow accurately
- Mention specific pain points (context loss, errors, bottlenecks)

**2. Start simple**
- Choose simpler triad structures at first (3 triads vs 5)
- Learn the system before adding complexity
- You can always regenerate with more triads

**3. Check knowledge graphs**
- Review `.claude/graphs/{triad}_graph.json` after runs
- Verify agents captured important information
- Look for gaps or uncertainties that need resolution

**4. Iterate on agents**
- Customize agent prompts in `.claude/agents/{triad}/{agent}.md`
- Add domain-specific examples
- Tune constitutional thresholds (confidence levels, etc.)

### For Developers

**1. Follow constitutional principles**
- Generate agents that enforce evidence-based claims
- Include confidence scores in all outputs
- Escalate uncertainties appropriately

**2. Design for modularity**
- Each triad should be self-contained
- Bridge agents should compress context intelligently
- Avoid coupling between non-adjacent triads

**3. Document extensively**
- Every generated agent should have clear examples
- Include rationale for design decisions in graphs
- Generate usage guides tailored to the workflow

**4. Test with real workflows**
- Generate systems for actual projects
- Validate that bridge agents preserve critical context
- Check that constitutional violations are caught

---

## Troubleshooting

### Command Not Found

**Problem**: `/generate-triads` doesn't work

**Solution**:
```bash
# Check if command file exists
ls .claude/commands/generate-triads.md

# If missing, re-run installer
./install.sh
```

### Hooks Not Executing

**Problem**: Knowledge graphs not updating

**Solution**:
```bash
# Make hooks executable
chmod +x .claude/hooks/*.py

# Check Python + NetworkX installed
python3 --version  # Should be 3.10+
python3 -c "import networkx; print('OK')"

# Verify settings.json
cat .claude/settings.json | python3 -m json.tool
```

### Generation Fails Partway

**Problem**: Generator stops mid-process

**Solution**:
```bash
# Check generator graph for incomplete state
cat .claude/graphs/generator_graph.json | python3 -m json.tool

# Clear and restart
rm .claude/graphs/generator_graph.json
> /generate-triads
```

### TRUST Violations

**Problem**: Work blocked by TRUST framework violations

**Solution**:
```bash
# View violations
cat .claude/constitutional/violations.json | python3 -m json.tool

# Common TRUST violations and fixes:
# - R (Require evidence): Add evidence field to node updates
# - T (Thorough): Increase confidence with better verification
# - R (Require evidence): Provide citations for claims
# - S (Show all work): Add decision rationale
# - T (Test assumptions): Validate assumptions

# Edit agent to comply with TRUST
open .claude/agents/{triad}/{agent}.md

# Re-run triad
> Start {TriadName}: [task]
```

### Context Not Preserved

**Problem**: Bridge agents losing information

**Solution**:
```bash
# Check bridge context files
ls .claude/graphs/bridge_*

# View compression
cat .claude/graphs/bridge_discovery_to_design.json

# If too aggressive compression, edit on_bridge_transition.py:
# Increase max_nodes from 20 to 30
# Adjust importance scoring weights
```

---

## Advanced Topics

### Creating Custom Commands

You can create additional slash commands:

```bash
# Create new command file
touch .claude/commands/my-command.md
```

```markdown
---
description: My custom command
---

# My Custom Command

[Command content here - will expand when user types /my-command]
```

### Integrating with MCP

If using Model Context Protocol (MCP):

```json
// In .claude/settings.json
{
  "mcp": {
    "servers": {
      "triad-server": {
        "command": "npx",
        "args": ["triad-mcp-server"]
      }
    }
  }
}
```

### Programmatic Access

You can invoke the generator programmatically:

```python
import subprocess
import json

# Run generator with preset answers
answers = {
    "workflow_type": "software-development",
    "phases": ["requirements", "design", "implementation"],
    "scale": "medium"
}

subprocess.run([
    "claude", "code", "--command", "/generate-triads",
    "--preset", json.dumps(answers)
])
```

---

## Further Reading

- **[Main README](README.md)** - Project overview
- **[Installation Guide](docs/INSTALLATION.md)** - Detailed setup
- **[Usage Guide](docs/USAGE.md)** - How to use generated triads
- **[Architecture](docs/ARCHITECTURE.md)** - System design
- **[Claude Code Docs](https://docs.claude.com/en/docs/claude-code)** - Official documentation

---

**Questions? Issues?**

- [GitHub Issues](https://github.com/reliable-agents-ai/triads/issues)
- [GitHub Discussions](https://github.com/reliable-agents-ai/triads/discussions)
- [Claude Code Community](https://claude.ai/community)

Happy triad building! 🎯
