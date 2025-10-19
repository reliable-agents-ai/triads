#!/usr/bin/env python3
"""PreToolUse Hook: Experience-Based Learning

Queries knowledge graphs for process knowledge relevant to impending tool use.
Injects checklists, patterns, warnings into agent context BEFORE tool executes.

This hook fires before EVERY tool execution and provides just-in-time
procedural knowledge based on learned experience.

Key Features:
- Early exit for read-only tools (Read, Grep, Glob) to avoid context clutter
- Top 3 most relevant items only (avoid context pollution)
- Priority-weighted relevance (CRITICAL gets 2.0x boost)
- NEVER blocks tool execution (always exits successfully)

Performance:
- Target: < 100ms (query engine is ~0.1ms, formatting is ~1ms)
- Monitored via stderr logging

Security:
- All inputs validated
- Graceful error handling (never fail)
- Always exits 0 (critical for not blocking tools)

Usage:
    This hook is invoked automatically by Claude Code before every tool use.
    Input comes from stdin as JSON, output goes to stdout for context injection.

Example Input (stdin):
    {
        "tool_name": "Write",
        "tool_input": {"file_path": "plugin.json", "content": "..."},
        "cwd": "/path/to/project"
    }

Example Output (stdout):
    ================================================================================
    # EXPERIENCE-BASED KNOWLEDGE
    ================================================================================

    Before using **Write**, consider this learned knowledge:

    ⚠️ CRITICAL: Version Bump File Checklist
    **Priority**: CRITICAL

    **Checklist**:
      □ Update plugin.json version field (.claude-plugin/plugin.json) — REQUIRED
      □ Update marketplace.json plugins[].version (.claude-plugin/marketplace.json) — REQUIRED
      □ Update pyproject.toml project.version (pyproject.toml) — REQUIRED
      □ Add CHANGELOG.md entry (CHANGELOG.md) — REQUIRED

    **Please verify all required items before proceeding.**
    ================================================================================
"""

import json
import sys
from pathlib import Path

# Add src to path for imports
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / "src"))

from triads.hooks.safe_io import safe_load_json_stdin  # noqa: E402

try:
    from triads.km.experience_query import ExperienceQueryEngine
    from triads.km.experience_tracker import ExperienceTracker
except ImportError as e:
    # If import fails, log but don't block
    print(f"Warning: Could not import KM modules: {e}", file=sys.stderr)
    ExperienceQueryEngine = None
    ExperienceTracker = None


# ============================================================================
# Configuration
# ============================================================================

# Read-only tools that don't modify state (early exit to avoid clutter)
READONLY_TOOLS = {"Read", "Grep", "Glob"}

# Maximum number of items to inject (avoid context pollution)
MAX_INJECTION_ITEMS = 3


# ============================================================================
# Formatting Functions
# ============================================================================


def should_inject_for_tool(tool_name: str) -> bool:
    """Check if we should inject knowledge for this tool.

    Early exit for read-only tools to avoid cluttering context with
    knowledge that's not relevant to read operations.

    Args:
        tool_name: Name of tool about to be executed

    Returns:
        True if we should inject knowledge, False to skip
    """
    if not tool_name:
        return False

    # Don't inject for read-only tools
    if tool_name in READONLY_TOOLS:
        return False

    return True


def format_checklist(knowledge) -> str:
    """Format checklist for injection into agent context.

    Creates a visual checklist with checkboxes, priority indicator,
    and file references.

    Args:
        knowledge: ProcessKnowledge object with checklist content

    Returns:
        Formatted checklist text ready for display
    """
    lines = [f"\n⚠️ **{knowledge.priority}: {knowledge.label}**"]
    lines.append(f"**Priority**: {knowledge.priority}")

    # Handle both dict format (with "items" key) and list format
    checklist_data = knowledge.content
    if isinstance(checklist_data, dict):
        items = checklist_data.get("items", [])
    elif isinstance(checklist_data, list):
        items = checklist_data
    else:
        items = []

    if items:
        lines.append("\n**Checklist**:")
        for item in items:
            # Handle both dict and string items
            if isinstance(item, dict):
                item_text = item.get("item", str(item))
                required = item.get("required", False)
                file_ref = item.get("file", "")
            else:
                item_text = str(item)
                required = False
                file_ref = ""

            required_label = "🔴 REQUIRED" if required else "🟡 Optional"
            file_suffix = f" ({file_ref})" if file_ref else ""

            lines.append(f"  □ {item_text}{file_suffix} — {required_label}")

    lines.append("\n**Please verify all required items before proceeding.**\n")
    return "\n".join(lines)


def format_pattern(knowledge) -> str:
    """Format pattern for injection into agent context.

    Creates a "when X, then Y" style guide.

    Args:
        knowledge: ProcessKnowledge object with pattern content

    Returns:
        Formatted pattern text ready for display
    """
    lines = [f"\nℹ️ **{knowledge.priority}: {knowledge.label}**"]

    if knowledge.description:
        lines.append(f"\n{knowledge.description}")

    pattern = knowledge.content
    if isinstance(pattern, dict):
        if "when" in pattern:
            lines.append(f"\n**When**: {pattern['when']}")
        if "then" in pattern:
            lines.append(f"**Then**: {pattern['then']}")
        if "example" in pattern:
            lines.append(f"**Example**: {pattern['example']}")

    return "\n".join(lines)


