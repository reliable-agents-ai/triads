"""
Tests for integrity tools repository layer.

Tests AbstractBackupRepository implementations:
- InMemoryBackupRepository (for testing)
- FileSystemBackupRepository (wraps BackupManager)
"""

from pathlib import Path

import pytest

from triads.tools.integrity.repository import (
    AbstractBackupRepository,
    FileSystemBackupRepository,
    InMemoryBackupRepository,
)


class TestInMemoryBackupRepository:
    """Test in-memory backup repository for testing."""

    def test_in_memory_backup_repo_create_backup(self):
        """Creating backup returns path and stores in memory."""
        repo = InMemoryBackupRepository()

        # Create first backup
        backup_path = repo.create_backup("design")
        assert backup_path is not None
        assert "design" in str(backup_path)
        assert backup_path.suffix == ".backup"

        # Create second backup for same triad
        backup_path2 = repo.create_backup("design")
        assert backup_path2 != backup_path  # Different paths
        assert "design" in str(backup_path2)

    def test_in_memory_backup_repo_list_backups(self):
        """Listing backups returns all backups for triad."""
        repo = InMemoryBackupRepository()

        # No backups initially
        assert repo.list_backups("design") == []

        # Create backups
        repo.create_backup("design")
        repo.create_backup("design")
        repo.create_backup("implementation")  # Different triad

        # List backups for design
        design_backups = repo.list_backups("design")
        assert len(design_backups) == 2
        assert all("design" in str(b) for b in design_backups)

        # List backups for implementation
        impl_backups = repo.list_backups("implementation")
        assert len(impl_backups) == 1
        assert "implementation" in str(impl_backups[0])

    def test_in_memory_backup_repo_restore_backup(self):
        """Restoring backup returns success."""
        repo = InMemoryBackupRepository()

        # Create backup
        backup_path = repo.create_backup("design")

        # Restore it
        success = repo.restore_backup("design", backup_path)
        assert success is True

        # Restore non-existent backup
        fake_path = Path("/fake/backup.json.backup")
        success = repo.restore_backup("design", fake_path)
        assert success is False

    def test_in_memory_backup_repo_implements_abstract_interface(self):
        """InMemoryBackupRepository implements AbstractBackupRepository."""
        repo = InMemoryBackupRepository()
        assert isinstance(repo, AbstractBackupRepository)


class TestFileSystemBackupRepository:
    """Test filesystem backup repository that wraps BackupManager."""

    def test_filesystem_backup_repo_wraps_backup_manager(self, tmp_path):
        """FileSystemBackupRepository uses BackupManager internally."""
        # Create repository with temp directory
        repo = FileSystemBackupRepository(graphs_dir=tmp_path)

        # Verify it has backup_manager attribute
        assert hasattr(repo, "backup_manager")
        assert repo.backup_manager is not None

    def test_filesystem_backup_repo_create_backup(self, tmp_path):
        """Creating backup delegates to BackupManager."""
        # Create a test graph file
        graph_file = tmp_path / "design_graph.json"
        graph_file.write_text('{"nodes": [], "links": []}')

        repo = FileSystemBackupRepository(graphs_dir=tmp_path)

        # Create backup
        backup_path = repo.create_backup("design")

        # Should return path
        assert backup_path is not None
        assert backup_path.exists()
        assert "design" in backup_path.name
        assert backup_path.suffix == ".backup"

    def test_filesystem_backup_repo_list_backups(self, tmp_path):
        """Listing backups delegates to BackupManager."""
        # Create test graph
        graph_file = tmp_path / "design_graph.json"
        graph_file.write_text('{"nodes": [], "links": []}')

        repo = FileSystemBackupRepository(graphs_dir=tmp_path)

        # Create backups
        repo.create_backup("design")
        repo.create_backup("design")

        # List backups
        backups = repo.list_backups("design")
        assert len(backups) == 2
        assert all("design" in b for b in backups)

    def test_filesystem_backup_repo_restore_backup(self, tmp_path):
        """Restoring backup delegates to BackupManager."""
        # Create test graph
        graph_file = tmp_path / "design_graph.json"
        graph_file.write_text('{"nodes": [{"id": "node1"}], "links": []}')

        repo = FileSystemBackupRepository(graphs_dir=tmp_path)

        # Create backup
        backup_path = repo.create_backup("design")
        backup_name = backup_path.name

        # Modify graph
        graph_file.write_text('{"nodes": [], "links": []}')

        # Restore backup
        success = repo.restore_backup("design", backup_name)
        assert success is True

        # Verify restoration
        restored_content = graph_file.read_text()
        assert "node1" in restored_content

    def test_filesystem_backup_repo_implements_abstract_interface(self, tmp_path):
        """FileSystemBackupRepository implements AbstractBackupRepository."""
        repo = FileSystemBackupRepository(graphs_dir=tmp_path)
        assert isinstance(repo, AbstractBackupRepository)
