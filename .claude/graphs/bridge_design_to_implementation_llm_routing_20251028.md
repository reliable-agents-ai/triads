# Bridge Design-to-Implementation: LLM Routing System

**Bridge ID**: `bridge_llm_routing_20251028`
**Created**: 2025-10-28
**Created By**: design-bridge
**Source Triad**: Design & Architecture
**Target Triad**: Implementation
**Confidence**: 0.95

---

## Design Quality Assessment

**Overall Score**: 92/100

**Breakdown**:
- **Completeness**: 95/100 - All key decisions documented (ADR-001), validation comprehensive
- **Clarity**: 90/100 - Clear implementation approach, some ambiguity around fallback edge cases
- **Testability**: 90/100 - Test cases defined, acceptance criteria clear
- **Constitutional Compliance**: 95/100 - Evidence-based, transparent, user-directed

**Ready for Implementation**: ✅ YES

---

## Executive Summary

**What to Build**: Replace brittle keyword-based routing with intelligent LLM routing using Claude Code headless mode.

**Core Architecture**: subprocess call to `claude -p` with JSON output, brief skill discovery from filesystem, timeout-based fallback to keyword matching.

**Key Constraint**: <2s latency, <$0.01 per call, graceful degradation on failure.

**Why This Matters**: Current routing fails on 60%+ of bug investigation requests (e.g., "investigate why command isn't there"). LLM routing understands intent, handles any phrasing, auto-discovers user-added brief skills.

**Critical ADR**: ADR-001 (Claude Code Headless) - User explicitly directed this approach. Constitutional requirement to follow user direction.

---

## Critical Architectural Decisions

### ADR-001: Claude Code Headless for LLM Routing

**Decision**: Use `claude -p` subprocess calls instead of Anthropic Python SDK.

**Why**:
1. **User Authority**: Explicitly requested by user (highest authority level)
2. **Superior Features**: Built-in cost tracking, duration tracking, session persistence, tool restrictions
3. **Security**: `--allowedTools ""` prevents routing from accessing files/executing code
4. **Constitutional**: User direction = absolute authority

**Implementation Impact**:
- Use `subprocess.run(["claude", "-p", prompt, "--output-format", "json", ...])`
- Parse JSON response with `total_cost_usd`, `duration_ms`, `result` fields
- Set timeout=2s, fallback to keyword matching on timeout
- Validate JSON schema before using routing decision

**Reference**: `.claude/graphs/adr_001_claude_code_headless_20251028.md`

---

## Implementation Roadmap

### Phase 1: Create Core LLM Routing Module (HIGH PRIORITY)

**Task**: Create `triads/llm_routing.py` with subprocess pattern

**File**: `triads/llm_routing.py` (NEW - ~250 lines)

**Key Functions**:
```python
def route_to_brief_skill(
    user_input: str,
    skills_dir: Path,
    confidence_threshold: float = 0.70,
    timeout: int = 2
) -> Dict[str, Any]:
    """
    Route user input to brief skill using Claude Code headless.

    Returns:
        {
            "brief_skill": "bug-brief",
            "confidence": 0.95,
            "reasoning": "User is investigating missing functionality...",
            "cost_usd": 0.003,
            "duration_ms": 1234
        }
    """
    # 1. Discover brief skills from filesystem
    # 2. Build routing prompt (system + user message)
    # 3. Call claude -p via subprocess
    # 4. Parse JSON response
    # 5. Validate confidence threshold
    # 6. Return routing decision

def _discover_brief_skills(skills_dir: Path) -> Dict[str, Dict[str, str]]:
    """Find all *-brief.md files, extract name/description/purpose."""
    pass

def _build_routing_system_prompt() -> str:
    """System prompt: routing agent instructions, JSON format, confidence scale."""
    pass

def _build_routing_user_message(user_input: str, brief_skills: Dict) -> str:
    """User message: request + available skills."""
    pass

def _keyword_fallback(user_input: str, brief_skills: Dict) -> Dict[str, Any]:
    """Fallback to simple keyword matching if LLM fails."""
    pass
```

**Acceptance Criteria**:
- [ ] Function exists: `route_to_brief_skill()`
- [ ] Subprocess call: `claude -p` with `--output-format json --allowedTools ""`
- [ ] Timeout: 2s with fallback to keyword matching
- [ ] JSON validation: Check schema before returning
- [ ] Cost tracking: Include `cost_usd` in response
- [ ] Duration tracking: Include `duration_ms` in response
- [ ] Error handling: Catch subprocess exceptions, log, fallback

**Estimated Time**: 4 hours

