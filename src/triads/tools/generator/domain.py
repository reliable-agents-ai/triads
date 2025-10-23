"""Domain models for generator tools.

Defines core data structures for agent generation operations.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class AgentDefinition:
    """Agent definition with metadata and content.

    Represents a generated agent with its role, tools, and
    markdown content.

    Attributes:
        name: Agent name (e.g., "investigator")
        role: Agent role description
        tools: List of tools agent can use
        content: Agent markdown content (full .md file)
        triad_id: Triad this agent belongs to
    """

    name: str
    role: str
    content: str
    triad_id: str
    tools: List[str] = field(default_factory=list)


@dataclass
class WorkflowTemplate:
    """Workflow template information.

    Represents a workflow template with domain and triad structure.

    Attributes:
        workflow_type: Type of workflow (e.g., "debugging", "software-development")
        domain: Human-readable domain description
        triads: List of triad identifiers
        description: Optional workflow description
    """

    workflow_type: str
    domain: str
    triads: List[str]
    description: Optional[str] = None
