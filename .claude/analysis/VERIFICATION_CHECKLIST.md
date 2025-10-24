# Verification Checklist - Phase 9 Cleanup

**Purpose**: Systematic verification before deleting refactored modules
**Date**: 2025-10-23
**Analyst**: senior-developer

---

## Phase 1: IMMEDIATE (Safe Now) ✅

### ✅ src/triads/generator/

**Status**: Ready to delete
**Evidence**:
- Module empty (0 bytes __init__.py)
- No external imports
- Baseline tests: 177+ passing

**Action**: Run `SAFE_DELETION_SCRIPT.sh`

---

## Phase 2: DEFERRED (Requires Verification)

### 🔍 src/triads/km/graph_access/

**Status**: BLOCKED - Needs migration first
**Lines**: 907 LOC
**Risk**: LOW (after migration)

**Blockers**:
1. `src/triads/km/experience_query.py` imports `GraphLoader`
2. `src/triads/km/commands.py` imports `GraphLoader`

**Verification Steps**:

```bash
# Step 1: Check current imports
echo "=== Current imports from graph_access ==="
grep -n "from triads.km.graph_access" src/triads/km/experience_query.py
grep -n "from triads.km.graph_access" src/triads/km/commands.py

# Step 2: Verify tools/knowledge has equivalent
echo "=== Checking tools/knowledge equivalent ==="
grep -r "class.*Repository" src/triads/tools/knowledge/repository.py | head -5
grep -r "def load_graph" src/triads/tools/knowledge/repository.py | head -5

# Step 3: Check test coverage
echo "=== Test coverage for graph_access ==="
find tests/ -name "*graph_access*" -o -name "*knowledge*" | head -10

# Step 4: Verify no other imports
echo "=== All imports from graph_access ==="
grep -r "from triads.km.graph_access" src/ hooks/ | grep -v "^src/triads/km/graph_access"
```

**Expected Results**:
- Only 2 files import from graph_access ✅ (confirmed)
- tools/knowledge has FileSystemKnowledgeRepository ✅ (confirmed)
- Migration path is clear

**Migration Task**:

**File 1**: `src/triads/km/experience_query.py`
```python
# OLD:
from triads.km.graph_access import GraphLoader

# NEW:
from triads.tools.knowledge.repository import FileSystemKnowledgeRepository

# Update usage:
# OLD: loader = GraphLoader()
# NEW: repo = FileSystemKnowledgeRepository()
```

**File 2**: `src/triads/km/commands.py`
```python
# OLD:
from triads.km.graph_access import GraphLoader

# NEW:
from triads.tools.knowledge.repository import FileSystemKnowledgeRepository

# Update usage:
# OLD: loader = GraphLoader()
# NEW: repo = FileSystemKnowledgeRepository()
```

**Post-Migration Verification**:
```bash
# Verify no remaining imports
grep -r "from triads.km.graph_access" src/ hooks/ | grep -v "^src/triads/km/graph_access"
# Expected: No results

# Run tests
pytest tests/ -v --tb=short

# Delete if all clear
rm -rf src/triads/km/graph_access/

# Commit
git add -A
git commit -m "cleanup: Remove km/graph_access (migrated to tools/knowledge)"
```

---

### 🔍 src/triads/workflow_enforcement/ (Refactored Files)

**Status**: Needs import verification
**Lines**: ~2,051 LOC deletable
**Risk**: LOW (shim provides fallback)

**Files to Verify**:

#### 1. validator_new.py (374 LOC)

```bash
# Check imports
grep -r "from triads.workflow_enforcement.validator_new\|import.*validator_new" src/ hooks/ tests/ | grep -v "^src/triads/workflow_enforcement" | grep -v "^tests/workflow_enforcement"

# Expected: No results (or only test imports)
# Refactored to: tools/workflow/validation.py
```

**Status**: [ ] VERIFIED [ ] SAFE TO DELETE

---

#### 2. enforcement_new.py (394 LOC)

```bash
# Check imports
grep -r "from triads.workflow_enforcement.enforcement_new\|import.*enforcement_new" src/ hooks/ tests/ | grep -v "^src/triads/workflow_enforcement" | grep -v "^tests/workflow_enforcement"

# Expected: No results
# Refactored to: tools/workflow/enforcement.py
```

**Status**: [ ] VERIFIED [ ] SAFE TO DELETE

---

#### 3. schema_loader.py (454 LOC)

