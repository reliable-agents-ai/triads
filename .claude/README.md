# Triad Generator System

**Version 1.0** | Self-discovering multi-agent workflow optimizer

---

## What Is This?

The **Triad Generator** is a meta-AI system that researches your workflow and designs custom teams of AI agents optimized for how you work.

Instead of generic AI assistants, you get **specialists organized in triads** (groups of 3) with **bridge agents** that preserve context between phases.

### Key Benefits

✅ **No context loss** - Bridge agents carry information forward automatically
✅ **Constitutional quality** - Built-in reliability principles prevent errors
✅ **Custom-designed** - Researched and tailored to your specific workflow
✅ **Self-contained** - Everything lives in `.claude/` folder
✅ **Local-first** - NetworkX graphs, no external services

---

## Quick Start

### Prerequisites

- **Python 3.10+** with NetworkX
- **Claude Code CLI** installed
- A git repository (any project)

### Installation

```bash
# Run the installer
./install-triads.sh

# Or manual setup:
mkdir -p .claude
# (installer will populate .claude/ folder)
```

### First Use

```bash
# Launch Claude Code
claude code

# Run the generator
> /generate-triads

# Follow the interactive prompts
# Answer questions about your workflow
# Get a custom triad system designed for you
```

---

## How It Works

### The Generator Triad (Meta-Level)

The system starts with 3 meta-agents that design your system:

```
┌─────────────────────┐
│ Domain Researcher   │  Asks questions, researches your domain
└──────────┬──────────┘
           │ Discovers workflow phases and needs
           ▼
┌─────────────────────┐
│ Workflow Analyst    │  Designs optimal triad structure
└──────────┬──────────┘
           │ Creates agent specifications
           ▼
┌─────────────────────┐
│ Triad Architect     │  Generates all files
└─────────────────────┘
```

### Your Custom Triads (Generated)

After generation, you'll have 3-5 triads like:

```
Discovery Triad       Design Triad         Implementation Triad
├─ Agent A           ├─ Bridge Agent 1 ◄──┘
├─ Agent B           ├─ Agent C
└─ Bridge Agent 1 ───┴─ Agent D
                     └─ Bridge Agent 2 ────┐
                                            │
                                     Validation Triad
                                     ├─ Bridge Agent 2
                                     ├─ Agent E
                                     └─ Agent F
```

**Bridge agents** (the overlapping ones) prevent context loss by:
- Participating in 2 triads simultaneously
- Compressing context intelligently (top 20 nodes)
- Preserving decisions, uncertainties, and key findings

---

## Core Concepts

### Triads (Groups of 3)

Based on Georg Simmel's sociological research:
- **Optimal size**: Small enough for accountability, large enough for diversity
- **Mediation**: Third member can resolve conflicts
- **Efficient**: Only 3 communication channels (vs 28 in 8-person team)
- **Proven**: Used in sports, military, business

### Overlapping Structure

Bridge agents create context flow:
```
Triad A          Triad B
Agent 1          Bridge Agent ← shared
Agent 2          Agent 3
Bridge Agent     Agent 4
```

**Result**: ~40% faster than hierarchical supervisor patterns (research/triads.md:145)

### Constitutional Principles

Every agent follows immutable principles:

1. **Thoroughness Over Speed** - Verify thoroughly, never shortcut
2. **Evidence-Based Claims** - Triple-verify, cite sources
3. **Uncertainty Escalation** - Never guess, escalate when unsure
4. **Complete Transparency** - Show all reasoning
5. **Assumption Auditing** - Question and validate everything

Different workflows prioritize different principles (auto-configured by generator).

### Knowledge Graphs

Each triad builds a NetworkX graph:
```json
{
  "nodes": [
    {
      "id": "finding_1",
      "type": "Finding",
      "label": "Security vulnerability in auth module",
      "confidence": 0.95,
      "evidence": "src/auth/jwt.py:45-67",
      "created_by": "code-analyst"
    }
  ],
  "links": [
    {
      "source": "finding_1",
      "target": "decision_1",
      "relation": "influences"
    }
  ]
}
```

**Location**: `.claude/graphs/{triad_name}_graph.json`

---

## Usage

### Invoking a Triad

Once your system is generated:

