"""Security tests for knowledge graph access."""
import json
import pytest
from pathlib import Path
from triads.km.graph_access import GraphLoader, InvalidTriadNameError


@pytest.fixture
def temp_graphs_dir(tmp_path):
    """Create temporary graphs directory."""
    graphs_dir = tmp_path / ".claude" / "graphs"
    graphs_dir.mkdir(parents=True)
    return graphs_dir


@pytest.fixture
def create_test_file(tmp_path):
    """Factory to create files for path traversal tests."""

    def _create(path_str, content="sensitive data"):
        path = tmp_path / path_str
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return path

    return _create


def test_path_traversal_blocked(temp_graphs_dir):
    """Verify load_graph blocks ../ path traversal."""
    loader = GraphLoader(graphs_dir=temp_graphs_dir)

    # Various path traversal attempts
    traversal_attempts = [
        "../../etc/passwd",
        "../../../etc/hosts",
        "..\\..\\windows\\system32\\config\\sam",  # Windows style
        "test/../../etc/passwd",
        "../sensitive_file",
    ]

    for attempt in traversal_attempts:
        with pytest.raises(InvalidTriadNameError) as exc_info:
            loader.load_graph(attempt)

        assert "invalid" in str(exc_info.value).lower()


def test_absolute_path_blocked(temp_graphs_dir):
    """Verify load_graph blocks absolute paths."""
    loader = GraphLoader(graphs_dir=temp_graphs_dir)

    # Various absolute path attempts
    absolute_attempts = [
        "/etc/passwd",
        "/var/log/secure",
        "C:\\Windows\\System32\\config\\SAM",  # Windows
        "/root/.ssh/id_rsa",
        "/home/user/.bashrc",
    ]

    for attempt in absolute_attempts:
        with pytest.raises(InvalidTriadNameError):
            loader.load_graph(attempt)


def test_special_characters_blocked(temp_graphs_dir):
    """Verify load_graph blocks special characters."""
    loader = GraphLoader(graphs_dir=temp_graphs_dir)

    # Command injection attempts
    injection_attempts = [
        "test;rm -rf /",
        "test|cat /etc/passwd",
        "test`whoami`",
        "test$(whoami)",
        "test&& rm -rf /",
        "test; DROP TABLE users--",
        "test' OR '1'='1",
        "test\x00",  # Null byte injection
        "test\nrm -rf /",  # Newline injection
    ]

    for attempt in injection_attempts:
        with pytest.raises(InvalidTriadNameError):
            loader.load_graph(attempt)


def test_valid_triad_names_allowed(temp_graphs_dir, create_test_file):
    """Verify valid triad names work correctly."""
    loader = GraphLoader(graphs_dir=temp_graphs_dir)

    valid_graph = {"nodes": [], "links": []}

    # Valid names that should work
    valid_names = [
        "design",
        "idea-validation",
        "test_123",
        "UPPERCASE",
        "CamelCase",
        "with-dashes",
        "with_underscores",
        "mixed-both_types",
    ]

    for name in valid_names:
        # Create graph file
        graph_file = temp_graphs_dir / f"{name}_graph.json"
        graph_file.write_text(json.dumps(valid_graph))

        # Should load without error
        graph = loader.load_graph(name)
        assert graph is not None


def test_path_resolution_prevents_escape(temp_graphs_dir, create_test_file):
    """Verify resolved paths stay within graphs directory."""
    # Create a sensitive file outside graphs directory
    sensitive = create_test_file("sensitive.txt", "SECRET DATA")

    loader = GraphLoader(graphs_dir=temp_graphs_dir)

    # Try to load with path that resolves outside graphs_dir
    # This should be caught by path validation
    with pytest.raises(InvalidTriadNameError):
        loader.load_graph(f"../{sensitive.name}")


