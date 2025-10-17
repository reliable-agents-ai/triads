"""Tests for safe_io module - hook I/O utilities."""

import io
import json
import sys
import tempfile
from pathlib import Path

import pytest

from triads.hooks.safe_io import (
    safe_load_json_file,
    safe_save_json_file,
    safe_load_json_stdin,
    validate_json_structure,
    safe_update_json_field,
)


# ============================================================================
# Test safe_load_json_file
# ============================================================================

def test_safe_load_json_file_success():
    """Test successful JSON file loading."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "test.json"
        data = {"key": "value", "number": 42}

        # Write test file
        with open(file_path, 'w') as f:
            json.dump(data, f)

        # Load with safe_load_json_file
        result = safe_load_json_file(file_path)

        assert result == data


def test_safe_load_json_file_string_path():
    """Test loading with string path instead of Path object."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = str(Path(tmpdir) / "test.json")
        data = {"test": True}

        with open(file_path, 'w') as f:
            json.dump(data, f)

        result = safe_load_json_file(file_path)

        assert result == data


def test_safe_load_json_file_not_found():
    """Test loading non-existent file returns default."""
    result = safe_load_json_file("/nonexistent/path/file.json")

    assert result is None


def test_safe_load_json_file_custom_default():
    """Test loading non-existent file returns custom default."""
    default = {"nodes": [], "links": []}
    result = safe_load_json_file("/nonexistent/path/file.json", default=default)

    assert result == default


def test_safe_load_json_file_invalid_json(capsys):
    """Test loading invalid JSON returns default and logs error."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "invalid.json"

        # Write invalid JSON
        with open(file_path, 'w') as f:
            f.write("{ invalid json }")

        result = safe_load_json_file(file_path, default={})

        assert result == {}

        # Check error was logged to stderr
        captured = capsys.readouterr()
        assert "Invalid JSON" in captured.err


def test_safe_load_json_file_path_traversal(capsys):
    """Test path traversal attempt is safely handled."""
    # Attempt to load /etc/passwd via path traversal
    result = safe_load_json_file("../../../etc/passwd", default=None)

    # Should return default (file doesn't contain valid JSON)
    assert result is None


def test_safe_load_json_file_permission_error(capsys):
    """Test permission error is handled gracefully."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "test.json"

        # Create file and make it unreadable
        with open(file_path, 'w') as f:
            json.dump({"test": True}, f)

        file_path.chmod(0o000)  # Remove all permissions

        try:
            result = safe_load_json_file(file_path, default={})

            assert result == {}

            # Check error was logged
            captured = capsys.readouterr()
            assert "Permission denied" in captured.err or "Error loading" in captured.err

        finally:
            # Restore permissions for cleanup
            file_path.chmod(0o644)


# ============================================================================
# Test safe_save_json_file
# ============================================================================

def test_safe_save_json_file_success():
    """Test successful JSON file saving."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "test.json"
        data = {"key": "value", "nested": {"a": 1, "b": 2}}

        success = safe_save_json_file(file_path, data)

        assert success is True
        assert file_path.exists()

        # Verify content
        with open(file_path, 'r') as f:
            loaded = json.load(f)
            assert loaded == data


def test_safe_save_json_file_string_path():
    """Test saving with string path instead of Path object."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = str(Path(tmpdir) / "test.json")
        data = {"test": True}

        success = safe_save_json_file(file_path, data)

        assert success is True
        assert Path(file_path).exists()


def test_safe_save_json_file_creates_parents():
    """Test saving creates parent directories automatically."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "subdir" / "nested" / "test.json"
        data = {"test": True}

        success = safe_save_json_file(file_path, data)

        assert success is True
        assert file_path.exists()
        assert file_path.parent.exists()


def test_safe_save_json_file_no_create_parents():
    """Test saving fails gracefully when parent doesn't exist and create_parents=False."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "nonexistent" / "test.json"
        data = {"test": True}

        success = safe_save_json_file(file_path, data, create_parents=False)

        assert success is False
        assert not file_path.exists()


