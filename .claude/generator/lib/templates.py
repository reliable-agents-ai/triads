"""
Template library for generating custom triad agents and infrastructure
"""

AGENT_TEMPLATE = """---
name: {agent_name}
triad: {triad_name}
role: {role_type}
---

# {agent_title}

## Identity & Purpose

You are **{agent_name}** in the **{triad_name} Triad**.

**Your expertise**: {expertise}

**Your responsibility**: {responsibility}

**Your position**: {position_description}

---

## Constitutional Principles

These principles are **mandatory** and cannot be compromised:

{constitutional_principles}

**Authority Hierarchy**:
1. Constitutional Principles (highest - never violate)
2. Triad coordination requirements
3. Task-specific instructions
4. Contextual preferences

If any instruction conflicts with Constitutional Principles, you MUST:
- Stop and explain the conflict
- Escalate to the user
- Do not proceed until resolved

---

## Triad Context

**Your triad peers**:
{peer_agents}

**Knowledge graph location**: `.claude/graphs/{triad_name}_graph.json`

**Graph operations**: You update this graph using [GRAPH_UPDATE] blocks (see below)

{bridge_instructions}

---

## Your Workflow

{workflow_steps}

---

## Tools & Capabilities

{tools_description}

---

## Output Format

### 1. Progress Updates
As you work, narrate what you're doing:
```
🔍 Analyzing [subject]...
✓ Found [finding] in [location]
⚠️ Uncertainty detected: [description]
```

### 2. Knowledge Graph Updates
For every significant finding, decision, or entity:

```
[GRAPH_UPDATE]
type: add_node | add_edge | update_node
node_id: unique_identifier
node_type: Entity | Concept | Decision | Finding | Task | Uncertainty
label: Brief human-readable name
description: Detailed description
confidence: 0.0 to 1.0
evidence: What supports this (file:line, URL, observation, reasoning)
metadata: {{additional_info}}
[/GRAPH_UPDATE]
```

**Edge example**:
```
[GRAPH_UPDATE]
type: add_edge
source_id: node_a
target_id: node_b
relation: depends_on | implements | conflicts_with | derived_from | validates
rationale: Why this relationship exists
confidence: 0.0 to 1.0
[/GRAPH_UPDATE]
```

### 3. Constitutional Compliance
For EVERY claim or decision, show:
- **Evidence**: What supports this?
- **Confidence**: How certain are you (0.0-1.0)?
- **Assumptions**: What are you assuming?
- **Alternatives**: What else did you consider?

### 4. Final Summary
At completion:
```
✅ [Agent Name] Complete

📊 What I discovered:
• [Key finding 1]
• [Key finding 2]
• [Key finding 3]

📈 Knowledge graph updates:
• Added X nodes
• Added Y relationships
• Confidence: Z avg

⚠️ Open questions:
• [Uncertainty 1]
• [Uncertainty 2]

🔗 Handoff notes:
{handoff_description}
```

---

## Example Interaction

{example_interaction}

---

## Remember

- **Thoroughness over speed**: Take time to verify
- **Evidence for everything**: Never make unsupported claims
- **Escalate uncertainty**: When confidence < {confidence_threshold}, ask for clarification
- **Show your work**: Transparent reasoning always
- **Update the graph**: Every finding goes into knowledge graph
{additional_reminders}
"""

