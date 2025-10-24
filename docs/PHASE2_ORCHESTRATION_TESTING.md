# Phase 2 Orchestration Testing Guide

**Version**: Phase 2 - Orchestrator Activation
**Status**: COMPLETE
**Date**: 2025-10-24

## Overview

Phase 2 activates the orchestration system by enhancing the Supervisor with work request detection and orchestration triggering capabilities. This guide documents how to test the activation in a real Claude Code environment.

## Implementation Summary

### Components Implemented

1. **Work Request Detection** (`detect_work_request()`)
   - Classifies user messages as work requests or Q&A
   - Routes all work through idea-validation (single entry point per ADR-007)
   - Supports 5 work types: feature, bug, refactor, design, release

2. **Enhanced Supervisor Instructions** (`format_supervisor_instructions()`)
   - Includes work detection protocol with pattern matching
   - Provides Q&A vs work classification guidance
   - Maintains emergency bypass (`/direct`) functionality

3. **Error Handling**
   - Hook catches all exceptions to prevent crashes
   - Falls back to minimal instructions on catastrophic failure
   - Logs errors to stderr for debugging

### Test Coverage

- **Unit Tests**: 105 passing
  - 17 work request detection tests
  - 14 orchestrator activation tests
  - 20 orchestrator instruction tests
  - 43 context passing tests
  - 11 integration tests

- **Coverage**: 84% (context_passing.py)

## Testing in Claude Code

### Prerequisites

1. **Verify hook is installed**:
   ```bash
   cat .claude/settings.json | jq '.hooks.userPromptSubmit'
   # Should show: "hooks/user_prompt_submit.py"
   ```

2. **Verify workflow configuration**:
   ```bash
   cat .claude/settings.json | jq '.triad_system.workflow'
   # Should show entry_point: "idea-validation"
   ```

### Test Scenarios

#### Scenario 1: Q&A Request (Should NOT Orchestrate)

**User Input**:
```
What is OAuth2?
```

**Expected Behavior**:
1. Supervisor receives instructions with detection protocol
2. Supervisor classifies as Q&A (matches "what is" pattern)
3. Supervisor answers directly WITHOUT invoking triads
4. User receives informational response

**Verification**:
- No Task tool invocations
- Direct answer provided
- No triad workflow initiated

---

#### Scenario 2: Feature Request (Should Orchestrate)

**User Input**:
```
Implement OAuth2 authentication
```

**Expected Behavior**:
1. Supervisor receives instructions with detection protocol
2. Supervisor classifies as FEATURE work request ("implement" pattern)
3. Supervisor identifies entry point: idea-validation triad
4. Supervisor uses Task tool to invoke research-analyst
5. Orchestration begins

**Verification**:
```
Expected Supervisor response:
"I've detected this as a feature request. I'll invoke the idea-validation triad to begin the workflow..."

[Task tool invocation to research-analyst with OAuth2 context]
```

---

#### Scenario 3: Bug Fix Request (Should Orchestrate)

**User Input**:
```
Fix the router crash when handling invalid input
```

**Expected Behavior**:
1. Classified as BUG work request ("fix" + "crash" patterns)
2. Routes to idea-validation (all work enters there per ADR-007)
3. Invokes research-analyst to analyze bug scope

**Verification**:
- Task tool invoked
- User sees: "Detected as bug fix request, invoking idea-validation..."

---

#### Scenario 4: Refactoring Request (Should Orchestrate)

**User Input**:
```
Refactor the messy code in router module
```

**Expected Behavior**:
1. Classified as REFACTOR ("refactor" + "messy code" patterns)
2. Routes to idea-validation
3. Workflow initiated

---

#### Scenario 5: Ambiguous Request (Should Ask for Clarification)

**User Input**:
```
The OAuth2 implementation
```

**Expected Behavior**:
1. No clear Q&A or work patterns detected
2. Supervisor asks user for clarification:
   ```
   "Are you asking about the OAuth2 implementation (Q&A), or would you like me to implement OAuth2 (work request)?"
   ```

**Verification**:
- No automatic routing
- User prompted to clarify intent

---

#### Scenario 6: Emergency Bypass (Should Skip Routing)

**User Input**:
```
/direct What are the current triads?
```

**Expected Behavior**:
1. Supervisor detects `/direct` prefix
2. Skips all routing logic
3. Answers directly without workflows

**Verification**:
- No triad invocation
- Direct response provided

---

### Debugging Failed Tests

#### Issue: Work Request Not Detected

