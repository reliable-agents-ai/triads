#!/usr/bin/env python3
"""
UserPromptSubmit Hook: Inject Supervisor Instructions + Workspace Context Detection

This hook runs before each user message and:
1. Detects context switches (Phase 4 - Workspace Architecture)
2. Manages workspace lifecycle (pause/resume/create)
3. Injects Supervisor instructions with routing context

Refactored to use Tool Abstraction Layer (Phase 7).
Phase 4 (Workspace Architecture): Added context switch detection integration

Hook Type: UserPromptSubmit
Configured in: hooks/hooks.json (plugin)

Previous implementation: 261 lines with workflow loading logic
Current implementation: ~800 lines with context detection + routing
"""

import json
import sys
import time
from pathlib import Path

# Add src and hooks to path for imports
repo_root = Path(__file__).parent.parent
if str(repo_root / "src") not in sys.path:
    sys.path.insert(0, str(repo_root / "src"))
if str(repo_root / "hooks") not in sys.path:
    sys.path.insert(0, str(repo_root / "hooks"))

# Import common utilities
from common import output_hook_result, get_project_dir  # noqa: E402

# Import LLM routing (v0.13.0 - Universal Context Discovery)
from triads.llm_routing import discover_context  # noqa: E402

# Import workspace context detection (Phase 4 - Workspace Architecture)
from workspace_detector import detect_and_handle_context_switch, format_context_detection_summary  # noqa: E402

# Import event capture
from triads.events.tools import capture_event  # noqa: E402


# NOTE: detect_work_request() removed in v0.13.0
# Q&A fast path eliminated - ALL messages now route through LLM discovery
# Design philosophy: Trade performance for intelligence, maximize supervisor context


def load_workflow_config():
    """
    Load workflow configuration from .claude/settings.json.

    Returns:
        dict: Workflow configuration, or None if loading fails
    """
    try:
        project_dir = get_project_dir()
        settings_path = project_dir / '.claude' / 'settings.json'

        with open(settings_path, 'r') as f:
            config = json.load(f)

        return config.get('triad_system', {})

    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print(f"⚠️  Could not load workflow config: {e}", file=sys.stderr)
        return None


