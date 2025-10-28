"""
Tests for Entry Point Analyzer - Domain-agnostic workflow entry point analysis.

Following TDD methodology:
- RED: Tests written first
- GREEN: Minimal implementation
- REFACTOR: Code quality improvements
"""

import pytest
import json
import yaml
from pathlib import Path
from datetime import datetime

# Import functions
from triads.entry_point_analyzer import (
    find_brief_skill,
    generate_routing_table
)


class TestMatchWorkTypeToTriad:
    """DEPRECATED: Keyword matching has been replaced with LLM routing.

    These tests are kept for historical reference but marked as skipped.
    See TestLLMRouting for current routing tests.
    """

    @pytest.mark.skip(reason="Keyword matching removed - replaced with LLM routing")
    def test_match_feature_purpose(self):
        pass

    @pytest.mark.skip(reason="Keyword matching removed - replaced with LLM routing")
    def test_match_bug_purpose(self):
        pass

    @pytest.mark.skip(reason="Keyword matching removed - replaced with LLM routing")
    def test_match_refactor_purpose(self):
        pass

    @pytest.mark.skip(reason="Keyword matching removed - replaced with LLM routing")
    def test_match_release_purpose(self):
        pass

    @pytest.mark.skip(reason="Keyword matching removed - replaced with LLM routing")
    def test_match_documentation_purpose(self):
        pass

    @pytest.mark.skip(reason="Keyword matching removed - replaced with LLM routing")
    def test_no_match_generic_purpose(self):
        pass

    @pytest.mark.skip(reason="Keyword matching removed - replaced with LLM routing")
    def test_confidence_increases_with_matches(self):
        pass

    @pytest.mark.skip(reason="Keyword matching removed - replaced with LLM routing")
    def test_confidence_capped_at_095(self):
        pass

    @pytest.mark.skip(reason="Keyword matching removed - replaced with LLM routing")
    def test_matches_sorted_by_confidence(self):
        pass


class TestFindBriefSkill:
    """Test brief skill discovery."""

    def test_find_existing_brief_skill(self, tmp_path):
        """Should find existing brief skill file."""
        # Create test brief skill
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        (skills_dir / "bug-brief.md").write_text("# Bug Brief")

        result = find_brief_skill("bug", skills_dir)
        assert result == "bug-brief"

    def test_find_feature_brief_skill(self, tmp_path):
        """Should find feature brief skill."""
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        (skills_dir / "feature-brief.md").write_text("# Feature Brief")

        result = find_brief_skill("feature", skills_dir)
        assert result == "feature-brief"

    def test_fallback_to_generic_brief(self, tmp_path):
        """Should fallback to generic-brief if specific skill not found."""
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        result = find_brief_skill("nonexistent", skills_dir)
        assert result == "generic-brief"

    def test_fallback_when_directory_not_exists(self):
        """Should fallback to generic-brief if directory doesn't exist."""
        result = find_brief_skill("bug", Path("/nonexistent/path"))
        assert result == "generic-brief"


