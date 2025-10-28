"""
Tests for coordination skill generator.

Tests template-based skill generation from routing table.
"""

import pytest
from pathlib import Path
import yaml
import tempfile
import shutil
from triads.coordination_skill_generator import (
    generate_coordination_skill,
    discover_brief_skills,
    generate_all_coordination_skills,
    COORDINATION_SKILL_TEMPLATE
)


@pytest.fixture
def test_output_dir():
    """Create temporary output directory."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def test_routing_table(test_output_dir):
    """Create test routing table YAML."""
    routing_table = {
        "version": "1.0.0",
        "domain": "software-development",
        "generated_at": "2025-10-28T18:42:04.059856+00:00",
        "routing_decisions": {
            "bug": {
                "description": "Bug fixes, error resolution, crash fixes",
                "keywords": ["fix", "bug", "error", "crash"],
                "target_triad": "implementation",
                "entry_agent": "senior-developer",
                "brief_skill": "bug-brief",
                "priority": 1,
                "confidence": 0.95
            },
            "feature": {
                "description": "New features, enhancements, capabilities",
                "keywords": ["feature", "add", "implement", "new"],
                "target_triad": "idea-validation",
                "entry_agent": "research-analyst",
                "brief_skill": "feature-brief",
                "priority": 2,
                "confidence": 0.90
            }
        }
    }

    routing_path = test_output_dir / "routing_table.yaml"
    routing_path.write_text(yaml.dump(routing_table, sort_keys=False))
    return routing_path


@pytest.fixture
def test_skills_dir(test_output_dir):
    """Create test skills directory with brief skills."""
    skills_dir = test_output_dir / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)

    # Create test brief skills
    (skills_dir / "bug-brief.md").write_text("# Bug Brief Skill")
    (skills_dir / "feature-brief.md").write_text("# Feature Brief Skill")
    (skills_dir / "refactor-brief.md").write_text("# Refactor Brief Skill")

    return skills_dir


class TestGenerateCoordinationSkill:
    """Test single coordination skill generation."""

    def test_generate_coordination_skill_creates_file(self, test_output_dir):
        """Test that coordination skill file is created."""
        work_type = "bug"
        config = {
            "keywords": ["fix", "bug", "error", "crash"],
            "target_triad": "implementation",
            "entry_agent": "senior-developer",
            "brief_skill": "bug-brief",
            "confidence": 0.95
        }
        domain = "software-development"

        skill_path = generate_coordination_skill(work_type, config, domain, test_output_dir)

        assert skill_path.exists()
        assert skill_path.name == "coordinate-bug.md"

    def test_generate_coordination_skill_has_correct_frontmatter(self, test_output_dir):
        """Test that generated skill has correct frontmatter."""
        work_type = "feature"
        config = {
            "keywords": ["feature", "add", "implement", "new"],
            "target_triad": "idea-validation",
            "entry_agent": "research-analyst",
            "brief_skill": "feature-brief",
            "confidence": 0.90
        }
        domain = "software-development"

        skill_path = generate_coordination_skill(work_type, config, domain, test_output_dir)
        content = skill_path.read_text()

        # Check frontmatter
        assert "name: coordinate-feature" in content
        assert "description: Coordinate feature workflow" in content
        assert "category: coordination" in content
        assert "domain: software-development" in content
        assert 'allowed_tools: ["Task", "Read", "Grep"]' in content

    def test_generate_coordination_skill_has_keywords(self, test_output_dir):
        """Test that generated skill includes keywords from config."""
        work_type = "bug"
        config = {
            "keywords": ["fix", "bug", "error", "crash"],
            "target_triad": "implementation",
            "entry_agent": "senior-developer",
            "brief_skill": "bug-brief",
            "confidence": 0.95
        }
        domain = "software-development"

        skill_path = generate_coordination_skill(work_type, config, domain, test_output_dir)
        content = skill_path.read_text()

        assert "fix, bug, error, crash" in content

    def test_generate_coordination_skill_has_triad_info(self, test_output_dir):
        """Test that generated skill includes triad and entry agent."""
        work_type = "feature"
        config = {
            "keywords": ["feature", "add"],
            "target_triad": "idea-validation",
            "entry_agent": "research-analyst",
            "brief_skill": "feature-brief",
            "confidence": 0.90
        }
        domain = "software-development"

        skill_path = generate_coordination_skill(work_type, config, domain, test_output_dir)
        content = skill_path.read_text()

        assert "idea-validation" in content
        assert "research-analyst" in content

    def test_generate_coordination_skill_has_brief_skill(self, test_output_dir):
        """Test that generated skill references correct brief skill."""
        work_type = "bug"
        config = {
            "keywords": ["fix", "bug"],
            "target_triad": "implementation",
            "entry_agent": "senior-developer",
            "brief_skill": "bug-brief",
            "confidence": 0.95
        }
        domain = "software-development"

        skill_path = generate_coordination_skill(work_type, config, domain, test_output_dir)
        content = skill_path.read_text()

        assert "bug-brief" in content

    def test_generate_coordination_skill_has_four_phases(self, test_output_dir):
        """Test that generated skill includes all 4 phases."""
        work_type = "feature"
        config = {
            "keywords": ["feature"],
            "target_triad": "idea-validation",
            "entry_agent": "research-analyst",
            "brief_skill": "feature-brief",
            "confidence": 0.90
        }
        domain = "software-development"

        skill_path = generate_coordination_skill(work_type, config, domain, test_output_dir)
        content = skill_path.read_text()

        # Check for 4 phases
        assert "Phase 1: CREATE BRIEF" in content
        assert "Phase 2: ROUTE TO TRIAD" in content
        assert "Phase 3: INVOKE TRIAD" in content
        assert "Phase 4: MONITOR EXECUTION" in content

    def test_generate_coordination_skill_has_error_handling(self, test_output_dir):
        """Test that generated skill includes error handling section."""
        work_type = "bug"
        config = {
            "keywords": ["fix", "bug"],
            "target_triad": "implementation",
            "entry_agent": "senior-developer",
            "brief_skill": "bug-brief",
            "confidence": 0.95
        }
        domain = "software-development"

        skill_path = generate_coordination_skill(work_type, config, domain, test_output_dir)
        content = skill_path.read_text()

        assert "## Error Handling" in content
        assert "Phase 1 Errors" in content
        assert "Phase 2 Errors" in content
        assert "Phase 3 Errors" in content
        assert "Phase 4 Errors" in content

    def test_generate_coordination_skill_has_examples(self, test_output_dir):
        """Test that generated skill includes examples section."""
        work_type = "feature"
        config = {
            "keywords": ["feature"],
            "target_triad": "idea-validation",
            "entry_agent": "research-analyst",
            "brief_skill": "feature-brief",
            "confidence": 0.90
        }
        domain = "software-development"

        skill_path = generate_coordination_skill(work_type, config, domain, test_output_dir)
        content = skill_path.read_text()

        assert "## Examples" in content

    def test_generate_coordination_skill_has_constitutional_compliance(self, test_output_dir):
        """Test that generated skill includes constitutional compliance section."""
        work_type = "bug"
        config = {
            "keywords": ["fix", "bug"],
            "target_triad": "implementation",
            "entry_agent": "senior-developer",
            "brief_skill": "bug-brief",
            "confidence": 0.95
        }
        domain = "software-development"

        skill_path = generate_coordination_skill(work_type, config, domain, test_output_dir)
        content = skill_path.read_text()

        assert "## Constitutional Compliance" in content
        assert "Evidence-Based" in content
        assert "Transparency" in content
        assert "Uncertainty Escalation" in content


class TestDiscoverBriefSkills:
    """Test brief skill discovery."""

    def test_discover_brief_skills_finds_all(self, test_skills_dir):
        """Test that all brief skills are discovered."""
        brief_skills = discover_brief_skills(test_skills_dir)

        assert "bug" in brief_skills
        assert "feature" in brief_skills
        assert "refactor" in brief_skills

    def test_discover_brief_skills_excludes_non_brief(self, test_skills_dir):
        """Test that non-brief skills are excluded."""
        # Create non-brief skill
        (test_skills_dir / "coordinate-bug.md").write_text("# Coordination Skill")

        brief_skills = discover_brief_skills(test_skills_dir)

        assert "bug" in brief_skills
        assert "coordinate-bug" not in brief_skills

    def test_discover_brief_skills_empty_directory(self, test_output_dir):
        """Test discovery in empty directory."""
        empty_dir = test_output_dir / "empty"
        empty_dir.mkdir()

        brief_skills = discover_brief_skills(empty_dir)

        assert brief_skills == []


class TestGenerateAllCoordinationSkills:
    """Test generating all coordination skills from routing table."""

    def test_generate_all_coordination_skills_creates_all_files(self, test_routing_table, test_output_dir):
        """Test that all coordination skills are generated."""
        output_dir = test_output_dir / "skills"

        generated_skills = generate_all_coordination_skills(test_routing_table, output_dir)

        assert len(generated_skills) == 2  # bug and feature
        assert all(skill_path.exists() for skill_path in generated_skills)

    def test_generate_all_coordination_skills_has_correct_names(self, test_routing_table, test_output_dir):
        """Test that generated skills have correct names."""
        output_dir = test_output_dir / "skills"

        generated_skills = generate_all_coordination_skills(test_routing_table, output_dir)
        skill_names = [skill_path.name for skill_path in generated_skills]

        assert "coordinate-bug.md" in skill_names
        assert "coordinate-feature.md" in skill_names

    def test_generate_all_coordination_skills_creates_output_dir(self, test_routing_table, test_output_dir):
        """Test that output directory is created if it doesn't exist."""
        output_dir = test_output_dir / "new_skills"
        assert not output_dir.exists()

        generate_all_coordination_skills(test_routing_table, output_dir)

        assert output_dir.exists()

    def test_generate_all_coordination_skills_returns_paths(self, test_routing_table, test_output_dir):
        """Test that function returns list of generated skill paths."""
        output_dir = test_output_dir / "skills"

        generated_skills = generate_all_coordination_skills(test_routing_table, output_dir)

        assert isinstance(generated_skills, list)
        assert all(isinstance(path, Path) for path in generated_skills)


