#!/usr/bin/env python3
"""
SessionStart Hook: Inject Routing + Knowledge Graph Context + Pending Handoffs + Workspace Resumption

This hook runs at the start of each Claude Code session and injects:
1. Workspace resumption prompt (if paused workspace detected)
2. Pending triad handoff instructions (if any)
3. Routing directives (from plugin ROUTING.md)
4. Knowledge graph context from all triads

Refactored to use Tool Abstraction Layer (Phase 7).
Phase 3 (Workspace Resumability): Added auto-resume detection

Hook Type: SessionStart
Configured in: hooks/hooks.json (plugin)

Previous implementation: 625 lines with embedded graph loading logic
Current implementation: ~100 lines using KnowledgeTools + handoff + workspace resumption
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path

# Setup import paths using shared utility
from setup_paths import setup_import_paths
setup_import_paths()

# Import tool layer and common utilities
from triads.tools.knowledge import KnowledgeTools  # noqa: E402
from common import get_project_dir, output_hook_result  # noqa: E402
from resumption_manager import should_auto_resume, generate_resumption_prompt  # noqa: E402
from event_capture_utils import capture_hook_execution, capture_hook_error  # noqa: E402
from constants import PLUGIN_VERSION  # noqa: E402


def check_workspace_resumption():
    """
    Check if there's a paused workspace that should auto-resume.

    Returns:
        tuple: (workspace_id, prompt) if resumable, (None, None) otherwise
    """
    try:
        if not should_auto_resume():
            return None, None

        # Get active workspace from .active marker
        from workspace_manager import get_active_workspace
        workspace_id = get_active_workspace()

        if not workspace_id:
            return None, None

        # Generate resumption prompt
        prompt = generate_resumption_prompt(workspace_id)

        if prompt:
            print(f"⏸️  Paused workspace detected: {workspace_id}", file=sys.stderr)
            return workspace_id, prompt

        return None, None

    except Exception as e:
        print(f"⚠️  Error checking workspace resumption: {e}", file=sys.stderr)
        return None, None


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
    """Generate session context using KnowledgeTools + check pending handoffs + workspace resumption."""
    start_time = time.time()

    try:
        # Priority 1: Check for paused workspace resumption
        workspace_id, resumption_prompt = check_workspace_resumption()

        if workspace_id and resumption_prompt:
            # Highest priority: Show workspace resumption prompt
            output_hook_result("SessionStart", resumption_prompt)

            # Capture successful execution event
            capture_hook_execution(
                "session_start",
                start_time,
                {
                    "source": "workspace_resumption",
                    "workspace_resumed": workspace_id,
                    "has_pending_handoff": False
                },
                workspace_id=workspace_id
            )
            return

        # Priority 2: Check for pending handoff
        pending_handoff = check_pending_handoff()

        if pending_handoff:
            # Show handoff instruction
            handoff_context = format_handoff_instruction(pending_handoff)
            print(f"🔗 Pending handoff detected: {pending_handoff['next_triad']}", file=sys.stderr)
            output_hook_result("SessionStart", handoff_context)

            # Capture successful execution event
            capture_hook_execution(
                "session_start",
                start_time,
                {
                    "source": "pending_handoff",
                    "workspace_resumed": None,
                    "has_pending_handoff": True,
                    "next_triad": pending_handoff['next_triad'],
                    "request_type": pending_handoff.get('request_type')
                },
                workspace_id=workspace_id if workspace_id else None
            )
            return

        # Priority 3: Normal session start (no workspace resumption, no handoff)
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

        # Capture successful execution event
        from workspace_manager import get_active_workspace
        active_workspace = get_active_workspace()

        capture_hook_execution(
            "session_start",
            start_time,
            {
                "source": "normal_session",
                "workspace_resumed": None,
                "has_pending_handoff": False,
                "knowledge_context_loaded": result.success
            },
            workspace_id=active_workspace
        )

    except Exception as e:
        # Capture error event
        capture_hook_error(
            "session_start",
            start_time,
            e
        )
        raise  # Re-raise to preserve existing error handling


if __name__ == "__main__":
    main()
