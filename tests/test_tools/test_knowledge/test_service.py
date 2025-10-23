"""Tests for knowledge tools service layer."""

import pytest

from triads.tools.knowledge.service import KnowledgeService, QueryResult, StatusResult
from triads.tools.knowledge.repository import GraphNotFoundError


class TestKnowledgeServiceQuery:
    """Tests for KnowledgeService.query_graph()."""

    def test_query_graph_success(self, seeded_repo):
        """Query returns results from specified graph."""
        service = KnowledgeService(seeded_repo)

        result = service.query_graph("design", "OAuth", min_confidence=0.0)

        assert isinstance(result, QueryResult)
        assert result.total == 1
        assert len(result.nodes) == 1
        assert result.nodes[0].id == "oauth_decision"

    def test_query_graph_with_confidence_filter(self, seeded_repo):
        """Query filters by minimum confidence."""
        service = KnowledgeService(seeded_repo)

        # Low confidence threshold - gets all 3 nodes
        result_low = service.query_graph("design", "", min_confidence=0.0)
        assert result_low.total == 3

        # High confidence threshold - only 2 nodes
        result_high = service.query_graph("design", "", min_confidence=0.85)
        assert result_high.total == 2

    def test_query_graph_missing_triad_raises(self, seeded_repo):
        """Query raises GraphNotFoundError for missing triad."""
        service = KnowledgeService(seeded_repo)

        with pytest.raises(GraphNotFoundError) as exc_info:
            service.query_graph("nonexistent", "test", min_confidence=0.0)

        assert "nonexistent" in str(exc_info.value)

    def test_query_graph_no_results(self, seeded_repo):
        """Query returns empty result when no matches."""
        service = KnowledgeService(seeded_repo)

        result = service.query_graph("design", "xyz_nonexistent", min_confidence=0.0)

        assert result.total == 0
        assert result.nodes == []


class TestKnowledgeServiceStatus:
    """Tests for KnowledgeService.get_graph_status()."""

    def test_get_status_all_graphs(self, seeded_repo):
        """Get status returns all graphs when triad not specified."""
        service = KnowledgeService(seeded_repo)

        result = service.get_graph_status(triad=None)

        assert isinstance(result, StatusResult)
        assert len(result.graphs) == 2
        triad_names = [g.triad for g in result.graphs]
        assert "design" in triad_names
        assert "implementation" in triad_names

    def test_get_status_single_graph(self, seeded_repo):
        """Get status returns single graph when triad specified."""
        service = KnowledgeService(seeded_repo)

        result = service.get_graph_status(triad="design")

        assert isinstance(result, StatusResult)
        assert len(result.graphs) == 1
        assert result.graphs[0].triad == "design"

    def test_get_status_missing_graph_raises(self, seeded_repo):
        """Get status raises GraphNotFoundError for missing graph."""
        service = KnowledgeService(seeded_repo)

        with pytest.raises(GraphNotFoundError):
            service.get_graph_status(triad="nonexistent")


class TestKnowledgeServiceShowNode:
    """Tests for KnowledgeService.show_node()."""

    def test_show_node_found_in_specified_triad(self, seeded_repo):
        """Show node returns node from specified triad."""
        service = KnowledgeService(seeded_repo)

        node = service.show_node("oauth_decision", triad="design")

        assert node is not None
        assert node.id == "oauth_decision"
        assert node.label == "OAuth2 Authentication Decision"

    def test_show_node_not_found_returns_none(self, seeded_repo):
        """Show node returns None when node doesn't exist."""
        service = KnowledgeService(seeded_repo)

        node = service.show_node("nonexistent", triad="design")

        assert node is None

    def test_show_node_search_all_triads(self, seeded_repo):
        """Show node searches all triads when triad not specified."""
        service = KnowledgeService(seeded_repo)

        node = service.show_node("oauth_impl", triad=None)

        assert node is not None
        assert node.id == "oauth_impl"


class TestKnowledgeServiceListTriads:
    """Tests for KnowledgeService.list_triads()."""

    def test_list_triads_returns_names_and_counts(self, seeded_repo):
        """List triads returns names with node counts."""
        service = KnowledgeService(seeded_repo)

        triads = service.list_triads()

        assert len(triads) == 2
        # Check structure - should be list of dicts
        assert all("name" in t and "node_count" in t for t in triads)
        # Check specific values
        design = next(t for t in triads if t["name"] == "design")
        assert design["node_count"] == 3

    def test_list_triads_empty_repo(self, empty_repo):
        """List triads returns empty list for empty repo."""
        service = KnowledgeService(empty_repo)

        triads = service.list_triads()

        assert triads == []
