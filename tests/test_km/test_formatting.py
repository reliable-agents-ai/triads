"""Tests for knowledge issue formatting and status files."""

import json

import pytest


def test_format_km_notification_empty():
    """Empty issue list should return None."""
    from triads.km.formatting import format_km_notification

    notification = format_km_notification([])

    assert notification is None


def test_format_km_notification_single_issue():
    """Single issue should format with count and type."""
    from triads.km.formatting import format_km_notification

    issues = [
        {
            "type": "sparse_entity",
            "triad": "discovery",
            "node_id": "test",
            "label": "Test",
            "priority": "medium",
        }
    ]

    notification = format_km_notification(issues)

    assert notification is not None
    assert "1" in notification
    assert "sparse" in notification.lower() or "entity" in notification.lower()


def test_format_km_notification_multiple_issues():
    """Multiple issues should group by type and priority."""
    from triads.km.formatting import format_km_notification

    issues = [
        {"type": "sparse_entity", "priority": "medium", "node_id": "1"},
        {"type": "low_confidence", "priority": "high", "node_id": "2"},
        {"type": "low_confidence", "priority": "high", "node_id": "3"},
        {"type": "missing_evidence", "priority": "high", "node_id": "4"},
    ]

    notification = format_km_notification(issues)

    assert notification is not None
    assert "4" in notification  # Total count
    assert "3" in notification  # High priority count
    # Should mention high priority issues


def test_format_km_notification_with_emoji():
    """Notification should include emoji for visual clarity."""
    from triads.km.formatting import format_km_notification

    issues = [{"type": "sparse_entity", "priority": "medium", "node_id": "1"}]

    notification = format_km_notification(issues)

    # Should have some emoji (clipboard, warning, etc.)
    assert any(char in notification for char in ["📋", "⚠️", "🔍", "❗"])


def test_get_agent_for_issue_sparse_entity():
    """Sparse entities should route to research-agent."""
    from triads.km.formatting import get_agent_for_issue

    issue = {"type": "sparse_entity", "node_id": "test"}

    agent = get_agent_for_issue(issue)

    assert agent == "research-agent"


def test_get_agent_for_issue_low_confidence():
    """Low confidence should route to verification-agent."""
    from triads.km.formatting import get_agent_for_issue

    issue = {"type": "low_confidence", "node_id": "test"}

    agent = get_agent_for_issue(issue)

    assert agent == "verification-agent"


def test_get_agent_for_issue_missing_evidence():
    """Missing evidence should route to verification-agent."""
    from triads.km.formatting import get_agent_for_issue

    issue = {"type": "missing_evidence", "node_id": "test"}

    agent = get_agent_for_issue(issue)

    assert agent == "verification-agent"


def test_get_agent_for_issue_unknown_type():
    """Unknown issue types should raise ValueError."""
    from triads.km.formatting import get_agent_for_issue

    issue = {"type": "unknown_issue_type", "node_id": "test"}

    with pytest.raises(ValueError, match="Unknown issue type"):
        get_agent_for_issue(issue)


def test_write_km_status_file_empty_queue(tmp_path, monkeypatch):
    """Empty queue should not create status file."""
    from triads.km.formatting import write_km_status_file

    # Mock queue location
    queue_file = tmp_path / "km_queue.json"
    status_file = tmp_path / "km_status.md"

    queue_file.write_text(json.dumps({"issues": [], "issue_count": 0}))

    monkeypatch.setattr("triads.km.formatting.QUEUE_FILE", queue_file)
    monkeypatch.setattr("triads.km.formatting.STATUS_FILE", status_file)

    write_km_status_file()

    assert not status_file.exists()


