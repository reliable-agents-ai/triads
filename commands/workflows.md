# Workflows Command

Manage workflow instances: list, show details, resume, view history, abandon, and analyze deviation patterns.

## Usage

### List all workflow instances

```python
from triads.workflow_enforcement.cli import list_workflows
print(list_workflows())
```

### List instances by status

```python
from triads.workflow_enforcement.cli import list_workflows

# Show only active workflows
print(list_workflows(status="in_progress"))

# Show only completed workflows
print(list_workflows(status="completed"))

# Show only abandoned workflows
print(list_workflows(status="abandoned"))
```

### Show instance details

```python
from triads.workflow_enforcement.cli import show_workflow
print(show_workflow("feature-oauth2-20251017-100523"))
```

### Resume a workflow

```python
from triads.workflow_enforcement.cli import resume_workflow
print(resume_workflow("feature-oauth2-20251017-100523"))
```

### View deviation history

```python
from triads.workflow_enforcement.cli import workflow_history
print(workflow_history("feature-oauth2-20251017-100523"))
```

### Abandon a workflow

```python
from triads.workflow_enforcement.cli import abandon_workflow
print(abandon_workflow(
    "feature-oauth2-20251017-100523",
    "Project cancelled, pivoting to different approach"
))
```

### Analyze deviations

```python
from triads.workflow_enforcement.cli import analyze_deviations
print(analyze_deviations())
```

## Commands

### `/workflows list [--status STATUS]`

List all workflow instances, optionally filtered by status.

**Status options**: `in_progress`, `completed`, `abandoned`

**Example output**:
```
Found 3 workflow instance(s):

  feature-oauth2-20251017-100523
    Title: OAuth2 Integration
    Status: in_progress
    Started: 2025-10-17T10:05:23Z
    Current: implementation

  bugfix-auth-20251016-143000
    Title: Fix Authentication Bug
    Status: completed
    Started: 2025-10-16T14:30:00Z
    Current: deployment
```

### `/workflows show <instance-id>`

Show detailed information about a specific workflow instance.

**Example output**:
```
Workflow Instance: feature-oauth2-20251017-100523

Title: OAuth2 Integration
Type: software-development
Status: in_progress
Started by: jane.doe@company.com
Started at: 2025-10-17T10:05:23Z

Progress:
  Current triad: implementation
  Completed: 2 triad(s)
  Skipped: 1 triad(s)
  Deviations: 1

Completed Triads:
  ✓ idea-validation (9.6 minutes)
  ✓ design (15.3 minutes)

Workflow Deviations:
  • skip_forward: Design completed in Figma with team
    idea-validation → implementation
    Skipped: design

Significance Metrics:
  Content: 257 lines
  Components: 8
  Complexity: substantial
```

### `/workflows resume <instance-id>`

Get guidance for resuming a workflow instance.

**Example output**:
```
Resuming workflow: OAuth2 Integration

Current triad: implementation
Progress: 2/5 triads completed

Continue with current: Start implementation
Or proceed to next: Start garden-tending
```

### `/workflows history <instance-id>`

Show deviation history and analytics for a workflow instance.

**Example output**:
```
Deviation History: OAuth2 Integration

Total deviations: 3

By Type:
  skip_forward: 2
  skip_backward: 1

Chronological History:
1. [2025-10-17T10:30:00Z] skip_forward
   idea-validation → implementation
   Reason: Design completed in Figma with team
   Skipped: design

2. [2025-10-17T12:15:00Z] skip_backward
   implementation → design
   Reason: Found design flaw during implementation

3. [2025-10-17T14:00:00Z] skip_forward
   design → garden-tending
   Reason: Implementation complete, moving to cleanup
   Skipped: implementation
```

### `/workflows abandon <instance-id> --reason "..."`

Mark a workflow instance as abandoned. Requires a reason.

**Example output**:
```
✓ Workflow abandoned: feature-oauth2-20251017-100523
Title: OAuth2 Integration
Reason: Project cancelled, pivoting to different approach
Moved to: .claude/workflows/abandoned/feature-oauth2-20251017-100523.json
```

### `/workflows analyze`

Analyze deviation patterns across all workflow instances.

**Example output**:
```
Workflow Deviation Analytics

Total Instances: 15
Instances with Deviations: 12 (80.0%)
Total Deviations: 34
Average per Instance: 2.3

Deviation Types:
  skip_forward: 22 (64.7%)
  skip_backward: 8 (23.5%)
  gate_skip: 4 (11.8%)

Most Skipped Triads:
  design: 12 times
  garden-tending: 8 times
  idea-validation: 2 times

Common Reason Keywords:
  completed: 8 occurrences
  external: 6 occurrences
  figma: 5 occurrences
  meeting: 4 occurrences

Recommendations:
  • 'design' is frequently skipped (12 times)
    Consider: Is this triad necessary? Should it be optional?
  • 50%+ deviations are 'skip_forward'
    Consider: Is workflow sequence realistic? Should enforcement be more flexible?
```

## Finding Instance IDs

If you don't know the exact instance ID:

1. **Use list**: `list_workflows()` to see all instances
2. **Filter by status**: `list_workflows(status="in_progress")` to narrow down
3. **Check recent**: Instances are sorted by started_at (most recent first)

Instance IDs are shown in list output and have format: `{slug}-{timestamp}-{microseconds}`

## Tips

1. **List first**: Use `/workflows list` to find instance IDs
2. **Filter by status**: Narrow down to active/completed/abandoned workflows
3. **Show details**: Use `/workflows show` to see full progress and deviations
4. **Resume guidance**: Use `/workflows resume` to get next step suggestions
5. **Track patterns**: Use `/workflows analyze` to identify workflow improvements

## Common Errors

### "Instance not found"
- Double-check instance ID spelling (case-sensitive)
- Use `/workflows list` to see all instances
- Instance may have been moved (check all statuses)

### "Invalid status"
- Status must be one of: `in_progress`, `completed`, `abandoned`
- Use exact values (case-sensitive)

### "Reason required"
- Abandoning workflows requires a reason for tracking
- Use: `abandon_workflow(instance_id, "reason here")`

## Workflow Instance Lifecycle

```
[Create] → instances/
    ↓
[Complete] → completed/
    or
[Abandon] → abandoned/
```

Instances are stored as JSON files in:
- `.claude/workflows/instances/` (active)
- `.claude/workflows/completed/` (finished)
- `.claude/workflows/abandoned/` (cancelled)

## See Also

- Workflow enforcement system documentation
- `.claude/workflow.json` schema reference
- Workflow instance JSON format
