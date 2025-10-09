"""Knowledge issue formatting for agents and users."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

# File paths
QUEUE_FILE = Path(".claude/km_queue.json")
STATUS_FILE = Path(".claude/km_status.md")

# Agent routing
ISSUE_TO_AGENT = {
    "sparse_entity": "research-agent",
    "low_confidence": "verification-agent",
    "missing_evidence": "verification-agent",
}


def format_km_notification(issues: list[dict[str, Any]]) -> str | None:
    """Format brief notification for user about detected issues.

    Args:
        issues: List of issue dictionaries

    Returns:
        Formatted notification string, or None if no issues
    """
    if not issues:
        return None

    total = len(issues)
    high_priority = sum(1 for i in issues if i.get("priority") == "high")

    # Count by type
    type_counts = Counter(i["type"] for i in issues)

    # Build notification
    if total == 1:
        issue_type = issues[0]["type"].replace("_", " ")
        return f"📋 1 KM issue detected ({issue_type})"

    # Multiple issues
    parts = []
    if high_priority > 0:
        parts.append(f"{high_priority} high priority")

    # Add type breakdown
    type_parts = []
    for issue_type, count in type_counts.most_common(3):
        type_name = issue_type.replace("_", " ")
        type_parts.append(f"{count} {type_name}")

    if type_parts:
        parts.append(", ".join(type_parts))

    detail = " (".join(parts) if parts else ""
    if detail:
        detail += ")"

    return f"📋 {total} KM issues detected {detail}"


def get_agent_for_issue(issue: dict[str, Any]) -> str:
    """Determine which system agent should handle an issue.

    Args:
        issue: Issue dictionary with 'type' field

    Returns:
        Agent name string

    Raises:
        ValueError: If issue type is unknown
    """
    issue_type = issue.get("type")

    if issue_type not in ISSUE_TO_AGENT:
        raise ValueError(f"Unknown issue type: {issue_type}")

    return ISSUE_TO_AGENT[issue_type]


def write_km_status_file() -> None:
    """Write agent-readable status file from issue queue.

    Reads from .claude/km_queue.json and writes to .claude/km_status.md.
    Groups issues by triad and priority for agent consumption.
    """
    # Load queue
    if not QUEUE_FILE.exists():
        return

    with open(QUEUE_FILE, "r") as f:
        queue = json.load(f)

    issues = queue.get("issues", [])

    if not issues:
        # Remove status file if no issues
        if STATUS_FILE.exists():
            STATUS_FILE.unlink()
        return

    # Group issues by triad and priority
    by_triad: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(
        lambda: {"high": [], "medium": []}
    )

    for issue in issues:
        triad = issue.get("triad", "unknown")
        priority = issue.get("priority", "medium")
        by_triad[triad][priority].append(issue)

    # Build markdown content
    lines = []
    lines.append("# Knowledge Management Status\n")
    lines.append("## Summary\n")

    total = len(issues)
    high_count = sum(1 for i in issues if i.get("priority") == "high")
    medium_count = total - high_count

    lines.append(f"**Total issues**: {total}\n")
    if high_count > 0:
        lines.append(f"- ⚠️  **{high_count} high priority**\n")
    if medium_count > 0:
        lines.append(f"- 📋 {medium_count} medium priority\n")

    lines.append("\n---\n\n")

    # List issues by triad
    for triad in sorted(by_triad.keys()):
        triad_issues = by_triad[triad]

        # Count for this triad
        triad_total = len(triad_issues["high"]) + len(triad_issues["medium"])
        lines.append(f"## {triad.title()} Triad ({triad_total} issues)\n\n")

        # High priority first
        if triad_issues["high"]:
            lines.append("### ⚠️  High Priority\n\n")
            for issue in triad_issues["high"]:
                lines.append(_format_issue_item(issue))

        # Medium priority
        if triad_issues["medium"]:
            lines.append("### 📋 Medium Priority\n\n")
            for issue in triad_issues["medium"]:
                lines.append(_format_issue_item(issue))

        lines.append("\n")

    # Write to file
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATUS_FILE, "w") as f:
        f.write("".join(lines))


def _format_issue_item(issue: dict[str, Any]) -> str:
    """Format a single issue as markdown list item.

    Args:
        issue: Issue dictionary

    Returns:
        Markdown formatted string
    """
    issue_type = issue["type"]
    node_id = issue["node_id"]
    label = issue.get("label", node_id)

    # Get agent responsible
    try:
        agent = get_agent_for_issue(issue)
        agent_text = f" → `{agent}`"
    except ValueError:
        agent_text = ""

    # Type-specific details
    details = []
    if issue_type == "sparse_entity":
        prop_count = issue.get("property_count", 0)
        details.append(f"{prop_count} properties")
    elif issue_type == "low_confidence":
        confidence = issue.get("confidence", 0)
        details.append(f"confidence: {confidence:.2f}")
    elif issue_type == "missing_evidence":
        details.append("no evidence")

    detail_text = f" ({', '.join(details)})" if details else ""

    # Type emoji
    type_emoji = {
        "sparse_entity": "🔍",
        "low_confidence": "⚠️",
        "missing_evidence": "❗",
    }.get(issue_type, "•")

    return f"- {type_emoji} **{label}** (`{node_id}`){detail_text}{agent_text}\n"
