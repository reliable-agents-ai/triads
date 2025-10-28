"""
Coordination Skill Generator - Domain-agnostic coordination skill creation.

Generates coordination skills based on routing_decision_table.yaml
and brief skill discovery.

Phase 3: Now supports LLM-based discovery without routing_decision_table.yaml
"""

import yaml
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime, UTC
from triads.llm_routing import _parse_frontmatter

# Constants for Phase 3: LLM-based discovery defaults
DEFAULT_TARGET_TRIAD = "implementation"
DEFAULT_ENTRY_AGENT = "senior-developer"
DEFAULT_CONFIDENCE = 0.85
DEFAULT_DOMAIN = "software-development"

# Coordination skill template with complete 4-phase workflow
COORDINATION_SKILL_TEMPLATE = """---
name: coordinate-{work_type}
description: Coordinate {work_type} workflow - transforms user request into brief, routes to appropriate triad, monitors execution. Keywords - {keyword_list}
category: coordination
domain: {domain}
allowed_tools: ["Task", "Read", "Grep"]
---

# {work_type_title} Coordination Skill

**Purpose**: Orchestrate complete {work_type} workflow from user request → brief → routing → triad execution.

---

## Skill Procedure

### Phase 1: CREATE BRIEF

**Objective**: Transform user request into structured {work_type_title}Brief.

**Action**:
Use Task tool to invoke brief skill:

```
Task(
  subagent_type="skill:{brief_skill}",
  description="Create {work_type} brief",
  prompt=\"\"\"
  {{{{user_message}}}}
  \"\"\"
)
```

**Capture**: Brief node ID from skill output (format: `{work_type}_brief_*`)

**If Brief Fails**: Ask user for more details about the {work_type}.

---

### Phase 2: ROUTE TO TRIAD

**Objective**: Determine target triad and entry agent from routing table.

**Action**:
Read routing decision table:

```
Read(file_path=".claude/routing_decision_table.yaml")
```

**Extract**:
- `target_triad`: {target_triad}
- `entry_agent`: {entry_agent}
- `confidence`: {confidence}

**If Ambiguous** (confidence < 0.70): Ask user to clarify work type.

---

### Phase 3: INVOKE TRIAD

**Objective**: Hand off to {target_triad} triad via {entry_agent} entry agent.

**Action**:
Use Task tool to invoke entry agent:

```
Task(
  subagent_type="agent:{target_triad}:{entry_agent}",
  description="{work_type_title} execution",
  prompt=\"\"\"
  HANDOFF FROM COORDINATION

  Work Type: {work_type}
  Brief Node: {{{{brief_node_id}}}}
  Original Request: {{{{user_message}}}}

  Please proceed with {work_type} workflow as specified in brief.
  Triad: {target_triad}
  Entry Point: {entry_agent}

  Constitutional Requirements:
  - Follow TDD cycle (RED-GREEN-REFACTOR) if code changes
  - Maintain ≥80% test coverage
  - Document all assumptions
  - Triple-verify before completion
  \"\"\"
)
```

**Monitor**: Track triad execution through knowledge graph updates.

**If Invocation Fails**: Provide fallback options or escalate to user.

---

### Phase 4: MONITOR EXECUTION

**Objective**: Track triad progress and report completion.

**Actions**:
1. Monitor knowledge graph for triad progress nodes
2. Check for completion signal from triad
3. Verify output confidence ≥ 0.85
4. Report status to user

**If Low Confidence** (< 0.85): Explain uncertainty and suggest follow-up actions.

---

## Error Handling

### Phase 1 Errors (Brief Creation)
- **Symptom**: Brief skill fails or returns error
- **Response**: Ask user for more details about the {work_type}
- **Example**: "Could you provide more details about [what's unclear]?"

### Phase 2 Errors (Routing Ambiguity)
- **Symptom**: Multiple work types match with similar confidence
- **Response**: Ask user to clarify work type
- **Example**: "This could be a {work_type} or [other type]. Which is it?"

### Phase 3 Errors (Triad Invocation)
- **Symptom**: Entry agent not available or triad fails to start
- **Response**: Provide fallback options
- **Example**: "Could not route to {target_triad}. Try [fallback] instead?"

### Phase 4 Errors (Low Confidence)
- **Symptom**: Result confidence < 0.85
- **Response**: Explain uncertainty to user
- **Example**: "Completed with 75% confidence due to [reason]. Review recommended."

---

## Examples

### Example 1: Software Development
**User Input**: "Login is broken, users can't sign in"

**Phase 1**: Creates BugBrief with issue details
**Phase 2**: Routes to implementation triad (confidence: 0.95)
**Phase 3**: Invokes senior-developer agent
**Phase 4**: Monitors fix implementation and testing

### Example 2: Research Domain
**User Input**: "Study correlation between X and Y"

**Phase 1**: Creates ResearchBrief with study parameters
**Phase 2**: Routes to research triad (confidence: 0.90)
**Phase 3**: Invokes research-lead agent
**Phase 4**: Monitors literature review and analysis

---

## Constitutional Compliance

This coordination skill follows constitutional principles:
- **Evidence-Based**: All routing decisions backed by confidence scores
- **Transparency**: Complete workflow visibility through 4 phases
- **Uncertainty Escalation**: Escalates when confidence < 0.70
- **Multi-Method Verification**: Routing table + brief validation + triad execution

---

*Generated by coordination-skill-generator.py v1.0.0*
*Domain: {domain}*
*Generated: {generated_at}*
"""


