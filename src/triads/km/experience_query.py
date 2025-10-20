"""Experience-based learning query engine.

This module provides the core query functionality for the Experience Learning System.
It finds relevant procedural knowledge (checklists, patterns, warnings, requirements)
based on tool execution context.

Key Features:
- High-performance relevance scoring (< 100ms target)
- Priority-weighted results (CRITICAL items get 2.0x boost)
- Structured trigger matching (tool + file + keywords)
- Per-session caching for speed

Security:
- All graph data treated as plain text (no eval/exec)
- Safe JSON parsing with error handling
- Input validation on all parameters

Performance:
- Target: P95 < 100ms (called on EVERY tool use)
- Cached graph loading (load once per session)
- Early exit on irrelevant tools
- Simple matching (no regex in hot path)

Usage:
    engine = ExperienceQueryEngine()

    # Query for tool context
    results = engine.query_for_tool_use(
        tool_name="Write",
        tool_input={"file_path": "plugin.json"},
        cwd="/path/to/project"
    )

    # Get all CRITICAL items
    critical = engine.get_critical_knowledge()

    for item in results:
        print(item.formatted_text)
"""

from __future__ import annotations

import fnmatch
import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from triads.km.graph_access import GraphLoader

# Initialize module logger
logger = logging.getLogger(__name__)

# Performance targets
TARGET_P95_MS = 100.0

# Relevance scoring weights (must sum to 1.0)
WEIGHT_TOOL = 0.40
WEIGHT_FILE = 0.40
WEIGHT_ACTION_KEYWORDS = 0.10
WEIGHT_CONTEXT_KEYWORDS = 0.10

# Priority multipliers
PRIORITY_MULTIPLIERS = {
    "CRITICAL": 2.0,
    "HIGH": 1.5,
    "MEDIUM": 1.0,
    "LOW": 0.5,
}

# Minimum relevance threshold after multiplier
RELEVANCE_THRESHOLD = 0.4

# Process types
PROCESS_TYPES = ["checklist", "pattern", "warning", "requirement"]


# ============================================================================
# Data Classes
# ============================================================================


@dataclass
class ProcessKnowledge:
    """A single piece of process knowledge (checklist, pattern, warning, requirement).

    Represents procedural knowledge that should be consulted before taking actions.

    Attributes:
        node_id: Unique identifier for the knowledge node
        triad: Source triad name (e.g., 'deployment', 'design')
        label: Human-readable title
        description: Detailed description of the process knowledge
        process_type: Type of knowledge (checklist, pattern, warning, requirement)
        priority: Priority level (CRITICAL, HIGH, MEDIUM, LOW)
        trigger_conditions: Conditions that trigger this knowledge
        content: Type-specific content (e.g., checklist items)
        relevance_score: Calculated relevance (0-1, after priority multiplier)
        formatted_text: Pre-formatted text for injection into context
        confidence: Confidence score (0.0-1.0) indicating reliability
        needs_validation: Whether this knowledge needs validation (confidence < 0.70)
        deprecated: Whether this knowledge has been deprecated
    """

    node_id: str
    triad: str
    label: str
    description: str
    process_type: str
    priority: str
    trigger_conditions: dict[str, Any]
    content: dict[str, Any]
    relevance_score: float
    formatted_text: str
    confidence: float
    needs_validation: bool
    deprecated: bool


# ============================================================================
# ExperienceQueryEngine: Main query class
# ============================================================================


