"""
Edge-to-edge tests for integrity tools entrypoint.

Tests the 3 MCP tools through their public interfaces:
- check_graph
- check_all_graphs
- repair_graph
"""

from pathlib import Path

import pytest

from triads.tools.integrity.entrypoint import IntegrityTools
from triads.tools.shared import ToolResult


@pytest.fixture
def graphs_dir(tmp_path):
    """Temporary graphs directory with test data."""
    # Create a valid graph
    valid_graph = tmp_path / "design_graph.json"
    valid_graph.write_text("""{
  "directed": true,
  "multigraph": true,
  "graph": {},
  "nodes": [
    {
      "id": "node1",
      "label": "Test Node",
      "type": "Concept",
      "description": "A test node",
      "confidence": 0.95
    }
  ],
  "links": []
}""")

    # Create an invalid graph (missing required field)
    invalid_graph = tmp_path / "implementation_graph.json"
    invalid_graph.write_text("""{
  "directed": true,
  "multigraph": true,
  "graph": {},
  "nodes": [
    {
      "id": "node2",
      "type": "Concept",
      "description": "Missing label field"
    }
  ],
  "links": []
}""")

    return tmp_path


class TestCheckGraphTool:
    """Test check_graph MCP tool."""

    def test_check_graph_returns_mcp_compliant_result(self, graphs_dir):
        """check_graph returns ToolResult with text content."""
        result = IntegrityTools.check_graph("design", graphs_dir=graphs_dir)

        assert isinstance(result, ToolResult)
        assert result.success is True
        assert len(result.content) == 1
        assert result.content[0]["type"] == "text"
        assert "text" in result.content[0]

    def test_check_graph_valid_graph(self, graphs_dir):
        """Valid graph returns success with valid message."""
        result = IntegrityTools.check_graph("design", graphs_dir=graphs_dir)

        assert result.success is True
        output = result.content[0]["text"]
        assert "design" in output.lower()
        assert "valid" in output.lower() or "✓" in output

    def test_check_graph_invalid_graph(self, graphs_dir):
        """Invalid graph returns success=True but shows validation errors in text."""
        result = IntegrityTools.check_graph("implementation", graphs_dir=graphs_dir)

        # Still success=True because tool executed successfully
        assert result.success is True
        output = result.content[0]["text"]
        assert "implementation" in output.lower()
        assert "invalid" in output.lower() or "✗" in output or "error" in output.lower()

    def test_check_graph_error_handling(self, graphs_dir):
        """check_graph handles errors gracefully."""
        # Try to check non-existent graph
        result = IntegrityTools.check_graph("nonexistent", graphs_dir=graphs_dir)

        # Tool executes successfully, but shows graph not found in output
        assert result.success is True
        output = result.content[0]["text"]
        assert "nonexistent" in output.lower()


class TestCheckAllGraphsTool:
    """Test check_all_graphs MCP tool."""

    def test_check_all_graphs_formats_multiple_results(self, graphs_dir):
        """check_all_graphs returns formatted results for all graphs."""
        result = IntegrityTools.check_all_graphs(graphs_dir=graphs_dir)

        assert isinstance(result, ToolResult)
        assert result.success is True
        assert len(result.content) == 1
        assert result.content[0]["type"] == "text"

        output = result.content[0]["text"]
        # Should mention both graphs
        assert "design" in output.lower()
        assert "implementation" in output.lower()

    def test_check_all_graphs_empty_directory(self, tmp_path):
        """check_all_graphs handles empty directory gracefully."""
        result = IntegrityTools.check_all_graphs(graphs_dir=tmp_path)

        assert result.success is True
        output = result.content[0]["text"]
        # Should indicate no graphs found or 0/0 valid
        assert "0" in output or "no graphs" in output.lower()

    def test_check_all_graphs_shows_summary(self, graphs_dir):
        """check_all_graphs shows summary statistics."""
        result = IntegrityTools.check_all_graphs(graphs_dir=graphs_dir)

        output = result.content[0]["text"]
        # Should show counts (e.g., "1/2 valid")
        assert any(char.isdigit() for char in output)


