#!/usr/bin/env python3
"""
Demonstration of Agent Upgrade System.

This script demonstrates the complete upgrade workflow:
1. Scan agents to find outdated versions
2. Generate upgraded content with template merge
3. Show diff for review
4. Apply upgrade with safety gates
5. Verify success

Run from repository root:
    python examples/upgrade_agent_demo.py
"""

import sys
from pathlib import Path

# Add src to path
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / "src"))

from triads.upgrade import UpgradeOrchestrator


def demo_scan_agents():
    """Demo 1: Scan agents and identify outdated versions."""
    print("\n" + "="*60)
    print("DEMO 1: Scan Agents")
    print("="*60)

    try:
        orchestrator = UpgradeOrchestrator()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("\nMake sure you're running from the repository root.")
        return

    print(f"\nLatest template version: {orchestrator.latest_version}")
    print("\nScanning all agents...")

    candidates = orchestrator.scan_agents()

    print(f"\nFound {len(candidates)} agents total")

    outdated = [c for c in candidates if c.needs_upgrade]
    print(f"Found {len(outdated)} agents needing upgrade")

    if outdated:
        print("\nAgents needing upgrade:")
        for candidate in outdated:
            print(f"  - {candidate}")
    else:
        print("\n✅ All agents are up to date!")

    return orchestrator, candidates


def demo_template_merge(orchestrator, candidates):
    """Demo 2: Template merge and content generation."""
    print("\n" + "="*60)
    print("DEMO 2: Template Merge")
    print("="*60)

    outdated = [c for c in candidates if c.needs_upgrade]

    if not outdated:
        print("\nNo agents need upgrade - skipping merge demo")
        return None, None

    # Pick first outdated agent
    candidate = outdated[0]

    print(f"\nGenerating upgraded content for: {candidate.agent_name}")
    print(f"  Current version: {candidate.current_version}")
    print(f"  Target version: {candidate.latest_version}")

    try:
        upgraded_content = orchestrator.generate_upgraded_content(candidate)

        print("\n✅ Successfully generated upgraded content")

        # Show what sections were added
        if "🧠 Knowledge Graph Protocol" in upgraded_content:
            print("  ✓ Added Knowledge Graph Protocol section")

        # Verify version updated
        if f"template_version: {orchestrator.latest_version}" in upgraded_content:
            print(f"  ✓ Updated version to {orchestrator.latest_version}")

        # Show diff
        print("\n" + "-"*60)
        print("DIFF PREVIEW (first 30 lines):")
        print("-"*60)

        current_content = candidate.agent_path.read_text()
        diff = orchestrator.show_diff(current_content, upgraded_content, candidate.agent_name)

        # Show first 30 lines of diff
        diff_lines = diff.split('\n')
        for line in diff_lines[:30]:
            print(line)

        if len(diff_lines) > 30:
            print(f"\n... ({len(diff_lines) - 30} more lines)")

        return candidate, upgraded_content

    except Exception as e:
        print(f"\n❌ Error generating upgrade: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def demo_safety_features(orchestrator, candidate, upgraded_content):
    """Demo 3: Safety features (backup, validation, atomic writes)."""
    print("\n" + "="*60)
    print("DEMO 3: Safety Features")
    print("="*60)

    if not candidate or not upgraded_content:
        print("\nNo upgrade content available - skipping safety demo")
        return

    print("\n1. BACKUP CREATION")
    print("-"*60)

    try:
        backup_path = orchestrator.backup_agent(candidate.agent_path)
        print(f"✓ Backup created: {backup_path.name}")
        print(f"  Location: {backup_path}")
        print(f"  Size: {backup_path.stat().st_size} bytes")
    except Exception as e:
        print(f"✗ Backup failed: {e}")

    print("\n2. CONTENT VALIDATION")
    print("-"*60)

    is_valid = orchestrator._validate_agent_content(upgraded_content)
    if is_valid:
        print("✓ Content validation passed")
        print("  - Has valid frontmatter")
        print("  - Has required fields (name, triad, role, template_version)")
    else:
        print("✗ Content validation failed")

    print("\n3. DRY-RUN MODE (Preview without applying)")
    print("-"*60)

    # Enable dry-run
    original_dry_run = orchestrator.dry_run
    orchestrator.dry_run = True

    print("Dry-run enabled: No files will be modified")
    success = orchestrator.apply_upgrade(candidate, upgraded_content)

    if success:
        print("✓ Dry-run successful - upgrade would work")

    # Verify file unchanged
    current_content = candidate.agent_path.read_text()
    if f"template_version: {candidate.current_version}" in current_content:
        print("✓ Verified: Original file unchanged")

    # Restore dry-run setting
    orchestrator.dry_run = original_dry_run


def demo_full_workflow():
    """Demo 4: Complete upgrade workflow (interactive)."""
    print("\n" + "="*60)
    print("DEMO 4: Full Upgrade Workflow")
    print("="*60)

    print("\nThis demo shows the complete interactive upgrade workflow.")
    print("For actual upgrades, use: /upgrade-agents --all")

    print("\nWorkflow steps:")
    print("  1. Scan for outdated agents")
    print("  2. Generate upgraded content (template merge)")
    print("  3. Show diff for review")
    print("  4. Get user confirmation")
    print("  5. Create backup")
    print("  6. Validate content")
    print("  7. Apply upgrade (atomic write)")
    print("  8. Report success")

    print("\nSafety features:")
    print("  ✓ Automatic backups before changes")
    print("  ✓ Content validation gates")
    print("  ✓ Atomic file writes (no partial updates)")
    print("  ✓ Dry-run mode for preview")
    print("  ✓ Path traversal protection")


def main():
    """Run all demos."""
    print("\n" + "="*60)
    print("AGENT UPGRADE SYSTEM - DEMONSTRATION")
    print("="*60)

    # Demo 1: Scan agents
    result = demo_scan_agents()
    if not result:
        return

    orchestrator, candidates = result

    # Demo 2: Template merge
    candidate, upgraded_content = demo_template_merge(orchestrator, candidates)

    # Demo 3: Safety features
    demo_safety_features(orchestrator, candidate, upgraded_content)

    # Demo 4: Full workflow overview
    demo_full_workflow()

    # Final summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    print("\nThe upgrade system provides:")
    print("  1. Automatic detection of outdated agents")
    print("  2. Smart template merging (preserves customizations)")
    print("  3. Multiple safety gates (backup, validation, atomic writes)")
    print("  4. Interactive workflow with user confirmation")
    print("  5. Dry-run mode for safe preview")

    print("\nUsage:")
    print("  /upgrade-agents --all              # Upgrade all agents")
    print("  /upgrade-agents --triad design     # Upgrade specific triad")
    print("  /upgrade-agents senior-developer   # Upgrade specific agent")
    print("  /upgrade-agents --all --dry-run    # Preview changes")

    print("\nDocumentation:")
    print("  docs/AGENT_UPGRADES.md")

    print("\n" + "="*60)


if __name__ == '__main__':
    main()
