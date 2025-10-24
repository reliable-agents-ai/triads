"""Tests for LLM disambiguation."""

import os
from unittest.mock import MagicMock, Mock, patch

import pytest

from triads.tools.router._llm_disambiguator import (
    DisambiguationError,
    LLMDisambiguator,
)

# Import anthropic for exception types
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class TestLLMDisambiguator:
    """Test LLM disambiguation client."""

    @pytest.fixture
    def mock_env_var(self, monkeypatch):
        """Mock ANTHROPIC_API_KEY environment variable."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-api-key")

    @pytest.fixture
    def disambiguator(self, mock_env_var):
        """Create disambiguator instance with mocked API key."""
        return LLMDisambiguator(timeout_ms=2000)

    @pytest.fixture
    def candidates(self):
        """Sample candidates for testing."""
        return [
            ("implementation", 0.75),
            ("design", 0.73),
            ("garden-tending", 0.70),
        ]

    def test_init_without_api_key(self, monkeypatch):
        """Test initialization fails without API key."""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

        with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
            LLMDisambiguator()

    def test_init_with_api_key(self, mock_env_var):
        """Test successful initialization with API key."""
        disambiguator = LLMDisambiguator(timeout_ms=3000)

        assert disambiguator.timeout_ms == 3000
        assert disambiguator.model == "claude-3-5-sonnet-20241022"

    def test_build_system_prompt(self, disambiguator):
        """Test system prompt construction."""
        prompt = disambiguator._build_system_prompt()

        assert "routing assistant" in prompt
        assert "idea-validation" in prompt
        assert "design" in prompt
        assert "implementation" in prompt
        assert "garden-tending" in prompt
        assert "deployment" in prompt

    def test_build_user_message_without_context(self, disambiguator, candidates):
        """Test user message construction without context."""
        prompt = "Let's build a new feature"
        msg = disambiguator._build_user_message(prompt, candidates, None)

        assert "Let's build a new feature" in msg
        assert "implementation" in msg
        assert "0.75" in msg
        assert "design" in msg
        assert "Recent conversation" not in msg

    def test_build_user_message_with_context(self, disambiguator, candidates):
        """Test user message construction with context."""
        prompt = "Let's build a new feature"
        context = ["Previous message 1", "Previous message 2", "Previous message 3"]
        msg = disambiguator._build_user_message(prompt, candidates, context)

        assert "Let's build a new feature" in msg
        assert "Recent conversation" in msg
        assert "Previous message 1" in msg
        assert "Previous message 2" in msg
        assert "Previous message 3" in msg

    def test_parse_response_valid(self, disambiguator, candidates):
        """Test parsing valid LLM response."""
        response_text = "implementation\nThe user wants to write code for a feature."

        triad, confidence, reasoning = disambiguator._parse_response(
            response_text, candidates
        )

        assert triad == "implementation"
        assert confidence == 0.90
        assert "write code" in reasoning

    def test_parse_response_no_reasoning(self, disambiguator, candidates):
        """Test parsing response without reasoning."""
        response_text = "design"

        triad, confidence, reasoning = disambiguator._parse_response(
            response_text, candidates
        )

        assert triad == "design"
        assert confidence == 0.90
        assert reasoning == "No reasoning provided"

    def test_parse_response_invalid_triad_partial_match(
        self, disambiguator, candidates
    ):
        """Test parsing response with partial triad name match."""
        response_text = "implementation phase\nUser wants to code."

        triad, confidence, reasoning = disambiguator._parse_response(
            response_text, candidates
        )

        assert triad == "implementation"
        assert confidence == 0.90

    def test_parse_response_invalid_triad_fallback(
        self, disambiguator, candidates
    ):
        """Test parsing response with completely invalid triad name."""
        response_text = "invalid-triad\nSome reasoning."

        triad, confidence, reasoning = disambiguator._parse_response(
            response_text, candidates
        )

        # Should fallback to highest semantic candidate
        assert triad == "implementation"
        assert confidence == 0.90
        assert "unclear" in reasoning.lower()

    @pytest.mark.skipif(not ANTHROPIC_AVAILABLE, reason="anthropic not installed")
    @patch("anthropic.Anthropic")
    def test_disambiguate_success(
        self, mock_anthropic_class, disambiguator, candidates
    ):
        """Test successful disambiguation."""
        # Mock the API response
        mock_response = Mock()
        mock_response.content = [
            Mock(text="implementation\nUser wants to implement a feature.")
        ]

        mock_client = Mock()
        mock_client.messages.create.return_value = mock_response
        disambiguator.client = mock_client

        prompt = "Let's build this feature"
        triad, confidence, reasoning = disambiguator.disambiguate(
            prompt, candidates
        )

        assert triad == "implementation"
        assert confidence == 0.90
        assert "implement a feature" in reasoning

        # Verify API was called correctly
        mock_client.messages.create.assert_called_once()
        call_kwargs = mock_client.messages.create.call_args[1]
        assert call_kwargs["model"] == "claude-3-5-sonnet-20241022"
        assert call_kwargs["max_tokens"] == 200
        assert call_kwargs["temperature"] == 0.0
        assert call_kwargs["timeout"] == 2.0

    @pytest.mark.skipif(not ANTHROPIC_AVAILABLE, reason="anthropic not installed")
    @patch("anthropic.Anthropic")
    def test_disambiguate_timeout(
        self, mock_anthropic_class, disambiguator, candidates
    ):
        """Test disambiguation timeout."""
        mock_client = Mock()
        mock_client.messages.create.side_effect = anthropic.APITimeoutError(
            "Timeout"
        )
        disambiguator.client = mock_client

        prompt = "Let's build this feature"

        with pytest.raises(TimeoutError, match="timed out after 2000ms"):
            disambiguator.disambiguate(prompt, candidates)

    @pytest.mark.skipif(not ANTHROPIC_AVAILABLE, reason="anthropic not installed")
    @patch("anthropic.Anthropic")
    def test_disambiguate_with_retry_success_first_attempt(
        self, mock_anthropic_class, disambiguator, candidates
    ):
        """Test retry succeeds on first attempt."""
        mock_response = Mock()
        mock_response.content = [Mock(text="design\nUser needs architecture.")]

        mock_client = Mock()
        mock_client.messages.create.return_value = mock_response
        disambiguator.client = mock_client

        prompt = "Let's plan the architecture"
        triad, confidence, reasoning = disambiguator.disambiguate_with_retry(
            prompt, candidates, max_retries=2
        )

        assert triad == "design"
        assert confidence == 0.90
        mock_client.messages.create.assert_called_once()

    @pytest.mark.skipif(not ANTHROPIC_AVAILABLE, reason="anthropic not installed")
    @patch("anthropic.Anthropic")
    @patch("time.sleep")  # Mock sleep to speed up tests
    def test_disambiguate_with_retry_timeout_then_success(
        self, mock_sleep, mock_anthropic_class, disambiguator, candidates
    ):
        """Test retry succeeds after timeout."""
        mock_response = Mock()
        mock_response.content = [Mock(text="implementation\nBuild feature.")]

        mock_client = Mock()
        mock_client.messages.create.side_effect = [
            anthropic.APITimeoutError("Timeout"),
            mock_response,
        ]
        disambiguator.client = mock_client

        prompt = "Build this"
        triad, confidence, reasoning = disambiguator.disambiguate_with_retry(
            prompt, candidates, max_retries=2
        )

        assert triad == "implementation"
        assert confidence == 0.90
        assert mock_client.messages.create.call_count == 2
        mock_sleep.assert_called_once_with(0.5)  # 500ms

    @pytest.mark.skipif(not ANTHROPIC_AVAILABLE, reason="anthropic not installed")
    @patch("anthropic.Anthropic")
    @patch("time.sleep")
    def test_disambiguate_with_retry_exhausted(
        self, mock_sleep, mock_anthropic_class, disambiguator, candidates
    ):
        """Test retry exhausted after max attempts."""
        mock_client = Mock()
        mock_client.messages.create.side_effect = anthropic.APITimeoutError(
            "Timeout"
        )
        disambiguator.client = mock_client

        prompt = "Build this"

        with pytest.raises(TimeoutError):
            disambiguator.disambiguate_with_retry(
                prompt, candidates, max_retries=2
            )

        # Should try 3 times (initial + 2 retries)
        assert mock_client.messages.create.call_count == 3
        # Should sleep twice (after 1st and 2nd failures)
        assert mock_sleep.call_count == 2

    @pytest.mark.skipif(not ANTHROPIC_AVAILABLE, reason="anthropic not installed")
    @patch("anthropic.Anthropic")
    def test_disambiguate_with_retry_auth_error_no_retry(
        self, mock_anthropic_class, disambiguator, candidates
    ):
        """Test authentication error doesn't retry."""
        mock_client = Mock()
        # Create a mock response for AuthenticationError
        mock_response = Mock()
        mock_response.request = Mock()
        mock_client.messages.create.side_effect = (
            anthropic.AuthenticationError("Invalid key", response=mock_response, body=None)
        )
        disambiguator.client = mock_client

        prompt = "Build this"

        with pytest.raises(anthropic.AuthenticationError):
            disambiguator.disambiguate_with_retry(
                prompt, candidates, max_retries=2
            )

        # Should not retry auth errors
        mock_client.messages.create.assert_called_once()

    @pytest.mark.skipif(not ANTHROPIC_AVAILABLE, reason="anthropic not installed")
    @patch("anthropic.Anthropic")
    @patch("time.sleep")
    def test_disambiguate_with_retry_connection_error(
        self, mock_sleep, mock_anthropic_class, disambiguator, candidates
    ):
        """Test retry on connection error."""
        mock_response = Mock()
        mock_response.content = [Mock(text="design\nArchitecture needed.")]

        mock_client = Mock()
        # Create a mock request for APIConnectionError
        mock_request = Mock()
        mock_client.messages.create.side_effect = [
            anthropic.APIConnectionError(message="Connection failed", request=mock_request),
            mock_response,
        ]
        disambiguator.client = mock_client

        prompt = "Plan architecture"
        triad, confidence, reasoning = disambiguator.disambiguate_with_retry(
            prompt, candidates, max_retries=2
        )

        assert triad == "design"
        assert mock_client.messages.create.call_count == 2
        mock_sleep.assert_called_once_with(0.5)

    @pytest.mark.skipif(not ANTHROPIC_AVAILABLE, reason="anthropic not installed")
    @patch("anthropic.Anthropic")
    @patch("time.sleep")
    def test_disambiguate_with_retry_rate_limit(
        self, mock_sleep, mock_anthropic_class, disambiguator, candidates
    ):
        """Test retry with longer wait on rate limit."""
        mock_response = Mock()
        mock_response.content = [Mock(text="implementation\nCode feature.")]

        mock_client = Mock()
        # Create a mock response for RateLimitError
        mock_http_response = Mock()
        mock_http_response.request = Mock()
        mock_client.messages.create.side_effect = [
            anthropic.RateLimitError("Rate limited", response=mock_http_response, body=None),
            mock_response,
        ]
        disambiguator.client = mock_client

        prompt = "Build feature"
        triad, confidence, reasoning = disambiguator.disambiguate_with_retry(
            prompt, candidates, max_retries=2
        )

        assert triad == "implementation"
        assert mock_client.messages.create.call_count == 2
        # Rate limit should wait longer (1000ms)
        mock_sleep.assert_called_once_with(1.0)


class TestDisambiguationError:
    """Test DisambiguationError exception."""

    def test_exception_creation(self):
        """Test creating DisambiguationError."""
        error = DisambiguationError("Test error message")
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)
