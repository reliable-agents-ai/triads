# Triads User Guide

> A simple guide to installing, generating, and customizing your workflow system

---

## What is Triads?

Triads is a **workflow system for Claude Code** that helps you organize complex work into phases (called "triads"). Each triad has specialized agents that work together and hand off context to the next phase.

**Example workflows**:
- **Software Development**: Idea Validation → Design → Implementation → Testing → Deployment
- **RFP Writing**: Analysis → Strategy → Writing → Review
- **Content Creation**: Research → Planning → Writing → Editing

---

## Quick Start

### 1. Install the Plugin (Once)

```bash
# Install triads plugin globally
claude plugin install triads

# Or install from local directory (development)
claude plugin install ./path/to/triads-plugin
```

**What you get**:
- Generator that interviews you and creates custom agents
- System hooks that manage knowledge graphs automatically
- `/generate-triads` command available in all projects

---

### 2. Generate Your Custom Workflow (Per Project)

```bash
# Start Claude Code in your project
cd ~/my-rfp-project
claude code

# Run the generator
> /generate-triads
```

**What happens**:

1. **Interview**: The generator asks about your workflow
   ```
   - What type of work do you do?
   - What phases does your work go through?
   - Where do you lose context or make mistakes?
   ```

2. **Design**: It proposes 2-3 triad structures
   ```
   OPTION A: 3 Triads (Simpler)
   Analysis → Strategy → Writing

   OPTION B: 4 Triads (More Specialized)
   Analysis → Strategy → Writing → Review

   Which fits better?
   ```

3. **Generation**: Creates custom agents for YOUR workflow
   ```
   ✓ .claude/agents/rfp-analysis/analyst.md
   ✓ .claude/agents/rfp-analysis/researcher.md
   ✓ .claude/agents/rfp-strategy/strategist.md
   ✓ .claude/agents/rfp-writing/writer.md
   ✓ .claude/ROUTING.md

   ✅ Custom RFP workflow generated!
   🔄 Restart session to activate agents
   ```

4. **Restart**: Exit and restart Claude Code
   ```bash
   exit
   claude code
   ```

---

### 3. Use Your Workflow

```bash
# Invoke a triad
> Start RFP Analysis: evaluate Acme Corp RFP requirements

# Agents work sequentially
Analyst → Researcher → Synthesizer
  ↓         ↓            ↓
Knowledge graph builds context

# Move to next phase
> Start RFP Strategy: develop win themes based on analysis

# Context automatically carries forward
```

---

## Understanding the System

### What's Installed Where?

```
Plugin (Global)                      Project (Your Work)
~/.claude/plugins/triads/           ~/my-project/.claude/
├── hooks/                          ├── agents/              ✏️ YOU OWN
│   └── on_stop.py                  │   ├── rfp-analysis/
├── km/                             │   ├── rfp-strategy/
│   └── detection.py                │   └── rfp-writing/
├── commands/                       │
│   └── generate-triads.md          ├── graphs/              📊 YOUR DATA
└── agents/                         │   ├── rfp-analysis_graph.json
    └── generator/                  │   └── rfp-strategy_graph.json
                                    │
                                    └── ROUTING.md           ✏️ YOU OWN
```

**Plugin (Managed by triads team)**:
- System machinery (hooks, knowledge management)
- Generator that creates custom agents
- Gets updated when you run `/plugin update triads`
- You don't edit this code

**Project (Managed by you)**:
- Custom agents created FOR your workflow
- Knowledge graphs with your project data
- You edit, customize, commit to git
- Re-generating = starting over (destructive)

---

## Customizing Your Agents

### Agents are YOUR Code

After generation, the agents in `.claude/agents/` are **yours to modify**. Think of them like code scaffolding:

```bash
# Edit anytime
vim .claude/agents/rfp-analysis/analyst.md

# Add domain-specific examples
# Tune instructions for your company
# Add evaluation criteria
# Improve prompts based on experience
```

