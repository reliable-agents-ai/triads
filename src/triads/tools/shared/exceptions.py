"""
Exceptions for MCP-compliant tool system.

Provides base ToolError exception and specific error types for validation failures.
"""


class ToolError(Exception):
    """
    Base exception for all tool-related errors.

    Used for validation errors, content type errors, and other tool operation failures.
    """
    pass
