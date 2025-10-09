# Building Autonomous AI Systems with Claude Code Hooks

**How we built a self-managing knowledge graph system using Claude Code's hook system**

*A case study in AI automation*

---

## The Challenge

We needed AI agents that could:
- **Remember** what they learned across sessions
- **Build** on previous work without repetition
- **Maintain** structured knowledge automatically

**The problem**: AI conversations are ephemeral. Once a session ends, context is lost.

**Traditional solution**: Manual note-taking, copying context between sessions, maintaining external databases.

**Our solution**: Use Claude Code hooks to build **autonomous memory**.

---

## What Are Claude Code Hooks?

Hooks are event listeners that execute code at specific points in Claude's lifecycle:

```
Session Starts → Hook fires → Load previous knowledge
    ↓
Agent works → Outputs findings
    ↓
Response completes → Hook fires → Save to knowledge graph
    ↓
Next session → Previous knowledge automatically loaded
```

**Zero manual work. Fully autonomous.**

---

## The Architecture

### Two Hooks, Infinite Memory

**Hook 1: SessionStart** (Inject Context)
```python
# Runs when session starts
# Loads all knowledge graphs
# Injects as context for Claude

print("Previous findings: Authentication module analyzed...")
print("Open questions: Token refresh implementation...")
print("Recent decisions: Chose JWT over sessions...")
```

**Hook 2: Stop** (Capture Knowledge)
```python
# Runs after Claude responds
# Scans for structured markers
# Updates knowledge graphs

# Agent outputs:
[GRAPH_UPDATE]
type: add_node
node_id: auth_module_001
label: Authentication Module
confidence: 0.95
evidence: src/auth/jwt.py:15-89
[/GRAPH_UPDATE]

# Hook captures and saves to JSON
```

### The Result

**Session 1**:
```
User: "Analyze the authentication system"
Agent: [analyzes code]
       [outputs GRAPH_UPDATE blocks]
Stop Hook: [saves to graph]
```

**Session 2** (days later):
```
SessionStart Hook: [loads previous graph]
Claude: "I see you've already analyzed the auth module.
         Previously identified: JWT implementation at src/auth/jwt.py
         Should I focus on the missing token refresh logic?"
```

**Claude remembers everything.** Automatically.

---

## Implementation: 5 Simple Steps

### Step 1: Define Your Structure

```python
# What should agents capture?
[GRAPH_UPDATE]
type: add_node
node_type: Finding | Decision | Question | Entity
label: Short description
description: Detailed info
confidence: 0.0 to 1.0
evidence: Source reference
[/GRAPH_UPDATE]
```

### Step 2: Create SessionStart Hook

```python
#!/usr/bin/env python3
# .claude/hooks/session_start.py

import json
from pathlib import Path

def main():
    # Load all knowledge graphs
    graphs_dir = Path('.claude/graphs')

    for graph_file in graphs_dir.glob('*.json'):
        with open(graph_file) as f:
            data = json.load(f)

        # Format for Claude
        print(f"Previous work on {graph_file.stem}:")
        for node in data['nodes']:
            print(f"  • {node['label']} ({node['confidence']})")

if __name__ == "__main__":
    main()
```

### Step 3: Create Stop Hook

```python
#!/usr/bin/env python3
# .claude/hooks/on_stop.py

import json
import re
from pathlib import Path

def extract_updates(text):
    """Find [GRAPH_UPDATE] blocks."""
    pattern = r'\[GRAPH_UPDATE\](.*?)\[/GRAPH_UPDATE\]'
    matches = re.findall(pattern, text, re.DOTALL)

    updates = []
    for match in matches:
        update = {}
        for line in match.strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                update[key.strip()] = value.strip()
        updates.append(update)

    return updates

def main():
    # Read transcript
    input_data = json.load(sys.stdin)
    transcript_path = input_data['transcript_path']

    # Parse conversation
    text = parse_transcript(transcript_path)

    # Extract updates
    updates = extract_updates(text)

    # Save to graph
    for update in updates:
        save_to_graph(update)

if __name__ == "__main__":
    main()
```

### Step 4: Configure Hooks

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 .claude/hooks/session_start.py"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 .claude/hooks/on_stop.py"
          }
        ]
      }
    ]
  }
}
```

### Step 5: Enjoy Autonomous Memory

```bash
# Session 1
User: "Analyze auth system"
[Knowledge graph created]

