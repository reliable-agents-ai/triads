"""Tests for triad discovery system.

Tests cover:
- Discovering triads from .claude/agents/ directory
- Parsing triad metadata (ID, path, agents)
- Caching behavior
- Error handling for missing directories
- Filtering hidden files and directories
"""

import os
import pytest
from pathlib import Path
from triads.workflow_enforcement.triad_discovery import (
    TriadDiscovery,
    TriadInfo,
    TriadDiscoveryError,
)


@pytest.fixture
def temp_agents_dir(tmp_path):
    """Create temporary .claude/agents directory for testing."""
    agents_dir = tmp_path / ".claude" / "agents"
    agents_dir.mkdir(parents=True)
    return agents_dir


@pytest.fixture
def populated_agents_dir(temp_agents_dir):
    """Create agents directory with sample triads."""
    # Create idea-validation triad
    idea_dir = temp_agents_dir / "idea-validation"
    idea_dir.mkdir()
    (idea_dir / "research-analyst.md").write_text("# Research Analyst")
    (idea_dir / "community-researcher.md").write_text("# Community Researcher")
    (idea_dir / "validation-synthesizer.md").write_text("# Validation Synthesizer")

    # Create design triad
    design_dir = temp_agents_dir / "design"
    design_dir.mkdir()
    (design_dir / "solution-architect.md").write_text("# Solution Architect")
    (design_dir / "design-bridge.md").write_text("# Design Bridge")

    # Create implementation triad
    impl_dir = temp_agents_dir / "implementation"
    impl_dir.mkdir()
    (impl_dir / "senior-developer.md").write_text("# Senior Developer")

    # Create hidden directory (should be ignored)
    hidden_dir = temp_agents_dir / ".hidden"
    hidden_dir.mkdir()
    (hidden_dir / "agent.md").write_text("# Hidden Agent")

    # Create hidden file (should be ignored)
    (idea_dir / ".hidden-agent.md").write_text("# Hidden")

    # Create non-markdown file (should be ignored)
    (idea_dir / "README.txt").write_text("README")

    return temp_agents_dir


class TestTriadInfo:
    """Test TriadInfo dataclass."""

    def test_triad_info_structure(self):
        """Test TriadInfo has expected fields."""
        info = TriadInfo(
            id="test-triad",
            path="/path/to/triad",
            agents=["agent1.md", "agent2.md"],
            agent_count=2
        )

        assert info.id == "test-triad"
        assert info.path == "/path/to/triad"
        assert info.agents == ["agent1.md", "agent2.md"]
        assert info.agent_count == 2

    def test_triad_info_agent_count_matches_list(self):
        """Test agent_count matches length of agents list."""
        info = TriadInfo(
            id="test",
            path="/path",
            agents=["a.md", "b.md", "c.md"],
            agent_count=3
        )

        assert info.agent_count == len(info.agents)


class TestTriadDiscoveryBasics:
    """Test basic discovery functionality."""

    def test_discover_triads_returns_list(self, temp_agents_dir):
        """Test discover_triads returns a list."""
        discovery = TriadDiscovery(base_path=str(temp_agents_dir))
        result = discovery.discover_triads()

        assert isinstance(result, list)

    def test_discover_triads_empty_directory(self, temp_agents_dir):
        """Test discovery with empty agents directory."""
        discovery = TriadDiscovery(base_path=str(temp_agents_dir))
        triads = discovery.discover_triads()

        assert triads == []

    def test_discover_triads_with_triads(self, populated_agents_dir):
        """Test discovery finds all triads."""
        discovery = TriadDiscovery(base_path=str(populated_agents_dir))
        triads = discovery.discover_triads()

        # Should find 3 visible triads (not .hidden)
        assert len(triads) == 3

        triad_ids = [t.id for t in triads]
        assert "idea-validation" in triad_ids
        assert "design" in triad_ids
        assert "implementation" in triad_ids
        assert ".hidden" not in triad_ids

    def test_missing_agents_directory_returns_empty(self, tmp_path):
        """Test graceful handling of missing directory."""
        non_existent = tmp_path / "does-not-exist"
        discovery = TriadDiscovery(base_path=str(non_existent))

        # Should not raise, should return empty list
        triads = discovery.discover_triads()
        assert triads == []


