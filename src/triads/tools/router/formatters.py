"""Formatters for router tool output.

Converts domain models to human-readable text formats for MCP tools.
"""

from triads.tools.router.domain import RoutingDecision, RouterState


def format_routing_decision(decision: RoutingDecision) -> str:
    """Format routing decision as human-readable text.

    Args:
        decision: RoutingDecision to format

    Returns:
        Formatted string with routing information

    Example:
        >>> decision = RoutingDecision(triad="implementation", confidence=0.92, method="semantic")
        >>> print(format_routing_decision(decision))
        Routing Decision:
          Triad: implementation
          Confidence: 92%
          Method: semantic
    """
    lines = [
        "Routing Decision:",
        f"  Triad: {decision.triad}",
        f"  Confidence: {decision.confidence:.0%}",
        f"  Method: {decision.method}"
    ]

    if decision.reasoning:
        lines.append(f"  Reasoning: {decision.reasoning}")

    return "\n".join(lines)


def format_router_state(state: RouterState) -> str:
    """Format router state as human-readable text.

    Args:
        state: RouterState to format

    Returns:
        Formatted string with state information

    Example:
        >>> state = RouterState(current_triad="design", session_id="abc123", turn_count=3)
        >>> print(format_router_state(state))
        Router State:
          Current Triad: design
          Session ID: abc123
          Turn Count: 3
    """
    lines = [
        "Router State:",
        f"  Current Triad: {state.current_triad or 'None'}",
        f"  Session ID: {state.session_id}",
        f"  Turn Count: {state.turn_count}"
    ]

    if state.conversation_start:
        lines.append(f"  Conversation Start: {state.conversation_start}")

    if state.last_activity:
        lines.append(f"  Last Activity: {state.last_activity}")

    return "\n".join(lines)
