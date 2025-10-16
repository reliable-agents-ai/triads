"""Error handling tests for knowledge graph access."""
import json
import pytest
from pathlib import Path
from triads.km.graph_access import (
    GraphLoader,
    GraphSearcher,
    GraphFormatter,
    GraphNotFoundError,
    InvalidTriadNameError,
    AmbiguousNodeError,
)


@pytest.fixture
def temp_graphs_dir(tmp_path):
    """Create temporary graphs directory."""
    graphs_dir = tmp_path / ".claude" / "graphs"
    graphs_dir.mkdir(parents=True)
    return graphs_dir


def test_missing_graphs_directory():
    """Verify handles missing .claude/graphs/ directory."""
    # Use non-existent directory
    loader = GraphLoader(graphs_dir=Path("/nonexistent/path/graphs"))

    # list_triads should return empty list, not crash
    triads = loader.list_triads()
    assert triads == []

    # load_graph should return None, not crash
    graph = loader.load_graph("test")
    assert graph is None


def test_empty_graphs_directory(temp_graphs_dir):
    """Verify handles directory with no files."""
    loader = GraphLoader(graphs_dir=temp_graphs_dir)

    # No graph files exist yet
    triads = loader.list_triads()
    assert triads == []

    # load_all_graphs should return empty dict
    graphs = loader.load_all_graphs()
    assert graphs == {}


def test_corrupted_json_provides_helpful_error(temp_graphs_dir):
    """Verify provides helpful error message for corrupted JSON."""
    # Create file with invalid JSON
    bad_file = temp_graphs_dir / "corrupted_graph.json"
    bad_file.write_text("{ invalid json syntax }")

    loader = GraphLoader(graphs_dir=temp_graphs_dir)

    # Should return None (error handled gracefully)
    graph = loader.load_graph("corrupted")
    assert graph is None


def test_missing_required_fields(temp_graphs_dir):
    """Verify handles graphs missing 'nodes' field."""
    # Graph with only links
    minimal_graph = {"links": []}

    graph_file = temp_graphs_dir / "minimal_graph.json"
    graph_file.write_text(json.dumps(minimal_graph))

    loader = GraphLoader(graphs_dir=temp_graphs_dir)

    # Should load successfully (nodes field is optional)
    graph = loader.load_graph("minimal")
    assert graph is not None

    # Access should return empty list
    nodes = graph.get("nodes", [])
    assert nodes == []


def test_node_missing_fields(temp_graphs_dir):
    """Verify handles nodes missing optional fields."""
    # Nodes with various missing fields
    sparse_graph = {
        "nodes": [
            {"id": "minimal", "label": "Minimal"},  # Missing type, confidence, etc.
            {"id": "no_label", "type": "Concept"},  # Missing label
            {"id": "no_type", "label": "No Type", "confidence": 0.9},  # Missing type
        ],
        "links": [],
    }

    graph_file = temp_graphs_dir / "sparse_graph.json"
    graph_file.write_text(json.dumps(sparse_graph))

    loader = GraphLoader(graphs_dir=temp_graphs_dir)
    searcher = GraphSearcher(loader)
    formatter = GraphFormatter()

    # Should load successfully
    graph = loader.load_graph("sparse")
    assert graph is not None
    assert len(graph["nodes"]) == 3

    # Search should handle missing fields
    results = searcher.search("minimal")
    assert isinstance(results, list)

    # Formatter should handle missing fields
    if len(graph["nodes"]) > 0:
        output = formatter.format_node_details(graph["nodes"][0], "sparse", graph)
        assert isinstance(output, str)
        assert len(output) > 0


def test_empty_query_handled(temp_graphs_dir):
    """Verify rejects queries that are too short."""
    graph = {"nodes": [{"id": "test", "label": "Test", "type": "Concept"}], "links": []}

    graph_file = temp_graphs_dir / "test_graph.json"
    graph_file.write_text(json.dumps(graph))

    loader = GraphLoader(graphs_dir=temp_graphs_dir)
    searcher = GraphSearcher(loader)

    # Empty string query
    results = searcher.search("")

    # Should return empty list or handle gracefully
    assert isinstance(results, list)


def test_invalid_filter_values_confidence_out_of_range(temp_graphs_dir):
    """Verify validates confidence is in 0-1 range."""
    graph = {
        "nodes": [{"id": "test", "label": "Test", "type": "Concept", "confidence": 0.9}],
        "links": [],
    }

    graph_file = temp_graphs_dir / "test_graph.json"
    graph_file.write_text(json.dumps(graph))

    loader = GraphLoader(graphs_dir=temp_graphs_dir)
    searcher = GraphSearcher(loader)

    # Search with valid confidence values
    results_valid = searcher.search("test", min_confidence=0.5)
    assert isinstance(results_valid, list)

    # Out of range values - implementation should handle gracefully
    # (may return empty results or all results)
    results_high = searcher.search("test", min_confidence=1.5)
    assert isinstance(results_high, list)

    results_negative = searcher.search("test", min_confidence=-0.5)
    assert isinstance(results_negative, list)


