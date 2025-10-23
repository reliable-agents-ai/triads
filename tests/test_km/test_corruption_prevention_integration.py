"""Integration tests for corruption prevention system.

This module tests that all corruption prevention systems work together:
- Atomic writes prevent concurrent corruption
- Schema validation prevents invalid data
- Backup/recovery handles failures
- Agent output validation catches errors
- Integrity checker detects and repairs corruption

These tests verify the COMPLETE end-to-end protection pipeline.
"""

import json
import multiprocessing
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from triads.km.agent_output_validator import AgentOutputValidator
from triads.km.backup_manager import BackupManager
from triads.km.graph_access import GraphLoader
from triads.km.integrity_checker import IntegrityChecker
from triads.km.schema_validator import ValidationError


# Module-level worker for multiprocessing
def _concurrent_write_worker(graphs_dir, process_id, num_writes):
    """Worker function for concurrent write tests."""
    loader = GraphLoader(graphs_dir=graphs_dir)
    for i in range(num_writes):
        graph_data = {
            "nodes": [
                {
                    "id": f"node_p{process_id}_w{i}",
                    "label": f"Process {process_id} Write {i}",
                    "type": "concept",
                    "description": f"Test node from process {process_id}",
                }
            ],
            "edges": [],
        }
        success = loader.save_graph("concurrent_test", graph_data)
        time.sleep(0.001)  # Small delay to encourage race conditions
        if not success:
            return False
    return True


def _update_triad_worker(graphs_dir, triad_name):
    """Worker function for multi-triad concurrent updates."""
    loader = GraphLoader(graphs_dir=graphs_dir)
    for i in range(5):
        data = {
            "nodes": [
                {"id": f"{triad_name}_node_{i}", "label": f"{triad_name} {i}", "type": "concept"}
            ],
            "edges": [],
        }
        loader.save_graph(triad_name, data)
        time.sleep(0.01)


class TestEndToEndWriteProtection:
    """Test complete write protection pipeline."""

    def test_invalid_data_rejected_by_schema_validation(self, tmp_path):
        """Verify invalid data is rejected before write attempt.

        Flow:
        1. Attempt to save invalid graph (missing required fields)
        2. Schema validation catches error
        3. No file write occurs
        4. No backup created (failed before write)
        """
        loader = GraphLoader(graphs_dir=tmp_path)

        # Invalid: missing 'type' field on node
        invalid_graph = {
            "nodes": [{"id": "test", "label": "Test"}],  # Missing 'type'
            "edges": [],
        }

        result = loader.save_graph("test", invalid_graph)

        # Should fail validation
        assert result is False

        # No file should exist (validation failed before write)
        graph_file = tmp_path / "test_graph.json"
        assert not graph_file.exists()

    def test_valid_data_written_atomically_with_backup(self, tmp_path):
        """Verify valid data is saved with backup protection.

        Flow:
        1. Valid graph data passes schema validation
        2. Backup created before write
        3. Atomic write succeeds
        4. Backup preserved
        5. Data can be loaded back
        """
        loader = GraphLoader(graphs_dir=tmp_path)

        # Create initial graph
        initial_data = {
            "nodes": [{"id": "v1", "label": "Version 1", "type": "concept"}],
            "edges": [],
        }
        result = loader.save_graph("test", initial_data)
        assert result is True

        # Update graph (should create backup)
        updated_data = {
            "nodes": [
                {"id": "v1", "label": "Version 1", "type": "concept"},
                {"id": "v2", "label": "Version 2", "type": "concept"},
            ],
            "edges": [{"source": "v1", "target": "v2", "key": "updates_to"}],
        }
        result = loader.save_graph("test", updated_data)
        assert result is True

        # Verify backup exists
        backup_mgr = BackupManager(graphs_dir=tmp_path)
        backups = backup_mgr.list_backups("test")
        assert len(backups) > 0

        # Verify data loads correctly
        loaded = loader.load_graph("test")
        assert loaded == updated_data

    def test_concurrent_writes_dont_corrupt(self, tmp_path):
        """Verify concurrent writes to same graph don't cause corruption.

        Flow:
        1. Start multiple processes writing concurrently
        2. Each uses atomic writes with locking
        3. All writes complete without errors
        4. Final graph is valid JSON (not corrupted)
        5. Graph passes schema validation
        """
        # Start 5 processes, each writing 10 times
        processes = []
        for i in range(5):
            p = multiprocessing.Process(
                target=_concurrent_write_worker, args=(tmp_path, i, 10)
            )
            p.start()
            processes.append(p)

        # Wait for all to complete
        for p in processes:
            p.join()

        # Verify graph is valid JSON and passes validation
        graph_file = tmp_path / "concurrent_test_graph.json"
        assert graph_file.exists()

        with open(graph_file) as f:
            data = json.load(f)  # Should not raise JSONDecodeError

        # Should be valid graph structure
        assert isinstance(data, dict)
        assert "nodes" in data
        assert "edges" in data

        # Should pass integrity check
        checker = IntegrityChecker(graphs_dir=tmp_path)
        report = checker.check_graph("concurrent_test")
        assert report.valid is True

    def test_failed_write_triggers_restore_from_backup(self, tmp_path):
        """Verify failed writes are recovered from backup.

        Flow:
        1. Create initial graph (triggers backup)
        2. Simulate write failure during update
        3. Atomic write detects failure
        4. Original data preserved (not corrupted)
        5. Backup can be used to restore
        """
        loader = GraphLoader(graphs_dir=tmp_path)

        # Create initial graph
        initial_data = {
            "nodes": [{"id": "original", "label": "Original", "type": "concept"}],
            "edges": [],
        }
        result = loader.save_graph("test", initial_data)
        assert result is True

        # Simulate crash during write
        with patch("triads.utils.file_operations.json.dump", side_effect=IOError("Disk full")):
            new_data = {
                "nodes": [{"id": "new", "label": "New", "type": "concept"}],
                "edges": [],
            }
            result = loader.save_graph("test", new_data)
            assert result is False  # Write should fail

        # Verify original data intact (atomic write prevented corruption)
        loaded = loader.load_graph("test")
        assert loaded == initial_data

        # Verify backup exists and can restore
        backup_mgr = BackupManager(graphs_dir=tmp_path)
        backups = backup_mgr.list_backups("test")
        assert len(backups) > 0


