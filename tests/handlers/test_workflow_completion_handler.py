"""
Tests for WorkflowCompletionHandler.

Tests cover:
- Extraction of [WORKFLOW_COMPLETE] blocks (simple, multiline, multiple)
- Validation of workflow completions
- Recording to completion file
- Cleanup of pending handoffs
- Full process flow (success and error cases)
- Edge cases (empty text, malformed blocks, special characters)

Constitutional Principles Applied:
- Quality paramount: >80% coverage target
- Exhaustive testing: All code paths covered
- Security by design: File operations and cleanup tested
- SOLID principles: Tests are focused and independent
"""

import json
import pytest
from pathlib import Path
from datetime import datetime

# Add hooks directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'hooks'))

from handlers.workflow_completion_handler import WorkflowCompletionHandler


# ==============================================================================
# Fixtures
# ==============================================================================

@pytest.fixture
def temp_workflow_dir(tmp_path):
    """Create temporary directory for workflow state."""
    workflow_dir = tmp_path / '.claude' / '.workflow'
    workflow_dir.mkdir(parents=True, exist_ok=True)
    return workflow_dir


@pytest.fixture
def temp_pending_handoff(tmp_path):
    """Create temporary pending handoff file."""
    handoff_file = tmp_path / '.claude' / '.pending_handoff.json'
    handoff_file.parent.mkdir(parents=True, exist_ok=True)
    return handoff_file


@pytest.fixture
def handler(temp_workflow_dir, temp_pending_handoff):
    """Create WorkflowCompletionHandler with temporary paths."""
    return WorkflowCompletionHandler(
        workflow_dir=temp_workflow_dir,
        pending_handoff_file=temp_pending_handoff
    )


# ==============================================================================
# Extraction Tests
# ==============================================================================

