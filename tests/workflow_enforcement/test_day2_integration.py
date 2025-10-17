"""Integration tests for Day 2 modules (triad discovery + metrics).

These tests demonstrate the modules working together to discover triads
and calculate metrics for dynamic workflow enforcement.
"""

import pytest
import os
from unittest.mock import patch
from triads.workflow_enforcement.triad_discovery import TriadDiscovery, TriadInfo
from triads.workflow_enforcement.metrics import (
    get_metrics_provider,
    CodeMetricsProvider,
    MetricsResult,
)


class TestTriadDiscoveryIntegration:
    """Test triad discovery with real .claude/agents directory."""

    def test_discover_real_triads(self):
        """Test discovering triads from actual .claude/agents directory."""
        # Use real directory if it exists
        if os.path.exists(".claude/agents"):
            discovery = TriadDiscovery(base_path=".claude/agents")
            triads = discovery.discover_triads()

            # Should find at least some triads
            assert len(triads) > 0

            # Each triad should have valid structure
            for triad in triads:
                assert isinstance(triad, TriadInfo)
                assert triad.id
                assert triad.path
                assert isinstance(triad.agents, list)
                assert triad.agent_count >= 0


class TestMetricsProviderIntegration:
    """Test metrics provider integration."""

    def test_get_code_metrics_provider(self):
        """Test getting code metrics provider from global registry."""
        provider = get_metrics_provider("code")

        assert provider is not None
        assert isinstance(provider, CodeMetricsProvider)
        assert provider.domain == "code"

    def test_calculate_code_metrics_mocked(self):
        """Test calculating code metrics with mocked git."""
        provider = get_metrics_provider("code")

        with patch.object(provider, '_count_loc_changes', return_value=(120, 40)):
            with patch.object(provider, '_count_files_changed', return_value=6):
                result = provider.calculate_metrics({"base_ref": "main"})

                assert isinstance(result, MetricsResult)
                assert result.content_created["type"] == "code"
                assert result.content_created["quantity"] == 120
                assert result.components_modified == 6
                assert result.complexity == "substantial"
                assert result.is_substantial() is True


class TestDiscoveryAndMetricsTogether:
    """Test triad discovery and metrics working together."""

    def test_workflow_enforcement_scenario(self, tmp_path):
        """Test complete workflow enforcement scenario.

        Simulates:
        1. Discover available triads
        2. Check if implementation triad exists
        3. Calculate code metrics
        4. Determine if Garden Tending required
        """
        # Setup: Create mock triad structure
        agents_dir = tmp_path / ".claude" / "agents"
        agents_dir.mkdir(parents=True)

        # Create implementation triad
        impl_dir = agents_dir / "implementation"
        impl_dir.mkdir()
        (impl_dir / "design-bridge.md").write_text("# Design Bridge")
        (impl_dir / "senior-developer.md").write_text("# Senior Developer")
        (impl_dir / "test-engineer.md").write_text("# Test Engineer")

        # Create garden-tending triad
        gt_dir = agents_dir / "garden-tending"
        gt_dir.mkdir()
        (gt_dir / "cultivator.md").write_text("# Cultivator")
        (gt_dir / "pruner.md").write_text("# Pruner")

        # Step 1: Discover triads
        discovery = TriadDiscovery(base_path=str(agents_dir))
        triads = discovery.discover_triads()

        assert len(triads) == 2
        assert discovery.triad_exists("implementation")
        assert discovery.triad_exists("garden-tending")

        # Step 2: Get implementation triad details
        impl_triad = discovery.get_triad("implementation")
        assert impl_triad is not None
        assert impl_triad.agent_count == 3

        # Step 3: Calculate code metrics (mocked)
        metrics_provider = get_metrics_provider("code")

        with patch.object(metrics_provider, '_count_loc_changes', return_value=(150, 60)):
            with patch.object(metrics_provider, '_count_files_changed', return_value=8):
                metrics = metrics_provider.calculate_metrics({})

                # Step 4: Determine if Garden Tending required
                assert metrics.is_substantial() is True

                # Garden Tending triad is available
                gt_triad = discovery.get_triad("garden-tending")
                assert gt_triad is not None

                # Workflow enforcement would require Garden Tending before deployment

    def test_domain_agnostic_extensibility(self):
        """Test that the system is extensible to non-code domains."""
        from triads.workflow_enforcement.metrics import MetricsProvider, MetricsRegistry

        # Create custom document metrics provider
        class DocumentMetricsProvider(MetricsProvider):
            @property
            def domain(self):
                return "document"

            def calculate_metrics(self, context):
                from triads.workflow_enforcement.metrics import MetricsResult

                # Simulate document analysis
                pages = context.get("pages_written", 0)
                sections = context.get("sections_modified", 0)

                if pages > 10 or sections > 5:
                    complexity = "substantial"
                elif pages > 3 or sections > 2:
                    complexity = "moderate"
                else:
                    complexity = "minimal"

                return MetricsResult(
                    content_created={"type": "document", "quantity": pages, "units": "pages"},
                    components_modified=sections,
                    complexity=complexity,
                    raw_data=context
                )

        # Register custom provider
        registry = MetricsRegistry()
        registry.register(DocumentMetricsProvider())

        # Use custom provider
        doc_provider = registry.get_provider("document")
        assert doc_provider is not None

        result = doc_provider.calculate_metrics({
            "pages_written": 12,
            "sections_modified": 4
        })

        assert result.content_created["type"] == "document"
        assert result.content_created["quantity"] == 12
        assert result.complexity == "substantial"
        assert result.is_substantial() is True


class TestRealWorldScenarios:
    """Test real-world workflow scenarios."""

    def test_small_refactor_scenario(self):
        """Test scenario: Small refactor (should NOT require Garden Tending)."""
        provider = get_metrics_provider("code")

        # Simulate small refactor: 25 lines, 2 files
        with patch.object(provider, '_count_loc_changes', return_value=(15, 10)):
            with patch.object(provider, '_count_files_changed', return_value=2):
                result = provider.calculate_metrics({})

                assert result.complexity == "minimal"
                assert result.is_substantial() is False

                # Garden Tending would be OPTIONAL (not required)

    def test_major_feature_scenario(self):
        """Test scenario: Major feature (SHOULD require Garden Tending)."""
        provider = get_metrics_provider("code")

        # Simulate major feature: 250 lines, 12 files
        with patch.object(provider, '_count_loc_changes', return_value=(200, 50)):
            with patch.object(provider, '_count_files_changed', return_value=12):
                result = provider.calculate_metrics({})

                assert result.complexity == "substantial"
                assert result.is_substantial() is True

                # Garden Tending would be REQUIRED before deployment

    def test_medium_change_scenario(self):
        """Test scenario: Medium change (SHOULD require Garden Tending)."""
        provider = get_metrics_provider("code")

        # Simulate medium change: 45 lines, 3 files
        with patch.object(provider, '_count_loc_changes', return_value=(30, 15)):
            with patch.object(provider, '_count_files_changed', return_value=3):
                result = provider.calculate_metrics({})

                assert result.complexity == "moderate"
                assert result.is_substantial() is True

                # Garden Tending would be RECOMMENDED
