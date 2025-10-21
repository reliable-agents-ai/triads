"""Integration tests for workflow matching system.

Test Coverage:
1. End-to-end workflow matching scenarios
2. Integration between matcher, keywords, and LLM fallback
3. Real-world use case validation
4. Module import and export verification
"""

import pytest
from triads.workflow_matching import (
    WorkflowMatcher,
    MatchResult,
    WORKFLOW_KEYWORDS,
    get_keywords,
    get_all_workflow_types,
    classify_with_llm,
)


class TestModuleImports:
    """Test module imports and exports."""

    def test_all_exports_available(self):
        """Test all expected exports are available."""
        from triads.workflow_matching import (
            WorkflowMatcher,
            MatchResult,
            WORKFLOW_KEYWORDS,
            get_keywords,
            get_all_workflow_types,
            classify_with_llm,
        )

        # All imports should succeed
        assert WorkflowMatcher is not None
        assert MatchResult is not None
        assert WORKFLOW_KEYWORDS is not None
        assert callable(get_keywords)
        assert callable(get_all_workflow_types)
        assert callable(classify_with_llm)

    def test_module_has_all_attribute(self):
        """Test module defines __all__ for explicit exports."""
        import triads.workflow_matching as wm
        assert hasattr(wm, "__all__")
        assert len(wm.__all__) == 6


class TestEndToEndWorkflowMatching:
    """Test end-to-end workflow matching scenarios."""

    @pytest.fixture
    def matcher(self):
        """Create matcher with full keyword library."""
        return WorkflowMatcher(WORKFLOW_KEYWORDS)

    def test_typical_bug_report(self, matcher):
        """Test typical bug report workflow."""
        message = (
            "I found a bug in the authentication system. When users try to login "
            "with special characters in their password, the system crashes with "
            "a null pointer exception. We need to fix this error ASAP."
        )

        result = matcher.match(message)

        # Should match bug-fix workflow
        assert result.workflow_type == "bug-fix"
        # Should have high confidence (multiple keywords)
        assert result.confidence > 0.5
        # Should match several keywords
        assert len(result.matched_keywords) >= 3
        # High confidence should not suggest generation
        if result.confidence >= 0.7:
            assert result.should_suggest_generation is False

    def test_typical_feature_request(self, matcher):
        """Test typical feature request workflow."""
        message = (
            "Let's add OAuth2 support to the application. We need to implement "
            "social login functionality and create new endpoints for the authentication flow."
        )

        result = matcher.match(message)

        # Should match feature-dev workflow
        assert result.workflow_type == "feature-dev"
        assert result.confidence > 0.3
        assert any(kw in result.matched_keywords
                   for kw in ["add", "implement", "create", "new"])

    def test_typical_performance_issue(self, matcher):
        """Test typical performance issue workflow."""
        message = (
            "The dashboard is really slow to load. I profiled the code and found "
            "a bottleneck in the database queries. We should optimize the caching "
            "to improve performance and reduce latency."
        )

        result = matcher.match(message)

        # Should match performance workflow
        assert result.workflow_type == "performance"
        assert result.confidence > 0.5
        assert any(kw in result.matched_keywords
                   for kw in ["slow", "optimize", "performance", "bottleneck"])

    def test_typical_refactoring_request(self, matcher):
        """Test typical refactoring request workflow."""
        message = (
            "The router code has a lot of technical debt. We should refactor it "
            "to improve maintainability. There's duplicate logic that should be "
            "extracted into a shared utility."
        )

        result = matcher.match(message)

        # Should match refactoring workflow
        assert result.workflow_type == "refactoring"
        assert result.confidence > 0.5
        assert any(kw in result.matched_keywords
                   for kw in ["refactor", "debt", "technical", "duplicate"])

    def test_typical_investigation_request(self, matcher):
        """Test typical investigation request workflow."""
        message = (
            "I need to investigate why the system is behaving strangely. "
            "Can you help me analyze the root cause of this issue and understand "
            "what's happening under the hood?"
        )

        result = matcher.match(message)

        # Should match investigation workflow
        assert result.workflow_type == "investigation"
        assert result.confidence > 0.5
        assert any(kw in result.matched_keywords
                   for kw in ["investigate", "why", "analyze", "understand"])


