"""Integration tests for workflow enforcement system.

Tests full workflow scenarios:
- Design → Implementation → Garden Tending → Deployment
- Bypass workflow with audit trail
- Blocking when GT required but not done
- State persistence across workflow phases
- Agent integrations
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from triads.workflow_enforcement import (
    AuditLogger,
    BlockingEnforcement,
    EmergencyBypass,
    WorkflowStateManager,
    WorkflowValidator,
    check_bypass,
    validate_deployment,
)


@pytest.fixture
def temp_workflow_dir():
    """Create temporary directory for workflow state and audit logs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def workflow_manager(temp_workflow_dir):
    """Create WorkflowStateManager with temp directory."""
    state_file = temp_workflow_dir / "workflow_state.json"
    return WorkflowStateManager(state_file)


@pytest.fixture
def audit_logger(temp_workflow_dir):
    """Create AuditLogger with temp directory."""
    audit_file = temp_workflow_dir / "workflow_audit.log"
    return AuditLogger(audit_file)


class TestCompleteWorkflow:
    """Test complete workflow from design to deployment."""

    @patch("triads.workflow_enforcement.validator.subprocess.run")
    def test_full_workflow_low_changes(
        self, mock_run, workflow_manager, temp_workflow_dir
    ):
        """Test full workflow with low changes (no GT required)."""
        # Mock git available with low metrics
        mock_rev_parse = MagicMock()
        mock_rev_parse.returncode = 0

        mock_diff = MagicMock()
        mock_diff.returncode = 0
        mock_diff.stdout = "10\t5\tfile.py\n"  # 15 LoC, 1 file

        mock_status = MagicMock()
        mock_status.returncode = 0
        mock_status.stdout = "M\tfile.py"

        mock_run.side_effect = [mock_rev_parse, mock_diff, mock_status]

        # Phase 1: Complete design
        workflow_manager.mark_completed("design")
        state = workflow_manager.load_state()
        assert "design" in state["completed_triads"]

        # Phase 2: Complete implementation
        workflow_manager.mark_completed("implementation")
        state = workflow_manager.load_state()
        assert "implementation" in state["completed_triads"]

        # Phase 3: Validate deployment (should pass - low changes)
        validator = WorkflowValidator()
        enforcement = BlockingEnforcement(workflow_manager, validator)

        result = enforcement.validate_or_block(allow_force=True)
        assert result is True  # Should pass without GT

    @patch("triads.workflow_enforcement.validator.subprocess.run")
    def test_full_workflow_high_changes_requires_gt(
        self, mock_run, workflow_manager
    ):
        """Test full workflow with high changes (GT required)."""
        # Mock git available with high metrics
        def mock_git_calls(*args, **kwargs):
            cmd = args[0]
            if "rev-parse" in cmd:
                result = MagicMock()
                result.returncode = 0
                return result
            elif "numstat" in cmd:
                result = MagicMock()
                result.returncode = 0
                # High LoC
                result.stdout = "\n".join([f"{i*10}\t{i*5}\tfile{i}.py" for i in range(20)])
                return result
            else:
                result = MagicMock()
                result.returncode = 0
                result.stdout = "M\tfile.py"
                return result

        mock_run.side_effect = mock_git_calls

        # Phase 1: Complete implementation
        workflow_manager.mark_completed("implementation")

        # Phase 2: Try to deploy (should block)
        validator = WorkflowValidator()
        enforcement = BlockingEnforcement(workflow_manager, validator)

        result = enforcement.validate_or_block(allow_force=True)
        assert result is False  # Should block

        # Phase 3: Complete Garden Tending
        workflow_manager.mark_completed("garden-tending")

        # Phase 4: Deploy again (should pass)
        result = enforcement.validate_or_block(allow_force=True)
        assert result is True

    def test_workflow_state_persistence(self, workflow_manager, temp_workflow_dir):
        """Test state persists across manager instances."""
        # Create state with first instance
        workflow_manager.mark_completed("design")
        workflow_manager.mark_completed("implementation")

        # Create second instance with same file
        state_file = temp_workflow_dir / "workflow_state.json"
        manager2 = WorkflowStateManager(state_file)

        # Verify state persisted
        state = manager2.load_state()
        assert "design" in state["completed_triads"]
        assert "implementation" in state["completed_triads"]

    def test_workflow_with_metadata_tracking(self, workflow_manager):
        """Test metadata is tracked through workflow phases."""
        # Design phase with metadata
        workflow_manager.mark_completed("design", metadata={"approved_by": "user"})

        # Implementation phase with additional metadata
        workflow_manager.mark_completed(
            "implementation", metadata={"loc_added": 150}
        )

        state = workflow_manager.load_state()
        assert state["metadata"]["approved_by"] == "user"
        assert state["metadata"]["loc_added"] == 150


