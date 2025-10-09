#!/usr/bin/env python3
"""
PostToolUse Hook: Update Knowledge Graphs

This hook runs after the Task tool completes (i.e., after a subagent finishes).
It extracts [GRAPH_UPDATE] blocks from the subagent's output and updates
the appropriate knowledge graph.

Hook Type: PostToolUse (matcher: Task)
Configured in: .claude/settings.json

Data Flow:
1. Subagent completes work
2. Task tool returns with tool_response containing output
3. This hook receives tool_input and tool_response
4. Hook identifies which triad the agent belongs to
5. Hook parses [GRAPH_UPDATE] blocks from output
6. Hook updates the triad's knowledge graph JSON file

Input Format (from stdin):
{
  "tool_name": "Task",
  "tool_input": {
    "subagent_type": "agent-name",
    "prompt": "task description"
  },
  "tool_response": {
    "output": "agent's output text with [GRAPH_UPDATE] blocks"
  },
  "session_id": "...",
  "cwd": "..."
}

Graph Update Format (in output text):
[GRAPH_UPDATE]
type: add_node | update_node | add_edge | update_edge
node_id: unique_identifier
node_type: Entity | Concept | Decision | Task | Finding | Uncertainty
label: Human readable name
description: Detailed description
confidence: 0.0-1.0
evidence: Citation or source
[/GRAPH_UPDATE]
"""

import json
import sys
import re
import glob
from pathlib import Path
from datetime import datetime

# ============================================================================
# Agent → Triad Mapping
# ============================================================================

def get_triad_for_agent(subagent_type):
    """
    Find which triad a subagent belongs to by searching for its file
    and parsing the frontmatter.

    Args:
        subagent_type: Agent name from tool_input.subagent_type

    Returns:
        triad_name: The triad this agent belongs to, or None if not found
    """
    # Search for agent file in .claude/agents/
    pattern = f".claude/agents/**/{subagent_type}.md"
    matches = glob.glob(pattern, recursive=True)

    if not matches:
        print(f"⚠️  Warning: Agent file not found for '{subagent_type}'", file=sys.stderr)
        return None

    agent_file = Path(matches[0])

    # Parse frontmatter to find triad field
    try:
        with open(agent_file, 'r') as f:
            in_frontmatter = False
            for line in f:
                line = line.strip()

                # Detect frontmatter boundaries
                if line == '---':
                    in_frontmatter = not in_frontmatter
                    continue

                # Parse triad field
                if in_frontmatter and line.startswith('triad:'):
                    triad_name = line.split(':', 1)[1].strip()
                    return triad_name

    except Exception as e:
        print(f"⚠️  Error reading agent file {agent_file}: {e}", file=sys.stderr)
        return None

    # Fallback: Use parent directory name
    return agent_file.parent.name

# ============================================================================
# Graph Update Extraction
# ============================================================================

def extract_graph_updates(tool_response):
    """
    Extract [GRAPH_UPDATE] blocks from subagent output.

    Args:
        tool_response: Dict with 'output' field containing subagent text

    Returns:
        List of update dictionaries
    """
    output_text = tool_response.get('output', '')

    if not output_text:
        return []

    # Pattern to match [GRAPH_UPDATE]...[/GRAPH_UPDATE]
    pattern = r'\[GRAPH_UPDATE\](.*?)\[/GRAPH_UPDATE\]'
    matches = re.findall(pattern, output_text, re.DOTALL)

    updates = []
    for match in matches:
        update = {}
        for line in match.strip().split('\n'):
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()

                # Parse lists (e.g., alternatives: ["A", "B"])
                if value.startswith('['):
                    try:
                        value = json.loads(value)
                    except json.JSONDecodeError:
                        pass  # Keep as string if not valid JSON

                # Parse confidence as float
                if key == 'confidence':
                    try:
                        value = float(value)
                    except ValueError:
                        pass

                update[key] = value

        if update:  # Only add non-empty updates
            updates.append(update)

    return updates