```bash
# Start the first triad
> Start {TriadName}: [describe your task]

# Example for software development:
> Start Discovery: analyze the authentication system

# Example for RFP writing:
> Start Analysis: review this RFP document [paste or provide path]
```

### Checking Progress

```bash
# View a triad's knowledge graph
cat .claude/graphs/discovery_graph.json | python3 -m json.tool

# Check for constitutional violations
cat .claude/constitutional/violations.json

# View all graphs
ls -lh .claude/graphs/
```

### Customizing Agents

Edit agent behavior:
```bash
# Open an agent's definition
open .claude/agents/{triad_name}/{agent_name}.md

# Modify the prompts, tools, or constraints
# Save and run - changes take effect immediately
```

### Adding Triads

Run the generator again:
```bash
> /generate-triads --extend

# Or start fresh:
> /generate-triads --redesign
```

---

## File Structure

After generation:

```
.claude/
├── commands/
│   └── generate-triads.md          # Slash command entry point
│
├── generator/                       # Meta-level system (ships with install)
│   ├── agents/
│   │   ├── domain-researcher.md    # Meta-agent 1
│   │   ├── workflow-analyst.md     # Meta-agent 2
│   │   └── triad-architect.md      # Meta-agent 3
│   └── lib/
│       └── templates.py             # Code generation templates
│
├── agents/                          # YOUR CUSTOM AGENTS (generated)
│   ├── {triad_1}/
│   │   ├── {agent_a}.md
│   │   ├── {agent_b}.md
│   │   └── {agent_c}.md
│   ├── {triad_2}/
│   │   └── ...
│   └── bridges/
│       ├── {bridge_agent_1}.md
│       └── {bridge_agent_2}.md
│
├── hooks/                           # Lifecycle automation (generated)
│   ├── on_subagent_start.py        # Loads context before agent runs
│   ├── on_subagent_end.py          # Updates graph after completion
│   └── on_bridge_transition.py     # Handles context handoff
│
├── graphs/                          # Knowledge graphs (runtime)
│   ├── {triad_1}_graph.json
│   ├── {triad_2}_graph.json
│   ├── bridge_contexts/
│   └── generator_graph.json        # Generator's own graph
│
├── constitutional/                  # Quality enforcement (generated)
│   ├── principles.md                # Your workflow's principles
│   ├── checkpoints.json             # Per-agent checks
│   └── violations.json              # Logged violations (if any)
│
├── settings.json                    # Claude Code hook configuration
├── README.md                        # This file (generated with your workflow)
└── WORKFLOW.md                      # Your specific usage guide (generated)
```

---

## How Generation Works

### Step 1: Research (Domain Researcher)

```
User: /generate-triads

Domain Researcher:
"What type of work do you need help with?"

User: "I write RFP responses"

Domain Researcher:
🔍 Researching RFP response workflows...
[WebSearch: "RFP response process"]
[WebSearch: "bid writing phases"]

📚 Findings: 5-phase process, compliance critical...

"Tell me more about..."
[Asks 5-7 targeted questions]
```

### Step 2: Design (Workflow Analyst)

```
Workflow Analyst:
"Based on your RFP workflow, here are 2 options:

OPTION A: 3 Triads (Simpler)
OPTION B: 4 Triads (More specialized)

Which fits better?"

User: "Option B"

Workflow Analyst:
"Let me finalize the details..."
[Asks 3-5 refinement questions]

"Here's the detailed design..."
[Shows complete triad structure]
```

### Step 3: Generate (Triad Architect)

```
Triad Architect:
"Generating your custom system..."

✓ Creating 12 agent files
✓ Generating hooks
✓ Setting up constitutional checks
✓ Writing documentation

✅ COMPLETE! Your RFP Response Triad System is ready.

Try: Start Analysis: [paste your RFP]
```

---

## Examples

### Software Development

**Generated triads**:
- Discovery (analyze codebase)
- Design (plan solution)
- Implementation (code + review)

**Bridge agents**:
- Knowledge Synthesizer (Discovery → Design)
- Solution Architect (Design → Implementation)

### RFP/Bid Writing

**Generated triads**:
- Analysis (extract requirements)
- Strategy (develop win themes)
- Writing (draft sections)
- Validation (compliance check)

