"""Fixtures for knowledge tools tests."""

import pytest

from triads.tools.knowledge.domain import KnowledgeGraph
from triads.tools.knowledge.repository import InMemoryGraphRepository
from tests.test_tools.test_knowledge.test_data import (
    get_sample_design_graph,
    get_sample_implementation_graph,
)


@pytest.fixture
def seeded_repo() -> InMemoryGraphRepository:
    """Create in-memory repository seeded with sample graphs."""
    graphs = {
        "design": get_sample_design_graph(),
        "implementation": get_sample_implementation_graph(),
    }
    return InMemoryGraphRepository(graphs)


@pytest.fixture
def empty_repo() -> InMemoryGraphRepository:
    """Create empty in-memory repository."""
    return InMemoryGraphRepository()
