"""Tests for knowledge graph schema validation.

This module tests that graphs are validated against a schema before
being saved, preventing invalid data from corrupting the graph files.

RED Phase: These tests should FAIL initially (feature not implemented yet).
"""

import pytest

from triads.km.graph_access import GraphLoader


class TestSchemaValidation:
    """Test graph schema validation before save."""

    def test_save_rejects_missing_nodes_key(self, tmp_path):
        """Verify save_graph rejects graphs without 'nodes' key.

        RED: Should FAIL - No schema validation yet
        """
        loader = GraphLoader(graphs_dir=tmp_path)
        invalid_graph = {"edges": []}  # Missing 'nodes' key

        result = loader.save_graph("test", invalid_graph)

        assert result is False

    def test_save_rejects_missing_edges_key(self, tmp_path):
        """Verify save_graph rejects graphs without 'edges' key.

        RED: Should FAIL - No schema validation yet
        """
        loader = GraphLoader(graphs_dir=tmp_path)
        invalid_graph = {"nodes": []}  # Missing 'edges' key

        result = loader.save_graph("test", invalid_graph)

        assert result is False

    def test_save_rejects_non_dict_graph(self, tmp_path):
        """Verify save_graph rejects non-dictionary graphs.

        RED: Should FAIL - No type validation yet
        """
        loader = GraphLoader(graphs_dir=tmp_path)

        result = loader.save_graph("test", ["not", "a", "dict"])

        assert result is False

    def test_save_rejects_nodes_not_list(self, tmp_path):
        """Verify save_graph rejects graphs where nodes is not a list.

        RED: Should FAIL - No structure validation yet
        """
        loader = GraphLoader(graphs_dir=tmp_path)
        invalid_graph = {"nodes": "not a list", "edges": []}

        result = loader.save_graph("test", invalid_graph)

        assert result is False

    def test_save_rejects_edges_not_list(self, tmp_path):
        """Verify save_graph rejects graphs where edges is not a list.

        RED: Should FAIL - No structure validation yet
        """
        loader = GraphLoader(graphs_dir=tmp_path)
        invalid_graph = {"nodes": [], "edges": "not a list"}

        result = loader.save_graph("test", invalid_graph)

        assert result is False


class TestNodeValidation:
    """Test individual node validation."""

    def test_save_rejects_node_without_id(self, tmp_path):
        """Verify save_graph rejects nodes missing 'id' field.

        RED: Should FAIL - No node field validation yet
        """
        loader = GraphLoader(graphs_dir=tmp_path)
        invalid_graph = {
            "nodes": [{"label": "Test", "type": "concept"}],  # Missing 'id'
            "edges": []
        }

        result = loader.save_graph("test", invalid_graph)

        assert result is False

    def test_save_rejects_node_without_label(self, tmp_path):
        """Verify save_graph rejects nodes missing 'label' field.

        RED: Should FAIL - No node field validation yet
        """
        loader = GraphLoader(graphs_dir=tmp_path)
        invalid_graph = {
            "nodes": [{"id": "test-1", "type": "concept"}],  # Missing 'label'
            "edges": []
        }

        result = loader.save_graph("test", invalid_graph)

        assert result is False

    def test_save_rejects_node_without_type(self, tmp_path):
        """Verify save_graph rejects nodes missing 'type' field.

        RED: Should FAIL - No node field validation yet
        """
        loader = GraphLoader(graphs_dir=tmp_path)
        invalid_graph = {
            "nodes": [{"id": "test-1", "label": "Test"}],  # Missing 'type'
            "edges": []
        }

        result = loader.save_graph("test", invalid_graph)

        assert result is False

    def test_save_rejects_invalid_node_type(self, tmp_path):
        """Verify save_graph rejects nodes with invalid type.

        RED: Should FAIL - No type enum validation yet
        """
        loader = GraphLoader(graphs_dir=tmp_path)
        invalid_graph = {
            "nodes": [{
                "id": "test-1",
                "label": "Test",
                "type": "invalid_type"  # Invalid type
            }],
            "edges": []
        }

        result = loader.save_graph("test", invalid_graph)

        assert result is False

    def test_save_accepts_valid_node_types(self, tmp_path):
        """Verify save_graph accepts all valid node types.

        RED: Should FAIL - No validation yet
        """
        loader = GraphLoader(graphs_dir=tmp_path)
        valid_types = [
            "concept", "decision", "entity", "finding",
            "task", "workflow", "uncertainty"
        ]

        for node_type in valid_types:
            valid_graph = {
                "nodes": [{
                    "id": f"test-{node_type}",
                    "label": f"Test {node_type}",
                    "type": node_type
                }],
                "edges": []
            }

            result = loader.save_graph("test", valid_graph)
            assert result is True, f"Failed to save valid node type: {node_type}"


