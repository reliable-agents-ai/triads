"""Tests for GraphSearcher class - search functionality."""
import pytest
from triads.km.graph_access import (
    GraphLoader,
    GraphSearcher,
    SearchResult,
    GraphNotFoundError,
    InvalidTriadNameError,
)


@pytest.fixture
def temp_graphs_dir(tmp_path):
    """Create temporary graphs directory."""
    graphs_dir = tmp_path / ".claude" / "graphs"
    graphs_dir.mkdir(parents=True)
    return graphs_dir


@pytest.fixture
def sample_graphs(temp_graphs_dir):
    """Create sample graphs for testing."""
    import json

    design_graph = {
        "nodes": [
            {
                "id": "oauth_decision",
                "label": "OAuth2 Authentication",
                "type": "Decision",
                "description": "Use OAuth2 for secure authentication flows",
                "confidence": 0.95,
            },
            {
                "id": "jwt_entity",
                "label": "JWT Tokens",
                "type": "Entity",
                "description": "JSON Web Tokens for session management",
                "confidence": 0.88,
            },
            {
                "id": "security_concept",
                "label": "Security Framework",
                "type": "Concept",
                "description": "Overall security architecture and patterns",
                "confidence": 0.92,
            },
        ],
        "links": [],
    }

    implementation_graph = {
        "nodes": [
            {
                "id": "auth_module",
                "label": "Authentication Module",
                "type": "Entity",
                "description": "Core authentication implementation with OAuth2",
                "confidence": 0.90,
            },
            {
                "id": "test_finding",
                "label": "Low Confidence Finding",
                "type": "Finding",
                "description": "This needs more research",
                "confidence": 0.70,
            },
        ],
        "links": [],
    }

    (temp_graphs_dir / "design_graph.json").write_text(json.dumps(design_graph))
    (temp_graphs_dir / "implementation_graph.json").write_text(json.dumps(implementation_graph))

    return {"design": design_graph, "implementation": implementation_graph}


@pytest.fixture
def loader_with_graphs(temp_graphs_dir, sample_graphs):
    """GraphLoader with sample graphs loaded."""
    return GraphLoader(graphs_dir=temp_graphs_dir)


@pytest.fixture
def searcher(loader_with_graphs):
    """GraphSearcher instance."""
    return GraphSearcher(loader_with_graphs)


def test_search_basic(searcher):
    """Verify substring matching works."""
    results = searcher.search("OAuth")

    assert len(results) >= 1
    # Should find "OAuth2 Authentication" and "OAuth2" in description
    labels = [r.label for r in results]
    assert "OAuth2 Authentication" in labels


def test_search_case_insensitive(searcher):
    """Verify case doesn't matter."""
    results_lower = searcher.search("oauth")
    results_upper = searcher.search("OAUTH")
    results_mixed = searcher.search("OaUtH")

    # All should find same results
    assert len(results_lower) == len(results_upper) == len(results_mixed)


def test_search_in_label(searcher):
    """Verify searches node labels."""
    results = searcher.search("JWT")

    assert len(results) >= 1
    # Should find "JWT Tokens"
    found = False
    for result in results:
        if "JWT" in result.label:
            found = True
            assert result.matched_field == "label"
            assert result.relevance_score == 1.0  # Label matches are highest priority
    assert found


def test_search_in_description(searcher):
    """Verify searches descriptions."""
    results = searcher.search("session management")

    assert len(results) >= 1
    found = False
    for result in results:
        if "session management" in result.snippet.lower():
            found = True
            assert result.matched_field == "description"
            assert result.relevance_score == 0.7  # Description matches are medium priority
    assert found


def test_search_in_id(searcher):
    """Verify searches node IDs."""
    results = searcher.search("oauth_decision")

    assert len(results) >= 1
    found = False
    for result in results:
        if result.node_id == "oauth_decision":
            found = True
            assert result.matched_field == "id"
            assert result.relevance_score == 0.5  # ID matches are lowest priority
    assert found


def test_search_relevance_ranking(searcher):
    """Verify label matches rank higher than description matches."""
    # Search for "authentication" which appears in both label and description
    results = searcher.search("authentication")

    # Results should be sorted by relevance (highest first)
    if len(results) >= 2:
        # First result should have higher or equal relevance
        for i in range(len(results) - 1):
            assert results[i].relevance_score >= results[i + 1].relevance_score


def test_search_filter_by_triad(searcher):
    """Verify triad filter works."""
    results = searcher.search("OAuth", triad="design")

    # Should only return results from design graph
    for result in results:
        assert result.triad == "design"


def test_search_filter_by_type(searcher):
    """Verify node type filter works."""
    results = searcher.search("OAuth", node_type="Decision")

    # Should only return Decision nodes
    for result in results:
        assert result.node_type == "Decision"


def test_search_filter_by_confidence(searcher):
    """Verify confidence threshold filter works."""
    results = searcher.search("", min_confidence=0.85)

    # All results should have confidence >= 0.85
    for result in results:
        assert result.confidence >= 0.85


def test_search_combined_filters(searcher):
    """Verify multiple filters work together."""
    results = searcher.search(
        "security", triad="design", node_type="Concept", min_confidence=0.90
    )

    # Should satisfy all filters
    for result in results:
        assert result.triad == "design"
        assert result.node_type == "Concept"
        assert result.confidence >= 0.90
        assert "security" in result.snippet.lower()


def test_search_no_results(searcher):
    """Verify returns empty list when no matches."""
    results = searcher.search("nonexistent_term_that_wont_match")

    assert results == []


def test_search_empty_query(searcher):
    """Verify handles empty/short queries."""
    # Empty query should match nothing (empty string won't be in any field)
    results = searcher.search("")

    # Depending on implementation, might return all or none
    # Let's verify it doesn't crash
    assert isinstance(results, list)


