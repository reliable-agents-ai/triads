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
from .config import RouterConfig
from .domain import RoutingDecision, RouterState
from .keywords import WORKFLOW_KEYWORDS, get_all_workflow_types, get_keywords
from .matching import MatchResult, WorkflowMatcher
from .repository import (
    AbstractRouterRepository,
    FileSystemRouterRepository,
    InMemoryRouterRepository,
    RouterRepositoryError,
)
from .router import TriadRouter
from ._notifications import NotificationBuilder
from ._semantic_router import SemanticRouter, TriadRoute, RoutingDecision
from ._llm_disambiguator import LLMDisambiguator, DisambiguationError
from ._state_manager import _RouterStateManager as RouterStateManager
from ._telemetry import TelemetryLogger
from ._grace_period import GracePeriodChecker
from ._manual_selector import ManualSelector
from ._embedder import RouterEmbedder

# Import CLI and training mode from old location (not yet migrated)
try:
    from triads.router.cli import RouterCLI
    from triads.router.training_mode import TrainingModeHandler
except ImportError:
    # Fallback if old location doesn't exist
    RouterCLI = None
    TrainingModeHandler = None

__all__ = [
    # Core orchestrator
    "TriadRouter",
    # State and config
    "RouterState",
    "RouterStateManager",
    "RouterConfig",
    # Components
    "RouterEmbedder",
    "SemanticRouter",
    "TriadRoute",
    "RoutingDecision",
    "GracePeriodChecker",
    "LLMDisambiguator",
    "DisambiguationError",
    "ManualSelector",
    # UI/UX
    "NotificationBuilder",
    "TrainingModeHandler",
    "RouterCLI",
    # Telemetry
    "TelemetryLogger",
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
