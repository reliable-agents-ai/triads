# Garden Tending Workflow - Context Memory

**Workflow**: Garden Tending
**Domain**: {{DOMAIN_TYPE}}
**Started**: {{START_DATE}}
**Status**: {{STATUS}}

This file captures context for garden tending workflows (refactoring and quality improvement), ensuring continuity across cultivator → pruner → gardener-bridge.

---

## 🎯 WORKFLOW PURPOSE

**Objective**: Improve code quality through refactoring, reduce technical debt, eliminate redundancy while maintaining all tests green.

**Success Criteria**:
- [ ] Code quality improved (measurable metrics)
- [ ] Technical debt reduced
- [ ] All tests still pass (no regressions)
- [ ] No functionality broken
- [ ] Refactoring documented

**Philosophy**: Cultivate growth opportunities, prune redundancy, preserve working systems.

---

## 📊 INITIAL STATE

### Quality Baseline

```yaml
initial_quality:
  test_coverage: "{{PERCENTAGE}}%"
  code_smells_detected: {{COUNT}}
  duplication: "{{PERCENTAGE}}% duplicated lines"
  complexity:
    average_cyclomatic: {{NUMBER}}
    max_cyclomatic: {{NUMBER}}
    functions_over_20_lines: {{COUNT}}

  linting_issues:
    - tool: "flake8"
      issues: {{COUNT}}
    - tool: "mypy"
      issues: {{COUNT}}

  technical_debt:
    - item: "{{DEBT_1}}"
      severity: "{{LOW|MEDIUM|HIGH}}"
    - item: "{{DEBT_2}}"
      severity: "{{SEVERITY}}"
```

---

## 📋 CULTIVATOR WORK

### Growth Opportunities Identified

```yaml
growth_opportunities:
  - opportunity_id: "GROW001"
    type: "{{EXTRACT_METHOD|RENAME|SIMPLIFY|DOCUMENTATION}}"
    location: "{{FILE}}:{{LINE}}"
    description: "{{WHAT_CAN_BE_IMPROVED}}"
    benefit: "{{WHY_THIS_HELPS}}"
    effort: "{{LOW|MEDIUM|HIGH}}"
    priority: "{{LOW|MEDIUM|HIGH}}"

  - opportunity_id: "GROW002"
    type: "Extract method"
    location: "src/api/suggest.py:45-78"
    description: "34-line function does multiple things (build context, call LLM, format response)"
    benefit: "Better testability, clearer responsibilities"
    effort: "LOW"
    priority: "HIGH"
```

### Beneficial Patterns Found

```yaml
beneficial_patterns:
  - pattern: "{{PATTERN_NAME}}"
    example_location: "{{FILE}}:{{LINE}}"
    description: "{{WHAT_MAKES_THIS_GOOD}}"
    propagation_opportunities:
      - "{{WHERE_ELSE_TO_APPLY_1}}"
      - "{{WHERE_ELSE_TO_APPLY_2}}"

  - pattern: "Dependency Injection"
    example_location: "src/core/llm_client.py:15"
    description: "LLM client accepts config as constructor param (easy to mock, test, swap implementations)"
    propagation_opportunities:
      - "Apply to ContextIndexer (currently uses global config)"
      - "Apply to CacheLayer (hardcoded Redis connection)"
```

### Consolidation Opportunities

```yaml
consolidation_opportunities:
  - opportunity_id: "CONS001"
    type: "{{DRY|MERGE|EXTRACT_COMMON}}"
    description: "{{WHAT_TO_CONSOLIDATE}}"
    locations:
      - "{{FILE_1}}:{{LINE}}"
      - "{{FILE_2}}:{{LINE}}"
    proposed_solution: "{{HOW_TO_CONSOLIDATE}}"
    risk: "{{LOW|MEDIUM|HIGH}}"

  - opportunity_id: "CONS002"
    type: "DRY"
    description: "Error handling code duplicated across 5 API endpoints"
    locations:
      - "src/api/suggest.py:123-135"
      - "src/api/health.py:45-57"
      - "src/api/config.py:78-90"
      - "src/api/feedback.py:102-114"
      - "src/api/status.py:67-79"
    proposed_solution: "Extract to error_handler decorator"
    risk: "LOW"
```

---

## 📋 PRUNER WORK

### 5 Safe Refactoring Rules

**Rules**:
1. ✅ Tests exist and pass BEFORE refactoring
2. ✅ ONE refactoring at a time
3. ✅ Run tests AFTER each refactoring
4. ✅ Commit AFTER each successful refactoring
5. ✅ NEVER change behavior, only structure

### Refactoring Execution

#### Refactoring 1: {{REFACTORING_NAME}}

