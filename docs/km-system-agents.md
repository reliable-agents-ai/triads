# Knowledge Management System Agents

## Overview

System agents are specialized Claude Code agents that automatically resolve quality issues detected in knowledge graphs. They work autonomously to enrich sparse entities, verify low-confidence claims, and add missing evidence.

## Available System Agents

### 1. research-agent

**Purpose:** Enrich sparse entities with comprehensive information

**Handles:** `sparse_entity` issues (entities with < 3 meaningful properties)

**Location:** `.claude/agents/system/research-agent.md`

**Process:**
1. Receives sparse entity (e.g., "JWT Library" with only 1 property)
2. Researches the entity (codebase search, web search, docs)
3. Adds meaningful properties (file_path, dependencies, purpose, etc.)
4. Cites all sources with verifiable evidence
5. Updates graph with [GRAPH_UPDATE] blocks

**Example Task:**
```
Enrich the sparse entity 'JWT Library' (jwt_lib) in the discovery triad.
Currently has only 1 properties.
Research and add meaningful properties to this node.
```

---

### 2. verification-agent

**Purpose:** Validate questionable information and add missing evidence

**Handles:**
- `low_confidence` issues (confidence < 0.85)
- `missing_evidence` issues (no evidence field)

**Location:** `.claude/agents/system/verification-agent.md`

**Process:**
1. Receives low-confidence or missing-evidence node
2. Investigates the claim through multiple sources
3. Either:
   - Verifies and strengthens (raises confidence to 0.85+)
   - Converts to Uncertainty node (if unverifiable)
   - Corrects incorrect information
4. Always adds comprehensive evidence

**Example Task:**
```
Verify the low-confidence node 'OAuth2 Decision' (oauth2_choice) in the design triad.
Current confidence: 0.72.
Validate the information and increase confidence, or mark as Uncertainty.
```

---

## Agent Management Functions

### get_system_agent()

**Purpose:** Get path to a system agent file

**Signature:**
```python
def get_system_agent(agent_name: str) -> Path | None
```

**Example:**
```python
from triads.km.system_agents import get_system_agent

agent_path = get_system_agent("research-agent")
# => Path('.claude/agents/system/research-agent.md')
```

---

### list_system_agents()

**Purpose:** List all available system agents

**Signature:**
```python
def list_system_agents() -> list[str]
```

**Example:**
```python
from triads.km.system_agents import list_system_agents

agents = list_system_agents()
# => ['research-agent', 'verification-agent']
```

---

### validate_agent_file()

**Purpose:** Validate agent file structure

**Signature:**
```python
def validate_agent_file(agent_path: Path) -> tuple[bool, list[str]]
```

**Returns:** `(is_valid, list_of_errors)`

**Checks:**
- File exists
- Has YAML frontmatter (starts with `---`)
- Required fields present: `name`, `role`
- Has content after frontmatter

**Example:**
```python
from triads.km.system_agents import get_system_agent, validate_agent_file

agent_path = get_system_agent("research-agent")
is_valid, errors = validate_agent_file(agent_path)

if is_valid:
    print("Agent file is valid")
else:
    print(f"Errors: {errors}")
```

---

### parse_agent_frontmatter()

**Purpose:** Parse YAML frontmatter from agent file

**Signature:**
```python
def parse_agent_frontmatter(agent_path: Path) -> dict[str, Any] | None
```

**Example:**
```python
from triads.km.system_agents import get_system_agent, parse_agent_frontmatter

agent_path = get_system_agent("verification-agent")
frontmatter = parse_agent_frontmatter(agent_path)

print(frontmatter)
# => {
#     'name': 'verification-agent',
#     'role': 'Knowledge validation specialist',
#     'type': 'system',
#     'purpose': 'Verify low-confidence claims and add missing evidence'
# }
```

---

### get_agent_for_issue_type()

**Purpose:** Map issue type to appropriate system agent

**Signature:**
```python
def get_agent_for_issue_type(issue_type: str) -> str
```

**Routing:**
| Issue Type | Agent |
|------------|-------|
| `sparse_entity` | `research-agent` |
| `low_confidence` | `verification-agent` |
| `missing_evidence` | `verification-agent` |

**Example:**
```python
from triads.km.system_agents import get_agent_for_issue_type

agent = get_agent_for_issue_type("sparse_entity")
# => "research-agent"

agent = get_agent_for_issue_type("low_confidence")
# => "verification-agent"
```

---

### format_agent_task()

**Purpose:** Format task description for agent invocation

**Signature:**
```python
def format_agent_task(issue: dict[str, Any]) -> str
```

