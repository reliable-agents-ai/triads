"""Workflow validation logic and metrics calculation.

This module implements the enforcement rules that determine when
Garden Tending is required before deployment.

Per ADR-002: Enforcement rules are:
- >100 lines of code changed, OR
- >5 files changed, OR
- New features added

DEPRECATED: This module is deprecated in v0.7.0 and will be removed in v1.0.0.
Use validator_new.py instead. See docs/MIGRATION_v1.0.md for migration guide.
"""

from __future__ import annotations

import subprocess
import warnings
from typing import Any

# Issue deprecation warning when module is imported
warnings.warn(
    "validator.py is deprecated and will be removed in v1.0.0. "
    "Use validator_new.py instead. "
    "See migration guide: docs/MIGRATION_v1.0.md",
    DeprecationWarning,
    stacklevel=2
)


# Enforcement thresholds (per ADR-002)
LOC_THRESHOLD = 100
FILES_THRESHOLD = 5

# Valid workflow transitions
VALID_TRANSITIONS = {
    None: {"idea-validation"},  # Can start with idea-validation
    "idea-validation": {"design"},
    "design": {"implementation"},
    "implementation": {"garden-tending", "deployment"},  # Can skip GT in some cases
    "garden-tending": {"deployment"},
    "deployment": set(),  # End of workflow
}


class WorkflowValidator:
    """Validates workflow transitions and calculates metrics.

    Example:
        validator = WorkflowValidator()
        metrics = validator.calculate_metrics()
        if validator.requires_garden_tending(metrics):
            print("Garden Tending required!")
    """

    def calculate_metrics(self, base_ref: str = "HEAD~1") -> dict[str, Any]:
        """Calculate code change metrics from git diff.

        Counts lines of code and files changed since the base reference.

        Args:
            base_ref: Git reference to compare against (default: HEAD~1)

        Returns:
            Metrics dictionary with:
            {
                "loc_changed": int,
                "files_changed": int,
                "has_new_features": bool,
                "git_available": bool
            }

        Example:
            metrics = validator.calculate_metrics(base_ref="main")
            print(f"Changed {metrics['loc_changed']} lines")
        """
        metrics = {
            "loc_changed": 0,
            "files_changed": 0,
            "has_new_features": False,
            "git_available": False,
        }

        try:
            # Check if git is available
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode != 0:
                # Not a git repository
                return metrics

            metrics["git_available"] = True

            # Get diff stats
            result = subprocess.run(
                ["git", "diff", "--numstat", base_ref, "HEAD"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:
                return metrics

            # Parse numstat output (format: additions deletions filename)
            lines = result.stdout.strip().split("\n")
            files_changed = set()
            total_loc = 0

            for line in lines:
                if not line:
                    continue

                parts = line.split("\t")
                if len(parts) < 3:
                    continue

                additions = parts[0]
                deletions = parts[1]
                filename = parts[2]

                # Skip binary files (marked with "-")
                if additions == "-" or deletions == "-":
                    continue

                # Count net lines changed
                try:
                    added = int(additions)
                    deleted = int(deletions)
                    total_loc += added + deleted  # Count both additions and deletions
                except ValueError:
                    continue

                # Track unique files
                files_changed.add(filename)

                # Detect new features (heuristic: new files in src/ or features/)
                if filename.startswith(("src/", "features/", "lib/")):
                    # Check if file is newly added
                    check_result = subprocess.run(
                        ["git", "diff", "--name-status", base_ref, "HEAD", "--", filename],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    if check_result.returncode == 0 and check_result.stdout.startswith("A\t"):
                        metrics["has_new_features"] = True

            metrics["loc_changed"] = total_loc
            metrics["files_changed"] = len(files_changed)

        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            # Git not available or command failed - return safe defaults
            pass

        return metrics

    def requires_garden_tending(
        self,
        metrics: dict[str, Any],
        flags: dict[str, bool] | None = None,
    ) -> bool:
        """Determine if Garden Tending is required based on metrics and flags.

        Per ADR-002 enforcement rules:
        - Override if require_garden_tending flag is set
        - Skip if skip_garden_tending flag is set
        - Otherwise, require if:
          - >100 lines changed, OR
          - >5 files changed, OR
          - New features added

        Args:
            metrics: Metrics from calculate_metrics()
            flags: Optional flags dict with:
                - require_garden_tending: Force requirement
                - skip_garden_tending: Force skip

        Returns:
            True if Garden Tending is required, False otherwise

        Example:
            metrics = validator.calculate_metrics()
            if validator.requires_garden_tending(metrics):
                print("Must run Garden Tending before deployment")
        """
        flags = flags or {}

        # Check override flags
        if flags.get("require_garden_tending"):
            return True
        if flags.get("skip_garden_tending"):
            return False

        # Apply enforcement rules
        loc = metrics.get("loc_changed") or 0
        files = metrics.get("files_changed") or 0
        has_features = bool(metrics.get("has_new_features"))

        return loc > LOC_THRESHOLD or files > FILES_THRESHOLD or has_features

    def is_valid_transition(self, from_phase: str | None, to_phase: str) -> bool:
        """Check if workflow transition is valid.

        Validates that the requested transition follows the allowed workflow sequence.

        Args:
            from_phase: Current phase (None if starting)
            to_phase: Target phase

        Returns:
            True if transition is valid, False otherwise

        Example:
            if validator.is_valid_transition("design", "implementation"):
                print("Valid transition")
            else:
                print("Invalid - must complete design first")
        """
        if from_phase not in VALID_TRANSITIONS:
            return False

        return to_phase in VALID_TRANSITIONS[from_phase]

    def get_required_phase(self, current_phase: str | None) -> str | None:
        """Get the next required phase in workflow.

        Args:
            current_phase: Current workflow phase

        Returns:
            Next required phase, or None if workflow complete

        Example:
            next_phase = validator.get_required_phase("design")
            print(f"Next: {next_phase}")  # "implementation"
        """
        if current_phase not in VALID_TRANSITIONS:
            return None

        valid_next = VALID_TRANSITIONS[current_phase]
        if not valid_next:
            return None  # End of workflow

        # Return first valid transition
        return sorted(valid_next)[0]
