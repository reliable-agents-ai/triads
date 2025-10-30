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

# System prompt for universal context discovery (v0.13.0)
DISCOVERY_SYSTEM_PROMPT = """You are an intelligent context discovery agent.

Your role is to analyze ALL user messages (questions AND work requests) and provide
comprehensive context enrichment for the supervisor agent.

Analyze the user's message and discover:
1. Intent classification (qa, work, or ambiguous)
2. Confidence scores for each interpretation
3. Recommended action (answer_directly, invoke_skill, or clarify)
4. Available brief skills and coordination skills
5. Workflow entry points (triad → agent)
6. Alternative interpretations
7. Complete reasoning chain

Output ONLY valid JSON (no markdown):
{
  "intent_type": "qa" | "work" | "ambiguous",
  "confidence": 0.92,
  "reasoning": "detailed analysis",
  "recommended_action": "invoke_skill" | "answer_directly" | "clarify",
  "brief_skill": "feature-brief" (if work),
  "available_brief_skills": [
    {"name": "feature-brief", "confidence": 0.85, "description": "..."},
    {"name": "bug-brief", "confidence": 0.10, "description": "..."}
  ],
  "available_coordination_skills": [
    {"name": "coordinate-feature", "description": "..."}
  ],
  "entry_triad": "idea-validation",
  "entry_agent": "research-analyst",
  "workflow_sequence": ["idea-validation", "design", "implementation", "garden-tending", "deployment"],
  "available_agents": {
    "idea-validation": ["research-analyst", "community-researcher", "validation-synthesizer"],
    "design": ["solution-architect", "design-bridge"]
  },
  "alternative_interpretations": [
    {"type": "qa", "confidence": 0.40, "rationale": "Could be asking for explanation"},
    {"type": "work", "confidence": 0.60, "rationale": "Could be requesting implementation"}
  ],
  "qa_confidence": 0.25,
  "work_confidence": 0.75,
  "work_type": "feature" | "bug" | "refactor" | null
}

Confidence scale:
- 0.90-1.00: Very clear intent
- 0.70-0.89: Probable intent
- 0.50-0.69: Ambiguous, lean toward interpretation
- 0.00-0.49: Highly ambiguous, clarification needed

Be objective. No hyperbole. Show complete reasoning."""


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


# ============================================================================
# Universal Context Discovery (v0.13.0)
# ============================================================================


def discover_context(
    user_input: str,
    skills_dir: Path,
    timeout: int = 10
) -> Dict[str, Any]:
    """Universal context discovery for ALL user messages (v0.13.0).

    This function replaces the Q&A fast path. ALL messages (questions AND work
    requests) are routed through LLM analysis to provide comprehensive context
    enrichment for the supervisor.

    Design Philosophy:
    - Trade performance for intelligence
    - Universal routing (no shortcuts)
    - Comprehensive context (skills, agents, triads, workflows)
    - Supervisor autonomy (supervisor decides based on context)

    Args:
        user_input: User's message (question or work request)
        skills_dir: Directory containing skills
        timeout: Max seconds for LLM call (default: 10)

    Returns:
        {
            "intent_type": "qa" | "work" | "ambiguous",
            "confidence": 0.92,
            "reasoning": "detailed analysis",
            "recommended_action": "invoke_skill" | "answer_directly" | "clarify",
            "brief_skill": "feature-brief" (if work),
            "available_brief_skills": [...],
            "available_coordination_skills": [...],
            "entry_triad": "idea-validation",
            "entry_agent": "research-analyst",
            "workflow_sequence": [...],
            "available_agents": {...},
            "alternative_interpretations": [...],
            "qa_confidence": 0.25,
            "work_confidence": 0.75,
            "work_type": "feature" | "bug" | "refactor" | null,
            "cost_usd": 0.0042,
            "duration_ms": 1847
        }

    Raises:
        ValueError: If skills directory is invalid

    Reference: v0.13.0 Universal Context Enrichment Architecture
    """
    # Step 1: Discover all skills
    brief_skills = _discover_brief_skills(skills_dir)
    coordination_skills = _discover_coordination_skills(skills_dir)

    if not brief_skills:
        raise ValueError(f"No brief skills found in {skills_dir}")

    # Step 2: Load workflow configuration
    workflow_config = _load_workflow_config()

    # Step 3: Build discovery prompt
    user_message = _build_discovery_prompt(
        user_input,
        brief_skills,
        coordination_skills,
        workflow_config
    )

    # Step 4: Call Claude Code headless
    try:
        discovery_result = _call_claude_headless(
            DISCOVERY_SYSTEM_PROMPT,
            user_message,
            timeout
        )
        return discovery_result

    except subprocess.TimeoutExpired:
        # Fallback with minimal context
        logger.warning(
            f"LLM discovery timed out after {timeout}s, using fallback"
        )
        return _fallback_discovery(user_input, brief_skills, coordination_skills)

    except Exception as e:
        # Log error and fallback
        logger.error(f"LLM discovery failed: {e}")
        return _fallback_discovery(user_input, brief_skills, coordination_skills)


