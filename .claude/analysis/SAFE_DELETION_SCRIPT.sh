#!/bin/bash
# Safe Deletion Script - Phase 9 Cleanup
# Date: 2025-10-23
# Analyst: senior-developer
#
# This script deletes ONLY modules confirmed safe through deep analysis
# See: module_deletion_analysis.md for full details

set -e  # Exit on any error

REPO_ROOT="/Users/iainnb/Documents/repos/triads"
cd "$REPO_ROOT"

echo "========================================="
echo "Phase 9 DDD Refactoring - Safe Deletions"
echo "========================================="
echo ""

# ============================================================================
# STEP 1: IMMEDIATE SAFE DELETION - generator/ (empty module)
# ============================================================================

echo "STEP 1: Delete empty generator/ module"
echo "--------------------------------------"

# Safety check: Verify no imports
echo "Safety check: Verifying no external imports..."
GENERATOR_IMPORTS=$(grep -r "from triads.generator" src/ hooks/ 2>/dev/null | grep -v "^src/triads/generator" || true)

if [ -n "$GENERATOR_IMPORTS" ]; then
    echo "❌ ERROR: Found imports from triads.generator:"
    echo "$GENERATOR_IMPORTS"
    echo "Aborting deletion."
    exit 1
else
    echo "✅ No external imports found"
fi

# Verify module is empty
GENERATOR_LOC=$(find src/triads/generator/ -name "*.py" -type f -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}' || echo "0")
echo "Generator module size: $GENERATOR_LOC lines"

if [ "$GENERATOR_LOC" -gt 10 ]; then
    echo "❌ ERROR: Generator module is not empty ($GENERATOR_LOC lines)"
    echo "Review module_deletion_analysis.md - may need manual inspection"
    exit 1
else
    echo "✅ Module is effectively empty (< 10 lines)"
fi

# Baseline test run
echo "Running baseline tests..."
if ! pytest tests/ -v --tb=short -x > /tmp/triads_test_baseline.log 2>&1; then
    echo "❌ ERROR: Tests failing BEFORE deletion. Fix tests first."
    echo "See: /tmp/triads_test_baseline.log"
    exit 1
else
    BASELINE_COUNT=$(grep -c "passed" /tmp/triads_test_baseline.log || echo "unknown")
    echo "✅ Baseline tests pass ($BASELINE_COUNT)"
fi

# Delete generator/
echo "Deleting src/triads/generator/..."
rm -rf src/triads/generator/

# Verify deletion
if [ -d "src/triads/generator/" ]; then
    echo "❌ ERROR: Directory still exists after deletion"
    exit 1
else
    echo "✅ src/triads/generator/ deleted"
fi

# Check if test_generator exists and is empty
if [ -d "tests/test_generator/" ]; then
    TEST_GEN_FILES=$(find tests/test_generator/ -name "*.py" -type f | wc -l)
    if [ "$TEST_GEN_FILES" -eq 0 ]; then
        echo "tests/test_generator/ exists but is empty, deleting..."
        rm -rf tests/test_generator/
        echo "✅ tests/test_generator/ deleted"
    else
        echo "⚠️  WARNING: tests/test_generator/ has $TEST_GEN_FILES files"
        echo "    Review manually before deleting"
    fi
fi

# Post-deletion test run
echo "Running post-deletion tests..."
if ! pytest tests/ -v --tb=short -x > /tmp/triads_test_after_generator.log 2>&1; then
    echo "❌ ERROR: Tests failing AFTER deletion"
    echo "See: /tmp/triads_test_after_generator.log"
    echo "Restore from git: git checkout src/triads/generator/"
    exit 1
else
    AFTER_COUNT=$(grep -c "passed" /tmp/triads_test_after_generator.log || echo "unknown")
    echo "✅ Post-deletion tests pass ($AFTER_COUNT)"
fi

# Git commit
echo "Creating git commit..."
git add -A
git commit -m "cleanup: Remove empty generator module

Module was empty (__init__.py with 0 bytes).
No external imports found.
Part of Phase 9 DDD refactoring cleanup.

Evidence:
- find src/triads/generator/ showed only empty __init__.py
- grep found no imports from module
- Baseline: $BASELINE_COUNT tests passing
- After deletion: $AFTER_COUNT tests passing

See: .claude/analysis/module_deletion_analysis.md

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

echo "✅ STEP 1 COMPLETE: generator/ deleted and committed"
echo ""

# ============================================================================
# SUMMARY
# ============================================================================

echo "========================================="
echo "Deletion Summary"
echo "========================================="
echo ""
echo "✅ Deleted: src/triads/generator/ (0 LOC)"
echo "✅ Tests: All passing ($AFTER_COUNT tests)"
echo "✅ Committed: Git history preserved"
echo ""
echo "Next steps (manual - requires verification):"
echo "1. Migrate km/graph_access imports (2 files)"
echo "2. Delete km/graph_access/ (907 LOC)"
echo "3. Verify workflow_enforcement file imports"
echo "4. Delete refactored workflow_enforcement files (2,051 LOC)"
echo ""
echo "See module_deletion_analysis.md for detailed plan."
echo ""
echo "========================================="
echo "Script complete!"
echo "========================================="
