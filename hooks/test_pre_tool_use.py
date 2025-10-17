#!/usr/bin/env python3
"""
Test hook to verify if PreToolUse fires.
This is a diagnostic script to check if PreToolUse is working.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

def main():
    """Test PreToolUse hook."""

    # Log to file so we can verify it fired
    log_file = Path('.claude/hooks/pre_tool_use_test.log')
    log_file.parent.mkdir(parents=True, exist_ok=True)

    with open(log_file, 'a') as f:
        f.write(f"\n{'='*80}\n")
        f.write(f"PreToolUse Hook Fired: {datetime.now().isoformat()}\n")
        f.write(f"{'='*80}\n")

        # Read stdin - PreToolUse receives tool_name and tool_input
        input_data = {}
        try:
            input_data = json.load(sys.stdin)
            f.write(f"Input data: {json.dumps(input_data, indent=2)}\n")

            # Log tool details
            tool_name = input_data.get('tool_name', 'unknown')
            tool_input = input_data.get('tool_input', {})

            f.write(f"\nTool Name: {tool_name}\n")
            f.write(f"Tool Input: {json.dumps(tool_input, indent=2)}\n")

        except json.JSONDecodeError as e:
            f.write(f"JSON decode error: {e}\n")
            # Try to read raw input
            try:
                sys.stdin.seek(0)
                input_text = sys.stdin.read()
                f.write(f"Raw input: {input_text}\n")
            except:
                f.write("Could not read raw input\n")
        except Exception as e:
            f.write(f"Unexpected error: {e}\n")

        f.write(f"{'='*80}\n\n")

    # Output to stderr so user sees it
    print("🧪 PreToolUse test hook fired!", file=sys.stderr)
    print(f"   Tool: {input_data.get('tool_name', 'unknown')}", file=sys.stderr)
    print(f"   Logged to: {log_file}", file=sys.stderr)

    # Output to stdout (would be injected as context if this works)
    print(f"\n⚠️ PRE-TOOL-USE TEST: Hook fired before {input_data.get('tool_name', 'tool')} execution!\n")

    # Return success (don't block the tool)
    sys.exit(0)

if __name__ == "__main__":
    main()
