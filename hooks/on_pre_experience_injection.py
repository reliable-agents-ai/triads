#!/usr/bin/env python3
"""PreToolUse Hook: Unified Dual-Mode Experience-Based Learning

This unified hook intelligently escalates from silent → inject → block based on
knowledge criticality and confidence. It merges the best of v1 (additionalContext)
and v2 (user-style interjections) into a single, context-aware system.

Key Innovation:
- Exit Code 0 + additionalContext JSON: Non-blocking knowledge injection
- Exit Code 2 + stderr: Blocking user-style interjections for CRITICAL mistakes

Decision Logic (Magical Blocking):
Block (exit 2) ONLY if ALL of:
- CRITICAL priority knowledge exists
- Confidence >= 0.85 (learned from strong evidence)
- Risky operation detected:
  * Write/Edit to version files with checklist knowledge
  * Bash commands that are point-of-no-return (git commit, npm publish, rm)
  * Very high confidence (>= 0.95) warnings
- Never blocks safe operations:
  * Read-only tools (Read, Grep, Glob)
  * Safe Bash commands (ls, cat, git status, git diff, etc.)
  * Unknown Bash commands (safe default)

Otherwise: Inject (exit 0) via additionalContext JSON

Philosophy: "Mostly Silent, Rarely Block" - Help without interrupting

Exit Codes:
- 0: Allow tool (with optional additionalContext)
- 2: Block tool and send user-style interjection to Claude

Configuration (ADR-005):
- TRIADS_NO_BLOCK=1: Disable blocking (force inject mode)
- TRIADS_NO_EXPERIENCE=1: Disable all injections
- TRIADS_BLOCK_THRESHOLD=0.85: Minimum confidence for blocking

Performance:
- Target: < 100ms (query engine is ~0.1ms, formatting is ~1ms)
- Monitored via stderr logging

Security:
- All inputs validated
- Graceful error handling (never fail on errors, exit 0)
- Input sanitization (natural language output, no eval/exec)

Usage:
    This hook is invoked automatically by Claude Code before every tool use.
    Input comes from stdin as JSON.
    - Exit 0: Output goes to additionalContext field
    - Exit 2: Output goes to stderr (user interjection)

Example Input (stdin):
    {
        "tool_name": "Write",
        "tool_input": {"file_path": "plugin.json", "content": "..."},
        "cwd": "/path/to/project"
    }

Example Output (Blocking Mode - Exit 2, stderr):
    ⚠️  Hold on - before you write that file, let me remind you about something important:

    **Version Bump File Checklist** - you need to:
      🔴 REQUIRED Update plugin.json version field
                  (.claude-plugin/plugin.json)
      🔴 REQUIRED Update marketplace.json plugins[].version
                  (.claude-plugin/marketplace.json)

    Can you make sure you cover all of these? This has caused issues before.

    (This reminder came from our experience-based learning system)

Example Output (Inject Mode - Exit 0, stdout JSON):
    {"additionalContext": "📚 **Relevant Experience**:\\n\\n• **Version Bump File Checklist** (CRITICAL)\\n  Complete checklist of ALL files...\\n"}
"""

import json
import os
import re
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

# Maximum items in interjection (blocking mode)
MAX_INTERJECTION_ITEMS = 2

# Blocking thresholds (from ADR-002)
BLOCK_CONFIDENCE_THRESHOLD = 0.85
BLOCK_VERY_HIGH_CONFIDENCE_THRESHOLD = 0.95

# File patterns for high-stakes detection
VERSION_FILE_PATTERNS = [
    "plugin.json",
    "marketplace.json",
    "pyproject.toml",
    "package.json",
    "version.py",
    "setup.py",
]

# ============================================================================
# Bash Command Classification (Magical Blocking)
# ============================================================================

# Safe bash commands - read-only operations that never modify state
SAFE_BASH_PATTERNS = [
    r"^\s*ls\b",
    r"^\s*cat\b",
    r"^\s*head\b",
    r"^\s*tail\b",
    r"^\s*grep\b",
    r"^\s*find\b",
    r"^\s*echo\b",
    r"^\s*pwd\b",
    r"^\s*which\b",
    r"^\s*type\b",
    r"^\s*git\s+status\b",
    r"^\s*git\s+diff\b",
    r"^\s*git\s+log\b",
    r"^\s*git\s+show\b",
    r"^\s*git\s+branch\b",
    r"^\s*npm\s+list\b",
    r"^\s*pip\s+list\b",
    r"^\s*python\s+--version\b",
    r"^\s*node\s+--version\b",
]

