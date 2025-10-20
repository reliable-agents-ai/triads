"""Unit tests for upgrade orchestrator.

Tests cover:
- Agent scanning and version detection
- Backup creation
- Diff generation
- Content validation
- Atomic upgrade application
- Security (path traversal protection)
"""

import tempfile
from pathlib import Path
from textwrap import dedent

import pytest

from triads.upgrade import UpgradeCandidate, UpgradeOrchestrator, UpgradeSecurityError


@pytest.fixture
def temp_agents_dir(tmp_path):
    """Create temporary agents directory structure."""
    agents_dir = tmp_path / ".claude" / "agents"
    agents_dir.mkdir(parents=True)

    # Create triad directories
    (agents_dir / "implementation").mkdir()
    (agents_dir / "design").mkdir()
    (agents_dir / "deployment").mkdir()

    return agents_dir


@pytest.fixture
def sample_agent_content():
    """Sample agent content with version 0.7.0."""
    return dedent("""\
        ---
        name: senior-developer
        triad: implementation
        role: implementer
        template_version: 0.7.0
        description: Implement features following design specifications
        ---
        # Senior Developer

        ## Role

        Build high-quality code following architectural decisions.

        ## Responsibilities

        1. Implement features per design specs
        2. Write tests
        3. Follow ADRs
    """)


@pytest.fixture
def upgraded_agent_content():
    """Sample upgraded agent content with version 0.8.0."""
    return dedent("""\
        ---
        name: senior-developer
        triad: implementation
        role: implementer
        template_version: 0.8.0
        description: Implement features following design specifications
        ---
        # Senior Developer

        ## Role

        Build high-quality code following architectural decisions.

        ## Responsibilities

        1. Implement features per design specs
        2. Write tests
        3. Follow ADRs
    """)


@pytest.fixture
def orchestrator_with_agents(temp_agents_dir, sample_agent_content):
    """Create orchestrator with test agents."""
    # Create some test agents
    agents = {
        "implementation/senior-developer.md": sample_agent_content,
        "implementation/test-engineer.md": sample_agent_content.replace(
            "senior-developer", "test-engineer"
        ).replace("implementer", "tester"),
        "design/solution-architect.md": sample_agent_content.replace(
            "senior-developer", "solution-architect"
        ).replace("implementation", "design").replace("implementer", "analyzer"),
    }

    for path, content in agents.items():
        agent_path = temp_agents_dir / path
        agent_path.write_text(content)

    # Create orchestrator pointing to temp directory
    orchestrator = UpgradeOrchestrator(dry_run=False)
    orchestrator.agents_dir = temp_agents_dir

    return orchestrator


class TestUpgradeCandidate:
    """Test UpgradeCandidate dataclass."""

    def test_needs_upgrade_when_versions_differ(self):
        """Test needs_upgrade returns True when versions differ."""
        candidate = UpgradeCandidate(
            agent_path=Path("test.md"),
            current_version="0.7.0",
            latest_version="0.8.0",
            triad_name="implementation",
            agent_name="senior-developer"
        )

        assert candidate.needs_upgrade is True

    def test_no_upgrade_when_versions_match(self):
        """Test needs_upgrade returns False when versions match."""
        candidate = UpgradeCandidate(
            agent_path=Path("test.md"),
            current_version="0.8.0",
            latest_version="0.8.0",
            triad_name="implementation",
            agent_name="senior-developer"
        )

        assert candidate.needs_upgrade is False

    def test_str_representation(self):
        """Test human-readable string representation."""
        candidate = UpgradeCandidate(
            agent_path=Path("test.md"),
            current_version="0.7.0",
            latest_version="0.8.0",
            triad_name="implementation",
            agent_name="senior-developer"
        )

        result = str(candidate)
        assert "implementation/senior-developer" in result
        assert "0.7.0" in result
        assert "0.8.0" in result
        assert "NEEDS UPGRADE" in result


class TestOrchestratorInit:
    """Test orchestrator initialization."""

    def test_init_with_valid_agents_dir(self, temp_agents_dir):
        """Test initialization with valid agents directory."""
        orchestrator = UpgradeOrchestrator()
        orchestrator.agents_dir = temp_agents_dir

        assert orchestrator.dry_run is False
        assert orchestrator.force is False
        assert orchestrator.agents_dir == temp_agents_dir
        assert orchestrator.latest_version == "0.8.0"

    def test_init_dry_run_mode(self):
        """Test initialization in dry-run mode."""
        orchestrator = UpgradeOrchestrator(dry_run=True)
        assert orchestrator.dry_run is True

    def test_init_force_mode(self):
        """Test initialization with force flag."""
        orchestrator = UpgradeOrchestrator(force=True)
        assert orchestrator.force is True


