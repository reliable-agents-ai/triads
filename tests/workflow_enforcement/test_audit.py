"""Unit tests for AuditLogger.

Tests cover:
- Log file creation
- Log entry format (JSON)
- Concurrent logging (multiple processes)
- User detection (git config vs. system)
- get_recent_bypasses
- Append-only behavior
"""

import json
import subprocess
import tempfile
import threading
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from triads.workflow_enforcement.audit import AuditLogger


@pytest.fixture
def temp_audit_file():
    """Create temporary audit log file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir) / "test_audit.log"


@pytest.fixture
def logger(temp_audit_file):
    """Create AuditLogger instance."""
    return AuditLogger(temp_audit_file)


class TestLogBypass:
    """Test bypass event logging."""

    def test_log_bypass_creates_file(self, logger, temp_audit_file):
        """Test logging creates audit file."""
        logger.log_bypass("Test bypass")

        assert temp_audit_file.exists()

    def test_log_bypass_creates_directory(self):
        """Test logging creates parent directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            audit_file = Path(tmpdir) / "nested" / "dir" / "audit.log"
            logger = AuditLogger(audit_file)

            logger.log_bypass("Test bypass")

            assert audit_file.exists()
            assert audit_file.parent.exists()

    def test_log_bypass_appends(self, logger, temp_audit_file):
        """Test logging appends to existing file."""
        logger.log_bypass("First bypass")
        logger.log_bypass("Second bypass")

        with open(temp_audit_file) as f:
            lines = f.readlines()

        assert len(lines) == 2

    def test_log_bypass_json_format(self, logger, temp_audit_file):
        """Test log entries are valid JSON."""
        logger.log_bypass("Test bypass")

        with open(temp_audit_file) as f:
            line = f.read().strip()
            entry = json.loads(line)

        assert isinstance(entry, dict)

    def test_log_bypass_required_fields(self, logger, temp_audit_file):
        """Test log entry contains required fields."""
        logger.log_bypass("Test bypass", metadata={"test": True})

        with open(temp_audit_file) as f:
            entry = json.loads(f.read().strip())

        assert "timestamp" in entry
        assert "event" in entry
        assert "user" in entry
        assert "justification" in entry
        assert "metadata" in entry

    def test_log_bypass_event_type(self, logger, temp_audit_file):
        """Test event type is set correctly."""
        logger.log_bypass("Test bypass")

        with open(temp_audit_file) as f:
            entry = json.loads(f.read().strip())

        assert entry["event"] == "emergency_bypass"

    def test_log_bypass_justification(self, logger, temp_audit_file):
        """Test justification is logged correctly."""
        justification = "Critical hotfix for production bug #1234"
        logger.log_bypass(justification)

        with open(temp_audit_file) as f:
            entry = json.loads(f.read().strip())

        assert entry["justification"] == justification

    def test_log_bypass_metadata(self, logger, temp_audit_file):
        """Test metadata is logged correctly."""
        metadata = {"loc_changed": 150, "files_changed": 8, "trigger": "manual"}
        logger.log_bypass("Test bypass", metadata=metadata)

        with open(temp_audit_file) as f:
            entry = json.loads(f.read().strip())

        assert entry["metadata"] == metadata

    def test_log_bypass_empty_metadata(self, logger, temp_audit_file):
        """Test logging with empty metadata."""
        logger.log_bypass("Test bypass")

        with open(temp_audit_file) as f:
            entry = json.loads(f.read().strip())

        assert entry["metadata"] == {}

    def test_log_bypass_timestamp_format(self, logger, temp_audit_file):
        """Test timestamp is in ISO 8601 format."""
        logger.log_bypass("Test bypass")

        with open(temp_audit_file) as f:
            entry = json.loads(f.read().strip())

        # Should be parseable as ISO format
        from datetime import datetime

        timestamp = datetime.fromisoformat(entry["timestamp"])
        assert isinstance(timestamp, datetime)

    def test_log_bypass_unicode_justification(self, logger, temp_audit_file):
        """Test logging with unicode characters."""
        justification = "紧急修复 🚨 for production"
        logger.log_bypass(justification)

        with open(temp_audit_file) as f:
            entry = json.loads(f.read().strip())

        assert entry["justification"] == justification


