"""CLI functions for workflow instance management.

This module provides user-facing functions for managing workflow instances:
- list_workflows(): List all workflow instances
- show_workflow(): Show detailed instance information
- resume_workflow(): Get guidance for resuming a workflow
- workflow_history(): Show deviation history
- abandon_workflow(): Mark instance as abandoned
- analyze_deviations(): Analyze deviation patterns

These functions are designed to be called from slash commands in Claude Code.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from triads.workflow_enforcement.instance_manager import (
    WorkflowInstanceManager,
    InstanceNotFoundError,
)
from triads.workflow_enforcement.schema_loader import WorkflowSchemaLoader


def list_workflows(status: str | None = None, base_dir: Path | str | None = None) -> str:
    """List all workflow instances, optionally filtered by status.

    Args:
        status: Optional status filter ("in_progress", "completed", "abandoned")
        base_dir: Base directory for workflows (default: .claude/workflows, used for testing)

    Returns:
        Formatted string showing instance list

    Example:
        >>> print(list_workflows())
        Found 3 workflow instance(s):

        feature-oauth2-20251017-100523
          Title: OAuth2 Integration
          Status: in_progress
          Started: 2025-10-17T10:05:23Z
          Current: implementation

        >>> print(list_workflows(status="completed"))
        Found 1 workflow instance(s):
        ...
    """
    manager = WorkflowInstanceManager(base_dir=base_dir)

    try:
        instances = manager.list_instances(status=status)
    except ValueError as e:
        return f"Error: {e}"

    if not instances:
        if status:
            return f"No {status} workflow instances found."
        return "No workflow instances found."

    output = [f"Found {len(instances)} workflow instance(s):\n"]

    for inst in instances:
        output.append(f"  {inst['instance_id']}")
        output.append(f"    Title: {inst['title']}")
        output.append(f"    Status: {inst['status']}")
        output.append(f"    Started: {inst['started_at']}")
        current = inst.get('current_triad') or 'Not started'
        output.append(f"    Current: {current}")
        output.append("")

    return "\n".join(output)


def show_workflow(instance_id: str, base_dir: Path | str | None = None) -> str:
    """Show detailed information about a specific workflow instance.

    Args:
        instance_id: Instance identifier
        base_dir: Base directory for workflows (default: .claude/workflows, used for testing)

    Returns:
        Formatted string with instance details

    Example:
        >>> print(show_workflow("feature-oauth2-20251017-100523"))
        Workflow Instance: feature-oauth2-20251017-100523

        Title: OAuth2 Integration
        Type: software-development
        Status: in_progress
        ...
    """
    manager = WorkflowInstanceManager(base_dir=base_dir)

    try:
        instance = manager.load_instance(instance_id)
    except InstanceNotFoundError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Error loading instance: {e}"

    output = [
        f"Workflow Instance: {instance.instance_id}\n",
        f"Title: {instance.metadata.get('title', 'Untitled')}",
        f"Type: {instance.workflow_type}",
        f"Status: {instance.metadata.get('status', 'unknown')}",
        f"Started by: {instance.metadata.get('started_by', 'unknown')}",
        f"Started at: {instance.metadata.get('started_at', 'unknown')}\n",
    ]

    # Progress
    progress = instance.workflow_progress
    current = progress.get('current_triad') or 'Not started'
    completed = len(progress.get('completed_triads', []))
    skipped = len(progress.get('skipped_triads', []))
    deviation_count = len(instance.workflow_deviations)

    output.extend([
        "Progress:",
        f"  Current triad: {current}",
        f"  Completed: {completed} triad(s)",
        f"  Skipped: {skipped} triad(s)",
        f"  Deviations: {deviation_count}\n",
    ])

    # Completed triads
    if progress.get('completed_triads'):
        output.append("Completed Triads:")
        for triad in progress['completed_triads']:
            duration = triad.get('duration_minutes', 0)
            output.append(f"  ✓ {triad['triad_id']} ({duration:.1f} minutes)")
        output.append("")

    # Deviations (last 5)
    if instance.workflow_deviations:
        output.append("Workflow Deviations:")
        for dev in instance.workflow_deviations[-5:]:
            dev_type = dev.get('type', 'unknown')
            reason = dev.get('reason', 'No reason provided')
            from_triad = dev.get('from_triad', 'unknown')
            to_triad = dev.get('to_triad', 'unknown')

            output.append(f"  • {dev_type}: {reason}")
            output.append(f"    {from_triad} → {to_triad}")

            if dev.get('skipped'):
                skipped_list = ', '.join(dev['skipped'])
                output.append(f"    Skipped: {skipped_list}")
        output.append("")

    # Significance metrics
    if instance.significance_metrics:
        output.append("Significance Metrics:")
        metrics = instance.significance_metrics

        if 'content_created' in metrics:
            content = metrics['content_created']
            quantity = content.get('quantity', 0)
            units = content.get('units', 'units')
            output.append(f"  Content: {quantity} {units}")

        if 'components_modified' in metrics:
            output.append(f"  Components: {metrics['components_modified']}")

        if 'complexity' in metrics:
            output.append(f"  Complexity: {metrics['complexity']}")

    return "\n".join(output)


def resume_workflow(instance_id: str, base_dir: Path | str | None = None, schema_file: Path | str | None = None) -> str:
    """Get guidance for resuming a workflow instance.

    Args:
        instance_id: Instance identifier
        base_dir: Base directory for workflows (default: .claude/workflows, used for testing)
        schema_file: Path to workflow schema (default: .claude/workflow.json, used for testing)

    Returns:
        Formatted string with resume guidance

    Example:
        >>> print(resume_workflow("feature-oauth2-20251017-100523"))
        Resuming workflow: OAuth2 Integration

        Current triad: implementation
        Progress: 2/5 triads completed

        Continue with current: Start implementation
        Or proceed to next: Start garden-tending
    """
    manager = WorkflowInstanceManager(base_dir=base_dir)
    schema_loader = WorkflowSchemaLoader(schema_file=schema_file)

    try:
        instance = manager.load_instance(instance_id)
        schema = schema_loader.load_schema()
    except InstanceNotFoundError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Error loading instance or schema: {e}"

    current = instance.workflow_progress.get('current_triad')

    if not current:
        # Not started yet - suggest first triad
        if schema.triads:
            first_triad = schema.triads[0]
            return (
                f"Workflow not yet started.\n"
                f"Suggested: Start {first_triad.id}: {instance.metadata.get('title')}"
            )
        else:
            return "Error: Workflow schema has no triads defined"

    # Already in progress
    output = [
        f"Resuming workflow: {instance.metadata.get('title', 'Untitled')}\n",
        f"Current triad: {current}",
        f"Progress: {len(instance.workflow_progress.get('completed_triads', []))}/{len(schema.triads)} triads completed\n",
    ]

    # Suggest next action
    completed_ids = [t['triad_id'] for t in instance.workflow_progress.get('completed_triads', [])]
    remaining = [t for t in schema.triads if t.id not in completed_ids and t.id != current]

    if remaining:
        next_triad = remaining[0]
        output.append(f"Continue with current: Start {current}")
        output.append(f"Or proceed to next: Start {next_triad.id}")
    else:
        output.append(f"Final triad: Start {current}")
        output.append("After completion, workflow will be complete!")

    return "\n".join(output)


def workflow_history(instance_id: str, base_dir: Path | str | None = None) -> str:
    """Show deviation history for a workflow instance.

    Args:
        instance_id: Instance identifier
        base_dir: Base directory for workflows (default: .claude/workflows, used for testing)

    Returns:
        Formatted string with deviation history

    Example:
        >>> print(workflow_history("feature-oauth2-20251017-100523"))
        Deviation History: OAuth2 Integration

        Total deviations: 3

        By Type:
          skip_forward: 2
          skip_backward: 1

        Chronological History:
        ...
    """
    manager = WorkflowInstanceManager(base_dir=base_dir)

    try:
        instance = manager.load_instance(instance_id)
    except InstanceNotFoundError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Error loading instance: {e}"

    if not instance.workflow_deviations:
        return f"No deviations recorded for: {instance.metadata.get('title', 'Untitled')}"

    output = [
        f"Deviation History: {instance.metadata.get('title', 'Untitled')}\n",
        f"Total deviations: {len(instance.workflow_deviations)}\n",
    ]

    # Group by type
    by_type = Counter(d.get('type', 'unknown') for d in instance.workflow_deviations)
    output.append("By Type:")
    for dev_type, count in by_type.most_common():
        output.append(f"  {dev_type}: {count}")
    output.append("")

    # Chronological history
    output.append("Chronological History:")
    for i, dev in enumerate(instance.workflow_deviations, 1):
        timestamp = dev.get('timestamp', 'unknown')
        dev_type = dev.get('type', 'unknown')
        reason = dev.get('reason', 'No reason provided')
        from_triad = dev.get('from_triad', 'unknown')
        to_triad = dev.get('to_triad', 'unknown')

        output.append(f"{i}. [{timestamp}] {dev_type}")
        output.append(f"   {from_triad} → {to_triad}")
        output.append(f"   Reason: {reason}")

        if dev.get('skipped'):
            skipped_list = ', '.join(dev['skipped'])
            output.append(f"   Skipped: {skipped_list}")
        output.append("")

    return "\n".join(output)


def abandon_workflow(instance_id: str, reason: str, base_dir: Path | str | None = None) -> str:
    """Mark a workflow instance as abandoned.

    Args:
        instance_id: Instance identifier
        reason: Reason for abandonment
        base_dir: Base directory for workflows (default: .claude/workflows, used for testing)

    Returns:
        Formatted string confirming abandonment

    Example:
        >>> print(abandon_workflow("feature-oauth2-20251017-100523", "Project cancelled"))
        ✓ Workflow abandoned: feature-oauth2-20251017-100523
        Moved to: .claude/workflows/abandoned/feature-oauth2-20251017-100523.json
    """
    if not reason:
        return "Error: Reason required for abandoning workflow"

    manager = WorkflowInstanceManager(base_dir=base_dir)

    try:
        instance = manager.load_instance(instance_id)

        # Confirm action (in actual use, this would prompt user)
        title = instance.metadata.get('title', 'Untitled')

        # Perform abandonment
        manager.abandon_instance(instance_id, reason)

        return (
            f"✓ Workflow abandoned: {instance_id}\n"
            f"Title: {title}\n"
            f"Reason: {reason}\n"
            f"Moved to: .claude/workflows/abandoned/{instance_id}.json"
        )

    except InstanceNotFoundError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Error abandoning instance: {e}"


def analyze_deviations(base_dir: Path | str | None = None) -> str:
    """Analyze deviation patterns across all workflow instances.

    Args:
        base_dir: Base directory for workflows (default: .claude/workflows, used for testing)

    Returns:
        Formatted string with deviation analytics

    Example:
        >>> print(analyze_deviations())
        Workflow Deviation Analytics

        Total Instances: 15
        Instances with Deviations: 12 (80.0%)
        Total Deviations: 34
        ...
    """
    manager = WorkflowInstanceManager(base_dir=base_dir)

    # Load all instances
    all_instances = []
    for status in ['in_progress', 'completed', 'abandoned']:
        try:
            instances = manager.list_instances(status=status)
            # Load full instances to get deviations
            for inst_summary in instances:
                try:
                    full_inst = manager.load_instance(inst_summary['instance_id'])
                    all_instances.append(full_inst)
                except Exception:
                    continue
        except Exception:
            continue

    if not all_instances:
        return "No workflow instances found"

    # Aggregate statistics
    total_instances = len(all_instances)
    total_deviations = sum(len(i.workflow_deviations) for i in all_instances)
    instances_with_deviations = sum(1 for i in all_instances if i.workflow_deviations)

    output = [
        "Workflow Deviation Analytics\n",
        f"Total Instances: {total_instances}",
        f"Instances with Deviations: {instances_with_deviations} ({instances_with_deviations / total_instances * 100:.1f}%)",
        f"Total Deviations: {total_deviations}",
    ]

    if total_deviations > 0:
        avg_per_instance = total_deviations / total_instances
        output.append(f"Average per Instance: {avg_per_instance:.1f}\n")

        # Deviation types
        all_deviations = [d for i in all_instances for d in i.workflow_deviations]
        by_type = Counter(d.get('type', 'unknown') for d in all_deviations)

        output.append("Deviation Types:")
        for dev_type, count in by_type.most_common():
            percentage = count / total_deviations * 100
            output.append(f"  {dev_type}: {count} ({percentage:.1f}%)")
        output.append("")

        # Most skipped triads
        skipped_triads = []
        for i in all_instances:
            for dev in i.workflow_deviations:
                if dev.get('skipped'):
                    skipped_triads.extend(dev['skipped'])

        if skipped_triads:
            most_skipped = Counter(skipped_triads)
            output.append("Most Skipped Triads:")
            for triad_id, count in most_skipped.most_common(5):
                output.append(f"  {triad_id}: {count} times")
            output.append("")

        # Common reason keywords
        reasons = [d.get('reason', '') for d in all_deviations if d.get('reason')]
        reason_keywords = []
        for reason in reasons:
            words = reason.lower().split()
            reason_keywords.extend([w for w in words if len(w) > 5])

        if reason_keywords:
            common_keywords = Counter(reason_keywords)
            output.append("Common Reason Keywords:")
            for keyword, count in common_keywords.most_common(10):
                output.append(f"  {keyword}: {count} occurrences")
            output.append("")

        # Recommendations
        output.append("Recommendations:")
        if skipped_triads:
            top_skipped = Counter(skipped_triads).most_common(1)[0]
            output.append(f"  • '{top_skipped[0]}' is frequently skipped ({top_skipped[1]} times)")
            output.append("    Consider: Is this triad necessary? Should it be optional?")

        skip_forward_count = by_type.get('skip_forward', 0)
        if skip_forward_count > total_deviations * 0.5:
            output.append("  • 50%+ deviations are 'skip_forward'")
            output.append("    Consider: Is workflow sequence realistic? Should enforcement be more flexible?")

    return "\n".join(output)