**This is expected and encouraged!** The generator creates a starting point. You refine it over time.

---

### Example Customization

**Generated analyst (default)**:
```markdown
# RFP Analyst

Analyze RFP requirements and identify key evaluation criteria.

## Your Task
- Read the RFP document
- Extract requirements
- Identify evaluation criteria
```

**Your customized analyst** (after working with it):
```markdown
# RFP Analyst

Analyze RFP requirements and identify key evaluation criteria.

## Your Task
- Read the RFP document
- Extract requirements
- Identify evaluation criteria

## Our Company Standards
- Always check for Section 508 compliance requirements
- Flag any "lowest price technically acceptable" clauses
- Identify page limits early (typically 10-25 pages)

## Examples from Past Wins
- Acme Corp RFP (2024): Focus on innovation, not cost
- TechCo RFP (2023): Emphasized past performance heavily
```

**Save and commit**:
```bash
git add .claude/agents/
git commit -m "Customize RFP analyst with company standards"
```

---

## Updating

### Plugin Updates (System Improvements)

```bash
# Update plugin infrastructure
> /plugin update triads

Updates:
✅ System hooks (bug fixes, new features)
✅ Knowledge management libraries
✅ Generator improvements

Does NOT touch:
✏️ Your custom agents (.claude/agents/)
📊 Your knowledge graphs (.claude/graphs/)
```

**When to update**:
- New features released
- Bug fixes available
- Security patches

**Impact**: Zero impact on your custom agents

---

### Customizing Agents (Your Work)

```bash
# Edit agents anytime
vim .claude/agents/rfp-writing/writer.md

# Commit changes
git add .claude/agents/
git commit -m "Add company branding guidelines"
```

**Your team gets improvements**:
```bash
git pull  # Gets your custom agent improvements
```

---

### Re-Generating (Starting Over)

```bash
# If you want to completely redesign your workflow
> /generate-triads

⚠️  Warning: This will overwrite:
  - .claude/agents/ (your custom agents)
  - .claude/ROUTING.md (your routing config)

  Your knowledge graphs will be preserved.

Continue? (y/N)
```

**Use re-generation when**:
- Workflow fundamentally changed
- Want to try different triad structure
- Starting fresh on new project type

**Before re-generating**:
```bash
# Backup your customizations if needed
cp -r .claude/agents/ .claude/agents.backup/
```

---

## How It Works

### Knowledge Graphs (Automatic)

As agents work, they create knowledge graphs that track:
- Entities (requirements, decisions, findings)
- Relationships (dependencies, conflicts)
- Uncertainties (things needing resolution)

```bash
# View your knowledge
cat .claude/graphs/rfp-analysis_graph.json

# Knowledge automatically carries forward
# When you "Start RFP Strategy", it loads
# context from "RFP Analysis" graph
```

**You don't manage graphs manually** - agents update them via `[GRAPH_UPDATE]` blocks in their output.

---

### Routing (Natural Suggestions)

The system suggests which triad to use:

```
You: "I need to analyze this RFP"

Claude: This sounds like RFP Analysis work.
        Would you like me to `Start RFP Analysis: analyze requirements`?

You: yes

Claude: [Invokes rfp-analysis triad]
```

**Customize routing** (optional):
```bash
# Edit routing suggestions
vim .claude/ROUTING.md

# Add examples specific to your domain
```

---

## Common Workflows

### Software Development

```bash
# Generate software dev triads
> /generate-triads
  → Choose: Idea Validation → Design → Implementation → Testing

# Use them
> Start Idea Validation: add OAuth2 authentication
> Start Design: OAuth2 integration architecture
> Start Implementation: build OAuth2 flow
```

---

### Content Creation

```bash
# Generate content triads
> /generate-triads
  → Choose: Research → Planning → Writing → Editing

# Use them
> Start Research: investigate AI safety regulations
> Start Planning: outline blog post structure
> Start Writing: draft blog post
```