class TestTriadMetadata:
    """Test triad metadata extraction."""

    def test_agents_sorted_alphabetically(self, populated_agents_dir):
        """Test agent files are sorted alphabetically."""
        discovery = TriadDiscovery(base_path=str(populated_agents_dir))
        triads = discovery.discover_triads()

        idea_triad = next(t for t in triads if t.id == "idea-validation")

        # Should be sorted
        assert idea_triad.agents == [
            "community-researcher.md",
            "research-analyst.md",
            "validation-synthesizer.md"
        ]

    def test_ignores_hidden_files(self, populated_agents_dir):
        """Test hidden files are ignored."""
        discovery = TriadDiscovery(base_path=str(populated_agents_dir))
        triads = discovery.discover_triads()

        idea_triad = next(t for t in triads if t.id == "idea-validation")

        # Should not include .hidden-agent.md
        assert ".hidden-agent.md" not in idea_triad.agents

    def test_ignores_hidden_directories(self, populated_agents_dir):
        """Test hidden directories are ignored."""
        discovery = TriadDiscovery(base_path=str(populated_agents_dir))
        triads = discovery.discover_triads()

        triad_ids = [t.id for t in triads]
        assert ".hidden" not in triad_ids

    def test_only_markdown_files(self, populated_agents_dir):
        """Test only .md files are included as agents."""
        discovery = TriadDiscovery(base_path=str(populated_agents_dir))
        triads = discovery.discover_triads()

        idea_triad = next(t for t in triads if t.id == "idea-validation")

        # Should not include README.txt
        assert "README.txt" not in idea_triad.agents

        # All agents should end with .md
        for agent in idea_triad.agents:
            assert agent.endswith(".md")

    def test_triad_path_correct(self, populated_agents_dir):
        """Test triad path is set correctly."""
        discovery = TriadDiscovery(base_path=str(populated_agents_dir))
        triads = discovery.discover_triads()

        idea_triad = next(t for t in triads if t.id == "idea-validation")

        expected_path = os.path.join(str(populated_agents_dir), "idea-validation")
        assert idea_triad.path == expected_path

    def test_agent_count_correct(self, populated_agents_dir):
        """Test agent_count matches actual agent count."""
        discovery = TriadDiscovery(base_path=str(populated_agents_dir))
        triads = discovery.discover_triads()

        idea_triad = next(t for t in triads if t.id == "idea-validation")
        design_triad = next(t for t in triads if t.id == "design")
        impl_triad = next(t for t in triads if t.id == "implementation")

        assert idea_triad.agent_count == 3
        assert design_triad.agent_count == 2
        assert impl_triad.agent_count == 1

    def test_multiple_agents_per_triad(self, populated_agents_dir):
        """Test triads with multiple agents."""
        discovery = TriadDiscovery(base_path=str(populated_agents_dir))
        triads = discovery.discover_triads()

        idea_triad = next(t for t in triads if t.id == "idea-validation")

        assert len(idea_triad.agents) == 3
        assert idea_triad.agent_count == 3

    def test_no_agents_in_triad(self, temp_agents_dir):
        """Test triad with no agent files."""
        empty_triad = temp_agents_dir / "empty-triad"
        empty_triad.mkdir()

        discovery = TriadDiscovery(base_path=str(temp_agents_dir))
        triads = discovery.discover_triads()

        empty = next(t for t in triads if t.id == "empty-triad")
        assert empty.agent_count == 0
        assert empty.agents == []


