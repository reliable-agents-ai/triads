"""Formatters for knowledge tool outputs.

Provides functions to format service results as human-readable text.
"""

from triads.tools.knowledge.service import QueryResult, StatusResult
from triads.tools.knowledge.domain import Node, KnowledgeGraph


def format_query_result(result: QueryResult) -> str:
    """Format QueryResult as human-readable text.

    Args:
        result: QueryResult from service

    Returns:
        Formatted text string

    Example:
        >>> result = QueryResult(nodes=[...], total=3)
        >>> text = format_query_result(result)
    """
    if result.total == 0:
        return "No nodes found matching query."

    lines = [f"Found {result.total} node(s):\n"]

    for node in result.nodes:
        lines.append(f"ID: {node.id}")
        lines.append(f"  Label: {node.label}")
        lines.append(f"  Type: {node.type}")
        lines.append(f"  Confidence: {node.confidence:.2f}")
        if node.content:
            # Truncate long content
            content = node.content[:200] + "..." if len(node.content) > 200 else node.content
            lines.append(f"  Content: {content}")
        lines.append("")  # Blank line

    return "\n".join(lines)


def format_status_result(result: StatusResult) -> str:
    """Format StatusResult as human-readable text.

    Args:
        result: StatusResult from service

    Returns:
        Formatted text string
    """
    if not result.graphs:
        return "No graphs found."

    lines = ["Knowledge Graph Status:\n"]

    for graph in result.graphs:
        lines.append(f"Triad: {graph.triad}")
        lines.append(f"  Nodes: {len(graph.nodes)}")
        lines.append(f"  Edges: {len(graph.edges)}")

        # Validation status
        is_valid, error = graph.validate()
        if is_valid:
            lines.append("  Status: Valid")
        else:
            lines.append(f"  Status: INVALID - {error}")

        lines.append("")  # Blank line

    return "\n".join(lines)


def format_node_details(node: Node | None) -> str:
    """Format node details as human-readable text.

    Args:
        node: Node to format, or None if not found

    Returns:
        Formatted text string
    """
    if node is None:
        return "Node not found."

    lines = [
        f"Node: {node.id}",
        f"Label: {node.label}",
        f"Type: {node.type}",
        f"Confidence: {node.confidence:.2f}",
    ]

    if node.content:
        lines.append(f"\nContent:\n{node.content}")

    if node.evidence:
        lines.append(f"\nEvidence:")
        for evidence in node.evidence:
            lines.append(f"  - {evidence}")

    if node.metadata:
        lines.append(f"\nMetadata:")
        for key, value in node.metadata.items():
            lines.append(f"  {key}: {value}")

    return "\n".join(lines)


def format_triad_list(triads: list[dict]) -> str:
    """Format triad list as human-readable text.

    Args:
        triads: List of triad dicts from service

    Returns:
        Formatted text string
    """
    if not triads:
        return "No triads found."

    lines = ["Available Knowledge Graphs:\n"]

    for triad in triads:
        lines.append(f"  {triad['name']}: {triad['node_count']} nodes")

    return "\n".join(lines)
