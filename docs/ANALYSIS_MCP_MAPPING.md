# Triads → MCP Server Mapping Analysis

**Date**: 2025-10-23
**Author**: Claude Code (Supervisor)
**Purpose**: Assess feasibility of mapping Triads capabilities to MCP server architecture

---

## Executive Summary

**TL;DR**: Triads could partially map to MCP, but **should not be forced into full MCP compliance** at this stage. Instead, we should:

1. ✅ **Abstract capabilities into "tool-like" interfaces** (your intuition is correct)
2. ✅ **Keep agent definitions and hooks local** (your concern is valid)
3. ✅ **Create an MCP-compatible layer** for specific capabilities
4. ❌ **Don't try to be a full MCP server** (architectural mismatch)

**Recommendation**: **Hybrid approach** - MCP-inspired abstraction with local execution

---

## Part 1: What Triads IS vs What MCP Expects

### Triads Architecture (Current State)

```
┌─────────────────────────────────────────────────────┐
│  Triads Plugin (Claude Code)                        │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │ Agent System │  │  KM System   │  │  Routing  │ │
│  │ (.md files)  │  │  (graphs)    │  │  (logic)  │ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
│                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │ Hook System  │  │  Workflows   │  │ Templates │ │
│  │ (Python)     │  │  (enforce)   │  │ (agent)   │ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
│                                                      │
│  All runs INSIDE Claude Code process                │
│  Deeply integrated with Task tool                   │
│  Stateful (knowledge graphs, routing state)         │
└─────────────────────────────────────────────────────┘
```

### MCP Server Architecture (Expected)

```
┌─────────────┐              ┌─────────────┐
│   Client    │              │ MCP Server  │
│  (Claude)   │◄────JSON────►│  (Triads)   │
└─────────────┘   RPC        └─────────────┘
                               │
                               ▼
                         ┌──────────┐
                         │   Data   │
                         │  Source  │
                         └──────────┘

- Stateless request/response
- Discovery via tools/list
- Simple JSON-RPC protocol
- Server runs OUTSIDE client
- Client has no knowledge of server internals
```

### Key Architectural Differences

| Aspect | Triads Current | MCP Expectation |
|--------|---------------|-----------------|
| **Execution** | Inside Claude Code (plugin) | Outside (separate process) |
| **State** | Stateful (graphs, routing) | Stateless (or server-managed) |
| **Integration** | Deep (hooks, Task tool) | Shallow (JSON-RPC) |
| **Discovery** | Compile-time (agent files) | Runtime (tools/list) |
| **Agent Definitions** | Local (.md files) | Would need to be remote |
| **Context** | Session-aware | Request-scoped |

---

## Part 2: Why Full MCP Mapping Doesn't Fit

### Problem 1: Agent Definitions Must Stay Local

**Your intuition is correct**: Claude needs agent definitions locally.

**Why?**
```python
# Agent file: .claude/agents/design/solution-architect.md
---
name: solution-architect
tools: Read, Grep, Glob, Write
description: Design technical solutions...
---

# This prompt content is what Task tool receives
# Claude Code loads this BEFORE invoking the agent
# Can't be remote without changing Claude Code's Task tool
```

**MCP would require**: Agent definitions transmitted via JSON-RPC
**Reality**: Claude Code's Task tool expects local `.md` files

**Verdict**: ❌ **Incompatible** - Can't move agent definitions to remote server

---

### Problem 2: Hooks Must Stay Local

**Your concern is valid**: Hooks are deeply integrated with Claude Code's lifecycle.

**Current Hook Integration**:
```
Session Start → session_start.py (injects routing context)
     ↓
User Input → user_prompt_submit.py (supervisor mode)
     ↓
Pre-Tool-Use → on_pre_experience_injection.py (inject knowledge)
     ↓
Session End → on_stop.py (save experience)
```

**MCP would require**: Hooks as remote "tools" that Claude calls
**Reality**: Hooks are lifecycle callbacks that Claude Code invokes automatically

**Verdict**: ❌ **Incompatible** - Hooks are event-driven, not request-driven

---

### Problem 3: Stateful Knowledge Graphs