def format_warning(knowledge) -> str:
    """Format warning for injection into agent context.

    Creates a warning with risk and mitigation guidance.

    Args:
        knowledge: ProcessKnowledge object with warning content

    Returns:
        Formatted warning text ready for display
    """
    lines = [f"\n⚠️ **{knowledge.priority} WARNING: {knowledge.label}**"]

    if knowledge.description:
        lines.append(f"\n{knowledge.description}")

    warning = knowledge.content
    if isinstance(warning, dict):
        if "risk" in warning:
            lines.append(f"\n**Risk**: {warning['risk']}")
        if "mitigation" in warning:
            lines.append(f"**Mitigation**: {warning['mitigation']}")
        if "consequence" in warning:
            lines.append(f"**Consequence**: {warning['consequence']}")

    return "\n".join(lines)


def format_requirement(knowledge) -> str:
    """Format requirement for injection into agent context.

    Creates a requirement statement with rationale.

    Args:
        knowledge: ProcessKnowledge object with requirement content

    Returns:
        Formatted requirement text ready for display
    """
    lines = [f"\nℹ️ **{knowledge.priority} REQUIREMENT: {knowledge.label}**"]

    if knowledge.description:
        lines.append(f"\n{knowledge.description}")

    requirement = knowledge.content
    if isinstance(requirement, dict):
        if "must" in requirement:
            lines.append(f"\n**Must**: {requirement['must']}")
        if "rationale" in requirement:
            lines.append(f"**Rationale**: {requirement['rationale']}")

    return "\n".join(lines)


def format_knowledge_item(knowledge) -> str:
    """Format a knowledge item based on its process_type.

    Dispatches to type-specific formatter.

    Args:
        knowledge: ProcessKnowledge object

    Returns:
        Formatted text ready for injection
    """
    process_type = knowledge.process_type

    if process_type == "checklist":
        return format_checklist(knowledge)
    elif process_type == "pattern":
        return format_pattern(knowledge)
    elif process_type == "warning":
        return format_warning(knowledge)
    elif process_type == "requirement":
        return format_requirement(knowledge)
    else:
        # Generic format
        return f"\nℹ️ **{knowledge.label}**\n{knowledge.description}\n"


# ============================================================================
# Main Hook Logic
# ============================================================================


def main():
    """Main hook entry point.

    Reads tool context from stdin, queries for relevant knowledge,
    formats and outputs to stdout for injection into agent context.

    CRITICAL: This function MUST always exit successfully (exit code 0)
    to avoid blocking tool execution. All errors are caught and logged
    to stderr.
    """
    try:
        # Check if query engine is available
        if ExperienceQueryEngine is None:
            # Can't query without engine, exit silently
            sys.exit(0)

        # Read hook input from stdin
        input_data = safe_load_json_stdin(default={})
        if not input_data:
            # Failed to parse stdin, exit silently
            sys.exit(0)

        # Extract hook parameters
        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})
        cwd = input_data.get("cwd", ".")

        # Early exit if no tool name
        if not tool_name:
            sys.exit(0)

        # Early exit for read-only tools (avoid context clutter)
        if not should_inject_for_tool(tool_name):
            print(f"Early exit for read-only tool: {tool_name}", file=sys.stderr)
            sys.exit(0)

        # Initialize query engine
        try:
            claude_dir = Path(cwd) / ".claude"
            engine = ExperienceQueryEngine(graphs_dir=claude_dir / "graphs")
        except Exception as e:
            print(f"Warning: Could not initialize query engine: {e}", file=sys.stderr)
            sys.exit(0)

        # Query for relevant knowledge
        try:
            relevant_knowledge = engine.query_for_tool_use(
                tool_name=tool_name,
                tool_input=tool_input,
                cwd=cwd
            )
        except Exception as e:
            print(f"Warning: Query failed: {e}", file=sys.stderr)
            sys.exit(0)

        # No relevant knowledge? Exit silently
        if not relevant_knowledge:
            print(f"No relevant knowledge found for {tool_name}", file=sys.stderr)
            sys.exit(0)

        # Limit to top N items (avoid context pollution)
        items_to_inject = relevant_knowledge[:MAX_INJECTION_ITEMS]

        # Record injections for outcome detection (Phase 3: Confidence-based learning)
        if ExperienceTracker is not None:
            try:
                tracker = ExperienceTracker(base_dir=Path(cwd))
                for knowledge in items_to_inject:
                    tracker.record_injection(
                        lesson_id=knowledge.node_id,
                        triad=knowledge.triad,
                        label=knowledge.label,
                        tool_name=tool_name,
                        confidence=knowledge.confidence
                    )
            except Exception as e:
                # Don't block on tracking errors
                print(f"Warning: Failed to record injection: {e}", file=sys.stderr)

        # Format output for injection
        output_lines = ["\n" + "=" * 80]
        output_lines.append("# 🧠 EXPERIENCE-BASED KNOWLEDGE")
        output_lines.append("=" * 80)
        output_lines.append(
            f"\nBefore using **{tool_name}**, consider this learned knowledge:\n"
        )

        # Format each knowledge item
        for knowledge in items_to_inject:
            output_lines.append(format_knowledge_item(knowledge))
            output_lines.append("-" * 80)

        output_lines.append(
            "\n**This knowledge was learned from previous experience.**"
        )
        output_lines.append("="*80 + "\n")

        # Output to stdout (gets injected into agent context)
        print("\n".join(output_lines))

        # Log success to stderr for debugging
        print(
            f"✓ Injected {len(items_to_inject)} knowledge items for {tool_name}",
            file=sys.stderr
        )

    except Exception as e:
        # CRITICAL: Log error but NEVER block tool execution
        print(f"Experience injection error: {e}", file=sys.stderr)

    finally:
        # CRITICAL: ALWAYS exit successfully (never block tools)
        sys.exit(0)


if __name__ == "__main__":
    main()