class TestExtractCompletions:
    """Tests for extract_completions method."""

    def test_extract_simple_completion(self, handler):
        """Test extraction of simple workflow completion."""
        text = """
        [WORKFLOW_COMPLETE]
        workflow_id: idea-validation
        final_status: SUCCESS
        [/WORKFLOW_COMPLETE]
        """

        completions = handler.extract_completions(text)

        assert len(completions) == 1
        assert completions[0]['workflow_id'] == 'idea-validation'
        assert completions[0]['final_status'] == 'SUCCESS'

    def test_extract_completion_with_multiline_summary(self, handler):
        """Test extraction of completion with multiline summary."""
        text = """
        [WORKFLOW_COMPLETE]
        workflow_id: design-phase
        final_status: SUCCESS
        completion_summary: |
          | Architecture decision records completed
          | API contracts finalized
          | Database schema approved
        [/WORKFLOW_COMPLETE]
        """

        completions = handler.extract_completions(text)

        assert len(completions) == 1
        assert completions[0]['workflow_id'] == 'design-phase'
        assert 'Architecture decision records' in completions[0]['completion_summary']
        assert 'API contracts finalized' in completions[0]['completion_summary']

    def test_extract_multiple_completions(self, handler):
        """Test extraction of multiple workflow completions."""
        text = """
        First workflow done:
        [WORKFLOW_COMPLETE]
        workflow_id: idea-validation
        final_status: SUCCESS
        [/WORKFLOW_COMPLETE]

        Second workflow done:
        [WORKFLOW_COMPLETE]
        workflow_id: design-phase
        final_status: SUCCESS
        [/WORKFLOW_COMPLETE]
        """

        completions = handler.extract_completions(text)

        assert len(completions) == 2
        assert completions[0]['workflow_id'] == 'idea-validation'
        assert completions[1]['workflow_id'] == 'design-phase'

    def test_extract_completion_with_all_fields(self, handler):
        """Test extraction of completion with all optional fields."""
        text = """
        [WORKFLOW_COMPLETE]
        workflow_id: implementation-phase
        final_status: SUCCESS
        completion_summary: |
          | All features implemented
          | Tests passing
        deliverables: |
          | Feature X module
          | Unit tests
          | Integration tests
        knowledge_updates: |
          | Added implementation patterns to graph
          | Documented edge cases
        [/WORKFLOW_COMPLETE]
        """

        completions = handler.extract_completions(text)

        assert len(completions) == 1
        assert completions[0]['workflow_id'] == 'implementation-phase'
        assert completions[0]['final_status'] == 'SUCCESS'
        assert 'All features implemented' in completions[0]['completion_summary']
        assert 'Feature X module' in completions[0]['deliverables']
        assert 'implementation patterns' in completions[0]['knowledge_updates']

    def test_extract_empty_text(self, handler):
        """Test extraction from empty text returns empty list."""
        completions = handler.extract_completions("")
        assert completions == []

    def test_extract_no_completion_blocks(self, handler):
        """Test extraction from text without completion blocks."""
        text = "This is just regular text with no workflow completions."
        completions = handler.extract_completions(text)
        assert completions == []

    def test_extract_malformed_block(self, handler):
        """Test extraction handles malformed blocks gracefully."""
        text = """
        [WORKFLOW_COMPLETE]
        This is malformed - no key:value pairs
        [/WORKFLOW_COMPLETE]
        """

        # Should not crash, may return empty or partial data
        completions = handler.extract_completions(text)
        assert isinstance(completions, list)

    def test_extract_unclosed_block(self, handler):
        """Test extraction handles unclosed blocks gracefully."""
        text = """
        [WORKFLOW_COMPLETE]
        workflow_id: test
        """

        # Should not match unclosed blocks
        completions = handler.extract_completions(text)
        assert completions == []

    def test_extract_different_status_values(self, handler):
        """Test extraction handles various status values."""
        text = """
        [WORKFLOW_COMPLETE]
        workflow_id: test-failed
        final_status: FAILED
        [/WORKFLOW_COMPLETE]

        [WORKFLOW_COMPLETE]
        workflow_id: test-partial
        final_status: PARTIAL
        [/WORKFLOW_COMPLETE]
        """

        completions = handler.extract_completions(text)

        assert len(completions) == 2
        assert completions[0]['final_status'] == 'FAILED'
        assert completions[1]['final_status'] == 'PARTIAL'


# ==============================================================================
# Validation Tests
# ==============================================================================

class TestValidateCompletion:
    """Tests for validate_completion method."""

    def test_validate_valid_minimal_completion(self, handler):
        """Test validation of minimal valid completion."""
        completion = {'workflow_id': 'test-workflow'}

        is_valid, error = handler.validate_completion(completion)

        assert is_valid is True
        assert error == ""

    def test_validate_valid_full_completion(self, handler):
        """Test validation of completion with all fields."""
        completion = {
            'workflow_id': 'test-workflow',
            'final_status': 'SUCCESS',
            'completion_summary': 'All done',
            'deliverables': 'Module X, Tests',
            'knowledge_updates': 'Graph updated'
        }

        is_valid, error = handler.validate_completion(completion)

        assert is_valid is True
        assert error == ""

    def test_validate_missing_workflow_id(self, handler):
        """Test validation fails when workflow_id is missing."""
        completion = {'final_status': 'SUCCESS'}

        is_valid, error = handler.validate_completion(completion)

        assert is_valid is False
        assert "workflow_id" in error

    def test_validate_empty_workflow_id(self, handler):
        """Test validation fails when workflow_id is empty string."""
        completion = {'workflow_id': ''}

        is_valid, error = handler.validate_completion(completion)

        assert is_valid is False
        assert "workflow_id" in error

    def test_validate_empty_dict(self, handler):
        """Test validation fails for empty dictionary."""
        completion = {}

        is_valid, error = handler.validate_completion(completion)

        assert is_valid is False
        assert "workflow_id" in error


# ==============================================================================
# Recording Tests
# ==============================================================================

