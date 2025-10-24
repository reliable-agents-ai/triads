"""Unified git command execution with error handling.

Consolidates duplicate git command execution patterns from:
- audit.py (user lookup)
- code_metrics.py (diff parsing)
- validator.py (diff parsing)

All git operations now use GitRunner for consistent error handling,
timeouts, and result parsing.

NOTE: GitRunner now delegates to CommandRunner for subprocess execution.
This provides consistent timeout, error handling, and security across
all subprocess operations in the codebase.
"""

from __future__ import annotations

import subprocess
from typing import Optional

from triads.utils.command_runner import CommandRunner, CommandResult


# Backward compatibility alias
GitCommandResult = CommandResult


class GitCommandError(Exception):
    """Raised when git command fails or times out."""
    pass


class GitRunner:
    """Executes git commands with consistent error handling.
    
    Provides unified interface for all git operations:
    - Automatic error handling
    - Timeout protection
    - Result parsing
    - Consistent error messages
    
    Example:
        # Run raw git command
        result = GitRunner.run(["status"])
        print(result.stdout)
        
        # Get user info
        name = GitRunner.get_user_name()
        email = GitRunner.get_user_email()
        
        # Parse diff
        changes = GitRunner.diff_numstat("HEAD~1")
        for added, deleted, filename in changes:
            print(f"{filename}: +{added} -{deleted}")
    """
    
    DEFAULT_TIMEOUT = 30
    
    @classmethod
    def run(
        cls,
        args: list[str],
        timeout: Optional[int] = None,
        check: bool = True
    ) -> GitCommandResult:
        """Run git command with error handling.

        Delegates to CommandRunner for consistent subprocess execution.

        Args:
            args: Git command arguments (without 'git' prefix)
            timeout: Command timeout in seconds (default: 30)
            check: Raise exception on non-zero exit (default: True)

        Returns:
            GitCommandResult with command output

        Raises:
            GitCommandError: If command fails or times out

        Example:
            result = GitRunner.run(["diff", "--numstat", "HEAD~1"])
            for line in result.stdout.split('\\n'):
                # Process diff output
                pass
        """
        timeout = timeout or cls.DEFAULT_TIMEOUT

        try:
            # Delegate to CommandRunner for consistent subprocess execution
            return CommandRunner.run_git(args, timeout=timeout, check=check)

        except subprocess.CalledProcessError as e:
            raise GitCommandError(
                f"Git command failed: git {' '.join(args)}\n"
                f"Exit code: {e.returncode}\n"
                f"Error: {e.stderr}"
            ) from e

        except TimeoutError as e:
            raise GitCommandError(
                f"Git command timed out after {timeout}s: git {' '.join(args)}"
            ) from e
    
    @classmethod
    def get_user_name(cls) -> str:
        """Get git user name from config.
        
        Returns:
            Git user name, or "unknown" if not configured
        
        Example:
            name = GitRunner.get_user_name()
            print(f"User: {name}")
        """
        try:
            result = cls.run(["config", "user.name"], timeout=2)
            name = result.stdout.strip()
            return name if name else "unknown"
        except GitCommandError:
            return "unknown"
    
    @classmethod
    def get_user_email(cls) -> str:
        """Get git user email from config.
        
        Returns:
            Git user email, or "unknown" if not configured
        
        Example:
            email = GitRunner.get_user_email()
            print(f"Email: {email}")
        """
        try:
            result = cls.run(["config", "user.email"], timeout=2)
            email = result.stdout.strip()
            return email if email else "unknown"
        except GitCommandError:
            return "unknown"
    
    @classmethod
    def diff_numstat(cls, base_ref: str, timeout: int = 30) -> list[tuple[int, int, str]]:
        """Get diff numstat (added, deleted, filename).
        
        Parses git diff --numstat output to extract line changes per file.
        Binary files (marked with "-") are automatically skipped.
        
        Args:
            base_ref: Git reference to compare against
            timeout: Command timeout in seconds
        
        Returns:
            List of (lines_added, lines_deleted, filename) tuples
        
        Raises:
            GitCommandError: If git command fails
        
        Example:
            changes = GitRunner.diff_numstat("HEAD~1")
            total_added = sum(a for a, d, f in changes)
            total_deleted = sum(d for a, d, f in changes)
            print(f"Total: +{total_added} -{total_deleted}")
        """
        result = cls.run(["diff", "--numstat", base_ref], timeout=timeout)
        
        changes = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            
            parts = line.split('\t')
            if len(parts) < 3:
                continue
            
            # Skip binary files (marked with "-")
            if parts[0] == "-" or parts[1] == "-":
                continue
            
            try:
                added = int(parts[0])
                deleted = int(parts[1])
                filename = parts[2]
                changes.append((added, deleted, filename))
            except ValueError:
                # Skip lines that can't be parsed as integers
                continue
        
        return changes
    
    @classmethod
    def diff_name_only(cls, base_ref: str, timeout: int = 30) -> list[str]:
        """Get list of changed files.
        
        Uses git diff --name-only to list files changed between base_ref and HEAD.
        
        Args:
            base_ref: Git reference to compare against
            timeout: Command timeout in seconds
        
        Returns:
            List of changed file paths
        
        Raises:
            GitCommandError: If git command fails
        
        Example:
            files = GitRunner.diff_name_only("origin/main")
            print(f"{len(files)} files changed")
        """
        result = cls.run(["diff", "--name-only", base_ref], timeout=timeout)
        return [f for f in result.stdout.strip().split('\n') if f]
    
    @classmethod
    def ls_files_untracked(cls, timeout: int = 30) -> list[str]:
        """Get list of untracked files.
        
        Uses git ls-files --others --exclude-standard to list untracked files
        (excludes .gitignore patterns).
        
        Args:
            timeout: Command timeout in seconds
        
        Returns:
            List of untracked file paths
        
        Raises:
            GitCommandError: If git command fails
        
        Example:
            untracked = GitRunner.ls_files_untracked()
            print(f"{len(untracked)} untracked files")
        """
        result = cls.run(["ls-files", "--others", "--exclude-standard"], timeout=timeout)
        return [f for f in result.stdout.strip().split('\n') if f]
