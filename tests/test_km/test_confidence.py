"""Tests for confidence calculation and management."""

import pytest

from triads.km.confidence import (
    SOURCE_USER_CORRECTION,
    SOURCE_REPEATED_MISTAKE,
    SOURCE_PROCESS_KNOWLEDGE_BLOCK,
    SOURCE_AGENT_INFERENCE,
    SOURCE_SUGGESTION,
    OUTCOME_SUCCESS,
    OUTCOME_FAILURE,
    OUTCOME_CONFIRMATION,
    OUTCOME_CONTRADICTION,
    STATUS_ACTIVE,
    STATUS_NEEDS_VALIDATION,
    STATUS_DEPRECATED,
    STATUS_ARCHIVED,
    calculate_initial_confidence,
    assign_status,
    update_confidence,
    check_deprecation,
    validate_confidence_value,
    get_confidence_band,
)


class TestCalculateInitialConfidence:
    """Test initial confidence calculation."""

    def test_user_correction_high_confidence(self):
        """User corrections should have high confidence (0.95)."""
        confidence = calculate_initial_confidence(
            SOURCE_USER_CORRECTION,
            "CRITICAL"
        )
        assert confidence == 0.95

    def test_repeated_mistake_with_repetition_boost(self):
        """Repeated mistakes should get confidence boost from repetition."""
        # 2 repetitions
        conf_2 = calculate_initial_confidence(
            SOURCE_REPEATED_MISTAKE,
            "HIGH",
            repetition_count=2
        )
        assert conf_2 >= 0.80

        # 3 repetitions (higher than 2)
        conf_3 = calculate_initial_confidence(
            SOURCE_REPEATED_MISTAKE,
            "HIGH",
            repetition_count=3
        )
        assert conf_3 > conf_2
        assert conf_3 <= 0.95  # Capped

    def test_process_knowledge_block_high_confidence(self):
        """Explicit [PROCESS_KNOWLEDGE] blocks should have high confidence."""
        confidence = calculate_initial_confidence(
            SOURCE_PROCESS_KNOWLEDGE_BLOCK,
            "MEDIUM"
        )
        assert confidence == 0.90

    def test_agent_inference_low_confidence(self):
        """Agent inferences should have lower confidence."""
        confidence = calculate_initial_confidence(
            SOURCE_AGENT_INFERENCE,
            "MEDIUM"
        )
        assert confidence == 0.65

    def test_suggestion_lowest_confidence(self):
        """Suggestions should have lowest confidence."""
        confidence = calculate_initial_confidence(
            SOURCE_SUGGESTION,
            "MEDIUM"
        )
        assert confidence == 0.50

    def test_critical_priority_boost(self):
        """CRITICAL priority should boost confidence."""
        conf_medium = calculate_initial_confidence(
            SOURCE_SUGGESTION,
            "MEDIUM"
        )
        conf_critical = calculate_initial_confidence(
            SOURCE_SUGGESTION,
            "CRITICAL"
        )
        assert conf_critical > conf_medium

    def test_conflicting_evidence_penalty(self):
        """Conflicting evidence should reduce confidence."""
        context_with_conflict = {"conflicting_evidence": True}

        conf_without = calculate_initial_confidence(
            SOURCE_AGENT_INFERENCE,
            "MEDIUM"
        )
        conf_with = calculate_initial_confidence(
            SOURCE_AGENT_INFERENCE,
            "MEDIUM",
            context=context_with_conflict
        )
        assert conf_with < conf_without

    def test_confidence_bounds(self):
        """Confidence should always be in range [0.50, 0.95]."""
        # Try all sources
        sources = [
            SOURCE_USER_CORRECTION,
            SOURCE_REPEATED_MISTAKE,
            SOURCE_PROCESS_KNOWLEDGE_BLOCK,
            SOURCE_AGENT_INFERENCE,
            SOURCE_SUGGESTION,
        ]

        for source in sources:
            conf = calculate_initial_confidence(source, "MEDIUM")
            assert 0.50 <= conf <= 0.95


