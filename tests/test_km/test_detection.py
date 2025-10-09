"""Tests for knowledge issue detection."""
import json


def test_detect_sparse_entity():
    """Should detect entity with < 3 meaningful properties."""
    from triads.km.detection import detect_km_issues

    graph_data = {
        "nodes": [
            {
                "id": "jwt_lib",
                "type": "Entity",
                "label": "JWT",
                "description": "JWT library",
                "confidence": 0.95,
                "evidence": "test:1",  # Has evidence to avoid that issue
                "created_by": "agent",
                "created_at": "2025-01-01T00:00:00Z",
                "properties": {"name": "JWT"},  # Only 1 property
            }
        ]
    }

    issues = detect_km_issues(graph_data, "discovery")

    assert len(issues) == 1
    assert issues[0]["type"] == "sparse_entity"
    assert issues[0]["node_id"] == "jwt_lib"
    assert issues[0]["property_count"] == 1
    assert issues[0]["priority"] == "medium"


def test_detect_low_confidence():
    """Should detect confidence below 0.85 threshold."""
    from triads.km.detection import detect_km_issues

    graph_data = {
        "nodes": [
            {
                "id": "uncertain_fact",
                "type": "Finding",
                "label": "Unverified claim",
                "confidence": 0.70,
                "evidence": "test:1",
                "properties": {"a": 1, "b": 2, "c": 3},
            }
        ]
    }

    issues = detect_km_issues(graph_data, "discovery")

    assert len(issues) == 1
    assert issues[0]["type"] == "low_confidence"
    assert issues[0]["confidence"] == 0.70
    assert issues[0]["priority"] == "high"


def test_detect_missing_evidence():
    """Should detect nodes without evidence citations."""
    from triads.km.detection import detect_km_issues

    graph_data = {
        "nodes": [
            {
                "id": "uncited_fact",
                "type": "Entity",
                "label": "Uncited entity",
                "confidence": 0.90,
                "properties": {"a": 1, "b": 2, "c": 3},
                # Missing: evidence field
            }
        ]
    }

    issues = detect_km_issues(graph_data, "discovery")

    assert len(issues) == 1
    assert issues[0]["type"] == "missing_evidence"
    assert issues[0]["priority"] == "high"


def test_uncertainty_nodes_not_flagged():
    """Uncertainty nodes should not trigger validation issues."""
    from triads.km.detection import detect_km_issues

    graph_data = {
        "nodes": [
            {
                "id": "known_unknown",
                "type": "Uncertainty",
                "label": "Unknown fact",
                "confidence": 0.50,  # Low confidence OK for Uncertainty
                # No evidence OK for Uncertainty
            }
        ]
    }

    issues = detect_km_issues(graph_data, "discovery")

    assert len(issues) == 0


def test_multiple_issues_on_same_node():
    """A node can have multiple issues (sparse + missing evidence)."""
    from triads.km.detection import detect_km_issues

    graph_data = {
        "nodes": [
            {
                "id": "problematic",
                "type": "Entity",
                "label": "Problematic entity",
                "confidence": 0.90,
                "properties": {"name": "test"},  # Sparse (1 property)
                # Missing evidence
            }
        ]
    }

    issues = detect_km_issues(graph_data, "discovery")

    # Should detect both sparse and missing evidence
    assert len(issues) == 2
    issue_types = {i["type"] for i in issues}
    assert "sparse_entity" in issue_types
    assert "missing_evidence" in issue_types


def test_count_meaningful_properties():
    """Should count only meaningful properties, not metadata."""
    from triads.km.detection import count_meaningful_properties

    node = {
        "id": "test",
        "type": "Entity",
        "label": "Test",
        "description": "Test description",
        "confidence": 0.95,
        "evidence": "test:1",
        "created_by": "agent",
        "created_at": "2025-01-01",
        "properties": {"meaningful_1": "value1", "meaningful_2": "value2"},
    }

    count = count_meaningful_properties(node)

    # Should only count properties dict contents
    assert count == 2


