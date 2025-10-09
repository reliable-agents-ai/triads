# The Complete Guide to Claude Code Hooks

**Master the art of automating Claude Code workflows with hooks**

*Based on real-world implementation of an autonomous knowledge graph system*

---

## Table of Contents

1. [What Are Claude Code Hooks?](#what-are-claude-code-hooks)
2. [Why Use Hooks?](#why-use-hooks)
3. [Available Hook Types](#available-hook-types)
4. [Configuration Guide](#configuration-guide)
5. [Development Workflow](#development-workflow)
6. [Real-World Example: Knowledge Graph System](#real-world-example-knowledge-graph-system)
7. [Debugging Techniques](#debugging-techniques)
8. [Best Practices](#best-practices)
9. [Common Pitfalls](#common-pitfalls)
10. [Troubleshooting](#troubleshooting)

---

## What Are Claude Code Hooks?

**Claude Code hooks** are shell commands that execute automatically at specific points in Claude Code's lifecycle. Think of them as event listeners that let you:

- **React** to events (session start, tool use, response completion)
- **Inject** custom context into Claude's environment
- **Automate** workflows (git commits, testing, logging, validation)
- **Extend** Claude Code's capabilities without modifying the core system

### How Hooks Work

```
┌─────────────────────────────────────────┐
│  Claude Code Event Occurs               │
│  (e.g., session starts, tool completes) │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  Hook Fires                              │
│  (based on configuration)                │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  Your Script Executes                    │
│  (receives data via stdin)               │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  Script Output                           │
│  (stdout → injected as context)          │
│  (stderr → logged for debugging)         │
└─────────────────────────────────────────┘
```

---

## Why Use Hooks?

### Automation Without Friction

Hooks eliminate manual steps in your workflow:

- **Before hooks**: No more "remember to check X before starting"
- **After hooks**: No more "remember to update Y when done"
- **Context hooks**: No more "let me search for that information"

### Real-World Use Cases

**Session Management**:
- Load project-specific context at session start
- Inject API keys, environment variables, or documentation
- Display project status, recent changes, or open issues

**Quality Assurance**:
- Run linters/formatters after file changes
- Execute tests after code modifications
- Validate commit messages or PR descriptions

**Knowledge Management**:
- Capture decisions made during sessions
- Build knowledge graphs of project understanding
- Generate session summaries or changelogs

**Integration**:
- Update external systems (Jira, Linear, Notion)
- Send notifications (Slack, Discord, email)
- Sync with version control (git auto-commit)

**Observability**:
- Log all tool uses for audit trails
- Monitor token usage and costs
- Track agent performance metrics

---

## Available Hook Types

### 1. SessionStart ✅ **WORKING**

**Fires**: Once when a Claude Code session begins

**Use for**:
- Loading project context
- Injecting documentation
- Displaying system status
- Setting environment variables

**Input** (via stdin):
```json
{
  "session_id": "abc123",
  "cwd": "/path/to/project"
}
```

**Output**: Text sent to stdout is injected as context for Claude

**Example**:
```python
#!/usr/bin/env python3
import json
import sys

# Read session info
data = json.load(sys.stdin)
cwd = data.get('cwd', '.')

# Load project context
print("=" * 80)
print("# Project Context")
print("=" * 80)
print(f"Working Directory: {cwd}")
print(f"Recent Changes: ...")
print("=" * 80)
```

---

### 2. Stop ✅ **WORKING**

**Fires**: After Claude finishes responding to user

**Use for**:
- Processing Claude's response
- Updating external systems
- Logging conversation history
- Capturing structured outputs

**Input** (via stdin):
```json
{
  "session_id": "abc123",
  "cwd": "/path/to/project",
  "transcript_path": "/path/to/session/transcript.jsonl"
}
```

**Critical Learning**: Read the **transcript file** to get full conversation:

```python
import json
from pathlib import Path

# Read hook input
input_data = json.load(sys.stdin)
transcript_path = input_data.get('transcript_path')

# Parse transcript (JSONL format)
with open(transcript_path, 'r') as f:
    for line in f:
        entry = json.loads(line)

        # CRITICAL: Message content is nested!
        if 'message' in entry and 'content' in entry['message']:
            content = entry['message']['content']

            # Content can be string or array
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and 'text' in item:
                        text = item['text']
                        # Process text...
            elif isinstance(content, str):
                # Process string...
```

**Common Pattern**: Extract structured data from responses
```python
import re

# Find custom markers in response
pattern = r'\[MY_MARKER\](.*?)\[/MY_MARKER\]'
matches = re.findall(pattern, response_text, re.DOTALL)
```

---

### 3. UserPromptSubmit ✅ **WORKING**

**Fires**: Before Claude processes user's prompt

**Use for**:
- Prompt validation
- Adding context based on prompt content
- Tracking user requests
- Custom prompt transformations

**Input** (via stdin):
```json
{
  "session_id": "abc123",
  "cwd": "/path/to/project",
  "prompt": "User's prompt text"
}
```

**Output**: Can modify or enhance the prompt

---

### 4. PostToolUse ❌ **BROKEN** (as of Oct 2025)

**Status**: Does not fire reliably. Multiple GitHub issues confirm this is a known bug.

**Intended use**:
- React to tool completions
- Validate tool outputs
- Log tool usage

**Workaround**: Use **Stop hook** instead. It fires after Claude's complete response (which includes all tool uses).

**GitHub Issues**:
- [#6305](https://github.com/anthropics/claude-code/issues/6305) - PostToolUse not executing
- [#6403](https://github.com/anthropics/claude-code/issues/6403) - "Trigger mechanism completely broken"
- [#3148](https://github.com/anthropics/claude-code/issues/3148) - Matcher issues

---

### 5. PreToolUse ❌ **BROKEN** (as of Oct 2025)

**Status**: Does not fire reliably. Same issues as PostToolUse.

**Workaround**: Use **UserPromptSubmit** to add context before Claude starts working.

---

### 6. SubagentStop ⚠️ **INCONSISTENT**

**Status**: May fire when subagents complete, but reliability varies.

**Recommendation**: Use **Stop hook** for more reliable subagent output processing.

---

### 7. Notification, SessionEnd, PreCompact

**Status**: Available but less commonly used. Refer to [official docs](https://docs.claude.com/en/docs/claude-code/hooks) for details.

---

## Configuration Guide

### Settings File Location

Hooks are configured in `.claude/settings.json` (project-level) or `~/.claude/settings.json` (global).

**Recommendation**: Use project-level settings for project-specific hooks.

### Basic Structure

```json
{
  "hooks": {
    "HookType": [
      {
        "matcher": "optional_pattern",
        "hooks": [
          {
            "type": "command",
            "command": "path/to/script.sh"
          }
        ]
      }
    ]
  }
}
```

**Critical**: The top-level `"hooks"` key is **required**. This is the #1 configuration mistake.

### Example: Complete Configuration

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
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 .claude/hooks/on_prompt.py"
          }
        ]
      }
    ]
  }
}
```

### Multiple Hooks

You can run multiple hooks for the same event:

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 .claude/hooks/log_conversation.py"
          },
          {
            "type": "command",
            "command": "python3 .claude/hooks/update_graphs.py"
          },
          {
            "type": "command",
            "command": "bash .claude/hooks/notify_slack.sh"
          }
        ]
      }
    ]
  }
}
```

**Note**: Hooks run in parallel by default.

### Matchers (for PostToolUse)

**Note**: PostToolUse is currently broken, but when/if fixed:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",  // Regex pattern
        "hooks": [
          {
            "type": "command",
            "command": "python3 .claude/hooks/format_code.py"
          }
        ]
      },
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 .claude/hooks/log_command.py"
          }
        ]
      }
    ]
  }
}
```

---

## Development Workflow

### Step 1: Plan Your Hook

**Ask yourself**:
1. What event do I want to react to?
2. What data do I need from Claude Code?
3. What should my hook do with that data?
4. What output should it produce?

**Example**: Knowledge Graph Hook
1. Event: After Claude responds (Stop hook)
2. Data: Conversation transcript
3. Action: Extract structured data, update graph
4. Output: Status message to stderr

---

### Step 2: Create Hook Script

**Basic Template**:

```python
#!/usr/bin/env python3
"""
Hook: [Hook Name]
Description: [What it does]
Hook Type: [SessionStart|Stop|UserPromptSubmit]
"""

import json
import sys
from pathlib import Path

def main():
    """Main hook execution."""

    # Read input from stdin
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        # Input might be plain text
        input_text = sys.stdin.read()
        input_data = {"text": input_text}

    # Extract what you need
    session_id = input_data.get('session_id')
    cwd = input_data.get('cwd')

    # Do your work
    result = do_something(input_data)

    # Output to stdout (injected as context)
    print(f"Hook result: {result}")

    # Log to stderr (for debugging)
    print(f"Hook executed successfully", file=sys.stderr)

def do_something(data):
    """Your hook logic here."""
    return "success"

if __name__ == "__main__":
    main()
```

**Make it executable**:
```bash
chmod +x .claude/hooks/my_hook.py
```

---

### Step 3: Configure in settings.json

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 .claude/hooks/my_hook.py"
          }
        ]
      }
    ]
  }
}
```

**Validate JSON**:
```bash
python3 -m json.tool < .claude/settings.json
```

---

### Step 4: Test Manually

Before testing in Claude Code, test your hook manually:

```bash
# Create test input
echo '{"session_id": "test", "cwd": "."}' > /tmp/test_input.json

# Run hook
cat /tmp/test_input.json | python3 .claude/hooks/my_hook.py

# Check output
echo $?  # Should be 0 (success)
```

**Tip**: Test with realistic data that matches what Claude Code will send.

---

### Step 5: Test in Claude Code

1. **Exit** any existing Claude Code session
2. **Start fresh** session (settings.json only loads at start)
3. **Trigger** the hook event
4. **Check** stderr for hook output
5. **Verify** hook did what you expected

**Debug logging**:
```python
import sys
from datetime import datetime

# Log to file for debugging
with open('.claude/hooks/debug.log', 'a') as f:
    f.write(f"{datetime.now()}: Hook fired\n")
    f.write(f"Input: {input_data}\n")
```

---

### Step 6: Iterate

Based on testing:
- Add error handling
- Improve performance
- Add more logging
- Handle edge cases

---

## Real-World Example: Knowledge Graph System

### The Challenge

Build a system where AI agents automatically:
1. Document their findings in structured format
2. Update a persistent knowledge graph
3. Context from previous sessions is automatically loaded

### The Solution

**Two hooks working together**:

1. **SessionStart**: Load existing knowledge graphs as context
2. **Stop**: Parse agent outputs and update graphs

### Architecture

```
Session Starts
     ↓
SessionStart Hook Fires
     ↓
Load all .claude/graphs/*.json files
     ↓
Format as human-readable summaries
     ↓
Output to stdout → Injected as context
     ↓
Claude has full knowledge of previous work ✅

─────────────────────────────────────────

Agent works, outputs:

[GRAPH_UPDATE]
type: add_node
node_id: auth_module_001
node_type: Entity
label: Authentication Module
description: JWT-based auth in src/auth/
confidence: 0.95
evidence: src/auth/jwt.py:15-89
[/GRAPH_UPDATE]

     ↓
Claude finishes response
     ↓
Stop Hook Fires
     ↓
Parse transcript for [GRAPH_UPDATE] blocks
     ↓
Extract structured data
     ↓
Load relevant knowledge graph JSON
     ↓
Add/update nodes and edges
     ↓
Save updated graph
     ↓
Knowledge persisted for next session ✅
```

### Implementation: SessionStart Hook

**File**: `.claude/hooks/session_start.py`

```python
#!/usr/bin/env python3
"""
SessionStart Hook: Inject Knowledge Graph Context

Loads all knowledge graphs and injects them as context.
"""

import json
from pathlib import Path
from datetime import datetime

def load_graph(graph_path):
    """Load a knowledge graph JSON file."""
    try:
        with open(graph_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def format_graph_summary(graph_data, triad_name):
    """Format a knowledge graph as human-readable context."""
    if not graph_data:
        return f"**{triad_name}**: No data yet\n"

    nodes = graph_data.get('nodes', [])

    summary = [f"**{triad_name.upper()} Knowledge Graph**"]
    summary.append(f"Nodes: {len(nodes)}")

    # Group by type
    by_type = {}
    for node in nodes:
        node_type = node.get('type', 'Unknown')
        by_type.setdefault(node_type, []).append(node)

    # Show top nodes of each type
    for node_type, type_nodes in sorted(by_type.items()):
        summary.append(f"\n**{node_type}** ({len(type_nodes)}):")
        top_nodes = sorted(type_nodes,
                          key=lambda n: n.get('confidence', 0),
                          reverse=True)[:5]
        for node in top_nodes:
            label = node.get('label', 'Unknown')
            conf = node.get('confidence', 0)
            summary.append(f"  • {label} (confidence: {conf:.2f})")

    return "\n".join(summary)

def main():
    """Generate knowledge graph context."""
    graphs_dir = Path('.claude/graphs')

    if not graphs_dir.exists():
        print("# 📊 Knowledge Graph System Active\n")
        print("No graphs yet. Agents will create them as they work.\n")
        return

    output = []
    output.append("=" * 80)
    output.append("# 📊 KNOWLEDGE GRAPH CONTEXT")
    output.append("=" * 80)
    output.append("")

    # Load all graphs
    for graph_file in graphs_dir.glob('*_graph.json'):
        triad_name = graph_file.stem.replace('_graph', '')
        graph_data = load_graph(graph_file)
        if graph_data:
            output.append(format_graph_summary(graph_data, triad_name))
            output.append("-" * 80)

    output.append("\n**Note**: Use [GRAPH_UPDATE] blocks to add findings")
    output.append("=" * 80)

    # Output to stdout (injected as context)
    print("\n".join(output))

if __name__ == "__main__":
    main()
```

### Implementation: Stop Hook

**File**: `.claude/hooks/on_stop.py`

```python
#!/usr/bin/env python3
"""
Stop Hook: Update Knowledge Graphs

Scans conversation for [GRAPH_UPDATE] blocks and updates graphs.
"""

import json
import sys
import re
from pathlib import Path
from datetime import datetime

def extract_graph_updates(text):
    """Extract [GRAPH_UPDATE] blocks from text."""
    pattern = r'\[GRAPH_UPDATE\](.*?)\[/GRAPH_UPDATE\]'
    matches = re.findall(pattern, text, re.DOTALL)

    updates = []
    for match in matches:
        update = {}
        for line in match.strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                update[key.strip()] = value.strip()
        if update:
            updates.append(update)

    return updates

def load_graph(triad_name):
    """Load or create a knowledge graph."""
    graphs_dir = Path('.claude/graphs')
    graphs_dir.mkdir(parents=True, exist_ok=True)

    graph_file = graphs_dir / f"{triad_name}_graph.json"

    if graph_file.exists():
        with open(graph_file, 'r') as f:
            return json.load(f)

    # Create new graph
    return {
        "directed": True,
        "nodes": [],
        "links": [],
        "_meta": {
            "triad_name": triad_name,
            "created_at": datetime.now().isoformat()
        }
    }

def apply_update(graph_data, update):
    """Apply an update to the graph."""
    update_type = update.get('type')

    if update_type == 'add_node':
        node = {
            'id': update.get('node_id'),
            'type': update.get('node_type'),
            'label': update.get('label'),
            'description': update.get('description', ''),
            'confidence': float(update.get('confidence', 1.0)),
            'evidence': update.get('evidence', ''),
            'created_at': datetime.now().isoformat()
        }

        # Check if exists
        if not any(n['id'] == node['id'] for n in graph_data['nodes']):
            graph_data['nodes'].append(node)
            print(f"✓ Added node: {node['id']}", file=sys.stderr)

    return graph_data

def save_graph(graph_data, triad_name):
    """Save graph to disk."""
    graphs_dir = Path('.claude/graphs')
    graph_file = graphs_dir / f"{triad_name}_graph.json"

    graph_data['_meta']['updated_at'] = datetime.now().isoformat()

    with open(graph_file, 'w') as f:
        json.dump(graph_data, f, indent=2)

def main():
    """Main Stop hook execution."""

    # Read input
    input_data = json.load(sys.stdin)

    # Get transcript path
    transcript_path = input_data.get('transcript_path')
    if not transcript_path or not Path(transcript_path).exists():
        return

    # Parse transcript
    conversation_text = []
    with open(transcript_path, 'r') as f:
        for line in f:
            entry = json.loads(line)

            # CRITICAL: Content is nested in message.content
            if 'message' in entry and 'content' in entry['message']:
                content = entry['message']['content']

                if isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict) and 'text' in item:
                            conversation_text.append(item['text'])
                elif isinstance(content, str):
                    conversation_text.append(content)

    full_text = '\n'.join(conversation_text)

    # Extract updates
    updates = extract_graph_updates(full_text)

    if not updates:
        return  # Exit silently

    print(f"\n{'='*80}", file=sys.stderr)
    print(f"📊 Knowledge Graph Update", file=sys.stderr)
    print(f"Found {len(updates)} [GRAPH_UPDATE] blocks", file=sys.stderr)
    print(f"{'='*80}\n", file=sys.stderr)

    # Group by triad (simplified - assumes 'default' for this example)
    triad = 'default'

    # Load graph
    graph_data = load_graph(triad)

    # Apply updates
    for update in updates:
        graph_data = apply_update(graph_data, update)

    # Save
    save_graph(graph_data, triad)

    print(f"✅ Graph updated: {len(graph_data['nodes'])} nodes\n", file=sys.stderr)

if __name__ == "__main__":
    main()
```

### Configuration

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

### Results

**Session 1**:
- User asks agent to analyze codebase
- Agent outputs [GRAPH_UPDATE] blocks
- Stop hook captures and saves to graph
- `.claude/graphs/default_graph.json` created

**Session 2** (new session):
- SessionStart hook loads graph
- Claude sees: "You've previously identified: Auth Module, Payment System..."
- Agent builds on existing knowledge
- Outputs more [GRAPH_UPDATE] blocks
- Graph grows incrementally

**Impact**:
- **Zero manual work**: Graphs update automatically
- **Persistent memory**: Context preserved across sessions
- **Structured knowledge**: Queryable, analyzable data
- **Scalable**: Handles multiple triads/domains

---

## Debugging Techniques

### 1. Add Debug Logging

```python
import sys
from datetime import datetime
from pathlib import Path

def debug_log(message):
    """Log to file for debugging."""
    log_file = Path('.claude/hooks/debug.log')
    with open(log_file, 'a') as f:
        f.write(f"{datetime.now().isoformat()}: {message}\n")

def main():
    debug_log("Hook fired")

    try:
        input_data = json.load(sys.stdin)
        debug_log(f"Input: {input_data}")
    except Exception as e:
        debug_log(f"Error: {e}")
        raise
```

### 2. Test Hooks Manually

```bash
# Create realistic test input
cat > /tmp/hook_input.json << 'EOF'
{
  "session_id": "test123",
  "cwd": "/Users/iainnb/Documents/repos/triads",
  "transcript_path": "/path/to/transcript.jsonl"
}
EOF

# Run hook
cat /tmp/hook_input.json | python3 .claude/hooks/my_hook.py

# Check exit code
echo $?  # 0 = success, non-zero = error

# Check output
cat .claude/hooks/debug.log
```

### 3. Validate Input/Output

```python
def validate_input(data):
    """Ensure required fields exist."""
    required = ['session_id', 'cwd']
    missing = [f for f in required if f not in data]
    if missing:
        raise ValueError(f"Missing fields: {missing}")
    return True

def main():
    input_data = json.load(sys.stdin)
    validate_input(input_data)
    # ... rest of hook
```

### 4. Check Hook Execution

```bash
# Verify hook fired
tail -f .claude/hooks/debug.log

# Check stderr output (hooks log here)
# Look in Claude Code output for hook messages
```

### 5. Test Configuration

```bash
# Validate JSON syntax
python3 -m json.tool < .claude/settings.json

# Check hook path is correct
python3 -c "from pathlib import Path; print(Path('.claude/hooks/my_hook.py').exists())"

# Test hook is executable
ls -la .claude/hooks/my_hook.py
# Should show: -rwxr-xr-x

# Make executable if needed
chmod +x .claude/hooks/my_hook.py
```

### 6. Inspect Transcript Format

When working with Stop hook, inspect actual transcript:

```bash
# Find latest transcript
ls -lt ~/Library/Application\ Support/Claude/sessions/

# View transcript structure
cat ~/Library/Application\ Support/Claude/sessions/*/transcript.jsonl | head -20 | python3 -m json.tool
```

**Critical finding**: Message content is in `entry['message']['content']`, not `entry['content']`!

---

## Best Practices

### 1. Make Hooks Fast

Hooks block Claude Code execution, so optimize for speed:

```python
# GOOD: Quick operation
def main():
    data = json.load(sys.stdin)
    result = process_quickly(data)
    print(result)

# BAD: Slow operation
def main():
    data = json.load(sys.stdin)
    time.sleep(5)  # Don't do this!
    make_slow_api_call()  # Or this!
```

**Tip**: For slow operations, write to a queue and process asynchronously:

```python
def main():
    data = json.load(sys.stdin)

    # Fast: Write to queue
    with open('.claude/hooks/queue.jsonl', 'a') as f:
        f.write(json.dumps(data) + '\n')

    # Separate process reads queue and does slow work
```

### 2. Handle Errors Gracefully

```python
def main():
    try:
        # Your hook logic
        result = do_work()
        print(result)
    except Exception as e:
        # Log error but don't crash
        print(f"Hook error: {e}", file=sys.stderr)
        # Exit successfully so Claude Code continues
        sys.exit(0)
```

**Key**: Hooks should fail gracefully. Don't break Claude Code because of a hook error.

### 3. Use Structured Output

```python
# GOOD: Structured, parseable
print(json.dumps({
    "status": "success",
    "graph_updates": 5,
    "nodes_added": ["node1", "node2"]
}))

# BAD: Unstructured
print("Updated some stuff")
```

### 4. Log to stderr, Output to stdout

```python
# stdout → injected as context for Claude
print("Here's the project status: ...")

# stderr → logged for debugging (not shown to Claude)
print("Hook executed in 0.5s", file=sys.stderr)
print(f"Debug: processed {count} items", file=sys.stderr)
```

### 5. Version Your Hooks

```python
#!/usr/bin/env python3
"""
Hook: session_start.py
Version: 1.2.0
Last Updated: 2025-10-09
"""

VERSION = "1.2.0"

def main():
    print(f"Hook version: {VERSION}", file=sys.stderr)
    # ... rest of hook
```

### 6. Document Hook Behavior

```python
"""
SessionStart Hook: Load Project Context

What it does:
1. Loads .env variables
2. Reads recent git commits
3. Displays open PRs
4. Shows project metrics

Input: {"session_id": "...", "cwd": "..."}
Output: Formatted project context (stdout)

Dependencies: python3, git

Configuration: .claude/settings.json
"""
```

### 7. Test Across Sessions

```bash
# Test sequence:
# 1. Fresh session → Hook should fire
# 2. Exit and restart → Hook should fire again
# 3. Change settings.json → Exit/restart → New config should load
```

### 8. Keep Hooks Simple

Each hook should do **one thing well**:

```python
# GOOD: Focused hook
def session_start_hook():
    """Load knowledge graphs only."""
    graphs = load_all_graphs()
    print(format_graphs(graphs))

# BAD: Kitchen sink hook
def session_start_hook():
    """Load graphs, check git, run tests, update Jira, send Slack message..."""
    # Too many responsibilities!
```

**Tip**: Multiple focused hooks > One complex hook

---

## Common Pitfalls

### 1. ❌ Forgetting Top-Level "hooks" Key

```json
// WRONG
{
  "SessionStart": [...]
}

// CORRECT
{
  "hooks": {
    "SessionStart": [...]
  }
}
```

**Symptom**: Hooks never fire
**Fix**: Wrap all hooks in `"hooks": { ... }`

---

### 2. ❌ Not Making Scripts Executable

```bash
# WRONG
-rw-r--r-- my_hook.py

# CORRECT
-rwxr-xr-x my_hook.py
```

**Symptom**: "Permission denied" errors
**Fix**: `chmod +x .claude/hooks/my_hook.py`

---

### 3. ❌ Using Broken Hook Types

```json
// WRONG (PostToolUse is broken as of Oct 2025)
{
  "hooks": {
    "PostToolUse": [...]  // Won't fire!
  }
}

// CORRECT
{
  "hooks": {
    "Stop": [...]  // Use this instead
  }
}
```

**Symptom**: Hook configured but never fires
**Fix**: Use working hook types (SessionStart, Stop, UserPromptSubmit)

---

### 4. ❌ Incorrect Transcript Parsing

```python
# WRONG
content = entry['content']  // This doesn't exist!

# CORRECT
if 'message' in entry and 'content' in entry['message']:
    content = entry['message']['content']
```

**Symptom**: Stop hook fires but finds no data
**Fix**: Access `entry['message']['content']`

---

### 5. ❌ Blocking Operations

```python
# WRONG
def main():
    time.sleep(10)  # Blocks Claude Code!
    make_slow_api_call()  # Also blocks!
```

**Symptom**: Claude Code freezes during hook execution
**Fix**: Keep hooks fast, defer slow work to background processes

---

### 6. ❌ Not Handling Missing Files

```python
# WRONG
transcript = open(transcript_path, 'r')  // Crashes if missing!

# CORRECT
if Path(transcript_path).exists():
    with open(transcript_path, 'r') as f:
        # ... process
else:
    print("Transcript not found", file=sys.stderr)
    return
```

**Symptom**: Hook crashes on certain events
**Fix**: Always check file existence first

---

### 7. ❌ Invalid JSON in settings.json

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 .claude/hooks/my_hook.py"  // Missing comma!
          }
        ]
      }
    ]  // Extra comma!
  },
}
```

**Symptom**: Settings not loaded, hooks don't fire
**Fix**: Validate with `python3 -m json.tool < .claude/settings.json`

---

### 8. ❌ Forgetting to Restart Session

```bash
# Edit .claude/settings.json
# ... keep working in same session
# Hooks don't update!
```

**Symptom**: Configuration changes don't take effect
**Fix**: Exit and restart Claude Code after changing settings.json

---

## Troubleshooting

### Hook Never Fires

**Checklist**:
1. ✅ Top-level `"hooks"` key in settings.json?
2. ✅ Script is executable? (`chmod +x`)
3. ✅ Path is correct in settings.json?
4. ✅ Using a working hook type? (Not PostToolUse/PreToolUse)
5. ✅ Started fresh session after config changes?
6. ✅ JSON syntax is valid? (`python3 -m json.tool`)

**Debug**:
```bash
# Test hook manually
echo '{"session_id": "test"}' | python3 .claude/hooks/my_hook.py

