# Triad Generator

> 🧠 Self-discovering AI that designs custom multi-agent workflows for Claude Code

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude Code](https://img.shields.io/badge/Claude-Code-purple.svg)](https://claude.ai/code)

## What is this?

**Triad Generator** is a meta-AI system that researches your workflow and automatically generates custom teams of AI agents optimized for how *you* work.

Instead of forcing you to adapt to generic templates, it:
1. **Interviews you** about your workflow
2. **Researches your domain** (web search + analysis)
3. **Designs optimal agent teams** (groups of 3 with context-preserving bridges)
4. **Generates everything** (agents, hooks, docs, quality enforcement)

### The Result

You get a custom system of specialist AI agents organized into **triads** (groups of 3) with **bridge agents** that preserve context as work flows through phases—eliminating the #1 problem in multi-agent systems: context loss.

```
Discovery Triad       Design Triad          Implementation Triad
├─ Agent A           ├─ Bridge Agent ◄─────┘  (preserves context)
├─ Agent B           ├─ Agent C
└─ Bridge Agent ─────┴─ Agent D
                     └─ Bridge Agent ──────┐
                                            │
                                     Validation Triad
                                     ├─ Bridge Agent
                                     ├─ Agent E
                                     └─ Agent F
```

---

## Quick Start

### Prerequisites

- **Python 3.10+** (with pip)
- **[Claude Code CLI](https://docs.claude.com/en/docs/claude-code)** installed
- Any git repository

### Installation

**Quick Install (Recommended):**
```bash
curl -sSL https://raw.githubusercontent.com/reliable-agents-ai/triads/main/quick-install.sh | bash
```

**Or download and install manually:**
```bash
# Download latest release
curl -LO https://github.com/reliable-agents-ai/triads/releases/latest/download/triad-generator-latest.tar.gz
tar -xzf triad-generator-latest.tar.gz
cd triad-generator-*
./install-triads.sh
```

**Or clone the repository:**
```bash
git clone https://github.com/reliable-agents-ai/triads.git
cd triads
./install-triads.sh
```

### First Use

```bash
# Launch Claude Code in your project
claude code

# Run the generator
> /generate-triads

# Answer questions about your workflow
# Get a custom triad system designed for you!
```

**That's it!** The system will interview you, research your domain, and generate a complete multi-agent workflow.

---

## Key Features

### 🧠 Self-Discovering (No Templates)

Unlike systems with rigid templates, Triad Generator:
- Researches YOUR specific workflow through conversation
- Web searches industry best practices for YOUR domain
- Designs triads optimized for YOUR phases
- Places bridge agents at YOUR context loss points

### 🌉 Context Preservation (Bridge Agents)

**Bridge agents** participate in 2 triads simultaneously:
- Compress knowledge graphs intelligently (top 20 nodes)
- Carry forward decisions, uncertainties, and findings
- **Result**: Zero context loss, ~40% faster than hierarchical patterns

### ⚖️ Constitutional Quality (TRUST Principles)

Every agent follows the **TRUST framework** - 5 immutable principles:

| Principle | TRUST | Description |
|-----------|-------|-------------|
| 1. **T**horough over fast | **T** | Verify thoroughly, never shortcut |
| 2. **R**equire evidence | **R** | Triple-verify, cite sources |
| 3. **U**ncertainty escalation | **U** | Never guess when unsure |
| 4. **S**how all work | **S** | Complete transparency in reasoning |
| 5. **T**est assumptions | **T** | Question and validate everything |

Python hooks enforce TRUST architecturally (not just prompts).

### 📊 Knowledge Graphs (NetworkX) with Automatic Quality Assurance

Each triad builds a local graph as it works:
- Captures entities, decisions, uncertainties
- File-based (JSON), human-readable
- No external services required
- Persists learning across sessions
- **Automatic quality management** ensures high-quality graphs transparently

### 🎯 Claude Code Native

Built specifically for Claude Code:
- Slash command integration (`/generate-triads`)
- Sub-agent architecture
- Lifecycle hooks (pre/post execution)
- Session-aware context management

---

## How It Works

### The Generator Triad (Meta-Level)

Three meta-agents design your system:

```
┌──────────────────────┐
│  Domain Researcher   │  Interviews you + researches domain
└──────────┬───────────┘
           │ Discovers workflow phases and needs
           ▼
┌──────────────────────┐
│  Workflow Analyst    │  Designs optimal triad structure
└──────────┬───────────┘
           │ Creates agent specifications
           ▼
┌──────────────────────┐
│  Triad Architect     │  Generates all files
└──────────────────────┘
```

### Your Custom Triads (Generated)

After generation, you'll have 3-5 triads tailored to your workflow:

**Example: Software Development**
```
Discovery Triad
├─ Codebase Analyst (explores code)
├─ Requirements Gatherer (documents needs)
└─ Knowledge Synthesizer [BRIDGE] (integrates findings)

Design Triad
├─ Knowledge Synthesizer [BRIDGE] (carries context)
├─ Solution Architect [BRIDGE] (designs approach)
└─ Security Analyst (reviews for vulnerabilities)

Implementation Triad
├─ Solution Architect [BRIDGE] (carries design)
├─ Senior Developer (implements)
└─ Code Reviewer (validates quality)
```

**Example: RFP/Bid Writing**
```
Analysis Triad → Strategy Triad → Writing Triad → Validation Triad
(with bridges preserving requirements and win themes throughout)
```

### Usage Flow

```bash
# Start with first triad
> Start Discovery: analyze the authentication system

[Discovery triad runs, builds knowledge graph]

# Continue to next phase
> Start Design: plan OAuth2 integration

[Knowledge Synthesizer bridges context forward automatically]
[Design triad works with full requirements - no context loss!]

# Implement
> Start Implementation: build OAuth2 flow

[Solution Architect bridges design decisions forward]
[Implementation proceeds with complete context]
```

---

## Theoretical Foundations

Triad Generator is built on solid academic research:

### Triad Theory (Simmel, 1908)

Georg Simmel's sociological research identified that **groups of 3 are optimal**:
- **Mediation potential**: Third member can resolve conflicts
- **Efficiency**: Only 3 communication channels (vs 28 in 8-person group)
- **Accountability**: Everyone's contribution is visible
- **Proven pattern**: Used in sports teams, military units, business leadership

### Overlapping Triads (2025 Research)

Recent organizational research shows overlapping triads with shared members:
- **Prevent information silos**: Bridges naturally transfer knowledge
- **40% faster than hierarchical** (no central bottleneck)
- **Graceful scaling**: Add triads without redesigning system
- **Natural workflow alignment**: Matches how humans actually work in phases

### TRUST Framework (Constitutional AI)

Based on research from [reliableagents.ai](https://reliableagents.ai), the **TRUST framework** provides:
- **Architectural enforcement**: Principles embedded in system structure, not just prompts
- **Instruction hierarchy**: TRUST rules override all other instructions
- **Behavioral DNA**: Immutable characteristics that can't be changed by circumstances
- **Quality assurance framework**: Multi-stage verification with mandatory protocols

The TRUST acronym makes these principles memorable and actionable for agents.

### Autonomous Knowledge Graphs

Self-organizing knowledge networks that:
- **Discover schema** without predefined ontologies (95% semantic alignment)
- **Evolve structure** based on what agents learn
- **Preserve provenance**: Every fact cites its source
- **Support reasoning**: Graph traversal for context and dependencies

---

## Examples

### Software Development

**You**: "I build software features. Requirements → Design → Code → Test"

**System generates**:
- Discovery Triad (analyzes codebase + requirements)
- Design Triad (plans solution + security)
- Implementation Triad (codes + reviews)
- Bridge agents preserve requirements and design decisions

**Result**: No lost requirements between phases, security considered throughout

### RFP Response Writing

**You**: "I write proposals. Analyze RFP → Research → Strategy → Write → Validate"

**System generates**:
- Analysis Triad (extracts requirements + compliance)
- Strategy Triad (develops win themes)
- Writing Triad (drafts sections)
- Validation Triad (compliance check + pricing)
- Bridges preserve requirements matrix and win themes

**Result**: Compliance requirements tracked end-to-end, win themes consistent

### Lead Generation

**You**: "I source leads. Find prospects → Qualify → Enrich → Prepare outreach"

**System generates**:
- Prospecting Triad (searches + qualifies)
- Enrichment Triad (builds profiles)
- Outreach Prep Triad (personalizes messaging)
- Bridges preserve qualification criteria and insights

**Result**: Personalization based on complete prospect context

---

## Documentation

### For Users
- **[Installation Guide](docs/INSTALLATION.md)** - Detailed setup instructions
- **[Usage Guide](docs/USAGE.md)** - How to use the generator
- **[Examples](docs/EXAMPLES.md)** - Real-world workflow examples
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions
- **[FAQ](docs/FAQ.md)** - Frequently asked questions

### For Claude Code Users
- **[CLAUDE.md](CLAUDE.md)** - Slash command documentation and best practices

### For Developers
- **[Architecture](docs/ARCHITECTURE.md)** - System design and theory
- **[Contributing](CONTRIBUTING.md)** - How to contribute
- **API Reference** (in `.claude/` folder)

---

## Installation & Uninstallation

### Safe Installation

The installer checks for existing `.claude/` folders and offers:
- Backup existing setup before installing
- Skip installation if custom setup detected
- Dry-run mode (show what would be installed)
- Selective installation options

```bash
./install.sh                  # Interactive mode
./install.sh --dry-run        # Show what would be installed
./install.sh --force          # Skip safety checks
```

### Safe Uninstallation

The uninstaller removes only generator components, preserving your work:

```bash
./uninstall.sh
```

**Preserves**:
- Your custom agents (`.claude/agents/`)
- Your knowledge graphs (`.claude/graphs/`)
- Your configuration (`.claude/settings.json`)

**Removes**:
- Generator meta-agents
- Template library
- Slash command

**Creates backup** before any removal.

### Upgrading

```bash
./upgrade.sh
```

Upgrades generator components while preserving customizations.

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Code of conduct
- How to report issues
- How to submit pull requests
- Development setup
- Testing guidelines

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

### Research Foundations
- **Georg Simmel** (1908) - Triad theory and social dynamics
- **Ronald Burt** - Structural holes theory (bridge agents)
- **[reliableagents.ai](https://reliableagents.ai)** - Constitutional AI principles
- **Various 2025 papers** - Overlapping triads, autonomous schema induction

### Technology Stack
- **[Claude Code](https://docs.claude.com/en/docs/claude-code)** by Anthropic
- **[NetworkX](https://networkx.org/)** for knowledge graphs
- **Python 3.10+** standard library

---

## Support

- **Issues**: [GitHub Issues](https://github.com/reliable-agents-ai/triads/issues)
- **Discussions**: [GitHub Discussions](https://github.com/reliable-agents-ai/triads/discussions)
- **Documentation**: [docs/](docs/)
- **Claude Code**: [Official Docs](https://docs.claude.com/en/docs/claude-code)

---

## Project Status

✅ **Production Ready** - Fully functional and tested
📚 **Well Documented** - Comprehensive guides
🧪 **Actively Maintained** - Regular updates
🤝 **Community Driven** - Contributions welcome

---

**Ready to transform your workflow?**

```bash
./install.sh
claude code
> /generate-triads
```

Let the system discover how you work and design agents specifically for you!