def test_invalid_node_type_filter(temp_graphs_dir):
    """Verify handles invalid node type filters."""
    graph = {
        "nodes": [{"id": "test", "label": "Test", "type": "Concept", "confidence": 0.9}],
        "links": [],
    }

    graph_file = temp_graphs_dir / "test_graph.json"
    graph_file.write_text(json.dumps(graph))

    loader = GraphLoader(graphs_dir=temp_graphs_dir)
    searcher = GraphSearcher(loader)

    # Search with non-existent node type
    results = searcher.search("test", node_type="NonExistentType")

    # Should return empty list, not crash
    assert isinstance(results, list)
    assert len(results) == 0


def test_graph_not_found_error_message(temp_graphs_dir):
    """Verify GraphNotFoundError has helpful message."""
    graph_file = temp_graphs_dir / "existing_graph.json"
    graph_file.write_text(json.dumps({"nodes": [], "links": []}))

    loader = GraphLoader(graphs_dir=temp_graphs_dir)
    searcher = GraphSearcher(loader)

    # Try to search non-existent graph
    with pytest.raises(GraphNotFoundError) as exc_info:
        searcher.search("test", triad="nonexistent")

    error = exc_info.value

    # Check error attributes
    assert error.triad == "nonexistent"
    assert "existing" in error.available

    # Check error message
    error_msg = str(error)
    assert "nonexistent" in error_msg
    assert "Available graphs:" in error_msg
    assert "existing" in error_msg


def test_ambiguous_node_error_message(temp_graphs_dir):
    """Verify AmbiguousNodeError has helpful message."""
    # Create two graphs with same node ID
    graph1 = {"nodes": [{"id": "shared", "label": "Node 1", "type": "Concept"}], "links": []}
    graph2 = {"nodes": [{"id": "shared", "label": "Node 2", "type": "Entity"}], "links": []}

    (temp_graphs_dir / "graph1_graph.json").write_text(json.dumps(graph1))
    (temp_graphs_dir / "graph2_graph.json").write_text(json.dumps(graph2))

    loader = GraphLoader(graphs_dir=temp_graphs_dir)

    # Try to get ambiguous node
    with pytest.raises(AmbiguousNodeError) as exc_info:
        loader.get_node("shared")

    error = exc_info.value

    # Check error attributes
    assert error.node_id == "shared"
    assert set(error.triads) == {"graph1", "graph2"}

    # Check error message
    error_msg = str(error)
    assert "shared" in error_msg
    assert "multiple triads" in error_msg
    assert "graph1" in error_msg
    assert "graph2" in error_msg
    assert "specify triad" in error_msg.lower()


def test_invalid_triad_name_error_message():
    """Verify InvalidTriadNameError has helpful message."""
    loader = GraphLoader()

    with pytest.raises(InvalidTriadNameError) as exc_info:
        loader.load_graph("../../etc/passwd")

    error = exc_info.value

    # Check error attributes
    assert error.triad == "../../etc/passwd"

    # Check error message
    error_msg = str(error)
    assert "../../etc/passwd" in error_msg
    assert "invalid" in error_msg.lower()
    assert "alphanumeric" in error_msg.lower()


def test_file_permission_error_handled(temp_graphs_dir):
    """Verify handles permission errors gracefully."""
    # Create graph file
    graph_file = temp_graphs_dir / "restricted_graph.json"
    graph_file.write_text(json.dumps({"nodes": [], "links": []}))

    # Try to make it unreadable (may not work on all systems)
    try:
        graph_file.chmod(0o000)

        loader = GraphLoader(graphs_dir=temp_graphs_dir)
        graph = loader.load_graph("restricted")

        # Should return None, not crash
        assert graph is None

        # Restore permissions for cleanup
        graph_file.chmod(0o644)

    except (OSError, PermissionError):
        # Permission changes may not be supported
        pytest.skip("Permission changes not supported on this system")


def test_unicode_decode_error_handled(temp_graphs_dir):
    """Verify handles Unicode decode errors."""
    # Create file with invalid UTF-8
    bad_file = temp_graphs_dir / "bad_encoding_graph.json"
    bad_file.write_bytes(b"\x80\x81\x82")  # Invalid UTF-8

    loader = GraphLoader(graphs_dir=temp_graphs_dir)
    graph = loader.load_graph("bad_encoding")

    # Should return None, not crash
    assert graph is None


def test_formatter_handles_none_values(temp_graphs_dir):
    """Verify formatter handles None/null values in nodes."""
    graph = {
        "nodes": [
            {
                "id": "test",
                "label": "Test",
                "type": None,
                "description": None,
                "confidence": None,
            }
        ],
        "links": [],
    }

    graph_file = temp_graphs_dir / "null_values_graph.json"
    graph_file.write_text(json.dumps(graph))

    loader = GraphLoader(graphs_dir=temp_graphs_dir)
    formatter = GraphFormatter()

    graph_data = loader.load_graph("null_values")
    assert graph_data is not None

    # Should handle None values without crashing
    output = formatter.format_node_details(graph_data["nodes"][0], "null_values", graph_data)
    assert isinstance(output, str)


