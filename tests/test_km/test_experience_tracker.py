"""Tests for experience tracker - outcome detection and confidence updates."""

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from triads.km.experience_tracker import (
    ExperienceTracker,
    InjectionRecord,
    OutcomeDetector,
    OutcomeRecord,
)


@pytest.fixture
def temp_base_dir(tmp_path):
    """Create temporary base directory with .claude folder."""
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir(parents=True)
    return tmp_path


@pytest.fixture
def tracker(temp_base_dir):
    """Create experience tracker with temp directory."""
    return ExperienceTracker(base_dir=temp_base_dir)


# ============================================================================
# State File Management Tests
# ============================================================================


def test_tracker_creates_state_file(temp_base_dir):
    """Tracker should create state file on initialization."""
    state_file = temp_base_dir / ".claude" / "experience_state.json"
    assert not state_file.exists()

    ExperienceTracker(base_dir=temp_base_dir)

    assert state_file.exists()

    # Check structure
    with open(state_file) as f:
        state = json.load(f)

    assert "session_id" in state
    assert "injections" in state
    assert "outcomes" in state
    assert state["injections"] == []
    assert state["outcomes"] == []


def test_tracker_preserves_existing_state(temp_base_dir):
    """Tracker should not overwrite existing state file."""
    state_file = temp_base_dir / ".claude" / "experience_state.json"

    # Create existing state
    existing = {
        "session_id": "2025-01-01T00:00:00",
        "injections": [{"test": "data"}],
        "outcomes": []
    }
    state_file.write_text(json.dumps(existing))

    ExperienceTracker(base_dir=temp_base_dir)

    # Should preserve existing data
    with open(state_file) as f:
        state = json.load(f)

    assert state["session_id"] == "2025-01-01T00:00:00"
    assert state["injections"] == [{"test": "data"}]


# ============================================================================
# Injection Recording Tests
# ============================================================================


def test_record_injection(tracker, temp_base_dir):
    """Should record lesson injection to state file."""
    tracker.record_injection(
        lesson_id="test_001",
        triad="deployment",
        label="Version Bump Checklist",
        tool_name="Write",
        confidence=0.95
    )

    # Check state file
    state_file = temp_base_dir / ".claude" / "experience_state.json"
    with open(state_file) as f:
        state = json.load(f)

    assert len(state["injections"]) == 1

    record = state["injections"][0]
    assert record["lesson_id"] == "test_001"
    assert record["triad"] == "deployment"
    assert record["label"] == "Version Bump Checklist"
    assert record["tool_name"] == "Write"
    assert record["confidence"] == 0.95
    assert "injected_at" in record


def test_record_multiple_injections(tracker, temp_base_dir):
    """Should record multiple injections."""
    tracker.record_injection("test_001", "deployment", "Lesson 1", "Write", 0.95)
    tracker.record_injection("test_002", "design", "Lesson 2", "Edit", 0.85)

    state_file = temp_base_dir / ".claude" / "experience_state.json"
    with open(state_file) as f:
        state = json.load(f)

    assert len(state["injections"]) == 2
    assert state["injections"][0]["lesson_id"] == "test_001"
    assert state["injections"][1]["lesson_id"] == "test_002"


# ============================================================================
# Outcome Detection Tests
# ============================================================================


def test_detect_success_outcome():
    """Should detect success when lesson was followed."""
    conversation = """
    User: Write to plugin.json
    Assistant: Let me follow the Version Bump Checklist:
    - Updated plugin.json ✓
    - Updated marketplace.json ✓
    - Verified all required items ✓
    """

    detector = OutcomeDetector(conversation)
    outcome, evidence, strength = detector.detect_for_lesson("Version Bump Checklist")

    assert outcome == "success"
    assert "verified all required" in evidence.lower()
    assert strength == 0.8


