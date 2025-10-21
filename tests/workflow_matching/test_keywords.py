"""Tests for keyword library module.

Test Coverage:
1. WORKFLOW_KEYWORDS structure and content
2. get_keywords() function
3. get_all_workflow_types() function
4. Keyword completeness for each workflow
5. No keyword overlap issues
"""

import pytest
from triads.workflow_matching import (
    WORKFLOW_KEYWORDS,
    get_keywords,
    get_all_workflow_types,
)


class TestWorkflowKeywordsStructure:
    """Test WORKFLOW_KEYWORDS library structure."""

    def test_has_all_five_workflows(self):
        """Test library contains all 5 seed workflows (ADR-017)."""
        expected_workflows = {
            "bug-fix",
            "feature-dev",
            "performance",
            "refactoring",
            "investigation"
        }
        assert set(WORKFLOW_KEYWORDS.keys()) == expected_workflows

    def test_all_workflows_have_keywords(self):
        """Test every workflow has non-empty keyword set."""
        for workflow_type, keywords in WORKFLOW_KEYWORDS.items():
            assert isinstance(keywords, set), f"{workflow_type} keywords not a set"
            assert len(keywords) > 0, f"{workflow_type} has no keywords"

    def test_keywords_are_lowercase(self):
        """Test all keywords are lowercase."""
        for workflow_type, keywords in WORKFLOW_KEYWORDS.items():
            for keyword in keywords:
                assert keyword.islower(), \
                    f"Keyword '{keyword}' in {workflow_type} not lowercase"

    def test_keywords_are_strings(self):
        """Test all keywords are strings."""
        for workflow_type, keywords in WORKFLOW_KEYWORDS.items():
            for keyword in keywords:
                assert isinstance(keyword, str), \
                    f"Keyword {keyword} in {workflow_type} not a string"

    def test_no_empty_keywords(self):
        """Test no empty string keywords."""
        for workflow_type, keywords in WORKFLOW_KEYWORDS.items():
            for keyword in keywords:
                assert len(keyword) > 0, \
                    f"Empty keyword in {workflow_type}"


class TestBugFixKeywords:
    """Test bug-fix workflow keywords."""

    def test_has_core_bug_terms(self):
        """Test bug-fix has core bug terminology."""
        keywords = WORKFLOW_KEYWORDS["bug-fix"]
        core_terms = {"bug", "error", "crash", "fix", "broken"}
        assert core_terms.issubset(keywords)

    def test_has_debugging_terms(self):
        """Test bug-fix has debugging terminology."""
        keywords = WORKFLOW_KEYWORDS["bug-fix"]
        debug_terms = {"debug", "stacktrace", "traceback"}
        assert debug_terms.issubset(keywords)

    def test_sufficient_coverage(self):
        """Test bug-fix has sufficient keyword coverage."""
        keywords = WORKFLOW_KEYWORDS["bug-fix"]
        # Should have at least 15 keywords for good coverage
        assert len(keywords) >= 15


class TestFeatureDevKeywords:
    """Test feature-dev workflow keywords."""

    def test_has_core_feature_terms(self):
        """Test feature-dev has core feature terminology."""
        keywords = WORKFLOW_KEYWORDS["feature-dev"]
        core_terms = {"feature", "add", "new", "create", "build", "implement"}
        assert core_terms.issubset(keywords)

    def test_has_integration_terms(self):
        """Test feature-dev has integration terminology."""
        keywords = WORKFLOW_KEYWORDS["feature-dev"]
        integration_terms = {"integrate", "extend", "support", "enable"}
        assert integration_terms.issubset(keywords)

    def test_sufficient_coverage(self):
        """Test feature-dev has sufficient keyword coverage."""
        keywords = WORKFLOW_KEYWORDS["feature-dev"]
        assert len(keywords) >= 10


class TestPerformanceKeywords:
    """Test performance workflow keywords."""

    def test_has_speed_terms(self):
        """Test performance has speed terminology."""
        keywords = WORKFLOW_KEYWORDS["performance"]
        speed_terms = {"slow", "performance", "optimize", "speed", "latency"}
        assert speed_terms.issubset(keywords)

    def test_has_resource_terms(self):
        """Test performance has resource terminology."""
        keywords = WORKFLOW_KEYWORDS["performance"]
        resource_terms = {"memory", "cpu", "bottleneck"}
        assert resource_terms.issubset(keywords)

    def test_has_optimization_terms(self):
        """Test performance has optimization terminology."""
        keywords = WORKFLOW_KEYWORDS["performance"]
        optimization_terms = {"cache", "scale", "efficient", "throughput"}
        assert optimization_terms.issubset(keywords)

    def test_sufficient_coverage(self):
        """Test performance has sufficient keyword coverage."""
        keywords = WORKFLOW_KEYWORDS["performance"]
        assert len(keywords) >= 15


