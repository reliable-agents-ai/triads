"""Metrics framework for workflow enforcement.

Provides pluggable metrics system that works across domains (code, documents,
RFP analysis, legal review, etc.). Each domain implements MetricsProvider
interface and returns generic MetricsResult.

Public API:
    - MetricsProvider: Abstract base class for providers
    - MetricsResult: Generic metrics result structure
    - MetricsCalculationError: Exception for calculation failures
    - CodeMetricsProvider: Git-based code metrics
    - MetricsRegistry: Registry for managing providers
    - get_metrics_provider(): Get provider from global registry

Example:
    # Use code metrics
    from triads.workflow_enforcement.metrics import get_metrics_provider

    provider = get_metrics_provider("code")
    result = provider.calculate_metrics({"base_ref": "main"})

    if result.is_substantial():
        print("Garden Tending recommended")

    # Create custom provider
    from triads.workflow_enforcement.metrics import MetricsProvider, MetricsResult

    class MyProvider(MetricsProvider):
        @property
        def domain(self):
            return "my-domain"

        def calculate_metrics(self, context):
            # Custom logic
            return MetricsResult(...)
"""

from triads.workflow_enforcement.metrics.base import (
    MetricsCalculationError,
    MetricsProvider,
    MetricsResult,
)
from triads.workflow_enforcement.metrics.code_metrics import CodeMetricsProvider
from triads.workflow_enforcement.metrics.registry import (
    MetricsRegistry,
    get_metrics_provider,
)

__all__ = [
    "MetricsCalculationError",
    "MetricsProvider",
    "MetricsResult",
    "CodeMetricsProvider",
    "MetricsRegistry",
    "get_metrics_provider",
]
