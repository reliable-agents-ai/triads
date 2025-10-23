# MCP Tools Catalog

**Version**: v0.10.0
**Total Tools**: 13
**Status**: Production Ready

---

## Overview

This document catalogs all MCP-compliant tools provided by the Triads tool abstraction layer. Each tool follows the Model Context Protocol specification and returns `ToolResult` objects.

---

## Knowledge Tools (5 tools)

### 1. query_graph

**Purpose**: Search knowledge graph by query string

**Parameters:**
```json
{
  "triad": {
    "type": "string",
    "description": "Triad name to search",
    "required": true
  },
  "query": {
    "type": "string",
    "description": "Search query (case-insensitive, searches labels and descriptions)",
    "required": true
  },
  "min_confidence": {
    "type": "number",
    "description": "Minimum confidence threshold (0.0-1.0)",
    "required": false,
    "default": 0.0
  }
}
```

**Returns:**
```json
{
  "success": true,
  "content": [
    {
      "type": "text",
      "text": "Query Results for 'OAuth':\n\n1. oauth_decision\n   Type: Decision\n   Label: OAuth2 vs JWT\n   Confidence: 0.95\n   Description: Chose OAuth2 for authentication...\n\n..."
    }
  ]
}
```

**Python Usage:**
```python
from triads.tools.knowledge import KnowledgeTools

result = KnowledgeTools.query_graph(
    triad="design",
    query="OAuth",
    min_confidence=0.85
)

if result.success:
    print(result.content[0]["text"])
```

**CLI Usage:**
```bash
python -m triads.tools.knowledge query_graph \
    --triad design \
    --query OAuth \
    --min-confidence 0.85
```

**Use Cases:**
- Search for decisions related to a topic
- Find all nodes mentioning a technology
- Filter by confidence level
- Knowledge discovery

---

### 2. get_graph_status

**Purpose**: Get metadata and health status for knowledge graphs

**Parameters:**
```json
{
  "triad": {
    "type": "string",
    "description": "Optional triad name (omit for all graphs)",
    "required": false
  }
}
```

**Returns:**
```json
{
  "success": true,
  "content": [
    {
      "type": "text",
      "text": "Knowledge Graph Status:\n\nTriad: design\n  Nodes: 31\n  Edges: 12\n  Status: Valid\n  Last Updated: 2025-10-23T10:30:00\n\n..."
    }
  ]
}
```

**Python Usage:**
```python
# All graphs
result = KnowledgeTools.get_graph_status()

# Single graph
result = KnowledgeTools.get_graph_status(triad="design")
```

**Use Cases:**
- Health checks
- Monitoring graph size
- Detecting integrity issues
- Dashboard metrics

---

### 3. show_node

**Purpose**: Get detailed information about a specific node

**Parameters:**
```json
{
  "node_id": {
    "type": "string",
    "description": "Node identifier",
    "required": true
  },
  "triad": {
    "type": "string",
    "description": "Optional triad name (omit to search all)",
    "required": false
  }
}
```

**Returns:**
```json
{
  "success": true,
  "content": [
    {
      "type": "text",
      "text": "Node Details:\n\nID: oauth_decision\nType: Decision\nLabel: OAuth2 vs JWT\nConfidence: 0.95\nCreated: 2025-10-15\nCreated By: solution-architect\n\nDescription:\nChose OAuth2 for authentication because...\n\nAlternatives:\n- JWT tokens (rejected - stateless issues)\n- Session cookies (rejected - scaling issues)\n\n..."
    }
  ]
}
```

**Python Usage:**
```python
result = KnowledgeTools.show_node(
    node_id="oauth_decision",
    triad="design"
)
```

**Use Cases:**
- View decision details
- Audit ADRs
- Link from other tools
- Deep dives

---

### 4. list_triads

**Purpose**: List all available triads with node counts

**Parameters:** None

**Returns:**
```json
{
  "success": true,
  "content": [
    {
      "type": "text",
      "text": "Available Knowledge Graphs:\n\n  default: 40 nodes\n  deployment: 6 nodes\n  design: 31 nodes\n  implementation: 81 nodes\n  ..."
    }
  ]
}
```

**Python Usage:**
```python
result = KnowledgeTools.list_triads()
```

**Use Cases:**
- Discovery
- Tab completion
- Validation
- Overview

---

### 5. get_session_context

**Purpose**: Get full session context for hooks (all graphs + routing directives)

**Parameters:**
```json
{
  "project_dir": {
    "type": "string",
    "description": "Optional project directory (defaults to current)",
    "required": false
  }
}
```

**Returns:**
```json
{
  "success": true,
  "content": [
    {
      "type": "text",
      "text": "Session Knowledge Context:\n\nKnowledge Graph Status:\n\n[Full status of all graphs]\n\n..."
    }
  ]
}
```

**Python Usage:**
```python
result = KnowledgeTools.get_session_context()
```

**Use Cases:**
- Session hooks
- Agent context loading
- Full system overview

---

## Integrity Tools (3 tools)

### 6. check_graph

**Purpose**: Validate single knowledge graph integrity

