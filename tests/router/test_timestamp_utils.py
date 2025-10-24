"""Tests for timestamp utility functions."""
from datetime import datetime, timezone
import re

from triads.tools.router._timestamp_utils import utc_now_iso, utc_now_aware


class TestTimestampUtils:
    """Test timestamp generation utilities."""

    def test_utc_now_iso_format(self):
        """Test ISO format with Z suffix."""
        timestamp = utc_now_iso()
        
        # Should match ISO 8601 format: YYYY-MM-DDTHH:MM:SS.ffffffZ
        pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}Z$'
        assert re.match(pattern, timestamp), f"Format incorrect: {timestamp}"
        
        # Should end with Z
        assert timestamp.endswith('Z')
        
        # Should contain T separator
        assert 'T' in timestamp

    def test_utc_now_iso_parseable(self):
        """Test that generated timestamp can be parsed back."""
        timestamp = utc_now_iso()
        
        # Should be parseable
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        
        # Should be timezone-aware
        assert dt.tzinfo is not None
        
        # Should be UTC
        assert dt.tzinfo == timezone.utc

    def test_utc_now_aware_returns_aware_datetime(self):
        """Test that utc_now_aware returns timezone-aware datetime."""
        dt = utc_now_aware()
        
        # Should be datetime
        assert isinstance(dt, datetime)
        
        # Should be timezone-aware
        assert dt.tzinfo is not None
        
        # Should be UTC
        assert dt.tzinfo == timezone.utc

    def test_utc_now_aware_recent_time(self):
        """Test that generated time is recent (within 1 second)."""
        before = datetime.now(timezone.utc)
        generated = utc_now_aware()
        after = datetime.now(timezone.utc)
        
        # Should be between before and after
        assert before <= generated <= after
        
        # Should be within 1 second
        assert (after - before).total_seconds() < 1.0

    def test_consistency_between_functions(self):
        """Test that both functions produce consistent times."""
        iso_str = utc_now_iso()
        aware_dt = utc_now_aware()
        
        # Parse ISO string
        parsed_dt = datetime.fromisoformat(iso_str.replace('Z', '+00:00'))
        
        # Should be within 1 second of each other
        diff = abs((parsed_dt - aware_dt).total_seconds())
        assert diff < 1.0, f"Time difference too large: {diff}s"
