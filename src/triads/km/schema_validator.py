"""Knowledge graph schema validation.

This module provides validation for knowledge graph structure and content
before saving to prevent corruption from invalid data.

Validates:
- Graph structure (must have nodes and edges)
- Node fields (id, label, type required)
- Node types (concept, decision, entity, finding, task, workflow, uncertainty)
- Confidence values (0.0-1.0 range)
- Edge structure (source, target required)
- Referential integrity (edges reference existing nodes)
"""

from __future__ import annotations

import logging
from typing import Any

# Initialize module logger
logger = logging.getLogger(__name__)

# Valid node types
VALID_NODE_TYPES = {
    "concept",
    "decision",
    "entity",
    "finding",
    "task",
    "workflow",
    "uncertainty",
}


class ValidationError(Exception):
    """Raised when graph validation fails."""

    def __init__(self, message: str, field: str | None = None) -> None:
        self.message = message
        self.field = field
        super().__init__(message)


def validate_graph_structure(graph_data: Any) -> bool:
    """Validate basic graph structure.

    Args:
        graph_data: Graph data to validate

    Returns:
        True if valid

    Raises:
        ValidationError: If validation fails
    """
    # Must be a dictionary
    if not isinstance(graph_data, dict):
        raise ValidationError(
            f"Graph must be a dictionary, got {type(graph_data).__name__}",
            field="graph",
        )

    # Must have 'nodes' key
    if "nodes" not in graph_data:
        raise ValidationError("Graph must have 'nodes' key", field="nodes")

    # Must have 'edges' or 'links' key (NetworkX uses 'links')
    if "edges" not in graph_data and "links" not in graph_data:
        raise ValidationError("Graph must have 'edges' or 'links' key", field="edges")

    # Nodes must be a list
    if not isinstance(graph_data["nodes"], list):
        raise ValidationError(
            f"Nodes must be a list, got {type(graph_data['nodes']).__name__}",
            field="nodes",
        )

    # Edges/links must be a list
    edges_key = "edges" if "edges" in graph_data else "links"
    if not isinstance(graph_data[edges_key], list):
        raise ValidationError(
            f"Edges must be a list, got {type(graph_data[edges_key]).__name__}",
            field=edges_key,
        )

    return True


def validate_node(node: dict[str, Any], index: int) -> bool:
    """Validate a single node.

    Args:
        node: Node data to validate
        index: Node index in nodes list (for error messages)

    Returns:
        True if valid

    Raises:
        ValidationError: If validation fails
    """
    # Node must be a dictionary
    if not isinstance(node, dict):
        raise ValidationError(
            f"Node at index {index} must be a dictionary, got {type(node).__name__}",
            field=f"nodes[{index}]",
        )

    # Must have 'id' field
    if "id" not in node:
        raise ValidationError(
            f"Node at index {index} missing required field 'id'",
            field=f"nodes[{index}].id",
        )

    # Must have 'label' field
    if "label" not in node:
        raise ValidationError(
            f"Node at index {index} (id: {node.get('id')}) missing required field 'label'",
            field=f"nodes[{index}].label",
        )

    # Must have 'type' field
    if "type" not in node:
        raise ValidationError(
            f"Node at index {index} (id: {node.get('id')}) missing required field 'type'",
            field=f"nodes[{index}].type",
        )

    # Type must be valid (case-insensitive)
    if node["type"].lower() not in VALID_NODE_TYPES:
        raise ValidationError(
            f"Node at index {index} (id: {node.get('id')}) has invalid type '{node['type']}'. "
            f"Valid types: {', '.join(sorted(VALID_NODE_TYPES))}",
            field=f"nodes[{index}].type",
        )

    # If confidence is present, validate range
    if "confidence" in node:
        confidence = node["confidence"]
        if not isinstance(confidence, (int, float)):
            raise ValidationError(
                f"Node at index {index} (id: {node.get('id')}) has non-numeric confidence: {type(confidence).__name__}",
                field=f"nodes[{index}].confidence",
            )
        if confidence < 0.0 or confidence > 1.0:
            raise ValidationError(
                f"Node at index {index} (id: {node.get('id')}) has confidence {confidence} outside valid range [0.0, 1.0]",
                field=f"nodes[{index}].confidence",
            )

    return True


def validate_edge(edge: dict[str, Any], index: int, node_ids: set[str]) -> bool:
    """Validate a single edge.

    Args:
        edge: Edge data to validate
        index: Edge index in edges list (for error messages)
        node_ids: Set of valid node IDs for referential integrity

    Returns:
        True if valid

    Raises:
        ValidationError: If validation fails
    """
    # Edge must be a dictionary
    if not isinstance(edge, dict):
        raise ValidationError(
            f"Edge at index {index} must be a dictionary, got {type(edge).__name__}",
            field=f"edges[{index}]",
        )

    # Must have 'source' field
    if "source" not in edge:
        raise ValidationError(
            f"Edge at index {index} missing required field 'source'",
            field=f"edges[{index}].source",
        )

    # Must have 'target' field
    if "target" not in edge:
        raise ValidationError(
            f"Edge at index {index} missing required field 'target'",
            field=f"edges[{index}].target",
        )

    # Source must reference existing node
    if edge["source"] not in node_ids:
        raise ValidationError(
            f"Edge at index {index} references non-existent source node '{edge['source']}'",
            field=f"edges[{index}].source",
        )

    # Target must reference existing node
    if edge["target"] not in node_ids:
        raise ValidationError(
            f"Edge at index {index} references non-existent target node '{edge['target']}'",
            field=f"edges[{index}].target",
        )

    return True


def validate_graph(graph_data: Any) -> bool:
    """Validate complete graph structure and content.

    Args:
        graph_data: Graph data to validate

    Returns:
        True if valid

    Raises:
        ValidationError: If validation fails with detailed error message
    """
    # Validate basic structure
    validate_graph_structure(graph_data)

    # Validate each node
    node_ids = set()
    for i, node in enumerate(graph_data["nodes"]):
        validate_node(node, i)
        node_ids.add(node["id"])

    # Validate each edge (handle both 'edges' and 'links' keys)
    edges_key = "edges" if "edges" in graph_data else "links"
    for i, edge in enumerate(graph_data[edges_key]):
        validate_edge(edge, i, node_ids)

    logger.debug(
        "Graph validation successful",
        extra={
            "nodes_count": len(graph_data["nodes"]),
            "edges_count": len(graph_data[edges_key]),
        },
    )

    return True
