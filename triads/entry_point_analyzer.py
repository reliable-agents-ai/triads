"""
Entry Point Analyzer - Domain-agnostic workflow entry point analysis.

Analyzes settings.json workflow structure to determine routing mappings
between work types and triad entry points.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime, UTC

# Domain-agnostic work type patterns
WORK_TYPE_PATTERNS = {
    "bug": {
        "keywords": ["fix", "bug", "error", "crash", "broken", "issue", "defect"],
        "purpose_patterns": ["fix", "debug", "resolve errors", "troubleshoot"],
        "priority": 1,
        "description": "Bug fixes, error resolution, crash fixes"
    },
    "feature": {
        "keywords": ["feature", "add", "implement", "new", "enhancement", "capability"],
        "purpose_patterns": ["research", "validate", "ideation", "new features"],
        "priority": 2,
        "description": "New features, enhancements, capabilities"
    },
    "refactor": {
        "keywords": ["refactor", "improve", "clean", "optimize", "restructure"],
        "purpose_patterns": ["improve quality", "refactor", "cleanup", "debt"],
        "priority": 3,
        "description": "Code improvements, refactoring, tech debt"
    },
    "release": {
        "keywords": ["release", "deploy", "publish", "version", "launch"],
        "purpose_patterns": ["release", "deploy", "publish", "distribution"],
        "priority": 4,
        "description": "Releases, deployments, versioning"
    },
    "documentation": {
        "keywords": ["document", "docs", "readme", "guide", "explain"],
        "purpose_patterns": ["documentation", "guide", "explain", "document"],
        "priority": 5,
        "description": "Documentation updates, guides, explanations"
    }
}


def match_work_type_to_triad(triad_purpose: str) -> List[Dict[str, Any]]:
    """
    Match triad purpose to work types based on keyword overlap.

    Args:
        triad_purpose: The purpose string from triad configuration

    Returns:
        List of matches with work_type and confidence score
    """
    purpose_lower = triad_purpose.lower()
    matches = []

    for work_type, config in WORK_TYPE_PATTERNS.items():
        match_score = 0.0

        # Check purpose patterns (higher weight)
        for pattern in config["purpose_patterns"]:
            if pattern in purpose_lower:
                match_score += 1.0

        # Check keywords (lower weight)
        for keyword in config["keywords"]:
            if keyword in purpose_lower:
                match_score += 0.5

        if match_score > 0:
            # Calculate confidence (0.70-0.95 range)
            confidence = min(0.95, 0.70 + (match_score * 0.10))
            matches.append({
                "work_type": work_type,
                "confidence": round(confidence, 2),
                "match_score": match_score
            })

    return sorted(matches, key=lambda x: x["confidence"], reverse=True)


def find_brief_skill(work_type: str, skills_dir: Path) -> str:
    """
    Find corresponding brief skill for work type.

    Args:
        work_type: The work type (bug, feature, refactor, etc.)
        skills_dir: Directory containing brief skills

    Returns:
        Brief skill name (e.g., "bug-brief")
    """
    brief_skill_path = skills_dir / f"{work_type}-brief.md"

    if brief_skill_path.exists():
        return f"{work_type}-brief"

    # Fallback to generic brief
    return "generic-brief"


def generate_routing_table(
    settings_path: Path,
    skills_dir: Path,
    output_path: Path
) -> Dict[str, Any]:
    """
    Generate routing_decision_table.yaml from settings.json.

    Args:
        settings_path: Path to settings.json
        skills_dir: Directory containing brief skills
        output_path: Path for output YAML file

    Returns:
        Generated routing table dictionary
    """
    # Load settings
    settings = json.loads(settings_path.read_text())
    triad_system = settings.get("triad_system", {})
    triads = triad_system.get("triads", {})
    domain = triad_system.get("workflow", {}).get("domain", "unknown")

    # Initialize routing decisions
    routing_decisions = {}

    # Analyze each triad
    for triad_name, triad_config in triads.items():
        purpose = triad_config.get("purpose", "")
        agents = triad_config.get("agents", [])

        if not agents:
            continue

        entry_agent = agents[0]
        matches = match_work_type_to_triad(purpose)

        # Assign to highest confidence work type
        for match in matches:
            work_type = match["work_type"]
            confidence = match["confidence"]

            # Only assign if higher confidence than existing
            if work_type not in routing_decisions or confidence > routing_decisions[work_type]["confidence"]:
                brief_skill = find_brief_skill(work_type, skills_dir)

                routing_decisions[work_type] = {
                    "description": WORK_TYPE_PATTERNS[work_type]["description"],
                    "keywords": WORK_TYPE_PATTERNS[work_type]["keywords"],
                    "target_triad": triad_name,
                    "entry_agent": entry_agent,
                    "brief_skill": brief_skill,
                    "priority": WORK_TYPE_PATTERNS[work_type]["priority"],
                    "confidence": confidence,
                    "examples": []
                }

    # Find first triad with agents for fallback
    fallback_triad = None
    fallback_agent = None
    for triad_name, triad_config in triads.items():
        agents = triad_config.get("agents", [])
        if agents:
            fallback_triad = triad_name
            fallback_agent = agents[0]
            break

    # Build complete routing table
    routing_table = {
        "version": "1.0.0",
        "domain": domain,
        "generated_at": datetime.now(UTC).isoformat(),
        "routing_decisions": routing_decisions,
        "fallback": {
            "target_triad": fallback_triad or "idea-validation",
            "entry_agent": fallback_agent or "research-analyst",
            "rationale": "First triad in workflow can handle general requests"
        },
        "ambiguity_resolution": {
            "strategy": "priority_score",
            "confidence_threshold": 0.70,
            "tiebreaker": "ask_user"
        }
    }

    # Write to file
    output_path.write_text(yaml.dump(routing_table, sort_keys=False, default_flow_style=False))

    return routing_table


if __name__ == "__main__":
    # Example usage
    import sys

    settings_path = Path(".claude/settings.json")
    skills_dir = Path(".claude/skills/software-development")
    output_path = Path(".claude/routing_decision_table.yaml")

    if not settings_path.exists():
        print(f"Error: {settings_path} not found", file=sys.stderr)
        sys.exit(1)

    routing_table = generate_routing_table(settings_path, skills_dir, output_path)
    print(f"Generated routing table with {len(routing_table['routing_decisions'])} work types")
    print(f"Output: {output_path}")