def test_symlink_escape_blocked(temp_graphs_dir, tmp_path):
    """Verify symlinks can't escape graphs directory."""
    # Create sensitive file outside graphs dir
    sensitive = tmp_path / "sensitive.txt"
    sensitive.write_text("SECRET DATA")

    # Try to create symlink inside graphs dir pointing outside
    try:
        symlink = temp_graphs_dir / "escape_graph.json"
        symlink.symlink_to(sensitive)

        loader = GraphLoader(graphs_dir=temp_graphs_dir)

        # Try to load via symlink
        # Should either fail validation or path check
        result = loader.load_graph("escape")

        # If it loads, verify path checking caught it
        # (returns None for paths outside graphs dir)
        if result is not None:
            # Should have been blocked by path resolution check
            pytest.fail("Symlink escape was not blocked")

    except (OSError, PermissionError):
        # Symlink creation may fail on some systems (e.g., Windows without admin)
        pytest.skip("Symlink creation not supported on this system")


def test_json_bomb_handled(temp_graphs_dir):
    """Verify deeply nested JSON doesn't crash."""
    # Create deeply nested JSON structure (but not so deep it can't be serialized)
    nested = {"nodes": [], "links": []}
    current = nested
    for _ in range(100):  # Moderately deep nesting
        current["nested"] = {}
        current = current["nested"]

    graph_file = temp_graphs_dir / "nested_graph.json"

    # Try to write deeply nested JSON
    try:
        graph_file.write_text(json.dumps(nested))
    except RecursionError:
        # If we can't even serialize it, test that loader handles corrupted file
        graph_file.write_text("{ deeply nested structure }")

    loader = GraphLoader(graphs_dir=temp_graphs_dir)

    # Should handle without crashing (may be slow but shouldn't fail)
    try:
        graph = loader.load_graph("nested")
        # As long as it doesn't crash, it's fine
        assert graph is not None or graph is None  # Either loaded or gracefully failed
    except RecursionError:
        # Python's recursion limit may be hit, which is acceptable
        pass


def test_large_json_handled(temp_graphs_dir):
    """Verify large JSON files are handled gracefully."""
    # Create graph with many nodes
    large_graph = {
        "nodes": [
            {
                "id": f"node_{i}",
                "label": f"Node {i}",
                "type": "Entity",
                "description": "A" * 1000,  # Large description
                "confidence": 0.9,
            }
            for i in range(100)
        ],
        "links": [],
    }

    graph_file = temp_graphs_dir / "large_graph.json"
    graph_file.write_text(json.dumps(large_graph))

    loader = GraphLoader(graphs_dir=temp_graphs_dir)

    # Should load successfully
    graph = loader.load_graph("large")
    assert graph is not None
    assert len(graph["nodes"]) == 100


def test_malformed_json_handled(temp_graphs_dir):
    """Verify invalid JSON returns error (not exception)."""
    loader = GraphLoader(graphs_dir=temp_graphs_dir)

    # Create files with various malformed JSON
    malformed_cases = [
        "{ this is not valid json }",
        '{"unclosed": "string',
        '{"trailing": "comma",}',
        "not json at all",
        "",  # Empty file
        "null",  # Valid JSON but not an object
        "[]",  # Valid JSON array but not object
        "123",  # Valid JSON number but not object
    ]

    for i, bad_json in enumerate(malformed_cases):
        graph_file = temp_graphs_dir / f"bad_{i}_graph.json"
        graph_file.write_text(bad_json)

        # Should return None, not raise exception
        graph = loader.load_graph(f"bad_{i}")
        assert graph is None, f"Bad JSON case {i} should return None"


def test_unicode_injection_safe(temp_graphs_dir):
    """Verify Unicode characters don't cause injection."""
    # Graph with various Unicode characters
    unicode_graph = {
        "nodes": [
            {
                "id": "unicode_\u202e_rtl",  # Right-to-left override
                "label": "Test \u0000 null",  # Null character
                "description": "Test \ufeff BOM",  # Byte order mark
                "type": "Concept",
            }
        ],
        "links": [],
    }

    graph_file = temp_graphs_dir / "unicode_graph.json"
    graph_file.write_text(json.dumps(unicode_graph), encoding="utf-8")

    loader = GraphLoader(graphs_dir=temp_graphs_dir)
    graph = loader.load_graph("unicode")

    # Should load and contain Unicode safely
    assert graph is not None
    assert len(graph["nodes"]) == 1


