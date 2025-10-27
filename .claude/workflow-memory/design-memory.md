# Design Workflow - Context Memory

**Workflow**: Design
**Domain**: {{DOMAIN_TYPE}}
**Started**: {{START_DATE}}
**Status**: {{STATUS}}

This file captures context for design workflows, ensuring continuity across validation-synthesizer → solution-architect → design-bridge.

---

## 🎯 WORKFLOW PURPOSE

**Objective**: Design technical solutions, evaluate alternatives, create Architecture Decision Records (ADRs), and prepare for implementation.

**Success Criteria**:
- [ ] Solution architecture designed
- [ ] Alternatives evaluated with trade-offs documented
- [ ] ADRs created for key decisions
- [ ] Implementation plan ready
- [ ] Design approved by user (HITL gate)

---

## 📊 FEATURE/PROBLEM BEING DESIGNED

### From Idea Validation

```yaml
validated_idea:
  name: "{{FEATURE_NAME}}"
  decision: "PROCEED"
  priority_score: {{SCORE}} / 100

  problem_statement: |
    {{PROBLEM_STATEMENT}}

  requirements:
    functional:
      - "{{REQUIREMENT_1}}"
      - "{{REQUIREMENT_2}}"
    non_functional:
      - "{{NFR_1}}"  # e.g., "Latency <100ms"
      - "{{NFR_2}}"  # e.g., "99.9% uptime"

  constraints:
    - "{{CONSTRAINT_1}}"
    - "{{CONSTRAINT_2}}"
```

**Example**:
```yaml
validated_idea:
  name: "AI-powered code suggestions"
  decision: "PROCEED"
  priority_score: 85 / 100

  problem_statement: |
    Developers spend 30% of time on repetitive boilerplate code.
    Context switching to documentation breaks flow state.
    AI-powered suggestions could improve productivity significantly.

  requirements:
    functional:
      - "Provide inline code suggestions based on cursor context"
      - "Use project files and dependencies as context"
      - "Support Python, JavaScript, TypeScript initially"
      - "Allow users to accept/reject/modify suggestions"

    non_functional:
      - "Latency: <100ms for suggestion generation"
      - "Accuracy: ≥70% suggestion acceptance rate"
      - "Privacy: Local processing preferred, no code sent to external servers without consent"
      - "Test coverage: ≥90%"

  constraints:
    - "Must use existing Claude API (no new LLM dependencies)"
    - "Budget: Maximum $50/month per user for API costs"
    - "Cannot slow down editor (maintain <50ms keypress latency)"
```

---

## 📋 SOLUTION ARCHITECT WORK

### Architecture Overview

```yaml
architecture:
  approach: "{{HIGH_LEVEL_APPROACH}}"
  style: "{{ARCHITECTURE_STYLE}}"  # e.g., "Client-server", "Microservices", "Event-driven"

  components:
    - name: "{{COMPONENT_1}}"
      responsibility: "{{WHAT_IT_DOES}}"
      technology: "{{TECH_STACK}}"

    - name: "{{COMPONENT_2}}"
      responsibility: "{{WHAT_IT_DOES}}"
      technology: "{{TECH_STACK}}"

  data_flow: |
    {{DESCRIBE_HOW_DATA_FLOWS_THROUGH_SYSTEM}}

  integration_points:
    - system: "{{EXTERNAL_SYSTEM}}"
      integration_type: "{{API|DATABASE|MESSAGE_QUEUE}}"
      purpose: "{{WHY_INTEGRATE}}"
```

