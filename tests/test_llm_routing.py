"""Tests for LLM-based routing system using Claude Code headless mode.

This module tests the intelligent routing system that replaces brittle keyword
matching with LLM-based intent detection via Claude Code headless mode.

Constitutional Requirements:
- TDD: Tests written BEFORE implementation (RED-GREEN-REFACTOR)
- Evidence-Based: Tests provide evidence that behavior works
- Multi-Method: Multiple test scenarios verify correctness
"""

import json
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from triads.llm_routing import (
    route_to_brief_skill,
    _discover_brief_skills,
    _call_claude_headless,
    _keyword_fallback,
)


class TestRouteToFullSkill:
    """Tests for main routing function."""

    def test_route_bug_investigation(self, tmp_path):
        """Bug investigation should route to bug-brief with high confidence.

        RED Phase Test: This test MUST fail initially because route_to_brief_skill
        is not yet implemented.

        Evidence: ADR-001 lines 506-516 specify bug investigation routing.
        Expected: confidence ≥0.85, correct skill, cost <$0.01, duration <2000ms
        """
        # Arrange: Create minimal brief skill structure
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        bug_brief = skills_dir / "bug-brief.md"
        bug_brief.write_text("""---
name: bug-brief
description: Transform vague bug report into complete BugBrief specification
category: brief
domain: software-development
---
# Bug Brief Skill
""")

        # Mock Claude Code headless response
        mock_claude_response = {
            "type": "result",
            "subtype": "success",
            "total_cost_usd": 0.003,
            "is_error": False,
            "duration_ms": 1200,
            "result": json.dumps({
                "brief_skill": "bug-brief",
                "confidence": 0.92,
                "reasoning": "User is investigating missing functionality"
            })
        }

        with patch('triads.llm_routing.subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                stdout=json.dumps(mock_claude_response),
                returncode=0
            )

            # Act: Route user input
            result = route_to_brief_skill(
                user_input="investigate why /upgrade-to-templates command isn't there",
                skills_dir=skills_dir,
                confidence_threshold=0.70,
                timeout=2
            )

        # Assert: Verify routing decision
        assert result["brief_skill"] == "bug-brief"
        assert result["confidence"] >= 0.85
        assert result["confidence"] <= 1.0
        assert "reasoning" in result
        assert result["cost_usd"] < 0.01
        assert result["duration_ms"] < 2000

    def test_route_feature_request(self, tmp_path):
        """Feature request should route to feature-brief with high confidence.

        Evidence: ADR-001 lines 521-532 specify feature request routing.
        """
        # Arrange
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        feature_brief = skills_dir / "feature-brief.md"
        feature_brief.write_text("""---
name: feature-brief
description: Transform feature idea into complete FeatureBrief specification
category: brief
domain: software-development
---
# Feature Brief Skill
""")

        mock_claude_response = {
            "type": "result",
            "subtype": "success",
            "total_cost_usd": 0.003,
            "is_error": False,
            "duration_ms": 1150,
            "result": json.dumps({
                "brief_skill": "feature-brief",
                "confidence": 0.96,
                "reasoning": "User requests new feature (dark mode)"
            })
        }

        with patch('triads.llm_routing.subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                stdout=json.dumps(mock_claude_response),
                returncode=0
            )

            # Act
            result = route_to_brief_skill(
                user_input="can we add dark mode to the UI",
                skills_dir=skills_dir
            )

        # Assert
        assert result["brief_skill"] == "feature-brief"
        assert result["confidence"] >= 0.90
        assert "dark mode" in result["reasoning"].lower()

    def test_route_refactoring_request(self, tmp_path):
        """Refactoring request should route to refactor-brief.

        Evidence: ADR-001 specifies system handles refactoring as work type.
        """
        # Arrange
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        refactor_brief = skills_dir / "refactor-brief.md"
        refactor_brief.write_text("""---
name: refactor-brief
description: Transform refactoring request into complete RefactorBrief
category: brief
domain: software-development
---
# Refactor Brief Skill
""")

        mock_claude_response = {
            "type": "result",
            "subtype": "success",
            "total_cost_usd": 0.003,
            "is_error": False,
            "duration_ms": 1100,
            "result": json.dumps({
                "brief_skill": "refactor-brief",
                "confidence": 0.94,
                "reasoning": "Code cleanup and quality improvement request"
            })
        }

        with patch('triads.llm_routing.subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                stdout=json.dumps(mock_claude_response),
                returncode=0
            )

            # Act
            result = route_to_brief_skill(
                user_input="the router code has lots of duplication and needs cleanup",
                skills_dir=skills_dir
            )

        # Assert
        assert result["brief_skill"] == "refactor-brief"
        assert result["confidence"] >= 0.90

    def test_route_ambiguous_request(self, tmp_path):
        """Ambiguous request should route with medium confidence.

        Evidence: ADR-001 lines 536-545 specify ambiguous routing.
        Expected: Confidence 0.70-0.85, reasonable skill choice.
        """
        # Arrange
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        bug_brief = skills_dir / "bug-brief.md"
        bug_brief.write_text("""---
name: bug-brief
description: Transform vague bug report into complete BugBrief specification
category: brief
---
# Bug Brief
""")

        mock_claude_response = {
            "type": "result",
            "subtype": "success",
            "total_cost_usd": 0.003,
            "is_error": False,
            "duration_ms": 1300,
            "result": json.dumps({
                "brief_skill": "bug-brief",
                "confidence": 0.75,
                "reasoning": "Performance issue, could be bug or optimization opportunity"
            })
        }

        with patch('triads.llm_routing.subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                stdout=json.dumps(mock_claude_response),
                returncode=0
            )

            # Act
            result = route_to_brief_skill(
                user_input="the system is slow",
                skills_dir=skills_dir
            )

        # Assert: Medium confidence for ambiguous input
        assert 0.70 <= result["confidence"] <= 0.85
        assert result["brief_skill"] in ["bug-brief"]

    def test_timeout_fallback(self, tmp_path):
        """LLM timeout should fallback to keyword matching.

        Evidence: ADR-001 lines 234-236, 451-460 specify timeout handling.
        Expected: Graceful degradation, no error to user.
        """
        # Arrange
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        bug_brief = skills_dir / "bug-brief.md"
        bug_brief.write_text("""---
name: bug-brief
description: Bug investigation skill
category: brief
---
# Bug Brief
""")

        with patch('triads.llm_routing.subprocess.run') as mock_run:
            # Simulate timeout
            mock_run.side_effect = subprocess.TimeoutExpired(
                cmd=["claude"], timeout=2
            )

            # Act
            result = route_to_brief_skill(
                user_input="investigate the bug in authentication",
                skills_dir=skills_dir,
                timeout=2
            )

        # Assert: Fallback should work
        assert result["brief_skill"] == "bug-brief"
        assert result["confidence"] == 0.60  # Lower confidence for fallback
        assert result["reasoning"] == "Fallback keyword matching"
        assert result["cost_usd"] == 0.0
        assert result["duration_ms"] == 0

    def test_cost_tracking(self, tmp_path):
        """Cost tracking should be included in response.

        Evidence: ADR-001 lines 320-326 specify cost tracking requirement.
        Expected: total_cost_usd field present, <$0.01 per call.
        """
        # Arrange
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        feature_brief = skills_dir / "feature-brief.md"
        feature_brief.write_text("""---
name: feature-brief
description: Feature specification skill
category: brief
---
# Feature Brief
""")

        mock_claude_response = {
            "type": "result",
            "subtype": "success",
            "total_cost_usd": 0.0035,  # Specific cost value
            "is_error": False,
            "duration_ms": 1180,
            "result": json.dumps({
                "brief_skill": "feature-brief",
                "confidence": 0.93,
                "reasoning": "New feature request"
            })
        }

        with patch('triads.llm_routing.subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                stdout=json.dumps(mock_claude_response),
                returncode=0
            )

            # Act
            result = route_to_brief_skill(
                user_input="add user profile feature",
                skills_dir=skills_dir
            )

        # Assert: Cost tracking present
        assert "cost_usd" in result
        assert result["cost_usd"] == 0.0035
        assert result["cost_usd"] < 0.01  # Budget requirement


