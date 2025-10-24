"""
Integration tests for the complete router system.

Tests end-to-end flows through all routing stages.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from triads.tools.router import (
    NotificationBuilder,
    RouterCLI,
    RouterConfig,
    RoutingDecision,
    TriadRouter,
    TrainingModeHandler,
)


class TestRouterIntegration:
    """Integration tests for TriadRouter orchestrator."""

    @pytest.fixture
    def temp_paths(self, tmp_path):
        """Create temporary paths for testing."""
        config_dir = tmp_path / "router"
        config_dir.mkdir()

        state_path = tmp_path / "router_state.json"
        config_path = config_dir / "config.json"

        # Create minimal config
        config_path.write_text(
            """
{
    "confidence_threshold": 0.70,
    "grace_period_turns": 5,
    "grace_period_minutes": 8,
    "llm_timeout_ms": 2000,
    "semantic_similarity_threshold": 0.10,
    "training_mode": false,
    "telemetry_enabled": false,
    "model_path": "sentence-transformers/all-MiniLM-L6-v2"
}
"""
        )

        return {
            "state_path": state_path,
            "config_path": config_path,
        }

    @pytest.fixture
    def mock_triad_routes(self, tmp_path):
        """Create mock triad_routes.json."""
        routes_dir = tmp_path / "router"
        routes_dir.mkdir(exist_ok=True)

        routes_path = routes_dir / "triad_routes.json"
        routes_path.write_text(
            """
{
    "routes": [
        {
            "name": "idea-validation",
            "description": "Research and validate ideas",
            "example_prompts": [
                "validate this idea",
                "research demand for this feature"
            ],
            "keywords": ["research", "validate", "demand"]
        },
        {
            "name": "implementation",
            "description": "Write production code",
            "example_prompts": [
                "implement authentication",
                "write code for feature X"
            ],
            "keywords": ["code", "implement", "write"]
        }
    ]
}
"""
        )

        return routes_path

    def test_semantic_routing_high_confidence(
        self, temp_paths, mock_triad_routes, monkeypatch
    ):
        """Test high confidence semantic routing."""
        # Mock config path
        monkeypatch.setenv("HOME", str(mock_triad_routes.parent.parent))

        # Patch RouterEmbedder and SemanticRouter to avoid file dependencies
        with patch(
            "triads.tools.router.router.RouterEmbedder"
        ) as mock_embedder_class, patch(
            "triads.tools.router.router.SemanticRouter"
        ) as mock_semantic_router_class:
            mock_embedder = MagicMock()
            mock_embedder_class.return_value = mock_embedder

            # Mock semantic router to return high confidence
            mock_semantic_router = MagicMock()
            mock_semantic_router.route.return_value = [
                ("implementation", 0.92),
                ("idea-validation", 0.45),
            ]
            mock_semantic_router.threshold_check.return_value = (
                RoutingDecision.ROUTE_IMMEDIATELY,
                [("implementation", 0.92)],
            )
            mock_semantic_router_class.return_value = mock_semantic_router

            router = TriadRouter(
                config_path=temp_paths["config_path"],
                state_path=temp_paths["state_path"],
            )

            result = router.route("write code for authentication")

            assert result["triad"] == "implementation"
            assert result["method"] == "semantic"
            assert result["confidence"] >= 0.70
            assert result["grace_period_active"] is False
            assert "latency_ms" in result

    def test_grace_period_continuation(self, temp_paths, mock_triad_routes, monkeypatch):
        """Test grace period prevents re-routing."""
        monkeypatch.setenv("HOME", str(mock_triad_routes.parent.parent))

        with patch("triads.tools.router.router.RouterEmbedder") as mock_embedder_class, patch(
            "triads.tools.router.router.SemanticRouter"
        ) as mock_semantic_router_class:
            mock_embedder = MagicMock()
            mock_embedder_class.return_value = mock_embedder

            mock_semantic_router = MagicMock()
            mock_semantic_router_class.return_value = mock_semantic_router

            router = TriadRouter(
                config_path=temp_paths["config_path"],
                state_path=temp_paths["state_path"],
            )

            # First route - activate implementation triad
            state = router.state_manager.load()
            router.grace_period.reset_grace_period(state, "implementation")
            router.state_manager.save(state)

            # Second route - should stay in implementation (grace period)
            result = router.route("validate idea")

            assert result["triad"] == "implementation"
            assert result["method"] == "grace_period"
            assert result["grace_period_active"] is True
            assert "grace_status" in result

    def test_manual_selection_fallback(
        self, temp_paths, mock_triad_routes, monkeypatch
    ):
        """Test manual selection when LLM unavailable."""
        monkeypatch.setenv("HOME", str(mock_triad_routes.parent.parent))
        # Ensure no API key
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

        with patch("triads.tools.router.router.RouterEmbedder") as mock_embedder_class, patch(
            "triads.tools.router.router.SemanticRouter"
        ) as mock_semantic_router_class:
            mock_embedder = MagicMock()
            mock_embedder_class.return_value = mock_embedder

            # Mock semantic router to return ambiguous scores
            mock_semantic_router = MagicMock()
            mock_semantic_router.route.return_value = [
                ("implementation", 0.65),
                ("idea-validation", 0.63),
            ]
            mock_semantic_router.threshold_check.return_value = (
                RoutingDecision.LLM_FALLBACK_REQUIRED,
                [("implementation", 0.65), ("idea-validation", 0.63)],
            )
            mock_semantic_router_class.return_value = mock_semantic_router

            router = TriadRouter(
                config_path=temp_paths["config_path"],
                state_path=temp_paths["state_path"],
            )

            # Mock manual selector to return a choice
            with patch.object(
                router.manual_selector,
                "select_triad",
                return_value=("implementation", "llm_unavailable"),
            ):
                result = router.route("ambiguous prompt")

                assert result["triad"] == "implementation"
                assert result["method"] == "manual"
                assert result["confidence"] == 1.0


class TestNotificationBuilder:
    """Test notification formatting."""

    def test_format_semantic_notification_high_confidence(self):
        """Test high confidence semantic notification."""
        notifier = NotificationBuilder()

        result = {
            "triad": "implementation",
            "confidence": 0.92,
            "method": "semantic",
            "reasoning": "High confidence semantic match (92%)",
            "grace_period_active": False,
            "latency_ms": 8.5,
        }

        notification = notifier.format_routing_notification(result)

        assert "implementation" in notification
        assert "🔀" in notification

    def test_format_grace_period_notification(self):
        """Test grace period notification with status."""
        notifier = NotificationBuilder()

        result = {
            "triad": "design",
            "confidence": 1.0,
            "method": "grace_period",
            "reasoning": "Continuing in design (grace period active)",
            "grace_period_active": True,
            "grace_status": {
                "active": True,
                "turns_remaining": 3,
                "minutes_remaining": 5.0,
                "reason": "both",
            },
            "latency_ms": 2.1,
        }

        notification = notifier.format_routing_notification(result)

        assert "design" in notification
        assert "💬" in notification
        assert "3" in notification or "5" in notification

    def test_format_manual_notification(self):
        """Test manual selection notification."""
        notifier = NotificationBuilder()

        result = {
            "triad": "deployment",
            "confidence": 1.0,
            "method": "manual",
            "reasoning": "Manual selection (reason: llm_unavailable)",
            "grace_period_active": False,
            "latency_ms": 150.0,
        }

        notification = notifier.format_routing_notification(result)

        assert "deployment" in notification
        assert "✅" in notification

    def test_format_cancelled_notification(self):
        """Test cancellation notification."""
        notifier = NotificationBuilder()

        result = {
            "triad": None,
            "confidence": 0.0,
            "method": "cancelled",
            "reasoning": "User cancelled routing",
            "grace_period_active": False,
            "latency_ms": 50.0,
        }

        notification = notifier.format_routing_notification(result)

        assert "cancelled" in notification.lower()
        assert "❌" in notification


class TestTrainingModeHandler:
    """Test training mode functionality."""

    def test_should_request_confirmation_enabled(self):
        """Test confirmation requested when enabled."""
        handler = TrainingModeHandler(enabled=True)

        result = {
            "triad": "implementation",
            "confidence": 0.85,
            "method": "semantic",
            "grace_period_active": False,
        }

        assert handler.should_request_confirmation(result) is True

    def test_should_not_request_confirmation_disabled(self):
        """Test no confirmation when disabled."""
        handler = TrainingModeHandler(enabled=False)

        result = {
            "triad": "implementation",
            "confidence": 0.85,
            "method": "semantic",
            "grace_period_active": False,
        }

        assert handler.should_request_confirmation(result) is False

    def test_should_not_request_confirmation_grace_period(self):
        """Test no confirmation for grace period continuations."""
        handler = TrainingModeHandler(enabled=True)

        result = {
            "triad": "design",
            "confidence": 1.0,
            "method": "grace_period",
            "grace_period_active": True,
        }

        assert handler.should_request_confirmation(result) is False

    def test_check_graduation(self):
        """Test graduation threshold detection."""
        handler = TrainingModeHandler(enabled=True, graduation_threshold=50)

        # Below threshold
        assert handler.check_graduation(25) is not None  # Milestone
        assert handler.check_graduation(30) is None  # No milestone

        # At threshold
        msg = handler.check_graduation(50)
        assert msg is not None
        assert "Congratulations" in msg

    def test_format_training_status(self):
        """Test training status formatting."""
        handler = TrainingModeHandler(enabled=True, graduation_threshold=50)

        status = handler.format_training_status(25)

        assert "Training Mode" in status
        assert "25/50" in status

    def test_toggle(self):
        """Test training mode toggle."""
        handler = TrainingModeHandler(enabled=False)

        # Enable
        msg = handler.toggle(True)
        assert handler.enabled is True
        assert "ENABLED" in msg

        # Disable
        msg = handler.toggle(False)
        assert handler.enabled is False
        assert "DISABLED" in msg


class TestRouterCLI:
    """Test CLI command handlers."""

    @pytest.fixture
    def temp_state_path(self, tmp_path):
        """Create temp state path."""
        return tmp_path / "router_state.json"

    @pytest.fixture
    def mock_config(self, tmp_path, monkeypatch):
        """Mock config path."""
        config_dir = tmp_path / "router"
        config_dir.mkdir()
        config_path = config_dir / "config.json"

        config_path.write_text(
            """
{
    "confidence_threshold": 0.70,
    "grace_period_turns": 5,
    "grace_period_minutes": 8,
    "llm_timeout_ms": 2000,
    "semantic_similarity_threshold": 0.10,
    "training_mode": false,
    "telemetry_enabled": false,
    "model_path": "sentence-transformers/all-MiniLM-L6-v2"
}
"""
        )

        monkeypatch.setenv("HOME", str(tmp_path))
        return config_path

    def test_status_no_active_triad(self, temp_state_path, mock_config):
        """Test status with no active triad."""
        with patch(
            "triads.tools.router.cli.RouterStateManager"
        ) as mock_state_manager_class, patch(
            "triads.tools.router.cli.RouterConfig"
        ) as mock_config_class, patch(
            "triads.tools.router.cli.TelemetryLogger"
        ):
            mock_state_manager = MagicMock()
            mock_state = MagicMock()
            mock_state.active_triad = None
            mock_state_manager.load.return_value = mock_state
            mock_state_manager_class.return_value = mock_state_manager

            mock_config_inst = MagicMock()
            mock_config_inst.training_mode = False
            mock_config_inst.telemetry_enabled = False
            mock_config_class.return_value = mock_config_inst

            cli = RouterCLI()
            status = cli.status()

            assert "No active triad" in status

    def test_switch_triad_valid(self, temp_state_path, mock_config):
        """Test switching to valid triad."""
        with patch(
            "triads.tools.router.cli.RouterStateManager"
        ) as mock_state_manager_class, patch(
            "triads.tools.router.cli.RouterConfig"
        ) as mock_config_class, patch(
            "triads.tools.router.cli.TelemetryLogger"
        ):
            mock_state_manager = MagicMock()
            mock_state = MagicMock()
            mock_state_manager.load.return_value = mock_state
            mock_state_manager_class.return_value = mock_state_manager

            mock_config_inst = MagicMock()
            mock_config_inst.telemetry_enabled = False
            mock_config_class.return_value = mock_config_inst

            cli = RouterCLI()
            result = cli.switch_triad("implementation")

            assert "Switched to implementation" in result

    def test_switch_triad_invalid(self, temp_state_path, mock_config):
        """Test switching to invalid triad."""
        with patch(
            "triads.tools.router.cli.RouterConfig"
        ) as mock_config_class, patch(
            "triads.tools.router.cli.TelemetryLogger"
        ):
            mock_config_inst = MagicMock()
            mock_config_inst.telemetry_enabled = False
            mock_config_class.return_value = mock_config_inst

            cli = RouterCLI()
            result = cli.switch_triad("invalid-triad")

            assert "Invalid triad" in result

    def test_reset(self, temp_state_path, mock_config):
        """Test state reset."""
        with patch(
            "triads.tools.router.cli.RouterStateManager"
        ) as mock_state_manager_class, patch(
            "triads.tools.router.cli.RouterConfig"
        ) as mock_config_class, patch(
            "triads.tools.router.cli.TelemetryLogger"
        ):
            mock_state_manager = MagicMock()
            mock_state_manager_class.return_value = mock_state_manager

            mock_config_inst = MagicMock()
            mock_config_inst.telemetry_enabled = False
            mock_config_class.return_value = mock_config_inst

            cli = RouterCLI()
            result = cli.reset()

            assert "reset" in result.lower()
            mock_state_manager.reset.assert_called_once()

    def test_training_mode_on(self, temp_state_path, mock_config):
        """Test enabling training mode."""
        with patch(
            "triads.tools.router.cli.RouterConfig"
        ) as mock_config_class, patch(
            "triads.tools.router.cli.TelemetryLogger"
        ):
            mock_config_inst = MagicMock()
            mock_config_inst.training_mode = False
            mock_config_inst.telemetry_enabled = False
            mock_config_class.return_value = mock_config_inst

            cli = RouterCLI()
            result = cli.training_mode("on")

            assert "ENABLED" in result

    def test_training_mode_off(self, temp_state_path, mock_config):
        """Test disabling training mode."""
        with patch(
            "triads.tools.router.cli.RouterConfig"
        ) as mock_config_class, patch(
            "triads.tools.router.cli.TelemetryLogger"
        ):
            mock_config_inst = MagicMock()
            mock_config_inst.training_mode = True
            mock_config_inst.telemetry_enabled = False
            mock_config_class.return_value = mock_config_inst

            cli = RouterCLI()
            result = cli.training_mode("off")

            assert "DISABLED" in result

    def test_training_mode_invalid(self, temp_state_path, mock_config):
        """Test invalid training mode argument."""
        with patch(
            "triads.tools.router.cli.RouterConfig"
        ) as mock_config_class, patch(
            "triads.tools.router.cli.TelemetryLogger"
        ):
            mock_config_inst = MagicMock()
            mock_config_inst.telemetry_enabled = False
            mock_config_class.return_value = mock_config_inst

            cli = RouterCLI()
            result = cli.training_mode("maybe")

            assert "Invalid" in result

    def test_stats_no_data(self, temp_state_path, mock_config):
        """Test stats with no telemetry data."""
        with patch(
            "triads.tools.router.cli.RouterConfig"
        ) as mock_config_class, patch(
            "triads.tools.router.cli.TelemetryLogger"
        ):
            mock_config_inst = MagicMock()
            mock_config_inst.telemetry_enabled = False
            mock_config_class.return_value = mock_config_inst

            cli = RouterCLI()
            result = cli.stats()

            assert "No routing data" in result
