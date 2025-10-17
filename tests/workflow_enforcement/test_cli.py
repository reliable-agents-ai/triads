"""Tests for workflow enforcement CLI functions.

Tests cover all CLI functions:
- list_workflows(base_dir=test_workflows_dir): List workflow instances
- show_workflow(): Show instance details
- resume_workflow(): Resume guidance
- workflow_history(): Deviation history
- abandon_workflow(): Abandon instance
- analyze_deviations(base_dir=test_workflows_dir): Deviation analytics
"""

import json
import pytest
from pathlib import Path
from datetime import datetime

from triads.workflow_enforcement.cli import (
    list_workflows,
    show_workflow,
    resume_workflow,
    workflow_history,
    abandon_workflow,
    analyze_deviations,
)
from triads.workflow_enforcement.instance_manager import WorkflowInstanceManager


@pytest.fixture
def test_workflows_dir(tmp_path):
    """Create temporary workflows directory."""
    workflows_dir = tmp_path / ".claude" / "workflows"
    workflows_dir.mkdir(parents=True)
    return workflows_dir


@pytest.fixture
def manager(test_workflows_dir):
    """Create instance manager with test directory."""
    return WorkflowInstanceManager(base_dir=test_workflows_dir)


@pytest.fixture
def sample_instance(manager):
    """Create a sample workflow instance for testing."""
    instance_id = manager.create_instance(
        workflow_type="software-development",
        title="OAuth2 Integration",
        user="test@example.com"
    )

    # Add some progress
    manager.mark_triad_completed(instance_id, "idea-validation", duration_minutes=9.6)
    manager.mark_triad_completed(instance_id, "design", duration_minutes=15.3)

    # Add a deviation
    manager.add_deviation(instance_id, {
        "type": "skip_forward",
        "from_triad": "idea-validation",
        "to_triad": "implementation",
        "skipped": ["design"],
        "reason": "Design completed in Figma",
        "user": "test@example.com"
    })

    # Update current triad
    manager.update_instance(instance_id, {
        "workflow_progress": {"current_triad": "implementation"}
    })

    return instance_id


@pytest.fixture
def workflow_schema(test_workflows_dir):
    """Create a sample workflow schema."""
    schema_file = test_workflows_dir.parent / "workflow.json"
    schema_data = {
        "workflow_name": "software-development",
        "version": "1.0.0",
        "enforcement": {
            "mode": "recommended"
        },
        "triads": [
            {"id": "idea-validation", "name": "Idea Validation", "type": "research", "required": True},
            {"id": "design", "name": "Design", "type": "planning", "required": True},
            {"id": "implementation", "name": "Implementation", "type": "execution", "required": True},
            {"id": "garden-tending", "name": "Garden Tending", "type": "quality", "required": True},
            {"id": "deployment", "name": "Deployment", "type": "release", "required": True},
        ],
        "workflow_rules": [
            {
                "rule_type": "sequential_progression",
                "description": "Triads should be completed in order",
                "track_deviations": True
            }
        ]
    }

    with open(schema_file, "w") as f:
        json.dump(schema_data, f, indent=2)

    return schema_file