class TestDiscoverBriefSkills:
    """Tests for brief skill discovery from filesystem."""

    def test_discover_brief_skills(self, tmp_path):
        """Should discover all *-brief.md files and parse frontmatter.

        Evidence: ADR-001 lines 122-123 specify discovery mechanism.
        """
        # Arrange: Create brief skills
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        # Bug brief
        (skills_dir / "bug-brief.md").write_text("""---
name: bug-brief
description: Transform bug report into specification
purpose: Bug investigation
category: brief
---
# Bug Brief
""")

        # Feature brief
        (skills_dir / "feature-brief.md").write_text("""---
name: feature-brief
description: Transform feature idea into specification
purpose: Feature planning
category: brief
---
# Feature Brief
""")

        # Non-brief file (should be ignored)
        (skills_dir / "coordinate-bug.md").write_text("""---
name: coordinate-bug
category: coordination
---
# Not a brief skill
""")

        # Act
        brief_skills = _discover_brief_skills(skills_dir)

        # Assert: Only brief skills discovered
        assert len(brief_skills) == 2
        assert "bug-brief" in brief_skills
        assert "feature-brief" in brief_skills
        assert "coordinate-bug" not in brief_skills

        # Verify metadata parsed
        assert brief_skills["bug-brief"]["description"] == "Transform bug report into specification"
        assert brief_skills["bug-brief"]["purpose"] == "Bug investigation"
        assert brief_skills["feature-brief"]["description"] == "Transform feature idea into specification"


