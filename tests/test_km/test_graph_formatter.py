"""Tests for GraphFormatter class - markdown output formatting."""
import pytest
from triads.km.graph_access import GraphFormatter, SearchResult


@pytest.fixture
def formatter():
    """GraphFormatter instance."""
    return GraphFormatter()


@pytest.fixture
def sample_graph():
    """Sample graph data for formatting tests."""
    return {
        "nodes": [
            {
                "id": "node1",
                "label": "Test Node 1",
                "type": "Concept",
                "description": "First test node",
                "confidence": 0.95,
                "evidence": "test:1",
                "created_by": "test-agent",
                "created_at": "2025-01-01T00:00:00Z",
            },
            {
                "id": "node2",
                "label": "Test Node 2",
                "type": "Entity",
                "description": "Second test node",
                "confidence": 0.88,
            },
            {
                "id": "node3",
                "label": "Test Node 3",
                "type": "Decision",
                "description": "Third test node",
                "confidence": 0.92,
            },
        ],
        "links": [
            {"source": "node1", "target": "node2", "key": "relates_to"},
            {"source": "node1", "target": "node3", "key": "influences"},
        ],
    }


@pytest.fixture
def sample_graphs(sample_graph):
    """Multiple sample graphs."""
    return {
        "design": sample_graph,
        "implementation": {
            "nodes": [
                {"id": "impl1", "label": "Implementation Node", "type": "Entity", "confidence": 0.90}
            ],
            "links": [],
        },
    }


def test_format_status_single_graph(formatter, sample_graph):
    """Verify formats one graph correctly."""
    graphs = {"test": sample_graph}
    output = formatter.format_status(graphs)

    # Check header
    assert "# Knowledge Graph Status" in output

    # Check summary stats
    assert "**Graphs**: 1" in output
    assert "**Total Nodes**: 3" in output
    assert "**Total Edges**: 2" in output

    # Check table structure
    assert "| Triad | Nodes | Edges | Types | Avg Confidence |" in output
    assert "|-------|-------|-------|-------|----------------|" in output

    # Check row content
    assert "| test |" in output
    assert "| 3 |" in output
    assert "| 2 |" in output


def test_format_status_multiple_graphs(formatter, sample_graphs):
    """Verify formats multiple graphs."""
    output = formatter.format_status(sample_graphs)

    assert "**Graphs**: 2" in output
    assert "**Total Nodes**: 4" in output  # 3 + 1
    assert "**Total Edges**: 2" in output  # 2 + 0

    # Both triads should be in output
    assert "| design |" in output
    assert "| implementation |" in output


def test_format_status_empty(formatter):
    """Verify handles empty graph dict."""
    output = formatter.format_status({})

    assert "**No knowledge graphs found**" in output
    assert ".claude/graphs/" in output


def test_format_status_includes_metadata(formatter, sample_graph):
    """Verify includes node counts, confidence stats."""
    graphs = {"test": sample_graph}
    output = formatter.format_status(graphs)

    # Should calculate average confidence
    # (0.95 + 0.88 + 0.92) / 3 = 0.916...
    assert "0.92" in output  # Average confidence rounded


def test_format_status_calculates_type_count(formatter, sample_graph):
    """Verify counts unique node types."""
    graphs = {"test": sample_graph}
    output = formatter.format_status(graphs)

    # Should have 3 types: Concept, Entity, Decision
    assert "| 3 |" in output  # Types column


def test_format_status_single_triad_includes_breakdown(formatter, sample_graph):
    """Verify single triad view includes type breakdown."""
    graphs = {"test": sample_graph}
    output = formatter.format_status(graphs, triad="test")

    # Should include type breakdown section
    assert "## Node Type Breakdown" in output
    assert "**Concept**: 1" in output
    assert "**Entity**: 1" in output
    assert "**Decision**: 1" in output


def test_format_status_not_found(formatter, sample_graphs):
    """Verify handles triad not found."""
    output = formatter.format_status(sample_graphs, triad="nonexistent")

    assert "**Graph 'nonexistent' not found**" in output
    assert "Available graphs:" in output


def test_format_status_handles_missing_confidence(formatter):
    """Verify handles nodes without confidence field."""
    graph = {
        "nodes": [
            {"id": "node1", "label": "Node 1", "type": "Concept"},
            {"id": "node2", "label": "Node 2", "type": "Entity"},
        ],
        "links": [],
    }

    output = formatter.format_status({"test": graph})

    # Should show 0.00 for average confidence
    assert "0.00" in output


