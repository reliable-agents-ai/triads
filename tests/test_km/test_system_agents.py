"""Tests for KM system agents."""

from pathlib import Path


def test_system_agents_directory_exists():
    """System agents directory should exist."""
    from triads.km.system_agents import SYSTEM_AGENTS_DIR

    assert SYSTEM_AGENTS_DIR.exists()
    assert SYSTEM_AGENTS_DIR.is_dir()


def test_get_system_agent_research():
    """Should find research-agent file."""
    from triads.km.system_agents import get_system_agent

    agent_path = get_system_agent("research-agent")

    assert agent_path is not None
    assert agent_path.exists()
    assert agent_path.name == "research-agent.md"


def test_get_system_agent_verification():
    """Should find verification-agent file."""
    from triads.km.system_agents import get_system_agent

    agent_path = get_system_agent("verification-agent")

    assert agent_path is not None
    assert agent_path.exists()
    assert agent_path.name == "verification-agent.md"


def test_get_system_agent_not_found():
    """Should return None for non-existent agent."""
    from triads.km.system_agents import get_system_agent

    agent_path = get_system_agent("nonexistent-agent")

    assert agent_path is None


def test_list_system_agents():
    """Should list all available system agents."""
    from triads.km.system_agents import list_system_agents

    agents = list_system_agents()

    assert len(agents) >= 2
    assert "research-agent" in agents
    assert "verification-agent" in agents


def test_validate_agent_file_research():
    """Research agent should have valid structure."""
    from triads.km.system_agents import get_system_agent, validate_agent_file

    agent_path = get_system_agent("research-agent")
    assert agent_path is not None

    is_valid, errors = validate_agent_file(agent_path)

    assert is_valid
    assert len(errors) == 0


def test_validate_agent_file_verification():
    """Verification agent should have valid structure."""
    from triads.km.system_agents import get_system_agent, validate_agent_file

    agent_path = get_system_agent("verification-agent")
    assert agent_path is not None

    is_valid, errors = validate_agent_file(agent_path)

    assert is_valid
    assert len(errors) == 0


def test_validate_agent_file_has_frontmatter():
    """Agent files must have YAML frontmatter."""
    # Create temporary invalid agent file
    import tempfile

    from triads.km.system_agents import validate_agent_file

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("# Agent without frontmatter\n\nContent here.")
        temp_path = Path(f.name)

    try:
        is_valid, errors = validate_agent_file(temp_path)

        assert not is_valid
        assert any("frontmatter" in err.lower() for err in errors)
    finally:
        temp_path.unlink()


def test_validate_agent_file_has_required_fields():
    """Agent frontmatter must have required fields."""
    import tempfile

    from triads.km.system_agents import validate_agent_file

    # Missing 'role' field
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("---\nname: test\n---\n\n# Agent")
        temp_path = Path(f.name)

    try:
        is_valid, errors = validate_agent_file(temp_path)

        assert not is_valid
        assert any("role" in err.lower() for err in errors)
    finally:
        temp_path.unlink()


def test_parse_agent_frontmatter():
    """Should parse agent frontmatter correctly."""
    from triads.km.system_agents import get_system_agent, parse_agent_frontmatter

    agent_path = get_system_agent("research-agent")
    assert agent_path is not None

    frontmatter = parse_agent_frontmatter(agent_path)

    assert frontmatter is not None
    assert "name" in frontmatter
    assert "role" in frontmatter
    assert frontmatter["name"] == "research-agent"


def test_get_agent_for_issue_type():
    """Should map issue types to correct agents."""
    from triads.km.system_agents import get_agent_for_issue_type

    assert get_agent_for_issue_type("sparse_entity") == "research-agent"
    assert get_agent_for_issue_type("low_confidence") == "verification-agent"
    assert get_agent_for_issue_type("missing_evidence") == "verification-agent"


def test_get_agent_for_issue_type_unknown():
    """Should raise ValueError for unknown issue type."""
    import pytest

    from triads.km.system_agents import get_agent_for_issue_type

    with pytest.raises(ValueError, match="Unknown issue type"):
        get_agent_for_issue_type("unknown_type")


def test_format_agent_task_sparse_entity():
    """Should format task description for sparse entity enrichment."""
    from triads.km.system_agents import format_agent_task

    issue = {
        "type": "sparse_entity",
        "triad": "discovery",
        "node_id": "jwt_lib",
        "label": "JWT Library",
        "property_count": 1,
    }

    task = format_agent_task(issue)

    assert "JWT Library" in task
    assert "jwt_lib" in task
    assert "sparse" in task.lower() or "enrich" in task.lower()
    assert "discovery" in task


def test_format_agent_task_low_confidence():
    """Should format task description for confidence verification."""
    from triads.km.system_agents import format_agent_task

    issue = {
        "type": "low_confidence",
        "triad": "design",
        "node_id": "uncertain_decision",
        "label": "OAuth2 Choice",
        "confidence": 0.72,
    }

    task = format_agent_task(issue)

    assert "OAuth2 Choice" in task
    assert "uncertain_decision" in task
    assert "0.72" in task or "72" in task
    assert "verif" in task.lower() or "confidence" in task.lower()


def test_format_agent_task_missing_evidence():
    """Should format task description for evidence validation."""
    from triads.km.system_agents import format_agent_task

    issue = {
        "type": "missing_evidence",
        "triad": "implementation",
        "node_id": "uncited_fact",
        "label": "Security claim",
    }

    task = format_agent_task(issue)

    assert "Security claim" in task
    assert "uncited_fact" in task
    assert "evidence" in task.lower()
