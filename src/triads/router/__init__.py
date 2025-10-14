"""
Router module for intelligent triad routing.

Provides semantic similarity-based routing with LLM fallback for ambiguous cases.
"""

from .cli import RouterCLI
from .config import RouterConfig
from .embedder import RouterEmbedder
from .grace_period import GracePeriodChecker
from .llm_disambiguator import DisambiguationError, LLMDisambiguator
from .manual_selector import ManualSelector
from .notifications import NotificationBuilder
from .router import TriadRouter
from .semantic_router import RoutingDecision, SemanticRouter, TriadRoute
from .state_manager import RouterState, RouterStateManager
from .telemetry import TelemetryLogger
from .training_mode import TrainingModeHandler

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
]
