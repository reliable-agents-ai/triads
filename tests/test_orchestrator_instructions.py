"""Tests for orchestrator instruction generation."""

import json
import sys
import tempfile
from pathlib import Path

import pytest

# Add hooks to path
repo_root = Path(__file__).parent.parent
if str(repo_root / "hooks") not in sys.path:
    sys.path.insert(0, str(repo_root / "hooks"))

from user_prompt_submit import generate_orchestrator_instructions, load_workflow_config


@pytest.fixture
def mock_config_file(tmp_path, monkeypatch):
    """Create temporary .claude/settings.json for testing."""
    # Create directory structure
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()

    # Sample config
    config = {
        "triad_system": {
            "triads": {
                "implementation": {
                    "purpose": "Code features, write tests, ensure quality",
                    "agents": [
                        "design-bridge",
                        "senior-developer",
                        "test-engineer"
                    ],
                    "final_agent": "test-engineer",
                    "next_triad": "garden-tending",
                    "graph_file": ".claude/graphs/implementation_graph.json"
                },
                "design": {
                    "purpose": "Design solutions, make architectural decisions",
                    "agents": [
                        "validation-synthesizer",
                        "solution-architect",
                        "design-bridge"
                    ],
                    "final_agent": "design-bridge",
                    "next_triad": "implementation",
                    "graph_file": ".claude/graphs/design_graph.json"
                }
            }
        }
    }

    # Write config
    settings_path = claude_dir / "settings.json"
    with open(settings_path, 'w') as f:
        json.dump(config, f)

    # Patch get_project_dir to return tmp_path
    def mock_get_project_dir():
        return tmp_path

    monkeypatch.setattr("user_prompt_submit.get_project_dir", mock_get_project_dir)

    return tmp_path


# ============================================================================
# Test generate_orchestrator_instructions
# ============================================================================

def test_generate_orchestrator_instructions_basic(mock_config_file):
    """Test basic orchestrator instruction generation."""
    instructions = generate_orchestrator_instructions(
        triad_name="implementation",
        user_request="Add OAuth2 support",
        request_type="feature"
    )

    # Check header
    assert "ORCHESTRATOR MODE" in instructions
    assert "TRIAD EXECUTION" in instructions

    # Check mission section
    assert "Add OAuth2 support" in instructions
    assert "feature" in instructions
    assert "implementation" in instructions
    assert "Code features, write tests, ensure quality" in instructions


def test_generate_orchestrator_instructions_agent_sequence(mock_config_file):
    """Test that agent sequence is properly formatted."""
    instructions = generate_orchestrator_instructions(
        triad_name="implementation",
        user_request="Test request",
        request_type="feature"
    )

    # Check all agents listed
    assert "design-bridge" in instructions
    assert "senior-developer" in instructions
    assert "test-engineer" in instructions

    # Check sequence formatting
    assert "AGENT SEQUENCE" in instructions
    assert "1. design-bridge" in instructions


def test_generate_orchestrator_instructions_protocol_steps(mock_config_file):
    """Test that all protocol steps are included."""
    instructions = generate_orchestrator_instructions(
        triad_name="implementation",
        user_request="Test request",
        request_type="feature"
    )

    # Check all 5 steps present
    assert "STEP 1: INVOKE" in instructions
    assert "STEP 2: CAPTURE" in instructions
    assert "STEP 3: CHECK GATES" in instructions
    assert "STEP 4: DISPLAY" in instructions
    assert "STEP 5: PASS CONTEXT" in instructions


def test_generate_orchestrator_instructions_hitl_protocol(mock_config_file):
    """Test that HITL gate protocol is included."""
    instructions = generate_orchestrator_instructions(
        triad_name="implementation",
        user_request="Test request",
        request_type="feature"
    )

    assert "HITL GATE PROTOCOL" in instructions
    assert "[HITL_REQUIRED]" in instructions
    assert "HUMAN APPROVAL REQUIRED" in instructions
    assert "HALT execution immediately" in instructions