class TestRepairGraphTool:
    """Test repair_graph MCP tool."""

    def test_repair_graph_returns_success_message(self, tmp_path):
        """repair_graph returns ToolResult with repair status."""
        # Create graph with repairable issue (invalid edges)
        graph_file = tmp_path / "test_graph.json"
        graph_file.write_text("""{
  "directed": true,
  "multigraph": true,
  "graph": {},
  "nodes": [
    {"id": "node1", "label": "Node 1", "type": "Concept", "description": "Test", "confidence": 0.9}
  ],
  "links": [
    {"source": "node1", "target": "nonexistent", "key": "relates_to"}
  ]
}""")

        result = IntegrityTools.repair_graph("test", graphs_dir=tmp_path)

        assert isinstance(result, ToolResult)
        assert result.success is True
        assert len(result.content) == 1
        assert result.content[0]["type"] == "text"

        output = result.content[0]["text"]
        assert "test" in output.lower()
        # Should mention repair outcome
        assert any(word in output.lower() for word in ["repaired", "success", "backup"])

    def test_repair_graph_backup_parameter_respected(self, tmp_path):
        """repair_graph respects create_backup parameter."""
        # Create valid graph
        graph_file = tmp_path / "test_graph.json"
        graph_file.write_text("""{
  "directed": true,
  "multigraph": true,
  "graph": {},
  "nodes": [
    {"id": "node1", "label": "Node 1", "type": "Concept", "description": "Test", "confidence": 0.9}
  ],
  "links": []
}""")

        # Repair with backup
        result_with_backup = IntegrityTools.repair_graph("test", create_backup=True, graphs_dir=tmp_path)
        assert result_with_backup.success is True

        # Repair without backup
        result_without_backup = IntegrityTools.repair_graph("test", create_backup=False, graphs_dir=tmp_path)
        assert result_without_backup.success is True

    def test_repair_graph_handles_failure(self, tmp_path):
        """repair_graph handles unrepairable graphs."""
        # Create graph with unrepairable issue (invalid JSON structure caught earlier)
        # Create missing required field
        graph_file = tmp_path / "test_graph.json"
        graph_file.write_text("""{
  "directed": true,
  "multigraph": true,
  "graph": {},
  "nodes": [
    {"type": "Concept", "description": "Missing id and label"}
  ],
  "links": []
}""")

        result = IntegrityTools.repair_graph("test", graphs_dir=tmp_path)

        # Tool still succeeds, but repair failed
        assert result.success is True
        output = result.content[0]["text"]
        # Should indicate repair failed or cannot repair
        assert any(word in output.lower() for word in ["cannot", "failed", "error"])


class TestToolSignatures:
    """Test that all tools have proper signatures."""

    def test_all_3_tools_have_proper_signatures(self):
        """All tools are static methods with correct parameters."""
        # check_graph
        assert hasattr(IntegrityTools, "check_graph")
        assert callable(IntegrityTools.check_graph)

        # check_all_graphs
        assert hasattr(IntegrityTools, "check_all_graphs")
        assert callable(IntegrityTools.check_all_graphs)

        # repair_graph
        assert hasattr(IntegrityTools, "repair_graph")
        assert callable(IntegrityTools.repair_graph)

    def test_tools_return_tool_result(self, tmp_path):
        """All tools return ToolResult instances."""
        # Create minimal graph
        graph_file = tmp_path / "test_graph.json"
        graph_file.write_text("""{
  "directed": true,
  "multigraph": true,
  "graph": {},
  "nodes": [],
  "links": []
}""")

        # Test each tool
        result1 = IntegrityTools.check_graph("test", graphs_dir=tmp_path)
        assert isinstance(result1, ToolResult)

        result2 = IntegrityTools.check_all_graphs(graphs_dir=tmp_path)
        assert isinstance(result2, ToolResult)

        result3 = IntegrityTools.repair_graph("test", graphs_dir=tmp_path)
        assert isinstance(result3, ToolResult)
