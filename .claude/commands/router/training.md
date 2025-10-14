---
description: Toggle training mode on or off
---

# Training Mode

Enable or disable training mode for the router.

**Usage**: `/router-training [on|off]`

## What is Training Mode?

Training mode helps you learn how the routing system works by:
- Showing routing suggestions with reasoning
- Requesting confirmation before routing
- Tracking your confirmations (graduation at 50)
- Helping you understand semantic vs LLM routing

## When to use it

- **Enable** when you're new to the triad system
- **Enable** if you want explicit control over routing
- **Disable** once you trust the automatic routing (after ~50 confirmations)

## Commands

```bash
/router-training on   # Enable training mode
/router-training off  # Disable training mode
```

**Note**: This change is for the current session only. For persistent changes, edit `~/.claude/router/config.json`

```python
from triads.router.cli import RouterCLI
import sys

if len(sys.argv) < 2:
    print("❌ Usage: /router-training [on|off]")
else:
    mode = sys.argv[1]
    cli = RouterCLI()
    print(cli.training_mode(mode))
```