class TestScanAgents:
    """Test agent scanning functionality."""

    def test_scan_all_agents(self, orchestrator_with_agents):
        """Test scanning all agents."""
        candidates = orchestrator_with_agents.scan_agents()

        # Should find 3 agents
        assert len(candidates) == 3

        # All should need upgrade (test data has 0.7.0)
        assert all(c.needs_upgrade for c in candidates)

        # Check agent names
        agent_names = {c.agent_name for c in candidates}
        expected = {"senior-developer", "test-engineer", "solution-architect"}
        assert agent_names == expected

    def test_scan_specific_triad(self, orchestrator_with_agents):
        """Test scanning agents in specific triad."""
        candidates = orchestrator_with_agents.scan_agents(triad_name="implementation")

        # Should find 2 agents in implementation
        assert len(candidates) == 2

        # All should be in implementation triad
        assert all(c.triad_name == "implementation" for c in candidates)

    def test_scan_specific_agents(self, orchestrator_with_agents):
        """Test scanning specific agent names."""
        candidates = orchestrator_with_agents.scan_agents(
            agent_names=["senior-developer", "solution-architect"]
        )

        # Should find 2 specific agents
        assert len(candidates) == 2

        agent_names = {c.agent_name for c in candidates}
        expected = {"senior-developer", "solution-architect"}
        assert agent_names == expected

    def test_scan_with_triad_and_agent_filters(self, orchestrator_with_agents):
        """Test scanning with both triad and agent filters."""
        candidates = orchestrator_with_agents.scan_agents(
            triad_name="implementation",
            agent_names=["senior-developer"]
        )

        # Should find 1 agent matching both filters
        assert len(candidates) == 1
        assert candidates[0].agent_name == "senior-developer"
        assert candidates[0].triad_name == "implementation"

    def test_scan_invalid_triad_raises_error(self, orchestrator_with_agents):
        """Test scanning with path traversal attempt raises security error."""
        with pytest.raises(UpgradeSecurityError, match="Security violation"):
            orchestrator_with_agents.scan_agents(triad_name="../../../etc")


class TestParseTemplateVersion:
    """Test template version parsing."""

    def test_parse_valid_version(self, temp_agents_dir, sample_agent_content):
        """Test parsing valid template version."""
        agent_path = temp_agents_dir / "test.md"
        agent_path.write_text(sample_agent_content)

        orchestrator = UpgradeOrchestrator()
        orchestrator.agents_dir = temp_agents_dir

        version = orchestrator._parse_template_version(agent_path)
        assert version == "0.7.0"

    def test_parse_missing_version_returns_unknown(self, temp_agents_dir):
        """Test parsing agent without template_version returns 'unknown'."""
        content = dedent("""\
            ---
            name: old-agent
            triad: test
            role: analyzer
            ---
            # Old Agent

            This agent has no template_version field.
        """)

        agent_path = temp_agents_dir / "test.md"
        agent_path.write_text(content)

        orchestrator = UpgradeOrchestrator()
        orchestrator.agents_dir = temp_agents_dir

        version = orchestrator._parse_template_version(agent_path)
        assert version == "unknown"

    def test_parse_no_frontmatter_returns_unknown(self, temp_agents_dir):
        """Test parsing agent without frontmatter returns 'unknown'."""
        content = "# Agent without frontmatter\n\nJust body content."

        agent_path = temp_agents_dir / "test.md"
        agent_path.write_text(content)

        orchestrator = UpgradeOrchestrator()
        orchestrator.agents_dir = temp_agents_dir

        version = orchestrator._parse_template_version(agent_path)
        assert version == "unknown"

    def test_parse_nonexistent_file_returns_unknown(self, temp_agents_dir):
        """Test parsing nonexistent file returns 'unknown'."""
        agent_path = temp_agents_dir / "nonexistent.md"

        orchestrator = UpgradeOrchestrator()
        orchestrator.agents_dir = temp_agents_dir

        version = orchestrator._parse_template_version(agent_path)
        assert version == "unknown"