**Example**:
```yaml
architecture:
  approach: "Hybrid client-server with local caching"
  style: "Layered architecture with async processing"

  components:
    - name: "Editor Plugin"
      responsibility: "Capture cursor context, display suggestions, handle user interactions"
      technology: "TypeScript, VS Code Extension API"

    - name: "Suggestion Service"
      responsibility: "Generate code suggestions using LLM with project context"
      technology: "Python, FastAPI, Claude API"

    - name: "Context Indexer"
      responsibility: "Index project files, create embeddings, maintain vector store"
      technology: "Python, ChromaDB, sentence-transformers"

    - name: "Cache Layer"
      responsibility: "Cache suggestions and embeddings to reduce API costs"
      technology: "Redis"

  data_flow: |
    1. User types in editor → Plugin captures cursor context (file, line, surrounding code)
    2. Plugin sends context to Suggestion Service via HTTP
    3. Suggestion Service:
       a. Queries Context Indexer for relevant project files (semantic search)
       b. Builds prompt with: cursor context + relevant files + dependencies
       c. Checks Cache Layer for similar previous requests
       d. If cache miss: Calls Claude API for suggestion
       e. Stores suggestion in cache
    4. Suggestion Service returns suggestion to Plugin
    5. Plugin displays inline suggestion to user
    6. User accepts/rejects → feedback logged for future improvements

  integration_points:
    - system: "Claude API"
      integration_type: "REST API"
      purpose: "Generate code suggestions using LLM"

    - system: "Project File System"
      integration_type: "File I/O"
      purpose: "Read project files for context indexing"

    - system: "Editor (VS Code)"
      integration_type: "Extension API"
      purpose: "Capture context and display suggestions"
```

### System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        VS Code Editor                           │
│                                                                 │
│  ┌───────────────────────────────────────────────────────┐     │
│  │              Editor Plugin (TypeScript)               │     │
│  │  - Capture cursor context                             │     │
│  │  - Display suggestions                                │     │
│  │  - Handle user interactions                           │     │
│  └────────────────┬──────────────────────────────────────┘     │
│                   │ HTTP Request (context)                      │
└───────────────────┼─────────────────────────────────────────────┘
                    │
                    ↓
┌───────────────────────────────────────────────────────────────┐
│              Suggestion Service (FastAPI)                      │
│                                                                │
│  ┌──────────────────┐    ┌────────────────┐    ┌──────────┐  │
│  │  Request Handler │ →  │  Cache Layer   │    │  Claude  │  │
│  │                  │    │  (Redis)       │    │   API    │  │
│  └─────────┬────────┘    └────────────────┘    └──────────┘  │
│            │                     ↑                    ↑        │
│            ↓                     │                    │        │
│  ┌──────────────────┐            │                    │        │
│  │ Context Indexer  │ ───────────┘                    │        │
│  │  (ChromaDB)      │                                 │        │
│  │  - Vector store  │ ────────────────────────────────┘        │
│  │  - Embeddings    │       (if cache miss)                    │
│  └──────────────────┘                                          │
└───────────────────────────────────────────────────────────────┘
```

### Alternative Solutions Considered

```yaml
alternatives:
  - alternative_id: "ALT1"
    name: "{{ALTERNATIVE_NAME}}"
    description: |
      {{DESCRIPTION}}

    pros:
      - "{{PRO_1}}"
      - "{{PRO_2}}"

    cons:
      - "{{CON_1}}"
      - "{{CON_2}}"

    trade_offs:
      - dimension: "{{DIMENSION}}"  # e.g., "Cost", "Complexity", "Performance"
        chosen_approach: "{{RATING}}"
        this_alternative: "{{RATING}}"

    reason_not_chosen: |
      {{REASONING}}

  - alternative_id: "ALT2"
    name: "{{ALTERNATIVE_NAME}}"
    description: |
      {{DESCRIPTION}}
    pros:
      - "{{PRO}}"
    cons:
      - "{{CON}}"
    reason_not_chosen: |
      {{REASONING}}
