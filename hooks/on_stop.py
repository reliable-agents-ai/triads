#!/usr/bin/env python3
"""
Stop Hook: Update Knowledge Graphs

This hook runs after Claude finishes responding.
It scans the response for [GRAPH_UPDATE] blocks and updates knowledge graphs.

Hook Type: Stop
Configured in: hooks/hooks.json (plugin)

Why Stop instead of PostToolUse?
PostToolUse hooks are currently broken in Claude Code (known bug, multiple GitHub issues).
Stop hooks work reliably and achieve the same goal - automatic graph updates.

Data Flow:
1. Claude finishes responding
2. Stop hook fires
3. Hook receives response text or transcript path
4. Scan for [GRAPH_UPDATE] blocks
5. Group updates by triad
6. Update each triad's graph
7. Save graphs to disk
8. Detect KM issues and update queue
"""

import glob
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# Add paths for KM imports - plugin-aware
plugin_root = os.environ.get('CLAUDE_PLUGIN_ROOT')
if plugin_root:
    # Plugin mode: KM modules in plugin src/
    sys.path.insert(0, str(Path(plugin_root) / "src"))
else:
    # Development mode: KM modules in src/triads
    repo_root = Path(__file__).parent.parent
    sys.path.insert(0, str(repo_root / "src"))

# Import from triads package (works in both plugin and dev mode)
from triads.km.auto_invocation import process_and_queue_invocations  # noqa: E402
from triads.km.confidence import (  # noqa: E402
    calculate_initial_confidence,
    assign_status,
    validate_confidence_value,
)
from triads.km.detection import detect_km_issues, update_km_queue  # noqa: E402
from triads.km.formatting import format_km_notification, write_km_status_file  # noqa: E402
from triads.hooks.safe_io import safe_load_json_file, safe_save_json_file  # noqa: E402

# ============================================================================
# Graph Update Extraction
# ============================================================================

def extract_pre_flight_checks_from_text(text):
    """
    Extract [PRE_FLIGHT_CHECK] blocks from text.

    Args:
        text: String containing [PRE_FLIGHT_CHECK]...[/PRE_FLIGHT_CHECK] blocks

    Returns:
        List of pre-flight check dictionaries
    """
    pattern = r'\[PRE_FLIGHT_CHECK\](.*?)\[/PRE_FLIGHT_CHECK\]'
    matches = re.findall(pattern, text, re.DOTALL)

    checks = []
    for match in matches:
        check = {'checklist_items': {}}
        for line in match.strip().split('\n'):
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()

                # Handle checklist items specially
                if key == 'checklist_items':
                    continue  # Skip the header
                elif line.startswith('  - '):
                    # Parse checklist item
                    item_line = line[4:]  # Remove "  - "
                    if '[' in item_line:
                        # Extract item name and status
                        item_parts = item_line.split('[')
                        item_name = item_parts[0].split(':')[0].strip()
                        status = 'PASS' if '✅' in item_line else 'FAIL'
                        check['checklist_items'][item_name] = {
                            'status': status,
                            'detail': item_parts[0].split(':', 1)[1].strip() if ':' in item_parts[0] else ''
                        }
                else:
                    # Regular key-value
                    # Parse JSON arrays
                    if value.startswith('['):
                        try:
                            value = json.loads(value)
                        except json.JSONDecodeError:
                            pass

                    check[key] = value

        checks.append(check)

    return checks


def extract_graph_updates_from_text(text):
    """
    Extract [GRAPH_UPDATE] blocks from any text.

    Args:
        text: String containing [GRAPH_UPDATE]...[/GRAPH_UPDATE] blocks

    Returns:
        List of update dictionaries
    """
    pattern = r'\[GRAPH_UPDATE\](.*?)\[/GRAPH_UPDATE\]'
    matches = re.findall(pattern, text, re.DOTALL)

    updates = []
    for match in matches:
        update = {}
        for line in match.strip().split('\n'):
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()

                # Parse JSON arrays
                if value.startswith('['):
                    try:
                        value = json.loads(value)
                    except json.JSONDecodeError:
                        pass

                # Parse confidence as float
                if key == 'confidence':
                    try:
                        value = float(value)
                    except ValueError:
                        pass

                update[key] = value

        if update:
            updates.append(update)

    return updates

# ============================================================================
# Pre-Flight Check Validation
# ============================================================================