# Check for errors
python3 .claude/hooks/my_hook.py < /tmp/input.json 2>&1 | grep -i error
```

---

### Hook Fires but Does Nothing

**Checklist**:
1. ✅ Hook receives correct input?
2. ✅ Input parsing works? (Check for JSON errors)
3. ✅ Logic conditions are met? (e.g., if statements)
4. ✅ Output goes to stdout (not stderr)?

**Debug**:
```python
# Add debug logging
def main():
    with open('/tmp/hook_debug.log', 'a') as f:
        f.write("Hook started\n")

    input_data = json.load(sys.stdin)

    with open('/tmp/hook_debug.log', 'a') as f:
        f.write(f"Received: {input_data}\n")

    # ... rest of hook
```

---

### Stop Hook Can't Find [GRAPH_UPDATE] Blocks

**Checklist**:
1. ✅ Parsing transcript correctly? (Check `entry['message']['content']`)
2. ✅ Regex pattern is correct?
3. ✅ [GRAPH_UPDATE] blocks are in response? (Check Claude's output)
4. ✅ Blocks are properly formatted? (No typos in markers)

**Debug**:
```python
# Log what you're scanning
def extract_updates(text):
    debug_log(f"Scanning {len(text)} chars")
    debug_log(f"Contains [GRAPH_UPDATE]: {'[GRAPH_UPDATE]' in text}")

    pattern = r'\[GRAPH_UPDATE\](.*?)\[/GRAPH_UPDATE\]'
    matches = re.findall(pattern, text, re.DOTALL)

    debug_log(f"Found {len(matches)} matches")
    return matches
