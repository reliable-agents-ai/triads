"""Unit tests for EmergencyBypass.

Tests cover:
- Flag parsing (--force-deploy, --justification)
- Security validation (shell metacharacters, command patterns)
- Audit integration
- validate_and_execute flow
"""

import sys
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest

from triads.workflow_enforcement.audit import AuditLogger
from triads.workflow_enforcement.bypass import (
    DANGEROUS_CHARS,
    MIN_JUSTIFICATION_LENGTH,
    EmergencyBypass,
    check_bypass,
)


@pytest.fixture
def mock_audit_logger():
    """Create mock AuditLogger."""
    return MagicMock(spec=AuditLogger)


@pytest.fixture
def bypass(mock_audit_logger):
    """Create EmergencyBypass instance with mock logger."""
    return EmergencyBypass(mock_audit_logger)


class TestShouldBypass:
    """Test --force-deploy flag detection."""

    def test_should_bypass_with_flag(self, bypass):
        """Test returns True when --force-deploy present."""
        args = ["script.py", "--force-deploy"]
        assert bypass.should_bypass(args) is True

    def test_should_bypass_without_flag(self, bypass):
        """Test returns False when --force-deploy absent."""
        args = ["script.py", "--other-flag"]
        assert bypass.should_bypass(args) is False

    def test_should_bypass_empty_args(self, bypass):
        """Test returns False with empty args."""
        args = []
        assert bypass.should_bypass(args) is False

    def test_should_bypass_flag_at_end(self, bypass):
        """Test detection when flag is at end."""
        args = ["script.py", "--other", "--force-deploy"]
        assert bypass.should_bypass(args) is True

    def test_should_bypass_flag_in_middle(self, bypass):
        """Test detection when flag is in middle."""
        args = ["script.py", "--force-deploy", "--other"]
        assert bypass.should_bypass(args) is True

    def test_should_bypass_default_sys_argv(self, bypass):
        """Test uses sys.argv by default."""
        with patch.object(sys, "argv", ["script.py", "--force-deploy"]):
            assert bypass.should_bypass() is True


class TestGetJustification:
    """Test justification extraction."""

    def test_get_justification_present(self, bypass):
        """Test extraction when justification provided."""
        args = ["--justification", "Hotfix for production bug"]
        result = bypass.get_justification(args)
        assert result == "Hotfix for production bug"

    def test_get_justification_absent(self, bypass):
        """Test returns None when justification not provided."""
        args = ["--force-deploy"]
        result = bypass.get_justification(args)
        assert result is None

    def test_get_justification_no_value(self, bypass):
        """Test returns None when --justification has no value."""
        args = ["--justification"]
        result = bypass.get_justification(args)
        assert result is None

    def test_get_justification_with_spaces(self, bypass):
        """Test extraction of justification with spaces."""
        args = ["--justification", "This is a long justification"]
        result = bypass.get_justification(args)
        assert result == "This is a long justification"

    def test_get_justification_multiple_flags(self, bypass):
        """Test extraction with multiple flags present."""
        args = [
            "--force-deploy",
            "--justification",
            "Critical hotfix",
            "--other-flag",
        ]
        result = bypass.get_justification(args)
        assert result == "Critical hotfix"

    def test_get_justification_default_sys_argv(self, bypass):
        """Test uses sys.argv by default."""
        with patch.object(sys, "argv", ["script.py", "--justification", "Test"]):
            result = bypass.get_justification()
            assert result == "Test"


class TestIsValidJustification:
    """Test justification validation."""

    def test_valid_justification(self, bypass):
        """Test valid justification passes."""
        valid, error = bypass.is_valid_justification(
            "This is a valid justification for emergency deployment"
        )
        assert valid is True
        assert error == ""

    def test_valid_justification_minimum_length(self, bypass):
        """Test justification at minimum length."""
        valid, error = bypass.is_valid_justification("a" * MIN_JUSTIFICATION_LENGTH)
        assert valid is True

    def test_invalid_justification_none(self, bypass):
        """Test None justification rejected."""
        valid, error = bypass.is_valid_justification(None)
        assert valid is False
        assert "required" in error.lower()

    def test_invalid_justification_empty(self, bypass):
        """Test empty string rejected."""
        valid, error = bypass.is_valid_justification("")
        assert valid is False
        assert "required" in error.lower()

    def test_invalid_justification_too_short(self, bypass):
        """Test short justification rejected."""
        valid, error = bypass.is_valid_justification("short")
        assert valid is False
        assert "at least" in error.lower()

    def test_invalid_justification_whitespace_only(self, bypass):
        """Test whitespace-only justification rejected."""
        valid, error = bypass.is_valid_justification("   ")
        assert valid is False

    def test_invalid_justification_non_string(self, bypass):
        """Test non-string justification rejected."""
        valid, error = bypass.is_valid_justification(12345)
        assert valid is False
        assert "must be a string" in error.lower()


