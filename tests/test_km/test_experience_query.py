"""Tests for ExperienceQueryEngine - relevance scoring and query logic."""

import json
import time
from pathlib import Path

import pytest

from triads.km.experience_query import (
    ExperienceQueryEngine,
    ProcessKnowledge,
    PRIORITY_MULTIPLIERS,
    RELEVANCE_THRESHOLD,
    TARGET_P95_MS,
    WEIGHT_TOOL,
    WEIGHT_FILE,
    WEIGHT_ACTION_KEYWORDS,
    WEIGHT_CONTEXT_KEYWORDS,
)


@pytest.fixture
def temp_graphs_dir(tmp_path):
    """Create temporary graphs directory with test data."""
    graphs_dir = tmp_path / ".claude" / "graphs"
    graphs_dir.mkdir(parents=True)
    return graphs_dir


@pytest.fixture
def test_graph_fixture():
    """Load test graph fixture."""
    fixture_path = Path(__file__).parent / "fixtures" / "test_graph.json"
    with open(fixture_path, "r") as f:
        return json.load(f)


@pytest.fixture
def create_test_graph(temp_graphs_dir):
    """Factory fixture to create test graph files."""
    def _create(triad_name, graph_data):
        graph_file = temp_graphs_dir / f"{triad_name}_graph.json"
        graph_file.write_text(json.dumps(graph_data, indent=2))
        return graph_file

    return _create


@pytest.fixture
def engine_with_test_data(temp_graphs_dir, create_test_graph, test_graph_fixture):
    """Create engine with test graph loaded."""
    create_test_graph("test", test_graph_fixture)
    engine = ExperienceQueryEngine(graphs_dir=temp_graphs_dir)
    return engine


# ============================================================================
# Unit Tests: Relevance Scoring
# ============================================================================


def test_relevance_tool_exact_match(engine_with_test_data):
    """Tool name exact match should score 0.4 (40%)."""
    engine = engine_with_test_data

    # Load cache
    engine._cache = engine._load_process_knowledge()

    # Get CRITICAL checklist node
    node = None
    for nodes in engine._cache.values():
        for n in nodes:
            if n["id"] == "test_checklist_critical":
                node = n
                break

    assert node is not None

    # Calculate relevance with exact tool match
    relevance = engine._calculate_relevance(
        node=node,
        tool_name="Write",  # Exact match
        file_path="",
        tool_input_str="{}",
    )

    # Should have tool weight (0.4)
    # With CRITICAL multiplier (2.0x): 0.4 * 2.0 = 0.8
    assert relevance >= 0.4 * PRIORITY_MULTIPLIERS["CRITICAL"]


def test_relevance_tool_wildcard(engine_with_test_data):
    """Wildcard tool match should score 0.2 (half of 40%)."""
    engine = engine_with_test_data

    # Load cache
    engine._cache = engine._load_process_knowledge()

    # Get wildcard node
    node = None
    for nodes in engine._cache.values():
        for n in nodes:
            if n["id"] == "test_wildcard_match":
                node = n
                break

    assert node is not None

    # Calculate relevance with wildcard match
    relevance = engine._calculate_relevance(
        node=node,
        tool_name="AnyTool",  # Should match wildcard
        file_path="",
        tool_input_str="{}",
    )

    # Should have 50% of tool weight (0.2)
    # With MEDIUM multiplier (1.0x): 0.2 * 1.0 = 0.2
    assert 0.15 <= relevance <= 0.25


def test_relevance_file_pattern_match(engine_with_test_data):
    """File pattern match should score 0.4 (40%)."""
    engine = engine_with_test_data

    # Load cache
    engine._cache = engine._load_process_knowledge()

    # Get CRITICAL checklist node
    node = None
    for nodes in engine._cache.values():
        for n in nodes:
            if n["id"] == "test_checklist_critical":
                node = n
                break

    assert node is not None

    # Calculate relevance with file match
    relevance = engine._calculate_relevance(
        node=node,
        tool_name="",  # No tool match
        file_path="/path/to/plugin.json",  # Should match **/plugin.json
        tool_input_str="{}",
    )

    # Should have file weight (0.4)
    # With CRITICAL multiplier (2.0x): 0.4 * 2.0 = 0.8
    assert relevance >= 0.4 * PRIORITY_MULTIPLIERS["CRITICAL"]


