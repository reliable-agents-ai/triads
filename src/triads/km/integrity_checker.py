"""Knowledge graph integrity checker and repair CLI.

This module provides validation and auto-repair functionality for knowledge graphs,
with a command-line interface for CI/CD integration.

Features:
- Validate single or all graphs
- Auto-repair common issues (invalid edges, etc.)
- Backup before repair
- Detailed reporting with exit codes
- CLI interface: triads-km check [--triad NAME] [--fix] [--verbose]

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
import json
import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from triads.km.backup_manager import BackupManager
from triads.km.schema_validator import ValidationError, validate_graph

# Initialize module logger
logger = logging.getLogger(__name__)


# ============================================================================
# Exit Codes
# ============================================================================


class ExitCode:
    """CLI exit codes for CI/CD integration."""

    SUCCESS = 0  # All graphs valid
    CORRUPTION_DETECTED = 1  # Corruption found (not fixed)
    REPAIR_FAILED = 2  # Repair attempted but failed


# ============================================================================
# Result Data Classes
# ============================================================================


@dataclass
class ValidationResult:
    """Result of validating a single graph.

    Attributes:
        triad: Triad name
        valid: True if graph is valid
        error: Error message if invalid
        error_field: Field that caused error (e.g., "nodes[0].label")
        error_count: Number of errors found
        file_path: Path to graph file
    """

    triad: str
    valid: bool
    error: str | None = None
    error_field: str | None = None
    error_count: int = 0
    file_path: Path | None = None


@dataclass
class RepairResult:
    """Result of attempting to repair a graph.

    Attributes:
        triad: Triad name
        success: True if repair succeeded
        message: Human-readable message
        actions_taken: Description of repair actions
        backup_created: True if backup was created before repair
    """

    triad: str
    success: bool
    message: str
    actions_taken: str | None = None
    backup_created: bool = False


@dataclass
class Summary:
    """Summary statistics for multiple validation results.

    Attributes:
        total: Total number of graphs checked
        valid: Number of valid graphs
        invalid: Number of invalid graphs
        corruption_rate: Fraction of corrupted graphs (0.0-1.0)
    """

    total: int
    valid: int
    invalid: int
    corruption_rate: float


# ============================================================================
# IntegrityChecker: Validation and Repair
# ============================================================================


class IntegrityChecker:
    """Validate and repair knowledge graphs.

    Features:
        - Check single or all graphs for corruption
        - Auto-repair common issues (invalid edges)
        - Backup before repair
        - Detailed error reporting

    Example:
        checker = IntegrityChecker(graphs_dir=Path(".claude/graphs"))
        result = checker.check_graph("design")
        if not result.valid:
            repair_result = checker.repair_graph("design")
    """

    def __init__(self, graphs_dir: Path | str) -> None:
        """Initialize integrity checker.

        Args:
            graphs_dir: Directory containing graph files
        """
        self.graphs_dir = Path(graphs_dir)
        self.backup_manager = BackupManager(graphs_dir=self.graphs_dir)

    def _get_graph_file(self, triad: str) -> Path:
        """Get path to graph file for a triad.

        Args:
            triad: Triad name

        Returns:
            Path to graph file
        """
        return self.graphs_dir / f"{triad}_graph.json"

    def _load_graph(self, triad: str) -> dict[str, Any] | None:
        """Load graph data from file.

        Args:
            triad: Triad name

        Returns:
            Graph data, or None if file doesn't exist or is corrupted
        """
        graph_file = self._get_graph_file(triad)

        if not graph_file.exists():
            return None

        try:
            with open(graph_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError, IOError) as e:
            logger.error(
                f"Failed to load graph: {type(e).__name__}",
                extra={"triad": triad, "error": str(e)}
            )
            return None

    def _save_graph(self, triad: str, graph_data: dict[str, Any]) -> bool:
        """Save graph data to file.

        Args:
            triad: Triad name
            graph_data: Graph data to save

        Returns:
            True on success, False on failure
        """
        graph_file = self._get_graph_file(triad)

        try:
            with open(graph_file, "w", encoding="utf-8") as f:
                json.dump(graph_data, f, indent=2)
            return True
        except (OSError, IOError) as e:
            logger.error(
                f"Failed to save graph: {type(e).__name__}",
                extra={"triad": triad, "error": str(e)}
            )
            return False

    def check_graph(self, triad: str) -> ValidationResult:
        """Check a single graph for corruption.

        Args:
            triad: Triad name

        Returns:
            ValidationResult with detailed information
        """
        graph_file = self._get_graph_file(triad)

        # Check if file exists
        if not graph_file.exists():
            return ValidationResult(
                triad=triad,
                valid=False,
                error=f"Graph file not found: {graph_file}",
                error_count=1,
                file_path=graph_file
            )

        # Load graph data
        graph_data = self._load_graph(triad)
        if graph_data is None:
            return ValidationResult(
                triad=triad,
                valid=False,
                error="Failed to load graph (invalid JSON or I/O error)",
                error_count=1,
                file_path=graph_file
            )

        # Validate graph structure
        try:
            validate_graph(graph_data)
            return ValidationResult(
                triad=triad,
                valid=True,
                error=None,
                error_count=0,
                file_path=graph_file
            )
        except ValidationError as e:
            return ValidationResult(
                triad=triad,
                valid=False,
                error=e.message,
                error_field=e.field,
                error_count=1,
                file_path=graph_file
            )

    def check_all_graphs(self) -> list[ValidationResult]:
        """Check all graphs in the directory.

        Returns:
            List of ValidationResult for each graph found
        """
        results = []

        # Find all graph files
        graph_files = sorted(self.graphs_dir.glob("*_graph.json"))

        for graph_file in graph_files:
            # Extract triad name from filename (e.g., "design_graph.json" -> "design")
            triad = graph_file.stem.replace("_graph", "")
            result = self.check_graph(triad)
            results.append(result)

        return results

    def repair_graph(self, triad: str) -> RepairResult:
        """Attempt to repair a corrupted graph.

        Repairs:
            - Remove edges pointing to nonexistent nodes
            - (Future: Remove nodes with invalid types, fix confidence ranges, etc.)

        Cannot repair:
            - Missing required fields (id, label, type)
            - Invalid JSON structure

        Args:
            triad: Triad name

        Returns:
            RepairResult with success status and actions taken
        """
        graph_file = self._get_graph_file(triad)

        # Load graph
        graph_data = self._load_graph(triad)
        if graph_data is None:
            return RepairResult(
                triad=triad,
                success=False,
                message="Cannot repair: Failed to load graph (invalid JSON or I/O error)",
                backup_created=False
            )

        # Create backup before repair
        backup_path = self.backup_manager.create_backup(triad)
        backup_created = backup_path is not None

        if not backup_created:
            logger.warning(
                "Failed to create backup before repair (continuing anyway)",
                extra={"triad": triad}
            )

        # Attempt repairs
        actions = []
        repaired = False

        # Repair 1: Remove nodes with invalid confidence values
        if "nodes" in graph_data:
            original_node_count = len(graph_data["nodes"])
            valid_nodes = []

            for node in graph_data["nodes"]:
                if not isinstance(node, dict):
                    continue

                # Check if confidence is invalid (non-numeric)
                if "confidence" in node:
                    confidence = node["confidence"]
                    if not isinstance(confidence, (int, float)):
                        # Try to parse if it's a string number
                        if isinstance(confidence, str):
                            try:
                                # Try to convert simple numeric strings
                                float(confidence)
                                # If successful, skip this node (it's likely template data)
                                continue
                            except ValueError:
                                # String is not numeric (e.g., "{0.9-1.0}"), skip this node
                                continue
                        else:
                            # Non-numeric, non-string confidence - skip
                            continue
                    elif confidence < 0.0 or confidence > 1.0:
                        # Out of range - skip
                        continue

                valid_nodes.append(node)

            removed_node_count = original_node_count - len(valid_nodes)
            if removed_node_count > 0:
                graph_data["nodes"] = valid_nodes
                actions.append(f"Removed {removed_node_count} node{'s' if removed_node_count != 1 else ''} with invalid confidence")
                repaired = True

        # Repair 2: Remove invalid edges (edges pointing to nonexistent nodes)
        # Handle both 'edges' and 'links' keys (NetworkX uses 'links')
        edges_key = "edges" if "edges" in graph_data else "links" if "links" in graph_data else None
        if "nodes" in graph_data and edges_key:
            node_ids = {node["id"] for node in graph_data["nodes"] if isinstance(node, dict) and "id" in node}
            original_edge_count = len(graph_data[edges_key])

            valid_edges = []
            for edge in graph_data[edges_key]:
                if isinstance(edge, dict) and "source" in edge and "target" in edge:
                    if edge["source"] in node_ids and edge["target"] in node_ids:
                        valid_edges.append(edge)

            removed_count = original_edge_count - len(valid_edges)
            if removed_count > 0:
                graph_data[edges_key] = valid_edges
                actions.append(f"Removed {removed_count} invalid edge{'s' if removed_count != 1 else ''}")
                repaired = True

        # If no repairs were made, check if graph is actually invalid
        if not repaired:
            # Validate to see what's wrong
            try:
                validate_graph(graph_data)
                return RepairResult(
                    triad=triad,
                    success=True,
                    message="Graph is already valid (no repairs needed)",
                    backup_created=backup_created
                )
            except ValidationError as e:
                return RepairResult(
                    triad=triad,
                    success=False,
                    message=f"Cannot repair: {e.message} (no automatic fix available)",
                    backup_created=backup_created
                )

        # Save repaired graph
        if not self._save_graph(triad, graph_data):
            # Restore from backup
            if backup_created and backup_path:
                logger.warning(
                    "Failed to save repaired graph, attempting restore from backup",
                    extra={"triad": triad}
                )
                latest_backup = self.backup_manager.list_backups(triad)[0]
                self.backup_manager.restore_backup(triad, latest_backup)

            return RepairResult(
                triad=triad,
                success=False,
                message="Failed to save repaired graph",
                backup_created=backup_created
            )

        # Validate repaired graph
        try:
            validate_graph(graph_data)
            return RepairResult(
                triad=triad,
                success=True,
                message=f"Successfully repaired graph",
                actions_taken="; ".join(actions),
                backup_created=backup_created
            )
        except ValidationError as e:
            # Repair introduced new errors - rollback
            logger.error(
                "Repair introduced new validation errors, rolling back",
                extra={"triad": triad, "error": e.message}
            )

            if backup_created and backup_path:
                latest_backup = self.backup_manager.list_backups(triad)[0]
                self.backup_manager.restore_backup(triad, latest_backup)

            return RepairResult(
                triad=triad,
                success=False,
                message=f"Repair failed validation: {e.message} (rolled back)",
                backup_created=backup_created
            )

    def get_summary(self, results: list[ValidationResult]) -> Summary:
        """Generate summary statistics from validation results.

        Args:
            results: List of ValidationResult objects

        Returns:
            Summary with counts and corruption rate
        """
        total = len(results)
        valid = sum(1 for r in results if r.valid)
        invalid = total - valid
        corruption_rate = invalid / total if total > 0 else 0.0

        return Summary(
            total=total,
            valid=valid,
            invalid=invalid,
            corruption_rate=corruption_rate
        )


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
