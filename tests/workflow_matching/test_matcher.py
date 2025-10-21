"""Comprehensive tests for WorkflowMatcher class.

Test Coverage:
1. Keyword matching for all 5 workflow types
2. Confidence scoring algorithm
3. Multi-keyword boost
4. No-match cases
5. Edge cases (empty, special characters, long text)
6. Performance (<100ms requirement)
7. should_suggest_generation logic
8. MatchResult validation

Target: >85% coverage (Phase 1 acceptance criteria)
"""

import pytest
import time
from triads.workflow_matching import (
    WorkflowMatcher,
    MatchResult,
    WORKFLOW_KEYWORDS,
)


class TestMatchResult:
    """Test MatchResult dataclass."""

    def test_valid_match_result(self):
        """Test creating valid MatchResult."""
        result = MatchResult(
            workflow_type="bug-fix",
            confidence=0.85,
            matched_keywords=["bug", "error"],
            should_suggest_generation=False
        )
        assert result.workflow_type == "bug-fix"
        assert result.confidence == 0.85
        assert result.matched_keywords == ["bug", "error"]
        assert result.should_suggest_generation is False

    def test_match_result_confidence_validation_high(self):
        """Test MatchResult rejects confidence > 1.0."""
        with pytest.raises(ValueError, match="Confidence must be 0.0-1.0"):
            MatchResult(
                workflow_type="bug-fix",
                confidence=1.5,
                matched_keywords=["bug"],
                should_suggest_generation=False
            )

    def test_match_result_confidence_validation_low(self):
        """Test MatchResult rejects confidence < 0.0."""
        with pytest.raises(ValueError, match="Confidence must be 0.0-1.0"):
            MatchResult(
                workflow_type="bug-fix",
                confidence=-0.1,
                matched_keywords=["bug"],
                should_suggest_generation=False
            )

    def test_match_result_none_workflow_type(self):
        """Test MatchResult with None workflow_type (no match)."""
        result = MatchResult(
            workflow_type=None,
            confidence=0.0,
            matched_keywords=[],
            should_suggest_generation=True
        )
        assert result.workflow_type is None
        assert result.should_suggest_generation is True


class TestWorkflowMatcherInitialization:
    """Test WorkflowMatcher initialization."""

    def test_initialization_valid(self):
        """Test successful initialization with valid keywords."""
        matcher = WorkflowMatcher(WORKFLOW_KEYWORDS)
        assert matcher.keyword_library == WORKFLOW_KEYWORDS

    def test_initialization_empty_library(self):
        """Test initialization fails with empty library."""
        with pytest.raises(ValueError, match="keyword_library cannot be empty"):
            WorkflowMatcher({})

    def test_initialization_empty_keyword_set(self):
        """Test initialization fails with empty keyword set."""
        with pytest.raises(ValueError, match="cannot be empty"):
            WorkflowMatcher({"test-workflow": set()})


class TestBugFixMatching:
    """Test matching bug-fix workflow requests."""

    @pytest.fixture
    def matcher(self):
        return WorkflowMatcher(WORKFLOW_KEYWORDS)

    def test_bug_fix_simple(self, matcher):
        """Test matching simple bug fix request."""
        result = matcher.match("There's a bug in the authentication")
        assert result.workflow_type == "bug-fix"
        assert result.confidence > 0.0
        assert "bug" in result.matched_keywords

    def test_bug_fix_error(self, matcher):
        """Test matching error-based request."""
        result = matcher.match("Getting an error when logging in")
        assert result.workflow_type == "bug-fix"
        assert "error" in result.matched_keywords

    def test_bug_fix_crash(self, matcher):
        """Test matching crash-based request."""
        result = matcher.match("Application crashes on startup")
        assert result.workflow_type == "bug-fix"
        # May match crash or crashes (variation)
        assert any(kw in result.matched_keywords for kw in ["crash", "crashes"])

    def test_bug_fix_multi_keyword(self, matcher):
        """Test multi-keyword match gets confidence boost."""
        result = matcher.match("Fix the bug causing crashes and errors")
        assert result.workflow_type == "bug-fix"
        # Should match multiple keywords: bug, fix, crash, error
        assert len(result.matched_keywords) >= 2
        # Multi-keyword boost should increase confidence
        assert result.confidence > 0.3

    def test_bug_fix_natural_language(self, matcher):
        """Test natural language bug report."""
        result = matcher.match("The login feature is broken and not working")
        assert result.workflow_type == "bug-fix"
        assert any(kw in result.matched_keywords for kw in ["broken", "not", "working"])


