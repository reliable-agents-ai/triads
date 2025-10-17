# Release Notes - v0.7.0 (PROPOSED)

> **Status**: Draft for validation - NOT YET IMPLEMENTED
>
> These are proposed release notes for validation. Please review to ensure alignment before development begins.

---

## Overview

Version 0.7.0 introduces **Generic Workflow Enforcement** - an intelligent system that tracks your workflow instances, enforces quality gates, and maintains a complete history of all your work.

**Key Innovation**: Unlike hardcoded workflow systems, this works with **any workflow you generate** - whether you're writing RFPs, building software, creating content, or managing any other multi-phase process.

---

## What's New

### 🔄 Workflow Instance Tracking

Every piece of work now gets its own tracked instance with complete history:

```bash
> Start RFP Analysis: Acme Corp manufacturing proposal

✓ Workflow instance created: rfp-acme-corp-manufacturing-20251017-100523
✓ Starting triad: rfp-analysis
```

**What this means:**
- Work on multiple projects concurrently
- Resume interrupted work anytime
- See complete history of what you've done
- Track time spent in each phase
- Never lose context

**Where instances are stored:**
```
.claude/workflows/
├── instances/        # Active work
├── completed/        # Finished work
└── abandoned/        # Cancelled work
```

---

### 📋 Workflow Schema Generation

When you run `/generate-triads`, the system now creates a workflow schema that defines your process:

**Generated `.claude/workflow.json`:**
```json
{
  "workflow_name": "rfp-writing",
  "triads": [
    {
      "id": "rfp-analysis",
      "name": "RFP Analysis",
      "type": "research",
      "position": 1,
      "required": true
    },
    {
      "id": "rfp-review",
      "name": "RFP Review",
      "type": "quality",
      "position": 4,
      "required": "conditional"
    },
    {
      "id": "rfp-submission",
      "name": "RFP Submission",
      "type": "release",
      "position": 5,
      "required": true
    }
  ],
  "enforcement": {
    "mode": "recommended",  // strict | recommended | optional
    "per_triad_overrides": {
      "legal-review": "strict",     // Cannot skip
      "docs-update": "optional"     // Can skip freely
    }
  },
  "workflow_rules": [
    {
      "rule_type": "sequential_progression",
      "description": "Triads should be completed in order",
      "track_deviations": true
    },
    {
      "rule_type": "conditional_requirement",
      "description": "Review required for substantial content",
      "gate_triad": "rfp-review",
      "before_triad": "rfp-submission",
      "condition": {
        "type": "significance_threshold",
        "metrics": {
          "content_created": {
            "threshold": 10,
            "units": "pages"
          },
          "components_modified": {
            "threshold": 3,
            "units": "sections"
          }
        }
      },
      "bypass_allowed": true
    }
  ]
}
```

**What this means:**
- Your workflow is self-documenting
- Enforcement rules match YOUR process (not hardcoded)
- Different workflows have different quality gates
- Thresholds are appropriate for your domain

---

### 🛡️ Configurable Workflow Enforcement

The system enforces your workflow sequence with **three enforcement modes** to match your needs:

- **Strict Mode** - Hard blocks (compliance-critical work)
- **Recommended Mode** - Warns, requires reason (DEFAULT)
- **Optional Mode** - Logs silently (experimental workflows)

**You choose the enforcement level** in `.claude/workflow.json`.

**Enforcement behavior depends on your mode:**

**Strict Mode (blocks deviations):**
```bash
> Start Implementation: OAuth2
🛑 ERROR: Cannot skip design (strict enforcement)

Must complete design OR use emergency override:
> Start Implementation: OAuth2 --force-skip design --justification "..."
```

**Recommended Mode (warns, requires reason):**
```bash
> Start Implementation: OAuth2
⚠️  RECOMMENDED: Complete design first

To skip: --skip design --reason "Design completed in Figma"

> Start Implementation: OAuth2 --skip design --reason "Design completed in Figma with team, mockups approved"
✓ Deviation recorded, proceeding...
```

**Optional Mode (logs silently):**
```bash
> Start Implementation: OAuth2
ℹ️  Skipped: design (optional mode - no reason required)
✓ Proceeding...
```

**RFP Writing Example:**
```bash
> Start RFP Analysis: Acme Corp proposal
> Start RFP Submission: Submit to Acme  # Skipping strategy and writing

ERROR: Workflow Steps Missing
Cannot proceed to submission without completing required steps.

Missing required triads:
  - rfp-strategy (position 2)
  - rfp-writing (position 3)
  - rfp-review (position 4, if proposal significant)

Next: Start RFP Strategy: Win themes for Acme Corp
```

