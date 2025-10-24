"""
Training mode for learning the routing system.

Provides confirmation prompts and graduation tracking for users
learning how the router works.
"""

from typing import Dict, Optional


class TrainingModeHandler:
    """
    Handles training mode suggestions and confirmations.

    Training mode helps users learn the routing system by:
    - Showing routing suggestions with reasoning
    - Requesting confirmation before routing
    - Tracking confirmations toward graduation
    - Suggesting graduation after threshold reached
    """

    def __init__(self, enabled: bool = False, graduation_threshold: int = 50):
        """
        Initialize training mode handler.

        Args:
            enabled: Whether training mode is currently enabled
            graduation_threshold: Number of confirmations before suggesting graduation
        """
        self.enabled = enabled
        self.graduation_threshold = graduation_threshold

    def should_request_confirmation(self, routing_result: Dict) -> bool:
        """
        Check if we should ask for confirmation in training mode.

        Only request confirmation for automated routing decisions
        (semantic, LLM). Don't confirm:
        - Grace period continuations (not routing decisions)
        - Cancellations (already aborted)
        - Manual selections (already confirmed by user)

        Args:
            routing_result: Dictionary from TriadRouter.route()

        Returns:
            True if should request confirmation, False otherwise
        """
        if not self.enabled:
            return False

        # Don't confirm grace period continuations or cancellations
        if routing_result["method"] in ["grace_period", "cancelled"]:
            return False

        # Don't confirm manual selections (already confirmed)
        if routing_result["method"] == "manual":
            return False

        return True

    def request_confirmation(self, routing_result: Dict) -> str:
        """
        Show suggestion and request confirmation.

        Displays routing suggestion with reasoning and asks user to:
        - Confirm (y/yes)
        - Cancel (n/no/c/cancel)
        - Request manual selection (m/manual)

        Args:
            routing_result: Dictionary from TriadRouter.route()

        Returns:
            "confirmed" - User confirmed the suggestion
            "cancelled" - User cancelled routing
            "manual" - User wants manual selection
        """
        triad = routing_result["triad"]
        confidence = routing_result["confidence"]
        method = routing_result["method"]
        reasoning = routing_result.get("reasoning", "")

        print(f"\n{'=' * 70}")
        print("🎓 Training Mode - Routing Suggestion")
        print(f"{'=' * 70}\n")
        print(f"I suggest routing to: {triad}")
        print(f"Confidence: {confidence:.0%}")
        print(f"Method: {method}")
        if reasoning:
            print(f"Reasoning: {reasoning}")
        print()

        while True:
            response = input("Proceed? [y/n/manual]: ").strip().lower()

            if response in ["y", "yes"]:
                return "confirmed"
            elif response in ["n", "no", "c", "cancel"]:
                return "cancelled"
            elif response in ["m", "manual"]:
                return "manual"
            else:
                print("❌ Invalid input. Please enter y, n, or manual")

    def increment_confirmations(self, confirmations: int) -> int:
        """
        Increment confirmation count.

        Args:
            confirmations: Current confirmation count

        Returns:
            Updated confirmation count
        """
        return confirmations + 1

    def check_graduation(self, confirmations: int) -> Optional[str]:
        """
        Check if user has reached graduation threshold.

        Returns message if graduated, None otherwise.

        Args:
            confirmations: Current confirmation count

        Returns:
            Graduation message if threshold reached, None otherwise
        """
        if confirmations >= self.graduation_threshold:
            return f"""
🎉 Congratulations! You've confirmed {confirmations} routing suggestions.

You're now familiar with the routing system. Consider disabling training mode:
    /router-training off

Or keep training mode enabled if you prefer explicit confirmations.
"""

        # Show progress at milestones
        milestones = [10, 25, 40]
        if confirmations in milestones:
            remaining = self.graduation_threshold - confirmations
            return f"""
✅ Training Progress: {confirmations}/{self.graduation_threshold} confirmations

{remaining} more confirmations until graduation.
"""

        return None

    def format_training_status(self, confirmations: int) -> str:
        """
        Format current training status.

        Args:
            confirmations: Current confirmation count

        Returns:
            Formatted status string
        """
        if not self.enabled:
            return "Training Mode: 🔴 Disabled"

        progress = f"{confirmations}/{self.graduation_threshold}"
        percentage = (confirmations / self.graduation_threshold) * 100

        if confirmations >= self.graduation_threshold:
            return f"""
Training Mode: 🟢 Enabled (Graduated!)
Confirmations: {progress} ({percentage:.0%})

You've reached the graduation threshold. Consider disabling training mode.
"""

        return f"""
Training Mode: 🟢 Enabled
Confirmations: {progress} ({percentage:.0%})
"""

    def toggle(self, new_state: bool) -> str:
        """
        Toggle training mode on or off.

        Args:
            new_state: True to enable, False to disable

        Returns:
            Status message
        """
        self.enabled = new_state

        if new_state:
            return """
🎓 Training mode ENABLED

The router will now:
- Show routing suggestions
- Request confirmation before routing
- Help you learn the system

After 50 confirmations, you'll be prompted to graduate.

Disable with: /router-training off
"""
        else:
            return """
✅ Training mode DISABLED

The router will now route automatically based on confidence.

Re-enable with: /router-training on
"""
