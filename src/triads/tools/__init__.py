"""
MCP-compliant tool abstraction layer for Triads.

This package provides tool interfaces following the Model Context Protocol (MCP)
specification. It implements a domain-driven design with Repository, Service,
Domain, and Entrypoint layers.

Modules:
    - shared: Common utilities (ToolResult, ToolError)
    - knowledge: Knowledge graph tools (query_graph, update_graph, validate_graph)
    - integrity: Graph integrity tools (check_integrity, repair_graph)
    - router: Routing tools (route_to_triad, get_routing_status)
    - workflow: Workflow tools (get_workflow_state, update_workflow_state, validate_workflow_step)
    - generator: Triad generation tools (generate_agents, generate_bridge_context)
"""

__version__ = "0.1.0"
