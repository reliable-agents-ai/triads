# Tool Abstraction Layer Architecture

**Status**: Production Ready (v0.10.0+)
**Last Updated**: 2025-10-23
**Confidence**: 1.0

---

## Overview

The Tool Abstraction Layer provides MCP-compliant tool interfaces following Domain-Driven Design (DDD) principles. It implements a clean architecture with strict separation of concerns across Repository, Service, Domain, and Entrypoint layers.

### Design Goals

1. **MCP Compliance**: All tools return `ToolResult` in MCP-compatible format
2. **Testability**: Edge-to-edge testing with in-memory repositories
3. **Maintainability**: Clear separation of concerns, single responsibility
4. **Reusability**: Tools used by hooks, plugins, MCP servers, and CLI
5. **Zero Regressions**: Strict TDD methodology (RED → GREEN → REFACTOR)

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                        ENTRYPOINT LAYER                           │
│  (MCP Tool Interface - Returns ToolResult)                        │
│                                                                   │
│  KnowledgeTools                                                   │
│  ├─ query_graph() → ToolResult                                   │
│  ├─ get_graph_status() → ToolResult                              │
│  ├─ show_node() → ToolResult                                     │
│  ├─ list_triads() → ToolResult                                   │
│  └─ get_session_context() → ToolResult                           │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│                        FORMATTERS LAYER                           │
│  (Converts service results to human-readable text)                │
│                                                                   │
│  format_query_result()                                            │
│  format_status_result()                                           │
│  format_node_details()                                            │
│  format_triad_list()                                              │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│                         SERVICE LAYER                             │
│  (Business Logic & Orchestration)                                 │
│                                                                   │
│  KnowledgeService                                                 │
│  ├─ query_graph() → QueryResult                                  │
│  ├─ get_graph_status() → StatusResult                            │
│  ├─ show_node() → Node                                            │
│  └─ list_triads() → List[TriadInfo]                              │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│                       REPOSITORY LAYER                            │
│  (Data Access Abstraction)                                        │
│                                                                   │
│  AbstractGraphRepository (Protocol)                               │
│  ├─ InMemoryGraphRepository (Testing)                            │
│  └─ FileSystemGraphRepository (Production)                        │
│                                                                   │
│  Wraps: triads.km.graph_access.GraphLoader                       │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│                         DOMAIN LAYER                              │
│  (Business Entities - Immutable)                                  │
│                                                                   │
│  Node (frozen dataclass)                                          │
│  Edge (frozen dataclass)                                          │
│  KnowledgeGraph                                                   │
│  └─ search() - Business logic                                    │
│  └─ validate() - Business logic                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Module Structure

### 1. Shared (`triads.tools.shared`)

Common utilities used across all tool modules.

**Files:**
- `result.py` - ToolResult dataclass (MCP-compliant)
- `exceptions.py` - ToolError base exception

**Key Types:**

```python
@dataclass(frozen=True)
class ToolResult:
    """MCP-compliant tool result."""
    success: bool
    content: List[Dict[str, str]]  # MCP content blocks
    error: Optional[str] = None

    def to_mcp(self) -> Dict:
        """Convert to MCP response format."""
        ...
```

**Content Types:**
- `text`: Text content (90% of uses)
- `resource`: File/agent generation

**Validation:**
- Content validated in `__post_init__`
- Immutable (frozen dataclass)
- Fail-fast design

---

### 2. Knowledge Tools (`triads.tools.knowledge`)

5 MCP tools for knowledge graph access.

#### Structure

```
knowledge/
├── __init__.py          # Exports KnowledgeTools
├── domain.py            # Node, Edge, KnowledgeGraph (frozen)
├── repository.py        # Abstract + implementations
├── service.py           # Business logic
├── formatters.py        # Text formatting
├── entrypoint.py        # MCP tool interface
└── bootstrap.py         # Dependency injection
```

#### Tools

1. **query_graph** - Search knowledge graphs
   ```python
   result = KnowledgeTools.query_graph(
       triad="design",
       query="OAuth",
       min_confidence=0.85
   )
   ```

2. **get_graph_status** - Health/metadata
   ```python
   result = KnowledgeTools.get_graph_status(triad="design")
   ```