```

---

### Hook Crashes Claude Code

**Checklist**:
1. ✅ Hook exits with code 0? (Success)
2. ✅ No uncaught exceptions?
3. ✅ Doesn't block for too long?

**Fix**:
```python
def main():
    try:
        # Your hook logic
        do_work()
        sys.exit(0)  # Explicit success
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(0)  # Still exit successfully to not break Claude
```

---

### Changes Not Reflected

**Symptom**: Updated hook script but behavior unchanged

**Cause**: Claude Code caches or you're in same session

**Fix**:
1. Save hook script
2. **Exit Claude Code completely**
3. Start **fresh session**
4. Test again

---

## Advanced Patterns

### Pattern 1: Chaining Hooks

Use one hook's output as input to another:

```python
# Hook 1: session_start.py
print(json.dumps({"session_context": "loaded"}))

# Hook 2: on_stop.py (reads session context)
# Can access environment or shared files
```

### Pattern 2: Conditional Execution

```python
def main():
    input_data = json.load(sys.stdin)

    # Only run in certain projects
    cwd = input_data.get('cwd', '')
    if '/sensitive-project/' not in cwd:
        return  # Skip this project

    # ... rest of hook
```

### Pattern 3: State Management

```python
# Maintain state across hook invocations
STATE_FILE = Path('.claude/hooks/state.json')

