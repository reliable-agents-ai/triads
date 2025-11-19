"""
Constants for Claude Code hooks.

Eliminates magic numbers/strings scattered throughout code.
Every constant includes documentation explaining:
- Purpose: Why it exists
- Impact: What happens if changed
- Evidence: Why this specific value

Single source of truth for configuration values.
"""

# ============================================================================
# Plugin Metadata
# ============================================================================

PLUGIN_VERSION = "0.16.0"
"""
Current plugin version.

Purpose: Version tracking for compatibility and debugging
Impact: Shown in events, logs, and error messages
Evidence: Incremented with each release (semantic versioning)
"""

# ============================================================================
# Time Thresholds
# ============================================================================

HANDOFF_EXPIRY_HOURS = 24
"""
Hours before pending handoff expires.

Purpose: Prevent stale handoffs from accumulating
Impact: Handoffs older than this are ignored/cleaned up
Evidence: 24 hours gives full business day for pickup
"""

# ============================================================================
# Confidence Thresholds
# ============================================================================

CONFIDENCE_THRESHOLD_ACCEPTABLE = 0.70
"""
Minimum acceptable confidence threshold (70%).

Purpose: Knowledge must meet minimum quality bar
Impact: Nodes below this flagged for review
Evidence: Based on KM validation research (70% = needs validation)
"""

CONFIDENCE_THRESHOLD_AUTO_PAUSE = 0.85
"""
Confidence threshold for workspace auto-pause (85%).

Purpose: Only auto-pause if context detection is confident
Impact: Workspace pause decisions at ≥85% confidence
Evidence: workspace_detector.py uses this threshold
"""

CONFIDENCE_THRESHOLD_HIGH = 0.90
"""
High confidence threshold (90%).

Purpose: High-quality knowledge threshold
Impact: Knowledge above this considered "high quality"
Evidence: Based on multi-method verification requirements
"""

CONFIDENCE_THRESHOLD_VERY_HIGH = 0.95
"""
Very high confidence threshold (95%) for critical blocking warnings.

Purpose: Block operations only when extremely confident about risk
Impact: Experience-based blocking only triggers at ≥95% confidence
Evidence: PreExperienceInjection hook uses this for blocking point-of-no-return operations
"""

# ============================================================================
# Security Limits (Rate Limiting, File Size)
# ============================================================================

MAX_EVENT_FILE_SIZE_MB = 10
"""
Maximum event file size in megabytes (10 MB).

Purpose: Prevent unbounded file growth
Impact: Triggers automatic file rotation
Evidence: 10 MB ≈ 50,000 events, sufficient for months of activity
Security: Prevents disk exhaustion DoS attacks
"""

MAX_EVENTS_PER_FILE = 10000
"""
Maximum events per file before rotation (10,000).

Purpose: Keep files manageable for parsing
Impact: Triggers automatic file rotation
Evidence: 10K events balances file size and rotation frequency
"""

EVENT_RATE_LIMIT_PER_MINUTE = 100
"""
Maximum events per hook per minute (100).

Purpose: Prevent event flooding DoS attacks
Impact: Events beyond this rate are dropped
Evidence: Normal hook execution = 1-10 events/min, 100 provides safety margin
Security: Prevents malicious/buggy hooks from overwhelming system
"""

# ============================================================================
# Input Validation
# ============================================================================

MAX_USER_INPUT_SIZE_KB = 100
"""
Maximum user input size in kilobytes (100 KB).

Purpose: Prevent memory exhaustion from large inputs
Impact: Inputs larger than this are truncated/rejected
Evidence: Typical user prompts = 0.1-5 KB, 100 KB provides generous margin
Security: Prevents buffer overflow and memory DoS attacks
"""

# ============================================================================
# File Paths
# ============================================================================

EVENTS_FILE = ".triads/events.jsonl"
"""
Path to events file (JSONL format).

Purpose: Centralized event storage location
Impact: All hooks write events to this file
Evidence: .triads/ directory for workspace-specific data
"""

# ============================================================================
# Separator Lines (Display)
# ============================================================================

SEPARATOR_LINE = "=" * 80
"""
Standard separator line for console output (80 characters).

Purpose: Visual separation in console output
Impact: Consistent formatting across hooks
Evidence: 80 chars = standard terminal width
"""