3. **show_node** - Detailed node info
   ```python
   result = KnowledgeTools.show_node(
       node_id="oauth_decision",
       triad="design"
   )
   ```

4. **list_triads** - List all triads
   ```python
   result = KnowledgeTools.list_triads()
   ```

5. **get_session_context** - Full session context (for hooks)
   ```python
   result = KnowledgeTools.get_session_context(project_dir)
   ```

#### Key Decisions

**Decision: Wrap km.graph_access**
Chose to wrap existing `GraphLoader` rather than reimplemented. Maintains DRY principle.

```python
class FileSystemGraphRepository(AbstractGraphRepository):
    def __init__(self):
        self.loader = GraphLoader()  # Wrap existing

    def get(self, triad: str) -> KnowledgeGraph:
        data = self.loader.load_graph(triad)
        return self._to_domain(data)  # Transform to domain model
```

**Decision: Frozen Domain Models**
All domain entities (`Node`, `Edge`) are frozen dataclasses for immutability.

**Decision: Separate Formatters**
Presentation logic separated from business logic (SRP).

---

### 3. Integrity Tools (`triads.tools.integrity`)

3 MCP tools for graph validation and repair.

#### Structure

```
integrity/
├── domain.py            # ValidationResult, RepairResult
├── repository.py        # Backup repositories
├── service.py           # Orchestrates IntegrityChecker + Backups
├── formatters.py        # Text formatting
├── entrypoint.py        # MCP tools
└── bootstrap.py         # DI
```

#### Tools

1. **check_graph** - Validate single graph
2. **check_all_graphs** - Validate all graphs
3. **repair_graph** - Repair with optional backup

#### Key Decisions

**Decision: Wrap IntegrityChecker**
Wraps existing `triads.km.integrity_checker.IntegrityChecker` to avoid duplication.

**Decision: Backup Repository Pattern**
Separates backup operations from validation logic.

---

### 4. Router Tools (`triads.tools.router`)

2 MCP tools for semantic routing.

#### Structure

```
router/
├── domain.py            # RoutingDecision, RouterState
├── repository.py        # State persistence
├── service.py           # Routing logic
├── formatters.py        # Text formatting
├── entrypoint.py        # MCP tools
└── bootstrap.py         # DI
```

#### Tools

1. **route_prompt** - Semantic routing for user prompts
2. **get_current_triad** - Get active triad

---

### 5. Workflow Tools (`triads.tools.workflow`)

3 MCP tools for workflow state management.

#### Structure

```
workflow/
├── domain.py            # WorkflowState, PhaseInfo
├── repository.py        # State persistence
├── service.py           # Workflow logic
├── formatters.py        # Text formatting
├── entrypoint.py        # MCP tools
└── bootstrap.py         # DI
```

#### Tools

1. **get_workflow_state** - Get current workflow
2. **update_workflow_state** - Update workflow
3. **validate_workflow_step** - Validate step transition

---

### 6. Generator Tools (`triads.tools.generator`)

1 MCP tool for agent generation.

#### Structure

```
generator/
├── domain.py            # AgentDefinition, WorkflowTemplate
├── repository.py        # Template repositories
├── service.py           # Generation logic
├── entrypoint.py        # MCP tool
└── bootstrap.py         # DI
```

#### Tool

1. **generate_agents** - Generate agents from workflow template
   - Returns `resource` content type (not text)
   - One resource per agent file

---

## Design Patterns

### 1. Repository Pattern

**Purpose**: Abstract data access, enable testing

**Interface:**
```python
class AbstractGraphRepository(Protocol):
    """Repository interface for knowledge graphs."""

    def get(self, triad: str) -> KnowledgeGraph:
        """Load graph for triad."""
        ...

    def list_all(self) -> List[KnowledgeGraph]:
        """Load all graphs."""
        ...
```

**Implementations:**
- `InMemoryGraphRepository` - For testing
- `FileSystemGraphRepository` - For production

**Benefits:**
- Edge-to-edge testing without file I/O
- Swap implementations without changing business logic
- Mock data for tests

### 2. Service Layer Pattern

**Purpose**: Business logic and orchestration

