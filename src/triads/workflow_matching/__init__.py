"""Workflow matching and gap detection.

Per ADR-013 (REVISED): Use Claude headless mode for workflow classification.
Simpler implementation (~50 lines vs ~500), better accuracy, acceptable latency.

Key Components:
- classify_workflow_headless: Claude headless mode classification
- HeadlessClassificationResult: Classification result dataclass
- WorkflowMatcher: Legacy keyword matching (deprecated, kept for backwards compatibility)

Performance:
- Headless classification: 1-3s (acceptable for rare gap detection events)

Usage:
    from triads.workflow_matching import classify_workflow_headless

    result = classify_workflow_headless("Fix the authentication bug")

    if result.workflow_type:
        print(f"Matched: {result.workflow_type} (confidence: {result.confidence})")
    else:
        print("No match - suggest workflow generation")
"""

from .headless_classifier import (
    classify_workflow_headless,
    HeadlessClassificationResult,
    WORKFLOW_DEFINITIONS,
)

# Configuration constants (centralized per P1 refactoring)
from . import config

# Legacy keyword matching (deprecated - kept for backwards compatibility)
from .matcher import WorkflowMatcher, MatchResult
from .keywords import WORKFLOW_KEYWORDS, get_keywords, get_all_workflow_types
from .llm_fallback import classify_with_llm

__all__ = [
    # New headless mode classifier (recommended)
    "classify_workflow_headless",
    "HeadlessClassificationResult",
    "WORKFLOW_DEFINITIONS",
    # Configuration (centralized constants)
    "config",
    # Legacy keyword matching (deprecated)
    "WorkflowMatcher",
    "MatchResult",
    "WORKFLOW_KEYWORDS",
    "get_keywords",
    "get_all_workflow_types",
    "classify_with_llm",
]