class TestBypassWorkflow:
    """Test emergency bypass workflow."""

    def test_bypass_with_audit_trail(self, workflow_manager, audit_logger):
        """Test bypass creates audit trail."""
        # Setup: Implementation done, GT required
        workflow_manager.mark_completed("implementation")

        # Bypass deployment
        bypass = EmergencyBypass(audit_logger)
        justification = "Critical hotfix for production bug #1234"
        result = bypass.execute_bypass(justification, metadata={"critical": True})

        assert result is True

        # Verify audit trail
        recent = audit_logger.get_recent_bypasses()
        assert len(recent) == 1
        assert recent[0]["justification"] == justification
        assert recent[0]["metadata"]["critical"] is True

    def test_bypass_full_flow(self, workflow_manager, audit_logger):
        """Test complete bypass flow from args to execution."""
        workflow_manager.mark_completed("implementation")

        args = [
            "--force-deploy",
            "--justification",
            "Emergency production hotfix",
        ]

        bypass = EmergencyBypass(audit_logger)
        result = bypass.validate_and_execute(args)

        assert result is True

        # Verify logged
        recent = audit_logger.get_recent_bypasses()
        assert len(recent) == 1

    def test_bypass_invalid_justification_blocks(self, audit_logger):
        """Test invalid bypass justification blocks deployment."""
        args = ["--force-deploy", "--justification", "short"]

        bypass = EmergencyBypass(audit_logger)

        with pytest.raises(SystemExit) as exc_info:
            bypass.validate_and_execute(args)

        assert exc_info.value.code == 1

        # Verify nothing logged
        recent = audit_logger.get_recent_bypasses()
        assert len(recent) == 0


class TestBlockingScenarios:
    """Test various blocking scenarios."""

    @patch("triads.workflow_enforcement.validator.subprocess.run")
    def test_blocks_when_gt_required_not_done(self, mock_run, workflow_manager):
        """Test blocking when GT required but not completed."""
        # Mock high metrics
        def mock_git_calls(*args, **kwargs):
            cmd = args[0]
            if "rev-parse" in cmd:
                result = MagicMock()
                result.returncode = 0
                return result
            elif "numstat" in cmd:
                result = MagicMock()
                result.returncode = 0
                result.stdout = "\n".join([f"50\t50\tfile{i}.py" for i in range(3)])
                return result
            else:
                result = MagicMock()
                result.returncode = 0
                result.stdout = "M\tfile.py"
                return result

        mock_run.side_effect = mock_git_calls

        # Implementation done, no GT
        workflow_manager.mark_completed("implementation")

        validator = WorkflowValidator()
        enforcement = BlockingEnforcement(workflow_manager, validator)

        result = enforcement.validate_or_block(allow_force=True)
        assert result is False

    def test_allows_when_gt_completed(self, workflow_manager):
        """Test allows deployment when GT completed."""
        workflow_manager.mark_completed("implementation")
        workflow_manager.mark_completed("garden-tending")

        validator = WorkflowValidator()
        enforcement = BlockingEnforcement(workflow_manager, validator)

        result = enforcement.validate_or_block(allow_force=True)
        assert result is True

    def test_allows_when_no_implementation_yet(self, workflow_manager):
        """Test allows deployment when implementation not started."""
        workflow_manager.mark_completed("design")

        validator = WorkflowValidator()
        enforcement = BlockingEnforcement(workflow_manager, validator)

        result = enforcement.validate_or_block(allow_force=True)
        assert result is True


class TestPublicAPIIntegration:
    """Test public API functions."""

    @patch("triads.workflow_enforcement.enforcement.BlockingEnforcement")
    def test_validate_deployment_function(self, mock_enforcement_class):
        """Test validate_deployment() convenience function."""
        mock_enforcement = MagicMock()
        mock_enforcement.validate_or_block.return_value = True
        mock_enforcement_class.return_value = mock_enforcement

        result = validate_deployment()

        assert result is True
        mock_enforcement.validate_or_block.assert_called_once()

    @patch("triads.workflow_enforcement.bypass.EmergencyBypass")
    def test_check_bypass_function(self, mock_bypass_class):
        """Test check_bypass() convenience function."""
        mock_bypass = MagicMock()
        mock_bypass.validate_and_execute.return_value = True
        mock_bypass_class.return_value = mock_bypass

        args = ["--force-deploy", "--justification", "Test"]
        result = check_bypass(args)

        assert result is True
        mock_bypass.validate_and_execute.assert_called_once_with(args)


