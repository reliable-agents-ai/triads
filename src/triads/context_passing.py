#!/usr/bin/env python3
"""
Context Passing Utilities for Triad Orchestration

This module provides utilities for extracting and formatting context
passed between agents in a triad execution sequence.

Per ADR-008: Context passed as structured summaries to prevent token bloat.

Created: 2025-10-24
Phase: Phase 1 - Core Orchestration
"""

import logging
import re
from typing import Dict, List, Optional

# Configure logging
logger = logging.getLogger(__name__)


def extract_graph_updates(agent_output: str) -> List[str]:
    """
    Extract [GRAPH_UPDATE] blocks from agent output.

    Parses agent output to find all knowledge graph update blocks,
    which are delimited by [GRAPH_UPDATE] and [/GRAPH_UPDATE] markers.

    Args:
        agent_output: Full text output from an agent

    Returns:
        List of graph update blocks (as strings), empty list if none found

    Example:
        >>> output = '''
        ... [GRAPH_UPDATE]
        ... type: add_node
        ... node_id: test_1
        ... [/GRAPH_UPDATE]
        ... '''
        >>> updates = extract_graph_updates(output)
        >>> len(updates)
        1
    """
    if not agent_output or not isinstance(agent_output, str):
        logger.warning("extract_graph_updates received invalid input")
        return []

    try:
        # Pattern matches [GRAPH_UPDATE]...[/GRAPH_UPDATE] blocks
        # DOTALL flag makes . match newlines
        pattern = r'\[GRAPH_UPDATE\](.*?)\[/GRAPH_UPDATE\]'
        matches = re.findall(pattern, agent_output, re.DOTALL | re.IGNORECASE)

        # Strip whitespace from each match
        updates = [match.strip() for match in matches]

        logger.debug(f"Extracted {len(updates)} graph update blocks")
        return updates

    except re.error as e:
        logger.error(f"Regex error in extract_graph_updates: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error in extract_graph_updates: {e}")
        return []


def extract_summary_sections(agent_output: str) -> Dict[str, List[str]]:
    """
    Extract key summary sections from agent output.

    Parses agent output to extract:
    - Findings: Key discoveries or conclusions
    - Decisions: Choices made with rationale
    - Questions: Open questions or uncertainties
    - Recommendations: Suggested next steps

    Args:
        agent_output: Full text output from an agent

    Returns:
        Dictionary with keys: findings, decisions, questions, recommendations
        Each value is a list of extracted items (empty list if section not found)

    Example:
        >>> output = '''
        ... ## Key Findings
        ... - Finding 1
        ... - Finding 2
        ...
        ... ## Open Questions
        ... - Question 1
        ... '''
        >>> sections = extract_summary_sections(output)
        >>> len(sections['findings'])
        2
        >>> len(sections['questions'])
        1
    """
    if not agent_output or not isinstance(agent_output, str):
        logger.warning("extract_summary_sections received invalid input")
        return {
            'findings': [],
            'decisions': [],
            'questions': [],
            'recommendations': []
        }

    result = {
        'findings': [],
        'decisions': [],
        'questions': [],
        'recommendations': []
    }

    try:
        # Extract findings
        findings_pattern = r'##\s*(?:Key\s+)?Findings?\s*\n(.*?)(?=\n##|\Z)'
        findings_match = re.search(findings_pattern, agent_output, re.DOTALL | re.IGNORECASE)
        if findings_match:
            result['findings'] = _extract_list_items(findings_match.group(1))

        # Extract decisions
        decisions_pattern = r'##\s*(?:Key\s+)?Decisions?\s*\n(.*?)(?=\n##|\Z)'
        decisions_match = re.search(decisions_pattern, agent_output, re.DOTALL | re.IGNORECASE)
        if decisions_match:
            result['decisions'] = _extract_list_items(decisions_match.group(1))

        # Extract questions
        questions_pattern = r'##\s*(?:Open\s+)?Questions?\s*\n(.*?)(?=\n##|\Z)'
        questions_match = re.search(questions_pattern, agent_output, re.DOTALL | re.IGNORECASE)
        if questions_match:
            result['questions'] = _extract_list_items(questions_match.group(1))

        # Extract recommendations
        rec_pattern = r'##\s*Recommendations?\s*\n(.*?)(?=\n##|\Z)'
        rec_match = re.search(rec_pattern, agent_output, re.DOTALL | re.IGNORECASE)
        if rec_match:
            result['recommendations'] = _extract_list_items(rec_match.group(1))

        logger.debug(f"Extracted summary sections: {len(result['findings'])} findings, "
                    f"{len(result['decisions'])} decisions, {len(result['questions'])} questions, "
                    f"{len(result['recommendations'])} recommendations")

    except re.error as e:
        logger.error(f"Regex error in extract_summary_sections: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in extract_summary_sections: {e}")

    return result


def _extract_list_items(text: str) -> List[str]:
    """
    Extract list items from markdown text.

    Handles both bulleted (-) and numbered (1.) lists.

    Args:
        text: Markdown text containing list items

    Returns:
        List of extracted items (without bullets/numbers)
    """
    if not text:
        return []

    items = []
    # Match lines starting with - or * or numbers followed by . or )
    pattern = r'^\s*(?:[-*]|\d+[.)]\s+)(.+)$'

    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue

        match = re.match(pattern, line)
        if match:
            items.append(match.group(1).strip())
        elif items and line:
            # Continuation of previous item (indented text)
            items[-1] += " " + line

    return items


