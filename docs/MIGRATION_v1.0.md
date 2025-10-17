# Migration Guide: v0.7 → v1.0

## Overview

Version 0.7.0 introduces a new, domain-agnostic workflow enforcement system. The legacy hardcoded system (validator.py and enforcement.py) is now deprecated and will be removed in v1.0.0.

This guide helps you migrate from the legacy system to the new schema-driven system.

---

## Deprecated Modules

The following modules are deprecated in v0.7 and will be removed in v1.0:

### validator.py → validator_new.py

**Old** (validator.py):
- Hardcoded triad names ("idea-validation", "design", etc.)
- Hardcoded workflow sequence
- Code-centric metrics (LoC, files changed)
- Git-specific implementation

**New** (validator_new.py):
- Schema-driven validation
- Works with ANY workflow defined in JSON/YAML
- Domain-agnostic metrics via MetricsProvider interface
- Pluggable metrics providers

**Migration Example**:

```python
# Before (v0.6 - v0.7)
from triads.workflow_enforcement.validator import WorkflowValidator

validator = WorkflowValidator()
metrics = validator.calculate_metrics()

if validator.requires_garden_tending(metrics):
    print("Garden Tending required")

# After (v0.7+)
from triads.workflow_enforcement.validator_new import WorkflowValidator
from triads.workflow_enforcement.schema_loader import WorkflowSchemaLoader
from triads.workflow_enforcement.triad_discovery import TriadDiscovery
from triads.workflow_enforcement.metrics import CodeMetricsProvider

# Load workflow schema
schema_loader = WorkflowSchemaLoader()
schema = schema_loader.load_schema()

# Discover available triads
discovery = TriadDiscovery()

# Create validator
validator = WorkflowValidator(schema, discovery)

# Calculate metrics
metrics_provider = CodeMetricsProvider()
metrics = metrics_provider.calculate_metrics({"base_ref": "HEAD~1"})

# Validate transition
validation = validator.validate_transition(
    instance_id="my-workflow",
    target_triad_id="deployment",
    metrics=metrics
)

if not validation.valid:
    print(f"Validation failed: {validation.violations}")
```

---

### enforcement.py → enforcement_new.py

**Old** (enforcement.py):
- Hardcoded enforcement logic
- Single enforcement mode (blocking)
- Exits with sys.exit(1) on failure

**New** (enforcement_new.py):
- Schema-driven enforcement
- Three enforcement modes:
  - `strict`: Block with exception
  - `recommended`: Warn but allow
  - `optional`: Silent validation
- Per-triad overrides
- Returns EnforcementResult (no sys.exit)

**Migration Example**:

```python
# Before (v0.6 - v0.7)
from triads.workflow_enforcement.enforcement import BlockingEnforcement, WorkflowBlockedError

enforcer = BlockingEnforcement(validator, state_manager)

try:
    enforcer.enforce_deployment()
    print("Deployment allowed")
except WorkflowBlockedError as e:
    print(f"Blocked: {e}")

# After (v0.7+)
from triads.workflow_enforcement.enforcement_new import WorkflowEnforcer

# Create enforcer
enforcer = WorkflowEnforcer(
    schema_loader=schema_loader,
    instance_manager=instance_manager,
    discovery=discovery,
    metrics_provider=metrics_provider
)

# Enforce transition
result = enforcer.enforce(
    instance_id="my-workflow",
    target_triad_id="deployment"
)

if result.allowed:
    print("Deployment allowed")
else:
    print(f"Blocked: {result.message}")
    print(f"Violations: {result.violations}")
```

---

## Key Differences

### 1. Schema-Driven vs. Hardcoded

**Old**: Workflow sequence hardcoded in Python:
```python
VALID_TRANSITIONS = {
    None: {"idea-validation"},
    "idea-validation": {"design"},
    "design": {"implementation"},
    # ...
}
```

**New**: Workflow defined in schema:
```yaml
# .claude/workflow_schema.yml
workflow:
  triads:
    - id: idea-validation
      next: [design]
    - id: design
      next: [implementation]
```

### 2. Metrics Providers

**Old**: Git diff hardcoded:
```python
validator.calculate_metrics()  # Always uses git
```

