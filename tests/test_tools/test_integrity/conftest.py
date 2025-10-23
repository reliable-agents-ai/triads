"""
Fixtures for integrity tools tests.
"""

import pytest


@pytest.fixture
def tmp_graphs_dir(tmp_path):
    """
    Create temporary graphs directory for testing.

    Returns:
        Path to temporary directory
    """
    graphs_dir = tmp_path / "graphs"
    graphs_dir.mkdir()
    return graphs_dir