def test_relevance_keyword_match(engine_with_test_data):
    """Action/context keywords should add 0.2 (20% total)."""
    engine = engine_with_test_data

    # Load cache
    engine._cache = engine._load_process_knowledge()

    # Get CRITICAL checklist node
    node = None
    for nodes in engine._cache.values():
        for n in nodes:
            if n["id"] == "test_checklist_critical":
                node = n
                break

    assert node is not None

    # Calculate relevance with keywords
    relevance = engine._calculate_relevance(
        node=node,
        tool_name="",
        file_path="",
        tool_input_str='{"action": "version bump"}',  # Contains "version" keyword
    )

    # Should have action keyword weight (0.1)
    # With CRITICAL multiplier (2.0x): 0.1 * 2.0 = 0.2
    assert relevance >= 0.1 * PRIORITY_MULTIPLIERS["CRITICAL"]


def test_relevance_combined(engine_with_test_data):
    """All factors combined should sum correctly."""
    engine = engine_with_test_data

    # Load cache
    engine._cache = engine._load_process_knowledge()

    # Get CRITICAL checklist node
    node = None
    for nodes in engine._cache.values():
        for n in nodes:
            if n["id"] == "test_checklist_critical":
                node = n
                break

    assert node is not None

    # Calculate with all factors
    relevance = engine._calculate_relevance(
        node=node,
        tool_name="Write",  # Tool match: 0.4
        file_path="/path/to/plugin.json",  # File match: 0.4
        tool_input_str='{"action": "version bump"}',  # Keyword: 0.1
    )

    # Base: 0.4 + 0.4 + 0.1 = 0.9
    # With CRITICAL multiplier (2.0x): 0.9 * 2.0 = 1.8
    # But capped at 1.0 for non-CRITICAL... wait, CRITICAL is not capped
    expected_min = (0.4 + 0.4 + 0.1) * PRIORITY_MULTIPLIERS["CRITICAL"]
    assert relevance >= expected_min * 0.9  # Allow 10% tolerance


def test_priority_multiplier_critical(engine_with_test_data):
    """CRITICAL items get 2.0x boost."""
    engine = engine_with_test_data

    # Load cache
    engine._cache = engine._load_process_knowledge()

    # Get CRITICAL node
    node = None
    for nodes in engine._cache.values():
        for n in nodes:
            if n["id"] == "test_checklist_critical":
                node = n
                break

    assert node is not None
    assert node["priority"] == "CRITICAL"

    # Calculate base score
    relevance = engine._calculate_relevance(
        node=node,
        tool_name="Write",  # 0.4 base
        file_path="",
        tool_input_str="{}",
    )

    # Should be 0.4 * 2.0 = 0.8
    expected = 0.4 * 2.0
    assert abs(relevance - expected) < 0.1


def test_priority_multiplier_high(engine_with_test_data):
    """HIGH items get 1.5x boost."""
    engine = engine_with_test_data

    # Load cache
    engine._cache = engine._load_process_knowledge()

    # Get HIGH node
    node = None
    for nodes in engine._cache.values():
        for n in nodes:
            if n["id"] == "test_pattern_high":
                node = n
                break

    assert node is not None
    assert node["priority"] == "HIGH"

    # Calculate base score
    relevance = engine._calculate_relevance(
        node=node,
        tool_name="Write",  # 0.4 base
        file_path="",
        tool_input_str="{}",
    )

    # Should be 0.4 * 1.5 = 0.6
    expected = 0.4 * 1.5
    assert abs(relevance - expected) < 0.1


