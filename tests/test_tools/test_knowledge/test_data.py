"""Sample graphs for testing knowledge tools."""

from triads.tools.knowledge.domain import Node, Edge, KnowledgeGraph


def get_sample_design_graph() -> KnowledgeGraph:
    """Create sample design graph with OAuth decision."""
    nodes = [
        Node(
            id="oauth_decision",
            label="OAuth2 Authentication Decision",
            type="decision",
            confidence=1.0,
            content="Decided to use OAuth2 for authentication",
            evidence=["Security best practices", "Industry standard"],
            metadata={"created_by": "solution-architect"}
        ),
        Node(
            id="api_design",
            label="REST API Design",
            type="concept",
            confidence=0.9,
            content="RESTful API following OpenAPI 3.0 spec",
            evidence=["OpenAPI docs"],
            metadata={"created_by": "solution-architect"}
        ),
        Node(
            id="low_confidence_finding",
            label="Unverified Security Finding",
            type="finding",
            confidence=0.6,
            content="Possible SQL injection risk - needs verification",
            evidence=[],
            metadata={"created_by": "test-engineer"}
        ),
    ]

    edges = [
        Edge(source="oauth_decision", target="api_design", relationship="implements")
    ]

    return KnowledgeGraph(triad="design", nodes=nodes, edges=edges)


def get_sample_implementation_graph() -> KnowledgeGraph:
    """Create sample implementation graph."""
    nodes = [
        Node(
            id="oauth_impl",
            label="OAuth2 Client Implementation",
            type="entity",
            confidence=1.0,
            content="Implemented OAuth2 client using requests-oauthlib",
            evidence=["src/auth/oauth.py:45"],
            metadata={"created_by": "senior-developer"}
        ),
        Node(
            id="security_test",
            label="OAuth Security Tests",
            type="entity",
            confidence=0.95,
            content="Comprehensive security test suite",
            evidence=["tests/test_oauth_security.py"],
            metadata={"created_by": "test-engineer"}
        ),
    ]

    edges = [
        Edge(source="security_test", target="oauth_impl", relationship="validates")
    ]

    return KnowledgeGraph(triad="implementation", nodes=nodes, edges=edges)


def get_invalid_graph_missing_node() -> KnowledgeGraph:
    """Create invalid graph with edge referencing non-existent node."""
    nodes = [
        Node(
            id="node1",
            label="Exists",
            type="concept",
            confidence=1.0,
        ),
    ]

    edges = [
        Edge(source="node1", target="missing_node", relationship="depends_on")
    ]

    return KnowledgeGraph(triad="invalid", nodes=nodes, edges=edges)
