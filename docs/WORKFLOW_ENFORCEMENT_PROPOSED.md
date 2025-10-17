# Workflow Enforcement User Guide (PROPOSED)

> **Status**: Draft for validation - NOT YET IMPLEMENTED
>
> This is a proposed user guide. Please review to ensure we're aligned before development begins.

---

## What is Workflow Enforcement?

Workflow Enforcement is a smart tracking and guidance system that:

1. **Tracks every piece of work** in its own instance file
2. **Guides your workflow sequence** with configurable enforcement
3. **Documents deviations** when you skip or adjust the workflow
4. **Maintains complete history** of everything you've done
5. **Works with ANY workflow** you generate (RFP writing, software dev, content creation, etc.)

**The Big Idea:** Instead of rigid rules, you choose your enforcement level:
- **Strict** - Blocks deviations (compliance work)
- **Recommended** - Warns and tracks (DEFAULT - most workflows)
- **Optional** - Logs silently (experimental work)

The system adapts to YOUR needs while maintaining visibility into how work actually happens.

---

## Quick Start (5 Minutes)

### 1. Generate Your Workflow (One Time)

```bash
cd your-project
claude code

> /generate-triads
```

**What happens:**
- System interviews you about your workflow
- Generates custom triads for YOUR process
- Creates `.claude/workflow.json` defining your workflow rules
- Creates `.claude/agents/` directories with your specialized agents

**Example for RFP Writing:**
```
✓ Created workflow schema: .claude/workflow.json
✓ Created triads:
  - rfp-analysis/
  - rfp-strategy/
  - rfp-writing/
  - rfp-review/  (quality gate)
  - rfp-submission/  (release)
```

---

### 2. Start Working

```bash
> Start RFP Analysis: Acme Corp manufacturing proposal
```

**What happens:**
```
✓ Workflow instance created: rfp-acme-corp-manufacturing-20251017-100523
✓ File: .claude/workflows/instances/rfp-acme-corp-manufacturing-20251017-100523.json
✓ Starting triad: rfp-analysis

[Analysis agents run...]

✓ RFP Analysis complete (duration: 25 minutes)
```

---

### 3. Continue Your Workflow

```bash
> Start RFP Strategy: Acme Corp win themes
```

**What happens:**
```
✓ Resuming instance: rfp-acme-corp-manufacturing-20251017-100523
✓ Marked rfp-analysis complete
✓ Starting triad: rfp-strategy

[Strategy agents run...]

✓ RFP Strategy complete (duration: 40 minutes)
```

**The system automatically:**
- Resumes your instance
- Tracks which phases are complete
- Records metrics and duration

---

### 4. Workflow Enforcement in Action

This example uses **Recommended Mode** (default):

```bash
> Start RFP Writing: Acme Corp proposal
[Write substantial content: 12 pages, 4 major sections]

> Start RFP Submission: Submit to Acme Corp  # Try to skip review
```

**What happens:**
```
⚠️  RECOMMENDED: Complete rfp-review first
════════════════════════════════════════════════════════════════════
Enforcement mode: RECOMMENDED

Current Progress: 3/5 triads complete
  ✓ rfp-analysis (completed 2025-10-17T10:30:00Z)
  ✓ rfp-strategy (completed 2025-10-17T11:10:00Z)
  ✓ rfp-writing (completed 2025-10-17T13:10:00Z)
  ⊘ rfp-review (recommended - content is substantial)
  ○ rfp-submission (current attempt)

Significance Assessment:
  - Content created: 12 pages (threshold: 10 pages)
  - Components modified: 4 sections (threshold: 3 sections)
  - Recommendation: Review before submission

Options:
  1. Follow workflow:
     > Start RFP Review: Final review before Acme submission

  2. Skip with documented reason:
     > Start RFP Submission: Submit to Acme Corp --skip rfp-review --reason "Client requested urgent submission, will do post-review"

════════════════════════════════════════════════════════════════════
```

**User chooses to skip (with reason):**
```bash
> Start RFP Submission: Submit to Acme Corp --skip rfp-review --reason "Client deadline 5pm today, VP approved submission without review, will follow up with quality review next week"

✓ Workflow deviation recorded
✓ Skipped: rfp-review
✓ Reason: Client deadline 5pm today, VP approved submission without review...
✓ Proceeding with submission...
```

---

### 5. Complete Required Step

```bash
> Start RFP Review: Final review before Acme submission

✓ Resuming instance: rfp-acme-corp-manufacturing-20251017-100523
✓ Starting triad: rfp-review

[Review agents run...]

✓ RFP Review complete (duration: 30 minutes)

> Start RFP Submission: Submit to Acme Corp

✓ Checking workflow sequence...
✓ All required triads complete: analysis, strategy, writing, review
✓ Proceeding with submission...
✓ RFP Submission complete (duration: 10 minutes)

✓ Workflow completed: rfp-acme-corp-manufacturing-20251017-100523
✓ Total duration: 3h 45m
✓ File moved to: .claude/workflows/completed/
```