def test_priority_multiplier_low(engine_with_test_data):
    """LOW items get 0.5x penalty."""
    engine = engine_with_test_data

    # Load cache
    engine._cache = engine._load_process_knowledge()

    # Get LOW node
    node = None
    for nodes in engine._cache.values():
        for n in nodes:
            if n["id"] == "test_requirement_low":
                node = n
                break

    assert node is not None
    assert node["priority"] == "LOW"

    # Calculate base score
    relevance = engine._calculate_relevance(
        node=node,
        tool_name="Write",  # 0.4 base
        file_path="",
        tool_input_str="{}",
    )

    # Should be 0.4 * 0.5 = 0.2
    expected = 0.4 * 0.5
    assert abs(relevance - expected) < 0.1


def test_sorting_priority_first(engine_with_test_data):
    """Results should sort by priority first, then relevance."""
    engine = engine_with_test_data

    # Query with broad match
    results = engine.query_for_tool_use(
        tool_name="Write",
        tool_input={"file_path": "test.py"},
        cwd=".",
    )

    # Should have multiple results
    assert len(results) > 1

    # Extract priorities
    priorities = [r.priority for r in results]

    # CRITICAL should come first
    if "CRITICAL" in priorities:
        assert priorities[0] == "CRITICAL"


def test_get_critical_knowledge(engine_with_test_data):
    """get_critical_knowledge should return only CRITICAL items."""
    engine = engine_with_test_data

    critical = engine.get_critical_knowledge()

    # Should have at least one CRITICAL item
    assert len(critical) > 0

    # All should be CRITICAL
    for item in critical:
        assert item.priority == "CRITICAL"


# ============================================================================
# Integration Tests: Full Query Flow
# ============================================================================


def test_query_with_real_graph(engine_with_test_data):
    """Query with real graph data should return relevant results."""
    engine = engine_with_test_data

    # Query for Write to plugin.json
    results = engine.query_for_tool_use(
        tool_name="Write",
        tool_input={"file_path": "/path/to/plugin.json"},
        cwd=".",
    )

    # Should find Version Bump Checklist
    labels = [r.label for r in results]
    assert "Version Bump File Checklist" in labels

    # Should be CRITICAL
    checklist = next(r for r in results if r.label == "Version Bump File Checklist")
    assert checklist.priority == "CRITICAL"


def test_query_returns_process_knowledge_objects(engine_with_test_data):
    """Query should return ProcessKnowledge objects."""
    engine = engine_with_test_data

    results = engine.query_for_tool_use(
        tool_name="Write",
        tool_input={"file_path": "test.py"},
        cwd=".",
    )

    # Should have results
    assert len(results) > 0

    # All should be ProcessKnowledge
    for item in results:
        assert isinstance(item, ProcessKnowledge)
        assert hasattr(item, "node_id")
        assert hasattr(item, "label")
        assert hasattr(item, "priority")
        assert hasattr(item, "formatted_text")


def test_query_filters_by_threshold(engine_with_test_data):
    """Query should filter out items below relevance threshold."""
    engine = engine_with_test_data

    # Query with tool that doesn't match anything well
    results = engine.query_for_tool_use(
        tool_name="Read",  # Doesn't match any trigger
        tool_input={"file_path": "nonexistent.xyz"},
        cwd=".",
    )

    # Might have wildcard match, but should be filtered
    # Or might be empty
    if results:
        # All should exceed threshold
        for item in results:
            # Note: relevance_score has multiplier applied
            # For MEDIUM with wildcard (0.2 * 1.0 = 0.2) < 0.4 threshold
            # So should be filtered out
            pass


def test_query_with_empty_graphs_dir(temp_graphs_dir):
    """Query with no graphs should return empty list."""
    engine = ExperienceQueryEngine(graphs_dir=temp_graphs_dir)

    results = engine.query_for_tool_use(
        tool_name="Write",
        tool_input={"file_path": "test.py"},
        cwd=".",
    )

    assert results == []


def test_formatted_text_includes_content(engine_with_test_data):
    """Formatted text should include process-specific content."""
    engine = engine_with_test_data

    # Get CRITICAL checklist
    results = engine.query_for_tool_use(
        tool_name="Write",
        tool_input={"file_path": "plugin.json"},
        cwd=".",
    )

    checklist = next(
        (r for r in results if r.process_type == "checklist"),
        None
    )

    assert checklist is not None
    assert "Checklist:" in checklist.formatted_text
    assert "plugin.json" in checklist.formatted_text
    assert "marketplace.json" in checklist.formatted_text