**Symptoms**:
- User says "Implement X" but Supervisor doesn't invoke triad

**Debug Steps**:
1. Check Supervisor instructions received:
   ```bash
   # Look at hook output
   python hooks/user_prompt_submit.py
   ```

2. Verify pattern matches:
   ```python
   from user_prompt_submit import detect_work_request
   detect_work_request("Implement OAuth2")
   # Should return: {'type': 'feature', 'triad': 'idea-validation', ...}
   ```

3. Check workflow config exists:
   ```bash
   cat .claude/settings.json | jq '.triad_system.workflow.entry_point'
   # Should output: "idea-validation"
   ```

---

#### Issue: Hook Crashes

**Symptoms**:
- No Supervisor instructions appear
- Error in Claude Code console

**Debug Steps**:
1. Check stderr:
   ```bash
   tail -f ~/.claude-code/logs/hooks.log
   ```

2. Test hook manually:
   ```bash
   python hooks/user_prompt_submit.py
   # Should output JSON with hookSpecificOutput
   ```

3. Verify Python dependencies:
   ```bash
   python -c "import json, sys; print('OK')"
   ```

---

## Performance Benchmarks

**From Integration Tests** (tests/test_integration_phase1.py):

| Operation | Target | Actual | Margin |
|-----------|--------|--------|--------|
| Work Request Detection | N/A | <1ms | N/A |
| Context Extraction | 100ms | ~15ms | 6.6x faster |
| Context Formatting | 50ms | ~3ms | 16.6x faster |
| Instruction Generation | 50ms | ~2ms | 25x faster |

**Total Hook Overhead**: <20ms (imperceptible to user)

---

## Known Limitations

### 1. Hook Cannot See User Message

The `UserPromptSubmit` hook runs BEFORE Claude processes the user message, so it cannot directly see what the user typed. Instead, the hook injects Supervisor instructions that teach the Supervisor HOW to detect work requests when it receives the message.

**Implication**: Detection happens at runtime in Supervisor, not in the hook.

### 2. Pattern-Based Detection

Work request detection uses keyword patterns, not semantic understanding.

**Edge Cases**:
- "Let's not implement OAuth2" might incorrectly match "implement"
- "What approach should we take to implement X?" could match both Q&A ("what approach") and work ("implement")

**Mitigation**: Q&A patterns checked FIRST (priority), so most cases handled correctly.

### 3. Single Entry Point Enforcement

ALL work enters through idea-validation, even urgent bugs or trivial refactors.

**Design Rationale**: Enforced by Standing Order 1 per ADR-007. Idea-validation adapts thoroughness internally.

---

## Manual Testing Checklist

Before approving Phase 2, verify:

- [ ] Q&A request answered directly (no triad invocation)
- [ ] Feature request triggers idea-validation
- [ ] Bug request triggers idea-validation
- [ ] Refactor request triggers idea-validation
- [ ] Ambiguous request prompts for clarification
- [ ] Emergency bypass (`/direct`) skips routing
- [ ] Hook handles missing config gracefully
- [ ] Hook never crashes (fallback works)
- [ ] Supervisor instructions include all ROE (1-4)
- [ ] Training mode protocol included

---

## Next Steps: Phase 3

Phase 3 will focus on:
1. **End-to-End Testing**: Test complete triad execution with orchestration
2. **Real Triad Validation**: Verify with actual idea-validation, implementation triads
3. **HITL Gate Testing**: Test human-in-the-loop approval flows
4. **Handoff Testing**: Verify automatic triad-to-triad handoffs

---

## Troubleshooting

### Common Issues

**Issue**: "Supervisor not following instructions"
- **Cause**: Instructions too complex or conflicting
- **Fix**: Simplify ROE, add explicit examples

**Issue**: "Work request classified incorrectly"
- **Cause**: Pattern ambiguity
- **Fix**: Add pattern to appropriate list, ensure Q&A priority

**Issue**: "Hook output not appearing"
- **Cause**: JSON formatting error
- **Fix**: Verify `output_hook_result()` produces valid JSON

---

## References

- **ADR-007**: Orchestration Architecture (Main Claude as orchestrator)
- **ADR-008**: Context Passing Protocol (summaries, not full outputs)
- **Phase 1 Implementation**: Context passing utilities (`src/triads/context_passing.py`)
- **Hook Implementation**: `hooks/user_prompt_submit.py`
- **Test Suite**: `tests/test_work_request_detection.py`, `tests/test_orchestrator_activation.py`

---

**Status**: Ready for test-engineer review and approval for Phase 3.
