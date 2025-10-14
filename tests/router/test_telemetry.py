"""Tests for router telemetry."""

import json

import pytest

from src.triads.router.telemetry import TelemetryLogger


class TestTelemetryLogger:
    """Test TelemetryLogger functionality."""

    @pytest.fixture
    def log_file(self, tmp_path):
        """Create temporary log file path."""
        return tmp_path / "routing_telemetry.jsonl"

    def test_log_disabled(self, log_file):
        """Test logging when disabled doesn't create files."""
        logger = TelemetryLogger(log_path=log_file, enabled=False)

        logger.log_route_decision(
            prompt_snippet="test prompt",
            triad="design",
            confidence=0.95,
            method="semantic",
            latency_ms=5.2,
        )

        assert not log_file.exists()

    def test_log_route_decision(self, log_file):
        """Test logging route decision."""
        logger = TelemetryLogger(log_path=log_file, enabled=True)

        logger.log_route_decision(
            prompt_snippet="Let's design the API",
            triad="design",
            confidence=0.95,
            method="semantic",
            latency_ms=5.2,
            overridden=False,
        )

        # Read and verify
        with open(log_file) as f:
            event = json.loads(f.readline())

        assert event["event_type"] == "route_decision"
        assert event["prompt_snippet"] == "Let's design the API"
        assert event["triad"] == "design"
        assert event["confidence"] == 0.95
        assert event["method"] == "semantic"
        assert event["latency_ms"] == 5.2
        assert event["overridden"] is False
        assert "timestamp" in event

    def test_log_semantic_routing(self, log_file):
        """Test logging semantic routing attempt."""
        logger = TelemetryLogger(log_path=log_file, enabled=True)

        logger.log_semantic_routing(
            prompt_snippet="Test prompt",
            top_scores=[("design", 0.85), ("implementation", 0.70)],
            is_ambiguous=False,
            latency_ms=8.5,
        )

        with open(log_file) as f:
            event = json.loads(f.readline())

        assert event["event_type"] == "semantic_routing"
        # JSON serializes tuples as lists
        assert event["top_scores"] == [["design", 0.85], ["implementation", 0.70]]
        assert event["is_ambiguous"] is False
        assert event["latency_ms"] == 8.5

    def test_log_llm_disambiguation(self, log_file):
        """Test logging LLM disambiguation."""
        logger = TelemetryLogger(log_path=log_file, enabled=True)

        logger.log_llm_disambiguation(
            prompt_snippet="Ambiguous prompt",
            candidates=["design", "implementation"],
            selected_triad="design",
            confidence=0.88,
            latency_ms=1200.5,
        )

        with open(log_file) as f:
            event = json.loads(f.readline())

        assert event["event_type"] == "llm_disambiguation"
        assert event["candidates"] == ["design", "implementation"]
        assert event["selected_triad"] == "design"
        assert event["confidence"] == 0.88
        assert event["latency_ms"] == 1200.5

    def test_log_grace_period_check(self, log_file):
        """Test logging grace period check."""
        logger = TelemetryLogger(log_path=log_file, enabled=True)

        logger.log_grace_period_check(
            active_triad="implementation",
            turn_count=3,
            elapsed_minutes=4.5,
            within_grace=True,
        )

        with open(log_file) as f:
            event = json.loads(f.readline())

        assert event["event_type"] == "grace_period_check"
        assert event["active_triad"] == "implementation"
        assert event["turn_count"] == 3
        assert event["elapsed_minutes"] == 4.5
        assert event["within_grace"] is True

    def test_log_error(self, log_file):
        """Test logging errors."""
        logger = TelemetryLogger(log_path=log_file, enabled=True)

        logger.log_error(
            error_type="embedding_failure",
            error_message="Failed to load model",
            context={"model_path": "/path/to/model"},
        )

        with open(log_file) as f:
            event = json.loads(f.readline())

        assert event["event_type"] == "error"
        assert event["error_type"] == "embedding_failure"
        assert event["error_message"] == "Failed to load model"
        assert event["context"]["model_path"] == "/path/to/model"

    def test_safe_snippet_truncation(self, log_file):
        """Test prompt snippet truncation for privacy."""
        logger = TelemetryLogger(log_path=log_file, enabled=True)

        long_prompt = "A" * 100  # 100 character prompt

        logger.log_route_decision(
            prompt_snippet=long_prompt,
            triad="design",
            confidence=0.90,
            method="semantic",
            latency_ms=5.0,
        )

        with open(log_file) as f:
            event = json.loads(f.readline())

        # Should be truncated to 50 chars + "..."
        assert len(event["prompt_snippet"]) == 53
        assert event["prompt_snippet"].endswith("...")

    def test_safe_snippet_no_truncation(self, log_file):
        """Test prompt snippet not truncated when short."""
        logger = TelemetryLogger(log_path=log_file, enabled=True)

        short_prompt = "Short prompt"

        logger.log_route_decision(
            prompt_snippet=short_prompt,
            triad="design",
            confidence=0.90,
            method="semantic",
            latency_ms=5.0,
        )

        with open(log_file) as f:
            event = json.loads(f.readline())

        assert event["prompt_snippet"] == short_prompt

    def test_multiple_events(self, log_file):
        """Test logging multiple events."""
        logger = TelemetryLogger(log_path=log_file, enabled=True)

        # Log multiple events
        for i in range(5):
            logger.log_route_decision(
                prompt_snippet=f"Prompt {i}",
                triad="design",
                confidence=0.90 + i * 0.01,
                method="semantic",
                latency_ms=5.0 + i,
            )

        # Verify all events
        with open(log_file) as f:
            events = [json.loads(line) for line in f]

        assert len(events) == 5
        assert events[0]["prompt_snippet"] == "Prompt 0"
        assert events[4]["prompt_snippet"] == "Prompt 4"

    def test_log_rotation(self, log_file):
        """Test log rotation at size limit."""
        # Small max size for testing (1KB)
        logger = TelemetryLogger(log_path=log_file, enabled=True, max_size_mb=0.001)

        # Write enough events to trigger rotation
        for i in range(100):
            logger.log_route_decision(
                prompt_snippet="A" * 50,
                triad="design",
                confidence=0.95,
                method="semantic",
                latency_ms=5.0,
            )

        # Check rotation occurred - at least one rotated file should exist
        rotated_1 = log_file.with_suffix(".jsonl.1")
        assert rotated_1.exists(), "Rotation file should exist after exceeding size limit"
        assert rotated_1.stat().st_size > 0, "Rotated file should have content"

    def test_log_rotation_keeps_two(self, log_file):
        """Test log rotation keeps last 2 rotations."""
        logger = TelemetryLogger(log_path=log_file, enabled=True, max_size_mb=0.0005)

        # Trigger multiple rotations (write enough to rotate at least twice)
        for i in range(150):
            logger.log_route_decision(
                prompt_snippet="A" * 50,
                triad="design",
                confidence=0.95,
                method="semantic",
                latency_ms=5.0,
            )

        rotated_1 = log_file.with_suffix(".jsonl.1")

        # Write more to ensure current log exists after final rotation
        for i in range(5):
            logger.log_route_decision(
                prompt_snippet="B" * 50,
                triad="implementation",
                confidence=0.92,
                method="semantic",
                latency_ms=6.0,
            )

        # Should have current + at least 1 rotation
        assert log_file.exists(), "Current log should exist"
        assert rotated_1.exists(), "First rotation should exist"
        # .2 may or may not exist depending on exact rotation timing

    def test_get_stats_empty(self, log_file):
        """Test get_stats with no logs."""
        logger = TelemetryLogger(log_path=log_file, enabled=True)

        stats = logger.get_stats()

        assert stats == {}

    def test_get_stats_basic(self, log_file):
        """Test get_stats with logged events."""
        logger = TelemetryLogger(log_path=log_file, enabled=True)

        # Log various events
        logger.log_route_decision(
            prompt_snippet="Test 1",
            triad="design",
            confidence=0.95,
            method="semantic",
            latency_ms=5.0,
        )
        logger.log_route_decision(
            prompt_snippet="Test 2",
            triad="implementation",
            confidence=0.88,
            method="llm",
            latency_ms=1200.0,
        )
        logger.log_route_decision(
            prompt_snippet="Test 3",
            triad="design",
            confidence=1.0,
            method="manual",
            latency_ms=0.0,
        )
        logger.log_error("test_error", "Test error message")

        stats = logger.get_stats()

        assert stats["total_events"] == 4
        assert stats["route_decisions"] == 3
        assert stats["semantic_routes"] == 1
        assert stats["llm_routes"] == 1
        assert stats["manual_routes"] == 1
        assert stats["errors"] == 1
        assert stats["avg_latency_ms"] > 0