def _discover_coordination_skills(skills_dir: Path) -> Dict[str, Dict[str, str]]:
    """Discover coordination skills from filesystem.

    Glob for coordinate-*.md files and parse frontmatter.

    Args:
        skills_dir: Directory containing skills

    Returns:
        {
            "coordinate-feature": {
                "name": "coordinate-feature",
                "description": "Orchestrate feature development...",
                "purpose": "Feature coordination",
                ...
            },
            ...
        }
    """
    coordination_skills = {}

    if not skills_dir.exists():
        logger.warning(f"Skills directory does not exist: {skills_dir}")
        return coordination_skills

    # Find all coordinate-*.md files
    for skill_file in skills_dir.glob("coordinate-*.md"):
        try:
            content = skill_file.read_text()
            metadata = _parse_frontmatter(content)

            # Only include if category is "coordination"
            if metadata.get("category") == "coordination":
                skill_name = metadata.get("name", skill_file.stem)
                coordination_skills[skill_name] = metadata

        except Exception as e:
            logger.warning(f"Failed to parse {skill_file}: {e}")

    return coordination_skills


def _load_workflow_config() -> Dict[str, Any]:
    """Load workflow configuration dynamically from .claude/settings.json.

    Returns:
        {
            "workflow_sequence": ["idea-validation", "design", ...],
            "triads": {
                "idea-validation": {
                    "entry_agent": "research-analyst",
                    "agents": ["research-analyst", "community-researcher", ...]
                },
                ...
            }
        }
        Returns empty dict if loading fails.
    """
    try:
        # Find .claude/settings.json
        settings_path = Path(".claude/settings.json")

        if not settings_path.exists():
            logger.warning(f"Workflow config not found: {settings_path}")
            return _fallback_workflow_config()

        # Load settings
        with open(settings_path, 'r') as f:
            settings = json.load(f)

        # Extract triad system configuration
        triad_system = settings.get('triad_system', {})
        workflow = triad_system.get('workflow', {})
        triads_config = triad_system.get('triads', {})

        # Build workflow sequence
        workflow_sequence = workflow.get('sequence', [])

        # Build triads dictionary with agents
        triads_dict = {}
        for triad_name, triad_def in triads_config.items():
            agents_list = triad_def.get('agents', [])
            entry_agent = agents_list[0] if agents_list else "unknown"

            triads_dict[triad_name] = {
                "entry_agent": entry_agent,
                "agents": agents_list
            }

        return {
            "workflow_sequence": workflow_sequence,
            "triads": triads_dict
        }

    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        logger.error(f"Failed to load workflow config: {e}")
        return _fallback_workflow_config()


def _fallback_workflow_config() -> Dict[str, Any]:
    """Fallback workflow configuration if settings.json unavailable.

    Returns minimal configuration to prevent failures.
    """
    logger.warning("Using fallback workflow configuration")
    return {
        "workflow_sequence": [
            "idea-validation",
            "design",
            "implementation",
            "garden-tending",
            "deployment"
        ],
        "triads": {
            "idea-validation": {
                "entry_agent": "research-analyst",
                "agents": [
                    "research-analyst",
                    "community-researcher",
                    "validation-synthesizer"
                ]
            },
            "design": {
                "entry_agent": "solution-architect",
                "agents": ["solution-architect", "design-bridge"]
            },
            "implementation": {
                "entry_agent": "senior-developer",
                "agents": ["senior-developer", "test-engineer"]
            },
            "garden-tending": {
                "entry_agent": "cultivator",
                "agents": ["cultivator", "pruner", "gardener-bridge"]
            },
            "deployment": {
                "entry_agent": "release-manager",
                "agents": ["release-manager", "documentation-updater"]
            }
        }
    }