# Point-of-no-return bash commands - irreversible or high-risk operations
RISKY_BASH_PATTERNS = [
    r"^\s*rm\b",
    r"^\s*mv\b",
    r"^\s*git\s+commit\b",
    r"^\s*git\s+push\b",
    r"^\s*git\s+merge\b",
    r"^\s*git\s+rebase\b",
    r"^\s*npm\s+publish\b",
    r"^\s*pip\s+install\b",
    r">\s*[\w/]+",  # Output redirects
    r">>\s*[\w/]+",  # Append redirects
]


def is_safe_bash_command(command: str) -> bool:
    """Check if a Bash command is safe (read-only).

    Args:
        command: The bash command string to check

    Returns:
        True if the command is safe (read-only), False if risky or unknown

    Examples:
        >>> is_safe_bash_command("ls -la")
        True
        >>> is_safe_bash_command("git status")
        True
        >>> is_safe_bash_command("git commit -m 'test'")
        False
        >>> is_safe_bash_command("rm -rf /")
        False
    """
    if not command:
        return False

    # Check if command matches any safe pattern
    for pattern in SAFE_BASH_PATTERNS:
        if re.match(pattern, command):
            return True

    return False


def is_risky_bash_command(command: str) -> bool:
    """Check if a Bash command is risky (point-of-no-return).

    Args:
        command: The bash command string to check

    Returns:
        True if the command is risky (irreversible/dangerous), False otherwise

    Examples:
        >>> is_risky_bash_command("git commit -m 'test'")
        True
        >>> is_risky_bash_command("rm -rf ./temp")
        True
        >>> is_risky_bash_command("ls -la")
        False
    """
    if not command:
        return False

    # Check if command matches any risky pattern
    for pattern in RISKY_BASH_PATTERNS:
        if re.search(pattern, command):
            return True

    return False


# ============================================================================
# Configuration Loading
# ============================================================================


def load_config() -> dict:
    """Load configuration from environment variables.

    Phase 1: Environment variables only
    Phase 2: Will add .claude/config/experience.yml support

    Environment Variables:
        TRIADS_NO_BLOCK=1: Disable blocking mode (force inject)
        TRIADS_NO_EXPERIENCE=1: Disable all experience injection
        TRIADS_BLOCK_THRESHOLD=0.85: Minimum confidence for blocking

    Returns:
        Configuration dictionary with keys:
        - blocking_enabled: bool
        - injection_enabled: bool
        - block_threshold: float
        - very_high_threshold: float
    """
    return {
        "blocking_enabled": os.getenv("TRIADS_NO_BLOCK") != "1",
        "injection_enabled": os.getenv("TRIADS_NO_EXPERIENCE") != "1",
        "block_threshold": float(
            os.getenv("TRIADS_BLOCK_THRESHOLD", str(BLOCK_CONFIDENCE_THRESHOLD))
        ),
        "very_high_threshold": float(
            os.getenv(
                "TRIADS_VERY_HIGH_THRESHOLD",
                str(BLOCK_VERY_HIGH_CONFIDENCE_THRESHOLD),
            )
        ),
    }


# ============================================================================
# Decision Logic (ADR-002)
# ============================================================================