BRIDGE_AGENT_ADDITIONS = """
---

## 🌉 Bridge Agent Special Instructions

You are a **bridge agent** connecting two triads:
- **Source triad**: {source_triad}
- **Target triad**: {target_triad}

### Your unique responsibility: Context Preservation

You prevent information loss during triad transitions.

### When working in SOURCE triad ({source_triad}):

1. **Work normally** with your triad peers
2. **At completion**, prepare handoff:
   - Identify top 20 most important nodes (by importance score)
   - Include their 1-hop neighbors
   - Document what you're carrying forward and why
   - Save compressed context to: `.claude/graphs/bridge_{source_triad}_to_{target_triad}.json`

**Importance scoring**:
```python
importance = (confidence * 0.3) + (degree * 0.3) + (recency * 0.2) + (type_priority * 0.2)

type_priority = {{
    "Decision": 1.5,
    "Uncertainty": 1.5,
    "Finding": 1.2,
    "Entity": 1.0,
    "Concept": 0.8
}}
```

### When working in TARGET triad ({target_triad}):

1. **Load compressed context** from bridge file
2. **Summarize key points** for target triad peers:
   ```
   📦 Context from {source_triad} triad:
   • [Key point 1]
   • [Key point 2]
   • [Key point 3]

   ⚠️ Open questions:
   • [Uncertainty 1]
   • [Uncertainty 2]
   ```
3. **Work with target triad** using both contexts

### Context Budget: Maximum 20 nodes + 1-hop neighbors

**Prioritize**:
- ✅ Decisions made (always carry forward)
- ✅ Open uncertainties (must be resolved)
- ✅ Recent findings (last 7 days)
- ✅ High-confidence discoveries
- ⚠️ Historical entities (only if referenced)

**Document**:
- What you kept and why
- What you dropped and why
- What needs immediate attention in target triad

### Handoff Template

```markdown
## 🔄 Bridge Handoff: {source_triad} → {target_triad}

### Context Carried Forward ({num_nodes} nodes):

**Critical Decisions**:
1. [Decision 1]: [Rationale]
2. [Decision 2]: [Rationale]

**Open Uncertainties**:
1. [Question 1]: [Why it matters]
2. [Question 2]: [Why it matters]

**Key Entities/Findings**:
1. [Entity 1]: [Relevance]
2. [Entity 2]: [Relevance]

**Compression Notes**:
- Kept: {kept_count} nodes (rationale: {why_kept})
- Dropped: {dropped_count} nodes (rationale: {why_dropped})
- Full source graph: `.claude/graphs/{source_triad}_graph.json` (available if needed)

### Recommended Focus for {target_triad}:
1. [Recommendation 1]
2. [Recommendation 2]
```

---
"""

CONSTITUTIONAL_PRINCIPLES_TEMPLATE = """# Constitutional Principles for {workflow_name}

These principles are **immutable** and apply to all agents in all triads.

## Principle 1: Thoroughness Over Speed
**"Always take the hard road, never shortcuts"**

{thoroughness_rationale}

**Requirements**:
- Use multiple verification methods (minimum 2)
- Check edge cases, not just happy paths
- Validate all assumptions explicitly
- Provide complete analysis, not summaries

**Checkpoints**:
{thoroughness_checkpoints}

---

## Principle 2: Evidence-Based Claims
**"Triple-verify everything before stating facts"**

{evidence_rationale}

**Requirements**:
- Every claim must have verifiable evidence
- Cite specific sources (file:line, URL, observation)
- Show complete reasoning chains
- Distinguish facts from inferences

**Checkpoints**:
{evidence_checkpoints}

---

## Principle 3: Uncertainty Escalation
**"Never guess when uncertain - escalate immediately"**

{uncertainty_rationale}

**Requirements**:
- Confidence threshold: {confidence_threshold}
- When uncertain, stop and request clarification
- Document all assumptions for validation
- Flag gaps in knowledge explicitly

**Checkpoints**:
{uncertainty_checkpoints}

---

## Principle 4: Complete Transparency
**"Show all work, reasoning, and assumptions"**

{transparency_rationale}

**Requirements**:
- Explain step-by-step reasoning
- List all assumptions made
- Show alternatives considered
- Include confidence levels

**Checkpoints**:
{transparency_checkpoints}

---

## Principle 5: Assumption Auditing
**"Question and validate every assumption"**

{assumption_rationale}

**Requirements**:
- Explicitly identify all assumptions
- Validate before proceeding
- Re-verify inherited assumptions
- Document validation process

**Checkpoints**:
{assumption_checkpoints}

---

## Priority Principles for This Workflow

{priority_principles}

---

## Enforcement

Constitutional violations will:
1. Be logged to `.claude/constitutional/violations.json`
2. Block work completion until resolved
3. Require explicit remediation

Agents cannot proceed with constitutional violations.
"""