class TestCoordinationSkillTemplate:
    """Test coordination skill template structure."""

    def test_template_has_all_placeholders(self):
        """Test that template includes all required placeholders."""
        required_placeholders = [
            "{work_type}",
            "{work_type_title}",
            "{keyword_list}",
            "{domain}",
            "{target_triad}",
            "{entry_agent}",
            "{brief_skill}",
            "{confidence}",
            "{generated_at}"
        ]

        for placeholder in required_placeholders:
            assert placeholder in COORDINATION_SKILL_TEMPLATE, f"Missing placeholder: {placeholder}"

    def test_template_has_frontmatter_section(self):
        """Test that template includes frontmatter."""
        assert "---" in COORDINATION_SKILL_TEMPLATE
        assert "name:" in COORDINATION_SKILL_TEMPLATE
        assert "description:" in COORDINATION_SKILL_TEMPLATE
        assert "category:" in COORDINATION_SKILL_TEMPLATE

    def test_template_has_four_phase_workflow(self):
        """Test that template includes 4-phase workflow."""
        assert "Phase 1: CREATE BRIEF" in COORDINATION_SKILL_TEMPLATE
        assert "Phase 2: ROUTE TO TRIAD" in COORDINATION_SKILL_TEMPLATE
        assert "Phase 3: INVOKE TRIAD" in COORDINATION_SKILL_TEMPLATE
        assert "Phase 4: MONITOR EXECUTION" in COORDINATION_SKILL_TEMPLATE

    def test_template_has_error_handling(self):
        """Test that template includes error handling section."""
        assert "## Error Handling" in COORDINATION_SKILL_TEMPLATE

    def test_template_has_examples(self):
        """Test that template includes examples section."""
        assert "## Examples" in COORDINATION_SKILL_TEMPLATE

    def test_template_has_constitutional_compliance(self):
        """Test that template includes constitutional compliance section."""
        assert "## Constitutional Compliance" in COORDINATION_SKILL_TEMPLATE


