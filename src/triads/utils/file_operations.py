"""Consolidated file operations with atomic writes and file locking.

This module provides unified utilities for:
- Directory creation (mkdir -p equivalent)
- Atomic JSON read/write with file locking
- Atomic file append with file locking
- File locking context manager

Used by state_manager.py and audit.py to prevent race conditions.
"""

from __future__ import annotations

import fcntl
import json
import os
import time
from pathlib import Path
from typing import Any


def ensure_parent_dir(file_path: Path) -> None:
    """Ensure parent directory exists for the given file path.

    Equivalent to `mkdir -p $(dirname file_path)`.

    Args:
        file_path: Path to file whose parent directory should exist

    Example:
        ensure_parent_dir(Path(".claude/workflow_state.json"))
        # Creates .claude/ if it doesn't exist
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)


class FileLocker:
    """Context manager for fcntl-based file locking.

    Example:
        with FileLocker(lock_path, exclusive=True) as lock_fh:
            # Exclusive lock held
            # Perform file operations
            pass
        # Lock released
    """

    def __init__(self, lock_path: Path, exclusive: bool = True):
        """Initialize file locker.

        Args:
            lock_path: Path to lock file
            exclusive: If True, acquire exclusive lock (LOCK_EX), else shared (LOCK_SH)
        """
        self.lock_path = lock_path
        self.exclusive = exclusive
        self.lock_fh = None

    def __enter__(self):
        """Acquire file lock."""
        ensure_parent_dir(self.lock_path)
        self.lock_fh = open(self.lock_path, "a+")
        lock_type = fcntl.LOCK_EX if self.exclusive else fcntl.LOCK_SH
        fcntl.flock(self.lock_fh.fileno(), lock_type)
        return self.lock_fh

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Release file lock."""
        if self.lock_fh:
            fcntl.flock(self.lock_fh.fileno(), fcntl.LOCK_UN)
            self.lock_fh.close()
        return False


def atomic_read_json(
    file_path: Path,
    default: dict[str, Any] | None = None,
    lock: bool = True,
) -> dict[str, Any]:
    """Read JSON file with optional file locking.

    Args:
        file_path: Path to JSON file
        default: Default value if file doesn't exist or is corrupted (default: {})
        lock: If True, acquire shared lock during read (default: True)

    Returns:
        Parsed JSON data as dictionary

    Example:
        state = atomic_read_json(
            Path(".claude/workflow_state.json"),
            default={"completed_triads": []}
        )
    """
    if default is None:
        default = {}

    # Return default if file doesn't exist
    if not file_path.exists():
        return default

    try:
        if lock:
            # Read with shared lock
            with open(file_path, "r") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                try:
                    data = json.load(f)
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        else:
            # Read without lock
            with open(file_path, "r") as f:
                data = json.load(f)

        return data if isinstance(data, dict) else default

    except (json.JSONDecodeError, OSError) as e:
        print(f"Warning: Error reading {file_path} ({e}). Using default.")
        return default


def atomic_write_json(
    file_path: Path,
    data: dict[str, Any],
    lock: bool = True,
    indent: int = 2,
) -> None:
    """Write JSON file atomically with optional file locking.

    Uses write-to-temp-then-rename pattern for atomicity.

    Args:
        file_path: Path to JSON file
        data: Data to write
        lock: If True, acquire exclusive lock during write (default: True)
        indent: JSON indentation (default: 2)

    Raises:
        OSError: If file operations fail

    Example:
        atomic_write_json(
            Path(".claude/workflow_state.json"),
            {"completed_triads": ["design", "implementation"]}
        )
    """
    # Ensure directory exists
    ensure_parent_dir(file_path)

    # Generate unique temp filename (avoids collision in concurrent writes)
    temp_file = file_path.with_suffix(f".tmp.{os.getpid()}.{int(time.time() * 1000000)}")

    try:
        if lock:
            # Write with exclusive lock
            with open(temp_file, "w") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    json.dump(data, f, indent=indent)
                    f.flush()
                    os.fsync(f.fileno())  # Ensure data written to disk
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        else:
            # Write without lock
            with open(temp_file, "w") as f:
                json.dump(data, f, indent=indent)
                f.flush()
                os.fsync(f.fileno())

        # Atomic rename (overwrites existing file)
        temp_file.replace(file_path)

    except Exception as e:
        # Clean up temp file on failure
        if temp_file.exists():
            temp_file.unlink()
        raise OSError(f"Failed to write {file_path}: {e}") from e


def atomic_append(
    file_path: Path,
    line: str,
    lock: bool = True,
) -> None:
    """Append line to file atomically with optional file locking.

    Args:
        file_path: Path to file
        line: Line to append (newline will be added if missing)
        lock: If True, acquire exclusive lock during append (default: True)

    Example:
        atomic_append(
            Path(".claude/workflow_audit.log"),
            json.dumps({"event": "bypass", "user": "john"})
        )
    """
    # Ensure directory exists
    ensure_parent_dir(file_path)

    # Ensure line ends with newline
    if not line.endswith("\n"):
        line += "\n"

    if lock:
        # Append with exclusive lock
        with open(file_path, "a") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.write(line)
                f.flush()
                os.fsync(f.fileno())
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    else:
        # Append without lock
        with open(file_path, "a") as f:
            f.write(line)
            f.flush()
            os.fsync(f.fileno())
