# Installation Guide

Complete installation instructions for the Triad Generator system.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Installation](#quick-installation)
- [Installation Options](#installation-options)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)
- [Uninstallation](#uninstallation)

---

## Prerequisites

### Required

1. **Python 3.10 or higher**
   ```bash
   python3 --version
   # Should show: Python 3.10.x or higher
   ```

2. **Claude Code CLI**
   - Install from: https://docs.claude.com/en/docs/claude-code
   - Verify installation:
     ```bash
     claude --version
     ```

3. **Git repository**
   - The system must be used within a Git repository
   - If your project isn't a Git repo yet:
     ```bash
     git init
     ```

### Optional (Installed Automatically)

- **NetworkX** - Python library for knowledge graphs
  - Automatically installed by setup script
  - Manual installation: `pip3 install networkx`

---

## Quick Installation

### Method 1: Quick Install (Recommended)

```bash
# One-liner installation
curl -sSL https://raw.githubusercontent.com/reliable-agents-ai/triads/main/quick-install.sh | bash

# Start using immediately
claude code
> /generate-triads
```

### Method 2: Download Release

```bash
# 1. Download latest release
curl -LO https://github.com/reliable-agents-ai/triads/releases/latest/download/triad-generator-latest.tar.gz

# 2. Extract
tar -xzf triad-generator-latest.tar.gz
cd triad-generator-*

# 3. Run installer
./install-triads.sh

# 4. Start using
claude code
> /generate-triads
```

### Method 3: Clone Repository

```bash
# 1. Clone the repository
git clone https://github.com/reliable-agents-ai/triads.git
cd triads

# 2. Run the installer
./install-triads.sh

# 3. Start using
claude code
> /generate-triads
```

---

## Installation Options

### Interactive Installation (Recommended)

The installer will:
1. Check for prerequisites
2. Detect existing `.claude/` setup
3. Offer backup options
4. Install selectively

```bash
./setup-complete.sh
```

**What it does:**
- Creates `.claude/` directory structure
- Installs generator meta-agents
- Sets up slash command
- Installs Python dependencies
- Creates initial configuration

### Dry-Run Mode

See what would be installed without making changes:

```bash
./setup-complete.sh --dry-run
```

**Output shows:**
- Files that would be created
- Directories that would be added
- Dependencies that would be installed
- Conflicts with existing files

### Force Installation

Skip safety checks and install anyway:

```bash
./setup-complete.sh --force
```

**Warning:** This will overwrite existing files. Use only if:
- You've backed up your `.claude/` folder
- You want a fresh installation
- You know what you're doing

### Selective Installation

Install only specific components:

```bash
# Install only meta-agents
./setup-complete.sh --components=agents

# Install only slash command
./setup-complete.sh --components=command

# Install agents and templates
./setup-complete.sh --components=agents,templates
```

---

## Installation Process Details

### What Gets Installed

The setup script creates this structure:

```
your-project/
└── .claude/
    ├── commands/
    │   └── generate-triads.md          # Slash command
    │
    ├── generator/
    │   ├── agents/
    │   │   ├── domain-researcher.md    # Meta-agent 1
    │   │   ├── workflow-analyst.md     # Meta-agent 2
    │   │   └── triad-architect.md      # Meta-agent 3
    │   └── lib/
    │       └── templates.py            # Code generation
    │
    ├── graphs/
    │   ├── .gitkeep                    # Empty graphs folder
    │   └── generator_graph.json        # Generator knowledge graph
    │
    ├── constitutional/
    │   ├── checkpoints.json            # Quality checks
    │   └── violations.json             # Violation log
    │
    ├── settings.json                   # Claude Code config
    └── README.md                       # System documentation
```

### Safety Mechanisms

**Pre-flight Checks:**
1. Checks if `.claude/` folder exists
2. Scans for custom agents or configurations
3. Offers backup before proceeding
4. Shows what will be modified

**Backup Creation:**
```bash
# Automatic backup created at:
.claude.backup.TIMESTAMP/

# Example:
.claude.backup.20250108_143022/
```

**Conflict Resolution:**
- Existing files are preserved by default
- User prompted for each conflict
- Options: Skip, Overwrite, Backup then overwrite

### Post-Installation

After installation completes:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ TRIAD GENERATOR INSTALLED SUCCESSFULLY!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Next steps:
1. Launch Claude Code:
   claude code

2. Generate your custom triad system:
   > /generate-triads

3. Answer questions about your workflow

4. Get a custom multi-agent system designed for you!

Documentation: .claude/README.md
```

---

## Verification

### Verify Installation

```bash
# 1. Check directory structure
ls -la .claude/

# Should show:
# commands/
# generator/
# graphs/
# constitutional/
# settings.json
# README.md

# 2. Check Python dependencies
python3 -c "import networkx; print('NetworkX OK')"
# Should print: NetworkX OK

# 3. Check slash command
cat .claude/commands/generate-triads.md
# Should show generator documentation

# 4. Check meta-agents
ls .claude/generator/agents/
# Should show:
# domain-researcher.md
# workflow-analyst.md
# triad-architect.md
```

### Test Run

```bash
# Launch Claude Code
claude code

# In Claude Code session, run:
> /generate-triads

# You should see:
# Domain Researcher activating...
# Asking about your workflow...
```

---

## Troubleshooting

### Issue: "Python version too old"

**Problem:** Python 3.10+ required

**Solution:**
```bash
# On macOS with Homebrew:
brew install python@3.11

# On Ubuntu/Debian:
sudo apt install python3.11

# Verify:
python3 --version
```

### Issue: "Claude Code not found"

**Problem:** Claude Code CLI not installed

**Solution:**
1. Visit https://docs.claude.com/en/docs/claude-code
2. Follow installation instructions
3. Verify: `claude --version`

### Issue: "NetworkX installation failed"

**Problem:** pip installation issues

**Solution:**
```bash
# Try with user flag:
pip3 install --user networkx

# Or with specific Python version:
python3.11 -m pip install networkx

# Verify:
python3 -c "import networkx"
```

### Issue: "Permission denied"

**Problem:** Installer script not executable

**Solution:**
```bash
chmod +x setup-complete.sh
./setup-complete.sh
```

### Issue: "Existing .claude/ folder detected"

**Problem:** You already have a Claude Code setup

**Solution:**

**Option 1: Backup and proceed**
```bash
# Installer will offer to backup
./setup-complete.sh
# Choose "Yes" when prompted for backup
```

**Option 2: Manual backup**
```bash
# Backup manually
cp -r .claude .claude.backup

# Then install
./setup-complete.sh --force
```

**Option 3: Merge manually**
```bash
# Install to temporary location
mkdir temp-install
cd temp-install
/path/to/setup-complete.sh

# Manually copy components you want:
cp -r temp-install/.claude/generator ../your-project/.claude/
cp temp-install/.claude/commands/generate-triads.md ../your-project/.claude/commands/
```

### Issue: "Slash command not working"

**Problem:** Claude Code not recognizing `/generate-triads`

**Solution:**
```bash
# 1. Verify file exists
ls .claude/commands/generate-triads.md

# 2. Restart Claude Code
# Exit and relaunch: claude code

# 3. Check settings.json
cat .claude/settings.json
# Should include commands configuration

# 4. Try absolute path
cat /full/path/to/.claude/commands/generate-triads.md
```

### Issue: "Hooks not executing"

**Problem:** Python hooks aren't running

**Solution:**
```bash
# Make hooks executable
chmod +x .claude/hooks/*.py

# Verify Python path
which python3

# Test hook manually
python3 .claude/hooks/on_subagent_start.py
```

---

## Uninstallation

### Safe Uninstall

The uninstaller removes generator components while preserving your custom work:

```bash
./uninstall.sh
```

**What's Removed:**
- Generator meta-agents (`.claude/generator/`)
- Slash command (`.claude/commands/generate-triads.md`)
- Template library (`.claude/generator/lib/`)

**What's Preserved:**
- Your custom agents (`.claude/agents/`)
- Knowledge graphs (`.claude/graphs/*.json`)
- Your settings (`.claude/settings.json`)
- Constitutional principles (`.claude/constitutional/`)

**Backup Created:**
```bash
# Before removal:
.claude.uninstall-backup.TIMESTAMP/
```

### Complete Removal

To remove everything including generated agents:

```bash
# Manual removal
rm -rf .claude/

# Or uninstall with --complete flag
./uninstall.sh --complete
```

**Warning:** This removes all Claude Code configuration, including:
- Generated triads
- Knowledge graphs
- All custom work

Only use if you want a completely clean slate.

---

## Upgrading

See [Upgrading Guide](UPGRADING.md) for instructions on updating to newer versions.

---

## Support

**Issues during installation:**
- Check [Troubleshooting](TROUBLESHOOTING.md)
- Search [GitHub Issues](https://github.com/reliable-agents-ai/triads/issues)
- Create new issue if problem persists

**Questions:**
- Read [FAQ](FAQ.md)
- Check [Usage Guide](USAGE.md)
- Ask in [Discussions](https://github.com/reliable-agents-ai/triads/discussions)

---

## Next Steps

After successful installation:

1. **Read the Quick Start**: See [README.md](../README.md#quick-start)
2. **Generate your system**: Run `/generate-triads` in Claude Code
3. **Learn to use it**: See [Usage Guide](USAGE.md)
4. **Explore examples**: See [Examples](EXAMPLES.md)

---

**Installation complete? Time to build your triad system!**

```bash
claude code
> /generate-triads
```
