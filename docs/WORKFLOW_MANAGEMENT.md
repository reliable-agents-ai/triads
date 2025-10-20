# Workflow Management Guide

> Multi-instance workflow tracking for concurrent feature development

**New in v0.7.0-alpha.7**: The triad system now supports multiple concurrent workflows per project, allowing you to work on multiple features simultaneously while maintaining systematic progress tracking.

---

## Table of Contents

- [Overview](#overview)
- [Workflow Instance Lifecycle](#workflow-instance-lifecycle)
- [Session Start Index](#session-start-index)
- [Slash Commands](#slash-commands)
- [Working with Multiple Workflows](#working-with-multiple-workflows)
- [Architecture](#architecture)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Overview

### What Are Workflow Instances?

A **workflow instance** represents a complete journey through the 5-triad system for a specific feature or project:

```
Idea Validation → Design → Implementation → Garden Tending → Deployment
```

Each workflow instance is:
- **Tracked separately** with a unique instance ID
- **Persistent across sessions** - resume where you left off
- **Self-contained** - has its own metadata, progress, and significance metrics
- **Concurrent-safe** - multiple workflows can run simultaneously

### Why Multi-Instance?

**Real-world development isn't linear**. You might be:
- Implementing OAuth2 integration (in Implementation phase)
- Designing a notification system (in Design phase)
- Validating an AI-powered search idea (in Idea Validation phase)

Previously, the system could only track one workflow at a time. Now you can work on all three simultaneously without confusion.

---

## Workflow Instance Lifecycle

### 1. Auto-Create on Triad Start

When you start any triad, the system automatically creates or resumes a workflow instance:

```bash
> Start Idea Validation: AI-powered code suggestions

# System automatically creates:
# .claude/workflows/instances/ai-powered-code-suggestions-20251020-143022-456789.json
```

**Instance ID Format**: `{slug}-{date}-{time}-{microseconds}.json`
- **Slug**: Lowercase, hyphenated title (from your triad command)
- **Date**: YYYYMMDD
- **Time**: HHMMSS
- **Microseconds**: Unique identifier

### 2. Track Progress

As you work through triads, bridge agents automatically mark phases as complete:

```bash
> Start Design: AI-powered code suggestions architecture
[Design Bridge marks "idea-validation" as completed]

> Start Implementation: Build code suggestion engine
[Design Bridge marks "design" as completed]

> Start Garden Tending: Refactor suggestion engine
[Gardener Bridge marks "implementation" as completed]

> Start Deployment: v1.5.0
[Gardener Bridge marks "garden-tending" as completed]
[Release Manager marks "deployment" as completed - workflow moves to completed/]
```

### 3. Resume Work

At session start, see all active workflows:

```
🔄 WORKFLOW CONTINUITY

Active Workflows (3):

1. AI-Powered Code Suggestions
   ID: ai-powered-code-suggestions-20251020-143022-456789
   Current: implementation
   Age: 2d

2. OAuth2 Integration
   ID: oauth2-integration-20251018-110234-123456
   Current: garden-tending
   Age: 5d

3. Real-Time Notifications
   ID: real-time-notifications-20251019-093012-789012
   Current: design
   Age: 3d

To resume: /workflows resume <instance-id>
To see all: /workflows list
```

### 4. Complete or Abandon

**Completion** (automatic):
- When deployment finishes, workflow moves to `.claude/workflows/completed/`
- Preserves full history for retrospectives

**Abandonment** (manual):
```bash
> /workflows abandon ai-powered-code-suggestions-20251020-143022-456789 --reason "Decided not to pursue this feature"
```
- Workflow moves to `.claude/workflows/abandoned/`
- Reason stored in metadata

---

## Session Start Index

### Automatic Display

Every session shows active workflows automatically:

```
🔄 WORKFLOW CONTINUITY

Active Workflows (2):

1. OAuth2 Integration
   ID: oauth2-integration-20251017-110234-123456
   Current: implementation
   Age: 2d

2. API Rate Limiting
   ID: api-rate-limiting-20251018-093012-234567
   Current: design
   Age: 1d

To resume: /workflows resume <instance-id>
To see all: /workflows list
```

### What's Shown

- **Title**: Human-readable workflow name
- **Instance ID**: Unique identifier for slash commands
- **Current Phase**: What triad you're currently in
- **Age**: Time since workflow started (e.g., "2d", "3h", "45m")

### Age Formatting

- **Days**: "2d" (if ≥ 1 day)
- **Hours**: "3h" (if ≥ 1 hour but < 1 day)
- **Minutes**: "45m" (if < 1 hour)

---

## Slash Commands

### `/workflows list`

List all workflow instances with filtering:

```bash
# List all active workflows
> /workflows list

# List completed workflows
> /workflows list --status completed

# List abandoned workflows
> /workflows list --status abandoned

# List all workflows (active, completed, abandoned)
> /workflows list --status all
```

**Output Example**:
```
Active Workflows (2):

1. OAuth2 Integration
   ID: oauth2-integration-20251017-110234-123456
   Current: implementation
   Completed: idea-validation, design
   Age: 2d
   Files: 8 changed, +245 lines, -67 lines

2. API Rate Limiting
   ID: api-rate-limiting-20251018-093012-234567
   Current: design
   Completed: idea-validation
   Age: 1d
   Files: 3 changed, +89 lines, -12 lines
```

### `/workflows resume <instance-id>`

Set a specific workflow as current for the session:

```bash
> /workflows resume oauth2-integration-20251017-110234-123456

✓ Resumed workflow: OAuth2 Integration
  Current phase: implementation
  Next step: Complete implementation, then run Garden Tending
```

**What This Does**:
- Sets `TRIADS_WORKFLOW_INSTANCE` environment variable
- All subsequent triad work applies to this workflow
- Bridge agents will track completion for this instance

### `/workflows show <instance-id>`

Display detailed workflow information:

```bash
> /workflows show oauth2-integration-20251017-110234-123456

Workflow: OAuth2 Integration
ID: oauth2-integration-20251017-110234-123456
Status: in_progress

Progress:
✓ idea-validation (completed 2d ago)
✓ design (completed 1d ago)
→ implementation (current, started 6h ago)
  garden-tending
  deployment

Metadata:
- Started: 2025-10-17 11:02:34
- Last updated: 2025-10-20 09:15:22
- User: iain@example.com
- Files changed: 8
- Lines added: 245
- Lines removed: 67

Significance Metrics:
- new_endpoints: 3
- auth_providers: ["google", "github", "microsoft"]
- tests_added: 12
```

### `/workflows abandon <instance-id> --reason "..."`

Mark a workflow as abandoned with justification:

```bash
> /workflows abandon api-rate-limiting-20251018-093012-234567 --reason "Business priorities changed, feature postponed"

✓ Workflow abandoned: API Rate Limiting
  Reason: Business priorities changed, feature postponed
  Moved to: .claude/workflows/abandoned/
```

---

## Working with Multiple Workflows

### Best Practices

**1. Start workflows explicitly**:
```bash
# Good: Clear, descriptive titles
> Start Idea Validation: OAuth2 integration for enterprise SSO
> Start Design: Real-time notification system with WebSockets

# Bad: Vague titles (harder to identify later)
> Start Idea Validation: New feature
> Start Design: System design
```

**2. Use `/workflows list` frequently**:
```bash
# Check active workflows before starting new work
> /workflows list

# See what you were working on
```

**3. Resume the right workflow**:
```bash
# Before continuing work on a specific feature
> /workflows resume oauth2-integration-20251017-110234-123456

# Then continue
> Start Implementation: OAuth2 login flow
```

**4. Complete phases systematically**:
```bash
# Don't skip phases - each triad marks progress
> Start Idea Validation: New feature
> Start Design: New feature
> Start Implementation: New feature
> Start Garden Tending: New feature cleanup
> Start Deployment: v1.5.0
```

### Common Workflows

**Scenario 1: Starting a new feature**
```bash
# System auto-creates workflow instance
> Start Idea Validation: AI-powered code review

# At session start, you'll see it in the index
```

**Scenario 2: Continuing existing work**
```bash
# At session start, see active workflows
> /workflows list

# Resume specific workflow
> /workflows resume ai-code-review-20251020-143022-456789

# Continue work
> Start Implementation: Build code review engine
```

**Scenario 3: Working on multiple features**
```bash
# Work on Feature A
> /workflows resume oauth2-integration-20251017-110234-123456
> Start Implementation: OAuth2 flow

# Switch to Feature B
> /workflows resume notifications-20251018-093012-234567
> Start Design: Notification architecture

# Switch back to Feature A
> /workflows resume oauth2-integration-20251017-110234-123456
> Continue implementation work
```

**Scenario 4: Abandoning a feature**
```bash
# List workflows
> /workflows list

# Abandon one
> /workflows abandon old-feature-20251015-120000-111111 --reason "Superseded by new approach"
```

---

## Architecture

### File Structure

```
.claude/workflows/
├── instances/                    # Active workflows
│   ├── oauth2-integration-20251017-110234-123456.json
│   ├── notifications-20251018-093012-234567.json
│   └── ai-code-review-20251020-143022-456789.json
├── completed/                    # Finished workflows
│   └── user-auth-20251010-100000-111111.json
├── abandoned/                    # Cancelled workflows
│   └── old-feature-20251015-120000-222222.json
└── current_instance.json         # Tracks current workflow for session
```

### Workflow Instance File Format

```json
{
  "instance_id": "oauth2-integration-20251017-110234-123456",
  "title": "OAuth2 Integration",
  "status": "in_progress",
  "current_triad": "implementation",
  "completed_triads": ["idea-validation", "design"],
  "metadata": {
    "user": "iain@example.com",
    "started_at": "2025-10-17T11:02:34Z",
    "last_updated": "2025-10-20T09:15:22Z",
    "files_changed": 8,
    "lines_added": 245,
    "lines_removed": 67
  },
  "significance_metrics": {
    "new_endpoints": 3,
    "auth_providers": ["google", "github", "microsoft"],
    "tests_added": 12
  }
}
```

### Atomic Operations

**Security & Reliability** (v0.7.0-alpha.7):
- **Path Traversal Prevention**: Instance IDs validated (alphanumeric + hyphens/underscores only)
- **Atomic File Operations**: All reads/writes use file locking to prevent corruption
- **Concurrent-Safe**: Tested with 5 concurrent threads, 100% stability

**Implementation** (`src/triads/utils/workflow_context.py`):
```python
# Validation pattern
INSTANCE_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')

# Atomic operations
def atomic_read_json(filepath):
    with fcntl.flock(file, fcntl.LOCK_SH):
        return json.load(file)

def atomic_write_json(filepath, data):
    with fcntl.flock(file, fcntl.LOCK_EX):
        json.dump(data, file)
```

### Bridge Agent Integration

Bridge agents (Design Bridge, Gardener Bridge) automatically track completion:

```python
from triads.workflow_enforcement.instance_manager import WorkflowInstanceManager
from triads.utils.workflow_context import get_current_instance_id

instance_id = get_current_instance_id()

if instance_id:
    manager = WorkflowInstanceManager()
    manager.mark_triad_completed(instance_id, "design")

    # Update significance metrics
    instance = manager.load_instance(instance_id)
    instance.significance_metrics.update({
        "tasks_created": 5,
        "adrs_written": 2
    })
    manager.update_instance(instance_id, instance.to_dict())
```

---

## Best Practices

### 1. Use Descriptive Titles

**Good**:
```bash
> Start Idea Validation: OAuth2 integration for enterprise SSO
> Start Design: Real-time WebSocket notification system
> Start Implementation: Machine learning-based code suggestions
```

**Bad**:
```bash
> Start Idea Validation: New feature
> Start Design: System
> Start Implementation: Code
```

**Why**: Instance IDs are derived from titles. Descriptive titles make workflows easier to identify in `/workflows list`.

### 2. Check Active Workflows Before Starting

```bash
# Always check what's in progress
> /workflows list

# See if you should resume existing work or start new
```

**Why**: Avoids creating duplicate workflows for the same feature.

### 3. Complete Phases Systematically

```bash
# Follow the 5-triad sequence
1. Start Idea Validation: [feature]
2. Start Design: [feature]
3. Start Implementation: [feature]
4. Start Garden Tending: [feature] cleanup
5. Start Deployment: [version]
```

**Why**: Workflow enforcement relies on this sequence. Skipping phases may trigger warnings.

### 4. Resume Before Continuing Work

```bash
# At session start, resume the workflow you want to work on
> /workflows resume oauth2-integration-20251017-110234-123456

# Then continue work
> Start Implementation: OAuth2 callback handling
```

**Why**: Ensures bridge agents track progress in the correct workflow instance.

### 5. Abandon Dormant Workflows

```bash
# If you're not going to continue a workflow
> /workflows abandon old-feature-20251015-120000-111111 --reason "Requirements changed, no longer needed"
```

**Why**: Keeps your active workflow list clean and focused.

---

## Troubleshooting

### Problem: "Workflow instance not found"

**Symptom**:
```bash
> /workflows resume nonexistent-id-12345
ERROR: Workflow instance not found: nonexistent-id-12345
```

**Solution**:
```bash
# List all workflows to find the correct ID
> /workflows list

# Copy the full instance ID from the output
> /workflows resume oauth2-integration-20251017-110234-123456
```

### Problem: Bridge agents not tracking completion

**Symptom**: Progress not updating in `/workflows show <id>`

**Diagnosis**:
```bash
# Check if workflow is currently active
> cat .claude/workflows/current_instance.json

# Should show your instance ID
```

**Solution**:
```bash
# Resume the workflow explicitly
> /workflows resume oauth2-integration-20251017-110234-123456

# Then run the triad
> Start Implementation: [feature]
```

### Problem: Multiple workflows with similar names

**Symptom**: Hard to distinguish workflows in `/workflows list`

**Solution**:
```bash
# Use /workflows show to see full details
> /workflows show oauth2-integration-20251017-110234-123456

# Look at metadata (started date, files changed, etc.)

# Abandon duplicates
> /workflows abandon oauth2-integration-20251017-999999-999999 --reason "Duplicate workflow"
```

### Problem: Workflow shows wrong status

**Symptom**: Workflow stuck in old phase

**Diagnosis**:
```bash
# Check workflow file directly
> cat .claude/workflows/instances/oauth2-integration-20251017-110234-123456.json

# Look at completed_triads and current_triad
```

**Solution**:
```bash
# Manually edit the file if needed (advanced users only)
# Or run the missing phase to update progress
> Start Design: OAuth2 architecture
```

### Problem: "Path traversal validation error"

**Symptom**:
```bash
WARNING: Invalid workflow instance ID detected: ../../../etc/passwd
```

**Cause**: Malicious or malformed instance ID

**Solution**: This is a security feature (v0.7.0-alpha.7). Use valid instance IDs from `/workflows list`.

### Problem: Race condition warnings

**Symptom**:
```bash
WARNING: File lock timeout on workflow instance
```

**Cause**: Multiple concurrent operations on the same workflow

**Solution**: This is rare but can happen with concurrent triad execution. The system will retry automatically. If it persists, wait a few seconds and try again.

---

## Migration from Single-Workflow System

### What Changed in v0.7.0-alpha.7

**Before (v0.7.0-alpha.6)**:
- Single `.claude/workflow_state.json` file
- One workflow at a time
- Manual tracking

**After (v0.7.0-alpha.7)**:
- Multiple `.claude/workflows/instances/*.json` files
- Multiple concurrent workflows
- Automatic tracking with instance IDs

### Backward Compatibility

The system is **backward compatible**:
- Old `workflow_state.json` (if it exists) is ignored
- New workflow instances created automatically
- No manual migration required

### If You Have Existing Work

**Option 1: Start fresh** (recommended)
```bash
# Just start working - new workflows will be created
> Start Idea Validation: [feature]
```

**Option 2: Manually migrate** (advanced)
```bash
# Check old state
> cat .claude/workflow_state.json

# Start a new workflow instance for that work
> Start [CurrentPhase]: [feature description]
```

---

## Summary

Multi-instance workflow management enables:
- ✅ **Concurrent feature development** - work on multiple features simultaneously
- ✅ **Session continuity** - resume where you left off
- ✅ **Automatic tracking** - bridge agents mark progress
- ✅ **Clean organization** - separate instances for each feature
- ✅ **Security & reliability** - path traversal prevention, atomic operations

**Key Commands**:
- `/workflows list` - See all workflows
- `/workflows resume <id>` - Resume specific workflow
- `/workflows show <id>` - View workflow details
- `/workflows abandon <id> --reason "..."` - Cancel workflow

**Next Steps**:
1. Start working on a feature - workflow instance created automatically
2. Check `/workflows list` at session start
3. Resume workflows explicitly with `/workflows resume <id>`
4. Complete phases systematically for proper tracking

---

**Need help?** See [Workflow Enforcement Guide](WORKFLOW_ENFORCEMENT.md) for quality gates and systematic work guidance.