**Triads KM System**:
```json
// .claude/graphs/design_graph.json
{
  "nodes": [...],
  "edges": [...],
  "updated_at": "2025-10-23T13:47:35"
}

// State persists across sessions
// Hooks inject relevant knowledge before tool use
// Agents update graphs during execution
```

**MCP Model**:
- Server maintains state OR client maintains state
- Each request is independent
- No automatic context injection

**Verdict**: ⚠️ **Partial** - Could work but loses automatic injection

---

### Problem 4: Triad Atomicity Principle

**Core Triads Concept** (ADR-006):
> Triads are ATOMIC units that never get decomposed

**MCP Model**:
- Tools are individual, discoverable capabilities
- Each tool is independently invocable
- No concept of "tool groups that must work together"

**Example**:
```
Design Triad = validation-synthesizer → solution-architect → design-bridge

In MCP, these would be 3 separate tools:
- validate_requirements
- design_solution
- bridge_to_implementation

But Triads says: You can't call solution-architect without validation-synthesizer!
```

**Verdict**: ❌ **Architectural mismatch** - MCP encourages granular tools, Triads requires composite workflows

---

## Part 3: What COULD Map to MCP

Despite the architectural mismatches, some Triads capabilities align well with MCP's tool model:

### ✅ Good Candidates for MCP-Style Tools

#### 1. Knowledge Management Operations

```python
# These are stateless queries - perfect for MCP tools

Tool: "query_knowledge_graph"
Input: { "triad": "design", "query": "checklists" }
Output: [ /* checklist nodes */ ]

Tool: "search_knowledge"
Input: { "triad": "deployment", "keywords": ["version", "bump"] }
Output: [ /* relevant nodes */ ]

Tool: "get_node_details"
Input: { "node_id": "process_version_bump_checklist_2025-10-17" }
Output: { /* full node with checklist items */ }
```

**Why it works**:
- Read-only operations
- Stateless (just querying existing data)
- Clear input/output contracts
- Independent of agent execution

---

#### 2. Integrity Checker Operations

```python
# CLI tools we already built - map naturally to MCP

Tool: "check_graph_integrity"
Input: { "triad": "design" }
Output: {
  "valid": true,
  "issues": [],
  "node_count": 31
}

Tool: "repair_graph"
Input: { "triad": "deployment", "backup": "20251023_142530" }
Output: {
  "success": true,
  "nodes_removed": 2,
  "backup_created": true
}

Tool: "list_backups"
Input: { "triad": "implementation" }
Output: [
  { "timestamp": "20251023_142530", "size": "12KB" },
  ...
]
```

**Why it works**:
- These are already CLI commands (`triads-km check`)
- Side-effect operations with clear results
- Independent of agent execution
- Could run remotely

---

#### 3. Router/Workflow Queries

```python
# Read-only routing information - good MCP candidates

Tool: "get_routing_status"
Input: {}
Output: {
  "current_triad": "design",
  "confidence": 0.95,
  "training_mode": true
}

Tool: "suggest_workflow"
Input: { "task_description": "Fix bug in router crash" }
Output: {
  "suggested_workflow": "bug-fix",
  "confidence": 0.87,
  "triads": ["investigation", "fixing", "verification"]
}

Tool: "list_available_triads"
Input: {}
Output: [
  { "name": "design", "agents": 3, "description": "..." },
  { "name": "implementation", "agents": 3, "description": "..." }
]
```

**Why it works**:
- Read-only metadata
- Useful for external tools to understand Triads state
- No execution required

---

#### 4. Workflow Enforcement Queries

```python
# Compliance checking - stateless reads

Tool: "check_deployment_readiness"
Input: {}
Output: {
  "ready": false,
  "blockers": [
    "Garden Tending required (technical debt > threshold)"
  ],
  "metrics": {
    "implementation_lines": 2500,
    "test_coverage": 0.88
  }
}

Tool: "get_workflow_state"
Input: {}
Output: {
  "current_instance": "workflow_20251023_134530",
  "triads_completed": ["design", "implementation"],
  "triads_remaining": ["garden-tending", "deployment"]
}
```

**Why it works**:
- Read-only state queries
- Useful for external monitoring
- Clear compliance checks

