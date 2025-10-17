# Workflow Enforcement Guide

> Automatic quality gates that ensure Garden Tending happens before deployment

---

## What is Workflow Enforcement?

**Workflow Enforcement** is an automatic quality system that ensures your code goes through proper maintenance (Garden Tending) before deployment when changes are significant.

**The Problem It Solves:**

In fast-paced development, it's easy to skip the Garden Tending phase and jump straight from Implementation to Deployment. This creates technical debt that accumulates over time.

**The Solution:**

The system automatically detects when changes are significant enough to warrant Garden Tending and blocks deployment until maintenance is complete—or allows you to override with a documented justification.

---

## How It Works

### Automatic Detection

When you try to deploy (`Start Deployment: v0.7.0`), the system automatically checks if Garden Tending is required by analyzing your recent changes:

**Garden Tending Required If:**
- **More than 100 lines of code changed**, OR
- **More than 5 files modified**, OR
- **New features added** (detected by file patterns)

**Garden Tending NOT Required If:**
- Small bug fixes (< 100 lines, < 5 files)
- Documentation-only changes
- Configuration updates

### The Workflow

```
Implementation Phase
       ↓
   [Changes Detected]
       ↓
   ┌─────────────┐
   │ Significant │ YES → Garden Tending Required
   │  Changes?   │           ↓
   └─────────────┘       Run Garden Tending
       │ NO                   ↓
       ↓                  Deployment
   Deployment Allowed
```

---

## Usage Examples

### Example 1: Normal Flow (Garden Tending Required)

You just implemented a large feature:

```bash
> Start Implementation: OAuth2 integration
[Implementation completes - 245 lines changed across 8 files]

> Start Deployment: v2.1.0
```

**System Response:**
```
════════════════════════════════════════════════════════════════════
ERROR: Garden Tending Required Before Deployment
════════════════════════════════════════════════════════════════════

Your changes require Garden Tending before deployment:

Current Metrics:
  - Lines changed: 245
  - Files changed: 8

Triggered Rules:
  ✗ 245 lines changed (threshold: 100)
  ✗ 8 files changed (threshold: 5)

Next Steps:

  1. Run Garden Tending to improve code quality:
     > Start Garden Tending: Post-OAuth2 implementation cleanup

  2. Then try deployment again:
     > Start Deployment: v2.1.0

OR if this is an emergency:

  Use the emergency bypass (requires justification):
  > Start Deployment: v2.1.0 --force-deploy --justification "Production incident affecting users, immediate hotfix required"

════════════════════════════════════════════════════════════════════
```

**Proper Resolution:**
```bash
# Run Garden Tending as recommended
> Start Garden Tending: Post-OAuth2 implementation cleanup
[Cultivator analyzes code, Pruner refactors, Gardener-Bridge validates]
✓ Garden Tending complete

# Now deployment proceeds normally
> Start Deployment: v2.1.0
✓ Deployment initiated
```

---

### Example 2: Small Changes (Garden Tending Not Required)

You fixed a small bug:

```bash
> Start Implementation: Fix login button color
[Implementation completes - 3 lines changed in 1 file]

> Start Deployment: v2.0.1
```

**System Response:**
```
✓ Workflow validation passed
✓ Changes are small (3 lines, 1 file)
✓ Garden Tending not required

Proceeding with deployment...
```

The system automatically allows deployment because changes are below the thresholds.

---

### Example 3: Emergency Deployment (Bypass)

Production is down and you need to deploy a critical hotfix immediately:

```bash
> Start Deployment: v2.0.2 --force-deploy --justification "Production database connection failing, users cannot login, hotfix critical"
```

**System Response:**
```
⚠️  WARNING: Emergency Bypass Activated

Justification: Production database connection failing, users cannot login, hotfix critical

✓ Bypass approved - proceeding with deployment
📝 Event logged to audit trail: .claude/workflow_audit.log

IMPORTANT: Schedule Garden Tending for next non-emergency deployment
```

**What Happens:**
- Deployment proceeds immediately
- Your justification is recorded in `.claude/workflow_audit.log`
- The bypass is timestamped and attributed to you (via git config)
- You can proceed with the emergency fix

---

## Understanding the Thresholds

### Lines of Code: 100

**Why 100 lines?**
Industry research (Google, GitHub) shows that code reviews become significantly less effective above 100 lines. Similarly, 100+ lines of new code typically introduces enough complexity to benefit from refactoring.

**What counts as a line:**
- Additions and deletions (from `git diff`)
- Code, comments, and blank lines
- Excludes: Auto-generated files, vendored dependencies

### Files Changed: 5

