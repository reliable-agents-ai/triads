---
description: Show routing statistics from telemetry
---

# Router Statistics

Display statistics from routing telemetry logs:
- **Total routes** - Number of routing decisions made
- **Method breakdown** - Semantic, LLM, manual percentages
- **Top triads** - Most frequently routed triads
- **Performance metrics** - Average confidence and latency

This helps you:
- Understand routing patterns
- Identify if semantic routing is working well
- See which triads you use most
- Monitor performance (latency)

```python
from triads.router.cli import RouterCLI

cli = RouterCLI()
print(cli.stats())
```

## Example Output

```
📊 Router Statistics
==================================================

Total Routes: 47

Method Breakdown:
  semantic    :  32 (68.1%)
  llm         :  12 (25.5%)
  manual      :   3 (6.4%)

Top Triads:
  implementation      :  22 (46.8%)
  design              :  15 (31.9%)
  idea-validation     :  10 (21.3%)

Performance:
  Average Confidence: 88%
  Average Latency: 12.3ms

Log file: ~/.claude/router/logs/routing_telemetry.jsonl
```

## Interpreting the Stats

- **High semantic %** (>70%) = Router is confident, embeddings working well
- **High LLM %** (>30%) = Many ambiguous prompts, may need better examples
- **High manual %** (>10%) = LLM failing or unavailable, check API key
- **Low latency** (<20ms) = Good performance
- **High latency** (>50ms) = May need optimization or LLM timeout issues