def generate_coordination_skill(
    work_type: str,
    config: Dict[str, Any],
    domain: str,
    output_dir: Path
) -> Path:
    """
    Generate coordination skill file for work type.

    Args:
        work_type: The work type (bug, feature, etc.)
        config: Routing configuration from routing_decision_table.yaml
        domain: Domain name (software-development, research, etc.)
        output_dir: Output directory for skill file

    Returns:
        Path to generated skill file
    """
    # Format keyword list
    keyword_list = ", ".join(config["keywords"])

    # Format work type title
    work_type_title = work_type.replace("-", " ").title()

    # Generate skill content using template
    content = COORDINATION_SKILL_TEMPLATE.format(
        work_type=work_type,
        work_type_title=work_type_title,
        keyword_list=keyword_list,
        domain=domain,
        target_triad=config["target_triad"],
        entry_agent=config["entry_agent"],
        brief_skill=config["brief_skill"],
        confidence=config["confidence"],
        generated_at=datetime.now(UTC).isoformat()
    )

    # Write to file
    output_path = output_dir / f"coordinate-{work_type}.md"
    output_path.write_text(content)

    return output_path


def discover_brief_skills(skills_dir: Path) -> List[str]:
    """
    Discover brief skills in skills directory.

    Args:
        skills_dir: Directory containing brief skills

    Returns:
        List of brief skill names (without -brief suffix)
    """
    brief_skills = []

    for skill_file in skills_dir.glob("*-brief.md"):
        work_type = skill_file.stem.replace("-brief", "")
        brief_skills.append(work_type)

    return brief_skills


def generate_all_coordination_skills(
    routing_table_path: Path,
    output_dir: Path
) -> List[Path]:
    """
    Generate coordination skills for all work types in routing table.

    Args:
        routing_table_path: Path to routing_decision_table.yaml
        output_dir: Output directory for skill files

    Returns:
        List of generated skill file paths
    """
    # Load routing table
    routing_table = yaml.safe_load(routing_table_path.read_text())
    domain = routing_table["domain"]
    routing_decisions = routing_table["routing_decisions"]

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate coordination skill for each work type
    generated_skills = []

    for work_type, config in routing_decisions.items():
        skill_path = generate_coordination_skill(
            work_type=work_type,
            config=config,
            domain=domain,
            output_dir=output_dir
        )
        generated_skills.append(skill_path)
        print(f"✅ Generated coordination skill: {skill_path.name}")

    return generated_skills


