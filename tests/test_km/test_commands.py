"""Tests for knowledge management CLI commands."""

import json
from pathlib import Path

import pytest

from triads.km.commands import validate_lesson, contradict_lesson, review_uncertain


@pytest.fixture
def temp_knowledge_base(tmp_path):
    """Create temporary knowledge base with test lessons."""
    graphs_dir = tmp_path / ".claude" / "graphs"
    graphs_dir.mkdir(parents=True)

    # Create test graph with uncertain lesson
    test_graph = {
        "directed": True,
        "nodes": [
            {
                "id": "uncertain_lesson_001",
                "type": "Concept",
                "label": "Database Migration Pattern",
                "description": "Pattern for database migrations",
                "process_type": "pattern",
                "priority": "MEDIUM",
                "confidence": 0.65,
                "needs_validation": True,
                "deprecated": False,
                "source": "agent_inference",
                "created_at": "2025-10-15T12:00:00",
                "success_count": 1,
                "failure_count": 0,
                "contradiction_count": 0,
                "trigger_conditions": {
                    "tool_names": ["Write"],
                    "file_patterns": ["**/*.sql"],
                    "action_keywords": ["migration"]
                }
            },
            {
                "id": "high_confidence_lesson",
                "type": "Concept",
                "label": "Version Bump Checklist",
                "description": "Checklist for version bumps",
                "process_type": "checklist",
                "priority": "CRITICAL",
                "confidence": 0.95,
                "needs_validation": False,
                "deprecated": False,
                "source": "user_correction",
                "created_at": "2025-10-10T10:00:00",
                "success_count": 5,
                "failure_count": 0,
                "contradiction_count": 0,
                "trigger_conditions": {
                    "tool_names": ["Write", "Edit"],
                    "file_patterns": ["**/plugin.json"]
                }
            },
            {
                "id": "deprecated_lesson",
                "type": "Concept",
                "label": "Old Pattern",
                "description": "Deprecated pattern",
                "process_type": "pattern",
                "priority": "LOW",
                "confidence": 0.25,
                "needs_validation": False,
                "deprecated": True,
                "deprecated_reason": "No longer applicable",
                "source": "agent_inference",
                "created_at": "2025-10-01T10:00:00"
            }
        ],
        "links": [],
        "_meta": {
            "triad_name": "design",
            "updated_at": "2025-10-15T12:00:00",
            "node_count": 3,
            "edge_count": 0
        }
    }

    graph_file = graphs_dir / "design_graph.json"
    graph_file.write_text(json.dumps(test_graph, indent=2))

    return tmp_path


# ============================================================================
# Validate Lesson Tests
# ============================================================================


def test_validate_lesson_by_label(temp_knowledge_base):
    """Should validate lesson by label and increase confidence."""
    result = validate_lesson("Database Migration Pattern", base_dir=temp_knowledge_base)

    assert "✅ Validated" in result
    assert "Database Migration Pattern" in result
    assert "65%" in result  # Old confidence
    assert "78%" in result  # New confidence (0.65 * 1.20 = 0.78)
    assert "↑" in result  # Increase indicator

    # Check graph was updated
    graph_file = temp_knowledge_base / ".claude" / "graphs" / "design_graph.json"
    with open(graph_file) as f:
        graph = json.load(f)

    lesson = next(n for n in graph['nodes'] if n['id'] == 'uncertain_lesson_001')
    assert lesson['confidence'] == pytest.approx(0.78, abs=0.01)
    assert lesson['needs_validation'] is False  # Above 0.70 now
    assert lesson['validation_count'] == 1
    assert 'last_validated_at' in lesson


def test_validate_lesson_by_id(temp_knowledge_base):
    """Should validate lesson by ID."""
    result = validate_lesson("uncertain_lesson_001", base_dir=temp_knowledge_base)

    assert "✅ Validated" in result
    assert "Database Migration Pattern" in result


def test_validate_nonexistent_lesson(temp_knowledge_base):
    """Should return error for nonexistent lesson."""
    result = validate_lesson("Nonexistent Lesson", base_dir=temp_knowledge_base)

    assert "❌" in result
    assert "not found" in result.lower()


