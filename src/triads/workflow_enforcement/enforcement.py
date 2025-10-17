"""Blocking enforcement for deployment workflow.

This module provides the entry point for validating workflow state
before allowing deployment to proceed.

Per ADR-004: Blocks deployment with exit code 1 if Garden Tending required
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from triads.workflow_enforcement.state_manager import WorkflowStateManager
from triads.workflow_enforcement.validator import WorkflowValidator


class BlockingEnforcement:
    """Enforces workflow requirements before deployment.

    Example:
        enforcement = BlockingEnforcement()
        enforcement.validate_or_block()  # Exits if validation fails
    """

    def __init__(
        self,
        state_manager: WorkflowStateManager | None = None,
        validator: WorkflowValidator | None = None,
    ):
        """Initialize enforcement system.

        Args:
            state_manager: State manager instance (default: new instance)
            validator: Validator instance (default: new instance)
        """
        self.state_manager = state_manager or WorkflowStateManager()
        self.validator = validator or WorkflowValidator()

    def validate_or_block(self, allow_force: bool = False) -> bool:
        """Validate workflow state and block if requirements not met.

        Checks if Garden Tending has been completed before allowing deployment.
        If validation fails, prints error message and exits with code 1.

        Args:
            allow_force: If True, return False instead of exiting (for testing)

        Returns:
            True if validation passed, False if blocked (only if allow_force=True)

        Exits:
            System exit with code 1 if validation fails and allow_force=False

        Example:
            enforcement = BlockingEnforcement()
            enforcement.validate_or_block()  # Proceeds or exits
        """
        # Load current workflow state
        state = self.state_manager.load_state()
        completed_triads = state.get("completed_triads") or []

        # Check if Garden Tending has been completed
        if "garden-tending" in completed_triads:
            return True  # Garden Tending completed - allow deployment

        # Check if Implementation was completed (which triggers GT requirement)
        if "implementation" not in completed_triads:
            # No implementation yet - Garden Tending not required
            return True

        # Implementation completed but Garden Tending not done - check metrics
        metrics = self.validator.calculate_metrics()

        if not self.validator.requires_garden_tending(metrics):
            # Metrics don't trigger Garden Tending requirement
            return True

        # Garden Tending is required but not completed - BLOCK
        self._print_block_message(metrics)

        if allow_force:
            return False  # For testing - don't exit

        sys.exit(1)  # Block deployment

    def _print_block_message(self, metrics: dict[str, Any]) -> None:
        """Print informative error message when blocking deployment.

        Args:
            metrics: Metrics that triggered the block
        """
        print("\n" + "=" * 70)
        print("ERROR: Garden Tending Required Before Deployment")
        print("=" * 70)
        print()
        print("Your changes require Garden Tending before deployment:")
        print()

        # Show which rules triggered
        loc = metrics.get("loc_changed", 0)
        files = metrics.get("files_changed", 0)
        has_features = metrics.get("has_new_features", False)

        if loc > 100:
            print(f"  - {loc} lines changed (threshold: 100)")
        if files > 5:
            print(f"  - {files} files changed (threshold: 5)")
        if has_features:
            print("  - New features detected")

        print()
        print("Required Action:")
        print("  Run: Start Garden Tending: Post-implementation cleanup")
        print()
        print("Or to bypass (not recommended):")
        print("  Use: --force-deploy --justification 'hotfix for production issue'")
        print()
        print("=" * 70)
        print()


def validate_deployment() -> bool:
    """Convenience function for validating deployment workflow.

    Returns:
        True if validation passed, exits otherwise

    Example:
        from triads.workflow_enforcement import validate_deployment
        validate_deployment()  # Call at start of release-manager
    """
    enforcement = BlockingEnforcement()
    return enforcement.validate_or_block()
