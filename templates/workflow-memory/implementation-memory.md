# Implementation Workflow - Context Memory

**Workflow**: Implementation
**Domain**: {{DOMAIN_TYPE}}
**Started**: {{START_DATE}}
**Status**: {{STATUS}}

This file captures context for implementation workflows, ensuring continuity across design-bridge → senior-developer → test-engineer.

---

## 🎯 WORKFLOW PURPOSE

**Objective**: Implement designed solutions following TDD, write comprehensive tests, ensure quality gates pass.

**Success Criteria**:
- [ ] All code implemented following design specifications
- [ ] Test coverage ≥80% (or project-specific threshold)
- [ ] All quality checks pass (linting, typing, formatting)
- [ ] All tests pass (unit, integration, e2e)
- [ ] Code reviewed against quality standards

---

## 📊 FROM DESIGN TRIAD

### Design Summary

```yaml
from_design:
  feature: "{{FEATURE_NAME}}"
  approved_date: "{{APPROVAL_DATE}}"

  components_to_build:
    - name: "{{COMPONENT_1}}"
      files: ["{{FILE_1}}", "{{FILE_2}}"]
      priority: 1

    - name: "{{COMPONENT_2}}"
      files: ["{{FILE_3}}", "{{FILE_4}}"]
      priority: 2

  adrs_to_follow:
    - adr: "{{ADR_NUMBER}}"
      summary: "{{SUMMARY}}"
      implication: "{{WHAT_THIS_MEANS_FOR_IMPLEMENTATION}}"

  non_functional_requirements:
    - "{{NFR_1}}"  # e.g., "Latency <100ms"
    - "{{NFR_2}}"  # e.g., "Test coverage ≥90%"

  implementation_order:
    1: "{{STEP_1}}"
    2: "{{STEP_2}}"
    3: "{{STEP_3}}"
```

---

## 📋 SENIOR DEVELOPER WORK

### TDD Cycle Tracking

#### Iteration 1: {{FEATURE_OR_COMPONENT_NAME}}

**RED Phase**:
```yaml
red_phase:
  test_file: "{{TEST_FILE_PATH}}"
  test_name: "{{TEST_FUNCTION_NAME}}"
  test_code: |
    {{TEST_CODE_SNIPPET}}

  ran_command: "{{PYTEST_COMMAND}}"
  result: "FAILED ❌"
  failure_reason: "{{WHY_IT_FAILED}}"  # Should be "feature not implemented"
  verified: "{{YES|NO}}"  # Did we verify it fails for the right reason?
```

**GREEN Phase**:
```yaml
green_phase:
  implementation_file: "{{IMPL_FILE_PATH}}"
  implementation_code: |
    {{CODE_SNIPPET}}

  ran_command: "{{PYTEST_COMMAND}}"
  result: "PASSED ✅"

  regression_check:
    ran_command: "pytest"  # All tests
    result: "{{ALL_PASSED|SOME_FAILED}}"
    failed_tests: ["{{TEST_1}}", "{{TEST_2}}"]  # If any failed
```

**BLUE Phase**:
```yaml
blue_phase:
  refactorings:
    - refactoring_id: 1
      description: "{{WHAT_WAS_REFACTORED}}"
      reason: "{{WHY}}"  # e.g., "Extract method (function too long)"
      before: |
        {{CODE_BEFORE}}
      after: |
        {{CODE_AFTER}}
      tests_still_pass: "{{YES|NO}}"

    - refactoring_id: 2
      description: "{{REFACTORING_2}}"
      reason: "{{WHY}}"
      tests_still_pass: "{{YES}}"

  final_test_run:
    ran_command: "pytest"
    result: "ALL PASSED ✅"
```

**VERIFY Phase**:
```yaml
verify_phase:
  automated_checks:
    - check: "pytest"
      result: "{{PASSED|FAILED}}"
      output: "{{SUMMARY}}"

    - check: "black --check ."
      result: "{{PASSED|FAILED}}"

    - check: "mypy src/"
      result: "{{PASSED|FAILED}}"

    - check: "flake8 src/"
      result: "{{PASSED|FAILED}}"

  code_review:
    - checklist_item: "DRY - No duplication"
      status: "✅ PASSED"
    - checklist_item: "Functions <20 lines"
      status: "✅ PASSED"
    - checklist_item: "Clear variable names"
      status: "✅ PASSED"
    - checklist_item: "Type hints on all signatures"
      status: "✅ PASSED"

  completeness_check:
    - item: "All requirements implemented"
      status: "✅ COMPLETE"
    - item: "Edge cases tested"
      status: "✅ COMPLETE"
    - item: "Error handling implemented"
      status: "✅ COMPLETE"
```

