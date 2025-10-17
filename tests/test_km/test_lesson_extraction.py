"""Tests for experience-based lesson extraction (Day 3)."""

import json
import sys
from pathlib import Path

import pytest

# Add src to path for imports
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root))

# Import hook functions directly
hook_path = repo_root / "hooks" / "on_stop.py"
spec = {'__file__': str(hook_path)}  # Set __file__ for exec context
with open(hook_path) as f:
    exec(f.read(), spec)

extract_process_knowledge_blocks = spec['extract_process_knowledge_blocks']
parse_process_knowledge_block = spec['parse_process_knowledge_block']
detect_user_corrections = spec['detect_user_corrections']
detect_repeated_mistakes = spec['detect_repeated_mistakes']
infer_priority_from_context = spec['infer_priority_from_context']
create_process_knowledge_node = spec['create_process_knowledge_node']
extract_lessons_from_conversation = spec['extract_lessons_from_conversation']


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def sample_process_knowledge_block():
    """Sample PROCESS_KNOWLEDGE block."""
    return """
[PROCESS_KNOWLEDGE]
type: checklist
label: Version Bump File Checklist
priority: CRITICAL
process_type: checklist
triad: deployment
trigger_conditions:
  tool_names: ["Write", "Edit"]
  file_patterns: ["**/plugin.json", "**/marketplace.json"]
  action_keywords: ["version", "bump", "release"]
checklist:
  - item: Update plugin.json version field required: true file: .claude-plugin/plugin.json
  - item: Update marketplace.json plugins[].version required: true file: .claude-plugin/marketplace.json
  - item: Update pyproject.toml project.version required: true file: pyproject.toml
[/PROCESS_KNOWLEDGE]
"""


@pytest.fixture
def user_correction_conversation():
    """Conversation with user corrections."""
    return """
User: Why didn't you update marketplace.json when bumping the version?
Assistant: I apologize for missing that. Let me update it now.

User: You forgot the CHANGELOG.md entry as well.
Assistant: You're right, I'll add that too.

User: Don't forget to run tests after making changes.
Assistant: Absolutely, running tests now.
"""


@pytest.fixture
def repeated_mistake_conversation():
    """Conversation with repeated mistakes."""
    return """
Assistant: I've updated plugin.json.
User: You need to update marketplace.json again - it's still at the old version.

Later in conversation...
Assistant: Version bump complete.
User: Another file was missing - you forgot marketplace.json still.
"""


# ============================================================================
# Test PROCESS_KNOWLEDGE Block Extraction
# ============================================================================

def test_extract_process_knowledge_blocks(sample_process_knowledge_block):
    """Test extraction of [PROCESS_KNOWLEDGE] blocks."""
    lessons = extract_process_knowledge_blocks(sample_process_knowledge_block)

    assert len(lessons) == 1
    lesson = lessons[0]

    assert lesson['type'] == 'Concept'
    assert lesson['label'] == 'Version Bump File Checklist'
    assert lesson['priority'] == 'CRITICAL'
    assert lesson['process_type'] == 'checklist'
    assert lesson['triad'] == 'deployment'

    # Check trigger conditions
    assert 'Write' in lesson['trigger_conditions']['tool_names']
    assert 'Edit' in lesson['trigger_conditions']['tool_names']
    assert '**/plugin.json' in lesson['trigger_conditions']['file_patterns']
    assert 'version' in lesson['trigger_conditions']['action_keywords']

    # Check checklist items
    assert len(lesson['checklist']) == 3
    assert any('plugin.json' in item['item'] for item in lesson['checklist'])
    assert any('marketplace.json' in item['item'] for item in lesson['checklist'])
    assert any('pyproject.toml' in item['item'] for item in lesson['checklist'])


def test_parse_process_knowledge_block_minimal():
    """Test parsing minimal PROCESS_KNOWLEDGE block."""
    block = """
label: Simple Lesson
type: warning
description: This is a test
"""
    lesson = parse_process_knowledge_block(block)

    assert lesson is not None
    assert lesson['label'] == 'Simple Lesson'
    assert lesson['process_type'] == 'warning'
    assert lesson['description'] == 'This is a test'


def test_parse_process_knowledge_block_missing_label():
    """Test parsing fails without required label."""
    block = """
type: warning
description: Missing label
"""
    lesson = parse_process_knowledge_block(block)

    # Should return None if label is missing
    assert lesson is None