**Content Creation Example:**
```bash
> Start Research: AI trends article
> Start Publishing: Publish to blog  # Skipping planning and drafting

ERROR: Workflow Steps Missing
Cannot proceed to publishing without completing required steps.

Missing required triads:
  - planning (position 2)
  - drafting (position 3)
  - editing (position 4, if content significant)

Next: Start Planning: Article structure and outline
```

**How it works:**
- **Configurable enforcement** - choose strict, recommended, or optional mode
- **Tracks deviations** - all skips/backward movement logged with reasons
- **Per-triad overrides** - mix enforcement levels (e.g., strict legal review, optional docs)
- **Deviation analytics** - understand real workflow patterns vs ideal

See [Enforcement Modes Guide](docs/WORKFLOW_ENFORCEMENT_MODES.md) for detailed comparison.

---

### 📊 Workflow Management CLI

New commands to manage your work:

#### List Active Work
```bash
> /workflows list

Active Workflows (3):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. rfp-acme-corp-manufacturing-20251017-100523
   Title: Acme Corp manufacturing proposal
   Current: rfp-writing
   Progress: 3/5 triads complete
   Age: 1h 25m

2. feature-oauth2-integration-20251017-110234
   Title: OAuth2 Integration
   Current: implementation
   Progress: 2/5 triads complete
   Age: 45m

3. blog-ai-trends-2025-20251017-143056
   Title: AI Trends 2025 article
   Current: research
   Progress: 1/4 triads complete
   Age: 10m
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

#### Resume Interrupted Work
```bash
> /workflows resume rfp-acme-corp-manufacturing-20251017-100523

✓ Resumed: Acme Corp manufacturing proposal
✓ Current phase: rfp-writing (3/5 complete)
✓ Next: rfp-review

You can continue with:
> Start RFP Review: Final review before submission
```

#### View History
```bash
> /workflows history --days 7

Completed Workflows (Last 7 Days):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. rfp-acme-corp-manufacturing-20251017-100523
   Completed: 2025-10-17T15:30:00Z
   Duration: 3h 45m
   Phases: analysis(25m) → strategy(40m) → writing(2h) → review(30m) → submission(10m)

2. feature-user-profiles-20251016-141234
   Completed: 2025-10-16T17:00:00Z
   Duration: 2h 15m
   Phases: idea-validation(10m) → design(35m) → implementation(1h) → garden-tending(20m) → deployment(10m)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Average duration: 3h 0m
Success rate: 100% (2/2 completed, 0 abandoned)
```

#### View Specific Instance
```bash
> /workflows show rfp-acme-corp-manufacturing-20251017-100523

Workflow Instance Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Title: Acme Corp manufacturing proposal
Type: rfp-writing
Status: in_progress

Started: 2025-10-17T10:05:23Z (1h 25m ago)
Started by: jane.doe@company.com

Progress: 3/5 triads complete
Current: rfp-writing

Completed:
  ✓ rfp-analysis (25 min) - 2025-10-17T10:30:00Z
  ✓ rfp-strategy (40 min) - 2025-10-17T11:10:00Z
  ✓ rfp-writing (2h 0m) - 2025-10-17T13:10:00Z

Pending:
  ○ rfp-review
  ○ rfp-submission

Metrics:
  Pages: 12
  Sections: 4
  Words: 3,500
  Measured: 2025-10-17T13:10:00Z

Notes:
  [2025-10-17T11:00] Need to emphasize sustainability in solution
  [2025-10-17T12:30] Include case study from Boeing project
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

#### Abandon Work
```bash
> /workflows abandon blog-ai-trends-2025-20251017-143056 --reason "Topic already covered by competitor"

✓ Workflow abandoned: blog-ai-trends-2025-20251017-143056
✓ Reason: Topic already covered by competitor
✓ Moved to: .claude/workflows/abandoned/
```

---

### 🚨 Emergency Bypass (Works for Any Workflow)

Need to skip a quality step? Document why:

**Software Development:**
```bash
> Start Deployment: v2.0.2 --force-deploy --justification "Production API down, affecting 10k users, hotfix critical"
```

**RFP Submission:**
```bash
> Start RFP Submission: Acme Corp --force-deploy --justification "Deadline is 5pm today, VP approved submission without review"
```

**Content Publishing:**
```bash
> Start Publishing: Blog post --force-deploy --justification "Breaking news, need to publish immediately, will edit post-publication"
```

**What happens:**
- Work proceeds immediately
- Justification logged to `.claude/workflow_audit.log`
- Timestamp and user recorded
- Can review bypass patterns later

---

