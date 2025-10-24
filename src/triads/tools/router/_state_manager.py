"""
Router state persistence (infrastructure layer).

Manages file I/O for router state with file locking and atomic writes.
Separated from domain logic per DDD principles.
"""

import fcntl
import json
import os
import sys
import tempfile
import uuid
from pathlib import Path
from typing import Optional

from .domain import RouterState
from ._router_paths import DEFAULT_PATHS


class _RouterStateManager:
    """
    Manages router state persistence with file locking and atomic writes.

    Features:
    - Concurrent access safety via fcntl.flock
    - Atomic writes via temp file + rename
    - Corruption recovery with automatic reset
    - Thread-safe operations

    This is a private infrastructure utility (underscore prefix).
    """

    def __init__(self, state_path: Optional[Path] = None):
        """
        Initialize state manager.

        Args:
            state_path: Path to state JSON file. Defaults to ~/.claude/router_state.json
        """
        if state_path is None:
            state_path = DEFAULT_PATHS.state_file

        self.state_path = Path(state_path)
        self.state_path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> RouterState:
        """
        Load state from disk with file locking.

        Returns:
            RouterState object (default state if file doesn't exist or is corrupted)
        """
        if not self.state_path.exists():
            return self._create_default_state()

        try:
            with open(self.state_path, "r") as f:
                # Acquire shared lock for reading
                fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                try:
                    data = json.load(f)
                    return RouterState.from_dict(data)
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        except (json.JSONDecodeError, KeyError) as e:
            # Corrupted state - log and reset
            print(
                f"Warning: Corrupted router state, resetting: {e}",
                file=sys.stderr
            )
            return self._create_default_state()

    def save(self, state: RouterState) -> None:
        """
        Save state to disk with atomic write.

        Uses temp file + rename for atomicity to prevent corruption.

        Args:
            state: RouterState to persist
        """
        # Write to temp file first
        temp_fd, temp_path = tempfile.mkstemp(
            dir=self.state_path.parent,
            text=True
        )

        try:
            with os.fdopen(temp_fd, "w") as f:
                # Acquire exclusive lock for writing
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    json.dump(state.to_dict(), f, indent=2)
                    f.flush()
                    os.fsync(f.fileno())  # Ensure written to disk
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)

            # Atomic rename
            os.rename(temp_path, self.state_path)
        except Exception:
            # Clean up temp file on error
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise

    def _create_default_state(self) -> RouterState:
        """Create default router state with new session ID."""
        return RouterState(
            session_id=str(uuid.uuid4())
        )

    def reset(self) -> None:
        """Clear state by deleting state file."""
        if self.state_path.exists():
            self.state_path.unlink()