**COMMIT Phase**:
```yaml
commit_phase:
  files_staged:
    - "{{FILE_1}}"
    - "{{FILE_2}}"

  commit_message: |
    {{TYPE}}: {{DESCRIPTION}}

    {{OPTIONAL_BODY}}

    Evidence:
    - Tests: {{COUNT}} passing
    - Quality: All checks passed
    - Coverage: {{PERCENTAGE}}%

  commit_hash: "{{HASH}}"
  verification: "git log -1 --oneline"
```

---

### Implementation Progress

```yaml
implementation_tracking:
  features_to_implement:
    - feature: "{{FEATURE_1}}"
      status: "{{PENDING|IN_PROGRESS|COMPLETE}}"
      files:
        - file: "{{FILE_1}}"
          status: "{{STATUS}}"
          test_coverage: "{{PERCENTAGE}}%"
        - file: "{{FILE_2}}"
          status: "{{STATUS}}"
          test_coverage: "{{PERCENTAGE}}%"

    - feature: "{{FEATURE_2}}"
      status: "{{STATUS}}"
      files:
        - file: "{{FILE_3}}"
          status: "{{STATUS}}"
```

---

## 📋 TEST ENGINEER WORK

### Test Strategy

```yaml
test_strategy:
  coverage_target: "{{PERCENTAGE}}%"  # e.g., 90%
  current_coverage: "{{PERCENTAGE}}%"

  test_pyramid:
    unit_tests:
      count: {{COUNT}}
      coverage: "{{PERCENTAGE}}%"
      files: ["{{TEST_FILE_1}}", "{{TEST_FILE_2}}"]

    integration_tests:
      count: {{COUNT}}
      coverage: "{{PERCENTAGE}}%"
      files: ["{{TEST_FILE_3}}"]

    e2e_tests:
      count: {{COUNT}}
      files: ["{{TEST_FILE_4}}"]
```

### Test Cases

```yaml
test_cases:
  - test_id: "T001"
    component: "{{COMPONENT_NAME}}"
    scenario: "{{WHAT_IS_BEING_TESTED}}"
    test_type: "{{UNIT|INTEGRATION|E2E}}"
    test_file: "{{FILE_PATH}}"
    test_function: "{{FUNCTION_NAME}}"

    given: "{{PRECONDITIONS}}"
    when: "{{ACTION}}"
    then: "{{EXPECTED_RESULT}}"

    status: "{{PASSING|FAILING|NOT_IMPLEMENTED}}"
    coverage_contribution: "{{LINES_COVERED}}"

  - test_id: "T002"
    component: "{{COMPONENT}}"
    scenario: "{{SCENARIO}}"
    test_type: "{{TYPE}}"
    # ... (same structure)
```

### Edge Cases Tested

```yaml
edge_cases:
  - case: "{{EDGE_CASE_DESCRIPTION}}"
    test_id: "{{TEST_ID}}"
    tested: "{{YES|NO}}"
    result: "{{PASSED|FAILED}}"

  - case: "Empty input"
    test_id: "T010"
    tested: "YES"
    result: "PASSED"

  - case: "Null input"
    test_id: "T011"
    tested: "YES"
    result: "PASSED"

  - case: "Very large input (>1M items)"
    test_id: "T012"
    tested: "YES"
    result: "PASSED"
```

### Security Tests

```yaml
security_tests:
  owasp_top_10:
    - vulnerability: "SQL Injection"
      test_id: "SEC001"
      tested: "{{YES|NO}}"
      result: "{{PASSED|FAILED}}"
      mitigation: "{{HOW_PREVENTED}}"

    - vulnerability: "XSS (Cross-Site Scripting)"
      test_id: "SEC002"
      tested: "{{YES|NO}}"
      result: "{{PASSED|FAILED}}"
      mitigation: "{{HOW_PREVENTED}}"

    - vulnerability: "Authentication Bypass"
      test_id: "SEC003"
      tested: "{{YES|NO}}"
      result: "{{PASSED|FAILED}}"
```

