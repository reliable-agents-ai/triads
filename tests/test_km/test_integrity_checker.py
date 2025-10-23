"""Tests for knowledge graph integrity checker CLI.

This module tests the integrity checking and auto-repair functionality
for knowledge graphs, including CLI interface and exit codes.

RED Phase: These tests should FAIL initially (feature not implemented yet).
GREEN Phase: Implement IntegrityChecker to make tests pass.
REFACTOR Phase: Clean up and optimize.
"""

import json
from pathlib import Path

import pytest

from triads.km.integrity_checker import (
    IntegrityChecker,
    ValidationResult,
    RepairResult,
    ExitCode,
)


class TestIntegrityCheckerBasicValidation:
    """Test basic validation functionality."""

    def test_check_valid_graph_returns_success(self, tmp_path):
        """Verify checking a valid graph returns success result.

        RED: Should FAIL - IntegrityChecker not implemented yet
        """
        # Create valid graph
        graph_file = tmp_path / "test_graph.json"
        valid_graph = {
            "nodes": [
                {"id": "node1", "label": "Test Node", "type": "entity"}
            ],
            "edges": []
        }
        graph_file.write_text(json.dumps(valid_graph))

        checker = IntegrityChecker(graphs_dir=tmp_path)
        result = checker.check_graph("test")

        assert result.valid is True
        assert result.triad == "test"
        assert result.error is None
        assert result.error_count == 0

    def test_check_corrupted_graph_returns_failure(self, tmp_path):
        """Verify checking a corrupted graph returns failure result.

        RED: Should FAIL - IntegrityChecker not implemented yet
        """
        # Create invalid graph (missing required field)
        graph_file = tmp_path / "test_graph.json"
        invalid_graph = {
            "nodes": [
                {"id": "node1", "type": "entity"}  # Missing 'label'
            ],
            "edges": []
        }
        graph_file.write_text(json.dumps(invalid_graph))

        checker = IntegrityChecker(graphs_dir=tmp_path)
        result = checker.check_graph("test")

        assert result.valid is False
        assert result.triad == "test"
        assert result.error is not None
        assert "label" in result.error.lower()
        assert result.error_count == 1

    def test_check_nonexistent_graph_returns_not_found(self, tmp_path):
        """Verify checking nonexistent graph returns appropriate result.

        RED: Should FAIL - IntegrityChecker not implemented yet
        """
        checker = IntegrityChecker(graphs_dir=tmp_path)
        result = checker.check_graph("nonexistent")

        assert result.valid is False
        assert result.error is not None
        assert "not found" in result.error.lower()

    def test_check_all_graphs_validates_multiple(self, tmp_path):
        """Verify check_all_graphs validates all graph files.

        RED: Should FAIL - IntegrityChecker not implemented yet
        """
        # Create multiple graphs
        for i in range(3):
            graph_file = tmp_path / f"test{i}_graph.json"
            valid_graph = {
                "nodes": [{"id": f"node{i}", "label": f"Node {i}", "type": "entity"}],
                "edges": []
            }
            graph_file.write_text(json.dumps(valid_graph))

        checker = IntegrityChecker(graphs_dir=tmp_path)
        results = checker.check_all_graphs()

        assert len(results) == 3
        assert all(r.valid for r in results)

    def test_check_all_graphs_reports_mixed_results(self, tmp_path):
        """Verify check_all_graphs reports both valid and invalid graphs.

        RED: Should FAIL - IntegrityChecker not implemented yet
        """
        # Valid graph
        valid_file = tmp_path / "valid_graph.json"
        valid_file.write_text(json.dumps({"nodes": [{"id": "n1", "label": "N1", "type": "entity"}], "edges": []}))

        # Invalid graph
        invalid_file = tmp_path / "invalid_graph.json"
        invalid_file.write_text(json.dumps({"nodes": [{"id": "n2", "type": "entity"}], "edges": []}))  # Missing label

        checker = IntegrityChecker(graphs_dir=tmp_path)
        results = checker.check_all_graphs()

        assert len(results) == 2
        valid_results = [r for r in results if r.valid]
        invalid_results = [r for r in results if not r.valid]
        assert len(valid_results) == 1
        assert len(invalid_results) == 1