class TestRecordCompletion:
    """Tests for record_completion method."""

    def test_record_minimal_completion(self, handler, temp_workflow_dir):
        """Test recording minimal workflow completion."""
        completion = {'workflow_id': 'test-workflow'}

        success = handler.record_completion(completion)

        assert success is True
        assert handler.completion_file.exists()

        # Verify file contents
        with open(handler.completion_file, 'r') as f:
            data = json.load(f)

        assert data['workflow_id'] == 'test-workflow'
        assert data['final_status'] == 'UNKNOWN'  # Default value
        assert data['completed'] is True
        assert 'timestamp' in data

    def test_record_full_completion(self, handler, temp_workflow_dir):
        """Test recording completion with all fields."""
        completion = {
            'workflow_id': 'test-workflow',
            'final_status': 'SUCCESS',
            'completion_summary': 'All features completed',
            'deliverables': 'Feature X, Tests',
            'knowledge_updates': 'Graph updated with patterns'
        }

        success = handler.record_completion(completion)

        assert success is True

        # Verify file contents
        with open(handler.completion_file, 'r') as f:
            data = json.load(f)

        assert data['workflow_id'] == 'test-workflow'
        assert data['final_status'] == 'SUCCESS'
        assert data['completion_summary'] == 'All features completed'
        assert data['deliverables'] == 'Feature X, Tests'
        assert data['knowledge_updates'] == 'Graph updated with patterns'

    def test_record_creates_directory(self, tmp_path):
        """Test recording creates directory if it doesn't exist."""
        nonexistent_dir = tmp_path / 'nonexistent' / '.workflow'
        handler = WorkflowCompletionHandler(workflow_dir=nonexistent_dir)

        completion = {'workflow_id': 'test-workflow'}
        success = handler.record_completion(completion)

        assert success is True
        assert nonexistent_dir.exists()
        assert handler.completion_file.exists()

    def test_record_overwrites_existing(self, handler, temp_workflow_dir):
        """Test recording overwrites existing completion file."""
        # Record first completion
        completion1 = {'workflow_id': 'workflow-1'}
        handler.record_completion(completion1)

        # Record second completion (should overwrite)
        completion2 = {'workflow_id': 'workflow-2'}
        success = handler.record_completion(completion2)

        assert success is True

        # Verify only second completion exists
        with open(handler.completion_file, 'r') as f:
            data = json.load(f)

        assert data['workflow_id'] == 'workflow-2'

    def test_record_uses_atomic_write(self, handler, temp_workflow_dir):
        """Test recording uses atomic write (temp file then rename)."""
        completion = {'workflow_id': 'test-workflow'}

        success = handler.record_completion(completion)

        assert success is True
        # Temp file should not exist after successful write
        temp_file = handler.completion_file.with_suffix('.tmp')
        assert not temp_file.exists()

    def test_record_removes_pending_handoff(self, handler, temp_pending_handoff):
        """Test recording removes pending handoff file."""
        # Create pending handoff file
        temp_pending_handoff.write_text('{"next_triad": "Testing"}')
        assert temp_pending_handoff.exists()

        # Record completion
        completion = {'workflow_id': 'test-workflow'}
        success = handler.record_completion(completion)

        assert success is True
        # Pending handoff should be removed
        assert not temp_pending_handoff.exists()

    def test_record_handles_missing_pending_handoff(self, handler, temp_pending_handoff):
        """Test recording succeeds even if pending handoff doesn't exist."""
        # Ensure pending handoff doesn't exist
        if temp_pending_handoff.exists():
            temp_pending_handoff.unlink()

        completion = {'workflow_id': 'test-workflow'}
        success = handler.record_completion(completion)

        assert success is True
        assert handler.completion_file.exists()


# ==============================================================================
# Process Flow Tests
# ==============================================================================

