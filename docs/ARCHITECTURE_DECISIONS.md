# Architecture Decision Records

> Key decisions made during the triads system design

---

## ADR-001: Plugin Architecture Over Project Installation

**Date**: 2025-10-15
**Status**: Accepted
**Context**: Originally designed as per-project `.claude/` installation

### Decision

Convert triads to a **Claude Code plugin** installed globally.

### Rationale

**Problems with project installation**:
- ❌ Pollutes user's `.claude/` with 20+ files
- ❌ Must install per-project (not true drop-in)
- ❌ Updates require re-running installer in each project
- ❌ Conflicts with user's existing `.claude/` setup
- ❌ Not portable across projects

**Benefits of plugin architecture**:
- ✅ Install once globally (`~/.claude/plugins/triads/`)
- ✅ Works in all projects automatically
- ✅ Easy updates (`/plugin update triads`)
- ✅ Non-invasive (only `.claude/graphs/` in project)
- ✅ Team-friendly (publish to marketplace)
- ✅ Industry-standard extension model

### Implementation

```
~/.claude/plugins/triads/        # Plugin (global)
├── .claude-plugin/
│   └── plugin.json
├── hooks/
├── km/
├── commands/
└── agents/generator/

user-project/.claude/            # Project (minimal)
├── agents/                      # Generated, user-owned
└── graphs/                      # Project data
```

### Consequences

- **Positive**: True drop-in, easy updates, works everywhere
- **Negative**: Requires Claude Code plugin system (available since recent release)
- **Migration**: Existing installations need to install plugin + migrate

---

## ADR-002: Scaffolding Model for Generated Agents

**Date**: 2025-10-15
**Status**: Accepted
**Context**: Question of whether generated agents are managed by plugin or user

### Decision

Generated agents follow the **scaffolding pattern** - user owns them after generation.

### Rationale

**Like**:
- `rails scaffold` - generates code you modify
- `create-react-app` eject - you own the config
- `dotnet new` templates - starting point

