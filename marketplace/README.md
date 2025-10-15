# Triads Marketplace

Official marketplace for the [triads](https://github.com/reliable-agents-ai/triads) Claude Code plugin.

## What is Triads?

Triads helps you organize complex work into phases (called "triads"). Each triad has specialized agents that work together and automatically hand off context to the next phase.

## Installation

```bash
# Add marketplace
/plugin marketplace add github:reliable-agents-ai/triads/marketplace

# Install triads plugin
/plugin install triads
```

## Usage

```bash
# In any project
cd ~/your-project
claude code

# Generate custom workflow
> /generate-triads

# Restart session
exit
claude code

# Use your workflow
> Start [TriadName]: [task]
```

## Documentation

- [User Guide](https://github.com/reliable-agents-ai/triads/blob/main/docs/USER_GUIDE.md)
- [Architecture Decisions](https://github.com/reliable-agents-ai/triads/blob/main/docs/ARCHITECTURE_DECISIONS.md)
- [Release Notes](https://github.com/reliable-agents-ai/triads/blob/main/RELEASE_NOTES_v0.3.0.md)

## Support

- [Issues](https://github.com/reliable-agents-ai/triads/issues)
- [Discussions](https://github.com/reliable-agents-ai/triads/discussions)
