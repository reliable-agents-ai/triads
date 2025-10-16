"""Integration tests for knowledge graph CLI commands."""
import json
import time
import pytest
from pathlib import Path
from triads.km.graph_access import GraphLoader, GraphSearcher, GraphFormatter


@pytest.fixture
def project_graphs_dir():
    """Use real project graphs directory."""
    return Path(".claude/graphs")


@pytest.fixture
def command_files_dir():
    """Path to command files."""
    return Path(".claude/commands")


def test_commands_exist(command_files_dir):
    """Verify all 4 .md files exist in .claude/commands/."""
    required_commands = [
        "knowledge-status.md",
        "knowledge-search.md",
        "knowledge-show.md",
        "knowledge-help.md",
    ]

    for cmd_file in required_commands:
        cmd_path = command_files_dir / cmd_file
        assert cmd_path.exists(), f"Command file {cmd_file} not found"
        assert cmd_path.is_file(), f"{cmd_file} is not a file"


def test_command_files_have_content(command_files_dir):
    """Verify each command file has proper content."""
    command_files = [
        "knowledge-status.md",
        "knowledge-search.md",
        "knowledge-show.md",
        "knowledge-help.md",
    ]

    for cmd_file in command_files:
        cmd_path = command_files_dir / cmd_file
        content = cmd_path.read_text()

        # Should have markdown header
        assert content.startswith("#"), f"{cmd_file} missing markdown header"

        # Should have substantial content (at least 500 chars)
        assert len(content) > 500, f"{cmd_file} has insufficient content"

        # Should mention relevant terms (help file is special - contains all commands)
        if "help" not in cmd_file:
            cmd_name = cmd_file.replace(".md", "").replace("-", " ")
            assert cmd_name.lower() in content.lower(), f"{cmd_file} doesn't mention {cmd_name}"


def test_command_files_have_valid_structure(command_files_dir):
    """Verify command files have proper structure."""
    command_files = [
        "knowledge-status.md",
        "knowledge-search.md",
        "knowledge-show.md",
        "knowledge-help.md",
    ]

    for cmd_file in command_files:
        cmd_path = command_files_dir / cmd_file
        content = cmd_path.read_text()

        # Should have ## Usage section (help file is special - has ## Commands instead)
        if "help" in cmd_file:
            assert "## Commands" in content, f"{cmd_file} missing Commands section"
        else:
            assert "## Usage" in content or "# Usage" in content, f"{cmd_file} missing Usage section"

        # Should have example code
        assert "```python" in content or "```" in content, f"{cmd_file} missing code examples"


@pytest.mark.skipif(
    not Path(".claude/graphs").exists(), reason="Project graphs directory not found"
)
def test_end_to_end_status(project_graphs_dir):
    """Test full workflow: load graphs -> format -> output."""
    loader = GraphLoader(graphs_dir=project_graphs_dir)
    formatter = GraphFormatter()

    # Load all graphs
    graphs = loader.load_all_graphs()

    # Should find at least some graphs in project
    assert len(graphs) > 0, "No graphs found in project"

    # Format status
    output = formatter.format_status(graphs)

    # Verify output structure
    assert "# Knowledge Graph Status" in output
    assert "**Graphs**:" in output
    assert "| Triad |" in output

    # Should be valid markdown
    assert output.startswith("#")


@pytest.mark.skipif(
    not Path(".claude/graphs").exists(), reason="Project graphs directory not found"
)
def test_end_to_end_search(project_graphs_dir):
    """Test full search workflow with real graphs."""
    loader = GraphLoader(graphs_dir=project_graphs_dir)
    searcher = GraphSearcher(loader)
    formatter = GraphFormatter()

    # Search for common term (likely to exist in project graphs)
    results = searcher.search("node")

    # Format results
    output = formatter.format_search_results(results, "node")

    # Verify output structure
    assert "# Search Results: 'node'" in output

    if len(results) > 0:
        # Should have triad sections
        assert "##" in output
        # Should have node headers
        assert "###" in output


@pytest.mark.skipif(
    not Path(".claude/graphs/generator_graph.json").exists(),
    reason="generator_graph.json not found",
)
def test_end_to_end_show(project_graphs_dir):
    """Test full show workflow with real graphs."""
    loader = GraphLoader(graphs_dir=project_graphs_dir)
    formatter = GraphFormatter()

    # Load a specific graph (generator_graph is usually present)
    graph = loader.load_graph("generator")

    if graph and len(graph.get("nodes", [])) > 0:
        # Get first node
        first_node = graph["nodes"][0]
        node_id = first_node["id"]

        # Format node details
        output = formatter.format_node_details(first_node, "generator", graph)

        # Verify output structure
        assert output.startswith("# ")
        assert f"**ID**: `{node_id}`" in output
        assert "**Triad**: generator" in output
        assert "## Attributes" in output


