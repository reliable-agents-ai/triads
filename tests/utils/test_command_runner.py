"""Tests for CommandRunner utility."""

import subprocess
from unittest.mock import Mock, patch
import pytest

from triads.utils.command_runner import CommandRunner, CommandResult


class TestCommandRunner:
    """Test CommandRunner class."""

    def test_run_success(self):
        """Test successful command execution."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="output",
                stderr="",
            )

            result = CommandRunner.run(["echo", "test"])

            assert result.success is True
            assert result.stdout == "output"
            assert result.stderr == ""
            assert result.returncode == 0

            # Verify subprocess.run called correctly
            mock_run.assert_called_once()
            call_args = mock_run.call_args
            assert call_args[0][0] == ["echo", "test"]
            assert call_args[1]["capture_output"] is True
            assert call_args[1]["text"] is True

    def test_run_with_timeout(self):
        """Test timeout parameter."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

            CommandRunner.run(["sleep", "1"], timeout=5)

            call_args = mock_run.call_args
            assert call_args[1]["timeout"] == 5

    def test_run_timeout_expired(self):
        """Test timeout exception handling."""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired("cmd", 10)

            with pytest.raises(TimeoutError, match="timed out after 10s"):
                CommandRunner.run(["sleep", "100"], timeout=10)

    def test_run_command_failed_check_true(self):
        """Test command failure with check=True raises exception."""
        with patch('subprocess.run') as mock_run:
            error = subprocess.CalledProcessError(returncode=1, cmd=["false"])
            error.stdout = ""
            error.stderr = "error"
            mock_run.side_effect = error

            with pytest.raises(subprocess.CalledProcessError):
                CommandRunner.run(["false"], check=True)

    def test_run_command_failed_check_false(self):
        """Test command failure with check=False returns result."""
        with patch('subprocess.run') as mock_run:
            error = subprocess.CalledProcessError(returncode=1, cmd=["false"])
            error.stdout = ""
            error.stderr = "error"
            mock_run.side_effect = error

            result = CommandRunner.run(["false"], check=False)

            assert result.success is False
            assert result.returncode == 1
            assert result.stderr == "error"

    def test_run_with_cwd(self):
        """Test cwd parameter."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

            CommandRunner.run(["ls"], cwd="/tmp")

            call_args = mock_run.call_args
            assert call_args[1]["cwd"] == "/tmp"

    def test_run_git_convenience(self):
        """Test run_git() convenience method."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                returncode=0, stdout="main\n", stderr=""
            )

            result = CommandRunner.run_git(["branch", "--show-current"])

            assert result.success is True
            assert result.stdout == "main\n"

            # Verify git was prepended
            call_args = mock_run.call_args
            assert call_args[0][0] == ["git", "branch", "--show-current"]

    def test_run_claude_convenience(self):
        """Test run_claude() convenience method."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout='{"result": "ok"}',
                stderr=""
            )

            result = CommandRunner.run_claude(["-p", "test", "--output-format", "json"])

            assert result.success is True
            assert "result" in result.stdout

            # Verify claude was prepended
            call_args = mock_run.call_args
            assert call_args[0][0] == ["claude", "-p", "test", "--output-format", "json"]

    def test_default_timeout(self):
        """Test default timeout is 30 seconds."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

            CommandRunner.run(["echo", "test"])

            call_args = mock_run.call_args
            assert call_args[1]["timeout"] == 30

    def test_run_git_with_custom_timeout(self):
        """Test run_git() respects custom timeout."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

            CommandRunner.run_git(["status"], timeout=5)

            call_args = mock_run.call_args
            assert call_args[1]["timeout"] == 5

    def test_run_git_with_cwd(self):
        """Test run_git() respects cwd parameter."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

            CommandRunner.run_git(["status"], cwd="/tmp")

            call_args = mock_run.call_args
            assert call_args[1]["cwd"] == "/tmp"

    def test_run_git_with_check_false(self):
        """Test run_git() respects check=False parameter."""
        with patch('subprocess.run') as mock_run:
            error = subprocess.CalledProcessError(returncode=1, cmd=["git", "status"])
            error.stdout = ""
            error.stderr = "error"
            mock_run.side_effect = error

            result = CommandRunner.run_git(["status"], check=False)

            assert result.success is False
            assert result.returncode == 1

    def test_run_claude_with_timeout(self):
        """Test run_claude() respects timeout parameter."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                returncode=0, stdout='{"result": "ok"}', stderr=""
            )

            CommandRunner.run_claude(["-p", "test"], timeout=60)

            call_args = mock_run.call_args
            assert call_args[1]["timeout"] == 60

    def test_command_result_dataclass(self):
        """Test CommandResult dataclass structure."""
        result = CommandResult(
            success=True,
            stdout="output",
            stderr="",
            returncode=0
        )

        assert result.success is True
        assert result.stdout == "output"
        assert result.stderr == ""
        assert result.returncode == 0

    def test_run_with_none_timeout_uses_default(self):
        """Test that timeout=None uses DEFAULT_TIMEOUT."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

            CommandRunner.run(["echo", "test"], timeout=None)

            call_args = mock_run.call_args
            assert call_args[1]["timeout"] == CommandRunner.DEFAULT_TIMEOUT

    def test_run_preserves_stdout_on_error_when_check_false(self):
        """Test that stdout is preserved when command fails with check=False."""
        with patch('subprocess.run') as mock_run:
            error = subprocess.CalledProcessError(returncode=1, cmd=["false"])
            error.stdout = "partial output"
            error.stderr = "error"
            mock_run.side_effect = error

            result = CommandRunner.run(["false"], check=False)

            assert result.stdout == "partial output"
            assert result.stderr == "error"
