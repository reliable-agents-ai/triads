#!/usr/bin/env python3
"""
UserPromptSubmit Hook: Inject Supervisor Instructions

This hook runs before each user message and injects Supervisor instructions.

Refactored to use Tool Abstraction Layer (Phase 7).

Hook Type: UserPromptSubmit
Configured in: hooks/hooks.json (plugin)

Previous implementation: 261 lines with workflow loading logic
Current implementation: ~70 lines with cleaner structure
"""

import json
import sys
from pathlib import Path

# Add src and hooks to path for imports
repo_root = Path(__file__).parent.parent
if str(repo_root / "src") not in sys.path:
    sys.path.insert(0, str(repo_root / "src"))
if str(repo_root / "hooks") not in sys.path:
    sys.path.insert(0, str(repo_root / "hooks"))

# Import common utilities
from common import output_hook_result, get_project_dir  # noqa: E402


def detect_work_request(user_message: str) -> dict:
    """
    Detect if user message is a work request and classify it.

    Distinguishes between Q&A requests (informational) and work requests
    (action required). Work requests trigger triad orchestration.

    Args:
        user_message: User's message to classify

    Returns:
        Dict with classification if work request:
            {'type': str, 'triad': str, 'original_request': str}
        Empty dict if Q&A or unclear

    Examples:
        >>> detect_work_request("Implement OAuth2")
        {'type': 'feature', 'triad': 'idea-validation', 'original_request': 'Implement OAuth2'}

        >>> detect_work_request("What is OAuth2?")
        {}

        >>> detect_work_request("Fix router crash")
        {'type': 'bug', 'triad': 'idea-validation', 'original_request': 'Fix router crash'}
    """
    if not user_message or not isinstance(user_message, str):
        return {}

    message_lower = user_message.lower()

    # Q&A indicators (NOT work requests)
    qa_patterns = [
        'what is', 'what are', 'what does',
        'how does', 'how do', 'how to',
        'explain', 'tell me about', 'tell me how',
        'can you explain', 'could you explain',
        'describe', 'why is', 'why does',
        'when should', 'where is', 'where does',
        'who is', 'which is'
    ]

    # Check if Q&A (return empty dict - not a work request)
    for pattern in qa_patterns:
        if pattern in message_lower:
            return {}

    # Work indicators by type
    work_patterns = {
        'feature': [
            'implement', 'add', 'create', 'build',
            'let\'s implement', 'let\'s add', 'let\'s create', 'let\'s build',
            'please implement', 'please add', 'please create',
            'we need to implement', 'we need to add',
            'develop', 'make'
        ],
        'bug': [
            'fix', 'bug', 'error', 'broken', 'issue',
            'crash', 'failing', 'not working',
            'resolve', 'correct', 'repair'
        ],
        'refactor': [
            'refactor', 'cleanup', 'clean up', 'improve',
            'consolidate', 'reorganize', 'restructure',
            'messy code', 'technical debt',
            'simplify', 'optimize'
        ],
        'design': [
            'design', 'architecture', 'how should we',
            'what approach', 'which approach',
            'architect', 'structure for'
        ],
        'release': [
            'deploy', 'release', 'publish',
            'ship', 'launch'
        ]
    }

    # Check for work patterns
    for work_type, patterns in work_patterns.items():
        for pattern in patterns:
            if pattern in message_lower:
                # Per ADR-007: ALL work enters through idea-validation
                return {
                    'type': work_type,
                    'triad': 'idea-validation',
                    'original_request': user_message
                }

    # No clear classification - return empty dict
    return {}


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
    lines.append("**ROE 1: TRIAGE PROTOCOL**")
    lines.append("- CLASSIFY every user message as Q&A OR work request")
    lines.append("")
    lines.append("**Q&A Indicators (NOT work requests)**:")
    lines.append("- what is, what are, what does")
    lines.append("- how does, how do, how to")
    lines.append("- explain, tell me about, describe")
    lines.append("- can you explain, could you explain")
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
    lines.append("- Triads are ATOMIC units")
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


def main():
    """
    Generate Supervisor instructions for user prompt.

    Entry point for UserPromptSubmit hook. Generates and outputs
    Supervisor standing orders including work request detection protocol.

    Error Handling:
        - Catches all exceptions to prevent hook crashes
        - Falls back to basic instructions if config fails
        - Logs errors to stderr for debugging
    """
    try:
        # Generate Supervisor instructions (with built-in fallback handling)
        supervisor_context = format_supervisor_instructions()

        # Output in Claude Code hook format
        output_hook_result("UserPromptSubmit", supervisor_context)

    except Exception as e:
        # Critical error - hook should never crash
        # Log to stderr
        import sys
        print(f"ERROR in UserPromptSubmit hook: {e}", file=sys.stderr)

        # Output minimal fallback instructions
        fallback = """
===============================================================================
# SUPERVISOR MODE (FALLBACK)
===============================================================================

**ERROR**: Hook encountered error while loading configuration.

**FALLBACK MODE**:
- Provide Q&A responses for user questions
- For work requests: Ask user to check .claude/settings.json configuration
- Report this error to user for investigation

**Error Details**: See stderr for technical details
===============================================================================
"""
        output_hook_result("UserPromptSubmit", fallback)


if __name__ == "__main__":
    main()
