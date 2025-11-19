"""
Graph Update Handler: Process knowledge graph updates.

Extracts [GRAPH_UPDATE] and [PRE_FLIGHT_CHECK] blocks from text,
validates quality gates, determines triad ownership, and applies updates.

Single Responsibility: Knowledge graph lifecycle management only.

Usage:
    handler = GraphUpdateHandler()
    result = handler.process(conversation_text, agent_name="senior-developer")
    # result = {"count": 5, "success": True, "updates_by_triad": {...}, "violations": []}
"""

import glob
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

from setup_paths import setup_import_paths
setup_import_paths()

from triads.hooks.safe_io import safe_load_json_file, safe_save_json_file  # noqa: E402


class GraphUpdateHandler:
    """Handler for knowledge graph updates."""

    def __init__(self, graphs_dir: Path = None):
        """
        Initialize graph update handler.

        Args:
            graphs_dir: Directory for knowledge graphs (default: .claude/graphs/)
        """
        self.graphs_dir = graphs_dir or Path('.claude/graphs')

    def extract_pre_flight_checks(self, text: str) -> List[Dict]:
        """
        Extract [PRE_FLIGHT_CHECK] blocks from text.

        Format:
        [PRE_FLIGHT_CHECK]
        node_id: node_001
        verification_status: PASSED
        checklist_items:
          - property_count: ✅ Has 5+ properties
          - confidence_check: ✅ Confidence >= 85%
        [/PRE_FLIGHT_CHECK]

        Args:
            text: String containing [PRE_FLIGHT_CHECK] blocks

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

    def extract_graph_updates(self, text: str) -> List[Dict]:
        """
        Extract [GRAPH_UPDATE] blocks from text.

        Format:
        [GRAPH_UPDATE]
        type: add_node
        node_id: node_001
        node_type: Entity
        label: Example Node
        confidence: 0.95
        [/GRAPH_UPDATE]

        Args:
            text: String containing [GRAPH_UPDATE] blocks

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

    def validate_pre_flight_checks(self, text: str, updates: List[Dict]) -> List[Dict]:
        """
        Validate that all graph updates have corresponding pre-flight checks.

        Quality gates enforced:
        1. Every [GRAPH_UPDATE] must have a [PRE_FLIGHT_CHECK]
        2. Pre-flight verification_status must be "PASSED"
        3. All required checklist items must be present
        4. All checklist items must pass (if verification_status is PASSED)

        Args:
            text: Full text to search for pre-flight checks
            updates: List of graph update dictionaries

        Returns:
            List of violation dictionaries (empty if all checks pass)
        """
        if not updates:
            return []

        pre_flight_checks = self.extract_pre_flight_checks(text)

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

    def get_triad_from_update(self, update: Dict) -> str:
        """
        Determine which triad an update belongs to.

        Strategy (in order of precedence):
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
            triad = self._lookup_agent_triad(agent_name)
            if triad:
                return triad

        # Infer from node_id prefix
        node_id = update.get('node_id', '')
        if '_' in node_id:
            potential_triad = node_id.split('_')[0]
            if self._is_valid_triad(potential_triad):
                return potential_triad

        # Default
        return 'default'

    def _lookup_agent_triad(self, agent_name: str) -> str:
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

    def _is_valid_triad(self, name: str) -> bool:
        """
        Check if a triad exists.

        Args:
            name: Potential triad name

        Returns:
            bool: True if triad exists
        """
        # Check if graph file exists OR agent directory exists
        return (self.graphs_dir / f'{name}_graph.json').exists() or \
               Path(f'.claude/agents/{name}').is_dir()

    def load_graph(self, triad_name: str) -> Dict:
        """
        Load a triad's knowledge graph or create a new one.

        Args:
            triad_name: Name of the triad

        Returns:
            dict: Graph data structure with nodes, links, and metadata
        """
        # Ensure graphs directory exists
        self.graphs_dir.mkdir(parents=True, exist_ok=True)

        graph_file = self.graphs_dir / f"{triad_name}_graph.json"

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

    def save_graph(self, graph_data: Dict, triad_name: str) -> bool:
        """
        Save a knowledge graph to disk.

        Updates metadata (updated_at, node_count, edge_count) before saving.

        Args:
            graph_data: Graph data structure
            triad_name: Name of the triad

        Returns:
            bool: True if save successful, False otherwise
        """
        # Ensure graphs directory exists
        self.graphs_dir.mkdir(parents=True, exist_ok=True)

        graph_file = self.graphs_dir / f"{triad_name}_graph.json"

        # Update metadata
        graph_data['_meta']['updated_at'] = datetime.now().isoformat()
        graph_data['_meta']['node_count'] = len(graph_data['nodes'])
        graph_data['_meta']['edge_count'] = len(graph_data['links'])

        # Use safe_save_json_file with atomic write
        if not safe_save_json_file(graph_file, graph_data):
            print(f"❌ Failed to save {triad_name} graph", file=sys.stderr)
            return False

        return True

    def apply_update(self, graph_data: Dict, update: Dict, agent_name: str) -> Dict:
        """
        Apply a single graph update to the graph data.

        Supported update types:
        - add_node: Add new node (skips if exists)
        - update_node: Update existing node (skips if not found)
        - add_edge: Add new edge (skips if exists)
        - update_edge: Update existing edge (skips if not found)

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
                 if e.get('source') == source and e.get('target') == target and e.get('key') == edge_type),
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

    def process(self, text: str, agent_name: str = "unknown") -> Dict:
        """
        Main entry point: extract, validate, and apply graph updates.

        Process flow:
        1. Extract [GRAPH_UPDATE] and [PRE_FLIGHT_CHECK] blocks
        2. Validate pre-flight checks (log violations)
        3. Group updates by triad
        4. For each triad:
           a. Load graph from disk
           b. Apply updates sequentially
           c. Save graph back to disk
        5. Return results

        Args:
            text: Conversation text containing [GRAPH_UPDATE] blocks
            agent_name: Name of the agent making updates (default: "unknown")

        Returns:
            dict: Processing results
                - count: Number of updates found
                - success: True if all updates applied successfully
                - updates_by_triad: Dict mapping triad name to list of updates
                - violations: List of pre-flight check violations
                - graphs_updated: List of triad names whose graphs were updated
        """
        # Extract updates
        updates = self.extract_graph_updates(text)

        if not updates:
            return {
                'count': 0,
                'success': True,
                'updates_by_triad': {},
                'violations': [],
                'graphs_updated': []
            }

        # Validate pre-flight checks
        violations = self.validate_pre_flight_checks(text, updates)

        # Group updates by triad
        updates_by_triad = {}
        for update in updates:
            triad = self.get_triad_from_update(update)
            if triad not in updates_by_triad:
                updates_by_triad[triad] = []
            updates_by_triad[triad].append(update)

        # Apply updates to each triad's graph
        graphs_updated = []
        for triad, triad_updates in updates_by_triad.items():
            # Load graph
            graph_data = self.load_graph(triad)

            # Apply updates
            for update in triad_updates:
                graph_data = self.apply_update(graph_data, update, agent_name)

            # Save graph
            if self.save_graph(graph_data, triad):
                graphs_updated.append(triad)

        return {
            'count': len(updates),
            'success': len(violations) == 0,
            'updates_by_triad': updates_by_triad,
            'violations': violations,
            'graphs_updated': graphs_updated
        }