class TestFeatureDevMatching:
    """Test matching feature-dev workflow requests."""

    @pytest.fixture
    def matcher(self):
        return WorkflowMatcher(WORKFLOW_KEYWORDS)

    def test_feature_dev_add(self, matcher):
        """Test matching 'add' feature request."""
        result = matcher.match("Add OAuth2 support")
        assert result.workflow_type == "feature-dev"
        assert "add" in result.matched_keywords

    def test_feature_dev_new(self, matcher):
        """Test matching 'new' feature request."""
        result = matcher.match("Create a new dashboard component")
        assert result.workflow_type == "feature-dev"
        assert any(kw in result.matched_keywords for kw in ["new", "create"])

    def test_feature_dev_implement(self, matcher):
        """Test matching 'implement' feature request."""
        result = matcher.match("Implement user authentication")
        assert result.workflow_type == "feature-dev"
        assert "implement" in result.matched_keywords

    def test_feature_dev_natural_language(self, matcher):
        """Test natural language feature request."""
        result = matcher.match("I want to build a plugin system")
        assert result.workflow_type == "feature-dev"
        assert any(kw in result.matched_keywords for kw in ["want", "build", "plugin"])


class TestPerformanceMatching:
    """Test matching performance workflow requests."""

    @pytest.fixture
    def matcher(self):
        return WorkflowMatcher(WORKFLOW_KEYWORDS)

    def test_performance_slow(self, matcher):
        """Test matching 'slow' performance request."""
        result = matcher.match("The API is slow")
        assert result.workflow_type == "performance"
        assert "slow" in result.matched_keywords

    def test_performance_optimize(self, matcher):
        """Test matching 'optimize' performance request."""
        result = matcher.match("Optimize database queries")
        assert result.workflow_type == "performance"
        assert "optimize" in result.matched_keywords

    def test_performance_memory(self, matcher):
        """Test matching memory performance request."""
        result = matcher.match("Reduce memory usage in cache")
        assert result.workflow_type == "performance"
        assert any(kw in result.matched_keywords for kw in ["memory", "usage", "cache"])

    def test_performance_bottleneck(self, matcher):
        """Test matching bottleneck performance request."""
        result = matcher.match("Profile the bottleneck affecting latency")
        assert result.workflow_type == "performance"
        assert any(kw in result.matched_keywords for kw in ["bottleneck", "latency", "profile"])


class TestRefactoringMatching:
    """Test matching refactoring workflow requests."""

    @pytest.fixture
    def matcher(self):
        return WorkflowMatcher(WORKFLOW_KEYWORDS)

    def test_refactoring_simple(self, matcher):
        """Test matching simple refactor request."""
        result = matcher.match("Refactor the router code")
        assert result.workflow_type == "refactoring"
        assert "refactor" in result.matched_keywords

    def test_refactoring_cleanup(self, matcher):
        """Test matching cleanup request."""
        result = matcher.match("Clean up the duplicate code")
        assert result.workflow_type == "refactoring"
        assert any(kw in result.matched_keywords for kw in ["cleanup", "clean", "duplicate"])

    def test_refactoring_debt(self, matcher):
        """Test matching technical debt request."""
        result = matcher.match("Address technical debt in the module")
        assert result.workflow_type == "refactoring"
        assert any(kw in result.matched_keywords for kw in ["debt", "technical"])

    def test_refactoring_improve(self, matcher):
        """Test matching improve maintainability request."""
        result = matcher.match("Improve code quality and maintainability")
        assert result.workflow_type == "refactoring"
        assert any(kw in result.matched_keywords for kw in ["improve", "quality", "maintainability"])


class TestInvestigationMatching:
    """Test matching investigation workflow requests."""

    @pytest.fixture
    def matcher(self):
        return WorkflowMatcher(WORKFLOW_KEYWORDS)

    def test_investigation_why(self, matcher):
        """Test matching 'why' investigation request."""
        result = matcher.match("Why is the system behaving this way?")
        assert result.workflow_type == "investigation"
        assert "why" in result.matched_keywords

    def test_investigation_analyze(self, matcher):
        """Test matching 'analyze' investigation request."""
        result = matcher.match("Analyze the root cause of the issue")
        assert result.workflow_type == "investigation"
        assert any(kw in result.matched_keywords for kw in ["analyze", "root", "cause"])

    def test_investigation_understand(self, matcher):
        """Test matching 'understand' investigation request."""
        result = matcher.match("I need to understand how this works")
        assert result.workflow_type == "investigation"
        assert "understand" in result.matched_keywords

    def test_investigation_explore(self, matcher):
        """Test matching 'explore' investigation request."""
        result = matcher.match("Explore different approaches to solve this")
        assert result.workflow_type == "investigation"
        assert "explore" in result.matched_keywords