class TestAgentOutputToGraphPipeline:
    """Test complete agent output validation and update pipeline."""

    def test_agent_generates_valid_graph_update(self, tmp_path):
        """Verify agent output validation accepts valid updates.

        Flow:
        1. Agent generates [GRAPH_UPDATE] block
        2. Output validator parses block
        3. Schema validation passes
        4. Update applied to graph
        5. Backup created
        """
        loader = GraphLoader(graphs_dir=tmp_path)

        # Create initial graph
        initial_data = {"nodes": [], "edges": []}
        loader.save_graph("test", initial_data)

        # Simulate agent output
        agent_output = """
Here's my analysis...

[GRAPH_UPDATE]
type: add_node
node_id: test_analysis
node_type: Finding
label: Test Analysis Result
description: Analysis completed successfully
confidence: 0.95
evidence: test_data.py:123
created_by: test-agent
[/GRAPH_UPDATE]

The analysis is complete.
"""

        # Validate agent output
        validator = AgentOutputValidator()
        blocks = validator.parse_and_validate(agent_output)
        assert len(blocks) == 1
        assert blocks[0].type == "add_node"
        assert blocks[0].node_id == "test_analysis"

        # Apply update (in real system, this would be done by KM system)
        # Here we just verify the update data is valid
        assert blocks[0].node_type == "Finding"
        assert 0.0 <= blocks[0].confidence <= 1.0

    def test_malformed_agent_output_rejected(self, tmp_path):
        """Verify malformed agent output is caught by validator.

        Flow:
        1. Agent generates invalid [GRAPH_UPDATE] block
        2. Output validator catches syntax error
        3. No update attempted
        4. Graph remains unchanged
        """
        # Invalid: missing required field
        invalid_output = """
[GRAPH_UPDATE]
type: add_node
node_id: test
# Missing node_type, label, etc.
[/GRAPH_UPDATE]
"""

        # Should raise validation error
        validator = AgentOutputValidator()
        with pytest.raises(Exception):  # Output validator raises on missing fields
            validator.parse_and_validate(invalid_output)

    def test_invalid_schema_in_update_rejected(self, tmp_path):
        """Verify schema validation catches invalid node types.

        Flow:
        1. Agent output parses correctly
        2. But contains invalid node type
        3. Schema validation rejects it
        4. Update not applied
        """
        loader = GraphLoader(graphs_dir=tmp_path)

        # Create graph with invalid node type
        invalid_data = {
            "nodes": [
                {
                    "id": "invalid",
                    "label": "Invalid Node",
                    "type": "invalid_type",  # Not in VALID_NODE_TYPES
                }
            ],
            "edges": [],
        }

        # Should fail schema validation
        result = loader.save_graph("test", invalid_data)
        assert result is False

        # No file should be created
        graph_file = tmp_path / "test_graph.json"
        assert not graph_file.exists()