---

## How It Works for Different Workflows

### Software Development Workflow

**Your generated triads:**
- `idea-validation` (research)
- `design` (planning)
- `implementation` (execution)
- `garden-tending` (quality)
- `deployment` (release)

**Workflow sequence (Recommended Mode):**
"Follow workflow in order; Garden Tending recommended before Deployment if changes substantial"

**Example:**
```bash
> Start Idea Validation: OAuth2 authentication
> Start Design: OAuth2 architecture
> Start Implementation: OAuth2 authentication
[Substantial changes: new authentication system, 8 components modified]

> Start Deployment: v2.1.0

⚠️  RECOMMENDED: Complete garden-tending first
Changes are substantial (8 components modified)

Options:
  1. Follow workflow: Start Garden Tending: Post-OAuth2 cleanup
  2. Skip with reason: --skip garden-tending --reason "..."

> Start Deployment: v2.1.0 --skip garden-tending --reason "Hotfix for production issue, will run garden-tending as separate PR post-deployment"

✓ Deviation recorded, proceeding with deployment...
```

**Or in Strict Mode (for compliance-critical work):**
```bash
> Start Deployment: v2.1.0

🛑 CRITICAL: Garden Tending Required
Enforcement mode: STRICT
Cannot skip garden-tending for substantial changes

Must either complete or use emergency override:
> Start Deployment: v2.1.0 --force-skip garden-tending --justification "..."
```

---

### RFP Writing Workflow

**Your generated triads:**
- `rfp-analysis` (research)
- `rfp-strategy` (planning)
- `rfp-writing` (execution)
- `rfp-review` (quality)
- `rfp-submission` (release)

**Workflow sequence rule:**
"Complete all triads in order; RFP Review required before Submission if content is substantial"

**Example:**
```bash
> Start RFP Analysis: Acme Corp manufacturing proposal
> Start RFP Strategy: Win themes
> Start RFP Writing: Acme Corp proposal
[Substantial content: comprehensive proposal, 12 pages, 4 major sections]

> Start RFP Submission: Submit to Acme Corp

ERROR: Workflow Steps Missing
Cannot proceed without completing rfp-review (content substantial)

Next: Start RFP Review: Final review before submission
```

---

### Content Creation Workflow

**Your generated triads:**
- `research` (research)
- `planning` (planning)
- `drafting` (execution)
- `editing` (quality)
- `publishing` (release)

**Workflow sequence rule:**
"Complete all triads in order; Editing required before Publishing if content is substantial"

**Example:**
```bash
> Start Research: AI trends 2025
> Start Planning: Article structure
> Start Drafting: AI trends 2025 blog post
[Substantial content: comprehensive article, 8 sections, rich media]

> Start Publishing: Publish to blog

ERROR: Workflow Steps Missing
Cannot proceed without completing editing (content substantial)

Next: Start Editing: Final edit before publishing
```

---

## Managing Multiple Workflows

### List Active Work

```bash
> /workflows list

Active Workflows (3):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. rfp-acme-corp-manufacturing-20251017-100523
   Title: Acme Corp manufacturing proposal
   Current: rfp-writing (3/5 complete)
   Age: 1h 25m

2. feature-oauth2-integration-20251017-110234
   Title: OAuth2 Integration
   Current: implementation (2/5 complete)
   Age: 45m

3. blog-ai-trends-2025-20251017-143056
   Title: AI Trends 2025 article
   Current: research (1/4 complete)
   Age: 10m
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Key information shown:**
- Instance ID (for resuming)
- Human-readable title
- Current phase and progress
- Time since started

---

### Resume Specific Workflow

```bash
> /workflows resume rfp-acme-corp-manufacturing-20251017-100523

✓ Resumed: Acme Corp manufacturing proposal
✓ Current phase: rfp-writing (3/5 complete)
✓ Completed: rfp-analysis, rfp-strategy, rfp-writing
✓ Next: rfp-review

