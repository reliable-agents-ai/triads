"""Bootstrap/factory functions for knowledge tools.

Provides factory function to create KnowledgeService with production dependencies.
"""

from pathlib import Path

from triads.tools.knowledge.repository import FileSystemGraphRepository
from triads.tools.knowledge.service import KnowledgeService


def bootstrap_knowledge_service(graphs_dir: Path | None = None) -> KnowledgeService:
    """Create KnowledgeService with production dependencies.

    Args:
        graphs_dir: Path to graphs directory (defaults to .claude/graphs)

    Returns:
        KnowledgeService instance configured for production use

    Example:
        >>> service = bootstrap_knowledge_service()
        >>> result = service.query_graph("design", "OAuth")
    """
    repo = FileSystemGraphRepository(graphs_dir)
    return KnowledgeService(repo)