def test_multiple_process_knowledge_blocks():
    """Test extracting multiple blocks from one text."""
    text = """
Some conversation text.

[PROCESS_KNOWLEDGE]
label: Lesson 1
type: warning
[/PROCESS_KNOWLEDGE]

More text.

[PROCESS_KNOWLEDGE]
label: Lesson 2
type: checklist
checklist:
  - item: Check this
[/PROCESS_KNOWLEDGE]
"""
    lessons = extract_process_knowledge_blocks(text)

    assert len(lessons) == 2
    assert lessons[0]['label'] == 'Lesson 1'
    assert lessons[1]['label'] == 'Lesson 2'


# ============================================================================
# Test User Correction Detection
# ============================================================================

def test_detect_user_corrections_missed(user_correction_conversation):
    """Test detection of 'you missed X' pattern."""
    corrections = detect_user_corrections(user_correction_conversation)

    # Should detect at least the "didn't update" and "forgot" patterns
    assert len(corrections) >= 2

    # Check for marketplace.json correction
    marketplace_corrections = [c for c in corrections if 'marketplace' in c['missed_item'].lower()]
    assert len(marketplace_corrections) > 0


def test_detect_user_corrections_forgot():
    """Test detection of 'you forgot X' pattern."""
    text = "You forgot to add the documentation."
    corrections = detect_user_corrections(text)

    assert len(corrections) == 1
    assert corrections[0]['action'] == 'forgot'
    assert 'documentation' in corrections[0]['missed_item'].lower()


def test_detect_user_corrections_dont_forget():
    """Test detection of 'don't forget X' pattern."""
    text = "Don't forget to run the linter."
    corrections = detect_user_corrections(text)

    assert len(corrections) == 1
    assert 'linter' in corrections[0]['missed_item'].lower()


def test_detect_user_corrections_should_have():
    """Test detection of 'you should have X' pattern."""
    text = "You should have checked the config file."
    corrections = detect_user_corrections(text)

    assert len(corrections) == 1
    assert 'config' in corrections[0]['missed_item'].lower()


def test_detect_user_corrections_why_didnt():
    """Test detection of 'why didn't you X' pattern."""
    text = "Why didn't you validate the input?"
    corrections = detect_user_corrections(text)

    assert len(corrections) == 1
    assert 'validate' in corrections[0]['missed_item'].lower()


def test_detect_no_corrections():
    """Test no false positives on normal conversation."""
    text = """
User: Great work on the implementation!
Assistant: Thank you!
User: The tests are all passing.
"""
    corrections = detect_user_corrections(text)

    assert len(corrections) == 0


# ============================================================================
# Test Repeated Mistake Detection
# ============================================================================

def test_detect_repeated_mistakes_again(repeated_mistake_conversation):
    """Test detection of 'X again' pattern."""
    repeated = detect_repeated_mistakes(repeated_mistake_conversation, [])

    assert len(repeated) >= 1

    # Should detect "update marketplace.json again"
    marketplace_repeats = [r for r in repeated if 'marketplace' in r['item'].lower()]
    assert len(marketplace_repeats) > 0


def test_detect_repeated_mistakes_another():
    """Test detection of 'another X was missing' pattern."""
    text = "Another configuration file was missing from the commit."
    repeated = detect_repeated_mistakes(text, [])

    assert len(repeated) == 1
    assert 'configuration file' in repeated[0]['item'].lower()


def test_detect_repeated_mistakes_still():
    """Test detection of 'still missing X' pattern."""
    text = "The file is still missing from the repository."
    repeated = detect_repeated_mistakes(text, [])

    assert len(repeated) == 1
    # Regex captures "The file" before "is still missing"
    assert 'file' in repeated[0]['item'].lower()


def test_detect_no_repeated_mistakes():
    """Test no false positives on normal conversation."""
    text = """
Assistant: I've completed the task.
User: Looks good!
"""
    repeated = detect_repeated_mistakes(text, [])

    assert len(repeated) == 0


# ============================================================================
# Test Priority Inference
# ============================================================================

def test_infer_priority_explicit():
    """Test explicit priority is preserved."""
    lesson = {'priority': 'HIGH'}
    priority = infer_priority_from_context(lesson, "")

    assert priority == 'HIGH'