You can continue with:
> Start RFP Review: Final review before submission
```

**When to use this:**
- Switching between multiple projects
- Returning after interruption
- Checking where you left off

---

### View Workflow Details

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

Completed Phases:
  ✓ rfp-analysis (25 min)
    Completed: 2025-10-17T10:30:00Z

  ✓ rfp-strategy (40 min)
    Completed: 2025-10-17T11:10:00Z

  ✓ rfp-writing (2h 0m)
    Completed: 2025-10-17T13:10:00Z

Pending Phases:
  ○ rfp-review
  ○ rfp-submission

Current Metrics:
  Pages: 12
  Sections: 4
  Words: 3,500
  Last measured: 2025-10-17T13:10:00Z

Notes:
  [2025-10-17T11:00] Need to emphasize sustainability in solution
  [2025-10-17T12:30] Include case study from Boeing project
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Shows:**
- Complete history of what's been done
- Time spent in each phase
- Current metrics (pages, lines, words, etc.)
- Notes added during work

---

### View Completed Work

```bash
> /workflows history --days 7

Completed Workflows (Last 7 Days):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. rfp-acme-corp-manufacturing-20251017-100523
   Title: Acme Corp manufacturing proposal
   Completed: 2025-10-17T15:30:00Z
   Duration: 3h 45m
   Breakdown:
     - rfp-analysis: 25 min
     - rfp-strategy: 40 min
     - rfp-writing: 2h 0m
     - rfp-review: 30 min
     - rfp-submission: 10 min

2. feature-user-profiles-20251016-141234
   Title: User Profile Pages
   Completed: 2025-10-16T17:00:00Z
   Duration: 2h 15m
   Breakdown:
     - idea-validation: 10 min
     - design: 35 min
     - implementation: 1h 0m
     - garden-tending: 20 min
     - deployment: 10 min

3. bugfix-payment-timeout-20251015-093045
   Title: Fix payment timeout
   Completed: 2025-10-15T09:45:00Z
   Duration: 12 min
   Breakdown:
     - idea-validation: 2 min (small change)
     - implementation: 5 min
     - deployment: 5 min
     (garden-tending skipped - only 3 lines changed)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Summary:
  Total completed: 3
  Average duration: 2h 4m
  Success rate: 100%
  Quality gates passed: 2/3
  Quality gates bypassed: 0/3
```

**Use cases:**
- "How long did the last RFP take?"
- "What did I work on last week?"
- "Am I getting faster or slower?"
- "How often am I bypassing quality gates?"

---

### Abandon Workflow

Sometimes you start work but decide not to continue:

```bash
> /workflows abandon blog-ai-trends-2025-20251017-143056 --reason "Topic already covered by competitor"

✓ Workflow abandoned: blog-ai-trends-2025-20251017-143056
✓ Reason: Topic already covered by competitor
✓ Moved to: .claude/workflows/abandoned/

Note: You can still view this instance with:
> /workflows show blog-ai-trends-2025-20251017-143056
```

**When to use:**
- Requirements changed
- Project cancelled
- Decided on different approach
- Duplicate work discovered

**Benefits:**
- Keep history (not deleted)
- Separate from active work
- Track why abandoned (analytics)

---

## Emergency Bypass

### When to Use

Use `--force-deploy` ONLY for genuine emergencies:

**✅ Valid emergencies:**
- Production outage affecting users
- Security vulnerability requiring immediate patch
- Legal/regulatory deadline with approval
- Critical data loss prevention

**❌ Not emergencies:**
- "Running late on deadline"
- "Don't feel like doing review"
- "Want to finish before weekend"
- "Tests failing, will fix later"

---

### How to Use

**Syntax:**
```bash
Start <ReleaseTriad>: <description> --force-deploy --justification "<reason>"
```

**Requirements:**
- Justification must be ≥10 characters
- No shell metacharacters (`$`, `;`, `|`, backticks, etc.)
- Clear explanation of emergency

---

### Examples by Domain

**Software Development:**
```bash
> Start Deployment: v2.0.2 --force-deploy --justification "Production API down for 10k users, immediate rollback needed, CTO approved"

⚠️  WARNING: Emergency Bypass Activated
Justification: Production API down for 10k users, immediate rollback needed, CTO approved

✓ Bypass approved - proceeding with deployment
📝 Event logged to: .claude/workflow_audit.log

IMPORTANT: Schedule Garden Tending for next non-emergency deployment
```

**RFP Writing:**
```bash
> Start RFP Submission: Acme Corp --force-deploy --justification "Submission deadline is 5pm today (1 hour), VP Sales approved submission without review"

⚠️  WARNING: Emergency Bypass Activated
Justification: Submission deadline is 5pm today (1 hour), VP Sales approved submission without review

✓ Bypass approved - proceeding with submission
📝 Event logged to: .claude/workflow_audit.log
```

**Content Publishing:**
```bash
> Start Publishing: Breaking news article --force-deploy --justification "Breaking news story, competitor publishing in 10 minutes, editor approved immediate publication"

⚠️  WARNING: Emergency Bypass Activated
Justification: Breaking news story, competitor publishing in 10 minutes, editor approved immediate publication

✓ Bypass approved - proceeding with publication
📝 Event logged to: .claude/workflow_audit.log