```yaml
refactoring_1:
  type: "{{EXTRACT_METHOD|RENAME|SIMPLIFY|DRY}}"
  description: "{{WHAT_IS_BEING_REFACTORED}}"
  location: "{{FILE}}:{{LINE}}"

  before:
    tests_status: "{{PASSING|FAILING}}"
    test_count: {{COUNT}}
    code: |
      {{CODE_BEFORE}}

  refactoring_applied:
    technique: "{{TECHNIQUE}}"  # e.g., "Extract Method", "Rename Variable"
    changes: |
      {{DESCRIPTION_OF_CHANGES}}
    code_after: |
      {{CODE_AFTER}}

  after:
    tests_status: "{{PASSING|FAILING}}"
    tests_run: "pytest {{FILE}}"
    result: "{{ALL_PASSED|SOME_FAILED}}"

  committed:
    commit_message: "refactor: {{DESCRIPTION}}"
    commit_hash: "{{HASH}}"
```

**Example**:
```yaml
refactoring_1:
  type: "Extract Method"
  description: "Extract 34-line suggest() function into smaller focused functions"
  location: "src/api/suggest.py:45-78"

  before:
    tests_status: "PASSING"
    test_count: 12
    code: |
      def suggest(request: SuggestRequest):
          # Build context (lines 45-55)
          cursor_context = {
              "file": request.file,
              "line": request.line,
              "code": request.surrounding_code
          }

          # Find relevant files (lines 56-63)
          indexer = ContextIndexer()
          relevant_files = indexer.search(cursor_context["code"], top_k=5)

          # Call LLM (lines 64-70)
          llm_client = ClaudeClient()
          prompt = f"Context: {cursor_context}\nRelevant: {relevant_files}\nSuggest:"
          suggestion = llm_client.complete(prompt)

          # Format response (lines 71-78)
          return {
              "suggestion": suggestion,
              "confidence": 0.85,
              "sources": [f["path"] for f in relevant_files]
          }

  refactoring_applied:
    technique: "Extract Method"
    changes: |
      Extracted 4 focused functions:
      - _build_cursor_context()
      - _find_relevant_files()
      - _generate_suggestion()
      - _format_response()

    code_after: |
      def suggest(request: SuggestRequest):
          cursor_context = _build_cursor_context(request)
          relevant_files = _find_relevant_files(cursor_context)
          suggestion = _generate_suggestion(cursor_context, relevant_files)
          return _format_response(suggestion, relevant_files)

      def _build_cursor_context(request: SuggestRequest) -> dict:
          return {
              "file": request.file,
              "line": request.line,
              "code": request.surrounding_code
          }

      def _find_relevant_files(cursor_context: dict) -> list:
          indexer = ContextIndexer()
          return indexer.search(cursor_context["code"], top_k=5)

      def _generate_suggestion(cursor_context: dict, relevant_files: list) -> str:
          llm_client = ClaudeClient()
          prompt = f"Context: {cursor_context}\nRelevant: {relevant_files}\nSuggest:"
          return llm_client.complete(prompt)

      def _format_response(suggestion: str, relevant_files: list) -> dict:
          return {
              "suggestion": suggestion,
              "confidence": 0.85,
              "sources": [f["path"] for f in relevant_files]
          }

  after:
    tests_status: "PASSING"
    tests_run: "pytest tests/test_api/test_suggest.py"
    result: "ALL PASSED ✅ (12/12)"

  committed:
    commit_message: "refactor: Extract methods from suggest() for clarity"
    commit_hash: "abc123"
```

### Refactoring Log

```yaml
refactorings_completed:
  - id: 1
    type: "Extract Method"
    file: "src/api/suggest.py"
    description: "Extracted 4 methods from suggest()"
    tests_pass: "YES"
    commit: "abc123"

  - id: 2
    type: "Rename"
    file: "src/core/llm_client.py"
    description: "Renamed 'get_completion' to 'complete' (clearer, shorter)"
    tests_pass: "YES"
    commit: "def456"

  - id: 3
    type: "DRY"
    file: "src/api/*.py"
    description: "Extracted error_handler decorator (removed 60 lines duplication)"
    tests_pass: "YES"
    commit: "ghi789"
```

### Duplication Removed

```yaml
duplication_removed:
  before:
    duplicated_lines: {{COUNT}}
    duplication_percentage: "{{PERCENTAGE}}%"

  after:
    duplicated_lines: {{COUNT}}
    duplication_percentage: "{{PERCENTAGE}}%"

  reduction: "{{PERCENTAGE_POINTS}}% reduction"

  techniques_used:
    - "Extract common code to utility functions"
    - "Create base classes for shared behavior"
    - "Use decorators for cross-cutting concerns"
```

