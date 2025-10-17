#!/usr/bin/env python
"""Generate workflow.json from existing .claude/agents/ directory.

This script scans the .claude/agents/ directory for triad subdirectories and
generates a workflow.json schema file. The schema defines the workflow structure
that enables workflow enforcement features.

Usage:
    python scripts/generate_workflow_schema.py
    python scripts/generate_workflow_schema.py --output custom/path/workflow.json
    python scripts/generate_workflow_schema.py --workflow-name my-workflow

The generated schema includes:
- All discovered triads in alphabetical order
- Inferred triad types (research, planning, execution, quality, release)
- Default enforcement mode (recommended)
- Sequential progression rules
"""

import argparse
import json
import sys
from pathlib import Path

# Add src to path to import triads modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from triads.workflow_enforcement.triad_discovery import TriadDiscovery


def infer_triad_type(triad_id: str) -> str:
    """Infer triad type from ID using keyword matching.

    Args:
        triad_id: Triad identifier (directory name)

    Returns:
        Triad type: research, planning, execution, quality, or release

    Examples:
        >>> infer_triad_type("idea-validation")
        'research'
        >>> infer_triad_type("design")
        'planning'
        >>> infer_triad_type("implementation")
        'execution'
        >>> infer_triad_type("garden-tending")
        'quality'
        >>> infer_triad_type("deployment")
        'release'
    """
    triad_lower = triad_id.lower()

    # Quality keywords (check first because it overlaps with research)
    quality_keywords = [
        "test", "review", "quality", "tending", "garden", "refactor",
        "cleanup", "polish", "qa", "audit"
    ]
    if any(kw in triad_lower for kw in quality_keywords):
        return "quality"

    # Research keywords
    research_keywords = [
        "research", "discovery", "analysis", "investigate", "explore",
        "validation", "rfp-analysis", "requirements", "study"
    ]
    if any(kw in triad_lower for kw in research_keywords):
        return "research"

    # Planning keywords
    planning_keywords = [
        "design", "plan", "strategy", "architect", "proposal", "rfp-strategy",
        "roadmap", "spec", "blueprint"
    ]
    if any(kw in triad_lower for kw in planning_keywords):
        return "planning"

    # Execution keywords
    execution_keywords = [
        "implement", "build", "create", "develop", "write", "coding",
        "construction", "generation", "execution", "drafting", "rfp-creation"
    ]
    if any(kw in triad_lower for kw in execution_keywords):
        return "execution"

    # Release keywords
    release_keywords = [
        "deploy", "release", "publish", "ship", "delivery", "launch",
        "submission", "finalize"
    ]
    if any(kw in triad_lower for kw in release_keywords):
        return "release"

    # Default to execution for unknown
    return "execution"


def generate_triad_name(triad_id: str) -> str:
    """Generate human-readable triad name from ID.

    Args:
        triad_id: Triad identifier (directory name)

    Returns:
        Human-readable name

    Examples:
        >>> generate_triad_name("idea-validation")
        'Idea Validation'
        >>> generate_triad_name("rfp-analysis")
        'RFP Analysis'
    """
    # Replace hyphens with spaces and title case
    name = triad_id.replace("-", " ").replace("_", " ").title()

    # Special cases for acronyms
    acronyms = ["Rfp", "Api", "Ui", "Ux", "Ai", "Ml", "Oauth", "Jwt"]
    for acronym in acronyms:
        if acronym in name:
            name = name.replace(acronym, acronym.upper())

    return name


