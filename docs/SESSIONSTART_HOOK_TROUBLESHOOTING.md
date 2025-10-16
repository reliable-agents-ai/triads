# SessionStart Hook Troubleshooting Guide

## Problem Summary

**Symptom**: SessionStart hook runs successfully (confirmed by logs) but its output is not injected into Claude's context.

**Root Cause**: Claude Code requires SessionStart hooks to output in a specific JSON format, not plain text.

---

## The Debugging Journey

### Initial Symptoms

1. Custom triad routing directives were not appearing in Claude's context
2. When user said "I am having behavioural issues with my son", Claude responded as generic programming assistant instead of routing to the parenting research triad system
3. Hook script ran without errors when executed manually

### Debugging Steps Taken

#### Step 1: Verify Hook Registration
✅ Confirmed `plugin.json` has `"hooks": "./hooks/hooks.json"` reference
✅ Confirmed `hooks.json` has valid SessionStart hook definition
✅ Both files were present and correctly formatted

#### Step 2: Verify Hook Execution
Added debug logging to `/tmp/claude_hook_debug.log`:

```python
debug_log_path = Path('/tmp/claude_hook_debug.log')
with open(debug_log_path, 'w') as debug_log:
    debug_log.write(f"CWD: {os.getcwd()}\n")
    debug_log.write(f"PWD: {os.environ.get('PWD')}\n")
    # ... more diagnostics
```

**Result**: ✅ Hook ran successfully, found settings.json, generated routing directives

#### Step 3: Verify Working Directory
**Issue Found**: Hook needs to find project-specific files (`.claude/settings.json`)

**Solution**: Added PWD environment variable fallback:

```python
def load_project_settings():
    settings_file = Path('.claude/settings.json')

    # Fallback to PWD if relative path doesn't work
    if not settings_file.exists():
        pwd = os.environ.get('PWD')
        if pwd:
            settings_file = Path(pwd) / '.claude/settings.json'

    # ... rest of function
```

**Result**: ✅ Hook could find project files from any working directory

#### Step 4: Verify Output Generation
Added logging to show what the hook outputs:

```python
try:
    with open('/tmp/claude_hook_debug.log', 'a') as debug_log:
        debug_log.write("FULL OUTPUT (what gets printed to stdout)\n")
        debug_log.write(f"Output has {len(output)} lines\n")
        debug_log.write("\n".join(output))
except:
    pass

print("\n".join(output))
```

**Result**: ✅ Hook generated correct routing directives and printed them to stdout

#### Step 5: Test Minimal Output
Simplified hook to output just one line:

```python
print("HOOK_TEST_WORKING")
```

**Result**: ❌ Still not appearing in Claude's context

#### Step 6: Research Claude Code Documentation
Found critical GitHub issues:
- [Issue #9455](https://github.com/anthropics/claude-code/issues/9455): Bug about additionalContext visibility
- [Official Hooks Documentation](https://docs.claude.com/en/docs/claude-code/hooks): Revealed JSON format requirement

---

## The Solution

### Required Format

Claude Code requires SessionStart hooks to output **JSON** in this exact format:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "Your context here"
  }
}
```

### Before (Incorrect - Plain Text)

```python
def main():
    output = []
    output.append("# My Custom Routing")
    output.append("Route to triads...")

    # ❌ WRONG - This won't be injected
    print("\n".join(output))
```

### After (Correct - JSON Format)

```python
def main():
    output = []
    output.append("# My Custom Routing")
    output.append("Route to triads...")

    # ✅ CORRECT - This will be injected into Claude's context
    hook_output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": "\n".join(output)
        }
    }

    print(json.dumps(hook_output))
```

---

## Implementation

### Full Working Example

See `hooks/session_start.py` for the complete implementation. Key sections:

```python
#!/usr/bin/env python3
import json
import os
from pathlib import Path
from datetime import datetime

def main():
    """Generate routing + knowledge graph context for session."""

    # Build context output
    output = []

    # Load project settings (with PWD fallback)
    settings = load_project_settings()
    if settings:
        routing_content = generate_routing_from_settings(settings)
        output.append(routing_content)

    # Load knowledge graphs
    graphs = load_all_graphs()
    output.append(format_graphs(graphs))

    # Output in the correct JSON format for Claude Code
    hook_output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": "\n".join(output)
        }
    }

    print(json.dumps(hook_output))

