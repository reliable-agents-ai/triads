"""Tests for GraphLoader class - lazy loading and caching."""
import json
import pytest
from pathlib import Path
from triads.km.graph_access import (
    GraphLoader,
    InvalidTriadNameError,
    AmbiguousNodeError,
)


@pytest.fixture
def temp_graphs_dir(tmp_path):
    """Create temporary graphs directory with test data."""
    graphs_dir = tmp_path / ".claude" / "graphs"
    graphs_dir.mkdir(parents=True)
    return graphs_dir


@pytest.fixture
def valid_graph_data():
    """Standard valid graph data for testing."""
    return {
        "directed": False,
        "multigraph": False,
        "graph": {},
        "nodes": [
            {
                "id": "test_node_1",
                "label": "Test Node 1",
                "type": "Concept",
                "description": "A test node for testing",
                "confidence": 0.95,
                "evidence": "test:1",
            },
            {
                "id": "test_node_2",
                "label": "Test Node 2",
                "type": "Entity",
                "description": "Another test node",
                "confidence": 0.88,
                "evidence": "test:2",
            },
        ],
        "links": [
            {
                "source": "test_node_1",
                "target": "test_node_2",
                "key": "relates_to",
            }
        ],
    }


@pytest.fixture
def create_test_graph(temp_graphs_dir):
    """Factory fixture to create test graph files."""

    def _create(triad_name, graph_data):
        graph_file = temp_graphs_dir / f"{triad_name}_graph.json"
        graph_file.write_text(json.dumps(graph_data, indent=2))
        return graph_file

    return _create


def test_init(temp_graphs_dir):
    """Verify initialization sets up cache and paths."""
    loader = GraphLoader(graphs_dir=temp_graphs_dir)
    assert loader._cache == {}
    assert loader._graphs_dir == temp_graphs_dir


def test_list_triads(temp_graphs_dir, create_test_graph, valid_graph_data):
    """Verify it finds all *_graph.json files."""
    # Create multiple graphs
    create_test_graph("design", valid_graph_data)
    create_test_graph("implementation", valid_graph_data)
    create_test_graph("deployment", valid_graph_data)

    loader = GraphLoader(graphs_dir=temp_graphs_dir)
    triads = loader.list_triads()

    assert len(triads) == 3
    assert triads == ["deployment", "design", "implementation"]  # Sorted


def test_list_triads_empty(temp_graphs_dir):
    """Verify handles missing graphs directory."""
    # Use non-existent directory
    missing_dir = temp_graphs_dir / "nonexistent"
    loader = GraphLoader(graphs_dir=missing_dir)

    triads = loader.list_triads()
    assert triads == []


def test_list_triads_filters_invalid_names(temp_graphs_dir, create_test_graph, valid_graph_data):
    """Verify only valid triad names are returned."""
    # Create graphs with valid and invalid names
    create_test_graph("valid-name", valid_graph_data)
    create_test_graph("also_valid", valid_graph_data)

    # Create files with invalid patterns (should be filtered)
    (temp_graphs_dir / "../etc/passwd_graph.json").parent.mkdir(exist_ok=True)
    (temp_graphs_dir / "invalid..name_graph.json").write_text("{}")

    loader = GraphLoader(graphs_dir=temp_graphs_dir)
    triads = loader.list_triads()

    # Should only return valid names
    assert "valid-name" in triads
    assert "also_valid" in triads
    assert "invalid..name" not in triads


def test_load_graph_success(temp_graphs_dir, create_test_graph, valid_graph_data):
    """Verify loads valid graph."""
    create_test_graph("test", valid_graph_data)

    loader = GraphLoader(graphs_dir=temp_graphs_dir)
    graph = loader.load_graph("test")

    assert graph is not None
    assert len(graph["nodes"]) == 2
    assert graph["nodes"][0]["id"] == "test_node_1"


def test_load_graph_caching(temp_graphs_dir, create_test_graph, valid_graph_data):
    """Verify second load uses cache (doesn't re-read file)."""
    graph_file = create_test_graph("test", valid_graph_data)

    loader = GraphLoader(graphs_dir=temp_graphs_dir)

    # First load - reads from file
    graph1 = loader.load_graph("test")
    assert graph1 is not None

    # Delete the file
    graph_file.unlink()

    # Second load - should use cache, not fail
    graph2 = loader.load_graph("test")
    assert graph2 is not None
    assert graph2 is graph1  # Same object from cache


