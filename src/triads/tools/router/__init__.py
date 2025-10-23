"""Router tools for MCP integration.

Provides tools for:
- route_prompt: Semantic routing for user prompts
- get_current_triad: Get active triad from router state

Also includes workflow matching and classification functionality
moved from workflow_matching module as part of Phase 9 DDD refactoring.
"""

from .classification import (
    HeadlessClassificationResult,
    classify_workflow_headless,
    WORKFLOW_DEFINITIONS,
)
from .domain import RoutingDecision, RouterState
from .keywords import WORKFLOW_KEYWORDS, get_all_workflow_types, get_keywords
from .matching import MatchResult, WorkflowMatcher
from .repository import (
    AbstractRouterRepository,
    FileSystemRouterRepository,
    InMemoryRouterRepository,
    RouterRepositoryError,
)

__all__ = [
    # Domain models
    "RoutingDecision",
    "RouterState",
    # Repository layer
    "AbstractRouterRepository",
    "FileSystemRouterRepository",
    "InMemoryRouterRepository",
    "RouterRepositoryError",
    # Workflow matching
    "WorkflowMatcher",
    "MatchResult",
    # Keywords
    "WORKFLOW_KEYWORDS",
    "get_keywords",
    "get_all_workflow_types",
    # Classification
    "classify_workflow_headless",
    "HeadlessClassificationResult",
    "WORKFLOW_DEFINITIONS",
]
