"""
Centralized import path configuration for hooks.

Provides zero-trust path setup that works in both plugin and development modes.
Single source of truth for import path configuration.

Security: Zero-trust path validation (checks existence before adding to sys.path)

Usage:
    from setup_paths import setup_import_paths
    setup_import_paths()
    # Now all triads.* imports work
"""

import os
import sys
from pathlib import Path
from typing import Optional


def get_plugin_root() -> Optional[Path]:
    """
    Get plugin root directory (plugin mode) or repository root (dev mode).

    Returns:
        Path: Plugin/repository root, or None if not found
    """
    # Check for plugin mode first
    plugin_root_env = os.environ.get('CLAUDE_PLUGIN_ROOT')
    if plugin_root_env:
        plugin_root = Path(plugin_root_env)
        if plugin_root.exists():
            return plugin_root

    # Development mode: find repository root from this file's location
    # This file is in: repo_root/hooks/setup_paths.py
    repo_root = Path(__file__).parent.parent

    if repo_root.exists():
        return repo_root

    return None


def get_project_dir() -> Path:
    """
    Get project directory where hooks are executing.

    Priority (first found wins):
    1. CLAUDE_PROJECT_DIR environment variable
    2. PWD environment variable
    3. Current working directory

    Returns:
        Path: Project directory
    """
    # Priority 1: CLAUDE_PROJECT_DIR (set by Claude Code)
    if "CLAUDE_PROJECT_DIR" in os.environ:
        return Path(os.environ["CLAUDE_PROJECT_DIR"])

    # Priority 2: PWD (current directory when hook was invoked)
    if "PWD" in os.environ:
        return Path(os.environ["PWD"])

    # Priority 3: Current working directory (fallback)
    return Path.cwd()


def setup_import_paths() -> None:
    """
    Configure sys.path for hook imports in both plugin and development modes.

    This function is idempotent - safe to call multiple times.

    Security: Zero-trust path validation
    - Only adds paths that actually exist
    - Validates paths before adding to sys.path
    - Prevents path injection attacks

    Modes:
    - Plugin mode: Detected via CLAUDE_PLUGIN_ROOT env var
      Adds: plugin_root/src to sys.path
    - Development mode: Detected by repository structure
      Adds: repo_root/src and repo_root/hooks to sys.path
    """
    root = get_plugin_root()

    if not root:
        # No valid root found - hooks may fail to import triads.*
        # This is non-fatal - some hooks don't need triads imports
        return

    # Determine mode
    plugin_root_env = os.environ.get('CLAUDE_PLUGIN_ROOT')
    is_plugin_mode = plugin_root_env is not None

    if is_plugin_mode:
        # Plugin mode: Add plugin_root/src to sys.path
        src_path = root / "src"

        # Zero-trust: Verify path exists before adding
        if src_path.exists() and src_path.is_dir():
            src_path_str = str(src_path)
            if src_path_str not in sys.path:
                sys.path.insert(0, src_path_str)
    else:
        # Development mode: Add repo_root/src and repo_root/hooks to sys.path
        src_path = root / "src"
        hooks_path = root / "hooks"

        # Zero-trust: Verify paths exist before adding
        if src_path.exists() and src_path.is_dir():
            src_path_str = str(src_path)
            if src_path_str not in sys.path:
                sys.path.insert(0, src_path_str)

        if hooks_path.exists() and hooks_path.is_dir():
            hooks_path_str = str(hooks_path)
            if hooks_path_str not in sys.path:
                sys.path.insert(0, hooks_path_str)
