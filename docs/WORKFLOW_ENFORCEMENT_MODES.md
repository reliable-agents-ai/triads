# Workflow Enforcement Modes (PROPOSED)

> **Status**: Draft for validation - NOT YET IMPLEMENTED
>
> This document describes the three enforcement modes available in v0.7.0

---

## Overview

Workflow enforcement supports **three modes** to match your team's needs:

1. **Strict Mode** - Blocks deviations, requires emergency bypass
2. **Recommended Mode** - Warns about deviations, requires documented reason (DEFAULT)
3. **Optional Mode** - Logs deviations, no friction

**Key insight:** Different workflows need different levels of enforcement. Medical software requires strict gates; creative work benefits from flexibility.

---

## Enforcement Modes Comparison

| Mode | When to Use | Deviation Behavior | Friction Level |
|------|-------------|-------------------|----------------|
| **Strict** | Regulated industries, compliance-critical, high-stakes | Hard block, requires `--force-deploy` | High |
| **Recommended** | Most workflows, collaborative teams, iterative work | Warns, requires `--skip <triad> --reason` | Medium |
| **Optional** | Experimental workflows, experienced teams, low-risk | Silently logs deviation | Low |

---

## Mode 1: Strict Enforcement

**Use when:** Compliance-critical, regulatory requirements, high-risk work

**Behavior:** Hard blocks deviations unless emergency bypass used

### Example: Medical Device Software

```json
{
  "workflow_name": "medical-device-development",
  "enforcement": {
    "mode": "strict",
    "per_triad_overrides": {
      "safety-review": "strict",      // Cannot be skipped ever
      "regulatory-compliance": "strict", // Cannot be skipped ever
      "design": "recommended"         // Can be skipped with reason
    }
  },
  "triads": [
    {"id": "requirements", "position": 1},
    {"id": "design", "position": 2},
    {"id": "implementation", "position": 3},
    {"id": "safety-review", "position": 4},
    {"id": "regulatory-compliance", "position": 5},
    {"id": "deployment", "position": 6}
  ]
}
```

### User Experience (Strict Mode)

**Trying to skip required step:**
```bash
> Start Implementation: Patient monitoring feature

🛑 ERROR: Workflow Steps Missing
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Cannot proceed to implementation without completing required steps.

Enforcement mode: STRICT
Missing required triads:
  - design (position 2) - CANNOT BE SKIPPED

You must complete design before proceeding:
> Start Design: Patient monitoring architecture

OR use emergency override (requires documentation):
> Start Implementation: ... --force-skip design --justification "CTO approved, emergency patient safety fix, design completed offline"

⚠️  Warning: Emergency overrides are logged and audited
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Trying to skip critical safety step:**
```bash
> Start Deployment: v2.0.1

🛑 CRITICAL: Safety Review Required
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Enforcement mode: STRICT
Missing critical triad: safety-review

Medical device software requires safety review before deployment.
This is a STRICT enforcement rule and cannot be bypassed without:

Emergency override (VP Engineering approval required):
> Start Deployment: v2.0.1 --force-skip safety-review --justification "VP Engineering approved emergency deployment, safety review in progress, patient safety not impacted"

⚠️  All emergency overrides are:
  - Logged to audit trail
  - Reported to compliance team
  - Subject to post-deployment review
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Audit Trail (Strict Mode)

```json
{
  "timestamp": "2025-10-17T10:30:00Z",
  "event": "strict_enforcement_override",
  "enforcement_mode": "strict",
  "triad_skipped": "safety-review",
  "user": "jane.doe@company.com",
  "justification": "VP Engineering approved emergency deployment, safety review in progress, patient safety not impacted",
  "instance_id": "feature-patient-monitoring-20251017-100000",
  "compliance_flags": ["high_risk", "requires_post_review"]
}
```

---

## Mode 2: Recommended Enforcement (DEFAULT)

**Use when:** Most workflows, collaborative work, iterative development

**Behavior:** Warns about deviations, requires documented reason but doesn't block

### Example: Software Development

```json
{
  "workflow_name": "software-development",
  "enforcement": {
    "mode": "recommended",  // Default
    "per_triad_overrides": {
      "garden-tending": "recommended",  // Warn if substantial changes
      "deployment": "recommended"
    }
  },
  "triads": [
    {"id": "idea-validation", "position": 1},
    {"id": "design", "position": 2},
    {"id": "implementation", "position": 3},
    {"id": "garden-tending", "position": 4},
    {"id": "deployment", "position": 5}
  ]
}
```

