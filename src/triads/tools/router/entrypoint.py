"""MCP tool entrypoints for router tools.

Provides 2 MCP-compliant tools for routing and state access.
"""

from triads.tools.shared import ToolResult
from triads.tools.router.bootstrap import bootstrap_router_service
from triads.tools.router.formatters import format_routing_decision, format_router_state


class RouterTools:
    """MCP tool entrypoints for router operations.

    All methods return ToolResult in MCP-compliant format.
    """

    @staticmethod
    def route_prompt(prompt: str) -> ToolResult:
        """Route user prompt to appropriate triad.

        MCP Tool: route_prompt

        Performs semantic routing on user prompt to determine which
        triad (idea-validation, design, implementation, etc.) should
        handle the request.

        Args:
            prompt: User's input prompt to route

        Returns:
            ToolResult with formatted routing decision

        Example:
            >>> result = RouterTools.route_prompt("Let's implement OAuth2")
            >>> print(result.content[0]["text"])
            Routing Decision:
              Triad: implementation
              Confidence: 88%
              Method: semantic
        """
        service = bootstrap_router_service()

        try:
            decision = service.route_prompt(prompt)
            formatted = format_routing_decision(decision)

            return ToolResult(
                success=True, content=[{"type": "text", "text": formatted}]
            )

        except Exception as e:
            return ToolResult(success=False, content=[], error=str(e))

    @staticmethod
    def get_current_triad() -> ToolResult:
        """Get currently active triad from router state.

        MCP Tool: get_current_triad

        Retrieves the current router state including active triad,
        session information, and turn count.

        Returns:
            ToolResult with formatted router state

        Example:
            >>> result = RouterTools.get_current_triad()
            >>> print(result.content[0]["text"])
            Router State:
              Current Triad: implementation
              Session ID: abc123...
              Turn Count: 5
        """
        service = bootstrap_router_service()

        try:
            state = service.get_current_triad()
            formatted = format_router_state(state)

            return ToolResult(
                success=True, content=[{"type": "text", "text": formatted}]
            )

        except Exception as e:
            return ToolResult(success=False, content=[], error=str(e))
