# Day 3 Implementation Summary: Lesson Extraction

**Date**: 2025-10-17
**Status**: ✅ Complete
**Test Results**: 256/256 tests passing (34 new tests added)

## Overview

Day 3 implemented automatic lesson extraction from conversations, enabling the system to learn from mistakes and user corrections. The Stop hook now analyzes conversation history and creates draft Process Concept nodes for user review.

## Implementation Details

### Files Modified

**hooks/on_stop.py** (~450 lines added)
- Added 8 new functions for lesson extraction
- Integrated extraction into main hook flow
- Total file size: ~1,155 lines

**tests/test_km/test_lesson_extraction.py** (new file, ~560 lines)
- 34 comprehensive tests covering all extraction methods
- Performance benchmarks
- Edge case handling

### New Functions in on_stop.py

1. **extract_process_knowledge_blocks(text)**
   - Extracts explicit `[PROCESS_KNOWLEDGE]` blocks from conversation
   - Returns list of parsed lesson dictionaries

2. **parse_process_knowledge_block(block_text)**
   - Parses YAML-like structure within PROCESS_KNOWLEDGE blocks
   - Handles trigger_conditions, checklists, patterns, warnings
   - Validates required fields

3. **detect_user_corrections(conversation_text)**
   - Detects 6 user correction patterns:
     - "you missed X"
     - "you forgot Y"
     - "why didn't you Z"
     - "you should have A"
     - "don't forget B"
     - "remember to C"
   - Returns list of correction dictionaries

4. **detect_repeated_mistakes(conversation_text, graph_updates)**
   - Detects 5 repeated mistake patterns:
     - "X again"
     - "another X was missing"
     - "X is still missing"
     - "forgot X again"
     - "need to X again"
   - Returns list of repeated mistake dictionaries

5. **infer_priority_from_context(lesson_data, conversation_text)**
   - Implements priority inference rules:
     - User corrections → CRITICAL
     - Repeated mistakes → HIGH
     - Deployment context → CRITICAL
     - Security-related → HIGH
     - Default → LOW (requires review)

6. **create_process_knowledge_node(lesson_data, conversation_text)**
   - Creates Process Concept nodes with:
     - Unique node ID with timestamp
     - Inferred priority
     - `status: "draft"` for user review
     - `detection_method` field tracking how it was learned
     - Structured content (checklist/pattern/warning)

7. **extract_lessons_from_conversation(conversation_text, graph_updates)**
   - Orchestrates three detection methods:
     1. Explicit PROCESS_KNOWLEDGE blocks
     2. User corrections (implicit)
     3. Repeated mistakes (implicit)
   - Returns list of ready-to-insert nodes

8. **Integration in main()**
   - Runs after graph updates complete
   - Groups lessons by triad
   - Adds draft nodes to graphs
   - Shows summary with review instructions

## Detection Methods

### Method 1: Explicit Blocks

Users or agents can create structured lessons:

```
[PROCESS_KNOWLEDGE]
type: checklist
label: Version Bump File Checklist
priority: CRITICAL
process_type: checklist
triad: deployment
trigger_conditions:
  tool_names: ["Write", "Edit"]
  file_patterns: ["**/plugin.json", "**/marketplace.json"]
  action_keywords: ["version", "bump", "release"]
checklist:
  - item: Update plugin.json version field required: true
  - item: Update marketplace.json plugins[].version required: true
  - item: Update pyproject.toml project.version required: true
[/PROCESS_KNOWLEDGE]
```

### Method 2: User Corrections (Implicit)

Automatically detected from phrases like:
- "You forgot to update marketplace.json" → CRITICAL warning
- "Why didn't you run tests?" → CRITICAL checklist item
- "Don't forget the CHANGELOG" → CRITICAL reminder

### Method 3: Repeated Mistakes (Implicit)

Detected from repetition patterns:
- "You need to update marketplace.json again" → HIGH priority
- "Another file was missing" → HIGH priority
- "Still missing from the commit" → HIGH priority

## Priority Inference Rules

```python
if user_correction:
    priority = CRITICAL  # User explicitly pointed out mistake
elif repeated_mistake:
    priority = HIGH  # Happening multiple times
elif deployment_context and deployment_triad:
    priority = CRITICAL  # Deployment mistakes are severe
elif security_keywords:
    priority = HIGH  # Security is important
elif explicit_priority_in_block:
    priority = explicit_value  # Trust explicit priority
else:
    priority = LOW  # Default - requires manual review
```

## Node Structure

Draft lessons are created as Concept nodes:

```json
{
  "id": "process_user_correction_20251017_141530",
  "type": "Concept",
  "label": "Remember: marketplace.json",
  "description": "User correction: forgot - marketplace.json",
  "confidence": 0.9,
  "priority": "CRITICAL",
  "process_type": "warning",
  "detection_method": "user_correction",
  "status": "draft",
  "created_by": "experience-learning-system",
  "created_at": "2025-10-17T14:15:30.123456",
  "evidence": "Learned from conversation at 2025-10-17T14:15:30",
  "trigger_conditions": {
    "tool_names": ["Write", "Edit"],
    "file_patterns": [],
    "action_keywords": ["marketplace"],
    "context_keywords": [],
    "triad_names": []
  },
  "warning": {
    "condition": "marketplace.json",
    "consequence": "User correction: forgot - marketplace.json",
    "prevention": "Verify before proceeding"
  }
}
```