### User Experience (Recommended Mode)

**Trying to skip step:**
```bash
> Start Implementation: OAuth2 authentication

⚠️  RECOMMENDED: Complete design first
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Enforcement mode: RECOMMENDED

Your workflow recommends completing these steps first:
  ✗ design (position 2) - not started

Skipping design may lead to:
  - Implementation issues discovered later
  - Rework needed
  - Missed design considerations

Options:
  1. Follow workflow:
     > Start Design: OAuth2 architecture

  2. Skip with reason:
     > Start Implementation: OAuth2 --skip design --reason "Design completed in Figma with team, mockups approved"

  3. Use different instance if design done elsewhere
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

To proceed, add: --skip design --reason "..."
```

**User provides reason and continues:**
```bash
> Start Implementation: OAuth2 --skip design --reason "Design completed in Figma with team yesterday, mockups in Slack #design channel"

✓ Workflow deviation recorded
✓ Skipped: design
✓ Reason: Design completed in Figma with team yesterday, mockups in Slack #design channel
✓ Proceeding with implementation...

ℹ️  Deviation logged to instance file for tracking
```

**Going backward (with reason):**
```bash
> Start Design: Revised OAuth2 architecture

⚠️  BACKWARD MOVEMENT DETECTED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Current position: implementation (3/5)
Requested: design (2/5)

Going backward typically indicates:
  - Design issue discovered during implementation
  - Requirements changed
  - Iterative refinement needed

To proceed, explain why:
> Start Design: Revised OAuth2 architecture --reason "Implementation revealed token storage security issue, revising design"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

> Start Design: Revised OAuth2 architecture --reason "Implementation revealed token storage security issue, revising design"

✓ Workflow deviation recorded
✓ Type: backward_movement (implementation → design)
✓ Reason: Implementation revealed token storage security issue...
✓ Proceeding with design revision...
```

### Audit Trail (Recommended Mode)

```json
{
  "timestamp": "2025-10-17T10:30:00Z",
  "event": "workflow_deviation",
  "enforcement_mode": "recommended",
  "deviation_type": "skip_forward",
  "from_triad": "idea-validation",
  "to_triad": "implementation",
  "skipped": ["design"],
  "reason": "Design completed in Figma with team yesterday, mockups in Slack #design channel",
  "user": "jane.doe@company.com",
  "instance_id": "feature-oauth2-20251017-100000"
}
```

---

## Mode 3: Optional Enforcement

**Use when:** Experimental workflows, very experienced teams, low-risk exploration

**Behavior:** Silently logs deviations, provides no warnings or friction

### Example: Content Creation (Blog)

```json
{
  "workflow_name": "blog-post-creation",
  "enforcement": {
    "mode": "optional",  // Very relaxed
    "track_deviations": true  // Still log for analytics
  },
  "triads": [
    {"id": "research", "position": 1},
    {"id": "outlining", "position": 2},
    {"id": "drafting", "position": 3},
    {"id": "editing", "position": 4},
    {"id": "publishing", "position": 5}
  ]
}
```

### User Experience (Optional Mode)

**Skipping steps (no warnings):**
```bash
> Start Drafting: AI trends 2025 article

ℹ️  Note: Skipped research, outlining
   To document why: add --reason "..."

> Start Drafting: AI trends 2025 article --reason "Research done during morning reading, outline in head"

✓ Starting drafting...
✓ Deviation logged (optional mode - no warnings)
```

**Or skip without reason (still logged):**
```bash
> Start Drafting: Quick thoughts on AI

✓ Starting drafting...
ℹ️  Skipped: research, outlining (no reason provided)
```

### Audit Trail (Optional Mode)

```json
{
  "timestamp": "2025-10-17T10:30:00Z",
  "event": "workflow_deviation",
  "enforcement_mode": "optional",
  "deviation_type": "skip_forward",
  "from_triad": null,
  "to_triad": "drafting",
  "skipped": ["research", "outlining"],
  "reason": "Research done during morning reading, outline in head",
  "user": "jane.doe@company.com",
  "instance_id": "blog-ai-trends-20251017-100000"
}
```

---

## Per-Triad Override Configuration

