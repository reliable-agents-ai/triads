# Knowledge Graph Corruption Prevention System

**Status**: Production Ready (v0.9.0)

**Last Updated**: 2025-10-23

## Overview

The corruption prevention system is a comprehensive, multi-layered defense-in-depth approach to ensuring knowledge graph integrity. It protects against corruption from crashes, concurrent writes, invalid data, and agent output errors.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Agent Output Layer                         │
│  • Parse [GRAPH_UPDATE] blocks                               │
│  • Validate field syntax                                     │
│  • Reject malformed updates                                  │
└──────────────────┬──────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────────┐
│                    Schema Validation Layer                    │
│  • Validate graph structure (nodes + edges)                  │
│  • Check required fields (id, label, type)                   │
│  • Validate node types                                       │
│  • Validate confidence ranges                                │
│  • Check referential integrity                               │
└──────────────────┬──────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────────┐
│                    Backup Layer                               │
│  • Create backup before every write                          │
│  • Auto-prune old backups (configurable limit)               │
│  • Support manual restore                                    │
│  • Auto-restore on corruption detection                      │
└──────────────────┬──────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────────┐
│                    Atomic Write Layer                         │
│  • Write to temp file                                        │
│  • File locking (prevents concurrent corruption)             │
│  • Atomic rename (all-or-nothing)                            │
│  • Crash-resistant (temp file discarded on failure)          │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. Agent Output Validator (`agent_output_validator.py`)

**Purpose**: Validate `[GRAPH_UPDATE]` blocks from agent outputs BEFORE applying to graphs.

**Features**:
- Parse YAML-like `[GRAPH_UPDATE]` blocks
- Validate required fields (`node_id`, `node_type`, `label`, etc.)
- Type checking (confidence in [0.0, 1.0], valid node types)
- Integration with schema validator

**Usage**:
```python
from triads.km.agent_output_validator import AgentOutputValidator

validator = AgentOutputValidator()
blocks = validator.parse_and_validate(agent_output)
for block in blocks:
    if block.type == "add_node":
        node_data = block.to_node_dict()
        # Apply to graph
```

**Tests**: 18 tests in `test_agent_output_validation.py`

### 2. Schema Validator (`schema_validator.py`)

**Purpose**: Validate graph structure and content before saving.

**Features**:
- Validate graph structure (must have nodes and edges)
- Validate node fields (id, label, type required)
- Validate node types (concept, decision, entity, finding, task, workflow, uncertainty)
- Validate confidence values (0.0-1.0)
- Validate edge structure (source, target required)
- Check referential integrity (edges reference existing nodes)

**Usage**:
```python
from triads.km.schema_validator import validate_graph, ValidationError

try:
    validate_graph(graph_data)
    # Graph is valid
except ValidationError as e:
    print(f"Validation failed: {e.message} (field: {e.field})")
```

**Tests**: 17 tests in `test_graph_schema_validation.py`

### 3. Backup Manager (`backup_manager.py`)

**Purpose**: Automatic backup/restore for all graph writes.

**Features**:
- Create timestamped backups before writes
- Auto-prune old backups (default: keep 5)
- List available backups for a graph
- Restore from latest or specific backup
- Configurable max backups via `.backups_config.json`

**Usage**:
```python
from triads.km.backup_manager import BackupManager

backup_mgr = BackupManager(max_backups=5)

# Create backup
backup_path = backup_mgr.create_backup("design")

# List backups (newest first)
backups = backup_mgr.list_backups("design")

# Restore from latest backup
success = backup_mgr.restore_latest("design")

# Restore from specific backup
success = backup_mgr.restore_from(backup_path)
```

**Tests**: 11 tests in `test_backup_recovery.py`

### 4. Atomic File Operations (`utils/file_operations.py`)

**Purpose**: Prevent corruption from crashes and concurrent writes.

**Features**:
- Write to temp file first
- Optional file locking (prevents race conditions)
- Atomic rename (all-or-nothing)
- Preserves original on failure
- Platform-independent (POSIX + Windows)

**Usage**:
```python
from triads.utils.file_operations import atomic_write_json

# Write with locking
atomic_write_json(path, data, lock=True, indent=2)

# File is either fully written or not written at all
# Original preserved on crash/failure
```

**Tests**: 7 tests in `test_graph_atomic_writes.py`

### 5. Integrity Checker CLI (`integrity_checker.py`)

**Purpose**: Detect and repair graph corruption.

**Features**:
- Check single or all graphs
- Detect JSON parsing errors
- Detect schema violations
- Auto-repair structural issues (invalid edges)
- CLI for CI/CD integration
- Exit codes for automation