class TestBackupAgent:
    """Test backup creation."""

    def test_backup_creates_file(self, orchestrator_with_agents, temp_agents_dir):
        """Test backup creates timestamped file."""
        agent_path = temp_agents_dir / "implementation" / "senior-developer.md"

        backup_path = orchestrator_with_agents.backup_agent(agent_path)

        # Check backup exists
        assert backup_path.exists()

        # Check in backups directory
        assert backup_path.parent.name == "backups"

        # Check filename format
        assert backup_path.stem.startswith("senior-developer_")
        assert backup_path.suffix == ".backup"

    def test_backup_preserves_content(self, orchestrator_with_agents, temp_agents_dir, sample_agent_content):
        """Test backup preserves original content."""
        agent_path = temp_agents_dir / "implementation" / "senior-developer.md"

        backup_path = orchestrator_with_agents.backup_agent(agent_path)

        # Content should match original
        backup_content = backup_path.read_text()
        original_content = agent_path.read_text()
        assert backup_content == original_content

    def test_backup_creates_directory_if_missing(self, temp_agents_dir, sample_agent_content):
        """Test backup creates backups directory if it doesn't exist."""
        agent_path = temp_agents_dir / "implementation" / "senior-developer.md"
        agent_path.write_text(sample_agent_content)

        # Ensure backups dir doesn't exist
        backup_dir = temp_agents_dir / "backups"
        assert not backup_dir.exists()

        orchestrator = UpgradeOrchestrator()
        orchestrator.agents_dir = temp_agents_dir

        backup_path = orchestrator.backup_agent(agent_path)

        # Backup directory should now exist
        assert backup_dir.exists()
        assert backup_path.exists()


class TestShowDiff:
    """Test diff generation."""

    def test_show_diff_basic(self, orchestrator_with_agents, sample_agent_content, upgraded_agent_content):
        """Test basic diff generation."""
        diff = orchestrator_with_agents.show_diff(
            current_content=sample_agent_content,
            proposed_content=upgraded_agent_content,
            agent_name="senior-developer"
        )

        # Check diff format
        assert "--- current/senior-developer" in diff
        assert "+++ proposed/senior-developer" in diff

        # Check version change
        assert "-template_version: 0.7.0" in diff
        assert "+template_version: 0.8.0" in diff

    def test_show_diff_identical_content(self, orchestrator_with_agents, sample_agent_content):
        """Test diff with identical content."""
        diff = orchestrator_with_agents.show_diff(
            current_content=sample_agent_content,
            proposed_content=sample_agent_content
        )

        # Identical content should produce empty diff
        assert diff == ""

    def test_show_diff_without_agent_name(self, orchestrator_with_agents, sample_agent_content, upgraded_agent_content):
        """Test diff without agent name specified."""
        diff = orchestrator_with_agents.show_diff(
            current_content=sample_agent_content,
            proposed_content=upgraded_agent_content
        )

        # Should use generic names
        assert "--- current" in diff
        assert "+++ proposed" in diff


class TestValidateAgentContent:
    """Test content validation."""

    def test_validate_valid_content(self, orchestrator_with_agents, sample_agent_content):
        """Test validation passes for valid content."""
        is_valid = orchestrator_with_agents._validate_agent_content(sample_agent_content)
        assert is_valid is True

    def test_validate_missing_frontmatter(self, orchestrator_with_agents):
        """Test validation fails without frontmatter."""
        content = "# Agent\n\nNo frontmatter here."
        is_valid = orchestrator_with_agents._validate_agent_content(content)
        assert is_valid is False

    def test_validate_missing_required_field(self, orchestrator_with_agents):
        """Test validation fails with missing required field."""
        content = dedent("""\
            ---
            name: test-agent
            triad: test
            # Missing role and template_version
            ---
            # Body
        """)
        is_valid = orchestrator_with_agents._validate_agent_content(content)
        assert is_valid is False

    def test_validate_unclosed_frontmatter(self, orchestrator_with_agents):
        """Test validation fails with unclosed frontmatter."""
        content = dedent("""\
            ---
            name: test-agent
            triad: test
            role: analyzer
            template_version: 0.8.0
            # Missing closing ---
            # Body
        """)
        is_valid = orchestrator_with_agents._validate_agent_content(content)
        assert is_valid is False