def test_validate_lesson_multiple_times(temp_knowledge_base):
    """Should allow multiple validations with diminishing returns."""
    # First validation
    result1 = validate_lesson("Database Migration Pattern", base_dir=temp_knowledge_base)
    assert "78%" in result1

    # Second validation
    result2 = validate_lesson("Database Migration Pattern", base_dir=temp_knowledge_base)
    # 0.78 * 1.20 = 0.936, shown as 93%
    assert "93%" in result2

    # Check validation count
    graph_file = temp_knowledge_base / ".claude" / "graphs" / "design_graph.json"
    with open(graph_file) as f:
        graph = json.load(f)

    lesson = next(n for n in graph['nodes'] if n['id'] == 'uncertain_lesson_001')
    assert lesson['validation_count'] == 2


# ============================================================================
# Contradict Lesson Tests
# ============================================================================


def test_contradict_lesson_with_reason(temp_knowledge_base):
    """Should contradict lesson and decrease confidence."""
    result = contradict_lesson(
        "Database Migration Pattern",
        reason="Doesn't work for NoSQL databases",
        base_dir=temp_knowledge_base
    )

    assert "⚠️  Contradicted" in result
    assert "Database Migration Pattern" in result
    assert "65%" in result  # Old confidence
    assert "26%" in result  # New confidence (0.65 * 0.40 = 0.26)
    assert "↓" in result  # Decrease indicator
    assert "Doesn't work for NoSQL databases" in result

    # Check graph was updated
    graph_file = temp_knowledge_base / ".claude" / "graphs" / "design_graph.json"
    with open(graph_file) as f:
        graph = json.load(f)

    lesson = next(n for n in graph['nodes'] if n['id'] == 'uncertain_lesson_001')
    assert lesson['confidence'] == pytest.approx(0.26, abs=0.01)
    assert lesson['deprecated'] is True  # Below 0.30 - deprecated!
    assert lesson['contradiction_count'] == 1
    assert 'last_contradicted_at' in lesson
    assert len(lesson['contradiction_reasons']) == 1
    assert lesson['contradiction_reasons'][0]['reason'] == "Doesn't work for NoSQL databases"


def test_contradict_lesson_auto_deprecates(temp_knowledge_base):
    """Should auto-deprecate when confidence drops below 0.30."""
    result = contradict_lesson("Database Migration Pattern", base_dir=temp_knowledge_base)

    assert "deprecated" in result.lower()
    assert "💡" in result  # Deprecation notice

    # Verify deprecation in graph
    graph_file = temp_knowledge_base / ".claude" / "graphs" / "design_graph.json"
    with open(graph_file) as f:
        graph = json.load(f)

    lesson = next(n for n in graph['nodes'] if n['id'] == 'uncertain_lesson_001')
    assert lesson['deprecated'] is True
    assert 'deprecated_reason' in lesson


def test_contradict_high_confidence_doesnt_deprecate(temp_knowledge_base):
    """Should not deprecate high-confidence lesson on first contradiction."""
    result = contradict_lesson("Version Bump Checklist", base_dir=temp_knowledge_base)

    # 0.95 * 0.40 = 0.38 (still above 0.30)
    assert "38%" in result
    assert "deprecated" not in result.lower()

    # Verify not deprecated
    graph_file = temp_knowledge_base / ".claude" / "graphs" / "design_graph.json"
    with open(graph_file) as f:
        graph = json.load(f)

    lesson = next(n for n in graph['nodes'] if n['id'] == 'high_confidence_lesson')
    assert lesson['deprecated'] is False


# ============================================================================
# Review Uncertain Tests
# ============================================================================


def test_review_uncertain_shows_uncertain_lessons(temp_knowledge_base):
    """Should show all uncertain lessons."""
    result = review_uncertain(base_dir=temp_knowledge_base)

    assert "⚠️  UNCERTAIN LESSONS NEEDING REVIEW" in result
    assert "Found 1 lesson(s) needing validation" in result
    assert "Database Migration Pattern" in result
    assert "65%" in result
    assert "design" in result  # Triad name

    # Should not show high-confidence lesson
    assert "Version Bump Checklist" not in result

    # Should not show deprecated lesson
    assert "Old Pattern" not in result