---

### ❌ Poor Candidates for MCP Tools

These should **NOT** be exposed as MCP tools:

#### 1. Agent Invocation

```python
# BAD: Don't expose this as MCP tool
Tool: "invoke_agent"
Input: { "agent": "solution-architect", "task": "..." }

Why bad:
- Requires local agent definitions
- Breaks triad atomicity (can't invoke agents individually)
- Complex state management (knowledge graph updates mid-execution)
- Deep Claude Code integration via Task tool
```

#### 2. Hook Execution

```python
# BAD: Hooks are lifecycle events, not tools
Tool: "run_pre_tool_use_hook"
Input: { "tool_name": "Write", "file": "foo.py" }

Why bad:
- Hooks fire automatically based on lifecycle
- Not request-driven
- Require Claude Code integration
- State changes (graph updates, experience tracking)
```

#### 3. Triad Workflows

```python
# BAD: Workflows are compositions, not atomic tools
Tool: "run_design_workflow"
Input: { "requirements": "..." }

Why bad:
- Multi-step process (3 agents sequentially)
- State changes at each step
- Knowledge graph updates throughout
- Requires triad atomicity preservation
```

---

## Part 4: Recommended Hybrid Approach

### Strategy: MCP-Inspired Abstraction, Not Full MCP Compliance

```
┌───────────────────────────────────────────────────────┐
│  Triads Plugin (Local to Claude Code)                 │
├───────────────────────────────────────────────────────┤
│                                                        │
│  ┌─────────────────────────────────────────────────┐  │
│  │  Agent System (stays local)                     │  │
│  │  - .md agent definitions                        │  │
│  │  - Task tool integration                        │  │
│  │  - Triad atomicity preserved                    │  │
│  └─────────────────────────────────────────────────┘  │
│                                                        │
│  ┌─────────────────────────────────────────────────┐  │
│  │  Hook System (stays local)                      │  │
│  │  - Lifecycle integration                        │  │
│  │  - Automatic context injection                  │  │
│  └─────────────────────────────────────────────────┘  │
│                                                        │
│  ┌─────────────────────────────────────────────────┐  │
│  │  Abstraction Layer (NEW - MCP-inspired)         │  │
│  │  ┌───────────────────────────────────────────┐  │  │
│  │  │  Tool Interface (MCP-compatible)          │  │  │
│  │  │  - query_knowledge()                      │  │  │
│  │  │  - check_integrity()                      │  │  │
│  │  │  - get_routing_status()                   │  │  │
│  │  │  - suggest_workflow()                     │  │  │
│  │  └───────────────────────────────────────────┘  │  │
│  │                                                   │  │
│  │  ┌───────────────────────────────────────────┐  │  │
│  │  │  Implementation (delegates to modules)    │  │  │
│  │  │  - km.graph_access.*                      │  │  │
│  │  │  - km.integrity_checker                   │  │  │
│  │  │  - router.*                                │  │  │
│  │  │  - workflow_enforcement.*                  │  │  │
│  │  └───────────────────────────────────────────┘  │  │
│  └─────────────────────────────────────────────────┘  │
│                                                        │
└───────────────────────────────────────────────────────┘

Optional Future: MCP Server Wrapper
┌─────────────────────────────────────┐
│  MCP Server (external process)      │
│  - Exposes abstraction layer        │
│  - JSON-RPC protocol                 │
│  - For external tools only           │
│  - Triads plugin still works local   │
└─────────────────────────────────────┘
```

---

## Part 5: Concrete Implementation Plan

### Phase 1: Create Tool Abstraction Layer (Internal)

**Goal**: Abstract capabilities into "tool-like" interfaces without MCP dependency

**File**: `src/triads/tools/__init__.py`