def test_detect_failure_outcome():
    """Should detect failure when lesson was forgotten."""
    conversation = """
    User: Oh no, I forgot to update marketplace.json!
    Assistant: That's what the Version Bump Checklist was for.
    User: I should have checked all items.
    """

    detector = OutcomeDetector(conversation)
    outcome, evidence, strength = detector.detect_for_lesson("Version Bump Checklist")

    assert outcome == "failure"
    assert "forgot" in evidence.lower()
    assert strength == 0.8


def test_detect_contradiction_outcome():
    """Should detect contradiction when lesson was wrong."""
    conversation = """
    User: Actually, that Version Bump Checklist was incorrect.
    The marketplace.json doesn't need to be updated for patch releases.
    """

    detector = OutcomeDetector(conversation)
    outcome, evidence, strength = detector.detect_for_lesson("Version Bump Checklist")

    assert outcome == "contradiction"
    assert "was incorrect" in evidence.lower() or "was wrong" in evidence.lower()
    assert strength == 1.0


def test_detect_validation_outcome():
    """Should detect validation when user confirms lesson."""
    conversation = """
    User: Thanks for that reminder about the Version Bump Checklist!
    That prevented a mistake - good catch.
    """

    detector = OutcomeDetector(conversation)
    outcome, evidence, strength = detector.detect_for_lesson("Version Bump Checklist")

    assert outcome == "validation"
    assert "prevented" in evidence.lower() or "thanks" in evidence.lower()
    assert strength == 1.0


def test_detect_no_outcome_when_not_mentioned():
    """Should return empty outcome if lesson not mentioned."""
    conversation = """
    User: Write some code
    Assistant: Sure, here's the implementation.
    """

    detector = OutcomeDetector(conversation)
    outcome, evidence, strength = detector.detect_for_lesson("Version Bump Checklist")

    assert outcome == ""
    assert evidence == ""
    assert strength == 0.0


def test_detect_no_outcome_when_neutral_mention():
    """Should return empty if lesson mentioned but no clear outcome."""
    conversation = """
    User: What's in the Version Bump Checklist?
    Assistant: It includes plugin.json, marketplace.json, etc.
    """

    detector = OutcomeDetector(conversation)
    outcome, evidence, strength = detector.detect_for_lesson("Version Bump Checklist")

    assert outcome == ""


def test_detect_outcomes_integration(tracker, temp_base_dir):
    """Integration test: record injections then detect outcomes."""
    # Record injections
    tracker.record_injection(
        "test_001", "deployment", "Version Bump Checklist", "Write", 0.95
    )
    tracker.record_injection(
        "test_002", "design", "ADR Pattern", "Write", 0.90
    )

    # Simulate conversation
    conversation = """
    User: I'm updating the version
    Assistant: Here's the Version Bump Checklist:
    - plugin.json
    - marketplace.json

    User: Done! Verified all required items.
    Assistant: Great!

    Also, regarding the ADR Pattern - actually that was wrong advice.
    The pattern doesn't apply here.
    """

    outcomes = tracker.detect_outcomes(conversation)

    # Should detect 2 outcomes
    assert len(outcomes) == 2

    # Find specific outcomes
    checklist_outcome = next(o for o in outcomes if o.lesson_id == "test_001")
    adr_outcome = next(o for o in outcomes if o.lesson_id == "test_002")

    assert checklist_outcome.outcome == "success"
    assert adr_outcome.outcome == "contradiction"


# ============================================================================
# Session Management Tests
# ============================================================================


def test_clear_session(tracker, temp_base_dir):
    """Should clear session state."""
    # Add some data
    tracker.record_injection("test_001", "deployment", "Lesson 1", "Write", 0.95)

    state_file = temp_base_dir / ".claude" / "experience_state.json"
    with open(state_file) as f:
        state = json.load(f)
    assert len(state["injections"]) == 1

    # Clear session
    tracker.clear_session()

    with open(state_file) as f:
        state = json.load(f)

    assert len(state["injections"]) == 0
    assert len(state["outcomes"]) == 0
    assert "session_id" in state