class TestApplyUpgrade:
    """Test upgrade application."""

    def test_apply_upgrade_success(self, orchestrator_with_agents, upgraded_agent_content, temp_agents_dir):
        """Test successful upgrade application."""
        candidates = orchestrator_with_agents.scan_agents(agent_names=["senior-developer"])
        candidate = candidates[0]

        success = orchestrator_with_agents.apply_upgrade(candidate, upgraded_agent_content)

        assert success is True

        # Check file was updated
        new_content = candidate.agent_path.read_text()
        assert "template_version: 0.8.0" in new_content

        # Check backup was created
        backup_dir = temp_agents_dir / "backups"
        backups = list(backup_dir.glob("senior-developer_*.md.backup"))
        assert len(backups) == 1

    def test_apply_upgrade_dry_run(self, orchestrator_with_agents, upgraded_agent_content):
        """Test dry-run mode doesn't modify files."""
        orchestrator_with_agents.dry_run = True

        candidates = orchestrator_with_agents.scan_agents(agent_names=["senior-developer"])
        candidate = candidates[0]

        original_content = candidate.agent_path.read_text()

        success = orchestrator_with_agents.apply_upgrade(candidate, upgraded_agent_content)

        assert success is True

        # File should be unchanged
        current_content = candidate.agent_path.read_text()
        assert current_content == original_content

    def test_apply_upgrade_invalid_content_fails(self, orchestrator_with_agents):
        """Test upgrade fails with invalid content."""
        candidates = orchestrator_with_agents.scan_agents(agent_names=["senior-developer"])
        candidate = candidates[0]

        invalid_content = "# Not valid agent content"

        success = orchestrator_with_agents.apply_upgrade(candidate, invalid_content)

        assert success is False

        # Original file should be unchanged
        current_content = candidate.agent_path.read_text()
        assert "template_version: 0.7.0" in current_content


class TestSecurityFeatures:
    """Test security features."""

    def test_safe_path_component_rejects_traversal(self, orchestrator_with_agents):
        """Test path component validation rejects traversal attempts."""
        dangerous_components = [
            "../../../etc",
            "../../passwords",
            "test/../../../root",
            "test/../../etc",
            "\\..\\..\\windows",
        ]

        for component in dangerous_components:
            is_safe = orchestrator_with_agents._is_safe_path_component(component)
            assert is_safe is False, f"Should reject: {component}"

    def test_safe_path_component_accepts_valid(self, orchestrator_with_agents):
        """Test path component validation accepts valid names."""
        valid_components = [
            "implementation",
            "design",
            "my-triad",
            "test_triad",
        ]

        for component in valid_components:
            is_safe = orchestrator_with_agents._is_safe_path_component(component)
            assert is_safe is True, f"Should accept: {component}"

    def test_safe_agent_path_rejects_outside_agents_dir(self, temp_agents_dir):
        """Test agent path validation rejects paths outside agents directory."""
        orchestrator = UpgradeOrchestrator()
        orchestrator.agents_dir = temp_agents_dir

        # Path outside agents directory
        outside_path = temp_agents_dir.parent / "etc" / "passwd"

        is_safe = orchestrator._is_safe_agent_path(outside_path)
        assert is_safe is False

    def test_safe_agent_path_accepts_inside_agents_dir(self, temp_agents_dir):
        """Test agent path validation accepts paths inside agents directory."""
        orchestrator = UpgradeOrchestrator()
        orchestrator.agents_dir = temp_agents_dir

        # Path inside agents directory
        inside_path = temp_agents_dir / "implementation" / "senior-developer.md"

        is_safe = orchestrator._is_safe_agent_path(inside_path)
        assert is_safe is True


class TestAtomicWrites:
    """Test atomic write behavior."""

    def test_atomic_write_leaves_no_temp_files(self, orchestrator_with_agents, upgraded_agent_content):
        """Test atomic write cleans up temp files on success."""
        candidates = orchestrator_with_agents.scan_agents(agent_names=["senior-developer"])
        candidate = candidates[0]

        orchestrator_with_agents.apply_upgrade(candidate, upgraded_agent_content)

        # Should not leave .tmp files
        temp_files = list(candidate.agent_path.parent.glob("*.tmp"))
        assert len(temp_files) == 0

    def test_atomic_write_cleans_temp_on_failure(self, orchestrator_with_agents, temp_agents_dir):
        """Test atomic write cleans up temp files on failure."""
        candidates = orchestrator_with_agents.scan_agents(agent_names=["senior-developer"])
        candidate = candidates[0]

        # Make write fail by removing parent directory permissions
        # (This test may not work on all systems due to permission handling)
        # Instead, we'll test with invalid content that fails validation

        invalid_content = "# Invalid content"

        orchestrator_with_agents.apply_upgrade(candidate, invalid_content)

        # Should not leave .tmp files
        temp_files = list(candidate.agent_path.parent.glob("*.tmp"))
        assert len(temp_files) == 0


