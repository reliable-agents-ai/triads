"""Tests for knowledge graph backup and recovery system.

This module tests automatic backup before writes and auto-restore on failure,
preventing data loss from corrupted writes or crashes.

RED Phase: These tests should FAIL initially (feature not implemented yet).
"""

import json
from pathlib import Path

import pytest

from triads.km.backup_manager import BackupManager
from triads.km.graph_access import GraphLoader


class TestBackupCreation:
    """Test automatic backup creation before writes."""

    def test_backup_created_before_save(self, tmp_path):
        """Verify backup is created before graph save operation.

        RED: Should FAIL - Backup system not implemented yet
        """
        loader = GraphLoader(graphs_dir=tmp_path)

        # Create initial graph
        initial_graph = {
            "nodes": [{"id": "node_1", "label": "Node 1", "type": "concept"}],
            "edges": []
        }
        loader.save_graph("test", initial_graph)

        # Modify and save again (should create backup)
        modified_graph = {
            "nodes": [
                {"id": "node_1", "label": "Node 1", "type": "concept"},
                {"id": "node_2", "label": "Node 2", "type": "concept"}
            ],
            "edges": []
        }
        loader.save_graph("test", modified_graph)

        # Verify backup was created
        backup_manager = BackupManager(graphs_dir=tmp_path)
        backups = backup_manager.list_backups("test")

        assert len(backups) >= 1

        # Verify backup contains original graph
        latest_backup = backups[0]
        backup_data = backup_manager.load_backup("test", latest_backup)
        assert len(backup_data["nodes"]) == 1

    def test_backup_has_timestamp_in_filename(self, tmp_path):
        """Verify backup filenames include timestamps.

        RED: Should FAIL - Backup naming not implemented yet
        """
        loader = GraphLoader(graphs_dir=tmp_path)
        backup_manager = BackupManager(graphs_dir=tmp_path)

        graph = {
            "nodes": [{"id": "node_1", "label": "Node 1", "type": "concept"}],
            "edges": []
        }

        # Save graph multiple times
        for i in range(3):
            graph["nodes"].append({
                "id": f"node_{i+2}",
                "label": f"Node {i+2}",
                "type": "concept"
            })
            loader.save_graph("test", graph)

        backups = backup_manager.list_backups("test")

        # Verify each backup has timestamp format
        for backup_name in backups:
            # Format: test_graph_YYYYMMDD_HHMMSS.json.backup
            assert "_graph_" in backup_name
            assert ".json.backup" in backup_name

    def test_no_backup_on_first_save(self, tmp_path):
        """Verify no backup created on first save (nothing to backup).

        RED: Should FAIL - Backup logic not implemented yet
        """
        loader = GraphLoader(graphs_dir=tmp_path)
        backup_manager = BackupManager(graphs_dir=tmp_path)

        graph = {
            "nodes": [{"id": "node_1", "label": "Node 1", "type": "concept"}],
            "edges": []
        }
        loader.save_graph("test", graph)

        backups = backup_manager.list_backups("test")

        # No backup on first save (nothing existed to backup)
        assert len(backups) == 0


class TestBackupRotation:
    """Test backup rotation (keeping last N backups)."""

    def test_backup_rotation_keeps_last_n(self, tmp_path):
        """Verify backup rotation keeps only last N backups.

        RED: Should FAIL - Rotation not implemented yet
        """
        # Configure backup manager to keep only 3 backups
        backup_manager = BackupManager(graphs_dir=tmp_path, max_backups=3)
        loader = GraphLoader(graphs_dir=tmp_path)

        # Create initial graph
        graph = {
            "nodes": [{"id": "node_1", "label": "Node 1", "type": "concept"}],
            "edges": []
        }
        loader.save_graph("test", graph)

        # Save 5 more times (should create 5 backups, keep only last 3)
        for i in range(5):
            graph["nodes"].append({
                "id": f"node_{i+2}",
                "label": f"Node {i+2}",
                "type": "concept"
            })
            loader.save_graph("test", graph)

        backups = backup_manager.list_backups("test")

        # Should have exactly 3 backups (rotated)
        assert len(backups) == 3

    def test_backup_rotation_keeps_newest(self, tmp_path):
        """Verify rotation keeps newest backups, deletes oldest.

        RED: Should FAIL - Rotation logic not implemented yet
        """
        backup_manager = BackupManager(graphs_dir=tmp_path, max_backups=2)
        loader = GraphLoader(graphs_dir=tmp_path)

        graph = {
            "nodes": [{"id": "node_1", "label": "Node 1", "type": "concept"}],
            "edges": []
        }
        loader.save_graph("test", graph)

        # Track which nodes were in each version
        versions = [1]

        for i in range(3):
            graph["nodes"].append({
                "id": f"node_{i+2}",
                "label": f"Node {i+2}",
                "type": "concept"
            })
            loader.save_graph("test", graph)
            versions.append(i+2)

        backups = backup_manager.list_backups("test")
        assert len(backups) == 2

        # Load backups and verify they're the newest
        backup_1 = backup_manager.load_backup("test", backups[0])
        backup_2 = backup_manager.load_backup("test", backups[1])

        # Newest backups should have more nodes
        assert len(backup_1["nodes"]) >= 3
        assert len(backup_2["nodes"]) >= 2


