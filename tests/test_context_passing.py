"""Tests for context passing utilities."""

import pytest

from triads.context_passing import (
    extract_graph_updates,
    extract_summary_sections,
    format_agent_context,
    detect_hitl_required,
    extract_hitl_prompt,
)


# ============================================================================
# Sample Agent Outputs for Testing
# ============================================================================

SAMPLE_OUTPUT_WITH_GRAPH_UPDATES = """
# Research Findings

Based on my analysis, I found the following:

[GRAPH_UPDATE]
type: add_node
node_id: oauth2_feasibility
node_type: Finding
label: OAuth2 Implementation Feasibility: HIGH
description: OAuth2 is feasible for this project
confidence: 0.95
[/GRAPH_UPDATE]

[GRAPH_UPDATE]
type: add_node
node_id: oauth2_standard
node_type: Concept
label: OAuth2 Industry Standard (RFC 6749)
description: OAuth 2.0 is the industry-standard protocol
confidence: 1.0
[/GRAPH_UPDATE]

## Key Findings

- OAuth2 is widely adopted and well-supported
- Implementation complexity: MEDIUM (estimated 2-3 weeks)
- Security considerations identified

## Open Questions

- What is user demand for OAuth2 vs other auth methods?
- Should we support OAuth 1.0a for backward compatibility?
- Which OAuth2 flows to implement?

## Recommendations

- Proceed to community validation to assess user demand
"""

SAMPLE_OUTPUT_WITH_DECISIONS = """
## Decisions

- Decided to use PostgreSQL over MySQL for better JSON support
- Selected FastAPI framework for REST API
- Will implement OAuth2 with Authorization Code flow

## Findings

- FastAPI has excellent async support
- PostgreSQL JSON functions superior to MySQL

## Questions

- What is the expected user load?
- Do we need horizontal scaling initially?
"""

SAMPLE_OUTPUT_WITH_HITL = """
# Design Complete

I have completed the solution architecture.

[HITL_REQUIRED]
Please review the following design before proceeding to implementation:

1. Microservices architecture with 3 services
2. Event-driven communication via RabbitMQ
3. PostgreSQL for persistence

Do you approve this design?
[/HITL_REQUIRED]

## Key Decisions

- Microservices for scalability
- Event-driven for loose coupling
"""

SAMPLE_OUTPUT_MINIMAL = """
Just some basic text without any special markers.
"""


# ============================================================================
# Test extract_graph_updates
# ============================================================================

def test_extract_graph_updates_multiple():
    """Test extracting multiple graph update blocks."""
    updates = extract_graph_updates(SAMPLE_OUTPUT_WITH_GRAPH_UPDATES)
    assert len(updates) == 2
    assert 'oauth2_feasibility' in updates[0]
    assert 'oauth2_standard' in updates[1]


def test_extract_graph_updates_none():
    """Test when no graph updates present."""
    updates = extract_graph_updates(SAMPLE_OUTPUT_MINIMAL)
    assert updates == []


def test_extract_graph_updates_empty_input():
    """Test with empty string input."""
    updates = extract_graph_updates("")
    assert updates == []


def test_extract_graph_updates_none_input():
    """Test with None input."""
    updates = extract_graph_updates(None)
    assert updates == []


def test_extract_graph_updates_invalid_type():
    """Test with non-string input."""
    updates = extract_graph_updates(123)
    assert updates == []


def test_extract_graph_updates_case_insensitive():
    """Test that marker matching is case-insensitive."""
    output = """
    [graph_update]
    test content
    [/graph_update]
    """
    updates = extract_graph_updates(output)
    assert len(updates) == 1


def test_extract_graph_updates_nested():
    """Test extraction with nested content."""
    output = """
    [GRAPH_UPDATE]
    type: add_node
    nested:
      - item1
      - item2
    [/GRAPH_UPDATE]
    """
    updates = extract_graph_updates(output)
    assert len(updates) == 1
    assert 'nested' in updates[0]


# ============================================================================
# Test extract_summary_sections
# ============================================================================

