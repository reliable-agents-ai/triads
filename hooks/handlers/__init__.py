"""
Handlers package for on_stop.py orchestrator.

This package contains specialized handlers that follow the Single Responsibility Principle.
Each handler manages one aspect of post-response processing.

Handlers:
- HandoffHandler: Triad handoff lifecycle management
- WorkflowCompletionHandler: Workflow completion recording
- GraphUpdateHandler: Knowledge graph updates with pre-flight validation
- KMValidationHandler: Experience-based learning (3 detection methods)
- WorkspacePauseHandler: Workspace auto-pause on session end

Architecture: Orchestrator Pattern
- on_stop.py delegates to these handlers
- Each handler is independently testable
- SOLID principles throughout
"""

__all__ = [
    'HandoffHandler',
    'WorkflowCompletionHandler',
    'GraphUpdateHandler',
    'KMValidationHandler',
    'WorkspacePauseHandler',
]