# ============================================================================
# Knowledge Graph Management
# ============================================================================

def load_graph(triad_name):
    """Load a triad's knowledge graph or create a new one."""
    graphs_dir = Path('.claude/graphs')
    graphs_dir.mkdir(parents=True, exist_ok=True)

    graph_file = graphs_dir / f"{triad_name}_graph.json"

    if graph_file.exists():
        try:
            with open(graph_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"⚠️  Warning: Corrupt graph file, creating new one", file=sys.stderr)

    # Create new graph structure
    return {
        "directed": True,
        "nodes": [],
        "links": [],
        "_meta": {
            "triad_name": triad_name,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "node_count": 0,
            "edge_count": 0
        }
    }

def save_graph(graph_data, triad_name):
    """Save a knowledge graph to disk."""
    graphs_dir = Path('.claude/graphs')
    graphs_dir.mkdir(parents=True, exist_ok=True)

    graph_file = graphs_dir / f"{triad_name}_graph.json"

    # Update metadata
    graph_data['_meta']['updated_at'] = datetime.now().isoformat()
    graph_data['_meta']['node_count'] = len(graph_data['nodes'])
    graph_data['_meta']['edge_count'] = len(graph_data['links'])

    with open(graph_file, 'w') as f:
        json.dump(graph_data, f, indent=2)

def apply_update(graph_data, update, agent_name):
    """
    Apply a single graph update to the graph data.

    Args:
        graph_data: The graph dictionary
        update: The update dictionary from [GRAPH_UPDATE] block
        agent_name: Name of the agent making the update

    Returns:
        Updated graph_data
    """
    update_type = update.get('type', '')

    if update_type == 'add_node':
        # Check if node already exists
        node_id = update.get('node_id')
        existing = [n for n in graph_data['nodes'] if n.get('id') == node_id]

        if existing:
            print(f"⚠️  Node {node_id} already exists, skipping add", file=sys.stderr)
            return graph_data

        # Create new node
        node = {
            'id': node_id,
            'type': update.get('node_type', 'Entity'),
            'label': update.get('label', node_id),
            'description': update.get('description', ''),
            'confidence': update.get('confidence', 1.0),
            'evidence': update.get('evidence', ''),
            'created_by': agent_name,
            'created_at': datetime.now().isoformat()
        }

        # Add optional fields
        for key in ['alternatives', 'rationale', 'status', 'priority']:
            if key in update:
                node[key] = update[key]

        graph_data['nodes'].append(node)
        print(f"✓ Added node: {node_id} ({node['type']})", file=sys.stderr)

    elif update_type == 'update_node':
        # Find and update existing node
        node_id = update.get('node_id')
        node = next((n for n in graph_data['nodes'] if n.get('id') == node_id), None)

        if not node:
            print(f"⚠️  Node {node_id} not found, skipping update", file=sys.stderr)
            return graph_data

        # Update fields (preserve original created_by and created_at)
        for key, value in update.items():
            if key not in ['type', 'node_id']:  # Don't overwrite structural fields
                node[key] = value

        node['updated_by'] = agent_name
        node['updated_at'] = datetime.now().isoformat()

        print(f"✓ Updated node: {node_id}", file=sys.stderr)

    elif update_type == 'add_edge':
        # Create new edge
        source = update.get('source')
        target = update.get('target')
        edge_type = update.get('edge_type', 'relates_to')

        if not source or not target:
            print(f"⚠️  Missing source or target for edge, skipping", file=sys.stderr)
            return graph_data

        # Check if edge already exists
        existing = [
            e for e in graph_data['links']
            if e.get('source') == source and e.get('target') == target and e.get('key') == edge_type
        ]

        if existing:
            print(f"⚠️  Edge {source} -> {target} ({edge_type}) already exists", file=sys.stderr)
            return graph_data

        edge = {
            'source': source,
            'target': target,
            'key': edge_type,
            'rationale': update.get('rationale', ''),
            'created_by': agent_name,
            'created_at': datetime.now().isoformat()
        }

        graph_data['links'].append(edge)
        print(f"✓ Added edge: {source} -> {target} ({edge_type})", file=sys.stderr)

    elif update_type == 'update_edge':
        # Find and update existing edge
        source = update.get('source')
        target = update.get('target')
        edge_type = update.get('edge_type', 'relates_to')

        edge = next(
            (e for e in graph_data['links']
             if e.get('source') == source and e.get('target') == target and e.get('key') == edge_type),
            None
        )

        if not edge:
            print(f"⚠️  Edge {source} -> {target} not found, skipping update", file=sys.stderr)
            return graph_data

        # Update rationale or other fields
        for key, value in update.items():
            if key not in ['type', 'source', 'target', 'edge_type']:
                edge[key] = value

        edge['updated_by'] = agent_name
        edge['updated_at'] = datetime.now().isoformat()

        print(f"✓ Updated edge: {source} -> {target}", file=sys.stderr)

    else:
        print(f"⚠️  Unknown update type: {update_type}", file=sys.stderr)

    return graph_data

