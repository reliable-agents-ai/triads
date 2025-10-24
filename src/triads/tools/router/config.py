"""
Router configuration management.

Loads configuration from JSON with environment variable overrides.
"""

import json
import os
from pathlib import Path
from typing import Optional

from ._router_paths import DEFAULT_PATHS


class RouterConfig:
    """
    Router configuration with environment variable overrides.

    Configuration is loaded from config.json with optional environment variable overrides:
    - CLAUDE_ROUTER_CONFIDENCE: Override confidence_threshold
    - CLAUDE_ROUTER_GRACE_TURNS: Override grace_period_turns
    - CLAUDE_ROUTER_GRACE_MINUTES: Override grace_period_minutes
    - CLAUDE_ROUTER_LLM_TIMEOUT: Override llm_timeout_ms
    - CLAUDE_ROUTER_SIMILARITY_THRESHOLD: Override semantic_similarity_threshold
    - CLAUDE_ROUTER_TRAINING: Override training_mode (true/false)
    - CLAUDE_ROUTER_TELEMETRY: Override telemetry_enabled (true/false)
    - CLAUDE_ROUTER_MODEL_PATH: Override model_path
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration.

        Args:
            config_path: Path to config.json. Defaults to ~/.claude/router/config.json
        """
        if config_path is None:
            config_path = DEFAULT_PATHS.config_file
        else:
            config_path = Path(config_path)

        if not config_path.exists():
            raise FileNotFoundError(
                f"Router config not found at {config_path}. "
                f"Run router installation to create it."
            )

        with open(config_path) as f:
            config = json.load(f)

        # Load with env var overrides
        self.confidence_threshold = self._get_float_env(
            "CLAUDE_ROUTER_CONFIDENCE",
            config["confidence_threshold"],
            min_val=0.0,
            max_val=1.0,
        )

        self.grace_period_turns = self._get_int_env(
            "CLAUDE_ROUTER_GRACE_TURNS",
            config["grace_period_turns"],
            min_val=0,
        )

        self.grace_period_minutes = self._get_int_env(
            "CLAUDE_ROUTER_GRACE_MINUTES",
            config["grace_period_minutes"],
            min_val=0,
        )

        self.llm_timeout_ms = self._get_int_env(
            "CLAUDE_ROUTER_LLM_TIMEOUT",
            config["llm_timeout_ms"],
            min_val=100,
            max_val=10000,
        )

        self.semantic_similarity_threshold = self._get_float_env(
            "CLAUDE_ROUTER_SIMILARITY_THRESHOLD",
            config["semantic_similarity_threshold"],
            min_val=0.0,
            max_val=1.0,
        )

        self.training_mode = self._get_bool_env(
            "CLAUDE_ROUTER_TRAINING",
            config["training_mode"],
        )

        self.telemetry_enabled = self._get_bool_env(
            "CLAUDE_ROUTER_TELEMETRY",
            config["telemetry_enabled"],
        )

        self.model_path = os.getenv("CLAUDE_ROUTER_MODEL_PATH", config["model_path"])

    @staticmethod
    def _get_float_env(
        var_name: str,
        default: float,
        min_val: Optional[float] = None,
        max_val: Optional[float] = None,
    ) -> float:
        """Get float from environment with validation."""
        env_val = os.getenv(var_name)
        if env_val is None:
            return default

        try:
            value = float(env_val)

            if min_val is not None and value < min_val:
                raise ValueError(f"{var_name} must be >= {min_val}, got {value}")

            if max_val is not None and value > max_val:
                raise ValueError(f"{var_name} must be <= {max_val}, got {value}")

            return value
        except ValueError as e:
            raise ValueError(f"Invalid {var_name} value '{env_val}': {e}") from e

    @staticmethod
    def _get_int_env(
        var_name: str,
        default: int,
        min_val: Optional[int] = None,
        max_val: Optional[int] = None,
    ) -> int:
        """Get integer from environment with validation."""
        env_val = os.getenv(var_name)
        if env_val is None:
            return default

        try:
            value = int(env_val)

            if min_val is not None and value < min_val:
                raise ValueError(f"{var_name} must be >= {min_val}, got {value}")

            if max_val is not None and value > max_val:
                raise ValueError(f"{var_name} must be <= {max_val}, got {value}")

            return value
        except ValueError as e:
            raise ValueError(f"Invalid {var_name} value '{env_val}': {e}") from e

    @staticmethod
    def _get_bool_env(var_name: str, default: bool) -> bool:
        """Get boolean from environment."""
        env_val = os.getenv(var_name)
        if env_val is None:
            return default

        return env_val.lower() in ("true", "1", "yes", "on")

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"RouterConfig("
            f"confidence_threshold={self.confidence_threshold}, "
            f"grace_period_turns={self.grace_period_turns}, "
            f"grace_period_minutes={self.grace_period_minutes}, "
            f"llm_timeout_ms={self.llm_timeout_ms}, "
            f"semantic_similarity_threshold={self.semantic_similarity_threshold}, "
            f"training_mode={self.training_mode}, "
            f"telemetry_enabled={self.telemetry_enabled}, "
            f"model_path={self.model_path}"
            f")"
        )
