#!/usr/bin/env python3
"""
SessionStart Hook: Inject Routing + Knowledge Graph Context

This hook runs at the start of each Claude Code session and:
1. Injects routing directives (from plugin ROUTING.md)
2. Loads all knowledge graphs to provide context to agents

When any subagent is invoked, it will have access to:
1. Routing suggestions for appropriate triad selection
2. Its own triad's knowledge graph (full detail)
3. Related triads' knowledge graphs (summary)
4. Bridge context from previous triads (if applicable)

Hook Type: SessionStart
Configured in: hooks/hooks.json (plugin)

Data Flow:
1. Hook runs at session start
2. Injects routing directives from ROUTING.md
3. Scans .claude/graphs/ for all *_graph.json files
4. Loads and formats graphs as context
5. Outputs context to stdout (Claude Code injects it)
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Add src to path for ExperienceQueryEngine import
repo_root = Path(__file__).parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root / "src"))

from triads.hooks.safe_io import safe_load_json_file  # noqa: E402

def load_graph(graph_path):
    """Load a knowledge graph JSON file."""
    return safe_load_json_file(graph_path, default=None)

def format_graph_summary(graph_data, triad_name):
    """Format a knowledge graph as human-readable context."""
    if not graph_data:
        return f"**{triad_name}**: No graph data yet\n"

    meta = graph_data.get('_meta', {})
    nodes = graph_data.get('nodes', [])
    links = graph_data.get('links', [])

    summary = []
    summary.append(f"**{triad_name.upper()} Knowledge Graph**")
    summary.append(f"Updated: {meta.get('updated_at', 'Unknown')}")
    summary.append(f"Nodes: {len(nodes)}, Edges: {len(links)}")
    summary.append("")

    # Group nodes by type
    nodes_by_type = {}
    for node in nodes:
        node_type = node.get('type', 'Unknown')
        if node_type not in nodes_by_type:
            nodes_by_type[node_type] = []
        nodes_by_type[node_type].append(node)

    # Show key nodes from each type
    for node_type, type_nodes in sorted(nodes_by_type.items()):
        summary.append(f"**{node_type} Nodes** ({len(type_nodes)}):")
        # Show top 5 nodes of each type (by confidence)
        def get_confidence(node):
            conf = node.get('confidence', 0)
            try:
                return float(conf)
            except (ValueError, TypeError):
                return 0.0
        top_nodes = sorted(type_nodes, key=get_confidence, reverse=True)[:5]
        for node in top_nodes:
            label = node.get('label', node.get('id', 'Unknown'))
            confidence = get_confidence(node)
            description = node.get('description', '')[:80]  # Truncate long descriptions
            summary.append(f"  • {label} (confidence: {confidence:.2f})")
            if description:
                summary.append(f"    {description}")
        if len(type_nodes) > 5:
            summary.append(f"  ... and {len(type_nodes) - 5} more")
        summary.append("")

    # Show key uncertainties (important for agents to address)
    uncertainties = [n for n in nodes if n.get('type') == 'Uncertainty']
    if uncertainties:
        summary.append("**⚠️  Known Uncertainties:**")
        for unc in uncertainties[:3]:  # Top 3 uncertainties
            label = unc.get('label', 'Unknown')
            desc = unc.get('description', '')
            summary.append(f"  • {label}")
            if desc:
                summary.append(f"    {desc}")
        if len(uncertainties) > 3:
            summary.append(f"  ... and {len(uncertainties) - 3} more")
        summary.append("")

    return "\n".join(summary)

def load_all_graphs():
    """Load all knowledge graphs from .claude/graphs/."""
    # Try relative path first (works when CWD is project directory)
    graphs_dir = Path('.claude/graphs')

    # If not found, try PWD environment variable (fallback for hooks)
    if not graphs_dir.exists():
        pwd = os.environ.get('PWD')
        if pwd:
            graphs_dir = Path(pwd) / '.claude/graphs'

    if not graphs_dir.exists():
        return []

    graphs = []
    for graph_file in graphs_dir.glob('*_graph.json'):
        # Extract triad name from filename (e.g., "discovery_graph.json" -> "discovery")
        triad_name = graph_file.stem.replace('_graph', '')
        graph_data = load_graph(graph_file)
        if graph_data:
            graphs.append({
                'triad': triad_name,
                'data': graph_data,
                'path': str(graph_file)
            })

    return graphs

def load_bridge_contexts():
    """Load bridge context files (compressed context from previous triads)."""
    # Try relative path first (works when CWD is project directory)
    graphs_dir = Path('.claude/graphs')

    # If not found, try PWD environment variable (fallback for hooks)
    if not graphs_dir.exists():
        pwd = os.environ.get('PWD')
        if pwd:
            graphs_dir = Path(pwd) / '.claude/graphs'

    if not graphs_dir.exists():
        return []

    bridges = []
    for bridge_file in graphs_dir.glob('bridge_*.json'):
        bridge_data = safe_load_json_file(bridge_file, default=None)
        if bridge_data is not None:
            bridges.append({
                'file': bridge_file.name,
                'data': bridge_data
            })

    return bridges

def load_critical_knowledge():
    """
    Load CRITICAL priority process knowledge for display at session start.

    Returns:
        List of critical knowledge items
    """
    try:
        from triads.km.experience_query import ExperienceQueryEngine

        # Determine graphs directory
        graphs_dir = Path('.claude/graphs')
        if not graphs_dir.exists():
            pwd = os.environ.get('PWD')
            if pwd:
                graphs_dir = Path(pwd) / '.claude/graphs'

        if not graphs_dir.exists():
            return []

        # Query for CRITICAL knowledge
        engine = ExperienceQueryEngine(base_dir=graphs_dir.parent)
        critical_items = engine.get_critical_knowledge()

        return critical_items
    except Exception:
        # If import fails or any error, silently return empty list
        return []

def format_critical_knowledge(critical_items):
    """
    Format CRITICAL priority knowledge for session start display.

    Args:
        critical_items: List of ProcessKnowledge objects

    Returns:
        str: Formatted critical knowledge section
    """
    if not critical_items:
        return ""

    output = []
    output.append("=" * 80)
    output.append("# ⚠️  CRITICAL LESSONS LEARNED")
    output.append("=" * 80)
    output.append("")
    output.append("**The following CRITICAL lessons were learned from previous mistakes:**")
    output.append("")

    for i, item in enumerate(critical_items[:5], 1):  # Show top 5 CRITICAL items
        output.append(f"## {i}. {item.label}")
        output.append(f"**Priority**: {item.priority}")
        output.append(f"**Type**: {item.process_type}")
        output.append(f"**Triad**: {item.triad}")

        # Format content based on type
        if item.process_type == 'checklist' and 'checklist' in item.content:
            output.append("")
            output.append("**Checklist**:")
            for check_item in item.content['checklist']:
                required = "🔴 REQUIRED" if check_item.get('required') else "🟡 Optional"
                file_ref = f" ({check_item.get('file', '')})" if check_item.get('file') else ""
                output.append(f"  □ {check_item['item']}{file_ref} — {required}")

        elif item.process_type == 'warning' and 'warning' in item.content:
            warning = item.content['warning']
            output.append("")
            output.append(f"**⚠️  Warning**: {warning.get('condition', '')}")
            output.append(f"**Consequence**: {warning.get('consequence', '')}")
            output.append(f"**Prevention**: {warning.get('prevention', '')}")

        elif item.process_type == 'pattern' and 'pattern' in item.content:
            pattern = item.content['pattern']
            output.append("")
            output.append(f"**When**: {pattern.get('when', '')}")
            output.append(f"**Then**: {pattern.get('then', '')}")
            output.append(f"**Rationale**: {pattern.get('rationale', '')}")

        # Show trigger conditions
        if item.content.get('trigger_conditions'):
            triggers = item.content['trigger_conditions']
            trigger_parts = []
            if triggers.get('tool_names'):
                trigger_parts.append(f"Tools: {', '.join(triggers['tool_names'])}")
            if triggers.get('file_patterns'):
                trigger_parts.append(f"Files: {', '.join(triggers['file_patterns'][:2])}")
            if triggers.get('action_keywords'):
                trigger_parts.append(f"Keywords: {', '.join(triggers['action_keywords'][:3])}")

            if trigger_parts:
                output.append("")
                output.append(f"**Applies when**: {' | '.join(trigger_parts)}")

        output.append("")
        output.append("-" * 80)
        output.append("")

    output.append("**💡 TIP**: Review these lessons before starting work to avoid repeating mistakes.")
    output.append("")
    output.append("=" * 80)
    output.append("")

    return "\n".join(output)

def load_project_settings():
    """
    Load project settings.json if exists.

    Returns:
        Dict or None: Settings data
    """
    # Try relative path first (works when CWD is project directory)
    settings_file = Path('.claude/settings.json')

    # If not found, try PWD environment variable (fallback for hooks)
    if not settings_file.exists():
        pwd = os.environ.get('PWD')
        if pwd:
            settings_file = Path(pwd) / '.claude/settings.json'

    return safe_load_json_file(settings_file, default=None)

def generate_routing_from_settings(settings):
    """
    Generate routing context from settings.json.

    Args:
        settings: Parsed settings.json

    Returns:
        str: Routing context for Claude
    """
    system_name = settings.get('system_name', 'Custom Triad System')
    triads = settings.get('triads', [])
    usage = settings.get('usage', {})

    if not triads:
        return None

    # Entry point (first triad)
    entry_triad = triads[0]

    routing = []
    routing.append(f"# ⚡ {system_name.upper()} ROUTING\n")
    routing.append("**CRITICAL DIRECTIVE**: This project uses a custom triad system.\n")
    routing.append(f"**System purpose**: {settings.get('description', system_name)}\n")

    # List triads
    routing.append("## Available Triads\n")
    for i, triad in enumerate(triads, 1):
        routing.append(f"### {i}. {triad['name'].replace('_', ' ').title()}")
        routing.append(f"**Description**: {triad['description']}")

        if i == 1:
            routing.append(f"**Entry Point**: User invokes this triad")
            routing.append(f"**Command**: `Start {triad['name']}: [description]`")
        else:
            routing.append(f"**Auto-invoked**: Runs automatically after previous triad")
        routing.append("")

    # Usage pattern
    routing.append("## How to Use\n")
    if 'start_command' in usage:
        routing.append(f"**Start command**: `{usage['start_command']}`\n")
    if 'example' in usage:
        routing.append(f"**Example**: `{usage['example']}`\n")

    # Routing logic with explicit recognition
    routing.append("## ⚠️ AUTOMATIC ROUTING - READ CAREFULLY\n")
    routing.append(f"**This project has a custom triad system for**: {settings.get('description', system_name)}\n")
    routing.append(f"\n**CRITICAL**: When a user message relates to {system_name.lower()}, you MUST invoke the triad system.\n")

    # Generate recognition patterns from system name and description
    routing.append(f"\n**Recognize these user statements as triggers**:\n")
    routing.append(f"- Questions or concerns about topics relevant to this system\n")
    routing.append(f"- Requests for help, information, or research on related topics\n")
    routing.append(f"- ANY statement that matches the system's purpose\n")

    routing.append(f"\n**Example user statements that should trigger routing**:\n")
    if 'example' in usage:
        # Extract a simpler version of the example
        example = usage['example']
        # Try to extract just the user question part
        if ':' in example:
            example = example.split(':', 1)[1].strip()
        routing.append(f'- "{example}"\n')
        # Generate variations
        routing.append(f'- "I have a question about..." (related topic)\n')
        routing.append(f'- "I need help with..." (related topic)\n')
        routing.append(f'- "Can you tell me about..." (related topic)\n')

    routing.append(f"\n**How to invoke (REQUIRED FORMAT)**:\n")
    routing.append(f"```")
    routing.append(f"Start {entry_triad['name']}: [user's exact question or concern]")
    routing.append(f"```\n")
    routing.append(f"**Do NOT**:\n")
    routing.append(f"- Respond as a generic assistant\n")
    routing.append(f"- Say you can't help\n")
    routing.append(f"- Redirect them elsewhere\n")
    routing.append(f"\n**Do**:\n")
    routing.append(f"- IMMEDIATELY invoke the triad with their question\n")
    routing.append(f"- Let the specialized agents handle it\n")

    # Workflow
    if 'workflow' in usage:
        routing.append("## Workflow\n")
        for step in usage['workflow']:
            routing.append(f"- {step}")
        routing.append("")

    return '\n'.join(routing)

def load_routing_directives():
    """
    Load routing directives from plugin or project.

    Priority:
    1. Project-level .claude/ROUTING.md (if exists)
    2. Plugin ROUTING.md (default)

    Returns:
        str: Routing content, or None if not found
    """
    # Check for project-level override (try relative path first)
    project_routing = Path('.claude/ROUTING.md')

    # If not found, try PWD environment variable (fallback for hooks)
    if not project_routing.exists():
        pwd = os.environ.get('PWD')
        if pwd:
            project_routing = Path(pwd) / '.claude/ROUTING.md'

    if project_routing.exists():
        return project_routing.read_text()

    # Fall back to plugin default
    plugin_root = os.environ.get('CLAUDE_PLUGIN_ROOT')
    if plugin_root:
        plugin_routing = Path(plugin_root) / 'ROUTING.md'
        if plugin_routing.exists():
            return plugin_routing.read_text()

    return None


def load_workflow_state():
    """
    Load workflow state to check for in-progress work.

    Returns:
        dict or None: Workflow state if available
    """
    try:
        from triads.workflow_enforcement.state_manager import WorkflowStateManager

        manager = WorkflowStateManager()
        state = manager.load_state()

        # Only return state if it has meaningful content
        if state and (state.get("current_phase") or state.get("completed_triads")):
            return state
    except Exception:
        # If workflow enforcement not available or errors, return None
        pass

    return None


def get_next_phase(current_phase):
    """
    Determine the next phase in the triad sequence.

    Args:
        current_phase: Current phase name

    Returns:
        str or None: Next phase name
    """
    phase_sequence = [
        "idea-validation",
        "design",
        "implementation",
        "garden-tending",
        "deployment"
    ]

    try:
        current_idx = phase_sequence.index(current_phase)
        if current_idx < len(phase_sequence) - 1:
            return phase_sequence[current_idx + 1]
    except (ValueError, IndexError):
        pass

    return None


def format_workflow_resumption(state):
    """
    Format workflow state as resumption prompt for user.

    Args:
        state: Workflow state dictionary

    Returns:
        str: Formatted resumption prompt
    """
    if not state:
        return ""

    current_phase = state.get("current_phase")
    completed_triads = state.get("completed_triads", [])
    last_transition = state.get("last_transition")
    metadata = state.get("metadata", {})

    # If no active phase, don't show resumption
    if not current_phase:
        return ""

    output = []
    output.append("=" * 80)
    output.append("# 🔄 WORKFLOW CONTINUITY")
    output.append("=" * 80)
    output.append("")

    # Check if current phase is completed
    if current_phase in completed_triads:
        # Phase complete - suggest next phase
        next_phase = get_next_phase(current_phase)

        output.append(f"✅ **{current_phase.replace('-', ' ').title()} Complete**")
        output.append("")

        if last_transition:
            output.append(f"Completed: {last_transition}")
            output.append("")

        if next_phase:
            output.append(f"**Ready for next phase: {next_phase.replace('-', ' ').title()}**")
            output.append("")
            output.append(f"To continue the workflow:")
            output.append(f"```")
            output.append(f"Start {next_phase}: [description of work]")
            output.append(f"```")
            output.append("")
            output.append("Or start new work with a different triad.")
        else:
            output.append("**Workflow complete!**")
            output.append("")
            output.append("All phases done. Ready to start new work.")
    else:
        # Phase in progress - suggest resumption
        output.append(f"📋 **Work in Progress: {current_phase.replace('-', ' ').title()}**")
        output.append("")

        if last_transition:
            output.append(f"Started: {last_transition}")
            output.append("")

        # Show what's been completed so far
        if completed_triads:
            output.append("**Completed phases:**")
            for phase in completed_triads:
                output.append(f"  ✓ {phase.replace('-', ' ').title()}")
            output.append("")

        # Show metadata if available (files changed, etc)
        if metadata:
            if metadata.get("files_changed"):
                output.append(f"**Modified files:** {metadata['files_changed']}")
            if metadata.get("loc_changed"):
                output.append(f"**Lines changed:** {metadata['loc_changed']}")
            if metadata:
                output.append("")

        output.append(f"**Options:**")
        output.append(f"1. Continue {current_phase}: Resume work in this phase")
        output.append(f"2. Complete and move forward: Finish {current_phase} and proceed to next phase")
        output.append(f"3. Start new work: Begin a different feature/task")
        output.append("")

        next_phase = get_next_phase(current_phase)
        if next_phase:
            output.append(f"**Next phase will be:** {next_phase.replace('-', ' ').title()}")
            output.append("")

    output.append("=" * 80)
    output.append("")

    return "\n".join(output)


def main():
    """Generate routing + knowledge graph context for session."""

    # Build context output
    output = []

    # === WORKFLOW CONTINUITY (FIRST - MOST IMPORTANT) ===

    workflow_state = load_workflow_state()
    if workflow_state:
        resumption_prompt = format_workflow_resumption(workflow_state)
        if resumption_prompt:
            output.append(resumption_prompt)

    # === ROUTING DIRECTIVES ===

    # Priority 1: Generate routing from settings.json (if exists)
    routing_content = None
    settings = load_project_settings()
    if settings:
        routing_content = generate_routing_from_settings(settings)

    # Priority 2: Fall back to .claude/ROUTING.md or plugin ROUTING.md
    if not routing_content:
        routing_content = load_routing_directives()

    # Output routing if we have it
    if routing_content:
        output.append("=" * 80)
        output.append(routing_content)
        output.append("=" * 80)
        output.append("")

    # === KNOWLEDGE GRAPHS ===

    # Load all graphs
    graphs = load_all_graphs()
    bridges = load_bridge_contexts()

    # If no graphs exist yet, output minimal context
    if not graphs and not bridges:
        output.append("# 📊 Knowledge Graph System Active\n")
        output.append("No knowledge graphs exist yet. As agents work, they will create and update graphs.")
        output.append("\nAgents should use [GRAPH_UPDATE] blocks to document findings.\n")

        # Output in JSON format for Claude Code
        hook_output = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": "\n".join(output)
            }
        }
        print(json.dumps(hook_output))
        return

    output.append("=" * 80)
    output.append("# 📊 KNOWLEDGE GRAPH CONTEXT")
    output.append("=" * 80)
    output.append("")
    output.append(f"**Session started**: {datetime.now().isoformat()}")
    output.append(f"**Available graphs**: {len(graphs)}")
    output.append("")

    # Add each graph's summary
    if graphs:
        output.append("## Triad Knowledge Graphs\n")
        for graph_info in sorted(graphs, key=lambda g: g['triad']):
            output.append(format_graph_summary(graph_info['data'], graph_info['triad']))
            output.append("-" * 80)
            output.append("")

    # Add CRITICAL learned knowledge (from experience system)
    critical_knowledge = load_critical_knowledge()
    if critical_knowledge:
        critical_section = format_critical_knowledge(critical_knowledge)
        if critical_section:
            output.append(critical_section)

    # Add calibration warnings for uncertain lessons (Phase 3: Confidence-based learning)
    uncertain_lessons = [item for item in critical_knowledge if item.needs_validation]
    if uncertain_lessons:
        output.append("=" * 80)
        output.append("# ⚠️  CALIBRATION WARNING")
        output.append("=" * 80)
        output.append("")
        output.append(f"**{len(uncertain_lessons)} lesson(s) need validation** (confidence < 0.70):")
        output.append("")
        for lesson in uncertain_lessons:
            conf_pct = int(lesson.confidence * 100)
            output.append(f"  • {lesson.label}")
            output.append(f"    Confidence: {conf_pct}% | Triad: {lesson.triad}")
            output.append(f"    This lesson is uncertain and may need validation.")
            output.append("")
        output.append("**Actions**:")
        output.append("- If a lesson proves correct during use, it will gain confidence")
        output.append("- If a lesson proves incorrect, mark it with `/knowledge-contradict`")
        output.append("- If you can validate a lesson, use `/knowledge-validate`")
        output.append("")
        output.append("=" * 80)
        output.append("")

    # Add bridge contexts (compressed context from previous triads)
    if bridges:
        output.append("## 🌉 Bridge Context\n")
        for bridge in bridges:
            output.append(f"**{bridge['file']}**")
            bridge_data = bridge['data']
            output.append(f"  Source: {bridge_data.get('source_triad', 'Unknown')}")
            output.append(f"  Target: {bridge_data.get('target_triad', 'Unknown')}")
            output.append(f"  Created: {bridge_data.get('created_at', 'Unknown')}")
            output.append(f"  Nodes: {len(bridge_data.get('compressed_nodes', []))}")
            output.append("")

    output.append("=" * 80)
    output.append("")
    output.append("**Note for Agents:**")
    output.append("- Use [GRAPH_UPDATE] blocks to add/update nodes and edges")
    output.append("- Include confidence scores (0.0-1.0) for all claims")
    output.append("- Cite evidence (file:line or source)")
    output.append("- Escalate uncertainties as Uncertainty nodes")
    output.append("")
    output.append("=" * 80)
    output.append("")

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