### 📈 Workflow Analytics

Every instance records detailed metrics:

```json
{
  "instance_id": "feature-oauth2-20251017-100523",
  "workflow_progress": {
    "completed_triads": [
      {
        "triad_id": "idea-validation",
        "completed_at": "2025-10-17T10:15:00Z",
        "duration_minutes": 9.6,
        "metrics": {
          "research_sources": 5,
          "priority_score": 0.85
        }
      },
      {
        "triad_id": "design",
        "completed_at": "2025-10-17T10:45:00Z",
        "duration_minutes": 30.0,
        "metrics": {
          "adrs_created": 3,
          "approval_received": true
        }
      }
    ]
  }
}
```

**Use cases:**
- "How long do implementation phases typically take?"
- "What's our average workflow completion time?"
- "Which workflows get abandoned most often?"
- "Are we bypassing quality gates too frequently?"

---

## Breaking Changes

### Workflow State File Removed

**Old (v0.6.x):**
```
.claude/workflow_state.json  # Single global state
```

**New (v0.7.0):**
```
.claude/workflows/instances/  # Multiple instance files
```

**Migration:** No action needed. Old state file is ignored. New instances created automatically.

---

### New Required File: workflow.json

**What it is:**
- Generated automatically by `/generate-triads`
- Defines your workflow sequence and rules
- Located at `.claude/workflow.json`

**What to do:**
- If you've customized your triads, re-run `/generate-triads` to create workflow schema
- OR manually create `.claude/workflow.json` (see User Guide for schema)

**Existing users:**
If you skip this, workflows will still work but without enforcement. You'll see:
```
⚠️  Warning: .claude/workflow.json not found
✓  Workflow enforcement disabled
✓  Proceeding without quality gates
```

---

## New Files and Directories

```
.claude/
├── workflow.json                      # NEW: Workflow schema
├── workflows/                         # NEW: Instance tracking
│   ├── instances/                     # Active work
│   ├── completed/                     # Finished work
│   └── abandoned/                     # Cancelled work
└── workflow_audit.log                 # Bypass audit trail
```

**Note:** All new files are auto-generated. You don't need to create them manually.

---

## Upgrade Guide

### Step 1: Update Plugin

```bash
claude plugin update triads
# OR
git pull && ./install-triads.sh
```

### Step 2: Generate Workflow Schema (If Custom Triads)

```bash
cd your-project
claude code

# If you've customized your triads, regenerate workflow schema:
> /generate-triads

# Follow prompts to define your workflow
# This creates .claude/workflow.json
```

### Step 3: Start Using Instances

```bash
# Old way (still works, but no tracking):
> Start Design: OAuth2 architecture

# New way (creates tracked instance):
> Start Design: OAuth2 authentication system

✓ Instance created: feature-oauth2-authentication-system-20251017-120000
```

**That's it!** Workflow tracking is automatic from this point.

---

## Use Cases by Domain

### Software Development

**Workflow:** idea-validation → design → implementation → garden-tending → deployment

**Quality Gate:** Garden Tending before Deployment

**Thresholds (Significance Metrics):**
- Substantial content created, OR
- Multiple components modified, OR
- Complex changes added

**Example:**
```bash
> Start Idea Validation: OAuth2 integration
> Start Design: OAuth2 architecture
> Start Implementation: OAuth2 integration
[Substantial changes: new authentication system, 8 files modified]

> Start Deployment: v2.1.0
ERROR: Missing Required Step
Must complete garden-tending before deployment (changes significant)

> Start Garden Tending: Post-OAuth2 cleanup
[Refactor, consolidate, test]

> Start Deployment: v2.1.0
✓ Workflow complete, deploying...
```

---

### RFP Writing

**Workflow:** rfp-analysis → rfp-strategy → rfp-writing → rfp-review → rfp-submission

**Quality Gate:** RFP Review before Submission

**Thresholds (Significance Metrics):**
- Substantial content written, OR
- Multiple major sections, OR
- Comprehensive proposal

**Example:**
```bash
> Start RFP Analysis: Acme Corp manufacturing proposal
> Start RFP Strategy: Win themes
> Start RFP Writing: Acme Corp proposal
[Substantial content: 12 pages, 4 major sections, comprehensive approach]

> Start RFP Submission: Submit to Acme Corp
ERROR: Missing Required Step
Must complete rfp-review before submission (proposal significant)

> Start RFP Review: Final review
[Review, improve, polish]

> Start RFP Submission: Submit to Acme Corp
✓ Workflow complete, submitting...
```

---

### Content Creation

**Workflow:** research → planning → drafting → editing → publishing

**Quality Gate:** Editing before Publishing

