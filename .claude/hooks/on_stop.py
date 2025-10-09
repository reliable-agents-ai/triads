#!/usr/bin/env python3
"""
Stop Hook: Update Knowledge Graphs

This hook runs after Claude finishes responding.
It scans the response for [GRAPH_UPDATE] blocks and updates knowledge graphs.

Hook Type: Stop
Configured in: .claude/settings.json

Why Stop instead of PostToolUse?
PostToolUse hooks are currently broken in Claude Code (known bug, multiple GitHub issues).
Stop hooks work reliably and achieve the same goal - automatic graph updates.

Data Flow:
1. Claude finishes responding
2. Stop hook fires
3. Hook receives response text or transcript path
4. Scan for [GRAPH_UPDATE] blocks
5. Group updates by triad
6. Update each triad's graph
7. Save graphs to disk
"""

import json
import sys
import re
import glob
from pathlib import Path
from datetime import datetime

# ============================================================================
# Graph Update Extraction
# ============================================================================

def extract_graph_updates_from_text(text):
    """
    Extract [GRAPH_UPDATE] blocks from any text.

    Args:
        text: String containing [GRAPH_UPDATE]...[/GRAPH_UPDATE] blocks

    Returns:
        List of update dictionaries
    """
    pattern = r'\[GRAPH_UPDATE\](.*?)\[/GRAPH_UPDATE\]'
    matches = re.findall(pattern, text, re.DOTALL)

    updates = []
    for match in matches:
        update = {}
        for line in match.strip().split('\n'):
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()

                # Parse JSON arrays
                if value.startswith('['):
                    try:
                        value = json.loads(value)
                    except json.JSONDecodeError:
                        pass

                # Parse confidence as float
                if key == 'confidence':
                    try:
                        value = float(value)
                    except ValueError:
                        pass

                update[key] = value

        if update:
            updates.append(update)

    return updates

# ============================================================================
# Triad Identification
# ============================================================================

def get_triad_from_update(update):
    """
    Determine which triad an update belongs to.

    Strategy:
    1. Check if update has 'triad' field explicitly
    2. Check if update has 'created_by' field, look up agent's triad
    3. Check node_id prefix (e.g., "discovery_node_001" -> "discovery")
    4. Default to 'default' triad

    Args:
        update: Update dictionary from [GRAPH_UPDATE] block

    Returns:
        triad_name: String name of triad
    """
    # Direct triad field
    if 'triad' in update:
        return update['triad']

    # Infer from agent
    if 'created_by' in update:
        agent_name = update['created_by']
        triad = lookup_agent_triad(agent_name)
        if triad:
            return triad

    # Infer from node_id prefix
    node_id = update.get('node_id', '')
    if '_' in node_id:
        potential_triad = node_id.split('_')[0]
        if is_valid_triad(potential_triad):
            return potential_triad

    # Default
    return 'default'

def lookup_agent_triad(agent_name):
    """
    Find which triad an agent belongs to by searching for its file.

    Args:
        agent_name: Name of the agent

    Returns:
        triad_name: String name of triad, or None if not found
    """
    pattern = f".claude/agents/**/{agent_name}.md"
    matches = glob.glob(pattern, recursive=True)

    if matches:
        agent_file = Path(matches[0])

        # Parse frontmatter for triad field
        try:
            with open(agent_file, 'r') as f:
                in_frontmatter = False
                for line in f:
                    line = line.strip()
                    if line == '---':
                        in_frontmatter = not in_frontmatter
                        continue
                    if in_frontmatter and line.startswith('triad:'):
                        return line.split(':', 1)[1].strip()
        except Exception:
            pass

        # Fallback to parent directory name
        return agent_file.parent.name

    return None

def is_valid_triad(name):
    """
    Check if a triad exists.

    Args:
        name: Potential triad name

    Returns:
        bool: True if triad exists
    """
    # Check if graph file exists OR agent directory exists
    return Path(f'.claude/graphs/{name}_graph.json').exists() or \
           Path(f'.claude/agents/{name}').is_dir()

