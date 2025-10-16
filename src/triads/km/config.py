"""Configuration constants for knowledge management module.

This module centralizes all configuration values for the KM system.
All magic numbers and thresholds should be defined here for easy tuning.

Usage:
    from triads.km import config

    snippet = text[:config.SEARCH_SNIPPET_LENGTH_LABEL]
"""

# Search configuration
SEARCH_SNIPPET_LENGTH_LABEL = 100
SEARCH_SNIPPET_LENGTH_DESCRIPTION = 150

# Relevance scoring
RELEVANCE_SCORE_LABEL_MATCH = 1.0
RELEVANCE_SCORE_DESCRIPTION_MATCH = 0.7
RELEVANCE_SCORE_ID_MATCH = 0.5

# Confidence thresholds
DEFAULT_MIN_CONFIDENCE = 0.0
WELL_VERIFIED_THRESHOLD = 0.85