class ExperienceQueryEngine:
    """Query engine for finding relevant process knowledge.

    Provides high-performance queries to find procedural knowledge (checklists,
    patterns, warnings, requirements) relevant to impending tool executions.

    Performance:
        - Target: P95 < 100ms (called on every tool use)
        - Achieves speed via caching, early exits, simple matching
        - Monitors and logs slow queries (> 100ms)

    Architecture:
        - Loads all graphs once, caches in memory
        - Filters by process_type (Concept nodes only)
        - Calculates relevance using structured scoring
        - Applies priority multipliers for CRITICAL/HIGH items
        - Returns top-N most relevant items

    Example:
        engine = ExperienceQueryEngine()

        # Query before Write to plugin.json
        results = engine.query_for_tool_use(
            tool_name="Write",
            tool_input={"file_path": "/path/to/plugin.json"},
            cwd="/path/to"
        )

        # Results are pre-formatted and ready to inject
        for item in results:
            print(item.formatted_text)
    """

    def __init__(self, graphs_dir: Path | None = None) -> None:
        """Initialize query engine with optional custom graphs directory.

        Args:
            graphs_dir: Path to graphs directory. Defaults to .claude/graphs/
        """
        self._loader = GraphLoader(graphs_dir=graphs_dir)
        self._cache: dict[str, list[dict[str, Any]]] | None = None
        self._graphs_dir = graphs_dir or Path(".claude/graphs")

    def query_for_tool_use(
        self,
        tool_name: str,
        tool_input: dict[str, Any],
        cwd: str = ".",
        max_results: int = 5,
    ) -> list[ProcessKnowledge]:
        """Query process knowledge relevant to impending tool use.

        Finds procedural knowledge (checklists, patterns, warnings, requirements)
        that should be consulted before executing the specified tool.

        Performance:
            - Target: < 100ms (P95)
            - Monitors execution time, logs warnings if slow
            - Early exits on irrelevant tools

        Args:
            tool_name: Name of tool about to be executed (e.g., "Write", "Edit")
            tool_input: Tool parameters (must include file_path for file tools)
            cwd: Current working directory (for resolving relative paths)
            max_results: Maximum number of results to return (default: 5)

        Returns:
            List of ProcessKnowledge objects, sorted by priority then relevance,
            deduplicated by label, limited to max_results.
            Empty list if no relevant knowledge found.

        Example:
            results = engine.query_for_tool_use(
                tool_name="Write",
                tool_input={"file_path": "plugin.json", "content": "..."},
                cwd="/Users/dev/project"
            )

            for item in results:
                print(f"[{item.priority}] {item.label}")
                print(item.formatted_text)
        """
        start_time = time.perf_counter()

        try:
            # Load and cache all process knowledge
            if self._cache is None:
                self._cache = self._load_process_knowledge()

            # Early exit if no process knowledge exists
            if not self._cache:
                return []

            # Extract file path if present
            file_path = tool_input.get("file_path", "")
            if file_path:
                # Normalize path (absolute or relative to cwd)
                try:
                    path_obj = Path(file_path)
                    if not path_obj.is_absolute():
                        path_obj = Path(cwd) / path_obj
                    file_path = str(path_obj)
                except (ValueError, OSError):
                    # Invalid path, use as-is
                    pass

            # Convert tool_input to string for keyword matching
            tool_input_str = json.dumps(tool_input, default=str).lower()

            # Calculate relevance for all process knowledge nodes
            results: list[tuple[dict[str, Any], str, float]] = []

            for triad_name, nodes in self._cache.items():
                for node in nodes:
                    relevance = self._calculate_relevance(
                        node=node,
                        tool_name=tool_name,
                        file_path=file_path,
                        tool_input_str=tool_input_str,
                    )

                    # Apply threshold
                    if relevance >= RELEVANCE_THRESHOLD:
                        results.append((node, triad_name, relevance))

            # Sort by priority (CRITICAL first), then by relevance
            results.sort(
                key=lambda x: (
                    -PRIORITY_MULTIPLIERS.get(x[0].get("priority", "MEDIUM"), 1.0),
                    -x[2]
                )
            )

            # Convert to ProcessKnowledge objects with deduplication
            knowledge_items = []
            seen_labels = set()

            for node, triad_name, relevance in results:
                item = self._node_to_process_knowledge(node, triad_name, relevance)
                if item:
                    # Deduplicate by label (handle duplicate nodes)
                    if item.label not in seen_labels:
                        seen_labels.add(item.label)
                        knowledge_items.append(item)

                        # Stop if we've reached max_results
                        if len(knowledge_items) >= max_results:
                            break

            return knowledge_items

        finally:
            # Monitor performance
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            if elapsed_ms > TARGET_P95_MS:
                logger.warning(
                    f"Slow experience query: {elapsed_ms:.1f}ms (target: {TARGET_P95_MS}ms)",
                    extra={
                        "tool_name": tool_name,
                        "file_path": tool_input.get("file_path", ""),
                        "elapsed_ms": elapsed_ms,
                    }
                )

    def get_critical_knowledge(self) -> list[ProcessKnowledge]:
        """Get all CRITICAL priority process knowledge.

        Returns all CRITICAL items regardless of context. Used for displaying
        at session start to ensure maximum visibility of critical procedures.

        Returns:
            List of CRITICAL ProcessKnowledge objects, sorted by relevance.
            Empty list if no critical knowledge exists.

        Example:
            critical = engine.get_critical_knowledge()
            print(f"You have {len(critical)} CRITICAL procedures to be aware of:")
            for item in critical:
                print(f"  - {item.label}")
        """
        # Load and cache all process knowledge
        if self._cache is None:
            self._cache = self._load_process_knowledge()

        if not self._cache:
            return []

        # Collect all CRITICAL nodes
        critical_items = []

        for triad_name, nodes in self._cache.items():
            for node in nodes:
                if node.get("priority") == "CRITICAL":
                    # Use max relevance since we're showing all CRITICAL
                    item = self._node_to_process_knowledge(node, triad_name, 1.0)
                    if item:
                        critical_items.append(item)

        return critical_items

    def _load_process_knowledge(self) -> dict[str, list[dict[str, Any]]]:
        """Load all process knowledge nodes from all graphs.

        Filters out deprecated nodes (deprecated = True).

        Returns:
            Dictionary mapping triad_name to list of process knowledge nodes.
            Empty dict if no graphs or no process knowledge found.
        """
        all_graphs = self._loader.load_all_graphs()
        process_knowledge: dict[str, list[dict[str, Any]]] = {}

        for triad_name, graph in all_graphs.items():
            nodes = graph.get("nodes", [])

            # Filter to process knowledge nodes (Concept type with process_type)
            # and exclude deprecated nodes
            process_nodes = [
                node for node in nodes
                if (
                    node.get("type") == "Concept"
                    and "process_type" in node
                    and not node.get("deprecated", False)  # Filter deprecated
                )
            ]

            if process_nodes:
                process_knowledge[triad_name] = process_nodes

        logger.debug(
            f"Loaded {sum(len(nodes) for nodes in process_knowledge.values())} "
            f"process knowledge nodes from {len(process_knowledge)} triads"
        )

        return process_knowledge

    def _calculate_relevance(
        self,
        node: dict[str, Any],
        tool_name: str,
        file_path: str,
        tool_input_str: str,
    ) -> float:
        """Calculate relevance score for a process knowledge node.

        Uses structured scoring algorithm:
        - Tool name match: 40% (exact) or 20% (wildcard)
        - File pattern match: 40%
        - Action keywords: 10%
        - Context keywords: 10%
        - Priority multiplier: CRITICAL=2.0x, HIGH=1.5x, MEDIUM=1.0x, LOW=0.5x
        - Confidence weighting: final_score * confidence (0.0-1.0)

        Args:
            node: Process knowledge node dictionary
            tool_name: Tool being executed
            file_path: Normalized file path (absolute)
            tool_input_str: JSON string of tool_input (for keyword matching)

        Returns:
            Relevance score (0-1+, can exceed 1.0 with CRITICAL multiplier).
            Higher scores = more relevant.
        """
        trigger_conditions = node.get("trigger_conditions", {})

        base_score = 0.0

        # 1. Tool name matching (40% weight)
        tool_names = trigger_conditions.get("tool_names", [])
        if tool_name in tool_names:
            base_score += WEIGHT_TOOL
        elif "*" in tool_names or "**" in tool_names:
            # Wildcard match (lower weight)
            base_score += WEIGHT_TOOL * 0.5

        # 2. File pattern matching (40% weight)
        if file_path:
            file_patterns = trigger_conditions.get("file_patterns", [])
            for pattern in file_patterns:
                if self._match_file_pattern(file_path, pattern):
                    base_score += WEIGHT_FILE
                    break  # Only count once

        # 3. Action keywords (10% weight)
        action_keywords = trigger_conditions.get("action_keywords", [])
        if action_keywords and tool_input_str:
            for keyword in action_keywords:
                if keyword.lower() in tool_input_str:
                    base_score += WEIGHT_ACTION_KEYWORDS
                    break  # Only count once

        # 4. Context keywords (10% weight)
        # Note: In full implementation, this would check recent conversation context
        # For now, check description field as proxy
        context_keywords = trigger_conditions.get("context_keywords", [])
        if context_keywords:
            description = node.get("description", "").lower()
            for keyword in context_keywords:
                if keyword.lower() in description or keyword.lower() in tool_input_str:
                    base_score += WEIGHT_CONTEXT_KEYWORDS
                    break  # Only count once

        # 5. Apply priority multiplier
        priority = node.get("priority", "MEDIUM")
        multiplier = PRIORITY_MULTIPLIERS.get(priority, 1.0)
        priority_score = base_score * multiplier

        # 6. Apply confidence weighting (Phase 2: Confidence-based learning)
        confidence = node.get("confidence", 1.0)  # Default to 1.0 for legacy nodes
        final_score = priority_score * confidence

        # Cap at 1.0 for sanity (though CRITICAL can exceed)
        return min(final_score, 1.0) if priority != "CRITICAL" else final_score

    def _match_file_pattern(self, file_path: str, pattern: str) -> bool:
        """Check if file path matches glob pattern.

        Supports:
        - * (any chars except /)
        - ** (any chars including /)
        - Standard glob patterns

        Args:
            file_path: Absolute file path
            pattern: Glob pattern (e.g., "**/plugin.json", "**/*version*")

        Returns:
            True if path matches pattern, False otherwise.
        """
        # Handle ** (match any directory depth)
        if "**" in pattern:
            # Convert to simple suffix/infix match
            # e.g., "**/plugin.json" -> ends with "plugin.json"
            # e.g., "**/*version*" -> contains "version"

            # Split on **
            parts = pattern.split("**")

            # Check each part
            if len(parts) == 2:
                prefix, suffix = parts

                # Remove leading/trailing slashes from suffix
                suffix = suffix.lstrip("/")

                if suffix:
                    # Use fnmatch on filename component
                    file_name = Path(file_path).name
                    if fnmatch.fnmatch(file_name, suffix.lstrip("/")):
                        return True
                    # Also try full path match
                    if fnmatch.fnmatch(file_path, f"*{suffix}"):
                        return True
                else:
                    # Just ** means match everything
                    return True

        # Standard fnmatch for simple patterns
        return fnmatch.fnmatch(file_path, pattern)

    def _node_to_process_knowledge(
        self,
        node: dict[str, Any],
        triad: str,
        relevance: float,
    ) -> ProcessKnowledge | None:
        """Convert node dictionary to ProcessKnowledge object.

        Args:
            node: Process knowledge node dictionary
            triad: Triad name
            relevance: Calculated relevance score

        Returns:
            ProcessKnowledge object, or None if invalid node
        """
        try:
            process_type = node.get("process_type", "pattern")
            priority = node.get("priority", "MEDIUM")

            # Extract confidence fields (Phase 2: Confidence-based learning)
            confidence = node.get("confidence", 1.0)  # Default to 1.0 for legacy nodes
            needs_validation = node.get("needs_validation", False)
            deprecated = node.get("deprecated", False)

            # Extract type-specific content
            content = {}
            if process_type == "checklist":
                content = node.get("checklist", {})
            elif process_type == "pattern":
                content = node.get("pattern", {})
            elif process_type == "warning":
                content = node.get("warning", {})
            elif process_type == "requirement":
                content = node.get("requirement", {})

            # Format for display
            formatted_text = self._format_for_display(node, process_type, priority)

            return ProcessKnowledge(
                node_id=node.get("id", "unknown"),
                triad=triad,
                label=node.get("label", "Unnamed Process"),
                description=node.get("description", ""),
                process_type=process_type,
                priority=priority,
                trigger_conditions=node.get("trigger_conditions", {}),
                content=content,
                relevance_score=relevance,
                formatted_text=formatted_text,
                confidence=confidence,
                needs_validation=needs_validation,
                deprecated=deprecated,
            )

        except Exception as e:
            logger.warning(
                f"Failed to convert node to ProcessKnowledge: {e}",
                extra={"node_id": node.get("id"), "error": str(e)}
            )
            return None

    def _format_for_display(
        self,
        node: dict[str, Any],
        process_type: str,
        priority: str,
    ) -> str:
        """Format process knowledge for injection into context.

        Formats according to priority and process type:
        - CRITICAL: Red warning, ==== borders, all caps
        - HIGH: Yellow warning, ---- borders
        - MEDIUM: Blue info, ---- borders
        - LOW: Gray info, no borders

        Args:
            node: Process knowledge node
            process_type: Type of knowledge (checklist, pattern, warning, requirement)
            priority: Priority level (CRITICAL, HIGH, MEDIUM, LOW)

        Returns:
            Formatted text ready for injection
        """
        label = node.get("label", "Unnamed Process")
        description = node.get("description", "")

        # Priority formatting
        if priority == "CRITICAL":
            icon = "⚠️"
            border = "=" * 60
            priority_label = "CRITICAL"
        elif priority == "HIGH":
            icon = "⚠️"
            border = "-" * 60
            priority_label = "HIGH PRIORITY"
        elif priority == "MEDIUM":
            icon = "ℹ️"
            border = "-" * 60
            priority_label = "IMPORTANT"
        else:  # LOW
            icon = "ℹ️"
            border = ""
            priority_label = "Note"

        # Build output
        lines = []

        if border:
            lines.append(border)

        lines.append(f"{icon} {priority_label}: {label}")

        if description:
            lines.append(f"\n{description}")

        # Add type-specific content
        if process_type == "checklist":
            checklist = node.get("checklist", {})
            items = checklist.get("items", [])
            if items:
                lines.append("\nChecklist:")
                for item in items:
                    lines.append(f"  [ ] {item}")

        elif process_type == "pattern":
            pattern = node.get("pattern", {})
            if "when" in pattern and "then" in pattern:
                lines.append(f"\nWhen: {pattern['when']}")
                lines.append(f"Then: {pattern['then']}")

        elif process_type == "warning":
            warning = node.get("warning", {})
            if "risk" in warning:
                lines.append(f"\nRisk: {warning['risk']}")
            if "mitigation" in warning:
                lines.append(f"Mitigation: {warning['mitigation']}")

        elif process_type == "requirement":
            requirement = node.get("requirement", {})
            if "must" in requirement:
                lines.append(f"\nRequirement: {requirement['must']}")
            if "rationale" in requirement:
                lines.append(f"Rationale: {requirement['rationale']}")

        if border:
            lines.append(border)

        return "\n".join(lines)
