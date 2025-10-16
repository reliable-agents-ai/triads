# Release v0.6.0 - Knowledge Graph CLI Access

**Release Date**: October 16, 2025

**Version**: 0.6.0 (minor version bump - new features, backward compatible)

---

## What's New

### Knowledge Access Commands

You can now explore knowledge accumulated by triads using 4 new CLI commands that provide powerful graph browsing and search capabilities!

#### `/knowledge-status [triad]`

View comprehensive statistics about your knowledge graphs:
- Total node and edge counts
- Node type distribution (Entity, Concept, Decision, Finding, Uncertainty)
- Average confidence scores across all nodes
- Recently modified graphs
- Health metrics for each triad's knowledge base

**Example**:
```bash
/knowledge-status design
```

**Output**:
```
Design Triad Knowledge Graph Status
====================================
Nodes: 42 | Edges: 67 | Avg Confidence: 0.89

Node Types:
- Decision: 8 (ADRs, architectural choices)
- Entity: 15 (components, systems)
- Concept: 12 (patterns, principles)
- Finding: 7 (research results)
```

#### `/knowledge-search <query>`

Search across all knowledge graphs with powerful filtering:
- **Case-insensitive substring matching** in labels, descriptions, and IDs
- **Filter by triad** - Narrow search to specific workflow (e.g., `--triad=design`)
- **Filter by type** - Find only Decisions, Entities, or other node types
- **Confidence threshold** - Show only high-confidence nodes (e.g., `--min-confidence=0.85`)
- **Relevance ranking** - Results sorted by match quality and confidence

**Examples**:
```bash
# Find all OAuth-related knowledge
/knowledge-search "OAuth"

# Find architectural decisions about authentication
/knowledge-search "auth" --triad=design --type=Decision

# Find high-confidence findings
/knowledge-search "performance" --type=Finding --min-confidence=0.90
```

**Output**:
```
Search Results for "OAuth"
==========================

Design Triad (2 matches):
------------------------
[1] auth_decision_oauth2 (Decision, confidence: 0.95)
    "OAuth2 authentication strategy"
    Match in: label

[2] oauth_implementation (Entity, confidence: 0.87)
    "OAuth2 provider integration with Anthropic API"
    Match in: description
```

#### `/knowledge-show <node_id>`

Display complete details for any node including:
- All attributes (type, label, description, confidence)
- Evidence and provenance (source, creation timestamp, creator)
- **Relationships** to other nodes (edges with labels)
- Full metadata for deep investigation

**Example**:
```bash
/knowledge-show auth_decision_oauth2
```

**Output**:
```
Node Details: auth_decision_oauth2
===================================

Type: Decision
Label: OAuth2 authentication strategy
Confidence: 0.95
Created: 2025-10-12T14:23:45Z
Created By: solution-architect

Description:
Use OAuth2 with JWT tokens for API authentication.
Provides better security than API keys and supports
token refresh and revocation.

Evidence:
- Industry standard (RFC 6749)
- Better security model than alternatives
- Existing library support

Relationships:
→ IMPLEMENTS → oauth_library (Entity)
→ REPLACES → api_key_auth (Decision)
← USES ← user_service (Entity)
```

#### `/knowledge-help`

Get complete reference documentation including:
- Command syntax and all available options
- Usage examples for common scenarios
- Filtering and search tips
- Troubleshooting guidance

---

## Key Features

**Zero Dependencies**
Uses Python standard library only - no additional packages required

**Fast Performance**
- Sub-30ms search and load operations
- Lazy loading with per-session caching
- Memory efficient (~50KB per graph)

**Secure**
- Path traversal protection prevents directory escapes
- Input sanitization protects against injection attacks
- Safe JSON parsing with graceful error handling

**Well-Tested**
- 148+ automated tests across 9 test modules
- 97% code coverage
- Comprehensive security and edge case testing

**User-Friendly**
- Clear error messages with actionable suggestions
- Helpful command examples
- Markdown-formatted output for readability

---

## Installation

### Update Existing Installation

If you already have triads installed via git:

```bash
cd ~/.claude/plugins/marketplaces/triads-marketplace
git pull
git checkout v0.6.0
```

### Fresh Installation

```bash
# Clone the repository
git clone https://github.com/reliable-agents-ai/triads.git ~/.claude/plugins/marketplaces/triads-marketplace
cd ~/.claude/plugins/marketplaces/triads-marketplace
git checkout v0.6.0

# Follow setup instructions in INSTALLATION.md
```

---

## Documentation

**User Guides**:
- [Knowledge Access Commands Guide](/Users/iainnb/Documents/repos/triads/docs/km-access-commands.md) - Complete documentation
- [Usage Guide](/Users/iainnb/Documents/repos/triads/docs/USAGE.md) - Working with triads
- [Architecture](/Users/iainnb/Documents/repos/triads/docs/ARCHITECTURE.md) - System design

**API Reference**:
- Command definitions in `.claude/commands/knowledge-*.md`
- Python module: `src/triads/km/graph_access.py`

**Full Changelog**: [CHANGELOG.md](/Users/iainnb/Documents/repos/triads/CHANGELOG.md)

---

## Try It Now

Start exploring your knowledge graphs immediately:

```bash
# See what graphs exist
/knowledge-status

# Search for something you've been working on
/knowledge-search "your topic"

# Get help and see all options
/knowledge-help
```

---

## What's Next

**Phase 2 Enhancements** (planned for future releases):
- Fuzzy search for typo tolerance
- Relationship traversal commands (e.g., "show all nodes connected to X")
- Graph visualization export (DOT format, Mermaid diagrams)
- Natural language queries powered by LLM
- Graph diffing (compare knowledge across versions)
- Confidence-based filtering improvements

**Feedback Welcome**:
Have ideas for knowledge graph features? Open an issue or start a discussion!

---

## Technical Details

**Implementation**:
- Module: `src/triads/km/graph_access.py` (1,126 lines)
- Classes: GraphLoader, GraphSearcher, GraphFormatter
- Commands: 4 CLI commands (510 lines of documentation)
- Tests: 9 test modules (148+ tests, 97% coverage)

**Architecture Decisions**:
This release implements ADRs from the Design triad:
- ADR-001: CLI commands as primary interface (not TUI/web)
- ADR-002: Lazy loading with per-session caching
- ADR-003: Substring search for MVP (fuzzy search in Phase 2)
- ADR-004: Shared utility module for reusability
- ADR-005: Markdown output format for readability

**Backward Compatibility**:
- No breaking changes to existing APIs
- Existing workflows continue to work unchanged
- New commands are opt-in

---

## Comparison Links

**Full Changelog**: https://github.com/reliable-agents-ai/triads/compare/v0.5.0...v0.6.0

**Previous Release**: [v0.2.0 Release Notes](https://github.com/reliable-agents-ai/triads/releases/tag/v0.2.0) (Auto-Router System)

---

Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>