# ============================================================================
# Main Hook Logic
# ============================================================================

def main():
    """Main hook execution."""

    # Read input from stdin
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Failed to parse JSON input: {e}", file=sys.stderr)
        return

    # Extract key data
    tool_name = input_data.get('tool_name')
    tool_input = input_data.get('tool_input', {})
    tool_response = input_data.get('tool_response', {})

    # Verify this is a Task tool invocation
    if tool_name != 'Task':
        print(f"⚠️  Ignoring non-Task tool: {tool_name}", file=sys.stderr)
        return

    # Extract subagent name
    subagent_type = tool_input.get('subagent_type')
    if not subagent_type:
        print(f"⚠️  Warning: No subagent_type in tool_input", file=sys.stderr)
        return

    print(f"\n{'='*80}", file=sys.stderr)
    print(f"📊 Knowledge Graph Update Hook", file=sys.stderr)
    print(f"{'='*80}", file=sys.stderr)
    print(f"Agent: {subagent_type}", file=sys.stderr)

    # Determine which triad this agent belongs to
    triad_name = get_triad_for_agent(subagent_type)
    if not triad_name:
        print(f"❌ Could not determine triad for agent '{subagent_type}'", file=sys.stderr)
        return

    print(f"Triad: {triad_name}", file=sys.stderr)

    # Extract graph updates from output
    updates = extract_graph_updates(tool_response)

    if not updates:
        print(f"ℹ️  No [GRAPH_UPDATE] blocks found in output", file=sys.stderr)
        print(f"{'='*80}\n", file=sys.stderr)
        return

    print(f"Updates: {len(updates)}", file=sys.stderr)
    print(f"{'='*80}\n", file=sys.stderr)

    # Load the triad's knowledge graph
    graph_data = load_graph(triad_name)

    # Apply each update
    for i, update in enumerate(updates, 1):
        print(f"[{i}/{len(updates)}] ", end='', file=sys.stderr)
        try:
            graph_data = apply_update(graph_data, update, subagent_type)
        except Exception as e:
            print(f"❌ Error applying update: {e}", file=sys.stderr)
            continue

    # Save the updated graph
    try:
        save_graph(graph_data, triad_name)
        print(f"\n✅ Knowledge graph updated: {triad_name}_graph.json", file=sys.stderr)
        print(f"   Nodes: {graph_data['_meta']['node_count']}, Edges: {graph_data['_meta']['edge_count']}", file=sys.stderr)
    except Exception as e:
        print(f"\n❌ Error saving graph: {e}", file=sys.stderr)

    print(f"{'='*80}\n", file=sys.stderr)

if __name__ == "__main__":
    main()