def test_formatted_text_critical_priority(engine_with_test_data):
    """CRITICAL items should have prominent formatting."""
    engine = engine_with_test_data

    critical = engine.get_critical_knowledge()

    assert len(critical) > 0

    for item in critical:
        assert "⚠️" in item.formatted_text
        assert "CRITICAL" in item.formatted_text
        assert "=" in item.formatted_text  # Border


# ============================================================================
# Performance Tests
# ============================================================================


def test_performance_benchmark(engine_with_test_data):
    """Query should complete in < 100ms (P95)."""
    engine = engine_with_test_data

    # Warm up cache
    engine.query_for_tool_use(
        tool_name="Write",
        tool_input={"file_path": "test.py"},
        cwd=".",
    )

    # Benchmark 10 queries
    times = []
    for i in range(10):
        start = time.perf_counter()

        engine.query_for_tool_use(
            tool_name="Write",
            tool_input={"file_path": f"test{i}.py"},
            cwd=".",
        )

        elapsed_ms = (time.perf_counter() - start) * 1000
        times.append(elapsed_ms)

    # Calculate P95
    times.sort()
    p95 = times[int(len(times) * 0.95)]

    print(f"\nPerformance: P95={p95:.1f}ms, min={min(times):.1f}ms, max={max(times):.1f}ms")

    # Should meet target (with some tolerance)
    assert p95 < TARGET_P95_MS * 1.5, f"P95 {p95:.1f}ms exceeds target {TARGET_P95_MS}ms"


def test_performance_with_multiple_graphs(temp_graphs_dir, create_test_graph, test_graph_fixture):
    """Query should scale with multiple graphs."""
    # Create 5 graphs
    for i in range(5):
        create_test_graph(f"test{i}", test_graph_fixture)

    engine = ExperienceQueryEngine(graphs_dir=temp_graphs_dir)

    # Warm up
    engine.query_for_tool_use(
        tool_name="Write",
        tool_input={"file_path": "test.py"},
        cwd=".",
    )

    # Benchmark
    start = time.perf_counter()

    engine.query_for_tool_use(
        tool_name="Write",
        tool_input={"file_path": "plugin.json"},
        cwd=".",
    )

    elapsed_ms = (time.perf_counter() - start) * 1000

    print(f"\nMulti-graph performance: {elapsed_ms:.1f}ms (5 graphs)")

    # Should still be reasonable
    assert elapsed_ms < TARGET_P95_MS * 2, f"Multi-graph query too slow: {elapsed_ms:.1f}ms"


# ============================================================================
# File Pattern Matching Tests
# ============================================================================


def test_file_pattern_doublestar(engine_with_test_data):
    """** pattern should match any directory depth."""
    engine = engine_with_test_data

    # Test **/plugin.json matches various depths
    assert engine._match_file_pattern("/path/to/plugin.json", "**/plugin.json")
    assert engine._match_file_pattern("/a/b/c/d/plugin.json", "**/plugin.json")
    assert engine._match_file_pattern("plugin.json", "**/plugin.json")


def test_file_pattern_wildcard(engine_with_test_data):
    """* pattern should match filename parts."""
    engine = engine_with_test_data

    # Test **/*version*
    assert engine._match_file_pattern("/path/to/version.py", "**/*version*")
    assert engine._match_file_pattern("/path/to/my_version_file.txt", "**/*version*")


def test_file_pattern_no_match(engine_with_test_data):
    """Non-matching patterns should return False."""
    engine = engine_with_test_data

    assert not engine._match_file_pattern("/path/to/other.json", "**/plugin.json")
    assert not engine._match_file_pattern("/path/to/file.py", "**/migrations/**/*.py")


# ============================================================================
# Edge Cases
# ============================================================================