# ============================================================================
# Knowledge Graph Management (Reused from post_tool_use.py)
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
            print(f"⚠️  Node {node_id} already exists, skipping", file=sys.stderr)
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
            print(f"⚠️  Node {node_id} not found, skipping", file=sys.stderr)
            return graph_data

        # Update fields (preserve original created_by and created_at)
        for key, value in update.items():
            if key not in ['type', 'node_id']:
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
            print(f"⚠️  Missing source or target for edge", file=sys.stderr)
            return graph_data

        # Check if edge already exists
        existing = [
            e for e in graph_data['links']
            if e.get('source') == source and e.get('target') == target and e.get('key') == edge_type
        ]

        if existing:
            print(f"⚠️  Edge {source} -> {target} already exists", file=sys.stderr)
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
            print(f"⚠️  Edge {source} -> {target} not found", file=sys.stderr)
            return graph_data

        # Update fields
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
# Main Stop Hook Logic
# ============================================================================

def main():
    """Main Stop hook execution."""

    # Read input (may be JSON with transcript_path, or plain text)
    input_text = sys.stdin.read()

    # Try to parse as JSON first
    conversation_text = None
    try:
        input_data = json.loads(input_text)

        # Check if we have a transcript_path
        transcript_path = input_data.get('transcript_path')
        if transcript_path and Path(transcript_path).exists():
            # Read full conversation from transcript JSONL
            with open(transcript_path, 'r') as f:
                transcript_lines = f.readlines()

            # Extract all text from transcript
            all_text = []
            for line in transcript_lines:
                try:
                    entry = json.loads(line)

                    # Check both entry['content'] and entry['message']['content']
                    content = None
                    if 'message' in entry and 'content' in entry['message']:
                        content = entry['message']['content']
                    elif 'content' in entry:
                        content = entry['content']

                    if content:
                        # Content can be string or array
                        if isinstance(content, list):
                            for item in content:
                                if isinstance(item, dict) and 'text' in item:
                                    all_text.append(item['text'])
                                elif isinstance(item, str):
                                    all_text.append(item)
                        elif isinstance(content, str):
                            all_text.append(content)
                except json.JSONDecodeError:
                    continue

            conversation_text = '\n'.join(all_text)
        else:
            # Use input data as text
            conversation_text = str(input_data)

    except json.JSONDecodeError:
        # Input is plain text
        conversation_text = input_text

    if not conversation_text:
        # No text to process
        return

    # Extract all [GRAPH_UPDATE] blocks
    updates = extract_graph_updates_from_text(conversation_text)

    if not updates:
        # No updates found - exit silently
        return

    print(f"\n{'='*80}", file=sys.stderr)
    print(f"📊 Knowledge Graph Update (Stop Hook)", file=sys.stderr)
    print(f"{'='*80}", file=sys.stderr)
    print(f"Found {len(updates)} [GRAPH_UPDATE] blocks", file=sys.stderr)
    print(f"{'='*80}\n", file=sys.stderr)

    # Group updates by triad
    updates_by_triad = {}
    for update in updates:
        triad = get_triad_from_update(update)
        if triad not in updates_by_triad:
            updates_by_triad[triad] = []
        updates_by_triad[triad].append(update)

    # Apply updates to each triad's graph
    for triad, triad_updates in updates_by_triad.items():
        print(f"Updating {triad} graph ({len(triad_updates)} updates)...", file=sys.stderr)

        graph_data = load_graph(triad)

        for i, update in enumerate(triad_updates, 1):
            agent_name = update.get('created_by', 'unknown')
            print(f"  [{i}/{len(triad_updates)}] ", end='', file=sys.stderr)
            try:
                graph_data = apply_update(graph_data, update, agent_name)
            except Exception as e:
                print(f"❌ Error: {e}", file=sys.stderr)
                continue

        # Save updated graph
        try:
            save_graph(graph_data, triad)
            print(f"✅ {triad}_graph.json updated: {graph_data['_meta']['node_count']} nodes, {graph_data['_meta']['edge_count']} edges\n", file=sys.stderr)
        except Exception as e:
            print(f"❌ Error saving {triad} graph: {e}\n", file=sys.stderr)

    print(f"{'='*80}\n", file=sys.stderr)

if __name__ == "__main__":
    main()