# Exit and restart

# Session 2
[Knowledge graph auto-loaded]
Claude: "Building on previous analysis..."
```

**That's it.** Hooks do the rest.

---

## Real-World Results

### Before Hooks
- ❌ "What did we discuss about auth last week?"
- ❌ Re-analyzing same code repeatedly
- ❌ Lost decisions and rationale
- ❌ No structured knowledge
- ❌ Manual note-taking required

### After Hooks
- ✅ "I see you previously analyzed auth (src/auth/jwt.py)"
- ✅ Builds incrementally on previous work
- ✅ All decisions preserved with rationale
- ✅ Queryable knowledge graph
- ✅ Fully autonomous

### Metrics

**Knowledge Capture**:
- 5 nodes captured in first session
- 12 nodes after 3 sessions
- 100% capture rate (no manual work)

**Context Preservation**:
- 100% of previous work loaded automatically
- Zero context loss between sessions
- Infinite memory (limited only by storage)

**Time Saved**:
- No re-analysis of previous work
- No manual note-taking
- No copying context between sessions
- Estimated: **30-50% time savings** on multi-session projects

---

## Key Learnings

### What Works
✅ **SessionStart hook** - Inject context at session start
✅ **Stop hook** - Process outputs after responses
✅ **Structured markers** - [GRAPH_UPDATE] blocks are reliable
✅ **JSON storage** - Simple, queryable, version-controllable

### What Doesn't (Yet)
❌ **PostToolUse hook** - Broken in current Claude Code (Oct 2025)
❌ **PreToolUse hook** - Also broken
⚠️ **SubagentStop hook** - Inconsistent

**Workaround**: Use Stop hook instead. Fires after complete response, captures everything.

### Critical Discovery

**Transcript parsing structure**:
```python
# WRONG (what we tried first)
content = entry['content']  # Doesn't exist!

# CORRECT (actual structure)
content = entry['message']['content']  # This works!
```

This one line was the difference between "hook fires but does nothing" and "fully functional system."

---

## Advanced Use Cases

### Multi-Domain Knowledge Graphs

```python
# Different graphs for different domains
.claude/graphs/
  ├── codebase_graph.json      # Code structure
  ├── architecture_graph.json  # System design
  ├── decisions_graph.json     # Tech decisions
  └── bugs_graph.json          # Known issues
```

### Bridge Agents (Context Transfer)

```python
# Agent working in one domain references another
[GRAPH_UPDATE]
type: add_edge
source: auth_module
target: user_service
edge_type: depends_on
rationale: Auth module requires user lookup
[/GRAPH_UPDATE]
```

### Confidence Tracking

```python
# Track certainty of findings
Low confidence (0.3): "Appears to use JWT"
High confidence (0.95): "Confirmed JWT at src/auth/jwt.py:15-89"

# Over time, confidence increases with more evidence
```

### Decision Provenance

```python
[GRAPH_UPDATE]
type: add_node
node_type: Decision
label: Use rotating refresh tokens
alternatives: ["Session-based", "Hybrid approach"]
rationale: Maintains stateless architecture
evidence: Discussion in session 2025-10-08
[/GRAPH_UPDATE]
```

---

## Beyond Knowledge Graphs

### Other Applications

**Quality Assurance**:
```python
# Stop hook runs tests after code changes
def on_stop():
    if code_changed():
        run_tests()
        run_linter()
        report_issues()
```

**Git Automation**:
```python
# Stop hook creates commits
def on_stop():
    if work_completed():
        git_add_changes()
        git_commit_with_ai_message()
```

**External Integration**:
```python
# Update project management tools
def on_stop():
    findings = extract_findings()
    update_jira(findings)
    notify_slack(findings)
```

**Cost Tracking**:
```python
# Monitor token usage
def on_stop():
    log_tokens_used()
    update_budget()
    alert_if_threshold_exceeded()