class TestAgentIntegration:
    """Test integration with agent workflows."""

    @patch("triads.workflow_enforcement.validator.subprocess.run")
    def test_design_bridge_to_implementation(self, mock_run, workflow_manager):
        """Test design-bridge marks design complete."""
        # Simulate design-bridge completing design phase
        workflow_manager.mark_completed("design", metadata={"adr_count": 3})

        state = workflow_manager.load_state()
        assert "design" in state["completed_triads"]
        assert state["current_phase"] == "design"
        assert state["metadata"]["adr_count"] == 3

    @patch("triads.workflow_enforcement.validator.subprocess.run")
    def test_gardener_bridge_to_deployment(self, mock_run, workflow_manager):
        """Test gardener-bridge marks GT complete."""
        # Simulate implementation → garden-tending
        workflow_manager.mark_completed("implementation")
        workflow_manager.mark_completed(
            "garden-tending", metadata={"refactored_files": 5}
        )

        state = workflow_manager.load_state()
        assert "garden-tending" in state["completed_triads"]

    @patch("triads.workflow_enforcement.validator.subprocess.run")
    def test_release_manager_validation(self, mock_run, workflow_manager):
        """Test release-manager validates before deployment."""
        # Mock low metrics
        mock_rev_parse = MagicMock()
        mock_rev_parse.returncode = 0

        mock_diff = MagicMock()
        mock_diff.returncode = 0
        mock_diff.stdout = "5\t5\tfile.py\n"

        mock_status = MagicMock()
        mock_status.returncode = 0
        mock_status.stdout = "M\tfile.py"

        mock_run.side_effect = [mock_rev_parse, mock_diff, mock_status]

        # Simulate release-manager workflow
        workflow_manager.mark_completed("implementation")

        validator = WorkflowValidator()
        enforcement = BlockingEnforcement(workflow_manager, validator)

        # Should pass (low changes)
        result = enforcement.validate_or_block(allow_force=True)
        assert result is True


class TestErrorRecovery:
    """Test error recovery scenarios."""

    def test_recovery_from_corrupted_state(self, temp_workflow_dir):
        """Test recovery when state file corrupted."""
        state_file = temp_workflow_dir / "workflow_state.json"

        # Create corrupted state
        state_file.write_text("{ corrupted json")

        # Should recover gracefully
        manager = WorkflowStateManager(state_file)
        state = manager.load_state()

        assert state["completed_triads"] == []
        assert state["current_phase"] is None

    def test_recovery_from_missing_audit_log(self, temp_workflow_dir):
        """Test recovery when audit log missing."""
        audit_file = temp_workflow_dir / "audit.log"

        logger = AuditLogger(audit_file)
        recent = logger.get_recent_bypasses()

        # Should return empty list instead of crashing
        assert recent == []

    def test_state_survives_concurrent_writes(self, workflow_manager):
        """Test state integrity with concurrent operations."""
        import threading

        errors = []

        def mark_phase(phase):
            try:
                workflow_manager.mark_completed(phase)
            except Exception as e:
                errors.append(e)

        # Try to mark different phases concurrently
        phases = ["design", "implementation", "garden-tending"]
        threads = [threading.Thread(target=mark_phase, args=(p,)) for p in phases]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # No errors should occur
        assert len(errors) == 0

        # All phases should be present
        state = workflow_manager.load_state()
        for phase in phases:
            assert phase in state["completed_triads"]


class TestComplexScenarios:
    """Test complex real-world scenarios."""

    @patch("triads.workflow_enforcement.validator.subprocess.run")
    def test_multiple_bypasses_tracked(self, mock_run, workflow_manager, audit_logger):
        """Test multiple bypasses are all tracked."""
        bypass = EmergencyBypass(audit_logger)

        # First bypass
        bypass.execute_bypass("Hotfix #1", metadata={"ticket": "BUG-001"})

        # Second bypass
        bypass.execute_bypass("Hotfix #2", metadata={"ticket": "BUG-002"})

        # Third bypass
        bypass.execute_bypass("Hotfix #3", metadata={"ticket": "BUG-003"})

        # Verify all tracked
        recent = audit_logger.get_recent_bypasses(limit=10)
        assert len(recent) == 3
        assert recent[0]["justification"] == "Hotfix #3"  # Most recent first
        assert recent[1]["justification"] == "Hotfix #2"
        assert recent[2]["justification"] == "Hotfix #1"

    @patch("triads.workflow_enforcement.validator.subprocess.run")
    def test_workflow_reset_after_deployment(self, mock_run, workflow_manager):
        """Test workflow can be reset after deployment."""
        # Complete workflow
        workflow_manager.mark_completed("design")
        workflow_manager.mark_completed("implementation")
        workflow_manager.mark_completed("garden-tending")

        # Reset for next cycle
        workflow_manager.clear_state()

        # Verify fresh state
        state = workflow_manager.load_state()
        assert state["completed_triads"] == []
        assert state["current_phase"] is None

    @patch("triads.workflow_enforcement.validator.subprocess.run")
    def test_partial_workflow_completion(self, mock_run, workflow_manager):
        """Test partial workflow states are valid."""
        # Only design completed
        workflow_manager.mark_completed("design")

        validator = WorkflowValidator()
        enforcement = BlockingEnforcement(workflow_manager, validator)

        # Should allow (no implementation yet)
        result = enforcement.validate_or_block(allow_force=True)
        assert result is True
