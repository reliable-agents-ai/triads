#!/usr/bin/env python3
"""Demonstration of Upgrade Orchestrator workflow.

This script demonstrates the complete upgrade process:
1. Scan agents to identify outdated versions
2. Review candidates needing upgrade
3. Show diff for user review
4. Create backup before modification
5. Apply upgrade atomically

Usage:
    # Dry-run (preview only)
    python examples/upgrade_orchestrator_demo.py --dry-run

    # Actually apply upgrades
    python examples/upgrade_orchestrator_demo.py
"""

import argparse
import sys
from pathlib import Path

# Add src to path
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / "src"))

from triads.upgrade import UpgradeOrchestrator


def demo_scan_workflow(dry_run: bool = True):
    """Demonstrate the complete scanning workflow.

    Args:
        dry_run: If True, don't modify any files
    """
    print("=" * 70)
    print("UPGRADE ORCHESTRATOR DEMONSTRATION")
    print("=" * 70)
    print()

    if dry_run:
        print("🔬 DRY-RUN MODE: No files will be modified")
        print()

    # Initialize orchestrator
    orchestrator = UpgradeOrchestrator(dry_run=dry_run)

    print(f"Latest template version: {orchestrator.latest_version}")
    print(f"Agents directory: {orchestrator.agents_dir}")
    print()

    # Step 1: Scan all agents
    print("-" * 70)
    print("STEP 1: Scanning all agents")
    print("-" * 70)
    print()

    candidates = orchestrator.scan_agents()

    print(f"Found {len(candidates)} agents:")
    print()

    # Group by upgrade status
    needs_upgrade = [c for c in candidates if c.needs_upgrade]
    up_to_date = [c for c in candidates if not c.needs_upgrade]

    print(f"✓ Up to date: {len(up_to_date)}")
    print(f"⚠️  Needs upgrade: {len(needs_upgrade)}")
    print()

    # Show agents needing upgrade
    if needs_upgrade:
        print("Agents needing upgrade:")
        for candidate in sorted(needs_upgrade, key=lambda c: (c.triad_name, c.agent_name)):
            print(f"  {candidate}")
        print()
    else:
        print("✓ All agents are up to date!")
        print()
        return

    # Step 2: Scan specific triad
    print("-" * 70)
    print("STEP 2: Scanning specific triad (implementation)")
    print("-" * 70)
    print()

    impl_candidates = orchestrator.scan_agents(triad_name="implementation")
    impl_needs_upgrade = [c for c in impl_candidates if c.needs_upgrade]

    print(f"Found {len(impl_candidates)} agents in implementation triad")
    print(f"Needs upgrade: {len(impl_needs_upgrade)}")
    print()

    for candidate in impl_needs_upgrade:
        print(f"  {candidate}")
    print()

    # Step 3: Demonstrate diff (using first candidate)
    if needs_upgrade:
        print("-" * 70)
        print("STEP 3: Showing diff for first candidate")
        print("-" * 70)
        print()

        candidate = needs_upgrade[0]
        print(f"Agent: {candidate.triad_name}/{candidate.agent_name}")
        print(f"Version: {candidate.current_version} → {candidate.latest_version}")
        print()

        # Read current content
        current_content = candidate.agent_path.read_text()

        # Create proposed content (just update version in frontmatter)
        proposed_content = current_content.replace(
            f"template_version: {candidate.current_version}",
            f"template_version: {candidate.latest_version}"
        )

        # Show diff
        diff = orchestrator.show_diff(
            current_content=current_content,
            proposed_content=proposed_content,
            agent_name=candidate.agent_name
        )

        print("Diff preview:")
        print(diff)
        print()

    # Step 4: Demonstrate backup
    print("-" * 70)
    print("STEP 4: Creating backup")
    print("-" * 70)
    print()

    if needs_upgrade:
        candidate = needs_upgrade[0]
        print(f"Creating backup for: {candidate.agent_name}")
        print()

        try:
            backup_path = orchestrator.backup_agent(candidate.agent_path)
            print(f"✓ Backup created: {backup_path}")
            print(f"  Location: {backup_path.relative_to(orchestrator.agents_dir)}")
            print()
        except Exception as e:
            print(f"✗ Backup failed: {e}")
            print()

    # Step 5: Apply upgrade (if not dry-run)
    print("-" * 70)
    print("STEP 5: Applying upgrade")
    print("-" * 70)
    print()

    if needs_upgrade:
        candidate = needs_upgrade[0]
        print(f"Upgrading: {candidate.triad_name}/{candidate.agent_name}")
        print()

        # Read and modify content
        current_content = candidate.agent_path.read_text()
        new_content = current_content.replace(
            f"template_version: {candidate.current_version}",
            f"template_version: {candidate.latest_version}"
        )

        # Apply upgrade
        success = orchestrator.apply_upgrade(candidate, new_content)

        if success:
            if dry_run:
                print("[DRY-RUN] Would have upgraded successfully")
            else:
                print("✓ Upgrade completed successfully")
                print()

                # Verify
                new_version = orchestrator._parse_template_version(candidate.agent_path)
                print(f"Verified new version: {new_version}")
        else:
            print("✗ Upgrade failed")
        print()

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print(f"Total agents scanned: {len(candidates)}")
    print(f"Agents up to date: {len(up_to_date)}")
    print(f"Agents needing upgrade: {len(needs_upgrade)}")
    print()

    if dry_run and needs_upgrade:
        print("🔬 DRY-RUN COMPLETE - No files were modified")
        print("Run without --dry-run to apply upgrades")
    elif needs_upgrade:
        print("✓ UPGRADES APPLIED")
        print()
        print("Note: This demo only upgraded one agent for demonstration.")
        print("In production, you would upgrade all candidates.")
    else:
        print("✓ All agents are up to date!")
    print()