**Usage**:
```bash
# Check all graphs
triads-km check

# Check specific graph
triads-km check --triad design

# Auto-repair corrupted graphs
triads-km check --fix

# Verbose output
triads-km check --verbose
```

**Programmatic Usage**:
```python
from triads.km.integrity_checker import IntegrityChecker

checker = IntegrityChecker()

# Check single graph
result = checker.check_graph("design")
if not result.valid:
    print(f"Error: {result.error}")

# Check all graphs
results = checker.check_all_graphs()
for result in results:
    print(f"{result.triad}: {'✓' if result.valid else '✗'}")

# Repair graph
repair_result = checker.repair_graph("design")
if repair_result.success:
    print(f"Repaired: {repair_result.actions_taken}")
```

**Tests**: 20 tests in `test_integrity_checker.py`

## Integration Tests

**File**: `test_corruption_prevention_integration.py`

**Coverage**: 16 tests verifying end-to-end protection

**Test Categories**:
1. **End-to-End Write Protection** (4 tests)
   - Invalid data rejected by schema validation
   - Valid data written atomically with backup
   - Concurrent writes don't corrupt
   - Failed writes restore from backup

2. **Agent Output to Graph Pipeline** (3 tests)
   - Valid agent output accepted
   - Malformed agent output rejected
   - Invalid schema in update rejected

3. **Corruption Recovery** (4 tests)
   - Integrity checker detects corruption
   - Auto-restore from backup on corruption
   - Backup preserved during repair
   - Repair fixes structural issues

4. **Performance Under Stress** (3 tests)
   - Concurrent writes complete in reasonable time
   - Large graph writes fast
   - Backup rotation works correctly

5. **Real-World Scenarios** (2 tests)
   - Multi-triad concurrent updates
   - Recovery from system crash during write

## Performance Benchmarks

**File**: `test_corruption_prevention_performance.py`

**Coverage**: 14 tests measuring performance characteristics

**Results** (M1/M2 Mac, typical):

| Operation | Small (10 nodes) | Medium (100 nodes) | Large (1000 nodes) |
|-----------|------------------|--------------------|--------------------|
| Validation | <1ms avg | <10ms avg | <50ms avg |
| Write (baseline) | ~5ms | ~15ms | ~80ms |
| Write (protected) | ~8ms | ~25ms | ~120ms |
| **Overhead** | **~60%** | **~67%** | **~50%** |

**Acceptable Overheads**:
- Validation overhead: <10% for typical graphs
- Write overhead: <100% (first write slower due to backup, subsequent writes faster)
- Memory usage: <10MB for 1000 nodes
- Disk usage: <6x graph size (with max_backups=5)

**Concurrency**:
- 10 concurrent processes: completes in <10s
- No corruption detected
- No deadlocks

## Deployment

### Requirements

- Python 3.13+
- Dependencies: `pytest`, `coverage` (for testing)

### Installation

System is already installed as part of `triads` package:

```bash
# Verify installation
python -c "from triads.km.schema_validator import validate_graph; print('✓ Installed')"

# Verify CLI
triads-km check --help
```

### Configuration

Create `.backups_config.json` in `.claude/graphs/` to configure backup settings:

```json
{
  "max_backups": 5
}
```

**Defaults**:
- `max_backups`: 5 (keep 5 most recent backups per graph)

### Enabling Auto-Restore

To enable automatic restore from backup when loading corrupted graphs:

```python
loader = GraphLoader()
graph = loader.load_graph("design", auto_restore=True)
```

## Testing

### Run All Corruption Prevention Tests

```bash
# All 89 tests (73 unit + 16 integration)
pytest tests/test_km/test_graph_atomic_writes.py \
       tests/test_km/test_graph_schema_validation.py \
       tests/test_km/test_agent_output_validation.py \
       tests/test_km/test_backup_recovery.py \
       tests/test_km/test_integrity_checker.py \
       tests/test_km/test_corruption_prevention_integration.py \
       -v

# Performance benchmarks
pytest tests/test_km/test_corruption_prevention_performance.py -v

# Full test suite (all 1400+ tests)
pytest tests/ -v
```

### Coverage

```bash
pytest tests/test_km/ --cov=src/triads/km --cov-report=html
```

**Current Coverage**:
- `schema_validator.py`: 72%
- `agent_output_validator.py`: 55%
- `backup_manager.py`: 72%
- `integrity_checker.py`: 34% (CLI code not fully covered)
- `loader.py` (graph_access): 41%
- `file_operations.py`: 76%
- **Overall**: 88% (full project)

