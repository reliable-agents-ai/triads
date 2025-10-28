---
name: create-hook-file
description: Create Claude Code lifecycle hooks with matcher patterns and event handlers. Use when generating hooks, creating event handlers, writing lifecycle hooks, setting up PreToolUse PostToolUse Notification UserPromptSubmit Stop SubagentStop PreCompact SessionStart SessionEnd hooks, hook configuration, hook scripts, Python hooks, Bash hooks, JSON hooks, hook matchers, tool call interception, notification handling, session lifecycle, hook file generation, hook templates, hook best practices, hook examples, hook validation, hook testing, event-driven hooks, async hooks, hook priorities, hook error handling, hook debugging, hook documentation, lifecycle events, tool use hooks, user prompt hooks, compaction hooks, hook patterns, hook strategies, hook architecture
---

# Create Hook File

**Purpose**: Generate Claude Code lifecycle hook files with proper matchers and event handlers following official Claude Code specifications.

**Authority**: Meta-level (creates Claude Code components)

**Based on**: [Official Claude Code Hooks Documentation](https://docs.claude.com/en/docs/claude-code/hooks.md)

---

## 📋 When to Invoke

**Invoke this skill when**:
- Generating lifecycle hooks
- Creating event handlers
- Setting up tool call interception
- Configuring notification handling
- Implementing session lifecycle management
- Adding validation hooks
- Creating custom workflow hooks

**Keywords that trigger this skill**:
- "create hook"
- "generate hook"
- "hook file"
- "lifecycle hook"
- "PreToolUse hook"
- "PostToolUse hook"
- "event handler"

---

## 🎯 Official Specification (From Claude Code Docs)

### What Are Hooks?

Hooks are scripts that run in response to Claude Code lifecycle events. They enable:
- **Tool call interception** (PreToolUse, PostToolUse)
- **Notification handling** (Notification)
- **User input processing** (UserPromptSubmit)
- **Session lifecycle** (SessionStart, SessionEnd, Stop, SubagentStop)
- **Memory management** (PreCompact)

### Hook Types (9 Events)

| Event | When it fires | Use cases |
|-------|---------------|-----------|
| **PreToolUse** | Before tool execution | Validation, modification, cancellation |
| **PostToolUse** | After tool execution | Logging, result transformation |
| **Notification** | When notification appears | Custom UI, filtering |
| **UserPromptSubmit** | Before user message sent | Input validation, augmentation |
| **Stop** | When main agent stops | Cleanup, validation |
| **SubagentStop** | When subagent stops | Subagent result processing |
| **PreCompact** | Before memory compaction | Memory preservation |
| **SessionStart** | When session begins | Initialization |
| **SessionEnd** | When session ends | Cleanup, reporting |

### Hook File Structure

```markdown
---
event: <event-type>
matcher:
  <matcher-fields>
---

<script-content>
```

### Matcher Fields

Matchers filter when hooks run:

**PreToolUse / PostToolUse**:
```yaml
matcher:
  tool_name: "Read"  # Exact match
  tool_name_pattern: ".*"  # Regex pattern
```

**Notification**:
```yaml
matcher:
  type: "ToolApprovalRequest"  # Notification type
```

**UserPromptSubmit**:
```yaml
matcher: {}  # Runs on all user prompts
```

**Stop / SubagentStop**:
```yaml
matcher:
  subagent_name: "gap-analyzer"  # Specific subagent
```

**PreCompact / SessionStart / SessionEnd**:
```yaml
matcher: {}  # No filtering
```

### Script Languages

- **Python** (.py): Full scripting, complex logic
- **Bash** (.sh): Shell commands, simple operations
- **JSON** (.json): Static responses, simple transformations

---

## 📋 Skill Procedure

### Step 1: Gather Hook Specifications

**Required information**:
```yaml
hook_spec:
  event: "{{PreToolUse|PostToolUse|Notification|UserPromptSubmit|Stop|SubagentStop|PreCompact|SessionStart|SessionEnd}}"
  purpose: "{{what-hook-does}}"
  matcher: "{{when-to-fire}}"
  script_language: "{{python|bash|json}}"
  input_fields: "{{what-hook-receives}}"
  output_fields: "{{what-hook-returns}}"
  priority: "{{execution-order}}"  # Optional
```

**Example**:
```yaml
hook_spec:
  event: "PreToolUse"
  purpose: "Validate Read tool only accesses allowed directories"
  matcher:
    tool_name: "Read"
  script_language: "python"
  input_fields: "tool_name, parameters"
  output_fields: "approved (boolean), replacement_result (optional)"
  priority: 10  # Higher priority = runs first
```

---

### Step 2: Create Hook Frontmatter

**Generate frontmatter following official spec**:

```yaml
---
event: {{event-type}}
matcher:
  {{matcher-fields}}
priority: {{optional-number}}  # Higher = earlier execution
---
```

**Matcher examples by event type**:

**PreToolUse / PostToolUse**:
```yaml
# Match specific tool
matcher:
  tool_name: "Read"

# Match tool pattern
matcher:
  tool_name_pattern: "(Read|Write|Edit)"

# Match all tools
matcher:
  tool_name_pattern: ".*"
```

**Notification**:
```yaml
# Match specific notification type
matcher:
  type: "ToolApprovalRequest"

# Match multiple types
matcher:
  type: "(ToolApprovalRequest|Warning)"
```

**UserPromptSubmit**:
```yaml
# Runs on all user prompts
matcher: {}
```

**Stop**:
```yaml
# Runs on main agent stop
matcher: {}
```

**SubagentStop**:
```yaml
# Match specific subagent
matcher:
  subagent_name: "gap-analyzer"

# Match subagent pattern
matcher:
  subagent_name_pattern: ".*-analyzer"
```

**PreCompact / SessionStart / SessionEnd**:
```yaml
# No filtering
matcher: {}
```

---

### Step 3: Create Hook Script

**Script structure varies by language**:

#### Python Hook (.py)

```python
#!/usr/bin/env python3
"""
Hook Description

Event: {{event-type}}
Purpose: {{what-hook-does}}
"""

import json
import sys

def main():
    # Read JSON input from stdin
    input_data = json.loads(sys.stdin.read())

    # Extract fields (varies by event type)
    # See "Input/Output Schemas" section below

    # Hook logic here

    # Return JSON output to stdout
    output = {
        # Fields vary by event type
    }

    print(json.dumps(output))
    sys.exit(0)

if __name__ == "__main__":
    main()
```

#### Bash Hook (.sh)

```bash
#!/bin/bash
"""
Hook Description

Event: {{event-type}}
Purpose: {{what-hook-does}}
"""

# Read JSON input from stdin
INPUT=$(cat)

# Parse JSON (using jq)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name')

# Hook logic here

# Return JSON output
cat <<EOF
{
  "approved": true
}
EOF

exit 0
```

#### JSON Hook (.json)

```json
{
  "approved": true,
  "message": "Static response"
}
```

**Note**: JSON hooks are static - they return the same response every time. Use for simple, unchanging responses only.

---

### Step 4: Input/Output Schemas by Event Type

#### PreToolUse Hook

**Input**:
```json
{
  "tool_name": "Read",
  "parameters": {
    "file_path": "/path/to/file.py",
    "offset": 0,
    "limit": 100
  }
}
```

**Output**:
```json
{
  "approved": true,  // Required: true|false
  "replacement_result": "Optional: replace tool execution with this result",
  "message": "Optional: explain why blocked/modified"
}
```

**Actions**:
- `approved: true` → Tool executes normally
- `approved: false` → Tool blocked, user sees message
- `replacement_result` → Tool doesn't execute, result injected

---

#### PostToolUse Hook

**Input**:
```json
{
  "tool_name": "Read",
  "parameters": {
    "file_path": "/path/to/file.py"
  },
  "result": {
    "success": true,
    "output": "file contents..."
  }
}
```

**Output**:
```json
{
  "replacement_result": "Optional: replace actual result with this"
}
```

**Actions**:
- No `replacement_result` → Original result used
- With `replacement_result` → Agent sees modified result

---

#### Notification Hook

**Input**:
```json
{
  "type": "ToolApprovalRequest",
  "message": "The Read tool wants to access /sensitive/file.txt",
  "metadata": {
    "tool_name": "Read",
    "file_path": "/sensitive/file.txt"
  }
}
```

**Output**:
```json
{
  "suppress": false,  // Optional: hide notification
  "replacement_message": "Optional: change notification text"
}
```

**Actions**:
- `suppress: true` → Notification hidden from user
- `replacement_message` → Changes notification text

---

#### UserPromptSubmit Hook

**Input**:
```json
{
  "prompt": "User's message text"
}
```

**Output**:
```json
{
  "approved": true,  // Required: true|false
  "replacement_prompt": "Optional: modify user's message",
  "message": "Optional: explain why blocked"
}
```

**Actions**:
- `approved: false` → Prompt blocked
- `replacement_prompt` → Changes user's message before agent sees it

**Use cases**:
- Add context to user prompts
- Enforce prompt templates
- Inject reminders

---

#### Stop Hook

**Input**:
```json
{
  "final_message": "Agent's last message to user"
}
```

**Output**:
```json
{
  "approved": true,  // Required: true|false
  "message": "Optional: explain why agent can't stop"
}
```

**Actions**:
- `approved: false` → Agent can't stop, continues working
- Useful for enforcing completion criteria

---

#### SubagentStop Hook

**Input**:
```json
{
  "subagent_name": "gap-analyzer",
  "final_message": "Subagent's last message"
}
```

**Output**:
```json
{
  "approved": true,
  "message": "Optional: explain why subagent can't stop"
}
```

**Actions**:
- Same as Stop hook but for subagents
- Useful for enforcing subagent protocols

---

#### PreCompact Hook

**Input**:
```json
{
  "messages": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}
```

**Output**:
```json
{
  "preserve_indices": [0, 5, 10]  // Optional: message indices to preserve
}
```

**Actions**:
- Specify which messages to keep during compaction
- Useful for preserving important context

---

#### SessionStart Hook

**Input**:
```json
{
  "session_id": "abc123",
  "timestamp": "2025-10-27T10:00:00Z"
}
```

**Output**:
```json
{
  "message": "Optional: inject message at session start"
}
```

**Actions**:
- Initialize session state
- Set up logging
- Inject welcome message

---

#### SessionEnd Hook

**Input**:
```json
{
  "session_id": "abc123",
  "timestamp": "2025-10-27T12:00:00Z",
  "duration_seconds": 7200
}
```

**Output**:
```json
{
  "message": "Optional: inject message at session end"
}
```

**Actions**:
- Cleanup session state
- Generate session report
- Save analytics

---

### Step 5: Hook Storage Location

**Path structure**: `.claude/hooks/<event-type>/<hook-name>.<ext>`

**Examples**:
- `.claude/hooks/pre_tool_use/validate-read-access.py`
- `.claude/hooks/post_tool_use/log-tool-usage.sh`
- `.claude/hooks/user_prompt_submit/inject-context.py`
- `.claude/hooks/stop/validate-completion.py`
- `.claude/hooks/session_start/initialize.sh`

**Directory names** (must match event type):
- `pre_tool_use/`
- `post_tool_use/`
- `notification/`
- `user_prompt_submit/`
- `stop/`
- `subagent_stop/`
- `pre_compact/`
- `session_start/`
- `session_end/`

---

### Step 6: Register Hook in Settings

**File**: `.claude/settings.json`

```json
{
  "hooks": {
    "pre_tool_use": [
      {
        "script": ".claude/hooks/pre_tool_use/validate-read-access.py",
        "enabled": true,
        "priority": 10
      }
    ],
    "post_tool_use": [
      {
        "script": ".claude/hooks/post_tool_use/log-tool-usage.sh",
        "enabled": true
      }
    ],
    "user_prompt_submit": [
      {
        "script": ".claude/hooks/user_prompt_submit/inject-context.py",
        "enabled": true
      }
    ]
  }
}
```

**Fields**:
- `script`: Path to hook file (relative to project root)
- `enabled`: `true`|`false` (disable without deleting)
- `priority`: Optional number (higher = runs first)

---

### Step 7: Validate Hook File

**Validation**:

```bash
# Check file exists
ls .claude/hooks/pre_tool_use/validate-read-access.py

# Check frontmatter (first 10 lines)
head -10 .claude/hooks/pre_tool_use/validate-read-access.py

# Verify executable (Python/Bash only)
test -x .claude/hooks/pre_tool_use/validate-read-access.py
chmod +x .claude/hooks/pre_tool_use/validate-read-access.py  # If not executable

# Test hook with sample input
echo '{"tool_name": "Read", "parameters": {"file_path": "/test.py"}}' | \
  .claude/hooks/pre_tool_use/validate-read-access.py
```

**Expected output**:
```json
{
  "approved": true
}
```

---

## 📊 Output Format

```yaml
hook_file_created:
  path: ".claude/hooks/{{event-type}}/{{hook-name}}.{{ext}}"
  frontmatter:
    event: "{{event-type}}"
    matcher:
      {{matcher-fields}}
    priority: {{number}}
  script_language: "{{python|bash|json}}"
  registered_in_settings: "{{YES|NO}}"
  validation: "{{PASS|FAIL}}"
  test_result: "{{output-from-test}}"
```

---

## 💡 Hook Examples

### Example 1: Validate Read Tool Access (PreToolUse)

**File**: `.claude/hooks/pre_tool_use/validate-read-access.py`

```python
#!/usr/bin/env python3
"""
Validate Read tool only accesses allowed directories.

Event: PreToolUse
Matcher: tool_name = "Read"
"""

import json
import sys
import os

ALLOWED_DIRS = [
    "/Users/iainnb/Documents/repos/triads",
    "/Users/iainnb/.claude"
]

def main():
    input_data = json.loads(sys.stdin.read())

    tool_name = input_data.get("tool_name")
    parameters = input_data.get("parameters", {})
    file_path = parameters.get("file_path", "")

    # Resolve to absolute path
    abs_path = os.path.abspath(file_path)

    # Check if path is within allowed directories
    allowed = any(abs_path.startswith(allowed_dir) for allowed_dir in ALLOWED_DIRS)

    if allowed:
        output = {
            "approved": True
        }
    else:
        output = {
            "approved": False,
            "message": f"Access denied: {file_path} is outside allowed directories"
        }

    print(json.dumps(output))
    sys.exit(0)

if __name__ == "__main__":
    main()
```

**Frontmatter**:
```yaml
---
event: PreToolUse
matcher:
  tool_name: "Read"
priority: 10
---
```

---

### Example 2: Log Tool Usage (PostToolUse)

**File**: `.claude/hooks/post_tool_use/log-tool-usage.sh`

```bash
#!/bin/bash
"""
Log all tool usage to file for audit trail.

Event: PostToolUse
Matcher: All tools
"""

# Read JSON input
INPUT=$(cat)

# Extract fields
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name')
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Log to file
LOG_FILE=".claude/logs/tool-usage.log"
mkdir -p "$(dirname "$LOG_FILE")"

echo "$TIMESTAMP | $TOOL_NAME | $INPUT" >> "$LOG_FILE"

# Return success (no modification)
cat <<EOF
{}
EOF

exit 0
```

**Frontmatter**:
```yaml
---
event: PostToolUse
matcher:
  tool_name_pattern: ".*"
---
```

---

### Example 3: Inject Context into User Prompts (UserPromptSubmit)

**File**: `.claude/hooks/user_prompt_submit/inject-context.py`

```python
#!/usr/bin/env python3
"""
Inject constitutional reminder into user prompts.

Event: UserPromptSubmit
Matcher: All prompts
"""

import json
import sys

CONSTITUTIONAL_REMINDER = """
REMINDER: Follow constitutional principles:
- Evidence-based claims only
- Multi-method verification (≥2 methods)
- Escalate uncertainty <90%
- Complete transparency
- Validate all assumptions
"""

def main():
    input_data = json.loads(sys.stdin.read())

    user_prompt = input_data.get("prompt", "")

    # Inject reminder at end of prompt
    augmented_prompt = f"{user_prompt}\n\n{CONSTITUTIONAL_REMINDER}"

    output = {
        "approved": True,
        "replacement_prompt": augmented_prompt
    }

    print(json.dumps(output))
    sys.exit(0)

if __name__ == "__main__":
    main()
```

**Frontmatter**:
```yaml
---
event: UserPromptSubmit
matcher: {}
---
```

---

### Example 4: Validate Completion Before Stop (Stop)

**File**: `.claude/hooks/stop/validate-completion.py`

```python
#!/usr/bin/env python3
"""
Validate agent completed all todos before stopping.

Event: Stop
Matcher: All stops
"""

import json
import sys
import os

def main():
    input_data = json.loads(sys.stdin.read())

    final_message = input_data.get("final_message", "")

    # Check if todos exist
    todo_file = ".claude/todos.json"

    if not os.path.exists(todo_file):
        # No todos, OK to stop
        output = {"approved": True}
    else:
        with open(todo_file, 'r') as f:
            todos = json.load(f)

        # Check for incomplete todos
        incomplete = [t for t in todos if t.get("status") != "completed"]

        if incomplete:
            output = {
                "approved": False,
                "message": f"Cannot stop: {len(incomplete)} todos incomplete. Complete all todos before stopping."
            }
        else:
            output = {"approved": True}

    print(json.dumps(output))
    sys.exit(0)

if __name__ == "__main__":
    main()
```

**Frontmatter**:
```yaml
---
event: Stop
matcher: {}
priority: 5
---
```

---

### Example 5: Preserve Important Messages (PreCompact)

**File**: `.claude/hooks/pre_compact/preserve-important.py`

```python
#!/usr/bin/env python3
"""
Preserve messages containing constitutional principles during compaction.

Event: PreCompact
Matcher: All compactions
"""

import json
import sys

IMPORTANT_KEYWORDS = [
    "constitutional",
    "evidence-based",
    "multi-method verification",
    "uncertainty escalation",
    "CLAUDE.md",
    "@import"
]

def main():
    input_data = json.loads(sys.stdin.read())

    messages = input_data.get("messages", [])

    # Find messages containing important keywords
    preserve_indices = []

    for i, message in enumerate(messages):
        content = message.get("content", "").lower()

        if any(keyword.lower() in content for keyword in IMPORTANT_KEYWORDS):
            preserve_indices.append(i)

    output = {
        "preserve_indices": preserve_indices
    }

    print(json.dumps(output))
    sys.exit(0)

if __name__ == "__main__":
    main()
```

**Frontmatter**:
```yaml
---
event: PreCompact
matcher: {}
---
```

---

### Example 6: Session Initialization (SessionStart)

**File**: `.claude/hooks/session_start/initialize.sh`

```bash
#!/bin/bash
"""
Initialize session logging and welcome message.

Event: SessionStart
Matcher: All sessions
"""

# Read JSON input
INPUT=$(cat)

SESSION_ID=$(echo "$INPUT" | jq -r '.session_id')
TIMESTAMP=$(echo "$INPUT" | jq -r '.timestamp')

# Create session log directory
mkdir -p .claude/logs/sessions

# Initialize session log
SESSION_LOG=".claude/logs/sessions/${SESSION_ID}.log"
echo "Session started: $TIMESTAMP" > "$SESSION_LOG"

# Return welcome message
cat <<EOF
{
  "message": "Session initialized. Constitutional principles active. All work will follow evidence-based, verified, transparent standards."
}
EOF

exit 0
```

**Frontmatter**:
```yaml
---
event: SessionStart
matcher: {}
---
```

---

## 🎯 Hook Best Practices (From Official Docs)

1. **Keep hooks fast**: Hooks block execution. Avoid slow operations.

2. **Handle errors gracefully**: Always catch exceptions, return valid JSON.

3. **Use matchers to filter**: Don't process every event if you only care about specific tools.

4. **Test hooks independently**: Use sample JSON input to test before deploying.

5. **Log hook activity**: Help debugging by logging decisions to file.

6. **Version control hooks**: Check hooks into git for team sharing.

7. **Document hook purpose**: Add clear comments explaining what hook does and why.

8. **Use priority for ordering**: Higher priority hooks run first (useful for dependencies).

9. **Enable/disable via settings**: Use `"enabled": false` instead of deleting hooks.

10. **Validate JSON output**: Malformed JSON will cause hook to fail.

---

## 🎯 Common Hook Patterns

### Pattern 1: Whitelist/Blacklist Validation

```python
# Whitelist: Only allow specific values
ALLOWED_TOOLS = ["Read", "Write", "Edit"]

if tool_name in ALLOWED_TOOLS:
    output = {"approved": True}
else:
    output = {"approved": False, "message": f"{tool_name} not allowed"}
```

### Pattern 2: Path Validation

```python
import os

ALLOWED_PATHS = ["/safe/dir1", "/safe/dir2"]

abs_path = os.path.abspath(file_path)
allowed = any(abs_path.startswith(p) for p in ALLOWED_PATHS)
```

### Pattern 3: Result Transformation

```python
# PostToolUse: Redact sensitive data from results
result = input_data.get("result", {})
output_text = result.get("output", "")

# Redact emails
import re
redacted = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', output_text)

output = {
    "replacement_result": {
        "success": True,
        "output": redacted
    }
}
```

### Pattern 4: Conditional Injection

```python
# UserPromptSubmit: Add context only if missing
user_prompt = input_data.get("prompt", "")

if "constitutional" not in user_prompt.lower():
    augmented = f"{user_prompt}\n\nREMINDER: Follow constitutional principles"
    output = {"approved": True, "replacement_prompt": augmented}
else:
    output = {"approved": True}  # No modification needed
```

### Pattern 5: Async Operations (Background)

```python
import subprocess
import threading

def async_log(data):
    # Run in background thread
    subprocess.run(["some-logging-command", data])

# Start background task
thread = threading.Thread(target=async_log, args=(json.dumps(input_data),))
thread.daemon = True
thread.start()

# Return immediately (don't block)
output = {"approved": True}
```

---

## 🎯 Hook Testing

### Test Script Template

```bash
#!/bin/bash
# Test hook with sample input

HOOK_FILE=".claude/hooks/pre_tool_use/validate-read-access.py"

# Sample input
cat <<EOF | python3 "$HOOK_FILE"
{
  "tool_name": "Read",
  "parameters": {
    "file_path": "/Users/iainnb/Documents/repos/triads/README.md"
  }
}
EOF

# Check exit code
if [ $? -eq 0 ]; then
    echo "✅ Hook executed successfully"
else
    echo "❌ Hook failed"
    exit 1
fi
```

### Test Cases

**Test approved case**:
```bash
echo '{"tool_name": "Read", "parameters": {"file_path": "/allowed/path.py"}}' | \
  .claude/hooks/pre_tool_use/validate-read-access.py
# Expected: {"approved": true}
```

**Test blocked case**:
```bash
echo '{"tool_name": "Read", "parameters": {"file_path": "/forbidden/path.py"}}' | \
  .claude/hooks/pre_tool_use/validate-read-access.py
# Expected: {"approved": false, "message": "..."}
```

**Test malformed input**:
```bash
echo 'not-json' | .claude/hooks/pre_tool_use/validate-read-access.py
# Expected: Graceful error handling
```

---

## 🎯 Hook Debugging

### Debug Logging

```python
import logging

# Setup logging
logging.basicConfig(
    filename='.claude/logs/hooks.log',
    level=logging.DEBUG,
    format='%(asctime)s | %(levelname)s | %(message)s'
)

def main():
    input_data = json.loads(sys.stdin.read())

    # Log input
    logging.debug(f"Hook input: {json.dumps(input_data)}")

    # Hook logic
    output = {"approved": True}

    # Log output
    logging.debug(f"Hook output: {json.dumps(output)}")

    print(json.dumps(output))
```

### Error Handling

```python
def main():
    try:
        input_data = json.loads(sys.stdin.read())

        # Hook logic
        output = {"approved": True}

        print(json.dumps(output))
        sys.exit(0)

    except Exception as e:
        # Log error
        logging.error(f"Hook error: {str(e)}")

        # Return safe default
        output = {
            "approved": False,
            "message": f"Hook error: {str(e)}"
        }

        print(json.dumps(output))
        sys.exit(1)
```

---

## 🎯 Success Criteria

- [ ] Frontmatter present with correct event type
- [ ] Matcher configured appropriately
- [ ] Script uses correct language (Python/Bash/JSON)
- [ ] Input/output schema matches event type
- [ ] Script is executable (chmod +x for Python/Bash)
- [ ] Hook registered in `.claude/settings.json`
- [ ] Hook tested with sample input
- [ ] JSON output is valid
- [ ] Hook handles errors gracefully
- [ ] Hook logs activity for debugging

---

**This skill creates Claude Code lifecycle hooks following official specifications.**

**Version**: 1.0.0
**Last Updated**: 2025-10-27
**Source**: [Claude Code Hooks Docs](https://docs.claude.com/en/docs/claude-code/hooks.md)