Note: Consider post-publication editing
```

---

### Audit Trail

Every bypass is logged:

**`.claude/workflow_audit.log`:**
```json
{"timestamp": "2025-10-17T14:30:00Z", "event": "emergency_bypass", "user": "jane.doe@company.com", "instance_id": "feature-payment-fix-20251017-143000", "justification": "Production API down for 10k users, immediate rollback needed, CTO approved", "metadata": {"version": "v2.0.2", "loc_changed": 15, "files_changed": 2}}
```

**Why this matters:**
- Compliance and accountability
- Review bypass patterns monthly
- Identify process improvements needed
- Demonstrate due diligence

**Good practice:**
```bash
# Monthly review
> cat .claude/workflow_audit.log | jq .justification

# Check if bypasses are truly emergencies
# If seeing "deadline" frequently → process issue
# If seeing "production down" → infrastructure issue
```

---

## Understanding Your Workflow Schema

### What is workflow.json?

**Location:** `.claude/workflow.json`

**Purpose:** Defines YOUR workflow rules (not hardcoded)

**Created by:** `/generate-triads` command

**Example for Software Development:**
```json
{
  "workflow_name": "software-development",
  "triads": [
    {
      "id": "idea-validation",
      "name": "Idea Validation",
      "type": "research",
      "position": 1,
      "required": true
    },
    {
      "id": "design",
      "name": "Design",
      "type": "planning",
      "position": 2,
      "required": true
    },
    {
      "id": "implementation",
      "name": "Implementation",
      "type": "execution",
      "position": 3,
      "required": true
    },
    {
      "id": "garden-tending",
      "name": "Garden Tending",
      "type": "quality",
      "position": 4,
      "required": "conditional"
    },
    {
      "id": "deployment",
      "name": "Deployment",
      "type": "release",
      "position": 5,
      "required": true
    }
  ],
  "workflow_rules": [
    {
      "rule_type": "quality_gate",
      "gate_triad": "garden-tending",
      "before_triad": "deployment",
      "condition": {
        "type": "significant_changes",
        "metrics": {
          "loc_threshold": 100,
          "files_threshold": 5
        }
      },
      "bypass_allowed": true
    }
  ]
}
```

---

### Triad Types

**`research`** - Gather information
- Software: idea-validation, discovery
- RFP: rfp-analysis
- Content: research

**`planning`** - Design approach
- Software: design, architecture
- RFP: rfp-strategy
- Content: planning, outlining

**`execution`** - Build/create
- Software: implementation, coding
- RFP: rfp-writing
- Content: drafting, writing

**`quality`** - Review/refine
- Software: garden-tending, code-review
- RFP: rfp-review, peer-review
- Content: editing, fact-checking

**`release`** - Publish/deploy
- Software: deployment, release
- RFP: rfp-submission
- Content: publishing

---

### How Rules Work

**The Pattern:**
```
IF [triad.type == "release"]
AND [significant_changes detected]
AND [quality triad NOT completed]
THEN [block release, require quality]
```

**What "significant changes" means:**
- Defined per workflow type
- Different thresholds for different domains
- Measured automatically

**Software example:**
- 100+ lines of code
- 5+ files modified
- New features added

**RFP example:**
- 10+ pages written
- 3+ major sections
- 2,000+ words

**Content example:**
- 1,500+ words written
- 5+ sections
- 3+ images added

---

### Customizing Your Schema

You can edit `.claude/workflow.json` to customize rules:

**Change thresholds:**
```json
{
  "condition": {
    "type": "significant_changes",
    "metrics": {
      "loc_threshold": 150,  // Changed from 100
      "files_threshold": 8    // Changed from 5
    }
  }
}
```

**Disable bypass:**
```json
{
  "bypass_allowed": false  // Changed from true
}
```

**Add custom metrics:**
```json
{
  "condition": {
    "type": "significant_changes",
    "metrics": {
      "test_coverage_below": 80,
      "complexity_above": 10
    }
  }
}
```

**Note:** Custom metrics support coming in v0.8.0

---

## Understanding Instance Files

### Where Are They?

```
.claude/workflows/
├── instances/              # Active work
│   ├── feature-oauth2-20251017-100523.json
│   ├── rfp-acme-20251017-110234.json
│   └── blog-post-20251017-143056.json
├── completed/              # Finished work
│   ├── feature-profiles-20251016-141234.json
│   └── bugfix-timeout-20251015-093045.json
└── abandoned/              # Cancelled work
    └── experiment-20251014-120000.json
