"""
Formatters for integrity tool output.

Formats ValidationResult and RepairResult into human-readable text output.
"""

from typing import List

from .domain import RepairResult, ValidationResult


def format_validation_result(result: ValidationResult) -> str:
    """
    Format a single ValidationResult as human-readable text.

    Args:
        result: ValidationResult to format

    Returns:
        Formatted text output
    """
    lines = []

    # Header
    lines.append(f"Graph Validation: {result.triad}")
    lines.append("=" * 50)

    # Status
    if result.valid:
        lines.append("✓ Status: VALID")
        lines.append("\nThe graph passed all validation checks.")
    else:
        lines.append("✗ Status: INVALID")
        lines.append(f"\nError: {result.error}")

        if result.error_field:
            lines.append(f"Field: {result.error_field}")

        if result.error_count > 0:
            lines.append(f"Errors found: {result.error_count}")

    # File path
    if result.file_path:
        lines.append(f"\nFile: {result.file_path}")

    return "\n".join(lines)


def format_all_validation_results(results: List[ValidationResult]) -> str:
    """
    Format multiple ValidationResults as summary report.

    Args:
        results: List of ValidationResult objects

    Returns:
        Formatted summary report
    """
    lines = []

    # Header
    lines.append("Graph Validation Summary")
    lines.append("=" * 50)

    if not results:
        lines.append("\nNo graphs found.")
        return "\n".join(lines)

    # Calculate summary stats
    total = len(results)
    valid_count = sum(1 for r in results if r.valid)
    invalid_count = total - valid_count
    corruption_rate = invalid_count / total if total > 0 else 0.0

    # Summary
    lines.append(f"\nTotal graphs: {total}")
    lines.append(f"Valid: {valid_count}")
    lines.append(f"Invalid: {invalid_count}")

    if invalid_count > 0:
        lines.append(f"Corruption rate: {corruption_rate:.1%}")

    lines.append("\nDetails:")
    lines.append("-" * 50)

    # Per-graph details
    for result in results:
        status_icon = "✓" if result.valid else "✗"
        lines.append(f"{status_icon} {result.triad}")

        if not result.valid:
            lines.append(f"  Error: {result.error}")
            if result.error_field:
                lines.append(f"  Field: {result.error_field}")

    return "\n".join(lines)


def format_repair_result(result: RepairResult) -> str:
    """
    Format a RepairResult as human-readable text.

    Args:
        result: RepairResult to format

    Returns:
        Formatted text output
    """
    lines = []

    # Header
    lines.append(f"Graph Repair: {result.triad}")
    lines.append("=" * 50)

    # Status
    if result.success:
        lines.append("✓ Status: SUCCESS")
        lines.append(f"\n{result.message}")

        if result.actions_taken:
            lines.append(f"\nActions taken:")
            lines.append(f"  {result.actions_taken}")
    else:
        lines.append("✗ Status: FAILED")
        lines.append(f"\n{result.message}")

    # Backup info
    if result.backup_created:
        lines.append(f"\nBackup created: Yes")
        if result.backup_path:
            lines.append(f"Backup location: {result.backup_path}")
    else:
        lines.append(f"\nBackup created: No")

    return "\n".join(lines)
