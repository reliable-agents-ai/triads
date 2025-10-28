---
name: upgrade-to-templates
description: Upgrade existing project to use new template system with @imports and constitutional architecture
category: system
---

# Upgrade to Templates

**Purpose**: Intelligently upgrade existing triads project to use the new template system while preserving all custom content.

**What this does**:
- Analyzes current `.claude/` structure
- Identifies missing templates (constitutional, methodologies, skills)
- Copies templates from `templates/` directory
- Updates CLAUDE.md to use @import syntax
- Preserves all existing triads, commands, and custom content
- Validates upgrade succeeded with no regressions

**Safety**: Creates git branch, backs up files, can rollback if issues.

---

## How It Works

This command invokes the **System Upgrade Triad**:

```
gap-analyzer → upgrade-executor → upgrade-bridge
```

### Phase 1: Gap Analysis (gap-analyzer)
- Scans current project structure
- Compares to template system
- Identifies what's missing
- Creates upgrade plan with risk assessment

### Phase 2: Execution (upgrade-executor)
- Creates git branch: `upgrade-to-templates`
- Backs up critical files
- Copies missing template files
- Updates CLAUDE.md with @imports
- Preserves custom content

### Phase 3: Validation (upgrade-bridge)
- Verifies all @imports resolve
- Tests existing commands still work
- Checks agents preserved
- Creates final upgrade report

---

## When to Use

**Use this command when**:
- You have an existing triads project
- You want to upgrade to new template system
- You want @import structure for maintainability
- You want constitutional architecture enforcement

**Don't use when**:
- Starting a new project (use `/triads:generate-triads` instead)
- Already using template system
- Don't have `templates/` directory

---

## Usage

```bash
/upgrade-to-templates
```

No arguments required - the agents will discover everything automatically.

---

## What Gets Added

### Constitutional Principles (6 files)
- `.claude/constitutional/evidence-based-claims.md`
- `.claude/constitutional/uncertainty-escalation.md`
- `.claude/constitutional/multi-method-verification.md`
- `.claude/constitutional/complete-transparency.md`
- `.claude/constitutional/assumption-auditing.md`
- `.claude/constitutional/communication-standards.md`

### Software Methodologies (4 files)
- `.claude/methodologies/software/tdd-methodology.md`
- `.claude/methodologies/software/code-quality-standards.md`
- `.claude/methodologies/software/security-protocols.md`
- `.claude/methodologies/software/git-workflow.md`

### Framework Skills (6 files)
- `.claude/skills/framework/validate-knowledge.md`
- `.claude/skills/framework/escalate-uncertainty.md`
- `.claude/skills/framework/cite-evidence.md`
- `.claude/skills/framework/validate-assumptions.md`
- `.claude/skills/framework/multi-method-verify.md`
- `.claude/skills/framework/bridge-compress.md`

### Standard Output Protocols (2 files)
- `.claude/protocols/standard-output.md` - OUTPUT envelope format
- `.claude/protocols/node-types.md` - Knowledge graph node types registry

### Brief Skills (Domain-Specific - 3 files for software)
- `.claude/skills/software-development/bug-brief.md`
- `.claude/skills/software-development/feature-brief.md`
- `.claude/skills/software-development/refactor-brief.md`

**What brief skills do**: Transform vague input → actionable specifications
- "login is broken" → Complete BugBrief specification
- "add dark mode" → Complete FeatureBrief specification
- "code is messy" → Complete RefactorBrief specification

### Updated CLAUDE.md
- Converts inline principles to @imports
- Adds methodology @imports
- Preserves custom sections (triad routing, knowledge mgmt)

---

## What Gets Preserved

✅ **All existing triads** (idea-validation, design, implementation, garden-tending, deployment)
✅ **All custom commands** (knowledge-*, workflows-*, etc.)
✅ **Output styles** (.claude/output-styles/)
✅ **Analysis and reports** (any custom work)
✅ **Knowledge management** (system remains intact)

**Nothing is deleted or overwritten** - only additions and CLAUDE.md merge.

---

## Safety Features

### Git Branch
Creates `upgrade-to-templates` branch before any changes.

**Rollback**:
```bash
git checkout main
git branch -D upgrade-to-templates
```

### Backups
Creates backups before critical changes:
- `CLAUDE.md.backup` (original CLAUDE.md)
- `.claude/agents.backup/` (original agents)

