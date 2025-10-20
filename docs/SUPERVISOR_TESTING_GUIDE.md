# Supervisor Testing Guide (Phase 1)

**Status**: Phase 1 deployed and ready for real-world testing
**Date**: 2025-10-20
**Version**: v0.8.0-alpha.1 (Supervisor Phase 1)

---

## Overview

This guide helps you test the newly deployed Supervisor-first architecture (Phase 1). The Supervisor agent now intercepts all user messages and provides intelligent triage and routing.

## What to Expect

### Supervisor Behavior (Phase 1)

When you interact with Claude Code, the Supervisor will:

1. **Inject Instructions** - On every user message, Supervisor instructions are added to context
2. **Triage Messages** - Classify whether your message is Q&A or work
3. **Q&A Handling** - Answer informational questions directly
4. **Work Classification** - Identify problem type (bug, feature, performance, etc.)
5. **Training Mode** - Always confirm before routing to workflows
6. **Fallback Routing** - Use existing triad commands when workflow library not yet ready

### What Phase 1 Includes

✅ **Implemented**:
- Supervisor instructions injection (UserPromptSubmit hook)
- Triage logic (Q&A vs. work)
- Problem classification guidelines
- Training mode with confirmations
- Emergency bypass (`/direct` command)
- Triad atomicity enforcement

⏳ **Not Yet Implemented** (future phases):
- Automated problem classification (Phase 3)
- Workflow library (Phase 2)
- Semantic routing (Phase 3)
- Execution monitoring (Phase 4)
- Learning system (Phase 5)

---

## How to Activate Supervisor

### Method 1: Restart Claude Code (Recommended)

The Supervisor hook needs to be loaded when Claude Code starts:

1. **Save any work in progress**
2. **Quit Claude Code completely**
3. **Restart Claude Code**
4. **Open this project** (`triads`)
5. **Start a new chat session**

The Supervisor should now be active!

### Method 2: Reload Project

If you don't want to restart:

1. Close the current project
2. Reopen the `triads` project
3. Start a new chat session

---

## Testing Scenarios

### Test 1: Q&A (Should Answer Directly)

**Try asking**:
```
What is the Supervisor agent?
```

**Expected behavior**:
- Supervisor triages this as Q&A
- Answers directly using knowledge from supervisor.md
- NO workflow routing
- NO triad invocation

**Success criteria**:
- ✅ You get a direct answer about the Supervisor
- ✅ No mention of "would you like me to start..."
- ✅ Information is accurate (references ADR-007, training mode, etc.)

### Test 2: Bug Report (Should Suggest Workflow)

**Try reporting**:
```
There's a bug where the hook doesn't load on session start
```

**Expected behavior**:
- Supervisor classifies as "bug fix" work
- Explains it's a bug fix work request
- Suggests appropriate action (Phase 1: fallback to investigation)
- Asks for confirmation before proceeding
- Shows confidence and rationale

**Success criteria**:
- ✅ Identifies this as a "bug" problem type
- ✅ Suggests next action
- ✅ Asks for confirmation (training mode)
- ✅ Explains why this workflow was chosen

### Test 3: Feature Request (Should Suggest Workflow)

**Try requesting**:
```
Let's add support for parallel workflow execution
```

**Expected behavior**:
- Supervisor classifies as "feature" work
- Suggests `Start Idea Validation:` or `Start Design:`
- Asks for confirmation
- Shows confidence score

**Success criteria**:
- ✅ Identifies this as feature development
- ✅ Suggests appropriate triad routing
- ✅ Explains the reasoning

### Test 4: Emergency Bypass (Should Skip Supervisor)

**Try using bypass**:
```
/direct Just show me the contents of hooks/hooks.json
```

**Expected behavior**:
- Supervisor skipped entirely
- Direct conversational response
- Reads the file and shows contents
- No workflow routing

**Success criteria**:
- ✅ No Supervisor triage
- ✅ Direct answer
- ✅ File contents displayed

### Test 5: Triad Atomicity Check

**Try asking**:
```
Can we use just the senior-developer agent from the implementation triad?
```

**Expected behavior**:
- Supervisor explains triad atomicity
- References ADR-006
- Explains triads are atomic units
- Mentions they cannot be decomposed

**Success criteria**:
- ✅ Clear explanation of atomicity principle
- ✅ References military organizational patterns
- ✅ Explains why this isn't allowed

### Test 6: Training Mode Confirmation

**Try work request**:
```
We need to optimize the router's performance
```

**Expected behavior**:
- Classifies as "performance" work
- Shows confidence score (e.g., "High confidence: 0.95")
- Suggests workflow
- ASKS FOR CONFIRMATION before executing
- Shows rationale

**Success criteria**:
- ✅ Asks "Would you like me to..."
- ✅ Shows confidence
- ✅ Explains reasoning
- ✅ Waits for user approval

### Test 7: Mid-Conversation Context

**Try follow-up during ongoing conversation**:
```
[After discussing something]
What were we talking about again?
```

**Expected behavior**:
- Supervisor doesn't force routing
- Handles as Q&A in context
- Continues natural conversation
- No workflow interruption

**Success criteria**:
- ✅ Natural conversational response
- ✅ No forced routing
- ✅ Context maintained

---

## What to Look For

### Success Indicators