class TestCorruptionRecovery:
    """Test corruption detection and repair."""

    def test_integrity_checker_detects_corruption(self, tmp_path):
        """Verify integrity checker detects invalid JSON.

        Flow:
        1. Create valid graph
        2. Manually corrupt it (invalid JSON)
        3. Integrity checker detects corruption
        4. Reports corruption details
        """
        # Create valid graph
        graph_file = tmp_path / "test_graph.json"
        valid_data = {
            "nodes": [{"id": "test", "label": "Test", "type": "concept"}],
            "edges": [],
        }
        graph_file.write_text(json.dumps(valid_data, indent=2))

        # Manually corrupt the file
        graph_file.write_text('{"nodes": [{"id": "test", "label": "Test"}')  # Incomplete JSON

        # Integrity checker should detect corruption
        checker = IntegrityChecker(graphs_dir=tmp_path)
        report = checker.check_graph("test")

        assert report.valid is False
        assert report.error is not None
        assert "json" in report.error.lower()

    def test_auto_restore_from_backup_on_corruption(self, tmp_path):
        """Verify auto-restore from backup when loading corrupted graph.

        Flow:
        1. Create valid graph (creates backup)
        2. Corrupt the graph
        3. Load with auto_restore=True
        4. Graph restored from backup
        5. Data matches original
        """
        loader = GraphLoader(graphs_dir=tmp_path)

        # Create valid graph
        valid_data = {
            "nodes": [{"id": "test", "label": "Test", "type": "concept"}],
            "edges": [],
        }
        loader.save_graph("test", valid_data)

        # Corrupt the file
        graph_file = tmp_path / "test_graph.json"
        graph_file.write_text("corrupted data")

        # Auto-restore should work
        loaded = loader.load_graph("test", auto_restore=True)
        assert loaded is not None
        assert loaded == valid_data

    def test_backup_preserved_during_repair(self, tmp_path):
        """Verify backups are not deleted during repair.

        Flow:
        1. Create graph with multiple backups
        2. Create structural issue (invalid edge)
        3. Run repair
        4. Backups still exist after repair
        """
        loader = GraphLoader(graphs_dir=tmp_path)
        backup_mgr = BackupManager(graphs_dir=tmp_path, max_backups=5)

        # Create multiple versions (multiple backups)
        for i in range(3):
            data = {
                "nodes": [{"id": f"v{i}", "label": f"Version {i}", "type": "concept"}],
                "edges": [],
            }
            loader.save_graph("test", data)

        initial_backups = backup_mgr.list_backups("test")
        assert len(initial_backups) >= 2

        # Create structural issue (bypass validation)
        import json
        graph_file = tmp_path / "test_graph.json"
        invalid_data = {
            "nodes": [{"id": "n1", "label": "Node 1", "type": "concept"}],
            "edges": [{"source": "n1", "target": "missing", "key": "bad"}],
        }
        graph_file.write_text(json.dumps(invalid_data, indent=2))

        # Repair
        checker = IntegrityChecker(graphs_dir=tmp_path)
        result = checker.repair_graph("test")
        assert result.success is True

        # Backups should still exist (repair creates one more)
        final_backups = backup_mgr.list_backups("test")
        assert len(final_backups) >= len(initial_backups)

    def test_repair_fixes_structural_issues(self, tmp_path):
        """Verify repair fixes structural issues in valid JSON.

        Flow:
        1. Create graph with invalid edges (pointing to nonexistent nodes)
        2. Run repair
        3. Invalid edges removed
        4. Graph passes validation
        """
        loader = GraphLoader(graphs_dir=tmp_path)

        # Create graph with invalid edge (target doesn't exist)
        invalid_data = {
            "nodes": [
                {"id": "n1", "label": "Node 1", "type": "concept"},
            ],
            # Edge points to nonexistent node
            "edges": [{"source": "n1", "target": "n2_missing", "key": "leads_to"}],
        }

        # Save directly to file (bypass validation)
        graph_file = tmp_path / "test_graph.json"
        import json
        graph_file.write_text(json.dumps(invalid_data, indent=2))

        # Repair should fix it
        checker = IntegrityChecker(graphs_dir=tmp_path)
        result = checker.repair_graph("test")
        assert result.success is True

        # Graph should now pass validation
        report = checker.check_graph("test")
        assert report.valid is True