def test_generate_orchestrator_instructions_context_format(mock_config_file):
    """Test that context format specification is included."""
    instructions = generate_orchestrator_instructions(
        triad_name="implementation",
        user_request="Test request",
        request_type="feature"
    )

    assert "CONTEXT FORMAT SPECIFICATION" in instructions
    assert "Pass SUMMARIES, not full outputs" in instructions
    assert "[GRAPH_UPDATE]" in instructions
    assert "[AGENT_CONTEXT]" in instructions


def test_generate_orchestrator_instructions_completion_protocol(mock_config_file):
    """Test that completion protocol is included."""
    instructions = generate_orchestrator_instructions(
        triad_name="implementation",
        user_request="Test request",
        request_type="feature"
    )

    assert "COMPLETION PROTOCOL" in instructions
    assert "SUMMARIZE triad results" in instructions
    assert "[HANDOFF_REQUEST]" in instructions


def test_generate_orchestrator_instructions_error_handling(mock_config_file):
    """Test that error handling protocol is included."""
    instructions = generate_orchestrator_instructions(
        triad_name="implementation",
        user_request="Test request",
        request_type="feature"
    )

    assert "ERROR HANDLING" in instructions
    assert "IF agent fails" in instructions
    assert "CAPTURE error details" in instructions
    assert "DO NOT" in instructions


def test_generate_orchestrator_instructions_begin_orchestration(mock_config_file):
    """Test that instructions end with begin orchestration message."""
    instructions = generate_orchestrator_instructions(
        triad_name="implementation",
        user_request="Test request",
        request_type="feature"
    )

    assert "BEGIN ORCHESTRATION" in instructions
    assert "Invoke first agent: design-bridge" in instructions


def test_generate_orchestrator_instructions_different_triad(mock_config_file):
    """Test generation for different triad."""
    instructions = generate_orchestrator_instructions(
        triad_name="design",
        user_request="Design OAuth2 architecture",
        request_type="architecture"
    )

    # Check correct triad details
    assert "design" in instructions
    assert "Design solutions, make architectural decisions" in instructions
    assert "validation-synthesizer" in instructions
    assert "solution-architect" in instructions
    assert "design-bridge" in instructions
    assert "Invoke first agent: validation-synthesizer" in instructions


def test_generate_orchestrator_instructions_graph_file(mock_config_file):
    """Test that knowledge graph file path is included."""
    instructions = generate_orchestrator_instructions(
        triad_name="implementation",
        user_request="Test request",
        request_type="feature"
    )

    assert "Knowledge Graph" in instructions
    assert ".claude/graphs/implementation_graph.json" in instructions


def test_generate_orchestrator_instructions_invalid_triad(mock_config_file):
    """Test handling of invalid triad name."""
    instructions = generate_orchestrator_instructions(
        triad_name="nonexistent-triad",
        user_request="Test request",
        request_type="feature"
    )

    assert "ERROR" in instructions
    assert "not found" in instructions


def test_generate_orchestrator_instructions_no_config(monkeypatch):
    """Test handling when config cannot be loaded."""
    def mock_get_project_dir():
        return Path("/nonexistent/path")

    monkeypatch.setattr("user_prompt_submit.get_project_dir", mock_get_project_dir)

    instructions = generate_orchestrator_instructions(
        triad_name="implementation",
        user_request="Test request",
        request_type="feature"
    )

    assert "ERROR" in instructions
    assert "Could not load" in instructions


def test_generate_orchestrator_instructions_special_characters(mock_config_file):
    """Test handling of special characters in user request."""
    instructions = generate_orchestrator_instructions(
        triad_name="implementation",
        user_request="Add OAuth2 with <script> and \"quotes\"",
        request_type="feature"
    )

    # Should include user request as-is (no escaping needed in markdown)
    assert "Add OAuth2 with <script> and \"quotes\"" in instructions


