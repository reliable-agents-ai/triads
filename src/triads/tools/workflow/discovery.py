"""Triad discovery system for dynamic workflow detection.

This module dynamically discovers triads by scanning the .claude/agents/ directory.
It enables the workflow enforcement system to work with ANY generated workflow
without hardcoding triad names.

Per ADR-GENERIC: Schema-driven, domain-agnostic workflow enforcement
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


class TriadDiscoveryError(Exception):
    """Raised when triad discovery fails."""
    pass


@dataclass
class TriadInfo:
    """Information about a discovered triad.

    Attributes:
        id: Triad identifier (directory name)
        path: Full path to triad directory
        agents: List of agent filenames (sorted, .md files only)
        agent_count: Number of agents in this triad

    Example:
        info = TriadInfo(
            id="idea-validation",
            path=".claude/agents/idea-validation",
            agents=["analyst.md", "researcher.md"],
            agent_count=2
        )
    """
    id: str
    path: str
    agents: list[str]
    agent_count: int


class TriadDiscovery:
    """Discovers triads by scanning filesystem.

    Scans .claude/agents/ directory to find all triads and their agents.
    Results are cached for performance.

    Example:
        discovery = TriadDiscovery()
        triads = discovery.discover_triads()

        for triad in triads:
            print(f"{triad.id}: {triad.agent_count} agents")

        if discovery.triad_exists("idea-validation"):
            print("Idea validation triad found!")
    """

    def __init__(self, base_path: str = ".claude/agents"):
        """Initialize discovery system.

        Args:
            base_path: Base directory containing triad subdirectories
                      (default: .claude/agents)
        """
        self.base_path = base_path
        self._cache: Optional[list[TriadInfo]] = None

    def discover_triads(self, force_refresh: bool = False) -> list[TriadInfo]:
        """Scan directory and return discovered triads.

        Scans base_path for subdirectories (each = one triad).
        Ignores hidden directories (starting with '.').

        Args:
            force_refresh: Clear cache and rescan filesystem

        Returns:
            List of TriadInfo objects, sorted by triad ID

        Example:
            triads = discovery.discover_triads()
            print(f"Found {len(triads)} triads")

            # Force refresh to see new triads
            triads = discovery.discover_triads(force_refresh=True)
        """
        # Return cached results if available
        if self._cache is not None and not force_refresh:
            return self._cache

        # Gracefully handle missing directory
        if not os.path.exists(self.base_path):
            self._cache = []
            return []

        triads = []

        try:
            # Scan for triad directories
            with os.scandir(self.base_path) as entries:
                for entry in entries:
                    # Only process visible directories
                    if entry.is_dir() and not entry.name.startswith('.'):
                        triad_id = entry.name
                        agents = self._scan_agents(entry.path)

                        triads.append(TriadInfo(
                            id=triad_id,
                            path=entry.path,
                            agents=agents,
                            agent_count=len(agents)
                        ))

        except PermissionError as e:
            raise TriadDiscoveryError(
                f"Failed to scan directory {self.base_path}: Permission denied"
            ) from e
        except OSError as e:
            raise TriadDiscoveryError(
                f"Failed to scan directory {self.base_path}: {e}"
            ) from e

        # Sort by triad ID for consistent ordering
        triads.sort(key=lambda t: t.id)

        # Cache results
        self._cache = triads
        return triads

    def _scan_agents(self, triad_path: str) -> list[str]:
        """Scan triad directory for agent files.

        Only includes:
        - Files ending with .md
        - Non-hidden files (not starting with '.')

        Args:
            triad_path: Path to triad directory

        Returns:
            Sorted list of agent filenames
        """
        agents = []

        try:
            for filename in os.listdir(triad_path):
                # Only include visible .md files
                if filename.endswith('.md') and not filename.startswith('.'):
                    agents.append(filename)
        except (PermissionError, OSError):
            # If we can't read a triad directory, return empty list
            # This allows discovery to continue for other triads
            return []

        return sorted(agents)

    def get_triad(self, triad_id: str) -> Optional[TriadInfo]:
        """Get specific triad by ID.

        Args:
            triad_id: Triad identifier (directory name)

        Returns:
            TriadInfo if found, None otherwise

        Example:
            triad = discovery.get_triad("idea-validation")
            if triad:
                print(f"Found {triad.agent_count} agents")
        """
        triads = self.discover_triads()
        return next((t for t in triads if t.id == triad_id), None)

    def triad_exists(self, triad_id: str) -> bool:
        """Check if triad exists.

        Args:
            triad_id: Triad identifier to check

        Returns:
            True if triad exists, False otherwise

        Example:
            if discovery.triad_exists("design"):
                print("Design triad is available")
        """
        return self.get_triad(triad_id) is not None
