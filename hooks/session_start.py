#!/usr/bin/env python3
"""
SessionStart Hook: Inject Routing + Knowledge Graph Context + Pending Handoffs

This hook runs at the start of each Claude Code session and injects:
1. Pending triad handoff instructions (if any)
2. Routing directives (from plugin ROUTING.md)
3. Knowledge graph context from all triads

Refactored to use Tool Abstraction Layer (Phase 7).

Hook Type: SessionStart
Configured in: hooks/hooks.json (plugin)

Previous implementation: 625 lines with embedded graph loading logic
Current implementation: ~80 lines using KnowledgeTools + handoff detection
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Add src and hooks to path for imports
repo_root = Path(__file__).parent.parent
if str(repo_root / "src") not in sys.path:
    sys.path.insert(0, str(repo_root / "src"))
if str(repo_root / "hooks") not in sys.path:
    sys.path.insert(0, str(repo_root / "hooks"))

# Import tool layer and common utilities
from triads.tools.knowledge import KnowledgeTools  # noqa: E402
from common import get_project_dir, output_hook_result  # noqa: E402


def check_pending_handoff():
    """
    Check if there's a pending triad handoff from previous session.

    Returns:
        dict or None: Handoff data if pending, None otherwise
    """
    pending_file = Path('.claude/.pending_handoff.json')

    if not pending_file.exists():
        return None

    try:
        with open(pending_file, 'r') as f:
            handoff = json.load(f)

        # Check timeout (24 hours)
        timestamp = datetime.fromisoformat(handoff['timestamp'])
        age_hours = (datetime.now() - timestamp).total_seconds() / 3600

        if age_hours > 24:
            # Expired - remove file
            pending_file.unlink()
            print(f"⚠️  Pending handoff expired (age: {age_hours:.1f}h)", file=sys.stderr)
            return None

        return handoff

    except Exception as e:
        print(f"⚠️  Error reading pending handoff: {e}", file=sys.stderr)
        return None


def format_handoff_instruction(handoff):
    """
    Format auto-invoke instruction for pending handoff.

    Args:
        handoff: Handoff data dictionary

    Returns:
        str: Formatted instruction text
    """
    # Load workflow config to get first agent dynamically
    try:
        project_dir = get_project_dir()
        settings_path = project_dir / '.claude' / 'settings.json'

        with open(settings_path, 'r') as f:
            config = json.load(f)

        next_triad = handoff['next_triad']
        triad_config = config.get('triad_system', {}).get('triads', {}).get(next_triad, {})

        # Get first agent from triad config
        agents = triad_config.get('agents', [])
        first_agent = agents[0] if agents else f"{next_triad}-analyst"  # Fallback to convention

    except (FileNotFoundError, json.JSONDecodeError, KeyError, IndexError) as e:
        print(f"⚠️  Could not load workflow config: {e}", file=sys.stderr)
        print(f"   Falling back to naming convention", file=sys.stderr)
        first_agent = f"{handoff['next_triad']}-analyst"

    lines = []
    lines.append("=" * 80)
    lines.append("# 🔗 PENDING TRIAD HANDOFF")
    lines.append("=" * 80)
    lines.append("")
    lines.append(f"**Previous triad handed off to**: {handoff['next_triad']}")
    lines.append(f"**Request type**: {handoff['request_type']}")
    lines.append(f"**Handoff age**: {_format_age(handoff['timestamp'])}")
    lines.append("")
    lines.append("## Handoff Context")
    lines.append("")
    lines.append(handoff['context'])
    lines.append("")
    if handoff.get('knowledge_graph'):
        lines.append(f"**Knowledge Graph**: {handoff['knowledge_graph']}")
    if handoff.get('updated_nodes'):
        lines.append(f"**Updated Nodes**: {', '.join(handoff['updated_nodes'])}")
    lines.append("")
    lines.append("## INSTRUCTION: Auto-Invoke Next Triad")
    lines.append("")
    lines.append("You MUST invoke the next triad to continue the workflow:")
    lines.append("")
    lines.append(f"1. Use Task tool to invoke: **{first_agent}** (first agent in {handoff['next_triad']} triad)")
    lines.append("2. Pass the handoff context above as part of your prompt")
    lines.append("3. After successful invocation, clear the pending handoff file:")
    lines.append("   ```bash")
    lines.append("   rm .claude/.pending_handoff.json")
    lines.append("   ```")
    lines.append("")
    lines.append("=" * 80)
    lines.append("")

    return "\n".join(lines)


def _format_age(timestamp_str):
    """Format timestamp age in human-readable form."""
    try:
        timestamp = datetime.fromisoformat(timestamp_str)
        delta = datetime.now() - timestamp
        hours = delta.total_seconds() / 3600

        if hours < 1:
            minutes = int(delta.total_seconds() / 60)
            return f"{minutes} minutes ago"
        elif hours < 24:
            return f"{int(hours)} hours ago"
        else:
            days = int(hours / 24)
            return f"{days} days ago"
    except:
        return "unknown"


def main():
    """Generate session context using KnowledgeTools + check pending handoffs."""
    # Check for pending handoff first
    pending_handoff = check_pending_handoff()

    if pending_handoff:
        # Priority: Show handoff instruction
        handoff_context = format_handoff_instruction(pending_handoff)
        print(f"🔗 Pending handoff detected: {pending_handoff['next_triad']}", file=sys.stderr)
        output_hook_result("SessionStart", handoff_context)
        return

    # No pending handoff - normal session start
    # Get project directory from environment
    project_dir = str(get_project_dir())

    # Use KnowledgeTools.get_session_context() instead of 600 lines of logic
    result = KnowledgeTools.get_session_context(project_dir)

    # Extract context from ToolResult
    if result.success:
        context = result.content[0]["text"]
    else:
        # Gracefully handle errors
        context = f"Error loading session context: {result.error}"

    # Output in Claude Code hook format
    output_hook_result("SessionStart", context)


if __name__ == "__main__":
    main()