```python
"""
Triads Tool Abstraction Layer

MCP-inspired but not MCP-compliant. Provides clean interfaces
for Triads capabilities that could later be exposed via MCP if desired.
"""

from dataclasses import dataclass
from typing import Any, Dict, List

@dataclass
class ToolResult:
    """Standard result format (MCP-inspired)"""
    success: bool
    content: List[Dict[str, Any]]  # MCP content format
    error: str | None = None

class KnowledgeTools:
    """Knowledge management operations"""

    @staticmethod
    def query_graph(triad: str, query: str) -> ToolResult:
        """Query knowledge graph (MCP-compatible)"""
        from triads.km.graph_access import search_knowledge
        results = search_knowledge(query, triad=triad)
        return ToolResult(
            success=True,
            content=[{"type": "text", "text": results}]
        )

    @staticmethod
    def get_node(node_id: str, triad: str | None = None) -> ToolResult:
        """Get node details (MCP-compatible)"""
        from triads.km.graph_access import show_node
        node = show_node(node_id, triad=triad)
        return ToolResult(
            success=True,
            content=[{"type": "text", "text": node}]
        )

class IntegrityTools:
    """Graph integrity operations"""

    @staticmethod
    def check_graph(triad: str) -> ToolResult:
        """Check graph integrity (MCP-compatible)"""
        from triads.km.integrity_checker import IntegrityChecker
        checker = IntegrityChecker()
        result = checker.check_graph(triad)
        return ToolResult(
            success=result.valid,
            content=[{
                "type": "text",
                "text": f"{result.node_count} nodes, {len(result.issues)} issues"
            }]
        )

class RouterTools:
    """Routing and workflow operations"""

    @staticmethod
    def get_status() -> ToolResult:
        """Get routing status (MCP-compatible)"""
        from triads.router import get_current_state
        state = get_current_state()
        return ToolResult(
            success=True,
            content=[{
                "type": "text",
                "text": f"Current triad: {state.current_triad}"
            }]
        )
```

**Benefits**:
- ✅ Clean interfaces (easier to test, maintain)
- ✅ MCP-compatible result format (future-proof)
- ✅ Decouples capabilities from implementation
- ✅ No external dependencies (stays in plugin)
- ✅ Could expose via MCP later if desired

---

### Phase 2: Refactor Existing Code to Use Tools

**Goal**: Replace direct module calls with tool interfaces

**Before**:
```python
# Agent or hook calling module directly
from triads.km.graph_access import search_knowledge
results = search_knowledge("checklist", triad="deployment")
```

**After**:
```python
# Agent or hook using tool interface
from triads.tools import KnowledgeTools
result = KnowledgeTools.query_graph("deployment", "checklist")
content = result.content[0]["text"]
```

**Benefits**:
- ✅ Consistent API across codebase
- ✅ Easier to add new capabilities
- ✅ Better error handling
- ✅ Logging/telemetry at tool boundary
- ✅ Testing via tool mocks

---

### Phase 3: Add Tool Registry (Optional)

**Goal**: Dynamic tool discovery (MCP-style but internal)

**File**: `src/triads/tools/registry.py`

```python
"""
Tool Registry - MCP-inspired discovery

Allows internal and external discovery of available tools.
Could power MCP server in future or remain internal-only.
"""

from typing import Dict, List, Callable
from dataclasses import dataclass

@dataclass
class ToolDefinition:
    """MCP-compatible tool definition"""
    name: str
    description: str
    input_schema: Dict  # JSON Schema
    category: str  # "knowledge", "integrity", "routing"

class ToolRegistry:
    """Centralized tool registry"""

    _tools: Dict[str, Callable] = {}
    _definitions: Dict[str, ToolDefinition] = {}

    @classmethod
    def register(cls, definition: ToolDefinition):
        """Register a tool (decorator pattern)"""
        def decorator(func: Callable):
            cls._tools[definition.name] = func
            cls._definitions[definition.name] = definition
            return func
        return decorator

    @classmethod
    def list_tools(cls, category: str | None = None) -> List[ToolDefinition]:
        """List available tools (MCP-style discovery)"""
        if category:
            return [d for d in cls._definitions.values() if d.category == category]
        return list(cls._definitions.values())

    @classmethod
    def call_tool(cls, name: str, **kwargs) -> ToolResult:
        """Invoke a tool by name"""
        if name not in cls._tools:
            return ToolResult(success=False, error=f"Tool {name} not found", content=[])
        return cls._tools[name](**kwargs)

# Usage:
@ToolRegistry.register(ToolDefinition(
    name="query_knowledge_graph",
    description="Query knowledge graph for relevant information",
    input_schema={
        "type": "object",
        "properties": {
            "triad": {"type": "string"},
            "query": {"type": "string"}
        },
        "required": ["triad", "query"]
    },
    category="knowledge"
))
def query_knowledge_graph(triad: str, query: str) -> ToolResult:
    return KnowledgeTools.query_graph(triad, query)
```