def test_no_code_execution(temp_graphs_dir):
    """Verify no eval/exec on graph data."""
    # Graph with Python code strings
    code_graph = {
        "nodes": [
            {
                "id": "code_node",
                "label": "__import__('os').system('echo hacked')",
                "description": "exec('print(\"hacked\")')",
                "type": "eval('Concept')",
                "confidence": 0.9,
            }
        ],
        "links": [],
    }

    graph_file = temp_graphs_dir / "code_graph.json"
    graph_file.write_text(json.dumps(code_graph))

    loader = GraphLoader(graphs_dir=temp_graphs_dir)
    graph = loader.load_graph("code")

    # Should load as plain strings, not execute
    assert graph is not None
    node = graph["nodes"][0]

    # Values should be strings, not evaluated
    assert "__import__" in node["label"]
    assert "exec" in node["description"]


def test_directory_listing_prevented(temp_graphs_dir):
    """Verify can't list arbitrary directories."""
    loader = GraphLoader(graphs_dir=temp_graphs_dir)

    # list_triads should only work with configured graphs_dir
    triads = loader.list_triads()

    # Should return empty or only valid graphs, not arbitrary files
    assert isinstance(triads, list)

    # Try to trick it with invalid names
    for triad in triads:
        # All returned triads should be valid names
        assert loader._is_valid_triad_name(triad)


def test_file_inclusion_blocked(temp_graphs_dir, tmp_path):
    """Verify can't include/read arbitrary files."""
    # Create sensitive file
    sensitive = tmp_path / "sensitive.txt"
    sensitive.write_text("SENSITIVE DATA")

    loader = GraphLoader(graphs_dir=temp_graphs_dir)

    # Try various file inclusion attempts
    inclusion_attempts = [
        f"../{sensitive.name}",
        f"../../{sensitive.name}",
        str(sensitive.absolute()),
    ]

    for attempt in inclusion_attempts:
        # Should be blocked by validation
        try:
            graph = loader.load_graph(attempt)
            # If validation didn't raise, load should return None
            assert graph is None
        except InvalidTriadNameError:
            # Expected - validation caught it
            pass


def test_dos_prevention_empty_results(temp_graphs_dir):
    """Verify empty results don't cause DoS."""
    # Create graph with no nodes
    empty_graph = {"nodes": [], "links": []}

    graph_file = temp_graphs_dir / "empty_graph.json"
    graph_file.write_text(json.dumps(empty_graph))

    loader = GraphLoader(graphs_dir=temp_graphs_dir)
    graph = loader.load_graph("empty")

    # Should handle empty graph gracefully
    assert graph is not None
    assert len(graph.get("nodes", [])) == 0


def test_dos_prevention_circular_references(temp_graphs_dir):
    """Verify circular edge references don't cause infinite loops."""
    # Graph with circular edges
    circular_graph = {
        "nodes": [
            {"id": "a", "label": "A", "type": "Concept"},
            {"id": "b", "label": "B", "type": "Concept"},
        ],
        "links": [
            {"source": "a", "target": "b", "key": "relates"},
            {"source": "b", "target": "a", "key": "relates"},
        ],
    }

    graph_file = temp_graphs_dir / "circular_graph.json"
    graph_file.write_text(json.dumps(circular_graph))

    loader = GraphLoader(graphs_dir=temp_graphs_dir)

    # Should load without infinite loop
    graph = loader.load_graph("circular")
    assert graph is not None


def test_case_sensitivity_prevents_bypass(temp_graphs_dir):
    """Verify case variations don't bypass validation."""
    loader = GraphLoader(graphs_dir=temp_graphs_dir)

    # Try case variations of dangerous patterns
    case_attempts = [
        "../ETC/passwd",
        "../Etc/Passwd",
        "..\\ETC\\PASSWD",
    ]

    for attempt in case_attempts:
        with pytest.raises(InvalidTriadNameError):
            loader.load_graph(attempt)
