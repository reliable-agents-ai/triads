"""Tests for atomic graph write operations.

This module tests that graph saves use atomic file operations with
locking to prevent corruption from concurrent writes and crashes.

RED Phase: These tests should FAIL initially (feature not implemented yet).
"""

import json
import multiprocessing
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from triads.km.graph_access import GraphLoader


# Module-level worker function for multiprocessing tests
def _write_graph_worker(graphs_dir, process_id):
    """Worker function to write graph data in separate process."""
    loader = GraphLoader(graphs_dir=graphs_dir)
    graph_data = {
        "nodes": [{
            "id": f"node_{process_id}",
            "label": f"Node {process_id}",
            "type": "concept"  # Added type field for schema validation
        }],
        "edges": []
    }
    # Try to write 10 times
    for i in range(10):
        loader.save_graph("test", graph_data)
        time.sleep(0.001)  # Small delay to encourage race conditions


class TestAtomicWrites:
    """Test atomic file operations for graph writes."""

    def test_save_graph_uses_atomic_write(self, tmp_path):
        """Verify save_graph uses atomic_write_json from file_operations.

        RED: Should FAIL - Currently uses plain json.dump()
        """
        with patch('triads.km.graph_access.loader.atomic_write_json') as mock_atomic:
            loader = GraphLoader(graphs_dir=tmp_path)
            graph_data = {"nodes": [], "edges": []}

            # This will fail because save_graph doesn't exist yet
            # or doesn't use atomic_write_json
            result = loader.save_graph("test", graph_data)

            # Verify atomic_write_json was called
            mock_atomic.assert_called_once()
            assert result is True

    def test_save_graph_uses_file_locking(self, tmp_path):
        """Verify save_graph uses file locking parameter.

        RED: Should FAIL - No locking parameter passed
        """
        with patch('triads.km.graph_access.loader.atomic_write_json') as mock_atomic:
            loader = GraphLoader(graphs_dir=tmp_path)
            graph_data = {"nodes": [], "edges": []}

            loader.save_graph("test", graph_data)

            # Verify lock=True was passed
            call_kwargs = mock_atomic.call_args[1]
            assert call_kwargs.get('lock') is True


class TestConcurrentWrites:
    """Test that concurrent writes don't corrupt graphs."""

    def test_concurrent_writes_dont_corrupt_graph(self, tmp_path):
        """Verify concurrent writes to same graph don't cause corruption.

        RED: Should FAIL - Plain json.dump allows race conditions
        """
        # Start 3 processes writing concurrently
        processes = []
        for i in range(3):
            p = multiprocessing.Process(target=_write_graph_worker, args=(tmp_path, i))
            p.start()
            processes.append(p)

        # Wait for all to complete
        for p in processes:
            p.join()

        # Verify graph is valid JSON (not corrupted)
        graph_file = tmp_path / "test_graph.json"
        assert graph_file.exists()

        # This will fail with plain json.dump due to race conditions
        with open(graph_file) as f:
            data = json.load(f)  # Should not raise JSONDecodeError

        assert isinstance(data, dict)
        assert "nodes" in data
        assert "edges" in data


class TestCrashResistance:
    """Test that crashes during write don't corrupt graphs."""

    def test_crash_during_write_preserves_original(self, tmp_path):
        """Verify crash mid-write doesn't corrupt existing file.

        RED: Should FAIL - Plain json.dump can leave partial writes
        """
        loader = GraphLoader(graphs_dir=tmp_path)

        # Create initial graph
        initial_data = {
            "nodes": [{"id": "node1", "label": "Initial"}],
            "edges": []
        }
        graph_file = tmp_path / "test_graph.json"
        graph_file.write_text(json.dumps(initial_data, indent=2))

        # Simulate crash during write by patching json.dump where it's used
        with patch('triads.utils.file_operations.json.dump', side_effect=IOError("Simulated crash")):
            new_data = {
                "nodes": [{"id": "node2", "label": "New"}],
                "edges": []
            }

            # Attempt to save (will crash)
            # Note: With atomic writes, this should NOT raise (returns False instead)
            result = loader.save_graph("test", new_data)
            assert result is False  # Atomic write fails gracefully

        # Verify original file is intact (not corrupted or partially written)
        with open(graph_file) as f:
            data = json.load(f)

        # With atomic writes, original data should be preserved
        # With plain json.dump, file might be corrupted or empty
        assert data == initial_data

    def test_successful_write_after_failed_write(self, tmp_path):
        """Verify system recovers from failed write attempt.

        RED: Should FAIL - Need atomic rename for recovery
        """
        loader = GraphLoader(graphs_dir=tmp_path)
        graph_file = tmp_path / "test_graph.json"

        # Create initial graph with valid data
        initial_data = {"nodes": [], "edges": []}
        graph_file.write_text(json.dumps(initial_data))

        # First write fails (using valid data that fails during actual write)
        with patch('triads.utils.file_operations.json.dump', side_effect=IOError("Disk full")):
            result = loader.save_graph("test", {
                "nodes": [{"id": "fail", "label": "Fail", "type": "concept"}],
                "edges": []
            })
            assert result is False  # Atomic write fails gracefully

        # Second write should succeed
        success_data = {
            "nodes": [{"id": "success", "label": "Success", "type": "concept"}],
            "edges": []
        }
        result = loader.save_graph("test", success_data)

        assert result is True
        with open(graph_file) as f:
            data = json.load(f)
        assert data == success_data


class TestAtomicWriteConfiguration:
    """Test atomic write configuration and parameters."""

    def test_save_graph_uses_json_indent(self, tmp_path):
        """Verify saved graph uses proper JSON indentation.

        RED: Should FAIL - Need to verify indent parameter
        """
        with patch('triads.km.graph_access.loader.atomic_write_json') as mock_atomic:
            loader = GraphLoader(graphs_dir=tmp_path)
            graph_data = {"nodes": [], "edges": []}

            loader.save_graph("test", graph_data)

            # Verify indent parameter
            call_kwargs = mock_atomic.call_args[1]
            assert call_kwargs.get('indent') == 2

    def test_save_graph_returns_false_on_failure(self, tmp_path):
        """Verify save_graph returns False when write fails.

        RED: Should FAIL - Need proper error handling
        """
        loader = GraphLoader(graphs_dir=tmp_path)

        with patch('triads.km.graph_access.loader.atomic_write_json', side_effect=OSError("Write failed")):
            result = loader.save_graph("test", {"nodes": [], "edges": []})

        assert result is False


# Run these tests to verify they FAIL (RED phase)
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