**Responsibilities:**
- Coordinate repositories
- Implement business rules
- Return domain objects

**Example:**
```python
class KnowledgeService:
    def __init__(self, repository: AbstractGraphRepository):
        self.repository = repository

    def query_graph(
        self,
        triad: str,
        query: str,
        min_confidence: float
    ) -> QueryResult:
        # Load graph
        graph = self.repository.get(triad)

        # Apply business logic
        nodes = graph.search(query, min_confidence)

        # Return domain result
        return QueryResult(
            triad=triad,
            query=query,
            nodes=nodes,
            total=len(nodes)
        )
```

### 3. Dependency Injection

**Purpose**: Decouple components, enable testing

**Bootstrap Function:**
```python
def bootstrap_knowledge_service() -> KnowledgeService:
    """Create KnowledgeService with dependencies."""
    if os.getenv("TEST_MODE"):
        repo = InMemoryGraphRepository()
    else:
        repo = FileSystemGraphRepository()

    return KnowledgeService(repository=repo)
```

**Usage in Entrypoint:**
```python
class KnowledgeTools:
    @staticmethod
    def query_graph(...) -> ToolResult:
        service = bootstrap_knowledge_service()
        result = service.query_graph(...)
        ...
```

**Testing:**
```python
def test_query_graph():
    # Inject test repository
    repo = InMemoryGraphRepository()
    repo.graphs["test"] = create_test_graph()

    service = KnowledgeService(repository=repo)
    result = service.query_graph("test", "OAuth", 0.0)

    assert len(result.nodes) == 2
```

### 4. Wrapper Pattern

**Purpose**: Reuse existing code, avoid duplication

**Example:**
```python
class FileSystemGraphRepository:
    def __init__(self):
        # Wrap existing production-tested loader
        self.loader = GraphLoader()

    def get(self, triad: str) -> KnowledgeGraph:
        # Load using existing logic
        data = self.loader.load_graph(triad)

        # Transform to domain model
        return self._to_domain(data)
```

**Benefits:**
- Don't Repeat Yourself (DRY)
- Single source of truth
- Leverage battle-tested code

---

## Testing Strategy

### RED-GREEN-REFACTOR Methodology

All tools implemented using strict TDD:

1. **RED**: Write failing test first
2. **GREEN**: Implement minimum code to pass
3. **REFACTOR**: Improve code quality

### Edge-to-Edge Testing

Test complete flow from entrypoint to repository:

```python
def test_query_graph_edge_to_edge(seeded_repo):
    """Test complete flow with in-memory repository."""
    # Patch bootstrap to return test service
    with patch('module.bootstrap', return_value=test_service):
        # Call entrypoint (full stack)
        result = KnowledgeTools.query_graph("test", "OAuth", 0.0)

        # Verify MCP-compliant result
        assert result.success
        assert result.content[0]["type"] == "text"
        assert "OAuth" in result.content[0]["text"]
```

### Test Organization

```
tests/test_tools/
├── test_shared/
│   └── test_result.py       # ToolResult tests
├── test_knowledge/
│   ├── conftest.py          # Shared fixtures
│   ├── test_domain.py       # Domain model tests
│   ├── test_repository.py   # Repository tests
│   ├── test_service.py      # Service tests
│   ├── test_formatters.py   # Formatter tests
│   └── test_entrypoint.py   # Edge-to-edge tests
├── test_integrity/
│   └── ...                  # Similar structure
├── test_integration/
│   └── test_hooks.py        # Hook integration
└── test_plugin/
    └── test_command_integration.py  # Plugin integration
```

### Coverage Requirements

- **Minimum**: 90% coverage
- **Achieved**: 95%+ across all modules
- **Exclusions**: Bootstrap files (trivial DI logic)

---

## Adding New Tools

### Step 1: Define Domain Models

```python
# domain.py
from dataclasses import dataclass

@dataclass(frozen=True)
class MyEntity:
    """Domain entity (immutable)."""
    id: str
    name: str
    confidence: float
```

### Step 2: Create Repository Interface

