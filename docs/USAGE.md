# Usage Guide

Learn how to use the Triad Generator system to create and work with custom multi-agent workflows.

---

## Table of Contents

- [Overview](#overview)
- [Generating Your Triad System](#generating-your-triad-system)
- [Working with Generated Triads](#working-with-generated-triads)
- [Knowledge Graphs](#knowledge-graphs)
- [Bridge Agents](#bridge-agents)
- [Constitutional Principles](#constitutional-principles)
- [Customization](#customization)
- [Best Practices](#best-practices)

---

## Overview

### The Two-Level System

**Level 1: Generator Triad (Meta-Level)**
- Domain Researcher → Workflow Analyst → Triad Architect
- Runs once to design your custom system
- Activated via `/generate-triads` command

**Level 2: Your Custom Triads (Generated)**
- 3-5 triads tailored to your workflow
- Each triad has 3 specialized agents
- Bridge agents preserve context between phases
- Used for your actual work

### Basic Workflow

```bash
# 1. Generate your system (once)
> /generate-triads
[Answer questions about your workflow]
[System generates custom triads]

# 2. Use your triads (ongoing work)

# Option A: Auto-Router (v0.2.0+, recommended)
> I need to analyze the authentication system
→ Auto-routes to Discovery triad

> Let's design OAuth2 integration now
→ Auto-routes to Design triad

> Can you implement the OAuth2 flow?
→ Auto-routes to Implementation triad

# Option B: Manual triad commands (still supported)
> Start Discovery: analyze authentication system
> Start Design: plan OAuth2 integration
> Start Implementation: build OAuth2 flow
```

**New in v0.2.0**: The auto-router eliminates manual triad commands. Just describe what you want in natural language and the system automatically routes to the appropriate triad. See the [Auto-Router section in README](../README.md#auto-router) for details.

**New in v0.7.0**: Multi-instance workflow management lets you work on multiple features concurrently. The system tracks each workflow separately with automatic progress tracking. See the [Workflow Management Guide](WORKFLOW_MANAGEMENT.md) for details.

---

## Generating Your Triad System

### Step 1: Launch the Generator

```bash
claude code
> /generate-triads
```

### Step 2: Interview with Domain Researcher

The Domain Researcher will ask about your workflow:

**Core Questions:**
1. What type of work do you need help with?
2. What phases does your work go through?
3. Where do you typically lose context or make mistakes?

**Example Response:**
```
I build software features for an existing web application.

My workflow:
1. Analyze requirements and existing code
2. Design the solution architecture
3. Implement the code
4. Review and test

I often lose requirements details when I get to coding,
and sometimes miss security considerations during design.
```

**Follow-up Questions:**
The researcher will ask 5-7 targeted questions like:
- Scale: How long are typical tasks? (hours/days/weeks)
- Team: Solo or collaborative work?
- Critical areas: What errors are most costly?
- Outputs: What artifacts do you need? (code, docs, tests)
- Domain specifics: Languages, frameworks, constraints

**Research Phase:**
```
🔍 Researching software development workflows...
[WebSearch: "software development workflow best practices"]
[WebSearch: "SDLC phases"]

📚 Research findings:
• Industry standard: Req → Design → Implementation → Testing
• Common failure: Requirements lost during coding ✓ (you mentioned this!)
• Critical: Security in design phase, code quality reviews
```

### Step 3: Design with Workflow Analyst

The analyst proposes 2-3 triad structures:

**Example:**
```
I've designed 2 options for your software development workflow:

OPTION A: 3 Triads (Simpler)
━━━━━━━━━━━━━━━━━━━━━━━━━━

Triad 1: Discovery
  • Codebase Analyst - Explores existing code
  • Requirements Gatherer - Documents needs
  • Knowledge Synthesizer [BRIDGE] - Integrates findings

Triad 2: Design
  • Knowledge Synthesizer [BRIDGE] - Carries requirements
  • Solution Architect [BRIDGE] - Plans solution
  • Security Analyst - Reviews for vulnerabilities

Triad 3: Implementation
  • Solution Architect [BRIDGE] - Carries design
  • Senior Developer - Implements code
  • Code Reviewer - Validates quality

Best for: Solo developers, quick iterations

OPTION B: 4 Triads (More specialized)
━━━━━━━━━━━━━━━━━━━━━━━━━━
[Similar structure with additional Testing triad]

Best for: Team environments, complex features

Which fits your workflow better?
```

**Refinement Questions:**
After you choose, the analyst asks 3-5 clarifying questions:
- Languages/frameworks (determines agent tools)
- Security focus areas (web, data, infrastructure)
- Review depth preferences
- Testing requirements
- Documentation needs

### Step 4: Generation with Triad Architect

The architect generates everything automatically:

```
🏗️ Generating your custom software development system...

✓ .claude/agents/discovery/codebase-analyst.md
✓ .claude/agents/discovery/requirements-gatherer.md
✓ .claude/agents/discovery/knowledge-synthesizer.md
✓ .claude/agents/design/knowledge-synthesizer.md
✓ .claude/agents/design/solution-architect.md
✓ .claude/agents/design/security-analyst.md
✓ .claude/agents/implementation/solution-architect.md
✓ .claude/agents/implementation/senior-developer.md
✓ .claude/agents/implementation/code-reviewer.md

✓ .claude/hooks/on_subagent_start.py
✓ .claude/hooks/on_subagent_end.py
✓ .claude/hooks/on_bridge_transition.py

✓ .claude/constitutional-principles.md
✓ .claude/WORKFLOW.md
✓ .claude/README.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ YOUR SOFTWARE DEVELOPMENT TRIAD SYSTEM IS READY!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

How to use:
> Start Discovery: analyze the authentication system
```

---

## Working with Generated Triads

### Starting a Triad

**Syntax:**
```bash
Start {TriadName}: {your task description}
```

**Examples:**
```bash
# Software Development
> Start Discovery: analyze the user authentication system
> Start Design: plan OAuth2 integration with existing auth
> Start Implementation: build OAuth2 login flow

# RFP Writing (if you generated for that domain)
> Start Analysis: review RFP requirements from proposal.pdf
> Start Strategy: develop win themes for cloud migration
> Start Writing: draft technical approach section

# Lead Generation
> Start Prospecting: find SaaS companies in fintech
> Start Enrichment: build profiles for top 20 prospects
> Start Outreach: personalize messaging for decision makers
```

### What Happens When You Start a Triad

**1. Agent Activation:**
All three agents in the triad activate and collaborate

**2. Knowledge Graph Building:**
```
Discovery Triad runs:
├─ Codebase Analyst explores src/auth/
├─ Requirements Gatherer documents needs
└─ Knowledge Synthesizer builds graph

Graph created: .claude/graphs/discovery_graph.json
```

**3. Work Output:**
Agents produce their specialized work:
- Analysis documents
- Design specifications
- Code implementations
- Review findings

**4. Context Capture:**
All findings, decisions, and uncertainties captured in knowledge graph

### Chaining Triads Together

**Natural Flow:**
```bash
# Phase 1: Discovery
> Start Discovery: analyze authentication system

[Discovery triad completes]
[Knowledge graph: discovery_graph.json created]

# Phase 2: Design
> Start Design: plan OAuth2 integration

[Knowledge Synthesizer (bridge) loads Discovery graph]
[Compresses to top 20 nodes]
[Brings forward to Design triad]
[Design proceeds with full requirements context - no loss!]

# Phase 3: Implementation
> Start Implementation: build OAuth2 flow

[Solution Architect (bridge) loads Design graph]
[Brings forward design decisions]
[Implementation has complete context]
```

**Key Benefit:** Each phase has full context from previous phases via bridge agents.

---

## Knowledge Graphs

### What They Capture

Knowledge graphs store everything learned during triad work:

**Node Types:**
- **Entity**: Things that exist (files, systems, users, components)
- **Concept**: Abstract ideas (patterns, principles, requirements)
- **Decision**: Choices made with rationale
- **Finding**: Discoveries and insights
- **Task**: Work items identified
- **Uncertainty**: Questions or unknowns

**Edge Types:**
- `relates_to`: General relationship
- `depends_on`: Dependency relationship
- `implements`: Implementation relationship
- `conflicts_with`: Conflicts or contradictions
- `influences`: Influence relationship

### Viewing Graphs

**Location:**
```bash
.claude/graphs/{triad_name}_graph.json
```

**View formatted:**
```bash
cat .claude/graphs/discovery_graph.json | python3 -m json.tool
```

**Example Graph:**
```json
{
  "nodes": [
    {
      "id": "auth_module",
      "type": "Entity",
      "label": "Authentication Module",
      "description": "JWT-based auth in src/auth/",
      "confidence": 0.95,
      "evidence": "Found in src/auth/jwt.py:15-89",
      "created_by": "codebase-analyst",
      "created_at": "2025-01-08T14:30:22Z"
    },
    {
      "id": "req_oauth2",
      "type": "Concept",
      "label": "OAuth2 Integration Requirement",
      "description": "Need to add OAuth2 for enterprise SSO",
      "confidence": 1.0,
      "evidence": "Requirements doc, stakeholder meeting",
      "created_by": "requirements-gatherer",
      "created_at": "2025-01-08T14:32:15Z"
    },
    {
      "id": "decision_strategy",
      "type": "Decision",
      "label": "Use OAuth2 library",
      "description": "Adopt authlib for OAuth2 implementation",
      "rationale": "Well-maintained, secure, good docs",
      "confidence": 0.88,
      "created_by": "knowledge-synthesizer",
      "created_at": "2025-01-08T14:35:00Z"
    }
  ],
  "links": [
    {
      "source": "req_oauth2",
      "target": "auth_module",
      "relation": "depends_on"
    },
    {
      "source": "decision_strategy",
      "target": "req_oauth2",
      "relation": "implements"
    }
  ]
}
```

### Graph Updates

**Agents update graphs automatically:**

Agents output special blocks that hooks process:
```
[GRAPH_UPDATE]
type: add_node
node_id: security_finding_1
node_type: Finding
label: "Potential SQL injection vulnerability"
description: "User input in src/db/query.py:45 not sanitized"
confidence: 0.92
evidence: "Line 45: cursor.execute(f'SELECT * FROM users WHERE id={user_id}')"
created_by: security-analyst
[/GRAPH_UPDATE]
```

The `on_subagent_end.py` hook:
1. Parses these blocks
2. Validates against constitutional principles
3. Updates the JSON file
4. Logs any violations

---

## Bridge Agents

### How They Work

**Bridge agents participate in 2 triads:**

```
Discovery Triad              Design Triad
├─ Codebase Analyst         ├─ Knowledge Synthesizer ◄───┐
├─ Requirements Gatherer    │  (same agent, carries context)
└─ Knowledge Synthesizer ───┘
```

**Context Compression:**

When a bridge agent transitions:

```python
# Load source graph
source_graph = load("discovery_graph.json")

# Score each node by importance
for node in source_graph:
    importance = (
        node.confidence *
        node.degree *  # how connected
        recency_factor *  # recent = higher score
        type_priority  # Decisions > Findings > Entities
    )

# Keep top 20 + their immediate neighbors
compressed = top_nodes(source_graph, n=20)

# Save for target triad
save("bridge_discovery_to_design.json", compressed)
```

**When target triad starts:**
```python
# Load compressed context
bridge_context = load("bridge_discovery_to_design.json")

# Inject into agent environment
agent_prompt += format_context(bridge_context)

# Agent has both:
# - Current triad's fresh graph
# - Critical context from previous triad
```

### Why Compression Matters

**Without compression:**
- Full graphs can be 1000+ nodes
- Exceeds context windows
- Slows processing
- Includes noise

**With compression:**
- Top 20 most important nodes
- ~80% size reduction
- Preserves critical context
- Fast processing
- Zero loss of key information

---

## TRUST Principles

### The TRUST Framework

Every agent follows the **TRUST framework** - 5 immutable rules:

| Letter | Principle | Description |
|--------|-----------|-------------|
| **T** | **Thorough over fast** | Verify thoroughly before claiming; never shortcut verification steps; take time to investigate properly |
| **R** | **Require evidence** | Triple-verify critical facts; cite sources for all claims; confidence scores must reflect certainty |
| **U** | **Uncertainty escalation** | Never guess when unsure; explicitly flag unknowns; ask for help when needed |
| **S** | **Show all work** | Show all reasoning; document decision rationale; make assumptions explicit |
| **T** | **Test assumptions** | Question all assumptions; verify inherited context; challenge uncited claims |

### How They're Enforced

**Architectural Enforcement:**

Python hooks check every agent output:

```python
# on_subagent_end.py
for update in graph_updates:
    # Check R: Require evidence
    if update.confidence > 0.7 and not update.evidence:
        log_violation("TRUST-R: Missing evidence for high-confidence claim")
        block_completion()

    # Check U: Uncertainty escalation
    if update.type == "Uncertainty" and not update.escalated:
        log_violation("TRUST-U: Uncertainty not escalated")

    # Check T: Test assumptions
    if "assume" in update.description.lower() and not update.validated:
        log_violation("TRUST-T: Unvalidated assumption")
```

**Violations Logged:**
```bash
cat .claude/constitutional/violations.json
```

```json
{
  "violations": [
    {
      "timestamp": "2025-01-08T15:22:10Z",
      "agent": "solution-architect",
      "principle": "TRUST-R: Require evidence",
      "description": "High confidence (0.9) without evidence",
      "context": "Node: architecture_decision_api_gateway",
      "severity": "high"
    }
  ]
}
```

---

## Customization

### Modifying Agents

**Edit agent behavior:**
```bash
# Open agent file
open .claude/agents/discovery/codebase-analyst.md

# Modify:
# - Identity & Purpose section
# - Tools and capabilities
# - TRUST focus areas
# - Workflow steps

# Save - changes apply immediately
```

**Example customization:**
```markdown
## Tools Available

- `Glob` tool for finding files matching patterns
- `Grep` tool for searching code
- `Read` tool for reading files
- `Bash` tool for running git commands

## Additional Focus (Custom)

When analyzing Python code:
- Check for type hints
- Look for docstrings
- Identify test coverage gaps
- Flag deprecated imports
```

### Adding a Triad

**Method 1: Re-run generator**
```bash
> /generate-triads --extend

# Generator will:
# - Load existing system
# - Ask what new phase you need
# - Design new triad
# - Generate and integrate
```

**Method 2: Manual creation**
```bash
# 1. Create triad folder
mkdir -p .claude/agents/new_triad

# 2. Create 3 agent files
# Use existing agents as templates
cp .claude/agents/discovery/codebase-analyst.md .claude/agents/new_triad/specialist-a.md

# 3. Edit each agent file
# 4. Update settings.json to register triad
```

### Adjusting TRUST Principles

**Edit global TRUST principles:**
```bash
open .claude/constitutional-principles.md

# Modify the TRUST framework
# Add domain-specific rules
# Adjust enforcement severity
```

**Edit per-agent checkpoints:**
```bash
open .claude/constitutional/checkpoints.json
```

```json
{
  "agents": {
    "security-analyst": {
      "required_fields": ["evidence", "severity", "remediation"],
      "min_confidence": 0.9,
      "must_flag_uncertainties": true
    },
    "code-reviewer": {
      "required_fields": ["evidence", "location"],
      "min_confidence": 0.8
    }
  }
}
```

---

## Best Practices

### Starting Out

1. **Be specific in your task descriptions**
   - ❌ "Start Discovery: look at the code"
   - ✅ "Start Discovery: analyze authentication system in src/auth/"

2. **Follow the natural workflow**
   - Complete Discovery before Design
   - Complete Design before Implementation
   - Let bridge agents carry context

3. **Review knowledge graphs between phases**
   ```bash
   cat .claude/graphs/discovery_graph.json | python3 -m json.tool | less
   ```

4. **Check for uncertainties**
   - Look for nodes with type: "Uncertainty"
   - Resolve before proceeding to next phase

### Working Efficiently

1. **Use triads for appropriate scope**
   - Small tasks: Use single triad
   - Medium tasks: 2-3 triads
   - Large tasks: Full workflow

2. **Leverage bridge agents**
   - They automatically preserve context
   - No need to repeat information
   - Trust the compression algorithm

3. **Monitor TRUST violations**
   ```bash
   cat .claude/constitutional/violations.json
   ```
   - Address patterns (same agent violating TRUST repeatedly)
   - Adjust agent prompts if needed

### Maintaining Quality

1. **Verify evidence for critical decisions**
   - Check that high-confidence nodes have evidence
   - Validate sources cited
   - Question assumptions

2. **Review bridge transitions**
   ```bash
   cat .claude/graphs/bridge_discovery_to_design.json
   ```
   - Ensure critical context preserved
   - Check that top 20 includes key decisions

3. **Update agents based on experience**
   - Add domain-specific instructions
   - Refine TRUST checkpoints
   - Document learned patterns

### Troubleshooting

**Graph not updating:**
```bash
# Check hook execution
ls -la .claude/hooks/
chmod +x .claude/hooks/*.py

# Test manually
python3 .claude/hooks/on_subagent_end.py
```

**Context not preserved:**
```bash
# Check bridge graph exists
ls .claude/graphs/bridge_*.json

# Verify compression ran
cat .claude/graphs/bridge_*.json | python3 -m json.tool
# Should have ~20 nodes
```

**Agent behavior issues:**
```bash
# Review agent file
cat .claude/agents/{triad}/{agent}.md

# Check TRUST violations
cat .claude/constitutional/violations.json

# Review recent graph updates
cat .claude/graphs/{triad}_graph.json | python3 -m json.tool
```

---

## Next Steps

- **See examples**: [Examples Guide](EXAMPLES.md)
- **Understand architecture**: [Architecture](ARCHITECTURE.md)
- **Troubleshoot issues**: [Troubleshooting](TROUBLESHOOTING.md)
- **Get help**: [FAQ](FAQ.md)

---

**Ready to master your triad system? Start experimenting!**

```bash
> Start Discovery: [your task]
```
