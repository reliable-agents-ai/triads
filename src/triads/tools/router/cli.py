"""
CLI command handlers for router slash commands.

Implements handlers for:
- /router-status - Show current router state
- /switch-triad - Manually switch triads
- /router-reset - Reset router state
- /router-training - Toggle training mode
- /router-stats - Show routing statistics
"""

import json
from pathlib import Path
from typing import Optional

from .config import RouterConfig
from ._grace_period import GracePeriodChecker
from ._notifications import NotificationBuilder
from ._router_paths import DEFAULT_PATHS
from ._state_manager import _RouterStateManager as RouterStateManager
from ._telemetry import TelemetryLogger
from .training_mode import TrainingModeHandler


class RouterCLI:
    """CLI command handlers for router commands."""

    def __init__(self):
        """Initialize CLI with router components."""
        self.state_manager = RouterStateManager()
        self.config = RouterConfig()
        self.telemetry = TelemetryLogger(enabled=self.config.telemetry_enabled)
        self.notifier = NotificationBuilder()
        self.training_handler = TrainingModeHandler(
            enabled=self.config.training_mode
        )

    def status(self) -> str:
        """
        Show current router status.

        Returns:
            Formatted status string with:
            - Active triad
            - Turn count
            - Last activity timestamp
            - Grace period status
        """
        state = self.state_manager.load()

        if not state.active_triad:
            return "ℹ️  No active triad. Router will choose based on your next prompt."

        grace_checker = GracePeriodChecker(
            self.state_manager,
            self.config.grace_period_turns,
            self.config.grace_period_minutes,
        )
        grace_status = grace_checker.get_grace_period_status(state)

        output = f"""
📊 Router Status
{'=' * 50}

Active Triad: {state.active_triad}
Turn Count: {state.turn_count}
Last Activity: {state.last_activity or 'N/A'}

{self.notifier.format_grace_period_summary(grace_status)}

Training Mode: {'🟢 Enabled' if self.config.training_mode else '🔴 Disabled'}
"""

        if self.config.training_mode:
            confirmations = state.training_mode_confirmations
            output += f"Training Confirmations: {confirmations}/50\n"

        return output.strip()

    def switch_triad(self, triad_name: str) -> str:
        """
        Switch to specified triad.

        Args:
            triad_name: Name of triad to switch to

        Returns:
            Success or error message
        """
        valid_triads = [
            "idea-validation",
            "design",
            "implementation",
            "garden-tending",
            "deployment",
        ]

        if triad_name not in valid_triads:
            return (
                f"❌ Invalid triad: {triad_name}\n\n"
                f"Valid triads:\n"
                + "\n".join(f"  - {t}" for t in valid_triads)
            )

        state = self.state_manager.load()

        # Reset grace period for new triad
        grace_checker = GracePeriodChecker(self.state_manager)
        grace_checker.reset_grace_period(state, triad_name)

        self.state_manager.save(state)

        # Log manual switch
        self.telemetry.log_event(
            "manual_switch",
            {"from_triad": state.active_triad, "to_triad": triad_name},
        )

        return f"✅ Switched to {triad_name}"

    def reset(self) -> str:
        """
        Reset router state.

        Clears all state including session ID, active triad, grace period.

        Returns:
            Success message
        """
        self.state_manager.reset()

        self.telemetry.log_event("state_reset", {})

        return "✅ Router state reset"

    def training_mode(self, mode: str) -> str:
        """
        Toggle training mode.

        Args:
            mode: "on" or "off"

        Returns:
            Status message with usage instructions
        """
        if mode not in ["on", "off"]:
            return "❌ Invalid mode. Use 'on' or 'off'"

        enabled = mode == "on"

        # Update training handler
        result = self.training_handler.toggle(enabled)

        # Log mode change
        self.telemetry.log_event("training_mode_change", {"enabled": enabled})

        # Note: Config changes are in-memory only
        # For persistent changes, user should edit config.json
        note = """
Note: This change is for the current session only.
For persistent changes, edit ~/.claude/router/config.json
"""

        return result + "\n" + note

    def stats(self) -> str:
        """
        Show routing statistics from telemetry.

        Returns:
            Formatted statistics including:
            - Total routes
            - Method breakdown (semantic/LLM/manual)
            - Average confidence
            - Average latency
        """
        log_path = DEFAULT_PATHS.telemetry_file

        if not log_path.exists():
            return "ℹ️  No routing data yet. Use the router first!"

        # Parse telemetry
        events = []
        with open(log_path) as f:
            for line in f:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

        if not events:
            return "ℹ️  No routing data yet."

        # Calculate stats
        route_decisions = [
            e for e in events if e.get("event_type") == "route_decision"
        ]
        total_routes = len(route_decisions)

        if total_routes == 0:
            return "ℹ️  No routing decisions recorded yet."

        methods = {}
        triads = {}
        total_confidence = 0
        total_latency = 0

        for event in route_decisions:
            method = event.get("method", "unknown")
            methods[method] = methods.get(method, 0) + 1

            triad = event.get("triad", "unknown")
            triads[triad] = triads.get(triad, 0) + 1

            total_confidence += event.get("confidence", 0)
            total_latency += event.get("latency_ms", 0)

        avg_confidence = total_confidence / total_routes
        avg_latency = total_latency / total_routes

        output = f"""
📊 Router Statistics
{'=' * 50}

Total Routes: {total_routes}

Method Breakdown:
"""
        for method, count in sorted(methods.items()):
            percentage = (count / total_routes) * 100
            output += f"  {method:12s}: {count:3d} ({percentage:.1f}%)\n"

        output += "\nTop Triads:\n"
        for triad, count in sorted(
            triads.items(), key=lambda x: x[1], reverse=True
        )[:3]:
            percentage = (count / total_routes) * 100
            output += f"  {triad:20s}: {count:3d} ({percentage:.1f}%)\n"

        output += f"""
Performance:
  Average Confidence: {avg_confidence:.0%}
  Average Latency: {avg_latency:.1f}ms

Log file: {log_path}
"""

        return output.strip()


def main():
    """Main entry point for CLI testing."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m triads.router.cli <command> [args...]")
        print("\nCommands:")
        print("  status")
        print("  switch <triad-name>")
        print("  reset")
        print("  training <on|off>")
        print("  stats")
        sys.exit(1)

    cli = RouterCLI()
    command = sys.argv[1]

    if command == "status":
        print(cli.status())
    elif command == "switch":
        if len(sys.argv) < 3:
            print("❌ Usage: switch <triad-name>")
            sys.exit(1)
        print(cli.switch_triad(sys.argv[2]))
    elif command == "reset":
        print(cli.reset())
    elif command == "training":
        if len(sys.argv) < 3:
            print("❌ Usage: training <on|off>")
            sys.exit(1)
        print(cli.training_mode(sys.argv[2]))
    elif command == "stats":
        print(cli.stats())
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
