"""Tests for agent output validation.

This module tests parsing and validating [GRAPH_UPDATE] blocks from agent
outputs BEFORE they're applied to graphs. Prevents corrupted agent output
from reaching knowledge graphs.

RED Phase: These tests should FAIL initially (feature not implemented yet).
"""

import pytest

from triads.km.agent_output_validator import (
    AgentOutputValidator,
    GraphUpdateBlock,
    ParseError,
    ValidationError,
)


class TestGraphUpdateBlockParsing:
    """Test parsing [GRAPH_UPDATE] blocks from agent output."""

    def test_parse_single_update_block(self):
        """Verify parsing a single valid [GRAPH_UPDATE] block.

        RED: Should FAIL - Parser not implemented yet
        """
        agent_output = """
Some agent text here.

[GRAPH_UPDATE]
type: add_node
node_id: test_node_1
node_type: Entity
label: Test Node
description: A test node
confidence: 0.95
created_by: test-agent
[/GRAPH_UPDATE]

More agent text here.
"""
        validator = AgentOutputValidator()
        blocks = validator.parse_update_blocks(agent_output)

        assert len(blocks) == 1
        assert blocks[0].node_id == "test_node_1"
        assert blocks[0].node_type == "Entity"
        assert blocks[0].label == "Test Node"
        assert blocks[0].confidence == 0.95

    def test_parse_multiple_update_blocks(self):
        """Verify parsing multiple [GRAPH_UPDATE] blocks in single output.

        RED: Should FAIL - Parser not implemented yet
        """
        agent_output = """
First update:

[GRAPH_UPDATE]
type: add_node
node_id: node_1
node_type: Concept
label: Node One
confidence: 0.9
created_by: test-agent
[/GRAPH_UPDATE]

Second update:

[GRAPH_UPDATE]
type: add_node
node_id: node_2
node_type: Decision
label: Node Two
confidence: 0.85
created_by: test-agent
[/GRAPH_UPDATE]
"""
        validator = AgentOutputValidator()
        blocks = validator.parse_update_blocks(agent_output)

        assert len(blocks) == 2
        assert blocks[0].node_id == "node_1"
        assert blocks[1].node_id == "node_2"

    def test_parse_no_update_blocks(self):
        """Verify handling output with no [GRAPH_UPDATE] blocks.

        RED: Should FAIL - Parser not implemented yet
        """
        agent_output = """
Just some regular agent output with no updates.
Nothing to parse here.
"""
        validator = AgentOutputValidator()
        blocks = validator.parse_update_blocks(agent_output)

        assert len(blocks) == 0

    def test_parse_malformed_block_missing_closing_tag(self):
        """Verify error on malformed block (missing closing tag).

        RED: Should FAIL - Error handling not implemented yet
        """
        agent_output = """
[GRAPH_UPDATE]
type: add_node
node_id: test_node
node_type: Concept
label: Test Node
"""
        validator = AgentOutputValidator()

        with pytest.raises(ParseError) as exc_info:
            validator.parse_update_blocks(agent_output)

        assert "missing closing tag" in str(exc_info.value).lower()

    def test_parse_empty_block(self):
        """Verify error on empty [GRAPH_UPDATE] block.

        RED: Should FAIL - Validation not implemented yet
        """
        agent_output = """
[GRAPH_UPDATE]
[/GRAPH_UPDATE]
"""
        validator = AgentOutputValidator()

        with pytest.raises(ParseError) as exc_info:
            validator.parse_update_blocks(agent_output)

        assert "empty" in str(exc_info.value).lower()

    def test_parse_block_with_invalid_yaml(self):
        """Verify error on block with malformed YAML-like content.

        RED: Should FAIL - YAML parsing not implemented yet
        """
        agent_output = """
[GRAPH_UPDATE]
type: add_node
invalid yaml structure
missing colons and proper format
[/GRAPH_UPDATE]
"""
        validator = AgentOutputValidator()

        with pytest.raises(ParseError) as exc_info:
            validator.parse_update_blocks(agent_output)

        assert "invalid" in str(exc_info.value).lower() or "parse" in str(exc_info.value).lower()


