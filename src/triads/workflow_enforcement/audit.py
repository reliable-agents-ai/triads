"""Audit logging for workflow enforcement bypasses.

This module maintains an audit trail of all emergency bypass events
for security and compliance purposes.

Per ADR-005: All bypasses must be logged with timestamp, user, and justification
"""

from __future__ import annotations

import getpass
import json
from datetime import datetime
from pathlib import Path
from typing import Any


# Configuration
AUDIT_LOG_FILE = Path(".claude/workflow_audit.log")


class AuditLogger:
    """Logs workflow enforcement bypass events for audit trail.

    Example:
        logger = AuditLogger()
        logger.log_bypass("Critical hotfix for bug #1234")
    """

    def __init__(self, log_file: Path | None = None):
        """Initialize audit logger.

        Args:
            log_file: Path to audit log file (default: .claude/workflow_audit.log)
        """
        self.log_file = log_file or AUDIT_LOG_FILE

    def log_bypass(
        self,
        justification: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Log an emergency bypass event.

        Creates a JSON log entry with timestamp, user, justification, and metadata.
        Appends to audit log file.

        Args:
            justification: Justification provided for bypass
            metadata: Optional metadata (e.g., metrics, state info)

        Example:
            logger.log_bypass(
                "Hotfix for production issue",
                metadata={"loc_changed": 245, "files_changed": 8}
            )
        """
        # Ensure directory exists
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        # Build log entry
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event": "emergency_bypass",
            "user": self._get_user(),
            "justification": justification,
            "metadata": metadata or {},
        }

        # Append to log file
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def get_recent_bypasses(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get recent bypass events from audit log.

        Args:
            limit: Maximum number of events to return

        Returns:
            List of bypass event dictionaries (most recent first)

        Example:
            recent = logger.get_recent_bypasses(limit=5)
            for event in recent:
                print(f"{event['timestamp']}: {event['justification']}")
        """
        if not self.log_file.exists():
            return []

        bypasses = []

        try:
            with open(self.log_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        entry = json.loads(line)
                        if entry.get("event") == "emergency_bypass":
                            bypasses.append(entry)
                    except json.JSONDecodeError:
                        continue  # Skip malformed lines

        except OSError:
            return []

        # Return most recent first (last N entries from file, reversed)
        return list(reversed(bypasses[-limit:]))

    def _get_user(self) -> str:
        """Get current user identifier.

        Returns:
            Username string

        Example:
            user = logger._get_user()
            print(f"Current user: {user}")
        """
        try:
            # Try to get git user first
            import subprocess

            result = subprocess.run(
                ["git", "config", "user.name"],
                capture_output=True,
                text=True,
                timeout=2,
            )

            if result.returncode == 0 and result.stdout.strip():
                git_user = result.stdout.strip()

                # Also get email for full identification
                email_result = subprocess.run(
                    ["git", "config", "user.email"],
                    capture_output=True,
                    text=True,
                    timeout=2,
                )

                if email_result.returncode == 0 and email_result.stdout.strip():
                    return f"{git_user} <{email_result.stdout.strip()}>"

                return git_user

        except (subprocess.SubprocessError, FileNotFoundError, Exception):
            # Catch all subprocess/git errors including generic exceptions from mocking
            pass

        # Fall back to system user
        try:
            return getpass.getuser()
        except Exception:
            return "unknown"
