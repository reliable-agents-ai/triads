"""Unit tests for GitRunner - unified git command execution.

Tests cover:
- run() method with success/failure/timeout
- get_user_name() and get_user_email()
- diff_numstat() parsing
- diff_name_only() file listing
- ls_files_untracked() file listing
- Error handling and edge cases
"""

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from triads.workflow_enforcement.git_utils import (
    GitRunner,
    GitCommandResult,
    GitCommandError,
)


class TestGitCommandResult:
    """Test GitCommandResult dataclass."""

    def test_result_fields(self):
        """Test GitCommandResult has expected fields."""
        result = GitCommandResult(
            success=True,
            stdout="output",
            stderr="",
            returncode=0
        )

        assert result.success is True
        assert result.stdout == "output"
        assert result.stderr == ""
        assert result.returncode == 0


class TestGitRunnerRun:
    """Test GitRunner.run() method."""

    @patch("subprocess.run")
    def test_run_success(self, mock_run):
        """Test successful git command execution."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "success output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        result = GitRunner.run(["status"])

        assert result.success is True
        assert result.stdout == "success output"
        assert result.stderr == ""
        assert result.returncode == 0

        # Verify git was called correctly
        mock_run.assert_called_once_with(
            ["git", "status"],
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )

    @patch("subprocess.run")
    def test_run_with_custom_timeout(self, mock_run):
        """Test run with custom timeout."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        GitRunner.run(["diff"], timeout=60)

        # Verify timeout was passed
        assert mock_run.call_args[1]["timeout"] == 60

    @patch("subprocess.run")
    def test_run_with_check_false(self, mock_run):
        """Test run with check=False."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "error"
        mock_run.return_value = mock_result

        result = GitRunner.run(["status"], check=False)

        assert result.success is False
        assert result.returncode == 1
        assert mock_run.call_args[1]["check"] is False

    @patch("subprocess.run")
    def test_run_failure_raises_error(self, mock_run):
        """Test failed command raises GitCommandError."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, ["git", "status"], stderr="command failed"
        )

        with pytest.raises(GitCommandError) as exc_info:
            GitRunner.run(["status"])

        assert "Git command failed" in str(exc_info.value)
        assert "git status" in str(exc_info.value)
        assert "Exit code: 1" in str(exc_info.value)

    @patch("subprocess.run")
    def test_run_timeout_raises_error(self, mock_run):
        """Test command timeout raises GitCommandError."""
        mock_run.side_effect = subprocess.TimeoutExpired(["git", "diff"], 30)

        with pytest.raises(GitCommandError) as exc_info:
            GitRunner.run(["diff"])

        assert "timed out after 30s" in str(exc_info.value)
        assert "git diff" in str(exc_info.value)

    @patch("subprocess.run")
    def test_run_multiple_args(self, mock_run):
        """Test run with multiple command arguments."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        GitRunner.run(["diff", "--numstat", "HEAD~1"])

        # Verify all args passed
        mock_run.assert_called_once_with(
            ["git", "diff", "--numstat", "HEAD~1"],
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )


class TestGetUserName:
    """Test GitRunner.get_user_name()."""

    @patch("subprocess.run")
    def test_get_user_name_success(self, mock_run):
        """Test getting git user name."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "John Doe\n"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        name = GitRunner.get_user_name()

        assert name == "John Doe"
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_get_user_name_empty_returns_unknown(self, mock_run):
        """Test empty user name returns 'unknown'."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "\n"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        name = GitRunner.get_user_name()

        assert name == "unknown"

    @patch("subprocess.run")
    def test_get_user_name_error_returns_unknown(self, mock_run):
        """Test error returns 'unknown'."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, ["git", "config", "user.name"]
        )

        name = GitRunner.get_user_name()

        assert name == "unknown"

    @patch("subprocess.run")
    def test_get_user_name_whitespace_trimmed(self, mock_run):
        """Test whitespace is trimmed from user name."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "  John Doe  \n"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        name = GitRunner.get_user_name()

        assert name == "John Doe"


class TestGetUserEmail:
    """Test GitRunner.get_user_email()."""

    @patch("subprocess.run")
    def test_get_user_email_success(self, mock_run):
        """Test getting git user email."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "john@example.com\n"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        email = GitRunner.get_user_email()

        assert email == "john@example.com"

    @patch("subprocess.run")
    def test_get_user_email_empty_returns_unknown(self, mock_run):
        """Test empty email returns 'unknown'."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        email = GitRunner.get_user_email()

        assert email == "unknown"

    @patch("subprocess.run")
    def test_get_user_email_error_returns_unknown(self, mock_run):
        """Test error returns 'unknown'."""
        mock_run.side_effect = GitCommandError("Config not found")

        email = GitRunner.get_user_email()

        assert email == "unknown"


class TestDiffNumstat:
    """Test GitRunner.diff_numstat()."""

    @patch("subprocess.run")
    def test_diff_numstat_basic(self, mock_run):
        """Test parsing basic numstat output."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "10\t5\tsrc/file1.py\n20\t10\tsrc/file2.py\n"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        changes = GitRunner.diff_numstat("HEAD~1")

        assert len(changes) == 2
        assert changes[0] == (10, 5, "src/file1.py")
        assert changes[1] == (20, 10, "src/file2.py")

    @patch("subprocess.run")
    def test_diff_numstat_with_binary_files(self, mock_run):
        """Test binary files are skipped."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "10\t5\tfile.py\n-\t-\timage.png\n15\t3\tscript.py\n"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        changes = GitRunner.diff_numstat("HEAD~1")

        # Binary file should be skipped
        assert len(changes) == 2
        assert changes[0] == (10, 5, "file.py")
        assert changes[1] == (15, 3, "script.py")

    @patch("subprocess.run")
    def test_diff_numstat_empty(self, mock_run):
        """Test empty diff output."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        changes = GitRunner.diff_numstat("HEAD~1")

        assert changes == []

    @patch("subprocess.run")
    def test_diff_numstat_with_invalid_lines(self, mock_run):
        """Test invalid lines are skipped."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = (
            "10\t5\tvalid.py\n"
            "invalid line\n"
            "notanumber\t5\tbad.py\n"
            "15\t3\tgood.py\n"
        )
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        changes = GitRunner.diff_numstat("HEAD~1")

        # Only valid lines parsed
        assert len(changes) == 2
        assert changes[0] == (10, 5, "valid.py")
        assert changes[1] == (15, 3, "good.py")

    @patch("subprocess.run")
    def test_diff_numstat_custom_ref(self, mock_run):
        """Test numstat with custom base reference."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "10\t5\tfile.py\n"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        GitRunner.diff_numstat("origin/main")

        # Verify correct ref passed
        mock_run.assert_called_once_with(
            ["git", "diff", "--numstat", "origin/main"],
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )

    @patch("subprocess.run")
    def test_diff_numstat_failure(self, mock_run):
        """Test diff failure raises error."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, ["git", "diff"], stderr="invalid ref"
        )

        with pytest.raises(GitCommandError):
            GitRunner.diff_numstat("invalid-ref")

    @patch("subprocess.run")
    def test_diff_numstat_timeout(self, mock_run):
        """Test diff timeout raises error."""
        mock_run.side_effect = subprocess.TimeoutExpired(["git", "diff"], 30)

        with pytest.raises(GitCommandError) as exc_info:
            GitRunner.diff_numstat("HEAD~1", timeout=30)

        assert "timed out" in str(exc_info.value)


class TestDiffNameOnly:
    """Test GitRunner.diff_name_only()."""

    @patch("subprocess.run")
    def test_diff_name_only_basic(self, mock_run):
        """Test getting list of changed files."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "src/file1.py\nsrc/file2.py\nREADME.md\n"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        files = GitRunner.diff_name_only("HEAD~1")

        assert len(files) == 3
        assert files == ["src/file1.py", "src/file2.py", "README.md"]

    @patch("subprocess.run")
    def test_diff_name_only_empty(self, mock_run):
        """Test empty diff returns empty list."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        files = GitRunner.diff_name_only("HEAD~1")

        assert files == []

    @patch("subprocess.run")
    def test_diff_name_only_with_empty_lines(self, mock_run):
        """Test empty lines are filtered."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "file1.py\n\nfile2.py\n\n"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        files = GitRunner.diff_name_only("HEAD~1")

        assert len(files) == 2
        assert files == ["file1.py", "file2.py"]

    @patch("subprocess.run")
    def test_diff_name_only_failure(self, mock_run):
        """Test diff failure raises error."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, ["git", "diff"]
        )

        with pytest.raises(GitCommandError):
            GitRunner.diff_name_only("HEAD~1")


class TestLsFilesUntracked:
    """Test GitRunner.ls_files_untracked()."""

    @patch("subprocess.run")
    def test_ls_files_untracked_basic(self, mock_run):
        """Test getting list of untracked files."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "new_file.py\ntemporary.txt\n"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        files = GitRunner.ls_files_untracked()

        assert len(files) == 2
        assert files == ["new_file.py", "temporary.txt"]

    @patch("subprocess.run")
    def test_ls_files_untracked_empty(self, mock_run):
        """Test no untracked files returns empty list."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        files = GitRunner.ls_files_untracked()

        assert files == []

    @patch("subprocess.run")
    def test_ls_files_untracked_excludes_ignored(self, mock_run):
        """Test --exclude-standard is used."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "file.py\n"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        GitRunner.ls_files_untracked()

        # Verify --exclude-standard was passed
        mock_run.assert_called_once_with(
            ["git", "ls-files", "--others", "--exclude-standard"],
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )

    @patch("subprocess.run")
    def test_ls_files_untracked_failure(self, mock_run):
        """Test ls-files failure raises error."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, ["git", "ls-files"]
        )

        with pytest.raises(GitCommandError):
            GitRunner.ls_files_untracked()


class TestGitCommandError:
    """Test GitCommandError exception."""

    def test_error_message(self):
        """Test error message is preserved."""
        error = GitCommandError("Test error message")
        assert str(error) == "Test error message"

    def test_error_inheritance(self):
        """Test GitCommandError inherits from Exception."""
        assert issubclass(GitCommandError, Exception)
