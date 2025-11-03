"""Context switch detection using Claude Code headless.

Constitutional TDD: GREEN Phase
Minimal implementation to make tests pass.

Uses Claude Code subprocess pattern for consistency with routing
(matches src/triads/llm_routing.py:274-330).
"""

import json
import re
import subprocess
from enum import Enum
from typing import Any, Dict, Optional


class ContextClassification(str, Enum):
    """Context switch classification types."""

    CONTINUATION = "CONTINUATION"  # User continues existing workspace
    NEW_WORK = "NEW_WORK"  # User requests completely different task
    QA = "QA"  # User asks question without changing context
    REFERENCE = "REFERENCE"  # User provides reference info without task change


def detect_context_switch(
    user_message: str, workspace_context: Optional[str]
) -> Dict[str, Any]:
    """Detect context switch using Claude Code headless subprocess.

    Uses simplified single-message approach for better reliability.

    Args:
        user_message: User's input message
        workspace_context: Current workspace context (None if no active workspace)

    Returns:
        {
            "classification": ContextClassification enum value,
            "confidence": float 0.0-1.0,
            "reasoning": str explanation,
            "needs_manual_confirmation": bool (True if confidence < 0.80),
            "cost_usd": float API cost,
            "duration_ms": int latency
        }

    Raises:
        RuntimeError: If Claude Code returns error
        json.JSONDecodeError: If response is invalid JSON

    Example:
        >>> result = detect_context_switch(
        ...     user_message="yes please, let's proceed",
        ...     workspace_context="Implementing workspace architecture Phase 1"
        ... )
        >>> result["classification"]
        <ContextClassification.CONTINUATION: 'CONTINUATION'>
        >>> result["confidence"]
        0.95
    """
    # Format context for clarity
    context_text = workspace_context or "No active workspace"

    # Build a single, consolidated prompt with mandatory JSON structure
    prompt = f"""MANDATORY: Respond with ONLY a valid JSON object following this exact structure:
{{
    "classification": "CONTINUATION|NEW_WORK|QA|REFERENCE",
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation"
}}

Classify this user message based on the current workspace context.

Classifications:
- CONTINUATION: User continues current workspace (feedback, approval, refinement)
- NEW_WORK: User requests completely different task unrelated to current context
- QA: User asks question about current work (no context change)
- REFERENCE: User provides clarification/reference info (no task change)

Current Workspace Context: {context_text}
User Message: "{user_message}"

Examples:
- "yes please, let's proceed" → CONTINUATION (high confidence)
- "Can you help me write a CSV parser?" → NEW_WORK (if workspace is about OAuth)
- "What coverage did we achieve?" → QA
- "One thing to note about X..." → REFERENCE

Classify the message and respond with the JSON structure above."""

    # Call Claude Code headless with simplified approach
    result = subprocess.run(
        [
            "claude",
            "-p",
            prompt,
            "--output-format",
            "json",
        ],
        capture_output=True,
        text=True,
        # No timeout - let it complete
        check=True,
    )

    # Parse outer JSON wrapper from --output-format json
    response = json.loads(result.stdout)

    # Handle Claude Code errors
    if response.get("is_error"):
        raise RuntimeError(f"Claude Code error: {response.get('result')}")

    # Extract JSON from the response (Claude may wrap it in markdown)
    result_text = response["result"]

    # Try to extract JSON from the response
    # Claude might wrap it in ```json blocks or include extra text
    # Look for JSON object in the response
    json_match = re.search(r'\{[^{}]*"classification"[^{}]*\}', result_text, re.DOTALL)
    if json_match:
        json_str = json_match.group()
        detection_result = json.loads(json_str)
    else:
        # If no JSON found, raise an error
        raise json.JSONDecodeError(
            f"No valid JSON found in response: {result_text[:200]}...",
            result_text,
            0
        )

    # Add metadata
    detection_result["cost_usd"] = response.get("total_cost_usd", 0.0)
    detection_result["duration_ms"] = response.get("duration_ms", 0)

    # Convert classification string to enum
    detection_result["classification"] = ContextClassification(
        detection_result["classification"]
    )

    # Flag for manual confirmation if confidence < 80%
    detection_result["needs_manual_confirmation"] = (
        detection_result["confidence"] < 0.80
    )

    return detection_result