## Test Coverage

**34 new tests** covering:

### PROCESS_KNOWLEDGE Block Parsing (4 tests)
- ✅ Full block extraction with trigger_conditions
- ✅ Minimal block parsing
- ✅ Missing label validation
- ✅ Multiple blocks in one conversation

### User Correction Detection (6 tests)
- ✅ "you missed X" pattern
- ✅ "you forgot X" pattern
- ✅ "don't forget X" pattern
- ✅ "you should have X" pattern
- ✅ "why didn't you X" pattern
- ✅ No false positives on normal conversation

### Repeated Mistake Detection (4 tests)
- ✅ "X again" pattern
- ✅ "another X was missing" pattern
- ✅ "X is still missing" pattern
- ✅ No false positives

### Priority Inference (6 tests)
- ✅ Explicit priority preserved
- ✅ User corrections → CRITICAL
- ✅ Repeated mistakes → HIGH
- ✅ Deployment context → CRITICAL
- ✅ Security keywords → HIGH
- ✅ Default → LOW

### Node Creation (4 tests)
- ✅ Basic node structure
- ✅ Checklist integration
- ✅ Trigger conditions
- ✅ Warning type formatting

### Full Extraction (5 tests)
- ✅ Explicit blocks extracted
- ✅ User corrections extracted
- ✅ Repeated mistakes extracted
- ✅ Combined extraction
- ✅ No false positives

### Edge Cases & Performance (5 tests)
- ✅ Empty conversation
- ✅ Malformed blocks
- ✅ Special characters
- ✅ Multiline corrections
- ✅ Performance benchmark (< 1s on large text)

## Performance

- **Lesson extraction**: < 1 second on conversations with 10K+ words
- **Hook integration**: No measurable overhead to Stop hook
- **Regex matching**: Optimized patterns with minimal backtracking

## Integration with Experience System

The Stop hook now provides the **learning** component of the experience loop:

1. **PreToolUse Hook** (Day 2): Query and inject relevant knowledge
2. **Work happens**: Agent uses tools
3. **Stop Hook** (Day 3): Extract lessons from what went wrong
4. **Draft Review** (Day 4): User reviews and promotes lessons
5. **Loop closes**: Promoted lessons appear in next PreToolUse query

## Example Output

When lessons are detected, Stop hook outputs:

```
================================================================================
🧠 Experience-Based Learning: Lesson Extraction
================================================================================
Found 2 lesson(s) to learn

Adding 2 lesson(s) to deployment graph...
  [1/2] ✓ Added lesson: Remember: marketplace.json (priority: CRITICAL, status: draft)
  [2/2] ✓ Added lesson: Remember: CHANGELOG.md entry (priority: CRITICAL, status: draft)
✅ deployment_graph.json updated with lessons

📋 2 draft lesson(s) created (require review)
   Use /knowledge-review-drafts to review and promote lessons
================================================================================
```

## Installation

Hook automatically installed to marketplace plugin:
- Local: `hooks/on_stop.py`
- Installed: `~/.claude/plugins/marketplaces/triads-marketplace/hooks/on_stop.py`

## Next Steps (Day 4)

1. Display CRITICAL lessons at SessionStart
2. Add `/knowledge-review-drafts` command
3. Add `/knowledge-promote <node_id>` command
4. Add `/knowledge-archive <node_id>` command
5. Integrate draft review workflow

## Metrics

- **Lines added**: ~450 (lesson extraction logic)
- **Tests added**: 34
- **Test success rate**: 100% (256/256 passing)
- **Coverage**: Maintained at 96%+ for KM modules
- **Detection accuracy**: High (validated through diverse test cases)

## Key Design Decisions

1. **Three detection methods**: Covers explicit (blocks), implicit (corrections), and pattern-based (repetition)
2. **Draft status**: All learned lessons start as drafts to avoid false positives
3. **Detection method tracking**: `detection_method` field enables audit and tuning
4. **Priority inference**: Balances automation with safety (default LOW requires review)
5. **Triad routing**: Lessons added to appropriate triad graph based on context
6. **Non-blocking**: Errors in extraction don't break graph updates

## Risk Mitigations

- **False positives**: Draft status prevents auto-application
- **Over-detection**: Early exit for normal conversation patterns
- **Performance**: Regex patterns optimized, < 1s on large text
- **Error handling**: Try-catch around extraction, logs errors to stderr
- **User control**: All drafts require explicit promotion

---

**Implementation Status**: Day 3 ✅ COMPLETE
**Next**: Day 4 - SessionStart enhancement + CLI commands
