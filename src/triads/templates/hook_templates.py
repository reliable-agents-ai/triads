"""
Hook template library for generating lifecycle hooks.

This module contains templates for creating Python hook scripts that
manage knowledge graph context and updates.
"""

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
    "UserPromptSubmit": [
      {{
        "hooks": [
          {{
            "type": "command",
            "command": "python3 .claude/hooks/user_prompt_submit.py"
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
    "km_system": {{
      "detection_enabled": true,
      "confidence_threshold": 0.85,
      "sparse_threshold": 3
    }},
    "note": "KM system auto-detects issues and provides enrichment capabilities"
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

### Knowledge Management

Your system includes intelligent knowledge management:

- **Auto-detection**: Sparse entities and low-confidence facts are detected automatically
- **Enrichment**: Use `/enrich-knowledge` to research sparse entities
- **Status**: Check `/km-status` to view knowledge graph health
- **Agent-driven**: Agents can invoke system agents mid-workflow for critical gaps

### Viewing Knowledge Graphs

Your triads build knowledge graphs as they work:

```bash
# View a triad's graph
cat .claude/graphs/{first_triad}_graph.json | python3 -m json.tool

# Check KM queue
cat .claude/km_queue.json | python3 -m json.tool

# View KM status
cat .claude/km_status.txt
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
│   ├── {first_triad}/   # Domain agents
│   └── system/          # KM system agents
├── hooks/               # Lifecycle automation
├── commands/            # Slash commands (/enrich-knowledge, etc.)
├── graphs/              # Knowledge graphs (created at runtime)
├── constitutional/      # Quality enforcement
└── README.md            # This file
```

## Customization

To modify an agent's behavior:
1. Edit its file in `.claude/agents/[triad]/[agent].md`
2. Agents will use new instructions on next invocation

To adjust KM thresholds:
- Edit `.claude/settings.json` (km_system section)
- Confidence threshold (default: 0.85)
- Sparse threshold (default: 3 properties)

## Support

For issues or questions about the triad system:
- Check: https://github.com/anthropics/claude-code
- Docs: https://docs.claude.com/en/docs/claude-code
"""


__all__ = [
    "SETTINGS_JSON_TEMPLATE",
    "README_TEMPLATE",
]