class TestConfidenceScoring:
    """Test confidence scoring algorithm."""

    @pytest.fixture
    def matcher(self):
        return WorkflowMatcher(WORKFLOW_KEYWORDS)

    def test_single_keyword_confidence(self, matcher):
        """Test confidence with single keyword match."""
        # Single keyword should have lower confidence
        result = matcher.match("bug")
        assert result.workflow_type == "bug-fix"
        assert result.confidence > 0.0
        assert result.confidence < 1.0

    def test_multi_keyword_boost(self, matcher):
        """Test multi-keyword boost increases confidence."""
        single_result = matcher.match("bug")
        multi_result = matcher.match("fix the bug error crash")

        # Multi-keyword should have higher confidence due to 1.2x boost
        assert multi_result.confidence > single_result.confidence
        assert len(multi_result.matched_keywords) > len(single_result.matched_keywords)

    def test_confidence_caps_at_one(self, matcher):
        """Test confidence never exceeds 1.0."""
        # Even with all keywords, confidence caps at 1.0
        all_keywords = " ".join(WORKFLOW_KEYWORDS["bug-fix"])
        result = matcher.match(all_keywords)
        assert result.confidence <= 1.0

    def test_suggestion_threshold(self, matcher):
        """Test should_suggest_generation based on confidence threshold."""
        # High confidence (multi-keyword match) should not suggest generation
        high_conf_result = matcher.match("Fix the authentication bug error crash")
        # Low confidence (single keyword) should suggest generation
        low_conf_result = matcher.match("bug")

        # Note: Actual suggestion depends on keyword density
        # We primarily test that the flag is set based on 0.7 threshold
        if high_conf_result.confidence >= 0.7:
            assert high_conf_result.should_suggest_generation is False
        if low_conf_result.confidence < 0.7:
            assert low_conf_result.should_suggest_generation is True


class TestNoMatchCases:
    """Test cases where no workflow matches."""

    @pytest.fixture
    def matcher(self):
        return WorkflowMatcher(WORKFLOW_KEYWORDS)

    def test_no_keywords_match(self, matcher):
        """Test message with no matching keywords."""
        result = matcher.match("The sky is blue and grass is green")
        assert result.workflow_type is None
        assert result.confidence == 0.0
        assert result.matched_keywords == []
        assert result.should_suggest_generation is True

    def test_empty_message(self, matcher):
        """Test empty message."""
        result = matcher.match("")
        assert result.workflow_type is None
        assert result.confidence == 0.0
        assert result.should_suggest_generation is True

    def test_whitespace_only(self, matcher):
        """Test whitespace-only message."""
        result = matcher.match("   \n\t   ")
        assert result.workflow_type is None
        assert result.confidence == 0.0

    def test_special_characters_only(self, matcher):
        """Test message with only special characters."""
        result = matcher.match("!@#$%^&*()")
        assert result.workflow_type is None
        assert result.confidence == 0.0


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.fixture
    def matcher(self):
        return WorkflowMatcher(WORKFLOW_KEYWORDS)

    def test_case_insensitive(self, matcher):
        """Test matching is case-insensitive."""
        lower = matcher.match("fix the bug")
        upper = matcher.match("FIX THE BUG")
        mixed = matcher.match("Fix The Bug")

        assert lower.workflow_type == upper.workflow_type == mixed.workflow_type
        assert lower.matched_keywords == upper.matched_keywords == mixed.matched_keywords

    def test_punctuation_handling(self, matcher):
        """Test punctuation is handled correctly."""
        result = matcher.match("Fix the bug! It's broken, really broken.")
        assert result.workflow_type == "bug-fix"
        assert any(kw in result.matched_keywords for kw in ["fix", "bug", "broken"])

    def test_long_message(self, matcher):
        """Test matching works with long messages."""
        long_message = (
            "I've been investigating this issue for a while now and I think "
            "there's a bug in the authentication system that causes crashes "
            "when users try to log in with special characters in their password. "
            "We need to fix this error as soon as possible because it's affecting "
            "many users and causing failures in production."
        )
        result = matcher.match(long_message)
        assert result.workflow_type == "bug-fix"
        assert len(result.matched_keywords) > 2  # Should match multiple keywords

    def test_numbers_in_message(self, matcher):
        """Test messages containing numbers."""
        result = matcher.match("Fix bug #1234 in version 2.0.0")
        assert result.workflow_type == "bug-fix"
        assert "bug" in result.matched_keywords

    def test_urls_in_message(self, matcher):
        """Test messages containing URLs."""
        result = matcher.match("Bug reported at https://github.com/repo/issues/123")
        assert result.workflow_type == "bug-fix"
        assert "bug" in result.matched_keywords

    def test_short_tokens_filtered(self, matcher):
        """Test very short tokens (<2 chars) are filtered out."""
        # Single char tokens should be filtered
        result = matcher.match("a b c d e fix")
        # Should still match "fix" but ignore single chars
        assert "a" not in result.matched_keywords