class TestProcess:
    """Tests for process method (full flow)."""

    def test_process_single_valid_completion(self, handler, temp_workflow_dir):
        """Test processing single valid workflow completion."""
        text = """
        [WORKFLOW_COMPLETE]
        workflow_id: idea-validation
        final_status: SUCCESS
        [/WORKFLOW_COMPLETE]
        """

        result = handler.process(text)

        assert result['count'] == 1
        assert result['success'] is True
        assert result['recorded'] == 1
        assert len(result['completions']) == 1
        assert len(result['errors']) == 0
        assert handler.completion_file.exists()

    def test_process_multiple_valid_completions(self, handler, temp_workflow_dir):
        """Test processing multiple valid workflow completions."""
        text = """
        [WORKFLOW_COMPLETE]
        workflow_id: idea-validation
        final_status: SUCCESS
        [/WORKFLOW_COMPLETE]

        [WORKFLOW_COMPLETE]
        workflow_id: design-phase
        final_status: SUCCESS
        [/WORKFLOW_COMPLETE]
        """

        result = handler.process(text)

        # Note: Only last completion is recorded (overwrites previous)
        assert result['count'] == 2
        assert result['recorded'] == 2  # Both processed
        assert len(result['completions']) == 2

    def test_process_invalid_completion(self, handler, temp_workflow_dir):
        """Test processing invalid workflow completion."""
        text = """
        [WORKFLOW_COMPLETE]
        final_status: SUCCESS
        [/WORKFLOW_COMPLETE]
        """

        result = handler.process(text)

        assert result['count'] == 1
        assert result['success'] is False
        assert result['recorded'] == 0
        assert len(result['errors']) == 1
        assert 'workflow_id' in result['errors'][0]['error']
        assert not handler.completion_file.exists()

    def test_process_mixed_valid_invalid(self, handler, temp_workflow_dir):
        """Test processing mix of valid and invalid completions."""
        text = """
        [WORKFLOW_COMPLETE]
        workflow_id: valid-workflow
        [/WORKFLOW_COMPLETE]

        [WORKFLOW_COMPLETE]
        final_status: SUCCESS
        [/WORKFLOW_COMPLETE]
        """

        result = handler.process(text)

        assert result['count'] == 2
        assert result['success'] is False  # Not all succeeded
        assert result['recorded'] == 1  # Only first one
        assert len(result['errors']) == 1  # Second one failed

    def test_process_empty_text(self, handler, temp_workflow_dir):
        """Test processing empty text."""
        result = handler.process("")

        assert result['count'] == 0
        assert result['success'] is True
        # Note: 'recorded' is not in result for empty text case
        assert len(result['completions']) == 0
        assert len(result['errors']) == 0

    def test_process_no_completion_blocks(self, handler, temp_workflow_dir):
        """Test processing text without completion blocks."""
        text = "This is just regular text."

        result = handler.process(text)

        assert result['count'] == 0
        assert result['success'] is True

    def test_process_complex_completion(self, handler, temp_workflow_dir, temp_pending_handoff):
        """Test processing complex completion with all fields."""
        # Create pending handoff
        temp_pending_handoff.write_text('{"next_triad": "Testing"}')

        text = """
        Implementation phase complete!

        [WORKFLOW_COMPLETE]
        workflow_id: implementation-phase
        final_status: SUCCESS
        completion_summary: |
          | All features implemented
          | Unit tests: 150 passing
          | Integration tests: 45 passing
          | Code review completed
        deliverables: |
          | User authentication module
          | API endpoints (15 total)
          | Database migrations
          | Documentation
        knowledge_updates: |
          | Added implementation patterns to graph
          | Documented edge cases in auth flow
          | Updated security best practices
        [/WORKFLOW_COMPLETE]

        All quality gates passed!
        """

        result = handler.process(text)

        assert result['count'] == 1
        assert result['success'] is True
        assert result['recorded'] == 1

        # Verify completion file
        with open(handler.completion_file, 'r') as f:
            data = json.load(f)

        assert data['workflow_id'] == 'implementation-phase'
        assert data['final_status'] == 'SUCCESS'
        assert 'All features implemented' in data['completion_summary']
        assert 'User authentication module' in data['deliverables']
        assert 'implementation patterns' in data['knowledge_updates']

        # Verify pending handoff was removed
        assert not temp_pending_handoff.exists()


