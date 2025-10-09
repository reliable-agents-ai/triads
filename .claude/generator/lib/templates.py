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

HOOK_ON_SUBAGENT_START = '''#!/usr/bin/env python3
"""
Hook: on_subagent_start.py
Executed BEFORE a sub-agent runs
Purpose: Load triad context into agent environment
"""

import json
import os
from pathlib import Path
from datetime import datetime

def load_graph(graph_path):
    """Load knowledge graph if it exists"""
    if Path(graph_path).exists():
        with open(graph_path, 'r') as f:
            return json.load(f)
    return None

def generate_context_summary(graph_data):
    """Create human-readable summary of graph"""
    if not graph_data:
        return {
            "status": "empty",
            "message": "No existing knowledge graph - starting fresh"
        }

    nodes = graph_data.get('nodes', [])
    edges = graph_data.get('links', [])

    # Group by type
    by_type = {}
    for node in nodes:
        node_type = node.get('type', 'Unknown')
        by_type.setdefault(node_type, []).append(node)

    # Key items
    decisions = [n for n in nodes if n.get('type') == 'Decision']
    uncertainties = [n for n in nodes if n.get('type') == 'Uncertainty']

    return {
        "total_nodes": len(nodes),
        "total_edges": len(edges),
        "by_type": {k: len(v) for k, v in by_type.items()},
        "key_decisions": [
            {"id": d['id'], "label": d.get('label', 'Unknown'),
             "confidence": d.get('confidence', 0)}
            for d in decisions[:5]
        ],
        "open_uncertainties": [
            {"id": u['id'], "label": u.get('label', 'Unknown'),
             "description": u.get('description', '')}
            for u in uncertainties
        ],
        "last_updated": graph_data.get('_meta', {}).get('updated_at', 'Unknown')
    }

def main():
    """Main hook execution"""

    # These would be set by Claude Code (simulated for now)
    agent_name = os.getenv('CLAUDE_AGENT_NAME', 'unknown')
    session_id = os.getenv('CLAUDE_SESSION_ID', 'session_001')

    # Determine triad from agent name
    # This mapping should be generated based on the actual triad design
    agent_dir = Path('.claude/agents')
    triad_name = None
    is_bridge = False

    # Find which triad this agent belongs to
    for triad_dir in agent_dir.iterdir():
        if triad_dir.is_dir() and triad_dir.name != 'bridges':
            agent_file = triad_dir / f"{agent_name}.md"
            if agent_file.exists():
                triad_name = triad_dir.name
                break

    # Check if bridge agent
    bridge_dir = agent_dir / 'bridges'
    if bridge_dir.exists():
        bridge_file = bridge_dir / f"{agent_name}.md"
        if bridge_file.exists():
            is_bridge = True

    if not triad_name:
        print(f"⚠️  Could not determine triad for agent: {agent_name}")
        return

    # Load triad graph
    graph_path = Path(f'.claude/graphs/{triad_name}_graph.json')
    graph_data = load_graph(graph_path)
    context_summary = generate_context_summary(graph_data)

    # For bridge agents, load source triad context too
    bridge_context = None
    if is_bridge:
        # Find bridge context files
        bridge_files = list(Path('.claude/graphs').glob(f'bridge_*_to_{triad_name}.json'))
        if bridge_files:
            bridge_context = load_graph(bridge_files[0])

    # Write context to environment file (Claude Code can inject this)
    context_file = Path(f'.claude/graphs/.context_{session_id}_{agent_name}.json')
    context_data = {
        "agent_name": agent_name,
        "triad_name": triad_name,
        "is_bridge": is_bridge,
        "graph_summary": context_summary,
        "bridge_context": bridge_context,
        "loaded_at": datetime.now().isoformat()
    }

    with open(context_file, 'w') as f:
        json.dump(context_data, f, indent=2)

    print(f"✓ Context loaded for {agent_name} ({triad_name} triad)")
    if is_bridge:
        print(f"  🌉 Bridge agent - loaded context from previous triad")
    print(f"  📊 Graph: {context_summary['total_nodes']} nodes, {context_summary['total_edges']} edges")

if __name__ == '__main__':
    main()
'''

