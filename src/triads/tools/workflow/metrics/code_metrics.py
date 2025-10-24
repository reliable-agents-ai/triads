"""Code metrics provider for git-based workflows.

Calculates metrics from git diff:
- Lines of code added/deleted
- Files changed
- Complexity assessment

Reuses logic from validator.py but in domain-agnostic framework.
"""

from __future__ import annotations

from typing import Any

from triads.tools.workflow.metrics.base import (
    MetricsProvider,
    MetricsResult,
    MetricsCalculationError,
)
from triads.tools.workflow.git_utils import GitRunner, GitCommandError


class CodeMetricsProvider(MetricsProvider):
    """Metrics provider for code changes (git-based).

    Analyzes git diff to calculate:
    - Lines added/deleted
    - Files changed (including optional untracked)
    - Complexity based on thresholds

    Example:
        provider = CodeMetricsProvider()

        # Basic usage (compare to HEAD~1)
        result = provider.calculate_metrics({})

        # Custom base reference
        result = provider.calculate_metrics({"base_ref": "main"})

        # Include untracked files
        result = provider.calculate_metrics({
            "base_ref": "main",
            "include_untracked": True
        })
    """

    @property
    def domain(self) -> str:
        """Return domain identifier.

        Returns:
            "code"
        """
        return "code"

    def calculate_metrics(self, context: dict[str, Any]) -> MetricsResult:
        """Calculate code metrics from git diff.

        Args:
            context: Context dict with optional keys:
                - base_ref (str): Git reference to compare against (default: "HEAD~1")
                - include_untracked (bool): Include untracked files (default: False)

        Returns:
            MetricsResult with code metrics

        Raises:
            MetricsCalculationError: If git commands fail

        Example:
            result = provider.calculate_metrics({"base_ref": "main"})
            print(f"Added {result.content_created['quantity']} lines")
            print(f"Changed {result.components_modified} files")
            print(f"Complexity: {result.complexity}")
        """
        base_ref = context.get("base_ref", "HEAD~1")
        include_untracked = context.get("include_untracked", False)

        # Count lines added/deleted
        loc_added, loc_deleted = self._count_loc_changes(base_ref)

        # Count files changed
        files_changed = self._count_files_changed(base_ref, include_untracked)

        # Calculate complexity
        total_loc = loc_added + loc_deleted
        complexity = self._assess_complexity(total_loc, files_changed)

        return MetricsResult(
            content_created={
                "type": "code",
                "quantity": loc_added,
                "units": "lines"
            },
            components_modified=files_changed,
            complexity=complexity,
            raw_data={
                "loc_added": loc_added,
                "loc_deleted": loc_deleted,
                "files_changed": files_changed,
                "base_ref": base_ref
            }
        )

    def _count_loc_changes(self, base_ref: str) -> tuple[int, int]:
        """Count lines added and deleted using git diff --numstat.

        Uses git diff --numstat which outputs:
            <added>\t<deleted>\t<filename>

        Binary files are marked with "-" and ignored.

        Args:
            base_ref: Git reference to compare against

        Returns:
            Tuple of (lines_added, lines_deleted)

        Raises:
            MetricsCalculationError: If git command fails

        Example:
            added, deleted = provider._count_loc_changes("main")
            print(f"Changed {added + deleted} lines total")
        """
        try:
            changes = GitRunner.diff_numstat(base_ref, timeout=30)
            added = sum(a for a, d, f in changes)
            deleted = sum(d for a, d, f in changes)
            return added, deleted
        except GitCommandError as e:
            raise MetricsCalculationError(str(e)) from e

    def _count_files_changed(self, base_ref: str, include_untracked: bool) -> int:
        """Count files changed using git diff --name-only.

        Optionally includes untracked files using git ls-files.

        Args:
            base_ref: Git reference to compare against
            include_untracked: Include untracked files in count

        Returns:
            Number of files changed

        Raises:
            MetricsCalculationError: If git command fails

        Example:
            count = provider._count_files_changed("main", include_untracked=True)
            print(f"{count} files changed")
        """
        try:
            changed_count = len(GitRunner.diff_name_only(base_ref, timeout=30))

            if include_untracked:
                untracked_count = len(GitRunner.ls_files_untracked(timeout=30))
                changed_count += untracked_count

            return changed_count
        except GitCommandError as e:
            raise MetricsCalculationError(str(e)) from e

    def _assess_complexity(self, total_loc: int, files_changed: int) -> str:
        """Assess complexity based on LoC and files changed.

        Thresholds (per ADR-002):
            - Substantial: >100 LoC OR >5 files
            - Moderate: >30 LoC OR >2 files
            - Minimal: Everything else

        Args:
            total_loc: Total lines changed (added + deleted)
            files_changed: Number of files changed

        Returns:
            Complexity level: "minimal", "moderate", or "substantial"

        Example:
            complexity = provider._assess_complexity(150, 8)
            assert complexity == "substantial"
        """
        if total_loc > 100 or files_changed > 5:
            return "substantial"
        elif total_loc > 30 or files_changed > 2:
            return "moderate"
        else:
            return "minimal"