def should_block_for_knowledge(
    knowledge_items,
    tool_name: str,
    tool_input: dict,
    config: dict,
) -> bool:
    """Decide if we should block tool execution (exit 2) vs inject context (exit 0).

    Block if ALL of:
    - CRITICAL priority knowledge exists
    - Confidence >= 0.85 (learned from strong evidence)
    - Risky tool (Write, Edit, Bash - not Read-only)
    - High-stakes context (version files + checklists OR confidence >= 0.95)

    Args:
        knowledge_items: List of ProcessKnowledge objects from query
        tool_name: Name of tool about to be executed
        tool_input: Tool parameters (must include file_path for file tools)
        config: Configuration dictionary from load_config()

    Returns:
        True if we should block and interject (exit 2)
        False if we should inject via additionalContext (exit 0)

    Examples:
        >>> # BLOCK: CRITICAL checklist, high confidence, version file
        >>> should_block_for_knowledge(
        ...     [checklist_node],  # CRITICAL, confidence=0.95
        ...     "Write",
        ...     {"file_path": "plugin.json"},
        ...     {"blocking_enabled": True, "block_threshold": 0.85}
        ... )
        True

        >>> # NO BLOCK: Read-only tool
        >>> should_block_for_knowledge(
        ...     [checklist_node],  # CRITICAL, confidence=0.95
        ...     "Read",
        ...     {"file_path": "plugin.json"},
        ...     {"blocking_enabled": True, "block_threshold": 0.85}
        ... )
        False

        >>> # NO BLOCK: Configuration disabled
        >>> should_block_for_knowledge(
        ...     [checklist_node],  # CRITICAL, confidence=0.95
        ...     "Write",
        ...     {"file_path": "plugin.json"},
        ...     {"blocking_enabled": False, "block_threshold": 0.85}
        ... )
        False
    """
    # Check if blocking is enabled in config
    if not config.get("blocking_enabled", True):
        return False

    if not knowledge_items:
        return False

    # Never block read-only tools
    if tool_name in READONLY_TOOLS:
        return False

    # MAGICAL BLOCKING: Parse Bash commands for intent
    if tool_name == "Bash":
        command = tool_input.get("command", "")

        # Never block safe read-only commands
        if is_safe_bash_command(command):
            return False

        # Only block if command is explicitly risky (point-of-no-return)
        if not is_risky_bash_command(command):
            # Unknown command - default to inject (don't block)
            return False

        # If we get here, it's a risky command - continue with blocking checks

    # Check for CRITICAL knowledge
    critical = [k for k in knowledge_items if k.priority == "CRITICAL"]
    if not critical:
        return False

    # High confidence threshold
    block_threshold = config.get("block_threshold", BLOCK_CONFIDENCE_THRESHOLD)
    high_confidence = [k for k in critical if k.confidence >= block_threshold]
    if not high_confidence:
        return False

    # High-stakes context detection
    file_path = tool_input.get("file_path", "")

    # Pattern 1: Version files with checklists
    is_version_file = any(
        pattern.lower() in file_path.lower() for pattern in VERSION_FILE_PATTERNS
    )
    is_checklist = any(k.process_type == "checklist" for k in high_confidence)

    if is_version_file and is_checklist:
        return True  # BLOCK: Proven risk pattern

    # Pattern 2: Very high confidence (>= 0.95) on any file
    very_high_threshold = config.get(
        "very_high_threshold", BLOCK_VERY_HIGH_CONFIDENCE_THRESHOLD
    )
    very_high_confidence = [k for k in critical if k.confidence >= very_high_threshold]
    if very_high_confidence:
        return True  # BLOCK: Very strong evidence

    return False  # Don't block otherwise


# ============================================================================
# User-Style Interjection Formatting (ADR-003)
# ============================================================================


def format_as_user_interjection(knowledge_items, tool_name: str) -> str:
    """Format knowledge as natural user interjection.

    Instead of formal warnings, this sounds like a helpful user reminding
    Claude about something important before they make a mistake.

    This is used for BLOCKING mode (exit 2 + stderr).

    Args:
        knowledge_items: List of ProcessKnowledge objects
        tool_name: Name of tool about to be used

    Returns:
        Natural language reminder formatted as user speech

    Example:
        >>> interjection = format_as_user_interjection(
        ...     [checklist_node],
        ...     "Write"
        ... )
        >>> print(interjection)
        ⚠️  Hold on - before you write that file, let me remind you...
    """
    lines = []

    # Natural opening based on priority
    critical = [k for k in knowledge_items if k.priority == "CRITICAL"]

    if critical:
        lines.append(
            f"⚠️  Hold on - before you {tool_name.lower()} that file, "
            f"let me remind you about something important:"
        )
    else:
        lines.append(f"Quick heads up before you {tool_name.lower()}:")

    lines.append("")

    # Format each knowledge item naturally
    for i, knowledge in enumerate(
        knowledge_items[:MAX_INTERJECTION_ITEMS], 1
    ):
        if knowledge.process_type == "checklist":
            lines.append(f"**{knowledge.label}** - you need to:")
            items = knowledge.content.get("items", [])
            for item in items[:5]:  # Limit to first 5
                if isinstance(item, dict):
                    status = "🔴 REQUIRED" if item.get("required") else "• "
                    item_text = item.get("item", str(item))
                    file_ref = item.get("file", "")
                    lines.append(f"  {status} {item_text}")
                    if file_ref:
                        lines.append(f"           ({file_ref})")
                else:
                    lines.append(f"  • {item}")

        elif knowledge.process_type == "warning":
            lines.append(f"**{knowledge.label}**:")
            warning = knowledge.content
            if isinstance(warning, dict):
                if "condition" in warning:
                    lines.append(f"  Condition: {warning['condition']}")
                if "risk" in warning:
                    lines.append(f"  Risk: {warning['risk']}")
                if "consequence" in warning:
                    lines.append(f"  Risk: {warning['consequence']}")
                if "prevention" in warning:
                    lines.append(f"  How to avoid: {warning['prevention']}")
                if "mitigation" in warning:
                    lines.append(f"  How to avoid: {warning['mitigation']}")

        elif knowledge.process_type == "pattern":
            lines.append(f"**{knowledge.label}**: {knowledge.description}")

        elif knowledge.process_type == "requirement":
            lines.append(f"**{knowledge.label}**:")
            requirement = knowledge.content
            if isinstance(requirement, dict):
                if "must" in requirement:
                    lines.append(f"  Requirement: {requirement['must']}")
                if "rationale" in requirement:
                    lines.append(f"  Why: {requirement['rationale']}")

        if i < len(knowledge_items[:MAX_INTERJECTION_ITEMS]):
            lines.append("")

    # Natural closing
    lines.append("")
    if critical:
        lines.append(
            "Can you make sure you cover all of these? "
            "This has caused issues before."
        )
    else:
        lines.append("Just wanted to make sure you're aware of this.")

    lines.append("")
    lines.append("(This reminder came from our experience-based learning system)")

    return "\n".join(lines)