class TestIntegrityCheckerRepair:
    """Test repair functionality."""

    def test_repair_missing_label_fails_gracefully(self, tmp_path):
        """Verify repair attempts but cannot fix missing required fields.

        RED: Should FAIL - Repair not implemented yet
        """
        # Create graph with missing label (unrecoverable)
        graph_file = tmp_path / "test_graph.json"
        invalid_graph = {
            "nodes": [{"id": "node1", "type": "entity"}],  # Missing label
            "edges": []
        }
        graph_file.write_text(json.dumps(invalid_graph))

        checker = IntegrityChecker(graphs_dir=tmp_path)
        result = checker.repair_graph("test")

        assert result.success is False
        assert result.triad == "test"
        assert "cannot repair" in result.message.lower() or "failed" in result.message.lower()

    def test_repair_invalid_edges_removes_them(self, tmp_path):
        """Verify repair removes edges pointing to nonexistent nodes.

        RED: Should FAIL - Repair not implemented yet
        """
        # Create graph with edge pointing to nonexistent node
        graph_file = tmp_path / "test_graph.json"
        invalid_graph = {
            "nodes": [{"id": "node1", "label": "Node 1", "type": "entity"}],
            "edges": [
                {"source": "node1", "target": "nonexistent"}  # Invalid target
            ]
        }
        graph_file.write_text(json.dumps(invalid_graph))

        checker = IntegrityChecker(graphs_dir=tmp_path)
        result = checker.repair_graph("test")

        assert result.success is True
        assert result.triad == "test"
        assert result.actions_taken is not None
        assert "removed 1 invalid edge" in result.actions_taken.lower()

        # Verify edge was actually removed
        repaired = json.loads(graph_file.read_text())
        assert len(repaired["edges"]) == 0

    def test_repair_creates_backup_before_modifying(self, tmp_path):
        """Verify repair creates backup before modifying graph.

        RED: Should FAIL - Repair not implemented yet
        """
        # Create graph needing repair
        graph_file = tmp_path / "test_graph.json"
        invalid_graph = {
            "nodes": [{"id": "node1", "label": "Node 1", "type": "entity"}],
            "edges": [{"source": "node1", "target": "ghost"}]
        }
        graph_file.write_text(json.dumps(invalid_graph))

        checker = IntegrityChecker(graphs_dir=tmp_path)
        result = checker.repair_graph("test")

        # Should have created backup
        backups_dir = tmp_path / "backups"
        assert backups_dir.exists()
        backup_files = list(backups_dir.glob("test_graph_*.json.backup"))
        assert len(backup_files) >= 1
        assert result.backup_created is True

    def test_repair_validates_repaired_graph(self, tmp_path):
        """Verify repair validates the graph after repair.

        RED: Should FAIL - Repair not implemented yet
        """
        # Create repairable graph
        graph_file = tmp_path / "test_graph.json"
        invalid_graph = {
            "nodes": [{"id": "node1", "label": "Node 1", "type": "entity"}],
            "edges": [{"source": "node1", "target": "ghost"}]
        }
        graph_file.write_text(json.dumps(invalid_graph))

        checker = IntegrityChecker(graphs_dir=tmp_path)
        result = checker.repair_graph("test")

        assert result.success is True
        # After repair, graph should be valid
        check_result = checker.check_graph("test")
        assert check_result.valid is True

    def test_repair_rollback_on_new_errors(self, tmp_path):
        """Verify repair rolls back if new errors are introduced.

        RED: Should FAIL - Rollback not implemented yet
        """
        # This is a tricky test - we'd need to mock repair logic to introduce new errors
        # For now, just verify the repair result has a rollback indicator
        # (This test might be refined in GREEN phase based on implementation)
        graph_file = tmp_path / "test_graph.json"
        invalid_graph = {
            "nodes": [{"id": "node1", "type": "entity"}],  # Missing label - can't repair
            "edges": []
        }
        graph_file.write_text(json.dumps(invalid_graph))

        checker = IntegrityChecker(graphs_dir=tmp_path)
        result = checker.repair_graph("test")

        # Since we can't repair missing labels, result should fail
        assert result.success is False