def _build_discovery_prompt(
    user_input: str,
    brief_skills: Dict[str, Dict[str, str]],
    coordination_skills: Dict[str, Dict[str, str]],
    workflow_config: Dict[str, Any]
) -> str:
    """Build user message for context discovery.

    Args:
        user_input: User's message
        brief_skills: Available brief skills
        coordination_skills: Available coordination skills
        workflow_config: Workflow configuration

    Returns:
        Formatted message for Claude
    """
    # Simplify skills for prompt
    simplified_brief = {
        name: {
            "name": info.get("name", name),
            "description": info.get("description", "No description")
        }
        for name, info in brief_skills.items()
    }

    simplified_coordination = {
        name: {
            "name": info.get("name", name),
            "description": info.get("description", "No description")
        }
        for name, info in coordination_skills.items()
    }

    brief_json = json.dumps(simplified_brief, indent=2)
    coordination_json = json.dumps(simplified_coordination, indent=2)
    workflow_json = json.dumps(workflow_config, indent=2)

    return f"""USER MESSAGE:
{user_input}

AVAILABLE BRIEF SKILLS:
{brief_json}

AVAILABLE COORDINATION SKILLS:
{coordination_json}

WORKFLOW CONFIGURATION:
{workflow_json}

Analyze the user's intent, classify as qa/work/ambiguous, and provide comprehensive
context enrichment including recommended action, available skills, workflow entry
points, and alternative interpretations.

Return JSON with complete analysis."""


def _fallback_discovery(
    user_input: str,
    brief_skills: Dict[str, Dict[str, str]],
    coordination_skills: Dict[str, Dict[str, str]]
) -> Dict[str, Any]:
    """Fallback discovery if LLM fails.

    Uses simple keyword matching to provide minimal context.

    Args:
        user_input: User's message
        brief_skills: Available brief skills
        coordination_skills: Available coordination skills

    Returns:
        Discovery result with lower confidence
    """
    user_input_lower = user_input.lower()

    # Simple heuristic: check for question words
    question_words = ['what', 'how', 'why', 'when', 'where', 'who', 'which']
    is_question = any(user_input_lower.startswith(word) for word in question_words)

    # Keyword matching for work type
    work_type = None
    if 'bug' in user_input_lower or 'fix' in user_input_lower:
        work_type = "bug"
    elif 'refactor' in user_input_lower or 'clean' in user_input_lower:
        work_type = "refactor"
    else:
        work_type = "feature"

    # Determine brief skill
    brief_skill = f"{work_type}-brief" if work_type else "feature-brief"

    # Determine intent
    if is_question:
        intent_type = "qa"
        qa_confidence = 0.60
        work_confidence = 0.40
        recommended_action = "answer_directly"
    else:
        intent_type = "work"
        qa_confidence = 0.40
        work_confidence = 0.60
        recommended_action = "invoke_skill"

    return {
        "intent_type": intent_type,
        "confidence": 0.60,
        "reasoning": "Fallback keyword matching (LLM unavailable)",
        "recommended_action": recommended_action,
        "brief_skill": brief_skill,
        "available_brief_skills": [
            {"name": name, "confidence": 0.33, "description": info.get("description", "")}
            for name, info in brief_skills.items()
        ],
        "available_coordination_skills": [
            {"name": name, "description": info.get("description", "")}
            for name, info in coordination_skills.items()
        ],
        "entry_triad": "idea-validation",
        "entry_agent": "research-analyst",
        "workflow_sequence": [
            "idea-validation", "design", "implementation",
            "garden-tending", "deployment"
        ],
        "available_agents": {},
        "alternative_interpretations": [],
        "qa_confidence": qa_confidence,
        "work_confidence": work_confidence,
        "work_type": work_type,
        "cost_usd": 0.0,
        "duration_ms": 0
    }
