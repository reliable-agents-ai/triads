"""
Handoff Handler: Process triad handoff requests.

Extracts [HANDOFF_REQUEST] blocks from text and queues them for next session.
Handles the complete handoff lifecycle: extraction → validation → queuing.

Single Responsibility: Handoff lifecycle management only.

Usage:
    handler = HandoffHandler()
    result = handler.process(conversation_text)
    # result = {"count": 2, "success": True, "requests": [...]}
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

from setup_paths import setup_import_paths
setup_import_paths()

from constants import HANDOFF_EXPIRY_HOURS  # noqa: E402


class HandoffHandler:
    """Handler for triad handoff requests."""

    def __init__(self, pending_dir: Path = None):
        """
        Initialize handoff handler.

        Args:
            pending_dir: Directory for pending handoffs (default: .claude/)
        """
        self.pending_dir = pending_dir or Path('.claude')
        self.pending_file = self.pending_dir / '.pending_handoff.json'

    def extract_requests(self, text: str) -> List[Dict]:
        """
        Extract [HANDOFF_REQUEST] blocks from text.

        Parses multiline format:
        [HANDOFF_REQUEST]
        next_triad: Implementation
        request_type: feature_complete
        context: |
          | Line 1
          | Line 2
        [/HANDOFF_REQUEST]

        Args:
            text: String containing [HANDOFF_REQUEST]...[/HANDOFF_REQUEST] blocks

        Returns:
            List of handoff request dictionaries
        """
        pattern = r'\[HANDOFF_REQUEST\](.*?)\[/HANDOFF_REQUEST\]'
        matches = re.findall(pattern, text, re.DOTALL)

        requests = []
        for match in matches:
            request = {}
            current_key = None
            multiline_value = []

            for line in match.strip().split('\n'):
                line_stripped = line.strip()

                # Check if this is a continuation of multiline value (starts with |)
                if line_stripped.startswith('|') and current_key:
                    multiline_value.append(line_stripped[1:].strip())
                    continue

                # Regular key: value line
                if ':' in line_stripped:
                    # Save previous multiline value if exists
                    if current_key and multiline_value:
                        request[current_key] = '\n'.join(multiline_value)
                        multiline_value = []

                    key, value = line_stripped.split(':', 1)
                    key = key.strip()
                    value = value.strip()

                    # If value is empty, this might be start of multiline
                    if not value or value == '|':
                        current_key = key
                        multiline_value = []
                    else:
                        request[key] = value
                        current_key = None

            # Save final multiline value if exists
            if current_key and multiline_value:
                request[current_key] = '\n'.join(multiline_value)

            if request:
                requests.append(request)

        return requests

    def validate_request(self, handoff: Dict) -> Tuple[bool, str]:
        """
        Validate handoff request structure.

        Required fields:
        - next_triad: Target triad name

        Optional fields:
        - request_type: Type of handoff (default: "unknown")
        - context: Handoff context
        - knowledge_graph: Knowledge graph state
        - updated_nodes: Comma-separated node IDs

        Args:
            handoff: Handoff request dictionary

        Returns:
            Tuple of (is_valid, error_message)
            - (True, "") if valid
            - (False, "error message") if invalid
        """
        if not handoff.get('next_triad'):
            return False, "Handoff request missing next_triad field"

        return True, ""

    def queue_handoff(self, handoff: Dict) -> bool:
        """
        Write handoff to pending handoff file.

        Creates .claude/.pending_handoff.json with:
        - next_triad: Target triad
        - request_type: Handoff type
        - context: Handoff context
        - knowledge_graph: Knowledge graph state
        - updated_nodes: List of updated node IDs
        - timestamp: ISO format timestamp
        - status: "pending"

        Args:
            handoff: Validated handoff request dictionary

        Returns:
            bool: True if handoff was queued successfully, False otherwise
        """
        try:
            # Ensure pending directory exists
            self.pending_dir.mkdir(exist_ok=True)

            # Build handoff data with defaults
            handoff_data = {
                'next_triad': handoff.get('next_triad'),
                'request_type': handoff.get('request_type', 'unknown'),
                'context': handoff.get('context', ''),
                'knowledge_graph': handoff.get('knowledge_graph', ''),
                'updated_nodes': (
                    handoff.get('updated_nodes', '').split(',')
                    if handoff.get('updated_nodes')
                    else []
                ),
                'timestamp': datetime.now().isoformat(),
                'status': 'pending',
                'expiry_hours': HANDOFF_EXPIRY_HOURS
            }

            # Write pending handoff atomically
            # Write to temp file first, then rename (atomic on POSIX)
            temp_file = self.pending_file.with_suffix('.tmp')
            with open(temp_file, 'w') as f:
                json.dump(handoff_data, f, indent=2)
            temp_file.rename(self.pending_file)

            # Log success to stderr (not captured by Claude Code)
            print(
                f"\n🔗 Handoff queued: → {handoff_data['next_triad']} triad",
                file=sys.stderr
            )
            print(
                f"   Type: {handoff_data['request_type']}",
                file=sys.stderr
            )
            print(
                f"   Status: Pending (will auto-invoke on next session)",
                file=sys.stderr
            )

            return True

        except Exception as e:
            print(
                f"❌ Error queuing handoff: {e}",
                file=sys.stderr
            )
            return False

    def process(self, text: str) -> Dict:
        """
        Main entry point: extract, validate, and queue handoffs.

        Processes all [HANDOFF_REQUEST] blocks in text:
        1. Extract handoff requests from text
        2. Validate each request
        3. Queue valid requests
        4. Report results

        Args:
            text: Conversation text containing [HANDOFF_REQUEST] blocks

        Returns:
            dict: Processing results
                - count: Number of handoff requests found
                - success: True if all handoffs queued successfully
                - requests: List of handoff request data
                - errors: List of validation errors (if any)
        """
        # Extract handoff requests
        requests = self.extract_requests(text)

        if not requests:
            return {
                'count': 0,
                'success': True,
                'requests': [],
                'errors': []
            }

        # Validate and queue each request
        queued_count = 0
        errors = []

        for handoff in requests:
            # Validate request
            is_valid, error_message = self.validate_request(handoff)

            if not is_valid:
                errors.append({
                    'handoff': handoff,
                    'error': error_message
                })
                print(f"⚠️  {error_message}", file=sys.stderr)
                continue

            # Queue valid request
            if self.queue_handoff(handoff):
                queued_count += 1
            else:
                errors.append({
                    'handoff': handoff,
                    'error': 'Failed to queue handoff'
                })

        return {
            'count': len(requests),
            'success': queued_count == len(requests),
            'queued': queued_count,
            'requests': requests,
            'errors': errors
        }