class TestListWorkflows:
    """Tests for list_workflows function."""

    def test_list_workflows_empty(self, manager, test_workflows_dir):
        """Test listing workflows when none exist."""
        output = list_workflows(base_dir=test_workflows_dir)
        assert "No workflow instances found" in output

    def test_list_workflows_single(self, manager, sample_instance, test_workflows_dir):
        """Test listing single workflow instance."""
        output = list_workflows(base_dir=test_workflows_dir)

        assert "Found 1 workflow instance(s)" in output
        assert sample_instance in output
        assert "OAuth2 Integration" in output
        assert "in_progress" in output
        assert "implementation" in output

    def test_list_workflows_multiple(self, manager, test_workflows_dir):
        """Test listing multiple workflow instances."""
        # Create multiple instances
        id1 = manager.create_instance("software-development", "OAuth2", "user1@example.com")
        id2 = manager.create_instance("software-development", "Payments", "user2@example.com")
        id3 = manager.create_instance("rfp-writing", "Acme Corp RFP", "user3@example.com")

        output = list_workflows(base_dir=test_workflows_dir)

        assert "Found 3 workflow instance(s)" in output
        assert id1 in output
        assert id2 in output
        assert id3 in output
        assert "OAuth2" in output
        assert "Payments" in output
        assert "Acme Corp RFP" in output

    def test_list_workflows_by_status_in_progress(self, manager, sample_instance, test_workflows_dir):
        """Test filtering by in_progress status."""
        # Create a completed instance
        id2 = manager.create_instance("software-development", "Completed Work", "user@example.com")
        manager.complete_instance(id2)

        output = list_workflows(status="in_progress", base_dir=test_workflows_dir)

        assert "Found 1 workflow instance(s)" in output
        assert sample_instance in output
        assert id2 not in output

    def test_list_workflows_by_status_completed(self, manager, sample_instance, test_workflows_dir):
        """Test filtering by completed status."""
        # Complete the sample instance
        manager.complete_instance(sample_instance)

        output = list_workflows(status="completed", base_dir=test_workflows_dir)

        assert "Found 1 workflow instance(s)" in output
        assert sample_instance in output

    def test_list_workflows_by_status_abandoned(self, manager, test_workflows_dir):
        """Test filtering by abandoned status."""
        # Create and abandon an instance
        instance_id = manager.create_instance("software-development", "Abandoned Work", "user@example.com")
        manager.abandon_instance(instance_id, "No longer needed")

        output = list_workflows(status="abandoned", base_dir=test_workflows_dir)

        assert "Found 1 workflow instance(s)" in output
        assert instance_id in output

    def test_list_workflows_invalid_status(self, manager, test_workflows_dir):
        """Test handling invalid status filter."""
        output = list_workflows(status="invalid_status", base_dir=test_workflows_dir)
        assert "Error:" in output
        assert "Invalid status" in output

    def test_list_workflows_sorts_by_date(self, manager, test_workflows_dir):
        """Test that workflows are sorted by start date (most recent first)."""
        # Create instances with slight delay
        import time

        id1 = manager.create_instance("software-development", "First", "user@example.com")
        time.sleep(0.01)
        id2 = manager.create_instance("software-development", "Second", "user@example.com")
        time.sleep(0.01)
        id3 = manager.create_instance("software-development", "Third", "user@example.com")

        output = list_workflows(base_dir=test_workflows_dir)

        # Check that most recent appears first
        lines = output.split("\n")
        id1_line = next(i for i, line in enumerate(lines) if id1 in line)
        id2_line = next(i for i, line in enumerate(lines) if id2 in line)
        id3_line = next(i for i, line in enumerate(lines) if id3 in line)

        assert id3_line < id2_line < id1_line

    def test_list_workflows_pagination_first_page(self, manager, test_workflows_dir):
        """Test pagination - first page."""
        # Create 10 instances
        for i in range(10):
            manager.create_instance("software-development", f"Feature {i}", "user@example.com")

        output = list_workflows(limit=5, offset=0, base_dir=test_workflows_dir)

        assert "Showing 5 of 10 workflow instance(s)" in output
        assert "(5 more available)" in output
        assert "(skipped first" not in output

    def test_list_workflows_pagination_second_page(self, manager, test_workflows_dir):
        """Test pagination - second page."""
        # Create 10 instances
        for i in range(10):
            manager.create_instance("software-development", f"Feature {i}", "user@example.com")

        output = list_workflows(limit=5, offset=5, base_dir=test_workflows_dir)

        assert "Showing 5 of 10 workflow instance(s)" in output
        assert "(skipped first 5)" in output
        assert "more available" not in output

    def test_list_workflows_pagination_larger_than_total(self, manager, test_workflows_dir):
        """Test pagination with limit larger than total."""
        # Create 3 instances
        for i in range(3):
            manager.create_instance("software-development", f"Feature {i}", "user@example.com")

        output = list_workflows(limit=10, offset=0, base_dir=test_workflows_dir)

        assert "Showing 3 of 3 workflow instance(s)" in output
        assert "more available" not in output
        assert "skipped" not in output

    def test_list_workflows_pagination_offset_beyond_total(self, manager, test_workflows_dir):
        """Test pagination with offset beyond total."""
        # Create 3 instances
        for i in range(3):
            manager.create_instance("software-development", f"Feature {i}", "user@example.com")

        output = list_workflows(limit=5, offset=10, base_dir=test_workflows_dir)

        assert "Showing 0 of 3 workflow instance(s)" in output
        assert "(skipped first 10)" in output