def generate_orchestrator_instructions(
    triad_name: str,
    user_request: str,
    request_type: str = "work"
) -> str:
    """
    Generate orchestrator instructions for triad execution.

    Per ADR-007: Main Claude orchestrates triads with injected instructions.
    This function generates the step-by-step protocol for coordinating agents.

    Args:
        triad_name: Name of triad to orchestrate (e.g., "implementation")
        user_request: Original user request being fulfilled
        request_type: Type of request (e.g., "feature", "bug", "refactor")

    Returns:
        Formatted orchestrator instructions as string

    Example:
        >>> instructions = generate_orchestrator_instructions(
        ...     triad_name="implementation",
        ...     user_request="Add OAuth2 support",
        ...     request_type="feature"
        ... )
        >>> "ORCHESTRATOR MODE" in instructions
        True
    """
    # Load triad config
    triad_config = load_workflow_config()
    if not triad_config or 'triads' not in triad_config:
        return "ERROR: Could not load triad configuration"

    # Get triad details
    triad_def = triad_config['triads'].get(triad_name)
    if not triad_def:
        return f"ERROR: Triad '{triad_name}' not found in configuration"

    agents = triad_def.get('agents', [])
    purpose = triad_def.get('purpose', 'Unknown purpose')
    graph_file = triad_def.get('graph_file', f'.claude/graphs/{triad_name}_graph.json')

    lines = []

    # Header
    lines.append("=" * 80)
    lines.append("# 🎯 ORCHESTRATOR MODE: TRIAD EXECUTION")
    lines.append("=" * 80)
    lines.append("")
    lines.append("**MODE**: You are now orchestrating a triad (ADR-007)")
    lines.append("")

    # Mission
    lines.append("## MISSION")
    lines.append("")
    lines.append(f"**User Request**: {user_request}")
    lines.append(f"**Request Type**: {request_type}")
    lines.append(f"**Triad**: {triad_name}")
    lines.append(f"**Purpose**: {purpose}")
    lines.append("")

    # Agent sequence
    lines.append("## AGENT SEQUENCE")
    lines.append("")
    for i, agent in enumerate(agents, 1):
        arrow = " → " if i < len(agents) else ""
        lines.append(f"{i}. {agent}{arrow}")
    lines.append("")
    lines.append(f"**Knowledge Graph**: {graph_file}")
    lines.append("")

    # Orchestration protocol
    lines.append("## ORCHESTRATION PROTOCOL")
    lines.append("")
    lines.append("For EACH agent in sequence, you SHALL follow this protocol:")
    lines.append("")
    lines.append("### STEP 1: INVOKE")
    lines.append("```")
    lines.append("Use Task tool to invoke agent:")
    lines.append("- subagent_type: {agent_name}")
    lines.append("- description: Brief description of work")
    lines.append("- prompt: Detailed instructions + context from previous agent")
    lines.append("```")
    lines.append("")
    lines.append("### STEP 2: CAPTURE")
    lines.append("Store agent output in memory for:")
    lines.append("- Context passing to next agent")
    lines.append("- HITL gate detection")
    lines.append("- Final summary to user")
    lines.append("")
    lines.append("### STEP 3: CHECK GATES")
    lines.append("```python")
    lines.append("# Check for HITL gate")
    lines.append("if '[HITL_REQUIRED]' in agent_output:")
    lines.append("    extract_hitl_prompt(agent_output)")
    lines.append("    present_to_user_for_approval()")
    lines.append("    wait_for_user_decision()")
    lines.append("    if user_approves:")
    lines.append("        continue_to_next_agent()")
    lines.append("    else:")
    lines.append("        halt_workflow()")
    lines.append("```")
    lines.append("")
    lines.append("### STEP 4: DISPLAY")
    lines.append("Show user agent's output:")
    lines.append("- Key findings")
    lines.append("- Decisions made")
    lines.append("- Progress update")
    lines.append("- Next steps")
    lines.append("")
    lines.append("### STEP 5: PASS CONTEXT")
    lines.append("If not final agent:")
    lines.append("```")
    lines.append("Extract from agent output:")
    lines.append("- [GRAPH_UPDATE] blocks")
    lines.append("- ## Findings sections")
    lines.append("- ## Decisions sections")
    lines.append("- ## Questions sections")
    lines.append("")
    lines.append("Format as [AGENT_CONTEXT] block:")
    lines.append("[AGENT_CONTEXT]")
    lines.append("from: {current_agent}")
    lines.append("to: {next_agent}")
    lines.append("")
    lines.append("## Key Findings")
    lines.append("- {finding_1}")
    lines.append("- {finding_2}")
    lines.append("")
    lines.append("## Decisions Made")
    lines.append("- {decision_1}")
    lines.append("")
    lines.append("## Open Questions")
    lines.append("- {question_1}")
    lines.append("[/AGENT_CONTEXT]")
    lines.append("```")
    lines.append("")

    # Context format specification
    lines.append("## CONTEXT FORMAT SPECIFICATION")
    lines.append("")
    lines.append("**CRITICAL**: Pass SUMMARIES, not full outputs (ADR-008)")
    lines.append("")
    lines.append("**Extract from agent output**:")
    lines.append("- Lines matching `[GRAPH_UPDATE]...[/GRAPH_UPDATE]`")
    lines.append("- Sections matching `## Findings`, `## Decisions`, `## Questions`")
    lines.append("- List items (lines starting with `-` or `*` or numbers)")
    lines.append("")
    lines.append("**Format as structured context**:")
    lines.append("- Count graph updates, don't include full content")
    lines.append("- Extract bullet points, preserve key information")
    lines.append("- Include questions to address")
    lines.append("- Keep recommendations from previous agent")
    lines.append("")

    # HITL protocol
    lines.append("## HITL GATE PROTOCOL")
    lines.append("")
    lines.append("**When agent output contains `[HITL_REQUIRED]`**:")
    lines.append("")
    lines.append("1. HALT execution immediately")
    lines.append("2. EXTRACT prompt text between markers")
    lines.append("3. DISPLAY to user with clear formatting:")
    lines.append("   ```")
    lines.append("   ⏸️  HUMAN APPROVAL REQUIRED")
    lines.append("   ")
    lines.append("   {agent_name} requests approval:")
    lines.append("   ")
    lines.append("   {extracted_prompt}")
    lines.append("   ")
    lines.append("   Do you approve? (yes/no)")
    lines.append("   ```")
    lines.append("4. WAIT for user response")
    lines.append("5. IF approved: Continue to next agent")
    lines.append("6. IF rejected: Halt workflow, ask user for next steps")
    lines.append("")

    # Completion protocol
    lines.append("## COMPLETION PROTOCOL")
    lines.append("")
    lines.append("When final agent completes:")
    lines.append("")
    lines.append("1. SUMMARIZE triad results:")
    lines.append("   - What was accomplished")
    lines.append("   - Key decisions made")
    lines.append("   - Deliverables produced")
    lines.append("2. CHECK for handoff to next triad:")
    lines.append("   - Look for `[HANDOFF_REQUEST]` marker")
    lines.append("   - If present: Inform user next triad will auto-invoke")
    lines.append("3. THANK user for patience")
    lines.append("4. AWAIT user feedback or next request")
    lines.append("")

    # Error handling
    lines.append("## ERROR HANDLING")
    lines.append("")
    lines.append("**IF agent fails or produces unclear output**:")
    lines.append("")
    lines.append("1. CAPTURE error details")
    lines.append("2. INFORM user of failure")
    lines.append("3. PRESENT options:")
    lines.append("   - Retry agent with clarification")
    lines.append("   - Skip to next agent (if safe)")
    lines.append("   - Abort triad execution")
    lines.append("4. AWAIT user decision")
    lines.append("")
    lines.append("**DO NOT**:")
    lines.append("- Continue silently after errors")
    lines.append("- Make assumptions about intent")
    lines.append("- Skip agents without user approval")
    lines.append("")

    # Footer
    lines.append("=" * 80)
    lines.append("")
    lines.append("**BEGIN ORCHESTRATION**")
    lines.append("")
    lines.append(f"Invoke first agent: {agents[0]}")
    lines.append("")
    lines.append("=" * 80)
    lines.append("")

    return "\n".join(lines)


