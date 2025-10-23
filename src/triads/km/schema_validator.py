"""Knowledge graph schema validation.

DEPRECATED: This module has been refactored into triads.tools.knowledge.validation
as part of the DDD architecture consolidation.

New location: triads.tools.knowledge.validation

This module provides backward compatibility. Please update imports to:
    from triads.tools.knowledge.validation import (
        ValidationError,
        VALID_NODE_TYPES,
        validate_graph,
        validate_graph_structure,
        validate_node,
        validate_edge
    )
"""

from __future__ import annotations

import warnings
from typing import Any

# Import from new location
from triads.tools.knowledge.validation import (
    ValidationError,
    VALID_NODE_TYPES,
    validate_graph,
    validate_graph_structure,
    validate_node,
    validate_edge,
)

# Show deprecation warning
warnings.warn(
    "triads.km.schema_validator is deprecated. "
    "Use triads.tools.knowledge.validation instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export everything for backward compatibility
__all__ = [
    "ValidationError",
    "VALID_NODE_TYPES",
    "validate_graph",
    "validate_graph_structure",
    "validate_node",
    "validate_edge",
]