You can mix enforcement levels within a single workflow:

### Example: RFP Writing (Mixed Enforcement)

```json
{
  "workflow_name": "rfp-writing",
  "enforcement": {
    "mode": "recommended",  // Default for most triads
    "per_triad_overrides": {
      "legal-review": "strict",       // Cannot skip (contracts)
      "rfp-analysis": "optional",     // Can skip freely (sometimes client provides)
      "rfp-strategy": "recommended",  // Should do, can skip with reason
      "rfp-review": "recommended"     // Should do if substantial
    }
  },
  "triads": [
    {"id": "rfp-analysis", "position": 1},
    {"id": "rfp-strategy", "position": 2},
    {"id": "rfp-writing", "position": 3},
    {"id": "rfp-review", "position": 4},
    {"id": "legal-review", "position": 5},
    {"id": "rfp-submission", "position": 6}
  ]
}
```

**User experience with mixed enforcement:**

```bash
# Skip analysis (optional mode - no warning)
> Start RFP Strategy: Acme Corp win themes
ℹ️  Skipped: rfp-analysis (optional - no reason required)
✓ Proceeding...

# Skip strategy (recommended mode - requires reason)
> Start RFP Writing: Acme Corp proposal

⚠️  RECOMMENDED: Complete rfp-strategy first
To skip: --skip rfp-strategy --reason "..."

> Start RFP Writing: Acme Corp proposal --skip rfp-strategy --reason "Strategy session with sales team yesterday"
✓ Deviation logged, proceeding...

# Try to skip legal review (strict mode - blocked)
> Start RFP Submission: Acme Corp

🛑 CRITICAL: Legal Review Required
Enforcement mode: STRICT
Cannot skip legal-review for contracts.

You must either:
  1. Complete legal review
  2. Emergency override: --force-skip legal-review --justification "..."
```

---

## Configuration Guide

### Setting Enforcement Mode

**In `.claude/workflow.json`:**

```json
{
  "workflow_name": "my-workflow",
  "enforcement": {
    "mode": "recommended",  // strict | recommended | optional
    "track_deviations": true,  // Always log deviations (even in optional mode)
    "require_reason": true,    // Require --reason flag (recommended/strict modes)
    "allow_backward": true,    // Allow going backward with reason
    "per_triad_overrides": {
      "critical-step": "strict",
      "optional-step": "optional"
    }
  }
}
```

---

### When to Use Each Mode

**Use STRICT when:**
- Regulatory compliance required (medical, finance, legal)
- Safety-critical systems (aerospace, automotive, medical devices)
- Audit requirements (SOC2, HIPAA, ISO)
- Client contractually requires process adherence
- High-stakes work where deviation = risk

**Use RECOMMENDED when:**
- Standard software development
- Collaborative workflows (design happens in multiple tools)
- Iterative work (learning as you go)
- Trusted teams with good judgment
- Want process improvement insights

**Use OPTIONAL when:**
- Experimental workflows (still figuring out process)
- Very experienced teams (know when to deviate)
- Low-risk work (blog posts, internal docs)
- Rapid prototyping
- Personal projects

---

## Deviation Analytics

Regardless of enforcement mode, all deviations are logged for insights:

```bash
> /workflows analyze --days 30

Workflow Deviation Analysis (Last 30 Days):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Enforcement Mode Distribution:
  - Strict: 5 workflows (critical systems)
  - Recommended: 18 workflows (standard work)
  - Optional: 2 workflows (experimental)

Most Skipped Triads:
  1. design (15/25 workflows - 60%)
     Enforcement: recommended
     Common reasons:
       - "Design in Figma" (8)
       - "Pair programming" (4)
       - "Simple change" (3)

     Recommendation: Consider:
       - Adding "Design complete in Figma" workflow variant
       - Defining "simple change" criteria

  2. rfp-analysis (8/12 RFP workflows - 67%)
     Enforcement: optional
     Common reasons:
       - "Client provided requirements" (5)
       - "Reusing previous analysis" (3)

     Recommendation: Working as intended (optional mode)

Backward Movement:
  - implementation → design: 3 occurrences
    Reasons: "Security issue found" (2), "Requirements changed" (1)

  Recommendation: Consider adding "design review checkpoint" after implementation starts

Strict Enforcement Overrides: 2 occurrences
  - Both for "safety-review" triad (medical device workflow)
  - Both approved by VP Engineering
  - Both had post-deployment review completed

  Status: All overrides properly handled ✓

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Migration Between Modes

You can change enforcement mode at any time:

### Tightening Enforcement (Optional → Recommended)

```json
{
  "enforcement": {
    "mode": "recommended",  // Changed from "optional"
    "migration": {
      "previous_mode": "optional",
      "changed_at": "2025-10-17T10:00:00Z",
      "reason": "Team growing, want more process consistency"
    }
  }
}
```

**Effect on existing instances:**
- Existing instances continue with old mode
- New instances use new mode
- No retroactive changes

### Relaxing Enforcement (Strict → Recommended)

```json
{
  "enforcement": {
    "mode": "recommended",  // Changed from "strict"
    "per_triad_overrides": {
      "safety-review": "strict"  // Keep critical steps strict
    },
    "migration": {
      "previous_mode": "strict",
      "changed_at": "2025-10-17T10:00:00Z",
      "reason": "Too much friction, team bypassing with fake reasons. Keeping safety-review strict."
    }
  }
}
```

---

## Best Practices by Mode

### Strict Mode Best Practices

✅ **Do:**
- Document exactly which triads are strict and why
- Provide clear emergency override process
- Review all overrides weekly
- Train team on compliance requirements
- Keep override justifications detailed

❌ **Don't:**
- Make everything strict (causes override fatigue)
- Use strict mode without real compliance need
- Make override process too complex (encourages workarounds)

### Recommended Mode Best Practices

✅ **Do:**
- Provide helpful context in warnings
- Make it easy to provide reasons
- Review deviation patterns monthly
- Adjust workflow based on common skips
- Celebrate teams that follow recommended flow

❌ **Don't:**
- Shame teams for deviations (kills honest reporting)
- Ignore patterns (if everyone skips design, fix workflow)
- Make reasons mandatory without explaining why

### Optional Mode Best Practices

✅ **Do:**
- Still encourage reason documentation
- Review logs to understand actual workflow
- Use for experimental workflows
- Transition to recommended mode once workflow stabilizes

❌ **Don't:**
- Use optional mode for compliance-critical work
- Forget to review logs (defeats purpose of tracking)
- Leave in optional mode forever (recommend/strict usually better)

---

## Command Reference

### Skip Forward (Recommended/Optional Mode)

```bash
# With reason (recommended)
> Start <Triad>: <description> --skip <triad-id> --reason "Why skipping"

# Without reason (optional mode only)
> Start <Triad>: <description>
```

### Skip Backward (Recommended/Optional Mode)

```bash
# Going back with reason
> Start <PreviousTriad>: <description> --reason "Why going backward"
```

### Emergency Override (Strict Mode)

```bash
# Force skip strict enforcement
> Start <Triad>: <description> --force-skip <triad-id> --justification "Emergency reason with approval"
```

### View Deviations

```bash
# View deviations for specific instance
> /workflows show <instance-id> --include-deviations

# Analyze deviation patterns
> /workflows analyze --days 30
```

---

## FAQ

### Can I have different modes for different workflows?

**Yes!** Each workflow has its own `workflow.json` with its own enforcement mode.

Example:
- Medical device workflow: `strict`
- Internal tools workflow: `recommended`
- Blog writing workflow: `optional`

### Can I change modes mid-project?

**Yes**, but it only affects new instances. Existing instances continue with their original mode.

### What if someone skips critical steps even in strict mode?

Strict mode still allows emergency overrides. All overrides are:
- Logged to audit trail
- Require detailed justification
- Reviewable by management
- Flagged for compliance review

If overrides are frequent, consider:
1. Is the workflow realistic?
2. Is the strict requirement necessary?
3. Do we need better training?

### How do I know which mode to use?

**Start with recommended mode** for most workflows. Move to:
- **Strict** if: Compliance required, high risk, audit requirements
- **Optional** if: Experimental, very experienced team, low risk

### Can I change enforcement for specific triads only?

**Yes!** Use `per_triad_overrides`:

```json
{
  "enforcement": {
    "mode": "recommended",
    "per_triad_overrides": {
      "security-review": "strict",
      "docs-update": "optional"
    }
  }
}
```

---

**Version:** 0.7.0 (PROPOSED)
**Status:** Draft for validation
**Last updated:** 2025-10-17
