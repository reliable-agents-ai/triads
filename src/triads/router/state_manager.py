"""
Router state management with file locking and atomic writes.

Manages persistent router state including active triad, conversation tracking,
and grace period enforcement.
"""

import fcntl
import json
import os
import sys
import tempfile
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .timestamp_utils import utc_now_aware, utc_now_iso


@dataclass
class RouterState:
    """
    Router state schema for tracking conversation and routing context.

    Attributes:
        session_id: Unique session identifier
        active_triad: Currently active triad name (None if no active triad)
        conversation_start: ISO 8601 timestamp when conversation started
        turn_count: Number of turns since triad activation
        last_activity: ISO 8601 timestamp of last routing activity
        pending_intents: List of pending intent classifications
        training_mode_confirmations: Count of confirmations in training mode
    """

    session_id: str
    active_triad: Optional[str] = None
    conversation_start: Optional[str] = None  # ISO 8601
    turn_count: int = 0
    last_activity: Optional[str] = None  # ISO 8601
    pending_intents: List[str] = field(default_factory=list)
    training_mode_confirmations: int = 0

    def to_json(self) -> dict:
        """Convert state to JSON-serializable dictionary."""
        return asdict(self)

    @classmethod
    def from_json(cls, data: dict) -> "RouterState":
        """
        Create RouterState from JSON dictionary.

        Handles missing fields gracefully by using defaults.
        """
        # Filter to only known fields to handle schema evolution
        valid_fields = {k: v for k, v in data.items() if k in cls.__annotations__}
        return cls(**valid_fields)

    def is_within_grace_period(
        self, grace_turns: int = 5, grace_minutes: int = 8
    ) -> bool:
        """
        Check if current state is within grace period.

        Grace period is satisfied if EITHER:
        - turn_count < grace_turns OR
        - time since conversation_start < grace_minutes

        Args:
            grace_turns: Maximum turns before grace period expires
            grace_minutes: Maximum minutes before grace period expires

        Returns:
            True if within grace period, False otherwise
        """
        if not self.active_triad or not self.conversation_start:
            return False

        # Check turn count
        if self.turn_count < grace_turns:
            return True

        # Check time elapsed
        try:
            start = datetime.fromisoformat(self.conversation_start.replace("Z", "+00:00"))
            now = utc_now_aware()
            elapsed_minutes = (now - start).total_seconds() / 60

            if elapsed_minutes < grace_minutes:
                return True
        except (ValueError, AttributeError):
            # Invalid timestamp - default to expired
            return False

        return False


class RouterStateManager:
    """
    Manages router state persistence with file locking and atomic writes.

    Features:
    - Concurrent access safety via fcntl.flock
    - Atomic writes via temp file + rename
    - Corruption recovery with automatic reset
    - Thread-safe operations
    """

    def __init__(self, state_path: Optional[Path] = None):
        """
        Initialize state manager.

        Args:
            state_path: Path to state JSON file. Defaults to ~/.claude/router_state.json
        """
        if state_path is None:
            state_path = Path.home() / ".claude" / "router_state.json"

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
                    return RouterState.from_json(data)
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
                    json.dump(state.to_json(), f, indent=2)
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
        return RouterState(session_id=str(uuid.uuid4()))

    def reset(self) -> None:
        """Clear state by deleting state file."""
        if self.state_path.exists():
            self.state_path.unlink()

    def update_activity(self, state: RouterState) -> RouterState:
        """
        Update last_activity timestamp and save.

        Args:
            state: Current router state

        Returns:
            Updated state
        """
        state.last_activity = utc_now_iso()
        self.save(state)
        return state

    def activate_triad(
        self, state: RouterState, triad_name: str
    ) -> RouterState:
        """
        Activate a triad and reset grace period.

        Args:
            state: Current router state
            triad_name: Name of triad to activate

        Returns:
            Updated state
        """
        state.active_triad = triad_name
        state.conversation_start = utc_now_iso()
        state.turn_count = 0
        state.last_activity = state.conversation_start
        self.save(state)
        return state

    def increment_turn(self, state: RouterState) -> RouterState:
        """
        Increment turn counter and update activity.

        Args:
            state: Current router state

        Returns:
            Updated state
        """
        state.turn_count += 1
        return self.update_activity(state)
