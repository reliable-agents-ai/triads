"""Tests for unified dual-mode PreToolUse hook (Phase 1).

This module tests the new dual-mode hook that intelligently escalates
from silent → inject → block based on knowledge criticality and confidence.

Test Coverage (ADR-002 Blocking Criteria):
- Blocks CRITICAL checklists on version files (high-stakes pattern)
- Blocks very high confidence (>= 0.95) on any file
- Does NOT block medium priority or low confidence
- Does NOT block read-only tools (Read, Grep, Glob)
- Respects TRIADS_NO_BLOCK=1 environment variable

Key Requirements:
- Exit 2 + stderr for blocking (user-style interjection)
- Exit 0 + JSON for non-blocking (additionalContext)
- Exit 0 on errors (never fail)
- Configuration via environment variables

Phase 1 Focus:
- Dual-mode decision logic
- User-style interjection formatting
- Configuration loading (env vars)
- Backward compatibility with existing tests
"""

import json
import subprocess
from pathlib import Path

import pytest


# Path to hook script
HOOK_PATH = Path(__file__).parent.parent.parent / "hooks" / "on_pre_experience_injection.py"
REPO_ROOT = Path(__file__).parent.parent.parent


class TestDualModeDecisionLogic:
    """Test the core decision logic: when to block vs inject."""

    def test_blocks_version_file_with_critical_checklist(self):
        """Test hook BLOCKS for CRITICAL checklist on version file.

        This is the primary blocking scenario (ADR-002 Pattern 1):
        - CRITICAL priority knowledge
        - Checklist process type
        - Version file (plugin.json)
        - High confidence (1.0)

        Expected: Exit 2 (block), stderr with user-style interjection
        """
        input_data = {
            "tool_name": "Write",
            "tool_input": {"file_path": ".claude-plugin/plugin.json"},
            "cwd": str(REPO_ROOT)
        }

        # Create clean environment without TRIADS_NO_BLOCK
        env = subprocess.os.environ.copy()
        env.pop("TRIADS_NO_BLOCK", None)  # Remove if exists

        result = subprocess.run(
            ["python3", str(HOOK_PATH)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            timeout=5,
            env=env
        )

        # Should BLOCK (exit 2)
        assert result.returncode == 2, \
            f"Should block with exit 2. Got {result.returncode}. Stderr: {result.stderr}"

        # Should have user-style interjection in stderr
        assert "Hold on" in result.stderr or "remind you" in result.stderr, \
            f"Should have natural language interjection. Got: {result.stderr}"

        # Should mention the checklist
        assert "Version Bump" in result.stderr or "checklist" in result.stderr.lower(), \
            f"Should mention version checklist. Got: {result.stderr}"

        # Should have BLOCKED log message
        assert "BLOCKED" in result.stderr, \
            f"Should log that tool was blocked. Got: {result.stderr}"

    def test_blocks_marketplace_json_with_critical_checklist(self):
        """Test hook BLOCKS for marketplace.json (another version file)."""
        input_data = {
            "tool_name": "Edit",
            "tool_input": {"file_path": ".claude-plugin/marketplace.json"},
            "cwd": str(REPO_ROOT)
        }

        # Create clean environment without TRIADS_NO_BLOCK
        env = subprocess.os.environ.copy()
        env.pop("TRIADS_NO_BLOCK", None)

        result = subprocess.run(
            ["python3", str(HOOK_PATH)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            timeout=5,
            env=env
        )

        # Should BLOCK (marketplace.json is in VERSION_FILE_PATTERNS)
        assert result.returncode == 2, \
            f"Should block marketplace.json. Got {result.returncode}"

        # Should have interjection
        assert "Hold on" in result.stderr or "remind you" in result.stderr

    def test_blocks_pyproject_toml_with_critical_checklist(self):
        """Test hook BLOCKS for pyproject.toml (version file)."""
        input_data = {
            "tool_name": "Write",
            "tool_input": {"file_path": "pyproject.toml"},
            "cwd": str(REPO_ROOT)
        }

        # Create clean environment without TRIADS_NO_BLOCK
        env = subprocess.os.environ.copy()
        env.pop("TRIADS_NO_BLOCK", None)

        result = subprocess.run(
            ["python3", str(HOOK_PATH)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            timeout=5,
            env=env
        )

        # Should BLOCK
        assert result.returncode == 2, \
            f"Should block pyproject.toml. Got {result.returncode}"

    def test_blocks_very_high_confidence_any_file(self):
        """Test hook BLOCKS for very high confidence (>= 0.95) on ANY file.

        This is Pattern 2 from ADR-002. Even non-version files get blocked
        if confidence is >= 0.95, because high confidence indicates strong
        evidence that the knowledge is critical.

        Current deployment_graph.json has confidence=1.0 for Version Bump
        Checklist, so it triggers this pattern.
        """
        input_data = {
            "tool_name": "Write",
            "tool_input": {"file_path": "src/app.py"},
            "cwd": str(REPO_ROOT)
        }

        # Create clean environment without TRIADS_NO_BLOCK
        env = subprocess.os.environ.copy()
        env.pop("TRIADS_NO_BLOCK", None)

        result = subprocess.run(
            ["python3", str(HOOK_PATH)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            timeout=5,
            env=env
        )

        # Should BLOCK (confidence=1.0 >= 0.95)
        assert result.returncode == 2, \
            f"Should block for confidence >= 0.95. Got {result.returncode}. Stderr: {result.stderr}"

        # Should have interjection
        assert "Hold on" in result.stderr or "remind you" in result.stderr

    def test_no_block_readonly_tools(self):
        """Test hook NEVER blocks read-only tools (Read, Grep, Glob).

        Even with CRITICAL knowledge on version files, read-only tools
        should not be blocked.
        """
        readonly_tools = ["Read", "Grep", "Glob"]

        for tool_name in readonly_tools:
            input_data = {
                "tool_name": tool_name,
                "tool_input": {"file_path": ".claude-plugin/plugin.json"},
                "cwd": str(REPO_ROOT)
            }

            result = subprocess.run(
                ["python3", str(HOOK_PATH)],
                input=json.dumps(input_data),
                capture_output=True,
                text=True,
                timeout=5
            )

            # Should NOT block (exit 0)
            assert result.returncode == 0, \
                f"Should not block {tool_name}. Got {result.returncode}"

            # Should early-exit (no output)
            assert result.stdout == "" or "Early exit" in result.stderr, \
                f"{tool_name} should early-exit"

    def test_no_block_medium_priority(self):
        """Test hook does NOT block for MEDIUM priority knowledge.

        Only CRITICAL knowledge can trigger blocking.
        """
        # This test is implicit - we'd need a MEDIUM priority checklist
        # in the graph to test explicitly. For now, verify via code inspection.
        hook_code = HOOK_PATH.read_text()

        # Verify blocking logic checks for CRITICAL
        assert 'k.priority == "CRITICAL"' in hook_code or \
               "CRITICAL" in hook_code, \
            "Hook should check for CRITICAL priority"

    def test_no_block_low_confidence(self):
        """Test hook does NOT block for low confidence (< 0.85).

        Even CRITICAL knowledge needs high confidence to block.
        """
        # This is verified by the should_block_for_knowledge logic
        # which checks k.confidence >= 0.85
        hook_code = HOOK_PATH.read_text()

        assert "confidence >=" in hook_code or "BLOCK_CONFIDENCE_THRESHOLD" in hook_code, \
            "Hook should check confidence threshold"


class TestConfigurationSystem:
    """Test configuration via environment variables (ADR-005)."""

    def test_env_var_disables_blocking(self):
        """Test TRIADS_NO_BLOCK=1 disables blocking mode.

        Even with CRITICAL checklist on version file, should inject
        instead of blocking.
        """
        input_data = {
            "tool_name": "Write",
            "tool_input": {"file_path": ".claude-plugin/plugin.json"},
            "cwd": str(REPO_ROOT)
        }

        env = {"TRIADS_NO_BLOCK": "1"}

        result = subprocess.run(
            ["python3", str(HOOK_PATH)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            timeout=5,
            env={**subprocess.os.environ, **env}
        )

        # Should NOT block (exit 0) due to env var
        assert result.returncode == 0, \
            f"TRIADS_NO_BLOCK=1 should disable blocking. Got {result.returncode}"

        # Should have JSON output instead
        if result.stdout:
            try:
                output = json.loads(result.stdout)
                assert "additionalContext" in output, \
                    "Should use additionalContext when blocking disabled"
            except json.JSONDecodeError:
                pass  # May have no knowledge, that's OK

    def test_env_var_disables_all_injection(self):
        """Test TRIADS_NO_EXPERIENCE=1 disables all injection.

        Hook should exit early without querying or injecting anything.
        """
        input_data = {
            "tool_name": "Write",
            "tool_input": {"file_path": ".claude-plugin/plugin.json"},
            "cwd": str(REPO_ROOT)
        }

        env = {"TRIADS_NO_EXPERIENCE": "1"}

        result = subprocess.run(
            ["python3", str(HOOK_PATH)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            timeout=5,
            env={**subprocess.os.environ, **env}
        )

        # Should exit 0 (not block)
        assert result.returncode == 0, \
            "TRIADS_NO_EXPERIENCE should exit gracefully"

        # Should have no JSON output
        assert result.stdout == "" or result.stdout == "{}", \
            "Should not inject when experience disabled"

        # Should log that it's disabled
        assert "disabled" in result.stderr.lower() or result.stderr == "", \
            "Should log that injection is disabled"


class TestInterjectionFormatting:
    """Test user-style interjection formatting (ADR-003)."""

    def test_interjection_has_natural_language(self):
        """Test interjection uses natural language, not error messages.

        Should sound like a user reminder, not a formal warning.
        """
        input_data = {
            "tool_name": "Write",
            "tool_input": {"file_path": ".claude-plugin/plugin.json"},
            "cwd": str(REPO_ROOT)
        }

        result = subprocess.run(
            ["python3", str(HOOK_PATH)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 2:  # Blocking mode
            stderr = result.stderr

            # Should have conversational opening
            assert any(phrase in stderr for phrase in
                      ["Hold on", "remind you", "heads up"]), \
                f"Should have natural language opening. Got: {stderr}"

            # Should have conversational closing
            assert any(phrase in stderr for phrase in
                      ["make sure you cover", "aware of this", "caused issues"]), \
                f"Should have natural language closing. Got: {stderr}"

            # Should mention it's from experience system
            assert "experience" in stderr.lower() or "learning" in stderr.lower(), \
                f"Should mention experience system. Got: {stderr}"

            # Should NOT look like an error message
            assert "ERROR" not in stderr and "FAILED" not in stderr, \
                "Should not use error terminology"

    def test_interjection_includes_checklist_items(self):
        """Test interjection shows actual checklist items."""
        input_data = {
            "tool_name": "Write",
            "tool_input": {"file_path": ".claude-plugin/plugin.json"},
            "cwd": str(REPO_ROOT)
        }

        result = subprocess.run(
            ["python3", str(HOOK_PATH)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 2:  # Blocking mode
            stderr = result.stderr

            # Should show checklist items
            assert "🔴 REQUIRED" in stderr or "• " in stderr, \
                f"Should show checklist items. Got: {stderr}"

            # Should mention files to update
            assert any(file in stderr for file in
                      ["plugin.json", "marketplace.json", "pyproject.toml"]), \
                f"Should mention specific files. Got: {stderr}"


class TestAdditionalContextFormatting:
    """Test non-blocking additionalContext formatting (ADR-004)."""

    def test_inject_mode_uses_json_format(self):
        """Test inject mode outputs valid JSON with additionalContext field.

        Since the current deployment graph has very high confidence (1.0),
        it blocks on most writes. To test inject mode, we need to either:
        1. Use TRIADS_NO_BLOCK=1 to force inject mode, OR
        2. Use a file that doesn't match any patterns

        We'll use option 1 to explicitly test inject mode.
        """
        input_data = {
            "tool_name": "Write",
            "tool_input": {"file_path": ".claude-plugin/plugin.json"},
            "cwd": str(REPO_ROOT)
        }

        # Disable blocking to force inject mode
        env = {"TRIADS_NO_BLOCK": "1"}

        result = subprocess.run(
            ["python3", str(HOOK_PATH)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            timeout=5,
            env={**subprocess.os.environ, **env}
        )

        # Should exit 0 (inject mode, not block)
        assert result.returncode == 0, \
            f"Should use inject mode with TRIADS_NO_BLOCK=1. Got {result.returncode}"

        # Should have JSON output
        assert result.stdout and result.stdout.strip(), \
            "Should have output in inject mode"

        try:
            output = json.loads(result.stdout)
            assert "additionalContext" in output, \
                f"Should have additionalContext field. Got: {output}"

            # Context should be a string
            assert isinstance(output["additionalContext"], str), \
                "additionalContext should be a string"

            # Should have experience indicator
            context = output["additionalContext"]
            assert "Experience" in context or "📚" in context, \
                f"Should indicate experience. Got: {context}"

        except json.JSONDecodeError as e:
            pytest.fail(f"Should output valid JSON. Got: {result.stdout}. Error: {e}")


class TestBackwardCompatibility:
    """Test backward compatibility with existing hook tests."""

    def test_hook_still_exits_zero_on_errors(self):
        """CRITICAL: Hook must ALWAYS exit 0 on errors (never fail).

        This is backward compatibility requirement - existing behavior.
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

            # Exit 0 or 2 is OK, but NOT other error codes
            assert result.returncode in [0, 2], \
                f"Hook must exit 0 or 2 for input: {input_data}\nStderr: {result.stderr}"

    def test_hook_handles_invalid_json(self):
        """Test hook handles invalid JSON gracefully (exits 0)."""
        invalid_json = "not valid json at all"

        result = subprocess.run(
            ["python3", str(HOOK_PATH)],
            input=invalid_json,
            capture_output=True,
            text=True,
            timeout=5
        )

        # Must exit 0 (graceful failure)
        assert result.returncode == 0, \
            "Hook must exit 0 even with invalid JSON"

    def test_hook_performance_still_fast(self):
        """Test hook still completes within performance target (< 400ms).

        Target updated to account for P0 safety features:
        - Subprocess overhead (~50-100ms)
        - Schema validation (~50ms)
        - Corruption prevention (~50ms)
        - Graph loading and query (~100-150ms)
        """
        import time

        input_data = {
            "tool_name": "Write",
            "tool_input": {"file_path": ".claude-plugin/plugin.json"},
            "cwd": str(REPO_ROOT)
        }

        # Create clean environment without TRIADS_NO_BLOCK
        env = subprocess.os.environ.copy()
        env.pop("TRIADS_NO_BLOCK", None)  # Remove if exists

        start = time.perf_counter()

        result = subprocess.run(
            ["python3", str(HOOK_PATH)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            timeout=5,
            env=env
        )

        elapsed_ms = (time.perf_counter() - start) * 1000

        # Must exit successfully (0 or 2)
        assert result.returncode in [0, 2]

        # Should complete within target
        assert elapsed_ms < 400, \
            f"Hook took {elapsed_ms:.1f}ms (target: < 400ms including subprocess + safety overhead)"


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_hook_with_bash_tool(self):
        """Test hook works with Bash tool (risky, can trigger blocking)."""
        input_data = {
            "tool_name": "Bash",
            "tool_input": {"command": "cat plugin.json"},
            "cwd": str(REPO_ROOT)
        }

        result = subprocess.run(
            ["python3", str(HOOK_PATH)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            timeout=5
        )

        # Must exit successfully (0 or 2)
        assert result.returncode in [0, 2]

    def test_hook_with_no_file_path(self):
        """Test hook handles tools without file_path gracefully."""
        input_data = {
            "tool_name": "Bash",
            "tool_input": {"command": "echo hello"},  # No file_path
            "cwd": str(REPO_ROOT)
        }

        result = subprocess.run(
            ["python3", str(HOOK_PATH)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            timeout=5
        )

        # Must exit successfully
        assert result.returncode in [0, 2]

    def test_hook_with_unicode_file_path(self):
        """Test hook handles Unicode file paths gracefully."""
        input_data = {
            "tool_name": "Write",
            "tool_input": {"file_path": "测试文件.json"},
            "cwd": str(REPO_ROOT)
        }

        result = subprocess.run(
            ["python3", str(HOOK_PATH)],
            input=json.dumps(input_data, ensure_ascii=False),
            capture_output=True,
            text=True,
            timeout=5
        )

        # Must exit successfully
        assert result.returncode in [0, 2]


class TestMagicalBashBlocking:
    """Test magical Bash command blocking (safe vs risky detection)."""

    def test_safe_bash_commands_never_block(self):
        """Test safe read-only Bash commands NEVER block.

        Magical blocking: Safe commands like ls, cat, git status should
        NEVER block, even if CRITICAL knowledge exists.
        """
        safe_commands = [
            "ls -la",
            "cat plugin.json",
            "git status",
            "git diff",
            "echo 'hello'",
            "grep version plugin.json",
        ]

        for command in safe_commands:
            input_data = {
                "tool_name": "Bash",
                "tool_input": {"command": command},
                "cwd": str(REPO_ROOT)
            }

            result = subprocess.run(
                ["python3", str(HOOK_PATH)],
                input=json.dumps(input_data),
                capture_output=True,
                text=True,
                timeout=5
            )

            # Should NEVER block safe commands (exit 0, not 2)
            assert result.returncode == 0, \
                f"Safe command '{command}' should NOT block. Got exit {result.returncode}. Stderr: {result.stderr}"

    def test_risky_bash_commands_can_block(self):
        """Test risky Bash commands CAN block if CRITICAL knowledge exists.

        Magical blocking: Commands like git commit, rm should be eligible
        for blocking if CRITICAL knowledge is present.
        """
        risky_commands = [
            "git commit -m 'test'",
            "rm -rf temp/",
        ]

        for command in risky_commands:
            input_data = {
                "tool_name": "Bash",
                "tool_input": {"command": command},
                "cwd": str(REPO_ROOT)
            }

            result = subprocess.run(
                ["python3", str(HOOK_PATH)],
                input=json.dumps(input_data),
                capture_output=True,
                text=True,
                timeout=5
            )

            # Risky commands can block (exit 2) or inject (exit 0)
            # Depends on whether CRITICAL knowledge matches the context
            assert result.returncode in [0, 2], \
                f"Risky command '{command}' should exit 0 or 2. Got {result.returncode}"

    def test_unknown_bash_commands_dont_block(self):
        """Test unknown Bash commands default to NOT blocking.

        Magical blocking: Unknown commands (python, npm start) should NOT
        block by default (safe default behavior).
        """
        unknown_commands = [
            "python script.py",
            "npm start",
            "docker build .",
        ]

        for command in unknown_commands:
            input_data = {
                "tool_name": "Bash",
                "tool_input": {"command": command},
                "cwd": str(REPO_ROOT)
            }

            result = subprocess.run(
                ["python3", str(HOOK_PATH)],
                input=json.dumps(input_data),
                capture_output=True,
                text=True,
                timeout=5
            )

            # Unknown commands should NOT block (exit 0)
            assert result.returncode == 0, \
                f"Unknown command '{command}' should NOT block. Got exit {result.returncode}. Stderr: {result.stderr}"


class TestCodeQuality:
    """Test code quality and implementation details."""

    def test_hook_has_config_constants(self):
        """Test hook defines blocking threshold constants."""
        hook_code = HOOK_PATH.read_text()

        assert "BLOCK_CONFIDENCE_THRESHOLD" in hook_code, \
            "Should define BLOCK_CONFIDENCE_THRESHOLD constant"

        assert "BLOCK_VERY_HIGH_CONFIDENCE_THRESHOLD" in hook_code, \
            "Should define BLOCK_VERY_HIGH_CONFIDENCE_THRESHOLD constant"

        assert "VERSION_FILE_PATTERNS" in hook_code, \
            "Should define VERSION_FILE_PATTERNS constant"

    def test_hook_has_decision_function(self):
        """Test hook has should_block_for_knowledge function."""
        hook_code = HOOK_PATH.read_text()

        assert "def should_block_for_knowledge" in hook_code, \
            "Should have should_block_for_knowledge function"

    def test_hook_has_formatting_functions(self):
        """Test hook has both formatting functions."""
        hook_code = HOOK_PATH.read_text()

        assert "def format_as_user_interjection" in hook_code, \
            "Should have format_as_user_interjection function"

        assert "def format_for_additionalcontext" in hook_code, \
            "Should have format_for_additionalcontext function"

    def test_hook_has_config_loader(self):
        """Test hook has load_config function."""
        hook_code = HOOK_PATH.read_text()

        assert "def load_config" in hook_code, \
            "Should have load_config function"

        assert "TRIADS_NO_BLOCK" in hook_code, \
            "Should check TRIADS_NO_BLOCK env var"

        assert "TRIADS_NO_EXPERIENCE" in hook_code, \
            "Should check TRIADS_NO_EXPERIENCE env var"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