def test_load_graph_not_found(temp_graphs_dir):
    """Verify returns None for missing graph."""
    loader = GraphLoader(graphs_dir=temp_graphs_dir)
    graph = loader.load_graph("nonexistent")

    assert graph is None


def test_load_graph_invalid_json(temp_graphs_dir):
    """Verify handles corrupted JSON gracefully."""
    # Create file with invalid JSON
    bad_file = temp_graphs_dir / "bad_graph.json"
    bad_file.write_text("{ this is not valid json }")

    loader = GraphLoader(graphs_dir=temp_graphs_dir)
    graph = loader.load_graph("bad")

    assert graph is None


def test_load_graph_non_dict_json(temp_graphs_dir):
    """Verify handles JSON that isn't a dict."""
    # Create file with valid JSON but not a dict
    bad_file = temp_graphs_dir / "array_graph.json"
    bad_file.write_text("[1, 2, 3]")

    loader = GraphLoader(graphs_dir=temp_graphs_dir)
    graph = loader.load_graph("array")

    assert graph is None


def test_load_graph_security_path_traversal(temp_graphs_dir):
    """Verify blocks ../ in triad names."""
    loader = GraphLoader(graphs_dir=temp_graphs_dir)

    with pytest.raises(InvalidTriadNameError) as exc_info:
        loader.load_graph("../../etc/passwd")

    assert "../../etc/passwd" in str(exc_info.value)
    assert "invalid" in str(exc_info.value).lower()


def test_load_graph_security_absolute_path(temp_graphs_dir):
    """Verify blocks absolute paths."""
    loader = GraphLoader(graphs_dir=temp_graphs_dir)

    with pytest.raises(InvalidTriadNameError):
        loader.load_graph("/etc/passwd")


def test_load_graph_security_special_characters(temp_graphs_dir):
    """Verify blocks special characters."""
    loader = GraphLoader(graphs_dir=temp_graphs_dir)

    # Various injection attempts
    dangerous_names = [
        "test;rm -rf /",
        "test|cat /etc/passwd",
        "test`whoami`",
        "test$USER",
        "test\\..\\..\\etc",
    ]

    for name in dangerous_names:
        with pytest.raises(InvalidTriadNameError):
            loader.load_graph(name)


def test_load_all_graphs(temp_graphs_dir, create_test_graph, valid_graph_data):
    """Verify loads multiple graphs."""
    create_test_graph("design", valid_graph_data)
    create_test_graph("implementation", valid_graph_data)

    loader = GraphLoader(graphs_dir=temp_graphs_dir)
    all_graphs = loader.load_all_graphs()

    assert len(all_graphs) == 2
    assert "design" in all_graphs
    assert "implementation" in all_graphs
    assert len(all_graphs["design"]["nodes"]) == 2


def test_load_all_graphs_skips_invalid(temp_graphs_dir, create_test_graph, valid_graph_data):
    """Verify load_all_graphs skips corrupted files."""
    # Create valid graph
    create_test_graph("good", valid_graph_data)

    # Create invalid graph
    (temp_graphs_dir / "bad_graph.json").write_text("invalid json")

    loader = GraphLoader(graphs_dir=temp_graphs_dir)
    all_graphs = loader.load_all_graphs()

    # Should only load the valid one
    assert len(all_graphs) == 1
    assert "good" in all_graphs


def test_get_node_found(temp_graphs_dir, create_test_graph, valid_graph_data):
    """Verify finds node by ID."""
    create_test_graph("test", valid_graph_data)

    loader = GraphLoader(graphs_dir=temp_graphs_dir)
    result = loader.get_node("test_node_1", triad="test")

    assert result is not None
    node, triad = result
    assert node["id"] == "test_node_1"
    assert node["label"] == "Test Node 1"
    assert triad == "test"


def test_get_node_not_found(temp_graphs_dir, create_test_graph, valid_graph_data):
    """Verify returns None for missing node."""
    create_test_graph("test", valid_graph_data)

    loader = GraphLoader(graphs_dir=temp_graphs_dir)
    result = loader.get_node("nonexistent_node", triad="test")

    assert result is None


