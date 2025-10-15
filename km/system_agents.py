"""System agents for resolving KM issues."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

# Configuration
SYSTEM_AGENTS_DIR = Path(".claude/agents/system")

# Agent routing (same as formatting.py for consistency)
ISSUE_TO_AGENT = {
    "sparse_entity": "research-agent",
    "low_confidence": "verification-agent",
    "missing_evidence": "verification-agent",
}


def get_system_agent(agent_name: str) -> Path | None:
    """Get path to a system agent file.

    Args:
        agent_name: Name of the agent (e.g., "research-agent")

    Returns:
        Path to agent file, or None if not found
    """
    agent_path = SYSTEM_AGENTS_DIR / f"{agent_name}.md"
    return agent_path if agent_path.exists() else None


def list_system_agents() -> list[str]:
    """List all available system agents.

    Returns:
        List of agent names (without .md extension)
    """
    if not SYSTEM_AGENTS_DIR.exists():
        return []

    agents = []
    for agent_file in SYSTEM_AGENTS_DIR.glob("*.md"):
        agents.append(agent_file.stem)

    return sorted(agents)


def validate_agent_file(agent_path: Path) -> tuple[bool, list[str]]:
    """Validate agent file structure.

    Args:
        agent_path: Path to agent markdown file

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    if not agent_path.exists():
        errors.append("File does not exist")
        return False, errors

    content = agent_path.read_text()

    # Check for frontmatter
    if not content.startswith("---"):
        errors.append("Missing YAML frontmatter (must start with ---)")
        return False, errors

    # Extract frontmatter
    parts = content.split("---", 2)
    if len(parts) < 3:
        errors.append("Invalid frontmatter format (must have closing ---)")
        return False, errors

    frontmatter_text = parts[1]

    # Check for required fields
    required_fields = ["name", "role"]
    for field in required_fields:
        if not re.search(rf"^{field}:\s*.+", frontmatter_text, re.MULTILINE):
            errors.append(f"Missing required field: {field}")

    # Check for content after frontmatter
    body = parts[2].strip()
    if not body:
        errors.append("Agent file has no content after frontmatter")

    return len(errors) == 0, errors


def parse_agent_frontmatter(agent_path: Path) -> dict[str, Any] | None:
    """Parse YAML frontmatter from agent file.

    Args:
        agent_path: Path to agent markdown file

    Returns:
        Dictionary of frontmatter fields, or None if invalid
    """
    if not agent_path.exists():
        return None

    content = agent_path.read_text()

    if not content.startswith("---"):
        return None

    parts = content.split("---", 2)
    if len(parts) < 3:
        return None

    frontmatter_text = parts[1]

    # Simple key: value parsing (not full YAML)
    frontmatter = {}
    for line in frontmatter_text.split("\n"):
        line = line.strip()
        if ":" in line:
            key, value = line.split(":", 1)
            frontmatter[key.strip()] = value.strip()

    return frontmatter


def get_agent_for_issue_type(issue_type: str) -> str:
    """Map issue type to system agent name.

    Args:
        issue_type: Type of issue (sparse_entity, low_confidence, etc.)

    Returns:
        Agent name

    Raises:
        ValueError: If issue type is unknown
    """
    if issue_type not in ISSUE_TO_AGENT:
        raise ValueError(f"Unknown issue type: {issue_type}")

    return ISSUE_TO_AGENT[issue_type]


def format_agent_task(issue: dict[str, Any]) -> str:
    """Format task description for system agent invocation.

    Args:
        issue: Issue dictionary from queue

    Returns:
        Formatted task string
    """
    issue_type = issue["type"]
    node_id = issue["node_id"]
    label = issue.get("label", node_id)
    triad = issue.get("triad", "unknown")

    if issue_type == "sparse_entity":
        property_count = issue.get("property_count", 0)
        return (
            f"Enrich the sparse entity '{label}' ({node_id}) in the {triad} triad. "
            f"Currently has only {property_count} properties. "
            f"Research and add meaningful properties to this node."
        )

    elif issue_type == "low_confidence":
        confidence = issue.get("confidence", 0.0)
        return (
            f"Verify the low-confidence node '{label}' ({node_id}) in the {triad} triad. "
            f"Current confidence: {confidence:.2f}. "
            f"Validate the information and increase confidence, or mark as Uncertainty."
        )

    elif issue_type == "missing_evidence":
        return (
            f"Add evidence to '{label}' ({node_id}) in the {triad} triad. "
            f"This node lacks citation/evidence. "
            f"Find and add verifiable evidence for this claim."
        )

    else:
        return f"Resolve issue for '{label}' ({node_id}) in the {triad} triad."