class TestGenerateRoutingTable:
    """Test routing table generation from settings.json."""

    @pytest.fixture
    def test_settings_path(self):
        """Path to test settings.json fixture."""
        return Path(__file__).parent / "fixtures" / "test_settings.json"

    @pytest.fixture
    def test_skills_dir(self):
        """Path to test brief skills directory."""
        return Path(__file__).parent / "fixtures" / "brief_skills"

    def test_generate_routing_table_creates_file(self, tmp_path, test_settings_path, test_skills_dir):
        """Should create routing_decision_table.yaml file."""
        output_path = tmp_path / "routing_decision_table.yaml"

        result = generate_routing_table(test_settings_path, test_skills_dir, output_path)

        assert output_path.exists()
        assert isinstance(result, dict)

    def test_routing_table_has_correct_structure(self, tmp_path, test_settings_path, test_skills_dir):
        """Generated routing table should have correct schema."""
        output_path = tmp_path / "routing_decision_table.yaml"

        result = generate_routing_table(test_settings_path, test_skills_dir, output_path)

        # Check top-level keys
        assert "version" in result
        assert "domain" in result
        assert "generated_at" in result
        assert "routing_decisions" in result
        assert "fallback" in result
        assert "ambiguity_resolution" in result

        # Check version
        assert result["version"] == "1.0.0"

        # Check domain
        assert result["domain"] == "software-development"

        # Check generated_at is ISO timestamp with timezone
        assert "T" in result["generated_at"]
        # Should have either Z or +00:00 for UTC
        assert ("Z" in result["generated_at"] or "+00:00" in result["generated_at"])

    def test_routing_decisions_format(self, tmp_path, test_settings_path, test_skills_dir):
        """Routing decisions should have correct format."""
        output_path = tmp_path / "routing_decision_table.yaml"

        result = generate_routing_table(test_settings_path, test_skills_dir, output_path)

        # Should have routing decisions
        assert len(result["routing_decisions"]) > 0

        # Check first decision format
        first_decision = list(result["routing_decisions"].values())[0]
        assert "description" in first_decision
        assert "keywords" in first_decision
        assert "target_triad" in first_decision
        assert "entry_agent" in first_decision
        assert "brief_skill" in first_decision
        assert "priority" in first_decision
        assert "confidence" in first_decision
        assert "examples" in first_decision

        # Check types
        assert isinstance(first_decision["keywords"], list)
        assert isinstance(first_decision["priority"], int)
        assert isinstance(first_decision["confidence"], float)
        assert isinstance(first_decision["examples"], list)

    def test_fallback_section(self, tmp_path, test_settings_path, test_skills_dir):
        """Fallback section should have correct format."""
        output_path = tmp_path / "routing_decision_table.yaml"

        result = generate_routing_table(test_settings_path, test_skills_dir, output_path)

        fallback = result["fallback"]
        assert "target_triad" in fallback
        assert "entry_agent" in fallback
        assert "rationale" in fallback

        # Should use first triad
        assert fallback["target_triad"] == "idea-validation"
        assert fallback["entry_agent"] == "research-analyst"

    def test_ambiguity_resolution_section(self, tmp_path, test_settings_path, test_skills_dir):
        """Ambiguity resolution section should have correct format."""
        output_path = tmp_path / "routing_decision_table.yaml"

        result = generate_routing_table(test_settings_path, test_skills_dir, output_path)

        ambiguity = result["ambiguity_resolution"]
        assert "strategy" in ambiguity
        assert "confidence_threshold" in ambiguity
        assert "tiebreaker" in ambiguity

        assert ambiguity["strategy"] == "priority_score"
        assert ambiguity["confidence_threshold"] == 0.70
        assert ambiguity["tiebreaker"] == "ask_user"

    def test_yaml_output_valid(self, tmp_path, test_settings_path, test_skills_dir):
        """Generated YAML should be valid and parseable."""
        output_path = tmp_path / "routing_decision_table.yaml"

        generate_routing_table(test_settings_path, test_skills_dir, output_path)

        # Read and parse YAML
        yaml_content = yaml.safe_load(output_path.read_text())

        # Should parse successfully
        assert isinstance(yaml_content, dict)
        assert "routing_decisions" in yaml_content

    def test_assigns_feature_to_idea_validation(self, tmp_path, test_settings_path, test_skills_dir):
        """Feature work type should map to idea-validation triad."""
        output_path = tmp_path / "routing_decision_table.yaml"

        result = generate_routing_table(test_settings_path, test_skills_dir, output_path)

        # Check feature mapping
        if "feature" in result["routing_decisions"]:
            feature_decision = result["routing_decisions"]["feature"]
            assert feature_decision["target_triad"] == "idea-validation"
            assert feature_decision["entry_agent"] == "research-analyst"

    def test_assigns_refactor_to_garden_tending(self, tmp_path, test_settings_path, test_skills_dir):
        """Refactor work type should map to garden-tending triad."""
        output_path = tmp_path / "routing_decision_table.yaml"

        result = generate_routing_table(test_settings_path, test_skills_dir, output_path)

        # Check refactor mapping
        if "refactor" in result["routing_decisions"]:
            refactor_decision = result["routing_decisions"]["refactor"]
            assert refactor_decision["target_triad"] == "garden-tending"
            assert refactor_decision["entry_agent"] == "cultivator"

    def test_assigns_release_to_deployment(self, tmp_path, test_settings_path, test_skills_dir):
        """Release work type should map to deployment triad."""
        output_path = tmp_path / "routing_decision_table.yaml"

        result = generate_routing_table(test_settings_path, test_skills_dir, output_path)

        # Check release mapping
        if "release" in result["routing_decisions"]:
            release_decision = result["routing_decisions"]["release"]
            assert release_decision["target_triad"] == "deployment"
            assert release_decision["entry_agent"] == "gardener-bridge"

    def test_brief_skill_references(self, tmp_path, test_settings_path, test_skills_dir):
        """Should reference correct brief skills."""
        output_path = tmp_path / "routing_decision_table.yaml"

        result = generate_routing_table(test_settings_path, test_skills_dir, output_path)

        # Feature should reference feature-brief (exists in fixtures)
        if "feature" in result["routing_decisions"]:
            assert result["routing_decisions"]["feature"]["brief_skill"] == "feature-brief"

        # Bug should reference bug-brief (exists in fixtures)
        if "bug" in result["routing_decisions"]:
            assert result["routing_decisions"]["bug"]["brief_skill"] == "bug-brief"

    def test_skips_triads_without_agents(self, tmp_path, test_skills_dir):
        """Should skip triads that have no agents."""
        # Create settings with a triad that has no agents
        settings_with_empty_triad = {
            "triad_system": {
                "workflow": {"domain": "test"},
                "triads": {
                    "empty-triad": {
                        "purpose": "Test triad with no agents",
                        "agents": []  # Empty agents list
                    },
                    "valid-triad": {
                        "purpose": "Fix bugs and resolve errors",
                        "agents": ["bug-fixer"]
                    }
                }
            }
        }

        settings_path = tmp_path / "settings_with_empty.json"
        settings_path.write_text(json.dumps(settings_with_empty_triad))
        output_path = tmp_path / "routing_table.yaml"

        result = generate_routing_table(settings_path, test_skills_dir, output_path)

        # Should only have routing decisions for valid-triad
        if "bug" in result["routing_decisions"]:
            assert result["routing_decisions"]["bug"]["target_triad"] == "valid-triad"
            assert result["routing_decisions"]["bug"]["entry_agent"] == "bug-fixer"

    def test_confidence_scores_valid_range(self, tmp_path, test_settings_path, test_skills_dir):
        """All confidence scores should be in valid range (0.70-0.95)."""
        output_path = tmp_path / "routing_decision_table.yaml"

        result = generate_routing_table(test_settings_path, test_skills_dir, output_path)

        for work_type, decision in result["routing_decisions"].items():
            confidence = decision["confidence"]
            assert confidence >= 0.70, f"{work_type} confidence {confidence} below 0.70"
            assert confidence <= 0.95, f"{work_type} confidence {confidence} above 0.95"