def test_infer_priority_user_correction():
    """Test user corrections are CRITICAL."""
    lesson = {'type': 'user_correction'}
    priority = infer_priority_from_context(lesson, "")

    assert priority == 'CRITICAL'


def test_infer_priority_repeated_mistake():
    """Test repeated mistakes are HIGH."""
    lesson = {'type': 'repeated_mistake'}
    priority = infer_priority_from_context(lesson, "")

    assert priority == 'HIGH'


def test_infer_priority_deployment_context():
    """Test deployment context is CRITICAL."""
    lesson = {'triad': 'deployment'}
    context = "We're doing a release and bumping the version."

    priority = infer_priority_from_context(lesson, context)

    assert priority == 'CRITICAL'


def test_infer_priority_security_context():
    """Test security-related is HIGH."""
    lesson = {
        'description': 'Add input validation to prevent injection attacks'
    }
    priority = infer_priority_from_context(lesson, "")

    assert priority == 'HIGH'


def test_infer_priority_default():
    """Test default priority is LOW."""
    lesson = {}
    priority = infer_priority_from_context(lesson, "")

    assert priority == 'LOW'


# ============================================================================
# Test Process Knowledge Node Creation
# ============================================================================

def test_create_process_knowledge_node_basic():
    """Test creating basic process knowledge node."""
    lesson_data = {
        'type': 'user_correction',
        'label': 'Test Lesson',
        'description': 'This is a test',
        'process_type': 'warning',
        'missed_item': 'check the logs'
    }

    node = create_process_knowledge_node(lesson_data, "")

    assert node['type'] == 'Concept'
    assert node['label'] == 'Test Lesson'
    assert node['description'] == 'This is a test'
    assert node['process_type'] == 'warning'
    assert node['status'] == 'draft'
    assert node['created_by'] == 'experience-learning-system'
    assert node['confidence'] == 0.9
    assert 'id' in node
    assert node['id'].startswith('process_')


def test_create_process_knowledge_node_with_checklist():
    """Test creating node with checklist."""
    lesson_data = {
        'label': 'Checklist Lesson',
        'process_type': 'checklist',
        'checklist': [
            {'item': 'Check file A', 'required': True},
            {'item': 'Check file B', 'required': False}
        ]
    }

    node = create_process_knowledge_node(lesson_data, "")

    assert node['process_type'] == 'checklist'
    assert 'checklist' in node
    assert len(node['checklist']) == 2
    assert node['checklist'][0]['item'] == 'Check file A'


def test_create_process_knowledge_node_with_trigger_conditions():
    """Test creating node with trigger conditions."""
    lesson_data = {
        'label': 'Triggered Lesson',
        'trigger_conditions': {
            'tool_names': ['Write', 'Edit'],
            'file_patterns': ['*.json'],
            'action_keywords': ['version']
        }
    }

    node = create_process_knowledge_node(lesson_data, "")

    assert 'trigger_conditions' in node
    assert 'Write' in node['trigger_conditions']['tool_names']
    assert '*.json' in node['trigger_conditions']['file_patterns']
    assert 'version' in node['trigger_conditions']['action_keywords']


def test_create_process_knowledge_node_warning_type():
    """Test creating warning-type node."""
    lesson_data = {
        'label': 'Warning Lesson',
        'process_type': 'warning',
        'description': 'This will cause problems',
        'missed_item': 'validation check'
    }

    node = create_process_knowledge_node(lesson_data, "")

    assert node['process_type'] == 'warning'
    assert 'warning' in node
    assert node['warning']['condition'] == 'validation check'
    assert node['warning']['consequence'] == 'This will cause problems'


# ============================================================================
# Test Full Lesson Extraction
# ============================================================================

def test_extract_lessons_explicit_block(sample_process_knowledge_block):
    """Test extracting explicit PROCESS_KNOWLEDGE blocks."""
    lessons = extract_lessons_from_conversation(sample_process_knowledge_block, [])

    assert len(lessons) >= 1

    # Should have the explicit lesson
    explicit_lessons = [l for l in lessons if 'Version Bump' in l['label']]
    assert len(explicit_lessons) == 1

    lesson = explicit_lessons[0]
    assert lesson['status'] == 'draft'
    assert lesson['type'] == 'Concept'


