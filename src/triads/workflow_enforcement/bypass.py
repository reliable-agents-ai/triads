"""Emergency bypass for workflow enforcement.

This module handles the --force-deploy flag and justification validation
for emergency deployments that need to skip Garden Tending.

Per ADR-005: Emergency bypass with audit trail
Security: Validates justification input to prevent shell injection
"""

from __future__ import annotations

import re
import sys
from typing import Any

from triads.workflow_enforcement.audit import AuditLogger


# Security: Characters that could enable shell injection
DANGEROUS_CHARS = ["$", "`", "\\", ";", "|", "&", ">", "<", "(", ")", "{", "}"]

# Minimum justification length
MIN_JUSTIFICATION_LENGTH = 10


class EmergencyBypass:
    """Handles emergency bypass with security validation and audit logging.

    Example:
        bypass = EmergencyBypass()
        if bypass.should_bypass(sys.argv):
            bypass.execute_bypass()  # Logs and allows deployment
    """

    def __init__(self, audit_logger: AuditLogger | None = None):
        """Initialize bypass handler.

        Args:
            audit_logger: Audit logger instance (default: new instance)
        """
        self.audit_logger = audit_logger or AuditLogger()

    def should_bypass(self, args: list[str] | None = None) -> bool:
        """Check if --force-deploy flag is present in arguments.

        Args:
            args: Command-line arguments (default: sys.argv)

        Returns:
            True if --force-deploy flag present

        Example:
            if bypass.should_bypass(sys.argv):
                print("Force deploy requested")
        """
        args = args or sys.argv
        return "--force-deploy" in args

    def get_justification(self, args: list[str] | None = None) -> str | None:
        """Extract justification from command-line arguments.

        Looks for --justification flag followed by justification text.

        Args:
            args: Command-line arguments (default: sys.argv)

        Returns:
            Justification string, or None if not provided

        Example:
            just = bypass.get_justification(sys.argv)
            if just:
                print(f"Justification: {just}")
        """
        args = args or sys.argv

        try:
            # Find --justification flag
            idx = args.index("--justification")

            # Get next argument as justification
            if idx + 1 < len(args):
                return args[idx + 1]

        except (ValueError, IndexError):
            pass

        return None

    def is_valid_justification(self, justification: str | None) -> tuple[bool, str]:
        """Validate justification meets security and content requirements.

        Security checks:
        - No shell metacharacters (prevents injection)
        - Minimum length requirement (ensures meaningful justification)

        Args:
            justification: Justification string to validate

        Returns:
            Tuple of (is_valid, error_message)
            If valid: (True, "")
            If invalid: (False, "reason")

        Example:
            valid, error = bypass.is_valid_justification("hotfix for bug #123")
            if not valid:
                print(f"Invalid: {error}")
        """
        if not justification:
            return False, "Justification is required with --force-deploy"

        if not isinstance(justification, str):
            return False, "Justification must be a string"

        # Check minimum length
        if len(justification.strip()) < MIN_JUSTIFICATION_LENGTH:
            return (
                False,
                f"Justification must be at least {MIN_JUSTIFICATION_LENGTH} characters",
            )

        # Security: Check for dangerous characters
        for char in DANGEROUS_CHARS:
            if char in justification:
                return (
                    False,
                    f"Justification contains dangerous character '{char}'. "
                    f"Please use only alphanumeric characters, spaces, and basic punctuation.",
                )

        # Additional security: Check for suspicious patterns
        suspicious_patterns = [
            r"rm\s+-rf",  # Dangerous rm command
            r"sudo\s+",  # Privilege escalation
            r"\$\(",  # Command substitution
            r"`.*`",  # Command substitution
        ]

        for pattern in suspicious_patterns:
            if re.search(pattern, justification, re.IGNORECASE):
                return (
                    False,
                    "Justification contains suspicious patterns. "
                    "Please provide a simple explanation.",
                )

        return True, ""

    def execute_bypass(
        self,
        justification: str,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Execute emergency bypass with audit logging.

        Args:
            justification: Validated justification string
            metadata: Optional metadata to include in audit log

        Returns:
            True (bypass approved)

        Example:
            if bypass.execute_bypass("hotfix for production issue"):
                print("Bypass approved and logged")
        """
        # Log bypass event
        self.audit_logger.log_bypass(
            justification=justification,
            metadata=metadata or {},
        )

        # Print confirmation
        print("\n" + "=" * 70)
        print("WARNING: Emergency Bypass Activated")
        print("=" * 70)
        print()
        print(f"Justification: {justification}")
        print()
        print("This bypass has been logged for audit purposes.")
        print("Garden Tending is still recommended after deployment.")
        print()
        print("=" * 70)
        print()

        return True

    def validate_and_execute(
        self,
        args: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Validate bypass request and execute if valid.

        Convenience method that combines checking, validation, and execution.

        Args:
            args: Command-line arguments (default: sys.argv)
            metadata: Optional metadata for audit log

        Returns:
            True if bypass executed, False if not requested

        Raises:
            SystemExit: If bypass requested but validation fails

        Example:
            if bypass.validate_and_execute(sys.argv):
                # Bypass approved - proceed with deployment
                pass
        """
        if not self.should_bypass(args):
            return False  # No bypass requested

        # Get justification
        justification = self.get_justification(args)

        # Validate justification
        valid, error = self.is_valid_justification(justification)

        if not valid:
            print("\n" + "=" * 70)
            print("ERROR: Invalid Emergency Bypass")
            print("=" * 70)
            print()
            print(error)
            print()
            print("Usage:")
            print("  --force-deploy --justification 'detailed reason for bypass'")
            print()
            print("Example:")
            print("  --force-deploy --justification 'Critical hotfix for production bug #1234'")
            print()
            print("=" * 70)
            print()
            sys.exit(1)

        # Execute bypass
        return self.execute_bypass(justification, metadata)


def check_bypass(args: list[str] | None = None) -> bool:
    """Convenience function to check and execute bypass.

    Args:
        args: Command-line arguments (default: sys.argv)

    Returns:
        True if bypass executed, False otherwise

    Example:
        from triads.workflow_enforcement import check_bypass
        if check_bypass(sys.argv):
            # Bypass approved
            pass
    """
    bypass = EmergencyBypass()
    return bypass.validate_and_execute(args)
