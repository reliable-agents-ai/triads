"""Tests for router configuration."""

import json

import pytest

from src.triads.router.config import RouterConfig


class TestRouterConfig:
    """Test RouterConfig loading and validation."""

    @pytest.fixture
    def config_file(self, tmp_path):
        """Create temporary config file."""
        config_path = tmp_path / "config.json"
        config_data = {
            "confidence_threshold": 0.70,
            "grace_period_turns": 5,
            "grace_period_minutes": 8,
            "llm_timeout_ms": 2000,
            "semantic_similarity_threshold": 0.10,
            "training_mode": False,
            "telemetry_enabled": True,
            "model_path": ".claude/router/models/all-MiniLM-L6-v2",
        }
        config_path.write_text(json.dumps(config_data))
        return config_path

    def test_load_default_config(self, config_file):
        """Test loading config with default values."""
        config = RouterConfig(config_path=str(config_file))

        assert config.confidence_threshold == 0.70
        assert config.grace_period_turns == 5
        assert config.grace_period_minutes == 8
        assert config.llm_timeout_ms == 2000
        assert config.semantic_similarity_threshold == 0.10
        assert config.training_mode is False
        assert config.telemetry_enabled is True
        assert config.model_path == ".claude/router/models/all-MiniLM-L6-v2"

    def test_load_nonexistent_config(self):
        """Test loading nonexistent config raises error."""
        with pytest.raises(FileNotFoundError, match="Router config not found"):
            RouterConfig(config_path="/nonexistent/config.json")

    def test_env_override_confidence(self, config_file, monkeypatch):
        """Test environment variable override for confidence threshold."""
        monkeypatch.setenv("CLAUDE_ROUTER_CONFIDENCE", "0.85")

        config = RouterConfig(config_path=str(config_file))

        assert config.confidence_threshold == 0.85

    def test_env_override_grace_turns(self, config_file, monkeypatch):
        """Test environment variable override for grace period turns."""
        monkeypatch.setenv("CLAUDE_ROUTER_GRACE_TURNS", "10")

        config = RouterConfig(config_path=str(config_file))

        assert config.grace_period_turns == 10

    def test_env_override_grace_minutes(self, config_file, monkeypatch):
        """Test environment variable override for grace period minutes."""
        monkeypatch.setenv("CLAUDE_ROUTER_GRACE_MINUTES", "15")

        config = RouterConfig(config_path=str(config_file))

        assert config.grace_period_minutes == 15

    def test_env_override_llm_timeout(self, config_file, monkeypatch):
        """Test environment variable override for LLM timeout."""
        monkeypatch.setenv("CLAUDE_ROUTER_LLM_TIMEOUT", "3000")

        config = RouterConfig(config_path=str(config_file))

        assert config.llm_timeout_ms == 3000

    def test_env_override_similarity_threshold(self, config_file, monkeypatch):
        """Test environment variable override for similarity threshold."""
        monkeypatch.setenv("CLAUDE_ROUTER_SIMILARITY_THRESHOLD", "0.15")

        config = RouterConfig(config_path=str(config_file))

        assert config.semantic_similarity_threshold == 0.15

    def test_env_override_training_mode(self, config_file, monkeypatch):
        """Test environment variable override for training mode."""
        monkeypatch.setenv("CLAUDE_ROUTER_TRAINING", "true")

        config = RouterConfig(config_path=str(config_file))

        assert config.training_mode is True

    def test_env_override_telemetry(self, config_file, monkeypatch):
        """Test environment variable override for telemetry."""
        monkeypatch.setenv("CLAUDE_ROUTER_TELEMETRY", "false")

        config = RouterConfig(config_path=str(config_file))

        assert config.telemetry_enabled is False

    def test_env_override_model_path(self, config_file, monkeypatch):
        """Test environment variable override for model path."""
        monkeypatch.setenv("CLAUDE_ROUTER_MODEL_PATH", "/custom/path/model")

        config = RouterConfig(config_path=str(config_file))

        assert config.model_path == "/custom/path/model"

    def test_invalid_confidence_value(self, config_file, monkeypatch):
        """Test invalid confidence threshold value."""
        monkeypatch.setenv("CLAUDE_ROUTER_CONFIDENCE", "1.5")

        with pytest.raises(ValueError, match="must be <= 1.0"):
            RouterConfig(config_path=str(config_file))

    def test_invalid_confidence_negative(self, config_file, monkeypatch):
        """Test negative confidence threshold value."""
        monkeypatch.setenv("CLAUDE_ROUTER_CONFIDENCE", "-0.5")

        with pytest.raises(ValueError, match="must be >= 0.0"):
            RouterConfig(config_path=str(config_file))

    def test_invalid_llm_timeout_too_low(self, config_file, monkeypatch):
        """Test LLM timeout too low."""
        monkeypatch.setenv("CLAUDE_ROUTER_LLM_TIMEOUT", "50")

        with pytest.raises(ValueError, match="must be >= 100"):
            RouterConfig(config_path=str(config_file))

    def test_invalid_llm_timeout_too_high(self, config_file, monkeypatch):
        """Test LLM timeout too high."""
        monkeypatch.setenv("CLAUDE_ROUTER_LLM_TIMEOUT", "20000")

        with pytest.raises(ValueError, match="must be <= 10000"):
            RouterConfig(config_path=str(config_file))

    def test_bool_env_variations(self, config_file, monkeypatch):
        """Test boolean environment variable parsing variations."""
        # Test various true values
        for true_val in ["true", "True", "TRUE", "1", "yes", "YES", "on", "ON"]:
            monkeypatch.setenv("CLAUDE_ROUTER_TRAINING", true_val)
            config = RouterConfig(config_path=str(config_file))
            assert config.training_mode is True

        # Test various false values
        for false_val in ["false", "False", "FALSE", "0", "no", "NO", "off", "OFF"]:
            monkeypatch.setenv("CLAUDE_ROUTER_TRAINING", false_val)
            config = RouterConfig(config_path=str(config_file))
            assert config.training_mode is False

    def test_repr(self, config_file):
        """Test string representation."""
        config = RouterConfig(config_path=str(config_file))
        repr_str = repr(config)

        assert "RouterConfig(" in repr_str
        assert "confidence_threshold=0.7" in repr_str
        assert "training_mode=False" in repr_str
