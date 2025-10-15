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

def load_graph(graph_path):
    """Load a knowledge graph JSON file."""
    try:
        with open(graph_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

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
    graphs_dir = Path('.claude/graphs')

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
    graphs_dir = Path('.claude/graphs')

    if not graphs_dir.exists():
        return []

    bridges = []
    for bridge_file in graphs_dir.glob('bridge_*.json'):
        try:
            with open(bridge_file, 'r') as f:
                bridge_data = json.load(f)
                bridges.append({
                    'file': bridge_file.name,
                    'data': bridge_data
                })
        except (FileNotFoundError, json.JSONDecodeError):
            continue

    return bridges

def load_routing_directives():
    """
    Load routing directives from plugin or project.

    Priority:
    1. Project-level .claude/ROUTING.md (if exists)
    2. Plugin ROUTING.md (default)

    Returns:
        str: Routing content, or None if not found
    """
    # Check for project-level override
    project_routing = Path('.claude/ROUTING.md')
    if project_routing.exists():
        return project_routing.read_text()

    # Fall back to plugin default
    plugin_root = os.environ.get('CLAUDE_PLUGIN_ROOT')
    if plugin_root:
        plugin_routing = Path(plugin_root) / 'ROUTING.md'
        if plugin_routing.exists():
            return plugin_routing.read_text()

    return None


def main():
    """Generate routing + knowledge graph context for session."""

    # Build context output
    output = []

    # === ROUTING DIRECTIVES ===
    routing_content = load_routing_directives()
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
        print("\n".join(output))
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

    # Output to stdout (Claude Code will inject this)
    print("\n".join(output))

if __name__ == "__main__":
    main()