**Parameters:**
```json
{
  "triad": {
    "type": "string",
    "description": "Triad name to validate",
    "required": true
  }
}
```

**Returns:**
```json
{
  "success": true,
  "content": [
    {
      "type": "text",
      "text": "Graph Validation Results:\n\nTriad: design\nStatus: INVALID\n\nErrors:\n- Edge source 'missing_node' does not exist\n- Node 'orphan_node' has no edges\n\n..."
    }
  ]
}
```

**Python Usage:**
```python
from triads.tools.integrity import IntegrityTools

result = IntegrityTools.check_graph(triad="design")
```

**Use Cases:**
- Pre-commit validation
- CI/CD checks
- Manual integrity checks

---

### 7. check_all_graphs

**Purpose**: Validate all knowledge graphs

**Parameters:** None

**Returns:**
```json
{
  "success": true,
  "content": [
    {
      "type": "text",
      "text": "All Graphs Validation:\n\nSummary:\n- Valid: 7 graphs\n- Invalid: 2 graphs\n\nDetails:\n\n[Per-graph results]\n\n..."
    }
  ]
}
```

**Python Usage:**
```python
result = IntegrityTools.check_all_graphs()
```

**Use Cases:**
- System health checks
- CI/CD pipelines
- Integrity monitoring

---

### 8. repair_graph

**Purpose**: Repair graph integrity issues with optional backup

**Parameters:**
```json
{
  "triad": {
    "type": "string",
    "description": "Triad name to repair",
    "required": true
  },
  "create_backup": {
    "type": "boolean",
    "description": "Create backup before repair",
    "required": false,
    "default": true
  }
}
```

**Returns:**
```json
{
  "success": true,
  "content": [
    {
      "type": "text",
      "text": "Graph Repair Results:\n\nTriad: design\nBackup Created: design_graph_backup_20251023_143000.json\n\nRepairs:\n- Removed orphaned edge to 'missing_node'\n- Added missing node metadata\n\nStatus: Valid\n"
    }
  ]
}
```

**Python Usage:**
```python
result = IntegrityTools.repair_graph(
    triad="design",
    create_backup=True
)
```

**Use Cases:**
- Fix broken references
- Clean up orphaned nodes
- Automated maintenance

---

## Router Tools (2 tools)

### 9. route_prompt

**Purpose**: Semantic routing for user prompts to appropriate triad

**Parameters:**
```json
{
  "prompt": {
    "type": "string",
    "description": "User prompt to route",
    "required": true
  }
}
```

**Returns:**
```json
{
  "success": true,
  "content": [
    {
      "type": "text",
      "text": "Routing Decision:\n\nPrompt: 'How should we architect the OAuth system?'\nRecommended Triad: design\nConfidence: 0.92\nMethod: semantic_embedding\n\nReasoning:\nPrompt contains architecture keywords and decision-making language.\n"
    }
  ]
}
```

**Python Usage:**
```python
from triads.tools.router import RouterTools

result = RouterTools.route_prompt(
    prompt="How should we architect OAuth?"
)
```

**Use Cases:**
- Supervisor routing
- User prompt classification
- Training mode

---

### 10. get_current_triad

**Purpose**: Get currently active triad from router state

**Parameters:** None

**Returns:**
```json
{
  "success": true,
  "content": [
    {
      "type": "text",
      "text": "Current Triad: implementation\n\nLast Updated: 2025-10-23T14:30:00\nMethod: manual_selection\nPrevious: design\n"
    }
  ]
}
```

**Python Usage:**
```python
result = RouterTools.get_current_triad()
```

**Use Cases:**
- Context awareness
- Workflow tracking
- State queries

---

## Workflow Tools (3 tools)

### 11. get_workflow_state

**Purpose**: Get current workflow instance state

**Parameters:**
```json
{
  "workflow_id": {
    "type": "string",
    "description": "Optional workflow instance ID",
    "required": false
  }
}
```

**Returns:**
```json
{
  "success": true,
  "content": [
    {
      "type": "text",
      "text": "Workflow State:\n\nID: feature_oauth_20251023\nType: feature_development\nCurrent Phase: implementation\nStatus: in_progress\n\nCompleted Phases:\n- idea_validation (2025-10-21)\n- design (2025-10-22)\n\nNext Phase: testing\n"
    }
  ]
}
```

**Python Usage:**
```python
from triads.tools.workflow import WorkflowTools

result = WorkflowTools.get_workflow_state()
```

**Use Cases:**
- Workflow tracking
- Progress monitoring
- Phase validation

---

### 12. update_workflow_state

**Purpose**: Update workflow instance state (advance phase, mark complete, etc.)

**Parameters:**
```json
{
  "workflow_id": {
    "type": "string",
    "description": "Workflow instance ID",
    "required": true
  },
  "action": {
    "type": "string",
    "enum": ["advance_phase", "mark_complete", "mark_deviation"],
    "required": true
  },
  "data": {
    "type": "object",
    "description": "Action-specific data",
    "required": false
  }
}
```

**Python Usage:**
```python
result = WorkflowTools.update_workflow_state(
    workflow_id="feature_oauth_20251023",
    action="advance_phase",
    data={"next_phase": "testing"}
)
```

