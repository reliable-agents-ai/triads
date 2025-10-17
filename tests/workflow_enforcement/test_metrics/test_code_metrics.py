"""Tests for code metrics provider.

Tests cover:
- Git-based metrics calculation
- LoC counting (added/deleted)
- File change counting
- Complexity assessment
- Error handling (git failures, timeouts)
- Edge cases (empty diffs, binary files)
"""

import pytest
import subprocess
from unittest.mock import patch, MagicMock
from triads.workflow_enforcement.metrics.code_metrics import (
    CodeMetricsProvider,
    MetricsCalculationError,
)
from triads.workflow_enforcement.metrics.base import MetricsResult


class TestCodeMetricsProviderBasics:
    """Test basic CodeMetricsProvider functionality."""

    def test_domain_property(self):
        """Test domain property returns 'code'."""
        provider = CodeMetricsProvider()
        assert provider.domain == "code"

    def test_calculate_metrics_returns_metrics_result(self):
        """Test calculate_metrics returns MetricsResult."""
        provider = CodeMetricsProvider()

        with patch.object(provider, '_count_loc_changes', return_value=(100, 50)):
            with patch.object(provider, '_count_files_changed', return_value=5):
                result = provider.calculate_metrics({})

                assert isinstance(result, MetricsResult)

    def test_calculate_metrics_default_context(self):
        """Test calculate_metrics with default context."""
        provider = CodeMetricsProvider()

        with patch.object(provider, '_count_loc_changes', return_value=(50, 20)):
            with patch.object(provider, '_count_files_changed', return_value=3):
                result = provider.calculate_metrics({})

                # Should use HEAD~1 as default base_ref
                assert result.raw_data["base_ref"] == "HEAD~1"

    def test_calculate_metrics_custom_base_ref(self):
        """Test calculate_metrics with custom base_ref."""
        provider = CodeMetricsProvider()

        with patch.object(provider, '_count_loc_changes', return_value=(50, 20)):
            with patch.object(provider, '_count_files_changed', return_value=3):
                result = provider.calculate_metrics({"base_ref": "main"})

                assert result.raw_data["base_ref"] == "main"


class TestLocCounting:
    """Test lines of code counting logic."""

    def test_count_loc_changes_success(self):
        """Test successful LoC counting."""
        provider = CodeMetricsProvider()

        mock_output = "50\t20\tfile1.py\n30\t10\tfile2.py\n"
        mock_result = MagicMock()
        mock_result.stdout = mock_output
        mock_result.returncode = 0

        with patch('subprocess.run', return_value=mock_result):
            added, deleted = provider._count_loc_changes("HEAD~1")

            assert added == 80  # 50 + 30
            assert deleted == 30  # 20 + 10

    def test_count_loc_changes_empty_diff(self):
        """Test LoC counting with no changes."""
        provider = CodeMetricsProvider()

        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_result.returncode = 0

        with patch('subprocess.run', return_value=mock_result):
            added, deleted = provider._count_loc_changes("HEAD~1")

            assert added == 0
            assert deleted == 0

    def test_count_loc_changes_binary_files_ignored(self):
        """Test binary files are ignored (marked with '-')."""
        provider = CodeMetricsProvider()

        mock_output = "50\t20\tfile.py\n-\t-\timage.png\n30\t10\tscript.py\n"
        mock_result = MagicMock()
        mock_result.stdout = mock_output
        mock_result.returncode = 0

        with patch('subprocess.run', return_value=mock_result):
            added, deleted = provider._count_loc_changes("HEAD~1")

            # Should only count .py files
            assert added == 80
            assert deleted == 30

    def test_count_loc_changes_invalid_lines_skipped(self):
        """Test invalid lines are skipped gracefully."""
        provider = CodeMetricsProvider()

        mock_output = "50\t20\tfile.py\ninvalid_line\n30\t10\tscript.py\n"
        mock_result = MagicMock()
        mock_result.stdout = mock_output
        mock_result.returncode = 0

        with patch('subprocess.run', return_value=mock_result):
            added, deleted = provider._count_loc_changes("HEAD~1")

            # Should skip invalid line
            assert added == 80
            assert deleted == 30

    def test_count_loc_changes_git_error(self):
        """Test git command failure raises MetricsCalculationError."""
        provider = CodeMetricsProvider()

        with patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'git')):
            with pytest.raises(MetricsCalculationError, match="Failed to calculate git diff"):
                provider._count_loc_changes("HEAD~1")

    def test_count_loc_changes_timeout(self):
        """Test git timeout raises MetricsCalculationError."""
        provider = CodeMetricsProvider()

        with patch('subprocess.run', side_effect=subprocess.TimeoutExpired('git', 30)):
            with pytest.raises(MetricsCalculationError, match="Git diff timed out"):
                provider._count_loc_changes("HEAD~1")

    def test_count_loc_changes_uses_correct_git_command(self):
        """Test correct git command is used."""
        provider = CodeMetricsProvider()

        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_result.returncode = 0

        with patch('subprocess.run', return_value=mock_result) as mock_run:
            provider._count_loc_changes("main")

            # Check git command
            call_args = mock_run.call_args[0][0]
            assert call_args == ["git", "diff", "--numstat", "main"]

            # Check other parameters
            call_kwargs = mock_run.call_args[1]
            assert call_kwargs['capture_output'] is True
            assert call_kwargs['text'] is True
            assert call_kwargs['check'] is True
            assert call_kwargs['timeout'] == 30