def validate_pre_flight_checks(text, updates):
    """
    Validate that all graph updates have corresponding pre-flight checks.

    Args:
        text: Full text to search for pre-flight checks
        updates: List of graph update dictionaries

    Returns:
        List of violation dictionaries
    """
    if not updates:
        return []

    pre_flight_checks = extract_pre_flight_checks_from_text(text)

    # Build map of node_id -> pre-flight check
    checks_by_node = {}
    for check in pre_flight_checks:
        node_id = check.get('node_id')
        if node_id:
            checks_by_node[node_id] = check

    violations = []

    for update in updates:
        node_id = update.get('node_id')
        if not node_id:
            continue

        # Check 1: Pre-flight check exists
        if node_id not in checks_by_node:
            violations.append({
                'type': 'missing_pre_flight_check',
                'node_id': node_id,
                'node_type': update.get('node_type', 'Unknown'),
                'severity': 'high',
                'principle': 'proactive_quality_assurance',
                'message': f'[GRAPH_UPDATE] for {node_id} has no [PRE_FLIGHT_CHECK]',
                'remediation': 'Add [PRE_FLIGHT_CHECK] block before [GRAPH_UPDATE]'
            })
            continue

        check = checks_by_node[node_id]

        # Check 2: Verification status is PASSED
        verification_status = check.get('verification_status', '').upper()
        if verification_status != 'PASSED':
            violations.append({
                'type': 'failed_pre_flight_verification',
                'node_id': node_id,
                'node_type': update.get('node_type', 'Unknown'),
                'severity': 'critical',
                'principle': 'proactive_quality_assurance',
                'verification_status': verification_status,
                'message': f'Pre-flight check for {node_id} status: {verification_status} (expected: PASSED)',
                'remediation': 'Fix quality issues or convert to Uncertainty node'
            })

        # Check 3: All required checklist items are present
        required_items = [
            'property_count',
            'confidence_check',
            'evidence_quality',
            'assumptions_handled',
            'node_type_correct'
        ]

        checklist = check.get('checklist_items', {})
        for item in required_items:
            if item not in checklist:
                violations.append({
                    'type': 'incomplete_pre_flight_checklist',
                    'node_id': node_id,
                    'node_type': update.get('node_type', 'Unknown'),
                    'severity': 'medium',
                    'principle': 'proactive_quality_assurance',
                    'missing_item': item,
                    'message': f'Pre-flight check for {node_id} missing checklist item: {item}',
                    'remediation': f'Add {item} check to pre-flight checklist'
                })

        # Check 4: All checklist items passed (if verification_status is PASSED)
        if verification_status == 'PASSED':
            failed_items = [
                name for name, details in checklist.items()
                if isinstance(details, dict) and details.get('status') == 'FAIL'
            ]
            if failed_items:
                violations.append({
                    'type': 'inconsistent_pre_flight_status',
                    'node_id': node_id,
                    'node_type': update.get('node_type', 'Unknown'),
                    'severity': 'high',
                    'principle': 'proactive_quality_assurance',
                    'failed_items': failed_items,
                    'message': f'Pre-flight check claims PASSED but items failed: {failed_items}',
                    'remediation': 'Fix failed items or set verification_status to FAILED'
                })

    return violations


# ============================================================================
# Triad Identification
# ============================================================================

def get_triad_from_update(update):
    """
    Determine which triad an update belongs to.

    Strategy:
    1. Check if update has 'triad' field explicitly
    2. Check if update has 'created_by' field, look up agent's triad
    3. Check node_id prefix (e.g., "discovery_node_001" -> "discovery")
    4. Default to 'default' triad

    Args:
        update: Update dictionary from [GRAPH_UPDATE] block

    Returns:
        triad_name: String name of triad
    """
    # Direct triad field
    if 'triad' in update:
        return update['triad']

    # Infer from agent
    if 'created_by' in update:
        agent_name = update['created_by']
        triad = lookup_agent_triad(agent_name)
        if triad:
            return triad

    # Infer from node_id prefix
    node_id = update.get('node_id', '')
    if '_' in node_id:
        potential_triad = node_id.split('_')[0]
        if is_valid_triad(potential_triad):
            return potential_triad

    # Default
    return 'default'

def lookup_agent_triad(agent_name):
    """
    Find which triad an agent belongs to by searching for its file.

    Args:
        agent_name: Name of the agent

    Returns:
        triad_name: String name of triad, or None if not found
    """
    pattern = f".claude/agents/**/{agent_name}.md"
    matches = glob.glob(pattern, recursive=True)

    if matches:
        agent_file = Path(matches[0])

        # Parse frontmatter for triad field
        try:
            with open(agent_file, 'r') as f:
                in_frontmatter = False
                for line in f:
                    line = line.strip()
                    if line == '---':
                        in_frontmatter = not in_frontmatter
                        continue
                    if in_frontmatter and line.startswith('triad:'):
                        return line.split(':', 1)[1].strip()
        except Exception:
            pass

        # Fallback to parent directory name
        return agent_file.parent.name

    return None

def is_valid_triad(name):
    """
    Check if a triad exists.

    Args:
        name: Potential triad name

    Returns:
        bool: True if triad exists
    """
    # Check if graph file exists OR agent directory exists
    return Path(f'.claude/graphs/{name}_graph.json').exists() or \
           Path(f'.claude/agents/{name}').is_dir()

# ============================================================================
# Knowledge Graph Management (Reused from post_tool_use.py)
# ============================================================================

def load_graph(triad_name):
    """Load a triad's knowledge graph or create a new one."""
    graphs_dir = Path('.claude/graphs')
    graphs_dir.mkdir(parents=True, exist_ok=True)

    graph_file = graphs_dir / f"{triad_name}_graph.json"

    # Use safe_load_json_file with default structure
    return safe_load_json_file(graph_file, default={
        "directed": True,
        "nodes": [],
        "links": [],
        "_meta": {
            "triad_name": triad_name,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "node_count": 0,
            "edge_count": 0
        }
    })