---

### Phase 2: Update Entry Point Analyzer (HIGH PRIORITY)

**Task**: Replace keyword matching with LLM routing

**File**: `triads/entry_point_analyzer.py` (~211 lines → ~150 lines)

**Changes**:
```python
# REMOVE: WORK_TYPE_PATTERNS dict (lines 9-40)
# REMOVE: match_work_type_to_triad() function (lines 41-68)

# ADD: Import LLM routing
from triads.llm_routing import route_to_brief_skill

# MODIFY: Main function
def analyze_entry_points(config_path: Path):
    # ... existing code ...

    # OLD:
    # matches = match_work_type_to_triad(triad_purpose)

    # NEW:
    routing_decision = route_to_brief_skill(
        user_input=triad_purpose,
        skills_dir=config_path.parent / "skills" / domain
    )

    if routing_decision["confidence"] >= 0.70:
        brief_skill = routing_decision["brief_skill"]
        # ... proceed with generation ...
    else:
        # Ask user for clarification
        print(f"Unclear routing (confidence: {routing_decision['confidence']})")
        print(f"Did you mean: {routing_decision['brief_skill']}?")
```

**Acceptance Criteria**:
- [ ] WORK_TYPE_PATTERNS removed
- [ ] match_work_type_to_triad() removed
- [ ] Imports route_to_brief_skill()
- [ ] Calls LLM routing instead of keyword matching
- [ ] Handles low confidence (<0.70) by asking user
- [ ] Logs cost and duration for monitoring

**Estimated Time**: 2 hours

---

### Phase 3: Update Coordination Skill Generator (MEDIUM PRIORITY)

**Task**: Remove dependency on `routing_decision_table.yaml`, use LLM routing

**File**: `triads/coordination_skill_generator.py` (~300 lines)

**Changes**:
```python
# REMOVE: YAML loading
# routing_config = yaml.safe_load(routing_table_path)

# ADD: LLM routing call per brief skill
from triads.llm_routing import route_to_brief_skill

for brief_skill_file in brief_skills:
    # Sample input for this brief skill (use description as example)
    sample_input = extract_sample_input(brief_skill_file)

    # Route to determine target triad
    routing_decision = route_to_brief_skill(
        user_input=sample_input,
        skills_dir=skills_dir
    )

    # Generate coordination skill with routing metadata
    generate_coordination_skill(
        brief_skill=brief_skill_file.stem,
        target_triad=routing_decision.get("target_triad", "implementation"),
        entry_agent=routing_decision.get("entry_agent", "senior-developer")
    )
```

**Acceptance Criteria**:
- [ ] No longer reads `routing_decision_table.yaml`
- [ ] Calls `route_to_brief_skill()` for each brief skill
- [ ] Uses routing decision to populate coordination skill template
- [ ] Handles custom domain brief skills (auto-discovered)

**Estimated Time**: 3 hours

---

### Phase 4: Delete Obsolete Routing Table (LOW PRIORITY)

**Task**: Remove `routing_decision_table.yaml` (no longer needed)

**File**: `.claude/routing_decision_table.yaml` (DELETE)

**Why**: Brief skills are now discovered from filesystem, LLM determines routing dynamically.

**Acceptance Criteria**:
- [ ] File deleted: `.claude/routing_decision_table.yaml`
- [ ] No code references remaining (grep for `routing_decision_table`)
- [ ] Tests updated to not expect this file

**Estimated Time**: 30 minutes

---

### Phase 5: Comprehensive Testing (HIGH PRIORITY)

**Task**: Create tests for LLM routing system

**File**: `tests/test_llm_routing.py` (NEW - ~400 lines)

**Test Cases**:

**Test 1: Bug Investigation Routing**
```python
def test_route_bug_investigation():
    """User says 'investigate why command isn't there' → bug-brief."""
    routing_decision = route_to_brief_skill(
        "investigate why /upgrade-to-templates command isn't there",
        skills_dir
    )
    assert routing_decision["brief_skill"] == "bug-brief"
    assert routing_decision["confidence"] >= 0.85
    assert "cost_usd" in routing_decision
    assert routing_decision["cost_usd"] < 0.01
    assert routing_decision["duration_ms"] < 2000
```

**Test 2: Feature Request Routing**
```python
def test_route_feature_request():
    """User says 'add dark mode' → feature-brief."""
    routing_decision = route_to_brief_skill(
        "can we add dark mode to the UI",
        skills_dir
    )
    assert routing_decision["brief_skill"] == "feature-brief"
    assert routing_decision["confidence"] >= 0.90
```

