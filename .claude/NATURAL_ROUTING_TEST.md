# Natural Routing Test Plan

## Hypothesis
Claude Code can naturally suggest appropriate triads without any router code, using only CLAUDE.md documentation in system context.

## Test Setup
1. ✅ Added TRIAD SYSTEM CONFIGURATION to CLAUDE.md (lines 1134-1209)
2. Exit current session (context is tainted - we discussed triads extensively)
3. Start fresh `claude code` session
4. Test with user requests that should trigger routing suggestions

## Test Scenarios

### Scenario 1: Feature Idea (Should suggest Idea Validation)
**User says**: "I'm thinking about adding AI-powered code suggestions to the triad system"

**Expected**: Claude naturally suggests `Start Idea Validation: AI-powered code suggestions`

**Actual**: [Fill in after test]

---

### Scenario 2: Architecture Question (Should suggest Design)
**User says**: "How should we structure the plugin system for extensibility?"

**Expected**: Claude naturally suggests `Start Design: Plugin system architecture`

**Actual**: [Fill in after test]

---

### Scenario 3: Pure Q&A (Should NOT suggest routing)
**User says**: "What's the difference between a bridge agent and a regular agent?"

**Expected**: Claude answers the question without suggesting a triad invocation

**Actual**: [Fill in after test]

---

### Scenario 4: Implementation Work (Should suggest Implementation)
**User says**: "Let's build the OAuth2 integration feature"

**Expected**: Claude suggests `Start Implementation: OAuth2 integration`

**Actual**: [Fill in after test]

---

### Scenario 5: Code Quality (Should suggest Garden Tending)
**User says**: "The router code has a lot of duplication, we should clean it up"

**Expected**: Claude suggests `Start Garden Tending: Router code consolidation`

**Actual**: [Fill in after test]

---

### Scenario 6: Release (Should suggest Deployment)
**User says**: "We're ready to release v0.3.0"

**Expected**: Claude suggests `Start Deployment: v0.3.0`

**Actual**: [Fill in after test]

---

## Success Criteria

✅ **Pass**: Claude naturally suggests correct triad in 5/6 work scenarios
✅ **Pass**: Claude does NOT suggest routing for Q&A scenario
✅ **Pass**: Suggestions follow pattern: "This sounds like {Triad} work. Would you like me to `{Command}`?"

❌ **Fail**: Claude doesn't recognize triad patterns
❌ **Fail**: Claude suggests routing for Q&A
❌ **Fail**: Claude requires prompting to check triads

## Test Date
2025-10-15

## Changes Made Before Test
- **Original CLAUDE.md**: 1,209 lines, routing at line 1,134
- **New CLAUDE.md**: 204 lines (83% reduction), routing at line 101
- **Moved out**: 780 lines of Claude Code tutorial → docs/CLAUDE_CODE_INTEGRATION_GUIDE.md
- **Added**: Specific example for "Is there any maintenance work needed?" → Garden Tending
- **Style**: "Military command" - actionable directives, not optional documentation

## Test Results
[To be filled in after fresh session test]

## Decision Point
- If test passes → Delete router entirely (5,500 lines), keep only CLAUDE.md documentation
- If test fails → Investigate why, possibly need minimal routing hints
