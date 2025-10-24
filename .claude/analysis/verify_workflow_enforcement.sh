#!/bin/bash
# Workflow Enforcement Import Verification Script
# Purpose: Check if refactored files have external imports before deletion
# Date: 2025-10-23

set -e

REPO_ROOT="/Users/iainnb/Documents/repos/triads"
cd "$REPO_ROOT"

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

    # Search for imports specifically from workflow_enforcement module
    IMPORTS=$(grep -r --include="*.py" "from triads.workflow_enforcement.$file\|from triads.workflow_enforcement import.*$file" src/ hooks/ 2>/dev/null | \
              grep -v "^src/triads/workflow_enforcement" | \
              grep -v "^src/triads/tools/workflow" || true)

    if [ -n "$IMPORTS" ]; then
        echo "❌ FOUND IMPORTS:"
        echo "$IMPORTS"
        echo ""
        ALL_CLEAR=false
    else
        echo "✅ No external imports"
    fi
    echo ""
done

echo ""
echo "========================================="
if [ "$ALL_CLEAR" = true ]; then
    echo "✅ ALL CLEAR - Safe to delete"
    echo "========================================="
    echo ""
    echo "Next steps:"
    echo "1. Run: bash .claude/analysis/delete_workflow_enforcement.sh"
    echo "2. Verify tests pass"
    echo "3. Review commit"
    exit 0
else
    echo "❌ IMPORTS FOUND - Do NOT delete yet"
    echo "========================================="
    echo ""
    echo "Action required:"
    echo "1. Review imports above"
    echo "2. Migrate to tools/workflow"
    echo "3. Re-run this script"
    exit 1
fi
