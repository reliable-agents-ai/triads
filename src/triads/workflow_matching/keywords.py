"""Keyword library for workflow matching.

This module defines the keyword sets for the 5 seed workflows that cover
80% of common development needs (per ADR-017: Workflow Library Bootstrap).

Seed Workflows (ADR-017):
1. bug-fix: Fixing errors, crashes, and defects
2. feature-dev: Building new features and capabilities
3. performance: Optimizing speed, memory, and efficiency
4. refactoring: Improving code quality and maintainability
5. investigation: Understanding root causes and exploring unknowns

Keywords are carefully chosen to:
- Cover common natural language variations
- Balance precision (avoid false matches) vs recall (catch valid matches)
- Include both technical terms and everyday language
"""

from typing import Dict, Set


# Keyword library for 5 seed workflows (ADR-017)
WORKFLOW_KEYWORDS: Dict[str, Set[str]] = {
    "bug-fix": {
        # Core bug terminology (include common variations)
        "bug", "bugs", "error", "errors", "crash", "crashes", "crashed",
        "fix", "fixes", "fixed", "broken", "issue", "issues",
        "fault", "faults", "defect", "defects", "failing", "failure", "failures",
        "exception", "exceptions",

        # Debugging terminology
        "stacktrace", "traceback", "debug",

        # Common phrases
        "not", "working", "doesnt", "work", "stopped",

        # Error types
        "null", "undefined",

        # Actions
        "repair", "resolve", "correct"
    },

    "feature-dev": {
        # Core feature terminology
        "feature", "add", "new", "create", "build", "implement",
        "develop", "development", "enhancement", "capability", "functionality",

        # Integration terminology
        "support", "enable", "integrate", "integration", "extend", "plugin",

        # Planning terminology (removed overly generic: should, could, would, need, want)

        # Nouns (removed generic: system, api)
        "component", "module", "interface"
    },

    "performance": {
        # Speed terminology
        "slow", "slower", "slowness", "performance", "optimize", "optimizing",
        "speed", "speeding", "latency", "faster", "quick", "responsive",

        # Resource terminology
        "bottleneck", "bottlenecks", "memory", "cpu", "profile", "profiling",
        "benchmark", "benchmarking", "usage", "consumption", "resource", "resources",

        # Optimization terminology
        "cache", "caching", "scale", "scaling", "efficient", "efficiency", "throughput",

        # Measurements
        "ms", "seconds", "minutes", "timeout", "delay"
    },

    "refactoring": {
        # Refactoring terminology
        "refactor", "cleanup", "simplify", "reorganize", "restructure",
        "rewrite", "consolidate",

        # Code quality terminology
        "debt", "technical", "improve", "maintainability",
        "readable", "modular", "clean", "quality",

        # Actions
        "extract", "split", "merge", "rename", "remove",
        "duplicate", "duplication", "dry"
    },

    "investigation": {
        # Investigation terminology
        "investigate", "analyzing", "analyze", "understand", "explore", "research",
        "study", "examine", "review", "assess", "audit",

        # Questions (removed overly generic: when, where, which, what)
        "why", "how",

        # Root cause terminology
        "causing", "cause", "root", "source", "origin",
        "diagnose", "determine",

        # Learning terminology
        "learn", "discover", "find", "identify", "trace"
    }
}


def get_keywords(workflow_type: str) -> Set[str]:
    """Get keywords for a workflow type.

    Args:
        workflow_type: Name of workflow (e.g., "bug-fix", "feature-dev")

    Returns:
        Set of keywords for the workflow type, or empty set if not found

    Example:
        >>> keywords = get_keywords("bug-fix")
        >>> "bug" in keywords
        True
    """
    return WORKFLOW_KEYWORDS.get(workflow_type, set())


def get_all_workflow_types() -> list[str]:
    """Get list of all workflow types.

    Returns:
        List of workflow type names

    Example:
        >>> types = get_all_workflow_types()
        >>> "bug-fix" in types
        True
        >>> len(types)
        5
    """
    return list(WORKFLOW_KEYWORDS.keys())