class TestInputValidation:
    """Tests for input validation in CLI functions."""

    def test_show_workflow_invalid_instance_id_empty(self, test_workflows_dir):
        """Test show_workflow with empty instance ID."""
        output = show_workflow("", base_dir=test_workflows_dir)
        assert "Error: Valid instance ID required" in output

    def test_show_workflow_invalid_instance_id_none(self, test_workflows_dir):
        """Test show_workflow with None instance ID."""
        output = show_workflow(None, base_dir=test_workflows_dir)
        assert "Error: Valid instance ID required" in output

    def test_resume_workflow_invalid_instance_id_empty(self, test_workflows_dir):
        """Test resume_workflow with empty instance ID."""
        output = resume_workflow("", base_dir=test_workflows_dir)
        assert "Error: Valid instance ID required" in output

    def test_workflow_history_invalid_instance_id_empty(self, test_workflows_dir):
        """Test workflow_history with empty instance ID."""
        output = workflow_history("", base_dir=test_workflows_dir)
        assert "Error: Valid instance ID required" in output

    def test_abandon_workflow_invalid_instance_id_empty(self, test_workflows_dir):
        """Test abandon_workflow with empty instance ID."""
        output = abandon_workflow("", "reason", base_dir=test_workflows_dir)
        assert "Error: Valid instance ID required" in output

    def test_abandon_workflow_invalid_reason_empty(self, test_workflows_dir):
        """Test abandon_workflow with empty reason."""
        output = abandon_workflow("some-id", "", base_dir=test_workflows_dir)
        assert "Error: Reason required for abandoning workflow" in output

    def test_abandon_workflow_invalid_reason_none(self, test_workflows_dir):
        """Test abandon_workflow with None reason."""
        output = abandon_workflow("some-id", None, base_dir=test_workflows_dir)
        assert "Error: Reason required for abandoning workflow" in output

    def test_list_workflows_invalid_status(self, test_workflows_dir):
        """Test list_workflows with invalid status."""
        output = list_workflows(status="invalid_status", base_dir=test_workflows_dir)
        assert "Error: Invalid status 'invalid_status'" in output
        assert "Must be one of: in_progress, completed, abandoned" in output


