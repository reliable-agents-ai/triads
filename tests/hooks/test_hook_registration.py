"""
Tests for hook registration and event coverage.

Ensures all 10 Claude Code hook event types are properly registered
and have corresponding implementation files.

RED-GREEN-REFACTOR: This test was written BEFORE fixing the registration issue.
It should FAIL initially, then PASS after the fix.
"""

import json
from pathlib import Path

import pytest


# All 10 Claude Code hook event types (official documentation)
CLAUDE_CODE_HOOK_EVENTS = {
    "SessionStart",
    "SessionEnd",
    "UserPromptSubmit",
    "PreToolUse",
    "PostToolUse",
    "PermissionRequest",
    "Stop",
    "SubagentStop",
    "PreCompact",
    "Notification",
}

# Mapping of hook events to their implementation files
HOOK_IMPLEMENTATION_FILES = {
    "SessionStart": "session_start.py",
    "SessionEnd": "session_end.py",
    "UserPromptSubmit": "user_prompt_submit.py",
    "PreToolUse": "on_pre_experience_injection.py",
    "PostToolUse": "post_tool_use.py",
    "PermissionRequest": "permission_request.py",
    "Stop": "on_stop.py",
    "SubagentStop": "subagent_stop.py",
    "PreCompact": "pre_compact.py",
    "Notification": "notification.py",
}


@pytest.fixture
def hooks_dir() -> Path:
    """Get the hooks directory path."""
    return Path(__file__).parent.parent.parent / "hooks"


@pytest.fixture
def hooks_json_path(hooks_dir) -> Path:
    """Get the hooks.json path."""
    return hooks_dir / "hooks.json"


@pytest.fixture
def hooks_config(hooks_json_path) -> dict:
    """Load the hooks.json configuration."""
    with open(hooks_json_path, "r") as f:
        return json.load(f)


class TestHookRegistration:
    """Tests for hook event registration in hooks.json."""

    def test_all_hook_events_registered(self, hooks_config):
        """All 10 Claude Code hook events must be registered in hooks.json.

        This test verifies comprehensive event coverage. Missing registrations
        mean hooks exist but are never called by Claude Code.
        """
        registered_events = set(hooks_config.get("hooks", {}).keys())
        missing_events = CLAUDE_CODE_HOOK_EVENTS - registered_events

        assert missing_events == set(), (
            f"Missing hook event registrations: {missing_events}. "
            f"These hooks have implementation files but are not registered in hooks.json."
        )

    def test_no_unknown_events_registered(self, hooks_config):
        """Only valid Claude Code hook events should be registered.

        Prevents registration of typos or invalid event names.
        """
        registered_events = set(hooks_config.get("hooks", {}).keys())
        unknown_events = registered_events - CLAUDE_CODE_HOOK_EVENTS

        assert unknown_events == set(), (
            f"Unknown hook events registered: {unknown_events}. "
            f"Valid events are: {CLAUDE_CODE_HOOK_EVENTS}"
        )

    def test_each_registration_has_command(self, hooks_config):
        """Each registered hook must have a command configuration.

        Empty registrations are invalid and will cause runtime errors.
        """
        hooks = hooks_config.get("hooks", {})

        for event_name, event_config in hooks.items():
            assert len(event_config) > 0, f"Hook {event_name} has empty configuration"

            for config in event_config:
                hook_list = config.get("hooks", [])
                assert len(hook_list) > 0, f"Hook {event_name} has no hook commands"

                for hook in hook_list:
                    assert "command" in hook, f"Hook {event_name} missing 'command' field"
                    assert hook["command"], f"Hook {event_name} has empty command"


class TestHookImplementationFiles:
    """Tests for hook implementation file existence."""

    def test_all_implementation_files_exist(self, hooks_dir):
        """All hook implementation files must exist.

        Ensures no dangling references in hooks.json.
        """
        missing_files = []

        for event_name, filename in HOOK_IMPLEMENTATION_FILES.items():
            filepath = hooks_dir / filename
            if not filepath.exists():
                missing_files.append(f"{event_name}: {filename}")

        assert missing_files == [], (
            f"Missing hook implementation files: {missing_files}"
        )

    def test_implementation_files_are_executable(self, hooks_dir):
        """All hook files should have Python shebang for direct execution."""
        for event_name, filename in HOOK_IMPLEMENTATION_FILES.items():
            filepath = hooks_dir / filename
            if filepath.exists():
                content = filepath.read_text()
                assert content.startswith("#!/usr/bin/env python3"), (
                    f"Hook {event_name} ({filename}) missing Python shebang"
                )

    def test_implementation_files_have_main(self, hooks_dir):
        """All hook files should have a main() function and __main__ block."""
        for event_name, filename in HOOK_IMPLEMENTATION_FILES.items():
            filepath = hooks_dir / filename
            if filepath.exists():
                content = filepath.read_text()
                assert "def main():" in content, (
                    f"Hook {event_name} ({filename}) missing main() function"
                )
                assert '__name__ == "__main__"' in content, (
                    f"Hook {event_name} ({filename}) missing __main__ block"
                )


class TestHookEventCapture:
    """Tests for event capture integration in hooks."""

    def test_all_hooks_capture_events(self, hooks_dir):
        """All hook implementations should use event capture utilities.

        Ensures observability for all hook executions.
        """
        hooks_without_capture = []

        for event_name, filename in HOOK_IMPLEMENTATION_FILES.items():
            filepath = hooks_dir / filename
            if filepath.exists():
                content = filepath.read_text()

                # Check for event capture function usage
                has_capture = any([
                    "capture_hook_execution" in content,
                    "capture_hook_error" in content,
                    "safe_capture_event" in content,
                ])

                if not has_capture:
                    hooks_without_capture.append(f"{event_name}: {filename}")

        assert hooks_without_capture == [], (
            f"Hooks missing event capture: {hooks_without_capture}. "
            f"All hooks should use capture_hook_execution/capture_hook_error."
        )


class TestHookConsistency:
    """Tests for consistency across hook implementations."""

    def test_hooks_use_shared_path_setup(self, hooks_dir):
        """All hooks should use shared path setup utility.

        Prevents import path duplication.
        """
        hooks_without_setup = []

        for event_name, filename in HOOK_IMPLEMENTATION_FILES.items():
            filepath = hooks_dir / filename
            if filepath.exists():
                content = filepath.read_text()

                if "from setup_paths import setup_import_paths" not in content:
                    hooks_without_setup.append(f"{event_name}: {filename}")

        assert hooks_without_setup == [], (
            f"Hooks not using shared path setup: {hooks_without_setup}"
        )

    def test_hooks_get_workspace_id(self, hooks_dir):
        """All hooks should get workspace ID for event context.

        Ensures events can be correlated to workspaces.
        """
        hooks_without_workspace = []

        for event_name, filename in HOOK_IMPLEMENTATION_FILES.items():
            filepath = hooks_dir / filename
            if filepath.exists():
                content = filepath.read_text()

                if "get_active_workspace" not in content:
                    hooks_without_workspace.append(f"{event_name}: {filename}")

        assert hooks_without_workspace == [], (
            f"Hooks not getting workspace ID: {hooks_without_workspace}"
        )
