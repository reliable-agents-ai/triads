"""Unified command execution with error handling.

Provides consistent subprocess execution with:
- Timeout enforcement
- Error handling
- Security (no shell=True)
- Testability (mockable)

This module consolidates subprocess patterns from:
- git_utils.py (GitRunner)
- workflow_context.py (ad-hoc git commands)
- headless_classifier.py (Claude subprocess calls)

Example:
    # Run any command
    result = CommandRunner.run(["echo", "hello"])
    print(result.stdout)

    # Git convenience
    result = CommandRunner.run_git(["status", "--short"])
    if result.success:
        print(result.stdout)

    # Claude convenience
    result = CommandRunner.run_claude(["-p", "test", "--output-format", "json"])
    response = json.loads(result.stdout)
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import Optional


@dataclass
class CommandResult:
    """Result of command execution.

    Attributes:
        success: Whether command succeeded (returncode == 0)
        stdout: Standard output from command
        stderr: Standard error from command
        returncode: Process exit code
    """
    success: bool
    stdout: str
    stderr: str
    returncode: int


class CommandRunner:
    """Execute external commands with consistent error handling.

    Provides unified interface for subprocess execution:
    - Automatic timeout enforcement
    - Consistent error handling
    - Security (array-style commands, no shell=True)
    - Testability (mockable subprocess.run)

    Example:
        # Basic usage
        result = CommandRunner.run(["ls", "-la"])

        # With timeout
        result = CommandRunner.run(["sleep", "5"], timeout=10)

        # Don't raise on error
        result = CommandRunner.run(["false"], check=False)
        if not result.success:
            print(f"Command failed: {result.stderr}")
    """

    DEFAULT_TIMEOUT = 30

    @classmethod
    def run(
        cls,
        cmd: list[str],
        timeout: Optional[int] = None,
        check: bool = True,
        cwd: Optional[str] = None
    ) -> CommandResult:
        """Run command with error handling and timeout.

        Args:
            cmd: Command as list (e.g., ["git", "status"])
            timeout: Timeout in seconds (default: 30)
            check: Raise on non-zero exit (default: True)
            cwd: Working directory (default: None)

        Returns:
            CommandResult with success, stdout, stderr, returncode

        Raises:
            TimeoutError: If command exceeds timeout
            subprocess.CalledProcessError: If check=True and command fails

        Example:
            result = CommandRunner.run(["git", "status"], timeout=5)
            print(result.stdout)
        """
        timeout = timeout or cls.DEFAULT_TIMEOUT

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=check,
                cwd=cwd
            )
            return CommandResult(
                success=True,
                stdout=result.stdout,
                stderr=result.stderr,
                returncode=result.returncode
            )

        except subprocess.TimeoutExpired as e:
            raise TimeoutError(
                f"Command {' '.join(cmd)} timed out after {timeout}s"
            ) from e

        except subprocess.CalledProcessError as e:
            if check:
                raise
            return CommandResult(
                success=False,
                stdout=e.stdout or "",
                stderr=e.stderr or "",
                returncode=e.returncode
            )

    @classmethod
    def run_git(
        cls,
        args: list[str],
        **kwargs
    ) -> CommandResult:
        """Run git command (convenience method).

        Args:
            args: Git arguments (e.g., ["status", "--short"])
            **kwargs: Passed to run()

        Returns:
            CommandResult from git command

        Example:
            result = CommandRunner.run_git(["branch", "--show-current"])
            if result.success:
                branch = result.stdout.strip()
        """
        return cls.run(["git"] + args, **kwargs)

    @classmethod
    def run_claude(
        cls,
        args: list[str],
        **kwargs
    ) -> CommandResult:
        """Run claude command (convenience method).

        Args:
            args: Claude arguments (e.g., ["-p", "prompt", "--allowedTools", ""])
            **kwargs: Passed to run()

        Returns:
            CommandResult from claude command

        Example:
            result = CommandRunner.run_claude(["-p", prompt, "--output-format", "json"])
            response = json.loads(result.stdout)
        """
        return cls.run(["claude"] + args, **kwargs)