class TestFileChangeCounting:
    """Test file change counting logic."""

    def test_count_files_changed_success(self):
        """Test successful file change counting."""
        provider = CodeMetricsProvider()

        mock_result = MagicMock()
        mock_result.stdout = "file1.py\nfile2.py\nfile3.py\n"
        mock_result.returncode = 0

        with patch('subprocess.run', return_value=mock_result):
            count = provider._count_files_changed("HEAD~1", include_untracked=False)

            assert count == 3

    def test_count_files_changed_empty(self):
        """Test file counting with no changes."""
        provider = CodeMetricsProvider()

        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_result.returncode = 0

        with patch('subprocess.run', return_value=mock_result):
            count = provider._count_files_changed("HEAD~1", include_untracked=False)

            assert count == 0

    def test_count_files_changed_with_untracked(self):
        """Test file counting includes untracked files."""
        provider = CodeMetricsProvider()

        def mock_run(cmd, **kwargs):
            mock_result = MagicMock()
            mock_result.returncode = 0

            if "ls-files" in cmd:
                # Untracked files
                mock_result.stdout = "new1.py\nnew2.py\n"
            else:
                # Changed files
                mock_result.stdout = "file1.py\nfile2.py\n"

            return mock_result

        with patch('subprocess.run', side_effect=mock_run):
            count = provider._count_files_changed("HEAD~1", include_untracked=True)

            # 2 changed + 2 untracked = 4
            assert count == 4

    def test_count_files_changed_without_untracked(self):
        """Test file counting excludes untracked files by default."""
        provider = CodeMetricsProvider()

        call_count = 0

        def mock_run(cmd, **kwargs):
            nonlocal call_count
            call_count += 1

            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "file1.py\nfile2.py\n"
            return mock_result

        with patch('subprocess.run', side_effect=mock_run):
            count = provider._count_files_changed("HEAD~1", include_untracked=False)

            # Should only call git once (for changed files, not untracked)
            assert call_count == 1
            assert count == 2

    def test_count_files_changed_git_error(self):
        """Test git error raises MetricsCalculationError."""
        provider = CodeMetricsProvider()

        with patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'git')):
            with pytest.raises(MetricsCalculationError, match="Failed to count changed files"):
                provider._count_files_changed("HEAD~1", include_untracked=False)

    def test_count_files_changed_timeout(self):
        """Test git timeout raises MetricsCalculationError."""
        provider = CodeMetricsProvider()

        with patch('subprocess.run', side_effect=subprocess.TimeoutExpired('git', 30)):
            with pytest.raises(MetricsCalculationError, match="Git file count timed out"):
                provider._count_files_changed("HEAD~1", include_untracked=False)


class TestComplexityAssessment:
    """Test complexity assessment logic."""

    def test_assess_complexity_minimal(self):
        """Test minimal complexity assessment."""
        provider = CodeMetricsProvider()

        # ≤30 LoC and ≤2 files = minimal
        assert provider._assess_complexity(10, 1) == "minimal"
        assert provider._assess_complexity(30, 2) == "minimal"
        assert provider._assess_complexity(5, 0) == "minimal"

    def test_assess_complexity_moderate(self):
        """Test moderate complexity assessment."""
        provider = CodeMetricsProvider()

        # >30 LoC or >2 files, but not substantial
        assert provider._assess_complexity(31, 1) == "moderate"
        assert provider._assess_complexity(50, 2) == "moderate"
        assert provider._assess_complexity(20, 3) == "moderate"
        assert provider._assess_complexity(100, 5) == "moderate"  # At threshold

    def test_assess_complexity_substantial(self):
        """Test substantial complexity assessment."""
        provider = CodeMetricsProvider()

        # >100 LoC or >5 files = substantial
        assert provider._assess_complexity(101, 1) == "substantial"
        assert provider._assess_complexity(200, 3) == "substantial"
        assert provider._assess_complexity(50, 6) == "substantial"
        assert provider._assess_complexity(101, 6) == "substantial"

    def test_assess_complexity_edge_cases(self):
        """Test complexity assessment edge cases."""
        provider = CodeMetricsProvider()

        # Zero changes
        assert provider._assess_complexity(0, 0) == "minimal"

        # Exactly at thresholds
        assert provider._assess_complexity(100, 5) == "moderate"  # Just below
        assert provider._assess_complexity(101, 5) == "substantial"  # Just above
        assert provider._assess_complexity(100, 6) == "substantial"  # Files over


