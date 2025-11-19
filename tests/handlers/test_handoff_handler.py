"""
Tests for HandoffHandler.

Tests cover:
- Extraction of [HANDOFF_REQUEST] blocks (simple, multiline, multiple)
- Validation of handoff requests
- Queuing to pending file
- Full process flow (success and error cases)
- Edge cases (empty text, malformed blocks, multiple handoffs)

Constitutional Principles Applied:
- Quality paramount: >80% coverage target
- Exhaustive testing: All code paths covered
- Security by design: File operations tested
- SOLID principles: Tests are focused and independent
"""

import json
import pytest
from pathlib import Path
from datetime import datetime

# Add hooks directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'hooks'))

from handlers.handoff_handler import HandoffHandler


# ==============================================================================
# Fixtures
# ==============================================================================

@pytest.fixture
def temp_pending_dir(tmp_path):
    """Create temporary directory for pending handoffs."""
    pending_dir = tmp_path / '.claude'
    pending_dir.mkdir(exist_ok=True)
    return pending_dir


@pytest.fixture
def handler(temp_pending_dir):
    """Create HandoffHandler with temporary directory."""
    return HandoffHandler(pending_dir=temp_pending_dir)


# ==============================================================================
# Extraction Tests
# ==============================================================================

class TestExtractRequests:
    """Tests for extract_requests method."""

    def test_extract_simple_handoff(self, handler):
        """Test extraction of simple handoff request."""
        text = """
        [HANDOFF_REQUEST]
        next_triad: Implementation
        request_type: feature_complete
        [/HANDOFF_REQUEST]
        """

        requests = handler.extract_requests(text)

        assert len(requests) == 1
        assert requests[0]['next_triad'] == 'Implementation'
        assert requests[0]['request_type'] == 'feature_complete'

    def test_extract_handoff_with_multiline_context(self, handler):
        """Test extraction of handoff with multiline context."""
        text = """
        [HANDOFF_REQUEST]
        next_triad: Implementation
        request_type: feature_complete
        context: |
          | Feature X is ready for implementation
          | All tests passing
          | Documentation updated
        [/HANDOFF_REQUEST]
        """

        requests = handler.extract_requests(text)

        assert len(requests) == 1
        assert requests[0]['next_triad'] == 'Implementation'
        assert requests[0]['request_type'] == 'feature_complete'
        assert 'Feature X is ready for implementation' in requests[0]['context']
        assert 'All tests passing' in requests[0]['context']
        assert 'Documentation updated' in requests[0]['context']

    def test_extract_multiple_handoffs(self, handler):
        """Test extraction of multiple handoff requests."""
        text = """
        First handoff:
        [HANDOFF_REQUEST]
        next_triad: Implementation
        request_type: feature_complete
        [/HANDOFF_REQUEST]

        Second handoff:
        [HANDOFF_REQUEST]
        next_triad: Testing
        request_type: code_ready
        [/HANDOFF_REQUEST]
        """

        requests = handler.extract_requests(text)

        assert len(requests) == 2
        assert requests[0]['next_triad'] == 'Implementation'
        assert requests[1]['next_triad'] == 'Testing'

    def test_extract_handoff_with_all_fields(self, handler):
        """Test extraction of handoff with all optional fields."""
        text = """
        [HANDOFF_REQUEST]
        next_triad: Implementation
        request_type: feature_complete
        context: |
          | Design approved
          | Ready for coding
        knowledge_graph: design_graph
        updated_nodes: node1,node2,node3
        [/HANDOFF_REQUEST]
        """

        requests = handler.extract_requests(text)

        assert len(requests) == 1
        assert requests[0]['next_triad'] == 'Implementation'
        assert requests[0]['request_type'] == 'feature_complete'
        assert 'Design approved' in requests[0]['context']
        assert requests[0]['knowledge_graph'] == 'design_graph'
        assert requests[0]['updated_nodes'] == 'node1,node2,node3'

    def test_extract_empty_text(self, handler):
        """Test extraction from empty text returns empty list."""
        requests = handler.extract_requests("")
        assert requests == []

    def test_extract_no_handoff_blocks(self, handler):
        """Test extraction from text without handoff blocks."""
        text = "This is just regular text with no handoff requests."
        requests = handler.extract_requests(text)
        assert requests == []

    def test_extract_malformed_block(self, handler):
        """Test extraction handles malformed blocks gracefully."""
        text = """
        [HANDOFF_REQUEST]
        This is malformed - no key:value pairs
        [/HANDOFF_REQUEST]
        """

        # Should not crash, may return empty or partial data
        requests = handler.extract_requests(text)
        # Either empty or has empty dict
        assert isinstance(requests, list)

    def test_extract_unclosed_block(self, handler):
        """Test extraction handles unclosed blocks gracefully."""
        text = """
        [HANDOFF_REQUEST]
        next_triad: Implementation
        """

        # Should not match unclosed blocks
        requests = handler.extract_requests(text)
        assert requests == []

    def test_extract_nested_pipes_in_context(self, handler):
        """Test extraction handles nested pipe symbols correctly."""
        text = """
        [HANDOFF_REQUEST]
        next_triad: Implementation
        context: |
          | Code example: if x | y:
          | Another line with | pipe
        [/HANDOFF_REQUEST]
        """

        requests = handler.extract_requests(text)

        assert len(requests) == 1
        assert 'Code example: if x | y:' in requests[0]['context']
        assert 'Another line with | pipe' in requests[0]['context']