def save_graph(graph_data, triad_name):
    """Save a knowledge graph to disk."""
    graphs_dir = Path('.claude/graphs')
    graphs_dir.mkdir(parents=True, exist_ok=True)

    graph_file = graphs_dir / f"{triad_name}_graph.json"

    # Update metadata
    graph_data['_meta']['updated_at'] = datetime.now().isoformat()
    graph_data['_meta']['node_count'] = len(graph_data['nodes'])
    graph_data['_meta']['edge_count'] = len(graph_data['links'])

    # Use safe_save_json_file with atomic write
    if not safe_save_json_file(graph_file, graph_data):
        print(f"❌ Failed to save {triad_name} graph", file=sys.stderr)

def apply_update(graph_data, update, agent_name):
    """
    Apply a single graph update to the graph data.

    Args:
        graph_data: The graph dictionary
        update: The update dictionary from [GRAPH_UPDATE] block
        agent_name: Name of the agent making the update

    Returns:
        Updated graph_data
    """
    update_type = update.get('type', '')

    if update_type == 'add_node':
        # Check if node already exists
        node_id = update.get('node_id')
        existing = [n for n in graph_data['nodes'] if n.get('id') == node_id]

        if existing:
            print(f"⚠️  Node {node_id} already exists, skipping", file=sys.stderr)
            return graph_data

        # Create new node
        node = {
            'id': node_id,
            'type': update.get('node_type', 'Entity'),
            'label': update.get('label', node_id),
            'description': update.get('description', ''),
            'confidence': update.get('confidence', 1.0),
            'evidence': update.get('evidence', ''),
            'created_by': agent_name,
            'created_at': datetime.now().isoformat()
        }

        # Add optional fields
        for key in ['alternatives', 'rationale', 'status', 'priority']:
            if key in update:
                node[key] = update[key]

        graph_data['nodes'].append(node)
        print(f"✓ Added node: {node_id} ({node['type']})", file=sys.stderr)

    elif update_type == 'update_node':
        # Find and update existing node
        node_id = update.get('node_id')
        node = next((n for n in graph_data['nodes'] if n.get('id') == node_id), None)

        if not node:
            print(f"⚠️  Node {node_id} not found, skipping", file=sys.stderr)
            return graph_data

        # Update fields (preserve original created_by and created_at)
        for key, value in update.items():
            if key not in ['type', 'node_id']:
                node[key] = value

        node['updated_by'] = agent_name
        node['updated_at'] = datetime.now().isoformat()

        print(f"✓ Updated node: {node_id}", file=sys.stderr)

    elif update_type == 'add_edge':
        # Create new edge
        source = update.get('source')
        target = update.get('target')
        edge_type = update.get('edge_type', 'relates_to')

        if not source or not target:
            print("⚠️  Missing source or target for edge", file=sys.stderr)
            return graph_data

        # Check if edge already exists
        existing = [
            e for e in graph_data['links']
            if e.get('source') == source and e.get('target') == target and e.get('key') == edge_type
        ]

        if existing:
            print(f"⚠️  Edge {source} -> {target} already exists", file=sys.stderr)
            return graph_data

        edge = {
            'source': source,
            'target': target,
            'key': edge_type,
            'rationale': update.get('rationale', ''),
            'created_by': agent_name,
            'created_at': datetime.now().isoformat()
        }

        graph_data['links'].append(edge)
        print(f"✓ Added edge: {source} -> {target} ({edge_type})", file=sys.stderr)

    elif update_type == 'update_edge':
        # Find and update existing edge
        source = update.get('source')
        target = update.get('target')
        edge_type = update.get('edge_type', 'relates_to')

        edge = next(
            (e for e in graph_data['links']
             if e.get('source') == source and e.get('target') == target and e.get('key') == edge_type),  # noqa: E501
            None
        )

        if not edge:
            print(f"⚠️  Edge {source} -> {target} not found", file=sys.stderr)
            return graph_data

        # Update fields
        for key, value in update.items():
            if key not in ['type', 'source', 'target', 'edge_type']:
                edge[key] = value

        edge['updated_by'] = agent_name
        edge['updated_at'] = datetime.now().isoformat()

        print(f"✓ Updated edge: {source} -> {target}", file=sys.stderr)

    else:
        print(f"⚠️  Unknown update type: {update_type}", file=sys.stderr)

    return graph_data

# ============================================================================
# Lesson Extraction (Experience-Based Learning)
# ============================================================================

def extract_process_knowledge_blocks(text):
    """
    Extract [PROCESS_KNOWLEDGE] blocks from conversation.

    These are explicitly formatted lessons agents create during conversation.

    Args:
        text: Conversation text

    Returns:
        List of process knowledge dictionaries
    """
    pattern = r'\[PROCESS_KNOWLEDGE\](.*?)\[/PROCESS_KNOWLEDGE\]'
    matches = re.findall(pattern, text, re.DOTALL)

    lessons = []
    for match in matches:
        lesson = parse_process_knowledge_block(match)
        if lesson:
            # Mark as explicit PROCESS_KNOWLEDGE block (for confidence calculation)
            lesson['type'] = 'process_knowledge_block'
            lessons.append(lesson)

    return lessons