class TestTemplateMerge:
    """Test Phase 3 template merge functionality."""

    def test_parse_agent_file(self, orchestrator_with_agents, sample_agent_content):
        """Test parsing agent into frontmatter and body."""
        frontmatter, body = orchestrator_with_agents._parse_agent_file(sample_agent_content)

        # Check frontmatter parsed correctly
        assert frontmatter['name'] == 'senior-developer'
        assert frontmatter['triad'] == 'implementation'
        assert frontmatter['role'] == 'implementer'
        assert frontmatter['template_version'] == '0.7.0'

        # Check body starts correctly
        assert body.strip().startswith('# Senior Developer')

    def test_identify_new_sections_v080(self, orchestrator_with_agents):
        """Test identifying new sections for v0.8.0."""
        new_sections = orchestrator_with_agents._identify_new_sections("0.8.0")
        assert "🧠 Knowledge Graph Protocol" in new_sections

    def test_identify_new_sections_unknown_version(self, orchestrator_with_agents):
        """Test no new sections for unknown version."""
        new_sections = orchestrator_with_agents._identify_new_sections("0.9.0")
        assert len(new_sections) == 0

    def test_get_kg_protocol_section(self, orchestrator_with_agents):
        """Test extracting Knowledge Graph Protocol section from template."""
        kg_protocol = orchestrator_with_agents._get_kg_protocol_section()

        # Should contain key elements
        assert "## 🧠 Knowledge Graph Protocol" in kg_protocol
        assert "Knowledge Graph Location" in kg_protocol
        assert "{triad_name}" in kg_protocol  # Template variable preserved

    def test_merge_sections_adds_kg_protocol(self, orchestrator_with_agents):
        """Test merging adds Knowledge Graph Protocol section."""
        # Agent without KG Protocol
        current_body = dedent("""\
            # Senior Developer

            ## Role

            Implement features.

            ## Constitutional Principles

            Always verify code.

            ## Workflow

            1. Read requirements
            2. Write code
            3. Test thoroughly
        """)

        new_sections = ["🧠 Knowledge Graph Protocol"]
        merged = orchestrator_with_agents._merge_sections(current_body, new_sections, True)

        # Should contain KG Protocol section
        assert "🧠 Knowledge Graph Protocol" in merged

        # Should preserve existing content
        assert "## Role" in merged
        assert "## Constitutional Principles" in merged
        assert "## Workflow" in merged

        # KG Protocol should be inserted after Constitutional Principles
        const_idx = merged.index("## Constitutional Principles")
        kg_idx = merged.index("🧠 Knowledge Graph Protocol")
        assert kg_idx > const_idx

    def test_merge_sections_skips_if_already_present(self, orchestrator_with_agents):
        """Test merge skips section if already present."""
        current_body = dedent("""\
            # Agent

            ## 🧠 Knowledge Graph Protocol

            Already here!

            ## Other Section

            Content.
        """)

        new_sections = ["🧠 Knowledge Graph Protocol"]
        merged = orchestrator_with_agents._merge_sections(current_body, new_sections, True)

        # Should be unchanged
        assert merged == current_body

    def test_format_agent_file(self, orchestrator_with_agents):
        """Test reconstructing agent file from frontmatter and body."""
        frontmatter = {
            'name': 'test-agent',
            'triad': 'test-triad',
            'role': 'tester',
            'template_version': '0.8.0'
        }
        body = "\n# Test Agent\n\nContent here.\n"

        formatted = orchestrator_with_agents._format_agent_file(frontmatter, body)

        # Should have proper structure
        assert formatted.startswith('---\n')
        assert 'name: test-agent' in formatted
        assert 'triad: test-triad' in formatted
        assert 'role: tester' in formatted
        assert 'template_version: 0.8.0' in formatted
        assert '---\n\n# Test Agent' in formatted

    def test_generate_upgraded_content_updates_version(self, orchestrator_with_agents):
        """Test generate_upgraded_content updates template version."""
        candidates = orchestrator_with_agents.scan_agents(agent_names=["senior-developer"])
        candidate = candidates[0]

        upgraded = orchestrator_with_agents.generate_upgraded_content(candidate)

        # Should update version
        assert "template_version: 0.8.0" in upgraded
        assert "template_version: 0.7.0" not in upgraded

    def test_generate_upgraded_content_adds_kg_protocol(self, orchestrator_with_agents):
        """Test generate_upgraded_content adds Knowledge Graph Protocol."""
        candidates = orchestrator_with_agents.scan_agents(agent_names=["senior-developer"])
        candidate = candidates[0]

        upgraded = orchestrator_with_agents.generate_upgraded_content(candidate)

        # Should add KG Protocol section
        assert "🧠 Knowledge Graph Protocol" in upgraded

    def test_generate_upgraded_content_preserves_existing(self, orchestrator_with_agents):
        """Test generate_upgraded_content preserves existing content."""
        candidates = orchestrator_with_agents.scan_agents(agent_names=["senior-developer"])
        candidate = candidates[0]

        original_content = candidate.agent_path.read_text()
        upgraded = orchestrator_with_agents.generate_upgraded_content(candidate)

        # Should preserve agent name
        assert "name: senior-developer" in upgraded

        # Should preserve role
        assert "Build high-quality code" in upgraded