def test_extract_summary_sections_findings():
    """Test extracting findings section."""
    sections = extract_summary_sections(SAMPLE_OUTPUT_WITH_GRAPH_UPDATES)
    assert len(sections['findings']) == 3
    assert 'OAuth2 is widely adopted' in sections['findings'][0]


def test_extract_summary_sections_questions():
    """Test extracting questions section."""
    sections = extract_summary_sections(SAMPLE_OUTPUT_WITH_GRAPH_UPDATES)
    assert len(sections['questions']) == 3
    assert 'user demand' in sections['questions'][0]


def test_extract_summary_sections_recommendations():
    """Test extracting recommendations section."""
    sections = extract_summary_sections(SAMPLE_OUTPUT_WITH_GRAPH_UPDATES)
    assert len(sections['recommendations']) == 1
    assert 'community validation' in sections['recommendations'][0]


def test_extract_summary_sections_decisions():
    """Test extracting decisions section."""
    sections = extract_summary_sections(SAMPLE_OUTPUT_WITH_DECISIONS)
    assert len(sections['decisions']) == 3
    assert 'PostgreSQL' in sections['decisions'][0]


def test_extract_summary_sections_empty():
    """Test with no sections present."""
    sections = extract_summary_sections(SAMPLE_OUTPUT_MINIMAL)
    assert sections['findings'] == []
    assert sections['decisions'] == []
    assert sections['questions'] == []
    assert sections['recommendations'] == []


def test_extract_summary_sections_invalid_input():
    """Test with invalid input."""
    sections = extract_summary_sections(None)
    assert all(len(v) == 0 for v in sections.values())


def test_extract_summary_sections_numbered_list():
    """Test extraction with numbered lists."""
    output = """
    ## Findings
    1. First finding
    2. Second finding
    3. Third finding
    """
    sections = extract_summary_sections(output)
    assert len(sections['findings']) == 3
    assert sections['findings'][0] == "First finding"


def test_extract_summary_sections_mixed_bullets():
    """Test extraction with mixed bullet styles."""
    output = """
    ## Questions
    - Question with dash
    * Question with asterisk
    1. Question numbered
    """
    sections = extract_summary_sections(output)
    assert len(sections['questions']) == 3


def test_extract_summary_sections_multiline_items():
    """Test extraction with multi-line list items."""
    output = """
    ## Findings
    - This is a finding
      that spans multiple lines
      and continues here
    - Another finding
    """
    sections = extract_summary_sections(output)
    assert len(sections['findings']) == 2
    assert 'spans multiple lines' in sections['findings'][0]


# ============================================================================
# Test format_agent_context
# ============================================================================

def test_format_agent_context_basic():
    """Test basic context formatting."""
    context = format_agent_context(
        from_agent="research-analyst",
        to_agent="community-researcher",
        agent_output=SAMPLE_OUTPUT_WITH_GRAPH_UPDATES
    )

    assert '[AGENT_CONTEXT]' in context
    assert '[/AGENT_CONTEXT]' in context
    assert 'from: research-analyst' in context
    assert 'to: community-researcher' in context


def test_format_agent_context_includes_graph_updates():
    """Test that context includes graph update summary."""
    context = format_agent_context(
        from_agent="research-analyst",
        to_agent="community-researcher",
        agent_output=SAMPLE_OUTPUT_WITH_GRAPH_UPDATES
    )

    assert 'Knowledge Graph Updates' in context
    assert '2 node(s) added/updated' in context


def test_format_agent_context_includes_findings():
    """Test that context includes findings."""
    context = format_agent_context(
        from_agent="research-analyst",
        to_agent="community-researcher",
        agent_output=SAMPLE_OUTPUT_WITH_GRAPH_UPDATES
    )

    assert 'Key Findings' in context
    assert 'OAuth2 is widely adopted' in context


def test_format_agent_context_includes_questions():
    """Test that context includes questions."""
    context = format_agent_context(
        from_agent="research-analyst",
        to_agent="community-researcher",
        agent_output=SAMPLE_OUTPUT_WITH_GRAPH_UPDATES
    )

    assert 'Open Questions' in context
    assert 'user demand' in context


