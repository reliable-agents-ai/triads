"""LLM-based routing system using Claude Code headless mode.

This module implements intelligent routing to replace brittle keyword matching.
Uses Claude Code CLI in headless mode for LLM-based intent detection.

Constitutional Requirements:
- Evidence-Based: Tests prove behavior
- User Authority: Implements user-directed Claude Code headless approach
- Security: Tool restrictions via --allowedTools ""

Reference: ADR-001 (.claude/graphs/adr_001_claude_code_headless_20251028.md)
"""

import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any

# Configure logging
logger = logging.getLogger(__name__)

# Confidence thresholds per ADR-001
FALLBACK_KEYWORD_MATCH_CONFIDENCE = 0.60  # Keyword match fallback
FALLBACK_DEFAULT_CONFIDENCE = 0.50  # No match, using first available
CONFIDENCE_THRESHOLD_DEFAULT = 0.70  # Minimum to proceed

# System prompt for routing agent
ROUTING_SYSTEM_PROMPT = """You are a routing agent for a workflow system.

Analyze user input and determine which brief skill should handle it.

Output ONLY valid JSON (no markdown):
{
  "brief_skill": "skill-name",
  "confidence": 0.95,
  "reasoning": "why this matches"
}

Confidence scale:
- 0.90-1.00: Clear match
- 0.70-0.89: Probable match
- 0.00-0.69: Unclear, ask user

Be objective. No hyperbole."""


def route_to_brief_skill(
    user_input: str,
    skills_dir: Path,
    confidence_threshold: float = CONFIDENCE_THRESHOLD_DEFAULT,
    timeout: int = 10
) -> Dict[str, Any]:
    """Route user input to brief skill using Claude Code headless.

    Args:
        user_input: User's request (e.g., "investigate why command isn't there")
        skills_dir: Directory containing brief skills
        confidence_threshold: Minimum confidence to proceed (0.0-1.0)
        timeout: Max seconds for LLM call (default: 10)

    Returns:
        {
            "brief_skill": "bug-brief",
            "confidence": 0.95,
            "reasoning": "User is investigating missing functionality...",
            "cost_usd": 0.003,
            "duration_ms": 1234
        }

    Reference: ADR-001 lines 98-167
    """
    # Step 1: Discover brief skills
    brief_skills = _discover_brief_skills(skills_dir)

    if not brief_skills:
        raise ValueError(f"No brief skills found in {skills_dir}")

    # Step 2: Build routing prompt
    user_message = _build_routing_user_message(user_input, brief_skills)

    # Step 3: Call Claude Code headless
    try:
        routing_decision = _call_claude_headless(
            ROUTING_SYSTEM_PROMPT,
            user_message,
            timeout
        )
        return routing_decision

    except subprocess.TimeoutExpired:
        # Fallback to keyword matching
        logger.warning(
            f"LLM routing timed out after {timeout}s, using keyword fallback"
        )
        return _keyword_fallback(user_input, brief_skills)

    except Exception as e:
        # Log error and fallback
        logger.error(f"LLM routing failed: {e}")
        return _keyword_fallback(user_input, brief_skills)


def _parse_frontmatter(content: str) -> Dict[str, str]:
    """Parse YAML frontmatter from markdown content.

    Args:
        content: Markdown file content with frontmatter

    Returns:
        Dictionary of frontmatter key-value pairs, empty if no frontmatter

    Example:
        >>> content = '''---
        ... name: bug-brief
        ... description: Bug investigation
        ... ---
        ... # Content'''
        >>> _parse_frontmatter(content)
        {'name': 'bug-brief', 'description': 'Bug investigation'}
    """
    if not content.startswith("---"):
        return {}

    # Extract frontmatter between --- markers
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}

    frontmatter_text = parts[1].strip()

    # Parse YAML-like frontmatter (simple key: value format)
    metadata = {}
    for line in frontmatter_text.split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip()

    return metadata