class TestGraphUpdateBlockValidation:
    """Test validating [GRAPH_UPDATE] blocks against schema."""

    def test_validate_add_node_block(self):
        """Verify validation of valid add_node block.

        RED: Should FAIL - Validation not implemented yet
        """
        agent_output = """
[GRAPH_UPDATE]
type: add_node
node_id: impl_auth_system
node_type: Entity
label: Authentication System
description: Implemented OAuth2 authentication
confidence: 1.0
file_path: src/auth/oauth.py
lines: 1-150
implements: task_oauth_integration
created_by: senior-developer
[/GRAPH_UPDATE]
"""
        validator = AgentOutputValidator()
        blocks = validator.parse_and_validate(agent_output)

        assert len(blocks) == 1
        assert blocks[0].is_valid is True

    def test_validate_rejects_missing_required_field(self):
        """Verify validation rejects block missing required field.

        RED: Should FAIL - Required field validation not implemented yet
        """
        agent_output = """
[GRAPH_UPDATE]
type: add_node
node_id: test_node
# Missing node_type (required)
label: Test Node
confidence: 0.9
created_by: test-agent
[/GRAPH_UPDATE]
"""
        validator = AgentOutputValidator()

        with pytest.raises(ValidationError) as exc_info:
            validator.parse_and_validate(agent_output)

        assert "node_type" in str(exc_info.value).lower()

    def test_validate_rejects_invalid_node_type(self):
        """Verify validation rejects invalid node_type.

        RED: Should FAIL - Node type validation not implemented yet
        """
        agent_output = """
[GRAPH_UPDATE]
type: add_node
node_id: test_node
node_type: InvalidType
label: Test Node
confidence: 0.9
created_by: test-agent
[/GRAPH_UPDATE]
"""
        validator = AgentOutputValidator()

        with pytest.raises(ValidationError) as exc_info:
            validator.parse_and_validate(agent_output)

        assert "invalid" in str(exc_info.value).lower() and "type" in str(exc_info.value).lower()

    def test_validate_rejects_invalid_confidence(self):
        """Verify validation rejects confidence outside [0.0, 1.0].

        RED: Should FAIL - Confidence validation not implemented yet
        """
        agent_output = """
[GRAPH_UPDATE]
type: add_node
node_id: test_node
node_type: Concept
label: Test Node
confidence: 1.5
created_by: test-agent
[/GRAPH_UPDATE]
"""
        validator = AgentOutputValidator()

        with pytest.raises(ValidationError) as exc_info:
            validator.parse_and_validate(agent_output)

        assert "confidence" in str(exc_info.value).lower()

    def test_validate_add_edge_block(self):
        """Verify validation of valid add_edge block.

        RED: Should FAIL - Edge validation not implemented yet
        """
        agent_output = """
[GRAPH_UPDATE]
type: add_edge
source: node_1
target: node_2
key: implements
rationale: Node 1 implements Node 2
confidence: 0.95
created_by: test-agent
[/GRAPH_UPDATE]
"""
        validator = AgentOutputValidator()
        blocks = validator.parse_and_validate(agent_output)

        assert len(blocks) == 1
        assert blocks[0].type == "add_edge"
        assert blocks[0].source == "node_1"
        assert blocks[0].target == "node_2"

    def test_validate_edge_missing_source(self):
        """Verify validation rejects edge missing source.

        RED: Should FAIL - Edge validation not implemented yet
        """
        agent_output = """
[GRAPH_UPDATE]
type: add_edge
target: node_2
key: implements
created_by: test-agent
[/GRAPH_UPDATE]
"""
        validator = AgentOutputValidator()

        with pytest.raises(ValidationError) as exc_info:
            validator.parse_and_validate(agent_output)

        assert "source" in str(exc_info.value).lower()

    def test_validate_edge_missing_target(self):
        """Verify validation rejects edge missing target.

        RED: Should FAIL - Edge validation not implemented yet
        """
        agent_output = """
[GRAPH_UPDATE]
type: add_edge
source: node_1
key: implements
created_by: test-agent
[/GRAPH_UPDATE]
"""
        validator = AgentOutputValidator()

        with pytest.raises(ValidationError) as exc_info:
            validator.parse_and_validate(agent_output)

        assert "target" in str(exc_info.value).lower()