```python
# repository.py
from typing import Protocol, List

class AbstractMyRepository(Protocol):
    """Repository interface."""

    def get(self, id: str) -> MyEntity:
        """Get entity by ID."""
        ...

    def list_all(self) -> List[MyEntity]:
        """List all entities."""
        ...


class InMemoryMyRepository:
    """Test implementation."""
    def __init__(self):
        self.entities = {}

    def get(self, id: str) -> MyEntity:
        if id not in self.entities:
            raise ValueError(f"Entity {id} not found")
        return self.entities[id]

    def list_all(self) -> List[MyEntity]:
        return list(self.entities.values())


class FileSystemMyRepository:
    """Production implementation."""
    def get(self, id: str) -> MyEntity:
        # Load from filesystem
        # OR wrap existing module
        ...
```

### Step 3: Implement Service

```python
# service.py
@dataclass
class MyResult:
    """Service layer result."""
    entity: MyEntity
    metadata: dict


class MyService:
    """Business logic."""

    def __init__(self, repository: AbstractMyRepository):
        self.repository = repository

    def process(self, id: str) -> MyResult:
        """Business logic method."""
        entity = self.repository.get(id)

        # Apply business rules
        ...

        return MyResult(entity=entity, metadata={...})
```

### Step 4: Create Formatters

```python
# formatters.py
def format_my_result(result: MyResult) -> str:
    """Format result as human-readable text."""
    lines = []
    lines.append(f"Entity: {result.entity.name}")
    lines.append(f"Confidence: {result.entity.confidence:.2f}")
    ...
    return "\n".join(lines)
```

### Step 5: Implement Entrypoint

```python
# entrypoint.py
from triads.tools.shared import ToolResult
from .bootstrap import bootstrap_my_service
from .formatters import format_my_result


class MyTools:
    """MCP tool entrypoints."""

    @staticmethod
    def my_tool(id: str) -> ToolResult:
        """MCP Tool: my_tool

        Args:
            id: Entity ID

        Returns:
            ToolResult with formatted entity details
        """
        service = bootstrap_my_service()

        try:
            result = service.process(id)
            formatted = format_my_result(result)

            return ToolResult(
                success=True,
                content=[{"type": "text", "text": formatted}]
            )

        except Exception as e:
            return ToolResult(
                success=False,
                content=[],
                error=str(e)
            )
```

### Step 6: Create Bootstrap

```python
# bootstrap.py
import os
from .service import MyService
from .repository import InMemoryMyRepository, FileSystemMyRepository


def bootstrap_my_service() -> MyService:
    """Create MyService with dependencies."""
    if os.getenv("TEST_MODE"):
        repo = InMemoryMyRepository()
    else:
        repo = FileSystemMyRepository()

    return MyService(repository=repo)
```

### Step 7: Write Tests (TDD)

```python
# tests/test_my_tool/test_entrypoint.py
from triads.tools.my_tool import MyTools


def test_my_tool_returns_mcp_compliant_result():
    """Test tool returns ToolResult."""
    result = MyTools.my_tool("test_id")

    assert hasattr(result, 'success')
    assert hasattr(result, 'content')
    assert hasattr(result, 'error')


def test_my_tool_edge_to_edge(seeded_repo):
    """Test complete flow."""
    # Patch bootstrap
    with patch('module.bootstrap', return_value=test_service):
        result = MyTools.my_tool("test_id")

        assert result.success
        assert result.content[0]["type"] == "text"
        assert "expected text" in result.content[0]["text"]
```

---

## Best Practices

### 1. Immutable Domain Models

✅ **DO:**
```python
@dataclass(frozen=True)
class Node:
    id: str
    label: str
```

❌ **DON'T:**
```python
@dataclass
class Node:
    id: str
    label: str
```

**Rationale**: Prevents bugs from accidental modification. Domain models are value objects.

### 2. Wrap, Don't Duplicate

✅ **DO:**
```python
class FileSystemRepo:
    def __init__(self):
        self.loader = GraphLoader()  # Reuse existing

    def get(self, triad: str):
        data = self.loader.load_graph(triad)
        return self._to_domain(data)
```

❌ **DON'T:**
```python
class FileSystemRepo:
    def get(self, triad: str):
        # Reimplementing graph loading logic
        with open(f"{triad}_graph.json") as f:
            ...
```