def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def main():
    state = load_state()
    state['last_run'] = datetime.now().isoformat()
    state['run_count'] = state.get('run_count', 0) + 1
    save_state(state)
```

### Pattern 4: External Integrations

```python
import requests

def main():
    input_data = json.load(sys.stdin)

    # Update external system
    response = requests.post('https://api.example.com/webhook', json={
        'event': 'claude_session_start',
        'session_id': input_data.get('session_id'),
        'timestamp': datetime.now().isoformat()
    })

    print("Session tracked externally", file=sys.stderr)
```

---

## Resources

### Official Documentation
- [Claude Code Hooks Reference](https://docs.claude.com/en/docs/claude-code/hooks)
- [Claude Code Documentation](https://docs.claude.com/en/docs/claude-code)

### Community Resources
- [claude-code-hooks-mastery](https://github.com/disler/claude-code-hooks-mastery) - Examples and patterns
- GitHub Issues: Search for "claude code hooks" to see common problems and solutions

### Known Issues
- [Issue #6305](https://github.com/anthropics/claude-code/issues/6305) - PostToolUse not firing
- [Issue #6403](https://github.com/anthropics/claude-code/issues/6403) - "Trigger mechanism broken"
- [Issue #3148](https://github.com/anthropics/claude-code/issues/3148) - Matcher patterns

---

## Conclusion

Claude Code hooks are a powerful automation system that lets you:

✅ **Inject context** automatically (SessionStart)
✅ **Process outputs** automatically (Stop)
✅ **Validate inputs** automatically (UserPromptSubmit)
✅ **Integrate with external systems**
✅ **Build persistent memory** (like knowledge graphs)

**Key Takeaways**:

1. **Use working hook types**: SessionStart, Stop, UserPromptSubmit work reliably
2. **Avoid broken hooks**: PostToolUse/PreToolUse don't fire (as of Oct 2025)
3. **Configuration matters**: Top-level `"hooks"` key is required
4. **Transcript parsing is tricky**: Content is in `entry['message']['content']`
5. **Test manually first**: Before testing in Claude Code
6. **Keep hooks fast**: They block execution
7. **Handle errors gracefully**: Don't crash Claude Code
8. **Debug with logging**: Write to files for inspection

**Real-World Impact**:

Our knowledge graph system proves hooks enable sophisticated automation:
- Zero manual work
- Persistent context across sessions
- Structured knowledge capture
- Scalable to complex workflows

Start simple, test thoroughly, and iterate. Hooks unlock Claude Code's full potential as an autonomous agent platform.

---

**Happy hooking!** 🪝

*Guide based on implementing a production knowledge graph system for triad-based AI agent orchestration. October 2025.*