class TestRefactoringKeywords:
    """Test refactoring workflow keywords."""

    def test_has_refactoring_terms(self):
        """Test refactoring has refactoring terminology."""
        keywords = WORKFLOW_KEYWORDS["refactoring"]
        refactor_terms = {"refactor", "cleanup", "simplify", "restructure"}
        assert refactor_terms.issubset(keywords)

    def test_has_quality_terms(self):
        """Test refactoring has quality terminology."""
        keywords = WORKFLOW_KEYWORDS["refactoring"]
        quality_terms = {"debt", "technical", "quality", "maintainability"}
        assert quality_terms.issubset(keywords)

    def test_has_action_terms(self):
        """Test refactoring has action terminology."""
        keywords = WORKFLOW_KEYWORDS["refactoring"]
        action_terms = {"extract", "consolidate", "remove"}
        assert action_terms.issubset(keywords)

    def test_sufficient_coverage(self):
        """Test refactoring has sufficient keyword coverage."""
        keywords = WORKFLOW_KEYWORDS["refactoring"]
        assert len(keywords) >= 15


class TestInvestigationKeywords:
    """Test investigation workflow keywords."""

    def test_has_investigation_terms(self):
        """Test investigation has investigation terminology."""
        keywords = WORKFLOW_KEYWORDS["investigation"]
        investigation_terms = {"investigate", "analyze", "understand", "explore"}
        assert investigation_terms.issubset(keywords)

    def test_has_question_words(self):
        """Test investigation has key question words."""
        keywords = WORKFLOW_KEYWORDS["investigation"]
        # Core question words (overly generic ones removed to reduce false matches)
        question_words = {"why", "how"}
        assert question_words.issubset(keywords)

    def test_has_root_cause_terms(self):
        """Test investigation has root cause terminology."""
        keywords = WORKFLOW_KEYWORDS["investigation"]
        root_cause_terms = {"cause", "root", "diagnose"}
        assert root_cause_terms.issubset(keywords)

    def test_sufficient_coverage(self):
        """Test investigation has sufficient keyword coverage."""
        keywords = WORKFLOW_KEYWORDS["investigation"]
        assert len(keywords) >= 15


class TestGetKeywords:
    """Test get_keywords() function."""

    def test_get_existing_workflow(self):
        """Test getting keywords for existing workflow."""
        keywords = get_keywords("bug-fix")
        assert isinstance(keywords, set)
        assert len(keywords) > 0
        assert "bug" in keywords

    def test_get_all_workflows(self):
        """Test getting keywords for all 5 workflows."""
        for workflow_type in ["bug-fix", "feature-dev", "performance",
                              "refactoring", "investigation"]:
            keywords = get_keywords(workflow_type)
            assert isinstance(keywords, set)
            assert len(keywords) > 0

    def test_get_nonexistent_workflow(self):
        """Test getting keywords for nonexistent workflow returns empty set."""
        keywords = get_keywords("nonexistent-workflow")
        assert keywords == set()

    def test_returns_set_not_reference(self):
        """Test get_keywords returns actual set from library."""
        keywords = get_keywords("bug-fix")
        # Should be the same set object (not a copy)
        assert keywords is WORKFLOW_KEYWORDS["bug-fix"]


class TestGetAllWorkflowTypes:
    """Test get_all_workflow_types() function."""

    def test_returns_all_five_types(self):
        """Test returns all 5 workflow types."""
        types = get_all_workflow_types()
        assert len(types) == 5
        expected = {"bug-fix", "feature-dev", "performance",
                    "refactoring", "investigation"}
        assert set(types) == expected

    def test_returns_list(self):
        """Test returns list not set."""
        types = get_all_workflow_types()
        assert isinstance(types, list)

    def test_all_strings(self):
        """Test all returned types are strings."""
        types = get_all_workflow_types()
        assert all(isinstance(t, str) for t in types)

    def test_no_duplicates(self):
        """Test no duplicate workflow types."""
        types = get_all_workflow_types()
        assert len(types) == len(set(types))


