"""Tests for convenience functions - CLI command wrappers."""
import json
import pytest
from triads.km import graph_access


@pytest.fixture
def temp_graphs_dir(tmp_path):
    """Create temporary graphs directory."""
    graphs_dir = tmp_path / ".claude" / "graphs"
    graphs_dir.mkdir(parents=True)
    return graphs_dir


@pytest.fixture
def sample_graphs(temp_graphs_dir):
    """Create sample graph files."""
    design_graph = {
        "nodes": [
            {
                "id": "oauth_decision",
                "label": "OAuth2 Authentication",
                "type": "Decision",
                "description": "Use OAuth2 for authentication",
                "confidence": 0.95,
            }
        ],
        "links": [],
    }

    impl_graph = {
        "nodes": [
            {
                "id": "auth_module",
                "label": "Auth Module",
                "type": "Entity",
                "description": "Authentication implementation",
                "confidence": 0.88,
            }
        ],
        "links": [],
    }

    (temp_graphs_dir / "design_graph.json").write_text(json.dumps(design_graph))
    (temp_graphs_dir / "implementation_graph.json").write_text(json.dumps(impl_graph))

    return temp_graphs_dir


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singleton instances between tests."""
    graph_access._loader = None
    graph_access._searcher = None
    yield
    graph_access._loader = None
    graph_access._searcher = None


@pytest.fixture
def mock_loader(temp_graphs_dir, sample_graphs, monkeypatch):
    """Monkeypatch GraphLoader to use temp directory."""
    original_init = graph_access.GraphLoader.__init__

    def patched_init(self, graphs_dir=None):
        original_init(self, graphs_dir=temp_graphs_dir)

    monkeypatch.setattr(graph_access.GraphLoader, "__init__", patched_init)
    return temp_graphs_dir


def test_get_status_all_graphs(mock_loader):
    """Verify works without triad parameter."""
    output = graph_access.get_status()

    # Should include both graphs
    assert "# Knowledge Graph Status" in output
    assert "design" in output
    assert "implementation" in output


def test_get_status_specific_triad(mock_loader):
    """Verify works with triad parameter."""
    output = graph_access.get_status(triad="design")

    # Should only include design graph
    assert "# Knowledge Graph Status" in output
    assert "design" in output
    # Should include type breakdown for single triad
    assert "## Node Type Breakdown" in output


def test_get_status_invalid_triad(mock_loader):
    """Verify error message when triad not found."""
    output = graph_access.get_status(triad="nonexistent")

    assert "**Graph 'nonexistent' not found**" in output
    assert "Available graphs:" in output


def test_get_status_invalid_triad_name(mock_loader):
    """Verify error message for invalid triad name."""
    output = graph_access.get_status(triad="../../etc/passwd")

    assert "**Invalid triad name" in output
    assert "Available graphs:" in output


def test_get_status_empty_directory(temp_graphs_dir, monkeypatch):
    """Verify handles empty graphs directory."""
    # Create empty directory
    empty_dir = temp_graphs_dir / "empty"
    empty_dir.mkdir()

    # Reset singleton to force new instance creation
    import triads.km.graph_access.commands as commands_module
    monkeypatch.setattr(commands_module, "_loader", None)
    monkeypatch.setattr(commands_module, "_searcher", None)

    original_init = graph_access.GraphLoader.__init__

    def patched_init(self, graphs_dir=None):
        original_init(self, graphs_dir=empty_dir)

    monkeypatch.setattr(graph_access.GraphLoader, "__init__", patched_init)

    output = graph_access.get_status()

    assert "**No knowledge graphs found**" in output


def test_search_knowledge_basic(mock_loader):
    """Verify basic search works."""
    output = graph_access.search_knowledge("OAuth")

    assert "# Search Results: 'OAuth'" in output
    assert "OAuth2 Authentication" in output


def test_search_knowledge_with_filters(mock_loader):
    """Verify filters apply correctly."""
    output = graph_access.search_knowledge(
        "auth", triad="design", node_type="Decision", min_confidence=0.90
    )

    # Should find high-confidence Decision in design
    if "No results found" not in output:
        assert "design" in output
        assert "Decision" in output


def test_search_knowledge_no_results(mock_loader):
    """Verify handles no results gracefully."""
    output = graph_access.search_knowledge("nonexistent_term")

    assert "**No results found for: 'nonexistent_term'**" in output
    assert "**Suggestions:**" in output


def test_search_knowledge_invalid_triad(mock_loader):
    """Verify error message for invalid triad."""
    output = graph_access.search_knowledge("test", triad="nonexistent")

    assert "**Graph 'nonexistent' not found**" in output
    assert "Available graphs:" in output


def test_show_node_found(mock_loader):
    """Verify displays node details."""
    output = graph_access.show_node("oauth_decision", triad="design")

    assert "# OAuth2 Authentication" in output
    assert "**ID**: `oauth_decision`" in output
    assert "**Triad**: design" in output


def test_show_node_not_found(mock_loader):
    """Verify error message when node missing."""
    output = graph_access.show_node("nonexistent_node", triad="design")

    assert "**Node 'nonexistent_node' not found in 'design' graph**" in output


def test_show_node_not_found_without_triad(mock_loader):
    """Verify error message when node not in any triad."""
    output = graph_access.show_node("nonexistent_node")

    assert "**Node 'nonexistent_node' not found**" in output
    assert "Available triads:" in output
    assert "Use `/knowledge-search nonexistent_node` to search" in output


def test_show_node_ambiguous(temp_graphs_dir, monkeypatch):
    """Verify error message for ambiguous IDs."""
    # Create two graphs with same node ID
    graph1 = {
        "nodes": [{"id": "shared_node", "label": "Node 1", "type": "Concept"}],
        "links": [],
    }
    graph2 = {
        "nodes": [{"id": "shared_node", "label": "Node 2", "type": "Entity"}],
        "links": [],
    }

    (temp_graphs_dir / "design_graph.json").write_text(json.dumps(graph1))
    (temp_graphs_dir / "implementation_graph.json").write_text(json.dumps(graph2))

    # Reset singleton to force new instance creation
    import triads.km.graph_access.commands as commands_module
    monkeypatch.setattr(commands_module, "_loader", None)
    monkeypatch.setattr(commands_module, "_searcher", None)

    original_init = graph_access.GraphLoader.__init__

    def patched_init(self, graphs_dir=None):
        original_init(self, graphs_dir=temp_graphs_dir)

    monkeypatch.setattr(graph_access.GraphLoader, "__init__", patched_init)

    output = graph_access.show_node("shared_node")

    assert "**Ambiguous node ID 'shared_node'**" in output
    assert "Found in multiple triads:" in output
    assert "design" in output
    assert "implementation" in output


def test_show_node_invalid_triad_name(mock_loader):
    """Verify error for invalid triad name."""
    output = graph_access.show_node("test_node", triad="../../etc/passwd")

    assert "**Invalid triad name" in output


def test_get_help():
    """Verify returns help text."""
    output = graph_access.get_help()

    assert "# Knowledge Graph CLI Commands" in output
    assert "## Commands" in output
    assert "/knowledge-status" in output
    assert "/knowledge-search" in output
    assert "/knowledge-show" in output
    assert "/knowledge-help" in output
    assert "## Examples" in output
    assert "## Troubleshooting" in output


def test_singleton_loader_reused():
    """Verify _get_loader returns same instance."""
    loader1 = graph_access._get_loader()
    loader2 = graph_access._get_loader()

    assert loader1 is loader2


def test_singleton_searcher_reused():
    """Verify _get_searcher returns same instance."""
    searcher1 = graph_access._get_searcher()
    searcher2 = graph_access._get_searcher()

    assert searcher1 is searcher2


def test_get_status_caches_across_calls(mock_loader):
    """Verify subsequent calls use cached graphs."""
    # First call
    output1 = graph_access.get_status()

    # Second call - should use cached loader
    output2 = graph_access.get_status()

    # Outputs should be identical
    assert output1 == output2


def test_search_knowledge_uses_cached_loader(mock_loader):
    """Verify search uses cached loader instance."""
    # Trigger loader creation
    graph_access.get_status()

    # Search should use same loader
    output = graph_access.search_knowledge("OAuth")

    assert "# Search Results" in output


def test_show_node_uses_cached_loader(mock_loader):
    """Verify show_node uses cached loader instance."""
    # Trigger loader creation
    graph_access.get_status()

    # Show should use same loader
    output = graph_access.show_node("oauth_decision", triad="design")

    assert "# OAuth2 Authentication" in output


def test_get_status_formats_correctly(mock_loader):
    """Verify output has proper markdown formatting."""
    output = graph_access.get_status()

    # Check markdown elements
    assert output.startswith("# ")
    assert "**Graphs**:" in output
    assert "| Triad |" in output
    assert "|-------|" in output


def test_search_knowledge_formats_correctly(mock_loader):
    """Verify search output has proper markdown formatting."""
    output = graph_access.search_knowledge("OAuth")

    assert output.startswith("# ")
    assert "## " in output  # Triad sections
    assert "###" in output  # Node headers


def test_show_node_formats_correctly(mock_loader):
    """Verify show output has proper markdown formatting."""
    output = graph_access.show_node("oauth_decision", triad="design")

    assert output.startswith("# ")
    assert "## Attributes" in output
    assert "**ID**:" in output
    assert "**Type**:" in output


def test_get_help_formats_correctly():
    """Verify help output has proper markdown formatting."""
    output = graph_access.get_help()

    assert output.startswith("# ")
    assert "## Commands" in output
    assert "### " in output  # Command headers
    assert "```python" in output  # Code blocks
