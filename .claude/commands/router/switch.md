---
description: Manually switch to a different triad
---

# Switch Triad

Manually override routing and switch to a specific triad. This bypasses the grace period and immediately activates the specified triad.

**Usage**: `/switch-triad [triad-name]`

**Available triads**:
- `idea-validation` - Research and validate new ideas
- `design` - Create ADRs and design solutions
- `implementation` - Write production code
- `garden-tending` - Refactor and improve quality
- `deployment` - Create releases and deploy

**Example**:
```
/switch-triad implementation
```

```python
from triads.router.cli import RouterCLI
import sys

# Get triad name from command arguments
if len(sys.argv) < 2:
    print("❌ Usage: /switch-triad [triad-name]")
else:
    triad_name = sys.argv[1]
    cli = RouterCLI()
    print(cli.switch_triad(triad_name))
```
