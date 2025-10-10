"""Automatic system agent invocation for KM issues.

This module handles automatic queueing of system agent invocations when
high-priority KM issues are detected. This is Phase 2 of the agent-automated
KM system - automatic cleanup without human intervention.

Design:
- High-priority issues (low_confidence, missing_evidence) → auto-invoke
- Medium-priority issues (sparse_entity) → logged only, not auto-invoked
- Invocations queued to .claude/km_pending_invocations.json
- Future: Integrate with Claude SDK for actual invocation
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, cast

from .formatting import get_agent_for_issue
from .system_agents import format_agent_task


def queue_auto_invocations(
    issues: list[dict[str, Any]], output_dir: str | None = None
) -> list[dict[str, Any]]:
    """Queue automatic system agent invocations for high-priority issues.

    Args:
        issues: List of KM issues from detect_km_issues()
        output_dir: Output directory for invocation queue file (for testing)

    Returns:
        List of invocation dictionaries with agent, task, issue, queued_at

    Strategy:
        - High priority (low_confidence, missing_evidence) → auto-invoke
        - Medium priority (sparse_entity) → don't auto-invoke
        - Creates invocation task with full context for agent
    """
    invocations = []

    for issue in issues:
        priority = issue.get("priority", "medium")

        # Only auto-invoke high-priority issues
        if priority != "high":
            continue

        # Get appropriate system agent for this issue type
        agent_name = get_agent_for_issue(issue)

        if not agent_name:
            # Unknown issue type, skip
            continue

        # Format task description for agent
        task = format_agent_task(issue)

        # Create invocation record
        invocation = {
            "agent": agent_name,
            "task": task,
            "issue": issue,  # Include full issue data for debugging/logging
            "queued_at": datetime.now().isoformat(),
        }

        invocations.append(invocation)

    return invocations


def save_invocation_queue(
    invocations: list[dict[str, Any]], file_path: str
) -> None:
    """Save invocation queue to JSON file.

    Args:
        invocations: List of invocation dictionaries
        file_path: Path to save invocations (usually .claude/km_pending_invocations.json)

    Format:
        {
            "invocations": [
                {
                    "agent": "verification-agent",
                    "task": "...",
                    "issue": {...},
                    "queued_at": "2024-10-10T..."
                }
            ]
        }
    """
    file_path_obj = Path(file_path)
    file_path_obj.parent.mkdir(parents=True, exist_ok=True)

    data = {"invocations": invocations}

    with open(file_path_obj, "w") as f:
        json.dump(data, f, indent=2)


def merge_invocations(
    existing: list[dict[str, Any]], new: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Merge new invocations with existing, avoiding duplicates.

    Args:
        existing: Existing invocations from file
        new: New invocations to add

    Returns:
        Merged list with no duplicates

    Duplicate detection:
        Two invocations are duplicates if they have the same:
        - agent name
        - node_id (from issue)
        - issue type
    """
    # Create lookup key for deduplication
    def make_key(inv: dict[str, Any]) -> tuple[str, str, str]:
        issue = inv.get("issue", {})
        return (
            inv.get("agent", ""),
            issue.get("node_id", ""),
            issue.get("type", ""),
        )

    # Build set of existing keys
    existing_keys = {make_key(inv) for inv in existing}

    # Merge: keep existing, add new if not duplicate
    merged = list(existing)

    for inv in new:
        key = make_key(inv)
        if key not in existing_keys:
            merged.append(inv)
            existing_keys.add(key)

    return merged


def load_invocation_queue(file_path: str) -> list[dict[str, Any]]:
    """Load existing invocation queue from file.

    Args:
        file_path: Path to invocations file

    Returns:
        List of existing invocations, or [] if file doesn't exist
    """
    file_path_obj = Path(file_path)

    if not file_path_obj.exists():
        return []

    try:
        with open(file_path_obj) as f:
            data: dict[str, Any] = json.load(f)
            invocations = data.get("invocations", [])
            return cast(list[dict[str, Any]], invocations)
    except (json.JSONDecodeError, KeyError):
        # Corrupt file, return empty
        return []


def process_and_queue_invocations(
    issues: list[dict[str, Any]], invocations_file: str | None = None
) -> tuple[list[dict[str, Any]], int]:
    """Process issues and queue invocations (main entry point).

    Args:
        issues: List of KM issues from detect_km_issues()
        invocations_file: Path to invocations file (default: .claude/km_pending_invocations.json)

    Returns:
        Tuple of (new_invocations, total_invocations_count)
    """
    if invocations_file is None:
        invocations_file = str(Path(".claude/km_pending_invocations.json"))

    # Queue new invocations for high-priority issues
    new_invocations = queue_auto_invocations(issues)

    if not new_invocations:
        return [], 0

    # Load existing invocations
    existing = load_invocation_queue(invocations_file)

    # Merge (avoiding duplicates)
    merged = merge_invocations(existing, new_invocations)

    # Save to file
    save_invocation_queue(merged, invocations_file)

    return new_invocations, len(merged)