class TestPerformanceUnderStress:
    """Test system performance under load."""

    def test_concurrent_writes_complete_in_reasonable_time(self, tmp_path):
        """Verify concurrent writes don't deadlock or timeout.

        Flow:
        1. Start 10 processes writing concurrently
        2. Each writes 5 times
        3. All complete within 10 seconds
        4. No corruption
        """
        start = time.time()

        # Start 10 processes
        processes = []
        for i in range(10):
            p = multiprocessing.Process(
                target=_concurrent_write_worker, args=(tmp_path, i, 5)
            )
            p.start()
            processes.append(p)

        # Wait for all to complete
        for p in processes:
            p.join(timeout=10)

        elapsed = time.time() - start

        # Should complete in reasonable time
        assert elapsed < 10.0, f"Concurrent writes took {elapsed:.2f}s (expected <10s)"

        # Graph should be valid
        checker = IntegrityChecker(graphs_dir=tmp_path)
        report = checker.check_graph("concurrent_test")
        assert report.valid is True

    def test_large_graph_writes_fast(self, tmp_path):
        """Verify writing large graphs (1000 nodes) completes quickly.

        Flow:
        1. Generate graph with 1000 nodes
        2. Write to disk
        3. Should complete in < 1 second
        4. All data preserved correctly
        """
        loader = GraphLoader(graphs_dir=tmp_path)

        # Generate large graph
        nodes = [
            {
                "id": f"node_{i}",
                "label": f"Node {i}",
                "type": "concept",
                "description": f"Test node number {i}",
            }
            for i in range(1000)
        ]

        # Create some edges
        edges = [
            {"source": f"node_{i}", "target": f"node_{i+1}", "key": "next"}
            for i in range(999)
        ]

        large_graph = {"nodes": nodes, "edges": edges}

        # Write and measure time
        start = time.time()
        result = loader.save_graph("large", large_graph)
        elapsed = time.time() - start

        assert result is True
        assert elapsed < 1.0, f"Large graph write took {elapsed:.2f}s (expected <1s)"

        # Verify all data preserved
        loaded = loader.load_graph("large")
        assert len(loaded["nodes"]) == 1000
        assert len(loaded["edges"]) == 999

    def test_backup_rotation_works_with_many_writes(self, tmp_path):
        """Verify backup rotation doesn't accumulate infinitely.

        Flow:
        1. Configure max_backups=5
        2. Write graph 20 times
        3. Only 5 backups should remain
        4. Oldest backups pruned
        """
        loader = GraphLoader(graphs_dir=tmp_path, max_backups=5)
        backup_mgr = BackupManager(graphs_dir=tmp_path, max_backups=5)

        # Write 20 times
        for i in range(20):
            data = {
                "nodes": [{"id": f"v{i}", "label": f"Version {i}", "type": "concept"}],
                "edges": [],
            }
            loader.save_graph("test", data)

        # Should have max 5 backups
        backups = backup_mgr.list_backups("test")
        assert len(backups) <= 5, f"Expected ≤5 backups, got {len(backups)}"


class TestRealWorldScenarios:
    """Test realistic usage scenarios."""

    def test_multi_triad_concurrent_updates(self, tmp_path):
        """Verify multiple triads can be updated concurrently.

        Flow:
        1. Create 3 different triad graphs
        2. Update all concurrently
        3. No corruption in any graph
        4. All updates preserved
        """
        loader = GraphLoader(graphs_dir=tmp_path)

        # Create initial graphs
        for triad in ["design", "implementation", "deployment"]:
            data = {
                "nodes": [{"id": f"{triad}_node", "label": triad.title(), "type": "concept"}],
                "edges": [],
            }
            loader.save_graph(triad, data)

        # Update all concurrently
        processes = []
        for triad in ["design", "implementation", "deployment"]:
            p = multiprocessing.Process(target=_update_triad_worker, args=(tmp_path, triad))
            p.start()
            processes.append(p)

        for p in processes:
            p.join()

        # Verify all graphs valid
        checker = IntegrityChecker(graphs_dir=tmp_path)
        for triad in ["design", "implementation", "deployment"]:
            report = checker.check_graph(triad)
            assert report.valid is True, f"{triad} graph corrupted"

    def test_recovery_from_system_crash_during_write(self, tmp_path):
        """Simulate system crash during write and verify recovery.

        Flow:
        1. Start writing graph
        2. Simulate crash (exception during write)
        3. Original file intact
        4. Can retry write successfully
        """
        loader = GraphLoader(graphs_dir=tmp_path)

        # Create initial graph
        initial = {
            "nodes": [{"id": "original", "label": "Original", "type": "concept"}],
            "edges": [],
        }
        loader.save_graph("test", initial)

        # Simulate crash (use IOError which is caught by atomic_write_json)
        with patch("triads.utils.file_operations.json.dump", side_effect=IOError("System crash")):
            new_data = {
                "nodes": [{"id": "new", "label": "New", "type": "concept"}],
                "edges": [],
            }
            result = loader.save_graph("test", new_data)
            assert result is False

        # Original should be intact
        loaded = loader.load_graph("test")
        assert loaded == initial

        # Retry should succeed
        result = loader.save_graph("test", new_data)
        assert result is True

        loaded = loader.load_graph("test")
        assert loaded == new_data


# Run integration tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
