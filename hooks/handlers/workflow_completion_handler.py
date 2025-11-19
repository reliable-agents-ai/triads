"""
Workflow Completion Handler: Process workflow completion notifications.

Extracts [WORKFLOW_COMPLETE] blocks from text and records workflow completion.
Handles cleanup of pending handoffs when workflow is complete.

Single Responsibility: Workflow completion lifecycle management only.

Usage:
    handler = WorkflowCompletionHandler()
    result = handler.process(conversation_text)
    # result = {"count": 1, "success": True, "completions": [...]}
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

from setup_paths import setup_import_paths
setup_import_paths()


class WorkflowCompletionHandler:
    """Handler for workflow completion notifications."""

    def __init__(self, workflow_dir: Path = None, pending_handoff_file: Path = None):
        """
        Initialize workflow completion handler.

        Args:
            workflow_dir: Directory for workflow state (default: .claude/.workflow/)
            pending_handoff_file: Path to pending handoff file (default: .claude/.pending_handoff.json)
        """
        self.workflow_dir = workflow_dir or Path('.claude/.workflow')
        self.completion_file = self.workflow_dir / 'completed.json'
        self.pending_handoff_file = pending_handoff_file or Path('.claude/.pending_handoff.json')

    def extract_completions(self, text: str) -> List[Dict]:
        """
        Extract [WORKFLOW_COMPLETE] blocks from text.

        Parses multiline format:
        [WORKFLOW_COMPLETE]
        workflow_id: idea-validation
        final_status: SUCCESS
        completion_summary: |
          | Line 1
          | Line 2
        [/WORKFLOW_COMPLETE]

        Args:
            text: String containing [WORKFLOW_COMPLETE]...[/WORKFLOW_COMPLETE] blocks

        Returns:
            List of workflow completion dictionaries
        """
        pattern = r'\[WORKFLOW_COMPLETE\](.*?)\[/WORKFLOW_COMPLETE\]'
        matches = re.findall(pattern, text, re.DOTALL)

        completions = []
        for match in matches:
            completion = {}
            current_key = None
            multiline_value = []

            for line in match.strip().split('\n'):
                line_stripped = line.strip()

                # Handle multiline with | prefix
                if line_stripped.startswith('|') and current_key:
                    multiline_value.append(line_stripped[1:].strip())
                    continue

                # Parse key: value
                if ':' in line_stripped:
                    # Save previous multiline value if exists
                    if current_key and multiline_value:
                        completion[current_key] = '\n'.join(multiline_value)
                        multiline_value = []

                    key, value = line_stripped.split(':', 1)
                    key = key.strip()
                    value = value.strip()

                    if not value or value == '|':
                        # Start of multiline value
                        current_key = key
                        multiline_value = []
                    else:
                        # Single-line value
                        completion[key] = value
                        current_key = None

            # Save final multiline value if exists
            if current_key and multiline_value:
                completion[current_key] = '\n'.join(multiline_value)

            if completion:
                completions.append(completion)

        return completions

    def validate_completion(self, completion: Dict) -> Tuple[bool, str]:
        """
        Validate workflow completion structure.

        Required fields:
        - workflow_id: Unique workflow identifier

        Optional fields:
        - final_status: Workflow final status (default: "UNKNOWN")
        - completion_summary: Summary of completion
        - deliverables: Deliverables produced
        - knowledge_updates: Knowledge graph updates summary

        Args:
            completion: Workflow completion dictionary

        Returns:
            Tuple of (is_valid, error_message)
            - (True, "") if valid
            - (False, "error message") if invalid
        """
        if not completion.get('workflow_id'):
            return False, "Workflow completion missing workflow_id field"

        return True, ""

    def record_completion(self, completion: Dict) -> bool:
        """
        Record workflow completion and cleanup pending handoffs.

        Creates .claude/.workflow/completed.json with:
        - workflow_id: Workflow identifier
        - final_status: Final status (SUCCESS, FAILED, PARTIAL, etc.)
        - completion_summary: Completion summary
        - deliverables: Deliverables produced
        - knowledge_updates: Knowledge updates summary
        - timestamp: ISO format timestamp
        - completed: True

        Also removes .claude/.pending_handoff.json if it exists
        (workflow is complete, no more handoffs needed).

        Args:
            completion: Validated workflow completion dictionary

        Returns:
            bool: True if completion was recorded successfully, False otherwise
        """
        try:
            # Ensure workflow directory exists
            self.workflow_dir.mkdir(parents=True, exist_ok=True)

            # Build completion record with defaults
            completion_record = {
                'workflow_id': completion.get('workflow_id'),
                'final_status': completion.get('final_status', 'UNKNOWN'),
                'completion_summary': completion.get('completion_summary', ''),
                'deliverables': completion.get('deliverables', ''),
                'knowledge_updates': completion.get('knowledge_updates', ''),
                'timestamp': datetime.now().isoformat(),
                'completed': True
            }

            # Write completion record atomically
            # Write to temp file first, then rename (atomic on POSIX)
            temp_file = self.completion_file.with_suffix('.tmp')
            with open(temp_file, 'w') as f:
                json.dump(completion_record, f, indent=2)
            temp_file.rename(self.completion_file)

            # Remove any pending handoff (workflow is complete)
            if self.pending_handoff_file.exists():
                self.pending_handoff_file.unlink()

            # Log success to stderr (not captured by Claude Code)
            print(
                f"\n🏁 Workflow Complete: {completion_record['final_status']}",
                file=sys.stderr
            )
            print(
                f"   Workflow ID: {completion_record['workflow_id']}",
                file=sys.stderr
            )
            print(
                f"   Deliverables: {completion.get('deliverables', 'N/A')}",
                file=sys.stderr
            )
            print(
                f"   All triads completed successfully!",
                file=sys.stderr
            )

            return True

        except Exception as e:
            print(
                f"❌ Error recording workflow completion: {e}",
                file=sys.stderr
            )
            return False

    def process(self, text: str) -> Dict:
        """
        Main entry point: extract, validate, and record completions.

        Processes all [WORKFLOW_COMPLETE] blocks in text:
        1. Extract workflow completions from text
        2. Validate each completion
        3. Record valid completions
        4. Cleanup pending handoffs
        5. Report results

        Args:
            text: Conversation text containing [WORKFLOW_COMPLETE] blocks

        Returns:
            dict: Processing results
                - count: Number of workflow completions found
                - success: True if all completions recorded successfully
                - completions: List of completion data
                - errors: List of validation errors (if any)
        """
        # Extract workflow completions
        completions = self.extract_completions(text)

        if not completions:
            return {
                'count': 0,
                'success': True,
                'completions': [],
                'errors': []
            }

        # Validate and record each completion
        recorded_count = 0
        errors = []

        for completion in completions:
            # Validate completion
            is_valid, error_message = self.validate_completion(completion)

            if not is_valid:
                errors.append({
                    'completion': completion,
                    'error': error_message
                })
                print(f"⚠️  {error_message}", file=sys.stderr)
                continue

            # Record valid completion
            if self.record_completion(completion):
                recorded_count += 1
            else:
                errors.append({
                    'completion': completion,
                    'error': 'Failed to record completion'
                })

        return {
            'count': len(completions),
            'success': recorded_count == len(completions),
            'recorded': recorded_count,
            'completions': completions,
            'errors': errors
        }