@pytest.mark.skipif(
    not Path(".claude/graphs").exists(), reason="Project graphs directory not found"
)
def test_performance_search(project_graphs_dir):
    """Verify search completes in <100ms for typical graphs."""
    loader = GraphLoader(graphs_dir=project_graphs_dir)
    searcher = GraphSearcher(loader)

    # Pre-load graphs (not counted in timing)
    loader.load_all_graphs()

    # Time search operation
    start = time.perf_counter()
    results = searcher.search("test")
    elapsed_ms = (time.perf_counter() - start) * 1000

    # Should complete quickly for typical graphs
    assert (
        elapsed_ms < 100
    ), f"Search took {elapsed_ms:.2f}ms (target: <100ms). Project may have large graphs."


@pytest.mark.skipif(
    not Path(".claude/graphs").exists(), reason="Project graphs directory not found"
)
def test_performance_load(project_graphs_dir):
    """Verify loading completes in <100ms per graph."""
    loader = GraphLoader(graphs_dir=project_graphs_dir)

    triads = loader.list_triads()

    if len(triads) > 0:
        # Test loading first graph
        first_triad = triads[0]

        start = time.perf_counter()
        graph = loader.load_graph(first_triad)
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert graph is not None
        assert (
            elapsed_ms < 100
        ), f"Loading {first_triad} took {elapsed_ms:.2f}ms (target: <100ms)"


@pytest.mark.skipif(
    not Path(".claude/graphs").exists(), reason="Project graphs directory not found"
)
def test_real_graphs_have_valid_structure(project_graphs_dir):
    """Verify real project graphs have valid structure."""
    loader = GraphLoader(graphs_dir=project_graphs_dir)
    graphs = loader.load_all_graphs()

    for triad_name, graph in graphs.items():
        # Should be a dict
        assert isinstance(graph, dict), f"{triad_name}: graph is not a dict"

        # Should have nodes (can be empty list)
        assert "nodes" in graph or "links" in graph, f"{triad_name}: missing nodes/links"

        # Check nodes structure if present
        if "nodes" in graph:
            nodes = graph["nodes"]
            assert isinstance(nodes, list), f"{triad_name}: nodes is not a list"

            for node in nodes:
                assert isinstance(node, dict), f"{triad_name}: node is not a dict"
                assert "id" in node, f"{triad_name}: node missing id field"


@pytest.mark.skipif(
    not Path(".claude/graphs").exists(), reason="Project graphs directory not found"
)
def test_search_returns_relevant_results(project_graphs_dir):
    """Verify search returns relevant results."""
    loader = GraphLoader(graphs_dir=project_graphs_dir)
    searcher = GraphSearcher(loader)

    # Search for "graph" which should exist in project graphs
    results = searcher.search("graph")

    if len(results) > 0:
        # Check first result has "graph" in it somewhere
        first = results[0]
        found_in = (
            "graph" in first.node_id.lower()
            or "graph" in first.label.lower()
            or "graph" in first.snippet.lower()
        )
        assert found_in, "Search result doesn't contain query term"


@pytest.mark.skipif(
    not Path(".claude/graphs").exists(), reason="Project graphs directory not found"
)
def test_caching_improves_performance(project_graphs_dir):
    """Verify caching makes second load faster."""
    loader = GraphLoader(graphs_dir=project_graphs_dir)

    triads = loader.list_triads()
    if len(triads) == 0:
        pytest.skip("No graphs to test caching")

    first_triad = triads[0]

    # First load (from disk)
    start1 = time.perf_counter()
    graph1 = loader.load_graph(first_triad)
    time1 = time.perf_counter() - start1

    # Second load (from cache)
    start2 = time.perf_counter()
    graph2 = loader.load_graph(first_triad)
    time2 = time.perf_counter() - start2

    # Should be same object
    assert graph1 is graph2

    # Second load should be faster (or at least not slower)
    # Allow some variance due to system load
    assert time2 <= time1 * 1.1, "Caching doesn't improve performance"


def test_formatter_produces_valid_markdown():
    """Verify formatter produces valid markdown structure."""
    from triads.km.graph_access import SearchResult

    formatter = GraphFormatter()

    # Test status formatting
    test_graph = {
        "nodes": [{"id": "n1", "label": "Node", "type": "Concept", "confidence": 0.9}],
        "links": [],
    }
    status = formatter.format_status({"test": test_graph})

    # Should have markdown headers (starts with # at beginning of string)
    assert status.startswith("# ") or "\n# " in status  # Header
    assert "| " in status  # Table syntax

    # Test search formatting
    results = [
        SearchResult(
            node_id="n1",
            triad="test",
            label="Node",
            node_type="Concept",
            confidence=0.9,
            matched_field="label",
            snippet="Node",
            relevance_score=1.0,
        )
    ]
    search = formatter.format_search_results(results, "test")

    assert search.startswith("# ")
    assert "## " in search
    assert "### " in search

    # Test node details formatting
    node = test_graph["nodes"][0]
    details = formatter.format_node_details(node, "test", test_graph)

    assert details.startswith("# ")
    assert "**ID**:" in details
    assert "**Type**:" in details
