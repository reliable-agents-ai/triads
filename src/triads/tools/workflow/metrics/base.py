"""Base classes for metrics framework.

Provides generic interfaces for measuring work across different domains
(code, documents, manual work, etc.). All metrics providers implement
the MetricsProvider interface and return MetricsResult objects.

Per ADR-GENERIC: Domain-agnostic workflow enforcement
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


class MetricsCalculationError(Exception):
    """Raised when metrics calculation fails."""
    pass


@dataclass
class MetricsResult:
    """Generic metrics result from any provider.

    This structure works across domains (code, documents, etc.) by using
    flexible content_created dict and generic complexity levels.

    Attributes:
        content_created: Dict describing what was created
            - type: Domain-specific type (e.g., "code", "document")
            - quantity: Numeric measure (e.g., lines, pages)
            - units: What quantity measures (e.g., "lines", "pages")
        components_modified: Number of components changed (files, sections, etc.)
        complexity: Complexity level ("minimal", "moderate", "substantial")
        raw_data: Provider-specific raw data for debugging/auditing

    Example:
        # Code metrics
        MetricsResult(
            content_created={"type": "code", "quantity": 257, "units": "lines"},
            components_modified=8,
            complexity="substantial",
            raw_data={"loc_added": 257, "loc_deleted": 50}
        )

        # Document metrics
        MetricsResult(
            content_created={"type": "document", "quantity": 5, "units": "pages"},
            components_modified=2,
            complexity="moderate",
            raw_data={"sections_modified": ["intro", "conclusion"]}
        )
    """
    content_created: dict[str, Any]
    components_modified: int
    complexity: str  # "minimal", "moderate", "substantial"
    raw_data: dict[str, Any]

    def is_substantial(self) -> bool:
        """Check if work is substantial.

        Work is substantial if complexity is "moderate" or "substantial".
        This is used to determine if Garden Tending is recommended.

        Returns:
            True if complexity >= moderate, False otherwise

        Example:
            if result.is_substantial():
                print("Garden Tending recommended")
        """
        return self.complexity in ["moderate", "substantial"]


class MetricsProvider(ABC):
    """Abstract base class for metrics providers.

    Each domain (code, documents, etc.) implements this interface to provide
    domain-specific metrics calculation that produces generic MetricsResult.

    Subclasses must implement:
        - domain: Property returning domain name
        - calculate_metrics(): Method to calculate metrics from context

    Example:
        class MyMetricsProvider(MetricsProvider):
            @property
            def domain(self) -> str:
                return "my-domain"

            def calculate_metrics(self, context: dict) -> MetricsResult:
                # Domain-specific calculation
                quantity = self._analyze(context)
                return MetricsResult(
                    content_created={"type": "my-domain", "quantity": quantity, "units": "items"},
                    components_modified=1,
                    complexity="moderate",
                    raw_data=context
                )
    """

    @property
    @abstractmethod
    def domain(self) -> str:
        """Domain this provider handles.

        Returns:
            Domain identifier (e.g., "code", "document", "manual")

        Example:
            provider = CodeMetricsProvider()
            print(provider.domain)  # "code"
        """
        pass

    @abstractmethod
    def calculate_metrics(self, context: dict[str, Any]) -> MetricsResult:
        """Calculate metrics for given context.

        Context structure is provider-specific. Code providers might use
        git references, document providers might use file paths, etc.

        Args:
            context: Provider-specific context for calculation

        Returns:
            MetricsResult with generic structure

        Raises:
            MetricsCalculationError: If calculation fails

        Example:
            provider = CodeMetricsProvider()
            result = provider.calculate_metrics({"base_ref": "main"})
            print(f"Complexity: {result.complexity}")
        """
        pass
