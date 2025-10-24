"""Metrics provider registry.

Central registry for metrics providers across domains.
Providers are registered by domain name and can be retrieved on demand.

Per ADR-GENERIC: Pluggable metrics system for any domain
"""

from __future__ import annotations

from typing import Optional

from triads.tools.workflow.metrics.base import MetricsProvider
from triads.tools.workflow.metrics.code_metrics import CodeMetricsProvider


class MetricsRegistry:
    """Registry for metrics providers.

    Manages metrics providers and provides lookup by domain.

    Example:
        registry = MetricsRegistry()

        # Register custom provider
        registry.register(MyCustomProvider())

        # Get provider
        provider = registry.get_provider("my-domain")
        if provider:
            result = provider.calculate_metrics(context)

        # List all domains
        domains = registry.list_domains()
    """

    def __init__(self):
        """Initialize empty registry."""
        self._providers: dict[str, MetricsProvider] = {}

    def register(self, provider: MetricsProvider) -> None:
        """Register a metrics provider.

        If a provider for this domain already exists, it will be replaced.

        Args:
            provider: MetricsProvider instance to register

        Example:
            registry = MetricsRegistry()
            registry.register(CodeMetricsProvider())
            registry.register(DocumentMetricsProvider())
        """
        self._providers[provider.domain] = provider

    def get_provider(self, domain: str) -> Optional[MetricsProvider]:
        """Get provider for domain.

        Args:
            domain: Domain identifier (e.g., "code", "document")

        Returns:
            MetricsProvider if found, None otherwise

        Example:
            provider = registry.get_provider("code")
            if provider:
                result = provider.calculate_metrics({})
        """
        return self._providers.get(domain)

    def list_domains(self) -> list[str]:
        """List all registered domains.

        Returns:
            List of domain identifiers

        Example:
            domains = registry.list_domains()
            print(f"Available: {', '.join(domains)}")
        """
        return list(self._providers.keys())


# Global registry with pre-registered providers
_global_registry = MetricsRegistry()
_global_registry.register(CodeMetricsProvider())


def get_metrics_provider(domain: str) -> Optional[MetricsProvider]:
    """Get metrics provider from global registry.

    Convenience function for accessing the global registry.

    Args:
        domain: Domain identifier

    Returns:
        MetricsProvider if found, None otherwise

    Example:
        provider = get_metrics_provider("code")
        if provider:
            result = provider.calculate_metrics({"base_ref": "main"})
    """
    return _global_registry.get_provider(domain)
