"""
Tests for MCP-compliant ToolResult format.

Following TDD (RED-GREEN-REFACTOR):
- RED: These tests fail initially (ToolResult not implemented)
- GREEN: Implement ToolResult to make tests pass
- REFACTOR: Improve implementation quality

MCP Specification Reference:
https://modelcontextprotocol.io/specification/2025-06-18/server/tools

Tool results must include:
- content: Array of content items (text, image, resource, etc.)
- isError: Boolean flag
- Each content item has a 'type' field
"""

import pytest
from dataclasses import FrozenInstanceError


def test_tool_result_text_content_mcp_compliant():
    """Test that ToolResult with text content matches MCP specification."""
    from triads.tools.shared import ToolResult

    # Create result with text content
    result = ToolResult(
        success=True,
        content=[{
            "type": "text",
            "text": "Query returned 5 nodes"
        }]
    )

    # Validate MCP-compliant structure
    assert result.success is True
    assert isinstance(result.content, list)
    assert len(result.content) == 1

    content_item = result.content[0]
    assert content_item["type"] == "text"
    assert "text" in content_item
    assert content_item["text"] == "Query returned 5 nodes"

    # Should not have isError=True when success=True
    assert result.error is None


def test_tool_result_resource_content_mcp_compliant():
    """Test that ToolResult with resource content matches MCP specification."""
    from triads.tools.shared import ToolResult

    # Create result with resource content (for generate_agents tool)
    result = ToolResult(
        success=True,
        content=[{
            "type": "resource",
            "resource": {
                "uri": "triads://agents/investigator.md",
                "mimeType": "text/markdown",
                "text": "---\nname: investigator\n---\n"
            }
        }]
    )

    # Validate MCP-compliant structure
    assert result.success is True
    assert len(result.content) == 1

    content_item = result.content[0]
    assert content_item["type"] == "resource"
    assert "resource" in content_item

    resource = content_item["resource"]
    assert resource["uri"] == "triads://agents/investigator.md"
    assert resource["mimeType"] == "text/markdown"
    assert "text" in resource


def test_tool_result_multiple_content_items():
    """Test that ToolResult can have multiple content items."""
    from triads.tools.shared import ToolResult

    result = ToolResult(
        success=True,
        content=[
            {"type": "text", "text": "Found 3 nodes:"},
            {"type": "text", "text": "- Node 1\n- Node 2\n- Node 3"}
        ]
    )

    assert len(result.content) == 2
    assert all(item["type"] == "text" for item in result.content)


def test_tool_result_error_format():
    """Test that ToolResult error format matches MCP spec."""
    from triads.tools.shared import ToolResult

    # Create error result
    result = ToolResult(
        success=False,
        content=[],
        error="Graph 'invalid-triad' not found"
    )

    # Validate error structure
    assert result.success is False
    assert result.error == "Graph 'invalid-triad' not found"
    assert result.content == []  # Error results can have empty content


def test_tool_result_validates_content_type():
    """Test that ToolResult validates content item types."""
    from triads.tools.shared import ToolResult, ToolError

    # Invalid content type should raise error
    with pytest.raises(ToolError) as exc_info:
        ToolResult(
            success=True,
            content=[{
                "type": "invalid_type",
                "data": "something"
            }]
        )

    assert "invalid content type" in str(exc_info.value).lower()


def test_tool_result_text_content_missing_text_field():
    """Test that text content items must have 'text' field."""
    from triads.tools.shared import ToolResult, ToolError

    with pytest.raises(ToolError) as exc_info:
        ToolResult(
            success=True,
            content=[{
                "type": "text"
                # Missing 'text' field
            }]
        )

    assert "text" in str(exc_info.value).lower()


def test_tool_result_resource_content_missing_required_fields():
    """Test that resource content items must have required fields."""
    from triads.tools.shared import ToolResult, ToolError

    # Missing 'resource' field
    with pytest.raises(ToolError) as exc_info:
        ToolResult(
            success=True,
            content=[{
                "type": "resource"
                # Missing 'resource' field
            }]
        )

    assert "resource" in str(exc_info.value).lower()

    # Resource missing 'uri'
    with pytest.raises(ToolError) as exc_info:
        ToolResult(
            success=True,
            content=[{
                "type": "resource",
                "resource": {
                    "mimeType": "text/plain",
                    "text": "content"
                    # Missing 'uri'
                }
            }]
        )

    assert "uri" in str(exc_info.value).lower()


def test_tool_result_immutable():
    """Test that ToolResult is immutable (frozen dataclass)."""
    from triads.tools.shared import ToolResult

    result = ToolResult(
        success=True,
        content=[{"type": "text", "text": "test"}]
    )

    # Should not be able to modify
    with pytest.raises(FrozenInstanceError):
        result.success = False


def test_tool_result_metadata_optional():
    """Test that metadata field is optional."""
    from triads.tools.shared import ToolResult

    # Without metadata
    result1 = ToolResult(
        success=True,
        content=[{"type": "text", "text": "test"}]
    )
    assert result1.metadata == {}

    # With metadata
    result2 = ToolResult(
        success=True,
        content=[{"type": "text", "text": "test"}],
        metadata={"tool_name": "query_graph", "duration_ms": 150}
    )
    assert result2.metadata["tool_name"] == "query_graph"
    assert result2.metadata["duration_ms"] == 150


def test_tool_result_to_mcp_format():
    """Test conversion to MCP protocol format."""
    from triads.tools.shared import ToolResult

    result = ToolResult(
        success=True,
        content=[{"type": "text", "text": "Success"}]
    )

    # Should have method to convert to MCP format
    mcp_format = result.to_mcp()

    assert "content" in mcp_format
    assert "isError" in mcp_format
    assert mcp_format["isError"] is False
    assert mcp_format["content"] == result.content


def test_tool_result_to_mcp_format_with_error():
    """Test conversion to MCP format for error results."""
    from triads.tools.shared import ToolResult

    result = ToolResult(
        success=False,
        content=[],
        error="Something went wrong"
    )

    mcp_format = result.to_mcp()

    assert mcp_format["isError"] is True
    assert "error" in mcp_format or len(mcp_format["content"]) > 0