```

---

### What's in an Instance File?

**`feature-oauth2-20251017-100523.json`:**
```json
{
  "instance_id": "feature-oauth2-20251017-100523",
  "workflow_type": "software-development",
  "workflow_schema_version": "1.0",

  "metadata": {
    "title": "OAuth2 Integration",
    "description": "Add OAuth2 authentication to login flow",
    "started_by": "jane.doe@company.com",
    "started_at": "2025-10-17T10:05:23Z",
    "status": "in_progress",
    "completed_at": null
  },

  "workflow_progress": {
    "current_triad": "implementation",
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
        "duration_minutes": 30,
        "metrics": {
          "adrs_created": 3,
          "approval_received": true
        }
      }
    ],
    "pending_triads": [
      "implementation",
      "garden-tending",
      "deployment"
    ]
  },

  "change_metrics": {
    "loc_added": 245,
    "loc_deleted": 12,
    "files_changed": 8,
    "new_files": [
      "src/auth/oauth2.py",
      "tests/test_oauth2.py"
    ],
    "has_new_features": true,
    "measured_at": "2025-10-17T11:30:00Z",
    "base_ref": "main"
  },

  "bypass_events": [],

  "notes": [
    {
      "timestamp": "2025-10-17T10:20:00Z",
      "user": "jane.doe@company.com",
      "note": "Need to check with security team about token storage"
    }
  ]
}
```

**Key sections:**
- **metadata** - Who, what, when, status
- **workflow_progress** - Which phases complete, which pending
- **change_metrics** - Code/content changes measured
- **bypass_events** - Emergency bypasses used
- **notes** - Annotations during work

---

### Can I Edit Instance Files?

**Yes, but be careful:**

Instance files are JSON - you can edit them, but:
- ✅ Adding notes: Safe
- ✅ Fixing typos in title: Safe
- ⚠️ Changing completed_triads: May bypass quality gates
- ⚠️ Changing metrics: May affect enforcement
- ❌ Changing instance_id: Will break references

**Better approach:**
Use CLI commands when possible:
```bash
# Add notes
> /workflows note <instance-id> "Need to update docs"

# Update status
> /workflows status <instance-id> abandoned

# Fix title
> /workflows rename <instance-id> "Better Title"
```

**Note:** CLI commands coming in v0.7.0

---

## Complete Workflow Enforcement Examples

### Example 1: Happy Path (All Steps Completed)

```bash
# Start new work
> Start Idea Validation: OAuth2 authentication
✓ Instance created: feature-oauth2-auth-20251017-100000
✓ Idea validation complete (10 min)

# Continue to design
> Start Design: OAuth2 architecture
✓ Resuming instance... (1/5 → 2/5)
✓ Design complete (35 min)

# Implement
> Start Implementation: OAuth2 code
✓ Resuming instance... (2/5 → 3/5)
✓ Implementation complete (1h 20m)
[Substantial changes: 8 components, new auth system]

# Try to deploy
> Start Deployment: v2.1.0
ERROR: Workflow Steps Missing
Must complete garden-tending (changes substantial)

# Complete quality review
> Start Garden Tending: Post-OAuth2 cleanup
✓ Resuming instance... (3/5 → 4/5)
✓ Garden tending complete (20 min)

# Now deployment works
> Start Deployment: v2.1.0
✓ Checking workflow... all steps complete
✓ Deployment initiated (2h 25m total)
```

---

### Example 2: Small Change (Quality Step Skipped)

```bash
# Start quick bugfix
> Start Idea Validation: Fix login button color
✓ Instance created: bugfix-login-button-20251017-110000
✓ Idea validation complete (2 min)

# Design (quick)
> Start Design: Color scheme update
✓ Design complete (3 min)

# Implement (minimal change)
> Start Implementation: Update CSS
✓ Implementation complete (5 min)
[Minimal changes: 1 component, 3 lines]

# Deploy directly
> Start Deployment: v2.0.1
✓ Checking workflow...
✓ Conditional: garden-tending NOT required (changes minimal)
✓ Deployment initiated (10 min total)
```

---

### Example 3: Skipping Steps (Blocked)

```bash
# Start work
> Start Idea Validation: Major refactoring
✓ Instance created

# Try to skip straight to implementation
> Start Implementation: Refactor auth module
ERROR: Workflow Steps Missing
Cannot skip design (position 2)
Must complete triads in sequence

# Must do design first
> Start Design: Refactoring architecture
✓ Design complete

# Now implementation works
> Start Implementation: Refactor auth module
✓ Implementation proceeds
```

---

### Example 4: Going Backward (Blocked)

```bash
# Complete several steps
> Start Idea Validation: User profiles
> Start Design: Profile architecture
> Start Implementation: Profile pages
✓ 3/5 triads complete

# Realize design needs revision
> Start Design: Revised profile architecture
ERROR: Cannot Go Backward in Workflow
Current position: implementation (3/5)
Attempted: design (2/5)

