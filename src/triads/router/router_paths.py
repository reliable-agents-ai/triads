"""
Centralized path management for router components.

Provides standard locations for all router configuration, state,
and telemetry files.
"""
from pathlib import Path
from typing import Optional


class RouterPaths:
    """
    Centralized router path management.
    
    Provides consistent path construction for all router files to prevent
    duplication and inconsistencies across components.
    """
    
    def __init__(self, base_dir: Optional[Path] = None):
        """
        Initialize router paths.
        
        Args:
            base_dir: Base directory for router files. Defaults to ~/.claude
        """
        if base_dir is None:
            base_dir = Path.home() / ".claude"
        
        self._base_dir = Path(base_dir)
    
    @property
    def base_dir(self) -> Path:
        """Base directory for all router files (~/.claude)."""
        return self._base_dir
    
    @property
    def router_dir(self) -> Path:
        """Router directory (~/.claude/router)."""
        return self._base_dir / "router"
    
    @property
    def config_file(self) -> Path:
        """Router configuration file (~/.claude/router/config.json)."""
        return self.router_dir / "config.json"
    
    @property
    def state_file(self) -> Path:
        """Router state file (~/.claude/router_state.json)."""
        return self._base_dir / "router_state.json"
    
    @property
    def routes_file(self) -> Path:
        """Triad routes file (~/.claude/router/triad_routes.json)."""
        return self.router_dir / "triad_routes.json"
    
    @property
    def logs_dir(self) -> Path:
        """Logs directory (~/.claude/router/logs)."""
        return self.router_dir / "logs"
    
    @property
    def telemetry_file(self) -> Path:
        """Telemetry log file (~/.claude/router/logs/routing_telemetry.jsonl)."""
        return self.logs_dir / "routing_telemetry.jsonl"


# Global singleton for default paths
DEFAULT_PATHS = RouterPaths()
