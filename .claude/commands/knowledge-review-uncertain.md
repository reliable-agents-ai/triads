---
description: Review all lessons that need validation (confidence < 0.70)
tags: [knowledge, review, validation, confidence]
---

# Review Uncertain Lessons

This command shows all lessons with low confidence that need validation or
review. These are lessons the system is uncertain about and may need your input.

## Usage

```
/knowledge-review-uncertain [triad]
```

## What This Shows

Lists all lessons where:
- `needs_validation: true` (confidence < 0.70)
- Not deprecated
- Grouped by confidence band

For each lesson:
- **Label** and **ID**
- **Confidence score** (percentage)
- **Triad** (source)
- **Statistics**: success/failure/contradiction counts
- **Created date** and **source** (how it was learned)

## Output Format

```
═══════════════════════════════════════════════════════════════
# ⚠️  UNCERTAIN LESSONS NEEDING REVIEW
═══════════════════════════════════════════════════════════════

Found 3 lesson(s) needing validation:

## 🔴 Low Confidence (< 0.50)

1. Database Connection Pool Pattern
   ID: db_pool_pattern_001
   Confidence: 45% | Triad: design
   Source: agent_inference | Created: 2025-10-15
   Statistics: 1 success, 2 failures, 0 contradictions

   💡 Action: Review and validate or contradict this lesson

## 🟡 Medium Confidence (0.50-0.69)

2. Version Bump Checklist
   ID: version_bump_checklist
   Confidence: 65% | Triad: deployment
   Source: user_correction | Created: 2025-10-10
   Statistics: 3 successes, 1 failure, 0 contradictions

   💡 Action: Validate to increase confidence above 70%

3. ADR Writing Pattern
   ID: adr_pattern_002
   Confidence: 68% | Triad: design
   Source: repeated_mistake | Created: 2025-10-12
   Statistics: 2 successes, 0 failures, 0 contradictions

   💡 Action: One more success will push this above 70%

═══════════════════════════════════════════════════════════════

## Summary by Triad

- deployment: 1 uncertain lesson
- design: 2 uncertain lessons

## Recommended Actions

1. **Validate** lessons you trust: `/knowledge-validate <id-or-label>`
2. **Contradict** incorrect lessons: `/knowledge-contradict <id-or-label> <reason>`
3. **Wait** for natural learning through usage outcomes

═══════════════════════════════════════════════════════════════
```

## Confidence Bands Explained

| Band | Confidence | Meaning | Action |
|------|------------|---------|--------|
| 🔴 Low | < 0.50 | Very uncertain | Review urgently |
| 🟡 Medium | 0.50-0.69 | Needs validation | Validate or wait |
| 🟢 High | 0.70-0.89 | Trusted | No action needed |
| ✅ Very High | ≥ 0.90 | Highly trusted | No action needed |

## Filtering by Triad

To review uncertain lessons in a specific triad:

```
/knowledge-review-uncertain deployment
/knowledge-review-uncertain design
```

## Natural vs Manual Validation

**Natural Learning (Preferred):**
- Lessons gain confidence through successful application
- System detects outcomes automatically
- Organic, evidence-based confidence growth

**Manual Validation (When Needed):**
- You have strong evidence the lesson is correct
- Testing confirmed the lesson works
- Want to fast-track a low-confidence lesson

## Notes

- **Automatically updated**: Confidence changes as lessons are used
- **Self-correcting**: Failed lessons lose confidence automatically
- **No action required**: Most lessons will naturally reach high confidence
- **Review periodically**: Check uncertain lessons every few weeks

## See Also

- `/knowledge-validate` - Manually validate a lesson
- `/knowledge-contradict` - Mark a lesson as incorrect
- `/knowledge-status` - See all lessons and confidence scores