class TestConfidenceValidation:
    """Test confidence score validation."""

    def test_save_rejects_confidence_below_zero(self, tmp_path):
        """Verify save_graph rejects nodes with confidence < 0.0.

        RED: Should FAIL - No confidence validation yet
        """
        loader = GraphLoader(graphs_dir=tmp_path)
        invalid_graph = {
            "nodes": [{
                "id": "test-1",
                "label": "Test",
                "type": "concept",
                "confidence": -0.1  # Invalid: < 0.0
            }],
            "edges": []
        }

        result = loader.save_graph("test", invalid_graph)

        assert result is False

    def test_save_rejects_confidence_above_one(self, tmp_path):
        """Verify save_graph rejects nodes with confidence > 1.0.

        RED: Should FAIL - No confidence validation yet
        """
        loader = GraphLoader(graphs_dir=tmp_path)
        invalid_graph = {
            "nodes": [{
                "id": "test-1",
                "label": "Test",
                "type": "concept",
                "confidence": 1.1  # Invalid: > 1.0
            }],
            "edges": []
        }

        result = loader.save_graph("test", invalid_graph)

        assert result is False

    def test_save_accepts_valid_confidence_range(self, tmp_path):
        """Verify save_graph accepts confidence in [0.0, 1.0] range.

        RED: Should FAIL - No validation yet
        """
        loader = GraphLoader(graphs_dir=tmp_path)
        valid_confidences = [0.0, 0.5, 0.95, 1.0]

        for conf in valid_confidences:
            valid_graph = {
                "nodes": [{
                    "id": "test-1",
                    "label": "Test",
                    "type": "concept",
                    "confidence": conf
                }],
                "edges": []
            }

            result = loader.save_graph("test", valid_graph)
            assert result is True, f"Failed to save valid confidence: {conf}"


class TestEdgeValidation:
    """Test edge structure validation."""

    def test_save_rejects_edge_without_source(self, tmp_path):
        """Verify save_graph rejects edges missing 'source' field.

        RED: Should FAIL - No edge field validation yet
        """
        loader = GraphLoader(graphs_dir=tmp_path)
        invalid_graph = {
            "nodes": [
                {"id": "n1", "label": "N1", "type": "concept"},
                {"id": "n2", "label": "N2", "type": "concept"}
            ],
            "edges": [{"target": "n2", "label": "related"}]  # Missing 'source'
        }

        result = loader.save_graph("test", invalid_graph)

        assert result is False

    def test_save_rejects_edge_without_target(self, tmp_path):
        """Verify save_graph rejects edges missing 'target' field.

        RED: Should FAIL - No edge field validation yet
        """
        loader = GraphLoader(graphs_dir=tmp_path)
        invalid_graph = {
            "nodes": [
                {"id": "n1", "label": "N1", "type": "concept"},
                {"id": "n2", "label": "N2", "type": "concept"}
            ],
            "edges": [{"source": "n1", "label": "related"}]  # Missing 'target'
        }

        result = loader.save_graph("test", invalid_graph)

        assert result is False

    def test_save_rejects_edge_to_nonexistent_node(self, tmp_path):
        """Verify save_graph rejects edges referencing nonexistent nodes.

        RED: Should FAIL - No referential integrity validation yet
        """
        loader = GraphLoader(graphs_dir=tmp_path)
        invalid_graph = {
            "nodes": [
                {"id": "n1", "label": "N1", "type": "concept"}
            ],
            "edges": [
                {"source": "n1", "target": "nonexistent", "label": "related"}
            ]
        }

        result = loader.save_graph("test", invalid_graph)

        assert result is False

    def test_save_accepts_valid_edges(self, tmp_path):
        """Verify save_graph accepts valid edges.

        RED: Should FAIL - No validation yet
        """
        loader = GraphLoader(graphs_dir=tmp_path)
        valid_graph = {
            "nodes": [
                {"id": "n1", "label": "N1", "type": "concept"},
                {"id": "n2", "label": "N2", "type": "concept"}
            ],
            "edges": [
                {"source": "n1", "target": "n2", "label": "related"}
            ]
        }

        result = loader.save_graph("test", valid_graph)

        assert result is True


# Run these tests to verify they FAIL (RED phase)
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