class TestShowWorkflow:
    """Tests for show_workflow function."""

    def test_show_workflow_basic(self, manager, sample_instance, test_workflows_dir):
        """Test showing basic workflow information."""
        output = show_workflow(sample_instance, base_dir=test_workflows_dir)

        assert sample_instance in output
        assert "OAuth2 Integration" in output
        assert "software-development" in output
        assert "in_progress" in output
        assert "test@example.com" in output

    def test_show_workflow_progress(self, manager, sample_instance, test_workflows_dir):
        """Test showing workflow progress."""
        output = show_workflow(sample_instance, base_dir=test_workflows_dir)

        assert "Progress:" in output
        assert "Current triad: implementation" in output
        assert "Completed: 2 triad(s)" in output
        assert "Deviations: 1" in output

    def test_show_workflow_completed_triads(self, manager, sample_instance, test_workflows_dir):
        """Test showing completed triads."""
        output = show_workflow(sample_instance, base_dir=test_workflows_dir)

        assert "Completed Triads:" in output
        assert "✓ idea-validation (9.6 minutes)" in output
        assert "✓ design (15.3 minutes)" in output

    def test_show_workflow_deviations(self, manager, sample_instance, test_workflows_dir):
        """Test showing workflow deviations."""
        output = show_workflow(sample_instance, base_dir=test_workflows_dir)

        assert "Workflow Deviations:" in output
        assert "skip_forward" in output
        assert "Design completed in Figma" in output
        assert "idea-validation → implementation" in output
        assert "Skipped: design" in output

    def test_show_workflow_not_found(self, manager, test_workflows_dir):
        """Test showing non-existent workflow."""
        output = show_workflow("nonexistent-instance", base_dir=test_workflows_dir)
        assert "Error:" in output
        assert "not found" in output.lower()

    def test_show_workflow_with_metrics(self, manager, sample_instance, test_workflows_dir):
        """Test showing workflow with significance metrics."""
        # Add metrics
        manager.update_instance(sample_instance, {
            "significance_metrics": {
                "content_created": {"type": "code", "quantity": 257, "units": "lines"},
                "components_modified": 8,
                "complexity": "substantial"
            }
        })

        output = show_workflow(sample_instance, base_dir=test_workflows_dir)

        assert "Significance Metrics:" in output
        assert "Content: 257 lines" in output
        assert "Components: 8" in output
        assert "Complexity: substantial" in output

    def test_show_workflow_no_progress(self, manager, test_workflows_dir, workflow_schema):
        """Test showing workflow with no progress yet."""
        instance_id = manager.create_instance("software-development", "New Workflow", "user@example.com")

        output = show_workflow(instance_id, base_dir=test_workflows_dir)

        assert "Current triad: Not started" in output
        assert "Completed: 0 triad(s)" in output


class TestResumeWorkflow:
    """Tests for resume_workflow function."""

    def test_resume_workflow_not_started(self, manager, test_workflows_dir, workflow_schema):
        """Test resuming workflow that hasn't started."""
        instance_id = manager.create_instance("software-development", "New Work", "user@example.com")

        output = resume_workflow(instance_id, base_dir=test_workflows_dir, schema_file=workflow_schema)

        assert "Workflow not yet started" in output
        assert "Start idea-validation" in output

    def test_resume_workflow_in_progress(self, manager, sample_instance, test_workflows_dir, workflow_schema):
        """Test resuming workflow in progress."""
        output = resume_workflow(sample_instance, base_dir=test_workflows_dir, schema_file=workflow_schema)

        assert "Resuming workflow: OAuth2 Integration" in output
        assert "Current triad: implementation" in output
        assert "Progress: 2/5 triads completed" in output
        assert "Continue with current: Start implementation" in output
        assert "Or proceed to next: Start garden-tending" in output

    def test_resume_workflow_final_triad(self, manager, test_workflows_dir, workflow_schema):
        """Test resuming workflow on final triad."""
        instance_id = manager.create_instance("software-development", "Final Stage", "user@example.com")

        # Mark all triads except last as completed
        manager.mark_triad_completed(instance_id, "idea-validation")
        manager.mark_triad_completed(instance_id, "design")
        manager.mark_triad_completed(instance_id, "implementation")
        manager.mark_triad_completed(instance_id, "garden-tending")
        manager.update_instance(instance_id, {
            "workflow_progress": {"current_triad": "deployment"}
        })

        output = resume_workflow(instance_id, base_dir=test_workflows_dir, schema_file=workflow_schema)

        assert "Final triad: Start deployment" in output
        assert "After completion, workflow will be complete!" in output

    def test_resume_workflow_not_found(self, manager, test_workflows_dir, workflow_schema):
        """Test resuming non-existent workflow."""
        output = resume_workflow("nonexistent-instance", base_dir=test_workflows_dir, schema_file=workflow_schema)
        assert "Error:" in output
        assert "not found" in output.lower()