def test_format_agent_context_includes_decisions():
    """Test that context includes decisions."""
    context = format_agent_context(
        from_agent="solution-architect",
        to_agent="design-bridge",
        agent_output=SAMPLE_OUTPUT_WITH_DECISIONS
    )

    assert 'Decisions Made' in context
    assert 'PostgreSQL' in context


def test_format_agent_context_empty_output():
    """Test formatting with empty agent output."""
    context = format_agent_context(
        from_agent="agent1",
        to_agent="agent2",
        agent_output=""
    )

    assert '[AGENT_CONTEXT]' in context
    assert 'from: agent1' in context


def test_format_agent_context_preextracted():
    """Test with pre-extracted updates and sections."""
    graph_updates = ['update1', 'update2']
    summary_sections = {
        'findings': ['Finding 1'],
        'decisions': [],
        'questions': ['Question 1'],
        'recommendations': []
    }

    context = format_agent_context(
        from_agent="agent1",
        to_agent="agent2",
        agent_output="",
        graph_updates=graph_updates,
        summary_sections=summary_sections
    )

    assert '2 node(s) added/updated' in context
    assert 'Finding 1' in context
    assert 'Question 1' in context


def test_format_agent_context_no_sections():
    """Test formatting when no sections are found."""
    context = format_agent_context(
        from_agent="agent1",
        to_agent="agent2",
        agent_output=SAMPLE_OUTPUT_MINIMAL
    )

    assert '[AGENT_CONTEXT]' in context
    # Should not include section headers if no content
    assert 'Key Findings' not in context
    assert 'Decisions Made' not in context


# ============================================================================
# Test detect_hitl_required
# ============================================================================

def test_detect_hitl_required_true():
    """Test detection when HITL marker present."""
    assert detect_hitl_required(SAMPLE_OUTPUT_WITH_HITL) is True


def test_detect_hitl_required_false():
    """Test detection when HITL marker absent."""
    assert detect_hitl_required(SAMPLE_OUTPUT_MINIMAL) is False


def test_detect_hitl_required_empty():
    """Test detection with empty input."""
    assert detect_hitl_required("") is False


def test_detect_hitl_required_none():
    """Test detection with None input."""
    assert detect_hitl_required(None) is False


def test_detect_hitl_required_case_insensitive():
    """Test that detection is case-insensitive."""
    output = "Some text [hitl_required] more text"
    assert detect_hitl_required(output) is True


def test_detect_hitl_required_multiple():
    """Test detection with multiple markers (should still return True)."""
    output = """
    [HITL_REQUIRED]
    First prompt
    [/HITL_REQUIRED]

    [HITL_REQUIRED]
    Second prompt
    [/HITL_REQUIRED]
    """
    assert detect_hitl_required(output) is True


# ============================================================================
# Test extract_hitl_prompt
# ============================================================================

def test_extract_hitl_prompt_with_delimiters():
    """Test extracting HITL prompt with full delimiters."""
    prompt = extract_hitl_prompt(SAMPLE_OUTPUT_WITH_HITL)
    assert 'Please review the following design' in prompt
    assert 'Microservices architecture' in prompt
    assert 'Do you approve' in prompt


def test_extract_hitl_prompt_without_delimiters():
    """Test extracting when only opening marker present."""
    output = """
    [HITL_REQUIRED]
    Please approve this change.

    More text here.
    """
    prompt = extract_hitl_prompt(output)
    assert 'Please approve this change' in prompt


def test_extract_hitl_prompt_no_marker():
    """Test extraction when no HITL marker present."""
    prompt = extract_hitl_prompt(SAMPLE_OUTPUT_MINIMAL)
    assert prompt == "Human approval required before proceeding."


def test_extract_hitl_prompt_empty_input():
    """Test extraction with empty input."""
    prompt = extract_hitl_prompt("")
    assert prompt == "Human approval required before proceeding."


def test_extract_hitl_prompt_none_input():
    """Test extraction with None input."""
    prompt = extract_hitl_prompt(None)
    assert prompt == "Human approval required before proceeding."


