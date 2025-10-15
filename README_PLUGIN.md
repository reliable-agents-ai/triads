# Triads Claude Code Plugin

> Workflow system for organizing complex work into phases with specialized agents

---

## What is Triads?

Triads helps you organize complex work into phases (called "triads"). Each triad has specialized agents that work together and automatically hand off context to the next phase.

**Install once, use everywhere.**

---

## Quick Start

### Install Plugin

```bash
# Install from this directory
claude plugin install .

# Or install from repository (future)
claude plugin install triads
```

### Generate Custom Workflow

```bash
# In any project
cd ~/your-project
claude code

# Generate custom triads for your workflow
> /generate-triads

# Restart to activate
exit
claude code

# Use your custom workflow
> Start [TriadName]: [task description]
```

---

## Plugin Structure

```
triads/
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest
│
├── hooks/
│   ├── hooks.json               # Hook registration
│   ├── session_start.py         # Inject routing + graphs
│   └── on_stop.py               # Parse [GRAPH_UPDATE] blocks
│
├── km/                          # Knowledge Management libraries
│   ├── detection.py
│   ├── auto_invocation.py
│   └── formatting.py
│
├── agents/
│   └── generator/               # Meta-agents (create custom triads)
│       ├── domain-researcher.md
│       ├── workflow-analyst.md
│       └── triad-architect.md
│
├── commands/
│   └── generate-triads.md       # /generate-triads command
│
├── templates/
│   └── templates.py             # Agent generation templates
│
└── ROUTING.md                   # Default routing directives
```

---

## What Gets Installed

**Plugin (Global)**:
- System hooks (automatic knowledge graph management)
- KM libraries (quality detection)
- Generator agents (create custom workflows)
- `/generate-triads` command
- Default routing directives

**Project (Per-Project)**:
- Custom agents (generated for your workflow)
- Knowledge graphs (your project data)
- Optional custom routing

---

## How It Works

### 1. Plugin Provides Infrastructure

The plugin installs globally and provides:
- Hooks that run automatically
- Knowledge management libraries
- Generator that creates custom agents
- Commands available in all projects

### 2. Generator Creates Custom Agents

When you run `/generate-triads`:
1. Interviews you about your workflow
2. Designs triad structure
3. Generates custom agents in `.claude/agents/`
4. Creates project-specific routing

**These agents are YOURS** - edit them freely, commit to git, share with team.

### 3. Hooks Manage Knowledge Automatically

As you work:
- `SessionStart` hook injects routing + graph context
- Agents use `[GRAPH_UPDATE]` blocks to document findings
- `Stop` hook parses updates and saves to knowledge graphs
- Context automatically carries forward between triads

---

## Example Workflows

### Software Development

```bash
> /generate-triads
  → Design: Idea Validation → Design → Implementation → Testing

> Start Idea Validation: add OAuth2 authentication
> Start Design: OAuth2 architecture
> Start Implementation: build OAuth2 flow
```

### RFP Writing

```bash
> /generate-triads
  → Design: Analysis → Strategy → Writing → Review

> Start Analysis: evaluate requirements in Acme RFP
> Start Strategy: develop win themes
> Start Writing: draft technical approach
```

---

## Customizing

### Edit Generated Agents

```bash
# Agents are scaffolded - you own them after generation
vim .claude/agents/your-triad/your-agent.md

# Add domain-specific examples
# Tune prompts for your company
# Improve instructions based on experience

# Commit customizations
git add .claude/agents/
git commit -m "Customize analyst with company standards"
```

### Custom Routing (Optional)

```bash
# Override plugin's default routing
vim .claude/ROUTING.md

# Add project-specific routing examples
```

---

## Updating

### Plugin Updates

```bash
# Update plugin infrastructure
claude plugin update triads

# Updates:
# ✅ System hooks (bug fixes, features)
# ✅ KM libraries
# ✅ Generator

# Does NOT touch:
# ✏️ Your custom agents
# 📊 Your knowledge graphs
```

### Agent Customization

```bash
# Edit agents anytime
vim .claude/agents/my-triad/my-agent.md

# Share with team via git
git add .claude/agents/
git commit -m "Improve agent prompts"
git push
```

---

## Development

### Local Testing

```bash
# Install plugin from local directory
claude plugin install .

# Validate plugin structure
claude plugin validate .

# Test in a project
cd ~/test-project
claude code
> /generate-triads
```

### Plugin Structure Requirements

From Claude Code docs:
- `plugin.json` in `.claude-plugin/` directory
- Commands in `commands/` (markdown files)
- Agents in `agents/` (markdown files)
- Hooks in `hooks/hooks.json`
- All paths relative, starting with `./`

---

## Documentation

- **[User Guide](docs/USER_GUIDE.md)** - Complete user documentation
- **[Architecture](docs/ARCHITECTURE_DECISIONS.md)** - Design decisions
- **[Main README](README.md)** - Project overview

---

## Support

- **Issues**: [GitHub Issues](https://github.com/reliable-agents-ai/triads/issues)
- **Discussions**: [GitHub Discussions](https://github.com/reliable-agents-ai/triads/discussions)

---

**Remember**: Plugin = System tools (managed by triads) | Agents = Your workflow (managed by you)