```bash
# Check imports
grep -r "from triads.workflow_enforcement.schema_loader\|import.*WorkflowSchemaLoader" src/ hooks/ tests/ | grep -v "^src/triads/workflow_enforcement" | grep -v "^tests/workflow_enforcement"

# Expected: No results
# Refactored to: tools/workflow/schema.py
```

**Status**: [ ] VERIFIED [ ] SAFE TO DELETE

---

#### 4. triad_discovery.py (192 LOC)

```bash
# Check imports
grep -r "from triads.workflow_enforcement.triad_discovery\|import.*TriadDiscovery" src/ hooks/ tests/ | grep -v "^src/triads/workflow_enforcement" | grep -v "^tests/workflow_enforcement"

# Expected: No results
# Refactored to: tools/workflow/discovery.py
```

**Status**: [ ] VERIFIED [ ] SAFE TO DELETE

---

#### 5. audit.py (144 LOC)

```bash
# Check imports
grep -r "from triads.workflow_enforcement.audit\|import.*AuditLogger" src/ hooks/ tests/ | grep -v "^src/triads/workflow_enforcement" | grep -v "^tests/workflow_enforcement"

# Expected: No results
# Refactored to: tools/workflow/audit.py
```

**Status**: [ ] VERIFIED [ ] SAFE TO DELETE

---

#### 6. bypass.py (259 LOC)

```bash
# Check imports
grep -r "from triads.workflow_enforcement.bypass\|import.*EmergencyBypass" src/ hooks/ tests/ | grep -v "^src/triads/workflow_enforcement" | grep -v "^tests/workflow_enforcement"

# Expected: No results
# Refactored to: tools/workflow/bypass.py
```

**Status**: [ ] VERIFIED [ ] SAFE TO DELETE

---

#### 7. git_utils.py (234 LOC)

```bash
# Check imports
grep -r "from triads.workflow_enforcement.git_utils\|import.*GitRunner" src/ hooks/ tests/ | grep -v "^src/triads/workflow_enforcement" | grep -v "^tests/workflow_enforcement"

# Expected: No results
# Refactored to: tools/workflow/git_utils.py
```

**Status**: [ ] VERIFIED [ ] SAFE TO DELETE

---

#### 8. metrics/ directory (~2,500 LOC)

```bash
# Check imports
grep -r "from triads.workflow_enforcement.metrics" src/ hooks/ tests/ | grep -v "^src/triads/workflow_enforcement" | grep -v "^tests/workflow_enforcement"

# Expected: No results
# Refactored to: tools/workflow/metrics/
```

**Status**: [ ] VERIFIED [ ] SAFE TO DELETE

---

### Verification Script

```bash
#!/bin/bash
# Run all verifications at once

echo "========================================="
echo "Workflow Enforcement Import Verification"
echo "========================================="
echo ""

FILES=(
    "validator_new"
    "enforcement_new"
    "schema_loader"
    "triad_discovery"
    "audit"
    "bypass"
    "git_utils"
    "metrics"
)

ALL_CLEAR=true

for file in "${FILES[@]}"; do
    echo "Checking: $file"
    IMPORTS=$(grep -r "from triads.workflow_enforcement.$file\|import.*$file" /Users/iainnb/Documents/repos/triads/src/ /Users/iainnb/Documents/repos/triads/hooks/ 2>/dev/null | grep -v "^/Users/iainnb/Documents/repos/triads/src/triads/workflow_enforcement" || true)

    if [ -n "$IMPORTS" ]; then
        echo "❌ FOUND IMPORTS:"
        echo "$IMPORTS"
        ALL_CLEAR=false
    else
        echo "✅ No external imports"
    fi
    echo ""
done

if [ "$ALL_CLEAR" = true ]; then
    echo "========================================="
    echo "✅ ALL CLEAR - Safe to delete"
    echo "========================================="
    exit 0
else
    echo "========================================="
    echo "❌ IMPORTS FOUND - Do NOT delete yet"
    echo "========================================="
    exit 1
fi
```

**Save as**: `.claude/analysis/verify_workflow_enforcement.sh`

---

### Deletion Script (After Verification)