def test_generate_orchestrator_instructions_unicode(mock_config_file):
    """Test handling of unicode characters in user request."""
    instructions = generate_orchestrator_instructions(
        triad_name="implementation",
        user_request="Add émoji support 🎉",
        request_type="feature"
    )

    assert "Add émoji support 🎉" in instructions


# ============================================================================
# Integration Tests
# ============================================================================

def test_orchestrator_instructions_complete_workflow(mock_config_file):
    """Test that generated instructions contain all necessary components."""
    instructions = generate_orchestrator_instructions(
        triad_name="implementation",
        user_request="Implement user authentication",
        request_type="feature"
    )

    # Verify structure completeness
    required_sections = [
        "ORCHESTRATOR MODE",
        "MISSION",
        "AGENT SEQUENCE",
        "ORCHESTRATION PROTOCOL",
        "CONTEXT FORMAT SPECIFICATION",
        "HITL GATE PROTOCOL",
        "COMPLETION PROTOCOL",
        "ERROR HANDLING",
        "BEGIN ORCHESTRATION"
    ]

    for section in required_sections:
        assert section in instructions, f"Missing required section: {section}"


def test_orchestrator_instructions_marker_compatibility(mock_config_file):
    """Test that instructions reference all required markers."""
    instructions = generate_orchestrator_instructions(
        triad_name="implementation",
        user_request="Test request",
        request_type="feature"
    )

    # All markers that agents might use
    required_markers = [
        "[GRAPH_UPDATE]",
        "[AGENT_CONTEXT]",
        "[HITL_REQUIRED]",
        "[HANDOFF_REQUEST]"
    ]

    for marker in required_markers:
        assert marker in instructions, f"Missing marker reference: {marker}"


def test_orchestrator_instructions_step_consistency(mock_config_file):
    """Test that step numbering is consistent."""
    instructions = generate_orchestrator_instructions(
        triad_name="implementation",
        user_request="Test request",
        request_type="feature"
    )

    # Check that all 5 steps are present and numbered correctly
    assert "STEP 1:" in instructions
    assert "STEP 2:" in instructions
    assert "STEP 3:" in instructions
    assert "STEP 4:" in instructions
    assert "STEP 5:" in instructions

    # Check order (STEP 1 should come before STEP 2, etc.)
    step1_pos = instructions.find("STEP 1:")
    step2_pos = instructions.find("STEP 2:")
    step3_pos = instructions.find("STEP 3:")
    step4_pos = instructions.find("STEP 4:")
    step5_pos = instructions.find("STEP 5:")

    assert step1_pos < step2_pos < step3_pos < step4_pos < step5_pos


# ============================================================================
# Edge Cases
# ============================================================================

def test_generate_orchestrator_instructions_empty_request(mock_config_file):
    """Test with empty user request."""
    instructions = generate_orchestrator_instructions(
        triad_name="implementation",
        user_request="",
        request_type="feature"
    )

    # Should still generate instructions
    assert "ORCHESTRATOR MODE" in instructions
    assert "implementation" in instructions


def test_generate_orchestrator_instructions_long_request(mock_config_file):
    """Test with very long user request."""
    long_request = "A" * 1000
    instructions = generate_orchestrator_instructions(
        triad_name="implementation",
        user_request=long_request,
        request_type="feature"
    )

    # Should include full request
    assert long_request in instructions


def test_generate_orchestrator_instructions_multiline_request(mock_config_file):
    """Test with multiline user request."""
    multiline_request = """
    Implement OAuth2 with:
    - Authorization code flow
    - Token refresh
    - Scope management
    """
    instructions = generate_orchestrator_instructions(
        triad_name="implementation",
        user_request=multiline_request,
        request_type="feature"
    )

    # Should preserve multiline format
    assert "Authorization code flow" in instructions