**Why 5 files?**
Changes touching 5+ files typically indicate:
- Feature work (multiple components modified)
- Architectural changes (cross-cutting concerns)
- Refactoring opportunities (patterns worth consolidating)

**What counts as a file:**
- Any file in `git diff --numstat`
- Code files, config files, tests
- Excludes: `.gitignore`, `package-lock.json`, `poetry.lock`

### New Features

**How detected:**
- New files in `src/`, `lib/`, `app/` directories
- New test files matching `test_*.py`, `*_test.py`, `*_spec.js`
- New components, modules, or packages

**Why it triggers Garden Tending:**
New features are the perfect time to:
- Ensure code quality from the start
- Document beneficial patterns
- Consolidate duplicate logic
- Update architecture docs

---

## Emergency Bypass System

### When to Use It

Use `--force-deploy` only for genuine emergencies:

**✅ Valid Use Cases:**
- Production outage affecting users
- Security vulnerability requiring immediate patch
- Critical bug causing data loss
- Regulatory compliance deadline (with approval)

**❌ Invalid Use Cases:**
- "Running late on sprint deadline"
- "Don't feel like running Garden Tending"
- "Want to deploy on Friday afternoon"
- "Tests are failing, will fix later"

### How to Use It

**Syntax:**
```bash
Start Deployment: <version> --force-deploy --justification "<reason>"
```

**Requirements:**
- Justification must be **at least 10 characters**
- No shell metacharacters (`$`, `;`, `|`, backticks, etc.)
- Clear explanation of why emergency bypass is needed

**Good Justifications:**
```bash
--justification "Production API failing for 30% of users, needs immediate rollback"

--justification "Security patch for CVE-2024-1234, actively being exploited"

--justification "Database migration stuck, blocking all deployments, approved by CTO"
```

**Bad Justifications:**
```bash
--justification "urgent"  # Too short (< 10 chars)

--justification "need to deploy before weekend"  # Not an emergency

--justification "bypass"  # Too vague
```

### Audit Trail

Every bypass is logged to `.claude/workflow_audit.log`:

```json
{
  "timestamp": "2025-10-17T10:30:45Z",
  "event": "emergency_bypass",
  "user": "jane.doe@company.com",
  "justification": "Production API failing for 30% of users, needs immediate rollback",
  "metadata": {
    "version": "v2.0.2",
    "loc_changed": 245,
    "files_changed": 8
  }
}
```

**Purpose:**
- Compliance and accountability
- Review patterns of bypasses
- Identify process improvement opportunities
- Demonstrate due diligence during audits

---

## Troubleshooting

### "Garden Tending required" but I just ran it

**Problem:** You ran Garden Tending, but deployment still blocks.

**Cause:** The workflow state file (`.claude/workflow_state.json`) might not have recorded the completion.

**Solution:**
```bash
# Check workflow state
cat .claude/workflow_state.json

# Should show:
{
  "completed_triads": ["implementation", "garden-tending"],
  "current_phase": "deployment",
  ...
}

# If "garden-tending" is missing, the Garden Tending didn't complete successfully
# Re-run Garden Tending and ensure it completes without errors
```

---

### "Invalid justification" error

**Problem:** Bypass fails with "Invalid justification" error.

**Common Causes:**

1. **Too short:**
   ```bash
   --justification "urgent"  # Only 6 chars, need 10+
   ```
   **Fix:** Provide detailed explanation (minimum 10 characters)

2. **Shell metacharacters:**
   ```bash
   --justification "Production down; need deploy"  # Contains ';'
   ```
   **Fix:** Remove dangerous characters: `$`, `;`, `|`, backticks, `&`

3. **Command patterns:**
   ```bash
   --justification "rm -rf old code, deploying new"  # Contains 'rm -rf'
   ```
   **Fix:** Avoid command-like patterns

**Correct Approach:**
```bash
--justification "Production database connection pool exhausted, users unable to access application, fix tested in staging"
```

---

### Metrics seem wrong

**Problem:** System says "245 lines changed" but you only modified 10 lines.

**Cause:** Metrics are calculated from `git diff` against the previous commit or branch.

**Check What's Being Measured:**
```bash
# See what git diff detects
git diff --numstat HEAD~1

# Output shows:
# 10      5       src/auth.py          # 10 additions, 5 deletions = 15 lines
# 150     80      package-lock.json    # 230 lines
# ...

# Total: 245 lines across all files
```

**Solutions:**

1. **Exclude auto-generated files** (add to `.gitignore`):
   ```
   package-lock.json
   poetry.lock
   *.pyc
   ```

2. **Commit in smaller chunks:**
   ```bash
   # Instead of one big commit:
   git add src/auth.py src/login.py
   git commit -m "feat: Add OAuth2 authentication"

   # Then separate commit for dependencies:
   git add package-lock.json
   git commit -m "chore: Update dependencies"
   ```