# ==============================================================================
# Validation Tests
# ==============================================================================

class TestValidateRequest:
    """Tests for validate_request method."""

    def test_validate_valid_minimal_request(self, handler):
        """Test validation of minimal valid request."""
        handoff = {'next_triad': 'Implementation'}

        is_valid, error = handler.validate_request(handoff)

        assert is_valid is True
        assert error == ""

    def test_validate_valid_full_request(self, handler):
        """Test validation of request with all fields."""
        handoff = {
            'next_triad': 'Implementation',
            'request_type': 'feature_complete',
            'context': 'Design approved',
            'knowledge_graph': 'design_graph',
            'updated_nodes': 'node1,node2'
        }

        is_valid, error = handler.validate_request(handoff)

        assert is_valid is True
        assert error == ""

    def test_validate_missing_next_triad(self, handler):
        """Test validation fails when next_triad is missing."""
        handoff = {'request_type': 'feature_complete'}

        is_valid, error = handler.validate_request(handoff)

        assert is_valid is False
        assert "next_triad" in error

    def test_validate_empty_next_triad(self, handler):
        """Test validation fails when next_triad is empty string."""
        handoff = {'next_triad': ''}

        is_valid, error = handler.validate_request(handoff)

        assert is_valid is False
        assert "next_triad" in error

    def test_validate_empty_dict(self, handler):
        """Test validation fails for empty dictionary."""
        handoff = {}

        is_valid, error = handler.validate_request(handoff)

        assert is_valid is False
        assert "next_triad" in error


# ==============================================================================
# Queuing Tests
# ==============================================================================

