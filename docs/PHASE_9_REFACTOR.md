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

## Phase 2: IntegrityChecker (NOT STARTED)

### Plan

Refactor `src/triads/km/integrity_checker.py` into `src/triads/tools/integrity/`.

**Current**: tools/integrity/ wraps IntegrityChecker
**Target**: Move actual validation and repair logic into service layer

---

## Phase 3: Other km/ Modules (NOT STARTED)

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

**Last Updated**: 2025-10-23
**Completed By**: senior-developer agent
