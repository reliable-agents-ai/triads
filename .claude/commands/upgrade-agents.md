---
description: Upgrade agents to latest template version
---

# Agent Upgrade System

Upgrade your existing agents to the latest template version while preserving customizations.

## Usage

```bash
/upgrade-agents [options] [agent-names...]
```

## Options

- `--all` - Upgrade all agents (prompts for confirmation per agent)
- `--dry-run` - Show what would change without applying
- `--force` - Skip confirmation prompts (use with caution)
- `--triad <name>` - Upgrade all agents in specific triad

## Examples

```bash
# Upgrade single agent
/upgrade-agents senior-developer

# Upgrade all agents in design triad
/upgrade-agents --triad design

# Preview changes for all agents
/upgrade-agents --all --dry-run

# Upgrade specific agents
/upgrade-agents cultivator pruner gardener-bridge

# Force upgrade without prompts (careful!)
/upgrade-agents --all --force
```

## What Gets Upgraded

The upgrade system:

- ✅ Adds new template sections (e.g., Knowledge Graph Protocol)
- ✅ Updates template version in frontmatter
- ✅ Preserves all your customizations
- ✅ Creates automatic backups before changes
- ✅ Shows diffs for review before applying

## Safety Features

- **Automatic backups**: Saved to `.claude/agents/backups/`
- **Dry-run mode**: Preview changes without modifying files
- **Diff preview**: See exactly what will change
- **Confirmation prompts**: Approve each upgrade individually
- **Atomic writes**: No partial updates if something fails
- **Content validation**: Rejects invalid agent structures

## Rollback

If you need to restore an agent:

```bash
# Find your backup
ls .claude/agents/backups/

# Restore from backup
cp .claude/agents/backups/solution-architect_20250120_143022.md.backup \
   .claude/agents/design/solution-architect.md
```

## Template Versions

**Current template version**: `0.8.0`

**Version history**:
- **0.8.0**: Added Knowledge Graph Protocol (mandatory section)
- **0.7.0**: Initial versioning system

**Check your agents' versions**:
```bash
grep "template_version:" .claude/agents/**/*.md
```

## Troubleshooting

**"No agents need upgrading"**
- All your agents are already up to date!

**"Validation failed"**
- The upgrade would create invalid agent structure
- Check error message for details
- Consider manual review

**"Error generating upgrade"**
- Template merge encountered unexpected structure
- Create GitHub issue with agent file (redact sensitive info)

**Agent looks wrong after upgrade**
- Restore from backup (see Rollback section above)
- Report issue with details

## Support

- [Agent Upgrades Guide](../../docs/AGENT_UPGRADES.md)
- [GitHub Issues](https://github.com/reliable-agents-ai/triads/issues)
