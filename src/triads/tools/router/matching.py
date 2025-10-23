"""Workflow matching using semantic keyword matching.

This module implements keyword-based matching with confidence scoring
for identifying workflow types from user messages.

Per ADR-013: Semantic keyword matching with confidence scoring and LLM fallback.
Performance Target: <100ms for keyword matching (ADR-013)

Moved from triads.workflow_matching.matcher as part of Phase 9 DDD refactoring.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Set
import re

import logging

logger = logging.getLogger(__name__)



@dataclass
class MatchResult:
    """Result of workflow matching attempt.

    Attributes:
        workflow_type: Matched workflow type (e.g., "bug-fix", "feature-dev")
                      or None if no confident match found
        confidence: Confidence score between 0.0 and 1.0
        matched_keywords: List of keywords that matched from the library
        should_suggest_generation: True if confidence < threshold
                                  or no match found, indicating user should be
                                  offered workflow generation
    """
    workflow_type: Optional[str]
    confidence: float
    matched_keywords: List[str]
    should_suggest_generation: bool

    def __post_init__(self):
        """Validate MatchResult fields."""
        if self.confidence < 0.0 or self.confidence > 1.0:
            raise ValueError(f"Confidence must be 0.0-1.0, got {self.confidence}")


class WorkflowMatcher:
    """Match user requests to workflow types using keyword matching.

    Uses semantic keyword matching with confidence scoring to identify
    which workflow type (if any) matches a user's natural language request.

    Algorithm:
    1. Normalize and tokenize user message
    2. For each workflow type, count keyword matches
    3. Calculate confidence: (matched / total) * boost factor
    4. Apply multi-match boost (1.2x if >1 keyword matches)
    5. Return best match if confidence >= threshold

    Performance: <100ms per match (ADR-013 requirement)

    Example:
        >>> matcher = WorkflowMatcher({"bug-fix": {"bug", "error", "crash"}})
        >>> result = matcher.match("There's a bug in the login")
        >>> result.workflow_type
        'bug-fix'
        >>> result.confidence > 0.5
        True
    """

    # Configuration constants (from config.py)
    # Imported here for self-containment per DDD principles
    CONFIDENCE_THRESHOLD = 0.7
    ABSOLUTE_WEIGHT = 0.7
    COVERAGE_WEIGHT = 0.3
    MAX_MATCHES_FOR_PERFECT = 4
    BOOST_MULTI_MATCH_HIGH = 1.15
    BOOST_MULTI_MATCH_MED = 1.1
    BOOST_THRESHOLD_HIGH = 3
    BOOST_THRESHOLD_MED = 2

    def __init__(
        self,
        keyword_library: Dict[str, Set[str]],
        confidence_threshold: Optional[float] = None
    ):
        """Initialize matcher with keyword library.

        Args:
            keyword_library: Map of workflow_type -> set of keywords
                Example: {"bug-fix": {"bug", "error", "crash", "fix"}}
            confidence_threshold: Optional threshold override (default: 0.7)

        Raises:
            ValueError: If keyword_library is empty or contains empty keyword sets
        """
        if not keyword_library:
            raise ValueError("keyword_library cannot be empty")

        for workflow_type, keywords in keyword_library.items():
            if not keywords:
                raise ValueError(f"Keyword set for '{workflow_type}' cannot be empty")

        self.keyword_library = keyword_library
        self.confidence_threshold = (
            confidence_threshold if confidence_threshold is not None
            else self.CONFIDENCE_THRESHOLD
        )

    def match(self, user_message: str) -> MatchResult:
        """Match user message to workflow type.

        Args:
            user_message: User's request text

        Returns:
            MatchResult with workflow type and confidence

        Performance: <100ms (ADR-013 requirement)
        """
        # Normalize message
        normalized = self._normalize_message(user_message)
        tokens = self._tokenize(normalized)

        # Score each workflow type
        scores = {}
        matched = {}

        for workflow_type, keywords in self.keyword_library.items():
            matched_kw = keywords.intersection(tokens)
            if matched_kw:
                # Improved scoring: balance absolute matches with coverage
                # This gives higher weight to absolute number of matches
                num_matched = len(matched_kw)
                coverage = num_matched / len(keywords)

                # Absolute match component (caps at MAX_MATCHES_FOR_PERFECT = 1.0)
                # Each match worth (1 / MAX_MATCHES_FOR_PERFECT) base score
                absolute_component = min(
                    num_matched / self.MAX_MATCHES_FOR_PERFECT, 1.0
                ) * self.ABSOLUTE_WEIGHT

                # Coverage component (less weight to avoid penalizing large keyword sets)
                coverage_component = coverage * self.COVERAGE_WEIGHT

                # Combined score
                score = min(absolute_component + coverage_component, 1.0)

                # Boost if multiple keywords match (stronger signal)
                if num_matched >= self.BOOST_THRESHOLD_HIGH:
                    score = min(score * self.BOOST_MULTI_MATCH_HIGH, 1.0)
                elif num_matched >= self.BOOST_THRESHOLD_MED:
                    score = min(score * self.BOOST_MULTI_MATCH_MED, 1.0)

                scores[workflow_type] = score
                matched[workflow_type] = list(matched_kw)

        # Find best match
        if not scores:
            return MatchResult(
                workflow_type=None,
                confidence=0.0,
                matched_keywords=[],
                should_suggest_generation=True  # No match, suggest generation
            )

        best_workflow = max(scores, key=scores.get)
        best_score = scores[best_workflow]

        # ADR-013: Confidence threshold check
        # Low confidence (< threshold) suggests generation
        return MatchResult(
            workflow_type=best_workflow,
            confidence=best_score,
            matched_keywords=matched[best_workflow],
            should_suggest_generation=(best_score < self.confidence_threshold)
        )

    def _normalize_message(self, message: str) -> str:
        """Normalize message for matching.

        Args:
            message: Raw user message

        Returns:
            Normalized lowercase message
        """
        return message.lower().strip()

    def _tokenize(self, message: str) -> Set[str]:
        """Extract tokens from message.

        Args:
            message: Normalized message

        Returns:
            Set of word tokens extracted from message

        Implementation:
            - Splits on word boundaries
            - Removes punctuation
            - Filters out very short tokens (<2 chars) to reduce noise
        """
        # Split on word boundaries, remove punctuation
        tokens = re.findall(r'\b\w+\b', message)

        # Filter out very short tokens (noise) and convert to set
        return {token for token in tokens if len(token) >= 2}