HOOK_ON_SUBAGENT_END = '''#!/usr/bin/env python3
"""
Hook: on_subagent_end.py
Executed AFTER a sub-agent completes
Purpose: Extract findings and update knowledge graph
"""

import json
import os
import re
from pathlib import Path
from datetime import datetime

def parse_graph_updates(agent_output):
    """Extract [GRAPH_UPDATE] blocks from agent output"""
    updates = []
    pattern = r'\\[GRAPH_UPDATE\\](.*?)\\[/GRAPH_UPDATE\\]'
    matches = re.findall(pattern, agent_output, re.DOTALL)

    for match in matches:
        update = {}
        for line in match.strip().split('\\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()

                # Try to parse as JSON if it looks like dict/list
                if value.startswith(('{', '[')):
                    try:
                        value = json.loads(value)
                    except:
                        pass

                update[key] = value

        if update:
            updates.append(update)

    return updates

def apply_updates_to_graph(graph_data, updates, agent_name):
    """Apply updates to graph structure"""
    if not graph_data:
        graph_data = {
            "directed": True,
            "multigraph": False,
            "graph": {},
            "nodes": [],
            "links": [],
            "_meta": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        }

    nodes = graph_data.get('nodes', [])
    edges = graph_data.get('links', [])

    for update in updates:
        update_type = update.get('type', '')

        if update_type == 'add_node':
            # Add new node
            node = {
                "id": update.get('node_id'),
                "type": update.get('node_type', 'Entity'),
                "label": update.get('label', ''),
                "description": update.get('description', ''),
                "confidence": float(update.get('confidence', 0.5)),
                "evidence": update.get('evidence', ''),
                "created_by": agent_name,
                "created_at": datetime.now().isoformat(),
                "metadata": update.get('metadata', {})
            }

            # Check if node already exists
            existing = [n for n in nodes if n['id'] == node['id']]
            if not existing:
                nodes.append(node)

        elif update_type == 'add_edge':
            # Add new edge
            edge = {
                "source": update.get('source_id'),
                "target": update.get('target_id'),
                "key": update.get('relation', 'relates_to'),
                "rationale": update.get('rationale', ''),
                "confidence": float(update.get('confidence', 0.5)),
                "created_by": agent_name,
                "created_at": datetime.now().isoformat()
            }

            # Check if edge already exists
            existing = [e for e in edges
                       if e['source'] == edge['source']
                       and e['target'] == edge['target']
                       and e['key'] == edge['key']]
            if not existing:
                edges.append(edge)

        elif update_type == 'update_node':
            # Update existing node
            node_id = update.get('node_id')
            for node in nodes:
                if node['id'] == node_id:
                    # Update fields
                    for key in ['label', 'description', 'confidence', 'evidence', 'metadata']:
                        if key in update:
                            node[key] = update[key]
                    node['updated_by'] = agent_name
                    node['updated_at'] = datetime.now().isoformat()
                    break

    graph_data['nodes'] = nodes
    graph_data['links'] = edges
    graph_data['_meta']['updated_at'] = datetime.now().isoformat()
    graph_data['_meta']['node_count'] = len(nodes)
    graph_data['_meta']['edge_count'] = len(edges)

    return graph_data

def check_constitutional_compliance(updates, agent_name):
    """Basic constitutional principle checking"""
    violations = []

    # Load constitutional checkpoints for this agent
    checkpoints_file = Path('.claude/constitutional/checkpoints.json')
    if checkpoints_file.exists():
        with open(checkpoints_file, 'r') as f:
            checkpoints = json.load(f)
            agent_checkpoints = checkpoints.get(agent_name, [])
    else:
        agent_checkpoints = []

    # Check each update
    for update in updates:
        # Evidence-based claims
        if update.get('type') == 'add_node':
            if not update.get('evidence'):
                violations.append({
                    "principle": "evidence-based-claims",
                    "severity": "high",
                    "description": f"Node '{update.get('node_id')}' lacks evidence",
                    "update": update
                })

        # Confidence threshold
        confidence = float(update.get('confidence', 1.0))
        if confidence < 0.7 and update.get('type') != 'Uncertainty':
            violations.append({
                "principle": "uncertainty-escalation",
                "severity": "medium",
                "description": f"Low confidence ({confidence}) should be flagged as uncertainty",
                "update": update
            })

    return violations

def main():
    """Main hook execution"""

    # Get agent info
    agent_name = os.getenv('CLAUDE_AGENT_NAME', 'unknown')
    agent_output = os.getenv('CLAUDE_AGENT_OUTPUT', '')
    session_id = os.getenv('CLAUDE_SESSION_ID', 'session_001')

    # For testing, read from a temp file if env var not set
    if not agent_output:
        output_file = Path(f'.claude/graphs/.output_{session_id}_{agent_name}.txt')
        if output_file.exists():
            agent_output = output_file.read_text()

    # Find triad
    agent_dir = Path('.claude/agents')
    triad_name = None

    for triad_dir in agent_dir.iterdir():
        if triad_dir.is_dir() and triad_dir.name != 'bridges':
            agent_file = triad_dir / f"{agent_name}.md"
            if agent_file.exists():
                triad_name = triad_dir.name
                break

    if not triad_name:
        print(f"⚠️  Could not determine triad for agent: {agent_name}")
        return

    # Parse updates
    updates = parse_graph_updates(agent_output)

    if not updates:
        print(f"ℹ️  No graph updates found in {agent_name} output")
        return

    print(f"✓ Found {len(updates)} graph updates from {agent_name}")

    # Check constitutional compliance
    violations = check_constitutional_compliance(updates, agent_name)

    if violations:
        print(f"⚠️  {len(violations)} constitutional violations detected:")
        for v in violations:
            print(f"   - {v['principle']}: {v['description']}")

        # Log violations
        violations_file = Path('.claude/constitutional/violations.json')
        violations_file.parent.mkdir(exist_ok=True)

        existing_violations = []
        if violations_file.exists():
            with open(violations_file, 'r') as f:
                existing_violations = json.load(f)

        existing_violations.extend([{
            **v,
            "agent": agent_name,
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id
        } for v in violations])

        with open(violations_file, 'w') as f:
            json.dump(existing_violations, f, indent=2)

        # In strict mode, we would block here
        # For now, just warn

    # Load current graph
    graph_path = Path(f'.claude/graphs/{triad_name}_graph.json')
    graph_data = None
    if graph_path.exists():
        with open(graph_path, 'r') as f:
            graph_data = json.load(f)

    # Apply updates
    graph_data = apply_updates_to_graph(graph_data, updates, agent_name)

    # Save updated graph
    graph_path.parent.mkdir(exist_ok=True)
    with open(graph_path, 'w') as f:
        json.dump(graph_data, f, indent=2)

    print(f"✓ Updated {triad_name} graph: {graph_data['_meta']['node_count']} nodes, {graph_data['_meta']['edge_count']} edges")

if __name__ == '__main__':
    main()
'''

SETTINGS_JSON_TEMPLATE = """{{
  "hooks": {{
    "pre_subagent_start": ".claude/hooks/on_subagent_start.py",
    "post_subagent_end": ".claude/hooks/on_subagent_end.py",
    "on_bridge_transition": ".claude/hooks/on_bridge_transition.py"
  }},
  "triad_system": {{
    "version": "1.0.0",
    "workflow": "{workflow_name}",
    "generated_at": "{timestamp}",
    "triads": {triads_list},
    "bridge_agents": {bridge_agents_list}
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