def route_user_request_universal(user_prompt: str) -> dict:
    """
    Universal context discovery for ALL messages (v0.13.0).

    This function replaces Q&A fast path with comprehensive LLM analysis
    for every user message, providing rich context to the supervisor.

    Args:
        user_prompt: User's message (question or work request)

    Returns:
        Discovery result dict with intent_type, confidence, recommended_action,
        available skills, workflow entry points, and alternatives.
        Returns None if discovery fails.
    """
    skills_dir = Path(".claude/skills/software-development")

    try:
        discovery_result = discover_context(
            user_input=user_prompt,
            skills_dir=skills_dir,
            timeout=10
        )
        return discovery_result
    except Exception as e:
        print(f"LLM context discovery failed: {e}", file=sys.stderr)
        return None


def format_supervisor_instructions() -> str:
    """
    Generate Supervisor instructions for main Claude.

    Dynamically loads workflow configuration from .claude/settings.json
    to make instructions workflow-agnostic.

    Returns:
        str: Formatted Supervisor instructions
    """
    # Load workflow configuration
    triad_config = load_workflow_config()

    lines = []

    lines.append("=" * 80)
    lines.append("# 🎯 SUPERVISOR STANDING ORDERS")
    lines.append("=" * 80)
    lines.append("")
    lines.append("**DIRECTIVE**: You are operating in Supervisor mode (ADR-007)")
    lines.append("")
    lines.append("## MISSION")
    lines.append("")
    lines.append("You SHALL serve as the primary interface for ALL user interactions.")
    lines.append("")
    lines.append("## RULES OF ENGAGEMENT")
    lines.append("")
    lines.append("**ROE 1: TRIAGE PROTOCOL** (Triage every message)")
    lines.append("- CLASSIFY every user message as Q&A OR work request")
    lines.append("")
    lines.append("**Q&A Indicators (NOT work requests)**:")
    lines.append("- what is, what are, what does")
    lines.append("- how does, how do, how to")
    lines.append("- explain, tell me about, describe")
    lines.append("- can you explain, could you explain")
    lines.append("- can you, could you, would you")
    lines.append("- why is, why does")
    lines.append("- when should, where is, who is, which is")
    lines.append("")
    lines.append("**Work Indicators by Type**:")
    lines.append("- **Feature**: implement, add, create, build, develop, make")
    lines.append("- **Bug**: fix, bug, error, broken, issue, crash, failing, not working")
    lines.append("- **Refactor**: refactor, cleanup, clean up, improve, consolidate, messy code")
    lines.append("- **Design**: design, architecture, how should we, what approach")
    lines.append("- **Release**: deploy, release, publish, ship, launch")
    lines.append("")
    lines.append("**Detection Priority**:")
    lines.append("1. If message matches Q&A patterns → ANSWER directly")
    lines.append("2. If message matches work patterns → INVOKE triad")
    lines.append("3. If ambiguous → ASK user for clarification")
    lines.append("")
    lines.append("**ROE 2: Q&A HANDLING**")
    lines.append("- ANSWER informational questions directly")
    lines.append("- DO NOT route Q&A through workflows")
    lines.append("- Provide concise, accurate responses")
    lines.append("")
    lines.append("**ROE 3: TRIAD ATOMICITY (NON-NEGOTIABLE)**")
    lines.append("- Triads are ATOMIC units - NEVER decompose them")
    lines.append("- YOU SHALL NOT decompose triads")
    lines.append("- YOU SHALL NOT extract individual agents")
    lines.append("- Triads MUST complete internally before handoff")
    lines.append("- Flexibility is achieved through workflow composition ONLY")
    lines.append("")
    lines.append("**ROE 4: EMERGENCY BYPASS**")
    lines.append("- IF user message starts with `/direct `: SKIP all routing")
    lines.append("- Allow direct conversation without workflow invocation")
    lines.append("- Use ONLY when explicitly requested by user")
    lines.append("")

    # Dynamic workflow section based on config
    if triad_config and 'workflow' in triad_config:
        workflow = triad_config['workflow']
        workflow_name = workflow.get('name', 'Workflow')
        entry_point = workflow.get('entry_point', 'unknown')
        entry_agent = workflow.get('entry_agent', 'unknown')
        sequence = workflow.get('sequence', [])

        lines.append(f"## WORKFLOW EXECUTION ORDERS: {workflow_name}")
        lines.append("")
        lines.append("**STANDING ORDER 1: SINGLE ENTRY POINT (ABSOLUTE)**")
        lines.append(f"- ALL work requests SHALL enter through {entry_point} triad")
        lines.append(f"- YOU SHALL invoke {entry_agent} for EVERY work request")
        lines.append(f"- NO EXCEPTIONS - even for refactoring, bugs, or urgent fixes")
        lines.append("")
        lines.append("**STANDING ORDER 2: COMPLETE WORKFLOW SEQUENCE (MANDATORY)**")
        lines.append("```")
        lines.append(" → ".join(sequence))
        lines.append("```")
        lines.append(f"- Every request SHALL flow through ALL {len(sequence)} triads")
        lines.append("- YOU SHALL NOT skip triads")
        lines.append("- YOU SHALL NOT shortcut the workflow")
        lines.append("- Triads adapt thoroughness internally - NOT by skipping")
        lines.append("")
        lines.append("**STANDING ORDER 3: EXECUTION PROCEDURE**")
        lines.append("FOR EVERY work request, YOU SHALL:")
        lines.append("1. CLASSIFY: Determine request type (feature|bug|refactor|release|other)")
        lines.append(f"2. INVOKE: Use Task tool to invoke {entry_agent}")
        lines.append(f"3. BRIEF: Pass classification + description to {entry_agent}")
        lines.append("4. MONITOR: Track workflow progress through handoffs")
        lines.append("")
        lines.append("**EXECUTION EXAMPLES**:")
        lines.append("```")
        lines.append("User: 'Add OAuth2 support'")
        lines.append(f"You: CLASSIFY as feature → INVOKE {entry_agent}")
        lines.append("")
        lines.append("User: 'Fix router crash bug'")
        lines.append(f"You: CLASSIFY as bug → INVOKE {entry_agent}")
        lines.append("")
        lines.append("User: 'Refactor messy code in X'")
        lines.append(f"You: CLASSIFY as refactor → INVOKE {entry_agent}")
        lines.append("")
        lines.append("User: 'Clean up the router module'")
        lines.append(f"You: CLASSIFY as refactor → INVOKE {entry_agent}")
        lines.append("```")
        lines.append("")
        lines.append("**STANDING ORDER 4: AUTOMATED HANDOFFS**")
        lines.append("- Triads SHALL hand off automatically when complete")
        lines.append("- YOU SHALL NOT manually invoke subsequent triads")
        lines.append("- Handoffs persist across sessions via pending state")
        lines.append("- SessionStart hook auto-invokes next triad on session restart")
        lines.append("")
    else:
        # Fallback if config couldn't be loaded
        lines.append("## ⚠️ WORKFLOW CONFIGURATION FAILURE")
        lines.append("")
        lines.append("**ERROR**: Could not load workflow configuration from .claude/settings.json")
        lines.append("")
        lines.append("**FALLBACK PROCEDURE**:")
        lines.append("- HALT workflow routing until configuration is fixed")
        lines.append("- NOTIFY user of configuration error")
        lines.append("- ACCEPT only Q&A requests until resolved")
        lines.append("")

    lines.append("## TRAINING MODE PROTOCOL")
    lines.append("")
    lines.append("**STATUS**: Training mode ACTIVE")
    lines.append("")
    lines.append("**PROCEDURE**:")
    lines.append("1. CLASSIFY the work request type")
    lines.append("2. ANNOUNCE your classification to user")
    lines.append("3. REQUEST user confirmation before invoking workflow")
    lines.append("4. INVOKE only after user approves")
    lines.append("5. ACCEPT user corrections without argument")
    lines.append("")
    lines.append("**DEACTIVATION**: Training mode OFF after 10 successful routings")
    lines.append("")
    lines.append("=" * 80)
    lines.append("")

    return "\n".join(lines)


