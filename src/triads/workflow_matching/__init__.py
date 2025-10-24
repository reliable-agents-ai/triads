"""Workflow matching and gap detection.

DEPRECATED: This module has been moved to triads.tools.router as part of
Phase 9 DDD refactoring. All functionality is now available from:

    from triads.tools.router import (
        classify_workflow_headless,
        HeadlessClassificationResult,
        WORKFLOW_DEFINITIONS,
        WorkflowMatcher,
        MatchResult,
        WORKFLOW_KEYWORDS,
        get_keywords,
        get_all_workflow_types,
    )

This module provides backward compatibility shims. New code should import
from triads.tools.router instead.

Migration Guide:
- Old: from triads.workflow_matching.matcher import WorkflowMatcher
  New: from triads.tools.router.matching import WorkflowMatcher
  OR:  from triads.tools.router import WorkflowMatcher

- Old: from triads.workflow_matching import classify_workflow_headless
  New: from triads.tools.router import classify_workflow_headless

- Old: from triads.workflow_matching.keywords import WORKFLOW_KEYWORDS
  New: from triads.tools.router import WORKFLOW_KEYWORDS

See docs/PHASE_9_REFACTOR.md for complete migration guide.
"""

import warnings

# Issue deprecation warning
warnings.warn(
    "triads.workflow_matching is deprecated and will be removed in a future version. "
    "Use triads.tools.router instead. "
    "See docs/PHASE_9_REFACTOR.md for migration guide.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export from new locations for backward compatibility
from triads.tools.router import (
    classify_workflow_headless,
    HeadlessClassificationResult,
    WORKFLOW_DEFINITIONS,
    WorkflowMatcher,
    MatchResult,
    WORKFLOW_KEYWORDS,
    get_keywords,
    get_all_workflow_types,
)

# Configuration constants - import from actual config.py file
# (workflow_matching/config.py has different constants than tools/router/config.py)
from triads.workflow_matching import config

# LLM fallback stub (was never implemented, always returned None)
def classify_with_llm(user_message: str, confidence_threshold: float = 0.7):
    """LLM-based workflow classification fallback (Phase 1 stub).

    This function was never fully implemented and always returned None.
    Kept for backward compatibility.

    DEPRECATED: Use classify_workflow_headless instead.

    Performance Target: <5s for LLM classification (not implemented)

    Args:
        user_message: User's request text
        confidence_threshold: Minimum confidence for classification (ignored in stub)

    Returns:
        None (stub always returns None)
    """
    warnings.warn(
        "classify_with_llm was never implemented and is deprecated. "
        "Use classify_workflow_headless instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return None

__all__ = [
    # Headless mode classifier
    "classify_workflow_headless",
    "HeadlessClassificationResult",
    "WORKFLOW_DEFINITIONS",
    # Configuration (shim)
    "config",
    # Keyword matching
    "WorkflowMatcher",
    "MatchResult",
    "WORKFLOW_KEYWORDS",
    "get_keywords",
    "get_all_workflow_types",
    # LLM fallback (stub)
    "classify_with_llm",
]