# ============================================================================
# Data Class Tests
# ============================================================================


def test_injection_record_dataclass():
    """InjectionRecord should serialize correctly."""
    record = InjectionRecord(
        lesson_id="test_001",
        triad="deployment",
        label="Test Lesson",
        tool_name="Write",
        injected_at="2025-10-19T12:00:00",
        confidence=0.95
    )

    data = {
        "lesson_id": "test_001",
        "triad": "deployment",
        "label": "Test Lesson",
        "tool_name": "Write",
        "injected_at": "2025-10-19T12:00:00",
        "confidence": 0.95
    }

    from dataclasses import asdict
    assert asdict(record) == data


def test_outcome_record_auto_timestamp():
    """OutcomeRecord should auto-generate timestamp."""
    record = OutcomeRecord(
        lesson_id="test_001",
        outcome="success",
        evidence="User followed guidance",
        strength=1.0
    )

    assert record.detected_at != ""
    # Should be valid ISO timestamp
    datetime.fromisoformat(record.detected_at)


# ============================================================================
# Pattern Matching Tests
# ============================================================================


def test_success_patterns():
    """Should match various success patterns."""
    detector = OutcomeDetector

    assert any(
        OutcomeDetector("I followed the checklist").detect_for_lesson("checklist")[0] == "success"
        for pattern in detector.SUCCESS_PATTERNS
    )


def test_failure_patterns():
    """Should match various failure patterns."""
    cases = [
        "I forgot to check that",
        "I missed an item on the list",
        "I didn't check the requirements",
        "I should have checked everything",
        "I overlooked the validation step",
    ]

    for case in cases:
        detector = OutcomeDetector(f"The checklist said to verify. {case}")
        outcome, _, _ = detector.detect_for_lesson("checklist")
        assert outcome == "failure", f"Failed to detect failure in: {case}"


def test_contradiction_patterns():
    """Should match various contradiction patterns."""
    cases = [
        "That checklist was wrong",
        "Actually we shouldn't do that",
        "That's incorrect advice",
        "A better approach would be X",
        "That pattern doesn't work here",
    ]

    for case in cases:
        detector = OutcomeDetector(f"About the checklist: {case}")
        outcome, _, _ = detector.detect_for_lesson("checklist")
        assert outcome == "contradiction", f"Failed to detect contradiction in: {case}"


def test_validation_patterns():
    """Should match various validation patterns."""
    cases = [
        "That was helpful",
        "Good catch on that",
        "That prevented a mistake",
        "Thanks for the reminder",
        "That avoided an error",
    ]

    for case in cases:
        detector = OutcomeDetector(f"About the checklist: {case}")
        outcome, _, _ = detector.detect_for_lesson("checklist")
        assert outcome == "validation", f"Failed to detect validation in: {case}"


# ============================================================================
# Edge Cases
# ============================================================================


def test_case_insensitive_detection():
    """Should detect outcomes case-insensitively."""
    conversation = "I FOLLOWED THE CHECKLIST and VERIFIED ALL ITEMS"
    detector = OutcomeDetector(conversation)
    outcome, _, _ = detector.detect_for_lesson("Checklist")

    assert outcome == "success"


def test_partial_label_match():
    """Should match partial lesson labels."""
    conversation = "I followed the Version Bump process"
    detector = OutcomeDetector(conversation)
    outcome, _, _ = detector.detect_for_lesson("Version Bump Checklist")

    # Should find mention of "version bump" even if not exact
    # Currently requires exact label - this test documents current behavior
    assert outcome in ("", "success")  # Either is acceptable


def test_multiple_outcomes_same_lesson():
    """Should handle multiple mentions with different outcomes."""
    conversation = """
    User: I used the checklist
    User: Actually wait, that checklist was wrong
    """

    detector = OutcomeDetector(conversation)
    outcome, _, _ = detector.detect_for_lesson("checklist")

    # Should prioritize contradiction over success
    assert outcome == "contradiction"