def generate_all_coordination_skills_from_discovery(
    skills_dir: Path,
    output_dir: Path,
    default_domain: str = DEFAULT_DOMAIN
) -> List[Path]:
    """
    Generate coordination skills for all discovered brief skills.

    Uses LLM routing discovery to find brief skills dynamically from filesystem
    instead of reading from routing_decision_table.yaml.

    Args:
        skills_dir: Directory containing brief skills (searches subdirectories)
        output_dir: Output directory for coordination skill files
        default_domain: Default domain if not specified in brief skill metadata

    Returns:
        List of generated skill file paths

    Example:
        >>> skills_dir = Path(".claude/skills")
        >>> output_dir = Path(".claude/skills/software-development")
        >>> generate_all_coordination_skills_from_discovery(skills_dir, output_dir)
        [PosixPath('.claude/skills/software-development/coordinate-bug.md'), ...]
    """
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Discover brief skills from filesystem (searches recursively)
    brief_skills = _discover_brief_skills_recursive(skills_dir)

    if not brief_skills:
        print(f"⚠️  No brief skills found in {skills_dir}")
        return []

    print(f"🔍 Discovered {len(brief_skills)} brief skills:")
    for skill_name in brief_skills.keys():
        print(f"   - {skill_name}")

    # Generate coordination skill for each discovered brief skill
    generated_skills = []

    for skill_name, skill_metadata in brief_skills.items():
        # Extract work type from skill name (remove "-brief" suffix)
        work_type = skill_name.replace("-brief", "")

        # Extract domain from metadata
        domain = skill_metadata.get("domain", default_domain)

        # Extract keywords from description (simple approach)
        # Keywords are embedded in description after "Keywords -"
        description = skill_metadata.get("description", "")
        keywords = _extract_keywords_from_description(description)

        # For Phase 3, use default routing to implementation triad
        # This can be enhanced later with actual LLM routing
        config = {
            "keywords": keywords,
            "target_triad": DEFAULT_TARGET_TRIAD,
            "entry_agent": DEFAULT_ENTRY_AGENT,
            "brief_skill": skill_name,
            "confidence": DEFAULT_CONFIDENCE
        }

        # Generate coordination skill
        skill_path = generate_coordination_skill(
            work_type=work_type,
            config=config,
            domain=domain,
            output_dir=output_dir
        )
        generated_skills.append(skill_path)
        print(f"✅ Generated coordination skill: {skill_path.name}")

    return generated_skills


def _discover_brief_skills_recursive(skills_dir: Path) -> Dict[str, Dict[str, str]]:
    """
    Discover brief skills recursively from filesystem.

    Searches for *-brief.md files in skills_dir and all subdirectories.
    Parses frontmatter to extract metadata.

    Args:
        skills_dir: Root directory to search for brief skills

    Returns:
        Dictionary mapping skill names to metadata

    Example:
        >>> _discover_brief_skills_recursive(Path(".claude/skills"))
        {
            "bug-brief": {"name": "bug-brief", "description": "...", "category": "brief"},
            "feature-brief": {"name": "feature-brief", ...}
        }
    """
    brief_skills = {}

    if not skills_dir.exists():
        return brief_skills

    # Search recursively for *-brief.md files
    for skill_file in skills_dir.rglob("*-brief.md"):
        try:
            content = skill_file.read_text()
            metadata = _parse_frontmatter(content)

            # Only include if category is "brief"
            if metadata.get("category") == "brief":
                skill_name = metadata.get("name", skill_file.stem)
                brief_skills[skill_name] = metadata

        except Exception as e:
            print(f"⚠️  Failed to parse {skill_file}: {e}")

    return brief_skills


def _extract_keywords_from_description(description: str) -> List[str]:
    """
    Extract keywords from brief skill description.

    Brief skill descriptions contain keywords after "Keywords -" or "Keywords:".
    Example: "...discovers via keywords - bug, issue, error, crash..."

    Args:
        description: Brief skill description string

    Returns:
        List of extracted keywords

    Example:
        >>> desc = "Transform bug report. Keywords - bug, issue, error"
        >>> _extract_keywords_from_description(desc)
        ['bug', 'issue', 'error']
    """
    # Look for keywords marker (case-insensitive)
    keywords_markers = ["Keywords - ", "Keywords: ", "keywords - ", "keywords: "]

    for marker in keywords_markers:
        if marker in description:
            # Extract text after marker
            after_marker = description.split(marker, 1)[1]

            # Take first clause (up to period or newline)
            keywords_text = after_marker.split(".")[0].split("\n")[0]

            # Split by comma, strip whitespace, filter empty
            keywords = [kw.strip() for kw in keywords_text.split(",") if kw.strip()]

            if keywords:
                return keywords

    # Fallback: infer keywords from common work type patterns
    return _infer_keywords_from_work_type(description)


def _infer_keywords_from_work_type(description: str) -> List[str]:
    """
    Infer keywords from description when explicit keywords not found.

    Args:
        description: Brief skill description

    Returns:
        List of inferred keywords based on common patterns
    """
    words = description.lower().split()

    # Pattern matching for common work types
    keyword_patterns = {
        "bug": ["bug", "issue", "error", "fix"],
        "feature": ["feature", "enhancement", "new", "add"],
        "refactor": ["refactor", "cleanup", "improve", "restructure"]
    }

    for work_type, default_keywords in keyword_patterns.items():
        if work_type in words:
            return default_keywords

    # Generic fallback
    return ["work"]


if __name__ == "__main__":
    # Example usage
    routing_table_path = Path(".claude/routing_decision_table.yaml")
    output_dir = Path(".claude/skills/software-development")

    generated_skills = generate_all_coordination_skills(routing_table_path, output_dir)
    print(f"\n✅ Generated {len(generated_skills)} coordination skills")
