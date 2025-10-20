#!/usr/bin/env python3
"""Example: Complete upgrade workflow using the orchestrator.

This example shows how Phase 3 (CLI) will use the orchestrator
to implement the complete upgrade workflow.

Workflow:
1. Scan for outdated agents
2. Show summary to user
3. For each agent:
   a. Show diff
   b. Request confirmation
   c. Create backup
   d. Apply upgrade
   e. Verify result
"""

import sys
from pathlib import Path

# Add src to path
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / "src"))

from triads.upgrade import UpgradeOrchestrator


def upgrade_workflow_example():
    """Example showing how CLI will orchestrate upgrades."""

    print("=" * 70)
    print("UPGRADE WORKFLOW EXAMPLE")
    print("=" * 70)
    print()

    # Step 1: Initialize orchestrator
    print("Step 1: Initialize orchestrator")
    orchestrator = UpgradeOrchestrator(dry_run=False)
    print(f"  Latest version: {orchestrator.latest_version}")
    print()

    # Step 2: Scan for outdated agents
    print("Step 2: Scan for outdated agents")
    candidates = orchestrator.scan_agents()
    needs_upgrade = [c for c in candidates if c.needs_upgrade]

    print(f"  Found {len(candidates)} agents")
    print(f"  Needs upgrade: {len(needs_upgrade)}")
    print()

    if not needs_upgrade:
        print("✓ All agents are up to date!")
        return

    # Step 3: Show summary
    print("Step 3: Show upgrade candidates")
    print()
    for candidate in needs_upgrade:
        print(f"  {candidate}")
    print()

    # Step 4: Confirm batch upgrade
    print("Step 4: Confirm upgrade")
    response = input(f"Upgrade {len(needs_upgrade)} agents? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled.")
        return
    print()

    # Step 5: Process each agent
    print("Step 5: Process upgrades")
    print()

    successes = 0
    failures = 0

    for i, candidate in enumerate(needs_upgrade, 1):
        print(f"[{i}/{len(needs_upgrade)}] {candidate.agent_name}")

        # Read current content
        current_content = candidate.agent_path.read_text()

        # Generate new content (simple version - replace version number)
        # In Phase 3, this will preserve customizations
        new_content = current_content.replace(
            f"template_version: {candidate.current_version}",
            f"template_version: {candidate.latest_version}"
        )

        # Show diff (abbreviated for demo)
        diff = orchestrator.show_diff(
            current_content=current_content,
            proposed_content=new_content,
            agent_name=candidate.agent_name
        )

        diff_lines = diff.split('\n')
        if len(diff_lines) > 10:
            # Show first 5 and last 5 lines
            print("  Diff preview (truncated):")
            for line in diff_lines[:5]:
                print(f"    {line}")
            print(f"    ... ({len(diff_lines) - 10} more lines) ...")
            for line in diff_lines[-5:]:
                print(f"    {line}")
        else:
            print("  Diff:")
            for line in diff_lines:
                print(f"    {line}")
        print()

        # Apply upgrade
        success = orchestrator.apply_upgrade(candidate, new_content)

        if success:
            successes += 1
            # Verify
            new_version = orchestrator._parse_template_version(candidate.agent_path)
            print(f"  ✓ Upgraded successfully (now {new_version})")
        else:
            failures += 1
            print(f"  ✗ Upgrade failed")
        print()

    # Summary
    print("=" * 70)
    print("UPGRADE COMPLETE")
    print("=" * 70)
    print()
    print(f"Successes: {successes}")
    print(f"Failures: {failures}")
    print()

    if failures > 0:
        print("⚠️  Some upgrades failed. Check backups in .claude/agents/backups/")
    else:
        print("✓ All upgrades completed successfully!")
    print()


def filter_by_triad_example():
    """Example showing triad-specific upgrades."""

    print("=" * 70)
    print("TRIAD-SPECIFIC UPGRADE EXAMPLE")
    print("=" * 70)
    print()

    orchestrator = UpgradeOrchestrator(dry_run=True)

    # Scan specific triad
    print("Scanning implementation triad only:")
    impl_candidates = orchestrator.scan_agents(triad_name="implementation")

    print(f"  Found {len(impl_candidates)} agents in implementation triad")
    print()

    for candidate in impl_candidates:
        status = "⚠️  NEEDS UPGRADE" if candidate.needs_upgrade else "✓ UP TO DATE"
        print(f"  {candidate.agent_name:20} {candidate.current_version:10} {status}")
    print()


def filter_by_agent_example():
    """Example showing agent-specific upgrades."""

    print("=" * 70)
    print("AGENT-SPECIFIC UPGRADE EXAMPLE")
    print("=" * 70)
    print()

    orchestrator = UpgradeOrchestrator(dry_run=True)

    # Scan specific agents
    agent_names = ["senior-developer", "test-engineer"]
    print(f"Scanning specific agents: {', '.join(agent_names)}")

    candidates = orchestrator.scan_agents(agent_names=agent_names)

    print(f"  Found {len(candidates)} matching agents")
    print()

    for candidate in candidates:
        print(f"  {candidate}")
    print()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Example upgrade workflow using orchestrator"
    )
    parser.add_argument(
        "--filter-triad",
        action="store_true",
        help="Show triad filtering example"
    )
    parser.add_argument(
        "--filter-agent",
        action="store_true",
        help="Show agent filtering example"
    )

    args = parser.parse_args()

    if args.filter_triad:
        filter_by_triad_example()
    elif args.filter_agent:
        filter_by_agent_example()
    else:
        upgrade_workflow_example()