class TestAssignStatus:
    """Test status assignment based on confidence."""

    def test_high_confidence_active(self):
        """Confidence >= 0.80 should be active."""
        assert assign_status(0.85, "MEDIUM") == STATUS_ACTIVE
        assert assign_status(0.95, "LOW") == STATUS_ACTIVE

    def test_medium_confidence_critical_active(self):
        """Confidence >= 0.70 with CRITICAL/HIGH priority should be active."""
        assert assign_status(0.72, "CRITICAL") == STATUS_ACTIVE
        assert assign_status(0.75, "HIGH") == STATUS_ACTIVE

    def test_medium_confidence_medium_priority_active(self):
        """Confidence >= 0.70 with MEDIUM/LOW priority should still be active."""
        assert assign_status(0.72, "MEDIUM") == STATUS_ACTIVE
        assert assign_status(0.75, "LOW") == STATUS_ACTIVE

    def test_low_confidence_needs_validation(self):
        """Confidence < 0.70 should need validation."""
        assert assign_status(0.65, "MEDIUM") == STATUS_NEEDS_VALIDATION
        assert assign_status(0.60, "HIGH") == STATUS_NEEDS_VALIDATION

    def test_very_low_confidence_archived(self):
        """Confidence < 0.50 should be archived."""
        assert assign_status(0.45, "MEDIUM") == STATUS_ARCHIVED
        assert assign_status(0.30, "CRITICAL") == STATUS_ARCHIVED


class TestUpdateConfidence:
    """Test Bayesian confidence updating."""

    def test_success_increases_confidence(self):
        """Success outcome should increase confidence by 15%."""
        initial = 0.80
        updated = update_confidence(initial, OUTCOME_SUCCESS)
        assert updated == pytest.approx(0.92, abs=0.01)  # 0.80 * 1.15

    def test_failure_decreases_confidence(self):
        """Failure outcome should decrease confidence by 40%."""
        initial = 0.80
        updated = update_confidence(initial, OUTCOME_FAILURE)
        assert updated == pytest.approx(0.48, abs=0.01)  # 0.80 * 0.60

    def test_confirmation_increases_confidence(self):
        """Confirmation outcome should increase confidence by 10%."""
        initial = 0.80
        updated = update_confidence(initial, OUTCOME_CONFIRMATION)
        assert updated == pytest.approx(0.88, abs=0.01)  # 0.80 * 1.10

    def test_contradiction_decreases_confidence(self):
        """Contradiction outcome should decrease confidence by 60%."""
        initial = 0.80
        updated = update_confidence(initial, OUTCOME_CONTRADICTION)
        assert updated == pytest.approx(0.32, abs=0.01)  # 0.80 * 0.40

    def test_asymmetric_updates(self):
        """Failures should be penalized more than successes rewarded."""
        initial = 0.80

        success_delta = update_confidence(initial, OUTCOME_SUCCESS) - initial
        failure_delta = initial - update_confidence(initial, OUTCOME_FAILURE)

        # Failure penalty should be larger than success boost
        assert failure_delta > success_delta

    def test_confidence_capped_at_99(self):
        """Confidence should never exceed 0.99 (epistemic humility)."""
        high_conf = 0.95
        updated = update_confidence(high_conf, OUTCOME_SUCCESS)
        assert updated <= 0.99

    def test_confidence_floored_at_10(self):
        """Confidence should never go below 0.10 (audit trail)."""
        low_conf = 0.15
        updated = update_confidence(low_conf, OUTCOME_CONTRADICTION)
        assert updated >= 0.10


class TestCheckDeprecation:
    """Test deprecation criteria."""

    def test_low_confidence_deprecates(self):
        """Confidence < 0.30 should trigger deprecation."""
        lesson = {
            "confidence": 0.25,
            "failure_count": 0,
            "success_count": 0,
            "contradiction_count": 0,
        }
        assert check_deprecation(lesson) is True

    def test_consistent_failures_deprecates(self):
        """3+ failures with no successes should trigger deprecation."""
        lesson = {
            "confidence": 0.70,
            "failure_count": 3,
            "success_count": 0,
            "contradiction_count": 0,
        }
        assert check_deprecation(lesson) is True

    def test_multiple_contradictions_deprecates(self):
        """2+ contradictions should trigger deprecation."""
        lesson = {
            "confidence": 0.70,
            "failure_count": 0,
            "success_count": 0,
            "contradiction_count": 2,
        }
        assert check_deprecation(lesson) is True

    def test_healthy_lesson_not_deprecated(self):
        """Healthy lessons should not be deprecated."""
        lesson = {
            "confidence": 0.80,
            "failure_count": 1,
            "success_count": 5,
            "contradiction_count": 0,
        }
        assert check_deprecation(lesson) is False

    def test_some_failures_ok_if_confidence_high(self):
        """Some failures acceptable if confidence still high."""
        lesson = {
            "confidence": 0.75,
            "failure_count": 2,
            "success_count": 0,
            "contradiction_count": 0,
        }
        # Not deprecated - need 3 failures OR low confidence
        assert check_deprecation(lesson) is False


