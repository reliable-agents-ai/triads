"""Workspace management for ephemeral workflow state.

Provides workspace lifecycle management:
- Create workspace with directory structure
- Load/save workspace state
- Track active workspace
- Mark workflows as paused/completed
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Workspace storage location
WORKSPACES_DIR = Path(".triads/workspaces")
ACTIVE_MARKER = Path(".triads/.active")


def atomic_write_json(file_path: Path, data: Any) -> None:
    """Atomic JSON write using temp file + os.replace().

    Args:
        file_path: Path to JSON file
        data: Data to write

    Example:
        atomic_write_json(Path("state.json"), {"status": "active"})
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = file_path.with_suffix(".tmp")

    # Write to temp file
    with open(temp_path, "w") as f:
        json.dump(data, f, indent=2)

    # Atomic replace
    temp_path.replace(file_path)


def atomic_read_json(file_path: Path) -> Any:
    """Atomic JSON read.

    Args:
        file_path: Path to JSON file

    Returns:
        Parsed JSON data

    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file contains invalid JSON

    Example:
        data = atomic_read_json(Path("state.json"))
    """
    with open(file_path, "r") as f:
        return json.load(f)


def generate_workspace_id(title: str) -> str:
    """Generate unique workspace ID from title.

    Format: workspace-{date}-{time}-{title-slug}

    Args:
        title: Brief title

    Returns:
        Workspace ID string

    Example:
        >>> generate_workspace_id("OAuth2 Authentication")
        'workspace-20251030-143022-oauth2-authentication'
    """
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y%m%d")
    time_str = now.strftime("%H%M%S")

    # Create slug from title (lowercase, alphanumeric + hyphens only)
    slug = "".join(c if c.isalnum() or c == " " else "" for c in title.lower())
    slug = "-".join(slug.split())[:40]  # Max 40 chars

    return f"workspace-{date_str}-{time_str}-{slug}"


def create_workspace(brief: dict[str, Any]) -> Path:
    """Create workspace directory with initial files.

    Creates:
    - workspace-{id}/
      - brief.json (feature/bug/refactor brief)
      - state.json (workflow state)
      - metadata.json (workspace metadata)
      - sessions.jsonl (event log)
      - scratchpad/{triad}/ (per-triad scratchpads)

    Args:
        brief: FeatureBrief/BugBrief/RefactorBrief dictionary

    Returns:
        Path to workspace directory

    Example:
        workspace_path = create_workspace({
            "brief_type": "feature",
            "title": "OAuth2 Authentication",
            "description": "...",
            "acceptance_criteria": [...]
        })
    """
    # Generate workspace ID
    workspace_id = generate_workspace_id(brief["title"])
    workspace_path = WORKSPACES_DIR / workspace_id

    # Create directory structure
    workspace_path.mkdir(parents=True, exist_ok=True)

    # Create initial files (atomic writes)
    atomic_write_json(workspace_path / "brief.json", brief)
    atomic_write_json(workspace_path / "state.json", _default_state(workspace_id))
    atomic_write_json(workspace_path / "metadata.json", _default_metadata(workspace_id))

    # Create empty sessions.jsonl
    (workspace_path / "sessions.jsonl").touch()

    # Create scratchpad directories
    triads = ["idea-validation", "design", "implementation", "garden-tending", "deployment"]
    for triad in triads:
        (workspace_path / "scratchpad" / triad).mkdir(parents=True, exist_ok=True)

    # Set as active
    set_active_workspace(workspace_id)

    return workspace_path


def load_workspace(workspace_id: str) -> dict[str, Any]:
    """Load workspace state and files.

    Args:
        workspace_id: Workspace identifier

    Returns:
        {
            "workspace_id": str,
            "brief": {...},
            "state": {...},
            "metadata": {...}
        }

    Raises:
        FileNotFoundError: If workspace doesn't exist

    Example:
        workspace = load_workspace("workspace-20251030-143022-oauth")
        print(workspace["state"]["status"])  # "active"
    """
    workspace_path = WORKSPACES_DIR / workspace_id

    if not workspace_path.exists():
        raise FileNotFoundError(f"Workspace not found: {workspace_id}")

    return {
        "workspace_id": workspace_id,
        "brief": atomic_read_json(workspace_path / "brief.json"),
        "state": atomic_read_json(workspace_path / "state.json"),
        "metadata": atomic_read_json(workspace_path / "metadata.json"),
    }


def set_active_workspace(workspace_id: str) -> None:
    """Set workspace as active via symlink.

    Creates .triads/.active symlink pointing to workspace directory.

    Args:
        workspace_id: Workspace identifier

    Example:
        set_active_workspace("workspace-20251030-143022-oauth")
    """
    workspace_path = WORKSPACES_DIR / workspace_id
    ACTIVE_MARKER.parent.mkdir(parents=True, exist_ok=True)

    # Remove existing symlink if present
    if ACTIVE_MARKER.exists() or ACTIVE_MARKER.is_symlink():
        ACTIVE_MARKER.unlink()

    # Create symlink
    ACTIVE_MARKER.symlink_to(workspace_path.resolve())


def get_active_workspace() -> str | None:
    """Get active workspace ID, or None if no active workspace.

    Returns:
        Workspace ID string, or None if no active workspace

    Example:
        active = get_active_workspace()
        if active:
            print(f"Active workspace: {active}")
        else:
            print("No active workspace")
    """
    if not ACTIVE_MARKER.exists():
        return None

    if not ACTIVE_MARKER.is_symlink():
        return None

    # Resolve symlink and get directory name
    workspace_path = ACTIVE_MARKER.resolve()
    return workspace_path.name


def mark_workspace_paused(workspace_id: str) -> None:
    """Mark workspace as paused.

    Updates state.json status to "paused" and last_updated timestamp.

    Args:
        workspace_id: Workspace identifier

    Example:
        mark_workspace_paused("workspace-20251030-143022-oauth")
    """
    _update_workspace_status(workspace_id, "paused")


def mark_workspace_completed(workspace_id: str) -> None:
    """Mark workspace as completed.

    Updates state.json status to "completed" and last_updated timestamp.

    Args:
        workspace_id: Workspace identifier

    Example:
        mark_workspace_completed("workspace-20251030-143022-oauth")
    """
    _update_workspace_status(workspace_id, "completed")


def _update_workspace_status(workspace_id: str, status: str) -> None:
    """Update workspace status (internal helper).

    Args:
        workspace_id: Workspace identifier
        status: New status ("active", "paused", "completed")
    """
    workspace_path = WORKSPACES_DIR / workspace_id
    state_file = workspace_path / "state.json"

    # Load current state
    state = atomic_read_json(state_file)

    # Update status and timestamp
    state["status"] = status
    state["last_updated"] = datetime.now(timezone.utc).isoformat()

    # Write back atomically
    atomic_write_json(state_file, state)


def _default_state(workspace_id: str) -> dict[str, Any]:
    """Generate default state.json.

    Args:
        workspace_id: Workspace identifier

    Returns:
        Default state dictionary
    """
    now = datetime.now(timezone.utc).isoformat()
    return {
        "workspace_id": workspace_id,
        "status": "active",
        "current_triad": None,
        "current_agent": None,
        "completed_triads": [],
        "completed_agents": [],
        "created_at": now,
        "last_updated": now,
    }


def _default_metadata(workspace_id: str) -> dict[str, Any]:
    """Generate default metadata.json.

    Args:
        workspace_id: Workspace identifier

    Returns:
        Default metadata dictionary
    """
    return {
        "workspace_id": workspace_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "session_count": 1,
    }
