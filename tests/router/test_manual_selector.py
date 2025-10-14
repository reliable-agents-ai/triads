"""Tests for manual triad selection UI."""

from unittest.mock import patch

import pytest

from src.triads.router.manual_selector import ManualSelector


class TestManualSelector:
    """Test manual triad selection UI."""

    @pytest.fixture
    def selector(self):
        """Create ManualSelector instance."""
        return ManualSelector()

    @pytest.fixture
    def candidates(self):
        """Sample candidates for testing."""
        return [
            ("implementation", 0.75),
            ("design", 0.73),
            ("garden-tending", 0.70),
        ]

    def test_format_reason_llm_failure(self, selector):
        """Test formatting of llm_failure reason."""
        formatted = selector._format_reason("llm_failure")
        assert "LLM disambiguation failed" in formatted
        assert "timeout or API error" in formatted

    def test_format_reason_low_confidence(self, selector):
        """Test formatting of low_confidence reason."""
        formatted = selector._format_reason("low_confidence")
        assert "Semantic routing confidence too low" in formatted

    def test_format_reason_disambiguation_needed(self, selector):
        """Test formatting of disambiguation_needed reason."""
        formatted = selector._format_reason("disambiguation_needed")
        assert "Multiple triads are similar matches" in formatted

    def test_format_reason_user_requested(self, selector):
        """Test formatting of user_requested reason."""
        formatted = selector._format_reason("user_requested")
        assert "Manual selection requested" in formatted

    def test_format_reason_unknown(self, selector):
        """Test formatting of unknown reason falls back to raw value."""
        formatted = selector._format_reason("unknown_reason")
        assert formatted == "unknown_reason"

    def test_get_triad_description_idea_validation(self, selector):
        """Test description for idea-validation triad."""
        desc = selector._get_triad_description("idea-validation")
        assert "Research ideas" in desc
        assert "validate with community" in desc

    def test_get_triad_description_design(self, selector):
        """Test description for design triad."""
        desc = selector._get_triad_description("design")
        assert "Create ADRs" in desc
        assert "design solutions" in desc

    def test_get_triad_description_implementation(self, selector):
        """Test description for implementation triad."""
        desc = selector._get_triad_description("implementation")
        assert "Write production code" in desc
        assert "implement features" in desc

    def test_get_triad_description_garden_tending(self, selector):
        """Test description for garden-tending triad."""
        desc = selector._get_triad_description("garden-tending")
        assert "Refactor code" in desc
        assert "improve quality" in desc

    def test_get_triad_description_deployment(self, selector):
        """Test description for deployment triad."""
        desc = selector._get_triad_description("deployment")
        assert "Create releases" in desc
        assert "update docs" in desc

    def test_get_triad_description_unknown(self, selector):
        """Test description for unknown triad."""
        desc = selector._get_triad_description("unknown-triad")
        assert desc == "No description available"

    @patch("builtins.input", return_value="1")
    @patch("builtins.print")
    def test_select_triad_first_option(
        self, mock_print, mock_input, selector, candidates
    ):
        """Test selecting first triad option."""
        prompt = "Build a feature"
        selected_triad, reason = selector.select_triad(
            prompt, candidates, reason="low_confidence"
        )

        assert selected_triad == "implementation"
        assert reason == "low_confidence"

        # Verify output formatting
        print_calls = [str(call) for call in mock_print.call_args_list]
        output = " ".join(print_calls)
        assert "Build a feature" in output
        assert "implementation" in output

    @patch("builtins.input", return_value="2")
    @patch("builtins.print")
    def test_select_triad_second_option(
        self, mock_print, mock_input, selector, candidates
    ):
        """Test selecting second triad option."""
        prompt = "Plan architecture"
        selected_triad, reason = selector.select_triad(
            prompt, candidates, reason="disambiguation_needed"
        )

        assert selected_triad == "design"
        assert reason == "disambiguation_needed"

    @patch("builtins.input", return_value="3")
    @patch("builtins.print")
    def test_select_triad_third_option(
        self, mock_print, mock_input, selector, candidates
    ):
        """Test selecting third triad option."""
        prompt = "Clean up code"
        selected_triad, reason = selector.select_triad(
            prompt, candidates, reason="llm_failure"
        )

        assert selected_triad == "garden-tending"
        assert reason == "llm_failure"

    @patch("builtins.input", return_value="c")
    @patch("builtins.print")
    def test_select_triad_cancel(
        self, mock_print, mock_input, selector, candidates
    ):
        """Test cancelling triad selection."""
        prompt = "Maybe do something"
        selected_triad, reason = selector.select_triad(
            prompt, candidates, reason="low_confidence"
        )

        assert selected_triad is None
        assert reason == "user_cancelled"

    @patch("builtins.input", side_effect=["4", "0", "2"])
    @patch("builtins.print")
    def test_select_triad_invalid_then_valid(
        self, mock_print, mock_input, selector, candidates
    ):
        """Test invalid input followed by valid selection."""
        prompt = "Do something"
        selected_triad, reason = selector.select_triad(
            prompt, candidates, reason="low_confidence"
        )

        assert selected_triad == "design"
        assert reason == "low_confidence"

        # Check error messages were printed
        print_calls = [str(call) for call in mock_print.call_args_list]
        output = " ".join(print_calls)
        assert "Invalid choice" in output

    @patch("builtins.input", side_effect=["invalid", "abc", "1"])
    @patch("builtins.print")
    def test_select_triad_non_numeric_then_valid(
        self, mock_print, mock_input, selector, candidates
    ):
        """Test non-numeric input followed by valid selection."""
        prompt = "Do something"
        selected_triad, reason = selector.select_triad(
            prompt, candidates, reason="low_confidence"
        )

        assert selected_triad == "implementation"
        assert reason == "low_confidence"

        # Check error messages were printed
        print_calls = [str(call) for call in mock_print.call_args_list]
        output = " ".join(print_calls)
        assert "Invalid input" in output

    @patch("builtins.input", return_value="1")
    @patch("builtins.print")
    def test_select_triad_long_prompt_truncated(
        self, mock_print, mock_input, selector, candidates
    ):
        """Test that long prompts are truncated in display."""
        prompt = "x" * 150  # Very long prompt
        selected_triad, reason = selector.select_triad(
            prompt, candidates, reason="low_confidence"
        )

        assert selected_triad == "implementation"

        # Check prompt was truncated
        print_calls = [str(call) for call in mock_print.call_args_list]
        output = " ".join(print_calls)
        assert "..." in output  # Ellipsis indicates truncation

    @patch("builtins.input", return_value="1")
    @patch("builtins.print")
    def test_select_triad_shows_confidence_scores(
        self, mock_print, mock_input, selector, candidates
    ):
        """Test that confidence scores are displayed."""
        prompt = "Do something"
        selector.select_triad(prompt, candidates, reason="low_confidence")

        print_calls = [str(call) for call in mock_print.call_args_list]
        output = " ".join(print_calls)

        # Check confidence scores are shown
        assert "75%" in output
        assert "73%" in output
        assert "70%" in output

    @patch("builtins.input", return_value="1")
    @patch("builtins.print")
    def test_select_triad_shows_descriptions(
        self, mock_print, mock_input, selector, candidates
    ):
        """Test that triad descriptions are displayed."""
        prompt = "Do something"
        selector.select_triad(prompt, candidates, reason="low_confidence")

        print_calls = [str(call) for call in mock_print.call_args_list]
        output = " ".join(print_calls)

        # Check descriptions are shown
        assert "Write production code" in output
        assert "Create ADRs" in output
        assert "Refactor code" in output
