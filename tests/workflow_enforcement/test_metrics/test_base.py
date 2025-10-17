"""Tests for metrics base classes and interfaces.

Tests cover:
- MetricsResult dataclass structure
- MetricsProvider abstract interface
- is_substantial() logic
"""

import pytest
from abc import ABC
from triads.workflow_enforcement.metrics.base import (
    MetricsResult,
    MetricsProvider,
)


class TestMetricsResult:
    """Test MetricsResult dataclass."""

    def test_metrics_result_structure(self):
        """Test MetricsResult has expected fields."""
        result = MetricsResult(
            content_created={
                "type": "code",
                "quantity": 257,
                "units": "lines"
            },
            components_modified=8,
            complexity="substantial",
            raw_data={"loc_added": 257, "loc_deleted": 50}
        )

        assert result.content_created["type"] == "code"
        assert result.content_created["quantity"] == 257
        assert result.content_created["units"] == "lines"
        assert result.components_modified == 8
        assert result.complexity == "substantial"
        assert result.raw_data["loc_added"] == 257

    def test_is_substantial_with_substantial_complexity(self):
        """Test is_substantial returns True for substantial complexity."""
        result = MetricsResult(
            content_created={"type": "code", "quantity": 100, "units": "lines"},
            components_modified=5,
            complexity="substantial",
            raw_data={}
        )

        assert result.is_substantial() is True

    def test_is_substantial_with_moderate_complexity(self):
        """Test is_substantial returns True for moderate complexity."""
        result = MetricsResult(
            content_created={"type": "code", "quantity": 50, "units": "lines"},
            components_modified=3,
            complexity="moderate",
            raw_data={}
        )

        assert result.is_substantial() is True

    def test_is_substantial_with_minimal_complexity(self):
        """Test is_substantial returns False for minimal complexity."""
        result = MetricsResult(
            content_created={"type": "code", "quantity": 10, "units": "lines"},
            components_modified=1,
            complexity="minimal",
            raw_data={}
        )

        assert result.is_substantial() is False

    def test_content_created_flexible_structure(self):
        """Test content_created can have different structures."""
        # Code content
        code_result = MetricsResult(
            content_created={"type": "code", "quantity": 100, "units": "lines"},
            components_modified=5,
            complexity="moderate",
            raw_data={}
        )
        assert code_result.content_created["type"] == "code"

        # Document content
        doc_result = MetricsResult(
            content_created={"type": "document", "quantity": 2, "units": "pages"},
            components_modified=1,
            complexity="minimal",
            raw_data={}
        )
        assert doc_result.content_created["type"] == "document"

    def test_raw_data_can_be_empty(self):
        """Test raw_data can be empty dict."""
        result = MetricsResult(
            content_created={"type": "manual", "quantity": 0, "units": "N/A"},
            components_modified=0,
            complexity="minimal",
            raw_data={}
        )

        assert result.raw_data == {}


class TestMetricsProvider:
    """Test MetricsProvider abstract base class."""

    def test_metrics_provider_is_abstract(self):
        """Test MetricsProvider cannot be instantiated directly."""
        with pytest.raises(TypeError):
            MetricsProvider()

    def test_metrics_provider_requires_domain_property(self):
        """Test subclass must implement domain property."""
        class InvalidProvider(MetricsProvider):
            def calculate_metrics(self, context):
                return MetricsResult(
                    content_created={},
                    components_modified=0,
                    complexity="minimal",
                    raw_data={}
                )

        with pytest.raises(TypeError):
            InvalidProvider()

    def test_metrics_provider_requires_calculate_metrics(self):
        """Test subclass must implement calculate_metrics method."""
        class InvalidProvider(MetricsProvider):
            @property
            def domain(self):
                return "test"

        with pytest.raises(TypeError):
            InvalidProvider()

    def test_valid_metrics_provider_implementation(self):
        """Test valid MetricsProvider implementation."""
        class ValidProvider(MetricsProvider):
            @property
            def domain(self):
                return "test"

            def calculate_metrics(self, context):
                return MetricsResult(
                    content_created={"type": "test", "quantity": 1, "units": "items"},
                    components_modified=1,
                    complexity="minimal",
                    raw_data=context
                )

        provider = ValidProvider()
        assert provider.domain == "test"

        result = provider.calculate_metrics({"key": "value"})
        assert result.complexity == "minimal"
        assert result.raw_data["key"] == "value"

    def test_metrics_provider_interface_signature(self):
        """Test MetricsProvider has correct interface signature."""
        # Check that MetricsProvider has the required methods
        assert hasattr(MetricsProvider, 'domain')
        assert hasattr(MetricsProvider, 'calculate_metrics')

        # Check that they're abstract
        assert getattr(MetricsProvider.domain, '__isabstractmethod__', False)
        assert getattr(MetricsProvider.calculate_metrics, '__isabstractmethod__', False)