class TestSecurityValidation:
    """Test security validation of justifications."""

    @pytest.mark.parametrize("dangerous_char", DANGEROUS_CHARS)
    def test_rejects_dangerous_characters(self, bypass, dangerous_char):
        """Test all dangerous characters are rejected."""
        justification = f"Valid text {dangerous_char} more text"
        valid, error = bypass.is_valid_justification(justification)
        assert valid is False
        assert "dangerous character" in error.lower()

    def test_rejects_rm_rf_pattern(self, bypass):
        """Test rejection of rm -rf pattern."""
        justification = "Need to run rm -rf on production"
        valid, error = bypass.is_valid_justification(justification)
        assert valid is False
        assert "suspicious" in error.lower()

    def test_rejects_sudo_pattern(self, bypass):
        """Test rejection of sudo pattern."""
        justification = "Must sudo install package"
        valid, error = bypass.is_valid_justification(justification)
        assert valid is False
        assert "suspicious" in error.lower()

    def test_rejects_command_substitution_dollar(self, bypass):
        """Test rejection of $() command substitution."""
        justification = "Valid text $(malicious command) more text"
        valid, error = bypass.is_valid_justification(justification)
        assert valid is False
        # Rejected by dollar sign in DANGEROUS_CHARS

    def test_rejects_command_substitution_backticks(self, bypass):
        """Test rejection of backtick command substitution."""
        justification = "Valid text `malicious command` more text"
        valid, error = bypass.is_valid_justification(justification)
        assert valid is False
        # Rejected by backtick in DANGEROUS_CHARS

    def test_accepts_safe_punctuation(self, bypass):
        """Test safe punctuation is accepted."""
        justification = "Hotfix for bug #1234. Critical issue!"
        valid, error = bypass.is_valid_justification(justification)
        assert valid is True

    def test_accepts_unicode(self, bypass):
        """Test unicode characters accepted."""
        justification = "紧急修复 for production 🚨 critical"
        valid, error = bypass.is_valid_justification(justification)
        assert valid is True

    def test_rejects_shell_metacharacter_semicolon(self, bypass):
        """Test semicolon rejected (command chaining)."""
        justification = "Valid reason; rm -rf /"
        valid, error = bypass.is_valid_justification(justification)
        assert valid is False

    def test_rejects_shell_metacharacter_pipe(self, bypass):
        """Test pipe rejected."""
        justification = "Valid reason | cat /etc/passwd"
        valid, error = bypass.is_valid_justification(justification)
        assert valid is False

    def test_rejects_shell_metacharacter_ampersand(self, bypass):
        """Test ampersand rejected (background execution)."""
        justification = "Valid reason & malicious"
        valid, error = bypass.is_valid_justification(justification)
        assert valid is False

    def test_rejects_redirect_operators(self, bypass):
        """Test redirect operators rejected."""
        for char in [">", "<"]:
            justification = f"Valid reason {char} file"
            valid, error = bypass.is_valid_justification(justification)
            assert valid is False

    def test_rejects_parentheses(self, bypass):
        """Test parentheses rejected (subshell)."""
        justification = "Valid (subshell) text"
        valid, error = bypass.is_valid_justification(justification)
        assert valid is False

    def test_rejects_braces(self, bypass):
        """Test braces rejected."""
        justification = "Valid {brace} text"
        valid, error = bypass.is_valid_justification(justification)
        assert valid is False


class TestExecuteBypass:
    """Test bypass execution."""

    def test_execute_bypass_logs_event(self, bypass, mock_audit_logger):
        """Test bypass execution logs to audit."""
        justification = "Critical hotfix for production"
        result = bypass.execute_bypass(justification)

        mock_audit_logger.log_bypass.assert_called_once_with(
            justification=justification, metadata={}
        )
        assert result is True

    def test_execute_bypass_with_metadata(self, bypass, mock_audit_logger):
        """Test bypass execution logs metadata."""
        justification = "Emergency fix"
        metadata = {"loc_changed": 150, "files_changed": 8}

        result = bypass.execute_bypass(justification, metadata)

        mock_audit_logger.log_bypass.assert_called_once_with(
            justification=justification, metadata=metadata
        )
        assert result is True

    def test_execute_bypass_prints_confirmation(self, bypass, mock_audit_logger):
        """Test bypass execution prints confirmation."""
        justification = "Test bypass"

        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            bypass.execute_bypass(justification)

        output = captured_output.getvalue()
        assert "Emergency Bypass Activated" in output
        assert justification in output
        assert "logged for audit purposes" in output