**Benefits**:
- ✅ Discoverable tools (list what's available)
- ✅ Schema-validated inputs
- ✅ Categorized capabilities
- ✅ Foundation for future MCP server
- ✅ Internal CLI can list tools

---

### Phase 4: Optional MCP Server Wrapper (Future)

**Goal**: Expose tool abstraction layer via MCP for external tools

**When**: Only if there's demand for external integration

**Architecture**:
```
External Tool (e.g., IDE) ◄──JSON-RPC──► MCP Server ──► Tool Registry ──► Triads Modules
                                          (Python)      (abstraction)     (implementation)
```

**Implementation**:
```python
# mcp_server.py (future, optional)
from modelcontextprotocol import Server
from triads.tools.registry import ToolRegistry

server = Server("triads-mcp")

@server.list_tools()
async def list_tools():
    """MCP tools/list handler"""
    tools = ToolRegistry.list_tools()
    return [
        {
            "name": tool.name,
            "description": tool.description,
            "inputSchema": tool.input_schema
        }
        for tool in tools
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """MCP tools/call handler"""
    result = ToolRegistry.call_tool(name, **arguments)
    return {
        "content": result.content,
        "isError": not result.success
    }
```

**Benefits**:
- ✅ External tools can query Triads state
- ✅ IDEs can integrate with Triads
- ✅ Doesn't affect core plugin functionality
- ✅ Optional (Triads works fine without it)

---

## Part 6: What Stays Local (Non-Negotiable)

These components **MUST** remain in the Claude Code plugin:

### 1. Agent Definitions (.md files)
**Why**: Claude Code's Task tool loads these directly
**Location**: `.claude/agents/*/`
**Not MCP-compatible**: Task tool expects local files

### 2. Hook System
**Why**: Lifecycle integration with Claude Code
**Location**: `hooks/*.py`
**Not MCP-compatible**: Event-driven, not request-driven

### 3. Triad Execution Logic
**Why**: Atomic workflows via Task tool
**Location**: Supervisor mode, agent prompts
**Not MCP-compatible**: Multi-step stateful processes

### 4. Knowledge Graph Files
**Why**: Hooks inject context automatically
**Location**: `.claude/graphs/*.json`
**Could be MCP-readable**: But injection must stay local

---

## Part 7: Decision Matrix

### Should Triads Be a Full MCP Server?

| Factor | Score | Reasoning |
|--------|-------|-----------|
| **Agent definitions compatibility** | ❌ 0/10 | Must stay local for Task tool |
| **Hook system compatibility** | ❌ 0/10 | Event-driven vs request-driven |
| **Triad atomicity preservation** | ❌ 2/10 | MCP wants granular tools |
| **State management** | ⚠️ 5/10 | Could work but loses auto-injection |
| **External integration value** | ⚠️ 6/10 | Some value but niche use case |
| **Implementation complexity** | ❌ 3/10 | Significant refactoring needed |
| **Ecosystem fit** | ⚠️ 5/10 | Partial - KM queries yes, workflows no |

**Overall**: **30/70 (43%)** - Not a good fit for full MCP server

---

### Should Triads Use MCP-Inspired Abstractions?

| Factor | Score | Reasoning |
|--------|-------|-----------|
| **Code organization** | ✅ 9/10 | Clean tool interfaces improve structure |
| **Testability** | ✅ 9/10 | Tool boundaries easier to mock |
| **Future flexibility** | ✅ 8/10 | Could expose via MCP later if needed |
| **Discoverability** | ✅ 8/10 | Registry makes capabilities clear |
| **Decoupling** | ✅ 9/10 | Separates interface from implementation |
| **Migration risk** | ✅ 7/10 | Low - internal refactoring only |
| **Maintenance** | ✅ 8/10 | Easier to maintain consistent APIs |

**Overall**: **58/70 (83%)** - **Strong recommendation**

---

## Part 8: Recommendations

### ✅ DO (High Value, Low Risk)

1. **Create tool abstraction layer** (`src/triads/tools/`)
   - MCP-inspired but not MCP-compliant
   - Standard `ToolResult` format
   - Categories: knowledge, integrity, routing, workflow

2. **Refactor to use tools internally**
   - Replace direct module calls with tool interfaces
   - Improve testability and maintainability
   - No external dependencies

3. **Add tool registry**
   - Internal discovery mechanism
   - Schema validation
   - Foundation for future MCP if desired

4. **Document tool catalog**
   - What capabilities exist
   - How to use each tool
   - Input/output contracts

### ⚠️ CONSIDER (Medium Value, Medium Risk)

5. **Optional MCP server wrapper**
   - Only if external integration demand exists
   - Exposes read-only operations (queries)
   - Doesn't affect core plugin

6. **Separate read/write operations**
   - Read operations → could be MCP tools
   - Write operations → stay in plugin hooks

### ❌ DON'T (Low Value, High Risk)

7. **Move agent definitions to remote server**
   - Breaks Task tool integration
   - Violates triad atomicity
   - No clear benefit

8. **Expose hook execution as MCP tools**
   - Hooks are lifecycle events, not request/response
   - Would break automatic context injection

9. **Force full MCP compliance**
   - Architectural mismatch
   - Loses core Triads benefits
   - High migration cost

---

## Part 9: Implementation Roadmap

### Phase 1: Tool Abstraction (2-3 hours)
- Create `src/triads/tools/__init__.py`
- Define `ToolResult` format
- Implement `KnowledgeTools` class
- Implement `IntegrityTools` class
- Implement `RouterTools` class
- Add basic tests

### Phase 2: Registry (2-3 hours)
- Create `src/triads/tools/registry.py`
- Implement `ToolRegistry` class
- Register existing tools
- Add `list_tools()` functionality
- Add CLI command: `triads tools list`

### Phase 3: Internal Refactoring (4-6 hours)
- Update hooks to use tool interfaces
- Update agent templates to reference tools
- Update CLI commands to use registry
- Add integration tests
- Update documentation

### Phase 4: Optional MCP Server (6-8 hours, only if needed)
- Install MCP SDK: `pip install modelcontextprotocol`
- Create `src/triads/mcp_server.py`
- Implement `tools/list` handler
- Implement `tools/call` handler
- Add MCP server tests
- Document external usage

**Total Estimate**: 8-12 hours (without MCP server), 14-20 hours (with MCP server)

---

## Part 10: Conclusion

### Your Intuitions Were Correct ✅

1. **"Claude will still need agent definitions locally"**
   - ✅ **Absolutely correct** - Task tool requires local .md files
   - Can't be moved to remote server without breaking Claude Code integration

2. **"Can we abstract capabilities into 'tools'"**
   - ✅ **Excellent idea** - Improves code organization
   - MCP-inspired abstraction provides clean interfaces
   - Future-proofs for possible MCP integration

3. **"Maybe not going full blown MCP"**
   - ✅ **Smart approach** - Full MCP is architectural mismatch
   - Hybrid (MCP-inspired locally, optional MCP server externally) is optimal

### Final Recommendation

**Implement MCP-inspired tool abstraction internally**, but **don't force full MCP compliance**.

**Benefits**:
- ✅ Cleaner code organization
- ✅ Better testability
- ✅ Discoverable capabilities
- ✅ Future flexibility (MCP server if needed)
- ✅ No breaking changes
- ✅ Agent definitions stay local
- ✅ Hooks stay local
- ✅ Triad atomicity preserved

**Next Steps**:
1. Review this analysis with stakeholders
2. Decide: "tool abstraction only" or "tool abstraction + MCP server"
3. If approved, start with Phase 1 (tool abstraction)
4. Iterate based on feedback

---

**Author**: Claude Code Supervisor
**Date**: 2025-10-23
**Status**: Ready for review
