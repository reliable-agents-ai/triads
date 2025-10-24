"""Backward compatibility shim for router module.

DEPRECATED: This module has been migrated to triads.tools.router.
Please update your imports:

    # Old (deprecated)
    from triads.router.config import RouterConfig

    # New (preferred)
    from triads.tools.router.config import RouterConfig

This shim will be removed in v0.11.0.
"""

import warnings


def _deprecation_warning(old_path: str, new_path: str) -> None:
    """Issue deprecation warning for old import."""
    warnings.warn(
        f"{old_path} is deprecated and will be removed in v0.11.0. "
        f"Use {new_path} instead.",
        DeprecationWarning,
        stacklevel=3
    )


def __getattr__(name: str):
    """Lazy-load from new location with deprecation warning."""
    # Map common imports
    import_map = {
        "RouterConfig": ("triads.tools.router.config", "RouterConfig"),
        "RouterState": ("triads.tools.router.domain", "RouterState"),
        "RoutingDecision": ("triads.tools.router.domain", "RoutingDecision"),
        "TriadRouter": ("triads.tools.router.router", "TriadRouter"),
        "RouterCLI": ("triads.tools.router.cli", "RouterCLI"),
        "TrainingModeHandler": ("triads.tools.router.training_mode", "TrainingModeHandler"),
        "RouterService": ("triads.tools.router.service", "RouterService"),
        "bootstrap_router_service": ("triads.tools.router.bootstrap", "bootstrap_router_service"),
        "RouterStateManager": ("triads.tools.router._state_manager", "_RouterStateManager"),
        "SemanticRouter": ("triads.tools.router._semantic_router", "SemanticRouter"),
        "LLMDisambiguator": ("triads.tools.router._llm_disambiguator", "LLMDisambiguator"),
        "GracePeriodChecker": ("triads.tools.router._grace_period", "GracePeriodChecker"),
        "NotificationBuilder": ("triads.tools.router._notifications", "NotificationBuilder"),
        "TelemetryLogger": ("triads.tools.router._telemetry", "TelemetryLogger"),
        "ManualSelector": ("triads.tools.router._manual_selector", "ManualSelector"),
        "RouterEmbedder": ("triads.tools.router._embedder", "RouterEmbedder"),
    }

    if name in import_map:
        new_module, new_name = import_map[name]
        _deprecation_warning(f"triads.router.{name}", f"{new_module}.{new_name}")

        import importlib
        module = importlib.import_module(new_module)
        return getattr(module, new_name)

    raise AttributeError(f"module 'triads.router' has no attribute '{name}'")