1. **Supervisor Instructions Visible**
   - Look for "🎯 SUPERVISOR MODE: ACTIVE" in session context
   - Should appear at start of session (or in system messages)

2. **Triage Working**
   - Q&A questions answered directly
   - Work requests classified correctly
   - Appropriate routing suggestions

3. **Training Mode Active**
   - Always asks for confirmation
   - Shows confidence scores
   - Explains reasoning

4. **Atomicity Enforced**
   - Never suggests decomposing triads
   - Always references intact triad composition
   - Emphasizes ADR-006

5. **Emergency Bypass Works**
   - `/direct` prefix skips Supervisor
   - Direct conversation mode
   - No workflow routing

### Warning Signs (Issues to Report)

1. ❌ **No Supervisor Context**
   - If you don't see Supervisor instructions
   - Hook may not be loading
   - Need to restart Claude Code

2. ❌ **Wrong Classification**
   - Q&A treated as work (forced routing)
   - Work treated as Q&A (missed routing opportunity)
   - Incorrect problem type identification

3. ❌ **No Training Mode**
   - Executes workflows without confirmation
   - Doesn't show confidence scores
   - Skips reasoning explanation

4. ❌ **Bypass Not Working**
   - `/direct` still triggers Supervisor
   - Can't skip routing when needed

5. ❌ **Triad Decomposition Suggested**
   - Supervisor suggests extracting individual agents
   - Violates atomicity principle
   - Critical architectural issue

---

## Debugging

### Check if Hook is Loaded

```bash
# Check if hook is registered
cat hooks/hooks.json | grep UserPromptSubmit

# Test hook execution
python3 hooks/user_prompt_submit.py | python3 -m json.tool | head -50
```

### Check Supervisor Context

Look for this in your Claude Code session:
```
🎯 SUPERVISOR MODE: ACTIVE
```

If you don't see this, the hook isn't firing.

### Check Hook Output

The hook should inject context that includes:
- Supervisor role description
- Triage logic (Q&A vs. work indicators)
- Triad Atomicity Principle
- Training mode instructions
- Emergency bypass (`/direct`)

### Force Hook Reload

If changes aren't appearing:
1. Quit Claude Code completely
2. Clear any cached plugin data (if applicable)
3. Restart Claude Code
4. Reopen project

---

## Known Limitations (Phase 1)

1. **No Workflow Library Yet**
   - Falls back to existing triad commands
   - Phase 2 will add proven workflow definitions

2. **Manual Classification**
   - Supervisor provides guidelines, not automation
   - Phase 3 will add semantic routing

3. **No Execution Monitoring**
   - Can't track workflow progress automatically
   - Phase 4 will add monitoring

4. **No Learning**
   - Doesn't improve from outcomes yet
   - Phase 5 will add learning system

5. **Limited Problem Types**
   - Only recognizes 6 problem types currently
   - More will be added as needed

---

## Feedback Collection

When testing, please note:

### What Worked Well
- Which scenarios worked as expected?
- What felt natural and helpful?
- What improved your workflow?

### What Didn't Work
- Which scenarios failed?
- What felt awkward or forced?
- What slowed you down?

### Classification Accuracy
- Did Supervisor correctly identify Q&A vs. work?
- Were problem types classified correctly?
- Any misrouting incidents?

### Training Mode
- Were confirmations helpful or annoying?
- Was rationale clear and useful?
- Right level of detail?

### Suggestions
- What would make this better?
- What's confusing?
- What's missing?

---

## Emergency Fallback

If Supervisor causes issues:

### Option 1: Use `/direct` Prefix

```
/direct [your message here]
```

This skips Supervisor entirely for that message.

### Option 2: Disable Hook Temporarily

Edit `hooks/hooks.json` and comment out UserPromptSubmit:

```json
{
  "hooks": {
    "SessionStart": [...],
    "// UserPromptSubmit": [...]
  }
}
```

Then restart Claude Code.

### Option 3: Revert Changes

```bash
git stash
# Or
git checkout HEAD hooks/user_prompt_submit.py hooks/hooks.json
```

Then restart Claude Code.

---

## Next Steps After Testing

Based on testing results:

1. **If working well**: Proceed to Phase 2 (Workflow Library)
2. **If issues found**: Fix Phase 1 issues first
3. **If needs adjustment**: Refine Supervisor behavior

Your feedback will shape Phase 2 development!

---

## Quick Reference

### Supervisor Commands

- **Normal message**: Supervisor triages automatically
- **Emergency bypass**: `/direct [message]`
- **Check context**: Look for "🎯 SUPERVISOR MODE: ACTIVE"

### Expected Behaviors

| Your Input | Supervisor Should |
|-----------|------------------|
| Question (what/how/explain) | Answer directly (Q&A) |
| "There's a bug..." | Classify as bug, suggest workflow |
| "Let's add..." | Classify as feature, suggest routing |
| "Optimize..." | Classify as performance, suggest workflow |
| "Refactor..." | Classify as refactoring, suggest workflow |
| "/direct ..." | Skip Supervisor, answer directly |

### Key Principles

- **Triads are atomic** - never decomposed
- **Training mode active** - always confirms
- **Emergency bypass** - `/direct` available
- **Q&A is valid** - not everything needs routing

---

**Ready to test?** Start a new Claude Code session and try the scenarios above!

**Questions?** See docs/adrs/ADR-SUPERVISOR-ARCHITECTURE.md for architecture details.