def format_supervisor_with_enriched_context(user_prompt: str, discovery_result: dict) -> str:
    """
    Generate supervisor instructions with enriched context discovery (v0.13.0).

    Args:
        user_prompt: Original user message
        discovery_result: Result from route_user_request_universal()

    Returns:
        Formatted context string with comprehensive discovery information
    """
    lines = []

    # Enhanced supervisor instructions
    lines.append(format_supervisor_instructions_enhanced())

    # Add discovery section if available
    if discovery_result:
        lines.append("\n" + "=" * 80)
        lines.append("# 🧠 INTELLIGENT ROUTING ANALYSIS")
        lines.append("=" * 80)
        lines.append("")
        lines.append(f"**User Message**: {user_prompt}")
        lines.append("")

        # Intent classification
        lines.append("## User Intent Classification")
        intent_type = discovery_result.get('intent_type', 'unknown')
        confidence = discovery_result.get('confidence', 0)
        lines.append(f"**Intent Type**: {intent_type}")
        lines.append(f"**Confidence**: {confidence * 100:.0f}%")
        lines.append(f"**Reasoning**: {discovery_result.get('reasoning', 'N/A')}")
        lines.append("")

        # Recommended action
        recommended = discovery_result.get('recommended_action', 'unknown')
        lines.append(f"**Recommended Action**: {recommended}")

        if intent_type == "work":
            brief_skill = discovery_result.get('brief_skill', 'unknown')
            work_type = discovery_result.get('work_type', 'unknown')
            lines.append(f"**Work Type**: {work_type}")
            lines.append(f"**Brief Skill**: {brief_skill}")

        lines.append("")

        # Available skills
        lines.append("## Available Brief Skills")
        brief_skills = discovery_result.get('available_brief_skills', [])
        for skill in brief_skills[:3]:  # Show top 3
            skill_name = skill.get('name', 'unknown')
            skill_conf = skill.get('confidence', 0) * 100
            skill_desc = skill.get('description', 'No description')
            lines.append(f"- **{skill_name}** ({skill_conf:.0f}%): {skill_desc}")
        lines.append("")

        # Workflow entry points
        lines.append("## Workflow Entry Points")
        entry_triad = discovery_result.get('entry_triad', 'unknown')
        entry_agent = discovery_result.get('entry_agent', 'unknown')
        lines.append(f"**Entry Triad**: {entry_triad}")
        lines.append(f"**Entry Agent**: {entry_agent}")
        lines.append("")

        # Workflow sequence
        workflow_seq = discovery_result.get('workflow_sequence', [])
        if workflow_seq:
            lines.append(f"**Sequence**: {' → '.join(workflow_seq)}")
            lines.append("")

        # Alternative interpretations
        alternatives = discovery_result.get('alternative_interpretations', [])
        if alternatives:
            lines.append("## Alternative Interpretations")
            for alt in alternatives:
                alt_type = alt.get('type', 'unknown')
                alt_conf = alt.get('confidence', 0) * 100
                alt_rationale = alt.get('rationale', 'No rationale')
                lines.append(f"- **{alt_type}** ({alt_conf:.0f}%): {alt_rationale}")
            lines.append("")

        # Confidence breakdown
        qa_conf = discovery_result.get('qa_confidence', 0) * 100
        work_conf = discovery_result.get('work_confidence', 0) * 100
        lines.append("## Confidence Breakdown")
        lines.append(f"- Q&A: {qa_conf:.0f}%")
        lines.append(f"- Work Request: {work_conf:.0f}%")
        lines.append("")

        # Performance metrics
        cost = discovery_result.get('cost_usd', 0)
        duration = discovery_result.get('duration_ms', 0)
        lines.append(f"**Performance**: ${cost:.4f} | {duration}ms")
        lines.append("")

        # Supervisor decision points
        lines.append("## Supervisor Decision Points")
        if recommended == "answer_directly":
            lines.append("✅ **RECOMMENDED**: Answer user's question directly")
        elif recommended == "invoke_skill":
            lines.append(f"✅ **RECOMMENDED**: Invoke `{discovery_result.get('brief_skill')}` skill")
        elif recommended == "clarify":
            lines.append("⚠️  **RECOMMENDED**: Ask user for clarification")
        lines.append("")

        lines.append("=" * 80)
        lines.append("")

    return "\n".join(lines)