if __name__ == "__main__":
    main()
```

### Helper: PWD Fallback Pattern

Use this pattern for all file loading in hooks:

```python
def load_project_file(relative_path):
    """Load file from project, with PWD fallback for hooks."""
    file_path = Path(relative_path)

    # Try relative path first
    if not file_path.exists():
        # Fallback to PWD environment variable
        pwd = os.environ.get('PWD')
        if pwd:
            file_path = Path(pwd) / relative_path

    if file_path.exists():
        return file_path.read_text()
    return None
```

---

## How to Test

### 1. Add Debug Logging

```python
# At start of main()
with open('/tmp/claude_hook_debug.log', 'w') as debug_log:
    debug_log.write(f"Hook ran at: {datetime.now()}\n")
    debug_log.write(f"CWD: {os.getcwd()}\n")
    debug_log.write(f"PWD: {os.environ.get('PWD')}\n")
```

### 2. Test Manually

```bash
cd /path/to/your/project
python3 ~/.claude/plugins/marketplaces/your-plugin/hooks/session_start.py
```

Should output valid JSON:
```json
{"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "..."}}
```

### 3. Test in Claude Code

```bash
# Update plugin
/plugins update your-marketplace

# Completely quit and restart Claude Code
# (SessionStart hooks only run once at session start)

# Start fresh session in your project directory
cd /path/to/your/project
claude
```

### 4. Verify Context Injection

Ask Claude: "What special instructions or context do you have loaded for this session?"

You should see your custom context in Claude's response.

---

## Common Issues

### Issue: Hook runs but context not injected
**Cause**: Using plain text instead of JSON format
**Solution**: Wrap output in JSON structure shown above

### Issue: Hook can't find project files
**Cause**: Hook runs from plugin directory, not project directory
**Solution**: Use PWD environment variable as fallback

### Issue: Hook runs twice or duplicates output
**Cause**: SessionStart runs once per session - if continued conversations, hook doesn't re-run
**Solution**: Start completely fresh session to test

### Issue: Changes not taking effect
**Cause**: Claude Code caches hook scripts
**Solution**: Completely quit and restart Claude Code (not just new conversation)

---

## Key Learnings

### 1. JSON Format is Required
Claude Code uses a structured approach to hook output. Plain text will be ignored.

### 2. Environment Variables Available
- `PWD`: User's project directory
- `CLAUDE_PLUGIN_ROOT`: Plugin installation directory
- `CLAUDECODE`: Set to "1" when running in Claude Code
- `CLAUDE_CODE_ENTRYPOINT`: Usually "cli"

### 3. Hook Execution Context
- Hooks run from plugin directory by default
- Use `PWD` to access user's project files
- Hooks have full Python environment available

### 4. Session Lifecycle
- SessionStart runs **once** at session start
- Context is injected into that entire conversation
- Continued conversations do **not** re-run the hook
- Must start fresh session to test changes

### 5. Debugging Approach
1. Log to `/tmp/` for visibility outside Claude
2. Test manually first: `python3 path/to/hook.py`
3. Verify JSON output format
4. Check timing: `stat -f "Modified: %Sm" /tmp/hook.log`
5. Restart Claude Code completely to reload hook code

---

## Related Issues

- [Issue #9455](https://github.com/anthropics/claude-code/issues/9455) - additionalContext visibility bug (fixed in 2.0.17)
- [Issue #9542](https://github.com/anthropics/claude-code/issues/9542) - Windows infinite hang with SessionStart
- [Issue #4318](https://github.com/anthropics/claude-code/issues/4318) - Original feature request for SessionStart hooks

---

## Version History

- **v0.4.6**: Fixed JSON format requirement (2025-10-16)
- **v0.4.5**: Added PWD fallback for project file loading (2025-10-16)
- **v0.4.4**: Added hooks reference to plugin.json (2025-10-16)
- **v0.4.3**: Enhanced routing recognition patterns (2025-10-16)
- **v0.4.2**: Added description field to agent frontmatter (2025-10-16)

---

## See Also

- [Official Hooks Documentation](https://docs.claude.com/en/docs/claude-code/hooks)
- [Plugin Development Guide](./CLAUDE_CODE_INTEGRATION_GUIDE.md)
- [Hook Examples](../hooks/)