**Bridge agents**:
- Requirements Synthesizer (Analysis → Strategy)
- Win Strategist (Strategy → Writing)
- Technical Specialist (Writing → Validation)

### Lead Generation

**Generated triads**:
- Prospecting (find leads)
- Enrichment (build profiles)
- Outreach Prep (personalize messaging)

**Bridge agents**:
- Prospect Synthesizer (Prospecting → Enrichment)
- Insight Generator (Enrichment → Outreach)

---

## Advanced Topics

### Context Compression

Bridge agents use importance scoring:
```python
importance = (
    confidence * 0.3 +
    node_degree * 0.3 +
    recency * 0.2 +
    type_priority * 0.2
)

# Type priorities:
# Decision: 1.5
# Uncertainty: 1.5
# Finding: 1.2
# Entity: 1.0
```

Only top 20 nodes + 1-hop neighbors carry forward.

### Constitutional Enforcement

Hooks check every agent output:
- Missing evidence → HIGH severity violation
- Low confidence (<0.7) → Escalation required
- Incomplete assumptions → MEDIUM severity

Violations logged to `.claude/constitutional/violations.json`

In strict mode (generated for high-stakes workflows), violations block completion.

### Knowledge Graph Operations

```python
import networkx as nx
import json

# Load a triad's graph
with open('.claude/graphs/discovery_graph.json') as f:
    data = json.load(f)
    G = nx.node_link_graph(data)

# Query
decisions = [n for n in G.nodes() if G.nodes[n]['type'] == 'Decision']
uncertainties = [n for n in G.nodes() if G.nodes[n]['type'] == 'Uncertainty']

# Find paths
path = nx.shortest_path(G, source='finding_1', target='decision_1')
```

### Extending the System

Add a triad manually:
```bash
# 1. Create folder
mkdir .claude/agents/new_triad

# 2. Create 3 agent files (use existing as templates)
cp .claude/agents/discovery/agent_a.md .claude/agents/new_triad/

# 3. Edit and customize

# 4. Update settings.json to include new triad
```

---

## Troubleshooting

### Hooks Not Running

```bash
# Check hook files are executable
chmod +x .claude/hooks/*.py

# Verify settings.json
cat .claude/settings.json

# Check Python/NetworkX installed
python3 -c "import networkx; print('OK')"
```

### Graph Not Updating

```bash
# Check if agent outputs [GRAPH_UPDATE] blocks
# Look for .claude/graphs/.output_* temp files

# Manually run hook
python3 .claude/hooks/on_subagent_end.py
```

### Constitutional Violations

```bash
# View violations
cat .claude/constitutional/violations.json | python3 -m json.tool

# Understand the issue
# Edit agent to fix (add evidence, raise confidence, etc.)
```

### Generation Failed

```bash
# Re-run with clean state
rm -rf .claude/agents
rm -rf .claude/graphs/*.json

# Run generator again
> /generate-triads
```

---

## Research Background

This system is based on:

1. **Simmel's Triad Theory** (sociology) - research/triads.md:3-8
2. **Overlapping Triads Pattern** (organizational design) - research/triads.md:39-105
3. **Constitutional AI Principles** (reliability) - research/agent-principles.md
4. **Autonomous Schema Induction** (knowledge graphs) - research/knowledge-memory.md:184-198

See `research/` folder for full academic foundations.

---

## Support & Development

**Repository**: [Your repo URL]

**Documentation**: This folder contains:
- `README.md` (this file) - System overview
- `WORKFLOW.md` (generated) - Your specific usage guide
- `constitutional/principles.md` (generated) - Your workflow principles
- `generator/agents/*.md` - Meta-agent definitions

**Issues**: Open an issue if you find bugs

**Contributions**: PRs welcome for:
- New domain patterns
- Agent role templates
- Hook improvements
- Documentation

---

## License

[Your license choice]

---

## Acknowledgments

Built on insights from:
- Georg Simmel (triad theory)
- Anthropic Claude (constitutional AI)
- LangChain/LangGraph (agent frameworks)
- NetworkX (graph library)

---

**Ready to generate your custom triad system?**

```bash
claude code
> /generate-triads
```