**Not like**:
- npm packages (you don't edit node_modules)
- VS Code extensions (you don't edit extension code)

**User needs**:
- Add domain-specific examples to agents
- Tune prompts based on experience
- Add company-specific evaluation criteria
- Commit customizations to git for team sharing

### Implementation

**Generator creates**:
```
.claude/agents/
├── rfp-analysis/
│   ├── analyst.md         # ✏️ User owns after generation
│   └── researcher.md      # ✏️ User owns after generation
└── rfp-strategy/
    └── strategist.md      # ✏️ User owns after generation
```

**User modifies**:
```bash
vim .claude/agents/rfp-analysis/analyst.md
# Add examples, tune instructions, improve prompts

git add .claude/agents/
git commit -m "Customize analyst with company standards"
```

**Re-generation**:
```bash
> /generate-triads

⚠️ Warning: This will overwrite your custom agents.
   Backup first if needed.

Continue? (y/N)
```

### Consequences

- **Positive**: Users can customize freely, commit to git, share with team
- **Negative**: Re-generation is destructive (loses customizations)
- **Mitigation**: Clear warnings, suggest backup before re-generation

---

## ADR-003: Hooks in Plugin, Not Project

**Date**: 2025-10-15
**Status**: Accepted
**Context**: Hooks are executable code that needs lifecycle management

### Decision

Hooks live in **plugin**, not project, even though they operate on project data.

### Rationale

**Hook code characteristics**:
- 🔧 Needs bug fixes, security patches
- 📦 Has dependencies (KM libraries)
- ♻️ Generic algorithms work for any project
- 🎯 Discovers project structure dynamically

**If hooks in project**:
- ❌ Every project has duplicate code (697 lines × N projects)
- ❌ Bug fix requires re-running installer everywhere
- ❌ Users might accidentally break system code
- ❌ Version drift across projects

**If hooks in plugin**:
- ✅ Single source of truth
- ✅ Update once, propagate everywhere
- ✅ Users can't accidentally break system
- ✅ Semantic versioning for compatibility

**Hook code is already generic**:
```python
# Discovers triads dynamically (no hardcoding)
def lookup_agent_triad(agent_name):
    pattern = f".claude/agents/**/{agent_name}.md"
    matches = glob.glob(pattern, recursive=True)
    # Works with ANY custom agents!
```

### Implementation

```
Plugin:
~/.claude/plugins/triads/hooks/
├── hooks.json                    # Hook registration
├── session_start.py              # Inject routing + graphs
└── on_stop.py                    # Parse [GRAPH_UPDATE] blocks

Project:
.claude/
├── agents/                       # Hook discovers these
└── graphs/                       # Hook updates these
```

### Consequences

- **Positive**: Easy maintenance, safe updates, generic algorithms
- **Negative**: Hook changes require plugin update (acceptable)
- **Migration**: Move hooks from project to plugin

---

## ADR-004: Delete Auto-Router Entirely

**Date**: 2025-10-15
**Status**: Accepted
**Context**: Auto-router v0.2.0 was 5,500 lines of ML-based routing code

### Decision

**Delete the entire auto-router** (100% code reduction).

Use **natural routing** via documentation instead.

### Rationale

**Original constraint** (violated by v0.2.0):
> "Use Claude Code as the interaction point with the LLM, instead of adding complex logic and integrations to do the same thing"

**Auto-router v0.2.0 violated this**:
- Added sentence-transformers, torch, numpy (2-3GB)
- Built parallel ML infrastructure
- Duplicated Claude's natural intelligence

**Natural routing insight**:
- Claude reads CLAUDE.md automatically (memory system)
- Can suggest triads naturally in conversation
- HITL confirmation provides control
- No code needed!

**Test result**:
- User: "Is there maintenance needed?"
- Expected: "This sounds like Garden Tending work. Would you like me to `Start Garden Tending: maintenance scan`?"
- Problem: CLAUDE.md was overloaded (1,209 lines), directive buried at line 1,134

**Solution**:
- Lean CLAUDE.md (204 lines, routing at line 101)
- Routing examples at line 162 (exactly the test case)
- Military command style (actionable, not documentation)

**For plugin approach**:
- SessionStart hook injects routing from plugin
- Works across all projects
- No project file modification needed

### Implementation

**Delete**:
- `src/triads/router/` (5,500 lines)
  - embedder.py (215 lines)
  - semantic_router.py (180 lines)
  - llm_disambiguator.py (140 lines)
  - router.py (330 lines)
  - All tests (~2,000 lines)

**Create instead**:
- `.claude/ROUTING.md` in plugin (50 lines)
- SessionStart hook reads and injects it

**Result**:
- 100% code reduction
- Zero dependencies removed
- Natural intelligence > artificial rules

### Consequences

- **Positive**: Constraint compliant, simpler, no ML dependencies
- **Negative**: Less automated (user confirms suggestions)
- **Tradeoff**: HITL adds friction but prevents errors (acceptable)

---

## ADR-005: HITL Validation Gates in Design Phase

**Date**: 2025-10-15
**Status**: Accepted
**Context**: Auto-router was over-engineered because no approval gate before implementation

### Decision

Add **mandatory HITL approval gate** after Solution Architect designs, before Design Bridge proceeds.

### Rationale

**Problem identified**:
- Solution Architect designed auto-router with ML infrastructure
- Design Bridge immediately compressed for Implementation
- User couldn't catch over-engineering before expensive work
- Violated constraint discovered after implementation

**Solution**:
- Solution Architect presents design with approval checklist
- User reviews architecture, dependencies, approach
- User must explicitly approve before proceeding
- Design Bridge verifies approval before compression

**Lesson for generator**:
- Embedded in workflow-analyst.md
- All future generated systems include HITL gates
- Documented with auto-router as cautionary example

### Implementation

**Solution Architect** (step 7 added):
```markdown
## Step 7: Present Design for User Approval (CRITICAL)

**STOP HERE**: Do not proceed to Design Bridge until user approves.

## Approval Checklist
- [ ] Architecture makes sense
- [ ] Key decisions are sound
- [ ] Approach is appropriately scoped
- [ ] Dependencies are acceptable
- [ ] Ready to proceed to implementation
```

**Design Bridge** (prerequisites added):
```markdown
## Prerequisites (CRITICAL)

**⚠️ APPROVAL GATE**: This agent should ONLY be invoked after:
1. Solution Architect has completed design
2. User has explicitly approved the design

[Check for approval node in knowledge graph]
```

**Knowledge Graph**:
```json
{
  "node_id": "design_approval_oauth2",
  "type": "Decision",
  "label": "User Approved Design",
  "approved_by": "user",
  "approved_at": "2025-10-15T10:30:00Z"
}
```

### Consequences

- **Positive**: Catches over-engineering early, enforces constraints
- **Negative**: Adds manual step (but that's the point - HITL)
- **Result**: Auto-router problem would have been caught at design phase

---

## ADR-006: Claude Code Configuration Conventions

**Date**: 2025-10-15
**Status**: Accepted
**Context**: Research into Claude Code documentation for appropriate storage locations

### Decision

Follow **Claude Code conventions** for file purposes:

- **settings.json**: Claude Code tool configuration (hooks, permissions, MCP)
- **CLAUDE.md**: Project instructions and workflow documentation
- **Plugins**: Extensions that work across projects

### Research

**From Claude Code docs**:

**settings.json** (docs.claude.com/en/docs/claude-code/settings.md):
> "Configure custom commands to run before or after tool executions"
> Examples: permissions, environment variables, hooks, plugins

**CLAUDE.md** (docs.claude.com/en/docs/claude-code/memory.md):
> "Store project-specific guidelines and preferences"
> Examples: "coding standards", "project architecture details", "common workflow commands"

**Plugins** (docs.claude.com/en/docs/claude-code/plugins):
> "Extend Claude Code with custom functionality that can be shared across projects and teams"

### Rationale

**Triad system is**:
- Not Claude Code configuration (not settings.json)
- More than project guidelines (CLAUDE.md could work but not ideal)
- Cross-project extension (perfect for plugin!)

**Previous approach issues**:
- Storing triad metadata in settings.json violated conventions
- CLAUDE.md became overloaded (1,209 lines)
- No separation between system and project concerns

### Implementation

**Plugin handles**:
- System infrastructure (hooks, KM libraries)
- Default routing directives
- Generator agents
- Commands

**Project contains**:
- Custom agents (generated, user-owned)
- Knowledge graphs (project data)
- Optional routing customization

**CLAUDE.md remains**:
- Project-specific TRUST principles
- Domain-specific guidelines
- Reference to plugin documentation

### Consequences

- **Positive**: Follows Claude Code conventions, clean separation
- **Negative**: Requires understanding of plugin system
- **Result**: Proper architectural boundaries

---

## Summary

| Decision | Outcome | Impact |
|----------|---------|--------|
| **Plugin Architecture** | Install once, works everywhere | True drop-in ✅ |
| **Scaffolding Model** | User owns agents after generation | Customization ✅ |
| **Hooks in Plugin** | System code managed separately | Easy updates ✅ |
| **Delete Auto-Router** | Natural routing via docs | Constraint compliant ✅ |
| **HITL Gates** | User approves designs | Prevents over-engineering ✅ |
| **File Conventions** | Follow Claude Code standards | Clean architecture ✅ |

**Net Result**:
- Removed 5,500 lines of router code
- Converted to plugin architecture
- Added HITL approval gates
- Followed Claude Code conventions
- Created clear user ownership model

**Next Steps**:
1. Create plugin structure
2. Reorganize codebase
3. Test full workflow
4. Publish plugin

---

**Lessons Learned**:
- Start with constraints, not solutions
- Natural intelligence > automation
- Plugins are the right extension model
- User ownership enables customization
- HITL gates catch problems early