3. **Use bypass if metrics misleading:**
   ```bash
   Start Deployment: v2.0.1 --force-deploy --justification "Metrics inflated by auto-generated package-lock.json (actual code change: 10 lines), Garden Tending not needed"
   ```

---

### Want to disable workflow enforcement

**For Testing/Development:**

**Option 1: Skip Garden Tending flag (coming in future version)**
```bash
Start Deployment: v2.0.1 --skip-garden-tending
```

**Option 2: Emergency bypass (current version)**
```bash
Start Deployment: v2.0.1 --force-deploy --justification "Development environment testing, bypassing workflow enforcement"
```

**For Production:**

Workflow enforcement is a quality gate. If you're consistently bypassing it, consider:

1. **Adjust thresholds** (future version will support configuration)
2. **Split work into smaller chunks** (each under 100 lines / 5 files)
3. **Schedule Garden Tending separately** (run before changes accumulate)

**Note:** Disabling workflow enforcement permanently is not recommended, as it defeats the purpose of maintaining code quality.

---

## Configuration (Future Version)

**Coming in v0.8.0:**

Custom thresholds via `.claude/workflow_config.json`:

```json
{
  "enforcement": {
    "loc_threshold": 150,          // Default: 100
    "files_threshold": 8,           // Default: 5
    "require_for_features": true    // Default: true
  }
}
```

**Current Version (v0.7.0):**
Thresholds are fixed at 100 lines / 5 files. Use emergency bypass if needed.

---

## Best Practices

### 1. Embrace Garden Tending

**Don't think of it as a blocker—think of it as a quality assistant:**

Garden Tending catches issues before they reach production:
- Duplicate code → Consolidated utilities
- Complex functions → Refactored for clarity
- Missing tests → Comprehensive coverage
- Security gaps → Hardened validation

**Time investment:** 15-30 minutes
**Time saved:** Hours of debugging, tech debt paydown

---

### 2. Commit Frequently

**Small, focused commits avoid triggering enforcement unnecessarily:**

**Instead of:**
```bash
# One massive commit
git add .
git commit -m "Implement entire OAuth2 system"
# 850 lines changed → Garden Tending required
```

**Do this:**
```bash
# Multiple focused commits
git commit -m "Add OAuth2 config schema"        # 45 lines
git commit -m "Implement token generation"      # 80 lines
git commit -m "Add OAuth2 login endpoint"       # 95 lines
git commit -m "Add integration tests"           # 120 lines

# Each deployment checks only the latest changes
# Small changes skip Garden Tending automatically
```

---

### 3. Schedule Garden Tending Proactively

**Run Garden Tending before it's required:**

```bash
# After completing a feature sprint
> Start Garden Tending: Weekly codebase maintenance

# After refactoring
> Start Garden Tending: Consolidate auth utilities

# Before major releases
> Start Garden Tending: Pre-v2.0 quality review
```

**Benefits:**
- Never blocked by workflow enforcement
- Catch issues early (cheaper to fix)
- Maintain high code quality continuously

---

### 4. Write Detailed Justifications

**If you must use bypass, explain clearly:**

**Bad:**
```bash
--justification "emergency deployment needed"
```

**Good:**
```bash
--justification "Production payment processor failing due to API timeout (new in v2.0.5), affecting checkout for all users. Fix tested in staging, reverts timeout from 30s to 60s. Approved by VP Engineering."
```

**Why it matters:**
- Future you (or teammates) can understand the decision
- Auditors can verify proper process
- Patterns of bypasses highlight process improvements needed

---

### 5. Review Audit Logs Regularly

**Check for bypass patterns:**

```bash
# View recent bypasses
cat .claude/workflow_audit.log | tail -20

# Count bypasses per user
cat .claude/workflow_audit.log | grep emergency_bypass | jq .user | sort | uniq -c

# Review justifications
cat .claude/workflow_audit.log | jq .justification
```

**Questions to ask:**
- Are bypasses truly emergencies?
- Is one team member bypassing frequently? (May need training)
- Are thresholds too strict? (Many false positives)
- Are thresholds too loose? (Never triggered)

---

## FAQ

### Why is Garden Tending enforced?

**Short answer:** Technical debt compounds exponentially. Small maintenance windows prevent large refactoring projects.

**Long answer:**

Code quality degrades naturally over time:
- Duplicate patterns emerge (copy-paste)
- Complexity increases (features bolted on)
- Tests lag behind (coverage drops)
- Documentation drifts (stale comments)

Garden Tending after significant changes prevents this drift. 15 minutes of maintenance today avoids 15 hours of refactoring tomorrow.