class TestGetUser:
    """Test user detection."""

    @patch("subprocess.run")
    def test_get_user_from_git_config(self, mock_run, logger):
        """Test user detection from git config."""
        # Mock git config user.name
        mock_name = MagicMock()
        mock_name.returncode = 0
        mock_name.stdout = "John Doe"

        # Mock git config user.email
        mock_email = MagicMock()
        mock_email.returncode = 0
        mock_email.stdout = "john@example.com"

        mock_run.side_effect = [mock_name, mock_email]

        user = logger._get_user()

        assert user == "John Doe <john@example.com>"

    @patch("subprocess.run")
    def test_get_user_git_name_only(self, mock_run, logger):
        """Test user detection with git name but no email."""
        # Mock git config user.name
        mock_name = MagicMock()
        mock_name.returncode = 0
        mock_name.stdout = "John Doe"

        # Mock git config user.email (fails)
        mock_email = MagicMock()
        mock_email.returncode = 1
        mock_email.stdout = ""

        mock_run.side_effect = [mock_name, mock_email]

        user = logger._get_user()

        assert user == "John Doe"

    @patch("subprocess.run")
    @patch("getpass.getuser")
    def test_get_user_fallback_to_system(
        self, mock_getuser, mock_run, logger
    ):
        """Test fallback to system user when git unavailable."""
        mock_run.side_effect = FileNotFoundError("git not found")
        mock_getuser.return_value = "systemuser"

        user = logger._get_user()

        assert user == "systemuser"

    @patch("subprocess.run")
    @patch("getpass.getuser")
    def test_get_user_fallback_on_git_error(
        self, mock_getuser, mock_run, logger
    ):
        """Test fallback when git config fails."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_run.return_value = mock_result
        mock_getuser.return_value = "systemuser"

        user = logger._get_user()

        assert user == "systemuser"

    @patch("subprocess.run")
    @patch("getpass.getuser")
    def test_get_user_unknown_on_all_failures(
        self, mock_getuser, mock_run, logger
    ):
        """Test returns 'unknown' when all methods fail."""
        mock_run.side_effect = Exception("Git failed")
        mock_getuser.side_effect = Exception("Getuser failed")

        user = logger._get_user()

        assert user == "unknown"


class TestGetRecentBypasses:
    """Test retrieving recent bypass events."""

    def test_get_recent_bypasses_empty_log(self, logger):
        """Test returns empty list for non-existent log."""
        recent = logger.get_recent_bypasses()
        assert recent == []

    def test_get_recent_bypasses_single_entry(self, logger, temp_audit_file):
        """Test retrieval of single bypass entry."""
        logger.log_bypass("Test bypass")

        recent = logger.get_recent_bypasses()

        assert len(recent) == 1
        assert recent[0]["justification"] == "Test bypass"

    def test_get_recent_bypasses_multiple_entries(self, logger):
        """Test retrieval of multiple bypass entries."""
        logger.log_bypass("First bypass")
        logger.log_bypass("Second bypass")
        logger.log_bypass("Third bypass")

        recent = logger.get_recent_bypasses()

        assert len(recent) == 3

    def test_get_recent_bypasses_order(self, logger):
        """Test bypasses returned in reverse order (most recent first)."""
        logger.log_bypass("First bypass")
        logger.log_bypass("Second bypass")
        logger.log_bypass("Third bypass")

        recent = logger.get_recent_bypasses()

        assert recent[0]["justification"] == "Third bypass"
        assert recent[1]["justification"] == "Second bypass"
        assert recent[2]["justification"] == "First bypass"

    def test_get_recent_bypasses_limit(self, logger):
        """Test limit parameter."""
        for i in range(10):
            logger.log_bypass(f"Bypass {i}")

        recent = logger.get_recent_bypasses(limit=5)

        assert len(recent) == 5
        assert recent[0]["justification"] == "Bypass 9"

    def test_get_recent_bypasses_limit_exceeds_total(self, logger):
        """Test limit larger than total entries."""
        logger.log_bypass("First")
        logger.log_bypass("Second")

        recent = logger.get_recent_bypasses(limit=10)

        assert len(recent) == 2

    def test_get_recent_bypasses_skips_malformed_lines(self, logger, temp_audit_file):
        """Test malformed JSON lines are skipped."""
        # Write valid entry
        logger.log_bypass("Valid bypass")

        # Append malformed entries
        with open(temp_audit_file, "a") as f:
            f.write("{ invalid json\n")
            f.write("not json at all\n")

        # Write another valid entry
        logger.log_bypass("Another valid bypass")

        recent = logger.get_recent_bypasses()

        # Should only return valid entries
        assert len(recent) == 2
        assert recent[0]["justification"] == "Another valid bypass"

    def test_get_recent_bypasses_filters_by_event_type(
        self, logger, temp_audit_file
    ):
        """Test only emergency_bypass events returned."""
        # Write emergency_bypass event
        logger.log_bypass("Test bypass")

        # Append different event type
        other_event = {
            "timestamp": "2025-10-17T10:00:00",
            "event": "other_event",
            "user": "test",
            "justification": "N/A",
            "metadata": {},
        }
        with open(temp_audit_file, "a") as f:
            f.write(json.dumps(other_event) + "\n")

        recent = logger.get_recent_bypasses()

        # Should only return emergency_bypass
        assert len(recent) == 1
        assert recent[0]["event"] == "emergency_bypass"

    def test_get_recent_bypasses_empty_lines(self, logger, temp_audit_file):
        """Test empty lines are skipped."""
        logger.log_bypass("First")

        with open(temp_audit_file, "a") as f:
            f.write("\n\n")

        logger.log_bypass("Second")

        recent = logger.get_recent_bypasses()

        assert len(recent) == 2


class TestConcurrentLogging:
    """Test concurrent logging from multiple threads."""

    def test_concurrent_logging_no_corruption(self, logger):
        """Test concurrent logging doesn't corrupt file."""
        num_threads = 10
        errors = []

        def log_bypass(thread_id):
            try:
                logger.log_bypass(f"Bypass from thread {thread_id}")
            except Exception as e:
                errors.append(e)

        # Create and start threads
        threads = [
            threading.Thread(target=log_bypass, args=(i,)) for i in range(num_threads)
        ]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # No errors should occur
        assert len(errors) == 0

        # All entries should be logged
        recent = logger.get_recent_bypasses(limit=num_threads)
        assert len(recent) == num_threads

    def test_concurrent_logging_all_entries_valid_json(self, logger, temp_audit_file):
        """Test all entries are valid JSON after concurrent writes."""
        num_threads = 20

        def log_bypass(thread_id):
            logger.log_bypass(f"Thread {thread_id}", metadata={"thread": thread_id})

        threads = [
            threading.Thread(target=log_bypass, args=(i,)) for i in range(num_threads)
        ]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # Read all lines and verify valid JSON
        with open(temp_audit_file) as f:
            lines = f.readlines()

        assert len(lines) == num_threads

        for line in lines:
            entry = json.loads(line.strip())
            assert "justification" in entry
            assert "thread" in entry["metadata"]