Solution: Start new workflow instance for design revision
OR continue forward and incorporate changes during quality review
```

---

### Example 5: Emergency Bypass

```bash
# Production is down
> Start Implementation: Hotfix payment timeout
✓ Implementation complete
[Critical fix: 15 lines]

# Need to deploy NOW
> Start Deployment: v2.0.2
ERROR: Workflow Steps Missing
Must complete garden-tending

# Use emergency bypass
> Start Deployment: v2.0.2 --force-deploy --justification "Production payment system down affecting all users, CTO approved immediate deployment, will run quality review post-deployment"

⚠️  WARNING: Emergency Bypass Activated
✓ Bypass approved
✓ Event logged to audit trail
✓ Deployment proceeding

REMINDER: Schedule garden-tending for next deployment
```

---

### Example 6: Multiple Concurrent Workflows

```bash
# Start OAuth2 work
> Start Idea Validation: OAuth2 integration
✓ Instance: feature-oauth2-20251017-100000

# Start login UI work (concurrent)
> Start Idea Validation: Login UI redesign
✓ Instance: feature-login-ui-20251017-110000

# Continue OAuth2
> Start Design: OAuth2 architecture
✓ Resuming: feature-oauth2-20251017-100000 (auto-detected)

# Switch to login UI
> Start Design: Login mockups
✓ Resuming: feature-login-ui-20251017-110000 (auto-detected)

# View all active work
> /workflows list
Active Workflows (2):
1. feature-oauth2-20251017-100000 (design, 2/5)
2. feature-login-ui-20251017-110000 (design, 2/5)

# Each workflow enforced independently
```

---

## Troubleshooting

### "No workflow schema found"

**Error:**
```
⚠️  Warning: .claude/workflow.json not found
✓  Workflow enforcement disabled
✓  Proceeding without quality gates
```

**Why this happens:**
- First time using v0.7.0
- Manually deleted workflow.json
- Working in new project

**Solution:**
```bash
> /generate-triads

# System will:
# - Interview you about workflow
# - Generate triads
# - Create workflow.json
```

**Temporary workaround:**
Work continues normally, just without enforcement:
```bash
> Start Design: OAuth2

✓ Design complete
(no instance tracking, no quality gates)
```

---

### "Cannot find instance to resume"

**Error:**
```
ERROR: Instance not found: feature-oauth2-20251017-100523
```

**Why this happens:**
- Instance ID mistyped
- Instance completed/abandoned
- Instance file deleted

**Solution:**
```bash
# List available instances
> /workflows list

Active Workflows (2):
1. feature-oauth2-integration-20251017-110234  ← Use this ID
2. blog-post-20251017-143056

# Resume with correct ID
> /workflows resume feature-oauth2-integration-20251017-110234
```

---

### "Required step missing but I just completed it"

**Error:**
```
ERROR: Workflow Steps Missing
Must complete garden-tending before deployment
(but you just ran it)
```

**Why this happens:**
- Instance file didn't update
- Different instance was used
- File locking issue (rare)

**Solution:**
```bash
# Check instance status
> /workflows show <instance-id>

# Look at completed_triads
# If the triad is missing, the completion wasn't recorded

# Check if you have multiple instances
> /workflows list

# Make sure you're working with the correct instance
# Re-run the required triad
> Start Garden Tending: Post-implementation cleanup

# Should work now
> Start Deployment: v2.1.0
```

---

### "Significance assessment seems wrong"

**Error:**
```
ERROR: Garden Tending Required
Changes assessed as substantial (8 components modified)

(but you only changed configuration)
```

**Why this happens:**
- Metrics include auto-generated files
- Metrics measured against wrong baseline
- Working directory has uncommitted changes from other work

**Check what's measured:**
```bash
# For code workflows, check git
git diff --numstat HEAD~1

# For content workflows, check files modified
ls -la docs/

# Shows what the system sees
```

**Solutions:**

**Option 1: Commit work separately**
```bash
# Commit actual changes
git add src/config.yml
git commit -m "Update OAuth config"

# Commit auto-generated separately
git add package-lock.json
git commit -m "Update dependencies"