```

**Example**:
```yaml
alternatives:
  - alternative_id: "ALT1"
    name: "Pure Client-Side Processing (Local LLM)"
    description: |
      Run small LLM (e.g., CodeGen 350M) entirely on user's machine.
      No server component, no API costs.

    pros:
      - "Zero API costs (no Claude API usage)"
      - "Maximum privacy (code never leaves user's machine)"
      - "No network latency"
      - "Works offline"

    cons:
      - "Lower quality suggestions (small model vs Claude)"
      - "High CPU/memory usage on user's machine"
      - "Slower on older machines"
      - "Limited context window (350M model can't handle large projects)"

    trade_offs:
      - dimension: "Cost"
        chosen_approach: "$30-50/user/month (Claude API)"
        this_alternative: "$0/month"

      - dimension: "Quality"
        chosen_approach: "90% (Claude 3.5 Sonnet)"
        this_alternative: "60% (CodeGen 350M)"

      - dimension: "Latency"
        chosen_approach: "80-100ms (network + API)"
        this_alternative: "200-500ms (local processing on CPU)"

    reason_not_chosen: |
      Quality is critical for user adoption (research showed 70% acceptance rate threshold).
      Local LLM (60% accuracy) would not meet user expectations.
      Cost savings ($30/month) not worth 30% accuracy drop.
      Decision: Prioritize quality over cost.

  - alternative_id: "ALT2"
    name: "GPT-4 Instead of Claude"
    description: |
      Use OpenAI GPT-4 API instead of Claude API for suggestions.

    pros:
      - "Slightly lower cost ($20/1M tokens vs $30/1M for Claude)"
      - "Larger ecosystem (more documentation, community examples)"
      - "Better tool use support"

    cons:
      - "Lower code quality than Claude (benchmark: 85% vs 90% acceptance)"
      - "Slower (150ms vs 100ms average latency)"
      - "New dependency (project already uses Claude API)"

    trade_offs:
      - dimension: "Cost"
        chosen_approach: "$30/user/month (Claude)"
        this_alternative: "$20/user/month (GPT-4)"

      - dimension: "Quality"
        chosen_approach: "90% acceptance (Claude)"
        this_alternative: "85% acceptance (GPT-4)"

      - dimension: "Consistency"
        chosen_approach: "Reuse existing Claude API"
        this_alternative: "Add new OpenAI dependency"

    reason_not_chosen: |
      Quality difference (90% vs 85%) matters more than cost difference ($10/month).
      Consistency: Project already uses Claude API - adding GPT-4 adds complexity.
      Latency: Claude is 50ms faster (100ms vs 150ms).
      Decision: Stay with Claude for quality and consistency.
```

---

## 📋 ARCHITECTURE DECISION RECORDS (ADRs)

### ADR Template

```yaml
adr:
  - adr_number: {{NUMBER}}
    title: "{{TITLE}}"
    status: "{{PROPOSED|ACCEPTED|DEPRECATED|SUPERSEDED}}"
    date: "{{DATE}}"

    context: |
      {{WHAT_IS_THE_SITUATION}}

    decision: |
      {{WHAT_WE_DECIDED}}

    consequences: |
      {{POSITIVE_AND_NEGATIVE_OUTCOMES}}

    alternatives_considered:
      - "{{ALTERNATIVE_1}}"
      - "{{ALTERNATIVE_2}}"

    references:
      - "{{REFERENCE_1}}"
```

**Example - ADR 1**:
```yaml
adr:
  - adr_number: 1
    title: "Use Claude API for Code Suggestions (Not Local LLM)"
    status: "ACCEPTED"
    date: "2024-10-27"

    context: |
      We need to generate high-quality code suggestions for developers.
      Two main approaches:
      1. Use cloud LLM (Claude API) - higher quality, costs money
      2. Use local LLM (CodeGen) - lower quality, free

      Research shows 70% acceptance rate threshold for adoption.
      Users prioritize quality over cost (validation research).

    decision: |
      We will use Claude API (3.5 Sonnet) for code suggestions.

      Rationale:
      - Quality: 90% acceptance rate (Claude) vs 60% (local model)
      - Latency: 100ms (Claude with caching) vs 200-500ms (local CPU processing)
      - User feedback: "Would pay for high-quality suggestions" (15/20 interviews)

      Cost mitigation:
      - Implement aggressive caching (Redis) to reduce API calls
      - Set monthly budget cap ($50/user, configurable)
      - Allow users to opt into local mode if cost is concern

    consequences: |
      **Positive**:
      - High-quality suggestions (90% acceptance rate target)
      - Faster response time (100ms vs 200-500ms local)
      - Better user satisfaction (quality prioritized)
      - Consistent with project's existing Claude API usage

      **Negative**:
      - Ongoing API costs ($30-50/user/month)
      - Requires network connection (no offline support)
      - Privacy consideration (code sent to Claude API - mitigated with user consent)

      **Mitigation**:
      - Implement caching to reduce costs by 50-70%
      - Make API usage opt-in with clear privacy disclosure
      - Consider adding local mode as fallback in future

    alternatives_considered:
      - "Local LLM (CodeGen 350M) - rejected due to quality (60% vs 90%)"
      - "GPT-4 API - rejected due to lower quality (85%) and latency (150ms)"
      - "Hybrid (local + cloud) - deferred to future iteration (complexity)"

    references:
      - "Validation research: 23/30 users prioritize quality over cost"
      - "Benchmark: Claude 90% acceptance vs GPT-4 85% vs CodeGen 60%"
      - "Cost analysis: templates/workflow-memory/idea-validation-memory.md"