**Test 3: Ambiguous Request (Low Confidence)**
```python
def test_route_ambiguous_request():
    """User says 'system is slow' → low confidence (0.70-0.85)."""
    routing_decision = route_to_brief_skill(
        "the system is slow",
        skills_dir
    )
    assert 0.70 <= routing_decision["confidence"] <= 0.85
    # Should route to bug-brief or refactor-brief (either valid)
```

**Test 4: Custom Brief Skill Discovery**
```python
def test_route_custom_brief_skill():
    """Custom 'market-analysis-brief' auto-discovered."""
    # Create custom brief skill
    create_custom_brief_skill("market-analysis-brief")

    routing_decision = route_to_brief_skill(
        "need to analyze market trends for Q4",
        skills_dir
    )
    assert routing_decision["brief_skill"] == "market-analysis-brief"
    assert routing_decision["confidence"] >= 0.90
```

**Test 5: Timeout Fallback**
```python
@mock.patch('subprocess.run', side_effect=subprocess.TimeoutExpired('claude', 2))
def test_route_timeout_fallback(mock_run):
    """LLM times out → fallback to keyword matching."""
    routing_decision = route_to_brief_skill(
        "fix the bug",
        skills_dir,
        timeout=2
    )
    # Should fallback successfully
    assert routing_decision["brief_skill"] == "bug-brief"
    assert routing_decision["confidence"] == 0.60  # Lower for fallback
    assert routing_decision["reasoning"] == "Fallback keyword matching"
```

**Test 6: Cost Validation**
```python
def test_route_cost_tracking():
    """Verify cost tracking works."""
    routing_decision = route_to_brief_skill(
        "investigate bug",
        skills_dir
    )
    assert "cost_usd" in routing_decision
    assert isinstance(routing_decision["cost_usd"], float)
    assert routing_decision["cost_usd"] < 0.01
```

**Test 7: Performance Validation**
```python
def test_route_performance():
    """Verify 95% of calls complete in <2s."""
    durations = []
    for _ in range(20):
        routing_decision = route_to_brief_skill(
            "random test input",
            skills_dir
        )
        durations.append(routing_decision["duration_ms"])

    # 95th percentile should be <2000ms
    assert sorted(durations)[18] < 2000
```

**Acceptance Criteria**:
- [ ] All 7 test cases pass
- [ ] Coverage ≥80% of llm_routing.py
- [ ] Tests include edge cases (timeout, errors, no skills)
- [ ] Tests validate cost and performance requirements
- [ ] Mock subprocess for fast test execution

**Estimated Time**: 5 hours

---

## File Structure Changes

### Files to CREATE

```
triads/
└── llm_routing.py (NEW - ~250 lines)
    - route_to_brief_skill()
    - _discover_brief_skills()
    - _build_routing_system_prompt()
    - _build_routing_user_message()
    - _keyword_fallback()

tests/
└── test_llm_routing.py (NEW - ~400 lines)
    - Test cases 1-7 as described above
```

### Files to MODIFY

```
triads/
├── entry_point_analyzer.py
│   - Remove: WORK_TYPE_PATTERNS (lines 9-40)
│   - Remove: match_work_type_to_triad() (lines 41-68)
│   - Add: import route_to_brief_skill
│   - Modify: analyze_entry_points() to use LLM routing
│
└── coordination_skill_generator.py
    - Remove: YAML loading
    - Add: LLM routing calls per brief skill
    - Modify: generate_coordination_skill() to use routing metadata
```

### Files to DELETE

```
.claude/
└── routing_decision_table.yaml (DELETE)
```

---

## Security Requirements

### REQ-SEC-1: Tool Restriction
**Risk**: LLM routing could access files or execute code unintentionally

**Mitigation**:
```python
subprocess.run([
    "claude",
    "-p", user_message,
    "--append-system-prompt", system_prompt,
    "--output-format", "json",
    "--allowedTools", "",  # ✅ Empty = no tools allowed
])
```

**Test**: Verify routing never accesses filesystem or executes commands

---

### REQ-SEC-2: Timeout Protection
**Risk**: Slow LLM calls block user indefinitely

**Mitigation**:
```python
try:
    result = subprocess.run(
        [...],
        timeout=2  # ✅ Max 2 seconds
    )
except subprocess.TimeoutExpired:
    # Fallback to keyword matching
    return _keyword_fallback(user_input, brief_skills)
```

**Test**: Verify fallback works when LLM times out

---

### REQ-SEC-3: JSON Validation
**Risk**: LLM returns invalid JSON, causing crashes

