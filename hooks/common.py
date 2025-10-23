"""
Common utilities for Claude Code hooks.

Provides shared functionality for hook implementations:
- Output formatting (Claude Code hook protocol)
- Environment detection
- Error handling
"""

import json
import os
from pathlib import Path
from typing import Optional


def format_hook_output(event_name: str, context: str) -> dict:
    """
    Format hook output per Claude Code hook protocol.

    Args:
        event_name: Hook event name (SessionStart, Stop, UserPromptSubmit)
        context: Additional context to inject

    Returns:
        dict: Formatted hook output for Claude Code
    """
    return {
        "hookSpecificOutput": {
            "hookEventName": event_name,
            "additionalContext": context
        }
    }


def get_project_dir() -> Path:
    """
    Get project directory from environment or current working directory.

    Checks (in order):
    1. CLAUDE_PROJECT_DIR environment variable
    2. PWD environment variable
    3. Current working directory

    Returns:
        Path: Project directory
    """
    if "CLAUDE_PROJECT_DIR" in os.environ:
        return Path(os.environ["CLAUDE_PROJECT_DIR"])
    if "PWD" in os.environ:
        return Path(os.environ["PWD"])
    return Path.cwd()


def output_hook_result(event_name: str, context: str) -> None:
    """
    Format and print hook output to stdout.

    Claude Code reads hook output from stdout and injects context.

    Args:
        event_name: Hook event name
        context: Context to inject
    """
    output = format_hook_output(event_name, context)
    print(json.dumps(output))


def safe_get_context(
    get_context_fn,
    error_prefix: str = "Error loading context"
) -> str:
    """
    Safely call a context-generating function with error handling.

    Args:
        get_context_fn: Function that returns context string
        error_prefix: Prefix for error messages

    Returns:
        str: Context string or error message
    """
    try:
        return get_context_fn()
    except Exception as e:
        return f"{error_prefix}: {str(e)}"