def test_review_uncertain_groups_by_confidence_band(temp_knowledge_base):
    """Should group lessons by confidence bands."""
    # Add a low-confidence lesson
    graph_file = temp_knowledge_base / ".claude" / "graphs" / "design_graph.json"
    with open(graph_file) as f:
        graph = json.load(f)

    graph['nodes'].append({
        "id": "very_uncertain",
        "type": "Concept",
        "label": "Very Uncertain Pattern",
        "process_type": "pattern",
        "confidence": 0.35,
        "needs_validation": True,
        "deprecated": False,
        "source": "agent_inference"
    })

    with open(graph_file, 'w') as f:
        json.dump(graph, f, indent=2)

    result = review_uncertain(base_dir=temp_knowledge_base)

    assert "🟡 Medium Confidence (0.50-0.69)" in result
    assert "Database Migration Pattern" in result


def test_review_uncertain_no_uncertain_lessons(temp_knowledge_base):
    """Should show success message when no uncertain lessons."""
    # Remove uncertain lesson
    graph_file = temp_knowledge_base / ".claude" / "graphs" / "design_graph.json"
    with open(graph_file) as f:
        graph = json.load(f)

    graph['nodes'] = [n for n in graph['nodes'] if n['id'] != 'uncertain_lesson_001']

    with open(graph_file, 'w') as f:
        json.dump(graph, f, indent=2)

    result = review_uncertain(base_dir=temp_knowledge_base)

    assert "✅ No uncertain lessons found" in result
    assert "confidence ≥ 70%" in result


def test_review_uncertain_filter_by_triad(temp_knowledge_base):
    """Should filter by triad when specified."""
    # Create another triad with uncertain lesson
    graphs_dir = temp_knowledge_base / ".claude" / "graphs"
    impl_graph = {
        "directed": True,
        "nodes": [{
            "id": "impl_uncertain",
            "type": "Concept",
            "label": "Implementation Pattern",
            "process_type": "pattern",
            "confidence": 0.60,
            "needs_validation": True,
            "deprecated": False
        }],
        "links": [],
        "_meta": {"triad_name": "implementation"}
    }

    impl_file = graphs_dir / "implementation_graph.json"
    impl_file.write_text(json.dumps(impl_graph, indent=2))

    # Review design triad only
    result = review_uncertain(triad="design", base_dir=temp_knowledge_base)

    assert "Database Migration Pattern" in result
    assert "Implementation Pattern" not in result


def test_review_uncertain_shows_statistics(temp_knowledge_base):
    """Should show success/failure/contradiction statistics."""
    result = review_uncertain(base_dir=temp_knowledge_base)

    assert "Statistics:" in result
    assert "success" in result
    assert "failure" in result
    assert "contradiction" in result


def test_review_uncertain_shows_recommendations(temp_knowledge_base):
    """Should show recommended actions."""
    result = review_uncertain(base_dir=temp_knowledge_base)

    assert "Recommended Actions" in result
    assert "/knowledge-validate" in result
    assert "/knowledge-contradict" in result
    assert "natural learning" in result.lower()


# ============================================================================
# Integration Tests
# ============================================================================


def test_validate_then_review(temp_knowledge_base):
    """Should show lesson disappear from review after validation."""
    # Review before
    result_before = review_uncertain(base_dir=temp_knowledge_base)
    assert "Database Migration Pattern" in result_before

    # Validate
    validate_lesson("Database Migration Pattern", base_dir=temp_knowledge_base)

    # Review after
    result_after = review_uncertain(base_dir=temp_knowledge_base)
    assert "No uncertain lessons found" in result_after


def test_contradict_then_review(temp_knowledge_base):
    """Should show deprecated lesson not appear in review."""
    # Contradict (will deprecate due to low confidence)
    contradict_lesson("Database Migration Pattern", base_dir=temp_knowledge_base)

    # Review - should not show deprecated
    result = review_uncertain(base_dir=temp_knowledge_base)
    assert "Database Migration Pattern" not in result
