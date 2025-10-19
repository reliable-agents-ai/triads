"""Experience tracker for confidence-based learning.

This module tracks which lessons are injected and detects outcomes
(success/failure/contradiction) to update confidence scores using Bayesian methods.

Key Features:
- Tracks lesson injections per session
- Detects outcomes from conversation analysis
- Updates confidence scores using Bayesian formulas
- Persists state to .claude/experience_state.json

Architecture:
- ExperienceTracker: Main class for tracking and outcome detection
- InjectionRecord: Data class for tracking what was injected
- OutcomeDetector: Analyzes conversation for lesson outcomes

Performance:
- State file is small (~1KB per session)
- Outcome detection is O(n) where n = conversation length
- Runs at session end only (not performance critical)

Usage:
    # In PreToolUse hook - track injection
    tracker = ExperienceTracker()
    tracker.record_injection(lesson_id, lesson_label, tool_name)

    # In Stop hook - detect outcomes and update
    tracker = ExperienceTracker()
    outcomes = tracker.detect_outcomes(conversation_text)
    tracker.update_confidence_scores(outcomes)
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from triads.km.confidence import update_confidence
from triads.hooks.safe_io import safe_load_json_file, safe_save_json_file


# ============================================================================
# Data Classes
# ============================================================================


@dataclass
class InjectionRecord:
    """Record of a lesson injection.

    Attributes:
        lesson_id: Unique ID of the lesson node
        triad: Source triad name
        label: Human-readable lesson label
        tool_name: Tool that triggered injection
        injected_at: ISO timestamp of injection
        confidence: Confidence score at injection time
    """
    lesson_id: str
    triad: str
    label: str
    tool_name: str
    injected_at: str
    confidence: float


@dataclass
class OutcomeRecord:
    """Record of a detected outcome.

    Attributes:
        lesson_id: Unique ID of the lesson node
        outcome: Type of outcome (success, failure, contradiction, validation)
        evidence: Text evidence supporting the outcome
        strength: Strength of evidence (0.0-1.0, default 1.0)
        detected_at: ISO timestamp of detection
    """
    lesson_id: str
    outcome: str  # success, failure, contradiction, validation
    evidence: str
    strength: float = 1.0
    detected_at: str = ""

    def __post_init__(self):
        if not self.detected_at:
            self.detected_at = datetime.now(timezone.utc).isoformat()


# ============================================================================
# ExperienceTracker: Main tracking class
# ============================================================================


class ExperienceTracker:
    """Tracks lesson injections and detects outcomes.

    Manages the experience state file which records:
    - Which lessons were injected during the session
    - When they were injected and for which tools
    - Detected outcomes and evidence

    State file: .claude/experience_state.json
    Format:
        {
            "session_id": "2025-10-19T12:34:56",
            "injections": [{lesson_id, triad, label, tool_name, injected_at, confidence}],
            "outcomes": [{lesson_id, outcome, evidence, strength, detected_at}]
        }
    """

    def __init__(self, base_dir: Path | None = None):
        """Initialize experience tracker.

        Args:
            base_dir: Base directory (contains .claude/). Defaults to cwd.
        """
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.state_file = self.base_dir / ".claude" / "experience_state.json"
        self._ensure_state_file()

    def _ensure_state_file(self) -> None:
        """Ensure state file exists with valid structure."""
        if not self.state_file.exists():
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            initial_state = {
                "session_id": datetime.now(timezone.utc).isoformat(),
                "injections": [],
                "outcomes": []
            }
            safe_save_json_file(self.state_file, initial_state)

    def record_injection(
        self,
        lesson_id: str,
        triad: str,
        label: str,
        tool_name: str,
        confidence: float
    ) -> None:
        """Record that a lesson was injected.

        Args:
            lesson_id: Unique ID of the lesson node
            triad: Source triad name
            label: Human-readable lesson label
            tool_name: Tool that triggered injection
            confidence: Confidence score at injection time
        """
        state = safe_load_json_file(self.state_file, default={})

        if "injections" not in state:
            state["injections"] = []

        record = InjectionRecord(
            lesson_id=lesson_id,
            triad=triad,
            label=label,
            tool_name=tool_name,
            injected_at=datetime.now(timezone.utc).isoformat(),
            confidence=confidence
        )

        state["injections"].append(asdict(record))
        safe_save_json_file(self.state_file, state)

    def detect_outcomes(self, conversation_text: str) -> list[OutcomeRecord]:
        """Detect outcomes from conversation analysis.

        Analyzes conversation for evidence of:
        - Success: Lesson was followed
        - Failure: Lesson was ignored/forgotten
        - Contradiction: Lesson was proven wrong
        - Validation: User explicitly validated lesson

        Args:
            conversation_text: Full conversation transcript

        Returns:
            List of detected outcomes
        """
        state = safe_load_json_file(self.state_file, default={})
        injections = state.get("injections", [])

        if not injections:
            return []

        outcomes = []
        detector = OutcomeDetector(conversation_text)

        for injection in injections:
            lesson_id = injection["lesson_id"]
            label = injection["label"]

            # Detect each outcome type
            outcome_type, evidence, strength = detector.detect_for_lesson(label)

            if outcome_type:
                outcomes.append(OutcomeRecord(
                    lesson_id=lesson_id,
                    outcome=outcome_type,
                    evidence=evidence,
                    strength=strength
                ))

        # Save outcomes to state
        if outcomes:
            if "outcomes" not in state:
                state["outcomes"] = []
            state["outcomes"].extend([asdict(o) for o in outcomes])
            safe_save_json_file(self.state_file, state)

        return outcomes

    def clear_session(self) -> None:
        """Clear session state (start fresh)."""
        new_state = {
            "session_id": datetime.now(timezone.utc).isoformat(),
            "injections": [],
            "outcomes": []
        }
        safe_save_json_file(self.state_file, new_state)


# ============================================================================
# OutcomeDetector: Conversation analysis for outcomes
# ============================================================================


class OutcomeDetector:
    """Detects lesson outcomes from conversation analysis.

    Uses pattern matching to detect:
    - Success: User followed the lesson
    - Failure: User forgot/ignored the lesson
    - Contradiction: User found the lesson wrong
    - Validation: User explicitly validated the lesson
    """

    # Patterns for outcome detection
    SUCCESS_PATTERNS = [
        r"followed.*checklist",
        r"completed.*all.*items",
        r"verified.*all.*required",
        r"checked.*all",
        r"applied.*pattern",
        r"followed.*guidance",
    ]

    FAILURE_PATTERNS = [
        r"forgot.*to",
        r"missed.*item",
        r"didn'?t.*check",
        r"should.*have.*checked",
        r"overlooked",
        r"failed.*to.*verify",
    ]

    CONTRADICTION_PATTERNS = [
        r"(?:was|is).*(?:wrong|incorrect)",
        r"actually.*(?:should|shouldn'?t)",
        r"incorrect.*(?:advice|checklist|pattern)",
        r"better.*approach.*(?:is|would be)",
        r"doesn'?t.*(?:work|apply)",
    ]

    VALIDATION_PATTERNS = [
        r"that.*was.*helpful",
        r"good.*(?:catch|reminder)",
        r"prevented.*mistake",
        r"avoided.*(?:error|issue)",
        r"thanks.*for.*(?:reminder|warning)",
    ]

    def __init__(self, conversation_text: str):
        """Initialize detector with conversation text.

        Args:
            conversation_text: Full conversation transcript
        """
        self.text = conversation_text.lower()

    def detect_for_lesson(self, lesson_label: str) -> tuple[str, str, float]:
        """Detect outcome for a specific lesson.

        Args:
            lesson_label: Human-readable lesson label

        Returns:
            Tuple of (outcome_type, evidence, strength)
            Returns ("", "", 0.0) if no outcome detected
        """
        # Search for lesson mention in conversation
        label_lower = lesson_label.lower()

        # Extract context around lesson mention (±100 chars)
        pattern = re.escape(label_lower)
        match = re.search(pattern, self.text)

        if not match:
            # Lesson not mentioned - could mean success (silently followed)
            # or not applicable (tool wasn't used)
            # Don't assume either way
            return ("", "", 0.0)

        start = max(0, match.start() - 100)
        end = min(len(self.text), match.end() + 100)
        context = self.text[start:end]

        # Check patterns in order of priority
        # 1. Contradiction (strongest signal)
        for pattern in self.CONTRADICTION_PATTERNS:
            if re.search(pattern, context, re.IGNORECASE):
                return ("contradiction", context, 1.0)

        # 2. Validation (explicit user feedback)
        for pattern in self.VALIDATION_PATTERNS:
            if re.search(pattern, context, re.IGNORECASE):
                return ("validation", context, 1.0)

        # 3. Failure (user admitted mistake)
        for pattern in self.FAILURE_PATTERNS:
            if re.search(pattern, context, re.IGNORECASE):
                return ("failure", context, 0.8)

        # 4. Success (user confirmed following)
        for pattern in self.SUCCESS_PATTERNS:
            if re.search(pattern, context, re.IGNORECASE):
                return ("success", context, 0.8)

        # Lesson mentioned but no clear outcome
        # Could be neutral reference
        return ("", "", 0.0)