class TestWorkflowHistory:
    """Tests for workflow_history function."""

    def test_workflow_history_basic(self, manager, sample_instance, test_workflows_dir):
        """Test viewing basic deviation history."""
        output = workflow_history(sample_instance, base_dir=test_workflows_dir)

        assert "Deviation History: OAuth2 Integration" in output
        assert "Total deviations: 1" in output

    def test_workflow_history_by_type(self, manager, sample_instance, test_workflows_dir):
        """Test deviation grouping by type."""
        # Add more deviations
        manager.add_deviation(sample_instance, {
            "type": "skip_forward",
            "from_triad": "design",
            "to_triad": "deployment",
            "reason": "Skipping implementation"
        })
        manager.add_deviation(sample_instance, {
            "type": "skip_backward",
            "from_triad": "implementation",
            "to_triad": "design",
            "reason": "Found design flaw"
        })

        output = workflow_history(sample_instance, base_dir=test_workflows_dir)

        assert "By Type:" in output
        assert "skip_forward: 2" in output
        assert "skip_backward: 1" in output

    def test_workflow_history_chronological(self, manager, sample_instance, test_workflows_dir):
        """Test chronological deviation listing."""
        output = workflow_history(sample_instance, base_dir=test_workflows_dir)

        assert "Chronological History:" in output
        assert "1. [" in output
        assert "skip_forward" in output
        assert "idea-validation → implementation" in output
        assert "Reason: Design completed in Figma" in output

    def test_workflow_history_no_deviations(self, manager, test_workflows_dir):
        """Test history for workflow with no deviations."""
        instance_id = manager.create_instance("software-development", "Clean Work", "user@example.com")

        output = workflow_history(instance_id, base_dir=test_workflows_dir)

        assert "No deviations recorded" in output
        assert "Clean Work" in output

    def test_workflow_history_not_found(self, manager, test_workflows_dir):
        """Test history for non-existent workflow."""
        output = workflow_history("nonexistent-instance", base_dir=test_workflows_dir)
        assert "Error:" in output
        assert "not found" in output.lower()


class TestAbandonWorkflow:
    """Tests for abandon_workflow function."""

    def test_abandon_workflow_basic(self, manager, sample_instance, test_workflows_dir):
        """Test abandoning a workflow."""
        output = abandon_workflow(sample_instance, "Project cancelled", base_dir=test_workflows_dir)

        assert "✓ Workflow abandoned" in output
        assert sample_instance in output
        assert "OAuth2 Integration" in output
        assert "Project cancelled" in output
        assert "abandoned/" in output

        # Verify instance was moved to abandoned directory
        instance = manager.load_instance(sample_instance)
        assert instance.metadata["status"] == "abandoned"
        assert instance.metadata["abandon_reason"] == "Project cancelled"

    def test_abandon_workflow_no_reason(self, manager, sample_instance, test_workflows_dir):
        """Test abandoning without reason fails."""
        output = abandon_workflow(sample_instance, "", base_dir=test_workflows_dir)
        assert "Error:" in output
        assert "Reason required" in output

    def test_abandon_workflow_not_found(self, manager, test_workflows_dir):
        """Test abandoning non-existent workflow."""
        output = abandon_workflow("nonexistent-instance", "Some reason", base_dir=test_workflows_dir)
        assert "Error:" in output
        assert "not found" in output.lower()


