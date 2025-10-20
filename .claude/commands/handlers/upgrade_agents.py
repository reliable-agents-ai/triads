#!/usr/bin/env python3
"""Handler for /upgrade-agents command.

This script orchestrates agent upgrades from the command line.
It's invoked by Claude Code when the user runs /upgrade-agents.
"""

import sys
from pathlib import Path

# Add src to path for imports
repo_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(repo_root / "src"))

from triads.upgrade import UpgradeOrchestrator


def parse_args(args: list[str]) -> dict:
    """Parse command-line arguments.

    Args:
        args: Command-line arguments (excluding script name)

    Returns:
        Dict with parsed options
    """
    parsed = {
        'dry_run': False,
        'force': False,
        'agent_names': [],
        'triad_name': None,
        'all': False,
    }

    i = 0
    while i < len(args):
        arg = args[i]

        if arg == '--dry-run':
            parsed['dry_run'] = True
        elif arg == '--force':
            parsed['force'] = True
        elif arg == '--all':
            parsed['all'] = True
        elif arg == '--triad':
            # Next arg is triad name
            i += 1
            if i < len(args):
                parsed['triad_name'] = args[i]
            else:
                print("Error: --triad requires a triad name")
                sys.exit(1)
        elif not arg.startswith('--'):
            # Positional argument - agent name
            parsed['agent_names'].append(arg)
        else:
            print(f"Unknown option: {arg}")
            sys.exit(1)

        i += 1

    return parsed


def show_usage():
    """Display usage information."""
    print("Usage: /upgrade-agents [options] [agent-names...]")
    print()
    print("Options:")
    print("  --all              Upgrade all agents (with confirmation)")
    print("  --dry-run          Preview changes without applying")
    print("  --force            Skip confirmation prompts")
    print("  --triad <name>     Upgrade all agents in specific triad")
    print()
    print("Examples:")
    print("  /upgrade-agents senior-developer")
    print("  /upgrade-agents --triad implementation")
    print("  /upgrade-agents --all --dry-run")
    print()


def main():
    """Execute upgrade command."""
    # Parse arguments
    args = parse_args(sys.argv[1:])

    # Validate usage
    if not args['all'] and not args['agent_names'] and not args['triad_name']:
        show_usage()
        sys.exit(1)

    # Create orchestrator
    try:
        orchestrator = UpgradeOrchestrator(
            dry_run=args['dry_run'],
            force=args['force']
        )
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("\nMake sure you're running this from the repository root.")
        sys.exit(1)

    # Determine what to upgrade
    agent_names = args['agent_names'] if args['agent_names'] else None
    triad_name = args['triad_name']

    # Run upgrade workflow
    try:
        stats = orchestrator.upgrade_all(
            agent_names=agent_names,
            triad_name=triad_name
        )

        # Exit with error code if any failed
        if stats['failed'] > 0:
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
