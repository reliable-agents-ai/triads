---
description: Mark a lesson as incorrect to decrease its confidence
tags: [knowledge, contradiction, confidence]
---

# Contradict Incorrect Lesson

This command allows you to mark a lesson as incorrect when you discover it
gives wrong advice. Contradicting a lesson decreases its confidence and may
auto-deprecate it if confidence drops too low.

## Usage

```
/knowledge-contradict <lesson-id-or-label> [reason]
```

## What This Does

1. **Finds the lesson** by ID or label (fuzzy search)
2. **Decreases confidence** using Bayesian update (contradiction outcome)
   - Formula: `confidence * 0.40` (60% decrease)
3. **Updates flags**:
   - Sets `needs_validation: true` if confidence drops below 0.70
   - Sets `deprecated: true` if confidence drops below 0.30
   - Adds `contradiction_count += 1`
   - Records `last_contradicted_at` timestamp
4. **Records reason** in `contradiction_reasons` array
5. **Saves graph** with updated confidence score

## When to Use

- **Lesson is wrong** - the advice doesn't apply or is incorrect
- **Better approach exists** - you've found a superior method
- **Context changed** - the lesson no longer applies
- **User reported issue** - feedback indicates the lesson is problematic

## Example

```
/knowledge-contradict "Database Migration Pattern" "Doesn't work for NoSQL databases"
```

**Output:**
```
⚠️  Contradicted: Database Migration Pattern
   Confidence: 0.75 → 0.30 (↓ 45%)
   Status: active → deprecated
   Reason: Doesn't work for NoSQL databases
   Graph: design_graph.json updated

💡 This lesson is now deprecated and will not be shown again.
```

## Auto-Deprecation

If confidence drops below **0.30** after contradiction:
- Lesson is marked `deprecated: true`
- Lesson will **NOT** appear in future injections
- Lesson remains in graph for historical record
- Deprecation reason is recorded

## Confidence Bands After Contradiction

| Before | After (×0.40) | Status |
|--------|---------------|--------|
| 0.95   | 0.38          | needs_validation |
| 0.75   | 0.30          | **deprecated** ⚠️ |
| 0.50   | 0.20          | **deprecated** ⚠️ |

## Notes

- **Strong signal**: Contradiction is the strongest negative signal
- **Provide reason**: Helps understand why the lesson failed
- **Irreversible deprecation**: Once deprecated, manual graph edit needed to restore
- **Historical record**: Deprecated lessons stay in graph but aren't shown

## See Also

- `/knowledge-validate` - Validate a correct lesson
- `/knowledge-review-uncertain` - Review uncertain lessons before contradicting
- `/knowledge-status` - Check confidence scores