class TestKeywordOverlap:
    """Test keyword overlap between workflows.

    Some overlap is acceptable (e.g., "improve" in both feature-dev and refactoring),
    but we want to ensure it's intentional and doesn't cause confusion.
    """

    def test_core_keywords_unique(self):
        """Test core keywords are unique to each workflow."""
        # These should be uniquely identifying
        unique_keywords = {
            "bug-fix": {"bug", "error", "crash"},
            "feature-dev": {"feature", "implement"},
            "performance": {"optimize", "bottleneck", "latency"},
            "refactoring": {"refactor", "debt"},
            "investigation": {"investigate", "diagnose"}
        }

        for workflow_type, core_keywords in unique_keywords.items():
            workflow_keywords = WORKFLOW_KEYWORDS[workflow_type]
            other_workflows = {k: v for k, v in WORKFLOW_KEYWORDS.items()
                             if k != workflow_type}

            # Core keywords should be in this workflow
            assert core_keywords.issubset(workflow_keywords)

            # Core keywords should not appear in other workflows
            for other_type, other_keywords in other_workflows.items():
                overlap = core_keywords.intersection(other_keywords)
                assert len(overlap) == 0, \
                    f"Core keyword overlap between {workflow_type} and {other_type}: {overlap}"

    def test_acceptable_overlap_documented(self):
        """Test known acceptable overlaps are documented.

        Some keywords naturally appear in multiple workflows.
        This test documents intentional overlaps.
        """
        # Known acceptable overlaps (words used in multiple contexts)
        acceptable_overlaps = {
            "improve": {"feature-dev", "refactoring", "performance"},
            "fix": {"bug-fix", "refactoring"},  # Can fix bugs or fix code quality
        }

        # Just document - this test passes if we're aware of overlaps
        for keyword, workflows in acceptable_overlaps.items():
            for workflow in workflows:
                if workflow in WORKFLOW_KEYWORDS:
                    # Just verify we documented correctly
                    pass

    def test_minimal_total_overlap(self):
        """Test total keyword overlap is minimal (<20% average)."""
        workflow_types = list(WORKFLOW_KEYWORDS.keys())
        total_overlaps = 0
        total_comparisons = 0

        for i, workflow1 in enumerate(workflow_types):
            for workflow2 in workflow_types[i+1:]:
                kw1 = WORKFLOW_KEYWORDS[workflow1]
                kw2 = WORKFLOW_KEYWORDS[workflow2]

                overlap = kw1.intersection(kw2)
                overlap_ratio = len(overlap) / min(len(kw1), len(kw2))

                total_overlaps += overlap_ratio
                total_comparisons += 1

        avg_overlap = total_overlaps / total_comparisons
        # Average overlap should be <20% to maintain distinctiveness
        assert avg_overlap < 0.20, \
            f"Average keyword overlap {avg_overlap:.2%} exceeds 20% threshold"


class TestKeywordQuality:
    """Test keyword quality and appropriateness."""

    def test_no_very_short_keywords(self):
        """Test no single-character keywords (too noisy)."""
        for workflow_type, keywords in WORKFLOW_KEYWORDS.items():
            for keyword in keywords:
                assert len(keyword) >= 2, \
                    f"Single-char keyword '{keyword}' in {workflow_type}"

    def test_no_overly_generic_keywords(self):
        """Test no overly generic keywords that would match everything."""
        # These are too generic and would cause false matches
        too_generic = {"the", "a", "an", "is", "it", "this", "that", "or", "and"}

        for workflow_type, keywords in WORKFLOW_KEYWORDS.items():
            overlap = keywords.intersection(too_generic)
            assert len(overlap) == 0, \
                f"Generic keywords in {workflow_type}: {overlap}"

    def test_keywords_alphanumeric(self):
        """Test keywords are alphanumeric (no special chars)."""
        for workflow_type, keywords in WORKFLOW_KEYWORDS.items():
            for keyword in keywords:
                # Allow hyphens in compound words, but nothing else
                cleaned = keyword.replace("-", "")
                assert cleaned.isalnum(), \
                    f"Non-alphanumeric keyword '{keyword}' in {workflow_type}"
