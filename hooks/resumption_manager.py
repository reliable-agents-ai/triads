"""Workspace resumption management.

Constitutional TDD: BLUE Phase
Refactored for code quality (functions ≤20 lines, extracted helpers).

Handles:
- State reconstruction from event logs
- Resumption decision logic
- Resumption prompt generation
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# Workspace storage location
WORKSPACES_DIR = Path(".triads/workspaces")

# Prompt formatting constants
PROMPT_SEPARATOR_LENGTH = 80
SUMMARY_MAX_LENGTH = 100
RECENT_AGENTS_SHOWN = 3


def _create_default_state(workspace_id: str) -> dict[str, Any]:
    """Create default workspace state.

    Args:
        workspace_id: Workspace identifier

    Returns:
        Default state dictionary
    """
    return {
        "workspace_id": workspace_id,
        "status": "active",
        "current_triad": None,
        "current_agent": None,
        "completed_triads": [],
        "completed_agents": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }


def _update_state_from_event(state: dict[str, Any], event: dict[str, Any]) -> None:
    """Update state based on single event.

    Mutates state dict in place based on event subject/predicate/object.

    Args:
        state: State dictionary to update
        event: Event dictionary with subject, predicate, object
    """
    subject = event.get("subject")
    predicate = event.get("predicate")
    obj = event.get("object", {})

    if subject == "workspace" and predicate == "paused":
        state["status"] = "paused"
        state["last_updated"] = event.get("timestamp")
    elif subject == "workspace" and predicate == "completed":
        state["status"] = "completed"
        state["last_updated"] = event.get("timestamp")
    elif subject == "triad" and predicate == "started":
        state["current_triad"] = obj.get("triad")
    elif subject == "triad" and predicate == "completed":
        triad = obj.get("triad")
        if triad and triad not in state["completed_triads"]:
            state["completed_triads"].append(triad)
    elif subject == "agent" and predicate == "started":
        state["current_agent"] = obj.get("agent")
    elif subject == "agent" and predicate == "completed":
        agent = obj.get("agent")
        if agent and agent not in state["completed_agents"]:
            state["completed_agents"].append(agent)
        state["current_agent"] = None


def reconstruct_state_from_events(workspace_path: Path) -> dict[str, Any]:
    """Reconstruct workspace state from sessions.jsonl event log.

    Used when state.json is corrupted or missing. Parses event log to
    determine current status, completed agents, and current triad.

    Args:
        workspace_path: Path to workspace directory

    Returns:
        Reconstructed state dictionary

    Example:
        >>> state = reconstruct_state_from_events(Path(".triads/workspaces/ws1"))
        >>> state["status"]
        'paused'
        >>> "research-analyst" in state["completed_agents"]
        True
    """
    workspace_id = workspace_path.name
    sessions_file = workspace_path / "sessions.jsonl"
    state = _create_default_state(workspace_id)

    if not sessions_file.exists():
        return state

    # Parse events to reconstruct state
    try:
        with open(sessions_file, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                try:
                    event = json.loads(line)
                    _update_state_from_event(state, event)
                except json.JSONDecodeError:
                    continue  # Skip corrupted lines

    except IOError:
        pass  # File read error - return default state

    return state


def can_resume_workspace(workspace_id: str) -> bool:
    """Check if workspace can be resumed.

    A workspace can be resumed if:
    - It exists
    - Status is "paused" (not "active" or "completed")
    - state.json is valid (or can be reconstructed)

    Args:
        workspace_id: Workspace identifier

    Returns:
        True if workspace can be resumed, False otherwise

    Example:
        >>> can_resume_workspace("workspace-20251030-143022-oauth")
        True  # If workspace is paused
    """
    workspace_path = WORKSPACES_DIR / workspace_id

    if not workspace_path.exists():
        return False

    state_file = workspace_path / "state.json"

    try:
        # Try to load state.json
        if state_file.exists():
            with open(state_file, "r") as f:
                state = json.load(f)
        else:
            # Reconstruct from events
            state = reconstruct_state_from_events(workspace_path)

        # Can only resume if paused
        return state.get("status") == "paused"

    except (json.JSONDecodeError, IOError):
        # Corrupted state - try reconstruction
        try:
            state = reconstruct_state_from_events(workspace_path)
            return state.get("status") == "paused"
        except Exception:
            return False


def should_auto_resume() -> bool:
    """Check if session should auto-resume a workspace.

    Auto-resume if:
    - .active marker exists
    - Points to a paused workspace
    - User hasn't explicitly started new work

    Returns:
        True if should auto-resume, False otherwise

    Example:
        >>> should_auto_resume()
        True  # If .active points to paused workspace
    """
    from workspace_manager import get_active_workspace

    active_workspace = get_active_workspace()

    if not active_workspace:
        return False

    return can_resume_workspace(active_workspace)


def _load_workspace_brief(workspace_path: Path) -> tuple[str, str]:
    """Load workspace brief title and summary.

    Args:
        workspace_path: Path to workspace directory

    Returns:
        Tuple of (title, summary)
    """
    brief_file = workspace_path / "brief.json"
    if brief_file.exists():
        try:
            with open(brief_file, "r") as f:
                brief = json.load(f)
            return brief.get("title", "Unknown"), brief.get("summary", "")
        except (json.JSONDecodeError, IOError):
            pass
    return workspace_path.name, ""


def _load_workspace_state(workspace_path: Path) -> dict[str, Any]:
    """Load workspace state (or reconstruct from events).

    Args:
        workspace_path: Path to workspace directory

    Returns:
        State dictionary
    """
    state_file = workspace_path / "state.json"
    if state_file.exists():
        try:
            with open(state_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return reconstruct_state_from_events(workspace_path)


def _format_resumption_prompt(
    title: str, summary: str, state: dict[str, Any]
) -> str:
    """Format resumption prompt from workspace data.

    Args:
        title: Workspace title
        summary: Workspace summary
        state: Workspace state dictionary

    Returns:
        Formatted prompt string
    """
    current_triad = state.get("current_triad", "unknown")
    completed_agents = state.get("completed_agents", [])
    next_agent = state.get("next_agent")
    current_phase = state.get("current_phase", "")

    lines = [
        "=" * PROMPT_SEPARATOR_LENGTH,
        "⏸️  PAUSED WORKSPACE DETECTED",
        "=" * PROMPT_SEPARATOR_LENGTH,
        "",
        f"**Workspace**: {title}",
    ]

    if summary:
        lines.append(f"**Summary**: {summary[:SUMMARY_MAX_LENGTH]}...")

    lines.extend(["", "**Progress**:", f"- Current Triad: {current_triad}"])

    if current_phase:
        lines.append(f"- Current Phase: {current_phase}")

    if completed_agents:
        recent = ", ".join(completed_agents[-RECENT_AGENTS_SHOWN:])
        lines.append(f"- Completed Agents: {recent}")

    if next_agent:
        lines.append(f"- Next Agent: {next_agent}")

    lines.extend([
        "",
        "**Options**:",
        "1. **Resume** - Continue where you left off",
        "2. **Abandon** - Start fresh (workspace will remain paused)",
        "3. **View Details** - See full workspace context",
        "",
        "What would you like to do?",
        "",
        "=" * PROMPT_SEPARATOR_LENGTH,
    ])

    return "\n".join(lines)


def generate_resumption_prompt(workspace_id: str) -> Optional[str]:
    """Generate resumption prompt for user.

    Creates context-rich prompt explaining:
    - What workspace was working on
    - What was completed
    - What's next
    - User options (continue, abandon, view details)

    Args:
        workspace_id: Workspace identifier

    Returns:
        Resumption prompt string, or None if workspace not found

    Example:
        >>> prompt = generate_resumption_prompt("workspace-20251030-143022-oauth")
        >>> "OAuth2 Authentication" in prompt
        True
    """
    workspace_path = WORKSPACES_DIR / workspace_id

    if not workspace_path.exists():
        return None

    try:
        title, summary = _load_workspace_brief(workspace_path)
        state = _load_workspace_state(workspace_path)
        return _format_resumption_prompt(title, summary, state)
    except (json.JSONDecodeError, IOError):
        return f"Paused workspace detected: {workspace_id}\n\nWould you like to resume?"