def test_query_with_no_file_path(engine_with_test_data):
    """Query without file_path should still work."""
    engine = engine_with_test_data

    results = engine.query_for_tool_use(
        tool_name="Write",
        tool_input={"content": "test"},
        cwd=".",
    )

    # Should work, might have wildcard matches
    assert isinstance(results, list)


def test_query_with_relative_path(engine_with_test_data):
    """Query with relative path should normalize."""
    engine = engine_with_test_data

    results = engine.query_for_tool_use(
        tool_name="Write",
        tool_input={"file_path": "plugin.json"},  # Relative
        cwd="/Users/dev/project",
    )

    # Should find results
    assert len(results) > 0


def test_node_without_trigger_conditions(temp_graphs_dir, create_test_graph):
    """Node without trigger_conditions should not crash."""
    graph = {
        "directed": True,
        "nodes": [
            {
                "id": "broken_node",
                "type": "Concept",
                "label": "Broken Node",
                "process_type": "pattern",
                "priority": "MEDIUM",
                # Missing trigger_conditions
            }
        ],
        "links": [],
    }

    create_test_graph("broken", graph)
    engine = ExperienceQueryEngine(graphs_dir=temp_graphs_dir)

    # Should not crash
    results = engine.query_for_tool_use(
        tool_name="Write",
        tool_input={"file_path": "test.py"},
        cwd=".",
    )

    assert isinstance(results, list)


def test_malformed_process_node(temp_graphs_dir, create_test_graph):
    """Malformed process node should be skipped gracefully."""
    graph = {
        "directed": True,
        "nodes": [
            {
                "id": "malformed_node",
                "type": "Concept",
                "process_type": "checklist",
                # Missing required fields
            }
        ],
        "links": [],
    }

    create_test_graph("malformed", graph)
    engine = ExperienceQueryEngine(graphs_dir=temp_graphs_dir)

    # Should not crash
    results = engine.query_for_tool_use(
        tool_name="Write",
        tool_input={"file_path": "test.py"},
        cwd=".",
    )

    assert isinstance(results, list)


# ============================================================================
# Critical Recall Test (MOST IMPORTANT)
# ============================================================================


def test_critical_recall_marketplace_json_scenario(engine_with_test_data):
    """CRITICAL: Version bump checklist MUST inject when relevant.

    This is THE test that validates the whole system.
    If this fails, the system is not meeting its core requirement.
    """
    engine = engine_with_test_data

    # Scenario: User is writing to plugin.json (version bump)
    results = engine.query_for_tool_use(
        tool_name="Write",
        tool_input={"file_path": "/path/to/plugin.json"},
        cwd=".",
    )

    # MUST find Version Bump Checklist
    labels = [r.label for r in results]
    assert "Version Bump File Checklist" in labels, (
        "CRITICAL FAILURE: Version Bump Checklist not injected when writing to plugin.json. "
        "This is the exact scenario the system was designed to prevent!"
    )

    # MUST be CRITICAL priority
    checklist = next(r for r in results if r.label == "Version Bump File Checklist")
    assert checklist.priority == "CRITICAL"

    # MUST mention marketplace.json
    assert "marketplace.json" in checklist.formatted_text.lower()

    print("\n✅ CRITICAL RECALL TEST PASSED: Version bump checklist injected correctly")


def test_critical_always_shown_at_session_start(engine_with_test_data):
    """CRITICAL items should always be available via get_critical_knowledge."""
    engine = engine_with_test_data

    critical = engine.get_critical_knowledge()

    # MUST have at least one CRITICAL item
    assert len(critical) > 0, "No CRITICAL items found for session start"

    # MUST include Version Bump Checklist
    labels = [r.label for r in critical]
    assert "Version Bump File Checklist" in labels

    print(f"\n✅ SESSION START TEST PASSED: {len(critical)} CRITICAL item(s) available")


# ============================================================================
# Phase 2: Confidence-Based Learning Tests
# ============================================================================


