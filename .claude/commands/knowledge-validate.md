---
description: Manually validate an uncertain lesson to increase its confidence
tags: [knowledge, validation, confidence]
---

# Validate Uncertain Lesson

This command allows you to manually validate a lesson that has low confidence
(marked with `needs_validation: true`). Validating a lesson increases its
confidence score and marks it as trusted.

## Usage

```
/knowledge-validate <lesson-id-or-label>
```

## What This Does

1. **Finds the lesson** by ID or label (fuzzy search)
2. **Increases confidence** using Bayesian update (validation outcome)
   - Formula: `confidence * 1.20` (20% increase)
3. **Updates flags**:
   - Sets `needs_validation: false` if confidence rises above 0.70
   - Adds `validation_count += 1`
   - Records `last_validated_at` timestamp
4. **Saves graph** with updated confidence score

## When to Use

- **You've verified** a lesson is correct through experience
- **Testing confirmed** the lesson's advice is sound
- **User feedback** validates the lesson's value
- **Multiple successes** give you confidence in the lesson

## Example

```
/knowledge-validate Version Bump Checklist
```

**Output:**
```
✅ Validated: Version Bump Checklist
   Confidence: 0.65 → 0.78 (↑ 13%)
   Status: needs_validation → active
   Graph: deployment_graph.json updated
```

## Notes

- **Fuzzy search**: You don't need exact lesson ID, label matching works
- **Threshold**: Confidence ≥ 0.70 removes `needs_validation` flag
- **Multiple triads**: Searches all graphs if triad not specified
- **Idempotent**: Safe to validate multiple times (diminishing returns)

## See Also

- `/knowledge-contradict` - Mark a lesson as incorrect
- `/knowledge-review-uncertain` - Review all uncertain lessons
- `/knowledge-status` - See all lesson confidence scores
