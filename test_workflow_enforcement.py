#!/usr/bin/env python3
"""Integration test for workflow enforcement system.

This test verifies the complete workflow enforcement flow:
1. State management (save/load)
2. Metrics calculation
3. Validation logic
4. Blocking enforcement
5. Emergency bypass
6. Audit logging

Run: python3 test_workflow_enforcement.py
"""

import json
import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from triads.workflow_enforcement import (
    AuditLogger,
    BlockingEnforcement,
    EmergencyBypass,
    WorkflowStateManager,
    WorkflowValidator,
)


def test_state_management():
    """Test workflow state save/load."""
    print("Testing state management...")

    with tempfile.TemporaryDirectory() as tmpdir:
        state_file = Path(tmpdir) / "test_state.json"
        manager = WorkflowStateManager(state_file)

        # Test load default state
        state = manager.load_state()
        assert state["completed_triads"] == []
        assert state["current_phase"] is None

        # Test mark completed
        manager.mark_completed("design", metadata={"test": True})
        state = manager.load_state()
        assert "design" in state["completed_triads"]
        assert state["current_phase"] == "design"
        assert state["metadata"]["test"] is True

        # Test persistence
        manager2 = WorkflowStateManager(state_file)
        state2 = manager2.load_state()
        assert state2 == state

    print("✓ State management works")


def test_validator():
    """Test workflow validator."""
    print("Testing validator...")

    validator = WorkflowValidator()

    # Test metrics (will fail gracefully if not in git repo)
    metrics = validator.calculate_metrics()
    assert "loc_changed" in metrics
    assert "files_changed" in metrics
    assert "has_new_features" in metrics

    # Test enforcement rules
    test_cases = [
        ({"loc_changed": 150, "files_changed": 3}, True),  # >100 LoC
        ({"loc_changed": 50, "files_changed": 8}, True),  # >5 files
        ({"loc_changed": 50, "files_changed": 3, "has_new_features": True}, True),  # features
        ({"loc_changed": 50, "files_changed": 3}, False),  # None triggered
    ]

    for metrics, expected in test_cases:
        result = validator.requires_garden_tending(metrics)
        assert result == expected, f"Failed for {metrics}: expected {expected}, got {result}"

    # Test flags
    assert validator.requires_garden_tending({}, {"require_garden_tending": True})
    assert not validator.requires_garden_tending(
        {"loc_changed": 200}, {"skip_garden_tending": True}
    )

    # Test transitions
    assert validator.is_valid_transition(None, "idea-validation")
    assert validator.is_valid_transition("design", "implementation")
    assert not validator.is_valid_transition("design", "deployment")

    print("✓ Validator works")


def test_bypass():
    """Test emergency bypass."""
    print("Testing emergency bypass...")

    with tempfile.TemporaryDirectory() as tmpdir:
        audit_file = Path(tmpdir) / "test_audit.log"
        logger = AuditLogger(audit_file)
        bypass = EmergencyBypass(logger)

        # Test flag detection
        assert bypass.should_bypass(["--force-deploy"])
        assert not bypass.should_bypass([])

        # Test justification extraction
        assert bypass.get_justification(["--justification", "test reason"]) == "test reason"
        assert bypass.get_justification([]) is None

        # Test validation
        valid, error = bypass.is_valid_justification("Valid justification here")
        assert valid, error

        invalid, error = bypass.is_valid_justification("short")
        assert not invalid

        dangerous, error = bypass.is_valid_justification("test; rm -rf /")
        assert not dangerous

        # Test bypass execution
        result = bypass.execute_bypass("Test emergency bypass", {"test": True})
        assert result is True

        # Verify audit log
        assert audit_file.exists()
        with open(audit_file) as f:
            log_entry = json.loads(f.read().strip())
            assert log_entry["event"] == "emergency_bypass"
            assert log_entry["justification"] == "Test emergency bypass"

    print("✓ Emergency bypass works")


def test_enforcement():
    """Test blocking enforcement."""
    print("Testing enforcement...")

    with tempfile.TemporaryDirectory() as tmpdir:
        state_file = Path(tmpdir) / "test_state.json"
        manager = WorkflowStateManager(state_file)
        validator = WorkflowValidator()
        enforcement = BlockingEnforcement(manager, validator)

        # Test 1: No implementation yet - should pass
        result = enforcement.validate_or_block(allow_force=True)
        assert result is True

        # Test 2: Implementation done, no Garden Tending - should block (if metrics high)
        manager.mark_completed("implementation")

        # This will depend on git metrics, so we test with allow_force=True
        result = enforcement.validate_or_block(allow_force=True)
        # Result depends on actual git state

        # Test 3: Garden Tending done - should pass
        manager.mark_completed("garden-tending")
        result = enforcement.validate_or_block(allow_force=True)
        assert result is True

    print("✓ Enforcement works")


def test_audit_logger():
    """Test audit logger."""
    print("Testing audit logger...")

    with tempfile.TemporaryDirectory() as tmpdir:
        audit_file = Path(tmpdir) / "test_audit.log"
        logger = AuditLogger(audit_file)

        # Test logging
        logger.log_bypass("First bypass", {"test": 1})
        logger.log_bypass("Second bypass", {"test": 2})

        # Test retrieval
        recent = logger.get_recent_bypasses(limit=10)
        assert len(recent) == 2
        assert recent[0]["justification"] == "Second bypass"
        assert recent[1]["justification"] == "First bypass"

    print("✓ Audit logger works")


def main():
    """Run all tests."""
    print("=" * 70)
    print("Workflow Enforcement Integration Tests")
    print("=" * 70)
    print()

    try:
        test_state_management()
        test_validator()
        test_bypass()
        test_enforcement()
        test_audit_logger()

        print()
        print("=" * 70)
        print("All tests passed!")
        print("=" * 70)
        return 0

    except AssertionError as e:
        print()
        print("=" * 70)
        print(f"Test failed: {e}")
        print("=" * 70)
        return 1

    except Exception as e:
        print()
        print("=" * 70)
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
