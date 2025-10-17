"""Workflow state management with atomic file operations.

This module handles persistent workflow state tracking using JSON storage
with file locking to prevent race conditions.

Per ADR-001: State stored in .claude/workflow_state.json
Per ADR-003: Uses fcntl for atomic writes on Unix systems
"""

from __future__ import annotations

import fcntl
import json
from datetime import datetime
from pathlib import Path
from typing import Any


# Configuration
STATE_FILE = Path(".claude/workflow_state.json")
VALID_TRIADS = {
    "idea-validation",
    "design",
    "implementation",
    "garden-tending",
    "deployment",
}


class WorkflowStateManager:
    """Manages workflow state with atomic file operations.

    Example:
        manager = WorkflowStateManager()
        state = manager.load_state()
        manager.mark_completed("design")
    """

    def __init__(self, state_file: Path | None = None):
        """Initialize state manager.

        Args:
            state_file: Path to state file (defaults to .claude/workflow_state.json)
        """
        self.state_file = state_file or STATE_FILE

    def load_state(self) -> dict[str, Any]:
        """Load workflow state from file with file locking.

        Handles missing or corrupted state files gracefully by returning
        a default empty state structure.

        Returns:
            State dictionary with structure:
            {
                "session_id": str,
                "completed_triads": list[str],
                "current_phase": str,
                "last_transition": str (ISO 8601),
                "metadata": dict
            }

        Example:
            state = manager.load_state()
            if "design" in state["completed_triads"]:
                print("Design phase completed")
        """
        # Ensure directory exists
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        # Return default state if file doesn't exist
        if not self.state_file.exists():
            return self._default_state()

        try:
            with open(self.state_file, "r") as f:
                # Acquire shared lock for reading
                fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                try:
                    state = json.load(f)
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)

            # Validate state structure
            if not isinstance(state, dict):
                return self._default_state()

            # Ensure required fields exist
            state.setdefault("session_id", self._generate_session_id())
            state.setdefault("completed_triads", [])
            state.setdefault("current_phase", None)
            state.setdefault("last_transition", None)
            state.setdefault("metadata", {})

            return state

        except (json.JSONDecodeError, OSError) as e:
            # Corrupted file - log and return default
            print(f"Warning: Corrupted state file ({e}). Using default state.")
            return self._default_state()

    def save_state(self, state: dict[str, Any]) -> None:
        """Save workflow state with atomic write and file locking.

        Uses file locking to prevent race conditions when multiple processes
        attempt to write simultaneously.

        Args:
            state: State dictionary to save

        Raises:
            OSError: If file operations fail

        Example:
            state = manager.load_state()
            state["current_phase"] = "implementation"
            manager.save_state(state)
        """
        # Ensure directory exists
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        # Write to temporary file first for atomicity
        temp_file = self.state_file.with_suffix(".tmp")

        try:
            with open(temp_file, "w") as f:
                # Acquire exclusive lock for writing
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    json.dump(state, f, indent=2)
                    f.flush()
                    # Ensure data is written to disk
                    import os
                    os.fsync(f.fileno())
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)

            # Atomic rename (overwrites existing file)
            temp_file.replace(self.state_file)

        except Exception as e:
            # Clean up temp file on failure
            if temp_file.exists():
                temp_file.unlink()
            raise OSError(f"Failed to save state: {e}") from e

    def mark_completed(self, triad: str, metadata: dict[str, Any] | None = None) -> None:
        """Mark a triad as completed and update state.

        Args:
            triad: Name of triad to mark completed (e.g., "design", "implementation")
            metadata: Optional metadata to store (e.g., metrics, trigger info)

        Raises:
            ValueError: If triad name is invalid

        Example:
            manager.mark_completed("design", metadata={
                "trigger": "user_command",
                "approved_by": "user"
            })
        """
        # Validate triad name
        if triad not in VALID_TRIADS:
            raise ValueError(
                f"Invalid triad '{triad}'. Must be one of: {', '.join(sorted(VALID_TRIADS))}"
            )

        # Load current state
        state = self.load_state()

        # Add to completed list (avoid duplicates)
        if triad not in state["completed_triads"]:
            state["completed_triads"].append(triad)

        # Update current phase
        state["current_phase"] = triad

        # Update timestamp
        state["last_transition"] = datetime.now().isoformat()

        # Merge metadata
        if metadata:
            state["metadata"].update(metadata)

        # Save updated state
        self.save_state(state)

    def clear_state(self) -> None:
        """Clear workflow state (start fresh).

        Useful for starting a new workflow session or resetting after deployment.

        Example:
            # After successful deployment, reset for next cycle
            manager.clear_state()
        """
        if self.state_file.exists():
            self.state_file.unlink()

    def _default_state(self) -> dict[str, Any]:
        """Create default empty state structure.

        Returns:
            Default state dictionary
        """
        return {
            "session_id": self._generate_session_id(),
            "completed_triads": [],
            "current_phase": None,
            "last_transition": None,
            "metadata": {},
        }

    def _generate_session_id(self) -> str:
        """Generate unique session ID.

        Returns:
            Session ID string (timestamp-based)
        """
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")