class TestIntegration:
    """Test full metrics calculation integration."""

    def test_calculate_metrics_full_integration(self):
        """Test full metrics calculation with all components."""
        provider = CodeMetricsProvider()

        with patch.object(provider, '_count_loc_changes', return_value=(120, 40)):
            with patch.object(provider, '_count_files_changed', return_value=6):
                result = provider.calculate_metrics({"base_ref": "main"})

                # Check structure
                assert result.content_created["type"] == "code"
                assert result.content_created["quantity"] == 120
                assert result.content_created["units"] == "lines"
                assert result.components_modified == 6
                assert result.complexity == "substantial"

                # Check raw data
                assert result.raw_data["loc_added"] == 120
                assert result.raw_data["loc_deleted"] == 40
                assert result.raw_data["files_changed"] == 6
                assert result.raw_data["base_ref"] == "main"

    def test_calculate_metrics_minimal_work(self):
        """Test metrics for minimal work."""
        provider = CodeMetricsProvider()

        with patch.object(provider, '_count_loc_changes', return_value=(10, 5)):
            with patch.object(provider, '_count_files_changed', return_value=1):
                result = provider.calculate_metrics({})

                assert result.complexity == "minimal"
                assert result.is_substantial() is False

    def test_calculate_metrics_moderate_work(self):
        """Test metrics for moderate work."""
        provider = CodeMetricsProvider()

        with patch.object(provider, '_count_loc_changes', return_value=(50, 20)):
            with patch.object(provider, '_count_files_changed', return_value=3):
                result = provider.calculate_metrics({})

                assert result.complexity == "moderate"
                assert result.is_substantial() is True

    def test_calculate_metrics_substantial_work(self):
        """Test metrics for substantial work."""
        provider = CodeMetricsProvider()

        with patch.object(provider, '_count_loc_changes', return_value=(150, 80)):
            with patch.object(provider, '_count_files_changed', return_value=8):
                result = provider.calculate_metrics({})

                assert result.complexity == "substantial"
                assert result.is_substantial() is True

    def test_calculate_metrics_with_include_untracked(self):
        """Test metrics calculation with untracked files."""
        provider = CodeMetricsProvider()

        with patch.object(provider, '_count_loc_changes', return_value=(50, 20)):
            with patch.object(provider, '_count_files_changed', return_value=5) as mock_count:
                result = provider.calculate_metrics({"include_untracked": True})

                # Check that include_untracked was passed
                mock_count.assert_called_once_with("HEAD~1", True)

    def test_calculate_metrics_propagates_errors(self):
        """Test errors are propagated from internal methods."""
        provider = CodeMetricsProvider()

        with patch.object(provider, '_count_loc_changes', side_effect=MetricsCalculationError("Test error")):
            with pytest.raises(MetricsCalculationError, match="Test error"):
                provider.calculate_metrics({})


class TestSecurityAndSafety:
    """Test security and safety measures."""

    def test_no_shell_injection_base_ref(self):
        """Test base_ref is safely passed to subprocess."""
        provider = CodeMetricsProvider()

        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_result.returncode = 0

        with patch('subprocess.run', return_value=mock_result) as mock_run:
            # Try malicious base_ref
            provider._count_loc_changes("main; rm -rf /")

            # Command should be list (not shell string)
            call_args = mock_run.call_args[0][0]
            assert isinstance(call_args, list)
            assert call_args[3] == "main; rm -rf /"  # Passed as argument, not shell command

    def test_subprocess_uses_check_flag(self):
        """Test subprocess uses check=True for error handling."""
        provider = CodeMetricsProvider()

        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_result.returncode = 0

        with patch('subprocess.run', return_value=mock_result) as mock_run:
            provider._count_loc_changes("HEAD~1")

            # Should use check=True
            assert mock_run.call_args[1]['check'] is True

    def test_subprocess_uses_timeout(self):
        """Test subprocess has timeout to prevent hanging."""
        provider = CodeMetricsProvider()

        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_result.returncode = 0

        with patch('subprocess.run', return_value=mock_result) as mock_run:
            provider._count_loc_changes("HEAD~1")

            # Should have timeout
            assert 'timeout' in mock_run.call_args[1]
            assert mock_run.call_args[1]['timeout'] == 30