class TestAnalyzeDeviations:
    """Tests for analyze_deviations function."""

    def test_analyze_deviations_empty(self, manager, test_workflows_dir):
        """Test analyzing when no workflows exist."""
        output = analyze_deviations(base_dir=test_workflows_dir)
        assert "No workflow instances found" in output

    def test_analyze_deviations_basic(self, manager, sample_instance, test_workflows_dir):
        """Test basic deviation analytics."""
        output = analyze_deviations(base_dir=test_workflows_dir)

        assert "Workflow Deviation Analytics" in output
        assert "Total Instances: 1" in output
        assert "Instances with Deviations: 1 (100.0%)" in output
        assert "Total Deviations: 1" in output

    def test_analyze_deviations_by_type(self, manager, test_workflows_dir):
        """Test deviation type aggregation."""
        # Create multiple instances with different deviation types
        for i in range(3):
            instance_id = manager.create_instance("software-development", f"Work {i}", "user@example.com")
            manager.add_deviation(instance_id, {
                "type": "skip_forward",
                "from_triad": "design",
                "to_triad": "implementation",
                "reason": f"Reason {i}"
            })

        for i in range(2):
            instance_id = manager.create_instance("software-development", f"Work skip_back {i}", "user@example.com")
            manager.add_deviation(instance_id, {
                "type": "skip_backward",
                "from_triad": "implementation",
                "to_triad": "design",
                "reason": f"Reason {i}"
            })

        output = analyze_deviations(base_dir=test_workflows_dir)

        assert "Deviation Types:" in output
        assert "skip_forward: 3 (60.0%)" in output
        assert "skip_backward: 2 (40.0%)" in output

    def test_analyze_deviations_most_skipped(self, manager, test_workflows_dir):
        """Test most skipped triads analysis."""
        # Create instances that skip design
        for i in range(3):
            instance_id = manager.create_instance("software-development", f"Work {i}", "user@example.com")
            manager.add_deviation(instance_id, {
                "type": "skip_forward",
                "from_triad": "idea-validation",
                "to_triad": "implementation",
                "skipped": ["design"],
                "reason": "Design done externally"
            })

        # Create instance that skips garden-tending
        for i in range(2):
            instance_id = manager.create_instance("software-development", f"Work gt {i}", "user@example.com")
            manager.add_deviation(instance_id, {
                "type": "skip_forward",
                "from_triad": "implementation",
                "to_triad": "deployment",
                "skipped": ["garden-tending"],
                "reason": "No time"
            })

        output = analyze_deviations(base_dir=test_workflows_dir)

        assert "Most Skipped Triads:" in output
        assert "design: 3 times" in output
        assert "garden-tending: 2 times" in output

    def test_analyze_deviations_reason_keywords(self, manager, test_workflows_dir):
        """Test common reason keyword extraction."""
        # Create instances with common keywords in reasons
        keywords = ["completed", "external", "figma", "meeting"]
        for i, keyword in enumerate(keywords):
            instance_id = manager.create_instance("software-development", f"Work {i}", "user@example.com")
            manager.add_deviation(instance_id, {
                "type": "skip_forward",
                "from_triad": "design",
                "to_triad": "implementation",
                "reason": f"Design {keyword} separately"
            })

        output = analyze_deviations(base_dir=test_workflows_dir)

        assert "Common Reason Keywords:" in output
        # At least one keyword should appear
        assert any(kw in output for kw in keywords)

    def test_analyze_deviations_recommendations(self, manager, test_workflows_dir):
        """Test that recommendations are generated."""
        # Create instances with many skip_forward deviations
        for i in range(5):
            instance_id = manager.create_instance("software-development", f"Work {i}", "user@example.com")
            manager.add_deviation(instance_id, {
                "type": "skip_forward",
                "from_triad": "idea-validation",
                "to_triad": "implementation",
                "skipped": ["design"],
                "reason": "Design done externally"
            })

        output = analyze_deviations(base_dir=test_workflows_dir)

        assert "Recommendations:" in output
        assert "frequently skipped" in output or "skip_forward" in output


