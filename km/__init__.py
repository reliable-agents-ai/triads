"""Knowledge Management module for Triads."""

from .detection import (
    count_meaningful_properties,
    detect_km_issues,
    update_km_queue,
)
from .formatting import (
    format_km_notification,
    get_agent_for_issue,
    write_km_status_file,
)
from .system_agents import (
    format_agent_task,
    get_agent_for_issue_type,
    get_system_agent,
    list_system_agents,
    parse_agent_frontmatter,
    validate_agent_file,
)

__all__ = [
    "count_meaningful_properties",
    "detect_km_issues",
    "format_agent_task",
    "format_km_notification",
    "get_agent_for_issue",
    "get_agent_for_issue_type",
    "get_system_agent",
    "list_system_agents",
    "parse_agent_frontmatter",
    "update_km_queue",
    "validate_agent_file",
    "write_km_status_file",
]
