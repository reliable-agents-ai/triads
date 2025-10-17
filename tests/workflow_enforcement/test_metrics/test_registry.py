"""Tests for metrics registry system.

Tests cover:
- Registering metrics providers
- Retrieving providers by domain
- Global registry functionality
- Pre-registered code provider
"""

import pytest
from triads.workflow_enforcement.metrics.base import MetricsProvider, MetricsResult
from triads.workflow_enforcement.metrics.registry import (
    MetricsRegistry,
    get_metrics_provider,
)
from triads.workflow_enforcement.metrics.code_metrics import CodeMetricsProvider


class DummyMetricsProvider(MetricsProvider):
    """Dummy provider for testing."""

    def __init__(self, domain_name: str = "test"):
        self._domain = domain_name

    @property
    def domain(self) -> str:
        return self._domain

    def calculate_metrics(self, context):
        return MetricsResult(
            content_created={"type": self._domain, "quantity": 1, "units": "items"},
            components_modified=1,
            complexity="minimal",
            raw_data=context
        )


class TestMetricsRegistryBasics:
    """Test basic MetricsRegistry functionality."""

    def test_registry_initialization(self):
        """Test registry can be initialized."""
        registry = MetricsRegistry()
        assert registry is not None

    def test_register_provider(self):
        """Test registering a provider."""
        registry = MetricsRegistry()
        provider = DummyMetricsProvider("test")

        registry.register(provider)

        # Should be able to retrieve it
        retrieved = registry.get_provider("test")
        assert retrieved is provider

    def test_register_multiple_providers(self):
        """Test registering multiple providers."""
        registry = MetricsRegistry()

        provider1 = DummyMetricsProvider("domain1")
        provider2 = DummyMetricsProvider("domain2")
        provider3 = DummyMetricsProvider("domain3")

        registry.register(provider1)
        registry.register(provider2)
        registry.register(provider3)

        assert registry.get_provider("domain1") is provider1
        assert registry.get_provider("domain2") is provider2
        assert registry.get_provider("domain3") is provider3

    def test_register_overwrites_existing(self):
        """Test registering same domain overwrites."""
        registry = MetricsRegistry()

        provider1 = DummyMetricsProvider("test")
        provider2 = DummyMetricsProvider("test")

        registry.register(provider1)
        registry.register(provider2)

        # Should get the second one
        retrieved = registry.get_provider("test")
        assert retrieved is provider2
        assert retrieved is not provider1


class TestProviderRetrieval:
    """Test provider retrieval methods."""

    def test_get_provider_exists(self):
        """Test getting a registered provider."""
        registry = MetricsRegistry()
        provider = DummyMetricsProvider("test")

        registry.register(provider)
        retrieved = registry.get_provider("test")

        assert retrieved is provider

    def test_get_provider_not_found(self):
        """Test getting non-existent provider returns None."""
        registry = MetricsRegistry()

        retrieved = registry.get_provider("does-not-exist")

        assert retrieved is None

    def test_get_provider_case_sensitive(self):
        """Test domain lookup is case-sensitive."""
        registry = MetricsRegistry()
        provider = DummyMetricsProvider("Test")

        registry.register(provider)

        assert registry.get_provider("Test") is provider
        assert registry.get_provider("test") is None

    def test_list_domains_empty(self):
        """Test list_domains with empty registry."""
        registry = MetricsRegistry()

        domains = registry.list_domains()

        assert domains == []

    def test_list_domains_with_providers(self):
        """Test list_domains returns all domains."""
        registry = MetricsRegistry()

        registry.register(DummyMetricsProvider("domain1"))
        registry.register(DummyMetricsProvider("domain2"))
        registry.register(DummyMetricsProvider("domain3"))

        domains = registry.list_domains()

        assert len(domains) == 3
        assert "domain1" in domains
        assert "domain2" in domains
        assert "domain3" in domains

    def test_list_domains_returns_list(self):
        """Test list_domains returns a list."""
        registry = MetricsRegistry()
        registry.register(DummyMetricsProvider("test"))

        domains = registry.list_domains()

        assert isinstance(domains, list)


class TestGlobalRegistry:
    """Test global registry functionality."""

    def test_get_metrics_provider_function_exists(self):
        """Test global get_metrics_provider function exists."""
        assert callable(get_metrics_provider)

    def test_get_metrics_provider_code_domain(self):
        """Test code provider is pre-registered."""
        provider = get_metrics_provider("code")

        assert provider is not None
        assert isinstance(provider, CodeMetricsProvider)
        assert provider.domain == "code"

    def test_get_metrics_provider_non_existent(self):
        """Test getting non-existent domain returns None."""
        provider = get_metrics_provider("does-not-exist-domain")

        assert provider is None

    def test_global_registry_has_code_provider(self):
        """Test global registry has code provider by default."""
        provider = get_metrics_provider("code")

        assert provider is not None

        # Should be functional
        from unittest.mock import patch
        with patch.object(provider, '_count_loc_changes', return_value=(50, 20)):
            with patch.object(provider, '_count_files_changed', return_value=3):
                result = provider.calculate_metrics({})
                assert result.complexity in ["minimal", "moderate", "substantial"]


class TestProviderUsage:
    """Test using registered providers."""

    def test_provider_can_calculate_metrics(self):
        """Test retrieved provider can calculate metrics."""
        registry = MetricsRegistry()
        provider = DummyMetricsProvider("test")
        registry.register(provider)

        retrieved = registry.get_provider("test")
        result = retrieved.calculate_metrics({"key": "value"})

        assert isinstance(result, MetricsResult)
        assert result.content_created["type"] == "test"
        assert result.raw_data["key"] == "value"

    def test_different_providers_independent(self):
        """Test different providers work independently."""
        registry = MetricsRegistry()

        provider1 = DummyMetricsProvider("domain1")
        provider2 = DummyMetricsProvider("domain2")

        registry.register(provider1)
        registry.register(provider2)

        result1 = registry.get_provider("domain1").calculate_metrics({})
        result2 = registry.get_provider("domain2").calculate_metrics({})

        assert result1.content_created["type"] == "domain1"
        assert result2.content_created["type"] == "domain2"


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_register_none_provider(self):
        """Test registering None raises error."""
        registry = MetricsRegistry()

        with pytest.raises(AttributeError):
            registry.register(None)

    def test_register_non_provider_raises_error(self):
        """Test registering non-provider raises error."""
        registry = MetricsRegistry()

        with pytest.raises(AttributeError):
            registry.register("not a provider")

    def test_empty_domain_name(self):
        """Test provider with empty domain."""
        registry = MetricsRegistry()
        provider = DummyMetricsProvider("")

        registry.register(provider)

        retrieved = registry.get_provider("")
        assert retrieved is provider

    def test_special_characters_in_domain(self):
        """Test domain names with special characters."""
        registry = MetricsRegistry()

        provider = DummyMetricsProvider("domain-with-dashes")
        registry.register(provider)

        retrieved = registry.get_provider("domain-with-dashes")
        assert retrieved is provider