class TestGenerateWithoutRoutingTable:
    """Test generation without routing_decision_table.yaml (Phase 3)."""

    @pytest.fixture
    def test_brief_skills_dir(self, test_output_dir):
        """Create test directory with brief skills having proper frontmatter."""
        skills_dir = test_output_dir / "skills" / "software-development"
        skills_dir.mkdir(parents=True, exist_ok=True)

        # Create bug-brief.md with frontmatter
        bug_brief = """---
name: bug-brief
description: Transform bug report into BugBrief specification
category: brief
domain: software-development
---

# Bug Brief Skill
Brief skill for bugs."""
        (skills_dir / "bug-brief.md").write_text(bug_brief)

        # Create feature-brief.md with frontmatter
        feature_brief = """---
name: feature-brief
description: Transform feature idea into FeatureBrief
category: brief
domain: software-development
---

# Feature Brief Skill
Brief skill for features."""
        (skills_dir / "feature-brief.md").write_text(feature_brief)

        return skills_dir.parent  # Return parent to match _discover_brief_skills expectations

    def test_generate_without_routing_table(self, test_brief_skills_dir, test_output_dir):
        """Test that coordination skills can be generated without YAML routing table."""
        output_dir = test_output_dir / "coordination_skills"

        # This should work WITHOUT a routing_decision_table.yaml file
        # Expected new signature: generate_all_coordination_skills(skills_dir, output_dir)
        from triads.coordination_skill_generator import generate_all_coordination_skills_from_discovery

        generated_skills = generate_all_coordination_skills_from_discovery(
            test_brief_skills_dir,
            output_dir
        )

        # Should generate coordination skills for discovered brief skills
        assert len(generated_skills) >= 2  # At least bug and feature
        assert all(skill_path.exists() for skill_path in generated_skills)

    def test_discovers_all_brief_skills(self, test_brief_skills_dir, test_output_dir):
        """Test that filesystem discovery finds all brief skills."""
        output_dir = test_output_dir / "coordination_skills"

        from triads.coordination_skill_generator import generate_all_coordination_skills_from_discovery

        generated_skills = generate_all_coordination_skills_from_discovery(
            test_brief_skills_dir,
            output_dir
        )

        skill_names = [skill_path.stem for skill_path in generated_skills]

        # Should find bug-brief and feature-brief
        assert "coordinate-bug" in skill_names
        assert "coordinate-feature" in skill_names

    def test_generates_coordinate_bug_skill(self, test_brief_skills_dir, test_output_dir):
        """Test that coordinate-bug.md is generated (was missing before!)."""
        output_dir = test_output_dir / "coordination_skills"

        from triads.coordination_skill_generator import generate_all_coordination_skills_from_discovery

        generated_skills = generate_all_coordination_skills_from_discovery(
            test_brief_skills_dir,
            output_dir
        )

        # Verify coordinate-bug.md exists
        bug_skill = output_dir / "coordinate-bug.md"
        assert bug_skill.exists()

        content = bug_skill.read_text()
        assert "bug-brief" in content
        assert "coordinate-bug" in content

    def test_generated_skills_have_correct_structure(self, test_brief_skills_dir, test_output_dir):
        """Test that generated skills have correct 4-phase structure."""
        output_dir = test_output_dir / "coordination_skills"

        from triads.coordination_skill_generator import generate_all_coordination_skills_from_discovery

        generated_skills = generate_all_coordination_skills_from_discovery(
            test_brief_skills_dir,
            output_dir
        )

        for skill_path in generated_skills:
            content = skill_path.read_text()

            # Check frontmatter
            assert "name: coordinate-" in content
            assert "category: coordination" in content

            # Check phases
            assert "Phase 1: CREATE BRIEF" in content
            assert "Phase 2: ROUTE TO TRIAD" in content
            assert "Phase 3: INVOKE TRIAD" in content
            assert "Phase 4: MONITOR EXECUTION" in content


class TestIntegration:
    """Integration tests for full workflow."""

    def test_end_to_end_skill_generation(self, test_routing_table, test_output_dir):
        """Test complete workflow from routing table to generated skills."""
        output_dir = test_output_dir / "skills"

        # Generate all skills
        generated_skills = generate_all_coordination_skills(test_routing_table, output_dir)

        # Verify all skills generated
        assert len(generated_skills) == 2

        # Verify each skill is valid
        for skill_path in generated_skills:
            assert skill_path.exists()
            content = skill_path.read_text()

            # Check frontmatter
            assert "name: coordinate-" in content
            assert "category: coordination" in content

            # Check phases
            assert "Phase 1: CREATE BRIEF" in content
            assert "Phase 2: ROUTE TO TRIAD" in content
            assert "Phase 3: INVOKE TRIAD" in content
            assert "Phase 4: MONITOR EXECUTION" in content

            # Check error handling
            assert "## Error Handling" in content

            # Check examples
            assert "## Examples" in content

            # Check constitutional compliance
            assert "## Constitutional Compliance" in content
