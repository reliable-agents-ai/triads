# Workflows Resume Command

Resume a specific workflow instance by ID.

## Usage

**Resume a workflow:**
```python
from triads.workflow_enforcement.instance_manager import WorkflowInstanceManager

manager = WorkflowInstanceManager()

# Load the instance
instance_id = "oauth2-integration-20251017-110234"
instance = manager.load_instance(instance_id)

print(f"Resuming: {instance.title}")
print(f"Current triad: {instance.current_triad}")
print(f"Completed triads: {', '.join(instance.completed_triads)}")
print()
print("Next steps:")
# Show what needs to be done in current triad
```

**Get instance details:**
```python
from triads.workflow_enforcement.instance_manager import WorkflowInstanceManager

manager = WorkflowInstanceManager()
instance = manager.load_instance("oauth2-integration-20251017-110234")

# Access instance properties
print(f"Title: {instance.title}")
print(f"Type: {instance.workflow_type}")
print(f"Started: {instance.started_at}")
print(f"Current: {instance.current_triad}")
print(f"Completed: {instance.completed_triads}")
print(f"Metadata: {instance.metadata}")
```

## Arguments

- **instance_id** (required): The unique identifier of the workflow instance to resume
  - Format: `{title-slug}-{timestamp}`
  - Example: `oauth2-integration-20251017-110234`

## Output

Shows the workflow context including:
- **title**: Workflow name
- **current_triad**: Which triad is active
- **completed_triads**: List of triads already completed
- **workflow_progress**: Progress through the workflow sequence
- **workflow_deviations**: Any deviations from standard workflow
- **significance_metrics**: Metrics about the workflow (LoC, files changed, etc.)

## Example

```
Resuming Workflow: OAuth2 Integration
Instance ID: oauth2-integration-20251017-110234

Current Triad: implementation
Completed Triads: idea-validation, design

Progress:
✓ idea-validation (completed 2024-10-17 11:05:23)
✓ design (completed 2024-10-17 12:30:45)
→ implementation (in progress since 2024-10-17 13:15:12)
  □ garden-tending (pending)
  □ deployment (pending)

Next Steps:
- Complete implementation triad
- Senior Developer: Write production code
- Test Engineer: Create comprehensive tests

To mark current triad complete:
Use bridge agent (test-engineer) to transition to garden-tending
```

## See Also

- `/workflows list` - List all workflows
- `/workflows abandon` - Abandon a workflow
- `/knowledge-show` - View knowledge graph details for this workflow