def format_agent_context(
    from_agent: str,
    to_agent: str,
    agent_output: str,
    graph_updates: Optional[List[str]] = None,
    summary_sections: Optional[Dict[str, List[str]]] = None
) -> str:
    """
    Format context for passing between agents.

    Creates [AGENT_CONTEXT] block with structured summary of previous agent's work.
    Per ADR-008: Pass summaries, not full outputs, to prevent token bloat.

    Args:
        from_agent: Name of agent that produced output
        to_agent: Name of agent receiving context
        agent_output: Full output from previous agent
        graph_updates: Pre-extracted graph updates (optional, will extract if None)
        summary_sections: Pre-extracted summary sections (optional, will extract if None)

    Returns:
        Formatted [AGENT_CONTEXT] block as string

    Example:
        >>> context = format_agent_context(
        ...     from_agent="research-analyst",
        ...     to_agent="community-researcher",
        ...     agent_output="[GRAPH_UPDATE]...\\n## Findings\\n- Finding 1"
        ... )
        >>> '[AGENT_CONTEXT]' in context
        True
    """
    if not agent_output or not isinstance(agent_output, str):
        logger.warning("format_agent_context received invalid agent_output")
        agent_output = ""

    # Extract if not provided
    if graph_updates is None:
        graph_updates = extract_graph_updates(agent_output)
    if summary_sections is None:
        summary_sections = extract_summary_sections(agent_output)

    lines = []
    lines.append("[AGENT_CONTEXT]")
    lines.append(f"from: {from_agent}")
    lines.append(f"to: {to_agent}")
    lines.append("")

    # Add graph updates summary
    if graph_updates:
        lines.append("## Knowledge Graph Updates")
        lines.append(f"- {len(graph_updates)} node(s) added/updated")
        lines.append("")

    # Add findings
    if summary_sections.get('findings'):
        lines.append("## Key Findings")
        for finding in summary_sections['findings']:
            lines.append(f"- {finding}")
        lines.append("")

    # Add decisions
    if summary_sections.get('decisions'):
        lines.append("## Decisions Made")
        for decision in summary_sections['decisions']:
            lines.append(f"- {decision}")
        lines.append("")

    # Add questions
    if summary_sections.get('questions'):
        lines.append("## Open Questions")
        for question in summary_sections['questions']:
            lines.append(f"- {question}")
        lines.append("")

    # Add recommendations
    if summary_sections.get('recommendations'):
        lines.append("## Recommendations")
        for rec in summary_sections['recommendations']:
            lines.append(f"- {rec}")
        lines.append("")

    lines.append("[/AGENT_CONTEXT]")

    context = "\n".join(lines)
    logger.debug(f"Formatted agent context from {from_agent} to {to_agent}")

    return context


def detect_hitl_required(agent_output: str) -> bool:
    """
    Detect if agent requires human-in-the-loop gate.

    Checks for [HITL_REQUIRED] marker in agent output.
    Per ADR-009: Agents can pause execution for user input.

    Args:
        agent_output: Full text output from an agent

    Returns:
        True if HITL gate required, False otherwise

    Example:
        >>> output = "Some text\\n[HITL_REQUIRED]\\nMore text"
        >>> detect_hitl_required(output)
        True
        >>> detect_hitl_required("No HITL marker here")
        False
    """
    if not agent_output or not isinstance(agent_output, str):
        return False

    try:
        # Case-insensitive search for [HITL_REQUIRED] marker
        pattern = r'\[HITL_REQUIRED\]'
        match = re.search(pattern, agent_output, re.IGNORECASE)

        found = match is not None
        if found:
            logger.info("HITL gate detected in agent output")

        return found

    except re.error as e:
        logger.error(f"Regex error in detect_hitl_required: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error in detect_hitl_required: {e}")
        return False


def extract_hitl_prompt(agent_output: str) -> str:
    """
    Extract HITL prompt message from agent output.

    Parses agent output to find prompt text associated with [HITL_REQUIRED] marker.
    Looks for text between [HITL_REQUIRED] and [/HITL_REQUIRED] tags.

    Args:
        agent_output: Full text output from an agent

    Returns:
        HITL prompt text, or generic message if not found

    Example:
        >>> output = '''
        ... [HITL_REQUIRED]
        ... Please review design before implementation.
        ... [/HITL_REQUIRED]
        ... '''
        >>> prompt = extract_hitl_prompt(output)
        >>> 'Please review design' in prompt
        True
    """
    if not agent_output or not isinstance(agent_output, str):
        logger.warning("extract_hitl_prompt received invalid input")
        return "Human approval required before proceeding."

    try:
        # Try to find text between [HITL_REQUIRED] and [/HITL_REQUIRED]
        pattern = r'\[HITL_REQUIRED\](.*?)\[/HITL_REQUIRED\]'
        match = re.search(pattern, agent_output, re.DOTALL | re.IGNORECASE)

        if match:
            prompt = match.group(1).strip()
            logger.debug("Extracted HITL prompt from delimited block")
            return prompt

        # Fallback: look for text immediately after [HITL_REQUIRED]
        pattern_fallback = r'\[HITL_REQUIRED\]\s*\n(.+?)(?:\n\n|\Z)'
        match_fallback = re.search(pattern_fallback, agent_output, re.DOTALL | re.IGNORECASE)

        if match_fallback:
            prompt = match_fallback.group(1).strip()
            logger.debug("Extracted HITL prompt from text after marker")
            return prompt

        # Default message if no prompt found
        logger.debug("No HITL prompt found, using default message")
        return "Human approval required before proceeding."

    except re.error as e:
        logger.error(f"Regex error in extract_hitl_prompt: {e}")
        return "Human approval required before proceeding."
    except Exception as e:
        logger.error(f"Unexpected error in extract_hitl_prompt: {e}")
        return "Human approval required before proceeding."
