#!/usr/bin/env python3
"""Migrate existing process knowledge nodes to confidence-based system.

This script adds new confidence fields to existing process knowledge nodes
while preserving all existing data. It's designed to be:
- Non-breaking: Doesn't remove any fields
- Idempotent: Safe to run multiple times
- Conservative: Infers confidence from existing status/priority

Usage:
    python scripts/migrate_confidence_fields.py [--dry-run]

Options:
    --dry-run    Show what would be changed without modifying files
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Add src to path for imports
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / "src"))

from triads.km.confidence import (
    calculate_initial_confidence,
    assign_status,
    validate_confidence_value,
)


def infer_confidence_from_existing(node: dict) -> float:
    """Infer confidence for existing node based on available data.

    Strategy:
    - If user promoted to active, assume high confidence (0.95)
    - If draft with CRITICAL priority, calculate from source
    - If draft with HIGH priority, calculate from source
    - Otherwise, use source-based calculation

    Args:
        node: Existing process knowledge node

    Returns:
        float: Inferred confidence score
    """
    # If already active (user promoted), trust that decision
    if node.get("status") == "active":
        return 0.95

    # Calculate from source and priority
    source = node.get("detection_method", "unknown")
    priority = node.get("priority", "MEDIUM")

    # Map legacy detection_method to new source types
    source_mapping = {
        "explicit": "process_knowledge_block",
        "user_correction": "user_correction",
        "repeated_mistake": "repeated_mistake",
        "pattern": "agent_inference",
        "unknown": "agent_inference",
    }

    mapped_source = source_mapping.get(source, "agent_inference")

    return calculate_initial_confidence(
        source=mapped_source,
        priority=priority,
        repetition_count=1
    )


def infer_status_from_existing(node: dict) -> str:
    """Infer status for existing node.

    Strategy:
    - active → keep active
    - archived → rename to deprecated
    - draft → calculate from confidence
    - missing + high confidence → active (likely user-created, intentional)
    - missing + low confidence → needs_validation (conservative)

    Args:
        node: Existing process knowledge node

    Returns:
        str: Inferred status
    """
    existing_status = node.get("status")

    if existing_status == "active":
        return "active"  # Keep active
    elif existing_status == "archived":
        return "deprecated"  # Rename to deprecated
    elif existing_status == "draft":
        # Calculate confidence, assign new status
        confidence = node.get("confidence", 0.70)
        priority = node.get("priority", "MEDIUM")
        return assign_status(confidence, priority)
    else:
        # No status field - infer from confidence and priority
        # If node exists without status, it was likely user-created or from old system
        # If it has high confidence (1.0) and CRITICAL priority, treat as active
        confidence = node.get("confidence", 0.70)
        priority = node.get("priority", "MEDIUM")

        # User-created nodes often have confidence=1.0 and no status
        # These should be active, not needs_validation
        if confidence >= 0.80:
            return "active"
        else:
            return assign_status(confidence, priority)


def migrate_node(node: dict) -> tuple[dict, list[str]]:
    """Add new confidence fields to a process knowledge node.

    Args:
        node: Process knowledge node dictionary

    Returns:
        tuple: (modified_node, list of changes made)
    """
    changes = []

    # Only process Concept nodes with process_type (process knowledge)
    if node.get("type") != "Concept" or "process_type" not in node:
        return node, changes

    # Add confidence if missing
    if "confidence" not in node:
        node["confidence"] = infer_confidence_from_existing(node)
        changes.append(f"Added confidence: {node['confidence']:.2f}")
    else:
        # Validate existing confidence
        old_conf = node["confidence"]
        node["confidence"] = validate_confidence_value(old_conf)
        if old_conf != node["confidence"]:
            changes.append(f"Validated confidence: {old_conf} → {node['confidence']}")

    # Update status if needed
    old_status = node.get("status")
    new_status = infer_status_from_existing(node)
    if old_status != new_status:
        node["status"] = new_status
        changes.append(f"Updated status: {old_status} → {new_status}")
    elif "status" not in node:
        node["status"] = new_status
        changes.append(f"Added status: {new_status}")

    # Add source (map from detection_method)
    if "source" not in node:
        detection_method = node.get("detection_method", "unknown")
        source_mapping = {
            "explicit": "process_knowledge_block",
            "user_correction": "user_correction",
            "repeated_mistake": "repeated_mistake",
            "pattern": "agent_inference",
            "unknown": "agent_inference",
        }
        node["source"] = source_mapping.get(detection_method, "agent_inference")
        changes.append(f"Added source: {node['source']}")

    # Initialize tracking fields
    tracking_fields = {
        "success_count": 0,
        "failure_count": 0,
        "confirmation_count": 0,
        "contradiction_count": 0,
        "injection_count": 0,
    }

    for field, default in tracking_fields.items():
        if field not in node:
            node[field] = default
            changes.append(f"Added {field}: {default}")

    # Initialize null fields
    null_fields = [
        "last_injected_at",
        "last_outcome",
        "deprecated_at",
        "deprecated_reason",
    ]

    for field in null_fields:
        if field not in node:
            node[field] = None
            changes.append(f"Added {field}: null")

    # Initialize array fields
    if "outcome_history" not in node:
        node["outcome_history"] = []
        changes.append("Added outcome_history: []")

    # Initialize boolean fields
    if "deprecation_automatic" not in node:
        node["deprecation_automatic"] = False
        changes.append("Added deprecation_automatic: false")

    # Add updated_at if missing
    if "updated_at" not in node:
        node["updated_at"] = node.get("created_at", datetime.now().isoformat())
        changes.append("Added updated_at")

    return node, changes


def migrate_graph_file(graph_file: Path, dry_run: bool = False) -> dict:
    """Migrate a single graph file.

    Args:
        graph_file: Path to graph JSON file
        dry_run: If True, don't modify files

    Returns:
        dict: Migration statistics
    """
    stats = {
        "file": graph_file.name,
        "nodes_processed": 0,
        "nodes_modified": 0,
        "changes": [],
    }

    # Load graph
    with open(graph_file, 'r') as f:
        graph = json.load(f)

    modified = False

    # Process each node
    for node in graph.get("nodes", []):
        stats["nodes_processed"] += 1

        modified_node, changes = migrate_node(node)

        if changes:
            stats["nodes_modified"] += 1
            stats["changes"].append({
                "node_id": node.get("id"),
                "label": node.get("label", ""),
                "changes": changes,
            })
            modified = True

    # Save if modified and not dry run
    if modified and not dry_run:
        with open(graph_file, 'w') as f:
            json.dump(graph, f, indent=2)

    return stats


def migrate_all_graphs(dry_run: bool = False) -> None:
    """Migrate all graph files in .claude/graphs/.

    Args:
        dry_run: If True, show changes without modifying files
    """
    graphs_dir = Path(".claude/graphs")

    if not graphs_dir.exists():
        print("❌ .claude/graphs/ directory not found")
        return

    graph_files = list(graphs_dir.glob("*_graph.json"))

    if not graph_files:
        print("ℹ️  No graph files found")
        return

    print(f"🔍 Found {len(graph_files)} graph files\n")

    if dry_run:
        print("🔬 DRY RUN MODE - No files will be modified\n")

    total_stats = {
        "files_processed": 0,
        "files_modified": 0,
        "total_nodes_processed": 0,
        "total_nodes_modified": 0,
    }

    for graph_file in graph_files:
        stats = migrate_graph_file(graph_file, dry_run=dry_run)

        total_stats["files_processed"] += 1
        total_stats["total_nodes_processed"] += stats["nodes_processed"]
        total_stats["total_nodes_modified"] += stats["nodes_modified"]

        if stats["nodes_modified"] > 0:
            total_stats["files_modified"] += 1

            print(f"📝 {stats['file']}")
            print(f"   Processed: {stats['nodes_processed']} nodes")
            print(f"   Modified: {stats['nodes_modified']} nodes")

            for change_entry in stats["changes"]:
                print(f"\n   Node: {change_entry['node_id']}")
                print(f"   Label: {change_entry['label']}")
                for change in change_entry['changes']:
                    print(f"     - {change}")

            print()

    # Summary
    print("=" * 60)
    print("📊 MIGRATION SUMMARY")
    print("=" * 60)
    print(f"Files processed: {total_stats['files_processed']}")
    print(f"Files modified: {total_stats['files_modified']}")
    print(f"Total nodes processed: {total_stats['total_nodes_processed']}")
    print(f"Total nodes modified: {total_stats['total_nodes_modified']}")

    if dry_run:
        print("\n🔬 DRY RUN COMPLETE - No files were modified")
        print("Run without --dry-run to apply changes")
    else:
        print("\n✅ MIGRATION COMPLETE")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Migrate process knowledge nodes to confidence-based system"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show changes without modifying files"
    )

    args = parser.parse_args()

    migrate_all_graphs(dry_run=args.dry_run)