def test_safe_save_json_file_atomic_write():
    """Test atomic write - no corrupted file on crash."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "test.json"

        # Write initial data
        initial_data = {"version": 1}
        safe_save_json_file(file_path, initial_data)

        # Verify initial save
        assert file_path.exists()

        # Now save new data
        new_data = {"version": 2, "updated": True}
        success = safe_save_json_file(file_path, new_data)

        assert success is True

        # File should contain new data (atomic replace worked)
        with open(file_path, 'r') as f:
            loaded = json.load(f)
            assert loaded == new_data

        # No temporary files left behind
        temp_files = list(file_path.parent.glob(".tmp_*.json"))
        assert len(temp_files) == 0


def test_safe_save_json_file_non_serializable(capsys):
    """Test saving non-serializable data fails gracefully."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "test.json"

        # Create non-serializable object
        class NonSerializable:
            pass

        data = {"obj": NonSerializable()}

        success = safe_save_json_file(file_path, data)

        assert success is False
        assert not file_path.exists()

        # Check error was logged
        captured = capsys.readouterr()
        assert "not JSON-serializable" in captured.err


def test_safe_save_json_file_permission_error(capsys):
    """Test permission error is handled gracefully."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Make directory read-only
        tmpdir_path = Path(tmpdir)
        tmpdir_path.chmod(0o444)

        file_path = tmpdir_path / "test.json"
        data = {"test": True}

        try:
            success = safe_save_json_file(file_path, data)

            assert success is False

            # Check error was logged
            captured = capsys.readouterr()
            assert "Permission denied" in captured.err or "Error saving" in captured.err

        finally:
            # Restore permissions for cleanup
            tmpdir_path.chmod(0o755)


def test_safe_save_json_file_custom_indent():
    """Test saving with custom indentation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "test.json"
        data = {"a": 1, "b": 2}

        # Save with indent=4
        safe_save_json_file(file_path, data, indent=4)

        # Read raw content
        content = file_path.read_text()

        # Should have 4-space indentation
        assert '    "a":' in content or '    "b":' in content


# ============================================================================
# Test safe_load_json_stdin
# ============================================================================

def test_safe_load_json_stdin_success(monkeypatch):
    """Test successful JSON loading from stdin."""
    data = {"tool_name": "Write", "tool_input": {"file_path": "test.py"}}
    json_string = json.dumps(data)

    # Mock stdin
    monkeypatch.setattr('sys.stdin', io.StringIO(json_string))

    result = safe_load_json_stdin()

    assert result == data


def test_safe_load_json_stdin_invalid_json(monkeypatch, capsys):
    """Test invalid JSON on stdin returns default."""
    # Mock stdin with invalid JSON
    monkeypatch.setattr('sys.stdin', io.StringIO("{ invalid json }"))

    result = safe_load_json_stdin(default={})

    assert result == {}

    # Check error was logged
    captured = capsys.readouterr()
    assert "Invalid JSON on stdin" in captured.err


def test_safe_load_json_stdin_custom_default(monkeypatch, capsys):
    """Test custom default on stdin error."""
    default = {"error": True}

    # Mock stdin with invalid JSON
    monkeypatch.setattr('sys.stdin', io.StringIO("not json"))

    result = safe_load_json_stdin(default=default)

    assert result == default


# ============================================================================
# Test validate_json_structure
# ============================================================================

def test_validate_json_structure_valid():
    """Test validation of valid JSON structure."""
    data = {"nodes": [], "links": [], "_meta": {}}
    required_keys = ["nodes", "links"]

    valid, error = validate_json_structure(data, required_keys)

    assert valid is True
    assert error is None


def test_validate_json_structure_missing_keys():
    """Test validation detects missing required keys."""
    data = {"nodes": []}
    required_keys = ["nodes", "links", "_meta"]

    valid, error = validate_json_structure(data, required_keys)

    assert valid is False
    assert "Missing required keys" in error
    assert "links" in error
    assert "_meta" in error


