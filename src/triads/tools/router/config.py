"""Configuration constants for router tools.

All thresholds are evidence-based per ADR-013:
- Confidence threshold 0.7 chosen after empirical testing (v0.8.0-alpha.5)
- Score boosts (1.15, 1.1) calibrated against test suite (1,281 tests)
- Timeout 30s based on Claude headless mode avg latency (~9s)

Per P1 refactoring: Extracting magic numbers for maintainability.

Moved from triads.workflow_matching.config as part of Phase 9 DDD refactoring.
"""

import logging

logger = logging.getLogger(__name__)


# ============================================================================
# Confidence Thresholds (ADR-013)
# ============================================================================

# Minimum confidence to accept a workflow match
# Below this threshold, suggest workflow generation instead
CONFIDENCE_THRESHOLD = 0.7

# Confidence bounds
CONFIDENCE_MIN = 0.0  # No match found
CONFIDENCE_MAX = 1.0  # Perfect match

# ============================================================================
# Scoring Weights (Keyword Matching)
# ============================================================================

# Weight for absolute keyword match count (0-1.0)
# Higher weight prioritizes number of matches
ABSOLUTE_WEIGHT = 0.7

# Weight for keyword coverage ratio (0-1.0)
# Lower weight to avoid penalizing large keyword sets
COVERAGE_WEIGHT = 0.3

# Maximum number of keyword matches that yields perfect absolute score
# e.g., 4 matches = 1.0 absolute component
MAX_MATCHES_FOR_PERFECT = 4

# ============================================================================
# Multi-Match Score Boosts
# ============================================================================

# Score boost when 3+ keywords match (15% boost)
# Indicates strong signal alignment
BOOST_MULTI_MATCH_HIGH = 1.15

# Score boost when 2+ keywords match (10% boost)
# Indicates moderate signal alignment
BOOST_MULTI_MATCH_MED = 1.1

# Thresholds for applying boosts
BOOST_THRESHOLD_HIGH = 3  # 3+ matches
BOOST_THRESHOLD_MED = 2   # 2+ matches

# ============================================================================
# API Timeouts
# ============================================================================

# Claude headless mode timeout (seconds)
# Empirical: avg ~9s, 30s allows for network variance
HEADLESS_TIMEOUT_SEC = 30

# Expected target latency for headless classification
# Used for performance monitoring/alerts
HEADLESS_TARGET_LATENCY_SEC = 9