class TestAutoRestore:
    """Test automatic restore on write failure."""

    def test_restore_on_validation_failure(self, tmp_path):
        """Verify auto-restore when validation fails during save.

        RED: Should FAIL - Auto-restore not implemented yet
        """
        loader = GraphLoader(graphs_dir=tmp_path)

        # Create valid initial graph
        valid_graph = {
            "nodes": [{"id": "node_1", "label": "Node 1", "type": "concept"}],
            "edges": []
        }
        loader.save_graph("test", valid_graph)

        # Try to save invalid graph (should fail and restore)
        invalid_graph = {
            "nodes": [{"id": "node_2"}],  # Missing required fields
            "edges": []
        }

        result = loader.save_graph("test", invalid_graph)

        # Save should fail
        assert result is False

        # Graph should still be valid original
        current_graph = loader.load_graph("test")
        assert len(current_graph["nodes"]) == 1
        assert current_graph["nodes"][0]["id"] == "node_1"

    def test_restore_on_file_corruption(self, tmp_path):
        """Verify auto-restore when file write is corrupted.

        RED: Should FAIL - Corruption detection not implemented yet
        """
        loader = GraphLoader(graphs_dir=tmp_path)
        backup_manager = BackupManager(graphs_dir=tmp_path)

        # Create valid initial graph
        valid_graph = {
            "nodes": [{"id": "node_1", "label": "Node 1", "type": "concept"}],
            "edges": []
        }
        loader.save_graph("test", valid_graph)

        # Manually corrupt the graph file
        graph_file = tmp_path / "test_graph.json"
        graph_file.write_text("{ corrupt json")

        # Attempt to load (should detect corruption and restore)
        restored_graph = loader.load_graph("test", auto_restore=True)

        # Should have restored valid graph
        assert len(restored_graph["nodes"]) == 1
        assert restored_graph["nodes"][0]["id"] == "node_1"

    def test_no_restore_if_no_backup_exists(self, tmp_path):
        """Verify graceful failure when no backup exists to restore.

        RED: Should FAIL - Backup existence check not implemented yet
        """
        loader = GraphLoader(graphs_dir=tmp_path)

        # Create corrupted file with no backup
        graph_file = tmp_path / "test_graph.json"
        graph_file.write_text("{ corrupt json")

        # Should raise appropriate error (not crash)
        with pytest.raises(Exception) as exc_info:
            loader.load_graph("test", auto_restore=True)

        assert "no backup" in str(exc_info.value).lower() or "corrupt" in str(exc_info.value).lower()


class TestBackupManager:
    """Test BackupManager utility methods."""

    def test_list_backups_returns_sorted_by_time(self, tmp_path):
        """Verify list_backups returns backups sorted by timestamp.

        RED: Should FAIL - Sorting not implemented yet
        """
        backup_manager = BackupManager(graphs_dir=tmp_path)
        loader = GraphLoader(graphs_dir=tmp_path)

        graph = {
            "nodes": [{"id": "node_1", "label": "Node 1", "type": "concept"}],
            "edges": []
        }
        loader.save_graph("test", graph)

        # Create multiple backups
        for i in range(3):
            graph["nodes"].append({
                "id": f"node_{i+2}",
                "label": f"Node {i+2}",
                "type": "concept"
            })
            loader.save_graph("test", graph)

        backups = backup_manager.list_backups("test")

        # Should be sorted with newest first
        assert len(backups) >= 2
        # Verify ordering (later timestamps should come first)
        for i in range(len(backups) - 1):
            assert backups[i] >= backups[i + 1]

    def test_prune_old_backups(self, tmp_path):
        """Verify manual pruning of old backups.

        RED: Should FAIL - Prune method not implemented yet
        """
        backup_manager = BackupManager(graphs_dir=tmp_path, max_backups=10)
        loader = GraphLoader(graphs_dir=tmp_path)

        graph = {
            "nodes": [{"id": "node_1", "label": "Node 1", "type": "concept"}],
            "edges": []
        }
        loader.save_graph("test", graph)

        # Create 7 backups
        for i in range(7):
            graph["nodes"].append({
                "id": f"node_{i+2}",
                "label": f"Node {i+2}",
                "type": "concept"
            })
            loader.save_graph("test", graph)

        backups_before = backup_manager.list_backups("test")
        assert len(backups_before) == 7

        # Prune to keep only 3
        backup_manager.prune_backups("test", keep=3)

        backups_after = backup_manager.list_backups("test")
        assert len(backups_after) == 3

    def test_get_backup_info(self, tmp_path):
        """Verify getting metadata about a backup.

        RED: Should FAIL - Metadata methods not implemented yet
        """
        backup_manager = BackupManager(graphs_dir=tmp_path)
        loader = GraphLoader(graphs_dir=tmp_path)

        graph = {
            "nodes": [{"id": "node_1", "label": "Node 1", "type": "concept"}],
            "edges": []
        }
        loader.save_graph("test", graph)

        graph["nodes"].append({"id": "node_2", "label": "Node 2", "type": "concept"})
        loader.save_graph("test", graph)

        backups = backup_manager.list_backups("test")
        assert len(backups) >= 1

        info = backup_manager.get_backup_info("test", backups[0])

        assert "timestamp" in info
        assert "size_bytes" in info
        assert "nodes_count" in info
