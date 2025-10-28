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

# Import will fail initially (RED phase) - that's expected
try:
    from triads.entry_point_analyzer import (
        match_work_type_to_triad,
        find_brief_skill,
        generate_routing_table,
        WORK_TYPE_PATTERNS
    )
except ImportError:
    # Expected in RED phase
    pass


class TestMatchWorkTypeToTriad:
    """Test keyword matching between triad purpose and work types."""

    def test_match_feature_purpose(self):
        """Feature keywords should match feature work type."""
        purpose = "Research ideas, validate community need, prioritize features"
        matches = match_work_type_to_triad(purpose)

        # Should match "feature" work type
        assert len(matches) > 0
        assert matches[0]["work_type"] == "feature"
        assert matches[0]["confidence"] >= 0.70
        assert matches[0]["confidence"] <= 0.95

    def test_match_bug_purpose(self):
        """Bug/fix keywords should match bug work type."""
        purpose = "Fix bugs, resolve errors, debug issues"
        matches = match_work_type_to_triad(purpose)

        # Should match "bug" work type
        assert len(matches) > 0
        assert matches[0]["work_type"] == "bug"
        assert matches[0]["confidence"] >= 0.70

    def test_match_refactor_purpose(self):
        """Refactor keywords should match refactor work type."""
        purpose = "Refactor code, reduce technical debt, improve code quality"
        matches = match_work_type_to_triad(purpose)

        # Should match "refactor" work type
        assert len(matches) > 0
        assert matches[0]["work_type"] == "refactor"
        assert matches[0]["confidence"] >= 0.70

    def test_match_release_purpose(self):
        """Release keywords should match release work type."""
        purpose = "Create releases, update documentation, publish packages"
        matches = match_work_type_to_triad(purpose)

        # Should match "release" work type
        assert len(matches) > 0
        assert matches[0]["work_type"] == "release"
        assert matches[0]["confidence"] >= 0.70

    def test_match_documentation_purpose(self):
        """Documentation keywords should match documentation work type."""
        purpose = "Write documentation, create guides, explain features"
        matches = match_work_type_to_triad(purpose)

        # Should match "documentation" work type
        assert len(matches) > 0
        assert matches[0]["work_type"] == "documentation"
        assert matches[0]["confidence"] >= 0.70

    def test_no_match_generic_purpose(self):
        """Generic purpose with no keywords should return empty matches."""
        purpose = "General system operations"
        matches = match_work_type_to_triad(purpose)

        # Should have no matches
        assert len(matches) == 0

    def test_confidence_increases_with_matches(self):
        """More keyword matches should increase confidence."""
        # Single keyword match
        purpose_single = "Add new feature"
        matches_single = match_work_type_to_triad(purpose_single)

        # Multiple keyword matches
        purpose_multiple = "Research new features, validate ideas, implement enhancements"
        matches_multiple = match_work_type_to_triad(purpose_multiple)

        # Multiple keywords should have higher confidence
        if matches_single and matches_multiple:
            assert matches_multiple[0]["confidence"] > matches_single[0]["confidence"]

    def test_confidence_capped_at_095(self):
        """Confidence should never exceed 0.95."""
        # Purpose with many keyword matches
        purpose = "Research new features, validate ideas, implement enhancements, add capabilities"
        matches = match_work_type_to_triad(purpose)

        if matches:
            assert matches[0]["confidence"] <= 0.95

    def test_matches_sorted_by_confidence(self):
        """Matches should be sorted by confidence descending."""
        purpose = "Fix bugs and add new features"  # Matches both bug and feature
        matches = match_work_type_to_triad(purpose)

        # Should have multiple matches
        if len(matches) >= 2:
            for i in range(len(matches) - 1):
                assert matches[i]["confidence"] >= matches[i + 1]["confidence"]


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


class TestWorkTypePatterns:
    """Test WORK_TYPE_PATTERNS constant."""

    def test_patterns_constant_exists(self):
        """WORK_TYPE_PATTERNS should be defined."""
        assert WORK_TYPE_PATTERNS is not None
        assert isinstance(WORK_TYPE_PATTERNS, dict)

    def test_all_work_types_present(self):
        """All expected work types should be in patterns."""
        expected_types = ["bug", "feature", "refactor", "release", "documentation"]

        for work_type in expected_types:
            assert work_type in WORK_TYPE_PATTERNS

    def test_pattern_structure(self):
        """Each pattern should have required fields."""
        for work_type, config in WORK_TYPE_PATTERNS.items():
            assert "keywords" in config
            assert "purpose_patterns" in config
            assert "priority" in config
            assert "description" in config

            assert isinstance(config["keywords"], list)
            assert isinstance(config["purpose_patterns"], list)
            assert isinstance(config["priority"], int)
            assert isinstance(config["description"], str)

    def test_priorities_unique(self):
        """Each work type should have unique priority."""
        priorities = [config["priority"] for config in WORK_TYPE_PATTERNS.values()]
        assert len(priorities) == len(set(priorities))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
