"""Confidence calculation and management for process knowledge.

This module implements evidence-based confidence scoring for process knowledge nodes,
following research patterns from RLHF, Bayesian updating, and online learning.

Research Foundation:
- RLHF (OpenAI, Anthropic): Trust scores determine update magnitude
- Bayesian updating: Prior + evidence → posterior confidence
- Online learning: Continuous refinement from feedback stream
- Confidence calibration: Ensure scores match accuracy
"""

from __future__ import annotations

from typing import Any


# Confidence thresholds (research-informed)
CONFIDENCE_THRESHOLDS = {
    "activation": 0.70,  # Minimum confidence to activate lesson
    "deprecation": 0.30,  # Below this, auto-deprecate
    "cap_max": 0.99,     # Maximum confidence (epistemic humility)
    "floor_min": 0.10,   # Minimum confidence (audit trail)
}

# Status values
STATUS_ACTIVE = "active"
STATUS_NEEDS_VALIDATION = "needs_validation"
STATUS_DEPRECATED = "deprecated"
STATUS_ARCHIVED = "archived"

# Source types for confidence calculation
SOURCE_USER_CORRECTION = "user_correction"
SOURCE_REPEATED_MISTAKE = "repeated_mistake"
SOURCE_PROCESS_KNOWLEDGE_BLOCK = "process_knowledge_block"
SOURCE_AGENT_INFERENCE = "agent_inference"
SOURCE_SUGGESTION = "suggestion"

# Outcome types for Bayesian updating
OUTCOME_SUCCESS = "success"
OUTCOME_FAILURE = "failure"
OUTCOME_CONFIRMATION = "confirmation"
OUTCOME_CONTRADICTION = "contradiction"


def calculate_initial_confidence(
    source: str,
    priority: str,
    repetition_count: int = 1,
    context: dict[str, Any] | None = None
) -> float:
    """Calculate initial confidence based on evidence source and context.

    Research basis:
    - Stronger evidence (user correction) → higher confidence
    - Repetition confirms pattern → confidence boost
    - High-stakes context (CRITICAL) → confidence boost
    - Weak evidence (agent guess) → lower confidence

    Args:
        source: Source of the lesson (user_correction, repeated_mistake, etc.)
        priority: Priority level (CRITICAL, HIGH, MEDIUM, LOW)
        repetition_count: How many times pattern has occurred (for repeated_mistake)
        context: Additional context dict (optional)

    Returns:
        float: Initial confidence score in range [0.50, 0.95]

    Examples:
        >>> calculate_initial_confidence("user_correction", "CRITICAL")
        0.95
        >>> calculate_initial_confidence("repeated_mistake", "HIGH", repetition_count=3)
        0.85
        >>> calculate_initial_confidence("agent_inference", "MEDIUM")
        0.65
    """
    # Base confidence from source
    base_confidences = {
        SOURCE_USER_CORRECTION: 0.95,         # Strongest signal (human identified error)
        SOURCE_REPEATED_MISTAKE: 0.75,        # Will be boosted by repetition
        SOURCE_PROCESS_KNOWLEDGE_BLOCK: 0.90, # Explicit, structured
        SOURCE_AGENT_INFERENCE: 0.65,         # Weak signal
        SOURCE_SUGGESTION: 0.50,              # Very weak
    }

    confidence = base_confidences.get(source, 0.60)

    # Boost for repetition (research: repeated patterns more reliable)
    if source == SOURCE_REPEATED_MISTAKE and repetition_count >= 2:
        repetition_boost = min(0.15, (repetition_count - 1) * 0.05)
        confidence += repetition_boost

    # Boost for CRITICAL priority (high-stakes context)
    if priority == "CRITICAL":
        confidence = min(0.95, confidence * 1.05)

    # Penalty for conflicting evidence (if provided in context)
    if context and context.get("conflicting_evidence"):
        confidence *= 0.85

    # Ensure bounds [0.50, 0.95]
    return max(0.50, min(0.95, confidence))


def assign_status(confidence: float, priority: str) -> str:
    """Assign lesson status based on confidence and priority.

    Rules (research-informed):
    - confidence >= 0.80 → active (learn immediately)
    - 0.70 <= confidence < 0.80 AND priority in [CRITICAL, HIGH] → active
    - confidence >= 0.70 AND priority in [MEDIUM, LOW] → active
    - confidence < 0.70 → needs_validation (flag for optional review)

    Args:
        confidence: Confidence score (0.0 to 1.0)
        priority: Priority level (CRITICAL, HIGH, MEDIUM, LOW)

    Returns:
        str: Status value (active, needs_validation, deprecated, archived)

    Examples:
        >>> assign_status(0.85, "MEDIUM")
        'active'
        >>> assign_status(0.72, "CRITICAL")
        'active'
        >>> assign_status(0.65, "MEDIUM")
        'needs_validation'
    """
    if confidence >= 0.80:
        return STATUS_ACTIVE
    elif confidence >= 0.70:
        # Lower bar for important contexts
        if priority in ["CRITICAL", "HIGH"]:
            return STATUS_ACTIVE
        else:
            return STATUS_ACTIVE  # Still active, but less confident
    elif confidence >= 0.50:
        return STATUS_NEEDS_VALIDATION
    else:
        return STATUS_ARCHIVED  # Too weak to be useful