# Significance assessed per commit
```

**Option 2: Use bypass with justification**
```bash
> Start Deployment: v2.0.1 --force-deploy --justification "Significance inflated by auto-generated files, actual change is configuration only (10 lines), no quality review needed"
```

**Option 3: Customize thresholds**
```bash
# Edit .claude/workflow.json to adjust what "substantial" means for your workflow
# See "Customizing Your Schema" section
```

---

### "Git not available"

**Error:**
```
⚠️  Warning: Git not available
✓  Metrics defaulting to 0 (quality gates won't trigger)
✓  Proceeding with deployment
```

**Why this happens:**
- Running in environment without git
- Git not in PATH
- Not in a git repository

**Impact:**
- Can't measure changes
- Quality gates won't trigger automatically
- Must rely on manual judgment

**Solution:**
```bash
# Ensure git available
which git

# If not installed
sudo apt-get install git  # Ubuntu/Debian
brew install git          # macOS

# Ensure in git repo
git status
```

---

## Best Practices

### 1. Start Small, Track Everything

**Don't overthink it - just start:**
```bash
> Start <FirstTriad>: Brief description of what you're doing
```

System handles the rest:
- Creates instance
- Tracks progress
- Measures changes
- Enforces quality

**Example:**
```bash
# Instead of:
> Start Design: Comprehensive OAuth2 authentication system with support for multiple providers including Google, GitHub, and Microsoft using industry-standard protocols...

# Just say:
> Start Design: OAuth2 authentication

# System generates ID:
# feature-oauth2-authentication-20251017-100523
```

---

### 2. Use Descriptive Titles

**Good titles help you find work later:**

**❌ Bad:**
```bash
> Start Implementation: Fix bug
> Start Implementation: Update code
> Start Implementation: Make changes
```

**✅ Good:**
```bash
> Start Implementation: Fix payment timeout on checkout
> Start Implementation: OAuth2 authentication for login
> Start Implementation: Add dark mode to settings page
```

**Why it matters:**
```bash
> /workflows list

Active Workflows (3):
1. bugfix-payment-timeout-checkout-20251017-100523  ← Clear
2. feature-oauth2-authentication-login-20251017-110234  ← Clear
3. feature-update-code-20251017-143056  ← Unclear - what code?
```

---

### 3. Review History Weekly

**Learn from your patterns:**
```bash
> /workflows history --days 7

# Questions to ask:
# - Average duration: Am I getting faster?
# - Quality gates: Am I bypassing too often?
# - Abandoned work: Am I starting work I don't finish?
# - Phase distribution: Where do I spend most time?
```

**Example insights:**
```
Last 7 days:
- 5 completed workflows
- Average: 2h 15m per workflow
- Implementation phase: 60% of time (should I get help?)
- Quality gates bypassed: 2/5 (40% bypass rate - too high?)
- Abandoned: 1/6 (17% - requirements unclear upfront?)
```

---

### 4. Add Notes During Work

**Capture context in the moment:**
```bash
> /workflows note feature-oauth2-20251017-100523 "Security team approved token storage approach"

> /workflows note rfp-acme-20251017-110234 "Client wants sustainability emphasized in executive summary"

> /workflows note blog-post-20251017-143056 "Need to fact-check statistics from McKinsey report"
```

**Why this helps:**
```bash
# Later when you resume:
> /workflows show feature-oauth2-20251017-100523

Notes:
  [10:20] Security team approved token storage approach
  [11:45] Need to implement refresh token rotation
  [13:30] Frontend team needs OAuth config by EOD tomorrow
```

**You'll remember the context** even after interruptions.

---

### 5. Don't Abuse Emergency Bypass

**Track your bypass rate:**
```bash
# Monthly review
> cat .claude/workflow_audit.log | grep emergency_bypass | wc -l
15 bypasses

> /workflows history --days 30 | grep "Completed:" | wc -l
20 workflows

# 15/20 = 75% bypass rate ← TOO HIGH
```

**Healthy bypass rates:**
- 0-10%: Excellent (quality gates working)
- 10-25%: Acceptable (occasional emergencies)
- 25-50%: Concerning (process may need adjustment)
- 50%+: Broken (either thresholds wrong OR workflow culture issue)

**If bypass rate is high:**
1. **Review justifications** - Are they really emergencies?
2. **Check thresholds** - Are they too strict for your domain?
3. **Examine process** - Is quality gate adding value or just friction?

---

### 6. Commit Instance Files (Team Workflows)

**Share workflow history with your team:**
```bash
# Add to git
git add .claude/workflows/

# Commit periodically
git commit -m "Update workflow instances"

# Push to remote
git push
```

**Benefits:**
- Team sees what you're working on
- Handoff work to teammates
- Track team-wide metrics
- Preserve history even if local files lost

**Example:**
```bash
# Jane starts work
> Start Implementation: OAuth2 integration
✓ Instance: feature-oauth2-20251017-100523

# Jane commits instance
git add .claude/workflows/instances/feature-oauth2-20251017-100523.json
git commit -m "Start OAuth2 implementation"
git push

# Bob pulls and sees active work
git pull
> /workflows list
Active: feature-oauth2-20251017-100523 (Jane, 2h ago, implementation)

# Bob can resume if Jane is out
> /workflows resume feature-oauth2-20251017-100523
```

---

## FAQ

### Why track instances instead of global state?

**Old way (single state file):**
- ❌ Can only work on one thing at a time
- ❌ Switching work loses context
- ❌ No history of completed work
- ❌ Can't resume interrupted work

**New way (instance files):**
- ✅ Work on multiple projects concurrently
- ✅ Each instance preserves its own context
- ✅ Complete history maintained
- ✅ Resume anytime, even weeks later

---

### Do I need workflow.json?

**Technically no**, but **practically yes**.

**Without workflow.json:**
```bash
> Start Deployment: v2.1.0

⚠️  Warning: .claude/workflow.json not found
✓  Workflow enforcement disabled
✓  Proceeding without quality gates
```

You can still use triads, but:
- ❌ No instance tracking
- ❌ No quality gates
- ❌ No history
- ❌ No metrics

**With workflow.json:**
- ✅ Full instance tracking
- ✅ Automatic quality gates
- ✅ Complete history
- ✅ Change metrics

**Get it by:**
```bash
> /generate-triads
```

---

### Can I customize thresholds?

**Yes** - edit `.claude/workflow.json`:

**Change from 100 lines to 150:**
```json
{
  "workflow_rules": [
    {
      "condition": {
        "metrics": {
          "loc_threshold": 150  // Changed from 100
        }
      }
    }
  ]
}
```

**Change from 5 files to 8:**
```json
{
  "workflow_rules": [
    {
      "condition": {
        "metrics": {
          "files_threshold": 8  // Changed from 5
        }
      }
    }
  ]
}
```

**Add custom metrics (v0.8.0+):**
```json
{
  "workflow_rules": [
    {
      "condition": {
        "metrics": {
          "test_coverage_below": 80,
          "complexity_above": 10
        }
      }
    }
  ]
}
```

---

### What if I have custom triads?

**This is the whole point** - the system works with ANY triads you generate.

**Example 1: Legal Document Review**
```json
{
  "workflow_name": "legal-review",
  "triads": [
    {"id": "intake", "type": "research"},
    {"id": "research", "type": "research"},
    {"id": "drafting", "type": "execution"},
    {"id": "peer-review", "type": "quality"},
    {"id": "client-review", "type": "release"}
  ],
  "workflow_rules": [
    {
      "gate_triad": "peer-review",
      "before_triad": "client-review",
      "condition": {
        "metrics": {
          "page_threshold": 5,
          "clause_threshold": 2
        }
      }
    }
  ]
}
```

**Example 2: Data Analysis**
```json
{
  "workflow_name": "data-analysis",
  "triads": [
    {"id": "data-collection", "type": "research"},
    {"id": "analysis", "type": "execution"},
    {"id": "validation", "type": "quality"},
    {"id": "reporting", "type": "release"}
  ],
  "workflow_rules": [
    {
      "gate_triad": "validation",
      "before_triad": "reporting",
      "condition": {
        "metrics": {
          "dataset_rows": 10000,
          "statistical_tests": 3
        }
      }
    }
  ]
}
```

---

### Does this work for teams?

**Currently:** Per-machine only (instance files local)

**Best practice:** Commit instance files to git

```bash
# Share with team
git add .claude/workflows/
git commit -m "Update workflow instances"
git push

# Team can see and resume
git pull
> /workflows list
```

**Future (v0.9.0+):**
- Cloud sync
- Team dashboards
- Shared workflows
- Real-time collaboration

---

### How do I migrate from v0.6.x?

**Good news:** No migration needed!

**Old workflows (v0.6.x):**
- Continue working normally
- No instance tracking
- No quality gates

**New workflows (v0.7.0+):**
- Automatic instance creation
- Full tracking and enforcement

**To start using new system:**
```bash
# Just run generate-triads
> /generate-triads

# Creates workflow.json
# Next time you start work, instance created automatically
> Start Design: OAuth2

✓ Instance created: feature-oauth2-20251017-100523
```

That's it!

---

## Getting Help

### Documentation
- [Installation Guide](INSTALLATION.md)
- [Usage Guide](USAGE.md)
- [Workflow Schema Reference](WORKFLOW_SCHEMA.md)
- [Troubleshooting](TROUBLESHOOTING.md)

### Support
- GitHub Issues: https://github.com/reliable-agents-ai/triads/issues
- Discussions: https://github.com/reliable-agents-ai/triads/discussions

### Feature Requests
We'd love to hear:
- What workflows are you using?
- What metrics matter for your domain?
- What CLI commands would help?
- What analytics would be useful?

**Open an issue** with your use case!

---

**Version:** 0.7.0 (PROPOSED)
**Status:** Draft for validation
**Last updated:** 2025-10-17