# ==============================================================================
# Edge Cases and Error Handling
# ==============================================================================

class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_special_characters_in_summary(self, handler):
        """Test handling of special characters in summary."""
        text = """
        [WORKFLOW_COMPLETE]
        workflow_id: test
        completion_summary: |
          | Special chars: <>&"'
          | Unicode: café résumé 日本語
        [/WORKFLOW_COMPLETE]
        """

        completions = handler.extract_completions(text)

        assert len(completions) == 1
        assert '<>&"\'' in completions[0]['completion_summary']
        assert 'café' in completions[0]['completion_summary']

    def test_very_long_summary(self, handler, temp_workflow_dir):
        """Test handling of very long completion summary."""
        long_summary = '\n'.join([f'| Line {i}' for i in range(1000)])
        text = f"""
        [WORKFLOW_COMPLETE]
        workflow_id: test
        completion_summary: |
{long_summary}
        [/WORKFLOW_COMPLETE]
        """

        result = handler.process(text)

        assert result['count'] == 1
        assert result['success'] is True

    def test_whitespace_handling(self, handler):
        """Test handling of various whitespace in completions."""
        text = """
        [WORKFLOW_COMPLETE]
          workflow_id:   test-workflow
          final_status:SUCCESS
        [/WORKFLOW_COMPLETE]
        """

        completions = handler.extract_completions(text)

        assert len(completions) == 1
        assert completions[0]['workflow_id'] == 'test-workflow'
        assert completions[0]['final_status'] == 'SUCCESS'

    def test_case_sensitive_workflow_ids(self, handler, temp_workflow_dir):
        """Test that workflow IDs preserve case."""
        text = """
        [WORKFLOW_COMPLETE]
        workflow_id: MyCustomWorkflow-v2
        [/WORKFLOW_COMPLETE]
        """

        result = handler.process(text)

        with open(handler.completion_file, 'r') as f:
            data = json.load(f)

        assert data['workflow_id'] == 'MyCustomWorkflow-v2'

    def test_failed_status_handling(self, handler, temp_workflow_dir):
        """Test recording of failed workflow."""
        text = """
        [WORKFLOW_COMPLETE]
        workflow_id: failed-workflow
        final_status: FAILED
        completion_summary: |
          | Integration tests failed
          | Rolled back changes
        [/WORKFLOW_COMPLETE]
        """

        result = handler.process(text)

        assert result['count'] == 1
        assert result['success'] is True

        with open(handler.completion_file, 'r') as f:
            data = json.load(f)

        assert data['final_status'] == 'FAILED'
        assert 'Integration tests failed' in data['completion_summary']

    def test_partial_status_handling(self, handler, temp_workflow_dir):
        """Test recording of partially completed workflow."""
        text = """
        [WORKFLOW_COMPLETE]
        workflow_id: partial-workflow
        final_status: PARTIAL
        completion_summary: |
          | Core features completed
          | Optional features deferred
        [/WORKFLOW_COMPLETE]
        """

        result = handler.process(text)

        with open(handler.completion_file, 'r') as f:
            data = json.load(f)

        assert data['final_status'] == 'PARTIAL'

    def test_empty_multiline_fields(self, handler):
        """Test handling of empty multiline fields."""
        text = """
        [WORKFLOW_COMPLETE]
        workflow_id: test
        completion_summary: |
        deliverables: |
        [/WORKFLOW_COMPLETE]
        """

        completions = handler.extract_completions(text)

        assert len(completions) == 1
        assert completions[0]['workflow_id'] == 'test'