```

**Example - ADR 2**:
```yaml
adr:
  - adr_number: 2
    title: "Use ChromaDB for Vector Store (Not Pinecone or FAISS)"
    status: "ACCEPTED"
    date: "2024-10-28"

    context: |
      Context Indexer needs vector database to store project file embeddings.
      Semantic search to find relevant files for LLM context.

      Options:
      1. ChromaDB (embedded, local)
      2. Pinecone (cloud, managed)
      3. FAISS (library, requires custom management)

    decision: |
      We will use ChromaDB as our vector database.

      Rationale:
      - Embedded: No separate service to manage (simplicity)
      - Local: No data sent to third-party (privacy)
      - Full-featured: Supports filtering, metadata, persistence
      - Python-native: Easy integration with FastAPI backend

    consequences: |
      **Positive**:
      - Simple deployment (embedded in Suggestion Service)
      - No additional costs (vs $70/month for Pinecone)
      - Better privacy (vectors stay local)
      - Fast local queries (<10ms vs 50ms network)

      **Negative**:
      - Scaling limits (single machine, not distributed)
      - No managed backups (must implement ourselves)
      - Memory usage (vectors stored in-process)

      **Acceptable Because**:
      - Project size typically <1M LOC (ChromaDB handles easily)
      - Local development tool (not web-scale service)
      - Can migrate to Pinecone later if scaling becomes issue

    alternatives_considered:
      - "Pinecone - rejected due to cost ($70/month) and privacy (cloud)"
      - "FAISS - rejected due to complexity (must implement persistence, management)"

    references:
      - "ChromaDB docs: https://docs.trychroma.com"
      - "Benchmark: ChromaDB 10ms vs Pinecone 50ms (local vs network)"
```

---

## 📋 IMPLEMENTATION PLAN

### High-Level Plan

```yaml
implementation_plan:
  phases:
    - phase: {{NUMBER}}
      name: "{{PHASE_NAME}}"
      description: |
        {{WHAT_THIS_PHASE_ACCOMPLISHES}}

      deliverables:
        - "{{DELIVERABLE_1}}"
        - "{{DELIVERABLE_2}}"

      estimated_effort: "{{EFFORT}}"  # e.g., "2 weeks", "10 dev-days"

      dependencies:
        - "{{DEPENDENCY_1}}"

      risks:
        - risk: "{{RISK}}"
          likelihood: "{{LOW|MEDIUM|HIGH}}"
          impact: "{{LOW|MEDIUM|HIGH}}"
          mitigation: "{{HOW_TO_MITIGATE}}"
