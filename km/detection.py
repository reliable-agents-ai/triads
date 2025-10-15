"""Knowledge issue detection for graph nodes."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

# Configuration
METADATA_FIELDS = {
    "id",
    "type",
    "label",
    "description",
    "confidence",
    "evidence",
    "created_by",
    "created_at",
    "updated_by",
    "updated_at",
}

CONFIDENCE_THRESHOLD = 0.85
SPARSE_PROPERTY_THRESHOLD = 3
QUEUE_FILE = Path(".claude/km_queue.json")


def count_meaningful_properties(node: dict[str, Any]) -> int:
    """Count meaningful properties (excluding metadata).

    Args:
        node: Graph node dictionary

    Returns:
        Number of meaningful properties
    """
    # If node has explicit properties dict, count those
    if "properties" in node and isinstance(node["properties"], dict):
        return len(node["properties"])

    # Otherwise count non-metadata fields
    return len([k for k in node.keys() if k not in METADATA_FIELDS])


def detect_km_issues(graph_data: dict[str, Any], triad_name: str) -> list[dict[str, Any]]:
    """Detect knowledge management issues in graph.

    Args:
        graph_data: Graph dictionary with 'nodes' list
        triad_name: Name of triad this graph belongs to

    Returns:
        List of issue dictionaries
    """
    issues = []

    for node in graph_data.get("nodes", []):
        node_id = node.get("id")
        node_type = node.get("type")

        # Skip Uncertainty nodes (they're allowed to be incomplete)
        if node_type == "Uncertainty":
            continue

        # Issue 1: Sparse entities
        if node_type in ["Entity", "Concept"]:
            property_count = count_meaningful_properties(node)
            if property_count < SPARSE_PROPERTY_THRESHOLD:
                issues.append(
                    {
                        "type": "sparse_entity",
                        "triad": triad_name,
                        "node_id": node_id,
                        "label": node.get("label", node_id),
                        "property_count": property_count,
                        "priority": "medium",
                    }
                )

        # Issue 2: Low confidence
        confidence = node.get("confidence", 1.0)
        if confidence < CONFIDENCE_THRESHOLD:
            issues.append(
                {
                    "type": "low_confidence",
                    "triad": triad_name,
                    "node_id": node_id,
                    "label": node.get("label", node_id),
                    "confidence": confidence,
                    "priority": "high",
                }
            )

        # Issue 3: Missing evidence
        if not node.get("evidence"):
            issues.append(
                {
                    "type": "missing_evidence",
                    "triad": triad_name,
                    "node_id": node_id,
                    "label": node.get("label", node_id),
                    "priority": "high",
                }
            )

        # Issue 4: Missing transparency (Decision nodes)
        # Principle #4: Complete Transparency - Decisions must show alternatives and rationale
        if node_type == "Decision":
            if not node.get("alternatives"):
                issues.append(
                    {
                        "type": "missing_alternatives",
                        "triad": triad_name,
                        "node_id": node_id,
                        "label": node.get("label", node_id),
                        "priority": "medium",
                        "principle": "transparency",
                    }
                )
            if not node.get("rationale"):
                issues.append(
                    {
                        "type": "missing_rationale",
                        "triad": triad_name,
                        "node_id": node_id,
                        "label": node.get("label", node_id),
                        "priority": "medium",
                        "principle": "transparency",
                    }
                )

        # Issue 5: Unvalidated assumptions
        # Principle #5: Assumption Auditing - Assumptions must be validated
        assumptions = node.get("assumptions", [])
        if assumptions:
            # Check if assumptions is a list of dicts with validation info
            if isinstance(assumptions, list) and len(assumptions) > 0:
                for idx, assumption in enumerate(assumptions):
                    if isinstance(assumption, dict):
                        # Check if assumption has been validated
                        if not assumption.get("validated", False):
                            issues.append(
                                {
                                    "type": "unvalidated_assumption",
                                    "triad": triad_name,
                                    "node_id": node_id,
                                    "label": node.get("label", node_id),
                                    "assumption_index": idx,
                                    "assumption_description": assumption.get(
                                        "description", "No description"
                                    ),
                                    "priority": "medium",
                                    "principle": "assumption_auditing",
                                }
                            )

    return issues


def update_km_queue(issues: list[dict[str, Any]]) -> None:
    """Add issues to queue, avoiding duplicates.

    Args:
        issues: List of issue dictionaries to add
    """
    QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Load existing queue
    if QUEUE_FILE.exists():
        with open(QUEUE_FILE, "r") as f:
            queue = json.load(f)
    else:
        queue = {"issues": [], "updated_at": None}

    # Add new issues (avoid duplicates by node_id)
    existing_ids = {i["node_id"] for i in queue["issues"]}
    for issue in issues:
        if issue["node_id"] not in existing_ids:
            issue["detected_at"] = datetime.now().isoformat()
            queue["issues"].append(issue)

    # Update metadata
    queue["updated_at"] = datetime.now().isoformat()
    queue["issue_count"] = len(queue["issues"])

    # Save
    with open(QUEUE_FILE, "w") as f:
        json.dump(queue, f, indent=2)
