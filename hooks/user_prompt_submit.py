#!/usr/bin/env python3
"""
UserPromptSubmit Hook: Inject Supervisor Instructions

This hook runs before each user message and injects Supervisor instructions
that guide main Claude to:
1. Triage Q&A vs. work requests
2. For work: classify problem type and suggest appropriate workflow
3. Execute workflows via Task tool

Hook Type: UserPromptSubmit
Configured in: hooks/hooks.json (plugin)

Supervisor Architecture (ADR-007):
- ALL user interactions route through Supervisor logic
- Supervisor is main Claude with specific prompting
- Workflows compose atomic triads (never decompose triads)
- Emergency bypass: User can prefix message with "/direct " to skip routing

Data Flow:
1. User submits message
2. Hook fires before Claude sees it
3. Hook injects Supervisor instructions
4. Main Claude follows Supervisor logic
5. Routes to appropriate workflow or answers directly
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Add paths for imports - plugin-aware
plugin_root = os.environ.get('CLAUDE_PLUGIN_ROOT')
if plugin_root:
    sys.path.insert(0, str(Path(plugin_root) / "src"))
else:
    repo_root = Path(__file__).parent.parent
    sys.path.insert(0, str(repo_root / "src"))

from triads.hooks.safe_io import safe_load_json_file  # noqa: E402


def load_workflow_library():
    """
    Load workflow library from .claude/workflows/proven/*.yaml

    Returns:
        list: List of workflow definitions
    """
    # Find project root
    workflows_dir = Path('.claude/workflows/proven')
    if not workflows_dir.exists():
        pwd = os.environ.get('PWD')
        if pwd:
            workflows_dir = Path(pwd) / '.claude/workflows/proven'

    if not workflows_dir.exists():
        return []

    workflows = []
    # For now, return empty list - workflows will be created in Phase 2
    # TODO: Load YAML workflow definitions once they exist

    return workflows


def format_supervisor_instructions(workflows):
    """
    Generate Supervisor instructions for main Claude.

    Args:
        workflows: List of available workflow definitions

    Returns:
        str: Formatted Supervisor instructions
    """
    output = []

    output.append("=" * 80)
    output.append("# 🎯 SUPERVISOR MODE: ACTIVE")
    output.append("=" * 80)
    output.append("")
    output.append("**You are operating in Supervisor mode** (ADR-007: Supervisor-First Architecture)")
    output.append("")
    output.append("## Your Role as Supervisor")
    output.append("")
    output.append("You serve as the primary interface for ALL user interactions. Your responsibilities:")
    output.append("")
    output.append("1. **Triage**: Determine if user message is Q&A or work request")
    output.append("2. **Q&A Handling**: Answer informational questions directly (no workflow routing)")
    output.append("3. **Work Classification**: For work requests, classify problem type")
    output.append("4. **Workflow Routing**: Suggest appropriate workflow and execute via Task tool")
    output.append("5. **Monitoring**: Track workflow execution and outcomes")
    output.append("")
    output.append("## Critical Principles")
    output.append("")
    output.append("### Triad Atomicity (ADR-006)")
    output.append("- **Triads are ATOMIC units** - they NEVER get decomposed")
    output.append("- Individual agents cannot be extracted from triads")
    output.append("- Triads work internally until complete, then hand off to next triad")
    output.append("- Flexibility via workflow composition (different triad sequences), NOT decomposition")
    output.append("")
    output.append("### Workflow Composition")
    output.append("- Workflows are sequences of intact triads")
    output.append("- Same triad can appear in multiple workflows")
    output.append("- Optimal workflow size: 2-5 triads (6-15 agents)")
    output.append("- Based on military organizational patterns (squad=9, ODA=12)")
    output.append("")
    output.append("### Emergency Bypass")
    output.append("- If user message starts with `/direct `, skip Supervisor routing")
    output.append("- Allow direct conversation without workflow invocation")
    output.append("- Use sparingly - Supervisor routing is preferred")
    output.append("")

    if workflows:
        output.append("## Available Workflows")
        output.append("")
        for workflow in workflows:
            output.append(f"### {workflow.get('name', 'Unknown')}")
            output.append(f"**Problem type**: {workflow.get('problem_type', 'unknown')}")
            output.append(f"**Description**: {workflow.get('description', '')}")
            output.append(f"**Indicators**: {', '.join(workflow.get('problem_indicators', []))}")
            output.append(f"**Triads**: {' → '.join(workflow.get('triads', []))}")
            output.append(f"**When to use**: {workflow.get('when_to_use', '')}")
            output.append("")
    else:
        output.append("## Current State: Workflow Library Not Yet Created")
        output.append("")
        output.append("**Phase 1 Status**: Supervisor core implementation in progress")
        output.append("**Next Phase**: Phase 2 will create workflow library (5 proven workflows)")
        output.append("")
        output.append("For now, use existing triad routing:")
        output.append("- Bug/issue → investigation needed")
        output.append("- New feature idea → `Start Idea Validation: [idea]`")
        output.append("- Architecture decision → `Start Design: [feature]`")
        output.append("- Implementation work → `Start Implementation: [feature]`")
        output.append("- Code cleanup → `Start Garden Tending: [scope]`")
        output.append("- Release → `Start Deployment: v[version]`")
        output.append("")

    output.append("## Triage Logic")
    output.append("")
    output.append("**Q&A indicators** (answer directly, no workflow):")
    output.append("- \"What is...\"")
    output.append("- \"How does... work?\"")
    output.append("- \"Explain...\"")
    output.append("- \"Can you tell me about...\"")
    output.append("- Questions about concepts, architecture, documentation")
    output.append("")
    output.append("**Work indicators** (classify and route to workflow):")
    output.append("- \"Implement...\"")
    output.append("- \"Fix this bug...\"")
    output.append("- \"We need to...\"")
    output.append("- \"Let's add...\"")
    output.append("- \"There's an error...\"")
    output.append("- \"Optimize...\"")
    output.append("- \"Refactor...\"")
    output.append("- \"Deploy...\"")
    output.append("")
    output.append("**When uncertain**: Ask clarifying question rather than guessing")
    output.append("")
    output.append("## Workflow Invocation Pattern")
    output.append("")
    output.append("When you classify a work request:")
    output.append("")
    output.append("1. **Identify problem type** (bug, feature, performance, refactoring, deployment)")
    output.append("2. **Suggest workflow** with brief explanation")
    output.append("3. **Confirm with user** before invoking (training mode)")
    output.append("4. **Invoke via Task tool** if user approves")
    output.append("")
    output.append("Example:")
    output.append("```")
    output.append("User: 'There's a bug where the router crashes on invalid input'")
    output.append("")
    output.append("You: 'This appears to be a **bug fix** work request. I recommend using")
    output.append("     the bug-fix workflow (investigation -> fixing -> verification).'")
    output.append("     ")
    output.append("     Would you like me to `Start Bug Investigation: Router crash on")
    output.append("     invalid input`?'")
    output.append("")
    output.append("User: 'Yes'")
    output.append("")
    output.append("You: [Use Task tool to invoke bug-investigation-triad]")
    output.append("```")
    output.append("")
    output.append("## Training Mode")
    output.append("")
    output.append("**Current state**: Training mode ACTIVE")
    output.append("- Always confirm workflow routing before executing")
    output.append("- Show confidence in classification")
    output.append("- Explain why workflow was chosen")
    output.append("- Accept user corrections")
    output.append("")
    output.append("**Graduation criteria**: TBD (proposed: 10 successful routings)")
    output.append("")
    output.append("## Important Reminders")
    output.append("")
    output.append("- **Q&A is valid**: Not everything needs a workflow - answer questions directly")
    output.append("- **Context matters**: If already deep in conversation, don't force routing")
    output.append("- **User control**: User can bypass routing with `/direct ` prefix")
    output.append("- **Learn from outcomes**: Track what works, improve routing over time")
    output.append("- **NEVER decompose triads**: Always compose workflows from intact triads")
    output.append("")
    output.append("=" * 80)
    output.append("")

    return "\n".join(output)


def check_emergency_bypass(context):
    """
    Check if user message starts with /direct to bypass Supervisor.

    Args:
        context: Hook context (may contain user message)

    Returns:
        bool: True if bypass detected
    """
    # TODO: Extract user message from context when available
    # For now, return False (no bypass)
    return False


def main():
    """Generate Supervisor instructions for user prompt."""

    # Check for emergency bypass
    # Note: Context structure TBD - may need adjustment when available
    if check_emergency_bypass({}):
        # Output empty context (no Supervisor injection)
        hook_output = {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": ""
            }
        }
        print(json.dumps(hook_output))
        return

    # Load workflow library
    workflows = load_workflow_library()

    # Generate Supervisor instructions
    supervisor_context = format_supervisor_instructions(workflows)

    # Output in Claude Code hook format
    hook_output = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": supervisor_context
        }
    }

    print(json.dumps(hook_output))


if __name__ == "__main__":
    main()