def format_for_additionalcontext(knowledge_items) -> str:
    """Format knowledge for non-blocking additionalContext field.

    Used when knowledge is helpful but not critical enough to block.
    This is INJECT mode (exit 0 + JSON with additionalContext).

    Args:
        knowledge_items: List of ProcessKnowledge objects

    Returns:
        Formatted text for additionalContext JSON field

    Example:
        >>> context = format_for_additionalcontext([checklist_node])
        >>> print(context)
        📚 **Relevant Experience**:

        • **Version Bump File Checklist** (CRITICAL)
          Complete checklist of ALL files...
    """
    lines = ["📚 **Relevant Experience**:", ""]

    for knowledge in knowledge_items[:MAX_INJECTION_ITEMS]:
        lines.append(f"• **{knowledge.label}** ({knowledge.priority})")
        if knowledge.description:
            # Truncate long descriptions
            desc = knowledge.description
            if len(desc) > 100:
                desc = desc[:100] + "..."
            lines.append(f"  {desc}")
        lines.append("")

    return "\n".join(lines)


# ============================================================================
# Legacy Formatting Functions (Backward Compatibility)
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
    """Main hook entry point with unified dual-mode logic.

    Flow:
    1. Load configuration (env vars)
    2. Query for relevant knowledge
    3. Decide: Block (exit 2) or Inject (exit 0)?
    4. If BLOCK: Format as user interjection → stderr → exit 2
    5. If INJECT: Format as additionalContext → stdout JSON → exit 0
    6. If NO knowledge: Exit 0 silently

    CRITICAL: This function MUST handle all errors gracefully.
    On errors, always exit 0 (never block tools on hook failures).
    """
    try:
        # Load configuration
        config = load_config()

        # Check if experience injection is completely disabled
        if not config.get("injection_enabled", True):
            print("Experience injection disabled via TRIADS_NO_EXPERIENCE=1", file=sys.stderr)
            sys.exit(0)

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
        if tool_name in READONLY_TOOLS:
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

        # Record injections for outcome detection (Phase 3: Confidence-based learning)
        if ExperienceTracker is not None:
            try:
                tracker = ExperienceTracker(base_dir=Path(cwd))
                for knowledge in relevant_knowledge:
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

        # ========================================================================
        # DECISION POINT: Block and interject (exit 2) or inject context (exit 0)?
        # ========================================================================
        if should_block_for_knowledge(relevant_knowledge, tool_name, tool_input, config):
            # BLOCKING MODE: Exit 2 + stderr (user-style interjection)
            interjection = format_as_user_interjection(relevant_knowledge, tool_name)
            print(interjection, file=sys.stderr)

            # Log that we blocked
            print(f"\n⚠️  BLOCKED {tool_name} with interjection", file=sys.stderr)

            sys.exit(2)  # EXIT CODE 2: Block tool, send feedback to Claude

        else:
            # INJECT MODE: Exit 0 + additionalContext JSON
            context = format_for_additionalcontext(relevant_knowledge)
            output = {"additionalContext": context}
            print(json.dumps(output))

            # Log non-blocking injection
            print(f"✓ Added context for {tool_name} (non-blocking)", file=sys.stderr)

            sys.exit(0)  # EXIT CODE 0: Allow tool with added context

    except Exception as e:
        # CRITICAL: Never block on errors
        print(f"Experience injection error: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