def test_count_properties_without_explicit_dict():
    """Should count non-metadata fields if no properties dict exists."""
    from triads.km.detection import count_meaningful_properties

    node = {
        "id": "test",
        "type": "Entity",
        "label": "Test",
        "confidence": 0.95,
        "extra_field_1": "value1",
        "extra_field_2": "value2",
        "extra_field_3": "value3",
    }

    count = count_meaningful_properties(node)

    # Should count extra fields (excluding metadata)
    assert count == 3


def test_queue_avoids_duplicates(tmp_path, monkeypatch):
    """Should not add duplicate issues to queue."""
    from triads.km.detection import update_km_queue

    # Mock the queue file location
    queue_file = tmp_path / "km_queue.json"
    monkeypatch.setattr("triads.km.detection.QUEUE_FILE", queue_file)

    issue = {
        "node_id": "test",
        "type": "sparse_entity",
        "label": "Test",
        "priority": "medium",
    }

    # Add twice
    update_km_queue([issue])
    update_km_queue([issue])

    # Should only exist once
    queue = json.loads(queue_file.read_text())
    assert len(queue["issues"]) == 1


def test_queue_preserves_existing_issues(tmp_path, monkeypatch):
    """Should preserve existing issues when adding new ones."""
    from triads.km.detection import update_km_queue

    queue_file = tmp_path / "km_queue.json"
    monkeypatch.setattr("triads.km.detection.QUEUE_FILE", queue_file)

    # Add first issue
    issue1 = {"node_id": "test1", "type": "sparse_entity", "label": "Test1"}
    update_km_queue([issue1])

    # Add second issue
    issue2 = {"node_id": "test2", "type": "low_confidence", "label": "Test2"}
    update_km_queue([issue2])

    # Both should exist
    queue = json.loads(queue_file.read_text())
    assert len(queue["issues"]) == 2
    node_ids = {i["node_id"] for i in queue["issues"]}
    assert "test1" in node_ids
    assert "test2" in node_ids


def test_queue_metadata_updated(tmp_path, monkeypatch):
    """Queue metadata should be updated on each write."""
    from triads.km.detection import update_km_queue

    queue_file = tmp_path / "km_queue.json"
    monkeypatch.setattr("triads.km.detection.QUEUE_FILE", queue_file)

    issue = {"node_id": "test", "type": "sparse_entity", "label": "Test"}
    update_km_queue([issue])

    queue = json.loads(queue_file.read_text())

    # Check metadata exists
    assert "updated_at" in queue
    assert "issue_count" in queue
    assert queue["issue_count"] == 1

    # Check issue has detected_at timestamp
    assert "detected_at" in queue["issues"][0]


def test_comprehensive_entity_not_flagged():
    """Entity with >= 3 properties should not be flagged as sparse."""
    from triads.km.detection import detect_km_issues

    graph_data = {
        "nodes": [
            {
                "id": "comprehensive",
                "type": "Entity",
                "label": "Comprehensive entity",
                "confidence": 0.95,
                "evidence": "test:1",
                "properties": {"prop1": "v1", "prop2": "v2", "prop3": "v3", "prop4": "v4"},
            }
        ]
    }

    issues = detect_km_issues(graph_data, "discovery")

    # Should have no issues (comprehensive, high confidence, has evidence)
    assert len(issues) == 0


def test_high_confidence_node_not_flagged():
    """Node with confidence >= 0.85 should not be flagged."""
    from triads.km.detection import detect_km_issues

    graph_data = {
        "nodes": [
            {
                "id": "confident",
                "type": "Finding",
                "label": "Confident finding",
                "confidence": 0.92,
                "evidence": "test:1",
                "properties": {"a": 1, "b": 2, "c": 3},
            }
        ]
    }

    issues = detect_km_issues(graph_data, "discovery")

    # Should have no low_confidence issue
    low_conf_issues = [i for i in issues if i["type"] == "low_confidence"]
    assert len(low_conf_issues) == 0
