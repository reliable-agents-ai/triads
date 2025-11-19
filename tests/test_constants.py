"""Tests for constants module."""

import sys
from pathlib import Path

# Add hooks to path
hooks_dir = Path(__file__).parent.parent / "hooks"
sys.path.insert(0, str(hooks_dir))

from constants import (
    CONFIDENCE_THRESHOLD_ACCEPTABLE,
    CONFIDENCE_THRESHOLD_AUTO_PAUSE,
    CONFIDENCE_THRESHOLD_HIGH,
    CONFIDENCE_THRESHOLD_VERY_HIGH,
    EVENT_RATE_LIMIT_PER_MINUTE,
    EVENTS_FILE,
    HANDOFF_EXPIRY_HOURS,
    MAX_EVENT_FILE_SIZE_MB,
    MAX_EVENTS_PER_FILE,
    MAX_USER_INPUT_SIZE_KB,
    PLUGIN_VERSION,
)


class TestConstants:
    """Test constants module."""

    def test_plugin_version_format(self):
        """Test plugin version is in semantic versioning format."""
        assert isinstance(PLUGIN_VERSION, str)
        parts = PLUGIN_VERSION.split(".")
        assert len(parts) == 3
        assert all(part.isdigit() for part in parts)

    def test_confidence_thresholds_ordered(self):
        """Test confidence thresholds are in ascending order."""
        assert CONFIDENCE_THRESHOLD_ACCEPTABLE < CONFIDENCE_THRESHOLD_AUTO_PAUSE
        assert CONFIDENCE_THRESHOLD_AUTO_PAUSE < CONFIDENCE_THRESHOLD_HIGH
        assert CONFIDENCE_THRESHOLD_HIGH < CONFIDENCE_THRESHOLD_VERY_HIGH

    def test_confidence_thresholds_range(self):
        """Test confidence thresholds are in valid range [0, 1]."""
        thresholds = [
            CONFIDENCE_THRESHOLD_ACCEPTABLE,
            CONFIDENCE_THRESHOLD_AUTO_PAUSE,
            CONFIDENCE_THRESHOLD_HIGH,
            CONFIDENCE_THRESHOLD_VERY_HIGH,
        ]
        for threshold in thresholds:
            assert 0 <= threshold <= 1

    def test_handoff_expiry_positive(self):
        """Test handoff expiry is positive."""
        assert HANDOFF_EXPIRY_HOURS > 0

    def test_rate_limit_reasonable(self):
        """Test rate limit is reasonable (not too low, not too high)."""
        assert 10 <= EVENT_RATE_LIMIT_PER_MINUTE <= 1000

    def test_file_size_limits_positive(self):
        """Test file size limits are positive."""
        assert MAX_EVENT_FILE_SIZE_MB > 0
        assert MAX_EVENTS_PER_FILE > 0
        assert MAX_USER_INPUT_SIZE_KB > 0

    def test_events_file_path_valid(self):
        """Test events file path is valid format."""
        assert EVENTS_FILE.endswith(".jsonl")
        assert "/" in EVENTS_FILE or "\\" in EVENTS_FILE  # Has directory component