def format_supervisor_instructions_enhanced() -> str:
    """
    Generate enhanced Supervisor instructions for v0.13.0.

    Returns:
        str: Formatted Supervisor instructions with universal routing context
    """
    # Load workflow configuration
    triad_config = load_workflow_config()

    lines = []

    lines.append("=" * 80)
    lines.append("# 🎯 SUPERVISOR STANDING ORDERS (v0.13.0)")
    lines.append("=" * 80)
    lines.append("")
    lines.append("**DIRECTIVE**: You are operating in Supervisor mode with Universal Context Enrichment")
    lines.append("")
    lines.append("## WHAT'S NEW IN v0.13.0")
    lines.append("")
    lines.append("**Universal Routing**: ALL messages (Q&A AND work) now routed through LLM analysis")
    lines.append("**Rich Context**: Comprehensive discovery of skills, agents, triads, workflows")
    lines.append("**Intelligent Decisions**: Supervisor decides based on enriched context")
    lines.append("**No Shortcuts**: Performance traded for intelligence and accuracy")
    lines.append("")
    lines.append("## MISSION")
    lines.append("")
    lines.append("You SHALL serve as the primary interface for ALL user interactions.")
    lines.append("You SHALL make intelligent routing decisions based on enriched context provided.")
    lines.append("")
    lines.append("## RULES OF ENGAGEMENT")
    lines.append("")
    lines.append("**ROE 1: CONTEXT-DRIVEN DECISIONS**")
    lines.append("- REVIEW the 🧠 INTELLIGENT ROUTING ANALYSIS section below")
    lines.append("- CONSIDER intent classification, confidence scores, alternatives")
    lines.append("- FOLLOW recommended action unless user explicitly requests otherwise")
    lines.append("- IF ambiguous (<70% confidence): ASK user for clarification")
    lines.append("")
    lines.append("**ROE 2: Q&A HANDLING**")
    lines.append("- IF intent_type='qa' AND recommended_action='answer_directly':")
    lines.append("  → ANSWER the question directly without invoking workflows")
    lines.append("- PROVIDE concise, accurate responses")
    lines.append("- CITE sources when applicable")
    lines.append("")
    lines.append("**ROE 3: WORK REQUEST HANDLING**")
    lines.append("- IF intent_type='work' AND recommended_action='invoke_skill':")
    lines.append("  → INVOKE the recommended brief skill")
    lines.append("  → PASS user's request to brief skill for structured specification")
    lines.append("- FOLLOW workflow entry points (entry_triad → entry_agent)")
    lines.append("")
    lines.append("**ROE 4: AMBIGUITY HANDLING**")
    lines.append("- IF intent_type='ambiguous' AND recommended_action='clarify':")
    lines.append("  → PRESENT alternative interpretations to user")
    lines.append("  → ASK user which interpretation is correct")
    lines.append("  → PROCEED only after user clarifies intent")
    lines.append("")
    lines.append("**ROE 5: EMERGENCY BYPASS**")
    lines.append("- IF user message starts with `/direct `: SKIP all routing")
    lines.append("- Allow direct conversation without workflow invocation")
    lines.append("- Use ONLY when explicitly requested by user")
    lines.append("")

    # Dynamic workflow section based on config
    if triad_config and 'workflow' in triad_config:
        workflow = triad_config['workflow']
        workflow_name = workflow.get('name', 'Workflow')
        entry_point = workflow.get('entry_point', 'unknown')
        entry_agent = workflow.get('entry_agent', 'unknown')
        sequence = workflow.get('sequence', [])

        lines.append(f"## WORKFLOW EXECUTION ORDERS: {workflow_name}")
        lines.append("")
        lines.append("**STANDING ORDER 1: SINGLE ENTRY POINT (ABSOLUTE)**")
        lines.append(f"- ALL work requests SHALL enter through {entry_point} triad")
        lines.append(f"- YOU SHALL invoke {entry_agent} for EVERY work request")
        lines.append(f"- NO EXCEPTIONS - routing analysis provides entry point automatically")
        lines.append("")
        lines.append("**STANDING ORDER 2: COMPLETE WORKFLOW SEQUENCE (MANDATORY)**")
        lines.append("```")
        lines.append(" → ".join(sequence))
        lines.append("```")
        lines.append(f"- Every request SHALL flow through ALL {len(sequence)} triads")
        lines.append("- YOU SHALL NOT skip triads")
        lines.append("- YOU SHALL NOT shortcut the workflow")
        lines.append("- Triads adapt thoroughness internally - NOT by skipping")
        lines.append("")
    else:
        # Fallback if config couldn't be loaded
        lines.append("## ⚠️ WORKFLOW CONFIGURATION FAILURE")
        lines.append("")
        lines.append("**ERROR**: Could not load workflow configuration from .claude/settings.json")
        lines.append("")
        lines.append("**FALLBACK PROCEDURE**:")
        lines.append("- HALT workflow routing until configuration is fixed")
        lines.append("- NOTIFY user of configuration error")
        lines.append("- ACCEPT only Q&A requests until resolved")
        lines.append("")

    lines.append("=" * 80)
    lines.append("")

    return "\n".join(lines)