def test_extract_hitl_prompt_whitespace_handling():
    """Test that whitespace is properly trimmed."""
    output = """
    [HITL_REQUIRED]

        Please approve with extra whitespace.

    [/HITL_REQUIRED]
    """
    prompt = extract_hitl_prompt(output)
    assert prompt == "Please approve with extra whitespace."
    assert not prompt.startswith('\n')
    assert not prompt.endswith('\n')


# ============================================================================
# Integration Tests
# ============================================================================

def test_full_context_passing_workflow():
    """Test complete workflow of extracting and formatting context."""
    # Step 1: Extract from agent output
    graph_updates = extract_graph_updates(SAMPLE_OUTPUT_WITH_GRAPH_UPDATES)
    summary_sections = extract_summary_sections(SAMPLE_OUTPUT_WITH_GRAPH_UPDATES)

    # Step 2: Verify extractions
    assert len(graph_updates) == 2
    assert len(summary_sections['findings']) == 3
    assert len(summary_sections['questions']) == 3

    # Step 3: Format context
    context = format_agent_context(
        from_agent="research-analyst",
        to_agent="community-researcher",
        agent_output=SAMPLE_OUTPUT_WITH_GRAPH_UPDATES,
        graph_updates=graph_updates,
        summary_sections=summary_sections
    )

    # Step 4: Verify formatted context
    assert '[AGENT_CONTEXT]' in context
    assert 'from: research-analyst' in context
    assert 'to: community-researcher' in context
    assert '2 node(s) added/updated' in context
    assert 'OAuth2 is widely adopted' in context
    assert 'user demand' in context
    assert 'community validation' in context


def test_hitl_gate_workflow():
    """Test complete HITL gate detection and prompt extraction workflow."""
    # Step 1: Detect HITL requirement
    hitl_required = detect_hitl_required(SAMPLE_OUTPUT_WITH_HITL)
    assert hitl_required is True

    # Step 2: Extract prompt
    prompt = extract_hitl_prompt(SAMPLE_OUTPUT_WITH_HITL)
    assert 'Please review the following design' in prompt

    # Step 3: Verify context formatting still works
    context = format_agent_context(
        from_agent="solution-architect",
        to_agent="design-bridge",
        agent_output=SAMPLE_OUTPUT_WITH_HITL
    )
    assert '[AGENT_CONTEXT]' in context


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================

def test_malformed_graph_update_block():
    """Test handling of malformed graph update blocks."""
    output = """
    [GRAPH_UPDATE]
    This is missing the closing tag
    """
    updates = extract_graph_updates(output)
    # Should return empty list (no properly closed blocks)
    assert updates == []


def test_overlapping_sections():
    """Test handling when section names overlap."""
    output = """
    ## Key Findings and Decisions
    - Item 1
    - Item 2

    ## Questions and Recommendations
    - Item 3
    """
    sections = extract_summary_sections(output)
    # Should extract based on exact section header match
    assert len(sections['findings']) == 0  # Not exact match
    assert len(sections['questions']) == 0  # Not exact match


def test_empty_sections():
    """Test sections that exist but have no content."""
    output = """
    ## Findings

    ## Questions
    """
    sections = extract_summary_sections(output)
    assert sections['findings'] == []
    assert sections['questions'] == []


def test_special_characters_in_content():
    """Test handling of special regex characters in content."""
    output = """
    ## Findings
    - Finding with [brackets] and (parentheses)
    - Finding with *asterisks* and $dollar signs
    """
    sections = extract_summary_sections(output)
    assert len(sections['findings']) == 2
    assert '[brackets]' in sections['findings'][0]
    assert '*asterisks*' in sections['findings'][1]


def test_unicode_content():
    """Test handling of unicode characters."""
    output = """
    ## Findings
    - Finding with émojis 🎉 and ünïcödë
    """
    sections = extract_summary_sections(output)
    assert len(sections['findings']) == 1
    assert '🎉' in sections['findings'][0]
    assert 'ünïcödë' in sections['findings'][0]