## Known Limitations

1. **Repair Limitations**:
   - Cannot repair invalid JSON (must restore from backup)
   - Can repair structural issues (invalid edges) only

2. **Performance**:
   - First write to graph slower (creates backup)
   - Large graphs (10,000+ nodes) may have noticeable overhead

3. **Concurrency**:
   - File locking is best-effort (some filesystems don't support flock)
   - NFS and remote filesystems may have reduced protection

4. **Backup Storage**:
   - Backups consume disk space (~5x graph size with default settings)
   - No automatic cleanup of very old backups (manual cleanup needed)

## Future Enhancements

### Short Term (v0.9.x)
- [ ] Add backup compression (gzip) to save disk space
- [ ] Add backup age-based cleanup (e.g., delete >30 days old)
- [ ] Improve CLI output formatting
- [ ] Add progress indicators for large operations

### Medium Term (v1.0.x)
- [ ] Add node field validation (custom validators per field)
- [ ] Add graph version tracking
- [ ] Add changelog for graph modifications
- [ ] Support for graph merging (conflict resolution)

### Long Term (v1.1+)
- [ ] Distributed locking for networked filesystems
- [ ] Real-time corruption monitoring
- [ ] Automatic corruption alerts
- [ ] Graph diff/patch system

## Troubleshooting

### Graph Won't Load

**Symptom**: `load_graph()` returns `None`

**Causes**:
1. File doesn't exist → Check `.claude/graphs/` directory
2. Invalid JSON → Run `triads-km check --triad <name>`
3. Schema validation failed → Check logs for ValidationError

**Solution**:
```bash
# Check integrity
triads-km check --triad design --verbose

# Restore from backup
python -c "from triads.km.graph_access import GraphLoader; loader = GraphLoader(); loader.load_graph('design', auto_restore=True)"
```

### Concurrent Writes Failing

**Symptom**: `save_graph()` returns `False` intermittently

**Causes**:
1. File locking timeout (another process writing)
2. Disk full
3. Permissions issue

**Solution**:
1. Check disk space: `df -h`
2. Check permissions: `ls -la .claude/graphs/`
3. Retry with exponential backoff

### Backup Directory Growing Large

**Symptom**: `.claude/graphs/backups/` directory using too much space

**Solution**:
```bash
# Check backup size
du -sh .claude/graphs/backups/

# Adjust max_backups in config
echo '{"max_backups": 3}' > .claude/graphs/.backups_config.json

# Manual cleanup (delete old backups)
find .claude/graphs/backups/ -name "*.json" -mtime +30 -delete
```

## Migration Guide

### From Previous Versions (< v0.9.0)

No migration needed - system is backward compatible.

**Changes**:
- `save_graph()` now creates backups automatically
- `save_graph()` now validates schema before saving
- Both changes are transparent to existing code

**Recommended**:
1. Run integrity check on all existing graphs:
   ```bash
   triads-km check --verbose
   ```

2. If corruption detected, repair:
   ```bash
   triads-km check --fix
   ```

3. Enable auto-restore in critical paths:
   ```python
   graph = loader.load_graph("design", auto_restore=True)
   ```

## Support

### Reporting Issues

If you encounter corruption despite these protections:

1. **Preserve Evidence**:
   - Don't delete corrupted file
   - Save all backups
   - Capture error messages/logs

2. **Run Diagnostics**:
   ```bash
   triads-km check --triad <name> --verbose > diagnostic.log 2>&1
   ```

3. **Report**:
   - Create GitHub issue with diagnostic log
   - Include corrupted file (if safe to share)
   - Include steps to reproduce

### Emergency Recovery

If all backups are corrupted or missing:

1. **Stop All Operations** - prevent further corruption
2. **Check Git History** - graphs may be committed
   ```bash
   git log -p .claude/graphs/<name>_graph.json
   ```

3. **Manual Reconstruction**:
   - Start with minimal valid graph: `{"nodes": [], "edges": []}`
   - Rebuild from logs/memory if needed

## References

- **Agent System Prompts**: See `.claude/agent_*.md` for graph update syntax
- **Graph Schema**: See `src/triads/km/schema_validator.py` for authoritative schema
- **ADRs**: See `docs/ADR_*.md` for design decisions
- **NetworkX Format**: https://networkx.org/documentation/stable/reference/readwrite/json_graph.html

## Changelog

### v0.9.0 (2025-10-23)
- Initial release of corruption prevention system
- 89 tests passing
- 88% code coverage
- Performance benchmarks established

---

**Maintained by**: Triads Development Team
**Last Reviewed**: 2025-10-23
