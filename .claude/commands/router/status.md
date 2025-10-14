---
description: Show current router status and grace period info
---

# Router Status

Display the current state of the triad router including:
- Active triad
- Turn count (within grace period)
- Last activity timestamp
- Grace period status (active/inactive, turns/time remaining)
- Training mode status

```python
from triads.router.cli import RouterCLI

cli = RouterCLI()
print(cli.status())
```
