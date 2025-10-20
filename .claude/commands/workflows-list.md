# Workflows List Command

List all workflow instances with their current status.

## Usage

**List all workflows:**
```python
from triads.workflow_enforcement.instance_manager import WorkflowInstanceManager

manager = WorkflowInstanceManager()
instances = manager.list_instances()

for instance in instances:
    print(f"{instance['instance_id']}: {instance['title']}")
    print(f"  Status: {instance['status']}")
    print(f"  Current: {instance['current_triad']}")
    print()
```

**List only active workflows:**
```python
from triads.workflow_enforcement.instance_manager import WorkflowInstanceManager

manager = WorkflowInstanceManager()
active = manager.list_instances(status="in_progress")

print(f"Active Workflows: {len(active)}")
for instance in active:
    print(f"- {instance['title']} ({instance['current_triad']})")
```

**List completed workflows:**
```python
from triads.workflow_enforcement.instance_manager import WorkflowInstanceManager

manager = WorkflowInstanceManager()
completed = manager.list_instances(status="completed")

print(f"Completed Workflows: {len(completed)}")
for instance in completed:
    print(f"- {instance['title']} (finished {instance.get('completed_at', 'unknown')})")
```

## Output

Shows a list of workflow instances with:
- **instance_id**: Unique identifier (e.g., "oauth2-integration-20251017-110234")
- **title**: Human-readable workflow title
- **workflow_type**: Type of workflow (idea-validation, design, implementation, etc.)
- **status**: Current status (in_progress, completed, abandoned)
- **started_at**: Timestamp when workflow started
- **current_triad**: Current triad in the workflow sequence
- **completed_at**: Timestamp when workflow completed (if applicable)

## Example

```
Active Workflows (3):

1. **OAuth2 Integration**
   ID: `oauth2-integration-20251017-110234`
   Current: implementation
   Age: 2d

2. **API Rate Limiting**
   ID: `api-rate-limiting-20251018-093012`
   Current: design
   Age: 1d

3. **Documentation Overhaul**
   ID: `docs-overhaul-20251019-140521`
   Current: garden-tending
   Age: 8h
```

## See Also

- `/workflows resume` - Resume a specific workflow
- `/workflows abandon` - Abandon a workflow
- `/knowledge-status` - View knowledge graph status
