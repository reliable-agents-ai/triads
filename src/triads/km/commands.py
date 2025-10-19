"""CLI command implementations for knowledge management.

This module provides command-line functions for:
- Validating uncertain lessons (increase confidence)
- Contradicting incorrect lessons (decrease confidence)
- Reviewing uncertain lessons (show lessons needing validation)

These commands integrate with the confidence-based learning system to allow
manual intervention when needed.

Usage:
    from triads.km.commands import validate_lesson, contradict_lesson, review_uncertain

    # Validate a lesson
    validate_lesson("Version Bump Checklist")

    # Contradict a lesson
    contradict_lesson("Database Pattern", "Doesn't work for NoSQL")

    # Review uncertain lessons
    review_uncertain()
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from triads.km.confidence import update_confidence, check_deprecation
from triads.km.graph_access import GraphLoader
from triads.hooks.safe_io import safe_load_json_file, safe_save_json_file


# ============================================================================
# Helper Functions
# ============================================================================


def _find_node_by_label_or_id(
    loader: GraphLoader,
    identifier: str,
    triad: str | None = None
) -> tuple[dict, str, dict] | None:
    """Find node by ID or label (fuzzy search).

    Args:
        loader: GraphLoader instance
        identifier: Node ID or label to search for
        triad: Optional triad to search in

    Returns:
        Tuple of (node, triad_name, graph_data) or None if not found
    """
    # Try exact ID match first
    try:
        result = loader.get_node(identifier, triad=triad)
        if result:
            node, found_triad = result
            graph_data = loader.load_graph(found_triad)
            return (node, found_triad, graph_data)
    except Exception:
        pass

    # Fall back to label search
    all_graphs = loader.load_all_graphs()

    if triad:
        # Search only specified triad
        if triad not in all_graphs:
            return None
        all_graphs = {triad: all_graphs[triad]}

    identifier_lower = identifier.lower()
    matches = []

    for triad_name, graph_data in all_graphs.items():
        for node in graph_data.get('nodes', []):
            # Only search Concept nodes with process_type (knowledge nodes)
            if node.get('type') != 'Concept' or 'process_type' not in node:
                continue

            label = node.get('label', '').lower()
            node_id = node.get('id', '').lower()

            # Exact match on label or ID
            if label == identifier_lower or node_id == identifier_lower:
                return (node, triad_name, graph_data)

            # Fuzzy match on label
            if identifier_lower in label:
                matches.append((node, triad_name, graph_data))

    # Return best fuzzy match if found
    if matches:
        return matches[0]

    return None


# ============================================================================
# Validate Lesson
# ============================================================================


def validate_lesson(
    lesson_identifier: str,
    triad: str | None = None,
    base_dir: Path | None = None
) -> str:
    """Manually validate an uncertain lesson to increase confidence.

    Args:
        lesson_identifier: Lesson ID or label (fuzzy search)
        triad: Optional triad name to search in
        base_dir: Base directory (defaults to cwd)

    Returns:
        Formatted result message

    Example:
        >>> validate_lesson("Version Bump Checklist")
        ✅ Validated: Version Bump Checklist
           Confidence: 0.65 → 0.78 (↑ 13%)
           ...
    """
    base_dir = base_dir or Path.cwd()
    loader = GraphLoader(graphs_dir=base_dir / ".claude" / "graphs")

    # Find the lesson by ID or label
    result = _find_node_by_label_or_id(loader, lesson_identifier, triad=triad)
    if result is None:
        return f"❌ Lesson not found: {lesson_identifier}"

    node, found_triad, graph_data = result

    # Get current confidence
    current_confidence = node.get('confidence', 0.75)
    node_label = node.get('label', lesson_identifier)

    # Update confidence (validation outcome)
    new_confidence = update_confidence(current_confidence, 'confirmation')

    # Find the node in graph_data and update it
    graph_node = next((n for n in graph_data['nodes'] if n.get('id') == node.get('id')), None)
    if not graph_node:
        return f"❌ Node not found in graph"

    # Update node in graph
    graph_node['confidence'] = new_confidence
    graph_node['needs_validation'] = new_confidence < 0.70

    # Update validation statistics
    if 'validation_count' not in graph_node:
        graph_node['validation_count'] = 0
    graph_node['validation_count'] += 1
    graph_node['last_validated_at'] = datetime.now(timezone.utc).isoformat()

    # Save graph
    graph_file = base_dir / ".claude" / "graphs" / f"{found_triad}_graph.json"
    safe_save_json_file(graph_file, graph_data)

    # Format output
    confidence_change = new_confidence - current_confidence
    confidence_pct_old = int(current_confidence * 100)
    confidence_pct_new = int(new_confidence * 100)
    change_pct = int(confidence_change * 100)

    status_old = "needs_validation" if current_confidence < 0.70 else "active"
    status_new = "needs_validation" if new_confidence < 0.70 else "active"

    output = []
    output.append("✅ Validated: " + node_label)
    output.append(f"   Confidence: {confidence_pct_old}% → {confidence_pct_new}% (↑ {change_pct}%)")
    if status_old != status_new:
        output.append(f"   Status: {status_old} → {status_new}")
    output.append(f"   Graph: {found_triad}_graph.json updated")

    return "\n".join(output)


# ============================================================================
# Contradict Lesson
# ============================================================================


def contradict_lesson(
    lesson_identifier: str,
    reason: str = "",
    triad: str | None = None,
    base_dir: Path | None = None
) -> str:
    """Mark a lesson as incorrect to decrease confidence.

    Args:
        lesson_identifier: Lesson ID or label (fuzzy search)
        reason: Why the lesson is incorrect
        triad: Optional triad name to search in
        base_dir: Base directory (defaults to cwd)

    Returns:
        Formatted result message

    Example:
        >>> contradict_lesson("DB Pattern", "Doesn't work for NoSQL")
        ⚠️  Contradicted: DB Pattern
           Confidence: 0.75 → 0.30 (↓ 45%)
           Status: active → deprecated
           ...
    """
    base_dir = base_dir or Path.cwd()
    loader = GraphLoader(graphs_dir=base_dir / ".claude" / "graphs")

    # Find the lesson by ID or label
    result = _find_node_by_label_or_id(loader, lesson_identifier, triad=triad)
    if result is None:
        return f"❌ Lesson not found: {lesson_identifier}"

    node, found_triad, graph_data = result

    # Get current confidence
    current_confidence = node.get('confidence', 0.75)
    node_label = node.get('label', lesson_identifier)

    # Update confidence (contradiction outcome - strong negative signal)
    new_confidence = update_confidence(current_confidence, 'contradiction')

    # Find the node in graph_data and update it
    graph_node = next((n for n in graph_data['nodes'] if n.get('id') == node.get('id')), None)
    if not graph_node:
        return f"❌ Node not found in graph"

    # Update node in graph
    graph_node['confidence'] = new_confidence
    graph_node['needs_validation'] = new_confidence < 0.70

    # Update contradiction statistics
    if 'contradiction_count' not in graph_node:
        graph_node['contradiction_count'] = 0
    graph_node['contradiction_count'] += 1
    graph_node['last_contradicted_at'] = datetime.now(timezone.utc).isoformat()

    # Record reason
    if 'contradiction_reasons' not in graph_node:
        graph_node['contradiction_reasons'] = []
    if reason:
        graph_node['contradiction_reasons'].append({
            'reason': reason,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })

    # Check deprecation
    if check_deprecation(graph_node):
        graph_node['deprecated'] = True
        graph_node['deprecated_reason'] = reason or f"Confidence dropped below threshold ({new_confidence:.2f})"

    # Save graph
    graph_file = base_dir / ".claude" / "graphs" / f"{found_triad}_graph.json"
    safe_save_json_file(graph_file, graph_data)

    # Format output
    confidence_change = new_confidence - current_confidence
    confidence_pct_old = int(current_confidence * 100)
    confidence_pct_new = int(new_confidence * 100)
    change_pct = abs(int(confidence_change * 100))

    was_deprecated = current_confidence >= 0.30 and new_confidence < 0.30

    output = []
    output.append("⚠️  Contradicted: " + node_label)
    output.append(f"   Confidence: {confidence_pct_old}% → {confidence_pct_new}% (↓ {change_pct}%)")

    if was_deprecated:
        output.append("   Status: active → deprecated")
        output.append("")
        output.append("💡 This lesson is now deprecated and will not be shown again.")

    if reason:
        output.append(f"   Reason: {reason}")

    output.append(f"   Graph: {found_triad}_graph.json updated")

    return "\n".join(output)


# ============================================================================
# Review Uncertain Lessons
# ============================================================================


def review_uncertain(
    triad: str | None = None,
    base_dir: Path | None = None
) -> str:
    """Review all lessons that need validation (confidence < 0.70).

    Args:
        triad: Optional triad name to filter by
        base_dir: Base directory (defaults to cwd)

    Returns:
        Formatted review of uncertain lessons

    Example:
        >>> print(review_uncertain())
        ═══════════════════════════════════════════
        # ⚠️  UNCERTAIN LESSONS NEEDING REVIEW
        ...
    """
    base_dir = base_dir or Path.cwd()
    loader = GraphLoader(graphs_dir=base_dir / ".claude" / "graphs")

    # Load all graphs
    all_graphs = loader.load_all_graphs()

    if triad:
        # Filter to specific triad
        if triad not in all_graphs:
            return f"❌ Triad not found: {triad}"
        all_graphs = {triad: all_graphs[triad]}

    # Collect uncertain lessons
    uncertain_lessons = []

    for triad_name, graph_data in all_graphs.items():
        nodes = graph_data.get('nodes', [])

        for node in nodes:
            # Only process knowledge nodes (Concept type with process_type)
            if node.get('type') != 'Concept' or 'process_type' not in node:
                continue

            # Skip deprecated
            if node.get('deprecated', False):
                continue

            # Check if needs validation
            confidence = node.get('confidence', 0.75)
            if confidence < 0.70:
                uncertain_lessons.append({
                    'node': node,
                    'triad': triad_name,
                    'confidence': confidence
                })

    if not uncertain_lessons:
        return "✅ No uncertain lessons found. All lessons have confidence ≥ 70%."

    # Sort by confidence (lowest first)
    uncertain_lessons.sort(key=lambda x: x['confidence'])

    # Group by confidence band
    low = [l for l in uncertain_lessons if l['confidence'] < 0.50]
    medium = [l for l in uncertain_lessons if 0.50 <= l['confidence'] < 0.70]

    # Format output
    output = []
    output.append("=" * 67)
    output.append("# ⚠️  UNCERTAIN LESSONS NEEDING REVIEW")
    output.append("=" * 67)
    output.append("")
    output.append(f"Found {len(uncertain_lessons)} lesson(s) needing validation:")
    output.append("")

    # Low confidence lessons
    if low:
        output.append("## 🔴 Low Confidence (< 0.50)")
        output.append("")
        for i, lesson in enumerate(low, 1):
            node = lesson['node']
            conf_pct = int(lesson['confidence'] * 100)

            output.append(f"{i}. {node.get('label', 'Unknown')}")
            output.append(f"   ID: {node.get('id', 'unknown')}")
            output.append(f"   Confidence: {conf_pct}% | Triad: {lesson['triad']}")

            source = node.get('source', 'unknown')
            created = node.get('created_at', 'unknown')[:10] if 'created_at' in node else 'unknown'
            output.append(f"   Source: {source} | Created: {created}")

            success = node.get('success_count', 0)
            failure = node.get('failure_count', 0)
            contradiction = node.get('contradiction_count', 0)
            output.append(f"   Statistics: {success} success, {failure} failure, {contradiction} contradiction")

            output.append("")
            output.append("   💡 Action: Review and validate or contradict this lesson")
            output.append("")

    # Medium confidence lessons
    if medium:
        output.append("## 🟡 Medium Confidence (0.50-0.69)")
        output.append("")
        for i, lesson in enumerate(medium, 1):
            node = lesson['node']
            conf_pct = int(lesson['confidence'] * 100)

            output.append(f"{i}. {node.get('label', 'Unknown')}")
            output.append(f"   ID: {node.get('id', 'unknown')}")
            output.append(f"   Confidence: {conf_pct}% | Triad: {lesson['triad']}")

            source = node.get('source', 'unknown')
            created = node.get('created_at', 'unknown')[:10] if 'created_at' in node else 'unknown'
            output.append(f"   Source: {source} | Created: {created}")

            success = node.get('success_count', 0)
            failure = node.get('failure_count', 0)
            contradiction = node.get('contradiction_count', 0)
            output.append(f"   Statistics: {success} success, {failure} failure, {contradiction} contradiction")

            output.append("")
            if conf_pct >= 65:
                output.append("   💡 Action: One more success will push this above 70%")
            else:
                output.append("   💡 Action: Validate to increase confidence")
            output.append("")

    output.append("=" * 67)
    output.append("")

    # Summary by triad
    triads_summary = {}
    for lesson in uncertain_lessons:
        t = lesson['triad']
        triads_summary[t] = triads_summary.get(t, 0) + 1

    output.append("## Summary by Triad")
    output.append("")
    for t, count in sorted(triads_summary.items()):
        output.append(f"- {t}: {count} uncertain lesson{'s' if count != 1 else ''}")

    output.append("")
    output.append("## Recommended Actions")
    output.append("")
    output.append("1. **Validate** lessons you trust: `/knowledge-validate <id-or-label>`")
    output.append("2. **Contradict** incorrect lessons: `/knowledge-contradict <id-or-label> <reason>`")
    output.append("3. **Wait** for natural learning through usage outcomes")
    output.append("")
    output.append("=" * 67)

    return "\n".join(output)
