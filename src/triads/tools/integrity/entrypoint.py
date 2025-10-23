"""
Entrypoint for integrity MCP tools.

Provides 3 MCP-compliant tools for graph validation and repair:
- check_graph: Validate a single graph
- check_all_graphs: Validate all graphs
- repair_graph: Repair a corrupted graph
"""

from pathlib import Path

from triads.tools.shared import ToolResult

from .bootstrap import bootstrap_integrity_service
from .formatters import (
    format_all_validation_results,
    format_repair_result,
    format_validation_result,
)


class IntegrityTools:
    """
    MCP tools for graph integrity checking and repair.

    Provides static methods that return MCP-compliant ToolResult objects.
    """

    @staticmethod
    def check_graph(triad: str, graphs_dir: Path | str | None = None) -> ToolResult:
        """
        Validate a single knowledge graph.

        Args:
            triad: Name of the triad graph to check
            graphs_dir: Directory containing graph files (default: .claude/graphs)

        Returns:
            ToolResult with validation report
        """
        try:
            service = bootstrap_integrity_service(graphs_dir=graphs_dir)
            result = service.check_graph(triad)
            formatted = format_validation_result(result)

            return ToolResult(
                success=True,
                content=[{"type": "text", "text": formatted}]
            )
        except Exception as e:
            return ToolResult(
                success=False,
                content=[],
                error=f"Failed to check graph '{triad}': {str(e)}"
            )

    @staticmethod
    def check_all_graphs(graphs_dir: Path | str | None = None) -> ToolResult:
        """
        Validate all knowledge graphs in the directory.

        Args:
            graphs_dir: Directory containing graph files (default: .claude/graphs)

        Returns:
            ToolResult with summary report of all graphs
        """
        try:
            service = bootstrap_integrity_service(graphs_dir=graphs_dir)
            results = service.check_all_graphs()
            formatted = format_all_validation_results(results)

            return ToolResult(
                success=True,
                content=[{"type": "text", "text": formatted}]
            )
        except Exception as e:
            return ToolResult(
                success=False,
                content=[],
                error=f"Failed to check graphs: {str(e)}"
            )

    @staticmethod
    def repair_graph(
        triad: str,
        create_backup: bool = True,
        graphs_dir: Path | str | None = None
    ) -> ToolResult:
        """
        Attempt to repair a corrupted knowledge graph.

        Args:
            triad: Name of the triad graph to repair
            create_backup: Whether to create backup before repair (default: True)
            graphs_dir: Directory containing graph files (default: .claude/graphs)

        Returns:
            ToolResult with repair report
        """
        try:
            service = bootstrap_integrity_service(graphs_dir=graphs_dir)
            result = service.repair_graph(triad, create_backup=create_backup)
            formatted = format_repair_result(result)

            return ToolResult(
                success=True,
                content=[{"type": "text", "text": formatted}]
            )
        except Exception as e:
            return ToolResult(
                success=False,
                content=[],
                error=f"Failed to repair graph '{triad}': {str(e)}"
            )
