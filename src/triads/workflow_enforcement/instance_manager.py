"""Workflow instance manager with atomic file operations.

This module manages individual workflow instance lifecycle:
- Create new workflow instances
- Load/update/complete/abandon instances
- Track triad completions and skips
- Record workflow deviations
- Store significance metrics

Instances are stored as JSON files in:
- .claude/workflows/instances/ (active)
- .claude/workflows/completed/ (finished)
- .claude/workflows/abandoned/ (cancelled)

Per ADR-INSTANCE: One JSON file per workflow instance for isolation
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any

from triads.utils.file_operations import (
    atomic_read_json,
    atomic_write_json,
    ensure_parent_dir,
)


class InstanceNotFoundError(Exception):
    """Raised when workflow instance cannot be found."""
    pass


class InstanceValidationError(Exception):
    """Raised when workflow instance validation fails."""
    pass


@dataclass
class WorkflowInstance:
    """Workflow instance data structure.

    Attributes:
        instance_id: Unique instance identifier (slug-timestamp)
        workflow_type: Workflow type (e.g., "software-development", "rfp-writing")
        metadata: Instance metadata (title, user, timestamps, status)
        workflow_progress: Progress tracking (current triad, completed, skipped)
        workflow_deviations: List of deviations from workflow rules
        significance_metrics: Metrics for significance evaluation
    """
    instance_id: str
    workflow_type: str
    metadata: dict[str, Any] = field(default_factory=dict)
    workflow_progress: dict[str, Any] = field(default_factory=dict)
    workflow_deviations: list[dict[str, Any]] = field(default_factory=list)
    significance_metrics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary for JSON serialization.

        Returns:
            Dictionary representation of instance
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WorkflowInstance:
        """Create instance from dictionary.

        Args:
            data: Dictionary data

        Returns:
            WorkflowInstance instance
        """
        return cls(
            instance_id=data["instance_id"],
            workflow_type=data["workflow_type"],
            metadata=data.get("metadata", {}),
            workflow_progress=data.get("workflow_progress", {}),
            workflow_deviations=data.get("workflow_deviations", []),
            significance_metrics=data.get("significance_metrics", {})
        )


class WorkflowInstanceManager:
    """Manages workflow instance lifecycle with atomic operations.

    Example:
        manager = WorkflowInstanceManager()
        instance_id = manager.create_instance("software-development", "OAuth2", "user@example.com")
        manager.mark_triad_completed(instance_id, "idea-validation")
        manager.complete_instance(instance_id)
    """

    def __init__(self, base_dir: Path | str | None = None):
        """Initialize instance manager.

        Args:
            base_dir: Base directory for instances (default: .claude/workflows)
        """
        if base_dir is None:
            base_dir = Path(".claude/workflows")
        self.base_dir = Path(base_dir)

        # Instance directories
        self.instances_dir = self.base_dir / "instances"
        self.completed_dir = self.base_dir / "completed"
        self.abandoned_dir = self.base_dir / "abandoned"

        # Ensure directories exist
        self.instances_dir.mkdir(parents=True, exist_ok=True)
        self.completed_dir.mkdir(parents=True, exist_ok=True)
        self.abandoned_dir.mkdir(parents=True, exist_ok=True)

    def create_instance(
        self,
        workflow_type: str,
        title: str,
        user: str,
        metadata: dict[str, Any] | None = None
    ) -> str:
        """Create new workflow instance.

        Args:
            workflow_type: Workflow type identifier
            title: Human-readable title for instance
            user: User creating the instance
            metadata: Optional additional metadata

        Returns:
            Unique instance ID

        Raises:
            InstanceValidationError: If validation fails

        Example:
            instance_id = manager.create_instance(
                "software-development",
                "OAuth2 Integration",
                "user@example.com"
            )
        """
        # Validate inputs
        if not workflow_type or not isinstance(workflow_type, str):
            raise InstanceValidationError(
                "Invalid workflow_type: must be non-empty string"
            )

        if not title or not isinstance(title, str):
            raise InstanceValidationError(
                "Invalid title: must be non-empty string"
            )

        if not user or not isinstance(user, str):
            raise InstanceValidationError(
                "Invalid user: must be non-empty string"
            )

        # Generate unique instance ID
        instance_id = self._generate_instance_id(title)

        # Build instance data
        now = datetime.now().isoformat()

        instance_data = {
            "instance_id": instance_id,
            "workflow_type": workflow_type,
            "metadata": {
                "title": title,
                "started_by": user,
                "started_at": now,
                "status": "in_progress",
                **(metadata or {})
            },
            "workflow_progress": {
                "current_triad": None,
                "completed_triads": [],
                "skipped_triads": []
            },
            "workflow_deviations": [],
            "significance_metrics": {}
        }

        # Write instance file with file locking
        instance_file = self.instances_dir / f"{instance_id}.json"
        atomic_write_json(instance_file, instance_data)

        return instance_id

    def load_instance(self, instance_id: str) -> WorkflowInstance:
        """Load workflow instance by ID.

        Searches in all directories (instances, completed, abandoned).

        Args:
            instance_id: Instance identifier

        Returns:
            WorkflowInstance object

        Raises:
            InstanceNotFoundError: If instance not found
            InstanceValidationError: If instance data is invalid

        Example:
            instance = manager.load_instance("oauth2-integration-20251017-100523")
        """
        # Security: Validate instance_id to prevent path traversal
        if not self._is_valid_instance_id(instance_id):
            raise InstanceNotFoundError(
                f"Invalid instance ID format: {instance_id}\n"
                f"Instance IDs must be alphanumeric with hyphens only."
            )

        # Try each directory
        for directory in [self.instances_dir, self.completed_dir, self.abandoned_dir]:
            instance_file = directory / f"{instance_id}.json"

            if instance_file.exists():
                try:
                    # Read JSON directly to catch parse errors
                    import json
                    with open(instance_file, "r") as f:
                        data = json.load(f)

                    # Validate required fields
                    if "instance_id" not in data or "workflow_type" not in data:
                        raise InstanceValidationError(
                            f"Instance file missing required fields: {instance_file}"
                        )

                    return WorkflowInstance.from_dict(data)

                except json.JSONDecodeError as e:
                    raise InstanceValidationError(
                        f"Invalid JSON in instance file: {instance_file}\n"
                        f"Error: {e}"
                    )
                except InstanceValidationError:
                    raise
                except Exception as e:
                    raise InstanceValidationError(
                        f"Error loading instance file: {instance_file}\n"
                        f"Error: {e}"
                    )

        # Not found in any directory
        raise InstanceNotFoundError(
            f"Instance not found: {instance_id}\n"
            f"Searched in: instances, completed, abandoned"
        )

    def update_instance(self, instance_id: str, updates: dict[str, Any]) -> None:
        """Update workflow instance with partial updates.

        Updates are merged with existing data (not replaced).

        Args:
            instance_id: Instance identifier
            updates: Partial updates to apply

        Raises:
            InstanceNotFoundError: If instance not found

        Example:
            manager.update_instance(instance_id, {
                "significance_metrics": {
                    "content_created": {"type": "code", "quantity": 257}
                }
            })
        """
        # Load current instance
        instance = self.load_instance(instance_id)

        # Apply updates (merge, don't replace)
        instance_dict = instance.to_dict()

        for key, value in updates.items():
            if key in instance_dict and isinstance(instance_dict[key], dict) and isinstance(value, dict):
                # Merge dictionaries
                instance_dict[key].update(value)
            else:
                # Replace value
                instance_dict[key] = value

        # Save updated instance
        instance_file = self._find_instance_file(instance_id)
        atomic_write_json(instance_file, instance_dict)

    def mark_triad_completed(
        self,
        instance_id: str,
        triad_id: str,
        duration_minutes: float | None = None
    ) -> None:
        """Mark a triad as completed in workflow progress.

        Args:
            instance_id: Instance identifier
            triad_id: Triad identifier
            duration_minutes: Optional duration in minutes

        Example:
            manager.mark_triad_completed("instance-123", "idea-validation")
        """
        instance = self.load_instance(instance_id)

        # Check if already completed
        completed_ids = [
            t["triad_id"]
            for t in instance.workflow_progress.get("completed_triads", [])
        ]

        if triad_id in completed_ids:
            # Already completed - update current_triad but don't duplicate
            self.update_instance(instance_id, {
                "workflow_progress": {
                    "current_triad": triad_id
                }
            })
            return

        # Add to completed list
        completion_record = {
            "triad_id": triad_id,
            "completed_at": datetime.now().isoformat(),
            "duration_minutes": duration_minutes or 0.0
        }

        instance.workflow_progress.setdefault("completed_triads", [])
        instance.workflow_progress["completed_triads"].append(completion_record)

        # Update current triad
        instance.workflow_progress["current_triad"] = triad_id

        # Save
        instance_file = self._find_instance_file(instance_id)
        atomic_write_json(instance_file, instance.to_dict())

    def mark_triad_skipped(
        self,
        instance_id: str,
        triad_id: str,
        reason: str
    ) -> None:
        """Mark a triad as skipped in workflow progress.

        Args:
            instance_id: Instance identifier
            triad_id: Triad identifier
            reason: Reason for skipping

        Example:
            manager.mark_triad_skipped("instance-123", "design", "Design in Figma")
        """
        instance = self.load_instance(instance_id)

        # Add to skipped list
        skip_record = {
            "triad_id": triad_id,
            "skipped_at": datetime.now().isoformat(),
            "reason": reason
        }

        instance.workflow_progress.setdefault("skipped_triads", [])
        instance.workflow_progress["skipped_triads"].append(skip_record)

        # Save
        instance_file = self._find_instance_file(instance_id)
        atomic_write_json(instance_file, instance.to_dict())

    def add_deviation(
        self,
        instance_id: str,
        deviation: dict[str, Any]
    ) -> None:
        """Add workflow deviation to instance.

        Args:
            instance_id: Instance identifier
            deviation: Deviation data (must include 'type' and 'reason')

        Example:
            manager.add_deviation(instance_id, {
                "type": "skip_forward",
                "from_triad": "idea-validation",
                "to_triad": "implementation",
                "skipped": ["design"],
                "reason": "Design completed in Figma",
                "user": "user@example.com"
            })
        """
        instance = self.load_instance(instance_id)

        # Add timestamp if not present
        if "timestamp" not in deviation:
            deviation["timestamp"] = datetime.now().isoformat()

        # Add to deviations list
        instance.workflow_deviations.append(deviation)

        # Save
        instance_file = self._find_instance_file(instance_id)
        atomic_write_json(instance_file, instance.to_dict())

    def complete_instance(self, instance_id: str) -> None:
        """Mark instance as completed and move to completed directory.

        Args:
            instance_id: Instance identifier

        Example:
            manager.complete_instance("instance-123")
        """
        # Load instance
        instance = self.load_instance(instance_id)

        # Update status
        instance.metadata["status"] = "completed"
        instance.metadata["completed_at"] = datetime.now().isoformat()

        # Move file from instances to completed
        self._move_instance_file(
            instance_id,
            self.instances_dir,
            self.completed_dir,
            instance.to_dict()
        )

    def abandon_instance(self, instance_id: str, reason: str) -> None:
        """Mark instance as abandoned and move to abandoned directory.

        Args:
            instance_id: Instance identifier
            reason: Reason for abandonment

        Example:
            manager.abandon_instance("instance-123", "No longer needed")
        """
        # Load instance
        instance = self.load_instance(instance_id)

        # Update status
        instance.metadata["status"] = "abandoned"
        instance.metadata["abandon_reason"] = reason
        instance.metadata["abandoned_at"] = datetime.now().isoformat()

        # Move file from instances to abandoned
        self._move_instance_file(
            instance_id,
            self.instances_dir,
            self.abandoned_dir,
            instance.to_dict()
        )

    def list_instances(self, status: str | None = None) -> list[dict[str, Any]]:
        """List workflow instances, optionally filtered by status.

        Args:
            status: Optional status filter ("in_progress", "completed", "abandoned")

        Returns:
            List of instance metadata dictionaries

        Example:
            # List all instances
            all_instances = manager.list_instances()

            # List only active instances
            active = manager.list_instances(status="in_progress")
        """
        instances = []

        # Determine which directories to search
        if status == "in_progress":
            directories = [self.instances_dir]
        elif status == "completed":
            directories = [self.completed_dir]
        elif status == "abandoned":
            directories = [self.abandoned_dir]
        elif status is None:
            directories = [self.instances_dir, self.completed_dir, self.abandoned_dir]
        else:
            raise ValueError(
                f"Invalid status: {status}. "
                f"Must be one of: in_progress, completed, abandoned, or None"
            )

        # Collect instances from directories
        for directory in directories:
            if not directory.exists():
                continue

            for instance_file in directory.glob("*.json"):
                try:
                    data = atomic_read_json(instance_file)

                    # Extract summary info
                    instances.append({
                        "instance_id": data["instance_id"],
                        "workflow_type": data["workflow_type"],
                        "title": data.get("metadata", {}).get("title", "Untitled"),
                        "status": data.get("metadata", {}).get("status", "unknown"),
                        "started_at": data.get("metadata", {}).get("started_at"),
                        "current_triad": data.get("workflow_progress", {}).get("current_triad")
                    })

                except Exception:
                    # Skip malformed files
                    continue

        # Sort by started_at (most recent first)
        instances.sort(key=lambda x: x.get("started_at", ""), reverse=True)

        return instances

    def _generate_instance_id(self, title: str) -> str:
        """Generate unique instance ID from title and timestamp.

        Format: {slug}-{timestamp}
        Example: oauth2-integration-20251017-100523

        Args:
            title: Instance title

        Returns:
            Unique instance ID
        """
        # Create slug from title
        slug = self._slugify(title)

        # Add timestamp for uniqueness
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

        # Add microseconds to ensure uniqueness even in rapid succession
        microseconds = int(time.time() * 1_000_000) % 1_000_000

        return f"{slug}-{timestamp}-{microseconds:06d}"

    def _slugify(self, text: str) -> str:
        """Convert text to slug (lowercase, alphanumeric with hyphens).

        Args:
            text: Text to slugify

        Returns:
            Slugified text

        Example:
            _slugify("OAuth2 & JWT Integration!") -> "oauth2-jwt-integration"
        """
        # Lowercase
        text = text.lower()

        # Replace non-alphanumeric with hyphens
        text = re.sub(r"[^a-z0-9]+", "-", text)

        # Remove leading/trailing hyphens
        text = text.strip("-")

        # Collapse multiple hyphens
        text = re.sub(r"-+", "-", text)

        # Limit length
        if len(text) > 50:
            text = text[:50].rstrip("-")

        return text or "instance"

    def _is_valid_instance_id(self, instance_id: str) -> bool:
        """Validate instance ID format (security check).

        Args:
            instance_id: Instance ID to validate

        Returns:
            True if valid, False otherwise
        """
        # Only allow alphanumeric and hyphens
        return bool(re.match(r"^[a-z0-9\-]+$", instance_id))

    def _find_instance_file(self, instance_id: str) -> Path:
        """Find instance file path across all directories.

        Args:
            instance_id: Instance identifier

        Returns:
            Path to instance file

        Raises:
            InstanceNotFoundError: If not found
        """
        for directory in [self.instances_dir, self.completed_dir, self.abandoned_dir]:
            instance_file = directory / f"{instance_id}.json"
            if instance_file.exists():
                return instance_file

        raise InstanceNotFoundError(f"Instance file not found: {instance_id}")

    def _move_instance_file(
        self,
        instance_id: str,
        from_dir: Path,
        to_dir: Path,
        data: dict[str, Any]
    ) -> None:
        """Move instance file between directories atomically.

        Args:
            instance_id: Instance identifier
            from_dir: Source directory
            to_dir: Destination directory
            data: Updated instance data
        """
        from_file = from_dir / f"{instance_id}.json"
        to_file = to_dir / f"{instance_id}.json"

        # Write to new location
        atomic_write_json(to_file, data)

        # Remove from old location (only if new file was written successfully)
        if from_file.exists():
            from_file.unlink()
