---
description: Reset router state
---

# Reset Router

Clear the router state file, resetting:
- Session ID
- Active triad
- Grace period counters
- Turn count
- Training mode confirmations

This is useful for:
- Starting a fresh routing session
- Clearing corrupted state
- Testing routing behavior

⚠️ **Warning**: This will clear your current session context. You'll start with a clean slate.

```python
from triads.router.cli import RouterCLI

cli = RouterCLI()
print(cli.reset())
```