def main():
    """
    Generate Supervisor instructions with Universal Context Discovery + Workspace Detection.

    Entry point for UserPromptSubmit hook. Processing order:
    1. PRIORITY 0: Workspace context switch detection (Phase 4)
    2. PRIORITY 1: Universal routing with LLM analysis (v0.13.0)
    3. PRIORITY 2: Supervisor instructions with enriched context

    Design Change (v0.13.0):
        - Removed Q&A fast path (pattern matching eliminated)
        - Universal routing for ALL messages
        - Rich context discovery (skills, agents, triads, workflows)
        - Supervisor makes intelligent decisions based on enriched context

    Design Change (Phase 4 - Workspace Architecture):
        - Added workspace context switch detection
        - Manages workspace lifecycle (pause/resume/create)
        - Detects NEW_WORK, CONTINUATION, QA, REFERENCE patterns
        - Auto-pauses workspaces on high-confidence context switches

    Error Handling:
        - Catches all exceptions to prevent hook crashes
        - Falls back to enhanced instructions if detection/discovery fails
        - Logs errors to stderr for debugging
    """
    start_time = time.time()

    try:
        # Read user input from stdin
        input_data = json.load(sys.stdin)
        user_prompt = input_data.get('prompt', '')

        # PRIORITY 0: Workspace context switch detection (Phase 4)
        context_switch_result = detect_and_handle_context_switch(user_prompt)

        if context_switch_result and context_switch_result.get("should_block"):
            # Context switch needs user confirmation - block supervisor routing
            user_message = context_switch_result.get("user_message", "")
            detection_summary = format_context_detection_summary(
                context_switch_result.get("detection_result", {})
            )

            # Output user-facing message + detection summary
            output_message = f"{user_message}\n\n{detection_summary}"
            output_hook_result("UserPromptSubmit", output_message)

            # Capture event for blocked context switch
            from triads.workspace_manager import get_active_workspace
            capture_event(
                subject="user",
                predicate="message_blocked",
                object_data={
                    "hook": "user_prompt_submit",
                    "message_length": len(user_prompt),
                    "context_switch_blocked": True,
                    "classification": context_switch_result.get("detection_result", {}).get("classification"),
                    "confidence": context_switch_result.get("detection_result", {}).get("confidence")
                },
                workspace_id=get_active_workspace(),
                hook_name="user_prompt_submit",
                execution_time_ms=(time.time() - start_time) * 1000,
                metadata={"version": "0.15.0"}
            )
            return

        # Log context switch detection (non-blocking)
        context_switch_detected = False
        workspace_action = "none"
        classification = "unknown"
        confidence = 0

        if context_switch_result:
            workspace_action = context_switch_result.get("workspace_action", "none")
            if workspace_action != "none":
                context_switch_detected = True
                detection_result = context_switch_result.get("detection_result", {})
                classification = detection_result.get("classification", "unknown")
                confidence = detection_result.get("confidence", 0) * 100
                print(
                    f"🔄 Context switch: {classification} "
                    f"({confidence:.0f}% confidence) → {workspace_action}",
                    file=sys.stderr
                )

        # PRIORITY 1: Universal context discovery (ALL messages)
        discovery_result = route_user_request_universal(user_prompt)

        # PRIORITY 2: Format context with discovery result
        supervisor_context = format_supervisor_with_enriched_context(
            user_prompt,
            discovery_result
        )
        output_hook_result("UserPromptSubmit", supervisor_context)

        # Capture successful execution event
        from triads.workspace_manager import get_active_workspace
        capture_event(
            subject="user",
            predicate="message_submitted",
            object_data={
                "hook": "user_prompt_submit",
                "message_length": len(user_prompt),
                "context_switch_detected": context_switch_detected,
                "workspace_action": workspace_action,
                "classification": classification,
                "routing_decision": discovery_result.get("recommended_action") if discovery_result else None
            },
            workspace_id=get_active_workspace(),
            hook_name="user_prompt_submit",
            execution_time_ms=(time.time() - start_time) * 1000,
            metadata={"version": "0.15.0"}
        )

    except Exception as e:
        # Critical error - hook should never crash
        print(f"ERROR in UserPromptSubmit hook: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()

        # Capture error event
        capture_event(
            subject="hook",
            predicate="failed",
            object_data={
                "hook": "user_prompt_submit",
                "error": str(e),
                "error_type": type(e).__name__
            },
            hook_name="user_prompt_submit",
            execution_time_ms=(time.time() - start_time) * 1000,
            metadata={"version": "0.15.0"}
        )

        # Output enhanced fallback instructions
        fallback = format_supervisor_instructions_enhanced()
        output_hook_result("UserPromptSubmit", fallback)


if __name__ == "__main__":
    main()
