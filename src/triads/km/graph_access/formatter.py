"""Markdown output formatting for knowledge graph CLI commands.

This module handles:
- format_status() - Graph status table
- format_search_results() - Search result formatting
- format_node_details() - Node detail view
- Consistent markdown output for all CLI commands
"""

from __future__ import annotations

import json
from typing import Any

from triads.km.graph_access.searcher import SearchResult


# ============================================================================
# GraphFormatter: Markdown output formatting
# ============================================================================


class GraphFormatter:
    """Markdown formatters for command output.

    Provides consistent, readable formatting for all knowledge graph
    CLI command outputs.

    Example:
        formatter = GraphFormatter()
        status = formatter.format_status(graphs)
        print(status)
    """

    @staticmethod
    def format_status(
        graphs: dict[str, dict[str, Any]], triad: str | None = None
    ) -> str:
        """Format /knowledge-status output as markdown table.

        Args:
            graphs: Dictionary of {triad_name: graph_data}
            triad: Optional triad name for single-triad view

        Returns:
            Markdown formatted status report

        Example:
            status = formatter.format_status(all_graphs)
            # Returns table with Triad | Nodes | Edges | Types | Avg Confidence
        """
        if not graphs:
            return "**No knowledge graphs found**\n\nNo graphs exist in `.claude/graphs/` directory."

        # Filter to single triad if specified
        if triad:
            if triad not in graphs:
                available = ", ".join(sorted(graphs.keys()))
                return f"**Graph '{triad}' not found**\n\nAvailable graphs: {available}"
            graphs = {triad: graphs[triad]}

        # Calculate summary statistics
        total_nodes = sum(len(g.get("nodes", [])) for g in graphs.values())
        total_edges = sum(len(g.get("links", [])) for g in graphs.values())

        lines = ["# Knowledge Graph Status\n"]
        lines.append(f"**Graphs**: {len(graphs)}")
        lines.append(f"**Total Nodes**: {total_nodes}")
        lines.append(f"**Total Edges**: {total_edges}\n")

        # Table header
        lines.append("| Triad | Nodes | Edges | Types | Avg Confidence |")
        lines.append("|-------|-------|-------|-------|----------------|")

        # Table rows
        for triad_name in sorted(graphs.keys()):
            graph = graphs[triad_name]
            nodes = graph.get("nodes", [])
            edges = graph.get("links", [])

            # Count node types
            types = set(n.get("type", "Unknown") for n in nodes)
            type_count = len(types)

            # Calculate average confidence
            confidences = []
            for node in nodes:
                try:
                    conf = float(node.get("confidence", 0))
                    confidences.append(conf)
                except (ValueError, TypeError):
                    pass

            avg_conf = sum(confidences) / len(confidences) if confidences else 0.0

            lines.append(
                f"| {triad_name} | {len(nodes)} | {len(edges)} | "
                f"{type_count} | {avg_conf:.2f} |"
            )

        # Add node type breakdown if single triad
        if triad and len(graphs) == 1:
            lines.append("\n## Node Type Breakdown\n")
            graph = list(graphs.values())[0]
            nodes = graph.get("nodes", [])

            # Count by type
            type_counts: dict[str, int] = {}
            for node in nodes:
                node_type = node.get("type", "Unknown")
                type_counts[node_type] = type_counts.get(node_type, 0) + 1

            for node_type in sorted(type_counts.keys()):
                count = type_counts[node_type]
                lines.append(f"- **{node_type}**: {count}")

        return "\n".join(lines)

    @staticmethod
    def format_search_results(
        results: list[SearchResult], query: str
    ) -> str:
        """Format /knowledge-search output.

        Args:
            results: List of SearchResult objects
            query: Original search query

        Returns:
            Markdown formatted search results

        Example:
            output = formatter.format_search_results(results, "OAuth")
        """
        if not results:
            return (
                f"**No results found for: '{query}'**\n\n"
                f"**Suggestions:**\n"
                f"- Try a broader search term\n"
                f"- Check available triads with `/knowledge-status`\n"
                f"- Search without filters (triad, type, confidence)\n"
            )

        lines = [f"# Search Results: '{query}'\n"]
        lines.append(f"**Found**: {len(results)} nodes\n")

        # Group by triad
        by_triad: dict[str, list[SearchResult]] = {}
        for result in results:
            if result.triad not in by_triad:
                by_triad[result.triad] = []
            by_triad[result.triad].append(result)

        # Format each triad's results
        for triad_name in sorted(by_triad.keys()):
            triad_results = by_triad[triad_name]
            lines.append(f"## {triad_name} ({len(triad_results)} results)\n")

            for result in triad_results:
                # Node header
                lines.append(
                    f"### {result.label} (`{result.node_id}`)\n"
                )

                # Metadata
                lines.append(
                    f"**Type**: {result.node_type} | "
                    f"**Confidence**: {result.confidence:.2f} | "
                    f"**Match**: {result.matched_field}\n"
                )

                # Snippet
                lines.append(f"> {result.snippet}\n")

        return "\n".join(lines)

    @staticmethod
    def format_node_details(
        node: dict[str, Any], triad: str, graph: dict[str, Any]
    ) -> str:
        """Format /knowledge-show output.

        Args:
            node: Node dictionary
            triad: Triad name
            graph: Full graph data (for relationships)

        Returns:
            Markdown formatted node details

        Example:
            details = formatter.format_node_details(node, 'design', graph)
        """
        node_id = node.get("id", "Unknown")
        label = node.get("label", node_id)

        lines = [f"# {label}\n"]
        lines.append(f"**ID**: `{node_id}`")
        lines.append(f"**Triad**: {triad}\n")

        # Core attributes
        lines.append("## Attributes\n")

        # Type and confidence
        lines.append(f"**Type**: {node.get('type', 'Unknown')}")

        confidence = node.get("confidence", 0)
        try:
            conf_value = float(confidence)
            lines.append(f"**Confidence**: {conf_value:.2f}")
        except (ValueError, TypeError):
            lines.append(f"**Confidence**: {confidence}")

        # Description
        description = node.get("description")
        if description:
            lines.append(f"\n**Description**:\n{description}\n")

        # Evidence
        evidence = node.get("evidence")
        if evidence:
            lines.append(f"**Evidence**:\n{evidence}\n")

        # Created/Updated
        created_by = node.get("created_by")
        if created_by:
            lines.append(f"**Created By**: {created_by}")

        created_at = node.get("created_at")
        if created_at:
            lines.append(f"**Created**: {created_at}")

        updated_at = node.get("updated_at")
        if updated_at:
            lines.append(f"**Updated**: {updated_at}")

        # Additional properties (exclude standard ones)
        standard_keys = {
            "id",
            "label",
            "type",
            "description",
            "confidence",
            "evidence",
            "created_by",
            "created_at",
            "updated_at",
        }

        additional = {k: v for k, v in node.items() if k not in standard_keys}
        if additional:
            lines.append("\n## Additional Properties\n")
            for key, value in sorted(additional.items()):
                # Format value
                if isinstance(value, (list, dict)):
                    value_str = json.dumps(value, indent=2)
                    lines.append(f"**{key}**:\n```json\n{value_str}\n```")
                else:
                    lines.append(f"**{key}**: {value}")

        # Relationships (edges)
        edges = graph.get("links", [])
        outgoing = [e for e in edges if e.get("source") == node_id]
        incoming = [e for e in edges if e.get("target") == node_id]

        if outgoing or incoming:
            lines.append("\n## Relationships\n")

        if outgoing:
            lines.append(f"**Outgoing** ({len(outgoing)}):")
            for edge in outgoing:
                target = edge.get("target", "Unknown")
                rel_type = edge.get("key", "relates_to")
                lines.append(f"- {rel_type} → `{target}`")

        if incoming:
            lines.append(f"\n**Incoming** ({len(incoming)}):")
            for edge in incoming:
                source = edge.get("source", "Unknown")
                rel_type = edge.get("key", "relates_to")
                lines.append(f"- `{source}` → {rel_type}")

        return "\n".join(lines)