**Use Cases:**
- Workflow progression
- Phase transitions
- State management

---

### 13. validate_workflow_step

**Purpose**: Validate if a workflow step transition is allowed

**Parameters:**
```json
{
  "workflow_id": {
    "type": "string",
    "description": "Workflow instance ID",
    "required": true
  },
  "from_phase": {
    "type": "string",
    "description": "Current phase",
    "required": true
  },
  "to_phase": {
    "type": "string",
    "description": "Desired next phase",
    "required": true
  }
}
```

**Returns:**
```json
{
  "success": true,
  "content": [
    {
      "type": "text",
      "text": "Validation Result: ALLOWED\n\nTransition: implementation → testing\nWorkflow: feature_development\n\nRequirements Met:\n- implementation phase completed\n- code metrics within bounds\n- tests written\n"
    }
  ]
}
```

**Python Usage:**
```python
result = WorkflowTools.validate_workflow_step(
    workflow_id="feature_oauth_20251023",
    from_phase="implementation",
    to_phase="testing"
)
```

**Use Cases:**
- Pre-transition validation
- Workflow enforcement
- Guard rails

---

## Generator Tools (1 tool)

### 14. generate_agents

**Purpose**: Generate agent files from workflow template

**Parameters:**
```json
{
  "workflow_name": {
    "type": "string",
    "description": "Workflow template name",
    "required": true
  },
  "domain": {
    "type": "string",
    "description": "Domain context (e.g., 'software_development')",
    "required": true
  }
}
```

**Returns** (Resource type, not text):
```json
{
  "success": true,
  "content": [
    {
      "type": "resource",
      "uri": "file://.claude/agents/discovery/research-analyst.md",
      "mimeType": "text/markdown",
      "text": "---\nname: Research Analyst\nrole: analyst\n...\n"
    },
    {
      "type": "resource",
      "uri": "file://.claude/agents/discovery/community-researcher.md",
      "mimeType": "text/markdown",
      "text": "---\nname: Community Researcher\n...\n"
    }
  ]
}
```

**Python Usage:**
```python
from triads.tools.generator import GeneratorTools

result = GeneratorTools.generate_agents(
    workflow_name="debugging",
    domain="software_development"
)

for resource in result.content:
    print(f"Generated: {resource['uri']}")
```

**Use Cases:**
- Workflow generation
- Agent creation
- Template instantiation

---

## Error Handling

All tools follow consistent error handling:

### Success Response

```json
{
  "success": true,
  "content": [...],
  "error": null
}
```

### Error Response

```json
{
  "success": false,
  "content": [],
  "error": "Triad 'invalid' not found. Available triads: default, design, implementation"
}
```

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "Triad not found" | Invalid triad name | Use `list_triads` to see available |
| "Node not found" | Invalid node_id | Check node exists in graph |
| "Graph file not found" | Missing .json file | Initialize graph directory |
| "Invalid confidence" | Value outside 0.0-1.0 | Use valid range |
| "Validation failed" | Integrity check failed | Use `repair_graph` |

---

## MCP Server Integration

### Server Configuration

```json
{
  "mcpServers": {
    "triads": {
      "command": "python",
      "args": ["-m", "triads.mcp.server"],
      "env": {
        "CLAUDE_PROJECT_DIR": "/path/to/project"
      }
    }
  }
}
```

### Tool Discovery

MCP clients can discover all 13 tools via `tools/list` endpoint.

### Tool Invocation

```json
{
  "method": "tools/call",
  "params": {
    "name": "query_graph",
    "arguments": {
      "triad": "design",
      "query": "OAuth",
      "min_confidence": 0.85
    }
  }
}
```

---

## Performance Characteristics

| Tool | P50 Latency | P95 Latency | Notes |
|------|-------------|-------------|-------|
| query_graph | 10ms | 50ms | Depends on graph size |
| get_graph_status | 5ms | 20ms | Fast metadata access |
| show_node | 8ms | 30ms | Single node lookup |
| list_triads | 3ms | 10ms | Directory scan |
| get_session_context | 50ms | 100ms | Loads all graphs |
| check_graph | 20ms | 80ms | Validation logic |
| check_all_graphs | 100ms | 300ms | Validates all graphs |
| repair_graph | 50ms | 200ms | Includes backup |
| route_prompt | 15ms | 30ms | Semantic embedding |
| generate_agents | 100ms | 300ms | Template processing |

**Measured on**: M2 MacBook Pro, 9 graphs, ~250 total nodes

---

## Versioning

Tools follow semantic versioning:

- **v0.10.0+**: Current production version
- **Stability**: Production ready, stable API
- **Breaking Changes**: Major version bumps only
- **Deprecation**: 6-month notice for removals

---

## References

- **Architecture**: [TOOL_ARCHITECTURE.md](./TOOL_ARCHITECTURE.md)
- **MCP Spec**: https://modelcontextprotocol.io/
- **Testing**: [TESTING_STRATEGY.md](./TESTING_STRATEGY.md)
- **Source**: `src/triads/tools/`

---

**Document Version**: 1.0
**Last Updated**: 2025-10-23
