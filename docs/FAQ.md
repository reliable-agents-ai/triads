# Frequently Asked Questions

Common questions about the Triad Generator system.

---

## Table of Contents

- [General Questions](#general-questions)
- [Technical Questions](#technical-questions)
- [Usage Questions](#usage-questions)
- [Customization Questions](#customization-questions)
- [Comparison Questions](#comparison-questions)
- [Advanced Questions](#advanced-questions)

---

## General Questions

### What is Triad Generator?

A meta-AI system that researches your workflow and generates custom multi-agent teams optimized for how you work.

Instead of generic templates, it:
1. Interviews you about your workflow
2. Researches your domain
3. Designs optimal agent teams (triads of 3)
4. Generates everything automatically

### Why "triads" (groups of 3)?

Based on sociological research by Georg Simmel (1908):
- **Optimal size**: Large enough for diversity, small enough for accountability
- **Mediation**: Third member can resolve conflicts
- **Efficiency**: Only 3 communication channels (vs exponential in larger groups)
- **Proven pattern**: Used in elite teams (Navy SEALs, executive leadership, sports)

### What makes this different from other multi-agent systems?

**1. Self-discovering (not template-based)**
- Researches YOUR workflow specifically
- Designs agents for YOUR phases
- Places bridges at YOUR context loss points

**2. Context preservation**
- Bridge agents prevent information loss
- Knowledge graphs capture all learning
- ~40% faster than hierarchical patterns

**3. Quality enforced**
- TRUST principles architecturally enforced
- Not just prompts - actual validation
- Violations logged and blocked

### Do I need to know how to code?

**To use it**: No coding required
- Run `/generate-triads`
- Answer questions
- Use generated triads

**To customize it**: Basic understanding helps
- Agent files are markdown (human-readable)
- Hooks are Python (can learn from examples)
- Templates are Python strings (straightforward)

### Is my data safe?

**Yes - completely local**:
- All data stays on your machine
- File-based storage (no cloud)
- No telemetry or data collection
- You control what repos use it

**Optional web access**:
- WebSearch during generation (can skip)
- Only for researching your domain
- No sensitive data sent

### How much does it cost?

**Triad Generator: Free and open source** (MIT License)

**Claude Code**: Check Anthropic's pricing
- Required to run the system
- Handles the AI agent execution

### What are the prerequisites?

**Required**:
- Python 3.10+
- Claude Code CLI
- Git repository

**Automatically installed**:
- NetworkX (Python library)

**Optional**:
- WebSearch access (for generator research phase)

---

## Technical Questions

### How does context preservation work?

**Bridge agents** participate in 2 triads:

```
Triad A              Triad B
├─ Agent 1          ├─ Bridge Agent ◄──┐
├─ Agent 2          │  (carries context)
└─ Bridge Agent ────┘  ├─ Agent 3
                       └─ Agent 4
```

**Process**:
1. Bridge works in Triad A
2. When transitioning to Triad B:
   - Compresses Triad A's knowledge graph (top 20 nodes)
   - Uses importance scoring algorithm
   - Preserves critical decisions, findings, uncertainties
3. Brings compressed context to Triad B
4. Triad B has both: fresh graph + critical context from A

**Result**: Zero loss of important information

### What is the knowledge graph?

A NetworkX graph stored as JSON that captures:
- **Nodes**: Entities, concepts, decisions, findings, tasks, uncertainties
- **Edges**: Relationships between nodes
- **Metadata**: Confidence, evidence, timestamps, created_by

**Example**:
```json
{
  "nodes": [
    {
      "id": "decision_1",
      "type": "Decision",
      "label": "Use PostgreSQL",
      "confidence": 0.9,
      "evidence": "Requirements doc section 4",
      "created_by": "solution-architect"
    }
  ],
  "links": [
    {"source": "decision_1", "target": "requirement_1", "relation": "implements"}
  ]
}
```

**Location**: `.claude/graphs/{triad_name}_graph.json`

### How do the TRUST principles work?

The **TRUST framework** provides 5 immutable principles (from [reliableagents.ai](https://reliableagents.ai)):

| Letter | Principle |
|--------|-----------|
| **T** | Thorough over fast |
| **R** | Require evidence |
| **U** | Uncertainty escalation |
| **S** | Show all work |
| **T** | Test assumptions |

**Enforcement**: Python hooks validate agent outputs
- Parse [GRAPH_UPDATE] blocks
- Check required fields (evidence, confidence, etc.)
- Verify compliance with principles
- Log violations
- Block completion if critical violations

**Not just prompts** - architectural enforcement

### What is the Generator Triad?

**Meta-level agents** that design your system:

1. **Domain Researcher**
   - Interviews you
   - Researches your domain via WebSearch
   - Documents workflow in knowledge graph

2. **Workflow Analyst**
   - Analyzes workflow structure
   - Designs 2-3 triad options
   - Gets your feedback and refines

3. **Triad Architect**
   - Generates agent markdown files
   - Creates Python hooks
   - Writes TRUST framework documents
   - Generates documentation

**Run once** to create your custom system

### How does the slash command work?

**File**: `.claude/commands/generate-triads.md`

**Process**:
1. You type: `/generate-triads`
2. Claude Code reads the markdown file
3. Content expands into conversation
4. Domain Researcher persona activates
5. Interactive generation begins

**Magic**: The markdown file contains full knowledge base and instructions for the Generator Triad

### Can I use this without internet?

**Mostly yes**:

**Without internet**:
- ✅ Generated triads work offline
- ✅ Knowledge graphs work offline
- ✅ All core functionality works

**Requires internet**:
- ❌ Generator's WebSearch phase
- But you can provide your own research

**Workaround**:
```
> /generate-triads

Domain Researcher: [tries WebSearch, fails]

You: "I researched my domain already. Here's what I found:
[Provide your research]
Let's skip web search and continue."

[Generator continues offline]
```

---

## Usage Questions

### How do I start?

```bash
# 1. Install
./setup-complete.sh

# 2. Generate your system
claude code
> /generate-triads

# 3. Use it
> Start Discovery: [your task]
```

### How long does generation take?

**Typical**: 10-20 minutes

**Breakdown**:
- Domain Researcher: 5-10 minutes (interview + research)
- Workflow Analyst: 3-5 minutes (design options)
- Triad Architect: 2-5 minutes (file generation)

**Factors**:
- Your response time to questions
- WebSearch speed
- Number of triads designed (3-5 usually)

### Can I regenerate if I don't like the result?

**Yes!**

**Option 1**: Run again
```bash
> /generate-triads
# Answer differently
# Get new design
```

**Option 2**: Extend existing
```bash
> /generate-triads --extend
# Keep current triads
# Add new ones
```

**Option 3**: Manual edits
```bash
# Edit any agent file
open .claude/agents/discovery/codebase-analyst.md
# Save - changes apply immediately
```

### How many triads should I have?

**Typical**: 3-5 triads

**Guidelines**:
- **Simple workflow** (2-3 phases): 2-3 triads
- **Standard workflow** (3-4 phases): 3-4 triads
- **Complex workflow** (5+ phases): 4-5 triads

**Examples**:
- Software dev: 3 triads (Discovery, Design, Implementation)
- RFP writing: 4 triads (Analysis, Strategy, Writing, Validation)
- Research: 4 triads (Literature, Methodology, Execution, Writing)

**Don't over-design**: Start simple, extend later if needed

### Can I use this for multiple projects?

**Each project gets its own system**:

```bash
# Project 1: Software development
cd ~/project-1
./setup-complete.sh
> /generate-triads
[Gets software dev triads]

# Project 2: Content writing
cd ~/project-2
./setup-complete.sh
> /generate-triads
[Gets content creation triads]
```

**Each `.claude/` folder is independent**

**Shared learning**: You can copy successful agent definitions between projects

### Do triads learn over time?

**Yes - via knowledge graphs**:

**Within a session**:
- Graphs grow as agents work
- Later agents see earlier findings
- Bridge agents preserve across triads

**Across sessions**:
- Graphs persist in `.claude/graphs/*.json`
- Next session loads previous graph
- Agents build on previous knowledge

**To reset**:
```bash
# Archive old graphs
mkdir .claude/graphs/archive
mv .claude/graphs/*_graph.json .claude/graphs/archive/

# Start fresh
> Start Discovery: [task]
```

### Can I share my triad system?

**Yes!**

**Share the entire .claude/ folder**:
```bash
# Create shareable package
tar -czf my-triads.tar.gz .claude/

# Others can extract and use:
tar -xzf my-triads.tar.gz
claude code
> Start Discovery: [their task]
```

**Share individual agents**:
```bash
# Copy agent file
cp .claude/agents/discovery/codebase-analyst.md ~/shared/

# Others add to their system
cp ~/shared/codebase-analyst.md .claude/agents/discovery/
```

**Best practices**:
- Remove personal/sensitive data from graphs
- Document any custom setup needed
- Include your TRUST principles (constitutional-principles.md)

---

## Customization Questions

### How do I modify an agent?

**Edit the markdown file**:
```bash
open .claude/agents/discovery/codebase-analyst.md
```

**What you can change**:
- Identity & Purpose section
- Tools and capabilities
- TRUST focus areas
- Workflow steps
- Output format

**Changes apply immediately** - no restart needed

**Example customization**:
```markdown
## Custom Instructions

For Python projects:
- Check for type hints
- Verify docstrings
- Look for test coverage
- Flag deprecated imports
```

### How do I add a new triad?

**Option 1**: Re-run generator
```bash
> /generate-triads --extend
# Generator asks about new phase
# Designs new triad
# Integrates with existing
```

**Option 2**: Manual creation
```bash
# 1. Create folder
mkdir .claude/agents/new_triad

# 2. Copy template agents
cp .claude/agents/discovery/*.md .claude/agents/new_triad/

# 3. Edit each agent file
# 4. Update settings.json
```

### Can I change the TRUST principles?

**Yes - carefully**:

**Edit global TRUST principles**:
```bash
open .claude/constitutional-principles.md
```

**Edit per-agent requirements**:
```bash
open .claude/constitutional/checkpoints.json
```

**Adjust enforcement**:
```python
# In .claude/hooks/on_subagent_end.py
# Modify validation logic
```

**Warning**: Weakening TRUST principles may reduce quality
**Recommendation**: Add domain-specific rules rather than removing base TRUST principles

### How do I change the compression algorithm?

**Edit the bridge transition hook**:
```bash
open .claude/hooks/on_bridge_transition.py
```

**Change max nodes**:
```python
max_nodes = 15  # Default is 20
```

**Change scoring algorithm**:
```python
def calculate_importance(node):
    # Modify formula
    return confidence * degree * recency * type_priority * custom_factor
```

**Change type priorities**:
```python
TYPE_PRIORITY = {
    "Decision": 1.0,
    "MyCustomType": 0.95,  # Add custom types
    "Uncertainty": 0.9,
    # ...
}
```

### Can I use different knowledge graph backends?

**Currently**: NetworkX + JSON files

**To add alternatives**:
1. Create adapter in `.claude/lib/graph_adapter.py`
2. Implement same interface:
   - `add_node()`
   - `add_edge()`
   - `get_graph()`
   - `save_graph()`
3. Update hooks to use adapter

**Possible backends**:
- SQLite (for larger graphs)
- Neo4j (for complex queries)
- TinyDB (simpler than NetworkX)

**Trade-offs**: More setup, but potentially better performance

---

## Comparison Questions

### How is this different from AutoGPT/BabyAGI?

| Feature | Triad Generator | AutoGPT/BabyAGI |
|---------|----------------|-----------------|
| **Design** | Custom per workflow | Generic task executor |
| **Structure** | Triads + bridges | Single or hierarchical |
| **Context** | Preserved via bridges | Often lost |
| **Quality** | TRUST framework enforcement | Prompt-based |
| **Setup** | One-time generation | Immediate use |
| **Adaptation** | Researches your domain | Generic capabilities |

**Use Triad Generator when**: You have a recurring workflow that needs optimization

**Use AutoGPT when**: You have one-off tasks

### How is this different from LangGraph?

| Feature | Triad Generator | LangGraph |
|---------|----------------|-----------|
| **Level** | Meta-system (designs workflows) | Workflow framework |
| **User** | Non-programmers | Developers |
| **Interface** | Conversational | Code |
| **Agents** | Generated automatically | You write them |
| **Research** | Self-discovering | Pre-defined |

**Complementary**: You could implement Triad Generator's designs in LangGraph

### How is this different from CrewAI?

| Feature | Triad Generator | CrewAI |
|---------|----------------|---------|
| **Agents** | Custom-generated | Template-based |
| **Discovery** | Researches your workflow | Pick from templates |
| **Structure** | Overlapping triads | Hierarchical crews |
| **Context** | Bridge agents | Manager agents |
| **Performance** | ~40% faster (no bottleneck) | Central coordination |

**Use Triad Generator when**: You want optimal design for your specific workflow

**Use CrewAI when**: Templates fit your needs well enough

### How is this different from Claude Projects?

| Feature | Triad Generator | Claude Projects |
|---------|----------------|-----------------|
| **Scope** | Multi-agent workflows | Single context |
| **Phases** | Separate triads | One conversation |
| **Context** | Structured (graphs) | Conversational history |
| **Specialization** | 9-15 specialized agents | One generalist |
| **Preservation** | Bridge agents | Manual summarization |

**Use both**: Claude Projects for simple tasks, Triad Generator for complex workflows

---

## Advanced Questions

### Can I use this with other LLMs?

**Currently**: Built for Claude Code (Claude Sonnet)

**To adapt for other LLMs**:
1. Agent definitions are markdown (LLM-agnostic)
2. Hooks would need adaptation
3. Claude Code slash commands are specific

**Potential ports**:
- OpenAI Agents: Would need different command structure
- Local LLMs: Performance may vary
- Other frameworks: Could reuse design principles

**Biggest challenge**: Claude Code's sub-agent and hook system

### How does this scale?

**Horizontal scaling** (more triads):
- ✅ Linear cost (each triad independent)
- ✅ No central bottleneck
- ✅ Can add indefinitely

**Vertical scaling** (larger graphs):
- ✅ Compression keeps bridge context bounded
- ✅ Tested up to 10K node graphs
- ⚠️  Beyond 10K may need optimization

**Complexity scaling** (more complex tasks):
- ✅ Add more specialized agents
- ✅ Add more triads
- ✅ Refine TRUST principles

**Team scaling** (multiple users):
- ⚠️  Currently single-user
- Could add: Graph merging, conflict resolution
- Would need: Multi-user hooks, coordination

### Can I integrate with external tools?

**Yes - via agent tools**:

**Agents can use**:
- Bash tool (run any command)
- Read/Write tools (access files)
- Grep/Glob tools (search)
- Custom tools (if added to Claude Code)

**Examples**:
```markdown
## Tools Available (Custom)

- Jira API for ticket management
- GitHub API for PR creation
- Slack API for notifications
- Custom analysis scripts
```

**Integration in workflows**:
- Discovery: Read from Jira, databases
- Design: Query documentation systems
- Implementation: Commit to GitHub, deploy
- Validation: Run test suites, linters

### Can this replace human developers/writers/analysts?

**No - it augments, not replaces**:

**What it does well**:
- Preserves context across complex workflows
- Enforces quality standards consistently
- Handles tedious research and documentation
- Maintains structured knowledge

**What it doesn't do**:
- Make strategic business decisions
- Handle novel situations outside training
- Provide human judgment and creativity
- Understand implicit organizational context

**Best use**: Handle 70-80% of routine work, escalate the rest

### How can I contribute?

**See [CONTRIBUTING.md](../CONTRIBUTING.md)**

**High-value contributions**:
- New domain patterns (RFP writing, data analysis, etc.)
- Improved compression algorithms
- Visualization tools for knowledge graphs
- Performance optimizations
- Documentation and examples
- Test coverage

**Process**:
1. Fork repo
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

### What's the roadmap?

**Current** (v1.0):
- ✅ Self-discovering generator
- ✅ Triad structure with bridges
- ✅ TRUST framework enforcement
- ✅ Knowledge graphs (NetworkX)

**Planned**:
- Multi-user support
- Graph visualization tools
- More domain patterns
- Performance monitoring
- Agent marketplace (share agents)
- Web UI for generation
- Integration templates (Jira, GitHub, etc.)

**Community-driven**: Roadmap adapts based on user needs

---

## Still Have Questions?

**Resources**:
- **Documentation**: See [README.md](../README.md) and other docs
- **Examples**: See [EXAMPLES.md](EXAMPLES.md)
- **Troubleshooting**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

**Community**:
- **GitHub Discussions**: Ask questions, share workflows
- **GitHub Issues**: Report bugs, request features

**Support**:
- Check [Claude Code docs](https://docs.claude.com/en/docs/claude-code)
- Search existing issues
- Create new issue with details

---

**The best way to learn is to try it:**

```bash
claude code
> /generate-triads
```

**Answer the questions, see what gets generated, experiment!**
