"""Workspace context detection integration.

Constitutional TDD: GREEN Phase
Integrates context_detector.py with hooks for workspace lifecycle management.

This module sits between user input and supervisor routing, detecting context
switches to manage workspace lifecycle (pause, resume, create new workspace).
"""

import json
import sys
from pathlib import Path
from typing import Dict, Optional

# Add src to path for imports
repo_root = Path(__file__).parent.parent
if str(repo_root / "src") not in sys.path:
    sys.path.insert(0, str(repo_root / "src"))

from src.triads.context_detector import (  # noqa: E402
    ContextClassification,
    detect_context_switch,
)
from src.triads.workspace_manager import (  # noqa: E402
    get_active_workspace,
    mark_workspace_paused,
)
from src.triads.event_logger import log_event  # noqa: E402


def get_workspace_context_summary(workspace_id: str) -> Optional[str]:
    """Get brief summary of workspace context for detection.

    Args:
        workspace_id: Workspace identifier

    Returns:
        Brief context string (1-2 sentences) or None if workspace not found

    Example:
        >>> summary = get_workspace_context_summary("workspace-20251030-143022-oauth")
        >>> "Implementing OAuth2 authentication" in summary
        True
    """
    workspace_path = Path(".triads/workspaces") / workspace_id

    if not workspace_path.exists():
        return None

    try:
        # Load brief for context
        brief_file = workspace_path / "brief.json"
        if not brief_file.exists():
            return None

        with open(brief_file, "r") as f:
            brief = json.load(f)

        title = brief.get("title", "Unknown")
        summary = brief.get("summary", "")

        # Load state for current phase
        state_file = workspace_path / "state.json"
        current_phase = "unknown"
        if state_file.exists():
            with open(state_file, "r") as f:
                state = json.load(f)
            current_phase = state.get("current_phase", "unknown")

        return f"Currently {current_phase}: {title}. {summary[:100]}"

    except (json.JSONDecodeError, IOError):
        return None


def handle_context_switch(
    user_message: str, detection_result: Dict
) -> Dict[str, str]:
    """Handle context switch based on detection result.

    Args:
        user_message: User's input message
        detection_result: Result from detect_context_switch()

    Returns:
        {
            "action": "continue|pause_and_create|ask_user",
            "message": str (user-facing message if action needed),
            "workspace_action": "none|pause|create",
            "needs_confirmation": bool
        }

    Example:
        >>> result = handle_context_switch(
        ...     user_message="yes please",
        ...     detection_result={"classification": "CONTINUATION", "confidence": 0.95}
        ... )
        >>> result["action"]
        'continue'
    """
    classification = detection_result["classification"]
    confidence = detection_result["confidence"]
    needs_manual = detection_result.get("needs_manual_confirmation", False)

    active_workspace = get_active_workspace()

    # CONTINUATION: Continue existing workspace
    if classification == ContextClassification.CONTINUATION:
        if not active_workspace:
            # Continuation without active workspace (shouldn't happen, but handle)
            return {
                "action": "ask_user",
                "message": "You said 'continue', but there's no active workspace. Did you mean to start new work?",
                "workspace_action": "none",
                "needs_confirmation": True,
            }

        return {
            "action": "continue",
            "message": "",
            "workspace_action": "none",
            "needs_confirmation": False,
        }

    # QA or REFERENCE: Continue without workspace change
    if classification in [ContextClassification.QA, ContextClassification.REFERENCE]:
        return {
            "action": "continue",
            "message": "",
            "workspace_action": "none",
            "needs_confirmation": False,
        }

    # NEW_WORK: Pause current workspace and create new one
    if classification == ContextClassification.NEW_WORK:
        if active_workspace:
            # Pause existing workspace
            workspace_path = Path(".triads/workspaces") / active_workspace

            # Log context switch event
            log_event(
                workspace_path=workspace_path,
                subject="workspace",
                predicate="context_switch_detected",
                object_data={
                    "user_message": user_message,
                    "classification": classification.value,
                    "confidence": confidence,
                    "new_work_detected": True,
                },
            )

            if needs_manual or confidence < 0.85:
                # Low confidence - ask user
                current_context = get_workspace_context_summary(active_workspace)
                return {
                    "action": "ask_user",
                    "message": f"I detected a possible context switch (confidence: {confidence*100:.0f}%).\n\n"
                    f"**Current Workspace**: {current_context}\n"
                    f"**Your Message**: {user_message}\n\n"
                    f"Do you want to:\n"
                    f"1. **Continue** current workspace\n"
                    f"2. **Pause** current workspace and start new work",
                    "workspace_action": "none",
                    "needs_confirmation": True,
                }

            # High confidence - auto-pause and notify
            mark_workspace_paused(active_workspace, reason="Context switch detected")

            current_context = get_workspace_context_summary(active_workspace)
            return {
                "action": "pause_and_create",
                "message": f"⏸️  **Context Switch Detected** (confidence: {confidence*100:.0f}%)\n\n"
                f"I've paused your current workspace:\n"
                f"{current_context}\n\n"
                f"Starting new workspace for: {user_message[:60]}...\n\n"
                f"You can resume the paused workspace anytime by saying 'resume {active_workspace}'",
                "workspace_action": "pause",
                "needs_confirmation": False,
            }

        # No active workspace - just create new one
        return {
            "action": "continue",
            "message": "",
            "workspace_action": "create",
            "needs_confirmation": False,
        }

    # Fallback (shouldn't reach here)
    return {
        "action": "continue",
        "message": "",
        "workspace_action": "none",
        "needs_confirmation": False,
    }