def parse_process_knowledge_block(block_text):
    """
    Parse a PROCESS_KNOWLEDGE block into structured data.

    Expected format:
    type: checklist|pattern|warning|requirement
    label: Human-readable label
    priority: CRITICAL|HIGH|MEDIUM|LOW
    process_type: checklist|pattern|warning|requirement
    trigger_conditions:
      tool_names: [tool1, tool2]
      file_patterns: [pattern1, pattern2]
      action_keywords: [keyword1, keyword2]
    checklist:
      - item: Description
        required: true|false
        file: path/to/file

    Args:
        block_text: Text inside PROCESS_KNOWLEDGE block

    Returns:
        Dictionary with process knowledge, or None if parse fails
    """
    lesson = {
        'type': 'Concept',
        'process_type': 'checklist',  # default
        'priority': 'MEDIUM',  # default
        'trigger_conditions': {
            'tool_names': [],
            'file_patterns': [],
            'action_keywords': [],
            'context_keywords': [],
            'triad_names': []
        }
    }

    current_section = None
    checklist_items = []

    for line in block_text.strip().split('\n'):
        # Keep original line for indentation check
        original_line = line
        line = line.strip()

        if not line or line.startswith('#'):
            continue

        # Section headers (only non-indented lines ending with :)
        if line.endswith(':') and ':' not in line[:-1] and not original_line.startswith((' ', '\t')):
            current_section = line[:-1].lower()
            continue

        # Parse trigger_conditions (indented sub-keys)
        if current_section == 'trigger_conditions' and original_line.startswith((' ', '\t')):
            if 'tool_names:' in line:
                value = line.split(':', 1)[1].strip()
                lesson['trigger_conditions']['tool_names'] = json.loads(value)
            elif 'file_patterns:' in line:
                value = line.split(':', 1)[1].strip()
                lesson['trigger_conditions']['file_patterns'] = json.loads(value)
            elif 'action_keywords:' in line:
                value = line.split(':', 1)[1].strip()
                lesson['trigger_conditions']['action_keywords'] = json.loads(value)
            elif 'context_keywords:' in line:
                value = line.split(':', 1)[1].strip()
                lesson['trigger_conditions']['context_keywords'] = json.loads(value)
            elif 'triad_names:' in line:
                value = line.split(':', 1)[1].strip()
                lesson['trigger_conditions']['triad_names'] = json.loads(value)
            continue

        # Parse key: value (for top-level fields only)
        if ':' in line and current_section not in ['checklist', 'pattern', 'warning', 'trigger_conditions']:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()

            if key == 'type':
                lesson['process_type'] = value
            elif key == 'label':
                lesson['label'] = value
            elif key == 'priority':
                lesson['priority'] = value.upper()
            elif key == 'description':
                lesson['description'] = value
            elif key == 'triad':
                lesson['triad'] = value

        # Parse checklist items
        elif current_section == 'checklist':
            if line.startswith('-') or line.startswith('•'):
                item_text = line[1:].strip()
                item = {'item': item_text, 'required': True}

                # Parse item properties
                if 'required:' in item_text:
                    parts = item_text.split('required:')
                    item['item'] = parts[0].strip()
                    item['required'] = 'true' in parts[1].lower()

                if 'file:' in item_text:
                    parts = item_text.split('file:')
                    item['item'] = parts[0].replace('required:', '').strip()
                    item['file'] = parts[1].strip()

                checklist_items.append(item)

    if checklist_items:
        lesson['checklist'] = checklist_items

    # Validate required fields
    if 'label' not in lesson:
        return None

    return lesson

