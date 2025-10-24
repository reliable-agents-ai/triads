"""Tests for work request detection in orchestrator activation."""

import sys
from pathlib import Path

import pytest

# Add hooks to path
repo_root = Path(__file__).parent.parent
if str(repo_root / "hooks") not in sys.path:
    sys.path.insert(0, str(repo_root / "hooks"))

from user_prompt_submit import detect_work_request


# ============================================================================
# Test Work Request Classification
# ============================================================================

def test_detect_work_request_feature():
    """Test detection of feature requests."""
    requests = [
        "Implement OAuth2 support",
        "Add user authentication",
        "Create new dashboard",
        "Build reporting module",
        "Let's implement caching",
        "Please add error handling",
        "We need to add logging",
        "Develop new API endpoint",
        "Make a settings page"
    ]

    for request in requests:
        result = detect_work_request(request)
        assert result != {}, f"Should detect work request: {request}"
        assert result['type'] == 'feature', f"Should classify as feature: {request}"
        assert result['triad'] == 'idea-validation', f"Should route to idea-validation: {request}"
        assert result['original_request'] == request


def test_detect_work_request_bug():
    """Test detection of bug fix requests."""
    requests = [
        "Fix router crash",
        "There's a bug in the login",
        "Error when saving data",
        "Broken authentication flow",
        "Issue with database connection",
        "App is crashing on startup",
        "Tests are failing",
        "Not working correctly",
        "Resolve memory leak",
        "Correct validation logic",
        "Repair broken import"
    ]

    for request in requests:
        result = detect_work_request(request)
        assert result != {}, f"Should detect work request: {request}"
        assert result['type'] == 'bug', f"Should classify as bug: {request}"
        assert result['triad'] == 'idea-validation'
        assert result['original_request'] == request


def test_detect_work_request_refactor():
    """Test detection of refactoring requests."""
    requests = [
        "Refactor the router module",
        "Cleanup messy code in auth",
        "Clean up the database layer",
        "Improve code quality",
        "Consolidate duplicate functions",
        "Reorganize the codebase",
        "Restructure the API",
        "This code has technical debt",
        "Simplify the algorithm",
        "Optimize performance"
    ]

    for request in requests:
        result = detect_work_request(request)
        assert result != {}, f"Should detect work request: {request}"
        assert result['type'] == 'refactor', f"Should classify as refactor: {request}"
        assert result['triad'] == 'idea-validation'
        assert result['original_request'] == request


def test_detect_work_request_design():
    """Test detection of design/architecture requests."""
    requests = [
        "Design the OAuth2 flow",
        "Architecture for plugin system",
        "How should we structure the database?",
        "What approach for caching?",
        "Which approach is best for auth?",
        "Architect the notification system",
        "Design structure for reporting"
    ]

    for request in requests:
        result = detect_work_request(request)
        assert result != {}, f"Should detect work request: {request}"
        assert result['type'] == 'design', f"Should classify as design: {request}"
        assert result['triad'] == 'idea-validation'
        assert result['original_request'] == request


def test_detect_work_request_release():
    """Test detection of release/deployment requests."""
    requests = [
        "Deploy to production",
        "Release version 1.0",
        "Publish the package",
        "Ship the new feature",
        "Launch the update"
    ]

    for request in requests:
        result = detect_work_request(request)
        assert result != {}, f"Should detect work request: {request}"
        assert result['type'] == 'release', f"Should classify as release: {request}"
        assert result['triad'] == 'idea-validation'
        assert result['original_request'] == request


# ============================================================================
# Test Q&A Detection (NOT work requests)
# ============================================================================

def test_detect_qa_not_work_request():
    """Test that Q&A questions are NOT classified as work requests."""
    qa_requests = [
        "What is OAuth2?",
        "What are the benefits of caching?",
        "What does this function do?",
        "How does authentication work?",
        "How do I run tests?",
        "How to configure the database?",
        "Explain the router system",
        "Tell me about triads",
        "Tell me how the workflow works",
        "Can you explain OAuth2?",
        "Could you explain the architecture?",
        "Describe the plugin system",
        "Why is the code structured this way?",
        "Why does caching improve performance?",
        "When should I use async?",
        "Where is the configuration file?",
        "Where does authentication happen?",
        "Who is responsible for deployment?",
        "Which is better: REST or GraphQL?"
    ]

    for request in qa_requests:
        result = detect_work_request(request)
        assert result == {}, f"Should NOT detect as work request: {request}"