```

**Example**:
```yaml
implementation_plan:
  phases:
    - phase: 1
      name: "Foundation: Context Indexer"
      description: |
        Build the Context Indexer component that indexes project files
        and creates embeddings for semantic search.

      deliverables:
        - "File system watcher to detect file changes"
        - "Embedding generation using sentence-transformers"
        - "ChromaDB integration for vector storage"
        - "Semantic search API (find relevant files by query)"
        - "Tests with ≥90% coverage"

      estimated_effort: "1 week (5 dev-days)"

      dependencies:
        - "ChromaDB library (pip install chromadb)"
        - "sentence-transformers library"

      risks:
        - risk: "Embedding generation too slow for large projects"
          likelihood: "MEDIUM"
          impact: "HIGH"
          mitigation: "Batch processing, incremental indexing, background worker"

        - risk: "Memory usage too high for large projects"
          likelihood: "LOW"
          impact: "MEDIUM"
          mitigation: "Lazy loading, chunk embeddings, configurable index size limit"

    - phase: 2
      name: "Core: Suggestion Service"
      description: |
        Build the Suggestion Service that generates code suggestions
        using Claude API with project context.

      deliverables:
        - "FastAPI service with /suggest endpoint"
        - "Claude API integration"
        - "Prompt engineering for code suggestions"
        - "Context building (cursor + relevant files)"
        - "Redis caching layer"
        - "Tests with ≥90% coverage"

      estimated_effort: "1.5 weeks (7 dev-days)"

      dependencies:
        - "Phase 1 complete (Context Indexer)"
        - "Claude API credentials"
        - "Redis running locally"

      risks:
        - risk: "Claude API latency >100ms"
          likelihood: "MEDIUM"
          impact: "HIGH"
          mitigation: "Aggressive caching, prompt optimization, streaming responses"

        - risk: "API costs exceed budget ($50/user/month)"
          likelihood: "MEDIUM"
          impact: "HIGH"
          mitigation: "Usage tracking, rate limiting, cost alerts, cache hit rate monitoring"

    - phase: 3
      name: "UI: Editor Plugin"
      description: |
        Build the VS Code extension that captures context and displays suggestions.

      deliverables:
        - "VS Code extension scaffolding"
        - "Context capture (cursor position, surrounding code)"
        - "HTTP client to Suggestion Service"
        - "Inline suggestion display (ghost text)"
        - "Keyboard shortcuts (Tab to accept, Esc to reject)"
        - "Tests with ≥90% coverage"

      estimated_effort: "1 week (5 dev-days)"

      dependencies:
        - "Phase 2 complete (Suggestion Service)"
        - "VS Code Extension API docs"

      risks:
        - risk: "Extension slows down editor"
          likelihood: "MEDIUM"
          impact: "HIGH"
          mitigation: "Async API calls, debouncing, performance profiling, <50ms keypress latency requirement"

    - phase: 4
      name: "Polish: Caching, Monitoring, Configuration"
      description: |
        Add production-ready features: caching, monitoring, user configuration.

      deliverables:
        - "Redis caching with 70% hit rate target"
        - "Usage analytics (acceptance rate, latency, cost)"
        - "User settings (enable/disable, budget cap, privacy mode)"
        - "Cost dashboard (API usage tracking)"
        - "Performance monitoring (latency, cache hit rate)"

      estimated_effort: "1 week (5 dev-days)"

      dependencies:
        - "Phase 3 complete (Editor Plugin)"

      risks:
        - risk: "Cache invalidation logic incorrect"
          likelihood: "LOW"
          impact: "MEDIUM"
          mitigation: "TTL-based expiry (1 hour), clear cache on file save"
```

### File Structure

```
project-root/
├── backend/
│   ├── suggestion_service/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── suggest.py         # /suggest endpoint
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── llm_client.py      # Claude API client
│   │   │   └── prompt_builder.py   # Build prompts with context
│   │   ├── context_indexer/
│   │   │   ├── __init__.py
│   │   │   ├── indexer.py          # Index project files
│   │   │   ├── embedder.py         # Generate embeddings
│   │   │   └── search.py           # Semantic search
│   │   ├── cache/
│   │   │   ├── __init__.py
│   │   │   └── redis_cache.py      # Redis caching layer
│   │   ├── main.py                 # FastAPI app
│   │   └── config.py               # Configuration
│   ├── tests/
│   │   ├── test_api/
│   │   ├── test_core/
│   │   ├── test_context_indexer/
│   │   └── test_cache/
│   ├── pyproject.toml
│   └── README.md
│
├── extension/
│   ├── src/
│   │   ├── extension.ts            # Extension entry point
│   │   ├── suggestionProvider.ts   # Capture context, display suggestions
│   │   ├── httpClient.ts           # Call Suggestion Service
│   │   └── config.ts               # User settings
│   ├── test/
│   ├── package.json
│   └── README.md
│
└── docs/
    ├── ADR-001-claude-api.md
    ├── ADR-002-chromadb.md
    └── architecture.md