**Thresholds (Significance Metrics):**
- Substantial content written, OR
- Multiple major sections, OR
- Rich media included

**Example:**
```bash
> Start Research: AI trends 2025
> Start Planning: Article outline
> Start Drafting: AI trends 2025 blog post
[Substantial content: comprehensive article, 8 sections, rich media]

> Start Publishing: Publish to blog
ERROR: Missing Required Step
Must complete editing before publishing (content significant)

> Start Editing: Final edit before publishing
[Edit, fact-check, proofread]

> Start Publishing: Publish to blog
✓ Workflow complete, publishing...
```

---

### Legal Document Review

**Workflow:** intake → research → drafting → peer-review → client-review → finalization

**Quality Gate:** Peer Review before Client Review

**Thresholds (Significance Metrics):**
- Substantial document length, OR
- Multiple major clauses, OR
- High-value contract

**Example:**
```bash
> Start Intake: Employment agreement - Senior Engineer
> Start Research: Employment law review
> Start Drafting: Employment agreement
[Substantial contract: comprehensive terms, 5 major clauses, equity component]

> Start Client Review: Send to hiring manager
ERROR: Missing Required Step
Must complete peer-review before client-review (contract significant)

> Start Peer Review: Senior partner review
[Legal review, compliance check]

> Start Client Review: Send to hiring manager
✓ Workflow complete, sending...
```

---

## Migration Examples

### Before v0.7.0 (No Tracking, No Enforcement)

```bash
# Work on OAuth2
> Start Design: OAuth2
[Design completes]

# Skip to deployment (no enforcement)
> Start Deployment: v2.1.0
[Deploys without implementation or quality review]

# Work on Login UI (loses OAuth2 context)
> Start Design: Login UI
[Design completes]

# Go back to OAuth2 (must remember where you were)
> Start Implementation: OAuth2
[No context from previous design work]
```

**Problems:**
- ❌ Can skip required workflow steps
- ❌ Can't work on multiple projects concurrently
- ❌ Lost context when switching
- ❌ No history of completed work
- ❌ Can't resume if interrupted
- ❌ No enforcement of process

---

### After v0.7.0 (Instance Tracking + Full Enforcement)

```bash
# Work on OAuth2 - enforces complete workflow
> Start Idea Validation: OAuth2 authentication system
✓ Instance created: feature-oauth2-authentication-system-20251017-100000

> Start Design: OAuth2 system
✓ Resuming instance (idea-validation complete)

> Start Deployment: v2.1.0  # Try to skip ahead
ERROR: Missing Required Steps
Must complete: implementation, garden-tending (if significant)

# Work on Login UI concurrently (OAuth2 instance preserved)
> Start Idea Validation: Login UI redesign
✓ Instance created: feature-login-ui-redesign-20251017-110000

# Resume OAuth2 (full context + enforcement)
> /workflows list
Active: feature-oauth2-authentication-system-20251017-100000 (current: design, 2/5 complete)

> Start Implementation: OAuth2 system
✓ Resuming instance: feature-oauth2-authentication-system-20251017-100000
✓ Design context loaded
✓ Next required step: implementation
[Implementation proceeds with full design context]

> Start Deployment: v2.1.0
✓ Checking workflow... implementation complete
✓ Conditional: garden-tending required (substantial changes detected)
ERROR: Must complete garden-tending before deployment
```

**Benefits:**
- ✅ Work on multiple projects concurrently
- ✅ Context preserved per instance
- ✅ Complete history maintained
- ✅ Resume anytime
- ✅ **Cannot skip required workflow steps**
- ✅ **Process integrity enforced**

---

## Technical Details

### Instance ID Format

```
<slug>-<timestamp>
```

**Examples:**
- `feature-oauth2-integration-20251017-100523`
- `rfp-acme-corp-manufacturing-20251017-143056`
- `blog-ai-trends-2025-20251017-090000`
- `bugfix-payment-timeout-20251017-153045`

**Generation:**
- Slug: First 40 chars of title, lowercase, hyphens
- Timestamp: `YYYYMMDD-HHMMSS` format
- Ensures uniqueness and chronological sorting

---

### Workflow Schema Reference

**Full schema specification:** See [Workflow Schema Guide](docs/WORKFLOW_SCHEMA.md)

**Minimum viable schema:**
```json
{
  "workflow_name": "my-workflow",
  "triads": [
    {"id": "analysis", "type": "research", "position": 1},
    {"id": "execution", "type": "execution", "position": 2},
    {"id": "quality", "type": "quality", "position": 3, "required": "conditional"},
    {"id": "release", "type": "release", "position": 4}
  ],
  "workflow_rules": [
    {
      "rule_type": "quality_gate",
      "gate_triad": "quality",
      "before_triad": "release",
      "condition": {
        "type": "significant_changes",
        "metrics": {"threshold": 100}
      }
    }
  ]
}
```