### Performance Tests

```yaml
performance_tests:
  - test_id: "PERF001"
    scenario: "{{WHAT_IS_BEING_MEASURED}}"
    requirement: "{{PERFORMANCE_REQUIREMENT}}"  # e.g., "Latency <100ms"
    actual: "{{MEASURED_VALUE}}"
    status: "{{PASSED|FAILED}}"

  - test_id: "PERF002"
    scenario: "Load test - 100 req/s for 1 minute"
    requirement: "No errors, <100ms p95 latency"
    actual: "0 errors, 85ms p95 latency"
    status: "PASSED"
```

---

## 🔗 HANDOFF TO GARDEN TENDING

### Quality Metrics

```yaml
quality_summary:
  test_coverage: "{{PERCENTAGE}}%"
  test_count: "{{TOTAL_TESTS}}"
  tests_passing: "{{PASSING_TESTS}}"
  tests_failing: "{{FAILING_TESTS}}"

  code_quality:
    - check: "black"
      status: "{{PASSED|FAILED}}"
    - check: "mypy"
      status: "{{PASSED|FAILED}}"
    - check: "flake8"
      status: "{{PASSED|FAILED}}"

  technical_debt:
    - item: "{{DEBT_ITEM_1}}"
      severity: "{{LOW|MEDIUM|HIGH}}"
      recommended_action: "{{ACTION}}"

    - item: "{{DEBT_ITEM_2}}"
      severity: "{{SEVERITY}}"
      recommended_action: "{{ACTION}}"

  refactoring_opportunities:
    - opportunity: "{{DESCRIPTION}}"
      location: "{{FILE}}:{{LINE}}"
      type: "{{DRY|NAMING|COMPLEXITY}}"
```

---

## 📊 KNOWLEDGE GRAPH UPDATES

```yaml
knowledge_nodes:
  - node_id: "IMPL_{{FEATURE}}_{{TIMESTAMP}}"
    node_type: "Implementation"
    label: "{{FEATURE_NAME}} implemented"
    description: |
      Implemented {{FEATURE}} following TDD cycle.
      {{COUNT}} tests, {{COVERAGE}}% coverage.
    confidence: 1.0
    evidence: |
      - Tests: {{COUNT}} passing (pytest output)
      - Coverage: {{PERCENTAGE}}% (coverage report)
      - Quality: All checks passed (black, mypy, flake8)
    created_by: "senior-developer"
    created_at: "{{TIMESTAMP}}"
```

---

## 🚨 ISSUES ENCOUNTERED

```yaml
issues:
  - issue_id: "ISS001"
    description: "{{WHAT_WENT_WRONG}}"
    impact: "{{IMPACT}}"
    resolution: "{{HOW_RESOLVED}}"
    prevention: "{{HOW_TO_PREVENT_FUTURE}}"

  - issue_id: "ISS002"
    description: "Performance test failed - latency 150ms vs requirement 100ms"
    impact: "Blocks completion"
    resolution: "Added caching layer - reduced latency to 85ms"
    prevention: "Add performance tests earlier in TDD cycle"
```

---

## 🎯 SUCCESS METRICS

```yaml
success_metrics:
  implementation_complete:
    - criterion: "All features implemented"
      status: "{{✅ COMPLETE | ⏳ IN PROGRESS}}"
    - criterion: "Test coverage ≥{{TARGET}}%"
      status: "{{STATUS}}"
    - criterion: "All quality checks pass"
      status: "{{STATUS}}"
    - criterion: "All tests pass"
      status: "{{STATUS}}"

  quality_gates:
    - gate: "No failing tests"
      status: "{{✅ PASSED | ❌ FAILED}}"
    - gate: "Coverage ≥{{TARGET}}%"
      status: "{{STATUS}}"
    - gate: "No security vulnerabilities"
      status: "{{STATUS}}"
    - gate: "Performance requirements met"
      status: "{{STATUS}}"
```

---

*This context memory ensures continuity and quality across the Implementation workflow.*

**Template Version**: v1.0.0
**Last Updated**: {{LAST_UPDATED}}