class TestWorkflowGapDetection:
    """Test gap detection (should_suggest_generation) scenarios."""

    @pytest.fixture
    def matcher(self):
        return WorkflowMatcher(WORKFLOW_KEYWORDS)

    def test_no_match_suggests_generation(self, matcher):
        """Test completely unrelated message suggests generation."""
        message = "The weather is nice today and I like pizza"

        result = matcher.match(message)

        assert result.workflow_type is None
        assert result.confidence == 0.0
        assert result.should_suggest_generation is True

    def test_low_confidence_suggests_generation(self, matcher):
        """Test low confidence match suggests generation."""
        # Single weak keyword
        message = "improve"

        result = matcher.match(message)

        # Might match something, but confidence should be low
        if result.confidence < 0.7:
            assert result.should_suggest_generation is True

    def test_high_confidence_no_suggestion(self, matcher):
        """Test high confidence match doesn't suggest generation."""
        message = "Fix the critical authentication bug causing crashes and errors"

        result = matcher.match(message)

        # Should have high confidence (4+ keyword matches)
        assert result.confidence >= 0.7
        # Should NOT suggest generation
        assert result.should_suggest_generation is False


class TestRealWorldExamples:
    """Test real-world examples from actual development scenarios."""

    @pytest.fixture
    def matcher(self):
        return WorkflowMatcher(WORKFLOW_KEYWORDS)

    def test_github_issue_bug(self, matcher):
        """Test GitHub-style bug issue."""
        message = (
            "**Bug Report**\n\n"
            "The login page crashes when clicking 'Remember Me'. "
            "Error: TypeError: Cannot read property 'checked' of null\n\n"
            "Steps to reproduce: 1. Go to /login 2. Click checkbox 3. Submit"
        )

        result = matcher.match(message)
        assert result.workflow_type == "bug-fix"

    def test_github_issue_feature(self, matcher):
        """Test GitHub-style feature request."""
        message = (
            "**Feature Request**\n\n"
            "Add support for dark mode theme. Users should be able to toggle "
            "between light and dark themes in settings."
        )

        result = matcher.match(message)
        assert result.workflow_type == "feature-dev"

    def test_slack_message_performance(self, matcher):
        """Test Slack-style performance complaint."""
        message = (
            "@here The API is super slow today. Some endpoints are timing out "
            "after 30 seconds. Can we optimize the database queries?"
        )

        result = matcher.match(message)
        assert result.workflow_type == "performance"

    def test_code_review_comment_refactoring(self, matcher):
        """Test code review comment about refactoring."""
        message = (
            "This function is doing too much. Let's extract the validation logic "
            "into a separate module to improve readability and reduce complexity."
        )

        result = matcher.match(message)
        assert result.workflow_type == "refactoring"

    def test_question_investigation(self, matcher):
        """Test question-style investigation request."""
        message = (
            "Why does the cache invalidation happen so frequently? "
            "I'd like to understand the root cause before making changes."
        )

        result = matcher.match(message)
        assert result.workflow_type == "investigation"


class TestMatcherWithCustomKeywords:
    """Test matcher works with custom keyword libraries."""

    def test_custom_workflow_single(self):
        """Test matcher with single custom workflow."""
        custom_keywords = {
            "documentation": {"docs", "documentation", "readme", "guide", "tutorial"}
        }

        matcher = WorkflowMatcher(custom_keywords)
        result = matcher.match("Update the documentation and readme files")

        assert result.workflow_type == "documentation"
        assert len(result.matched_keywords) >= 2

    def test_custom_workflow_multiple(self):
        """Test matcher with multiple custom workflows."""
        custom_keywords = {
            "security": {"security", "vulnerability", "exploit", "patch"},
            "deployment": {"deploy", "release", "production", "rollout"},
        }

        matcher = WorkflowMatcher(custom_keywords)

        # Test security match
        sec_result = matcher.match("Fix security vulnerability in auth")
        assert sec_result.workflow_type == "security"

        # Test deployment match
        deploy_result = matcher.match("Deploy to production environment")
        assert deploy_result.workflow_type == "deployment"