**New**: Pluggable metrics providers:
```python
# Use code metrics
code_metrics = CodeMetricsProvider()
metrics = code_metrics.calculate_metrics({"base_ref": "HEAD~1"})

# Or create custom metrics provider
class CustomMetricsProvider(MetricsProvider):
    @property
    def domain(self) -> str:
        return "custom"
    
    def calculate_metrics(self, context):
        # Custom logic
        return MetricsResult(...)
```

### 3. Enforcement Modes

**Old**: Only blocking enforcement:
```python
enforcer.enforce_deployment()  # Always blocks or passes
```

**New**: Three enforcement modes:
```python
# Strict: Block with exception
enforcer.enforce(instance_id, triad_id)

# Recommended: Warn but allow
result = enforcer.enforce(instance_id, triad_id)
if result.enforcement_level == "recommended":
    print(f"Warning: {result.message}")
    # Continue anyway

# Optional: Silent validation
result = enforcer.enforce(instance_id, triad_id)
if result.enforcement_level == "optional":
    # Just log, no warning
    pass
```

---

## Migration Checklist

- [ ] **Update imports** from `validator` to `validator_new`
- [ ] **Update imports** from `enforcement` to `enforcement_new`
- [ ] **Create workflow schema** if using custom workflow (`.claude/workflow_schema.yml`)
- [ ] **Replace `calculate_metrics()`** with metrics provider
- [ ] **Replace `requires_garden_tending()`** with `validate_transition()`
- [ ] **Replace `enforce_deployment()`** with `enforce()`
- [ ] **Handle `EnforcementResult`** instead of exception-based flow
- [ ] **Update tests** to mock new interfaces
- [ ] **Remove sys.exit() handling** (enforcer returns result, doesn't exit)

---

## Timeline

- **v0.7.0** (Current): Legacy modules deprecated, warnings added
- **v0.8.0-0.9.0**: Migration period, both systems work
- **v1.0.0**: Legacy modules removed

---

## Need Help?

- **Documentation**: [docs/WORKFLOW_ENFORCEMENT_PROPOSED.md](./WORKFLOW_ENFORCEMENT_PROPOSED.md)
- **Examples**: [examples/workflow_enforcement/](../examples/workflow_enforcement/)
- **Issues**: https://github.com/reliable-agents-ai/triads/issues

---

## Benefits of New System

1. **Domain-agnostic**: Works for any workflow, not just code workflows
2. **Flexible**: Schema-driven, easily customizable
3. **Testable**: Clear interfaces, easy to mock
4. **Extensible**: Plugin architecture for metrics providers
5. **No side effects**: Returns results instead of sys.exit()
6. **Better error messages**: Structured violations with remediation steps

---

## Common Pitfalls

### Pitfall 1: Forgetting to load schema

```python
# ❌ BAD: Validator without schema
validator = WorkflowValidator(None, discovery)  # Will fail

# ✅ GOOD: Load schema first
schema_loader = WorkflowSchemaLoader()
schema = schema_loader.load_schema()
validator = WorkflowValidator(schema, discovery)
```

### Pitfall 2: Using old metrics format

```python
# ❌ BAD: Old metrics dict
metrics = {
    "loc_changed": 150,
    "files_changed": 8,
    "has_new_features": True
}

# ✅ GOOD: MetricsResult object
from triads.workflow_enforcement.metrics import MetricsResult

metrics = MetricsResult(
    content_created={"type": "code", "quantity": 150, "units": "lines"},
    components_modified=8,
    complexity="substantial"
)
```

### Pitfall 3: Expecting sys.exit()

```python
# ❌ BAD: Expecting exception/exit
try:
    enforcer.enforce(instance_id, triad_id)
    # Continues here even if validation failed
except Exception:
    # Never called in new system
    pass

# ✅ GOOD: Check result
result = enforcer.enforce(instance_id, triad_id)
if not result.allowed:
    print(f"Failed: {result.message}")
    # Handle failure appropriately
```

---

## Questions?

If you have questions about migration, please:
1. Check the [documentation](./WORKFLOW_ENFORCEMENT_PROPOSED.md)
2. Look at [examples](../examples/workflow_enforcement/)
3. Open an issue on GitHub

We're here to help make migration smooth!
