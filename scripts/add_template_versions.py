#!/usr/bin/env python3
"""Add template_version to existing agent files.

This script adds the template_version field to agent frontmatter for upgrade tracking.
It's designed to be:
- Non-breaking: Doesn't remove any fields
- Idempotent: Safe to run multiple times
- Conservative: Only adds version if missing

Usage:
    python scripts/add_template_versions.py [--dry-run]

Options:
    --dry-run    Show what would be changed without modifying files
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

# Add src to path for imports
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / "src"))

from triads.templates.agent_templates import AGENT_TEMPLATE_VERSION


def parse_frontmatter(content: str) -> tuple[dict, str, str]:
    """Parse YAML frontmatter from agent file.

    Args:
        content: Full file content

    Returns:
        tuple: (frontmatter_dict, frontmatter_text, body_text)
    """
    # Match YAML frontmatter between --- markers
    pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
    match = re.match(pattern, content, re.DOTALL)

    if not match:
        raise ValueError("No YAML frontmatter found")

    frontmatter_text = match.group(1)
    body_text = match.group(2)

    # Parse frontmatter into dict
    frontmatter = {}
    for line in frontmatter_text.split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue

        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip()

    return frontmatter, frontmatter_text, body_text


def add_template_version(content: str, version: str) -> tuple[str, bool]:
    """Add template_version to agent frontmatter if missing.

    Args:
        content: Original file content
        version: Version string to add

    Returns:
        tuple: (new_content, was_modified)
    """
    try:
        frontmatter, frontmatter_text, body = parse_frontmatter(content)
    except ValueError as e:
        return content, False

    # Check if already has template_version
    if 'template_version' in frontmatter:
        return content, False

    # Build new frontmatter with template_version after role
    lines = frontmatter_text.split('\n')
    new_lines = []
    version_added = False

    for line in lines:
        new_lines.append(line)

        # Add template_version after role field
        if line.startswith('role:') and not version_added:
            new_lines.append(f'template_version: {version}')
            version_added = True

    # If role field not found, add at end
    if not version_added:
        new_lines.append(f'template_version: {version}')

    new_frontmatter = '\n'.join(new_lines)
    new_content = f"---\n{new_frontmatter}\n---\n{body}"

    return new_content, True


def migrate_agent_file(
    agent_path: Path, version: str, dry_run: bool = False
) -> tuple[bool, str]:
    """Add template_version to single agent file.

    Args:
        agent_path: Path to agent markdown file
        version: Version string to add
        dry_run: If True, don't modify file

    Returns:
        tuple: (was_modified, status_message)
    """
    try:
        content = agent_path.read_text()
    except Exception as e:
        return False, f"Error reading file: {e}"

    new_content, modified = add_template_version(content, version)

    if not modified:
        return False, "Already has template_version"

    if not dry_run:
        # Atomic write: temp file → rename
        temp_path = agent_path.with_suffix('.tmp')
        try:
            temp_path.write_text(new_content)
            temp_path.replace(agent_path)
        except Exception as e:
            if temp_path.exists():
                temp_path.unlink()
            return False, f"Error writing file: {e}"

    return True, f"Added template_version: {version}"


def migrate_all_agents(version: str, dry_run: bool = False) -> None:
    """Migrate all agent files in .claude/agents/.

    Args:
        version: Version string to add
        dry_run: If True, show changes without modifying files
    """
    agents_dir = Path(".claude/agents")

    if not agents_dir.exists():
        print("❌ .claude/agents/ directory not found")
        return

    # Find all .md files recursively
    agent_files = list(agents_dir.rglob("*.md"))

    if not agent_files:
        print("ℹ️  No agent files found")
        return

    print(f"🔍 Found {len(agent_files)} agent files\n")

    if dry_run:
        print("🔬 DRY RUN MODE - No files will be modified\n")

    stats = {
        "total": 0,
        "modified": 0,
        "skipped": 0,
        "errors": 0,
    }

    for agent_file in sorted(agent_files):
        stats["total"] += 1
        relative_path = agent_file.relative_to(agents_dir)

        modified, message = migrate_agent_file(agent_file, version, dry_run=dry_run)

        if modified:
            stats["modified"] += 1
            print(f"✓ {relative_path}: {message}")
        elif "Error" in message:
            stats["errors"] += 1
            print(f"✗ {relative_path}: {message}")
        else:
            stats["skipped"] += 1
            # Don't print skipped files to reduce noise

    # Summary
    print("\n" + "=" * 60)
    print("📊 MIGRATION SUMMARY")
    print("=" * 60)
    print(f"Total files: {stats['total']}")
    print(f"Modified: {stats['modified']}")
    print(f"Skipped (already has version): {stats['skipped']}")
    print(f"Errors: {stats['errors']}")

    if dry_run:
        print("\n🔬 DRY RUN COMPLETE - No files were modified")
        print("Run without --dry-run to apply changes")
    else:
        print("\n✅ MIGRATION COMPLETE")
        if stats['errors'] > 0:
            print(f"⚠️  {stats['errors']} files had errors (see above)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Add template_version to existing agent files"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show changes without modifying files"
    )
    parser.add_argument(
        "--version",
        default=AGENT_TEMPLATE_VERSION,
        help=f"Version to add (default: {AGENT_TEMPLATE_VERSION})"
    )

    args = parser.parse_args()

    migrate_all_agents(version=args.version, dry_run=args.dry_run)