def _discover_brief_skills(skills_dir: Path) -> Dict[str, Dict[str, str]]:
    """Discover brief skills from filesystem.

    Glob for *-brief.md files and parse frontmatter.

    Args:
        skills_dir: Directory containing brief skills

    Returns:
        {
            "bug-brief": {
                "name": "bug-brief",
                "description": "Transform bug report...",
                "purpose": "Bug investigation",
                ...
            },
            ...
        }

    Reference: ADR-001 lines 122-123
    """
    brief_skills = {}

    if not skills_dir.exists():
        logger.warning(f"Skills directory does not exist: {skills_dir}")
        return brief_skills

    # Find all *-brief.md files
    for skill_file in skills_dir.glob("*-brief.md"):
        try:
            content = skill_file.read_text()
            metadata = _parse_frontmatter(content)

            # Only include if category is "brief"
            if metadata.get("category") == "brief":
                skill_name = metadata.get("name", skill_file.stem)
                brief_skills[skill_name] = metadata

        except Exception as e:
            logger.warning(f"Failed to parse {skill_file}: {e}")

    return brief_skills


def _build_routing_user_message(
    user_input: str,
    brief_skills: Dict[str, Dict[str, str]]
) -> str:
    """Build user message for routing agent.

    Args:
        user_input: User's request
        brief_skills: Available brief skills with metadata

    Returns:
        Formatted message for Claude

    Reference: ADR-001 lines 214-229
    """
    # Simplify brief skills for prompt (only name and description)
    simplified_skills = {
        name: {
            "name": info.get("name", name),
            "description": info.get("description", "No description")
        }
        for name, info in brief_skills.items()
    }

    skills_json = json.dumps(simplified_skills, indent=2)

    return f"""USER REQUEST:
{user_input}

AVAILABLE BRIEF SKILLS:
{skills_json}

Analyze the user's intent and return routing decision as JSON."""


def _call_claude_headless(
    system_prompt: str,
    user_message: str,
    timeout: int
) -> Dict[str, Any]:
    """Call Claude Code headless via subprocess.

    Args:
        system_prompt: System instructions for routing
        user_message: User message with available skills
        timeout: Max seconds for call

    Returns:
        {
            "brief_skill": "bug-brief",
            "confidence": 0.95,
            "reasoning": "...",
            "cost_usd": 0.003,
            "duration_ms": 1234
        }

    Raises:
        subprocess.TimeoutExpired: If call exceeds timeout
        RuntimeError: If Claude returns error response

    Reference: ADR-001 lines 130-167
    """
    # Execute Claude Code headless
    result = subprocess.run(
        [
            "claude",
            "-p", user_message,
            "--append-system-prompt", system_prompt,
            "--output-format", "json",
            "--allowedTools", "",  # Security: no tools during routing
        ],
        capture_output=True,
        text=True,
        timeout=timeout,
        check=True
    )

    # Parse JSON response
    response = json.loads(result.stdout)

    # Check for error
    if response.get("is_error"):
        raise RuntimeError(f"Claude Code error: {response.get('result')}")

    # Extract routing decision from response["result"]
    routing_decision = json.loads(response["result"])

    # Add metadata from Claude response
    routing_decision["cost_usd"] = response.get("total_cost_usd", 0.0)
    routing_decision["duration_ms"] = response.get("duration_ms", 0)

    return routing_decision


def _keyword_fallback(
    user_input: str,
    brief_skills: Dict[str, Dict[str, str]]
) -> Dict[str, Any]:
    """Fallback to simple keyword matching if LLM fails.

    Args:
        user_input: User's request
        brief_skills: Available brief skills

    Returns:
        Routing decision with lower confidence

    Reference: ADR-001 lines 243-261
    """
    user_input_lower = user_input.lower()

    # Try to match skill name in user input
    for skill_name, skill_info in brief_skills.items():
        # Extract base name (remove "-brief" suffix)
        base_name = skill_name.replace("-brief", "")

        if base_name in user_input_lower:
            return {
                "brief_skill": skill_name,
                "confidence": FALLBACK_KEYWORD_MATCH_CONFIDENCE,
                "reasoning": "Fallback keyword matching",
                "cost_usd": 0.0,
                "duration_ms": 0
            }

    # Default: return first available skill
    first_skill = list(brief_skills.keys())[0]
    return {
        "brief_skill": first_skill,
        "confidence": FALLBACK_DEFAULT_CONFIDENCE,
        "reasoning": "No match found, using first available skill",
        "cost_usd": 0.0,
        "duration_ms": 0
    }
