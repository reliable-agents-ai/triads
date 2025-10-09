# Contributing to Triad Generator

Thank you for your interest in contributing to Triad Generator! This document provides guidelines and information for contributors.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Submitting Changes](#submitting-changes)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Release Process](#release-process)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of experience level, background, or identity.

### Expected Behavior

- Be respectful and considerate in all interactions
- Welcome newcomers and help them get started
- Provide constructive feedback
- Focus on what's best for the project and community
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Trolling, insulting/derogatory comments, and personal attacks
- Publishing others' private information without permission
- Any conduct that could reasonably be considered inappropriate

### Enforcement

Violations may result in temporary or permanent ban from the project. Report issues to the project maintainers.

---

## How Can I Contribute?

### Reporting Bugs

Before creating a bug report:
1. Check existing issues to avoid duplicates
2. Use the latest version to see if the bug persists
3. Collect relevant information (OS, Python version, error messages)

**Good bug reports include:**
- Clear, descriptive title
- Steps to reproduce the issue
- Expected vs actual behavior
- Error messages and logs
- System information (OS, Python version, Claude Code version)
- Screenshots if applicable

### Suggesting Enhancements

Enhancement suggestions are welcome! Please include:
- Clear description of the proposed feature
- Use cases and examples
- Why this would be valuable to users
- Potential implementation approach (optional)

### Areas for Contribution

**High-Impact Areas:**
- New domain templates (RFP writing, data analysis, etc.)
- Enhanced context compression algorithms
- Additional constitutional principle patterns
- Knowledge graph visualization tools
- Performance optimizations

**Documentation:**
- Usage examples for different domains
- Video tutorials or guides
- Translations
- API documentation improvements

**Testing:**
- Test coverage improvements
- Edge case testing
- Integration tests
- Performance benchmarks

---

## Development Setup

### Prerequisites

- **Python 3.10+** with pip
- **[Claude Code CLI](https://docs.claude.com/en/docs/claude-code)** installed
- **Git** for version control
- **NetworkX** library

### Setup Steps

```bash
# 1. Fork and clone the repository
git clone https://github.com/reliable-agents-ai/triads.git
cd triad-generator

# 2. Create a test project directory
mkdir test-project
cd test-project

# 3. Run the installer
../setup-complete.sh

# 4. Test the installation
claude code
> /generate-triads
```

### Development Environment

```bash
# Install dependencies
pip3 install networkx

# For testing
pip3 install pytest pytest-cov

# For linting
pip3 install flake8 black
```

---

## Project Structure

```
triad-generator/
├── .claude/                        # Generated Claude Code setup
│   ├── commands/
│   │   └── generate-triads.md     # Slash command
│   ├── generator/
│   │   ├── agents/                # Meta-agents
│   │   │   ├── domain-researcher.md
│   │   │   ├── workflow-analyst.md
│   │   │   └── triad-architect.md
│   │   └── lib/
│   │       └── templates.py       # Code generation templates
│   ├── graphs/                    # Knowledge graphs (runtime)
│   ├── constitutional/            # Quality enforcement
│   └── README.md                  # System documentation
│
├── docs/                          # User documentation
├── research/                      # Research notes (not in repo)
├── setup-complete.sh              # Installation script
├── install-triads.sh              # Bootstrap installer
├── uninstall.sh                   # Safe removal script
├── upgrade.sh                     # Upgrade script
├── README.md                      # Main documentation
├── CLAUDE.md                      # Claude Code integration guide
├── LICENSE                        # MIT License
└── CONTRIBUTING.md                # This file
```

---

## Coding Standards

### Python Code

**Style:**
- Follow PEP 8 conventions
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Maximum line length: 100 characters

**Example:**
```python
def compress_knowledge_graph(graph, max_nodes=20):
    """
    Compress a knowledge graph to the most important nodes.

    Args:
        graph (networkx.Graph): The source knowledge graph
        max_nodes (int): Maximum nodes to preserve (default: 20)

    Returns:
        networkx.Graph: Compressed graph with top-scoring nodes

    Uses importance scoring: confidence × degree × recency × type_priority
    """
    # Implementation here
    pass
```

**Formatting:**
```bash
# Auto-format with black
black .claude/generator/lib/templates.py

# Check with flake8
flake8 .claude/generator/lib/templates.py
```

### Markdown Files (Agent Definitions)

**Structure:**
- Use YAML frontmatter for metadata
- Clear section headers with ##
- Code examples in fenced blocks with language tags
- Consistent formatting for constitutional principles

**Example:**
```markdown
---
name: example-agent
triad: discovery
role: specialist
---

# Example Agent

## Identity & Purpose
You are **Example Agent** in the **Discovery Triad**...

## Constitutional Principles
1. **Thoroughness Over Speed** - Always verify before claiming
```

### Commit Messages

**Format:**
```
<type>: <subject>

<body>

<footer>
```

**Types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `refactor:` Code refactoring
- `test:` Test additions or changes
- `chore:` Build/tooling changes

**Example:**
```
feat: Add context compression for bridge agents

Implement importance scoring algorithm that ranks nodes based on:
- Confidence scores
- Graph degree (connections)
- Recency (temporal metadata)
- Node type priority

Reduces graph size by ~80% while preserving critical context.

Closes #42
```

---

## Submitting Changes

### Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow coding standards
   - Add tests if applicable
   - Update documentation

3. **Test thoroughly**
   ```bash
   # Test the generator
   cd test-project
   claude code
   > /generate-triads

   # Run any automated tests
   pytest
   ```

4. **Commit with clear messages**
   ```bash
   git add .
   git commit -m "feat: your feature description"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create Pull Request**
   - Use a clear, descriptive title
   - Reference any related issues
   - Describe what changed and why
   - Include testing details
   - Add screenshots if applicable

### Pull Request Checklist

- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated (README, CLAUDE.md, etc.)
- [ ] No new warnings generated
- [ ] Tests added/updated and passing
- [ ] Dependent changes merged and published

---

## Testing Guidelines

### Manual Testing

**Generator Triad:**
```bash
# Test end-to-end generation
claude code
> /generate-triads

# Test with different workflows:
# - Software development
# - RFP/bid writing
# - Lead generation
# - Data analysis
```

**Generated Triads:**
```bash
# Test generated agents work correctly
> Start Discovery: analyze authentication system
> Start Design: plan OAuth2 integration
> Start Implementation: build OAuth2 flow

# Verify:
# - Knowledge graphs created
# - Bridge agents preserve context
# - Constitutional checks enforced
```

### Automated Testing (Future)

```python
# Example test structure
def test_domain_researcher_questions():
    """Test that Domain Researcher asks minimum 5 questions"""
    # Test implementation
    pass

def test_knowledge_graph_compression():
    """Test graph compression preserves top 20 nodes"""
    # Test implementation
    pass
```

### Testing Checklist

- [ ] Generator runs without errors
- [ ] All three meta-agents activate in sequence
- [ ] Generated files are valid markdown/Python
- [ ] Knowledge graphs created with correct schema
- [ ] Bridge agents compress context correctly
- [ ] Constitutional hooks enforce principles
- [ ] Documentation accurate and complete

---

## Documentation

### What to Document

**Code Changes:**
- Update inline comments
- Add docstrings to new functions
- Update templates.py if adding new templates

**User-Facing Changes:**
- Update README.md
- Update CLAUDE.md for /command changes
- Add examples to docs/EXAMPLES.md
- Update docs/USAGE.md if workflow changes

**Architecture Changes:**
- Update docs/ARCHITECTURE.md
- Document design decisions
- Update research attribution if applicable

### Documentation Style

**Clarity:**
- Write for beginners (assume no prior knowledge)
- Use examples liberally
- Explain the "why" not just the "how"

**Structure:**
- Start with overview/summary
- Use clear section headers
- Include code examples
- Provide troubleshooting guidance

**Example:**
```markdown
## Bridge Agents

### What They Are
Bridge agents participate in two triads simultaneously...

### Why They Matter
Context loss is the #1 problem in multi-agent systems...

### How They Work
```python
# When exiting Triad A:
compress_graph(source_graph, top_n=20)
```

### Example
```bash
> Start Design: plan OAuth2
[Knowledge Synthesizer bridges Discovery context forward]
```
```

---

## Release Process

### For Maintainers

Creating a new release is automated via GitHub Actions. See [RELEASE_GUIDE.md](RELEASE_GUIDE.md) for complete instructions.

**Quick Release Steps:**

1. **Update VERSION file**
   ```bash
   echo "0.0.2" > VERSION
   git add VERSION
   git commit -m "Bump version to 0.0.2"
   git push
   ```

2. **Create and push tag**
   ```bash
   git tag v0.0.2
   git push origin v0.0.2
   ```

3. **GitHub Actions automatically:**
   - Builds release tarball
   - Generates checksums
   - Creates GitHub Release
   - Attaches downloadable assets

**Monitor release:** https://github.com/reliable-agents-ai/triads/actions

**Pre-release checklist:**
- [ ] All tests passing
- [ ] Documentation updated
- [ ] CHANGELOG prepared (if applicable)
- [ ] Tested on clean system
- [ ] Breaking changes documented

For detailed release instructions, see [RELEASE_GUIDE.md](RELEASE_GUIDE.md).

---

## Questions?

- **General questions**: Open a [GitHub Discussion](https://github.com/reliable-agents-ai/triads/discussions)
- **Bug reports**: Create an [Issue](https://github.com/reliable-agents-ai/triads/issues)
- **Security concerns**: Email maintainers directly (do not post publicly)

---

## Recognition

Contributors will be recognized in:
- README.md acknowledgments section
- Release notes
- Project documentation

Thank you for helping make Triad Generator better! 🎯