def test_write_km_status_file_with_issues(tmp_path, monkeypatch):
    """Should create markdown status file with issues grouped by triad and priority."""
    from triads.km.formatting import write_km_status_file

    queue_file = tmp_path / "km_queue.json"
    status_file = tmp_path / "km_status.md"

    # Create queue with multiple issues
    queue = {
        "issues": [
            {
                "type": "sparse_entity",
                "triad": "discovery",
                "node_id": "node1",
                "label": "Node 1",
                "priority": "medium",
                "property_count": 1,
            },
            {
                "type": "low_confidence",
                "triad": "discovery",
                "node_id": "node2",
                "label": "Node 2",
                "priority": "high",
                "confidence": 0.70,
            },
            {
                "type": "missing_evidence",
                "triad": "design",
                "node_id": "node3",
                "label": "Node 3",
                "priority": "high",
            },
        ],
        "issue_count": 3,
    }

    queue_file.write_text(json.dumps(queue))

    monkeypatch.setattr("triads.km.formatting.QUEUE_FILE", queue_file)
    monkeypatch.setattr("triads.km.formatting.STATUS_FILE", status_file)

    write_km_status_file()

    assert status_file.exists()

    content = status_file.read_text()

    # Check structure
    assert "# Knowledge Management Status" in content
    assert "## Summary" in content
    assert "total issues" in content.lower() and "3" in content

    # Check triads are grouped
    assert "discovery" in content.lower()
    assert "design" in content.lower()

    # Check issues are listed
    assert "node1" in content or "Node 1" in content
    assert "node2" in content or "Node 2" in content
    assert "node3" in content or "Node 3" in content

    # Check priorities
    assert "high" in content.lower()
    assert "medium" in content.lower()


def test_write_km_status_file_includes_agent_routing(tmp_path, monkeypatch):
    """Status file should indicate which agent handles each issue."""
    from triads.km.formatting import write_km_status_file

    queue_file = tmp_path / "km_queue.json"
    status_file = tmp_path / "km_status.md"

    queue = {
        "issues": [
            {
                "type": "sparse_entity",
                "triad": "discovery",
                "node_id": "node1",
                "label": "Node 1",
                "priority": "medium",
            }
        ],
        "issue_count": 1,
    }

    queue_file.write_text(json.dumps(queue))

    monkeypatch.setattr("triads.km.formatting.QUEUE_FILE", queue_file)
    monkeypatch.setattr("triads.km.formatting.STATUS_FILE", status_file)

    write_km_status_file()

    content = status_file.read_text()

    # Should mention the agent responsible
    assert "research-agent" in content.lower() or "research" in content.lower()


def test_write_km_status_file_markdown_formatting(tmp_path, monkeypatch):
    """Status file should use proper markdown formatting."""
    from triads.km.formatting import write_km_status_file

    queue_file = tmp_path / "km_queue.json"
    status_file = tmp_path / "km_status.md"

    queue = {
        "issues": [
            {
                "type": "sparse_entity",
                "triad": "discovery",
                "node_id": "node1",
                "label": "Node 1",
                "priority": "medium",
                "property_count": 1,
            }
        ],
        "issue_count": 1,
    }

    queue_file.write_text(json.dumps(queue))

    monkeypatch.setattr("triads.km.formatting.QUEUE_FILE", queue_file)
    monkeypatch.setattr("triads.km.formatting.STATUS_FILE", status_file)

    write_km_status_file()

    content = status_file.read_text()

    # Check markdown elements
    assert content.startswith("#")  # Has heading
    assert "##" in content  # Has subheadings
    assert "-" in content or "*" in content  # Has list items


def test_write_km_status_file_groups_by_priority(tmp_path, monkeypatch):
    """Issues should be grouped by priority (high first)."""
    from triads.km.formatting import write_km_status_file

    queue_file = tmp_path / "km_queue.json"
    status_file = tmp_path / "km_status.md"

    queue = {
        "issues": [
            {
                "type": "sparse_entity",
                "triad": "discovery",
                "node_id": "medium1",
                "priority": "medium",
            },
            {
                "type": "low_confidence",
                "triad": "discovery",
                "node_id": "high1",
                "priority": "high",
            },
        ],
        "issue_count": 2,
    }

    queue_file.write_text(json.dumps(queue))

    monkeypatch.setattr("triads.km.formatting.QUEUE_FILE", queue_file)
    monkeypatch.setattr("triads.km.formatting.STATUS_FILE", status_file)

    write_km_status_file()

    content = status_file.read_text()

    # High priority should appear before medium
    high_pos = content.find("high1")
    medium_pos = content.find("medium1")

    assert high_pos < medium_pos