**Example:**
```python
from triads.km.system_agents import format_agent_task

issue = {
    "type": "sparse_entity",
    "triad": "discovery",
    "node_id": "jwt_lib",
    "label": "JWT Library",
    "property_count": 1
}

task = format_agent_task(issue)
print(task)
# => "Enrich the sparse entity 'JWT Library' (jwt_lib) in the discovery triad.
#     Currently has only 1 properties.
#     Research and add meaningful properties to this node."
```

---

## Usage Patterns

### Pattern 1: Manual Agent Invocation

```python
from triads.km.system_agents import (
    get_agent_for_issue_type,
    format_agent_task,
    get_system_agent
)

# Load issue from queue
issue = {
    "type": "sparse_entity",
    "node_id": "jwt_lib",
    "label": "JWT Library",
    "triad": "discovery",
    "property_count": 1
}

# Determine which agent to use
agent_name = get_agent_for_issue_type(issue["type"])
# => "research-agent"

# Format task description
task = format_agent_task(issue)

# Get agent path
agent_path = get_system_agent(agent_name)

# Invoke agent (in Claude Code CLI)
# Start research-agent: Enrich the sparse entity 'JWT Library' (jwt_lib)...
```

### Pattern 2: Batch Processing

```python
import json
from triads.km.system_agents import get_agent_for_issue_type, format_agent_task

# Load all issues
with open(".claude/km_queue.json", "r") as f:
    queue = json.load(f)

# Group by agent
by_agent = {}
for issue in queue["issues"]:
    agent = get_agent_for_issue_type(issue["type"])
    if agent not in by_agent:
        by_agent[agent] = []
    by_agent[agent].append(issue)

# Process each agent's issues
for agent_name, issues in by_agent.items():
    print(f"\n{agent_name} has {len(issues)} issues:")
    for issue in issues:
        task = format_agent_task(issue)
        print(f"  - {task[:80]}...")
```

### Pattern 3: Validation Check

```python
from triads.km.system_agents import list_system_agents, validate_agent_file, get_system_agent

# Validate all system agents
agents = list_system_agents()
for agent_name in agents:
    agent_path = get_system_agent(agent_name)
    is_valid, errors = validate_agent_file(agent_path)

    if is_valid:
        print(f"✅ {agent_name}: Valid")
    else:
        print(f"❌ {agent_name}: Invalid")
        for error in errors:
            print(f"   - {error}")
```

---

## Integration with KM System

### Flow: Detection → Formatting → Status File → Agent Invocation

```
1. Graph Update
   ↓
2. on_stop.py hook detects issues
   ↓
3. Issues added to km_queue.json
   ↓
4. write_km_status_file() creates km_status.md
   ↓
5. User/system invokes appropriate agent
   ↓
6. Agent reads status file
   ↓
7. Agent researches/verifies
   ↓
8. Agent outputs [GRAPH_UPDATE] blocks
   ↓
9. on_stop.py updates graph
   ↓
10. Issue removed from queue (if resolved)
```

---

## Agent File Structure

### Required Frontmatter

```yaml
---
name: agent-name
role: Brief role description
type: system
purpose: What this agent does
---
```

### Content Sections

1. **Role**: What the agent is responsible for
2. **Responsibilities**: Detailed task breakdown
3. **Process**: Step-by-step workflow
4. **Output Format**: [GRAPH_UPDATE] examples
5. **Constitutional Compliance**: TRUST framework adherence
6. **Examples**: Real-world use cases
7. **Quality Checklist**: Pre-output verification
8. **Common Mistakes**: What to avoid

---

## Testing

### Unit Tests

Comprehensive test suite in `tests/test_km/test_system_agents.py`:

- `test_system_agents_directory_exists`: Directory structure
- `test_get_system_agent_*`: Agent file discovery
- `test_list_system_agents`: Listing functionality
- `test_validate_agent_file_*`: File validation
- `test_parse_agent_frontmatter`: Frontmatter parsing
- `test_get_agent_for_issue_type_*`: Issue routing
- `test_format_agent_task_*`: Task formatting

Run tests:
```bash
uv run pytest tests/test_km/test_system_agents.py -v
```

### Integration Testing

Manual integration test:

1. Create test issue:
```bash
echo '{
  "issues": [{
    "type": "sparse_entity",
    "triad": "test",
    "node_id": "test_node",
    "label": "Test Entity",
    "property_count": 1,
    "priority": "medium"
  }],
  "issue_count": 1
}' > .claude/km_queue.json
```

2. Generate status file:
```python
from triads.km.formatting import write_km_status_file
write_km_status_file()
```

3. Check status file:
```bash
cat .claude/km_status.md
```

4. Invoke agent:
```
Start research-agent: Enrich the sparse entity 'Test Entity' (test_node) in the test triad.
```

---

## Future Enhancements

### 1. Automated Agent Invocation