**Industry evidence:**
- Google enforces 100-line code review limits (same threshold)
- Microsoft found 80% of production bugs introduced in complex changes (>100 lines)
- Martin Fowler: "Refactoring should be continuous, not periodic"

---

### Can I customize the thresholds?

**Current version (v0.7.0):** No, thresholds are fixed at 100 lines / 5 files.

**Future version (v0.8.0):** Yes, via `.claude/workflow_config.json`.

**Workaround for now:**
If thresholds don't fit your workflow, use emergency bypass with clear justification:

```bash
--justification "Project uses micro-services pattern, changes always touch 6+ files for consistency, bypassing file count threshold"
```

Then open an issue requesting configurable thresholds with your use case.

---

### What if git isn't available?

**Scenario:** Running in environment without git (Docker container, CI/CD)

**Behavior:** Workflow enforcement gracefully degrades:
- Metrics default to 0 lines, 0 files
- Garden Tending is NOT required (safe default)
- Deployment proceeds normally

**Warning message:**
```
⚠️  Git not available - cannot calculate change metrics
✓  Defaulting to Garden Tending NOT required
```

**Recommendation:** Ensure git is available in deployment environments for proper enforcement.

---

### Does this work with monorepos?

**Yes, but thresholds may need adjustment in future versions.**

**Current behavior:**
- Metrics calculated from entire repository `git diff`
- Changing 10 files across 10 micro-services = 10 files (triggers enforcement)

**Future improvement (v0.8.0+):**
- Path-based thresholds (different rules for different subdirectories)
- Service-level metrics (only count changes in current service)

**Workaround:**
Use bypass with clear justification for cross-service changes:

```bash
--justification "Monorepo pattern, updating shared auth library across 8 services, actual code change per service is minimal"
```

---

## Technical Details

### State File Location

**Workflow state:** `.claude/workflow_state.json`

**Contains:**
```json
{
  "session_id": "abc123",
  "completed_triads": ["idea-validation", "design", "implementation", "garden-tending"],
  "current_phase": "deployment",
  "last_transition": "2025-10-17T10:30:00Z",
  "metadata": {
    "trigger": "user_command",
    "metrics": {
      "loc_changed": 245,
      "files_changed": 8,
      "has_new_features": true
    }
  }
}
```

**Safe to delete:** File regenerates automatically. Delete if corrupted.

---

### Audit Log Location

**Audit trail:** `.claude/workflow_audit.log`

**Format:** JSON Lines (one JSON object per line)

**Example:**
```json
{"timestamp": "2025-10-17T10:30:45Z", "event": "emergency_bypass", "user": "jane@example.com", "justification": "Production incident", "metadata": {"version": "v2.0.1"}}
{"timestamp": "2025-10-17T11:15:22Z", "event": "emergency_bypass", "user": "john@example.com", "justification": "Security patch CVE-2024-1234", "metadata": {"version": "v2.0.2"}}
```

**Safe to archive:** Old entries can be moved to backup. Log is append-only.

---

### Security Measures

**Input validation:**
- Justifications sanitized to prevent shell injection
- Dangerous characters blocked: `$`, `;`, `|`, backticks, `&`, `>`, `<`
- Command patterns rejected: `rm -rf`, `sudo`, etc.

**File operations:**
- Atomic writes prevent corruption (write-to-temp-then-rename)
- File locking prevents race conditions (concurrent deployments)
- Append-only audit log prevents tampering

**Audit trail:**
- Every bypass logged with timestamp, user, justification
- User detected from git config (`git config user.email`)
- Metadata includes version, metrics, session ID

---

## Support

### Getting Help

**Check documentation first:**
- [Usage Guide](USAGE.md) - General workflow system usage
- [Troubleshooting](TROUBLESHOOTING.md) - Common issues
- [FAQ](FAQ.md) - Frequently asked questions

**Still stuck?**
- Open an issue: [GitHub Issues](https://github.com/reliable-agents-ai/triads/issues)
- Include: error message, `.claude/workflow_state.json`, recent commands

**Feature requests:**
- Configurable thresholds
- Path-based rules (monorepo support)
- Slack/email notifications for bypasses

Open an issue with your use case!

---

## Changelog

### v0.7.0 (Current)
- Initial release of Workflow Enforcement
- Fixed thresholds: 100 lines / 5 files
- Emergency bypass with audit logging
- Automatic change detection via git diff

### Future (v0.8.0+)
- Configurable thresholds via `.claude/workflow_config.json`
- Path-based rules for monorepos
- `--skip-garden-tending` flag for development
- Bypass notifications (Slack/email)

---

**Happy coding! Let the system guide you toward better code quality.** 🌱
