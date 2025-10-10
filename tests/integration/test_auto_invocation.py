"""Integration tests for automatic system agent invocation.

These tests verify that the KM system automatically queues system agent
invocations for high-priority issues without human intervention.

RED-GREEN-BLUE: Phase 2 RED - These tests will initially FAIL.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

import pytest

# Add src to path
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root / "src"))

from triads.km.detection import detect_km_issues  # noqa: E402
from triads.km.formatting import get_agent_for_issue  # noqa: E402


class TestAutoInvocationLogic:
    """Test automatic system agent invocation logic."""

    def test_high_priority_issues_trigger_invocation(self, tmp_path: Path) -> None:
        """High-priority issues should trigger auto-invocation."""
        # Simulate detection finding high-priority issues
        from typing import Any
        issues: list[dict[str, Any]] = [
            {
                "type": "low_confidence",
                "node_id": "test_node_1",
                "label": "Test Node 1",
                "confidence": 0.72,
                "priority": "high",
                "triad": "test",
            },
            {
                "type": "missing_evidence",
                "node_id": "test_node_2",
                "label": "Test Node 2",
                "priority": "high",
                "triad": "test",
            },
        ]

        # This function should exist in on_stop.py after Phase 2 GREEN
        from triads.km.auto_invocation import queue_auto_invocations

        invocations = queue_auto_invocations(issues, str(tmp_path))

        # Should queue invocations for both high-priority issues
        assert len(invocations) == 2, "Should queue 2 invocations for 2 high-priority issues"

        # Check first invocation
        inv1 = invocations[0]
        assert inv1["agent"] == "verification-agent", "low_confidence should route to verification-agent"  # noqa: E501
        assert "test_node_1" in inv1["task"], "Task should mention node_id"
        assert "confidence: 0.72" in inv1["task"] or "0.72" in inv1["task"], "Task should include confidence"  # noqa: E501
        assert "queued_at" in inv1, "Should have timestamp"

        # Check second invocation
        inv2 = invocations[1]
        assert inv2["agent"] == "verification-agent", "missing_evidence should route to verification-agent"  # noqa: E501
        assert "test_node_2" in inv2["task"], "Task should mention node_id"

    def test_medium_priority_issues_not_auto_invoked(self, tmp_path: Path) -> None:
        """Medium-priority issues should NOT trigger auto-invocation."""
        # Simulate detection finding only medium-priority issues
        issues = [
            {
                "type": "sparse_entity",
                "node_id": "sparse_node",
                "label": "Sparse Node",
                "property_count": 1,
                "priority": "medium",
                "triad": "test",
            }
        ]

        from triads.km.auto_invocation import queue_auto_invocations

        invocations = queue_auto_invocations(issues, str(tmp_path))

        # Should NOT queue invocations for medium-priority issues
        assert len(invocations) == 0, "Should not auto-invoke for medium-priority issues"

    def test_mixed_priority_issues_only_high_invoked(self, tmp_path: Path) -> None:
        """Mixed priorities: only high-priority should trigger invocation."""
        issues = [
            {
                "type": "low_confidence",
                "node_id": "high_pri_node",
                "label": "High Priority",
                "confidence": 0.65,
                "priority": "high",
                "triad": "test",
            },
            {
                "type": "sparse_entity",
                "node_id": "med_pri_node",
                "label": "Medium Priority",
                "property_count": 2,
                "priority": "medium",
                "triad": "test",
            },
        ]

        from triads.km.auto_invocation import queue_auto_invocations

        invocations = queue_auto_invocations(issues, str(tmp_path))

        # Should only queue 1 invocation (high-priority)
        assert len(invocations) == 1, "Should only auto-invoke high-priority issues"
        assert invocations[0]["agent"] == "verification-agent"
        assert "high_pri_node" in invocations[0]["task"]

    def test_invocation_file_format(self, tmp_path: Path) -> None:
        """Invocation queue file should have proper JSON format."""
        issues = [
            {
                "type": "low_confidence",
                "node_id": "test_node",
                "label": "Test Node",
                "confidence": 0.70,
                "priority": "high",
                "triad": "discovery",
            }
        ]

        from triads.km.auto_invocation import queue_auto_invocations, save_invocation_queue

        invocations = queue_auto_invocations(issues, str(tmp_path))
        invocations_file = tmp_path / "km_pending_invocations.json"
        save_invocation_queue(invocations, str(invocations_file))

        # File should exist
        assert invocations_file.exists(), "Invocation queue file should be created"

        # File should be valid JSON
        with open(invocations_file) as f:
            data = json.load(f)

        # Check structure
        assert "invocations" in data, "File should have 'invocations' key"
        assert isinstance(data["invocations"], list), "'invocations' should be a list"
        assert len(data["invocations"]) == 1, "Should have 1 invocation"

        # Check invocation structure
        inv = data["invocations"][0]
        assert "agent" in inv, "Invocation should have 'agent' field"
        assert "task" in inv, "Invocation should have 'task' field"
        assert "issue" in inv, "Invocation should have 'issue' field (full issue data)"
        assert "queued_at" in inv, "Invocation should have 'queued_at' timestamp"

        # Validate timestamp format (ISO 8601)
        try:
            datetime.fromisoformat(inv["queued_at"])
        except ValueError:
            pytest.fail("queued_at should be valid ISO 8601 timestamp")

    def test_agent_routing_correctness(self, tmp_path: Path) -> None:
        """Verify correct agent routing for each issue type."""
        from triads.km.auto_invocation import queue_auto_invocations

        # Test low_confidence → verification-agent
        issues_low_conf = [
            {"type": "low_confidence", "node_id": "n1", "priority": "high", "triad": "test"}
        ]
        invs = queue_auto_invocations(issues_low_conf, str(tmp_path))
        assert invs[0]["agent"] == "verification-agent"

        # Test missing_evidence → verification-agent
        issues_no_evidence = [
            {"type": "missing_evidence", "node_id": "n2", "priority": "high", "triad": "test"}
        ]
        invs = queue_auto_invocations(issues_no_evidence, str(tmp_path))
        assert invs[0]["agent"] == "verification-agent"

    def test_task_description_includes_context(self, tmp_path: Path) -> None:
        """Task description should include enough context for agent."""
        from triads.km.auto_invocation import queue_auto_invocations

        issues = [
            {
                "type": "low_confidence",
                "node_id": "auth_decision",
                "label": "Authentication Decision",
                "confidence": 0.68,
                "priority": "high",
                "triad": "discovery",
                "node_type": "Decision",
            }
        ]

        invocations = queue_auto_invocations(issues, str(tmp_path))
        task = invocations[0]["task"]

        # Task should include key context
        assert "auth_decision" in task, "Should mention node_id"
        assert "Authentication Decision" in task or "auth_decision" in task, "Should mention label or id"  # noqa: E501
        assert "confidence" in task.lower() or "0.68" in task, "Should mention confidence issue"
        assert "discovery" in task, "Should mention triad"

    def test_no_duplicate_invocations(self, tmp_path: Path) -> None:
        """Same issue should not be queued multiple times."""
        from triads.km.auto_invocation import queue_auto_invocations, save_invocation_queue

        invocations_file = tmp_path / "km_pending_invocations.json"

        # First batch of issues
        issues1 = [
            {"type": "low_confidence", "node_id": "dup_node", "priority": "high", "triad": "test"}
        ]
        invs1 = queue_auto_invocations(issues1, str(tmp_path))
        save_invocation_queue(invs1, str(invocations_file))

        # Second batch with same issue (simulates multiple detections)
        issues2 = [
            {"type": "low_confidence", "node_id": "dup_node", "priority": "high", "triad": "test"}
        ]
        invs2 = queue_auto_invocations(issues2, str(tmp_path))

        # Load existing and merge
        with open(invocations_file) as f:
            existing = json.load(f)["invocations"]

        # Should detect duplicate
        from triads.km.auto_invocation import merge_invocations

        merged = merge_invocations(existing, invs2)

        # Should still have only 1 invocation (no duplicate)
        assert len(merged) == 1, "Should not create duplicate invocations"

    def test_empty_issues_no_invocations(self, tmp_path: Path) -> None:
        """No issues should result in no invocations."""
        from triads.km.auto_invocation import queue_auto_invocations

        invocations = queue_auto_invocations([], str(tmp_path))

        assert len(invocations) == 0, "No issues should produce no invocations"

    def test_invocation_includes_full_issue_data(self, tmp_path: Path) -> None:
        """Invocation should include full issue data for debugging."""
        from triads.km.auto_invocation import queue_auto_invocations

        issues = [
            {
                "type": "missing_evidence",
                "node_id": "test_node",
                "label": "Test Label",
                "priority": "high",
                "triad": "discovery",
                "detected_at": "2024-10-10T10:00:00Z",
            }
        ]

        invocations = queue_auto_invocations(issues, str(tmp_path))
        inv = invocations[0]

        # Full issue should be embedded
        assert "issue" in inv, "Should include full issue data"
        assert inv["issue"]["node_id"] == "test_node"
        assert inv["issue"]["type"] == "missing_evidence"
        assert inv["issue"]["priority"] == "high"


class TestAutoInvocationIntegration:
    """Test integration of auto-invocation with existing KM system."""

    def test_integration_with_detection(self, tmp_path: Path) -> None:
        """Auto-invocation should work with real detection output."""
        # Create a graph with quality issues
        graph_data = {
            "nodes": [
                {
                    "id": "bad_node",
                    "type": "Entity",
                    "label": "Bad Entity",
                    "confidence": 0.65,  # Low confidence
                    "properties": {"name": "Bad"},  # Only 1 property
                },
            ],
            "links": [],
        }

        # Detect issues (uses real detection.py)
        issues = detect_km_issues(graph_data, "test")

        # Should detect low_confidence (high priority)
        high_priority = [i for i in issues if i.get("priority") == "high"]
        assert len(high_priority) >= 1, "Should detect at least 1 high-priority issue"

        # Auto-invoke should work with these real issues
        from triads.km.auto_invocation import queue_auto_invocations

        invocations = queue_auto_invocations(issues, str(tmp_path))

        # Should queue invocations for high-priority issues
        assert len(invocations) >= 1, "Should auto-invoke for detected high-priority issues"

    def test_integration_with_formatting(self, tmp_path: Path) -> None:
        """Auto-invocation should use formatting.py for agent routing."""
        issues = [
            {"type": "low_confidence", "node_id": "n1", "priority": "high", "triad": "test"},
            {"type": "missing_evidence", "node_id": "n2", "priority": "high", "triad": "test"},
        ]

        from triads.km.auto_invocation import queue_auto_invocations

        invocations = queue_auto_invocations(issues, str(tmp_path))

        # Should use get_agent_for_issue from formatting.py
        for inv in invocations:
            # Verify agent name matches what formatting.py would return
            issue_type = [i for i in issues if i["node_id"] in inv["task"]][0]["type"]
            expected_agent = get_agent_for_issue({"type": issue_type})
            assert inv["agent"] == expected_agent, f"Should route {issue_type} to {expected_agent}"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
