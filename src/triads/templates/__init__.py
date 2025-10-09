"""
Template library for Triad Generator.

This module provides templates for generating:
- Custom agent markdown files
- Lifecycle hooks (Python scripts)
- Knowledge Management infrastructure
- Configuration files
"""

from triads.templates.agent_templates import (
    AGENT_TEMPLATE,
    BRIDGE_AGENT_ADDITIONS,
    CONSTITUTIONAL_PRINCIPLES_TEMPLATE,
)
from triads.templates.hook_templates import (
    README_TEMPLATE,
    SETTINGS_JSON_TEMPLATE,
)
from triads.templates.km_templates import (
    ENRICH_KNOWLEDGE_COMMAND,
    KM_STATUS_COMMAND,
    RESEARCH_AGENT_TEMPLATE,
    VERIFICATION_AGENT_TEMPLATE,
    get_domain_research_strategy,
)

__all__ = [
    # Agent templates
    "AGENT_TEMPLATE",
    "BRIDGE_AGENT_ADDITIONS",
    "CONSTITUTIONAL_PRINCIPLES_TEMPLATE",
    # Hook templates
    "SETTINGS_JSON_TEMPLATE",
    "README_TEMPLATE",
    # KM templates
    "RESEARCH_AGENT_TEMPLATE",
    "VERIFICATION_AGENT_TEMPLATE",
    "ENRICH_KNOWLEDGE_COMMAND",
    "KM_STATUS_COMMAND",
    "get_domain_research_strategy",
]
