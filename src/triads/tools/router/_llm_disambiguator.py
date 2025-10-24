"""
LLM-based disambiguation for ambiguous routing decisions.

Uses Claude API to determine the best triad when semantic routing is uncertain.
"""

import os
import time
from typing import List, Optional, Tuple

import anthropic


class LLMDisambiguator:
    """
    Claude API client for disambiguating low-confidence or ambiguous prompts.

    Uses Claude 3.5 Sonnet to determine the best triad when semantic routing
    confidence is low or multiple candidates have similar scores.
    """

    def __init__(self, timeout_ms: int = 2000):
        """
        Initialize LLM disambiguator.

        Args:
            timeout_ms: Timeout in milliseconds for API calls (default: 2000ms)

        Raises:
            ValueError: If ANTHROPIC_API_KEY environment variable is not set
        """
        # Get API key from environment
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        self.client = anthropic.Anthropic(api_key=api_key)
        self.timeout_ms = timeout_ms
        self.model = "claude-3-5-sonnet-20241022"

    def disambiguate(
        self,
        prompt: str,
        candidates: List[Tuple[str, float]],
        context: Optional[List[str]] = None,
    ) -> Tuple[str, float, str]:
        """
        Use LLM to determine the best triad for an ambiguous prompt.

        Args:
            prompt: User's input prompt
            candidates: Top 3 (triad_name, confidence) tuples from semantic routing
            context: Recent conversation messages (optional)

        Returns:
            Tuple of (triad_name, confidence, reasoning)

        Raises:
            TimeoutError: If LLM call exceeds timeout_ms
            anthropic.APIError: If API call fails
        """
        start_time = time.time()

        # Build disambiguation prompt
        system_prompt = self._build_system_prompt()
        user_message = self._build_user_message(prompt, candidates, context)

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=200,
                temperature=0.0,  # Deterministic
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
                timeout=self.timeout_ms / 1000.0,  # Convert to seconds
            )

            elapsed_ms = (time.time() - start_time) * 1000

            # Parse response
            result = self._parse_response(response.content[0].text, candidates)
            return result

        except anthropic.APITimeoutError:
            raise TimeoutError(
                f"LLM disambiguation timed out after {self.timeout_ms}ms"
            )
        except anthropic.APIError:
            raise

    def _build_system_prompt(self) -> str:
        """Build system prompt for LLM disambiguation."""
        return """You are a routing assistant that determines which triad (workflow phase) best matches a user's prompt.

Your task: Analyze the user's prompt and select the most appropriate triad from the candidates provided.

Triads:
- idea-validation: Research and validate new ideas, assess demand, determine priority
- design: Create architectural decisions, design solutions, write ADRs
- implementation: Write production code, implement features
- garden-tending: Refactor code, improve quality, reduce technical debt
- deployment: Create releases, update documentation, publish versions

Respond with ONLY the triad name (lowercase, hyphenated) followed by your reasoning on the next line.
Example:
implementation
The user wants to write code for a specific feature."""

    def _build_user_message(
        self,
        prompt: str,
        candidates: List[Tuple[str, float]],
        context: Optional[List[str]],
    ) -> str:
        """Build user message with prompt, candidates, and optional context."""
        msg = f"User prompt: {prompt}\n\n"

        if context:
            msg += "Recent conversation:\n"
            for msg_text in context[-3:]:  # Last 3 messages
                msg += f"- {msg_text}\n"
            msg += "\n"

        msg += "Candidate triads (from semantic analysis):\n"
        for triad, score in candidates:
            msg += f"- {triad} (confidence: {score:.2f})\n"

        msg += "\nWhich triad best fits this prompt?"
        return msg

    def _parse_response(
        self, response_text: str, candidates: List[Tuple[str, float]]
    ) -> Tuple[str, float, str]:
        """
        Parse LLM response to extract triad name and reasoning.

        Expected format:
        triad-name
        Reasoning text here...

        Args:
            response_text: Raw LLM response
            candidates: Original candidates for validation

        Returns:
            Tuple of (triad_name, confidence, reasoning)
        """
        lines = response_text.strip().split("\n", 1)

        triad_name = lines[0].strip().lower()
        reasoning = lines[1].strip() if len(lines) > 1 else "No reasoning provided"

        # Validate triad name is in candidates
        candidate_names = [name for name, _ in candidates]
        if triad_name not in candidate_names:
            # Try to find closest match
            for name in candidate_names:
                if name in triad_name or triad_name in name:
                    triad_name = name
                    break
            else:
                # Fallback to highest semantic score
                triad_name = candidates[0][0]
                reasoning = (
                    f"LLM response unclear, using highest semantic match. "
                    f"Original: {response_text}"
                )

        # Confidence for LLM disambiguation is typically high (0.90)
        confidence = 0.90

        return (triad_name, confidence, reasoning)

    def disambiguate_with_retry(
        self,
        prompt: str,
        candidates: List[Tuple[str, float]],
        context: Optional[List[str]] = None,
        max_retries: int = 2,
    ) -> Tuple[str, float, str]:
        """
        Disambiguate with exponential backoff retry.

        Retries on:
        - TimeoutError
        - anthropic.APIConnectionError
        - anthropic.RateLimitError

        Does NOT retry on:
        - anthropic.AuthenticationError (bad API key)
        - ValueError (invalid input)

        Args:
            prompt: User's input prompt
            candidates: Top 3 candidates from semantic routing
            context: Recent conversation messages (optional)
            max_retries: Maximum number of retries (default: 2)

        Returns:
            Tuple of (triad_name, confidence, reasoning)

        Raises:
            TimeoutError: If all retries timeout
            anthropic.APIConnectionError: If connection fails after retries
            anthropic.RateLimitError: If rate limited after retries
            anthropic.AuthenticationError: If API key is invalid
        """
        for attempt in range(max_retries + 1):
            try:
                return self.disambiguate(prompt, candidates, context)

            except TimeoutError:
                if attempt == max_retries:
                    raise
                wait_ms = 500 * (2**attempt)  # 500ms, 1000ms
                time.sleep(wait_ms / 1000.0)

            except anthropic.APIConnectionError:
                if attempt == max_retries:
                    raise
                wait_ms = 500 * (2**attempt)
                time.sleep(wait_ms / 1000.0)

            except anthropic.RateLimitError:
                if attempt == max_retries:
                    raise
                wait_ms = 1000 * (2**attempt)  # Longer wait for rate limits
                time.sleep(wait_ms / 1000.0)

            except anthropic.AuthenticationError:
                # Don't retry auth errors
                raise

        # Should never reach here, but satisfy type checker
        raise RuntimeError("Retry loop failed unexpectedly")


class DisambiguationError(Exception):
    """Raised when LLM disambiguation fails and manual selection is required."""

    pass