---

## Team Usage

### Sharing Custom Agents

```bash
# Commit your customized agents
git add .claude/agents/
git commit -m "Add company-specific RFP evaluation criteria"
git push

# Team members pull
git pull

# They get your custom agents ✅
# They already have plugin installed ✅
# Works immediately
```

---

### Team Standards

**Everyone installs plugin once**:
```bash
claude plugin install triads
```

**Project has custom agents**:
```bash
git clone company/rfp-project
cd rfp-project
claude code

# Custom agents already in .claude/agents/
# Works immediately
```

---

## FAQ

### Do I need to install per project?

**No!** Install the plugin once globally:
```bash
claude plugin install triads  # Once, works everywhere
```

Then generate custom agents per project:
```bash
cd ~/project-a
claude code
> /generate-triads  # Creates agents for this project

cd ~/project-b
claude code
> /generate-triads  # Creates different agents for this project
```

---

### Can I use the same agents across projects?

Yes! If you generate the same workflow type (e.g., "RFP Writing"), you can copy agents:

```bash
# Copy agents from one project to another
cp -r ~/project-a/.claude/agents/ ~/project-b/.claude/agents/

# Or commit to template repo
git clone company/rfp-template
# Use template's agents as starting point
```

---

### What if I break an agent?

Just restore from git:
```bash
git checkout .claude/agents/rfp-analysis/analyst.md
```

Or re-generate:
```bash
> /generate-triads
# Regenerate just that triad
```

---

### Can I create agents manually without the generator?

Yes! The generator is optional. You can:

1. **Create agents manually**:
   ```bash
   mkdir -p .claude/agents/my-triad
   vim .claude/agents/my-triad/my-agent.md
   ```

2. **Copy from examples**:
   ```bash
   # Plugin includes example agents
   cp ~/.claude/plugins/triads/examples/agent.md .claude/agents/my-triad/
   ```

The plugin works with ANY agents in `.claude/agents/` - generated or manual.

---

### How do I uninstall?

**Remove plugin**:
```bash
claude plugin uninstall triads
```

**Clean up project** (optional):
```bash
# Remove generated agents (if you want)
rm -rf .claude/agents/

# Keep knowledge graphs (your data)
# Keep in .claude/graphs/
```

---

## Troubleshooting

### "Command not found: /generate-triads"

**Solution**: Plugin not installed or not enabled
```bash
claude plugin list           # Check if installed
claude plugin install triads # Install if missing
```

---

### "Agents not loading after generation"

**Solution**: Restart session required
```bash
exit
claude code  # Restart to load new agents
```

---

### "Knowledge graphs not updating"

**Solution**: Check hook is working
```bash
# Look for stderr output after Claude responds
# Should see "📊 Knowledge Graph Update"

# If missing, check plugin hooks
claude --debug  # Shows hook execution
```

---

### "I want different triad structure"

**Solution**: Re-generate
```bash
# Backup first (if you have customizations)
cp -r .claude/agents/ .claude/agents.backup/

# Regenerate
> /generate-triads
```

---

## Next Steps

1. **Install plugin**: `claude plugin install triads`
2. **Generate workflow**: `/generate-triads` in your project
3. **Try it out**: `Start [TriadName]: [task]`
4. **Customize agents**: Edit `.claude/agents/` to fit your needs
5. **Share with team**: Commit customized agents to git

---

## Support

- **Documentation**: [Full docs](../README.md)
- **GitHub Issues**: [Report bugs](https://github.com/reliable-agents-ai/triads/issues)
- **Discussions**: [Ask questions](https://github.com/reliable-agents-ai/triads/discussions)

---

**Remember**:
- **Plugin** = System tools (managed by triads)
- **Agents** = Your customized workflow (managed by you)
- **Graphs** = Your project data (grows as you work)

Happy workflow building! 🎯
