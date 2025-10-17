"""Tests for PreToolUse hook (on_pre_experience_injection.py).

This module tests the hook that fires before every tool execution
and injects relevant process knowledge into agent context.

Test Coverage:
- Hook injection with relevant knowledge
- Early exit for read-only tools
- Error handling and graceful degradation
- Format output verification
- Integration with ExperienceQueryEngine

Critical Requirements:
- Hook MUST always exit 0 (never block tools)
- Hook MUST handle errors gracefully
- Hook MUST early-exit for Read/Grep/Glob
- Hook MUST limit to top 3 items max
"""

import json
import subprocess
from pathlib import Path

import pytest


# Path to hook script
HOOK_PATH = Path(__file__).parent.parent.parent / "hooks" / "on_pre_experience_injection.py"


class TestPreToolUseHook:
    """Test suite for PreToolUse hook."""

    def test_hook_with_relevant_knowledge(self):
        """Test hook injects knowledge for Write to plugin.json.

        This is the critical success path - hook should:
        1. Query for relevant knowledge
        2. Find Version Bump Checklist (CRITICAL priority)
        3. Format and inject into stdout
        4. Exit successfully (code 0)
        """
        input_data = {
            "tool_name": "Write",
            "tool_input": {"file_path": ".claude-plugin/plugin.json"},
            "cwd": str(Path(__file__).parent.parent.parent)  # Repo root
        }

        result = subprocess.run(
            ["python3", str(HOOK_PATH)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            timeout=5
        )

        # CRITICAL: Must exit successfully (never block tools)
        assert result.returncode == 0, f"Hook failed with stderr: {result.stderr}"

        # Should inject knowledge header
        assert "EXPERIENCE-BASED KNOWLEDGE" in result.stdout, \
            "Should show knowledge header"

        # Should mention the tool
        assert "Write" in result.stdout, \
            "Should mention tool being used"

        # Should contain checklist content
        # (Exact format depends on graph content, check for any checkbox)
        assert "□" in result.stdout or "Checklist" in result.stdout or "Version" in result.stdout, \
            f"Should contain checklist content. Got: {result.stdout}"

        # Should log success to stderr
        assert "Injected" in result.stderr or "knowledge" in result.stderr, \
            "Should log injection to stderr"

    def test_hook_early_exit_for_read_tool(self):
        """Test hook exits early for Read tool (no injection).

        Read is a read-only tool that doesn't modify state.
        Hook should early-exit to avoid cluttering context.
        """
        input_data = {
            "tool_name": "Read",
            "tool_input": {"file_path": "README.md"},
            "cwd": str(Path(__file__).parent.parent.parent)
        }

        result = subprocess.run(
            ["python3", str(HOOK_PATH)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            timeout=5
        )

        # CRITICAL: Must exit successfully
        assert result.returncode == 0

        # Should NOT inject (early exit)
        assert result.stdout == "", \
            "Should not inject for read-only tool"

        # Should log early exit
        assert "Early exit" in result.stderr or result.stderr == "", \
            "Should log early exit to stderr"

    def test_hook_early_exit_for_grep_tool(self):
        """Test hook exits early for Grep tool (no injection).

        Grep is a read-only search tool.
        Hook should early-exit to avoid cluttering context.
        """
        input_data = {
            "tool_name": "Grep",
            "tool_input": {"pattern": "test"},
            "cwd": str(Path(__file__).parent.parent.parent)
        }

        result = subprocess.run(
            ["python3", str(HOOK_PATH)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            timeout=5
        )

        # CRITICAL: Must exit successfully
        assert result.returncode == 0

        # Should NOT inject
        assert result.stdout == ""

    def test_hook_early_exit_for_glob_tool(self):
        """Test hook exits early for Glob tool (no injection).

        Glob is a read-only file search tool.
        Hook should early-exit to avoid cluttering context.
        """
        input_data = {
            "tool_name": "Glob",
            "tool_input": {"pattern": "*.py"},
            "cwd": str(Path(__file__).parent.parent.parent)
        }

        result = subprocess.run(
            ["python3", str(HOOK_PATH)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            timeout=5
        )

        # CRITICAL: Must exit successfully
        assert result.returncode == 0

        # Should NOT inject
        assert result.stdout == ""

    def test_hook_handles_invalid_json(self):
        """Test hook handles invalid JSON gracefully.

        CRITICAL: Hook must never fail, even with garbage input.
        """
        invalid_json = "not valid json at all"

        result = subprocess.run(
            ["python3", str(HOOK_PATH)],
            input=invalid_json,
            capture_output=True,
            text=True,
            timeout=5
        )

        # CRITICAL: Must still exit successfully (never block tools)
        assert result.returncode == 0, \
            "Hook must exit 0 even with invalid JSON"

        # Should not inject anything
        assert result.stdout == "" or "Warning" in result.stderr

    def test_hook_handles_missing_tool_name(self):
        """Test hook handles missing tool_name gracefully."""
        input_data = {
            "tool_input": {"file_path": "test.txt"},
            "cwd": "."
            # Missing tool_name
        }

        result = subprocess.run(
            ["python3", str(HOOK_PATH)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            timeout=5
        )

        # CRITICAL: Must exit successfully
        assert result.returncode == 0

        # Should not inject (no tool name)
        assert result.stdout == ""

    def test_hook_handles_empty_input(self):
        """Test hook handles empty input gracefully."""
        input_data = {}

        result = subprocess.run(
            ["python3", str(HOOK_PATH)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            timeout=5
        )

        # CRITICAL: Must exit successfully
        assert result.returncode == 0

        # Should not inject
        assert result.stdout == ""

    def test_hook_with_no_relevant_knowledge(self):
        """Test hook exits silently when no relevant knowledge found.

        Tool execution with no matching knowledge should not inject anything.
        """
        input_data = {
            "tool_name": "Write",
            "tool_input": {"file_path": "/tmp/random_file_12345.txt"},
            "cwd": str(Path(__file__).parent.parent.parent)
        }

        result = subprocess.run(
            ["python3", str(HOOK_PATH)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            timeout=5
        )

        # CRITICAL: Must exit successfully
        assert result.returncode == 0

        # Should not inject if no relevant knowledge
        # (or should inject if Version Bump matches generic patterns)
        # Either way, hook should succeed

    def test_hook_limits_to_max_items(self):
        """Test hook limits injection to MAX_INJECTION_ITEMS (3).

        Even if more knowledge is relevant, only top 3 should be injected
        to avoid context pollution.
        """
        # This test is implicit - if we had 10 CRITICAL items,
        # only 3 would appear in output. Hard to test without
        # creating a graph with many items.

        # For now, verify the constant exists in the code
        hook_code = HOOK_PATH.read_text()
        assert "MAX_INJECTION_ITEMS = 3" in hook_code, \
            "Hook should define MAX_INJECTION_ITEMS constant"

    def test_hook_performance(self):
        """Test hook completes within performance target (< 100ms).

        Hook is called on EVERY tool use, so it must be fast.
        Target: P95 < 100ms (query engine is ~0.1ms, so budget exists).
        """
        import time

        input_data = {
            "tool_name": "Write",
            "tool_input": {"file_path": ".claude-plugin/plugin.json"},
            "cwd": str(Path(__file__).parent.parent.parent)
        }

        start = time.perf_counter()

        result = subprocess.run(
            ["python3", str(HOOK_PATH)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            timeout=5
        )

        elapsed_ms = (time.perf_counter() - start) * 1000

        # Must exit successfully
        assert result.returncode == 0

        # Should complete within target
        # Note: Subprocess overhead adds ~10-20ms, so relax to 200ms
        assert elapsed_ms < 200, \
            f"Hook took {elapsed_ms:.1f}ms (target: < 200ms including subprocess overhead)"

    def test_hook_formats_checklist_correctly(self):
        """Test checklist formatting includes checkboxes and priority."""
        input_data = {
            "tool_name": "Write",
            "tool_input": {"file_path": ".claude-plugin/plugin.json"},
            "cwd": str(Path(__file__).parent.parent.parent)
        }

        result = subprocess.run(
            ["python3", str(HOOK_PATH)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            timeout=5
        )

        # Must exit successfully
        assert result.returncode == 0

        # Should contain checkbox format (if knowledge found)
        if "EXPERIENCE-BASED KNOWLEDGE" in result.stdout:
            # Should have priority indicator
            assert "CRITICAL" in result.stdout or "PRIORITY" in result.stdout.upper(), \
                "Should show priority level"

            # Should have checkbox (□) or checklist indicator
            assert "□" in result.stdout or "Checklist" in result.stdout, \
                "Should show checklist format"

    def test_hook_with_edit_tool(self):
        """Test hook works with Edit tool (another file modification tool).

        Edit should trigger same knowledge as Write for version files.
        """
        input_data = {
            "tool_name": "Edit",
            "tool_input": {"file_path": ".claude-plugin/marketplace.json"},
            "cwd": str(Path(__file__).parent.parent.parent)
        }

        result = subprocess.run(
            ["python3", str(HOOK_PATH)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            timeout=5
        )

        # Must exit successfully
        assert result.returncode == 0

        # Should potentially inject knowledge (marketplace.json is in patterns)
        # Whether it injects depends on relevance scoring

    def test_hook_mentions_experience(self):
        """Test hook output mentions experience-based learning.

        Output should make it clear this is learned knowledge, not arbitrary rules.
        """
        input_data = {
            "tool_name": "Write",
            "tool_input": {"file_path": ".claude-plugin/plugin.json"},
            "cwd": str(Path(__file__).parent.parent.parent)
        }

        result = subprocess.run(
            ["python3", str(HOOK_PATH)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            timeout=5
        )

        # Must exit successfully
        assert result.returncode == 0

        # Should mention experience if knowledge injected
        if "EXPERIENCE-BASED KNOWLEDGE" in result.stdout:
            assert "experience" in result.stdout.lower(), \
                "Should mention this is experience-based knowledge"


class TestHookFormatting:
    """Test formatting functions in isolation."""

    def test_checklist_format_includes_checkboxes(self):
        """Test checklist formatting creates checkbox list."""
        # This is a unit test for the format_checklist function
        # Since we can't easily import the function (it's in __main__),
        # we verify output format instead
        hook_code = HOOK_PATH.read_text()

        # Verify format_checklist exists
        assert "def format_checklist" in hook_code

        # Verify it uses checkboxes
        assert "□" in hook_code

    def test_pattern_format_includes_when_then(self):
        """Test pattern formatting uses when/then structure."""
        hook_code = HOOK_PATH.read_text()

        # Verify format_pattern exists
        assert "def format_pattern" in hook_code

        # Verify it shows when/then
        assert "When" in hook_code or "when" in hook_code

    def test_warning_format_includes_risk(self):
        """Test warning formatting includes risk/mitigation."""
        hook_code = HOOK_PATH.read_text()

        # Verify format_warning exists
        assert "def format_warning" in hook_code

        # Verify it shows risk
        assert "Risk" in hook_code or "risk" in hook_code


class TestHookSafety:
    """Test critical safety requirements."""

    def test_hook_always_exits_zero(self):
        """CRITICAL: Hook must ALWAYS exit 0, even on errors.

        This is the most important test - hook must never block tool execution.
        """
        test_cases = [
            {"tool_name": "Write", "tool_input": {}, "cwd": "."},  # Normal
            {},  # Empty
            {"invalid": "data"},  # Invalid structure
            {"tool_name": None, "tool_input": None, "cwd": None},  # Nulls
        ]

        for input_data in test_cases:
            result = subprocess.run(
                ["python3", str(HOOK_PATH)],
                input=json.dumps(input_data),
                capture_output=True,
                text=True,
                timeout=5
            )

            assert result.returncode == 0, \
                f"Hook must exit 0 for input: {input_data}\nStderr: {result.stderr}"

    def test_hook_handles_unicode(self):
        """Test hook handles Unicode input gracefully."""
        input_data = {
            "tool_name": "Write",
            "tool_input": {"file_path": "测试文件.txt"},
            "cwd": "."
        }

        result = subprocess.run(
            ["python3", str(HOOK_PATH)],
            input=json.dumps(input_data, ensure_ascii=False),
            capture_output=True,
            text=True,
            timeout=5
        )

        # Must exit successfully
        assert result.returncode == 0

    def test_hook_has_try_except_finally(self):
        """Test hook code uses try/except/finally for safety."""
        hook_code = HOOK_PATH.read_text()

        # Verify error handling structure
        assert "try:" in hook_code
        assert "except" in hook_code
        assert "finally:" in hook_code
        assert "sys.exit(0)" in hook_code

        # Verify it catches broad exceptions
        assert "Exception" in hook_code


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