### Validation
Validates after each phase:
- Files copied successfully
- @imports resolve
- Commands still work
- No regressions

---

## Expected Output

The triad will produce 3 reports:

### 1. Gap Analysis Report
- Current state vs. target state
- Missing components identified
- Risk assessment
- Upgrade plan with phases

### 2. Execution Report
- Each phase execution status
- Files copied
- CLAUDE.md changes
- Issues encountered

### 3. Final Upgrade Report
- Validation results
- Quality assessment (score)
- Regression check
- Recommendations

**At the end, you'll get a comprehensive report with next steps.**

---

## Example Session

```
User: /upgrade-to-templates

Claude: I'll invoke the System Upgrade Triad to analyze and upgrade your project.

[Invokes gap-analyzer]

gap-analyzer: Analyzing current structure...
- Found: CLAUDE.md (root)
- Found: 5 existing triads
- Found: Custom commands
- Missing: Constitutional principles (@import structure)
- Missing: Software methodologies
- Missing: Framework skills

Creating upgrade plan with 7 phases...

[Gap analysis report generated]

[Invokes upgrade-executor]

upgrade-executor: Executing upgrade plan...
Phase 1: Safety Measures
  ✅ Created branch: upgrade-to-templates
  ✅ Backed up CLAUDE.md

Phase 2: Constitutional Principles
  ✅ Copied 6 files to .claude/constitutional/

Phase 3: Software Methodologies
  ✅ Copied 4 files to .claude/methodologies/software/

Phase 4: Framework Skills
  ✅ Copied 6 files to .claude/skills/framework/

Phase 5: CLAUDE.md Update
  ✅ Merged with @imports
  ✅ Preserved custom sections

[Execution report generated]

[Invokes upgrade-bridge]

upgrade-bridge: Validating upgrade...
  ✅ All 16 @imports resolve
  ✅ All commands preserved
  ✅ All agents preserved
  ✅ No regressions found

Quality Score: 98%

Recommendation: MERGE TO MAIN

[Final upgrade report generated]

---

✅ Upgrade complete! Your project now uses the template system.

Next steps:
1. Review the upgrade report
2. Merge to main: git checkout main && git merge upgrade-to-templates
3. Test in Claude Code to verify @imports load
4. Celebrate - you're now dogfooding the system! 🎉
```

---

## Troubleshooting

### Issue: "@imports not resolving"
**Cause**: File paths incorrect or files missing
**Solution**: Check `.claude/constitutional/`, `.claude/methodologies/software/`, `.claude/skills/framework/` exist with correct files

### Issue: "Commands not working"
**Cause**: Commands directory moved or renamed
**Solution**: Verify `.claude/commands/` preserved, check command file names unchanged

### Issue: "Agents missing"
**Cause**: Unexpected directory changes
**Solution**: Check `.claude/agents.backup/` exists, restore if needed

### Issue: "CLAUDE.md broken"
**Cause**: Merge conflict or syntax error
**Solution**: Use `CLAUDE.md.backup` to restore, retry merge carefully

---

## After Upgrade

### Immediate
1. **Merge to main**: `git checkout main && git merge upgrade-to-templates`
2. **Test**: Load project in Claude Code, verify @imports work
3. **Clean up**: Delete backups: `rm CLAUDE.md.backup && rm -rf .claude/agents.backup`

### Optional
1. **Customize methodologies**: Tailor templates to project needs
2. **Add other domains**: If project expands (research, content, business)
3. **Create domain skills**: Based on methodology templates
4. **Update documentation**: Note upgraded architecture

---

## Benefits of Upgrade

**Before**:
- ❌ Constitutional principles inline in CLAUDE.md (hard to maintain)
- ❌ No methodology templates
- ❌ Skills must be commands (not keyword-discoverable)
- ❌ Harder to scale to other domains

**After**:
- ✅ Constitutional principles @imported (maintainable, reusable)
- ✅ Software methodology templates (TDD, code quality, security, git)
- ✅ Framework skills (keyword-discoverable)
- ✅ Scalable architecture for other domains
- ✅ Defense-in-depth enforcement (5 layers)
- ✅ Ready for full dogfooding

---

## Related Commands

- `/triads:generate-triads` - Generate new project from scratch
- `/knowledge-status` - Check knowledge management system
- `/workflows-list` - List available triads

---

**Status**: Ready to use
**Risk**: LOW (creates branch, backs up files, can rollback)
**Recommendation**: Run this to dogfood the new template system!