class TestIntegration:
    """Integration tests for CLI workflow."""

    def test_full_workflow_lifecycle(self, manager, test_workflows_dir, workflow_schema):
        """Test complete workflow lifecycle through CLI."""
        # 1. Create instance (not through CLI, but simulates workflow start)
        instance_id = manager.create_instance(
            "software-development",
            "Full Lifecycle Test",
            "user@example.com"
        )

        # 2. List workflows
        output = list_workflows(base_dir=test_workflows_dir)
        assert instance_id in output
        assert "Full Lifecycle Test" in output

        # 3. Resume (should suggest first triad)
        output = resume_workflow(instance_id, base_dir=test_workflows_dir, schema_file=workflow_schema)
        assert "Workflow not yet started" in output
        assert "Start idea-validation" in output

        # 4. Complete first triad
        manager.mark_triad_completed(instance_id, "idea-validation", duration_minutes=10.0)
        manager.update_instance(instance_id, {
            "workflow_progress": {"current_triad": "design"}
        })

        # 5. Show progress
        output = show_workflow(instance_id, base_dir=test_workflows_dir)
        assert "Completed: 1 triad(s)" in output
        assert "✓ idea-validation (10.0 minutes)" in output

        # 6. Add deviation
        manager.add_deviation(instance_id, {
            "type": "skip_forward",
            "from_triad": "design",
            "to_triad": "implementation",
            "skipped": ["design"],
            "reason": "Design completed in Figma"
        })

        # 7. View history
        output = workflow_history(instance_id, base_dir=test_workflows_dir)
        assert "Total deviations: 1" in output
        assert "skip_forward: 1" in output

        # 8. Analyze patterns
        output = analyze_deviations(base_dir=test_workflows_dir)
        assert "Total Instances: 1" in output
        assert "Total Deviations: 1" in output

        # 9. Abandon workflow
        output = abandon_workflow(instance_id, "Test complete", base_dir=test_workflows_dir)
        assert "✓ Workflow abandoned" in output

        # 10. Verify abandoned
        output = list_workflows(status="abandoned", base_dir=test_workflows_dir)
        assert instance_id in output

    def test_multiple_workflows_analysis(self, manager, test_workflows_dir):
        """Test analyzing patterns across multiple workflows."""
        # Create diverse set of workflows
        workflows = []

        # 3 workflows with skip_forward to implementation
        for i in range(3):
            instance_id = manager.create_instance("software-development", f"Skip Design {i}", "user@example.com")
            manager.add_deviation(instance_id, {
                "type": "skip_forward",
                "from_triad": "idea-validation",
                "to_triad": "implementation",
                "skipped": ["design"],
                "reason": "Design completed externally"
            })
            workflows.append(instance_id)

        # 2 workflows with skip_backward
        for i in range(2):
            instance_id = manager.create_instance("software-development", f"Back to Design {i}", "user@example.com")
            manager.add_deviation(instance_id, {
                "type": "skip_backward",
                "from_triad": "implementation",
                "to_triad": "design",
                "reason": "Found design flaw"
            })
            workflows.append(instance_id)

        # 1 workflow with no deviations
        instance_id = manager.create_instance("software-development", "Clean Flow", "user@example.com")
        workflows.append(instance_id)

        # Analyze
        output = analyze_deviations(base_dir=test_workflows_dir)

        assert "Total Instances: 6" in output
        assert "Instances with Deviations: 5 (83.3%)" in output
        assert "Total Deviations: 5" in output
        assert "skip_forward: 3 (60.0%)" in output
        assert "skip_backward: 2 (40.0%)" in output
        assert "Most Skipped Triads:" in output
        assert "design: 3 times" in output


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_show_workflow_malformed_data(self, manager, sample_instance, test_workflows_dir):
        """Test handling workflow with malformed data gracefully."""
        # This should not crash even if some data is missing
        manager.update_instance(sample_instance, {
            "workflow_progress": {"current_triad": None}
        })

        output = show_workflow(sample_instance, base_dir=test_workflows_dir)
        assert "Workflow Instance:" in output
        # Should show "Not started" for None current_triad
        assert "Current triad:" in output

    def test_list_workflows_with_corrupted_file(self, manager, test_workflows_dir):
        """Test that corrupted files are skipped gracefully."""
        # Create a valid instance
        instance_id = manager.create_instance("software-development", "Valid", "user@example.com")

        # Create a corrupted JSON file
        corrupt_file = test_workflows_dir / "instances" / "corrupted.json"
        corrupt_file.write_text("{ invalid json ]}")

        # Should still list valid instance
        output = list_workflows(base_dir=test_workflows_dir)
        assert instance_id in output
        assert "Valid" in output

    def test_analyze_deviations_with_missing_fields(self, manager, test_workflows_dir):
        """Test analyze handles deviations with missing fields."""
        instance_id = manager.create_instance("software-development", "Test", "user@example.com")

        # Add deviation with missing type
        manager.add_deviation(instance_id, {
            "from_triad": "design",
            "to_triad": "implementation",
            "reason": "Some reason"
        })

        # Should not crash
        output = analyze_deviations(base_dir=test_workflows_dir)
        assert "Total Instances: 1" in output
        assert "Total Deviations: 1" in output