class TestUpgradeWorkflow:
    """Test complete upgrade workflow (Phase 3 integration)."""

    def test_upgrade_agent_interactive_workflow(self, orchestrator_with_agents, monkeypatch):
        """Test upgrade_agent with user confirmation."""
        # Mock user input: 'y' to confirm
        monkeypatch.setattr('builtins.input', lambda _: 'y')

        candidates = orchestrator_with_agents.scan_agents(agent_names=["senior-developer"])
        candidate = candidates[0]

        success = orchestrator_with_agents.upgrade_agent(candidate)

        assert success is True

        # Verify upgrade applied
        new_content = candidate.agent_path.read_text()
        assert "template_version: 0.8.0" in new_content
        assert "🧠 Knowledge Graph Protocol" in new_content

    def test_upgrade_agent_user_cancels(self, orchestrator_with_agents, monkeypatch):
        """Test upgrade_agent when user cancels."""
        # Mock user input: 'n' to cancel
        monkeypatch.setattr('builtins.input', lambda _: 'n')

        candidates = orchestrator_with_agents.scan_agents(agent_names=["senior-developer"])
        candidate = candidates[0]

        success = orchestrator_with_agents.upgrade_agent(candidate)

        assert success is False

        # Verify no upgrade applied
        content = candidate.agent_path.read_text()
        assert "template_version: 0.7.0" in content

    def test_upgrade_agent_with_force_flag(self, orchestrator_with_agents):
        """Test upgrade_agent with force flag (no confirmation)."""
        orchestrator_with_agents.force = True

        candidates = orchestrator_with_agents.scan_agents(agent_names=["senior-developer"])
        candidate = candidates[0]

        success = orchestrator_with_agents.upgrade_agent(candidate, require_confirmation=False)

        assert success is True

        # Verify upgrade applied
        new_content = candidate.agent_path.read_text()
        assert "template_version: 0.8.0" in new_content

    def test_upgrade_all_workflow(self, orchestrator_with_agents, monkeypatch):
        """Test upgrade_all with multiple agents."""
        # Mock user input: always confirm
        monkeypatch.setattr('builtins.input', lambda _: 'y')

        stats = orchestrator_with_agents.upgrade_all()

        # Should have upgraded 3 agents (senior-developer, test-engineer, solution-architect)
        assert stats['total'] == 3
        assert stats['upgraded'] == 3
        assert stats['failed'] == 0

    def test_upgrade_all_no_agents_need_upgrade(self, orchestrator_with_agents):
        """Test upgrade_all when all agents already up to date."""
        # First upgrade all
        orchestrator_with_agents.force = True
        orchestrator_with_agents.upgrade_all()

        # Now try again - should find nothing to upgrade
        stats = orchestrator_with_agents.upgrade_all()

        assert stats['total'] == 0
        assert stats['upgraded'] == 0

    def test_upgrade_all_with_triad_filter(self, orchestrator_with_agents, monkeypatch):
        """Test upgrade_all with triad filter."""
        monkeypatch.setattr('builtins.input', lambda _: 'y')

        stats = orchestrator_with_agents.upgrade_all(triad_name="implementation")

        # Should only upgrade agents in implementation triad
        assert stats['total'] == 2