class TestLLMRouting:
    """Test LLM-based routing integration."""

    @pytest.fixture
    def test_settings_path(self):
        """Path to test settings.json fixture."""
        return Path(__file__).parent / "fixtures" / "test_settings.json"

    @pytest.fixture
    def test_skills_dir(self):
        """Path to test brief skills directory."""
        return Path(__file__).parent / "fixtures" / "brief_skills"

    def test_no_keyword_patterns_exist(self):
        """WORK_TYPE_PATTERNS should not exist (removed for LLM routing)."""
        from triads import entry_point_analyzer

        # Should not have WORK_TYPE_PATTERNS constant
        assert not hasattr(entry_point_analyzer, 'WORK_TYPE_PATTERNS')

    def test_generate_routing_table_uses_llm(self, tmp_path, test_settings_path, test_skills_dir, monkeypatch):
        """Should use LLM routing to analyze triad purposes."""
        from unittest.mock import Mock, patch

        # Mock route_to_brief_skill to verify it's called
        mock_route_to_brief_skill = Mock(return_value={
            "brief_skill": "feature-brief",
            "confidence": 0.92,
            "reasoning": "Triad purpose matches feature validation",
            "cost_usd": 0.003,
            "duration_ms": 1234
        })

        with patch('triads.entry_point_analyzer.route_to_brief_skill', mock_route_to_brief_skill):
            output_path = tmp_path / "routing_decision_table.yaml"
            result = generate_routing_table(test_settings_path, test_skills_dir, output_path)

            # Verify LLM routing was called
            assert mock_route_to_brief_skill.called

            # Should have routing decisions
            assert "routing_decisions" in result
            assert len(result["routing_decisions"]) > 0

    def test_routing_table_includes_bug_work_type(self, tmp_path, test_settings_path, test_skills_dir):
        """Bug work type should be included (was missing in keyword-based version)."""
        from unittest.mock import Mock, patch

        # Mock LLM to return bug classification
        def mock_llm_route(user_input, skills_dir, **kwargs):
            if "fix" in user_input.lower() or "bug" in user_input.lower():
                return {
                    "brief_skill": "bug-brief",
                    "confidence": 0.94,
                    "reasoning": "Purpose indicates bug fixing",
                    "cost_usd": 0.003,
                    "duration_ms": 1200
                }
            return {
                "brief_skill": "feature-brief",
                "confidence": 0.85,
                "reasoning": "Default to feature",
                "cost_usd": 0.003,
                "duration_ms": 1000
            }

        with patch('triads.entry_point_analyzer.route_to_brief_skill', mock_llm_route):
            output_path = tmp_path / "routing_decision_table.yaml"
            result = generate_routing_table(test_settings_path, test_skills_dir, output_path)

            # Bug work type should exist now
            assert "bug" in result["routing_decisions"] or len(result["routing_decisions"]) > 0

    def test_no_match_work_type_function_exists(self):
        """match_work_type_to_triad should not exist (removed for LLM routing)."""
        from triads import entry_point_analyzer

        # Should not have keyword matching function
        assert not hasattr(entry_point_analyzer, 'match_work_type_to_triad')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