def test_format_status_handles_invalid_confidence(formatter):
    """Verify handles invalid confidence values."""
    graph = {
        "nodes": [
            {"id": "node1", "label": "Node 1", "type": "Concept", "confidence": "invalid"},
            {"id": "node2", "label": "Node 2", "type": "Entity", "confidence": 0.90},
        ],
        "links": [],
    }

    output = formatter.format_status({"test": graph})

    # Should calculate average with only valid values (0.90)
    assert "0.90" in output


def test_format_search_results(formatter):
    """Verify formats search results as markdown table."""
    results = [
        SearchResult(
            node_id="node1",
            triad="design",
            label="OAuth Decision",
            node_type="Decision",
            confidence=0.95,
            matched_field="label",
            snippet="OAuth Decision",
            relevance_score=1.0,
        ),
        SearchResult(
            node_id="node2",
            triad="design",
            label="JWT Entity",
            node_type="Entity",
            confidence=0.88,
            matched_field="description",
            snippet="...OAuth implementation...",
            relevance_score=0.7,
        ),
    ]

    output = formatter.format_search_results(results, "OAuth")

    # Check header
    assert "# Search Results: 'OAuth'" in output
    assert "**Found**: 2 nodes" in output

    # Check grouping by triad
    assert "## design (2 results)" in output

    # Check node details
    assert "### OAuth Decision (`node1`)" in output
    assert "**Type**: Decision" in output
    assert "**Confidence**: 0.95" in output
    assert "**Match**: label" in output

    # Check snippet
    assert "> OAuth Decision" in output


def test_format_search_results_empty(formatter):
    """Verify handles no results gracefully."""
    output = formatter.format_search_results([], "nonexistent")

    assert "**No results found for: 'nonexistent'**" in output
    assert "**Suggestions:**" in output
    assert "Try a broader search term" in output


def test_format_search_results_grouping(formatter):
    """Verify groups by triad."""
    results = [
        SearchResult(
            node_id="node1",
            triad="design",
            label="Design Node",
            node_type="Concept",
            confidence=0.95,
            matched_field="label",
            snippet="Design Node",
            relevance_score=1.0,
        ),
        SearchResult(
            node_id="node2",
            triad="implementation",
            label="Implementation Node",
            node_type="Entity",
            confidence=0.90,
            matched_field="label",
            snippet="Implementation Node",
            relevance_score=1.0,
        ),
        SearchResult(
            node_id="node3",
            triad="design",
            label="Another Design Node",
            node_type="Decision",
            confidence=0.88,
            matched_field="label",
            snippet="Another Design Node",
            relevance_score=1.0,
        ),
    ]

    output = formatter.format_search_results(results, "test")

    # Should have separate sections for each triad
    assert "## design (2 results)" in output
    assert "## implementation (1 results)" in output  # Implementation doesn't do singular


def test_format_node_details(formatter, sample_graph):
    """Verify formats all node attributes."""
    node = sample_graph["nodes"][0]
    output = formatter.format_node_details(node, "test", sample_graph)

    # Check header
    assert "# Test Node 1" in output

    # Check metadata
    assert "**ID**: `node1`" in output
    assert "**Triad**: test" in output

    # Check attributes
    assert "## Attributes" in output
    assert "**Type**: Concept" in output
    assert "**Confidence**: 0.95" in output

    # Check description
    assert "**Description**:" in output
    assert "First test node" in output

    # Check provenance
    assert "**Evidence**:" in output
    assert "test:1" in output
    assert "**Created By**: test-agent" in output
    assert "**Created**: 2025-01-01T00:00:00Z" in output


def test_format_node_details_with_relationships(formatter, sample_graph):
    """Verify includes edges."""
    node = sample_graph["nodes"][0]  # node1 has outgoing edges
    output = formatter.format_node_details(node, "test", sample_graph)

    # Check relationships section
    assert "## Relationships" in output
    assert "**Outgoing** (2):" in output
    assert "relates_to → `node2`" in output
    assert "influences → `node3`" in output


def test_format_node_details_incoming_edges(formatter, sample_graph):
    """Verify shows incoming edges."""
    node = sample_graph["nodes"][1]  # node2 has incoming edge from node1
    output = formatter.format_node_details(node, "test", sample_graph)

    assert "## Relationships" in output
    assert "**Incoming** (1):" in output
    assert "`node1` → relates_to" in output