def test_validate_json_structure_not_dict():
    """Test validation detects non-dictionary data."""
    data = ["not", "a", "dict"]
    required_keys = ["key"]

    valid, error = validate_json_structure(data, required_keys)

    assert valid is False
    assert "must be a dictionary" in error


def test_validate_json_structure_empty_required():
    """Test validation with no required keys."""
    data = {"anything": "goes"}
    required_keys = []

    valid, error = validate_json_structure(data, required_keys)

    assert valid is True
    assert error is None


# ============================================================================
# Test safe_update_json_field
# ============================================================================

def test_safe_update_json_field_top_level():
    """Test updating top-level field."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "test.json"
        initial_data = {"version": "1.0.0", "name": "test"}

        # Save initial data
        safe_save_json_file(file_path, initial_data)

        # Update version field
        success = safe_update_json_field(file_path, ["version"], "2.0.0")

        assert success is True

        # Verify update
        result = safe_load_json_file(file_path)
        assert result["version"] == "2.0.0"
        assert result["name"] == "test"  # Other fields unchanged


def test_safe_update_json_field_nested():
    """Test updating nested field."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "test.json"
        initial_data = {
            "_meta": {
                "created_at": "2025-01-01",
                "updated_at": "2025-01-01"
            }
        }

        safe_save_json_file(file_path, initial_data)

        # Update nested field
        success = safe_update_json_field(
            file_path,
            ["_meta", "updated_at"],
            "2025-10-17"
        )

        assert success is True

        # Verify update
        result = safe_load_json_file(file_path)
        assert result["_meta"]["updated_at"] == "2025-10-17"
        assert result["_meta"]["created_at"] == "2025-01-01"  # Other fields unchanged


def test_safe_update_json_field_creates_nested():
    """Test updating creates missing nested fields."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "test.json"
        initial_data = {"existing": "data"}

        safe_save_json_file(file_path, initial_data)

        # Update field that doesn't exist yet
        success = safe_update_json_field(
            file_path,
            ["new", "nested", "field"],
            "value"
        )

        assert success is True

        # Verify nested structure was created
        result = safe_load_json_file(file_path)
        assert result["new"]["nested"]["field"] == "value"
        assert result["existing"] == "data"


def test_safe_update_json_field_nonexistent_file():
    """Test updating nonexistent file fails gracefully."""
    success = safe_update_json_field(
        "/nonexistent/file.json",
        ["field"],
        "value"
    )

    assert success is False


# ============================================================================
# Integration Tests
# ============================================================================

def test_load_save_roundtrip():
    """Test complete load-modify-save cycle."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "graph.json"

        # Initial data
        graph = {
            "nodes": [
                {"id": "node1", "label": "Node 1"},
                {"id": "node2", "label": "Node 2"}
            ],
            "links": [],
            "_meta": {
                "created_at": "2025-10-17",
                "node_count": 2
            }
        }

        # Save
        assert safe_save_json_file(file_path, graph) is True

        # Load
        loaded = safe_load_json_file(file_path)
        assert loaded == graph

        # Modify
        loaded["nodes"].append({"id": "node3", "label": "Node 3"})
        loaded["_meta"]["node_count"] = 3

        # Save again
        assert safe_save_json_file(file_path, loaded) is True

        # Load and verify
        final = safe_load_json_file(file_path)
        assert len(final["nodes"]) == 3
        assert final["_meta"]["node_count"] == 3


def test_concurrent_write_safety():
    """Test that atomic writes prevent corruption."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "test.json"

        # Write initial data
        safe_save_json_file(file_path, {"version": 1})

        # Simulate concurrent writes (in reality, OS handles atomicity)
        success1 = safe_save_json_file(file_path, {"version": 2})
        success2 = safe_save_json_file(file_path, {"version": 3})

        assert success1 is True
        assert success2 is True

        # File should have valid JSON (last write wins)
        result = safe_load_json_file(file_path)
        assert result is not None
        assert "version" in result
        assert result["version"] in [2, 3]  # One of the writes succeeded


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
