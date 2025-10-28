"""
Entry Point Analyzer - Domain-agnostic workflow entry point analysis.

Analyzes settings.json workflow structure to determine routing mappings
between work types and triad entry points using LLM-based intent detection.

Uses Claude Code headless mode to replace brittle keyword matching.
Reference: ADR-001 (.claude/graphs/adr_001_claude_code_headless_20251028.md)
"""

import json
import logging
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, UTC
from triads.llm_routing import route_to_brief_skill

# Configure logging
logger = logging.getLogger(__name__)


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


def _extract_work_type_from_skill(brief_skill: str) -> str:
    """Extract work type from brief skill name.

    Args:
        brief_skill: Brief skill name (e.g., "bug-brief")

    Returns:
        Work type (e.g., "bug")
    """
    return brief_skill.replace("-brief", "")


def _create_routing_decision(
    triad_name: str,
    entry_agent: str,
    brief_skill: str,
    confidence: float,
    purpose: str,
    reasoning: str,
    priority: int
) -> Dict[str, Any]:
    """Create a routing decision entry.

    Args:
        triad_name: Name of the triad
        entry_agent: First agent in the triad
        brief_skill: Brief skill to use
        confidence: Routing confidence score
        purpose: Triad purpose description
        reasoning: LLM reasoning for this routing
        priority: Priority ranking

    Returns:
        Routing decision dictionary
    """
    return {
        "description": purpose,
        "keywords": [],  # No keywords in LLM-based routing
        "target_triad": triad_name,
        "entry_agent": entry_agent,
        "brief_skill": brief_skill,
        "priority": priority,
        "confidence": confidence,
        "examples": [],
        "llm_reasoning": reasoning
    }


def _find_fallback_triad(triads: Dict[str, Any]) -> tuple[Optional[str], Optional[str]]:
    """Find first triad with agents for fallback routing.

    Args:
        triads: Dictionary of triad configurations

    Returns:
        Tuple of (fallback_triad_name, fallback_agent_name)
    """
    for triad_name, triad_config in triads.items():
        agents = triad_config.get("agents", [])
        if agents:
            return triad_name, agents[0]
    return None, None


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

    # Analyze each triad using LLM routing
    for triad_name, triad_config in triads.items():
        purpose = triad_config.get("purpose", "")
        agents = triad_config.get("agents", [])

        if not agents:
            continue

        entry_agent = agents[0]

        # Use LLM to route triad purpose to brief skill
        try:
            routing_result = route_to_brief_skill(
                user_input=purpose,
                skills_dir=skills_dir,
                timeout=5  # Longer timeout for routing table generation
            )

            brief_skill = routing_result["brief_skill"]
            confidence = routing_result["confidence"]
            reasoning = routing_result.get("reasoning", "")

            # Extract work type from brief skill name
            work_type = _extract_work_type_from_skill(brief_skill)

            # Only assign if higher confidence than existing
            if work_type not in routing_decisions or confidence > routing_decisions[work_type]["confidence"]:
                routing_decisions[work_type] = _create_routing_decision(
                    triad_name=triad_name,
                    entry_agent=entry_agent,
                    brief_skill=brief_skill,
                    confidence=confidence,
                    purpose=purpose,
                    reasoning=reasoning,
                    priority=len(routing_decisions) + 1
                )
                logger.info(
                    f"Mapped '{work_type}' to triad '{triad_name}' "
                    f"(confidence: {confidence:.2f})"
                )

        except Exception as e:
            # Log error and skip triad if LLM routing fails
            logger.warning(f"LLM routing failed for triad '{triad_name}': {e}")
            continue

    # Find first triad with agents for fallback
    fallback_triad, fallback_agent = _find_fallback_triad(triads)

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
