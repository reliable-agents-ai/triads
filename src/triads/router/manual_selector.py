"""
Manual triad selection UI for when automated routing fails.

Provides interactive prompt for user to manually select triad when
LLM disambiguation fails or confidence is too low.
"""

from typing import List, Optional, Tuple


class ManualSelector:
    """Interactive prompt for manual triad selection."""

    def select_triad(
        self,
        prompt: str,
        candidates: List[Tuple[str, float]],
        reason: str = "disambiguation_needed",
    ) -> Tuple[Optional[str], str]:
        """
        Show interactive prompt for manual triad selection.

        Args:
            prompt: User's original prompt
            candidates: Top 3 (triad_name, confidence) tuples
            reason: Why manual selection is needed (for telemetry)

        Returns:
            Tuple of (selected_triad, reason_code)
            - selected_triad: Name of selected triad or None if cancelled
            - reason_code: "user_override", "llm_failure", "low_confidence", "user_cancelled"
        """
        print("\n" + "=" * 70)
        print("🤔 Manual Triad Selection Required")
        print("=" * 70)
        print(
            f"\nYour prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}"
        )
        print(f"\nReason: {self._format_reason(reason)}\n")

        print("Please select a triad:\n")
        for i, (triad, confidence) in enumerate(candidates, 1):
            print(f"  {i}. {triad:20s} (confidence: {confidence:.0%})")
            print(f"     {self._get_triad_description(triad)}")
            print()

        print("  c. Cancel routing (stay in current triad)")
        print()

        while True:
            choice = input("Select option [1-3 or c]: ").strip().lower()

            if choice == "c":
                return (None, "user_cancelled")

            try:
                choice_num = int(choice)
                if 1 <= choice_num <= len(candidates):
                    selected_triad = candidates[choice_num - 1][0]
                    return (selected_triad, reason)
                else:
                    print(
                        f"❌ Invalid choice. Please enter 1-{len(candidates)} or c"
                    )
            except ValueError:
                print(
                    f"❌ Invalid input. Please enter 1-{len(candidates)} or c"
                )

    def _format_reason(self, reason: str) -> str:
        """Format reason code into human-readable message."""
        reason_map = {
            "llm_failure": "LLM disambiguation failed (timeout or API error)",
            "low_confidence": "Semantic routing confidence too low",
            "disambiguation_needed": "Multiple triads are similar matches",
            "user_requested": "Manual selection requested",
        }
        return reason_map.get(reason, reason)

    def _get_triad_description(self, triad: str) -> str:
        """Get human-readable description of triad."""
        descriptions = {
            "idea-validation": "Research ideas, validate with community, assess priority",
            "design": "Create ADRs, design solutions, plan architecture",
            "implementation": "Write production code, implement features",
            "garden-tending": "Refactor code, improve quality, reduce debt",
            "deployment": "Create releases, update docs, deploy",
        }
        return descriptions.get(triad, "No description available")