class TestIntegrityCheckerCLI:
    """Test CLI interface and exit codes."""

    def test_cli_check_all_graphs_exit_0_when_valid(self, tmp_path, monkeypatch, capsys):
        """Verify CLI exits with 0 when all graphs are valid.

        RED: Should FAIL - CLI not implemented yet
        """
        # Create valid graph
        graph_file = tmp_path / "test_graph.json"
        valid_graph = {"nodes": [{"id": "n1", "label": "N1", "type": "entity"}], "edges": []}
        graph_file.write_text(json.dumps(valid_graph))

        # Mock sys.argv and run CLI
        import sys
        monkeypatch.setattr(sys, "argv", ["triads-km", "check", "--dir", str(tmp_path)])

        from triads.km.integrity_checker import main
        exit_code = main()

        assert exit_code == ExitCode.SUCCESS
        captured = capsys.readouterr()
        assert "1/1 graphs valid" in captured.out or "All graphs valid" in captured.out

    def test_cli_check_exit_1_when_corruption_detected(self, tmp_path, monkeypatch, capsys):
        """Verify CLI exits with 1 when corruption detected.

        RED: Should FAIL - CLI not implemented yet
        """
        # Create invalid graph
        graph_file = tmp_path / "test_graph.json"
        invalid_graph = {"nodes": [{"id": "n1", "type": "entity"}], "edges": []}  # Missing label
        graph_file.write_text(json.dumps(invalid_graph))

        import sys
        monkeypatch.setattr(sys, "argv", ["triads-km", "check", "--dir", str(tmp_path)])

        from triads.km.integrity_checker import main
        exit_code = main()

        assert exit_code == ExitCode.CORRUPTION_DETECTED
        captured = capsys.readouterr()
        assert "0/1 graphs valid" in captured.out or "corruption" in captured.out.lower()

    def test_cli_check_specific_triad(self, tmp_path, monkeypatch, capsys):
        """Verify CLI can check specific triad with --triad flag.

        RED: Should FAIL - CLI not implemented yet
        """
        # Create multiple graphs
        for name in ["test1", "test2"]:
            graph_file = tmp_path / f"{name}_graph.json"
            graph_file.write_text(json.dumps({"nodes": [{"id": "n1", "label": "N1", "type": "entity"}], "edges": []}))

        import sys
        monkeypatch.setattr(sys, "argv", ["triads-km", "check", "--triad", "test1", "--dir", str(tmp_path)])

        from triads.km.integrity_checker import main
        exit_code = main()

        assert exit_code == ExitCode.SUCCESS
        captured = capsys.readouterr()
        # Should only mention test1, not test2
        assert "test1" in captured.out

    def test_cli_check_with_verbose_flag(self, tmp_path, monkeypatch, capsys):
        """Verify CLI provides detailed output with --verbose flag.

        RED: Should FAIL - CLI not implemented yet
        """
        # Create invalid graph
        graph_file = tmp_path / "test_graph.json"
        invalid_graph = {"nodes": [{"id": "n1", "type": "entity"}], "edges": []}
        graph_file.write_text(json.dumps(invalid_graph))

        import sys
        monkeypatch.setattr(sys, "argv", ["triads-km", "check", "--verbose", "--dir", str(tmp_path)])

        from triads.km.integrity_checker import main
        exit_code = main()

        assert exit_code == ExitCode.CORRUPTION_DETECTED
        captured = capsys.readouterr()
        # Verbose should show detailed error info
        assert "label" in captured.out.lower()
        assert "nodes[0]" in captured.out or "node at index 0" in captured.out.lower()

    def test_cli_check_with_fix_flag(self, tmp_path, monkeypatch, capsys):
        """Verify CLI auto-repairs with --fix flag.

        RED: Should FAIL - CLI not implemented yet
        """
        # Create repairable graph
        graph_file = tmp_path / "test_graph.json"
        invalid_graph = {
            "nodes": [{"id": "node1", "label": "Node 1", "type": "entity"}],
            "edges": [{"source": "node1", "target": "ghost"}]
        }
        graph_file.write_text(json.dumps(invalid_graph))

        import sys
        monkeypatch.setattr(sys, "argv", ["triads-km", "check", "--fix", "--dir", str(tmp_path)])

        from triads.km.integrity_checker import main
        exit_code = main()

        assert exit_code == ExitCode.SUCCESS
        captured = capsys.readouterr()
        assert "repaired" in captured.out.lower() or "fixed" in captured.out.lower()

        # Verify graph was actually repaired
        repaired = json.loads(graph_file.read_text())
        assert len(repaired["edges"]) == 0

    def test_cli_check_fix_exits_2_on_repair_failure(self, tmp_path, monkeypatch, capsys):
        """Verify CLI exits with 2 when repair fails.

        RED: Should FAIL - CLI not implemented yet
        """
        # Create unrepairable graph
        graph_file = tmp_path / "test_graph.json"
        invalid_graph = {"nodes": [{"id": "n1", "type": "entity"}], "edges": []}  # Can't repair missing label
        graph_file.write_text(json.dumps(invalid_graph))

        import sys
        monkeypatch.setattr(sys, "argv", ["triads-km", "check", "--fix", "--dir", str(tmp_path)])

        from triads.km.integrity_checker import main
        exit_code = main()

        assert exit_code == ExitCode.REPAIR_FAILED
        captured = capsys.readouterr()
        assert "failed" in captured.out.lower() or "cannot" in captured.out.lower()


