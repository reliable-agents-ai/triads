"""Tests for knowledge tools domain layer."""

import pytest

from triads.tools.knowledge.domain import Node, Edge, KnowledgeGraph
from tests.test_tools.test_knowledge.test_data import (
    get_sample_design_graph,
    get_invalid_graph_missing_node,
)


class TestNode:
    """Tests for Node domain model."""

    def test_node_creation_with_required_fields(self):
        """Node can be created with only required fields."""
        node = Node(
            id="test_node",
            label="Test Node",
            type="concept",
            confidence=0.9
        )

        assert node.id == "test_node"
        assert node.label == "Test Node"
        assert node.type == "concept"
        assert node.confidence == 0.9
        assert node.content is None
        assert node.evidence is None
        assert node.metadata is None

    def test_node_creation_with_all_fields(self):
        """Node can be created with all fields."""
        node = Node(
            id="test_node",
            label="Test Node",
            type="decision",
            confidence=1.0,
            content="Test content",
            evidence=["evidence1", "evidence2"],
            metadata={"author": "test"}
        )

        assert node.content == "Test content"
        assert node.evidence == ["evidence1", "evidence2"]
        assert node.metadata == {"author": "test"}


class TestEdge:
    """Tests for Edge domain model."""

    def test_edge_requires_source_and_target(self):
        """Edge requires source, target, and relationship."""
        edge = Edge(
            source="node1",
            target="node2",
            relationship="depends_on"
        )

        assert edge.source == "node1"
        assert edge.target == "node2"
        assert edge.relationship == "depends_on"


class TestKnowledgeGraph:
    """Tests for KnowledgeGraph domain model."""

    def test_knowledge_graph_search_by_label(self):
        """Search finds nodes by label substring (case-insensitive)."""
        graph = get_sample_design_graph()

        results = graph.search("OAuth", min_confidence=0.0)

        assert len(results) == 1  # Only oauth_decision has "OAuth" in label
        assert results[0].id == "oauth_decision"
        assert results[0].label == "OAuth2 Authentication Decision"

    def test_knowledge_graph_search_by_content(self):
        """Search finds nodes by content substring."""
        graph = get_sample_design_graph()

        results = graph.search("RESTful", min_confidence=0.0)

        assert len(results) == 1
        assert results[0].id == "api_design"

    def test_knowledge_graph_search_by_confidence(self):
        """Search filters nodes by minimum confidence."""
        graph = get_sample_design_graph()

        # All nodes
        all_results = graph.search("", min_confidence=0.0)
        assert len(all_results) == 3

        # High confidence only
        high_conf_results = graph.search("", min_confidence=0.85)
        assert len(high_conf_results) == 2

        ids = [n.id for n in high_conf_results]
        assert "oauth_decision" in ids
        assert "api_design" in ids
        assert "low_confidence_finding" not in ids

    def test_knowledge_graph_search_empty_query_returns_all(self):
        """Empty query returns all nodes matching confidence filter."""
        graph = get_sample_design_graph()

        results = graph.search("", min_confidence=0.0)

        assert len(results) == 3

    def test_knowledge_graph_search_no_matches(self):
        """Search returns empty list when no matches found."""
        graph = get_sample_design_graph()

        results = graph.search("nonexistent", min_confidence=0.0)

        assert results == []

    def test_knowledge_graph_validate_valid_structure(self):
        """Validation passes for valid graph structure."""
        graph = get_sample_design_graph()

        is_valid, error = graph.validate()

        assert is_valid is True
        assert error is None

    def test_knowledge_graph_validate_invalid_edge_references(self):
        """Validation fails when edge references non-existent node."""
        graph = get_invalid_graph_missing_node()

        is_valid, error = graph.validate()

        assert is_valid is False
        assert error is not None
        assert "missing_node" in error
        assert "does not exist" in error.lower()

    def test_knowledge_graph_validate_empty_graph(self):
        """Empty graph with no edges is valid."""
        graph = KnowledgeGraph(triad="empty", nodes=[], edges=[])

        is_valid, error = graph.validate()

        assert is_valid is True
        assert error is None