**Mitigation**:
```python
try:
    response = json.loads(result.stdout)
    routing_decision = json.loads(response["result"])

    # Validate schema
    assert "brief_skill" in routing_decision
    assert "confidence" in routing_decision
    assert 0.0 <= routing_decision["confidence"] <= 1.0
except (json.JSONDecodeError, AssertionError, KeyError) as e:
    logger.error(f"Invalid JSON from LLM: {e}")
    return _keyword_fallback(user_input, brief_skills)
```

**Test**: Verify malformed JSON triggers fallback

---

## Performance Requirements

### PERF-1: Latency <2 Seconds
**Target**: 95% of routing calls complete in <2s

**Measurement**: Monitor `duration_ms` field from response

**Mitigation**:
- Timeout set to 2s
- Fallback to keyword matching on timeout
- Optimize prompt size (cache brief skill descriptions)

---

### PERF-2: Cost <$0.01 per Call
**Target**: Average cost <$0.005 per call

**Measurement**: Monitor `total_cost_usd` field from response

**Mitigation**:
- Use efficient model (claude-3-5-sonnet)
- Keep prompts small (~500 tokens)
- Cache routing decisions for identical queries

---

## Testing Checklist

### Functional Tests
- [ ] Bug investigation requests route to bug-brief (confidence ≥0.85)
- [ ] Feature requests route to feature-brief (confidence ≥0.90)
- [ ] Refactoring requests route to refactor-brief (confidence ≥0.90)
- [ ] Ambiguous requests return low confidence (0.70-0.85)
- [ ] Custom brief skills auto-discovered and routable

### Performance Tests
- [ ] 95% of calls complete in <2000ms (duration_ms check)
- [ ] Average cost <$0.005 per call (total_cost_usd check)
- [ ] Timeout fallback works (timeout=2s test)

### Security Tests
- [ ] Tool restrictions enforced (`--allowedTools ""`)
- [ ] No file access during routing (monitoring)
- [ ] JSON validation prevents crashes (malformed input test)

### Edge Case Tests
- [ ] No brief skills found → default routing with confidence 0.50
- [ ] LLM API failure → fallback to keyword matching
- [ ] Multiple skills match → user clarification prompt
- [ ] Empty user input → error handling

---

## Quality Gates

**Before claiming Phase 1-5 complete**:

1. **Code Quality**:
   - [ ] All functions ≤20 lines (extract if longer)
   - [ ] No magic numbers (use constants)
   - [ ] Clear variable names (no abbreviations)
   - [ ] Docstrings for all public functions
   - [ ] Type hints for function signatures

2. **Testing**:
   - [ ] Coverage ≥80% for llm_routing.py
   - [ ] All 7 test cases pass
   - [ ] Edge cases covered (timeout, errors, no skills)
   - [ ] Performance tests validate <2s latency
   - [ ] Cost tests validate <$0.01 per call

3. **Security**:
   - [ ] Tool restrictions verified
   - [ ] Timeout protection tested
   - [ ] JSON validation tested
   - [ ] No hardcoded secrets (use environment variables)

4. **Documentation**:
   - [ ] README updated with LLM routing explanation
   - [ ] ADR-001 referenced in code comments
   - [ ] Example usage shown in docstrings
   - [ ] Troubleshooting guide for common issues

5. **Constitutional Compliance**:
   - [ ] Evidence-based: All claims tested empirically
   - [ ] Thorough: All edge cases handled
   - [ ] Transparent: Logging for cost/duration/failures
   - [ ] User authority: ADR-001 implemented exactly as designed

---

## Reference Documentation

### ADRs (Design Decisions)
- **ADR-001**: Claude Code Headless for LLM Routing
  - File: `.claude/graphs/adr_001_claude_code_headless_20251028.md`
  - Key: Use `claude -p` subprocess, not Anthropic SDK
  - Authority: User explicit direction

### Validation (Research)
- **Validation Document**: `.claude/graphs/validation_claude_code_headless_20251028.md`
  - Evidence: 4 verification methods
  - Confidence: 95%
  - Key findings: Headless superior to SDK (8/10 features)

### Bug Brief (Original Problem)
- **Bug Brief**: `.claude/graphs/bug_brief_llm_routing_20251028.md`
  - Problem: Keyword routing fails 60%+ of time
  - Solution: LLM routing with brief skill discovery
  - Impact: coordinate-bug.md was never generated

### External Documentation
- **Claude Code Headless Docs**: https://docs.claude.com/en/docs/claude-code/headless
  - CLI parameters, JSON output format, examples

---

