# Triads Plugin: Claude Code Component Overlay

**How the Triads System Layers on Top of Claude Code**

**Version**: 1.0
**Date**: 2025-10-27
**Purpose**: Understand how triads generator and plugin architecture overlay on Claude Code's component system

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [The Overlay Concept](#2-the-overlay-concept)
3. [Plugin Architecture](#3-plugin-architecture)
4. [Generator System](#4-generator-system)
5. [Runtime System](#5-runtime-system)
6. [Component Mapping](#6-component-mapping)
7. [Lifecycle Flow](#7-lifecycle-flow)
8. [Installation & Distribution](#8-installation--distribution)
9. [Examples](#9-examples)

---

## 1. Executive Summary

### What Is Triads?

**Triads** is a Claude Code plugin that provides:
1. **Generator System**: Meta-agents that design custom multi-agent workflows
2. **Runtime System**: Hooks, commands, and tools that manage workflow execution
3. **Knowledge Management**: Graph-based context preservation across agent interactions

### How It Overlays

```
┌─────────────────────────────────────────────────────────────┐
│                    Claude Code (Base)                        │
│  Components: Agents, Skills, Hooks, Commands, MCP Tools     │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   │ (Triads Plugin Installed)
                   ↓
┌─────────────────────────────────────────────────────────────┐
│                 Triads Plugin (Overlay)                      │
├─────────────────────────────────────────────────────────────┤
│  ADDS:                                                       │
│  • Generator meta-agents (design workflow)                   │
│  • Supervisor agent (route requests)                         │
│  • Workflow triads (execute work)                            │
│  • Knowledge management hooks (preserve context)             │
│  • Slash commands (user interface)                           │
│  • MCP tools (routing, knowledge access)                     │
└─────────────────────────────────────────────────────────────┘
```

**Key Insight**: Triads is **not a replacement** for Claude Code - it's an **enhancement layer** that adds workflow orchestration, context preservation, and meta-generation capabilities on top of Claude Code's existing agent system.

---

## 2. The Overlay Concept

### Base Layer: Claude Code

**What Claude Code Provides**:
- Agent invocation via Task tool
- Hook system for lifecycle interception
- Slash commands for user interaction
- MCP tools for external integrations
- Skills for progressive disclosure
- Project instructions (CLAUDE.md)
- Output styles for personality

**Limitations**:
- No built-in workflow orchestration
- No context preservation between agents
- No automatic agent generation
- No knowledge graph management
- Manual agent creation

### Overlay Layer: Triads Plugin

**What Triads Adds**:
- **Workflow Orchestration**: Supervisor routes to appropriate triads
- **Context Preservation**: Knowledge graphs + bridge agents
- **Meta-Generation**: Generator triad creates custom agents
- **Quality Gates**: Constitutional checkpoints via hooks
- **Lifecycle Management**: Hooks for session start, tool use, stop
- **User Interface**: Slash commands for knowledge/workflow management

**Integration Points**:
```
Claude Code Component → Triads Uses It For
────────────────────────────────────────────
Agents (.claude/agents/) → Custom workflow triads + supervisor
Hooks (.claude/hooks/)   → Knowledge injection, validation gates
Commands (.claude/commands/) → /knowledge-*, /workflow-*, /generate-workflow
MCP Tools (src/triads/) → Router, knowledge access, integrity checks
Settings (hooks.json)    → Plugin hook registration
```

---

## 3. Plugin Architecture

### Plugin Manifest

**File**: `.claude-plugin/plugin.json`

```json
{
  "name": "triads",
  "version": "0.9.0-alpha.1",
  "description": "Triad workflow system for Claude Code",
  "author": {
    "name": "Reliable Agents AI",
    "url": "https://github.com/reliable-agents-ai/triads"
  },
  "repository": "https://github.com/reliable-agents-ai/triads",
  "keywords": [
    "workflow",
    "agents",
    "knowledge-management",
    "productivity",
    "context-preservation"
  ],
  "license": "MIT",
  "hooks": "./hooks/hooks.json"
}
```

**What This Does**:
- Registers plugin with Claude Code
- Points to hook configuration
- Provides metadata for plugin marketplace
- Enables `CLAUDE_PLUGIN_ROOT` environment variable

---

### Hook Registration

**File**: `hooks/hooks.json`

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/session_start.py"
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/user_prompt_submit.py"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/on_stop.py"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/on_pre_experience_injection.py"
          }
        ]
      }
    ]
  }
}
```

**Hook Purposes**:

| Hook | Purpose | Triads Usage |
|------|---------|--------------|
| **SessionStart** | Fires when Claude Code session starts | Display welcome message, check for updates, initialize knowledge graphs |
| **UserPromptSubmit** | Fires on every user message | Supervisor routing logic, workflow detection, knowledge graph queries |
| **PreToolUse** | Fires before any tool use | Experience injection (checklist/pattern/warning delivery), knowledge validation gates |
| **Stop** | Fires when agent completes task | Save knowledge graphs, update workflow progress |

---

### File Structure

**Complete plugin installation**:

```
project-root/
├── .claude-plugin/
│   ├── plugin.json                   # Plugin manifest
│   └── marketplace.json               # Marketplace listing
│
├── .claude/
│   ├── agents/
│   │   ├── supervisor/
│   │   │   └── supervisor.md         # ADDED: Routes work to triads
│   │   │
│   │   ├── idea-validation/          # ADDED: Generated triad
│   │   │   ├── research-analyst.md
│   │   │   ├── community-researcher.md
│   │   │   └── validation-synthesizer.md (bridge)
│   │   │
│   │   ├── design/                   # ADDED: Generated triad
│   │   │   ├── solution-architect.md
│   │   │   └── design-bridge.md (bridge)
│   │   │
│   │   ├── implementation/           # ADDED: Generated triad
│   │   │   ├── design-bridge.md (receives context)
│   │   │   ├── senior-developer.md
│   │   │   └── test-engineer.md
│   │   │
│   │   ├── garden-tending/           # ADDED: Generated triad
│   │   │   ├── cultivator.md
│   │   │   ├── pruner.md
│   │   │   └── gardener-bridge.md (dual-output)
│   │   │
│   │   ├── deployment/               # ADDED: Generated triad
│   │   │   ├── release-manager.md
│   │   │   └── documentation-updater.md
│   │   │
│   │   └── system/                   # ADDED: Meta-level agents
│   │       ├── verification-agent.md
│   │       └── research-agent.md
│   │
│   ├── commands/
│   │   ├── knowledge-help.md         # ADDED: /knowledge-help
│   │   ├── knowledge-status.md       # ADDED: /knowledge-status
│   │   ├── knowledge-search.md       # ADDED: /knowledge-search <query>
│   │   ├── knowledge-show.md         # ADDED: /knowledge-show <triad>
│   │   ├── knowledge-validate.md     # ADDED: /knowledge-validate <lesson_id>
│   │   ├── knowledge-contradict.md   # ADDED: /knowledge-contradict <lesson_id>
│   │   ├── knowledge-review-uncertain.md # ADDED: /knowledge-review-uncertain
│   │   ├── generate-workflow.md      # ADDED: /generate-workflow
│   │   ├── upgrade-agents.md         # ADDED: /upgrade-agents
│   │   ├── workflows-list.md         # ADDED: /workflows-list
│   │   └── workflows-resume.md       # ADDED: /workflows-resume
│   │
│   ├── graphs/
│   │   ├── generator_graph.json      # ADDED: Generator triad knowledge
│   │   ├── supervisor_graph.json     # ADDED: Supervisor routing history
│   │   ├── idea-validation_graph.json # ADDED: Triad knowledge
│   │   ├── design_graph.json         # ADDED: Triad knowledge
│   │   ├── implementation_graph.json # ADDED: Triad knowledge
│   │   ├── garden-tending_graph.json # ADDED: Triad knowledge
│   │   ├── deployment_graph.json     # ADDED: Triad knowledge
│   │   └── system_graph.json         # ADDED: System-level knowledge
│   │
│   ├── workflows/
│   │   └── proven/                   # ADDED: Seed workflows
│   │       ├── bug-fix.yaml
│   │       ├── feature-dev.yaml
│   │       ├── performance.yaml
│   │       ├── refactoring.yaml
│   │       └── investigation.yaml
│   │
│   ├── generator/                    # ADDED: Generator meta-system
│   │   └── lib/
│   │       └── (Python templates)
│   │
│   └── output-styles/
│       └── constitutional.md         # ADDED: TDD + constitutional principles
│
├── hooks/
│   ├── hooks.json                    # ADDED: Hook registration
│   ├── session_start.py              # ADDED: Session initialization
│   ├── user_prompt_submit.py         # ADDED: Supervisor routing
│   ├── on_stop.py                    # ADDED: Knowledge saving
│   └── on_pre_experience_injection.py # ADDED: Experience delivery
│
├── src/triads/                       # ADDED: Python package
│   ├── km/                           # Knowledge management
│   │   ├── graph_access.py           # Load/save graphs
│   │   ├── schema_validator.py       # Validate graph structure
│   │   ├── agent_output_validator.py # Parse [GRAPH_UPDATE] blocks
│   │   ├── backup_manager.py         # Automatic backups
│   │   └── integrity_checker.py      # Detect corruption
│   │
│   ├── router/                       # Workflow routing
│   │   ├── repository.py             # Router service
│   │   ├── matching.py               # Keyword matching
│   │   ├── classification.py         # LLM classification
│   │   └── entrypoint.py             # MCP tools (route_prompt, get_current_triad)
│   │
│   └── utils/
│       └── file_operations.py        # Atomic writes
│
├── pyproject.toml                    # ADDED: Python package config
├── CLAUDE.md                         # ADDED: Project instructions
└── README.md                         # ADDED: Usage guide
```

**Legend**:
- ADDED: Files created by triads plugin installation
- (No markers): User's existing project files (unchanged)

---

## 4. Generator System

### Purpose

The **Generator System** is a meta-level triad that **designs and creates custom workflow triads** for users.

**When Used**: Once during initial setup (via `/generate-triads` command, deprecated in v0.9+)

**Why Deprecated**: In v0.9+, the system ships with 5 proven seed workflows (bug-fix, feature-dev, performance, refactoring, investigation). The supervisor can generate new workflows on-demand when gaps are detected (via `/generate-workflow`).

### Generator Triad Structure

**Components** (historically):
1. **Domain Researcher** (gatherer)
   - Interviews user about their workflow
   - Performs web research on domain
   - Identifies workflow phases
   - Documents pain points

2. **Workflow Analyst** (processor)
   - Analyzes workflow structure
   - Designs 2-3 triad options
   - Gets user choice
   - Creates agent specifications

3. **Triad Architect** (bridge/generator)
   - Loads design specifications
   - Generates agent markdown files
   - Creates Python hooks
   - Writes documentation

**Current State (v0.9+)**:
- Generator triad deprecated for initial setup
- Seed workflows provided out-of-box
- Organic generation mode used for gap-detected workflows
- Workflow Analyst invoked directly by Supervisor (skips broad domain research)

### How Generator Uses Claude Code Components

| Generator Agent | Uses Claude Code Component | For What |
|-----------------|----------------------------|----------|
| Domain Researcher | WebSearch, WebFetch tools | Research user's domain, industry patterns |
| Domain Researcher | AskUserQuestion tool | Interview user about workflow |
| Domain Researcher | Read, Grep, Glob tools | Examine user's codebase |
| Workflow Analyst | Write tool | Create agent specifications in knowledge graph |
| Triad Architect | Write tool | Generate agent .md files, hooks, configs |
| All | Knowledge graphs (.claude/graphs/) | Preserve context across generator agents |

---

### Generator Knowledge Graph

**File**: `.claude/graphs/generator_graph.json`

**Contents**:
```json
{
  "nodes": [
    {
      "id": "workflow_discovery",
      "type": "Finding",
      "label": "User Workflow Discovery",
      "description": "User builds software features in phases: discover → design → implement → refine → deploy",
      "confidence": 1.0,
      "evidence": "User interview 2025-10-15",
      "created_by": "domain-researcher"
    },
    {
      "id": "triad_design_option_1",
      "type": "Decision",
      "label": "4-Triad Structure",
      "description": "Design → Implementation → Garden Tending → Deployment",
      "alternatives": ["3-triad", "5-triad"],
      "chosen": true,
      "confidence": 0.95,
      "created_by": "workflow-analyst"
    },
    {
      "id": "agent_spec_senior_developer",
      "type": "Concept",
      "label": "Senior Developer Agent Specification",
      "description": "Writes production code, follows ADRs, uses safe refactoring",
      "tools": ["Read", "Write", "Edit", "Bash"],
      "created_by": "triad-architect"
    }
  ],
  "edges": [
    {
      "source": "workflow_discovery",
      "target": "triad_design_option_1",
      "relationship": "informs"
    },
    {
      "source": "triad_design_option_1",
      "target": "agent_spec_senior_developer",
      "relationship": "requires"
    }
  ]
}
```

**Purpose**:
- Preserves generation decisions
- Enables regeneration if needed
- Documents why agents were created
- Provides audit trail

---

## 5. Runtime System

### Purpose

The **Runtime System** executes user's actual work using generated triads.

**When Used**: Continuously during development work

### Components

#### 1. Supervisor Agent

**File**: `.claude/agents/supervisor/supervisor.md`

**Purpose**: Routes user requests to appropriate workflows

**How It Uses Claude Code**:
- Registered as agent (invoked via Task tool or hook)
- Uses ALL tools (unique privilege)
- Injected into every user message via UserPromptSubmit hook
- Makes routing decisions using classification logic

**Workflow**:
```
User: "There's a memory leak in the router"
  ↓
UserPromptSubmit hook fires
  ↓
Supervisor injected into context
  ↓
Classifies: bug-fix workflow (confidence: 0.95)
  ↓
Suggests: "Start Bug Fix: memory leak in router"
  ↓
User confirms
  ↓
Invokes bug-fix workflow (3 triads)
```

**Configuration**:
```yaml
---
name: supervisor
triad: supervisor
role: orchestrator
tools: ALL
scope: meta
---
```

**Key Feature**: Supervisor is **meta-level** - operates above workflows, not within them.

---

#### 2. Workflow Triads

**Structure**: 3 agents per triad (gatherer → processor → bridge)

**Example: Bug Fix Workflow**

```yaml
# .claude/workflows/proven/bug-fix.yaml
name: Bug Fix
problem_type: bug
description: Systematic bug investigation and resolution
triads:
  - bug-investigation-triad
  - bug-fixing-triad
  - verification-triad
when_to_use: Clear bug with error message or failing test
```

**Triad Sequence**:
1. **Bug Investigation Triad**
   - analyze → reproduce → diagnose (bridge)

2. **Bug Fixing Triad**
   - diagnose (receives context) → fix → test (bridge)

3. **Verification Triad**
   - test (receives context) → regression-test → document

**How They Use Claude Code**:
- Each agent is a `.claude/agents/{triad}/{agent}.md` file
- Agents invoked sequentially via Task tool
- Internal handoffs use knowledge graphs
- Bridge agents compress context between triads

---

#### 3. Knowledge Graphs

**One graph per triad** + **bridge graphs** for context transfer

**Example Flow**:

```
Idea Validation Triad:
  research-analyst creates nodes:
    - finding: "LangGraph has pause/resume built-in"
    - finding: "Current execution is stateless"

  validation-synthesizer (bridge) compresses top-20 nodes
    → Saves to bridge_idea_to_design.json

Design Triad:
  validation-synthesizer (receives bridge context)
    → Loads bridge_idea_to_design.json
    → Has requirements without re-research

  solution-architect creates nodes:
    - decision: "Use LangGraph interrupt() method"
    - concept: "Add checkpoint storage"

  design-bridge compresses top-20 nodes
    → Saves to bridge_design_to_implementation.json

Implementation Triad:
  design-bridge (receives bridge context)
    → Loads bridge_design_to_implementation.json
    → Has design without re-decisions

  ... and so on
```

**File Locations**:
```
.claude/graphs/
├── idea-validation_graph.json         # Triad graph
├── design_graph.json                  # Triad graph
├── implementation_graph.json          # Triad graph
├── bridge_idea_to_design.json         # Context transfer
├── bridge_design_to_implementation.json # Context transfer
└── feedback_garden_to_design.json     # Feedback loop
```

---

#### 4. Hooks

**Purpose**: Lifecycle automation and quality enforcement

**SessionStart Hook**:
```python
# hooks/session_start.py

def on_session_start():
    """Display welcome, initialize graphs, check for updates"""

    print("🔺 Triads v0.9.0-alpha.1")
    print("📚 Knowledge Management: ACTIVE")
    print("🧭 Supervisor: READY")

    # Initialize knowledge graphs if missing
    ensure_graphs_exist()

    # Check for agent updates
    check_agent_versions()

    return ""  # No context injection
```

**UserPromptSubmit Hook**:
```python
# hooks/user_prompt_submit.py

def on_user_prompt_submit(user_message):
    """Inject supervisor routing logic"""

    # Load supervisor agent definition
    supervisor = load_agent("supervisor/supervisor.md")

    # Inject supervisor instructions
    return f"""
    {supervisor}

    User Message: {user_message}

    Determine if this is:
    - Q&A (answer directly)
    - Work request (route to workflow)
    """
```

**PreToolUse Hook**:
```python
# hooks/on_pre_experience_injection.py

def on_pre_tool_use(tool_name, tool_input, description):
    """Inject relevant checklists/patterns/warnings"""

    # Query knowledge graphs for relevant experience
    experience = query_experience(
        tool_name=tool_name,
        file_patterns=extract_files(tool_input),
        action_keywords=extract_keywords(description)
    )

    if experience:
        return format_experience_injection(experience)

    return ""  # No injection
```

**Stop Hook**:
```python
# hooks/on_stop.py

def on_stop():
    """Save knowledge graphs, update progress"""

    # Save all modified graphs
    save_all_graphs()

    # Update workflow progress
    update_workflow_status()

    return ""
```

---

#### 5. Slash Commands

**Purpose**: User interface for knowledge and workflow management

**Knowledge Management Commands**:

| Command | Purpose | Implementation |
|---------|---------|----------------|
| `/knowledge-help` | Show knowledge management guide | Markdown file with instructions |
| `/knowledge-status` | Show statistics (lessons, confidence) | Python script queries graphs |
| `/knowledge-search <query>` | Search across all graphs | Python script with text search |
| `/knowledge-show <triad>` | Display triad's knowledge | Python script loads graph, formats output |
| `/knowledge-validate <id>` | Manually increase confidence | Python script updates node, saves graph |
| `/knowledge-contradict <id>` | Mark lesson as incorrect | Python script decreases confidence |
| `/knowledge-review-uncertain` | Review lessons <70% confidence | Python script filters, presents for validation |

**Workflow Management Commands**:

| Command | Purpose | Implementation |
|---------|---------|----------------|
| `/generate-workflow` | Generate new workflow for gap | Invokes workflow-analyst in organic mode |
| `/upgrade-agents` | Upgrade to latest template version | Python script updates agent frontmatter |
| `/workflows-list` | Show available workflows | Scans `.claude/workflows/proven/` |
| `/workflows-resume` | Resume paused workflow | Loads saved state, continues |

**How Commands Use Claude Code**:
```
Command File: .claude/commands/knowledge-status.md

---
name: knowledge-status
description: Display knowledge management statistics
---

Run this command to show statistics:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/knowledge_status.py
```

Output format: [example output]
```

When user types `/knowledge-status`, Claude Code:
1. Reads `.claude/commands/knowledge-status.md`
2. Expands the content into current context
3. Claude executes the bash command
4. User sees formatted statistics

---

#### 6. MCP Tools

**Purpose**: Programmatic access to routing and knowledge

**File**: `src/triads/router/entrypoint.py`

**Tools Exposed**:

```python
@mcp_tool
def route_prompt(prompt: str) -> dict:
    """
    Route a prompt to appropriate workflow

    Returns:
        {
            "workflow_type": "bug-fix",
            "confidence": 0.95,
            "reasoning": "Detected error message and failing test",
            "suggested_command": "Start Bug Fix: memory leak in router"
        }
    """
    router = RouterService()
    result = router.route(prompt)
    return result.to_dict()

@mcp_tool
def get_current_triad() -> dict:
    """
    Get currently active triad/workflow

    Returns:
        {
            "workflow": "bug-fix",
            "current_triad": "bug-investigation-triad",
            "progress": "2/3 triads complete",
            "state": "in_progress"
        }
    """
    workflow_manager = WorkflowManager()
    return workflow_manager.get_current()
```

**How MCP Tools Use Claude Code**:
- Registered via `pyproject.toml` MCP server configuration
- Claude Code loads tools automatically on session start
- Available to Main Claude and all agents
- Tools can be invoked like any other tool (Read, Write, etc.)

---

## 6. Component Mapping

### Complete Mapping Table

| Triads Feature | Claude Code Component | File Location | Purpose |
|----------------|----------------------|---------------|---------|
| **Supervisor Routing** | Agent + Hook | `.claude/agents/supervisor/supervisor.md` + `hooks/user_prompt_submit.py` | Triage Q&A vs work, route to workflows |
| **Workflow Triads** | Agents (organized in dirs) | `.claude/agents/{triad}/` | Specialized agents for work phases |
| **Bridge Agents** | Agents (special role) | `.claude/agents/{triad}/{bridge}.md` | Context compression and handoff |
| **Knowledge Graphs** | Custom (JSON files) | `.claude/graphs/*.json` | Persistent context storage |
| **Constitutional Principles** | Output Style | `.claude/output-styles/constitutional.md` | TDD, evidence, uncertainty, transparency |
| **Experience Injection** | PreToolUse Hook | `hooks/on_pre_experience_injection.py` | Deliver checklists/patterns/warnings |
| **Session Init** | SessionStart Hook | `hooks/session_start.py` | Welcome message, graph initialization |
| **Knowledge Saving** | Stop Hook | `hooks/on_stop.py` | Auto-save graphs on agent completion |
| **Knowledge Commands** | Slash Commands | `.claude/commands/knowledge-*.md` | User interface for knowledge management |
| **Workflow Commands** | Slash Commands | `.claude/commands/workflows-*.md` | User interface for workflow management |
| **Router Service** | MCP Tools | `src/triads/router/entrypoint.py` | Programmatic routing access |
| **Graph Access** | Python Library | `src/triads/km/` | Load/save/validate graphs |
| **Seed Workflows** | Custom (YAML files) | `.claude/workflows/proven/*.yaml` | Pre-defined workflow structures |
| **Project Instructions** | CLAUDE.md | `CLAUDE.md` | Universal constitutional principles |

---

### Component Dependencies

```
Constitutional Principles (Output Style)
  ↓
  Applies to Main Claude
  ↓
Supervisor (Agent + Hook)
  ↓
  Routes to Workflows (YAML)
  ↓
Triads (Agents)
  ↓
  Update Knowledge Graphs (JSON)
  ↓
Experience Injection (Hook)
  ↓
  Loads from Knowledge Graphs
  ↓
User sees checklists/patterns/warnings
```

**Critical Path**:
1. User sends message
2. UserPromptSubmit hook injects Supervisor
3. Supervisor uses Router MCP tool
4. Router returns workflow suggestion
5. User confirms
6. Supervisor invokes triad agents via Task tool
7. Agents update knowledge graphs via [GRAPH_UPDATE]
8. PreToolUse hook injects experience from graphs
9. Stop hook saves graphs
10. Cycle repeats

---

## 7. Lifecycle Flow

### Complete Session Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. User starts Claude Code                                  │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. SessionStart Hook Fires                                  │
│    - hooks/session_start.py executes                        │
│    - Displays welcome message                               │
│    - Initializes knowledge graphs                           │
│    - Checks for agent updates                               │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. User Types Message                                       │
│    Example: "There's a memory leak in the router"          │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. UserPromptSubmit Hook Fires                              │
│    - hooks/user_prompt_submit.py executes                   │
│    - Loads supervisor agent definition                      │
│    - Injects supervisor instructions into context           │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Main Claude (with Supervisor injected) Responds          │
│    - Classifies: bug-fix workflow (confidence: 0.95)       │
│    - Suggests: "Start Bug Fix: memory leak in router"      │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. User Confirms                                            │
│    "yes"                                                    │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. Supervisor Invokes Bug-Investigation Triad               │
│    - Uses Task tool to invoke first agent                   │
│    - Agent: bug-analyzer                                    │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│ 8. Bug-Analyzer Agent Executes                              │
│    - Uses Read tool to examine code                         │
│    - Uses Grep to search for memory patterns                │
│    - Creates [GRAPH_UPDATE] with findings                   │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│ 9. Bug-Analyzer Completes, Stop Hook Fires                  │
│    - hooks/on_stop.py executes                              │
│    - Saves updated knowledge graph                          │
│    - Updates workflow progress                              │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│ 10. Supervisor Invokes Next Agent (Bug-Reproducer)          │
│     - Uses Task tool                                        │
│     - Agent receives context from knowledge graph           │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│ 11. Bug-Reproducer About to Use Write Tool                  │
│     - PreToolUse hook fires                                 │
│     - hooks/on_pre_experience_injection.py executes         │
│     - Queries graphs for relevant experience                │
│     - Finds: "Testing Checklist for Bug Reproduction"      │
│     - Injects checklist into context                        │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│ 12. Bug-Reproducer Sees Checklist                           │
│     "Before writing reproduction test:                      │
│      □ Verify environment matches production               │
│      □ Isolate minimal test case                           │
│      □ Document expected vs actual behavior"               │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│ 13. Bug-Reproducer Completes, Workflow Continues            │
│     - Diagnostician agent invoked                           │
│     - Bridge agent compresses findings                      │
│     - Next triad (Bug-Fixing) begins                        │
│     - ... cycle repeats through all 3 triads                │
└─────────────────────────────────────────────────────────────┘
```

---

### Tool Use Interception Example

**Scenario**: Agent about to commit code with Write tool

```
Agent: [Planning to use Write tool for auth.py]
  ↓
PreToolUse Hook Fires
  ↓
hooks/on_pre_experience_injection.py executes:

  tool_name = "Write"
  file = "auth.py"
  action_keywords = ["authentication", "commit"]

  experience = query_experience(
      tool_names=["Write"],
      file_patterns=["**/auth*.py"],
      action_keywords=["authentication", "security"]
  )

  # Found: Security Checklist for Authentication Code

  return """
  ⚠️ SECURITY CHECKLIST (from knowledge graph)

  Before committing authentication code:
  □ Password hashing uses bcrypt/scrypt
  □ No secrets in code (use environment variables)
  □ SQL injection prevention (parameterized queries)
  □ Session tokens are cryptographically secure

  This checklist was learned from security-review on 2025-10-10.
  """
  ↓
Agent receives injected checklist BEFORE using Write tool
  ↓
Agent reviews checklist, validates code
  ↓
Agent proceeds with Write tool (or fixes issues first)
```

---

## 8. Installation & Distribution

### Plugin Installation

**Method 1: Claude Code Plugin Marketplace** (future)
```bash
# In Claude Code
> /plugin install triads
```

**Method 2: Manual Installation** (current)
```bash
# Clone repository
git clone https://github.com/reliable-agents-ai/triads
cd triads

# Install plugin
./install.sh

# Or with Python package manager
pip install -e .
```

**What install.sh Does**:
```bash
#!/bin/bash

# 1. Create .claude-plugin/ directory
mkdir -p .claude-plugin

# 2. Copy plugin manifest
cp plugin.json .claude-plugin/

# 3. Create .claude/ structure
mkdir -p .claude/{agents,commands,graphs,workflows,generator}

# 4. Copy agent definitions
cp -r agents/* .claude/agents/

# 5. Copy slash commands
cp -r commands/* .claude/commands/

# 6. Copy seed workflows
cp -r workflows/* .claude/workflows/

# 7. Install hooks
mkdir -p hooks
cp hooks/*.py hooks/
cp hooks/hooks.json hooks/

# 8. Install Python package
pip install -e .

# 9. Create project instructions
cp CLAUDE.md ./

# 10. Create output style
cp output-styles/constitutional.md .claude/output-styles/

echo "✅ Triads plugin installed!"
```

---

### Package Structure

```
triads/
├── .claude-plugin/
│   ├── plugin.json              # Plugin manifest
│   └── marketplace.json          # Marketplace listing
│
├── .claude/
│   ├── agents/                  # Template agents (copied to user project)
│   ├── commands/                # Template commands
│   ├── workflows/               # Seed workflows
│   ├── generator/lib/           # Generator templates
│   └── output-styles/           # Constitutional style
│
├── hooks/                       # Hook scripts
│   ├── hooks.json
│   ├── session_start.py
│   ├── user_prompt_submit.py
│   ├── on_stop.py
│   └── on_pre_experience_injection.py
│
├── src/triads/                  # Python package
│   ├── __init__.py
│   ├── km/                      # Knowledge management
│   ├── router/                  # Workflow routing
│   └── utils/                   # Utilities
│
├── tests/                       # Test suite
├── docs/                        # Documentation
├── pyproject.toml               # Python package config
├── install.sh                   # Installation script
├── CLAUDE.md                    # Project instructions template
└── README.md                    # User guide
```

---

### Version Management

**File**: `.claude-plugin/plugin.json`

```json
{
  "version": "0.9.0-alpha.1"
}
```

**Also in**:
- `pyproject.toml` → `version = "0.9.0a1"`
- `.claude-plugin/marketplace.json` → `plugins[0].version = "0.9.0-alpha.1"`

**Upgrade Process**:
```bash
# User pulls latest from GitHub
git pull origin main

# Runs upgrade command
/upgrade-agents

# Script updates:
- Agent frontmatter (template_version field)
- Hook scripts (if changed)
- Seed workflows (if changed)
- Python package (pip install -e .)
```

---

## 9. Examples

### Example 1: Simple Workflow Execution

**User Goal**: Fix a bug

**Full Flow**:

```
User: "The login form crashes when email is empty"
  ↓
Supervisor (via hook):
  Classified as: bug-fix
  Confidence: 0.98
  Suggested: "Start Bug Fix: login form crash on empty email"
  ↓
User: "yes"
  ↓
Workflow: bug-fix (3 triads)
  ├─ Bug Investigation Triad
  │   ├─ bug-analyzer uses Grep → finds validation code
  │   ├─ bug-reproducer uses Write → creates failing test
  │   └─ diagnostician (bridge) → compresses to 20 key findings
  │
  ├─ Bug Fixing Triad
  │   ├─ diagnostician loads bridge context
  │   ├─ bug-fixer uses Edit → adds email validation
  │   └─ tester (bridge) → verifies fix, compresses results
  │
  └─ Verification Triad
      ├─ tester loads bridge context
      ├─ regression-tester uses Bash → runs full test suite
      └─ documenter → updates CHANGELOG, creates [GRAPH_UPDATE]
  ↓
Knowledge Graph Updated:
  .claude/graphs/bug-fixing_graph.json now contains:
  - Finding: "Email validation missing in LoginForm.validate()"
  - Decision: "Add Yup schema validation for email field"
  - Pattern: "Always validate user inputs on both client and server"
  ↓
Future Benefit:
  Next time agent touches LoginForm, PreToolUse hook injects:
  "⚠️ PATTERN: Always validate user inputs on both client and server
   (learned from bug-fix on 2025-10-27)"
```

---

### Example 2: Knowledge Accumulation Over Time

**Session 1: Initial Bug Fix**
```
User fixes validation bug
  ↓
Knowledge created:
  - Finding: "Missing email validation" (confidence: 1.0)
  - Pattern: "Validate inputs client + server" (confidence: 0.85)
```

**Session 2: Different Developer Touches Same Code**
```
Agent about to edit LoginForm
  ↓
PreToolUse hook queries knowledge graph
  ↓
Finds pattern: "Validate inputs client + server" (confidence: 0.85)
  ↓
Injects warning:
  "⚠️ PATTERN: When editing forms, remember to validate on both
   client and server (learned from previous bug fix)"
  ↓
Developer sees warning, adds server-side validation
  ↓
Creates [GRAPH_UPDATE]:
  type: validate_lesson
  lesson_id: pattern_validate_inputs
  outcome: followed
  ↓
Confidence boosted: 0.85 → 0.90
```

**Session 3: User Explicitly Validates**
```
User: /knowledge-validate pattern_validate_inputs
  ↓
Confidence boosted: 0.90 → 0.95
  ↓
Pattern now has HIGH confidence, will be injected more frequently
```

**Session 10: Pattern Becomes Critical**
```
After 10 successful uses without violations:
  Confidence: 0.95 → 1.0
  Priority: MEDIUM → CRITICAL
  ↓
Pattern now injected with 🔴 CRITICAL indicator:
  "🔴 CRITICAL PATTERN: Always validate inputs client + server
   (verified 10 times, 0 violations)"
```

---

### Example 3: Workflow Gap Detection & Generation

**Scenario**: User has task outside seed workflows

```
User: "Migrate database from PostgreSQL to MongoDB"
  ↓
Supervisor uses Router MCP tool
  ↓
Router checks seed workflows:
  - bug-fix? No (not fixing error)
  - feature-dev? No (not adding capability)
  - performance? No (not optimizing)
  - refactoring? No (not cleaning code)
  - investigation? No (not researching)
  ↓
Router result:
  workflow_type: None
  confidence: 0.0
  gap_detected: true
  ↓
Supervisor responds:
  "🔍 WORKFLOW GAP DETECTED

   Your request: 'Migrate database from PostgreSQL to MongoDB'

   This doesn't match any existing workflow:
   - bug-fix (fixing errors)
   - feature-dev (new capabilities)
   - performance (optimization)
   - refactoring (code cleanup)
   - investigation (understanding)

   This appears to be a database migration workflow.

   Would you like me to generate a custom workflow for
   database migrations? (Note: Requires session restart)"
  ↓
User: "Yes please"
  ↓
Supervisor invokes /generate-workflow
  ↓
Workflow Analyst (organic mode):
  Skips: Broad domain research
  Focuses: This specific migration scenario
  Designs: 3-triad workflow
    1. Migration Planning (assess → design → risk-analysis)
    2. Data Migration (export → transform → import)
    3. Validation & Cutover (validate → test → deploy)
  ↓
Workflow created: .claude/workflows/proven/database-migration.yaml
  ↓
Supervisor:
  "✅ New workflow created: database-migration

   Please restart Claude Code to load it.

   After restart, I'll recognize 'database migration' requests
   and route to this workflow automatically."
  ↓
User restarts
  ↓
Next session:
  User: "Migrate database from PostgreSQL to MongoDB"
  Supervisor: Matched workflow: database-migration (confidence: 0.95)
```

---

## Summary

### Key Takeaways

1. **Triads is an Overlay**: It doesn't replace Claude Code - it enhances it with workflow orchestration, context preservation, and meta-generation.

2. **Two-Level System**:
   - **Generator** (meta-level): Designs custom workflows (deprecated for initial setup, used for gap generation)
   - **Runtime** (execution): Runs workflows using supervisor + triads + knowledge graphs

3. **Component Synergy**:
   - Agents = workflow triads
   - Hooks = lifecycle automation + experience injection
   - Commands = user interface
   - MCP Tools = programmatic access
   - Knowledge Graphs = context preservation

4. **Progressive Enhancement**:
   - Install once → Get supervisor + seed workflows
   - Use continuously → Accumulate knowledge
   - Detect gaps → Generate new workflows
   - Learn patterns → Improve over time

5. **Constitutional Compliance**:
   - Output style enforces TDD + principles for Main Claude
   - Agent prompts enforce protocols for triads
   - Hooks enforce quality gates (experience injection)
   - Knowledge graphs enforce evidence + confidence

---

**This overlay architecture allows triads to add sophisticated workflow orchestration and knowledge management on top of Claude Code's flexible agent system without requiring changes to Claude Code itself.**
