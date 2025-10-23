"""
Shared utilities for MCP-compliant tool system.

Exports:
    - ToolResult: MCP-compliant result format
    - ToolError: Base exception for tool errors
"""

from .exceptions import ToolError
from .result import ToolResult

__all__ = [
    "ToolResult",
    "ToolError",
]