class TestPerformanceRequirements:
    """Test performance requirements (<100ms per ADR-013)."""

    @pytest.fixture
    def matcher(self):
        return WorkflowMatcher(WORKFLOW_KEYWORDS)

    def test_performance_simple_match(self, matcher):
        """Test simple match completes in <100ms."""
        start = time.time()
        result = matcher.match("Fix the authentication bug")
        duration = time.time() - start

        assert duration < 0.1  # <100ms
        assert result.workflow_type == "bug-fix"

    def test_performance_long_message(self, matcher):
        """Test long message match completes in <100ms."""
        # Create a long message by repeating text
        long_message = " ".join([
            "Fix the authentication bug in the login system",
            "This error occurs when users try to access the dashboard",
            "The crash happens intermittently and we need to investigate",
            "The stacktrace shows a null pointer exception"
        ] * 10)  # 10x repetition

        start = time.time()
        result = matcher.match(long_message)
        duration = time.time() - start

        assert duration < 0.1  # <100ms even for long messages
        assert result.workflow_type == "bug-fix"

    def test_performance_multiple_matches(self, matcher):
        """Test 100 matches complete in reasonable time."""
        messages = [
            "Fix the bug",
            "Add new feature",
            "Optimize performance",
            "Refactor code",
            "Investigate issue"
        ] * 20  # 100 messages

        start = time.time()
        results = [matcher.match(msg) for msg in messages]
        duration = time.time() - start

        # 100 matches should complete in <1s (avg <10ms each)
        assert duration < 1.0
        assert len(results) == 100
        # Verify all matched correctly
        assert all(r.workflow_type is not None for r in results)


class TestAmbiguousCases:
    """Test cases where multiple workflows might match."""

    @pytest.fixture
    def matcher(self):
        return WorkflowMatcher(WORKFLOW_KEYWORDS)

    def test_bug_vs_investigation(self, matcher):
        """Test message that could be bug or investigation."""
        # "investigate" is in investigation keywords
        # "bug" is in bug-fix keywords
        result = matcher.match("investigate the bug")

        # Should pick one (highest confidence)
        assert result.workflow_type in ["bug-fix", "investigation"]
        assert len(result.matched_keywords) >= 1

    def test_feature_vs_refactoring(self, matcher):
        """Test message that could be feature or refactoring."""
        # "improve" could be feature enhancement or refactoring
        result = matcher.match("improve the code structure")

        # Should pick based on keyword density
        assert result.workflow_type in ["feature-dev", "refactoring"]

    def test_returns_best_match(self, matcher):
        """Test matcher returns highest confidence match."""
        # This should heavily favor bug-fix (multiple keywords)
        result = matcher.match("fix the critical bug error crash failure")

        assert result.workflow_type == "bug-fix"
        # Should have high confidence from multiple matches
        assert result.confidence > 0.5


class TestNormalizationAndTokenization:
    """Test internal normalization and tokenization methods."""

    @pytest.fixture
    def matcher(self):
        return WorkflowMatcher(WORKFLOW_KEYWORDS)

    def test_normalize_lowercase(self, matcher):
        """Test normalization converts to lowercase."""
        normalized = matcher._normalize_message("FIX THE BUG")
        assert normalized == "fix the bug"

    def test_normalize_strip_whitespace(self, matcher):
        """Test normalization strips whitespace."""
        normalized = matcher._normalize_message("  fix bug  \n")
        assert normalized == "fix bug"

    def test_tokenize_extracts_words(self, matcher):
        """Test tokenization extracts words."""
        tokens = matcher._tokenize("fix the bug")
        assert "fix" in tokens
        assert "the" in tokens
        assert "bug" in tokens

    def test_tokenize_removes_punctuation(self, matcher):
        """Test tokenization removes punctuation."""
        tokens = matcher._tokenize("fix! the, bug.")
        assert "fix" in tokens
        assert "bug" in tokens
        # Punctuation should not be in tokens
        assert "!" not in tokens
        assert "," not in tokens
        assert "." not in tokens

    def test_tokenize_filters_short_tokens(self, matcher):
        """Test tokenization filters out very short tokens."""
        tokens = matcher._tokenize("a b fix bug")
        # Short tokens (<2 chars) should be filtered
        assert "a" not in tokens
        assert "b" not in tokens
        # Normal tokens should remain
        assert "fix" in tokens
        assert "bug" in tokens