```bash
#!/bin/bash
# Delete refactored workflow_enforcement files
# ONLY run after verification script passes

set -e

REPO_ROOT="/Users/iainnb/Documents/repos/triads"
cd "$REPO_ROOT"

echo "Deleting refactored workflow_enforcement files..."

# Baseline test
echo "Running baseline tests..."
pytest tests/ -v --tb=short -x > /tmp/before_wf_deletion.log 2>&1
BASELINE=$(grep -c "passed" /tmp/before_wf_deletion.log || echo "unknown")
echo "Baseline: $BASELINE tests passing"

# Delete files
rm src/triads/workflow_enforcement/validator_new.py
rm src/triads/workflow_enforcement/enforcement_new.py
rm src/triads/workflow_enforcement/schema_loader.py
rm src/triads/workflow_enforcement/triad_discovery.py
rm src/triads/workflow_enforcement/audit.py
rm src/triads/workflow_enforcement/bypass.py
rm src/triads/workflow_enforcement/git_utils.py
rm -rf src/triads/workflow_enforcement/metrics/

echo "Files deleted. Running post-deletion tests..."

# Post-deletion test
pytest tests/ -v --tb=short -x > /tmp/after_wf_deletion.log 2>&1
AFTER=$(grep -c "passed" /tmp/after_wf_deletion.log || echo "unknown")
echo "After deletion: $AFTER tests passing"

# Compare
if [ "$BASELINE" != "$AFTER" ]; then
    echo "⚠️  WARNING: Test count changed ($BASELINE → $AFTER)"
    echo "Review logs:"
    echo "  Before: /tmp/before_wf_deletion.log"
    echo "  After:  /tmp/after_wf_deletion.log"
fi

# Commit
git add -A
git commit -m "cleanup: Remove refactored workflow_enforcement files

Files moved to tools/workflow/:
- validator_new.py → validation.py
- enforcement_new.py → enforcement.py
- schema_loader.py → schema.py
- triad_discovery.py → discovery.py
- audit.py → audit.py
- bypass.py → bypass.py
- git_utils.py → git_utils.py
- metrics/ → metrics/

Kept:
- instance_manager.py (active imports)
- state_manager.py (active)
- cli.py (verify usage)
- __init__.py (backward compatibility shim)

Baseline: $BASELINE tests
After: $AFTER tests

Part of Phase 9 DDD refactoring cleanup.
See: .claude/analysis/module_deletion_analysis.md

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

echo "✅ Deletion complete and committed"
```

**Save as**: `.claude/analysis/delete_workflow_enforcement.sh`

---

## Phase 3: FUTURE (v0.11.0+)

### ⏰ src/triads/workflow_matching/ (Shim)

**Status**: Keep for deprecation period
**Lines**: ~1,800 LOC
**Risk**: MEDIUM
**Planned**: Delete in v0.11.0

**Checklist for v0.11.0**:

- [ ] Deprecation warning issued for 1+ versions
- [ ] No external imports (verify with grep)
- [ ] Tests migrated to test_tools/test_router/
- [ ] Documentation updated
- [ ] Migration guide published

**Verification**:
```bash
# Check for stragglers
grep -r "from triads.workflow_matching" src/ hooks/ | grep -v "^src/triads/workflow_matching"

# Expected: No results

# Delete
rm -rf src/triads/workflow_matching/
rm -rf tests/workflow_matching/

# Commit
git add -A
git commit -m "cleanup: Remove workflow_matching shim (deprecated in v0.10.0)"
```

---

## Summary Checklist

### Immediate Actions ✅
- [x] Analysis complete
- [ ] Run SAFE_DELETION_SCRIPT.sh (deletes generator/)
- [ ] Verify tests pass

### Short-term Actions 🔍
- [ ] Migrate km/experience_query.py to use tools/knowledge
- [ ] Migrate km/commands.py to use tools/knowledge
- [ ] Delete km/graph_access/
- [ ] Run verify_workflow_enforcement.sh
- [ ] If clear, run delete_workflow_enforcement.sh
- [ ] Update documentation

### Medium-term Actions ⏰
- [ ] Wait for v0.11.0
- [ ] Delete workflow_matching/ shim
- [ ] Update migration guide

### Long-term Actions 📋
- [ ] Consider router convergence (old vs new)
- [ ] Evaluate km/ consolidation
- [ ] Migrate instance_manager if needed

---

## Success Metrics

**After all deletions**:
- Lines deleted: ~4,758 LOC
- Lines kept: ~9,657 LOC
- Tests passing: 1,553+ (baseline)
- Functionality preserved: 100%
- Reversibility: 100% (git history)

---

**Document status**: Ready for execution
**Last updated**: 2025-10-23
**Next review**: After each deletion phase