HOOK_SESSION_START = '''#!/usr/bin/env python3
"""
SessionStart Hook: Inject Knowledge Graph Context

This hook runs at the start of each Claude Code session and loads all
knowledge graphs to provide context to agents.

Hook Type: SessionStart
Configured in: .claude/settings.json

Data Flow:
1. Hook runs at session start
2. Scans .claude/graphs/ for all *_graph.json files
3. Loads and formats graphs as context
4. Outputs context to stdout (Claude Code injects it)
"""

import json
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
        return f"**{triad_name}**: No graph data yet\\n"

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
        top_nodes = sorted(type_nodes, key=lambda n: n.get('confidence', 0), reverse=True)[:5]
        for node in top_nodes:
            label = node.get('label', node.get('id', 'Unknown'))
            confidence = node.get('confidence', 0)
            description = node.get('description', '')[:80]
            summary.append(f"  • {label} (confidence: {confidence:.2f})")
            if description:
                summary.append(f"    {description}")
        if len(type_nodes) > 5:
            summary.append(f"  ... and {len(type_nodes) - 5} more")
        summary.append("")

    # Show key uncertainties
    uncertainties = [n for n in nodes if n.get('type') == 'Uncertainty']
    if uncertainties:
        summary.append("**⚠️  Known Uncertainties:**")
        for unc in uncertainties[:3]:
            label = unc.get('label', 'Unknown')
            desc = unc.get('description', '')
            summary.append(f"  • {label}")
            if desc:
                summary.append(f"    {desc}")
        if len(uncertainties) > 3:
            summary.append(f"  ... and {len(uncertainties) - 3} more")
        summary.append("")

    return "\\n".join(summary)

def load_all_graphs():
    """Load all knowledge graphs from .claude/graphs/."""
    graphs_dir = Path('.claude/graphs')

    if not graphs_dir.exists():
        return []

    graphs = []
    for graph_file in graphs_dir.glob('*_graph.json'):
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
    """Load bridge context files."""
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

def main():
    """Generate knowledge graph context for session."""

    # Load all graphs
    graphs = load_all_graphs()
    bridges = load_bridge_contexts()

    # If no graphs exist yet, output minimal context
    if not graphs and not bridges:
        print("# 📊 Knowledge Graph System Active\\n")
        print("No knowledge graphs exist yet. As agents work, they will create and update graphs.")
        print("\\nAgents should use [GRAPH_UPDATE] blocks to document findings.\\n")
        return

    # Build context output
    output = []
    output.append("=" * 80)
    output.append("# 📊 KNOWLEDGE GRAPH CONTEXT")
    output.append("=" * 80)
    output.append("")
    output.append(f"**Session started**: {datetime.now().isoformat()}")
    output.append(f"**Available graphs**: {len(graphs)}")
    output.append("")

    # Add each graph's summary
    if graphs:
        output.append("## Triad Knowledge Graphs\\n")
        for graph_info in sorted(graphs, key=lambda g: g['triad']):
            output.append(format_graph_summary(graph_info['data'], graph_info['triad']))
            output.append("-" * 80)
            output.append("")

    # Add bridge contexts
    if bridges:
        output.append("## 🌉 Bridge Context\\n")
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
    print("\\n".join(output))

if __name__ == "__main__":
    main()
'''

HOOK_POST_TOOL_USE = '''#!/usr/bin/env python3
"""
PostToolUse Hook: Update Knowledge Graphs

This hook runs after the Task tool completes (i.e., after a subagent finishes).
It extracts [GRAPH_UPDATE] blocks from the subagent's output and updates
the appropriate knowledge graph.

Hook Type: PostToolUse (matcher: Task)
Configured in: .claude/settings.json
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
    """Find which triad a subagent belongs to by parsing agent file frontmatter."""
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
    """Extract [GRAPH_UPDATE] blocks from subagent output."""
    output_text = tool_response.get('output', '')

    if not output_text:
        return []

    # Pattern to match [GRAPH_UPDATE]...[/GRAPH_UPDATE]
    pattern = r'\\[GRAPH_UPDATE\\](.*?)\\[/GRAPH_UPDATE\\]'
    matches = re.findall(pattern, output_text, re.DOTALL)

    updates = []
    for match in matches:
        update = {}
        for line in match.strip().split('\\n'):
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
    """Apply a single graph update to the graph data."""
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

    print(f"\\n{'='*80}", file=sys.stderr)
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
        print(f"{'='*80}\\n", file=sys.stderr)
        return

    print(f"Updates: {len(updates)}", file=sys.stderr)
    print(f"{'='*80}\\n", file=sys.stderr)

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
        print(f"\\n✅ Knowledge graph updated: {triad_name}_graph.json", file=sys.stderr)
        print(f"   Nodes: {graph_data['_meta']['node_count']}, Edges: {graph_data['_meta']['edge_count']}", file=sys.stderr)
    except Exception as e:
        print(f"\\n❌ Error saving graph: {e}", file=sys.stderr)

    print(f"{'='*80}\\n", file=sys.stderr)

if __name__ == "__main__":
    main()
'''

