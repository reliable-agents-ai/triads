"""Tests for router path management."""
from pathlib import Path
import tempfile

from triads.router.router_paths import RouterPaths, DEFAULT_PATHS


class TestRouterPaths:
    """Test RouterPaths path construction."""

    def test_default_base_dir(self):
        """Test default base directory is ~/.claude."""
        paths = RouterPaths()
        assert paths.base_dir == Path.home() / ".claude"

    def test_custom_base_dir(self):
        """Test custom base directory."""
        custom_dir = Path("/custom/path")
        paths = RouterPaths(base_dir=custom_dir)
        assert paths.base_dir == custom_dir

    def test_router_dir(self):
        """Test router directory construction."""
        paths = RouterPaths()
        assert paths.router_dir == Path.home() / ".claude" / "router"

    def test_config_file(self):
        """Test config file path."""
        paths = RouterPaths()
        assert paths.config_file == Path.home() / ".claude" / "router" / "config.json"

    def test_state_file(self):
        """Test state file path."""
        paths = RouterPaths()
        assert paths.state_file == Path.home() / ".claude" / "router_state.json"

    def test_routes_file(self):
        """Test routes file path."""
        paths = RouterPaths()
        assert paths.routes_file == Path.home() / ".claude" / "router" / "triad_routes.json"

    def test_logs_dir(self):
        """Test logs directory path."""
        paths = RouterPaths()
        assert paths.logs_dir == Path.home() / ".claude" / "router" / "logs"

    def test_telemetry_file(self):
        """Test telemetry file path."""
        paths = RouterPaths()
        expected = Path.home() / ".claude" / "router" / "logs" / "routing_telemetry.jsonl"
        assert paths.telemetry_file == expected

    def test_custom_base_propagates(self):
        """Test custom base directory propagates to all paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            custom_base = Path(tmpdir) / "custom_claude"
            paths = RouterPaths(base_dir=custom_base)
            
            assert paths.base_dir == custom_base
            assert paths.router_dir == custom_base / "router"
            assert paths.config_file == custom_base / "router" / "config.json"
            assert paths.state_file == custom_base / "router_state.json"
            assert paths.routes_file == custom_base / "router" / "triad_routes.json"
            assert paths.logs_dir == custom_base / "router" / "logs"
            assert paths.telemetry_file == custom_base / "router" / "logs" / "routing_telemetry.jsonl"

    def test_default_paths_singleton(self):
        """Test DEFAULT_PATHS singleton."""
        assert DEFAULT_PATHS is not None
        assert isinstance(DEFAULT_PATHS, RouterPaths)
        assert DEFAULT_PATHS.base_dir == Path.home() / ".claude"

    def test_paths_are_path_objects(self):
        """Test all paths return Path objects."""
        paths = RouterPaths()
        
        assert isinstance(paths.base_dir, Path)
        assert isinstance(paths.router_dir, Path)
        assert isinstance(paths.config_file, Path)
        assert isinstance(paths.state_file, Path)
        assert isinstance(paths.routes_file, Path)
        assert isinstance(paths.logs_dir, Path)
        assert isinstance(paths.telemetry_file, Path)
