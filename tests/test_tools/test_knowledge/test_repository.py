"""Tests for knowledge tools repository layer."""

import pytest

from triads.tools.knowledge.repository import (
    InMemoryGraphRepository,
    GraphNotFoundError,
)
from triads.tools.knowledge.domain import Node, Edge, KnowledgeGraph


class TestInMemoryGraphRepository:
    """Tests for InMemoryGraphRepository."""

    def test_in_memory_repo_get_existing_graph(self, seeded_repo):
        """Get returns graph when it exists."""
        graph = seeded_repo.get("design")

        assert graph.triad == "design"
        assert len(graph.nodes) == 3
        assert any(n.id == "oauth_decision" for n in graph.nodes)

    def test_in_memory_repo_get_missing_graph_raises(self, seeded_repo):
        """Get raises GraphNotFoundError when graph doesn't exist."""
        with pytest.raises(GraphNotFoundError) as exc_info:
            seeded_repo.get("nonexistent")

        assert "nonexistent" in str(exc_info.value)
        assert "design" in str(exc_info.value)  # Shows available graphs

    def test_in_memory_repo_list_all(self, seeded_repo):
        """List all returns all graphs."""
        graphs = seeded_repo.list_all()

        assert len(graphs) == 2
        triad_names = [g.triad for g in graphs]
        assert "design" in triad_names
        assert "implementation" in triad_names

    def test_in_memory_repo_list_all_empty(self, empty_repo):
        """List all returns empty list when no graphs."""
        graphs = empty_repo.list_all()

        assert graphs == []

    def test_in_memory_repo_get_from_empty_raises(self, empty_repo):
        """Get from empty repo raises with appropriate message."""
        with pytest.raises(GraphNotFoundError) as exc_info:
            empty_repo.get("any_graph")

        assert "any_graph" in str(exc_info.value)


class TestFileSystemGraphRepository:
    """Tests for FileSystemGraphRepository.

    Note: FileSystemGraphRepository wraps existing km.graph_access,
    so we mainly test the transformation logic.
    """

    def test_filesystem_repo_loads_from_existing_km_graph_access(self, tmp_path):
        """FileSystemGraphRepository can load from real graph files."""
        # This test verifies integration with existing km.graph_access
        # Implementation will use GraphLoader from triads.km.graph_access
        pytest.skip("Will implement after repository implementation")