def update_confidence(
    current_confidence: float,
    outcome: str,
) -> float:
    """Update confidence based on outcome (Bayesian updating pattern).

    Research basis:
    - Success: Modest increase (evidence confirms hypothesis)
    - Failure: Significant decrease (evidence contradicts hypothesis)
    - Contradiction: Strong decrease (human override signal)
    - Confirmation: Modest increase (human validation)

    Asymmetry rationale (research-informed):
    - Negative evidence should outweigh positive (prevent overconfidence)
    - Human feedback (contradiction/confirmation) stronger than outcomes

    Args:
        current_confidence: Current confidence score
        outcome: Outcome type (success, failure, contradiction, confirmation)

    Returns:
        float: Updated confidence score, bounded [0.10, 0.99]

    Examples:
        >>> update_confidence(0.80, "success")
        0.92  # +15%
        >>> update_confidence(0.80, "failure")
        0.48  # -40%
        >>> update_confidence(0.80, "contradiction")
        0.32  # -60%
    """
    multipliers = {
        OUTCOME_SUCCESS: 1.15,       # +15% (lesson worked)
        OUTCOME_CONFIRMATION: 1.10,  # +10% (human validated)
        OUTCOME_FAILURE: 0.60,       # -40% (lesson didn't work)
        OUTCOME_CONTRADICTION: 0.40, # -60% (human rejected)
    }

    multiplier = multipliers.get(outcome, 1.0)
    new_confidence = current_confidence * multiplier

    # Cap at 0.99 (never 100% certain - epistemic humility)
    # Floor at 0.10 (keep for audit trail, but effectively deprecated)
    return max(
        CONFIDENCE_THRESHOLDS["floor_min"],
        min(CONFIDENCE_THRESHOLDS["cap_max"], new_confidence)
    )


def check_deprecation(lesson: dict[str, Any]) -> bool:
    """Determine if lesson should be deprecated.

    Rules (research-informed):
    - confidence < 0.30 → deprecated (too unreliable)
    - failure_count >= 3 AND success_count == 0 → deprecated (consistently wrong)
    - contradiction_count >= 2 → deprecated (human rejected multiple times)

    Args:
        lesson: Lesson dictionary with confidence and outcome counts

    Returns:
        bool: True if should be deprecated, False otherwise

    Examples:
        >>> check_deprecation({"confidence": 0.25, "failure_count": 0, "success_count": 0})
        True
        >>> check_deprecation({"confidence": 0.70, "failure_count": 3, "success_count": 0})
        True
        >>> check_deprecation({"confidence": 0.80, "failure_count": 1, "success_count": 5})
        False
    """
    # Rule 1: Confidence too low
    if lesson.get("confidence", 1.0) < CONFIDENCE_THRESHOLDS["deprecation"]:
        return True

    # Rule 2: Consistently failing
    failure_count = lesson.get("failure_count", 0)
    success_count = lesson.get("success_count", 0)
    if failure_count >= 3 and success_count == 0:
        return True

    # Rule 3: Multiple human contradictions
    contradiction_count = lesson.get("contradiction_count", 0)
    if contradiction_count >= 2:
        return True

    return False


def validate_confidence_value(confidence: Any) -> float:
    """Validate and sanitize confidence score.

    Security: Prevent confidence manipulation attacks.

    Args:
        confidence: Confidence value to validate

    Returns:
        float: Validated confidence in range [0.0, 1.0]
    """
    # Type check
    if not isinstance(confidence, (int, float)):
        return 0.70  # Conservative default

    # Bounds check
    if confidence < 0.0 or confidence > 1.0:
        return max(0.0, min(1.0, confidence))

    return float(confidence)


def get_confidence_band(confidence: float) -> str:
    """Get confidence band for calibration reporting.

    Args:
        confidence: Confidence score

    Returns:
        str: Band label (e.g., "0.90-1.00")
    """
    if confidence >= 0.90:
        return "0.90-1.00"
    elif confidence >= 0.80:
        return "0.80-0.90"
    elif confidence >= 0.70:
        return "0.70-0.80"
    else:
        return "0.60-0.70"