def test_search_special_characters(searcher):
    """Verify handles special characters in query."""
    # Should handle regex special characters safely
    results = searcher.search("OAuth2 (test)")

    # Should not crash, even if no results
    assert isinstance(results, list)


def test_search_invalid_triad_raises_error(searcher):
    """Verify raises GraphNotFoundError for invalid triad."""
    with pytest.raises(GraphNotFoundError) as exc_info:
        searcher.search("test", triad="nonexistent")

    assert "nonexistent" in str(exc_info.value)
    assert exc_info.value.triad == "nonexistent"


def test_search_invalid_triad_name_raises_error(searcher):
    """Verify raises GraphNotFoundError for invalid triad name characters."""
    with pytest.raises(GraphNotFoundError):
        searcher.search("test", triad="../../etc/passwd")


def test_get_confidence_handles_missing(searcher):
    """Verify _get_confidence handles missing confidence field."""
    node = {"id": "test", "label": "Test"}

    confidence = searcher._get_confidence(node)
    assert confidence == 0.0


def test_get_confidence_handles_invalid_type(searcher):
    """Verify _get_confidence handles non-numeric confidence."""
    node = {"id": "test", "label": "Test", "confidence": "invalid"}

    confidence = searcher._get_confidence(node)
    assert confidence == 0.0


def test_find_best_match_label_priority(searcher):
    """Verify label matches have highest priority."""
    result = searcher._find_best_match(
        "test", node_id="node_1", label="Test Label", description="Other description"
    )

    assert result is not None
    field, snippet, relevance = result
    assert field == "label"
    assert relevance == 1.0


def test_find_best_match_description_priority(searcher):
    """Verify description matches have medium priority."""
    result = searcher._find_best_match(
        "test", node_id="node_1", label="Other Label", description="Test description"
    )

    assert result is not None
    field, snippet, relevance = result
    assert field == "description"
    assert relevance == 0.7


def test_find_best_match_id_priority(searcher):
    """Verify ID matches have lowest priority."""
    result = searcher._find_best_match(
        "test", node_id="test_node", label="Other Label", description="Other description"
    )

    assert result is not None
    field, snippet, relevance = result
    assert field == "id"
    assert relevance == 0.5


def test_find_best_match_no_match(searcher):
    """Verify returns None when no match found."""
    result = searcher._find_best_match(
        "nonexistent", node_id="node_1", label="Test Label", description="Test description"
    )

    assert result is None


def test_create_snippet_basic(searcher):
    """Verify creates snippet with context."""
    text = "This is a test string with some context around the match"
    snippet = searcher._create_snippet(text, "test", max_len=30)

    assert "test" in snippet.lower()
    assert len(snippet) <= 33  # max_len + ellipsis


def test_create_snippet_at_start(searcher):
    """Verify snippet at text start has no leading ellipsis."""
    text = "Test at the start of the string"
    snippet = searcher._create_snippet(text, "test", max_len=30)

    assert not snippet.startswith("...")
    assert "test" in snippet.lower()


def test_create_snippet_at_end(searcher):
    """Verify snippet at text end has no trailing ellipsis."""
    text = "String with match at the end test"
    snippet = searcher._create_snippet(text, "test", max_len=50)

    assert not snippet.endswith("...")
    assert "test" in snippet.lower()


def test_create_snippet_in_middle(searcher):
    """Verify snippet in middle has both ellipses."""
    text = "A" * 50 + " test " + "B" * 50
    snippet = searcher._create_snippet(text, "test", max_len=20)

    assert snippet.startswith("...")
    assert snippet.endswith("...")
    assert "test" in snippet.lower()


def test_create_snippet_no_match(searcher):
    """Verify handles case where match not found (shouldn't happen but be safe)."""
    text = "Text without the search term"
    snippet = searcher._create_snippet(text, "nonexistent", max_len=20)

    # Should return truncated text
    assert len(snippet) <= 23  # max_len + ellipsis


def test_search_result_dataclass():
    """Verify SearchResult dataclass works correctly."""
    result = SearchResult(
        node_id="test_node",
        triad="design",
        label="Test Node",
        node_type="Concept",
        confidence=0.95,
        matched_field="label",
        snippet="Test Node description",
        relevance_score=1.0,
    )

    assert result.node_id == "test_node"
    assert result.triad == "design"
    assert result.confidence == 0.95


def test_search_sorts_by_relevance_and_confidence(searcher):
    """Verify search results sorted by relevance first, then confidence."""
    # Search broadly to get multiple results
    results = searcher.search("e")  # Common letter, should match many

    if len(results) >= 2:
        # Verify sorting: relevance descending, then confidence descending
        for i in range(len(results) - 1):
            if results[i].relevance_score == results[i + 1].relevance_score:
                # Same relevance - confidence should be descending
                assert results[i].confidence >= results[i + 1].confidence
            else:
                # Different relevance - should be descending
                assert results[i].relevance_score > results[i + 1].relevance_score


def test_search_with_unicode_query(searcher):
    """Verify handles Unicode in search query."""
    # Should not crash with Unicode
    results = searcher.search("你好")
    assert isinstance(results, list)


def test_search_filter_excludes_low_confidence(searcher):
    """Verify min_confidence filter excludes low confidence nodes."""
    # Search without filter
    all_results = searcher.search("finding")

    # Search with high confidence filter
    high_conf_results = searcher.search("finding", min_confidence=0.85)

    # Should have fewer results (filtered out low confidence)
    assert len(high_conf_results) <= len(all_results)

    # Verify low confidence node is excluded
    low_conf_found = any(r.confidence < 0.85 for r in high_conf_results)
    assert not low_conf_found