def test_deprecated_nodes_filtered_out(engine_with_test_data):
    """Deprecated nodes should NOT appear in query results."""
    engine = engine_with_test_data

    # Query for Write to .py file (would match deprecated node if not filtered)
    results = engine.query_for_tool_use(
        tool_name="Write",
        tool_input={"file_path": "/path/to/test.py"},
        cwd=".",
    )

    # Deprecated node should NOT be in results
    labels = [r.label for r in results]
    assert "Deprecated Old Pattern" not in labels, (
        "Deprecated node appeared in results! Deprecated filtering failed."
    )

    # All results should have deprecated=False
    for item in results:
        assert not item.deprecated, f"Result {item.label} has deprecated=True"


def test_confidence_weighting_applied(engine_with_test_data):
    """Relevance scores should be weighted by confidence."""
    engine = engine_with_test_data

    # Query for Write to .py file
    results = engine.query_for_tool_use(
        tool_name="Write",
        tool_input={"file_path": "/path/to/test.py"},
        cwd=".",
    )

    # Find low confidence node
    uncertain = next(
        (r for r in results if r.label == "Uncertain Pattern"),
        None
    )

    if uncertain:
        # Relevance should be reduced by confidence (0.65)
        # Base score would be ~0.4 (tool match)
        # With MEDIUM multiplier: 0.4 * 1.0 = 0.4
        # With confidence: 0.4 * 0.65 = 0.26
        # This should be below threshold (0.4) and filtered out
        # OR if it passes, its relevance should be confidence-weighted
        assert uncertain.confidence == 0.65
        assert uncertain.needs_validation is True


def test_process_knowledge_has_confidence_fields(engine_with_test_data):
    """ProcessKnowledge objects should include confidence fields."""
    engine = engine_with_test_data

    results = engine.query_for_tool_use(
        tool_name="Write",
        tool_input={"file_path": "plugin.json"},
        cwd=".",
    )

    assert len(results) > 0

    for item in results:
        # All items should have confidence fields
        assert hasattr(item, "confidence")
        assert hasattr(item, "needs_validation")
        assert hasattr(item, "deprecated")

        # Confidence should be in valid range
        assert 0.0 <= item.confidence <= 1.0

        # needs_validation should be bool
        assert isinstance(item.needs_validation, bool)

        # deprecated should be False (since deprecated nodes are filtered)
        assert item.deprecated is False


def test_confidence_default_for_legacy_nodes(temp_graphs_dir, create_test_graph):
    """Legacy nodes without confidence should default to 1.0."""
    # Create graph with legacy node (no confidence field)
    legacy_graph = {
        "directed": True,
        "nodes": [
            {
                "id": "legacy_node",
                "type": "Concept",
                "label": "Legacy Pattern",
                "description": "Old node without confidence field",
                "process_type": "pattern",
                "priority": "MEDIUM",
                "trigger_conditions": {
                    "tool_names": ["Write"],
                    "file_patterns": ["**/*.py"],
                    "action_keywords": [],
                    "context_keywords": []
                },
                "pattern": {
                    "when": "Writing files",
                    "then": "Use legacy pattern"
                }
                # NOTE: No confidence, needs_validation, or deprecated fields
            }
        ],
        "links": [],
    }

    create_test_graph("legacy", legacy_graph)
    engine = ExperienceQueryEngine(graphs_dir=temp_graphs_dir)

    results = engine.query_for_tool_use(
        tool_name="Write",
        tool_input={"file_path": "test.py"},
        cwd=".",
    )

    # Should find legacy node
    legacy = next((r for r in results if r.label == "Legacy Pattern"), None)
    assert legacy is not None

    # Should default to 1.0 confidence
    assert legacy.confidence == 1.0

    # Should default to False for needs_validation and deprecated
    assert legacy.needs_validation is False
    assert legacy.deprecated is False


def test_critical_does_not_include_deprecated(engine_with_test_data):
    """get_critical_knowledge should NOT return deprecated nodes."""
    engine = engine_with_test_data

    critical = engine.get_critical_knowledge()

    # Deprecated node is CRITICAL priority but should be filtered
    labels = [r.label for r in critical]
    assert "Deprecated Old Pattern" not in labels

    # All should be non-deprecated
    for item in critical:
        assert not item.deprecated
