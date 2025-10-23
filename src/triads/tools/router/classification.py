"""Workflow classification using Claude headless mode.

Per ADR-013 (REVISED): Use `claude -p` subprocess for workflow gap detection and classification.
Simpler implementation (~30 lines vs ~500), better accuracy (LLM understanding vs keywords),
acceptable latency (~9s on rare gap detection events).

Performance Target: ~9s for classification (acceptable for rare gap detection events)

Moved from triads.workflow_matching.headless_classifier as part of Phase 9 DDD refactoring.
"""

import json
import subprocess
from dataclasses import dataclass
from typing import Optional
import logging

from triads.utils.command_runner import CommandRunner

logger = logging.getLogger(__name__)


# Configuration constants
HEADLESS_TIMEOUT_SEC = 30
HEADLESS_TARGET_LATENCY_SEC = 9


@dataclass
class HeadlessClassificationResult:
    """Result of headless workflow classification.

    Attributes:
        workflow_type: Matched workflow type or None if no match
        confidence: Confidence score between 0.0 and 1.0
        reasoning: LLM's reasoning for the classification
    """

    workflow_type: Optional[str]
    confidence: float
    reasoning: str


# Workflow definitions for classification
WORKFLOW_DEFINITIONS = {
    "bug-fix": "Fixing bugs, errors, crashes, broken functionality, or defects",
    "feature-dev": "Adding new features, functionality, capabilities, or enhancements",
    "performance": "Optimizing performance, speed, memory usage, or efficiency",
    "refactoring": "Refactoring, cleaning up code, reducing technical debt, improving code quality",
    "investigation": "Investigating issues, understanding behavior, analyzing root causes, exploring options",
}


def classify_workflow_headless(user_message: str) -> HeadlessClassificationResult:
    """Classify user message to workflow type using Claude headless mode.

    Args:
        user_message: User's request text

    Returns:
        HeadlessClassificationResult with workflow type and confidence

    Performance: 1-3s (acceptable for rare gap detection events)
    """
    # Handle edge cases
    if not user_message or not user_message.strip():
        return HeadlessClassificationResult(
            workflow_type=None, confidence=0.0, reasoning="Empty message"
        )

    # Build classification prompt
    prompt = _build_classification_prompt(user_message)

    try:
        # Call Claude API via headless mode
        response = _call_claude_api(prompt)

        # Parse response
        return _parse_classification_response(response)

    except TimeoutError as e:
        logger.warning(f"Claude API timeout: {e}")
        return HeadlessClassificationResult(
            workflow_type=None,
            confidence=0.0,
            reasoning=f"API timeout: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Claude API error: {e}")
        return HeadlessClassificationResult(
            workflow_type=None, confidence=0.0, reasoning=f"API error: {str(e)}"
        )


def _build_classification_prompt(user_message: str) -> str:
    """Build classification prompt for Claude.

    Args:
        user_message: User's request text

    Returns:
        Formatted prompt for Claude API
    """
    workflow_list = "\n".join(
        [f"- **{wf}**: {desc}" for wf, desc in WORKFLOW_DEFINITIONS.items()]
    )

    prompt = f"""Classify the following user request into one of these workflow types, or return "none" if no workflow matches:

{workflow_list}

User request: "{user_message}"

Respond in JSON format:
{{
  "workflow_type": "bug-fix" | "feature-dev" | "performance" | "refactoring" | "investigation" | null,
  "confidence": 0.0-1.0,
  "reasoning": "Brief explanation of classification"
}}

Rules:
- Return null for workflow_type if the request doesn't clearly match any workflow
- Confidence should be 0.0 if no match, otherwise 0.7-1.0 for clear matches
- Keep reasoning concise (1-2 sentences)"""

    return prompt


def _call_claude_api(prompt: str, timeout: int = HEADLESS_TIMEOUT_SEC) -> str:
    """Call Claude via headless mode (subprocess).

    Args:
        prompt: Classification prompt
        timeout: Command timeout in seconds (default: HEADLESS_TIMEOUT_SEC)

    Returns:
        JSON classification response

    Raises:
        TimeoutError: If command exceeds timeout
        Exception: For other errors
    """
    try:
        # Call claude -p with no tools for faster execution
        result = CommandRunner.run_claude(
            [
                "-p",
                prompt,
                "--allowedTools",
                "",  # No tools needed = faster
                "--output-format",
                "json",
            ],
            timeout=timeout
        )

        # Parse outer JSON response
        response = json.loads(result.stdout)

        # Extract the classification result from response
        if "result" not in response:
            raise Exception("No 'result' field in claude response")

        return response["result"]

    except TimeoutError:
        # CommandRunner already raises TimeoutError with formatted message
        raise
    except subprocess.CalledProcessError as e:
        raise Exception(f"Claude command failed: {e.stderr}")
    except FileNotFoundError:
        raise Exception("claude command not found. Is Claude Code installed?")
    except json.JSONDecodeError as e:
        raise Exception(f"Invalid JSON from claude: {e}")


def _parse_classification_response(response_text: str) -> HeadlessClassificationResult:
    """Parse Claude API response.

    Args:
        response_text: JSON classification from Claude API

    Returns:
        HeadlessClassificationResult parsed from response

    Raises:
        Exception: If response parsing fails
    """
    try:
        # Parse the classification JSON directly
        classification = json.loads(response_text)

        # Extract fields
        workflow_type = classification.get("workflow_type")
        confidence = float(classification.get("confidence", 0.0))
        reasoning = classification.get("reasoning", "No reasoning provided")

        return HeadlessClassificationResult(
            workflow_type=workflow_type, confidence=confidence, reasoning=reasoning
        )

    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse JSON response: {e}")
    except (KeyError, ValueError) as e:
        raise Exception(f"Invalid response format: {e}")