def detect_user_corrections(conversation_text):
    """
    Detect when user corrects the agent (indicates a lesson to learn).

    Patterns:
    - "you missed X"
    - "you forgot Y"
    - "don't forget Z"
    - "you should have checked A"
    - "why didn't you B"

    Args:
        conversation_text: Full conversation text

    Returns:
        List of correction dictionaries
    """
    correction_patterns = [
        r'you\s+(missed|forgot|skipped)\s+(.+?)[\.\n]',
        r'why\s+(didn\'t|did not)\s+you\s+(.+?)[\?\.\n]',
        r'you\s+should\s+have\s+(.+?)[\.\n]',
        r'don\'t\s+forget\s+(.+?)[\.\n]',
        r'remember\s+to\s+(.+?)[\.\n]',
        r'you\s+need\s+to\s+(.+?)[\.\n]'
    ]

    corrections = []

    for pattern in correction_patterns:
        matches = re.finditer(pattern, conversation_text, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            # Extract what was missed/forgotten
            if len(match.groups()) == 2:
                action_verb = match.group(1)
                missed_item = match.group(2).strip()
            else:
                action_verb = 'check'
                missed_item = match.group(1).strip()

            corrections.append({
                'type': 'user_correction',
                'pattern': pattern,
                'action': action_verb,
                'missed_item': missed_item,
                'context': match.group(0)
            })

    return corrections

def detect_repeated_mistakes(conversation_text, graph_updates):
    """
    Detect when the same mistake happens multiple times.

    Indicators:
    - Same file edited twice for the same reason
    - Same error message appears multiple times
    - Same operation attempted multiple times

    Args:
        conversation_text: Full conversation text
        graph_updates: List of graph updates from this conversation

    Returns:
        List of repeated mistake dictionaries
    """
    repeated = []

    # Look for explicit "again" or "another" patterns
    repeat_patterns = [
        r'(?:we|I|you)\s+(?:need to|should|must)\s+(.+?)\s+again',
        r'another\s+(.+?)\s+(?:was|is)\s+(?:missing|needed)',
        r'(.+?)\s+is\s+still\s+missing',  # More specific "X is still missing" pattern
        r'forgot\s+(.+?)\s+again',
        r'(.+?)\s+again[\.\n]',  # More general "X again" pattern
    ]

    for pattern in repeat_patterns:
        matches = re.finditer(pattern, conversation_text, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            repeated.append({
                'type': 'repeated_mistake',
                'pattern': pattern,
                'item': match.group(1).strip(),
                'context': match.group(0)
            })

    return repeated

def infer_priority_from_context(lesson_data, conversation_text):
    """
    Infer priority level from context.

    Rules:
    1. User-reported corrections → CRITICAL
    2. Deployment triad context → CRITICAL
    3. Repeated mistakes → HIGH
    4. Security-related → HIGH
    5. Explicit priority in lesson → use that
    6. Default → LOW (for review)

    Args:
        lesson_data: Lesson dictionary
        conversation_text: Full conversation text

    Returns:
        Priority string (CRITICAL, HIGH, MEDIUM, LOW)
    """
    # Use explicit priority if provided
    if 'priority' in lesson_data and lesson_data['priority'] in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
        return lesson_data['priority']

    # User correction = CRITICAL
    if lesson_data.get('type') == 'user_correction':
        return 'CRITICAL'

    # Repeated mistake = HIGH
    if lesson_data.get('type') == 'repeated_mistake':
        return 'HIGH'

    # Check for deployment context
    deployment_keywords = ['deploy', 'release', 'version', 'publish', 'marketplace']
    if any(kw in conversation_text.lower() for kw in deployment_keywords):
        if lesson_data.get('triad') == 'deployment':
            return 'CRITICAL'

    # Check for security context
    security_keywords = ['security', 'validation', 'injection', 'path traversal', 'sanitize']
    if any(kw in str(lesson_data).lower() for kw in security_keywords):
        return 'HIGH'

    # Default to LOW for manual review
    return 'LOW'

def create_process_knowledge_node(lesson_data, conversation_text):
    """
    Create a Process Concept node from lesson data.

    Args:
        lesson_data: Lesson dictionary
        conversation_text: Full conversation text

    Returns:
        Node dictionary ready for graph insertion
    """
    # Generate node ID
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    lesson_type = lesson_data.get('type', 'lesson')
    node_id = f"process_{lesson_type}_{timestamp}"

    # Infer priority
    priority = infer_priority_from_context(lesson_data, conversation_text)

    # Calculate initial confidence based on evidence source
    source = lesson_data.get('type', 'unknown')
    repetition_count = lesson_data.get('repetition_count', 1)
    confidence = calculate_initial_confidence(
        source=source,
        priority=priority,
        repetition_count=repetition_count,
        context=lesson_data
    )

    # Assign status based on confidence
    status = assign_status(confidence, priority)

    # Build node
    node = {
        'id': node_id,
        'type': 'Concept',
        'label': lesson_data.get('label', f"Lesson: {lesson_data.get('missed_item', 'Unknown')}"),
        'description': lesson_data.get('description', ''),
        'confidence': confidence,  # Calculated from evidence source
        'priority': priority,
        'process_type': lesson_data.get('process_type', 'warning'),
        'detection_method': lesson_data.get('type', 'explicit'),  # Preserve detection method (legacy)
        'source': source,  # NEW: Source for confidence tracking
        'status': status,  # NEW: Confidence-based status (active/needs_validation)
        'created_by': 'experience-learning-system',
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),  # NEW: Track updates
        'evidence': f"Learned from conversation at {datetime.now().isoformat()}",

        # NEW: Initialize outcome tracking fields
        'success_count': 0,
        'failure_count': 0,
        'confirmation_count': 0,
        'contradiction_count': 0,
        'injection_count': 0,
        'last_injected_at': None,
        'last_outcome': None,
        'outcome_history': [],
        'deprecated_at': None,
        'deprecated_reason': None,
        'deprecation_automatic': False,
    }

    # Add trigger conditions if present
    if 'trigger_conditions' in lesson_data:
        node['trigger_conditions'] = lesson_data['trigger_conditions']

    # Add process-type specific content
    if lesson_data.get('process_type') == 'checklist' and 'checklist' in lesson_data:
        node['checklist'] = lesson_data['checklist']
    elif lesson_data.get('process_type') == 'pattern' and 'pattern' in lesson_data:
        node['pattern'] = lesson_data['pattern']
    elif lesson_data.get('process_type') == 'warning':
        node['warning'] = {
            'condition': lesson_data.get('missed_item', ''),
            'consequence': lesson_data.get('description', 'May cause issues'),
            'prevention': lesson_data.get('prevention', 'Verify before proceeding')
        }

    return node

def extract_lessons_from_conversation(conversation_text, graph_updates):
    """
    Extract all lessons from a conversation.

    Combines three detection methods:
    1. [PROCESS_KNOWLEDGE] blocks (explicit)
    2. User corrections (implicit)
    3. Repeated mistakes (implicit)

    Args:
        conversation_text: Full conversation text
        graph_updates: List of graph updates from this conversation

    Returns:
        List of process knowledge nodes to add to graphs
    """
    lessons = []

    # Method 1: Extract explicit [PROCESS_KNOWLEDGE] blocks
    explicit_lessons = extract_process_knowledge_blocks(conversation_text)
    for lesson_data in explicit_lessons:
        node = create_process_knowledge_node(lesson_data, conversation_text)
        lessons.append(node)

    # Method 2: Detect user corrections
    corrections = detect_user_corrections(conversation_text)
    for correction in corrections:
        # Create a warning-type process knowledge
        lesson_data = {
            'type': 'user_correction',
            'process_type': 'warning',
            'label': f"Remember: {correction['missed_item']}",
            'description': f"User correction: {correction['action']} - {correction['missed_item']}",
            'missed_item': correction['missed_item'],
            'trigger_conditions': {
                'tool_names': ['Write', 'Edit'],
                'file_patterns': [],
                'action_keywords': [correction['missed_item'].split()[0]],
                'context_keywords': [],
                'triad_names': []
            }
        }
        node = create_process_knowledge_node(lesson_data, conversation_text)
        lessons.append(node)

    # Method 3: Detect repeated mistakes
    repeated = detect_repeated_mistakes(conversation_text, graph_updates)
    for mistake in repeated:
        lesson_data = {
            'type': 'repeated_mistake',
            'process_type': 'warning',
            'label': f"Repeated Issue: {mistake['item']}",
            'description': f"This mistake has occurred multiple times: {mistake['item']}",
            'missed_item': mistake['item'],
            'trigger_conditions': {
                'tool_names': ['*'],
                'file_patterns': [],
                'action_keywords': [mistake['item'].split()[0]],
                'context_keywords': [],
                'triad_names': []
            }
        }
        node = create_process_knowledge_node(lesson_data, conversation_text)
        lessons.append(node)

    return lessons

# ============================================================================
# Main Stop Hook Logic
# ============================================================================

def main():
    """Main Stop hook execution."""

    # Read input (may be JSON with transcript_path, or plain text)
    input_text = sys.stdin.read()

    # Try to parse as JSON first
    conversation_text = None
    try:
        input_data = json.loads(input_text)

        # Check if we have a transcript_path
        transcript_path = input_data.get('transcript_path')
        if transcript_path and Path(transcript_path).exists():
            # Read full conversation from transcript JSONL
            with open(transcript_path, 'r') as f:
                transcript_lines = f.readlines()

            # Extract all text from transcript
            all_text = []
            for line in transcript_lines:
                try:
                    entry = json.loads(line)

                    # Check both entry['content'] and entry['message']['content']
                    content = None
                    if 'message' in entry and 'content' in entry['message']:
                        content = entry['message']['content']
                    elif 'content' in entry:
                        content = entry['content']

                    if content:
                        # Content can be string or array
                        if isinstance(content, list):
                            for item in content:
                                if isinstance(item, dict) and 'text' in item:
                                    all_text.append(item['text'])
                                elif isinstance(item, str):
                                    all_text.append(item)
                        elif isinstance(content, str):
                            all_text.append(content)
                except json.JSONDecodeError:
                    continue

            conversation_text = '\n'.join(all_text)
        else:
            # Use input data as text
            conversation_text = str(input_data)

    except json.JSONDecodeError:
        # Input is plain text
        conversation_text = input_text

    if not conversation_text:
        # No text to process
        return

    # Extract all [GRAPH_UPDATE] blocks
    updates = extract_graph_updates_from_text(conversation_text)

    if not updates:
        # No updates found - exit silently
        return

    print(f"\n{'='*80}", file=sys.stderr)
    print("📊 Knowledge Graph Update (Stop Hook)", file=sys.stderr)
    print(f"{'='*80}", file=sys.stderr)
    print(f"Found {len(updates)} [GRAPH_UPDATE] blocks", file=sys.stderr)

    # Validate pre-flight checks
    pre_flight_violations = validate_pre_flight_checks(conversation_text, updates)

    if pre_flight_violations:
        print(f"⚠️  Found {len(pre_flight_violations)} pre-flight check violations", file=sys.stderr)

        # Log violations to constitutional violations file
        violations_file = Path('.claude/constitutional/violations.json')
        violations_file.parent.mkdir(parents=True, exist_ok=True)

        existing_violations = []
        if violations_file.exists():
            try:
                with open(violations_file, 'r') as f:
                    existing_violations = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                existing_violations = []

        # Add new violations with timestamps
        for violation in pre_flight_violations:
            violation['detected_at'] = datetime.now().isoformat()
            violation['hook'] = 'on_stop'
            existing_violations.append(violation)

        with open(violations_file, 'w') as f:
            json.dump(existing_violations, f, indent=2)

        # Show summary
        critical = sum(1 for v in pre_flight_violations if v.get('severity') == 'critical')
        high = sum(1 for v in pre_flight_violations if v.get('severity') == 'high')
        medium = sum(1 for v in pre_flight_violations if v.get('severity') == 'medium')

        print(f"   Critical: {critical}, High: {high}, Medium: {medium}", file=sys.stderr)
        print(f"   Logged to: {violations_file}", file=sys.stderr)
    else:
        print("✓ All graph updates have valid pre-flight checks", file=sys.stderr)

    print(f"{'='*80}\n", file=sys.stderr)

    # Group updates by triad
    updates_by_triad = {}
    for update in updates:
        triad = get_triad_from_update(update)
        if triad not in updates_by_triad:
            updates_by_triad[triad] = []
        updates_by_triad[triad].append(update)

    # Apply updates to each triad's graph
    for triad, triad_updates in updates_by_triad.items():
        print(f"Updating {triad} graph ({len(triad_updates)} updates)...", file=sys.stderr)

        graph_data = load_graph(triad)

        for i, update in enumerate(triad_updates, 1):
            agent_name = update.get('created_by', 'unknown')
            print(f"  [{i}/{len(triad_updates)}] ", end='', file=sys.stderr)
            try:
                graph_data = apply_update(graph_data, update, agent_name)
            except Exception as e:
                print(f"❌ Error: {e}", file=sys.stderr)
                continue

        # Save updated graph
        try:
            save_graph(graph_data, triad)
            print(f"✅ {triad}_graph.json updated: {graph_data['_meta']['node_count']} nodes, {graph_data['_meta']['edge_count']} edges", file=sys.stderr)  # noqa: E501

            # Detect KM issues
            issues = detect_km_issues(graph_data, triad)
            if issues:
                update_km_queue(issues)
                notification = format_km_notification(issues)
                if notification:
                    print(f"{notification}\n", file=sys.stderr)

                # Auto-invoke system agents for high-priority issues (Phase 2)
                try:
                    new_invocations, total = process_and_queue_invocations(issues)
                    if new_invocations:
                        print(
                            f"🤖 Auto-queued {len(new_invocations)} system agent(s) "
                            f"for high-priority issues\n",
                            file=sys.stderr
                        )
                except Exception as e:
                    print(f"⚠️  Auto-invocation warning: {e}\n", file=sys.stderr)
            else:
                print("", file=sys.stderr)
        except Exception as e:
            print(f"❌ Error saving {triad} graph: {e}\n", file=sys.stderr)

    # Write status file for agents
    try:
        write_km_status_file()
    except Exception as e:
        print(f"❌ Error writing KM status file: {e}", file=sys.stderr)

    # ========================================================================
    # Experience-Based Learning: Extract lessons from conversation
    # ========================================================================
    print(f"\n{'='*80}", file=sys.stderr)
    print("🧠 Experience-Based Learning: Lesson Extraction", file=sys.stderr)
    print(f"{'='*80}", file=sys.stderr)

    try:
        lessons = extract_lessons_from_conversation(conversation_text, updates)

        if lessons:
            print(f"Found {len(lessons)} lesson(s) to learn", file=sys.stderr)

            # Group lessons by triad (use 'default' if not specified)
            lessons_by_triad = {}
            for lesson in lessons:
                triad = lesson.get('triad', 'default')
                if triad not in lessons_by_triad:
                    lessons_by_triad[triad] = []
                lessons_by_triad[triad].append(lesson)

            # Add lessons to graphs
            for triad, triad_lessons in lessons_by_triad.items():
                print(f"\nAdding {len(triad_lessons)} lesson(s) to {triad} graph...", file=sys.stderr)

                graph_data = load_graph(triad)

                for i, lesson in enumerate(triad_lessons, 1):
                    node_id = lesson['id']
                    priority = lesson.get('priority', 'LOW')
                    confidence = lesson.get('confidence', 0.75)
                    status = lesson.get('status', 'needs_validation')

                    # Check if lesson already exists
                    existing = [n for n in graph_data['nodes'] if n.get('id') == node_id]
                    if existing:
                        print(f"  [{i}/{len(triad_lessons)}] ⚠️  Lesson {node_id} already exists, skipping", file=sys.stderr)
                        continue

                    # Add lesson node to graph
                    graph_data['nodes'].append(lesson)
                    print(f"  [{i}/{len(triad_lessons)}] ✓ Added lesson: {lesson['label']} (confidence: {int(confidence*100)}%, status: {status})", file=sys.stderr)

                # Save updated graph
                try:
                    save_graph(graph_data, triad)
                    print(f"✅ {triad}_graph.json updated with lessons", file=sys.stderr)
                except Exception as e:
                    print(f"❌ Error saving lessons to {triad} graph: {e}", file=sys.stderr)

            # Show summary of uncertain lessons
            uncertain_lessons = [l for l in lessons if l.get('confidence', 1.0) < 0.70]
            if uncertain_lessons:
                print(f"\n⚠️  {len(uncertain_lessons)} uncertain lesson(s) created (confidence < 70%)", file=sys.stderr)
                print("   Use /knowledge-review-uncertain to review and validate lessons", file=sys.stderr)

        else:
            print("No lessons extracted from this conversation", file=sys.stderr)

    except Exception as e:
        print(f"❌ Error during lesson extraction: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)

    print(f"{'='*80}\n", file=sys.stderr)

    # ========================================================================
    # Phase 3: Outcome Detection & Confidence Updates
    # ========================================================================
    print(f"\n{'='*80}", file=sys.stderr)
    print("🎯 Confidence-Based Learning: Outcome Detection", file=sys.stderr)
    print(f"{'='*80}", file=sys.stderr)

    try:
        # Import experience tracker
        try:
            from triads.km.experience_tracker import ExperienceTracker
        except ImportError as e:
            print(f"⚠️  Experience tracker not available: {e}", file=sys.stderr)
            ExperienceTracker = None

        if ExperienceTracker is not None:
            tracker = ExperienceTracker()

            # Detect outcomes from conversation
            outcomes = tracker.detect_outcomes(conversation_text)

            if outcomes:
                print(f"Found {len(outcomes)} lesson outcome(s)", file=sys.stderr)

                # Group outcomes by lesson and update confidence
                outcomes_by_lesson = {}
                for outcome in outcomes:
                    lesson_id = outcome.lesson_id
                    if lesson_id not in outcomes_by_lesson:
                        outcomes_by_lesson[lesson_id] = []
                    outcomes_by_lesson[lesson_id].append(outcome)

                # Update confidence scores in graphs
                for lesson_id, lesson_outcomes in outcomes_by_lesson.items():
                    # Find which graph contains this lesson
                    for triad in ['deployment', 'design', 'implementation', 'garden-tending', 'idea-validation', 'default']:
                        graph_data = load_graph(triad)

                        # Find the lesson node
                        lesson_node = next(
                            (n for n in graph_data['nodes'] if n.get('id') == lesson_id),
                            None
                        )

                        if lesson_node:
                            current_confidence = lesson_node.get('confidence', 0.75)

                            # Apply all outcomes to this lesson
                            for outcome_record in lesson_outcomes:
                                outcome_type = outcome_record.outcome

                                # Update confidence using Bayesian method
                                new_confidence = update_confidence(
                                    current_confidence,
                                    outcome_type
                                )

                                # Update node
                                lesson_node['confidence'] = new_confidence

                                # Track statistics
                                if 'success_count' not in lesson_node:
                                    lesson_node['success_count'] = 0
                                if 'failure_count' not in lesson_node:
                                    lesson_node['failure_count'] = 0
                                if 'contradiction_count' not in lesson_node:
                                    lesson_node['contradiction_count'] = 0

                                if outcome_type == 'success':
                                    lesson_node['success_count'] += 1
                                elif outcome_type == 'failure':
                                    lesson_node['failure_count'] += 1
                                elif outcome_type == 'contradiction':
                                    lesson_node['contradiction_count'] += 1
                                elif outcome_type == 'confirmation':
                                    # Confirmation is manual validation, treat as success
                                    lesson_node['success_count'] += 1

                                # Update needs_validation flag
                                lesson_node['needs_validation'] = new_confidence < 0.70

                                # Check deprecation
                                from triads.km.confidence import check_deprecation
                                if check_deprecation(lesson_node):
                                    lesson_node['deprecated'] = True
                                    lesson_node['deprecated_reason'] = f"Confidence dropped below threshold ({new_confidence:.2f})"

                                current_confidence = new_confidence

                                print(
                                    f"  ✓ {outcome_type.upper()}: {lesson_node.get('label', lesson_id)} "
                                    f"({current_confidence:.2f})",
                                    file=sys.stderr
                                )

                            # Save updated graph
                            try:
                                save_graph(graph_data, triad)
                            except Exception as e:
                                print(f"❌ Error saving confidence updates to {triad} graph: {e}", file=sys.stderr)

                            break  # Found the lesson, stop searching other triads

                # Clear session state for next session
                tracker.clear_session()
                print(f"✅ Confidence scores updated, session cleared", file=sys.stderr)

            else:
                print("No outcomes detected in this session", file=sys.stderr)
        else:
            print("Experience tracker not available, skipping outcome detection", file=sys.stderr)

    except Exception as e:
        print(f"❌ Error during outcome detection: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)

    print(f"{'='*80}\n", file=sys.stderr)


if __name__ == "__main__":
    main()