## Implementation Entry Point

**Start Here**: Phase 1 - Create `triads/llm_routing.py`

**First Function to Write**: `route_to_brief_skill()`

**First Test to Write**: `test_route_bug_investigation()`

**Development Workflow**:
1. Write test (RED)
2. Implement function (GREEN)
3. Refactor for quality (REFACTOR)
4. Run all tests
5. Check coverage ≥80%
6. Commit with conventional commit message

**Example First Commit**:
```bash
git commit -m "feat(routing): Add LLM-based routing with Claude Code headless

Implements route_to_brief_skill() using subprocess call to 'claude -p'.
Includes timeout protection, fallback to keyword matching, and cost tracking.

- triads/llm_routing.py: New module with routing functions
- tests/test_llm_routing.py: Test for bug investigation routing
- Coverage: 85% of llm_routing.py

Refs: ADR-001 (Claude Code Headless)
Evidence: User explicit direction + validation doc"
```

---

## Success Criteria

**Definition of Done** (entire implementation):

1. ✅ `triads/llm_routing.py` created with all functions
2. ✅ `triads/entry_point_analyzer.py` updated (keyword matching removed)
3. ✅ `triads/coordination_skill_generator.py` updated (YAML dependency removed)
4. ✅ `.claude/routing_decision_table.yaml` deleted
5. ✅ All 7 test cases pass
6. ✅ Coverage ≥80% for llm_routing.py
7. ✅ Performance validated: 95% <2s latency
8. ✅ Cost validated: Average <$0.005 per call
9. ✅ Security validated: Tool restrictions enforced
10. ✅ Documentation updated
11. ✅ All existing tests still pass (61 tests)
12. ✅ Constitutional compliance verified

**Acceptance**: User validates that "investigate why command isn't there" correctly routes to bug-brief with confidence ≥0.85.

---

## Risk Register

### Risk 1: LLM Latency Exceeds 2s
**Likelihood**: Medium
**Impact**: High (poor UX)
**Mitigation**: Timeout + fallback to keyword matching
**Monitoring**: Track `duration_ms` field

### Risk 2: Cost Accumulation
**Likelihood**: Low
**Impact**: Medium (budget)
**Mitigation**: Monitor `total_cost_usd`, alert if >$0.01
**Monitoring**: Daily cost reports

### Risk 3: JSON Parsing Failures
**Likelihood**: Low
**Impact**: Medium (routing fails)
**Mitigation**: JSON schema validation + retry + fallback
**Monitoring**: Log all parsing errors

### Risk 4: Subprocess Failures
**Likelihood**: Low
**Impact**: High (routing breaks)
**Mitigation**: Exception handling + fallback + logging
**Monitoring**: Alert on subprocess errors

---

## For Senior Developer

### Quick Start

1. **Read ADR-001 first**: `.claude/graphs/adr_001_claude_code_headless_20251028.md`
   - Understand WHY Claude Code headless (user authority)
   - Review subprocess pattern (lines 130-166)
   - Note security requirements (tool restrictions)

2. **Create `triads/llm_routing.py`**:
   - Start with `route_to_brief_skill()` function
   - Implement subprocess call pattern from ADR-001
   - Add timeout protection (2s)
   - Add fallback to keyword matching

3. **Write tests first** (TDD):
   - `tests/test_llm_routing.py`
   - Test 1: Bug investigation routing
   - Verify: confidence ≥0.85, cost <$0.01, duration <2s

4. **Update entry point analyzer**:
   - Remove `WORK_TYPE_PATTERNS` dict
   - Replace `match_work_type_to_triad()` with LLM routing call
   - Test with "investigate why command isn't there"

5. **Validate performance and cost**:
   - Run 20 routing calls
   - Check: 95% <2s, average cost <$0.005

### Common Pitfalls to Avoid

❌ **Don't use Anthropic SDK** - User explicitly requested Claude Code headless
❌ **Don't skip timeout** - Must have 2s timeout with fallback
❌ **Don't ignore tool restrictions** - Must use `--allowedTools ""`
❌ **Don't skip JSON validation** - LLM could return malformed JSON
❌ **Don't hardcode secrets** - Use environment variables (none needed for Claude CLI)

### Questions?

Refer to:
- ADR-001 for design rationale
- Validation doc for research evidence
- Bug brief for original problem context

---

**Bridge Complete**: 2025-10-28
**Handoff To**: Implementation Triad (senior-developer)
**Entry Point**: Phase 1 - Create `triads/llm_routing.py`
**Estimated Total Time**: 14.5 hours (across 5 phases)