class TestValidateConfidenceValue:
    """Test confidence value validation."""

    def test_valid_confidence_unchanged(self):
        """Valid confidence values should pass through."""
        assert validate_confidence_value(0.85) == 0.85
        assert validate_confidence_value(0.50) == 0.50
        assert validate_confidence_value(1.0) == 1.0
        assert validate_confidence_value(0.0) == 0.0

    def test_invalid_type_returns_default(self):
        """Invalid types should return default 0.70."""
        assert validate_confidence_value("0.85") == 0.70
        assert validate_confidence_value(None) == 0.70
        assert validate_confidence_value([0.85]) == 0.70

    def test_out_of_bounds_clamped(self):
        """Out of bounds values should be clamped to [0.0, 1.0]."""
        assert validate_confidence_value(1.5) == 1.0
        assert validate_confidence_value(-0.2) == 0.0


class TestGetConfidenceBand:
    """Test confidence band classification."""

    def test_very_high_band(self):
        """Confidence >= 0.90 should be in 0.90-1.00 band."""
        assert get_confidence_band(0.90) == "0.90-1.00"
        assert get_confidence_band(0.95) == "0.90-1.00"
        assert get_confidence_band(0.99) == "0.90-1.00"

    def test_high_band(self):
        """Confidence 0.80-0.89 should be in 0.80-0.90 band."""
        assert get_confidence_band(0.80) == "0.80-0.90"
        assert get_confidence_band(0.85) == "0.80-0.90"
        assert get_confidence_band(0.89) == "0.80-0.90"

    def test_medium_band(self):
        """Confidence 0.70-0.79 should be in 0.70-0.80 band."""
        assert get_confidence_band(0.70) == "0.70-0.80"
        assert get_confidence_band(0.75) == "0.70-0.80"
        assert get_confidence_band(0.79) == "0.70-0.80"

    def test_low_band(self):
        """Confidence < 0.70 should be in 0.60-0.70 band."""
        assert get_confidence_band(0.60) == "0.60-0.70"
        assert get_confidence_band(0.65) == "0.60-0.70"
        assert get_confidence_band(0.50) == "0.60-0.70"


class TestConfidenceIntegration:
    """Integration tests for full confidence lifecycle."""

    def test_user_correction_lifecycle(self):
        """Test full lifecycle for user correction."""
        # 1. Calculate initial confidence
        confidence = calculate_initial_confidence(
            SOURCE_USER_CORRECTION,
            "CRITICAL"
        )
        assert confidence == 0.95

        # 2. Assign status
        status = assign_status(confidence, "CRITICAL")
        assert status == STATUS_ACTIVE

        # 3. Success boosts confidence
        confidence = update_confidence(confidence, OUTCOME_SUCCESS)
        assert confidence > 0.95
        assert confidence <= 0.99  # Capped

        # 4. Lesson should not be deprecated
        lesson = {
            "confidence": confidence,
            "success_count": 1,
            "failure_count": 0,
            "contradiction_count": 0,
        }
        assert check_deprecation(lesson) is False

    def test_agent_inference_self_correction(self):
        """Test self-correction for wrong agent inference."""
        # 1. Low initial confidence
        confidence = calculate_initial_confidence(
            SOURCE_AGENT_INFERENCE,
            "MEDIUM"
        )
        assert confidence == 0.65

        # 2. Status: needs validation
        status = assign_status(confidence, "MEDIUM")
        assert status == STATUS_NEEDS_VALIDATION

        # 3. Multiple failures
        for _ in range(3):
            confidence = update_confidence(confidence, OUTCOME_FAILURE)

        # 4. Should be deprecated
        lesson = {
            "confidence": confidence,
            "success_count": 0,
            "failure_count": 3,
            "contradiction_count": 0,
        }
        assert check_deprecation(lesson) is True

    def test_uncertain_lesson_validated(self):
        """Test uncertain lesson becoming active after validation."""
        # 1. Uncertain initial confidence
        confidence = calculate_initial_confidence(
            SOURCE_AGENT_INFERENCE,
            "MEDIUM"
        )
        assert confidence == 0.65

        # 2. Needs validation
        status = assign_status(confidence, "MEDIUM")
        assert status == STATUS_NEEDS_VALIDATION

        # 3. User validates
        confidence = update_confidence(confidence, OUTCOME_CONFIRMATION)

        # 4. Should now be active
        new_status = assign_status(confidence, "MEDIUM")
        assert new_status == STATUS_ACTIVE
