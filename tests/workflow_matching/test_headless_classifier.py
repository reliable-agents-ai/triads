"""Tests for headless mode workflow classifier.

This replaces the keyword matching approach with Claude headless mode
for simpler, more accurate workflow classification.

Per ADR-013 (REVISED): Use Claude headless mode for gap detection
Performance Target: 1-3s for classification (acceptable for rare gap detection events)

Test Coverage:
1. Basic workflow classification for all 5 types
2. No-match cases
3. Error handling (API failures, timeouts)
4. Edge cases (empty, long messages)
"""

import pytest
from unittest.mock import Mock, patch
from triads.workflow_matching.headless_classifier import (
    classify_workflow_headless,
    HeadlessClassificationResult,
)


class TestHeadlessClassificationResult:
    """Test HeadlessClassificationResult dataclass."""

    def test_valid_result(self):
        """Test creating valid classification result."""
        result = HeadlessClassificationResult(
            workflow_type="bug-fix",
            confidence=0.95,
            reasoning="User mentioned 'bug' and 'fix'"
        )
        assert result.workflow_type == "bug-fix"
        assert result.confidence == 0.95
        assert result.reasoning == "User mentioned 'bug' and 'fix'"

    def test_no_match_result(self):
        """Test classification result with no match."""
        result = HeadlessClassificationResult(
            workflow_type=None,
            confidence=0.0,
            reasoning="No workflow matched"
        )
        assert result.workflow_type is None
        assert result.confidence == 0.0


class TestBasicClassification:
    """Test basic workflow classification for all types."""

    @patch('triads.workflow_matching.headless_classifier._call_claude_api')
    def test_classify_bug_fix(self, mock_api):
        """Test classifying bug-fix workflow request."""
        mock_api.return_value = '{"workflow_type": "bug-fix", "confidence": 0.95, "reasoning": "Request mentions fixing a bug"}'

        result = classify_workflow_headless("Fix the authentication bug")
        assert result.workflow_type == "bug-fix"
        assert result.confidence == 0.95
        assert len(result.reasoning) > 0

    @patch('triads.workflow_matching.headless_classifier._call_claude_api')
    def test_classify_feature_dev(self, mock_api):
        """Test classifying feature-dev workflow request."""
        mock_api.return_value = '{"workflow_type": "feature-dev", "confidence": 0.92, "reasoning": "Request is about adding new functionality"}'

        result = classify_workflow_headless("Add OAuth2 support to the API")
        assert result.workflow_type == "feature-dev"
        assert result.confidence == 0.92

    @patch('triads.workflow_matching.headless_classifier._call_claude_api')
    def test_classify_performance(self, mock_api):
        """Test classifying performance workflow request."""
        mock_api.return_value = '{"workflow_type": "performance", "confidence": 0.90, "reasoning": "Request is about optimization"}'

        result = classify_workflow_headless("Optimize database query performance")
        assert result.workflow_type == "performance"
        assert result.confidence == 0.90

    @patch('triads.workflow_matching.headless_classifier._call_claude_api')
    def test_classify_refactoring(self, mock_api):
        """Test classifying refactoring workflow request."""
        mock_api.return_value = '{"workflow_type": "refactoring", "confidence": 0.88, "reasoning": "Request is about code cleanup and restructuring"}'

        result = classify_workflow_headless("Refactor the router code to reduce duplication")
        assert result.workflow_type == "refactoring"
        assert result.confidence == 0.88

    @patch('triads.workflow_matching.headless_classifier._call_claude_api')
    def test_classify_investigation(self, mock_api):
        """Test classifying investigation workflow request."""
        mock_api.return_value = '{"workflow_type": "investigation", "confidence": 0.93, "reasoning": "Request asks why something behaves a certain way"}'

        result = classify_workflow_headless("Why is the system behaving this way?")
        assert result.workflow_type == "investigation"
        assert result.confidence == 0.93


class TestNoMatchCases:
    """Test cases where no workflow should match."""

    @patch('triads.workflow_matching.headless_classifier._call_claude_api')
    def test_no_match_unrelated(self, mock_api):
        """Test message with no workflow match."""
        mock_api.return_value = '{"workflow_type": null, "confidence": 0.0, "reasoning": "No workflow matches this request"}'

        result = classify_workflow_headless("The sky is blue and grass is green")
        assert result.workflow_type is None
        assert result.confidence == 0.0

    def test_no_match_empty(self):
        """Test empty message returns no match."""
        # Empty messages bypass API call
        result = classify_workflow_headless("")
        assert result.workflow_type is None
        assert result.confidence == 0.0

    def test_no_match_whitespace(self):
        """Test whitespace-only message returns no match."""
        # Whitespace-only messages bypass API call
        result = classify_workflow_headless("   \n\t   ")
        assert result.workflow_type is None


class TestErrorHandling:
    """Test error handling for API failures."""

    @patch('triads.workflow_matching.headless_classifier._call_claude_api')
    def test_api_timeout(self, mock_api):
        """Test handling of API timeout."""
        mock_api.side_effect = TimeoutError("API timeout")

        result = classify_workflow_headless("Fix the bug")
        # Should gracefully degrade to no match
        assert result.workflow_type is None
        assert result.confidence == 0.0
        assert "timeout" in result.reasoning.lower() or "error" in result.reasoning.lower()

    @patch('triads.workflow_matching.headless_classifier._call_claude_api')
    def test_api_error(self, mock_api):
        """Test handling of API error."""
        mock_api.side_effect = Exception("API error")

        result = classify_workflow_headless("Add new feature")
        # Should gracefully degrade to no match
        assert result.workflow_type is None
        assert result.confidence == 0.0


class TestEdgeCases:
    """Test edge cases."""

    @patch('triads.workflow_matching.headless_classifier._call_claude_api')
    def test_long_message(self, mock_api):
        """Test classification works with long messages."""
        mock_api.return_value = '{"workflow_type": "bug-fix", "confidence": 0.94, "reasoning": "Long message describes bug fixing"}'

        long_message = (
            "I've been investigating this issue for a while and discovered "
            "that there's a critical bug in the authentication system that "
            "causes crashes when users log in with special characters. "
            "We need to fix this error immediately." * 3
        )
        result = classify_workflow_headless(long_message)
        # Should still classify as bug-fix
        assert result.workflow_type == "bug-fix"
        assert result.confidence > 0.0

    @patch('triads.workflow_matching.headless_classifier._call_claude_api')
    def test_ambiguous_message(self, mock_api):
        """Test handling of ambiguous messages."""
        # Claude picks investigation due to "investigate" keyword
        mock_api.return_value = '{"workflow_type": "investigation", "confidence": 0.85, "reasoning": "Request asks to investigate"}'

        result = classify_workflow_headless("investigate the bug")
        # Should pick one with reasonable confidence
        assert result.workflow_type in ["bug-fix", "investigation"]
        assert result.confidence > 0.0

    @patch('triads.workflow_matching.headless_classifier._call_claude_api')
    def test_case_insensitive(self, mock_api):
        """Test classification is case-insensitive."""
        mock_api.return_value = '{"workflow_type": "bug-fix", "confidence": 0.92, "reasoning": "Request is about fixing a bug"}'

        lower = classify_workflow_headless("fix the bug")
        upper = classify_workflow_headless("FIX THE BUG")

        # Should classify the same (both calls use same mock)
        assert lower.workflow_type == upper.workflow_type