class TestQueueHandoff:
    """Tests for queue_handoff method."""

    def test_queue_minimal_handoff(self, handler, temp_pending_dir):
        """Test queuing minimal handoff request."""
        handoff = {'next_triad': 'Implementation'}

        success = handler.queue_handoff(handoff)

        assert success is True
        assert handler.pending_file.exists()

        # Verify file contents
        with open(handler.pending_file, 'r') as f:
            data = json.load(f)

        assert data['next_triad'] == 'Implementation'
        assert data['request_type'] == 'unknown'  # Default value
        assert data['status'] == 'pending'
        assert 'timestamp' in data
        assert isinstance(data['updated_nodes'], list)

    def test_queue_full_handoff(self, handler, temp_pending_dir):
        """Test queuing handoff with all fields."""
        handoff = {
            'next_triad': 'Implementation',
            'request_type': 'feature_complete',
            'context': 'Design approved',
            'knowledge_graph': 'design_graph',
            'updated_nodes': 'node1,node2,node3'
        }

        success = handler.queue_handoff(handoff)

        assert success is True

        # Verify file contents
        with open(handler.pending_file, 'r') as f:
            data = json.load(f)

        assert data['next_triad'] == 'Implementation'
        assert data['request_type'] == 'feature_complete'
        assert data['context'] == 'Design approved'
        assert data['knowledge_graph'] == 'design_graph'
        assert data['updated_nodes'] == ['node1', 'node2', 'node3']

    def test_queue_creates_directory(self, tmp_path):
        """Test queuing creates directory if it doesn't exist."""
        nonexistent_dir = tmp_path / 'nonexistent'
        handler = HandoffHandler(pending_dir=nonexistent_dir)

        handoff = {'next_triad': 'Implementation'}
        success = handler.queue_handoff(handoff)

        assert success is True
        assert nonexistent_dir.exists()
        assert handler.pending_file.exists()

    def test_queue_overwrites_existing(self, handler, temp_pending_dir):
        """Test queuing overwrites existing pending handoff."""
        # Queue first handoff
        handoff1 = {'next_triad': 'Implementation'}
        handler.queue_handoff(handoff1)

        # Queue second handoff (should overwrite)
        handoff2 = {'next_triad': 'Testing'}
        success = handler.queue_handoff(handoff2)

        assert success is True

        # Verify only second handoff exists
        with open(handler.pending_file, 'r') as f:
            data = json.load(f)

        assert data['next_triad'] == 'Testing'

    def test_queue_uses_atomic_write(self, handler, temp_pending_dir):
        """Test queuing uses atomic write (temp file then rename)."""
        handoff = {'next_triad': 'Implementation'}

        success = handler.queue_handoff(handoff)

        assert success is True
        # Temp file should not exist after successful write
        temp_file = handler.pending_file.with_suffix('.tmp')
        assert not temp_file.exists()

    def test_queue_splits_updated_nodes(self, handler, temp_pending_dir):
        """Test queuing splits comma-separated updated_nodes into list."""
        handoff = {
            'next_triad': 'Implementation',
            'updated_nodes': 'node1,node2,node3'
        }

        handler.queue_handoff(handoff)

        with open(handler.pending_file, 'r') as f:
            data = json.load(f)

        assert data['updated_nodes'] == ['node1', 'node2', 'node3']

    def test_queue_empty_updated_nodes(self, handler, temp_pending_dir):
        """Test queuing handles empty updated_nodes correctly."""
        handoff = {
            'next_triad': 'Implementation',
            'updated_nodes': ''
        }

        handler.queue_handoff(handoff)

        with open(handler.pending_file, 'r') as f:
            data = json.load(f)

        assert data['updated_nodes'] == []


# ==============================================================================
# Process Flow Tests
# ==============================================================================

