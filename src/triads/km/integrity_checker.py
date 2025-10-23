"""Knowledge graph integrity checker and repair CLI.

DEPRECATED: Core functionality moved to triads.tools.integrity.checker
as part of the DDD architecture consolidation.

New locations:
- IntegrityChecker: triads.tools.integrity.checker.IntegrityChecker
- ValidationResult: triads.tools.integrity.checker.ValidationResult
- RepairResult: triads.tools.integrity.checker.RepairResult
- Summary: triads.tools.integrity.checker.Summary

This module maintains backward compatibility for the CLI interface:
- triads-km check [--triad NAME] [--fix] [--verbose]

Please update imports to:
    from triads.tools.integrity.checker import (
        IntegrityChecker,
        ValidationResult,
        RepairResult,
        Summary
    )

Exit Codes:
    0: All graphs valid
    1: Corruption detected (not fixed)
    2: Repair attempted but failed

Usage:
    # Check all graphs
    python -m triads.km.integrity_checker check

    # Check specific triad
    python -m triads.km.integrity_checker check --triad design

    # Auto-repair corrupted graphs
    python -m triads.km.integrity_checker check --fix

    # Verbose output
    python -m triads.km.integrity_checker check --verbose
"""

from __future__ import annotations

import argparse
import sys
import warnings
from pathlib import Path

# Import from new location
from triads.tools.integrity.checker import (
    IntegrityChecker,
    ValidationResult,
    RepairResult,
    Summary,
)

# Show deprecation warning
warnings.warn(
    "triads.km.integrity_checker is deprecated. "
    "Use triads.tools.integrity.checker instead. "
    "CLI functionality remains available for backward compatibility.",
    DeprecationWarning,
    stacklevel=2
)


# ============================================================================
# Exit Codes
# ============================================================================


class ExitCode:
    """CLI exit codes for CI/CD integration."""

    SUCCESS = 0  # All graphs valid
    CORRUPTION_DETECTED = 1  # Corruption found (not fixed)
    REPAIR_FAILED = 2  # Repair attempted but failed


# ============================================================================
# CLI Interface
# ============================================================================


def format_validation_output(
    results: list[ValidationResult],
    verbose: bool = False
) -> str:
    """Format validation results for CLI output.

    Args:
        results: List of ValidationResult objects
        verbose: Include detailed error information

    Returns:
        Formatted output string
    """
    lines = []

    # Summary
    checker = IntegrityChecker(graphs_dir=".")  # Dummy for summary
    summary = checker.get_summary(results)
    lines.append(f"\n{summary.valid}/{summary.total} graphs valid")

    if summary.invalid > 0:
        lines.append(f"{summary.invalid} corrupted ({summary.corruption_rate:.1%})")

    lines.append("")

    # Per-graph details
    for result in results:
        status = "✓" if result.valid else "✗"
        lines.append(f"{status} {result.triad}")

        if not result.valid and verbose:
            lines.append(f"  Error: {result.error}")
            if result.error_field:
                lines.append(f"  Field: {result.error_field}")
            if result.file_path:
                lines.append(f"  File: {result.file_path}")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point.

    Args:
        argv: Command-line arguments (defaults to sys.argv)

    Returns:
        Exit code (0=success, 1=corruption detected, 2=repair failed)
    """
    parser = argparse.ArgumentParser(
        prog="triads-km",
        description="Knowledge graph integrity checker and repair tool"
    )
    parser.add_argument(
        "command",
        choices=["check"],
        help="Command to execute"
    )
    parser.add_argument(
        "--triad",
        help="Check specific triad (default: all graphs)"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Auto-repair corrupted graphs"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed error information"
    )
    parser.add_argument(
        "--dir",
        default=".claude/graphs",
        help="Directory containing graph files (default: .claude/graphs)"
    )

    args = parser.parse_args(argv)

    # Initialize checker
    graphs_dir = Path(args.dir)
    checker = IntegrityChecker(graphs_dir=graphs_dir)

    # Check graphs
    if args.triad:
        results = [checker.check_graph(args.triad)]
    else:
        results = checker.check_all_graphs()

    # Auto-repair if requested
    if args.fix:
        for result in results:
            if not result.valid:
                repair_result = checker.repair_graph(result.triad)
                if repair_result.success:
                    print(f"✓ Repaired {result.triad}: {repair_result.actions_taken}")
                    # Update result to reflect repair
                    result.valid = True
                    result.error = None
                else:
                    print(f"✗ Failed to repair {result.triad}: {repair_result.message}")

        # Re-check if repairs were made
        if args.triad:
            results = [checker.check_graph(args.triad)]
        else:
            results = checker.check_all_graphs()

    # Display results
    output = format_validation_output(results, verbose=args.verbose)
    print(output)

    # Determine exit code
    summary = checker.get_summary(results)

    if summary.invalid == 0:
        return ExitCode.SUCCESS
    elif args.fix:
        # If --fix was used and there are still invalid graphs, repair failed
        return ExitCode.REPAIR_FAILED
    else:
        # Corruption detected but not fixed
        return ExitCode.CORRUPTION_DETECTED


if __name__ == "__main__":
    sys.exit(main())