class TestAppendOnly:
    """Test append-only behavior."""

    def test_append_only_preserves_existing(self, logger, temp_audit_file):
        """Test new logs don't overwrite existing entries."""
        logger.log_bypass("First bypass")
        first_content = temp_audit_file.read_text()

        logger.log_bypass("Second bypass")
        second_content = temp_audit_file.read_text()

        # First content should be preserved
        assert first_content in second_content

    def test_append_only_multiple_instances(self, temp_audit_file):
        """Test multiple logger instances append to same file."""
        logger1 = AuditLogger(temp_audit_file)
        logger2 = AuditLogger(temp_audit_file)

        logger1.log_bypass("From logger 1")
        logger2.log_bypass("From logger 2")

        with open(temp_audit_file) as f:
            lines = f.readlines()

        assert len(lines) == 2


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_log_bypass_very_long_justification(self, logger, temp_audit_file):
        """Test logging very long justification."""
        justification = "a" * 10000
        logger.log_bypass(justification)

        with open(temp_audit_file) as f:
            entry = json.loads(f.read().strip())

        assert entry["justification"] == justification

    def test_log_bypass_special_characters(self, logger, temp_audit_file):
        """Test logging with special characters."""
        justification = 'Test "quotes" and \\backslashes\\ and \nnewlines'
        logger.log_bypass(justification)

        with open(temp_audit_file) as f:
            entry = json.loads(f.read().strip())

        assert entry["justification"] == justification

    def test_log_bypass_large_metadata(self, logger, temp_audit_file):
        """Test logging with large metadata."""
        metadata = {f"key_{i}": f"value_{i}" for i in range(100)}
        logger.log_bypass("Test bypass", metadata=metadata)

        with open(temp_audit_file) as f:
            entry = json.loads(f.read().strip())

        assert len(entry["metadata"]) == 100

    def test_get_recent_bypasses_file_read_error(self, logger, temp_audit_file):
        """Test handling of file read errors."""
        # Create logger with non-existent directory (will fail on read)
        bad_logger = AuditLogger(Path("/nonexistent/path/audit.log"))

        recent = bad_logger.get_recent_bypasses()

        # Should return empty list instead of crashing
        assert recent == []

    @patch("subprocess.run")
    def test_get_user_timeout(self, mock_run, logger):
        """Test handling of git timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired("git", 2)

        user = logger._get_user()

        # Should fallback gracefully
        assert user in ["unknown", "systemuser"]  # Depends on getpass success

    def test_log_bypass_none_metadata(self, logger, temp_audit_file):
        """Test logging with None metadata."""
        logger.log_bypass("Test bypass", metadata=None)

        with open(temp_audit_file) as f:
            entry = json.loads(f.read().strip())

        # Should default to empty dict
        assert entry["metadata"] == {}