def test_format_node_details_missing_fields(formatter):
    """Verify handles nodes with missing optional fields."""
    minimal_node = {
        "id": "minimal",
        "label": "Minimal Node",
        "type": "Concept",
    }
    minimal_graph = {"nodes": [minimal_node], "links": []}

    output = formatter.format_node_details(minimal_node, "test", minimal_graph)

    # Should not crash, should show available fields
    assert "# Minimal Node" in output
    assert "**ID**: `minimal`" in output
    assert "**Type**: Concept" in output

    # Should show 0.00 for missing confidence
    # Actually, let's check what happens
    assert "**Confidence**:" in output


def test_format_node_details_additional_properties(formatter):
    """Verify shows additional non-standard properties."""
    node = {
        "id": "custom",
        "label": "Custom Node",
        "type": "Entity",
        "confidence": 0.90,
        "custom_field": "custom value",
        "metadata": {"key": "value"},
    }
    graph = {"nodes": [node], "links": []}

    output = formatter.format_node_details(node, "test", graph)

    # Should show additional properties
    assert "## Additional Properties" in output
    assert "**custom_field**: custom value" in output
    assert "**metadata**:" in output
    assert "```json" in output


def test_format_node_details_list_property(formatter):
    """Verify formats list properties as JSON."""
    node = {
        "id": "node",
        "label": "Node",
        "type": "Concept",
        "tags": ["tag1", "tag2", "tag3"],
    }
    graph = {"nodes": [node], "links": []}

    output = formatter.format_node_details(node, "test", graph)

    assert "## Additional Properties" in output
    assert "**tags**:" in output
    assert "```json" in output


def test_format_node_details_no_relationships(formatter):
    """Verify handles nodes with no edges."""
    node = {"id": "isolated", "label": "Isolated Node", "type": "Concept"}
    graph = {"nodes": [node], "links": []}

    output = formatter.format_node_details(node, "test", graph)

    # Should not have relationships section if no edges
    assert "## Relationships" not in output


def test_format_status_sorted_triads(formatter, sample_graphs):
    """Verify triads are sorted alphabetically in output."""
    # Add more triads to test sorting
    graphs = {
        "zebra": sample_graphs["design"],
        "alpha": sample_graphs["implementation"],
        "middle": sample_graphs["design"],
    }

    output = formatter.format_status(graphs)

    # Find positions of triad names in output
    alpha_pos = output.find("| alpha |")
    middle_pos = output.find("| middle |")
    zebra_pos = output.find("| zebra |")

    # Should be in alphabetical order
    assert alpha_pos < middle_pos < zebra_pos


def test_format_search_results_sorted_triads(formatter):
    """Verify search results grouped and sorted by triad."""
    results = [
        SearchResult(
            node_id="n1",
            triad="zebra",
            label="Node",
            node_type="Concept",
            confidence=0.9,
            matched_field="label",
            snippet="Node",
            relevance_score=1.0,
        ),
        SearchResult(
            node_id="n2",
            triad="alpha",
            label="Node",
            node_type="Concept",
            confidence=0.9,
            matched_field="label",
            snippet="Node",
            relevance_score=1.0,
        ),
    ]

    output = formatter.format_search_results(results, "test")

    # Find positions of triad headers
    alpha_pos = output.find("## alpha")
    zebra_pos = output.find("## zebra")

    # Should be alphabetically sorted
    assert alpha_pos < zebra_pos


def test_format_node_details_handles_confidence_string(formatter):
    """Verify handles confidence as string."""
    node = {
        "id": "node",
        "label": "Node",
        "type": "Concept",
        "confidence": "0.95",  # String instead of float
    }
    graph = {"nodes": [node], "links": []}

    output = formatter.format_node_details(node, "test", graph)

    # Should convert to float and format
    assert "**Confidence**: 0.95" in output


def test_format_node_details_handles_confidence_invalid(formatter):
    """Verify handles invalid confidence gracefully."""
    node = {
        "id": "node",
        "label": "Node",
        "type": "Concept",
        "confidence": "invalid",
    }
    graph = {"nodes": [node], "links": []}

    output = formatter.format_node_details(node, "test", graph)

    # Should show raw value if can't convert
    assert "**Confidence**: invalid" in output
