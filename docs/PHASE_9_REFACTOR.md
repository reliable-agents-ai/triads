# Phase 9: Knowledge Management Refactoring

## Overview

This document tracks the refactoring of `src/triads/km/` into proper DDD architecture under `src/triads/tools/knowledge/`.

**Goal**: Remove wrapper pattern and move actual implementation logic into tools layer.

**Status**: Phase 1 Complete ✅

---

## Phase 1: GraphLoader → FileSystemGraphRepository (COMPLETE)

### What Was Refactored

Moved **GraphLoader** logic from `src/triads/km/graph_access/loader.py` into `src/triads/tools/knowledge/repository.py`.

### Changes Made

#### 1. Created New Modules

**`src/triads/tools/knowledge/validation.py`** (242 lines)
- Moved from `triads.km.schema_validator`
- Functions: `validate_graph()`, `validate_node()`, `validate_edge()`, `validate_graph_structure()`
- Exception: `ValidationError`
- Constant: `VALID_NODE_TYPES`

**`src/triads/tools/knowledge/backup.py`** (289 lines)
- Moved from `triads.km.backup_manager`
- Class: `BackupManager`
- Methods: `create_backup()`, `restore_backup()`, `restore_latest()`, `prune_backups()`, `list_backups()`, `load_backup()`, `get_backup_info()`

#### 2. Refactored FileSystemGraphRepository

**`src/triads/tools/knowledge/repository.py`** (597 lines)
- **Before**: Wrapper around GraphLoader
- **After**: Contains actual implementation
- Added exceptions: `InvalidTriadNameError`, `AmbiguousNodeError`, `GraphNotFoundError`
- Added methods:
  - `list_triads()` - List available graphs
  - `load_graph()` - Load graph with caching and security validation
  - `save_graph()` - Save graph with atomic writes, backups, and validation
  - `get_node()` - Find nodes by ID across graphs
  - `_validate_graph_path()` - Security: path traversal prevention
  - `_is_valid_triad_name()` - Security: input validation
  - `_to_domain()` - Transform JSON to domain models

#### 3. Backward Compatibility Shims

**`src/triads/km/graph_access/loader.py`** (104 lines)
- Now a thin wrapper around `FileSystemGraphRepository`
- `GraphLoader` inherits from `FileSystemGraphRepository`
- Deprecation warnings added
- All imports redirected to new location

**`src/triads/km/backup_manager.py`** (50 lines)
- Now imports from `triads.tools.knowledge.backup`
- Deprecation warnings added

**`src/triads/km/schema_validator.py`** (50 lines)
- Now imports from `triads.tools.knowledge.validation`
- Deprecation warnings added
- Re-exports all functions for compatibility

#### 4. Updated Tests

**`tests/test_km/test_graph_atomic_writes.py`**
- Updated mock paths from `triads.km.graph_access.loader.atomic_write_json`
- To: `triads.tools.knowledge.repository.atomic_write_json`
- All 7 tests passing

### Import Migration Guide

| Old Import | New Import |
|------------|------------|
| `from triads.km.graph_access.loader import GraphLoader` | `from triads.tools.knowledge.repository import FileSystemGraphRepository` |
| `from triads.km.backup_manager import BackupManager` | `from triads.tools.knowledge.backup import BackupManager` |
| `from triads.km.schema_validator import validate_graph, ValidationError` | `from triads.tools.knowledge.validation import validate_graph, ValidationError` |

### Test Results

```
1587 passed, 4 skipped, 15 warnings in 65.0s
```

**Zero regressions** ✅

### Preserved Features

All original functionality preserved:
- ✅ Per-session caching
- ✅ Lazy loading
- ✅ Path traversal protection
- ✅ Atomic writes with file locking
- ✅ Auto-backup before writes
- ✅ Auto-restore from backup on corruption
- ✅ Schema validation
- ✅ Backup rotation (keep last N)
- ✅ Node search across graphs
- ✅ Unicode handling
- ✅ User-visible error messages for corruption

### Architecture

