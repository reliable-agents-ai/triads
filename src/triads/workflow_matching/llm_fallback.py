"""LLM-based workflow classification fallback.

This module provides LLM-powered classification for cases where keyword
matching fails or produces low confidence results.

Per ADR-013: LLM fallback for ambiguous cases
Performance Target: <5s for LLM classification

Phase 1: Stub implementation (returns None)
Phase 2: Full LLM integration with Claude API
Phase 3: Integration with Supervisor routing logic
"""

from typing import Optional

from triads.workflow_matching import config


def classify_with_llm(
    user_message: str,
    confidence_threshold: float = config.CONFIDENCE_THRESHOLD
) -> Optional[str]:
    """Use LLM to classify workflow type when keyword matching fails.

    This function provides a fallback mechanism for cases where:
    1. No keywords match (keyword confidence = 0.0)
    2. Multiple workflows match with similar confidence
    3. Keyword confidence < threshold but message clearly indicates work type

    Args:
        user_message: User's request text
        confidence_threshold: Minimum confidence for LLM classification
                             (default: config.CONFIDENCE_THRESHOLD per ADR-013)

    Returns:
        Workflow type if LLM confident, None otherwise

    Performance:
        Phase 1: Immediate return (stub)
        Phase 2+: <5s for LLM API call (ADR-013 requirement)

    Note:
        Phase 1 implementation is a stub that always returns None.
        Full LLM integration will be implemented in Phase 2 with:
        - Claude API integration
        - Prompt engineering for workflow classification
        - Timeout enforcement (<5s)
        - Error handling and graceful degradation

    Example (Phase 2+):
        >>> # When keyword matching is ambiguous:
        >>> result = classify_with_llm("The code needs better structure")
        >>> result  # May return "refactoring" via LLM
        'refactoring'

        >>> # When no clear match:
        >>> result = classify_with_llm("Random unrelated text")
        >>> result  # LLM returns None (no confident match)
        None
    """
    # Phase 1: Stub implementation - always return None
    # Phase 2 will add:
    # 1. Claude API client initialization
    # 2. Workflow classification prompt
    # 3. Response parsing
    # 4. Confidence thresholding
    # 5. Timeout enforcement (<5s)
    # 6. Error handling

    return None