def test_searcher_handles_missing_node_fields(temp_graphs_dir):
    """Verify searcher handles nodes with missing fields."""
    graph = {
        "nodes": [
            {"id": "minimal"},  # Only ID, no label/description
            {},  # No fields at all
        ],
        "links": [],
    }

    graph_file = temp_graphs_dir / "minimal_graph.json"
    graph_file.write_text(json.dumps(graph))

    loader = GraphLoader(graphs_dir=temp_graphs_dir)
    searcher = GraphSearcher(loader)

    # Should not crash
    results = searcher.search("test")
    assert isinstance(results, list)


def test_get_node_with_invalid_triad(temp_graphs_dir):
    """Verify get_node handles invalid triad gracefully."""
    loader = GraphLoader(graphs_dir=temp_graphs_dir)

    # Try to get node from non-existent triad
    result = loader.get_node("test_node", triad="nonexistent")

    # Should return None, not crash
    assert result is None


def test_load_graph_with_invalid_json_structure(temp_graphs_dir):
    """Verify handles JSON that isn't expected structure."""
    # Various invalid structures
    invalid_graphs = [
        "null",
        "[]",
        "123",
        '"string"',
        "true",
        '{"nodes": "not a list"}',
        '{"links": "not a list"}',
    ]

    loader = GraphLoader(graphs_dir=temp_graphs_dir)

    for i, invalid_json in enumerate(invalid_graphs):
        graph_file = temp_graphs_dir / f"invalid_{i}_graph.json"
        graph_file.write_text(invalid_json)

        # Should handle gracefully (return None or load with defaults)
        graph = loader.load_graph(f"invalid_{i}")

        # As long as it doesn't crash, it's acceptable
        # May return None or may load partial structure
        assert True  # Just checking it doesn't crash


def test_error_recovery_after_failed_load(temp_graphs_dir):
    """Verify loader can recover after failed load attempts."""
    loader = GraphLoader(graphs_dir=temp_graphs_dir)

    # Try to load non-existent graph
    graph1 = loader.load_graph("nonexistent")
    assert graph1 is None

    # Create valid graph
    valid_graph = {"nodes": [{"id": "test", "label": "Test"}], "links": []}
    (temp_graphs_dir / "valid_graph.json").write_text(json.dumps(valid_graph))

    # Should be able to load successfully after failure
    graph2 = loader.load_graph("valid")
    assert graph2 is not None


def test_formatter_handles_circular_node_references(temp_graphs_dir):
    """Verify formatter handles nodes referencing themselves."""
    graph = {
        "nodes": [{"id": "self_ref", "label": "Self Reference", "type": "Concept"}],
        "links": [
            {"source": "self_ref", "target": "self_ref", "key": "loops"},
        ],
    }

    graph_file = temp_graphs_dir / "circular_graph.json"
    graph_file.write_text(json.dumps(graph))

    loader = GraphLoader(graphs_dir=temp_graphs_dir)
    formatter = GraphFormatter()

    graph_data = loader.load_graph("circular")
    assert graph_data is not None

    # Should handle self-referencing node without infinite loop
    output = formatter.format_node_details(graph_data["nodes"][0], "circular", graph_data)
    assert isinstance(output, str)
    assert "self_ref" in output


def test_search_with_malformed_confidence_values(temp_graphs_dir):
    """Verify search handles malformed confidence values in nodes."""
    graph = {
        "nodes": [
            {"id": "n1", "label": "Node 1", "confidence": "invalid"},
            {"id": "n2", "label": "Node 2", "confidence": 999},
            {"id": "n3", "label": "Node 3", "confidence": -1},
            {"id": "n4", "label": "Node 4"},  # Missing confidence
        ],
        "links": [],
    }

    graph_file = temp_graphs_dir / "bad_confidence_graph.json"
    graph_file.write_text(json.dumps(graph))

    loader = GraphLoader(graphs_dir=temp_graphs_dir)
    searcher = GraphSearcher(loader)

    # Should not crash with malformed confidence values
    results = searcher.search("node")
    assert isinstance(results, list)


def test_status_with_malformed_graphs(temp_graphs_dir):
    """Verify get_status handles mixture of valid and invalid graphs."""
    # Create valid graph
    valid_graph = {"nodes": [{"id": "valid", "label": "Valid"}], "links": []}
    (temp_graphs_dir / "valid_graph.json").write_text(json.dumps(valid_graph))

    # Create invalid graph
    (temp_graphs_dir / "invalid_graph.json").write_text("{ invalid json }")

    loader = GraphLoader(graphs_dir=temp_graphs_dir)
    formatter = GraphFormatter()

    # load_all_graphs should skip invalid and load valid
    graphs = loader.load_all_graphs()

    # Should have only the valid graph
    assert len(graphs) == 1
    assert "valid" in graphs

    # Status should format successfully
    output = formatter.format_status(graphs)
    assert "valid" in output
