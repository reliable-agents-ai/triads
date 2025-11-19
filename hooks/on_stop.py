#!/usr/bin/env python3
"""
Stop Hook: Orchestrator for post-response processing.

This hook runs after Claude finishes responding.
Delegates to specialized handlers for:
- Graph updates and validation
- Knowledge management and experience learning
- Triad handoffs
- Workflow completion
- Workspace lifecycle management

Hook Type: Stop
Configured in: hooks/hooks.json (plugin)

Architecture: Orchestrator Pattern
- Minimal orchestration logic (< 200 lines)
- Delegates to single-responsibility handlers
- Each handler is independently testable
- SOLID principles throughout
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path

# Use shared path setup utility
from setup_paths import setup_import_paths
setup_import_paths()

# Import event capture utilities
from event_capture_utils import capture_hook_execution, capture_hook_error  # noqa: E402

# Import specialized handlers
from handlers.graph_update_handler import GraphUpdateHandler  # noqa: E402
from handlers.km_validation_handler import KMValidationHandler  # noqa: E402
from handlers.handoff_handler import HandoffHandler  # noqa: E402
from handlers.workflow_completion_handler import WorkflowCompletionHandler  # noqa: E402
from handlers.workspace_pause_handler import WorkspacePauseHandler  # noqa: E402

# Import KM modules for issue detection and auto-invocation
from triads.km.detection import detect_km_issues, update_km_queue  # noqa: E402
from triads.km.formatting import format_km_notification, write_km_status_file  # noqa: E402
from triads.km.auto_invocation import process_and_queue_invocations  # noqa: E402
from triads.workspace_manager import get_active_workspace  # noqa: E402

# Import safe I/O for graph operations
from triads.hooks.safe_io import safe_load_json_file, safe_save_json_file  # noqa: E402


def _extract_text_from_content_item(item):
    """
    Extract text from a single content item.

    Args:
        item: Content item (dict with 'text' key or string)

    Returns:
        str or None: Extracted text or None if not extractable
    """
    if isinstance(item, dict) and 'text' in item:
        return item['text']
    elif isinstance(item, str):
        return item
    return None


def _get_content_from_entry(entry):
    """
    Get content field from transcript entry.

    Args:
        entry: Dictionary representing a transcript entry

    Returns:
        Content field (string, list, or None)
    """
    if 'message' in entry and 'content' in entry['message']:
        return entry['message']['content']
    elif 'content' in entry:
        return entry['content']
    return None


def _extract_content_from_entry(entry):
    """
    Extract content from a transcript entry.

    Args:
        entry: Dictionary representing a transcript entry

    Returns:
        list: List of text strings extracted from content
    """
    content = _get_content_from_entry(entry)
    if not content:
        return []

    # Handle different content formats
    if isinstance(content, str):
        return [content]

    if isinstance(content, list):
        texts = []
        for item in content:
            text = _extract_text_from_content_item(item)
            if text:
                texts.append(text)
        return texts

    return []


def _parse_transcript_file(transcript_path):
    """
    Parse JSONL transcript file and extract all text.

    Args:
        transcript_path: Path to transcript JSONL file

    Returns:
        str: Joined text from all entries
    """
    with open(transcript_path, 'r') as f:
        transcript_lines = f.readlines()

    all_text = []
    for line in transcript_lines:
        try:
            entry = json.loads(line)
            texts = _extract_content_from_entry(entry)
            all_text.extend(texts)
        except json.JSONDecodeError:
            continue

    return '\n'.join(all_text)


def read_conversation_text() -> str:
    """
    Read conversation text from stdin.

    Handles two input formats:
    1. JSON with transcript_path: Read transcript from JSONL file
    2. Plain text: Use input directly

    Returns:
        str: Full conversation text
    """
    input_text = sys.stdin.read()

    # Try to parse as JSON first
    try:
        input_data = json.loads(input_text)

        # Check if we have a transcript_path
        transcript_path = input_data.get('transcript_path')
        if transcript_path and Path(transcript_path).exists():
            return _parse_transcript_file(transcript_path)
        else:
            # Use input data as text
            return str(input_data)

    except json.JSONDecodeError:
        # Input is plain text
        return input_text


def log_violations(violations):
    """
    Log constitutional violations to violations file.

    Args:
        violations: List of violation dictionaries
    """
    if not violations:
        return

    violations_file = Path('.claude/constitutional/violations.json')
    violations_file.parent.mkdir(parents=True, exist_ok=True)

    # Load existing violations
    existing_violations = []
    if violations_file.exists():
        existing_violations = safe_load_json_file(violations_file, default=[])

    # Add new violations with timestamps
    for violation in violations:
        violation['detected_at'] = datetime.now().isoformat()
        violation['hook'] = 'on_stop'
        existing_violations.append(violation)

    # Save updated violations
    safe_save_json_file(violations_file, existing_violations)


def _print_violation_summary(violations):
    """
    Print summary of constitutional violations.

    Args:
        violations: List of violation dictionaries
    """
    print(f"   ⚠️  {len(violations)} pre-flight violations", file=sys.stderr)

    critical = sum(1 for v in violations if v.get('severity') == 'critical')
    high = sum(1 for v in violations if v.get('severity') == 'high')
    medium = sum(1 for v in violations if v.get('severity') == 'medium')
    print(f"   Critical: {critical}, High: {high}, Medium: {medium}", file=sys.stderr)


def _process_graph_km_issues(graphs_updated):
    """
    Detect KM issues and auto-invoke system agents for updated graphs.

    Args:
        graphs_updated: List of triad names that were updated
    """
    for triad in graphs_updated:
        graph_data = safe_load_json_file(
            Path(f'.claude/graphs/{triad}_graph.json'),
            default={"nodes": [], "links": []}
        )

        issues = detect_km_issues(graph_data, triad)
        if not issues:
            continue

        # Update KM queue and show notification
        update_km_queue(issues)
        notification = format_km_notification(issues)
        if notification:
            print(f"\n{notification}", file=sys.stderr)

        # Auto-invoke system agents for high-priority issues
        try:
            new_invocations, total = process_and_queue_invocations(issues)
            if new_invocations:
                print(
                    f"🤖 Auto-queued {len(new_invocations)} system agent(s) "
                    f"for high-priority issues",
                    file=sys.stderr
                )
        except Exception as e:
            print(f"⚠️  Auto-invocation warning: {e}", file=sys.stderr)


def _process_km_lessons(km_result):
    """
    Add extracted lessons to appropriate triad graphs.

    Args:
        km_result: Dictionary with lessons_by_triad and other KM data
    """
    for triad, triad_lessons in km_result['lessons_by_triad'].items():
        graph_data = safe_load_json_file(
            Path(f'.claude/graphs/{triad}_graph.json'),
            default={"directed": True, "nodes": [], "links": [], "_meta": {}}
        )

        # Add lessons that don't already exist
        added_count = 0
        for lesson in triad_lessons:
            node_id = lesson['id']
            existing = [n for n in graph_data['nodes'] if n.get('id') == node_id]
            if not existing:
                graph_data['nodes'].append(lesson)
                added_count += 1

        if added_count > 0:
            # Update metadata and save
            graph_data['_meta']['updated_at'] = datetime.now().isoformat()
            graph_data['_meta']['node_count'] = len(graph_data['nodes'])
            safe_save_json_file(Path(f'.claude/graphs/{triad}_graph.json'), graph_data)
            print(f"   ✓ Added {added_count} lesson(s) to {triad} graph", file=sys.stderr)


def _handle_graph_updates(conversation_text):
    """
    Process Phase 2: Graph Updates.

    Args:
        conversation_text: Full conversation text

    Returns:
        dict: Graph update results
    """
    print("\n🔄 Processing Graph Updates...", file=sys.stderr)

    graph_handler = GraphUpdateHandler()
    graph_result = graph_handler.process(conversation_text, agent_name="unknown")

    if graph_result['count'] > 0:
        print(f"   Found {graph_result['count']} [GRAPH_UPDATE] blocks", file=sys.stderr)
        print(f"   Updated {len(graph_result['graphs_updated'])} graph(s): {', '.join(graph_result['graphs_updated'])}", file=sys.stderr)

        # Log and summarize constitutional violations
        if graph_result['violations']:
            log_violations(graph_result['violations'])
            _print_violation_summary(graph_result['violations'])
        else:
            print("   ✓ All graph updates have valid pre-flight checks", file=sys.stderr)

        # Detect KM issues and auto-invoke system agents
        _process_graph_km_issues(graph_result['graphs_updated'])

        # Write KM status file
        try:
            write_km_status_file()
        except Exception as e:
            print(f"⚠️  Error writing KM status file: {e}", file=sys.stderr)
    else:
        print("   No graph updates found", file=sys.stderr)

    return graph_result


def _handle_km_processing(conversation_text, updates_by_triad):
    """
    Process Phase 3: Knowledge Management (Experience Learning).

    Args:
        conversation_text: Full conversation text
        updates_by_triad: Graph updates organized by triad

    Returns:
        dict: KM processing results
    """
    print("\n🧠 Processing Experience-Based Learning...", file=sys.stderr)

    km_handler = KMValidationHandler()
    km_result = km_handler.process(conversation_text, updates_by_triad)

    if km_result['count'] > 0:
        print(f"   Found {km_result['count']} lesson(s)", file=sys.stderr)
        print(f"   Explicit: {km_result['explicit_count']}, "
              f"Corrections: {km_result['correction_count']}, "
              f"Repeated: {km_result['repeated_count']}", file=sys.stderr)

        # Add lessons to graphs
        _process_km_lessons(km_result)

        # Show summary of uncertain lessons
        uncertain_lessons = [l for l in km_result['lessons'] if l.get('confidence', 1.0) < 0.70]
        if uncertain_lessons:
            print(f"   ⚠️  {len(uncertain_lessons)} uncertain lesson(s) (confidence < 70%)", file=sys.stderr)
            print("   Use /knowledge-review-uncertain to review", file=sys.stderr)
    else:
        print("   No lessons extracted", file=sys.stderr)

    return km_result


def _handle_handoffs(conversation_text):
    """
    Process Phase 4: Handoff Processing.

    Args:
        conversation_text: Full conversation text

    Returns:
        dict: Handoff processing results
    """
    print("\n🔗 Processing Handoff Requests...", file=sys.stderr)

    handoff_handler = HandoffHandler()
    handoff_result = handoff_handler.process(conversation_text)

    if handoff_result['count'] > 0:
        print(f"   Found {handoff_result['count']} handoff request(s)", file=sys.stderr)
        if handoff_result['success']:
            print(f"   ✓ All {handoff_result['queued']} handoff(s) queued successfully", file=sys.stderr)
        else:
            print(f"   ⚠️  {len(handoff_result['errors'])} handoff(s) failed", file=sys.stderr)
    else:
        print("   No handoff requests found", file=sys.stderr)

    return handoff_result


def _handle_workflow_completions(conversation_text):
    """
    Process Phase 5: Workflow Completion.

    Args:
        conversation_text: Full conversation text

    Returns:
        dict: Workflow completion results
    """
    print("\n🏁 Processing Workflow Completions...", file=sys.stderr)

    completion_handler = WorkflowCompletionHandler()
    completion_result = completion_handler.process(conversation_text)

    if completion_result['count'] > 0:
        print(f"   Found {completion_result['count']} workflow completion(s)", file=sys.stderr)
        if completion_result['success']:
            print(f"   ✓ All {completion_result['recorded']} completion(s) recorded", file=sys.stderr)
        else:
            print(f"   ⚠️  {len(completion_result['errors'])} completion(s) failed", file=sys.stderr)
    else:
        print("   No workflow completions found", file=sys.stderr)

    return completion_result


def _handle_workspace_pause():
    """
    Process Phase 6: Workspace Auto-Pause.

    Returns:
        dict: Workspace pause results
    """
    print("\n💾 Workspace Auto-Pause Check...", file=sys.stderr)

    pause_handler = WorkspacePauseHandler()
    pause_result = pause_handler.process()

    if pause_result['paused']:
        print(f"   ⏸️  Auto-paused workspace: {pause_result['workspace_id']}", file=sys.stderr)
    else:
        print(f"   {pause_result.get('reason', 'No pause needed')}", file=sys.stderr)

    return pause_result


def main():
    """
    Main orchestrator: delegates to specialized handlers.

    Process flow:
    1. Read conversation text
    2. Graph updates (GraphUpdateHandler)
       - Extract [GRAPH_UPDATE] and [PRE_FLIGHT_CHECK] blocks
       - Validate quality gates
       - Apply updates to graphs
       - Detect KM issues and auto-invoke system agents
    3. Knowledge management (KMValidationHandler)
       - Extract [PROCESS_KNOWLEDGE] blocks
       - Detect user corrections and repeated mistakes
       - Create process knowledge nodes
       - Add to graphs with confidence scores
    4. Outcome detection & confidence updates (inline for now)
    5. Handoff processing (HandoffHandler)
    6. Workflow completion (WorkflowCompletionHandler)
    7. Workspace auto-pause (WorkspacePauseHandler)
    8. Event capture
    """
    start_time = time.time()

    try:
        # ====================================================================
        # Phase 1: Read Input
        # ====================================================================
        conversation_text = read_conversation_text()

        if not conversation_text:
            # No text to process - exit silently
            return

        print(f"\n{'='*80}", file=sys.stderr)
        print("📊 Stop Hook Processing (Orchestrator)", file=sys.stderr)
        print(f"{'='*80}", file=sys.stderr)

        # ====================================================================
        # Phase 2-6: Delegate to Specialized Handlers
        # ====================================================================
        graph_result = _handle_graph_updates(conversation_text)
        km_result = _handle_km_processing(conversation_text, graph_result.get('updates_by_triad', {}))
        handoff_result = _handle_handoffs(conversation_text)
        completion_result = _handle_workflow_completions(conversation_text)
        pause_result = _handle_workspace_pause()

        print(f"\n{'='*80}", file=sys.stderr)

        # ====================================================================
        # Phase 7: Capture Event
        # ====================================================================
        capture_hook_execution(
            hook_name="on_stop",
            start_time=start_time,
            object_data={
                "graph_updates": graph_result['count'],
                "graphs_updated": len(graph_result['graphs_updated']),
                "lessons_extracted": km_result['count'],
                "handoffs_queued": handoff_result.get('queued', 0),
                "workflows_completed": completion_result.get('recorded', 0),
                "workspace_paused": pause_result['paused'],
                "violations": len(graph_result['violations'])
            },
            workspace_id=get_active_workspace(),
            predicate="executed"
        )

    except Exception as e:
        # Capture error event
        capture_hook_error(
            hook_name="on_stop",
            start_time=start_time,
            error=e
        )

        # Print error for debugging
        print(f"\n❌ Stop Hook Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)


if __name__ == "__main__":
    main()