def test_extract_lessons_user_corrections(user_correction_conversation):
    """Test extracting lessons from user corrections."""
    lessons = extract_lessons_from_conversation(user_correction_conversation, [])

    assert len(lessons) >= 2

    # Should detect marketplace.json and CHANGELOG.md corrections
    marketplace_lessons = [l for l in lessons if 'marketplace' in l['label'].lower()]
    changelog_lessons = [l for l in lessons if 'changelog' in l['label'].lower()]

    assert len(marketplace_lessons) > 0
    assert len(changelog_lessons) > 0

    # All should be CRITICAL priority (user corrections)
    for lesson in lessons:
        assert lesson['priority'] == 'CRITICAL'
        assert lesson['status'] == 'draft'


def test_extract_lessons_repeated_mistakes(repeated_mistake_conversation):
    """Test extracting lessons from repeated mistakes."""
    lessons = extract_lessons_from_conversation(repeated_mistake_conversation, [])

    assert len(lessons) >= 1

    # Should detect marketplace.json lessons (may be detected as user_correction or repeated_mistake)
    marketplace_lessons = [l for l in lessons if 'marketplace' in l['label'].lower()]
    assert len(marketplace_lessons) > 0

    # These lessons should be HIGH or CRITICAL priority (both acceptable for repeated issues)
    for lesson in marketplace_lessons:
        assert lesson['priority'] in ['HIGH', 'CRITICAL']


def test_extract_lessons_combined():
    """Test extracting lessons from combined conversation."""
    text = """
User: You forgot to update marketplace.json.

[PROCESS_KNOWLEDGE]
label: Always Check Marketplace
type: checklist
checklist:
  - item: Verify marketplace.json is updated
[/PROCESS_KNOWLEDGE]

User: You need to update it again - still missing.
"""

    lessons = extract_lessons_from_conversation(text, [])

    # Should extract:
    # 1. Explicit PROCESS_KNOWLEDGE block
    # 2. User correction ("forgot")
    # 3. Repeated mistake ("again - still missing")
    assert len(lessons) >= 3

    # Check we have different types
    types = {l['process_type'] for l in lessons}
    assert 'checklist' in types  # From explicit block
    assert 'warning' in types  # From corrections/mistakes


def test_extract_no_lessons():
    """Test no false positives on normal conversation."""
    text = """
User: Great work!
Assistant: Thank you!
User: The implementation looks good.
Assistant: I appreciate the feedback.
"""

    lessons = extract_lessons_from_conversation(text, [])

    assert len(lessons) == 0


# ============================================================================
# Test Edge Cases and Error Handling
# ============================================================================

def test_empty_conversation():
    """Test handling empty conversation."""
    lessons = extract_lessons_from_conversation("", [])
    assert len(lessons) == 0


def test_malformed_process_knowledge_block():
    """Test handling malformed PROCESS_KNOWLEDGE block."""
    text = """
[PROCESS_KNOWLEDGE]
This is not properly formatted
No key-value pairs
[/PROCESS_KNOWLEDGE]
"""

    lessons = extract_lessons_from_conversation(text, [])

    # Should not crash, might return 0 or 1 depending on validation
    assert isinstance(lessons, list)


def test_special_characters_in_corrections():
    """Test handling special characters in user corrections."""
    text = "You forgot to update the file: config/app.json (line 42)."
    corrections = detect_user_corrections(text)

    assert len(corrections) == 1
    assert 'config' in corrections[0]['missed_item'] or 'update' in corrections[0]['missed_item']


def test_multiline_correction():
    """Test detection across multiple lines."""
    text = """
User: You missed
the important validation step.
"""
    corrections = detect_user_corrections(text)

    # Should detect even across lines
    assert len(corrections) >= 1


# ============================================================================
# Performance Tests
# ============================================================================

def test_lesson_extraction_performance():
    """Test lesson extraction performance on large conversation."""
    # Create large conversation with mixed content
    large_text = "\n".join([
        "User: Some text here." * 100,
        "You forgot something.",
        "Assistant: Response." * 100,
        "[PROCESS_KNOWLEDGE]\nlabel: Test\n[/PROCESS_KNOWLEDGE]",
        "More conversation." * 100,
        "Another file was missing.",
    ])

    import time
    start = time.time()
    lessons = extract_lessons_from_conversation(large_text, [])
    duration = time.time() - start

    # Should complete in reasonable time (< 1 second)
    assert duration < 1.0
    assert len(lessons) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