def demo_security_features():
    """Demonstrate security features."""
    print("=" * 70)
    print("SECURITY FEATURES DEMONSTRATION")
    print("=" * 70)
    print()

    orchestrator = UpgradeOrchestrator(dry_run=True)

    # Test path traversal protection
    print("Testing path traversal protection:")
    print()

    dangerous_inputs = [
        "../../../etc/passwd",
        "../../secrets",
        "..\\..\\windows\\system32",
        "test/../../../root",
    ]

    for dangerous in dangerous_inputs:
        is_safe = orchestrator._is_safe_path_component(dangerous)
        status = "✗ REJECTED" if not is_safe else "⚠️  ALLOWED"
        print(f"  {status}: {dangerous}")
    print()

    # Test valid inputs
    print("Testing valid inputs:")
    print()

    valid_inputs = [
        "implementation",
        "design",
        "my-custom-triad",
    ]

    for valid in valid_inputs:
        is_safe = orchestrator._is_safe_path_component(valid)
        status = "✓ ALLOWED" if is_safe else "✗ REJECTED"
        print(f"  {status}: {valid}")
    print()


def demo_validation():
    """Demonstrate content validation."""
    print("=" * 70)
    print("CONTENT VALIDATION DEMONSTRATION")
    print("=" * 70)
    print()

    orchestrator = UpgradeOrchestrator(dry_run=True)

    # Valid content
    valid_content = """---
name: test-agent
triad: test
role: analyzer
template_version: 0.8.0
---
# Test Agent

Body content here.
"""

    is_valid = orchestrator._validate_agent_content(valid_content)
    print(f"Valid content: {'✓ PASS' if is_valid else '✗ FAIL'}")
    print()

    # Missing frontmatter
    invalid_no_frontmatter = "# Agent without frontmatter"
    is_valid = orchestrator._validate_agent_content(invalid_no_frontmatter)
    print(f"No frontmatter: {'✓ PASS' if is_valid else '✗ FAIL (expected)'}")
    print()

    # Missing required field
    invalid_missing_field = """---
name: test-agent
triad: test
---
# Missing role and template_version
"""
    is_valid = orchestrator._validate_agent_content(invalid_missing_field)
    print(f"Missing required fields: {'✓ PASS' if is_valid else '✗ FAIL (expected)'}")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Demonstrate Upgrade Orchestrator workflow"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without modifying files"
    )
    parser.add_argument(
        "--security-demo",
        action="store_true",
        help="Show security features demonstration"
    )
    parser.add_argument(
        "--validation-demo",
        action="store_true",
        help="Show validation demonstration"
    )

    args = parser.parse_args()

    if args.security_demo:
        demo_security_features()
    elif args.validation_demo:
        demo_validation()
    else:
        demo_scan_workflow(dry_run=args.dry_run)