def generate_workflow_schema(
    output_path: Path | None = None,
    workflow_name: str | None = None,
    agents_dir: Path | None = None
) -> dict:
    """Generate workflow schema from discovered triads.

    Args:
        output_path: Path to write workflow.json (default: .claude/workflow.json)
        workflow_name: Workflow name (default: inferred from current directory)
        agents_dir: Path to agents directory (default: .claude/agents)

    Returns:
        Generated schema dictionary

    Raises:
        SystemExit: If no triads found or generation fails
    """
    # Set defaults
    if output_path is None:
        output_path = Path(".claude/workflow.json")

    if agents_dir is None:
        agents_dir = Path(".claude/agents")

    if workflow_name is None:
        # Infer from current directory
        workflow_name = Path.cwd().name or "custom-workflow"

    # Discover triads
    discovery = TriadDiscovery(base_path=str(agents_dir))

    try:
        triads = discovery.discover_triads()
    except Exception as e:
        print(f"Error: Failed to discover triads: {e}", file=sys.stderr)
        sys.exit(1)

    if not triads:
        print(f"Error: No triads found in {agents_dir}", file=sys.stderr)
        print(f"\nExpected structure:", file=sys.stderr)
        print(f"  .claude/agents/", file=sys.stderr)
        print(f"    triad-1/", file=sys.stderr)
        print(f"      agent1.md", file=sys.stderr)
        print(f"      agent2.md", file=sys.stderr)
        print(f"    triad-2/", file=sys.stderr)
        print(f"      agent1.md", file=sys.stderr)
        sys.exit(1)

    # Generate schema
    schema = {
        "workflow_name": workflow_name,
        "version": "1.0.0",
        "enforcement": {
            "mode": "recommended",
            "per_triad_overrides": {}
        },
        "triads": [],
        "workflow_rules": [
            {
                "rule_type": "sequential_progression",
                "description": "Triads should be completed in order",
                "track_deviations": True
            }
        ]
    }

    # Add triads
    for triad in triads:
        triad_type = infer_triad_type(triad.id)
        triad_name = generate_triad_name(triad.id)

        schema["triads"].append({
            "id": triad.id,
            "name": triad_name,
            "type": triad_type,
            "required": True
        })

    return schema


def save_schema(schema: dict, output_path: Path) -> None:
    """Save schema to file with proper formatting.

    Args:
        schema: Schema dictionary
        output_path: Path to write file
    """
    # Ensure parent directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write with pretty formatting
    with open(output_path, "w") as f:
        json.dump(schema, f, indent=2)
        f.write("\n")  # Add trailing newline


def print_summary(schema: dict, output_path: Path) -> None:
    """Print generation summary.

    Args:
        schema: Generated schema
        output_path: Path where schema was written
    """
    print(f"✓ Generated workflow schema: {output_path}")
    print(f"  Workflow: {schema['workflow_name']}")
    print(f"  Triads: {len(schema['triads'])}")
    print(f"  Enforcement mode: {schema['enforcement']['mode']}")
    print()

    # List triads with types
    print("Triads discovered:")
    for triad in schema["triads"]:
        print(f"  • {triad['id']:30s} [{triad['type']}]")
    print()

    # Customization suggestions
    print("Customization suggestions:")
    print("  • Update workflow_name if needed")
    print("  • Change enforcement mode (strict/recommended/optional)")
    print("  • Adjust triad types if inference was incorrect:")
    print("    - research:  discovery, analysis, investigation")
    print("    - planning:  design, strategy, architecture")
    print("    - execution: implementation, creation, development")
    print("    - quality:   testing, review, refactoring")
    print("    - release:   deployment, publishing, delivery")
    print("  • Mark optional triads with 'required': false")
    print("  • Add per-triad enforcement overrides")
    print("  • Add conditional requirements (gate triads)")
    print()
    print(f"Edit: {output_path}")


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Generate workflow.json from .claude/agents/ directory",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Generate workflow.json in default location:
    python scripts/generate_workflow_schema.py

  Specify custom output path:
    python scripts/generate_workflow_schema.py --output custom/workflow.json

  Specify workflow name:
    python scripts/generate_workflow_schema.py --workflow-name rfp-writing

  Specify custom agents directory:
    python scripts/generate_workflow_schema.py --agents-dir path/to/agents
        """
    )

    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path(".claude/workflow.json"),
        help="Output path for workflow.json (default: .claude/workflow.json)"
    )

    parser.add_argument(
        "--workflow-name", "-n",
        type=str,
        help="Workflow name (default: inferred from current directory)"
    )

    parser.add_argument(
        "--agents-dir", "-a",
        type=Path,
        default=Path(".claude/agents"),
        help="Path to agents directory (default: .claude/agents)"
    )

    parser.add_argument(
        "--print-only", "-p",
        action="store_true",
        help="Print schema to stdout instead of writing file"
    )

    args = parser.parse_args()

    # Generate schema
    try:
        schema = generate_workflow_schema(
            output_path=args.output if not args.print_only else None,
            workflow_name=args.workflow_name,
            agents_dir=args.agents_dir
        )
    except SystemExit:
        raise
    except Exception as e:
        print(f"Error: Failed to generate schema: {e}", file=sys.stderr)
        sys.exit(1)

    # Output
    if args.print_only:
        print(json.dumps(schema, indent=2))
    else:
        save_schema(schema, args.output)
        print_summary(schema, args.output)


if __name__ == "__main__":
    main()
