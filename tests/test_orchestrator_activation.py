"""Tests for orchestrator activation logic in Supervisor instructions."""

import json
import sys
import tempfile
from pathlib import Path

import pytest

# Add hooks to path
repo_root = Path(__file__).parent.parent
if str(repo_root / "hooks") not in sys.path:
    sys.path.insert(0, str(repo_root / "hooks"))

from user_prompt_submit import (
    detect_work_request,
    format_supervisor_instructions,
    generate_orchestrator_instructions
)


@pytest.fixture
def mock_config_file(tmp_path, monkeypatch):
    """Create temporary .claude/settings.json for testing."""
    # Create directory structure
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()

    # Sample config with full workflow
    config = {
        "triad_system": {
            "workflow": {
                "name": "Software Development Workflow",
                "entry_point": "idea-validation",
                "entry_agent": "research-analyst",
                "sequence": [
                    "idea-validation",
                    "design",
                    "implementation",
                    "garden-tending",
                    "deployment"
                ]
            },
            "triads": {
                "idea-validation": {
                    "purpose": "Research ideas, validate community need",
                    "agents": [
                        "research-analyst",
                        "community-researcher",
                        "validation-synthesizer"
                    ],
                    "final_agent": "validation-synthesizer",
                    "next_triad": "design",
                    "graph_file": ".claude/graphs/idea_validation_graph.json"
                },
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
# Test Supervisor Instructions Include Detection Protocol
# ============================================================================

def test_supervisor_instructions_include_triage_protocol(mock_config_file):
    """Test that Supervisor instructions include work request detection protocol."""
    instructions = format_supervisor_instructions()

    assert "TRIAGE PROTOCOL" in instructions
    assert "CLASSIFY every user message as Q&A OR work request" in instructions


def test_supervisor_instructions_include_qa_indicators(mock_config_file):
    """Test that Supervisor instructions list Q&A indicators."""
    instructions = format_supervisor_instructions()

    # Q&A indicators
    qa_keywords = [
        "what is", "what are", "what does",
        "how does", "how do", "how to",
        "explain", "tell me about", "describe"
    ]

    for keyword in qa_keywords:
        assert keyword in instructions.lower(), f"Missing Q&A indicator: {keyword}"


def test_supervisor_instructions_include_work_indicators(mock_config_file):
    """Test that Supervisor instructions list work indicators by type."""
    instructions = format_supervisor_instructions()

    # Work type categories
    assert "Feature" in instructions
    assert "Bug" in instructions
    assert "Refactor" in instructions
    assert "Design" in instructions
    assert "Release" in instructions

    # Sample keywords for each type
    work_keywords = [
        "implement", "add", "create",  # Feature
        "fix", "bug", "error",  # Bug
        "refactor", "cleanup", "improve",  # Refactor
        "design", "architecture",  # Design
        "deploy", "release", "publish"  # Release
    ]

    for keyword in work_keywords:
        assert keyword in instructions.lower(), f"Missing work indicator: {keyword}"


def test_supervisor_instructions_include_detection_priority(mock_config_file):
    """Test that detection priority rules are included."""
    instructions = format_supervisor_instructions()

    assert "Detection Priority" in instructions
    assert "If message matches Q&A patterns" in instructions
    assert "If message matches work patterns" in instructions
    assert "If ambiguous" in instructions


def test_supervisor_instructions_include_workflow_sequence(mock_config_file):
    """Test that workflow sequence is included."""
    instructions = format_supervisor_instructions()

    # Should show complete workflow
    assert "idea-validation" in instructions
    assert "design" in instructions
    assert "implementation" in instructions
    assert "garden-tending" in instructions
    assert "deployment" in instructions


def test_supervisor_instructions_single_entry_point(mock_config_file):
    """Test that single entry point protocol is emphasized."""
    instructions = format_supervisor_instructions()

    assert "SINGLE ENTRY POINT" in instructions
    assert "idea-validation" in instructions
    assert "research-analyst" in instructions
    assert "ALL work requests SHALL enter through" in instructions


# ============================================================================
# Test Integration: Detection + Orchestration
# ============================================================================

def test_work_request_leads_to_orchestration(mock_config_file):
    """Test that work request detection can trigger orchestration."""
    # Step 1: Detect work request
    user_message = "Implement OAuth2 support"
    result = detect_work_request(user_message)

    assert result != {}
    assert result['type'] == 'feature'
    assert result['triad'] == 'idea-validation'

    # Step 2: Generate orchestrator instructions for detected triad
    orchestrator_instructions = generate_orchestrator_instructions(
        triad_name=result['triad'],
        user_request=result['original_request'],
        request_type=result['type']
    )

    # Verify orchestration instructions
    assert "ORCHESTRATOR MODE" in orchestrator_instructions
    assert "Implement OAuth2 support" in orchestrator_instructions
    assert "feature" in orchestrator_instructions
    assert "research-analyst" in orchestrator_instructions


def test_qa_request_no_orchestration(mock_config_file):
    """Test that Q&A requests don't trigger orchestration."""
    # Q&A request
    user_message = "What is OAuth2?"
    result = detect_work_request(user_message)

    # Should NOT be detected as work request
    assert result == {}


def test_supervisor_can_handle_both_modes(mock_config_file):
    """Test that Supervisor instructions support both Q&A and orchestration."""
    instructions = format_supervisor_instructions()

    # Should have Q&A handling
    assert "Q&A HANDLING" in instructions
    assert "ANSWER informational questions directly" in instructions

    # Should have workflow execution
    assert "WORKFLOW EXECUTION ORDERS" in instructions
    assert "INVOKE" in instructions


# ============================================================================
# Test Error Handling
# ============================================================================

def test_supervisor_instructions_with_missing_config(monkeypatch):
    """Test that Supervisor instructions handle missing config gracefully."""
    def mock_get_project_dir():
        return Path("/nonexistent/path")

    monkeypatch.setattr("user_prompt_submit.get_project_dir", mock_get_project_dir)

    instructions = format_supervisor_instructions()

    # Should include error message
    assert "CONFIGURATION FAILURE" in instructions or "ERROR" in instructions
    # Should still have basic instructions
    assert "SUPERVISOR" in instructions


def test_supervisor_instructions_always_include_roe(mock_config_file):
    """Test that Rules of Engagement are always included."""
    instructions = format_supervisor_instructions()

    # All ROE should be present
    assert "ROE 1: TRIAGE PROTOCOL" in instructions
    assert "ROE 2: Q&A HANDLING" in instructions
    assert "ROE 3: TRIAD ATOMICITY" in instructions
    assert "ROE 4: EMERGENCY BYPASS" in instructions


# ============================================================================
# Test Training Mode Protocol
# ============================================================================

def test_supervisor_instructions_include_training_mode(mock_config_file):
    """Test that training mode protocol is included."""
    instructions = format_supervisor_instructions()

    assert "TRAINING MODE PROTOCOL" in instructions
    assert "CLASSIFY the work request type" in instructions
    assert "REQUEST user confirmation" in instructions


# ============================================================================
# Test Emergency Bypass
# ============================================================================

def test_supervisor_instructions_include_emergency_bypass(mock_config_file):
    """Test that emergency bypass protocol is included."""
    instructions = format_supervisor_instructions()

    assert "EMERGENCY BYPASS" in instructions
    assert "/direct" in instructions
    assert "SKIP all routing" in instructions


# ============================================================================
# Test Completeness
# ============================================================================

def test_supervisor_instructions_complete_workflow(mock_config_file):
    """Test that Supervisor instructions are complete and well-formatted."""
    instructions = format_supervisor_instructions()

    # Check structure
    required_sections = [
        "SUPERVISOR STANDING ORDERS",
        "MISSION",
        "RULES OF ENGAGEMENT",
        "WORKFLOW EXECUTION ORDERS",
        "TRAINING MODE PROTOCOL"
    ]

    for section in required_sections:
        assert section in instructions, f"Missing section: {section}"

    # Check it's non-empty
    assert len(instructions) > 1000, "Instructions seem too short"

    # Check formatting
    assert "=" * 80 in instructions, "Missing section separators"
