"""
Tests for UserPromptSubmit hook.

Tests the hook that injects Supervisor instructions before each user message.
"""

import json
import subprocess
from pathlib import Path


class TestUserPromptSubmitHook:
    """Test UserPromptSubmit hook functionality."""

    def test_hook_exists(self):
        """Test that hook file exists and is executable."""
        hook_path = Path("hooks/user_prompt_submit.py")

        assert hook_path.exists(), "Hook file should exist"
        assert hook_path.stat().st_mode & 0o111, "Hook should be executable"

    def test_hook_executes(self):
        """Test that hook executes without errors."""
        hook_path = Path("hooks/user_prompt_submit.py")

        result = subprocess.run(
            ["python3", str(hook_path)],
            capture_output=True,
            text=True,
            timeout=5
        )

        assert result.returncode == 0, f"Hook should execute successfully: {result.stderr}"
        assert result.stdout, "Hook should produce output"

    def test_hook_output_format(self):
        """Test that hook output is valid JSON in correct format."""
        hook_path = Path("hooks/user_prompt_submit.py")

        result = subprocess.run(
            ["python3", str(hook_path)],
            capture_output=True,
            text=True,
            timeout=5
        )

        # Parse JSON output
        try:
            output = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            pytest.fail(f"Hook output should be valid JSON: {e}\nOutput: {result.stdout}")

        # Check structure
        assert "hookSpecificOutput" in output, "Output should have hookSpecificOutput key"
        hook_output = output["hookSpecificOutput"]

        assert "hookEventName" in hook_output, "Should have hookEventName"
        assert hook_output["hookEventName"] == "UserPromptSubmit", "Event name should be UserPromptSubmit"

        assert "additionalContext" in hook_output, "Should have additionalContext"
        assert isinstance(hook_output["additionalContext"], str), "additionalContext should be string"

    def test_hook_injects_supervisor_instructions(self):
        """Test that hook injects Supervisor instructions."""
        hook_path = Path("hooks/user_prompt_submit.py")

        result = subprocess.run(
            ["python3", str(hook_path)],
            capture_output=True,
            text=True,
            timeout=5
        )

        output = json.loads(result.stdout)
        context = output["hookSpecificOutput"]["additionalContext"]

        # Check for key Supervisor elements
        assert "SUPERVISOR MODE" in context or "Supervisor" in context, "Should mention Supervisor"
        assert "Triage" in context or "triage" in context, "Should include triage instructions"
        assert "Q&A" in context or "question" in context.lower(), "Should mention Q&A handling"
        assert "workflow" in context.lower(), "Should mention workflow routing"
        assert "ADR-007" in context or "Triad Atomicity" in context, "Should reference architecture"

    def test_hook_includes_atomic_principle(self):
        """Test that hook includes triad atomicity principle."""
        hook_path = Path("hooks/user_prompt_submit.py")

        result = subprocess.run(
            ["python3", str(hook_path)],
            capture_output=True,
            text=True,
            timeout=5
        )

        output = json.loads(result.stdout)
        context = output["hookSpecificOutput"]["additionalContext"]

        # Check for atomicity principle
        assert "atomic" in context.lower() or "ATOMIC" in context, "Should mention atomic triads"
        assert "NEVER" in context or "never" in context, "Should emphasize no decomposition"

    def test_hook_includes_training_mode(self):
        """Test that hook includes training mode instructions."""
        hook_path = Path("hooks/user_prompt_submit.py")

        result = subprocess.run(
            ["python3", str(hook_path)],
            capture_output=True,
            text=True,
            timeout=5
        )

        output = json.loads(result.stdout)
        context = output["hookSpecificOutput"]["additionalContext"]

        # Check for training mode
        assert "training" in context.lower() or "Training Mode" in context, "Should mention training mode"
        assert "confirm" in context.lower(), "Should include confirmation requirement"

    def test_hook_includes_emergency_bypass(self):
        """Test that hook includes emergency bypass instructions."""
        hook_path = Path("hooks/user_prompt_submit.py")

        result = subprocess.run(
            ["python3", str(hook_path)],
            capture_output=True,
            text=True,
            timeout=5
        )

        output = json.loads(result.stdout)
        context = output["hookSpecificOutput"]["additionalContext"]

        # Check for bypass
        assert "/direct" in context or "bypass" in context.lower(), "Should mention emergency bypass"
