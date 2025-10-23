"""Integrity tools for MCP server.

Provides 3 MCP tools for graph validation and repair:
- check_graph: Validate a single graph
- check_all_graphs: Validate all graphs
- repair_graph: Repair a corrupted graph

Also exports core checker classes:
- IntegrityChecker: Validate and repair graphs
- ValidationResult: Result of validation
- RepairResult: Result of repair attempt
- Summary: Summary statistics
"""

from triads.tools.integrity.checker import (
    IntegrityChecker,
    ValidationResult,
    RepairResult,
    Summary,
)
from triads.tools.integrity.entrypoint import IntegrityTools

__all__ = [
    "IntegrityTools",
    "IntegrityChecker",
    "ValidationResult",
    "RepairResult",
    "Summary",
]