class TestIntegrityCheckerReporting:
    """Test reporting and output formatting."""

    def test_validation_result_contains_file_path(self, tmp_path):
        """Verify validation result includes file path.

        RED: Should FAIL - ValidationResult not fully implemented yet
        """
        graph_file = tmp_path / "test_graph.json"
        valid_graph = {"nodes": [{"id": "n1", "label": "N1", "type": "entity"}], "edges": []}
        graph_file.write_text(json.dumps(valid_graph))

        checker = IntegrityChecker(graphs_dir=tmp_path)
        result = checker.check_graph("test")

        assert result.file_path is not None
        assert "test_graph.json" in str(result.file_path)

    def test_validation_result_includes_error_details(self, tmp_path):
        """Verify validation result includes detailed error information.

        RED: Should FAIL - Error details not captured yet
        """
        graph_file = tmp_path / "test_graph.json"
        invalid_graph = {"nodes": [{"id": "n1", "type": "entity"}], "edges": []}
        graph_file.write_text(json.dumps(invalid_graph))

        checker = IntegrityChecker(graphs_dir=tmp_path)
        result = checker.check_graph("test")

        assert result.error is not None
        assert result.error_field is not None
        assert "nodes[0].label" in result.error_field or "label" in result.error_field

    def test_repair_result_lists_actions_taken(self, tmp_path):
        """Verify repair result lists all actions taken.

        RED: Should FAIL - Action logging not implemented yet
        """
        graph_file = tmp_path / "test_graph.json"
        invalid_graph = {
            "nodes": [{"id": "node1", "label": "Node 1", "type": "entity"}],
            "edges": [
                {"source": "node1", "target": "ghost1"},
                {"source": "node1", "target": "ghost2"}
            ]
        }
        graph_file.write_text(json.dumps(invalid_graph))

        checker = IntegrityChecker(graphs_dir=tmp_path)
        result = checker.repair_graph("test")

        assert result.actions_taken is not None
        assert "2 invalid edge" in result.actions_taken.lower()

    def test_summary_report_counts_valid_and_invalid(self, tmp_path):
        """Verify summary report counts valid/invalid graphs correctly.

        RED: Should FAIL - Summary reporting not implemented yet
        """
        # Create mix of valid and invalid
        valid_file = tmp_path / "valid_graph.json"
        valid_file.write_text(json.dumps({"nodes": [{"id": "n1", "label": "N1", "type": "entity"}], "edges": []}))

        invalid_file = tmp_path / "invalid_graph.json"
        invalid_file.write_text(json.dumps({"nodes": [{"id": "n2", "type": "entity"}], "edges": []}))

        checker = IntegrityChecker(graphs_dir=tmp_path)
        results = checker.check_all_graphs()
        summary = checker.get_summary(results)

        assert summary.total == 2
        assert summary.valid == 1
        assert summary.invalid == 1
        assert summary.corruption_rate == 0.5
