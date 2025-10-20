# Agent Upgrade System

Comprehensive guide to upgrading agents to the latest template version while preserving customizations.

## Table of Contents

- [Overview](#overview)
- [When to Upgrade](#when-to-upgrade)
- [Quick Start](#quick-start)
- [Command Reference](#command-reference)
- [How It Works](#how-it-works)
- [Safety Features](#safety-features)
- [Troubleshooting](#troubleshooting)
- [Architecture](#architecture)

---

## Overview

The Agent Upgrade System allows you to apply template updates to existing agents without losing customizations. When the triads plugin releases template improvements (like the Knowledge Graph Protocol in v0.8.0), you can upgrade all your agents automatically.

**What gets upgraded**:
- New template sections added to agents
- Template version field updated in frontmatter
- All customizations preserved (examples, domain-specific content, custom tools)

**What stays the same**:
- Your agent customizations
- Custom sections you added
- Domain-specific examples
- Triad-specific workflows

---

## When to Upgrade

Upgrade your agents when:

1. **Plugin updates announce new template features**
   - Check release notes for template changes
   - Example: v0.8.0 added Knowledge Graph Protocol

2. **You see "outdated template" warnings**
   - Claude Code may notify you about outdated agents
   - Check template versions with: `grep template_version: .claude/agents/**/*.md`

3. **You want new capabilities**
   - New template sections add functionality
   - Upgrades are backward-compatible (old agents still work)

**You don't need to upgrade** if:
- Your agents work fine and you don't want new features
- You're in the middle of critical work (upgrade later)
- You prefer manual updates

---

## Quick Start

### 1. Check Current Versions

```bash
# See all agent versions
grep "template_version:" .claude/agents/**/*.md

# See which agents need upgrade
python -c "from triads.upgrade import UpgradeOrchestrator; \
  orch = UpgradeOrchestrator(); \
  [print(c) for c in orch.scan_agents() if c.needs_upgrade]"
```

### 2. Preview Changes (Dry Run)

```bash
# See what would change
/upgrade-agents --all --dry-run
```

### 3. Upgrade Agents

```bash
# Upgrade all agents (interactive)
/upgrade-agents --all

# Upgrade specific triad
/upgrade-agents --triad implementation

# Upgrade specific agents
/upgrade-agents senior-developer test-engineer
```

### 4. Verify Success

```bash
# Check versions updated
grep "template_version:" .claude/agents/**/*.md

# Check agents work
# (Test by invoking an agent)
```

---

## Command Reference

### Basic Usage

```bash
/upgrade-agents [options] [agent-names...]
```

### Options

| Option | Description |
|--------|-------------|
| `--all` | Upgrade all agents (with confirmation) |
| `--dry-run` | Preview changes without applying |
| `--force` | Skip confirmation prompts (dangerous!) |
| `--triad <name>` | Upgrade all agents in specific triad |

### Examples

**Upgrade single agent**:
```bash
/upgrade-agents senior-developer
```

**Upgrade all agents in a triad**:
```bash
/upgrade-agents --triad design
```

**Preview changes for all agents**:
```bash
/upgrade-agents --all --dry-run
```

**Upgrade multiple specific agents**:
```bash
/upgrade-agents cultivator pruner gardener-bridge
```

**Force upgrade without confirmation** (use with caution):
```bash
/upgrade-agents --all --force
```

---

## How It Works

### Upgrade Workflow

```
1. Scan Agents
   ├─ Find all .md files in .claude/agents/
   ├─ Parse template_version from frontmatter
   └─ Identify agents with old versions

2. Generate Upgraded Content
   ├─ Parse current agent (frontmatter + body)
   ├─ Update frontmatter version
   ├─ Identify new sections to add
   ├─ Smart merge: Insert new sections, preserve all existing content
   └─ Reconstruct agent file

3. Show Diff for Review
   ├─ Generate unified diff (like git diff)
   └─ Display additions in context

4. Get User Confirmation
   ├─ Prompt: Apply? [y/N/d/s]
   ├─ Options: yes, no, diff again, skip
   └─ Respect --force flag

5. Apply Upgrade (Multi-Gate Safety)
   ├─ Gate 1: Create backup (.claude/agents/backups/)
   ├─ Gate 2: Validate new content structure
   ├─ Gate 3: Atomic write (temp file → rename)
   └─ Report success/failure
```

### Template Merge Strategy

For v0.8.0 (Knowledge Graph Protocol):

1. **Parse agent**: Extract frontmatter and body
2. **Update version**: `template_version: 0.8.0`
3. **Find insertion point**: After "Constitutional Principles" section
4. **Extract protocol**: Get full KG Protocol section from template
5. **Insert section**: Add with proper spacing
6. **Preserve content**: All existing sections remain unchanged

**Smart detection**: If agent already has the section, skip insertion.

---

## Safety Features

### 1. Automatic Backups

Every upgrade creates a timestamped backup:

```
.claude/agents/backups/
├── senior-developer_20250120_143022.md.backup
├── test-engineer_20250120_143045.md.backup
└── cultivator_20250120_143108.md.backup
```

**Restore from backup**:
```bash
cp .claude/agents/backups/senior-developer_20250120_143022.md.backup \
   .claude/agents/implementation/senior-developer.md
```

### 2. Dry-Run Mode

Preview changes without modifying files:

```bash
/upgrade-agents --all --dry-run
```

Output shows:
- Which agents need upgrade
- Diff of proposed changes
- No files modified

### 3. Diff Preview

Before applying, you see exactly what changes:

```diff
--- current/senior-developer
+++ proposed/senior-developer
@@ -3,6 +3,7 @@
 name: senior-developer
 triad: implementation
 role: developer
+template_version: 0.8.0
 ---

+## 🧠 Knowledge Graph Protocol (MANDATORY)
+(new section inserted here)
```

### 4. Interactive Confirmation

For each agent:

```
📦 Upgrading senior-developer
   Current version: 0.7.0
   Target version: 0.8.0

📊 Proposed changes:
(diff shown)

❓ Apply this upgrade? [y/N/d(iff)/s(kip)]:
```

Options:
- `y` - Apply upgrade
- `N` - Cancel (default)
- `d` - Show diff again
- `s` - Skip this agent, continue to next

### 5. Content Validation

Before writing, validates:
- ✅ Valid YAML frontmatter (`---` markers)
- ✅ Required fields present (`name`, `triad`, `role`, `template_version`)
- ✅ Structure integrity

Rejects upgrades that would create broken agents.

### 6. Atomic Writes

Uses temp file → rename pattern:

```python
temp_path.write_text(new_content)
temp_path.replace(agent_path)  # Atomic on POSIX
```

**Guarantees**: No partial writes if process crashes.

### 7. Path Traversal Protection

Validates all paths to prevent security vulnerabilities:
- Rejects `../` in triad names
- Validates agent paths within `.claude/agents/`
- Blocks null bytes and path separators

---

## Troubleshooting

### "No agents need upgrading"

**Cause**: All agents already have latest template version.

**Solution**: No action needed - you're up to date!

**Verify**:
```bash
grep "template_version: 0.8.0" .claude/agents/**/*.md
```

---

### "Validation failed"

**Cause**: Upgraded content would have invalid structure.

**Symptoms**:
```
✗ Validation failed for senior-developer
  Backup preserved at: senior-developer_20250120_143022.md.backup
```

**Debug**:
1. Check error message for specifics
2. Inspect backup file for current state
3. Report issue if unexpected

**Manual fix**:
```bash
# Review backup
cat .claude/agents/backups/senior-developer_20250120_143022.md.backup

# Restore if needed
cp .claude/agents/backups/senior-developer_20250120_143022.md.backup \
   .claude/agents/implementation/senior-developer.md
```

---

### "Error generating upgrade"

**Cause**: Template merge encountered unexpected agent structure.

**Symptoms**:
```
❌ Error generating upgrade: Could not parse agent frontmatter
```

**Solutions**:

**1. Check agent file syntax**:
```bash
# View agent file
cat .claude/agents/implementation/senior-developer.md

# Check frontmatter has --- markers
head -10 .claude/agents/implementation/senior-developer.md
```

**2. Manual upgrade**:
- Open agent in editor
- Compare with template (`src/triads/templates/agent_templates.py`)
- Add missing sections manually
- Update `template_version: 0.8.0`

**3. Report issue**:
- Create GitHub issue with agent structure (redact sensitive content)
- Include error message and stack trace

---

### Agent looks wrong after upgrade

**Cause**: Merge inserted section in wrong place, or formatting issue.

**Solution**:

**1. Restore from backup**:
```bash
ls .claude/agents/backups/
cp .claude/agents/backups/{agent}_{timestamp}.md.backup \
   .claude/agents/{triad}/{agent}.md
```

**2. Manual merge**:
- Open template section in `src/triads/templates/agent_templates.py`
- Copy Knowledge Graph Protocol section
- Paste into agent at correct location (after Constitutional Principles)
- Update version: `template_version: 0.8.0`

**3. Report issue**:
- Describe what looks wrong
- Include agent structure (before/after)

---

### "Agents directory not found"

**Cause**: Running from wrong directory, or `.claude/agents/` doesn't exist.

**Solution**:
```bash
# Check current directory
pwd

# Should be in repo root (contains .claude/)
ls -la | grep .claude

# If wrong, navigate to repo root
cd /path/to/your/triads-repo

# If .claude/agents/ doesn't exist
ls -la .claude/
mkdir -p .claude/agents
```

---

## Architecture

### Components

**1. UpgradeOrchestrator** (`src/triads/upgrade/orchestrator.py`)
- Core upgrade logic
- Agent scanning, backup, diff, validation, atomic writes
- 440 lines, 34 tests, 89% coverage

**2. UpgradeCandidate** (dataclass)
- Represents agent eligible for upgrade
- Tracks version, path, triad, name
- `needs_upgrade` property

**3. Slash Command** (`.claude/commands/upgrade-agents.md`)
- User-facing documentation
- Examples and options

**4. Command Handler** (`.claude/commands/handlers/upgrade_agents.py`)
- CLI argument parsing
- Invokes orchestrator
- Exit codes for success/failure

### Design Decisions

**Why simple regex parsing instead of YAML library?**
- Agent frontmatter is simple key-value pairs
- Regex is defensive and sufficient
- Avoids external dependencies (PyYAML)
- Reduces attack surface

**Why template merge instead of full generation?**
- Preserves all user customizations
- Less risky than regenerating from scratch
- Easier to debug and verify
- Users can review diffs before applying

**Why backup location `.claude/agents/backups/`?**
- Easy to discover (close to agents)
- Matches mental model (backups are agent-related)
- Not hidden, so users know they exist
- Simple to restore (copy command)

**Why permissive validation?**
- Goal: Prevent obviously broken files
- Not goal: Enforce perfect structure
- Overly strict validation would reject valid customizations
- Defensive approach balances safety and flexibility

### Extension Points

**Future template versions**:

Add to `_identify_new_sections()`:
```python
def _identify_new_sections(self, version: str) -> List[str]:
    if version == "0.9.0":
        return ["🧠 Knowledge Graph Protocol", "🔄 New Feature Section"]
    if version == "0.8.0":
        return ["🧠 Knowledge Graph Protocol"]
    return []
```

Add to `_merge_sections()`:
```python
if "🔄 New Feature Section" in new_sections:
    # Implement merge strategy for new section
    ...
```

**AI-powered customization detection** (Phase 3B - future):
- Use generation triad to semantically analyze agents
- Detect user customizations vs template defaults
- Intelligently merge custom examples with new template
- Currently: Simple template merge (v0.8.0 MVP)

---

## Template Versions

### Version History

**v0.8.0** (Current)
- Added: Knowledge Graph Protocol (mandatory section)
- Added: Template version tracking
- Migration: Automatic via upgrade system

**v0.7.0**
- Initial template structure
- Constitutional Principles framework
- Triad coordination patterns

### Checking Versions

**Your agents**:
```bash
grep "template_version:" .claude/agents/**/*.md
```

**Latest template**:
```bash
grep "AGENT_TEMPLATE_VERSION" src/triads/templates/agent_templates.py
```

**Find outdated agents**:
```bash
# Any agent without template_version field
grep -L "template_version:" .claude/agents/**/*.md
```

---

## Examples

### Example 1: Upgrade All Agents

```bash
$ /upgrade-agents --all

📋 Found 18 agents needing upgrade

📦 Upgrading senior-developer
   Current version: 0.7.0
   Target version: 0.8.0

📊 Proposed changes:
--- current/senior-developer
+++ proposed/senior-developer
@@ -3,6 +3,7 @@
 name: senior-developer
 triad: implementation
 role: developer
+template_version: 0.8.0
 ---
... (diff continues)

❓ Apply this upgrade? [y/N/d(iff)/s(kip)]: y
  ✓ Backed up to senior-developer_20250120_143022.md.backup
  ✓ Upgraded senior-developer
✅ Upgraded senior-developer to v0.8.0

(Repeats for each agent)

============================================================
📊 UPGRADE SUMMARY
============================================================
Total agents scanned: 18
Successfully upgraded: 18
Skipped: 0
Failed: 0
```

### Example 2: Dry Run Preview

```bash
$ /upgrade-agents --all --dry-run

📋 Found 18 agents needing upgrade

📦 Upgrading senior-developer
   Current version: 0.7.0
   Target version: 0.8.0

📊 Proposed changes:
(diff shown)

[DRY-RUN] Would upgrade .claude/agents/implementation/senior-developer.md

(Repeats for each agent - no files modified)
```

### Example 3: Upgrade Specific Triad

```bash
$ /upgrade-agents --triad design

📋 Found 3 agents needing upgrade

📦 Upgrading solution-architect
   Current version: 0.7.0
   Target version: 0.8.0

(Interactive workflow for 3 agents in design triad)
```

### Example 4: Restore from Backup

```bash
$ ls .claude/agents/backups/
senior-developer_20250120_143022.md.backup
test-engineer_20250120_143045.md.backup

$ cp .claude/agents/backups/senior-developer_20250120_143022.md.backup \
     .claude/agents/implementation/senior-developer.md

$ echo "Restored senior-developer to pre-upgrade state"
```

---

## Support

- **Documentation**: This file
- **Issues**: [GitHub Issues](https://github.com/reliable-agents-ai/triads/issues)
- **Discussions**: [GitHub Discussions](https://github.com/reliable-agents-ai/triads/discussions)

---

**Last Updated**: 2025-01-20 (Template v0.8.0)