def detect_and_handle_context_switch(user_message: str) -> Optional[Dict]:
    """Main entry point for workspace context detection.

    Detects context switches and handles workspace lifecycle (pause/resume/create).
    Called from UserPromptSubmit hook before supervisor routing.

    Args:
        user_message: User's input message

    Returns:
        {
            "should_block": bool (whether to block supervisor routing),
            "user_message": str (message to show user if blocking),
            "workspace_action": str (none|pause|create),
            "detection_result": dict (full detection result for logging)
        }

        Returns None if detection fails (allows fallback to supervisor routing).

    Example:
        >>> result = detect_and_handle_context_switch("Can you help me parse CSV files?")
        >>> result["workspace_action"]
        'pause'  # If active workspace exists and switching to new work
    """
    try:
        # Get active workspace context
        active_workspace = get_active_workspace()
        workspace_context = None
        if active_workspace:
            workspace_context = get_workspace_context_summary(active_workspace)

        # Detect context switch
        detection_result = detect_context_switch(
            user_message=user_message, workspace_context=workspace_context
        )

        # Handle switch
        action_result = handle_context_switch(user_message, detection_result)

        # Determine if we should block supervisor routing
        should_block = action_result.get("needs_confirmation", False)
        user_facing_message = action_result.get("message", "")
        workspace_action = action_result.get("workspace_action", "none")

        return {
            "should_block": should_block,
            "user_message": user_facing_message,
            "workspace_action": workspace_action,
            "detection_result": detection_result,
        }

    except Exception as e:
        # Don't crash hook - log error and continue to supervisor
        print(
            f"Warning: Context detection failed: {e}", file=sys.stderr
        )
        return None


def format_context_detection_summary(detection_result: Dict) -> str:
    """Format detection result for logging/display.

    Args:
        detection_result: Result from detect_context_switch()

    Returns:
        Formatted summary string

    Example:
        >>> result = {
        ...     "classification": "CONTINUATION",
        ...     "confidence": 0.95,
        ...     "reasoning": "User approving previous work"
        ... }
        >>> summary = format_context_detection_summary(result)
        >>> "CONTINUATION" in summary
        True
    """
    classification = detection_result.get("classification", "unknown")
    confidence = detection_result.get("confidence", 0) * 100
    reasoning = detection_result.get("reasoning", "No reasoning provided")
    cost = detection_result.get("cost_usd", 0)
    duration = detection_result.get("duration_ms", 0)

    return f"""
📊 **Context Detection Result**:
- Classification: {classification}
- Confidence: {confidence:.0f}%
- Reasoning: {reasoning}
- Performance: ${cost:.4f} | {duration}ms
""".strip()
