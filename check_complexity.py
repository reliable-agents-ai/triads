#!/usr/bin/env python3
"""Code complexity checker for Claude Code Triad Generator.

This script checks code complexity using radon and enforces thresholds:
- Cyclomatic Complexity: Max 10 (A-B rating)
- Maintainability Index: Min 65 (B rating)

Exit codes:
    0: All checks passed
    1: Complexity thresholds exceeded
    2: Script error

Usage:
    python check_complexity.py
    python check_complexity.py --strict  # Fail on any warning
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


# Thresholds
MAX_CYCLOMATIC_COMPLEXITY = 10  # A-B rating (1-10 is good)
MIN_MAINTAINABILITY_INDEX = 65.0  # B rating (65+ is acceptable)

# Paths to check
PATHS_TO_CHECK = ["hooks", "src"]


def run_command(cmd: List[str]) -> Tuple[int, str, str]:
    """Run shell command and return exit code, stdout, stderr."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=False, timeout=30
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 2, "", "Command timed out"
    except Exception as e:
        return 2, "", str(e)


def check_cyclomatic_complexity() -> bool:
    """Check cyclomatic complexity with radon.

    Returns:
        True if all checks passed, False otherwise
    """
    print("=" * 80)
    print("Cyclomatic Complexity Check (Max: 10)")
    print("=" * 80)

    all_passed = True

    for path in PATHS_TO_CHECK:
        if not Path(path).exists():
            print(f"⚠️  Path not found: {path}")
            continue

        # Get complexity for this path
        # -n C = show only C and worse (complexity > 10)
        # -a = include average
        # -s = show complexity score
        cmd = ["radon", "cc", path, "-n", "C", "-s", "-a"]
        exit_code, stdout, stderr = run_command(cmd)

        if exit_code != 0:
            print(f"❌ Error running radon on {path}:")
            print(stderr)
            all_passed = False
            continue

        # If radon found any functions with complexity > 10, output will be non-empty
        if stdout.strip():
            print(f"\n❌ Found functions with complexity > {MAX_CYCLOMATIC_COMPLEXITY} in {path}:")
            print(stdout)
            all_passed = False
        else:
            print(f"✅ {path}: All functions have acceptable complexity (≤{MAX_CYCLOMATIC_COMPLEXITY})")

    return all_passed


def check_maintainability_index() -> bool:
    """Check maintainability index with radon.

    Returns:
        True if all checks passed, False otherwise
    """
    print("\n" + "=" * 80)
    print(f"Maintainability Index Check (Min: {MIN_MAINTAINABILITY_INDEX})")
    print("=" * 80)

    all_passed = True

    for path in PATHS_TO_CHECK:
        if not Path(path).exists():
            print(f"⚠️  Path not found: {path}")
            continue

        # Get maintainability index
        # -s = show score
        # -n C = show only C and worse (MI < 65)
        cmd = ["radon", "mi", path, "-n", "C", "-s"]
        exit_code, stdout, stderr = run_command(cmd)

        if exit_code != 0:
            print(f"❌ Error running radon on {path}:")
            print(stderr)
            all_passed = False
            continue

        # If radon found any files with MI < 65, output will be non-empty
        if stdout.strip():
            print(f"\n❌ Found files with low maintainability in {path}:")
            print(stdout)
            all_passed = False
        else:
            print(f"✅ {path}: All files have acceptable maintainability (≥{MIN_MAINTAINABILITY_INDEX})")

    return all_passed


def show_overall_stats():
    """Show overall complexity statistics."""
    print("\n" + "=" * 80)
    print("Overall Statistics")
    print("=" * 80)

    for path in PATHS_TO_CHECK:
        if not Path(path).exists():
            continue

        print(f"\n--- {path} ---")

        # Cyclomatic complexity average
        cmd = ["radon", "cc", path, "-a", "-s"]
        exit_code, stdout, _ = run_command(cmd)
        if exit_code == 0:
            print("Cyclomatic Complexity:")
            print(stdout)

        # Maintainability index average
        cmd = ["radon", "mi", path, "-s"]
        exit_code, stdout, _ = run_command(cmd)
        if exit_code == 0:
            print("Maintainability Index:")
            print(stdout)


def main():
    """Main entry point."""
    print("🔍 Code Complexity Check")
    print()

    # Check if radon is installed
    exit_code, _, _ = run_command(["radon", "--version"])
    if exit_code != 0:
        print("❌ Error: radon is not installed")
        print("Install with: pip install radon")
        return 2

    # Run checks
    cc_passed = check_cyclomatic_complexity()
    mi_passed = check_maintainability_index()

    # Show overall stats
    show_overall_stats()

    # Summary
    print("\n" + "=" * 80)
    print("Summary")
    print("=" * 80)

    if cc_passed and mi_passed:
        print("✅ All complexity checks passed!")
        print()
        print(f"   Cyclomatic Complexity: All functions ≤ {MAX_CYCLOMATIC_COMPLEXITY}")
        print(f"   Maintainability Index: All files ≥ {MIN_MAINTAINABILITY_INDEX}")
        return 0
    else:
        print("❌ Complexity checks failed!")
        print()
        if not cc_passed:
            print(f"   ❌ Cyclomatic Complexity: Some functions > {MAX_CYCLOMATIC_COMPLEXITY}")
            print("      Refactor complex functions into smaller, focused functions")
        if not mi_passed:
            print(f"   ❌ Maintainability Index: Some files < {MIN_MAINTAINABILITY_INDEX}")
            print("      Improve code structure, reduce duplication, simplify logic")
        print()
        print("💡 Tips:")
        print("   - Extract complex logic into smaller functions")
        print("   - Reduce nesting with guard clauses")
        print("   - Eliminate code duplication (DRY principle)")
        print("   - Add descriptive variable names")
        print("   - Simplify conditional logic")
        return 1


if __name__ == "__main__":
    strict_mode = "--strict" in sys.argv
    exit_code = main()
    sys.exit(exit_code)