# ============================================================================
# Test Edge Cases
# ============================================================================

def test_detect_work_request_invalid_input():
    """Test handling of invalid inputs."""
    assert detect_work_request(None) == {}
    assert detect_work_request("") == {}
    assert detect_work_request(123) == {}
    assert detect_work_request([]) == {}


def test_detect_work_request_case_insensitive():
    """Test that detection is case-insensitive."""
    requests = [
        "IMPLEMENT OAuth2",
        "Implement OAuth2",
        "implement oauth2"
    ]

    for request in requests:
        result = detect_work_request(request)
        assert result['type'] == 'feature'


def test_detect_work_request_mixed_case():
    """Test mixed case in messages."""
    result = detect_work_request("Let's Add OAuth2 Support")
    assert result['type'] == 'feature'

    result = detect_work_request("Fix Router CRASH")
    assert result['type'] == 'bug'


def test_detect_work_request_with_punctuation():
    """Test messages with various punctuation."""
    requests = [
        "Implement OAuth2!",
        "Fix the bug.",
        "Add logging?",
        "Refactor code, please",
        "Design architecture: plugins"
    ]

    for request in requests:
        result = detect_work_request(request)
        assert result != {}, f"Should detect work request: {request}"


def test_detect_work_request_multiline():
    """Test multiline messages."""
    request = """
    Implement OAuth2 with:
    - Authorization code flow
    - Token refresh
    - Scope management
    """
    result = detect_work_request(request)
    assert result['type'] == 'feature'
    assert result['original_request'] == request


def test_detect_work_request_long_message():
    """Test long messages."""
    request = "I'd like to implement OAuth2 support for user authentication " * 10
    result = detect_work_request(request)
    assert result['type'] == 'feature'


def test_detect_work_request_ambiguous():
    """Test ambiguous messages that don't clearly indicate work or Q&A."""
    ambiguous = [
        "OAuth2",
        "The router",
        "Thoughts on caching?",
        "Hmm, the tests...",
        "Looking at the code"
    ]

    for request in ambiguous:
        result = detect_work_request(request)
        # Ambiguous messages should return empty dict (no classification)
        assert result == {}, f"Should not classify ambiguous message: {request}"


def test_detect_work_request_qa_pattern_priority():
    """Test that Q&A patterns take priority over work patterns."""
    # These contain both Q&A and work indicators - Q&A should win
    requests = [
        "What is the best way to implement OAuth2?",
        "How does the refactoring work?",
        "Explain how to fix this bug",
        "Tell me about how to add authentication"
    ]

    for request in requests:
        result = detect_work_request(request)
        assert result == {}, f"Q&A should take priority: {request}"


# ============================================================================
# Test Entry Point Routing
# ============================================================================

def test_detect_work_request_single_entry_point():
    """Test that ALL work requests route to idea-validation (ADR-007)."""
    all_work_types = [
        "Implement OAuth2",  # feature
        "Fix router crash",  # bug
        "Refactor code",  # refactor
        "Design architecture",  # design
        "Deploy to production"  # release
    ]

    for request in all_work_types:
        result = detect_work_request(request)
        assert result['triad'] == 'idea-validation', \
            f"All work should enter through idea-validation: {request}"


def test_detect_work_request_preserves_original():
    """Test that original request is preserved exactly."""
    request = "Implement OAuth2 with special chars: <>&\"'"
    result = detect_work_request(request)
    assert result['original_request'] == request, "Should preserve exact request"


# ============================================================================
# Test Pattern Matching Behavior
# ============================================================================

def test_detect_work_request_multiple_patterns():
    """Test behavior when message matches multiple patterns."""
    # When multiple patterns match, first iteration match wins
    # (dict iteration order: feature, bug, refactor, design, release)

    # Contains both "implement" (feature) and "fix" (bug)
    result = detect_work_request("Fix and implement OAuth2")
    # "implement" in feature list will match first (dict iteration order)
    assert result['type'] in ['feature', 'bug'], "Should match one of the patterns"

    # Contains both "add" (feature) and "refactor"
    result = detect_work_request("Add code and refactor it")
    assert result['type'] in ['feature', 'refactor'], "Should match one of the patterns"
