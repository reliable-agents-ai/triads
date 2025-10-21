"""Workflow context utilities for tracking current workflow instance.

This module provides utilities for managing the "current" workflow instance
that agents are working on. It handles:
- Getting the current active instance ID
- Setting the current instance
- Auto-creating instances when starting triads
- Detecting instance from context clues
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from triads.utils.command_runner import CommandRunner
from triads.utils.file_operations import atomic_read_json, atomic_write_json
from triads.workflow_enforcement.instance_manager import WorkflowInstanceManager


def _validate_instance_id(instance_id: Optional[str]) -> bool:
    """Validate workflow instance ID format (prevent path traversal).

    Args:
        instance_id: Instance ID to validate

    Returns:
        True if valid, False otherwise

    Security:
        - Prevents path traversal (../, /, \\)
        - Enforces alphanumeric + hyphen/underscore only
        - Limits length to 255 characters

    Example:
        >>> _validate_instance_id("my-workflow-123")
        True
        >>> _validate_instance_id("../../../etc/passwd")
        False
    """
    if not instance_id or not isinstance(instance_id, str):
        return False

    # Prevent path traversal
    if '..' in instance_id or '/' in instance_id or '\\' in instance_id:
        return False

    # Enforce format: alphanumeric, hyphens, underscores only
    if not re.match(r'^[\w\-]+$', instance_id):
        return False

    # Length limits (prevent resource exhaustion)
    if len(instance_id) > 255:
        return False

    return True


def get_workflow_dir(cwd: str = ".") -> Path:
    """Get the .claude/workflows directory.

    Args:
        cwd: Current working directory

    Returns:
        Path to workflows directory
    """
    return Path(cwd) / ".claude" / "workflows"


def get_current_instance_file(cwd: str = ".") -> Path:
    """Get path to current instance marker file.

    Args:
        cwd: Current working directory

    Returns:
        Path to current_instance.json file
    """
    return get_workflow_dir(cwd) / "current_instance.json"


def get_current_instance_id(cwd: str = ".") -> Optional[str]:
    """Get the current active workflow instance ID.

    Checks in this order:
    1. Environment variable TRIADS_WORKFLOW_INSTANCE (must be valid format)
    2. Current instance file (.claude/workflows/current_instance.json)
    3. Most recently modified instance in instances/ directory

    Args:
        cwd: Current working directory

    Returns:
        Instance ID if found, None otherwise

    Note:
        Environment variable TRIADS_WORKFLOW_INSTANCE is validated to prevent
        path traversal attacks. Invalid values are ignored with a warning.
    """
    # 1. Check environment variable (highest priority, with validation)
    env_instance = os.environ.get("TRIADS_WORKFLOW_INSTANCE")
    if env_instance:
        # Validate env var to prevent path traversal
        if not _validate_instance_id(env_instance):
            import logging
            logging.warning(
                f"Invalid TRIADS_WORKFLOW_INSTANCE ignored: {env_instance}. "
                f"Must match pattern [\\w\\-]+ (alphanumeric, hyphens, underscores only)"
            )
        else:
            return env_instance

    # 2. Check current instance file (with atomic read)
    current_file = get_current_instance_file(cwd)
    if current_file.exists():
        try:
            # Use atomic read with file locking (prevents race conditions)
            data = atomic_read_json(current_file, default=None)
            if data:
                instance_id = data.get("instance_id")
                if instance_id:
                    # Verify instance still exists
                    manager = WorkflowInstanceManager(base_dir=get_workflow_dir(cwd))
                    try:
                        manager.load_instance(instance_id)
                        return instance_id
                    except Exception:
                        # Instance doesn't exist anymore, clear the file
                        current_file.unlink()
        except Exception as e:
            # File corrupt or read error - log and continue
            import logging
            logging.warning(f"Error reading current_instance.json: {e}")

    # 3. Fall back to most recently modified instance
    manager = WorkflowInstanceManager(base_dir=get_workflow_dir(cwd))
    active_instances = manager.list_instances(status="in_progress")

    if active_instances:
        # Sort by most recent activity (started_at or updated_at)
        sorted_instances = sorted(
            active_instances,
            key=lambda x: x.get("updated_at", x.get("started_at", "")),
            reverse=True
        )
        return sorted_instances[0]["instance_id"]

    return None


def set_current_instance(instance_id: str, cwd: str = ".") -> None:
    """Set the current workflow instance with atomic file operations.

    Args:
        instance_id: Instance ID to set as current
        cwd: Current working directory

    Raises:
        ValueError: If instance_id is invalid or contains path traversal

    Note:
        Uses atomic write operations with file locking to prevent race
        conditions when multiple processes/threads access the file.
    """
    # Validate instance_id (prevent path traversal)
    if not _validate_instance_id(instance_id):
        raise ValueError(
            f"Invalid instance_id: {instance_id}. "
            f"Must match pattern [\\w\\-]+ (alphanumeric, hyphens, underscores only)"
        )

    current_file = get_current_instance_file(cwd)

    data = {
        "instance_id": instance_id,
        "set_at": datetime.now(timezone.utc).isoformat()
    }

    # Use atomic write with file locking (prevents race conditions)
    atomic_write_json(current_file, data)


def auto_create_instance_if_needed(
    workflow_type: str = "software-development",
    title: Optional[str] = None,
    user: Optional[str] = None,
    cwd: str = "."
) -> str:
    """Auto-create a workflow instance if none exists.

    This is called when starting a triad and no current instance is found.

    Args:
        workflow_type: Type of workflow (default: "software-development")
        title: Workflow title (default: auto-generated from context)
        user: User identifier (default: from git config or "unknown")
        cwd: Current working directory

    Returns:
        Instance ID (existing or newly created)
    """
    # Check if we already have a current instance
    existing_id = get_current_instance_id(cwd)
    if existing_id:
        return existing_id

    # Need to create a new instance
    manager = WorkflowInstanceManager(base_dir=get_workflow_dir(cwd))

    # Auto-generate title if not provided
    if not title:
        # Try to infer from git branch or current directory
        try:
            result = CommandRunner.run_git(
                ["branch", "--show-current"],
                cwd=cwd,
                timeout=2,
                check=False  # Don't raise on error
            )
            if result.success:
                branch = result.stdout.strip()
                if branch and branch not in ["main", "master", "develop"]:
                    title = f"Work on {branch}"
        except Exception:
            pass

        if not title:
            title = f"Work session {datetime.now(timezone.utc).strftime('%Y-%m-%d')}"

    # Get user from git config if not provided
    if not user:
        try:
            result = CommandRunner.run_git(
                ["config", "user.email"],
                cwd=cwd,
                timeout=2,
                check=False  # Don't raise on error
            )
            if result.success:
                user = result.stdout.strip()
        except Exception:
            pass

        if not user:
            user = os.environ.get("USER", "unknown")

    # Create the instance
    instance_id = manager.create_instance(
        workflow_type=workflow_type,
        title=title,
        user=user,
        metadata={
            "auto_created": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    )

    # Set it as current
    set_current_instance(instance_id, cwd)

    return instance_id


def get_or_create_instance(
    workflow_type: str = "software-development",
    title: Optional[str] = None,
    user: Optional[str] = None,
    cwd: str = "."
) -> str:
    """Get current instance or create one if needed.

    Convenience function that combines get_current_instance_id() and
    auto_create_instance_if_needed().

    Args:
        workflow_type: Type of workflow (default: "software-development")
        title: Workflow title (default: auto-generated)
        user: User identifier (default: from git config)
        cwd: Current working directory

    Returns:
        Instance ID
    """
    return auto_create_instance_if_needed(workflow_type, title, user, cwd)
