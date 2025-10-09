# Troubleshooting Guide

Solutions to common issues when using the Triad Generator system.

---

## Table of Contents

- [Installation Issues](#installation-issues)
- [Generator Issues](#generator-issues)
- [Triad Execution Issues](#triad-execution-issues)
- [Knowledge Graph Issues](#knowledge-graph-issues)
- [Bridge Agent Issues](#bridge-agent-issues)
- [Hook Issues](#hook-issues)
- [TRUST Violations](#trust-violations)
- [Performance Issues](#performance-issues)

---

## Installation Issues

### Issue: Python version too old

**Error**:
```
Python 3.10+ required, found Python 3.9.x
```

**Solution**:

```bash
# On macOS with Homebrew
brew install python@3.11
python3.11 --version

# On Ubuntu/Debian
sudo apt update
sudo apt install python3.11

# Verify
python3 --version
# Should show 3.10 or higher
```

**Update shell to use new version**:
```bash
# Add to ~/.bashrc or ~/.zshrc
alias python3=/usr/local/bin/python3.11

# Reload
source ~/.bashrc  # or source ~/.zshrc
```

---

### Issue: NetworkX installation fails

**Error**:
```
ERROR: Could not install packages due to an EnvironmentError
```

**Solution 1**: Install with user flag
```bash
pip3 install --user networkx
```

**Solution 2**: Use specific Python version
```bash
python3.11 -m pip install networkx
```

**Solution 3**: Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install networkx
```

**Verify**:
```bash
python3 -c "import networkx; print('NetworkX OK')"
```

---

### Issue: Claude Code not found

**Error**:
```
command not found: claude
```

**Solution**:

1. Install Claude Code:
   - Visit: https://docs.claude.com/en/docs/claude-code
   - Follow installation instructions

2. Verify installation:
   ```bash
   claude --version
   ```

3. If installed but not in PATH:
   ```bash
   # Find Claude Code
   which claude

   # Add to PATH (if needed)
   export PATH="$PATH:/path/to/claude"
   ```

---

### Issue: Permission denied on setup script

**Error**:
```
-bash: ./setup-complete.sh: Permission denied
```

**Solution**:
```bash
chmod +x setup-complete.sh
./setup-complete.sh
```

---

### Issue: Existing .claude/ folder detected

**Error**:
```
⚠️  Existing .claude/ folder detected
Installation aborted to prevent overwriting
```

**Solution 1**: Backup and proceed
```bash
# Create backup
cp -r .claude .claude.backup.$(date +%Y%m%d_%H%M%S)

# Run installer with force flag
./setup-complete.sh --force
```

**Solution 2**: Merge manually
```bash
# Install to temporary location
mkdir temp-install
cd temp-install
/path/to/setup-complete.sh

# Copy only generator components
cp -r temp-install/.claude/generator ../.claude/
cp temp-install/.claude/commands/generate-triads.md ../.claude/commands/

# Clean up
cd ..
rm -rf temp-install
```

**Solution 3**: Review and selective install
```bash
./setup-complete.sh --dry-run
# Review what would be installed

./setup-complete.sh --components=agents,command
# Install only specific components
```

---

## Generator Issues

### Issue: /generate-triads command not found

**Error**:
```
Unknown command: /generate-triads
```

**Solution 1**: Verify file exists
```bash
ls .claude/commands/generate-triads.md
```

If missing:
```bash
./setup-complete.sh --components=command
```

**Solution 2**: Restart Claude Code
```bash
# Exit Claude Code (Ctrl+D or /exit)
# Relaunch
claude code
```

**Solution 3**: Check settings.json
```bash
cat .claude/settings.json
```

Should include commands configuration. If not:
```bash
./setup-complete.sh --force
```

---

### Issue: Domain Researcher doesn't ask questions

**Symptom**: Generator activates but immediately completes without interviewing

**Solution**:

Check `.claude/generator/agents/domain-researcher.md`:

```bash
cat .claude/generator/agents/domain-researcher.md | grep "questions"
```

Should include interview protocol. If missing or corrupted:

```bash
# Re-run setup
./setup-complete.sh --force

# Or download fresh copy
curl -sSL https://raw.githubusercontent.com/reliable-agents-ai/triads/main/.claude/generator/agents/domain-researcher.md > .claude/generator/agents/domain-researcher.md
```

---

### Issue: WebSearch fails during research

**Error**:
```
WebSearch failed: Network error
```

**Solution**:

**Check internet connection**:
```bash
ping google.com
```

**Try manual search**:
If WebSearch unavailable, provide research manually:
```
> /generate-triads

You: "I build software. Workflow: requirements → design → code.
Based on my research, standard SDLC includes these phases..."
```

**Proceed without web research**:
Generator can work with your provided information if WebSearch is unavailable.

---

### Issue: Generated files incomplete

**Symptom**: Some agent files or hooks missing

**Solution**:

**Check generation log**:
Look for errors during generation in Claude Code output

**Re-run Triad Architect manually**:
```bash
# Ensure generator graph exists
ls .claude/graphs/generator_graph.json

# Re-run generation
> Please activate Triad Architect and regenerate the system files
```

**Verify all required files**:
```bash
# Should have:
ls .claude/agents/*/
ls .claude/hooks/
ls .claude/constitutional-principles.md
```

**If still incomplete**:
```bash
./setup-complete.sh --force
# Then re-run /generate-triads
```

---

## Triad Execution Issues

### Issue: "Start {Triad}" command doesn't work

**Error**:
```
Unknown triad: Discovery
```

**Solution**:

**Check triad was generated**:
```bash
ls .claude/agents/
# Should show triad folders
```

**Check agent files exist**:
```bash
ls .claude/agents/discovery/
# Should show 3 agent markdown files
```

**Correct syntax**:
```bash
# Correct
> Start Discovery: analyze authentication system

# Incorrect
> Start discovery: ...  (lowercase)
> /start Discovery: ...  (slash command)
> discovery: ...  (no "Start")
```

**If triad missing**:
```bash
# Re-run generator
> /generate-triads --extend
```

---

### Issue: Agents not collaborating

**Symptom**: Only one agent responds, others silent

**Solution**:

**Check all agent files valid**:
```bash
# Each should be valid markdown with YAML frontmatter
for file in .claude/agents/discovery/*.md; do
    echo "Checking $file"
    head -n 10 "$file"
done
```

**Check agent names in frontmatter**:
```yaml
---
name: codebase-analyst  # Must match filename
triad: discovery        # Must match folder
---
```

**Restart Claude Code**:
Sometimes agent definitions need reload:
```bash
# Exit and relaunch
claude code
```

---

### Issue: Agent outputs but nothing happens

**Symptom**: Agent produces text but no graph updates, no progress

**Solution**:

**Check agent is outputting [GRAPH_UPDATE] blocks**:
Agent output should include:
```
[GRAPH_UPDATE]
type: add_node
node_id: ...
...
[/GRAPH_UPDATE]
```

**Check hooks are executable**:
```bash
ls -la .claude/hooks/
# Should show -rwxr-xr-x permissions

# If not:
chmod +x .claude/hooks/*.py
```

**Test hook manually**:
```bash
export CLAUDE_AGENT_NAME=test-agent
python3 .claude/hooks/on_subagent_end.py
# Should run without errors
```

---

## Knowledge Graph Issues

### Issue: Graph file not created

**Symptom**: `.claude/graphs/{triad}_graph.json` doesn't exist after running triad

**Solution**:

**Check hooks directory**:
```bash
ls .claude/hooks/
# Should contain: on_subagent_start.py, on_subagent_end.py
```

**Check hooks are executable**:
```bash
chmod +x .claude/hooks/*.py
```

**Check Python can import NetworkX**:
```bash
python3 -c "import networkx; print('OK')"
```

**Run hook manually to see errors**:
```bash
export CLAUDE_AGENT_NAME=test-agent
python3 .claude/hooks/on_subagent_start.py
```

**Check write permissions**:
```bash
ls -ld .claude/graphs/
# Should be writable: drwxr-xr-x

touch .claude/graphs/test.json
# Should succeed
rm .claude/graphs/test.json
```

---

### Issue: Graph not updating

**Symptom**: Graph file exists but doesn't change when triads run

**Solution**:

**Check agent output format**:
Agents must output exactly:
```
[GRAPH_UPDATE]
type: add_node
node_id: unique_id
node_type: Entity
label: "Node label"
description: "Description"
confidence: 0.95
evidence: "Source"
created_by: agent-name
[/GRAPH_UPDATE]
```

**Check hook is running**:
Add debug output to `.claude/hooks/on_subagent_end.py`:
```python
print("DEBUG: Hook running")
print(f"DEBUG: Agent: {os.environ.get('CLAUDE_AGENT_NAME')}")
```

**Check for temp files**:
```bash
ls .claude/graphs/.output_*
# Hook writes to temp files first
```

**Manually run hook with sample input**:
```bash
export CLAUDE_AGENT_NAME=test-agent
echo '[GRAPH_UPDATE]
type: add_node
node_id: test1
node_type: Entity
label: "Test"
confidence: 0.9
evidence: "Test"
created_by: test-agent
[/GRAPH_UPDATE]' | python3 .claude/hooks/on_subagent_end.py
```

---

### Issue: Graph corrupted

**Error**:
```
JSONDecodeError: Expecting property name enclosed in double quotes
```

**Solution**:

**Backup corrupted graph**:
```bash
cp .claude/graphs/discovery_graph.json .claude/graphs/discovery_graph.json.corrupted
```

**Try to fix JSON**:
```bash
# Use Python to validate and reformat
python3 -m json.tool .claude/graphs/discovery_graph.json > .claude/graphs/discovery_graph_fixed.json

# If successful:
mv .claude/graphs/discovery_graph_fixed.json .claude/graphs/discovery_graph.json
```

**If unfixable, start fresh**:
```bash
# Remove corrupted graph
rm .claude/graphs/discovery_graph.json

# Initialize empty graph
echo '{"nodes": [], "links": []}' > .claude/graphs/discovery_graph.json

# Re-run triad
> Start Discovery: [your task]
```

---

## Bridge Agent Issues

### Issue: Bridge agent not preserving context

**Symptom**: Target triad doesn't have information from source triad

**Solution**:

**Check bridge graph exists**:
```bash
ls .claude/graphs/bridge_*.json
# Should see bridge files like: bridge_discovery_to_design.json
```

**Check bridge graph has content**:
```bash
cat .claude/graphs/bridge_discovery_to_design.json | python3 -m json.tool
# Should have ~20-40 nodes
```

**Check bridge transition hook**:
```bash
chmod +x .claude/hooks/on_bridge_transition.py
python3 .claude/hooks/on_bridge_transition.py
```

**Check agent is correctly identified as bridge**:
In `.claude/agents/bridges/{agent}.md`:
```yaml
---
name: knowledge-synthesizer
triad: discovery,design  # Should list BOTH triads
role: bridge             # Must say "bridge"
---
```

**Manual bridge transition**:
```bash
# If automatic transition failed, manually compress:
python3 << 'EOF'
import json
import networkx as nx

# Load source graph
with open('.claude/graphs/discovery_graph.json') as f:
    data = json.load(f)

# Simple compression: take first 20 nodes
compressed = {
    "nodes": data["nodes"][:20],
    "links": [l for l in data["links"] if l["source"] in [n["id"] for n in data["nodes"][:20]]]
}

# Save bridge graph
with open('.claude/graphs/bridge_discovery_to_design.json', 'w') as f:
    json.dump(compressed, f, indent=2)

print("Manual bridge created")
EOF
```

---

### Issue: Too much context in bridge (context window exceeded)

**Symptom**: Bridge agent fails with context too large error

**Solution**:

**Reduce compression size**:
Edit `.claude/hooks/on_bridge_transition.py`:
```python
# Change from 20 to 15
max_nodes = 15
```

**Increase selectivity**:
Adjust importance scoring to be more selective:
```python
# Increase type priority differences
TYPE_PRIORITY = {
    "Decision": 1.0,
    "Uncertainty": 0.9,
    "Finding": 0.7,    # Lower than default
    "Concept": 0.4,     # Lower
    "Task": 0.3,        # Lower
    "Entity": 0.1       # Much lower
}
```

**Manual selective compression**:
Choose critical nodes manually:
```python
# Edit bridge graph, keep only critical nodes
python3 -c "
import json
with open('.claude/graphs/bridge_discovery_to_design.json') as f:
    data = json.load(f)

# Filter to only Decision and Uncertainty nodes
critical = [n for n in data['nodes'] if n['type'] in ['Decision', 'Uncertainty']]

with open('.claude/graphs/bridge_discovery_to_design.json', 'w') as f:
    json.dump({'nodes': critical, 'links': []}, f, indent=2)
"
```

---

## Hook Issues

### Issue: Hooks not executing

**Symptom**: No graph updates, no errors, hooks seem to be ignored

**Solution**:

**Check hooks are executable**:
```bash
ls -la .claude/hooks/
# Should show: -rwxr-xr-x

chmod +x .claude/hooks/*.py
```

**Check shebang line**:
Edit each hook, first line should be:
```python
#!/usr/bin/env python3
```

**Check Python path**:
```bash
which python3
# Update shebang if needed:
# #!/usr/bin/python3
```

**Test hook directly**:
```bash
./.claude/hooks/on_subagent_start.py
# Should run without "Permission denied"
```

**Check Claude Code hook configuration**:
```bash
cat .claude/settings.json | grep -A 5 hooks
```

Should include:
```json
"hooks": {
  "on_subagent_start": ".claude/hooks/on_subagent_start.py",
  "on_subagent_end": ".claude/hooks/on_subagent_end.py"
}
```

---

### Issue: Hook errors

**Error in hook output**:
```
ImportError: No module named 'networkx'
```

**Solution**:

**Install NetworkX**:
```bash
pip3 install networkx
```

**Check import in Python**:
```bash
python3 -c "import networkx; print('OK')"
```

**If using virtual environment**:
```bash
# Activate venv first
source venv/bin/activate
pip install networkx

# Update hook shebang to use venv Python
#!/path/to/venv/bin/python3
```

**Other import errors**:
```bash
# Install any missing dependencies
pip3 install networkx datetime json os sys
```

---

## TRUST Violations

### Issue: Constant violations logged

**Symptom**: `.claude/constitutional/violations.json` fills with TRUST violations

**Solution**:

**Review violations**:
```bash
cat .claude/constitutional/violations.json | python3 -m json.tool | less
```

**Common TRUST violation patterns**:

**1. R: Missing evidence**:
```json
{
  "principle": "TRUST-R: Require evidence",
  "description": "High confidence without evidence"
}
```

**Fix**: Update agent prompt to always include evidence:
```markdown
## Output Format
When adding nodes to knowledge graph:
- Always include `evidence` field (TRUST-R)
- Cite specific sources, line numbers, documents
```

**2. U: Unescalated uncertainties**:
```json
{
  "principle": "TRUST-U: Uncertainty escalation",
  "description": "Uncertainty not flagged"
}
```

**Fix**: Update agent to explicitly escalate:
```markdown
When you encounter uncertainties (TRUST-U):
- Create Uncertainty node
- Set `escalated: true`
- Flag for review
```

**3. S: Undocumented decisions**:
```json
{
  "principle": "TRUST-S: Show all work",
  "description": "Decision without rationale"
}
```

**Fix**: Require rationale in Decision nodes:
```markdown
For all decisions (TRUST-S):
- Include `rationale` field
- Explain why this choice was made
- Document alternatives considered
```

**Adjust enforcement severity**:
Edit `.claude/constitutional/checkpoints.json`:
```json
{
  "agents": {
    "codebase-analyst": {
      "min_confidence": 0.7,  // Lower from 0.9 if too strict
      "required_fields": ["evidence"]  // Reduce requirements
    }
  }
}
```

---

### Issue: Violations blocking work

**Symptom**: Agent can't complete due to critical violations

**Solution**:

**Review and fix violation**:
```bash
# See what's blocking
tail -n 20 .claude/constitutional/violations.json
```

**Common fixes**:

**Missing required field**:
- Agent needs to include all required fields
- Check agent's TRUST principles
- Add field to agent's output

**Confidence too low**:
- Agent expressing uncertainty appropriately
- Either: increase confidence with better evidence
- Or: Create Uncertainty node instead

**Temporary workaround** (not recommended):
```bash
# Reduce enforcement strictness temporarily
# Edit .claude/hooks/on_subagent_end.py
# Comment out blocking logic:
# if any(v['severity'] == 'high' for v in violations):
#     block_completion()  # Commented out
```

**Permanent fix**: Update agent behavior to comply with principles

---

## Performance Issues

### Issue: Slow graph operations

**Symptom**: Hooks take long time to run

**Solution**:

**Check graph size**:
```bash
wc -l .claude/graphs/*.json
# Should be < 10,000 lines per file
```

**If graphs too large**:
```bash
# Compress manually
python3 << 'EOF'
import json

for triad in ['discovery', 'design', 'implementation']:
    try:
        with open(f'.claude/graphs/{triad}_graph.json') as f:
            data = json.load(f)

        # Keep only recent nodes (last 100)
        recent = data['nodes'][-100:]
        recent_ids = {n['id'] for n in recent}
        links = [l for l in data['links'] if l['source'] in recent_ids]

        with open(f'.claude/graphs/{triad}_graph.json', 'w') as f:
            json.dump({'nodes': recent, 'links': links}, f)

        print(f"Compressed {triad}")
    except:
        pass
EOF
```

**Optimize NetworkX operations**:
Edit hooks to use more efficient algorithms

**Archive old graphs**:
```bash
mkdir .claude/graphs/archive
mv .claude/graphs/*_graph.json .claude/graphs/archive/
# Start fresh
```

---

### Issue: Triads running slow

**Symptom**: Each triad takes very long to complete

**Solution**:

**Check task scope**:
- Are you giving triads too large tasks?
- Break into smaller subtasks

**Check agent prompts**:
- Are agents doing unnecessary work?
- Trim agent responsibilities

**Check context size**:
```bash
# Check bridge graphs aren't too large
du -h .claude/graphs/bridge_*.json
# Should be < 100 KB each
```

**Reduce bridge compression size**:
```python
# In on_bridge_transition.py
max_nodes = 10  # Reduce from 20
```

---

## Getting More Help

If issues persist:

1. **Check logs**:
   ```bash
   # Claude Code may have logs
   cat ~/.claude/logs/latest.log
   ```

2. **Enable debug mode**:
   ```bash
   # Add to hooks for more output
   DEBUG = True
   ```

3. **Search GitHub Issues**:
   - https://github.com/reliable-agents-ai/triads/issues

4. **Create new issue**:
   - Include error messages
   - Include system info (OS, Python version)
   - Include steps to reproduce

5. **Community discussions**:
   - https://github.com/reliable-agents-ai/triads/discussions

---

**Most issues have simple solutions. Check the basics first: permissions, paths, Python version, NetworkX installation.**