class TestCaching:
    """Test caching behavior."""

    def test_cache_works(self, populated_agents_dir):
        """Test results are cached."""
        discovery = TriadDiscovery(base_path=str(populated_agents_dir))

        # First call
        triads1 = discovery.discover_triads()

        # Second call (should use cache)
        triads2 = discovery.discover_triads()

        # Should return same instance
        assert triads1 is triads2

    def test_force_refresh_clears_cache(self, populated_agents_dir):
        """Test force_refresh clears cache."""
        discovery = TriadDiscovery(base_path=str(populated_agents_dir))

        # First call
        triads1 = discovery.discover_triads()

        # Add new triad
        new_triad = populated_agents_dir / "new-triad"
        new_triad.mkdir()
        (new_triad / "agent.md").write_text("# Agent")

        # Without refresh, should not see new triad
        triads2 = discovery.discover_triads(force_refresh=False)
        assert len(triads2) == 3

        # With refresh, should see new triad
        triads3 = discovery.discover_triads(force_refresh=True)
        assert len(triads3) == 4


class TestQueryInterface:
    """Test query methods."""

    def test_get_triad_by_id(self, populated_agents_dir):
        """Test getting specific triad by ID."""
        discovery = TriadDiscovery(base_path=str(populated_agents_dir))

        triad = discovery.get_triad("idea-validation")

        assert triad is not None
        assert triad.id == "idea-validation"
        assert triad.agent_count == 3

    def test_get_triad_not_found(self, populated_agents_dir):
        """Test getting non-existent triad returns None."""
        discovery = TriadDiscovery(base_path=str(populated_agents_dir))

        triad = discovery.get_triad("does-not-exist")

        assert triad is None

    def test_triad_exists(self, populated_agents_dir):
        """Test checking if triad exists."""
        discovery = TriadDiscovery(base_path=str(populated_agents_dir))

        assert discovery.triad_exists("idea-validation") is True
        assert discovery.triad_exists("design") is True
        assert discovery.triad_exists("does-not-exist") is False

    def test_get_triad_uses_cache(self, populated_agents_dir):
        """Test get_triad uses cached results."""
        discovery = TriadDiscovery(base_path=str(populated_agents_dir))

        # Prime cache
        discovery.discover_triads()

        # Delete a triad directory
        import shutil
        shutil.rmtree(populated_agents_dir / "design")

        # get_triad should still find it (using cache)
        triad = discovery.get_triad("design")
        assert triad is not None


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_default_base_path(self):
        """Test default base_path is .claude/agents."""
        discovery = TriadDiscovery()

        assert discovery.base_path == ".claude/agents"

    def test_symlinks_handled(self, temp_agents_dir):
        """Test symbolic links are handled correctly."""
        # Create real triad
        real_triad = temp_agents_dir / "real-triad"
        real_triad.mkdir()
        (real_triad / "agent.md").write_text("# Agent")

        # Create symlink to triad (if supported)
        try:
            symlink = temp_agents_dir / "symlink-triad"
            symlink.symlink_to(real_triad)
        except (OSError, NotImplementedError):
            pytest.skip("Symlinks not supported on this platform")

        discovery = TriadDiscovery(base_path=str(temp_agents_dir))
        triads = discovery.discover_triads()

        # Should discover both (symlink is treated as directory)
        triad_ids = [t.id for t in triads]
        assert "real-triad" in triad_ids
        assert "symlink-triad" in triad_ids

    def test_permission_denied_handled(self, temp_agents_dir, monkeypatch):
        """Test permission errors are handled gracefully."""
        # This is difficult to test portably, so we'll mock os.scandir
        def mock_scandir(path):
            raise PermissionError("Permission denied")

        monkeypatch.setattr(os, "scandir", mock_scandir)

        discovery = TriadDiscovery(base_path=str(temp_agents_dir))

        # Should raise TriadDiscoveryError with clear message
        with pytest.raises(TriadDiscoveryError, match="Failed to scan directory"):
            discovery.discover_triads()

    def test_triad_id_from_directory_name(self, temp_agents_dir):
        """Test triad ID is exactly the directory name."""
        triad_dir = temp_agents_dir / "my-custom-triad-123"
        triad_dir.mkdir()
        (triad_dir / "agent.md").write_text("# Agent")

        discovery = TriadDiscovery(base_path=str(temp_agents_dir))
        triads = discovery.discover_triads()

        assert triads[0].id == "my-custom-triad-123"