class TestGraphUpdateBlockIntegration:
    """Test integration with GraphLoader to prevent corrupted updates."""

    def test_safe_apply_valid_update(self, tmp_path):
        """Verify valid update is applied to graph.

        RED: Should FAIL - Integration not implemented yet
        """
        from triads.km.graph_access import GraphLoader

        # Create initial graph
        loader = GraphLoader(graphs_dir=tmp_path)
        initial_graph = {
            "nodes": [
                {"id": "node_1", "label": "Node 1", "type": "concept"}
            ],
            "edges": []
        }
        loader.save_graph("test", initial_graph)

        # Apply update
        agent_output = """
[GRAPH_UPDATE]
type: add_node
node_id: node_2
node_type: Concept
label: Node 2
description: Second node
confidence: 0.9
created_by: test-agent
[/GRAPH_UPDATE]
"""
        validator = AgentOutputValidator()
        blocks = validator.parse_and_validate(agent_output)

        # Apply to graph
        success = validator.apply_updates(blocks, loader, "test")

        assert success is True

        # Verify node was added
        graph = loader.load_graph("test")
        assert len(graph["nodes"]) == 2
        assert graph["nodes"][1]["id"] == "node_2"

    def test_safe_apply_rejects_invalid_update(self, tmp_path):
        """Verify invalid update is NOT applied to graph.

        RED: Should FAIL - Validation integration not implemented yet
        """
        from triads.km.graph_access import GraphLoader

        # Create initial graph
        loader = GraphLoader(graphs_dir=tmp_path)
        initial_graph = {
            "nodes": [
                {"id": "node_1", "label": "Node 1", "type": "concept"}
            ],
            "edges": []
        }
        loader.save_graph("test", initial_graph)

        # Attempt to apply invalid update
        agent_output = """
[GRAPH_UPDATE]
type: add_node
node_id: node_2
node_type: InvalidType
label: Node 2
confidence: 1.5
created_by: test-agent
[/GRAPH_UPDATE]
"""
        validator = AgentOutputValidator()

        with pytest.raises(ValidationError):
            blocks = validator.parse_and_validate(agent_output)
            validator.apply_updates(blocks, loader, "test")

        # Verify graph unchanged
        graph = loader.load_graph("test")
        assert len(graph["nodes"]) == 1

    def test_safe_apply_atomic_multiple_updates(self, tmp_path):
        """Verify multiple updates applied atomically (all or nothing).

        RED: Should FAIL - Atomic updates not implemented yet
        """
        from triads.km.graph_access import GraphLoader

        # Create initial graph
        loader = GraphLoader(graphs_dir=tmp_path)
        initial_graph = {
            "nodes": [
                {"id": "node_1", "label": "Node 1", "type": "concept"}
            ],
            "edges": []
        }
        loader.save_graph("test", initial_graph)

        # Multiple updates, second is invalid
        agent_output = """
[GRAPH_UPDATE]
type: add_node
node_id: node_2
node_type: Concept
label: Node 2
confidence: 0.9
created_by: test-agent
[/GRAPH_UPDATE]

[GRAPH_UPDATE]
type: add_node
node_id: node_3
node_type: InvalidType
label: Node 3
confidence: 1.5
created_by: test-agent
[/GRAPH_UPDATE]
"""
        validator = AgentOutputValidator()

        with pytest.raises(ValidationError):
            blocks = validator.parse_and_validate(agent_output)
            validator.apply_updates(blocks, loader, "test")

        # Verify graph unchanged (neither update applied)
        graph = loader.load_graph("test")
        assert len(graph["nodes"]) == 1


class TestGraphUpdateBlockHelpers:
    """Test helper functions for working with update blocks."""

    def test_block_to_node_dict(self):
        """Verify converting GraphUpdateBlock to node dictionary.

        RED: Should FAIL - Conversion not implemented yet
        """
        agent_output = """
[GRAPH_UPDATE]
type: add_node
node_id: test_node
node_type: Entity
label: Test Node
description: A test
confidence: 0.95
created_by: test-agent
[/GRAPH_UPDATE]
"""
        validator = AgentOutputValidator()
        blocks = validator.parse_and_validate(agent_output)

        node_dict = blocks[0].to_node_dict()

        assert node_dict["id"] == "test_node"
        assert node_dict["type"] == "entity"  # Normalized to lowercase
        assert node_dict["label"] == "Test Node"
        assert node_dict["confidence"] == 0.95

    def test_block_to_edge_dict(self):
        """Verify converting GraphUpdateBlock to edge dictionary.

        RED: Should FAIL - Conversion not implemented yet
        """
        agent_output = """
[GRAPH_UPDATE]
type: add_edge
source: node_1
target: node_2
key: implements
rationale: Test relationship
confidence: 0.9
created_by: test-agent
[/GRAPH_UPDATE]
"""
        validator = AgentOutputValidator()
        blocks = validator.parse_and_validate(agent_output)

        edge_dict = blocks[0].to_edge_dict()

        assert edge_dict["source"] == "node_1"
        assert edge_dict["target"] == "node_2"
        assert edge_dict["key"] == "implements"
        assert edge_dict["rationale"] == "Test relationship"
