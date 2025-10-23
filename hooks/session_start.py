#!/usr/bin/env python3
"""
SessionStart Hook: Inject Routing + Knowledge Graph Context

This hook runs at the start of each Claude Code session and injects:
1. Routing directives (from plugin ROUTING.md)
2. Knowledge graph context from all triads

Refactored to use Tool Abstraction Layer (Phase 7).

Hook Type: SessionStart
Configured in: hooks/hooks.json (plugin)

Previous implementation: 625 lines with embedded graph loading logic
Current implementation: ~50 lines using KnowledgeTools
"""

import sys
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


def main():
    """Generate session context using KnowledgeTools."""
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