---

## 📋 GARDENER BRIDGE WORK

### Quality Improvement Summary

```yaml
quality_improvement:
  before:
    test_coverage: "{{PERCENTAGE}}%"
    code_smells: {{COUNT}}
    duplication: "{{PERCENTAGE}}%"
    complexity_avg: {{NUMBER}}

  after:
    test_coverage: "{{PERCENTAGE}}%"
    code_smells: {{COUNT}}
    duplication: "{{PERCENTAGE}}%"
    complexity_avg: {{NUMBER}}

  improvements:
    - metric: "Duplication"
      before: "15%"
      after: "5%"
      improvement: "-10 percentage points"

    - metric: "Average cyclomatic complexity"
      before: "8.5"
      after: "4.2"
      improvement: "-4.3 (50% reduction)"

    - metric: "Functions >20 lines"
      before: "23"
      after: "7"
      improvement: "-16 functions refactored"
```

### Patterns Discovered for Design Triad

```yaml
improvement_patterns:
  - pattern: "Error handling via decorators"
    description: "Eliminated duplication by extracting error handling to decorator"
    benefit: "60 lines removed, consistent error responses"
    recommendation: "Use this pattern for future endpoints"

  - pattern: "Dependency injection for testability"
    description: "Injected dependencies instead of hardcoding"
    benefit: "Easier to mock, test, swap implementations"
    recommendation: "Apply to all new components"
```

---

## 🔗 HANDOFF TO DEPLOYMENT

### Pre-Deployment Checklist

```yaml
pre_deployment:
  code_quality:
    - criterion: "All tests pass"
      status: "{{✅ PASSED | ❌ FAILED}}"
    - criterion: "Test coverage ≥{{TARGET}}%"
      status: "{{PASSED|FAILED}}"
    - criterion: "No linting errors"
      status: "{{PASSED|FAILED}}"
    - criterion: "No security vulnerabilities"
      status: "{{PASSED|FAILED}}"

  refactoring_complete:
    - criterion: "All planned refactorings done"
      status: "{{COMPLETE|INCOMPLETE}}"
    - criterion: "No TODOs or FIXMEs left"
      status: "{{COMPLETE|INCOMPLETE}}"
    - criterion: "Documentation updated"
      status: "{{COMPLETE|INCOMPLETE}}"

  stability:
    - criterion: "No regressions introduced"
      status: "{{VERIFIED|FAILED}}"
    - criterion: "Performance benchmarks met"
      status: "{{MET|FAILED}}"
```

---

## 📊 KNOWLEDGE GRAPH UPDATES

```yaml
knowledge_nodes:
  - node_id: "GARDEN_{{SCOPE}}_{{TIMESTAMP}}"
    node_type: "Refactoring"
    label: "Refactored {{SCOPE}} - improved quality"
    description: |
      Refactored {{SCOPE}}:
      - {{COUNT}} refactorings applied
      - Duplication reduced by {{PERCENTAGE}}%
      - Complexity reduced by {{AMOUNT}}
      All tests still passing.
    confidence: 1.0
    evidence: |
      - Tests: {{COUNT}} passing (no regressions)
      - Duplication: {{BEFORE}}% → {{AFTER}}%
      - Complexity: {{BEFORE}} → {{AFTER}}
      - Commits: {{COMMIT_LIST}}
    created_by: "pruner"
    created_at: "{{TIMESTAMP}}"
```

---

## 🚨 ISSUES ENCOUNTERED

```yaml
issues:
  - issue_id: "REF001"
    description: "Refactoring broke test_suggest_with_cache"
    resolution: "Reverted refactoring, fixed test, re-applied refactoring"
    prevention: "Always run tests before committing refactoring"

  - issue_id: "REF002"
    description: "Complexity increased after refactoring (too many small functions)"
    resolution: "Consolidated related helpers into cohesive modules"
    prevention: "Balance between too large and too fragmented"
```

---

## 🎯 SUCCESS METRICS

```yaml
success_metrics:
  refactoring_complete:
    - criterion: "All growth opportunities addressed"
      status: "{{✅ COMPLETE | ⏳ IN PROGRESS}}"
    - criterion: "Duplication reduced by ≥{{TARGET}}%"
      status: "{{STATUS}}"
    - criterion: "All tests still pass"
      status: "{{STATUS}}"

  quality_gates:
    - gate: "No regressions"
      status: "{{✅ PASSED | ❌ FAILED}}"
    - gate: "Code quality improved (measurable)"
      status: "{{STATUS}}"
```

---

*This context memory ensures continuity and quality across the Garden Tending workflow.*

**Template Version**: v1.0.0
**Last Updated**: {{LAST_UPDATED}}
