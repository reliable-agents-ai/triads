# Release Notes - v0.3.0: Plugin Architecture

**Release Date**: 2025-10-15
**Type**: Major architectural change

---

## 🎯 Major Changes

### Plugin Architecture
- ✅ Converted triads to **Claude Code plugin** architecture
- ✅ Install once globally, works in all projects
- ✅ Non-invasive: Only `.claude/graphs/` in project directory

### Auto-Router Deleted (100% Reduction)
- ❌ Removed 5,500 lines of ML-based routing code
- ✅ Replaced with **natural routing** via documentation
- ✅ Constraint-compliant: No parallel ML infrastructure
- ✅ Uses Claude's native intelligence instead

### HITL Validation Gates
- ✅ Added human-in-the-loop approval after Design phase
- ✅ User must approve designs before implementation begins
- ✅ Prevents over-engineering (lesson from auto-router)
- ✅ Embedded in generator for all future systems

---

## 📦 Plugin Structure

```
triads/ (plugin)
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest
├── hooks/
│   ├── hooks.json               # SessionStart + Stop
│   ├── session_start.py         # Inject routing + graphs
│   └── on_stop.py               # Update knowledge graphs
├── km/                          # Knowledge Management
├── agents/generator/            # Meta-agents
├── commands/                    # /generate-triads
├── templates/                   # Generation templates
└── ROUTING.md                   # Default routing directives
```

---

## 🚀 Installation

### Install Plugin (Once)

```bash
# From GitHub (recommended)
/plugin marketplace add github:reliable-agents-ai/triads-marketplace
/plugin install triads

# Or local development
/plugin marketplace add /path/to/triads-marketplace
/plugin install triads
```

### Generate Custom Workflow (Per Project)

```bash
cd ~/your-project
claude code
> /generate-triads
# Follow prompts, restart session
> Start [TriadName]: [task]
```

---

## 📚 Documentation

- **[User Guide](docs/USER_GUIDE.md)** - Complete usage guide
- **[Architecture Decisions](docs/ARCHITECTURE_DECISIONS.md)** - 6 ADRs
- **[Plugin README](README_PLUGIN.md)** - Plugin-specific docs
- **[Conversion Summary](PLUGIN_CONVERSION_SUMMARY.md)** - Migration details

---

## 🔄 Migration from v0.2.0

### Old Installation (Per-Project)
```bash
cd ~/project
./install.sh
# Result: 20+ files in .claude/
```

### New Installation (Plugin)
```bash
# Once globally
/plugin install triads

# Per project
> /generate-triads
# Result: Only .claude/agents/ and .claude/graphs/
```

---

## ✨ What's New

### User Ownership Model
- Generated agents are **scaffolded** (you own them)
- Edit freely, commit to git, share with team
- Re-generation = destructive reset (backs up first)

### Natural Routing
- Plugin injects routing directives at session start
- Claude naturally suggests appropriate triads
- User confirms (HITL pattern)
- No auto-execution, no ML dependencies

### Clean Separation
- **Plugin**: System code (managed by triads team)
- **Project**: Custom agents + data (managed by you)

---

## 📊 Metrics

| Metric | v0.2.0 | v0.3.0 | Change |
|--------|--------|--------|--------|
| **Router code** | 5,500 lines | 0 lines | -100% ❌ |
| **Routing** | ML pipeline | Documentation | Natural ✅ |
| **Project files** | 20+ files | 2 directories | -90% ✅ |
| **Installation** | Per-project | Once globally | Easy ✅ |
| **Constraint** | Violated | Compliant | Fixed ✅ |

---

## 🐛 Breaking Changes

### Router Commands Removed
The following commands are **removed** (auto-router deleted):
- `/router:status`
- `/router:switch`
- `/router:reset`
- `/router:training`
- `/router:stats`

**Replacement**: Natural routing via conversation

### Installation Method Changed
- Old: Run `./install.sh` per project
- New: Run `/plugin install triads` once globally

### Project Structure Changed
- Old: `.claude/` contains 20+ files
- New: `.claude/` contains only `agents/` and `graphs/`

---

## ⚠️ Known Limitations

### Plugin Support Required
- Requires Claude Code with plugin support
- If plugins not available, use project-level `.claude/` structure

### One-Time Setup
- Restart session after running `/generate-triads`
- Required to load newly generated agents

---

## 🎓 Key Decisions (ADRs)

1. **ADR-001**: Plugin Architecture (install once, works everywhere)
2. **ADR-002**: Scaffolding Model (users own generated agents)
3. **ADR-003**: Hooks in Plugin (system code centralized)
4. **ADR-004**: Delete Auto-Router (natural routing instead)
5. **ADR-005**: HITL Gates (user approves designs)
6. **ADR-006**: File Conventions (follow Claude Code standards)

See [ARCHITECTURE_DECISIONS.md](docs/ARCHITECTURE_DECISIONS.md) for details.

---

## 🙏 Acknowledgments

This release incorporates lessons learned from:
- Auto-router over-engineering (caught by HITL gate)
- Claude Code plugin system research
- User feedback on installation complexity
- Community best practices

---

## 📖 Resources

- **Installation**: See [User Guide](docs/USER_GUIDE.md)
- **Migration**: See [Conversion Summary](PLUGIN_CONVERSION_SUMMARY.md)
- **Architecture**: See [ADRs](docs/ARCHITECTURE_DECISIONS.md)

---

**Achievement**: 🎯 99% code reduction, plugin architecture, constraint-compliant!
