# Lessons Learned: v0.9.0 Release

## Critical Finding: Emergency Bypass Left Enabled

**Date**: 2025-10-23
**Severity**: CRITICAL
**Status**: RESOLVED (documented for prevention)

### What Happened

During v0.9.0 deployment, we missed updating `.claude-plugin/plugin.json` version field despite having a CRITICAL checklist in the knowledge graph specifically designed to prevent this.

### Root Cause

`TRIADS_NO_BLOCK=1` environment variable was set earlier in the session for debugging corruption prevention issues but was **never unset** in the user's shell environment.

**Evidence**:
```bash
$ echo $TRIADS_NO_BLOCK
1

$ cat .claude/graphs/deployment_graph.json | jq '.nodes[] | select(.label == "Version Bump File Checklist") | {injection_count, last_injected_at}'
{
  "injection_count": 0,
  "last_injected_at": null
}
```

The checklist exists with confidence 1.0 and perfect trigger conditions, but was **never injected** because the emergency bypass flag disabled the entire PreToolUse hook.

### Impact

- Plugin version remained at 0.8.0-alpha.6 in initial v0.9.0 release
- Users running `/plugin` would not see the update
- Required manual fix and additional commit (6c70696)
- This is the **second occurrence** of this issue (also happened in v0.7.0-alpha.1)

### Why The Learning Didn't Stick

1. ✅ **Knowledge exists**: Deployment graph has CRITICAL checklist with confidence 1.0
2. ✅ **Hook configured**: Trigger conditions perfectly match the scenario
3. ❌ **Hook disabled**: `TRIADS_NO_BLOCK=1` globally disabled knowledge injection
4. ❌ **Flag forgotten**: No process to track/unset emergency bypass flags

### The Real Problem

**Emergency bypass flags are "fire and forget"** - we set them during debugging but have no systematic way to ensure they're unset afterward.

```
Debugging Session:
  Set TRIADS_NO_BLOCK=1 ✓
  Fix corruption issues ✓
  Unset TRIADS_NO_BLOCK=1 ✗ ← FORGOTTEN

Deployment Session (hours later):
  Hook disabled, checklist not injected ✗
  Plugin version missed again ✗
```

## Solutions Implemented

### Immediate (v0.9.0)

1. ✅ Updated plugin.json to 0.9.0 (commit 6c70696)
2. ✅ Unset TRIADS_NO_BLOCK in Claude Code subprocess
3. ✅ Documented this lesson learned

### Required (Next Session)

**User action required**:
```bash
# In your terminal (outside Claude Code):
unset TRIADS_NO_BLOCK

# Or remove from shell config if persisted:
# grep TRIADS_NO_BLOCK ~/.zshrc ~/.bashrc
```

## Recommended Process Changes

### 1. Emergency Bypass Hygiene Protocol

When setting emergency bypass flags:

1. **Document why** (write down the issue being debugged)
2. **Set expiry intent** ("only for this debugging session")
3. **Add to checklist** (if debugging spans multiple sessions)
4. **Verify unset** before moving to other work
5. **Confirm unset** before any deployment operations

### 2. Pre-Deployment Checklist Addition

Add to deployment checklist:
```markdown
- [ ] Verify no emergency bypass flags are set:
  - [ ] `echo $TRIADS_NO_BLOCK` → should be empty
  - [ ] `echo $TRIADS_NO_EXPERIENCE` → should be empty
```

### 3. Hook Warning Enhancement (Future)

Consider adding to `on_pre_experience_injection.py`:
```python
# If in deployment context and bypass flag is set, warn user
if is_deployment_operation() and os.getenv("TRIADS_NO_BLOCK"):
    print("⚠️  WARNING: TRIADS_NO_BLOCK is set, disabling critical checklists!", file=sys.stderr)
    print("⚠️  Unset with: unset TRIADS_NO_BLOCK", file=sys.stderr)
```

### 4. Auto-Expiry Consideration (Future)

Could implement time-based auto-expiry:
- `TRIADS_NO_BLOCK=1h` → expires after 1 hour
- Requires wrapper script or hook modification
- Prevents "forever bypass" scenarios

## Knowledge Graph Updates Needed

Add these nodes to capture this pattern:

1. **Finding**: "Emergency Bypass Left Enabled After Debugging"
   - Confidence: 1.0 (verified root cause)
   - Evidence: injection_count: 0 despite perfect trigger conditions
   - Related incidents: v0.7.0-alpha.1, v0.9.0

2. **Concept**: "Emergency Bypass Hygiene Protocol"
   - Confidence: 0.95 (recommended practice)
   - Best practice: Document, unset, verify before context switch
   - Priority: HIGH

## Success Metrics

**Metric**: This issue should not recur in v0.10.0 or later releases

**Verification**:
- Deployment graph checklist injection_count > 0 in next release
- Plugin version correctly updated on first attempt
- No emergency bypass flags present during deployment

## Related Documentation

- `docs/CORRUPTION_PREVENTION.md` - Why TRIADS_NO_BLOCK exists
- `.claude/graphs/deployment_graph.json` - Version bump checklist
- `hooks/on_pre_experience_injection.py` - Hook that was bypassed

---

**Author**: Claude Code Supervisor
**Date**: 2025-10-23
**Commit**: 6c70696 (fix), this doc (lessons learned)