```python
# Automatically invoke agents for high-priority issues
def auto_resolve_high_priority():
    with open(".claude/km_queue.json") as f:
        queue = json.load(f)

    high_priority = [i for i in queue["issues"] if i["priority"] == "high"]

    for issue in high_priority:
        agent = get_agent_for_issue_type(issue["type"])
        task = format_agent_task(issue)
        # Invoke agent via Claude Code API
        invoke_agent(agent, task)
```

### 2. Agent Performance Metrics

Track resolution success and time:

```json
{
  "research-agent": {
    "assigned": 15,
    "resolved": 12,
    "failed": 3,
    "avg_resolution_time": "2.5 minutes"
  },
  "verification-agent": {
    "assigned": 8,
    "resolved": 8,
    "failed": 0,
    "avg_resolution_time": "1.8 minutes"
  }
}
```

### 3. Custom System Agents

Create custom agents for project-specific issues:

```bash
# Create new agent
cp .claude/agents/system/research-agent.md \
   .claude/agents/system/security-audit-agent.md

# Edit for security-specific validation
# Add to routing in system_agents.py
```

---

## Related Documentation

- [Detection System](km-detection.md) - How issues are detected
- [Formatting System](km-formatting.md) - How issues are formatted
- [User Commands](km-user-commands.md) - Manual issue management (Phase 4)
- [Fresh Context](km-fresh-context.md) - Agent context injection (Phase 5)

---

## Configuration

### Agent Directory

```python
# In src/triads/km/system_agents.py
SYSTEM_AGENTS_DIR = Path(".claude/agents/system")
```

### Agent Routing

```python
ISSUE_TO_AGENT = {
    "sparse_entity": "research-agent",
    "low_confidence": "verification-agent",
    "missing_evidence": "verification-agent",
}
```

To add custom routing:
```python
ISSUE_TO_AGENT["outdated_info"] = "refresh-agent"
```

---

## Best Practices

### For Agent Authors

1. **Follow frontmatter schema**: Include all required fields
2. **Provide examples**: Real-world use cases help agents understand
3. **Include quality checklist**: Pre-output verification prevents errors
4. **Document constitutional compliance**: TRUST framework adherence
5. **Test agents manually**: Verify they produce correct [GRAPH_UPDATE] blocks

### For Agent Users

1. **Review status file first**: Understand what needs resolution
2. **Invoke appropriate agent**: Use get_agent_for_issue_type()
3. **Monitor graph updates**: Check that issues are resolved
4. **Validate results**: Ensure confidence scores and evidence are adequate
5. **Clear resolved issues**: Remove from queue after successful resolution

---

## Troubleshooting

### Agent Not Found

**Problem:** `get_system_agent()` returns `None`

**Solution:**
```bash
# Check agent directory exists
ls -la .claude/agents/system/

# Verify agent file naming
ls .claude/agents/system/*.md

# Agent names must match: {name}.md
```

### Invalid Agent File

**Problem:** `validate_agent_file()` returns errors

**Solution:**
```python
from triads.km.system_agents import validate_agent_file, get_system_agent

agent_path = get_system_agent("research-agent")
is_valid, errors = validate_agent_file(agent_path)

for error in errors:
    print(error)  # Fix each error

# Common issues:
# - Missing frontmatter (must start with ---)
# - Missing required field (name, role)
# - Empty content after frontmatter
```

### Wrong Agent for Issue

**Problem:** Issue routed to wrong agent

**Solution:**
```python
# Check routing configuration
from triads.km.system_agents import ISSUE_TO_AGENT
print(ISSUE_TO_AGENT)

# Update if needed
ISSUE_TO_AGENT["your_issue_type"] = "your-agent"
```

---

## Implementation Notes

### Type Safety

Full type annotations for mypy:
```python
def get_system_agent(agent_name: str) -> Path | None
def list_system_agents() -> list[str]
def validate_agent_file(agent_path: Path) -> tuple[bool, list[str]]
def parse_agent_frontmatter(agent_path: Path) -> dict[str, Any] | None
def get_agent_for_issue_type(issue_type: str) -> str
def format_agent_task(issue: dict[str, Any]) -> str
```

### Error Handling

- `get_system_agent()` returns `None` if agent not found (not an error)
- `get_agent_for_issue_type()` raises `ValueError` for unknown types
- `validate_agent_file()` returns errors list (never raises)
- `parse_agent_frontmatter()` returns `None` for invalid files

### Performance

- File operations are cached by OS
- Agent listing is O(n) where n = number of .md files
- Validation uses regex for efficient frontmatter parsing
- Task formatting is string interpolation (fast)

### Testing Strategy

- Unit tests for each function
- Integration tests with actual agent files
- Validation tests with invalid agents (missing fields, etc.)
- 86% coverage on system_agents.py