```

---

## Technical Deep Dive

### How Hooks Actually Work

1. **Event occurs** (session start, response complete, etc.)
2. **Claude Code checks** settings.json for registered hooks
3. **Executes command** with event data piped to stdin
4. **Reads stdout** and injects as context (for SessionStart)
5. **Logs stderr** for debugging

### Input Format

```json
{
  "session_id": "abc123",
  "cwd": "/path/to/project",
  "transcript_path": "/path/to/transcript.jsonl"
}
```

### Transcript Format (JSONL)

```json
{"message": {"role": "user", "content": "Analyze auth"}}
{"message": {"role": "assistant", "content": [{"type": "text", "text": "..."}]}}
```

**Critical**: Content is in `message.content`, not at top level.

### Error Handling

```python
def main():
    try:
        # Hook logic
        do_work()
    except Exception as e:
        # Log but don't crash Claude
        print(f"Hook error: {e}", file=sys.stderr)
        sys.exit(0)  # Success exit code
```

**Philosophy**: Hooks enhance, they don't break. Always exit successfully.

---

## Performance Considerations

### Hook Execution Speed

Hooks block Claude Code, so optimize for speed:

**Fast** (< 100ms):
- ✅ Load small JSON files
- ✅ Parse text with regex
- ✅ Write to local files

**Slow** (> 1s):
- ⚠️ API calls
- ⚠️ Database queries
- ⚠️ Heavy computation

**Solution**: Queue heavy work for background processing:

```python
def main():
    # Fast: Write to queue
    with open('work_queue.jsonl', 'a') as f:
        f.write(json.dumps(task) + '\n')

    # Separate process handles queue
```

### Storage Scaling

**Small projects** (< 100 nodes): Single JSON file
**Medium projects** (100-1000 nodes): Multiple domain-specific graphs
**Large projects** (> 1000 nodes): Database backend with JSON cache

Our implementation handles 100+ nodes with zero noticeable delay.

---

## Getting Started

### Minimal Implementation (30 minutes)

**1. Create SessionStart hook** (10 min)
```bash
mkdir -p .claude/hooks
cat > .claude/hooks/session_start.py << 'EOF'
#!/usr/bin/env python3
print("🚀 Session started")
print("📁 Working directory:", ".")
EOF
chmod +x .claude/hooks/session_start.py
```

**2. Create Stop hook** (10 min)
```bash
cat > .claude/hooks/on_stop.py << 'EOF'
#!/usr/bin/env python3
import sys
print("✅ Session ending", file=sys.stderr)
EOF
chmod +x .claude/hooks/on_stop.py
```

**3. Configure** (5 min)
```json
{
  "hooks": {
    "SessionStart": [{"hooks": [{"type": "command", "command": "python3 .claude/hooks/session_start.py"}]}],
    "Stop": [{"hooks": [{"type": "command", "command": "python3 .claude/hooks/on_stop.py"}]}]
  }
}
```

**4. Test** (5 min)
```bash
# Exit Claude Code
# Start fresh session
# See "🚀 Session started" message
```

**Expand from there.**

---

## Conclusion

### What We Built

An **autonomous AI memory system** using Claude Code hooks:
- Captures knowledge automatically
- Preserves context indefinitely
- Builds structured, queryable graphs
- Requires zero manual work

### What You Can Build

Hooks enable **any workflow automation**:
- Quality assurance
- External integrations
- Git automation
- Cost tracking
- Session logging
- Context injection

### The Opportunity

Claude Code hooks transform AI from a **conversation tool** into an **autonomous agent platform**.

**Before**: AI assists with tasks
**After**: AI maintains its own knowledge, builds on previous work, operates autonomously

This is **AI that remembers.**

---

## Resources

**Full Implementation Guide**: `CLAUDE_CODE_HOOKS_GUIDE.md` (12,000+ words)
**Our Implementation**: `.claude/hooks/` (session_start.py, on_stop.py)
**Test System**: `.claude/agents/test/hello-agent.md`
**Documentation**: All findings documented in research files

**GitHub Issues** (Known bugs):
- [#6305](https://github.com/anthropics/claude-code/issues/6305) - PostToolUse broken
- [#6403](https://github.com/anthropics/claude-code/issues/6403) - Trigger mechanism issues

**Official Docs**: [docs.claude.com/claude-code/hooks](https://docs.claude.com/en/docs/claude-code/hooks)

---

## Try It Yourself

```bash
# Clone our implementation
git clone [repo-url]

# Install hooks
./install.sh

# Start session
claude code

# Watch autonomous memory in action
```

**The future of AI is autonomous. Build it with hooks.**

---

*Case study based on implementing a production knowledge graph system for multi-agent orchestration. October 2025.*

**Questions? Want to discuss implementation? Let's talk.**