def test_get_node_without_triad(temp_graphs_dir, create_test_graph):
    """Verify searches all triads when triad not specified."""
    # Create two graphs with different node IDs
    graph1 = {
        "nodes": [{"id": "unique_node_1", "label": "Node in Design", "type": "Concept"}],
        "links": [],
    }
    graph2 = {
        "nodes": [{"id": "unique_node_2", "label": "Node in Implementation", "type": "Entity"}],
        "links": [],
    }

    create_test_graph("design", graph1)
    create_test_graph("implementation", graph2)

    loader = GraphLoader(graphs_dir=temp_graphs_dir)

    # Should find unique node without specifying triad
    result = loader.get_node("unique_node_1")

    assert result is not None
    node, triad = result
    assert node["id"] == "unique_node_1"
    assert triad == "design"


def test_get_node_ambiguous(temp_graphs_dir, create_test_graph):
    """Verify raises AmbiguousNodeError for duplicate IDs."""
    # Create two graphs with same node ID
    graph1 = {
        "nodes": [{"id": "shared_node", "label": "Node in Design", "type": "Concept"}],
        "links": [],
    }
    graph2 = {
        "nodes": [{"id": "shared_node", "label": "Node in Implementation", "type": "Entity"}],
        "links": [],
    }

    create_test_graph("design", graph1)
    create_test_graph("implementation", graph2)

    loader = GraphLoader(graphs_dir=temp_graphs_dir)

    with pytest.raises(AmbiguousNodeError) as exc_info:
        loader.get_node("shared_node")  # No triad specified

    assert "shared_node" in str(exc_info.value)
    assert "design" in str(exc_info.value)
    assert "implementation" in str(exc_info.value)
    assert exc_info.value.node_id == "shared_node"
    assert set(exc_info.value.triads) == {"design", "implementation"}


def test_get_node_with_triad_filter(temp_graphs_dir, create_test_graph):
    """Verify triad filter disambiguates duplicate IDs."""
    # Create two graphs with same node ID
    graph1 = {
        "nodes": [{"id": "shared_node", "label": "Node in Design", "type": "Concept"}],
        "links": [],
    }
    graph2 = {
        "nodes": [{"id": "shared_node", "label": "Node in Implementation", "type": "Entity"}],
        "links": [],
    }

    create_test_graph("design", graph1)
    create_test_graph("implementation", graph2)

    loader = GraphLoader(graphs_dir=temp_graphs_dir)

    # Specify triad - should work without ambiguity error
    result = loader.get_node("shared_node", triad="design")

    assert result is not None
    node, triad = result
    assert node["label"] == "Node in Design"
    assert triad == "design"


def test_is_valid_triad_name():
    """Verify triad name validation."""
    loader = GraphLoader()

    # Valid names
    assert loader._is_valid_triad_name("design")
    assert loader._is_valid_triad_name("idea-validation")
    assert loader._is_valid_triad_name("test_123")
    assert loader._is_valid_triad_name("UPPERCASE")

    # Invalid names
    assert not loader._is_valid_triad_name("../etc/passwd")
    assert not loader._is_valid_triad_name("/absolute/path")
    assert not loader._is_valid_triad_name("has spaces")
    assert not loader._is_valid_triad_name("has.dot")
    assert not loader._is_valid_triad_name("has;semicolon")
    assert not loader._is_valid_triad_name("")


def test_load_graph_unicode_handling(temp_graphs_dir):
    """Verify handles Unicode content correctly."""
    unicode_graph = {
        "nodes": [
            {
                "id": "unicode_node",
                "label": "Unicode Test: 你好世界 🎯",
                "description": "Description with emoji 🚀 and Chinese 中文",
                "type": "Concept",
            }
        ],
        "links": [],
    }

    graph_file = temp_graphs_dir / "unicode_graph.json"
    graph_file.write_text(json.dumps(unicode_graph, ensure_ascii=False), encoding="utf-8")

    loader = GraphLoader(graphs_dir=temp_graphs_dir)
    graph = loader.load_graph("unicode")

    assert graph is not None
    assert graph["nodes"][0]["label"] == "Unicode Test: 你好世界 🎯"


def test_load_graph_missing_nodes_field(temp_graphs_dir):
    """Verify handles graphs without 'nodes' field."""
    minimal_graph = {"graph": {}, "links": []}

    graph_file = temp_graphs_dir / "minimal_graph.json"
    graph_file.write_text(json.dumps(minimal_graph))

    loader = GraphLoader(graphs_dir=temp_graphs_dir)
    graph = loader.load_graph("minimal")

    # Should load successfully (nodes field is optional in structure)
    assert graph is not None
    assert graph.get("nodes", []) == []