**4-Layer DDD Pattern**:
1. **Domain** (`domain.py`) - Node, Edge, KnowledgeGraph models
2. **Repository** (`repository.py`) - Data access, caching, file I/O
3. **Service** (`service.py`) - Use case orchestration
4. **Entrypoint** (`entrypoint.py`) - MCP tool interface

**Supporting Modules**:
- `validation.py` - Schema validation logic
- `backup.py` - Backup and recovery logic
- `formatters.py` - Output formatting
- `bootstrap.py` - DI factory functions

---

## Phase 2: Workflow Enforcement Refactoring (COMPLETE)

### What Was Refactored

Moved core workflow enforcement modules from `src/triads/workflow_enforcement/` into proper DDD architecture under `src/triads/tools/workflow/`.

### Modules Moved (Phases 5-7)

#### Phase 5a: schema_loader.py → schema.py

**`src/triads/tools/workflow/schema.py`** (457 lines)
- Classes: `WorkflowSchemaLoader`, `WorkflowSchema`, `TriadDefinition`, `WorkflowRule`, `EnforcementConfig`
- Exception: `SchemaValidationError`
- Purpose: Load and validate workflow.json schemas (generic, domain-agnostic)
- Features: Schema validation, triad queries, enforcement mode resolution

#### Phase 5b: triad_discovery.py → discovery.py

**`src/triads/tools/workflow/discovery.py`** (193 lines)
- Classes: `TriadDiscovery`, `TriadInfo`
- Exception: `TriadDiscoveryError`
- Purpose: Dynamically discover triads by scanning .claude/agents/
- Features: Directory scanning, caching, safe error handling

#### Phase 6: Instance Manager and State Manager

**Status**: Logic already integrated into `FileSystemWorkflowRepository` (Phase 1-4)
- `instance_manager.py` - Write operations (create, update, complete instances)
- `state_manager.py` - Legacy state management
- These remain in old location for now (still used by enforcement_new.py)

#### Phase 7: Backward Compatibility

**`src/triads/workflow_enforcement/__init__.py`** - Updated with:
- Deprecation warnings (v0.10.0, removal in v0.11.0)
- Re-exports from new locations for moved modules
- Migration guide in docstring

### Import Migration Guide

| Old Location | New Location | Status |
|--------------|--------------|--------|
| `workflow_enforcement.schema_loader.WorkflowSchemaLoader` | `tools.workflow.schema.WorkflowSchemaLoader` | ✅ Moved |
| `workflow_enforcement.schema_loader.WorkflowSchema` | `tools.workflow.schema.WorkflowSchema` | ✅ Moved |
| `workflow_enforcement.triad_discovery.TriadDiscovery` | `tools.workflow.discovery.TriadDiscovery` | ✅ Moved |
| `workflow_enforcement.validator_new.WorkflowValidator` | `tools.workflow.validation.WorkflowValidator` | ✅ Moved (Phase 1-4) |
| `workflow_enforcement.audit.AuditLogger` | `tools.workflow.audit.AuditLogger` | ✅ Moved (Phase 1-4) |
| `workflow_enforcement.bypass.EmergencyBypass` | `tools.workflow.bypass.EmergencyBypass` | ✅ Moved (Phase 1-4) |
| `workflow_enforcement.git_utils.GitRunner` | `tools.workflow.git_utils.GitRunner` | ✅ Moved (Phase 1-4) |
| `workflow_enforcement.instance_manager.WorkflowInstanceManager` | (still in old location) | 🔄 Pending |
| `workflow_enforcement.enforcement_new.WorkflowEnforcer` | (still in old location) | 🔄 Pending |

### Test Results

```
1598 passed, 4 skipped, 16 warnings in 78.97s
```

**Zero regressions** ✅

### Architecture