```

---

## 📋 DESIGN BRIDGE WORK

### Design Compression

**Top Priority Items for Implementation**:
```yaml
design_summary:
  critical_decisions:
    - decision: "{{DECISION_1}}"
      rationale: "{{WHY}}"
      adr: "{{ADR_NUMBER}}"

    - decision: "{{DECISION_2}}"
      rationale: "{{WHY}}"
      adr: "{{ADR_NUMBER}}"

  must_haves:
    - "{{REQUIREMENT_1}}"
    - "{{REQUIREMENT_2}}"

  nice_to_haves:
    - "{{ENHANCEMENT_1}}"

  implementation_order:
    1: "{{PHASE_1}}"
    2: "{{PHASE_2}}"
    3: "{{PHASE_3}}"

  key_files_to_create:
    - "{{FILE_PATH_1}} - {{PURPOSE}}"
    - "{{FILE_PATH_2}} - {{PURPOSE}}"
```

**Example**:
```yaml
design_summary:
  critical_decisions:
    - decision: "Use Claude API for suggestions (not local LLM)"
      rationale: "Quality (90% vs 60%), user research showed quality > cost priority"
      adr: "ADR-001"

    - decision: "Use ChromaDB for vector store (not Pinecone)"
      rationale: "Simplicity (embedded), privacy (local), cost ($0 vs $70/month)"
      adr: "ADR-002"

    - decision: "Hybrid architecture (client plugin + server service)"
      rationale: "Balance latency (100ms) with quality (Claude API)"
      adr: "ADR-003"

  must_haves:
    - "Latency <100ms (non-functional requirement)"
    - "Test coverage ≥90% (project standard)"
    - "Privacy: User consent before sending code to API"
    - "Cost tracking: Budget cap enforcement ($50/user/month)"

  nice_to_haves:
    - "Multi-language support beyond Python/JS/TS"
    - "Offline mode with local LLM fallback"
    - "Suggestion quality feedback loop (learning from accept/reject)"

  implementation_order:
    1: "Context Indexer (foundation for semantic search)"
    2: "Suggestion Service (core LLM integration)"
    3: "Editor Plugin (UI for displaying suggestions)"
    4: "Caching + Monitoring (production readiness)"

  key_files_to_create:
    - "backend/suggestion_service/api/suggest.py - Main API endpoint"
    - "backend/suggestion_service/core/llm_client.py - Claude API integration"
    - "backend/suggestion_service/context_indexer/indexer.py - File indexing logic"
    - "extension/src/suggestionProvider.ts - VS Code suggestion provider"
    - "extension/src/httpClient.ts - HTTP client to backend"
```

---

## 🔗 HANDOFF TO IMPLEMENTATION TRIAD

### Context Summary for Implementation

```yaml
handoff_to_implementation:
  what_to_build:
    summary: "{{ONE_SENTENCE_SUMMARY}}"
    components:
      - name: "{{COMPONENT_1}}"
        files_to_create:
          - "{{FILE_1}}"
          - "{{FILE_2}}"
        key_classes:
          - "{{CLASS_1}}"
      - name: "{{COMPONENT_2}}"
        files_to_create:
          - "{{FILE_3}}"

  start_here:
    - "{{INSTRUCTION_1}}"
    - "{{INSTRUCTION_2}}"

  adrs_to_follow:
    - "{{ADR_1}} - {{SUMMARY}}"
    - "{{ADR_2}} - {{SUMMARY}}"

  non_negotiables:
    - "{{REQUIREMENT_1}}"
    - "{{REQUIREMENT_2}}"

  testing_requirements:
    - "{{TEST_REQUIREMENT_1}}"
    - "{{TEST_REQUIREMENT_2}}"

  questions_for_implementation:
    - "{{QUESTION_1}}"
