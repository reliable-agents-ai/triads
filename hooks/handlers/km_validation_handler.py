"""
KM Validation Handler: Process knowledge management and experience-based learning.

Extracts process knowledge from conversations using three detection methods:
1. Explicit [PROCESS_KNOWLEDGE] blocks
2. User corrections (implicit learning)
3. Repeated mistakes (implicit learning)

Creates process knowledge nodes with confidence scores and priority levels.

Single Responsibility: Knowledge management and experience learning only.

Usage:
    handler = KMValidationHandler()
    result = handler.process(conversation_text, graph_updates)
    # result = {"count": 3, "lessons": [...], "lessons_by_triad": {...}}
"""

import json
import re
from datetime import datetime
from typing import Dict, List

from setup_paths import setup_import_paths
setup_import_paths()

from triads.km.confidence import (  # noqa: E402
    calculate_initial_confidence,
    assign_status,
)


class KMValidationHandler:
    """Handler for knowledge management and experience-based learning."""

    def __init__(self):
        """Initialize KM validation handler."""
        pass

    def extract_process_knowledge_blocks(self, text: str) -> List[Dict]:
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
            lesson = self.parse_process_knowledge_block(match)
            if lesson:
                # Mark as explicit PROCESS_KNOWLEDGE block (for confidence calculation)
                lesson['type'] = 'process_knowledge_block'
                lessons.append(lesson)

        return lessons

    def parse_process_knowledge_block(self, block_text: str) -> Dict:
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

    def detect_user_corrections(self, conversation_text: str) -> List[Dict]:
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

    def detect_repeated_mistakes(self, conversation_text: str, graph_updates: List[Dict]) -> List[Dict]:
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

    def infer_priority_from_context(self, lesson_data: Dict, conversation_text: str) -> str:
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

    def create_process_knowledge_node(self, lesson_data: Dict, conversation_text: str) -> Dict:
        """
        Create a Process Concept node from lesson data.

        Calculates initial confidence based on evidence source,
        assigns status (active/needs_validation), and initializes
        outcome tracking fields for Bayesian confidence updates.

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
        priority = self.infer_priority_from_context(lesson_data, conversation_text)

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

    def extract_lessons_from_conversation(
        self,
        conversation_text: str,
        graph_updates: List[Dict]
    ) -> List[Dict]:
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
        explicit_lessons = self.extract_process_knowledge_blocks(conversation_text)
        for lesson_data in explicit_lessons:
            node = self.create_process_knowledge_node(lesson_data, conversation_text)
            lessons.append(node)

        # Method 2: Detect user corrections
        corrections = self.detect_user_corrections(conversation_text)
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
            node = self.create_process_knowledge_node(lesson_data, conversation_text)
            lessons.append(node)

        # Method 3: Detect repeated mistakes
        repeated = self.detect_repeated_mistakes(conversation_text, graph_updates)
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
            node = self.create_process_knowledge_node(lesson_data, conversation_text)
            lessons.append(node)

        return lessons

    def process(self, conversation_text: str, graph_updates: List[Dict]) -> Dict:
        """
        Main entry point: extract and create process knowledge nodes.

        Process flow:
        1. Extract explicit [PROCESS_KNOWLEDGE] blocks
        2. Detect user corrections (implicit learning)
        3. Detect repeated mistakes (implicit learning)
        4. Create process knowledge nodes with confidence scores
        5. Group lessons by triad for graph insertion
        6. Return results

        Args:
            conversation_text: Full conversation text
            graph_updates: List of graph updates from conversation (for repeated mistake detection)

        Returns:
            dict: Processing results
                - count: Number of lessons extracted
                - lessons: List of process knowledge nodes
                - lessons_by_triad: Dict mapping triad name to list of lessons
                - explicit_count: Number of explicit [PROCESS_KNOWLEDGE] blocks
                - correction_count: Number of user corrections detected
                - repeated_count: Number of repeated mistakes detected
        """
        # Extract all lessons
        lessons = self.extract_lessons_from_conversation(conversation_text, graph_updates)

        # Group lessons by triad
        lessons_by_triad = {}
        for lesson in lessons:
            triad = lesson.get('triad', 'default')
            if triad not in lessons_by_triad:
                lessons_by_triad[triad] = []
            lessons_by_triad[triad].append(lesson)

        # Count by detection method
        explicit_count = len([l for l in lessons if l.get('detection_method') == 'process_knowledge_block'])
        correction_count = len([l for l in lessons if l.get('detection_method') == 'user_correction'])
        repeated_count = len([l for l in lessons if l.get('detection_method') == 'repeated_mistake'])

        return {
            'count': len(lessons),
            'lessons': lessons,
            'lessons_by_triad': lessons_by_triad,
            'explicit_count': explicit_count,
            'correction_count': correction_count,
            'repeated_count': repeated_count
        }
