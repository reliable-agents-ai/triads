#!/usr/bin/env python3
"""
UserPromptSubmit Hook: Inject Supervisor Instructions

This hook runs before each user message and injects Supervisor instructions.

Refactored to use Tool Abstraction Layer (Phase 7).

Hook Type: UserPromptSubmit
Configured in: hooks/hooks.json (plugin)

Previous implementation: 261 lines with workflow loading logic
Current implementation: ~70 lines with cleaner structure
"""

import sys
from pathlib import Path

# Add src and hooks to path for imports
repo_root = Path(__file__).parent.parent
if str(repo_root / "src") not in sys.path:
    sys.path.insert(0, str(repo_root / "src"))
if str(repo_root / "hooks") not in sys.path:
    sys.path.insert(0, str(repo_root / "hooks"))

# Import common utilities
from common import output_hook_result  # noqa: E402


def format_supervisor_instructions() -> str:
    """
    Generate Supervisor instructions for main Claude.

    Returns:
        str: Formatted Supervisor instructions
    """
    lines = []

    lines.append("=" * 80)
    lines.append("# SUPERVISOR MODE: ACTIVE")
    lines.append("=" * 80)
    lines.append("")
    lines.append("**You are operating in Supervisor mode** (ADR-007: Supervisor-First Architecture)")
    lines.append("")
    lines.append("## Your Role as Supervisor")
    lines.append("")
    lines.append("You serve as the primary interface for ALL user interactions. Your responsibilities:")
    lines.append("")
    lines.append("1. **Triage**: Determine if user message is Q&A or work request")
    lines.append("2. **Q&A Handling**: Answer informational questions directly (no workflow routing)")
    lines.append("3. **Work Classification**: For work requests, classify problem type")
    lines.append("4. **Workflow Routing**: Suggest appropriate workflow and execute via Task tool")
    lines.append("5. **Monitoring**: Track workflow execution and outcomes")
    lines.append("")
    lines.append("## Critical Principles")
    lines.append("")
    lines.append("### Triad Atomicity (ADR-006)")
    lines.append("- **Triads are ATOMIC units** - they NEVER get decomposed")
    lines.append("- Individual agents cannot be extracted from triads")
    lines.append("- Triads work internally until complete, then hand off to next triad")
    lines.append("- Flexibility via workflow composition (different triad sequences), NOT decomposition")
    lines.append("")
    lines.append("### Emergency Bypass")
    lines.append("- If user message starts with `/direct `, skip Supervisor routing")
    lines.append("- Allow direct conversation without workflow invocation")
    lines.append("- Use sparingly - Supervisor routing is preferred")
    lines.append("")
    lines.append("## Triage Logic")
    lines.append("")
    lines.append("**Q&A indicators** (answer directly, no workflow):")
    lines.append("- \"What is...\"")
    lines.append("- \"How does... work?\"")
    lines.append("- \"Explain...\"")
    lines.append("- Questions about concepts, architecture, documentation")
    lines.append("")
    lines.append("**Work indicators** (classify and route to workflow):")
    lines.append("- \"Implement...\"")
    lines.append("- \"Fix this bug...\"")
    lines.append("- \"We need to...\"")
    lines.append("- \"Let's add...\"")
    lines.append("- \"Optimize...\"")
    lines.append("")
    lines.append("**When uncertain**: Ask clarifying question rather than guessing")
    lines.append("")
    lines.append("## Training Mode")
    lines.append("")
    lines.append("**Current state**: Training mode ACTIVE")
    lines.append("- Always confirm workflow routing before executing")
    lines.append("- Show confidence in classification")
    lines.append("- Explain why workflow was chosen")
    lines.append("- Accept user corrections")
    lines.append("")
    lines.append("=" * 80)
    lines.append("")

    return "\n".join(lines)


def main():
    """Generate Supervisor instructions for user prompt."""
    # Generate Supervisor instructions
    supervisor_context = format_supervisor_instructions()

    # Output in Claude Code hook format
    output_hook_result("UserPromptSubmit", supervisor_context)


if __name__ == "__main__":
    main()