```

**Example**:
```yaml
handoff_to_implementation:
  what_to_build:
    summary: "AI-powered code suggestion system with VS Code plugin, FastAPI backend, and Claude API integration"
    components:
      - name: "Context Indexer"
        files_to_create:
          - "backend/suggestion_service/context_indexer/indexer.py"
          - "backend/suggestion_service/context_indexer/embedder.py"
          - "backend/suggestion_service/context_indexer/search.py"
        key_classes:
          - "ContextIndexer (main orchestrator)"
          - "Embedder (sentence-transformers wrapper)"
          - "SemanticSearch (ChromaDB wrapper)"

      - name: "Suggestion Service"
        files_to_create:
          - "backend/suggestion_service/api/suggest.py"
          - "backend/suggestion_service/core/llm_client.py"
          - "backend/suggestion_service/core/prompt_builder.py"
        key_classes:
          - "SuggestAPI (FastAPI endpoint)"
          - "ClaudeClient (API wrapper)"
          - "PromptBuilder (context → prompt)"

      - name: "Editor Plugin"
        files_to_create:
          - "extension/src/suggestionProvider.ts"
          - "extension/src/httpClient.ts"
        key_classes:
          - "SuggestionProvider (VS Code API)"
          - "HttpClient (Axios wrapper)"

  start_here:
    - "Phase 1: Build Context Indexer first (foundation for everything else)"
    - "Start with: backend/suggestion_service/context_indexer/indexer.py"
    - "Follow TDD: Write tests first (test_indexer.py)"
    - "Reference: ADR-002 for ChromaDB integration details"

  adrs_to_follow:
    - "ADR-001: Use Claude API (not local LLM) - see templates/workflow-memory/design-memory.md"
    - "ADR-002: Use ChromaDB (not Pinecone) - embedded, local, simple"
    - "ADR-003: Hybrid architecture (plugin + service) - balance latency + quality"

  non_negotiables:
    - "Latency: <100ms for /suggest endpoint (verified with load testing)"
    - "Test coverage: ≥90% (project standard, enforced by pre-commit)"
    - "Privacy: User consent dialog before first API call, clear data disclosure"
    - "Cost tracking: Redis counter for API usage, alert at 80% of budget cap"

  testing_requirements:
    - "Unit tests: All classes with ≥90% coverage"
    - "Integration tests: Context Indexer + Suggestion Service end-to-end"
    - "Load tests: /suggest endpoint handles 100 req/s with <100ms latency"
    - "Cost tests: Verify caching reduces API calls by ≥70%"

  questions_for_implementation:
    - "Prompt engineering: What's the optimal prompt structure? (Experiment and iterate)"
    - "Context window: How many files to include? (Start with top-5, tune based on quality)"
    - "Caching key: Cache by (file, line, surrounding code) or just (file, line)?"
```

---

## 🚨 HITL GATE: USER APPROVAL

### Design Review Checklist

```yaml
design_review:
  presented_to_user:
    - item: "Architecture overview with system diagram"
      status: "{{✅ APPROVED | ⏳ PENDING | ❌ CHANGES REQUESTED}}"
      feedback: |
        {{USER_FEEDBACK}}

    - item: "Alternative solutions and trade-offs"
      status: "{{STATUS}}"
      feedback: |
        {{FEEDBACK}}

    - item: "ADRs for key decisions"
      status: "{{STATUS}}"
      feedback: |
        {{FEEDBACK}}

    - item: "Implementation plan (phases, effort estimates)"
      status: "{{STATUS}}"
      feedback: |
        {{FEEDBACK}}

  user_decision: "{{APPROVE | REQUEST_CHANGES | REJECT}}"

  changes_requested:
    - "{{CHANGE_1}}"
    - "{{CHANGE_2}}"

  approval_date: "{{DATE}}"
  approved_by: "{{USER_NAME}}"
```

**Example - APPROVED**:
```yaml
design_review:
  presented_to_user:
    - item: "Architecture overview with system diagram"
      status: "✅ APPROVED"
      feedback: |
        "Architecture looks good. Hybrid approach makes sense.
        Concerned about API costs - good to see caching plan."

    - item: "Alternative solutions and trade-offs"
      status: "✅ APPROVED"
      feedback: |
        "Appreciate the thoroughness. Agree that quality > cost for this use case."

    - item: "ADRs for key decisions"
      status: "✅ APPROVED"
      feedback: |
        "ADRs are clear and well-reasoned. Particularly like ADR-002 (ChromaDB) rationale."

    - item: "Implementation plan (phases, effort estimates)"
      status: "✅ APPROVED"
      feedback: |
        "4-week timeline seems reasonable. Start with Phase 1."

  user_decision: "APPROVE"

  changes_requested: []

  approval_date: "2024-10-28"
  approved_by: "User"