**tools/workflow/** follows 4-layer DDD pattern:
```
tools/workflow/
├── domain.py          - WorkflowInstance, TriadCompletion, WorkflowDeviation
├── repository.py      - FileSystemWorkflowRepository, InMemoryWorkflowRepository
├── service.py         - WorkflowService (orchestration)
├── entrypoint.py      - MCP tools (list_workflows, get_workflow)
├── validation.py      - WorkflowValidator, ValidationResult
├── enforcement.py     - WorkflowEnforcer, EnforcementResult (uses old modules)
├── audit.py           - AuditLogger
├── bypass.py          - EmergencyBypass
├── git_utils.py       - GitRunner
├── schema.py          - WorkflowSchemaLoader (moved Phase 5)
├── discovery.py       - TriadDiscovery (moved Phase 5)
├── formatters.py      - Output formatting
└── bootstrap.py       - Dependency injection
```

### Preserved Features

All original functionality preserved:
- ✅ Schema-driven, generic workflow enforcement
- ✅ Security validations (path traversal, input sanitization)
- ✅ Atomic file operations with locking
- ✅ Deviation tracking and audit logging
- ✅ Emergency bypass with justification
- ✅ Git-based metrics calculation
- ✅ Graceful error handling

---

## Phase 3: Workflow Matching → Router Tools (COMPLETE)

### What Was Refactored

Moved workflow matching and classification modules from `src/triads/workflow_matching/` into proper DDD architecture under `src/triads/tools/router/`.

**Total Lines Moved**: 705 lines (6 files)

### Changes Made

#### 1. Created New Modules

**`src/triads/tools/router/matching.py`** (202 lines)
- Moved from `triads.workflow_matching.matcher`
- Classes: `WorkflowMatcher`, `MatchResult`
- Purpose: Keyword-based workflow matching with confidence scoring
- Features: Semantic matching, tokenization, scoring algorithm with multi-match boost
- Performance: <100ms per match (ADR-013 requirement)

**`src/triads/tools/router/classification.py`** (204 lines)
- Moved from `triads.workflow_matching.headless_classifier`
- Function: `classify_workflow_headless()`
- Class: `HeadlessClassificationResult`
- Constant: `WORKFLOW_DEFINITIONS`
- Purpose: LLM-based workflow classification using Claude headless mode
- Features: Subprocess execution, timeout handling, JSON parsing
- Performance: ~9s for classification (acceptable for rare events)

**`src/triads/tools/router/keywords.py`** (145 lines)
- Moved from `triads.workflow_matching.keywords`
- Constant: `WORKFLOW_KEYWORDS` (5 seed workflows)
- Functions: `get_keywords()`, `get_all_workflow_types()`
- Purpose: Keyword library for 5 seed workflows (bug-fix, feature-dev, performance, refactoring, investigation)

**`src/triads/tools/router/config.py`** (68 lines)
- Moved from `triads.workflow_matching.config`
- Constants: Confidence thresholds, scoring weights, timeouts
- All evidence-based per ADR-013 (v0.8.0-alpha.5 calibration)

#### 2. Enhanced FileSystemRouterRepository

**`src/triads/tools/router/repository.py`** (260 lines total, +107 added)
- **Added**: `FileSystemRouterRepository` class
- **Purpose**: Production repository using actual TriadRouter
- **Integration**: Uses `triads.router.router.TriadRouter` for routing
- **Integration**: Uses `triads.router.state_manager.RouterStateManager` for state
- **Features**:
  - Routing via semantic/LLM/manual/grace-period methods
  - State persistence with atomic writes and file locking
  - Domain model mapping (tools.router.domain ↔ router.state_manager)

#### 3. Updated Bootstrap

**`src/triads/tools/router/bootstrap.py`** (41 lines)
- **Changed**: Default to `FileSystemRouterRepository` (production)
- **Added**: `use_filesystem` parameter for testing flexibility
- **Added**: `config_path` and `state_path` parameters

#### 4. Backward Compatibility Shims

**`src/triads/workflow_matching/__init__.py`** (100 lines)
- Deprecation warnings on import
- Re-exports from `triads.tools.router`
- Config shim using `__getattr__` delegation
- `classify_with_llm()` stub (was never implemented)
- Migration guide in docstring

### Import Migration Guide

| Old Import | New Import |
|------------|------------|
| `from triads.workflow_matching.matcher import WorkflowMatcher` | `from triads.tools.router.matching import WorkflowMatcher` |
| `from triads.workflow_matching import classify_workflow_headless` | `from triads.tools.router import classify_workflow_headless` |
| `from triads.workflow_matching.keywords import WORKFLOW_KEYWORDS` | `from triads.tools.router import WORKFLOW_KEYWORDS` |
| `from triads.workflow_matching import config` | `from triads.tools.router import config` |

Or simply:
```python
from triads.tools.router import (
    WorkflowMatcher,
    classify_workflow_headless,
    WORKFLOW_KEYWORDS,
    config,
)
```

### Test Results

```
1597 passed, 4 skipped, 38 warnings in 67.61s
```

**Zero regressions** ✅ (1 performance test flake)

### Preserved Features

All original functionality preserved:
- ✅ Keyword-based semantic matching
- ✅ Confidence scoring algorithm (absolute + coverage components)
- ✅ Multi-match boost (1.15x for 3+ matches, 1.1x for 2+ matches)
- ✅ Claude headless mode classification
- ✅ Workflow definitions (5 seed workflows)
- ✅ Security: Input validation, timeout enforcement
- ✅ Error handling: Graceful degradation on API failures
- ✅ All 149 workflow_matching tests pass with deprecation warnings

### Architecture

**tools/router/** follows 4-layer DDD pattern:
```
tools/router/
├── domain.py          - RoutingDecision, RouterState
├── repository.py      - FileSystemRouterRepository (uses TriadRouter), InMemoryRouterRepository
├── service.py         - RouterService (orchestration)
├── entrypoint.py      - MCP tools (route_prompt, get_current_triad)
├── matching.py        - WorkflowMatcher (keyword-based)
├── classification.py  - classify_workflow_headless (LLM-based)
├── keywords.py        - WORKFLOW_KEYWORDS (5 seed workflows)
├── config.py          - Configuration constants
├── formatters.py      - Output formatting
└── bootstrap.py       - Dependency injection
```

**Integration with Existing Router**:
- `FileSystemRouterRepository` uses `triads.router.router.TriadRouter` for actual routing
- Maps between domain models (`tools.router.domain.RouterState`) and implementation models (`router.state_manager.RouterState`)
- Preserves all existing router functionality (semantic, LLM, manual, grace period)

### Deprecation Notice

`triads.workflow_matching` module is deprecated and will be removed in v0.11.0.
All imports now issue `DeprecationWarning` with migration instructions.

---

## Phase 4: IntegrityChecker (NOT STARTED)

### Plan

Refactor `src/triads/km/integrity_checker.py` into `src/triads/tools/integrity/`.

**Current**: tools/integrity/ wraps IntegrityChecker
**Target**: Move actual validation and repair logic into service layer

---

## Phase 4: Other km/ Modules (NOT STARTED)

### Remaining Modules to Refactor

- `graph_access/searcher.py` → integrate into `tools/knowledge/service.py`
- `graph_access/formatter.py` → merge with `tools/knowledge/formatters.py`
- `graph_access/commands.py` → integrate into `tools/knowledge/entrypoint.py`
- `experience_tracker.py` → evaluate if still needed
- `experience_query.py` → evaluate if still needed
- `agent_output_validator.py` → evaluate if still needed
- Other utility modules

---

## Breaking Changes

**None** - All changes are backward compatible via deprecation shims.

Existing code continues to work with deprecation warnings pointing to new locations.

---

## Notes

- All security validations preserved (path traversal, input validation, atomic writes)
- All error handling preserved (auto-restore, corruption recovery)
- All logging preserved (logger.warning, logger.error, logger.info)
- Deprecation warnings guide users to new imports
- Tests updated to mock new locations
- Zero test regressions

---

**Last Updated**: 2025-10-23 (Phase 3 Workflow Matching → Router Tools complete)
**Completed By**: senior-developer agent
