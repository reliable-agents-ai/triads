"""
MCP-compliant ToolResult format.

Implements Model Context Protocol (MCP) specification for tool results:
https://modelcontextprotocol.io/specification/2025-06-18/server/tools

Tool results must include:
- content: Array of content items (text, image, resource, etc.)
- isError: Boolean flag

Each content item has a 'type' field and type-specific fields.
"""

from dataclasses import dataclass, field
from typing import Any, Optional

from .exceptions import ToolError


# Supported content types (initially text and resource, can extend to image/audio later)
SUPPORTED_CONTENT_TYPES = {"text", "resource"}


@dataclass(frozen=True)
class ToolResult:
    """
    MCP-compliant tool result container.

    Represents the result of a tool execution in a format compliant with the
    Model Context Protocol specification.

    Attributes:
        success: Whether the tool execution succeeded
        content: Array of content items (text, resource, etc.)
        error: Optional error message (present when success=False)
        metadata: Optional metadata dictionary for tool execution details

    Example (text content):
        >>> result = ToolResult(
        ...     success=True,
        ...     content=[{"type": "text", "text": "Query returned 5 nodes"}]
        ... )

    Example (resource content):
        >>> result = ToolResult(
        ...     success=True,
        ...     content=[{
        ...         "type": "resource",
        ...         "resource": {
        ...             "uri": "triads://agents/investigator.md",
        ...             "mimeType": "text/markdown",
        ...             "text": "---\\nname: investigator\\n---\\n"
        ...         }
        ...     }]
        ... )

    Example (error result):
        >>> result = ToolResult(
        ...     success=False,
        ...     content=[],
        ...     error="Graph 'invalid-triad' not found"
        ... )
    """

    success: bool
    content: list[dict[str, Any]]
    error: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """
        Validate content structure after initialization.

        Raises:
            ToolError: If content items have invalid types or missing required fields
        """
        # Validate each content item
        for idx, item in enumerate(self.content):
            if not isinstance(item, dict):
                raise ToolError(f"Content item {idx} must be a dictionary")

            if "type" not in item:
                raise ToolError(f"Content item {idx} missing required 'type' field")

            content_type = item["type"]

            # Validate content type is supported
            if content_type not in SUPPORTED_CONTENT_TYPES:
                raise ToolError(
                    f"Content item {idx} has invalid content type '{content_type}'. "
                    f"Supported types: {', '.join(sorted(SUPPORTED_CONTENT_TYPES))}"
                )

            # Validate type-specific requirements
            if content_type == "text":
                self._validate_text_content(item, idx)
            elif content_type == "resource":
                self._validate_resource_content(item, idx)

    def _validate_text_content(self, item: dict[str, Any], idx: int) -> None:
        """
        Validate text content item has required fields.

        Args:
            item: Content item dictionary
            idx: Index of content item (for error messages)

        Raises:
            ToolError: If required fields are missing
        """
        if "text" not in item:
            raise ToolError(f"Text content item {idx} missing required 'text' field")

    def _validate_resource_content(self, item: dict[str, Any], idx: int) -> None:
        """
        Validate resource content item has required fields.

        Args:
            item: Content item dictionary
            idx: Index of content item (for error messages)

        Raises:
            ToolError: If required fields are missing
        """
        if "resource" not in item:
            raise ToolError(f"Resource content item {idx} missing required 'resource' field")

        resource = item["resource"]
        if not isinstance(resource, dict):
            raise ToolError(f"Resource content item {idx} 'resource' must be a dictionary")

        if "uri" not in resource:
            raise ToolError(f"Resource content item {idx} missing required 'uri' field in resource")

    def to_mcp(self) -> dict[str, Any]:
        """
        Convert to MCP protocol format.

        Returns a dictionary matching the MCP specification format:
        - content: Array of content items
        - isError: Boolean flag (inverted from success)

        For error results, the error message can be included either:
        - As a separate "error" field, OR
        - As a text content item

        Returns:
            Dictionary in MCP protocol format

        Example:
            >>> result = ToolResult(success=True, content=[{"type": "text", "text": "OK"}])
            >>> result.to_mcp()
            {"content": [{"type": "text", "text": "OK"}], "isError": False}
        """
        mcp_format = {
            "content": self.content,
            "isError": not self.success,
        }

        # Include error message if present
        if self.error is not None:
            mcp_format["error"] = self.error

        return mcp_format