**Rationale**: Single source of truth, avoid divergence.

### 3. Fail Fast

✅ **DO:**
```python
@dataclass(frozen=True)
class ToolResult:
    content: List[Dict]

    def __post_init__(self):
        if not self.content:
            raise ToolError("Content cannot be empty")

        for item in self.content:
            if "type" not in item:
                raise ToolError("Content must have 'type' field")
```

❌ **DON'T:**
```python
# Validate lazily at use time
def to_mcp(self):
    if not self.content:
        raise ToolError(...)
```

**Rationale**: Catch errors immediately at creation time.

### 4. Test at Multiple Levels

✅ **DO:**
```
tests/
├── test_domain.py       # Domain logic
├── test_repository.py   # Data access
├── test_service.py      # Business logic
└── test_entrypoint.py   # Edge-to-edge
```

❌ **DON'T:**
```
tests/
└── test_entrypoint.py   # Only integration tests
```

**Rationale**: Pinpoint failures quickly, test each layer independently.

---

## Metrics

### Code Reduction

**Before** (embedded logic in hooks/modules):
- hooks/session_start.py: 625 lines
- hooks/user_prompt_submit.py: 261 lines
- hooks/on_stop.py: 1304 lines
- **Total**: ~2190 lines

**After** (using tools):
- hooks/session_start.py: 53 lines
- hooks/user_prompt_submit.py: 109 lines
- hooks/common.py: 85 lines
- **Total**: ~250 lines

**Reduction**: 89% fewer lines

### Test Coverage

- **Total Tests**: 1587 (up from 1568 before tools)
- **Tool Tests**: 168 tests (11% of total)
- **Coverage**: 95%+ across tool modules
- **Zero Regressions**: All existing tests still pass

### Performance

- **session_start hook**: <100ms (was ~300ms with embedded logic)
- **query_graph tool**: ~10-50ms depending on graph size
- **get_session_context**: ~80ms for all graphs

---

## Migration Guide

### From km.graph_access to KnowledgeTools

**Before:**
```python
from triads.km.graph_access import search_knowledge

results = search_knowledge("OAuth", triad="design", min_confidence=0.85)
# Returns: List[dict]
```

**After:**
```python
from triads.tools.knowledge import KnowledgeTools

result = KnowledgeTools.query_graph(
    triad="design",
    query="OAuth",
    min_confidence=0.85
)
# Returns: ToolResult (MCP-compliant)
# Access: result.content[0]["text"]
```

### From Direct Graph Loading to Tools

**Before:**
```python
from triads.km.graph_access.loader import GraphLoader

loader = GraphLoader()
graph_data = loader.load_graph("design")
# Process raw JSON
```

**After:**
```python
from triads.tools.knowledge import KnowledgeTools

result = KnowledgeTools.get_graph_status(triad="design")
# Returns formatted status
```

### Backward Compatibility

`km.graph_access` module still works (not deprecated yet). Migration is optional but recommended for new code.

---

## Troubleshooting

### Issue: "Module not found: triads.tools"

**Solution**: Ensure you've installed from the correct directory:
```bash
pip install -e .
```

### Issue: Test fails with "Cannot mock bootstrap"

**Solution**: Patch at module level, not import level:
```python
# ❌ Wrong
with patch('entrypoint.bootstrap_service'):
    ...

# ✅ Correct
with patch('triads.tools.knowledge.bootstrap.bootstrap_knowledge_service'):
    ...
```

### Issue: "FileSystemRepository failed"

**Solution**: Check `.claude/graphs/` directory exists:
```bash
mkdir -p .claude/graphs
```

---

## References

- **MCP Specification**: https://modelcontextprotocol.io/
- **ADR-TOOL-ARCHITECTURE**: `.claude/graphs/design_graph.json`
- **Implementation Graph**: `.claude/graphs/implementation_graph.json`
- **Test Reports**: `tests/test_tools/`

---

## Contributors

- senior-developer (implementation)
- test-engineer (quality gates)
- design-bridge (ADR documentation)

---

**Document Version**: 1.0
**Architecture Version**: v0.10.0+
**Status**: Production Ready