---

### Instance File Reference

**Full instance file specification:** See [Instance File Format](docs/INSTANCE_FORMAT.md)

**Minimum instance file:**
```json
{
  "instance_id": "feature-oauth2-20251017-100523",
  "workflow_type": "software-development",
  "metadata": {
    "title": "OAuth2 Integration",
    "status": "in_progress",
    "started_at": "2025-10-17T10:05:23Z"
  },
  "workflow_progress": {
    "current_triad": "implementation",
    "completed_triads": [
      {
        "triad_id": "idea-validation",
        "completed_at": "2025-10-17T10:15:00Z",
        "duration_minutes": 9.6
      }
    ]
  }
}
```

---

## Performance Impact

**Instance file operations:**
- Create instance: < 10ms
- Update instance: < 20ms (atomic writes with locking)
- List instances: < 50ms (directory scan)
- Load instance: < 10ms

**Storage:**
- Typical instance file: 1-5 KB
- 1,000 completed workflows: ~5 MB
- Negligible disk space impact

**Concurrency:**
- File locking prevents race conditions
- Safe for concurrent workflow instances
- Atomic writes prevent corruption

---

## Known Limitations

### 1. Git Required for Change Metrics

**Impact:** If git unavailable, metrics default to 0 (quality gates won't trigger)

**Workaround:** Ensure git available in deployment environments

**Future:** Support manual metrics (v0.8.0)

---

### 2. Unix/macOS Only (File Locking)

**Impact:** File locking uses `fcntl` (Unix-only)

**Workaround:** Windows users: file locking disabled, may have race conditions

**Future:** Windows support via `msvcrt` (v0.8.0)

---

### 3. No Multi-User Workflow Instances

**Impact:** Instances are per-machine, not shared across team

**Workaround:** Commit instance files to git for team visibility

**Future:** Cloud sync support (v0.9.0+)

---

## Troubleshooting

### "No workflow schema found"

**Error:**
```
⚠️  Warning: .claude/workflow.json not found
```

**Solution:**
```bash
> /generate-triads
# Or manually create .claude/workflow.json
```

---

### "Cannot resume instance - not found"

**Error:**
```
ERROR: Instance not found: feature-oauth2-20251017-100523
```

**Solution:**
```bash
# List available instances
> /workflows list

# Use correct instance ID from list
> /workflows resume <correct-id>
```

---

### "Quality gate failed but I just ran quality triad"

**Cause:** Instance file didn't record completion

**Solution:**
```bash
# Check instance status
> /workflows show <instance-id>

# If quality triad missing, re-run it
> Start <QualityTriad>: <description>
```

---

## What's Next (v0.8.0+)

### Planned Features

**Workflow Templates:**
```bash
> /workflows create --template hotfix
✓ Created from template: bugfix-payment-20251017-120000
```

**Team Collaboration:**
```bash
> /workflows share feature-oauth2-20251017-100523
✓ Shared with team via .claude/workflows/shared/
```

**Custom Metrics:**
```json
{
  "condition": {
    "type": "custom_metric",
    "metric_name": "test_coverage",
    "threshold": 80,
    "operator": "less_than"
  }
}
```

**Workflow Visualization:**
```bash
> /workflows visualize rfp-acme-corp-20251017-100523

RFP Analysis → RFP Strategy → RFP Writing → RFP Review → RFP Submission
    ✓              ✓             ✓             (current)       (pending)
   25m            40m            2h
```

**Notifications:**
```json
{
  "notifications": {
    "quality_gate_triggered": {
      "channels": ["slack", "email"],
      "message": "Quality review needed for ${instance_title}"
    }
  }
}
```

---

## Feedback Welcome

This is a major architectural change. We'd love to hear:

- Does instance tracking work for your use case?
- Are the CLI commands intuitive?
- What metrics matter for your domain?
- What workflow types should we test?

**Open an issue:** https://github.com/reliable-agents-ai/triads/issues

---

## Credits

**Design inspiration:**
- Workflow instance concept: @iainnb
- Schema-driven enforcement: Triad architect discussions
- Multi-domain support: Community feedback

**Contributors:**
- [Full contributor list]

---

## License

MIT License - see [LICENSE](LICENSE) file

---

**Version:** 0.7.0
**Release Date:** TBD (pending validation)
**Status:** PROPOSED - awaiting approval before implementation
