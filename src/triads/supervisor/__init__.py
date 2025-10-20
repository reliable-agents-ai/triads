"""
Supervisor module for triad routing and orchestration.

This module implements the Supervisor-first architecture (ADR-007) where
all user interactions are triaged and routed through a Supervisor agent
that classifies problems and routes to appropriate workflows.

Key components:
- core.py: Supervisor invocation logic
- classifier.py: Problem classification (Phase 3)
- executor.py: Workflow execution monitoring (Phase 4)
- learning.py: Routing improvement over time (Phase 5)

Phase 1 Status: Core implementation only
Future phases will add classification, execution, and learning capabilities.
"""

from triads.supervisor.core import invoke_supervisor

__all__ = ["invoke_supervisor"]