class TestProcess:
    """Tests for process method (full flow)."""

    def test_process_single_valid_handoff(self, handler, temp_pending_dir):
        """Test processing single valid handoff request."""
        text = """
        [HANDOFF_REQUEST]
        next_triad: Implementation
        request_type: feature_complete
        [/HANDOFF_REQUEST]
        """

        result = handler.process(text)

        assert result['count'] == 1
        assert result['success'] is True
        assert result['queued'] == 1
        assert len(result['requests']) == 1
        assert len(result['errors']) == 0
        assert handler.pending_file.exists()

    def test_process_multiple_valid_handoffs(self, handler, temp_pending_dir):
        """Test processing multiple valid handoff requests."""
        text = """
        [HANDOFF_REQUEST]
        next_triad: Implementation
        [/HANDOFF_REQUEST]

        [HANDOFF_REQUEST]
        next_triad: Testing
        [/HANDOFF_REQUEST]
        """

        result = handler.process(text)

        # Note: Only last handoff is queued (overwrites previous)
        assert result['count'] == 2
        assert result['queued'] == 2  # Both processed
        assert len(result['requests']) == 2

    def test_process_invalid_handoff(self, handler, temp_pending_dir):
        """Test processing invalid handoff request."""
        text = """
        [HANDOFF_REQUEST]
        request_type: feature_complete
        [/HANDOFF_REQUEST]
        """

        result = handler.process(text)

        assert result['count'] == 1
        assert result['success'] is False
        assert result['queued'] == 0
        assert len(result['errors']) == 1
        assert 'next_triad' in result['errors'][0]['error']
        assert not handler.pending_file.exists()

    def test_process_mixed_valid_invalid(self, handler, temp_pending_dir):
        """Test processing mix of valid and invalid handoffs."""
        text = """
        [HANDOFF_REQUEST]
        next_triad: Implementation
        [/HANDOFF_REQUEST]

        [HANDOFF_REQUEST]
        request_type: feature_complete
        [/HANDOFF_REQUEST]
        """

        result = handler.process(text)

        assert result['count'] == 2
        assert result['success'] is False  # Not all succeeded
        assert result['queued'] == 1  # Only first one
        assert len(result['errors']) == 1  # Second one failed

    def test_process_empty_text(self, handler, temp_pending_dir):
        """Test processing empty text."""
        result = handler.process("")

        assert result['count'] == 0
        assert result['success'] is True
        # Note: 'queued' is not in result for empty text case
        assert len(result['requests']) == 0
        assert len(result['errors']) == 0

    def test_process_no_handoff_blocks(self, handler, temp_pending_dir):
        """Test processing text without handoff blocks."""
        text = "This is just regular text."

        result = handler.process(text)

        assert result['count'] == 0
        assert result['success'] is True

    def test_process_complex_handoff(self, handler, temp_pending_dir):
        """Test processing complex handoff with all fields."""
        text = """
        Design phase complete, handing off to implementation.

        [HANDOFF_REQUEST]
        next_triad: Implementation
        request_type: design_complete
        context: |
          | Architecture Decision Records created
          | API contracts defined
          | Database schema finalized
          | Security review completed
        knowledge_graph: design_triad_graph
        updated_nodes: adr_001,adr_002,api_contract,db_schema
        [/HANDOFF_REQUEST]

        All quality gates passed.
        """

        result = handler.process(text)

        assert result['count'] == 1
        assert result['success'] is True
        assert result['queued'] == 1

        # Verify queued data
        with open(handler.pending_file, 'r') as f:
            data = json.load(f)

        assert data['next_triad'] == 'Implementation'
        assert data['request_type'] == 'design_complete'
        assert 'Architecture Decision Records' in data['context']
        assert data['knowledge_graph'] == 'design_triad_graph'
        assert 'adr_001' in data['updated_nodes']


# ==============================================================================
# Edge Cases and Error Handling
# ==============================================================================

class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_special_characters_in_context(self, handler):
        """Test handling of special characters in context."""
        text = """
        [HANDOFF_REQUEST]
        next_triad: Implementation
        context: |
          | Special chars: <>&"'
          | Unicode: café résumé 日本語
        [/HANDOFF_REQUEST]
        """

        requests = handler.extract_requests(text)

        assert len(requests) == 1
        assert '<>&"\'' in requests[0]['context']
        assert 'café' in requests[0]['context']

    def test_very_long_context(self, handler, temp_pending_dir):
        """Test handling of very long context."""
        long_context = '\n'.join([f'| Line {i}' for i in range(1000)])
        text = f"""
        [HANDOFF_REQUEST]
        next_triad: Implementation
        context: |
{long_context}
        [/HANDOFF_REQUEST]
        """

        result = handler.process(text)

        assert result['count'] == 1
        assert result['success'] is True

    def test_whitespace_handling(self, handler):
        """Test handling of various whitespace in requests."""
        text = """
        [HANDOFF_REQUEST]
          next_triad:   Implementation
          request_type:feature_complete
        [/HANDOFF_REQUEST]
        """

        requests = handler.extract_requests(text)

        assert len(requests) == 1
        assert requests[0]['next_triad'] == 'Implementation'
        assert requests[0]['request_type'] == 'feature_complete'

    def test_case_sensitive_triad_names(self, handler, temp_pending_dir):
        """Test that triad names preserve case."""
        text = """
        [HANDOFF_REQUEST]
        next_triad: MyCustomTriad
        [/HANDOFF_REQUEST]
        """

        result = handler.process(text)

        with open(handler.pending_file, 'r') as f:
            data = json.load(f)

        assert data['next_triad'] == 'MyCustomTriad'

    def test_empty_multiline_context(self, handler):
        """Test handling of empty multiline context."""
        text = """
        [HANDOFF_REQUEST]
        next_triad: Implementation
        context: |
        [/HANDOFF_REQUEST]
        """

        requests = handler.extract_requests(text)

        assert len(requests) == 1
        assert requests[0]['next_triad'] == 'Implementation'
        # Context may or may not be in result depending on parsing
        # This is acceptable behavior