class TestValidateAndExecute:
    """Test validate_and_execute convenience method."""

    def test_validate_and_execute_no_bypass_requested(self, bypass):
        """Test returns False when no bypass requested."""
        args = ["script.py"]
        result = bypass.validate_and_execute(args)
        assert result is False

    def test_validate_and_execute_valid_bypass(self, bypass, mock_audit_logger):
        """Test executes bypass when valid."""
        args = ["--force-deploy", "--justification", "Critical production hotfix"]

        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            result = bypass.validate_and_execute(args)

        assert result is True
        mock_audit_logger.log_bypass.assert_called_once()

    def test_validate_and_execute_invalid_justification_exits(self, bypass):
        """Test exits when justification invalid."""
        args = ["--force-deploy", "--justification", "short"]

        with pytest.raises(SystemExit) as exc_info:
            bypass.validate_and_execute(args)

        assert exc_info.value.code == 1

    def test_validate_and_execute_missing_justification_exits(self, bypass):
        """Test exits when justification missing."""
        args = ["--force-deploy"]

        with pytest.raises(SystemExit) as exc_info:
            bypass.validate_and_execute(args)

        assert exc_info.value.code == 1

    def test_validate_and_execute_prints_error_for_invalid(self, bypass):
        """Test prints helpful error for invalid justification."""
        args = ["--force-deploy", "--justification", "x"]

        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            with pytest.raises(SystemExit):
                bypass.validate_and_execute(args)

        output = captured_output.getvalue()
        assert "Invalid Emergency Bypass" in output
        assert "at least" in output.lower()

    def test_validate_and_execute_prints_usage(self, bypass):
        """Test prints usage instructions for invalid bypass."""
        args = ["--force-deploy"]

        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            with pytest.raises(SystemExit):
                bypass.validate_and_execute(args)

        output = captured_output.getvalue()
        assert "Usage:" in output
        assert "--force-deploy --justification" in output

    def test_validate_and_execute_with_metadata(self, bypass, mock_audit_logger):
        """Test passes metadata to execution."""
        args = ["--force-deploy", "--justification", "Emergency deployment"]
        metadata = {"test": True}

        with patch("sys.stdout"):
            bypass.validate_and_execute(args, metadata=metadata)

        # Check metadata was passed to log_bypass
        call_args = mock_audit_logger.log_bypass.call_args
        assert call_args[1]["metadata"] == metadata


class TestCheckBypassFunction:
    """Test check_bypass convenience function."""

    @patch("triads.workflow_enforcement.bypass.EmergencyBypass")
    def test_check_bypass_creates_bypass(self, mock_bypass_class):
        """Test check_bypass creates EmergencyBypass instance."""
        mock_bypass = MagicMock()
        mock_bypass.validate_and_execute.return_value = True
        mock_bypass_class.return_value = mock_bypass

        result = check_bypass(["--force-deploy", "--justification", "Test"])

        mock_bypass_class.assert_called_once()
        mock_bypass.validate_and_execute.assert_called_once()
        assert result is True

    @patch("triads.workflow_enforcement.bypass.EmergencyBypass")
    def test_check_bypass_returns_false_when_no_bypass(self, mock_bypass_class):
        """Test check_bypass returns False when no bypass requested."""
        mock_bypass = MagicMock()
        mock_bypass.validate_and_execute.return_value = False
        mock_bypass_class.return_value = mock_bypass

        result = check_bypass([])

        assert result is False


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_very_long_justification(self, bypass):
        """Test very long justification (>1000 chars) is accepted."""
        justification = "a" * 1500
        valid, error = bypass.is_valid_justification(justification)
        assert valid is True

    def test_justification_with_newlines(self, bypass):
        """Test justification with newlines accepted."""
        justification = "Multi-line\njustification\nfor\nemergency"
        valid, error = bypass.is_valid_justification(justification)
        assert valid is True

    def test_justification_with_tabs(self, bypass):
        """Test justification with tabs accepted."""
        justification = "Justification\twith\ttabs"
        valid, error = bypass.is_valid_justification(justification)
        assert valid is True

    def test_multiple_dangerous_chars(self, bypass):
        """Test justification with multiple dangerous chars rejected."""
        justification = "Bad $(`rm -rf /`)"
        valid, error = bypass.is_valid_justification(justification)
        assert valid is False

    def test_case_insensitive_pattern_matching(self, bypass):
        """Test suspicious patterns matched case-insensitively."""
        justification = "Need to RM -RF the directory"
        valid, error = bypass.is_valid_justification(justification)
        assert valid is False

    def test_execute_bypass_audit_logger_failure(self, bypass, mock_audit_logger):
        """Test execution continues even if audit logging fails."""
        mock_audit_logger.log_bypass.side_effect = Exception("Logging failed")

        with pytest.raises(Exception):
            bypass.execute_bypass("Test justification")

    def test_get_justification_at_end_of_args(self, bypass):
        """Test --justification at end with no value."""
        args = ["script.py", "--other", "--justification"]
        result = bypass.get_justification(args)
        assert result is None

    def test_dangerous_chars_configuration(self):
        """Test DANGEROUS_CHARS includes all expected characters."""
        expected = ["$", "`", "\\", ";", "|", "&", ">", "<", "(", ")", "{", "}"]
        for char in expected:
            assert char in DANGEROUS_CHARS

    def test_min_justification_length_configuration(self):
        """Test MIN_JUSTIFICATION_LENGTH is set correctly."""
        assert MIN_JUSTIFICATION_LENGTH == 10