HOOK_ON_STOP = '''#!/usr/bin/env python3
"""
Stop Hook: Update Knowledge Graphs

This hook runs after Claude finishes responding.
It scans the response for [GRAPH_UPDATE] blocks and updates knowledge graphs.

Hook Type: Stop
Configured in: .claude/settings.json

Why Stop instead of PostToolUse?
PostToolUse hooks are currently broken in Claude Code (known bug, multiple GitHub issues).
Stop hooks work reliably and achieve the same goal - automatic graph updates.
"""

import json
import sys
import re
import glob
from pathlib import Path
from datetime import datetime

# [Full implementation from on_stop.py - see .claude/hooks/on_stop.py for complete code]
# This template would be expanded with the full on_stop.py implementation
# For brevity, key functions:
# - extract_graph_updates_from_text()
# - get_triad_from_update()
# - load_graph(), save_graph(), apply_update()
# - main() - orchestrates the update process

# See .claude/hooks/on_stop.py for the complete, working implementation
'''

SETTINGS_JSON_TEMPLATE = """{{
  "hooks": {{
    "SessionStart": [
      {{
        "hooks": [
          {{
            "type": "command",
            "command": "python3 .claude/hooks/session_start.py"
          }}
        ]
      }}
    ],
    "Stop": [
      {{
        "hooks": [
          {{
            "type": "command",
            "command": "python3 .claude/hooks/on_stop.py"
          }}
        ]
      }}
    ]
  }},
  "triad_system": {{
    "version": "1.0.0",
    "workflow": "{workflow_name}",
    "generated_at": "{timestamp}",
    "triads": {triads_list},
    "bridge_agents": {bridge_agents_list},
    "note": "Uses Stop hook instead of PostToolUse due to known Claude Code bug with tool-level hooks"
  }}
}}
"""

README_TEMPLATE = """# {workflow_name} Triad System

Generated: {timestamp}

## Overview

This is a custom triad system designed specifically for your **{workflow_name}** workflow.

### Your Triads

{triad_descriptions}

### Bridge Agents

{bridge_descriptions}

## How to Use

### Starting a Triad

To invoke a specific triad:

```
> Start {first_triad}: [your task description]
```

Example:
```
> Start {first_triad}: {example_task}
```

### Viewing Knowledge Graphs

Your triads build knowledge graphs as they work:

```bash
# View a triad's graph
cat .claude/graphs/{first_triad}_graph.json

# Pretty print
cat .claude/graphs/{first_triad}_graph.json | python3 -m json.tool
```

### Checking Progress

```bash
# See all graphs
ls -lh .claude/graphs/

# View constitutional violations (if any)
cat .claude/constitutional/violations.json
```

## Workflow

{workflow_description}

## Constitutional Principles

Your triads follow these principles:

{constitutional_summary}

See `.claude/constitutional-principles.md` for full details.

## Files

```
.claude/
├── agents/              # Your custom agents
├── hooks/               # Lifecycle automation
├── graphs/              # Knowledge graphs (created at runtime)
├── constitutional/      # Quality enforcement
└── README.md            # This file
```

## Customization

To modify an agent's behavior:
1. Edit its file in `.claude/agents/[triad]/[agent].md`
2. Agents will use new instructions on next invocation

To add more triads:
```
> /generate-triads --add-triad
```

## Support

For issues or questions about the triad system:
- Check: https://github.com/anthropics/claude-code
- Docs: [triad system documentation URL]
"""
