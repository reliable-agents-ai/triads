"""Integration tests for agent template quality standards.

These tests verify that generated agent templates include quality examples,
checklists, and standards to help agents produce high-quality graph updates
without needing to manually check KM status.

RED-GREEN-BLUE: These tests are written first and will initially FAIL.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Import the template generation function
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root / ".claude/generator/lib"))

from templates import AGENT_TEMPLATE  # noqa: E402


class TestAgentTemplateQuality:
    """Test that AGENT_TEMPLATE includes quality standards."""

    def test_template_has_bad_vs_good_examples(self) -> None:
        """Agents should see BAD and GOOD [GRAPH_UPDATE] examples."""
        # Check for BAD example marker
        assert "❌ BAD" in AGENT_TEMPLATE or "BAD EXAMPLE" in AGENT_TEMPLATE, (
            "Template must include BAD example of graph update"
        )

        # Check for GOOD example marker
        assert "✅ GOOD" in AGENT_TEMPLATE or "GOOD EXAMPLE" in AGENT_TEMPLATE, (
            "Template must include GOOD example of graph update"
        )

        # Verify both examples contain [GRAPH_UPDATE] blocks
        assert AGENT_TEMPLATE.count("[GRAPH_UPDATE]") >= 2, (
            "Template must include at least 2 [GRAPH_UPDATE] examples (BAD + GOOD)"
        )

    def test_template_has_sparse_entity_bad_example(self) -> None:
        """Template should show what a sparse entity looks like (to avoid)."""
        # Should mention sparse or minimal properties as antipattern
        template_lower = AGENT_TEMPLATE.lower()
        has_sparse_warning = any(
            phrase in template_lower
            for phrase in ["sparse", "too few properties", "minimal properties"]
        )
        assert has_sparse_warning, (
            "Template must warn about sparse entities with minimal properties"
        )

    def test_template_has_low_confidence_bad_example(self) -> None:
        """Template should show what low confidence without evidence looks like."""
        template_lower = AGENT_TEMPLATE.lower()
        has_confidence_warning = any(
            phrase in template_lower
            for phrase in [
                "low confidence",
                "confidence: 0.5",
                "confidence: 0.6",
                "confidence: 0.7",
            ]
        )
        assert has_confidence_warning, (
            "Template must show low confidence example as antipattern"
        )

    def test_template_has_missing_evidence_bad_example(self) -> None:
        """Template should show what missing evidence looks like."""
        # Look for example without evidence or with weak evidence
        template_lower = AGENT_TEMPLATE.lower()
        has_evidence_warning = any(
            phrase in template_lower
            for phrase in [
                "missing evidence",
                'evidence: ""',
                "evidence: (empty)",
                "no evidence",
            ]
        )
        assert has_evidence_warning, (
            "Template must show missing evidence example as antipattern"
        )

    def test_template_has_pre_output_checklist(self) -> None:
        """Agents should have a checklist to verify before outputting updates."""
        template_lower = AGENT_TEMPLATE.lower()

        # Check for checklist section
        has_checklist_section = any(
            phrase in template_lower
            for phrase in [
                "checklist",
                "before outputting",
                "quality standards",
                "verify:",
            ]
        )
        assert has_checklist_section, (
            "Template must include pre-output quality checklist"
        )

        # Check for specific quality criteria
        assert "3+ properties" in AGENT_TEMPLATE or "at least 3" in template_lower, (
            "Checklist must mention 3+ properties requirement"
        )

        assert "0.85" in AGENT_TEMPLATE or "confidence" in template_lower, (
            "Checklist must mention confidence threshold"
        )

        assert "evidence" in template_lower, (
            "Checklist must mention evidence requirement"
        )

    def test_template_does_not_reference_manual_km_commands(self) -> None:
        """Agents should NOT be told to check km_status.md or run KM commands."""
        template_lower = AGENT_TEMPLATE.lower()

        # Should NOT mention these manual KM activities
        forbidden_phrases = [
            "check km_status.md",
            "read km_status.md",
            "/km-status",
            "/enrich-knowledge",
            "/validate-knowledge",
            "run /km",
        ]

        for phrase in forbidden_phrases:
            assert phrase not in template_lower, (
                f"Template must NOT tell agents to '{phrase}' - "
                "KM is automatic, not manual"
            )

    def test_template_has_output_quality_standards_section(self) -> None:
        """Template should have dedicated section explaining quality standards."""
        # Look for section header
        has_quality_section = any(
            phrase in AGENT_TEMPLATE
            for phrase in [
                "## Output Quality Standards",
                "## Quality Standards",
                "## Graph Update Quality",
            ]
        )
        assert has_quality_section, (
            "Template must have 'Output Quality Standards' section"
        )

    def test_template_explains_confidence_scoring(self) -> None:
        """Template should explain how to score confidence appropriately."""
        template_lower = AGENT_TEMPLATE.lower()

        # Should explain confidence levels
        has_confidence_guidance = (
            "0.90" in AGENT_TEMPLATE
            or "0.95" in AGENT_TEMPLATE
            or "high confidence" in template_lower
        )
        assert has_confidence_guidance, (
            "Template must explain confidence scoring (0.90-0.95 for verified claims)"
        )

    def test_template_shows_strong_evidence_examples(self) -> None:
        """Template should show what strong evidence looks like."""
        # Should have examples with file:line or specific citations
        has_strong_evidence = any(
            pattern in AGENT_TEMPLATE
            for pattern in [
                "file:line",
                ".py:",
                ".js:",
                "src/",
                "line ",
                "commit ",
            ]
        )
        assert has_strong_evidence, (
            "Template must show examples of strong evidence (file:line, URLs, etc.)"
        )

    def test_template_emphasizes_prevention_over_detection(self) -> None:
        """Template should focus on producing quality, not checking for issues."""
        template_lower = AGENT_TEMPLATE.lower()

        # Should emphasize creation of quality
        quality_phrases = [
            "produce",
            "create",
            "generate",
            "high-quality",
            "comprehensive",
        ]
        quality_count = sum(phrase in template_lower for phrase in quality_phrases)

        # Should NOT emphasize checking/fixing
        checking_phrases = ["check for issues", "fix issues", "detect problems"]
        checking_count = sum(phrase in template_lower for phrase in checking_phrases)

        assert quality_count > checking_count, (
            "Template should emphasize quality production over issue detection"
        )


class TestTemplateIntegration:
    """Test that template can be formatted and used."""

    def test_template_can_be_formatted(self) -> None:
        """Template should have all necessary placeholders."""
        required_placeholders = [
            "{agent_name}",
            "{triad_name}",
            "{role_type}",
            "{agent_title}",
        ]

        for placeholder in required_placeholders:
            assert placeholder in AGENT_TEMPLATE, (
                f"Template must include {placeholder} placeholder"
            )

    def test_formatted_template_produces_valid_markdown(self) -> None:
        """Formatted template should produce valid markdown."""
        # Format with test values (all required placeholders)
        formatted = AGENT_TEMPLATE.format(
            agent_name="test-agent",
            triad_name="test",
            role_type="specialist",
            agent_title="Test Agent",
            expertise="Testing expertise",
            responsibility="Test responsibilities",
            position_description="First agent in test triad",
            constitutional_principles="Test principles",
            peer_agents="Test peers",
            bridge_instructions="",
            workflow_steps="Test workflow",
            tools_description="Test tools",
            handoff_description="Test handoff",
            example_interaction="Test example",
            confidence_threshold="0.85",
            additional_reminders="",
        )

        # Should have YAML frontmatter
        assert formatted.startswith("---"), "Formatted template must have frontmatter"

        # Should have proper sections
        assert "# Test Agent" in formatted, "Must have agent title"
        assert "## Identity" in formatted or "## Purpose" in formatted, (
            "Must have identity/purpose section"
        )

    def test_template_length_is_reasonable(self) -> None:
        """Template should be comprehensive but not overwhelming."""
        # Count lines
        line_count = len(AGENT_TEMPLATE.split("\n"))

        # Should be substantial (has examples, checklist, etc.)
        assert line_count > 100, (
            "Template should be comprehensive (>100 lines with examples)"
        )

        # But not excessively long (agents need to read it)
        assert line_count < 500, (
            "Template should be concise (<500 lines for agent readability)"
        )


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