```

**Example - CHANGES REQUESTED**:
```yaml
design_review:
  presented_to_user:
    - item: "Architecture overview"
      status: "⏳ CHANGES REQUESTED"
      feedback: |
        "Concerned about Redis dependency. Can we use in-memory cache first,
        add Redis only if needed?"

    - item: "Implementation plan"
      status: "⏳ CHANGES REQUESTED"
      feedback: |
        "4 weeks is too long. Can we ship Phase 1-2 in 2 weeks as MVP,
        then iterate with Phase 3-4?"

  user_decision: "REQUEST_CHANGES"

  changes_requested:
    - "Replace Redis with in-memory cache (Python dict) for MVP"
    - "Revise implementation plan: Ship Phase 1-2 as MVP (2 weeks), Phase 3-4 as iterations"
    - "Add cost monitoring earlier (Phase 2 instead of Phase 4)"

  approval_date: null  # Not approved yet
```

---

## 📊 KNOWLEDGE GRAPH UPDATES

### ADR Nodes

```yaml
knowledge_nodes:
  - node_id: "ADR_001_{{TIMESTAMP}}"
    node_type: "ADR"
    label: "Use Claude API for code suggestions"
    description: |
      Decision to use Claude API instead of local LLM for higher quality (90% vs 60% acceptance).
    confidence: 0.95
    evidence: |
      - Validation research: 90% acceptance with Claude vs 60% with CodeGen
      - User interviews: 15/20 prioritize quality over cost
      - Benchmark: Claude 100ms latency vs CodeGen 200-500ms
    created_by: "solution-architect"
    created_at: "2024-10-27T14:30:00Z"

  - node_id: "ADR_002_{{TIMESTAMP}}"
    node_type: "ADR"
    label: "Use ChromaDB for vector store"
    description: |
      Decision to use ChromaDB (embedded) instead of Pinecone (cloud) for simplicity and privacy.
    confidence: 0.90
    evidence: |
      - Benchmark: ChromaDB 10ms vs Pinecone 50ms (local vs network)
      - Cost: $0 vs $70/month for Pinecone
      - Privacy: Local storage vs cloud
    created_by: "solution-architect"
    created_at: "2024-10-28T09:15:00Z"
```

---

## 📚 RESOURCES

### Design References

```yaml
resources:
  design_docs:
    - title: "System Architecture Diagram"
      location: "{{PATH_TO_DIAGRAM}}"
      notes: "High-level component overview"

    - title: "API Specification"
      location: "{{PATH_TO_API_SPEC}}"
      notes: "OpenAPI 3.0 spec for Suggestion Service"

  adrs:
    - title: "ADR-001: Claude API Selection"
      location: "docs/adrs/001-claude-api.md"
      summary: "Use Claude API for quality (90% acceptance)"

    - title: "ADR-002: ChromaDB for Vectors"
      location: "docs/adrs/002-chromadb.md"
      summary: "Use ChromaDB for simplicity and privacy"

  external_references:
    - title: "VS Code Extension API"
      url: "https://code.visualstudio.com/api"
      relevance: "For building Editor Plugin (Phase 3)"

    - title: "Claude API Documentation"
      url: "https://docs.anthropic.com/claude/reference"
      relevance: "For Suggestion Service integration (Phase 2)"

    - title: "ChromaDB Documentation"
      url: "https://docs.trychroma.com"
      relevance: "For Context Indexer implementation (Phase 1)"
```

---

## 🎯 SUCCESS METRICS

```yaml
success_metrics:
  design_complete:
    - criterion: "Architecture designed with component diagram"
      status: "{{✅ COMPLETE | ⏳ IN PROGRESS}}"
    - criterion: "≥2 alternatives evaluated with trade-offs"
      status: "{{STATUS}}"
    - criterion: "≥2 ADRs created for key decisions"
      status: "{{STATUS}}"
    - criterion: "Implementation plan with phases and estimates"
      status: "{{STATUS}}"
    - criterion: "User approval obtained (HITL gate)"
      status: "{{STATUS}}"

  quality_gates:
    - gate: "All decisions have documented reasoning"
      status: "{{✅ PASSED | ❌ FAILED}}"
    - gate: "All ADRs include alternatives considered"
      status: "{{STATUS}}"
    - gate: "Implementation plan addresses all requirements"
      status: "{{STATUS}}"
```

---

*This context memory ensures continuity and quality across the Design workflow.*

**Template Version**: v1.0.0
**Last Updated**: {{LAST_UPDATED}}