class TestCallClaudeHeadless:
    """Tests for Claude Code headless subprocess call."""

    def test_call_claude_headless_success(self):
        """Successful Claude call should return routing decision.

        Evidence: ADR-001 lines 130-167 specify subprocess call pattern.
        """
        # Arrange
        system_prompt = "You are a routing agent"
        user_message = "Route this: investigate bug"

        mock_claude_response = {
            "type": "result",
            "subtype": "success",
            "total_cost_usd": 0.003,
            "is_error": False,
            "duration_ms": 1234,
            "result": json.dumps({
                "brief_skill": "bug-brief",
                "confidence": 0.92,
                "reasoning": "Bug investigation"
            })
        }

        with patch('triads.llm_routing.subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                stdout=json.dumps(mock_claude_response),
                returncode=0
            )

            # Act
            result = _call_claude_headless(system_prompt, user_message, timeout=2)

        # Assert: Verify subprocess call
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert call_args[0][0] == ["claude", "-p", user_message,
                                     "--append-system-prompt", system_prompt,
                                     "--output-format", "json",
                                     "--allowedTools", ""]
        assert call_args[1]["timeout"] == 2
        assert call_args[1]["capture_output"] is True

        # Verify result
        assert result["brief_skill"] == "bug-brief"
        assert result["confidence"] == 0.92
        assert result["cost_usd"] == 0.003
        assert result["duration_ms"] == 1234

    def test_call_claude_headless_error_response(self):
        """Claude error response should raise RuntimeError.

        Evidence: ADR-001 lines 148-149 specify error handling.
        """
        # Arrange
        mock_error_response = {
            "type": "result",
            "is_error": True,
            "result": "API rate limit exceeded"
        }

        with patch('triads.llm_routing.subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                stdout=json.dumps(mock_error_response),
                returncode=0
            )

            # Act & Assert
            with pytest.raises(RuntimeError, match="Claude Code error"):
                _call_claude_headless("prompt", "message", timeout=2)

    def test_call_claude_headless_timeout(self):
        """Timeout should raise TimeoutExpired.

        Evidence: ADR-001 lines 160-162 specify timeout handling.
        """
        # Arrange
        with patch('triads.llm_routing.subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired(
                cmd=["claude"], timeout=2
            )

            # Act & Assert
            with pytest.raises(subprocess.TimeoutExpired):
                _call_claude_headless("prompt", "message", timeout=2)


class TestKeywordFallback:
    """Tests for keyword-based fallback when LLM fails."""

    def test_keyword_fallback_matches_skill_name(self):
        """Keyword fallback should match skill name in user input.

        Evidence: ADR-001 lines 243-261 specify fallback mechanism.
        """
        # Arrange
        brief_skills = {
            "bug-brief": {"description": "Bug investigation"},
            "feature-brief": {"description": "Feature planning"}
        }

        # Act
        result = _keyword_fallback("investigate the bug", brief_skills)

        # Assert
        assert result["brief_skill"] == "bug-brief"
        assert result["confidence"] == 0.60
        assert result["reasoning"] == "Fallback keyword matching"
        assert result["cost_usd"] == 0.0

    def test_keyword_fallback_no_match(self):
        """No keyword match should return first available skill.

        Evidence: ADR-001 lines 254-261 specify default fallback.
        """
        # Arrange
        brief_skills = {
            "bug-brief": {"description": "Bug investigation"},
            "feature-brief": {"description": "Feature planning"}
        }

        # Act
        result = _keyword_fallback("something unrelated", brief_skills)

        # Assert
        assert result["brief_skill"] == "bug-brief"  # First in dict
        assert result["confidence"] == 0.50  # Lower confidence
        assert "No match found" in result["reasoning"]