class TestKeywordLibraryIntegration:
    """Test integration between keyword library and matcher."""

    def test_all_workflows_matchable(self):
        """Test all workflows in library are matchable."""
        matcher = WorkflowMatcher(WORKFLOW_KEYWORDS)

        # Test each workflow can be matched
        test_messages = {
            "bug-fix": "fix the bug",
            "feature-dev": "add new feature",
            "performance": "optimize performance",
            "refactoring": "refactor code",
            "investigation": "investigate issue",
        }

        for expected_workflow, message in test_messages.items():
            result = matcher.match(message)
            assert result.workflow_type == expected_workflow, \
                f"Failed to match {expected_workflow} with '{message}'"

    def test_get_keywords_matches_library(self):
        """Test get_keywords returns same sets as library."""
        for workflow_type in get_all_workflow_types():
            keywords = get_keywords(workflow_type)
            assert keywords == WORKFLOW_KEYWORDS[workflow_type]


class TestLLMFallbackIntegration:
    """Test LLM fallback integration (Phase 1: stub only)."""

    def test_llm_fallback_stub_returns_none(self):
        """Test LLM fallback stub always returns None in Phase 1."""
        result = classify_with_llm("Any message")
        assert result is None

    def test_matcher_can_use_llm_fallback(self):
        """Test conceptual integration with LLM fallback.

        Phase 1: Just verify they can work together conceptually.
        Phase 2+: Actual integration where matcher calls LLM on low confidence.
        """
        matcher = WorkflowMatcher(WORKFLOW_KEYWORDS)
        message = "ambiguous request"

        # Get matcher result
        match_result = matcher.match(message)

        # If matcher has low/no confidence, could use LLM fallback (Phase 2+)
        if match_result.confidence < 0.7:
            llm_result = classify_with_llm(message)
            # Phase 1: LLM returns None
            assert llm_result is None
            # Phase 2+: Could use llm_result as fallback


class TestPerformanceIntegration:
    """Test performance across integrated components."""

    @pytest.fixture
    def matcher(self):
        return WorkflowMatcher(WORKFLOW_KEYWORDS)

    def test_end_to_end_performance(self, matcher):
        """Test end-to-end matching performance <100ms."""
        import time

        messages = [
            "Fix authentication bug",
            "Add OAuth support",
            "Optimize database queries",
            "Refactor router code",
            "Investigate performance issue",
        ] * 10  # 50 messages

        start = time.time()
        results = [matcher.match(msg) for msg in messages]
        duration = time.time() - start

        # All matches should complete quickly
        assert duration < 0.5  # <10ms per message on average
        assert len(results) == 50
        assert all(r.workflow_type is not None for r in results)


class TestErrorHandling:
    """Test error handling and edge cases."""

    @pytest.fixture
    def matcher(self):
        return WorkflowMatcher(WORKFLOW_KEYWORDS)

    def test_unicode_handling(self, matcher):
        """Test matcher handles unicode characters."""
        message = "Fix 🐛 bug in système d'authentification"
        result = matcher.match(message)
        # Should still match bug-fix
        assert result.workflow_type == "bug-fix"

    def test_very_long_message(self, matcher):
        """Test matcher handles very long messages."""
        # Create 10KB message
        long_message = " ".join(["fix", "bug", "error"] * 1000)
        result = matcher.match(long_message)

        # Should still match and perform well
        assert result.workflow_type == "bug-fix"
        assert result.confidence > 0.5

    def test_malformed_input_empty(self, matcher):
        """Test matcher handles empty input gracefully."""
        result = matcher.match("")
        assert result.workflow_type is None
        assert result.confidence == 0.0

    def test_malformed_input_whitespace(self, matcher):
        """Test matcher handles whitespace-only input."""
        result = matcher.match("   \n\t   ")
        assert result.workflow_type is None
        assert result.confidence == 0.0
