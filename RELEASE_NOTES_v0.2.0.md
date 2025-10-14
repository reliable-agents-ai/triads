# Release v0.2.0: Auto-Router System

## 🚀 Major Feature: Intelligent Triad Routing

The auto-router automatically detects your intent and routes to the appropriate triad without requiring manual "Start {Triad}:" commands. This release brings seamless context-aware routing with intelligent fallbacks.

### Key Features

#### 🧠 Multi-Stage Routing
- **Semantic routing** (<20ms P95 latency) using sentence-transformers (all-MiniLM-L6-v2)
- **LLM fallback** for ambiguous prompts via Claude API when semantic confidence is low
- **Grace period mechanism** (5 turns OR 8 minutes) prevents disruptive mid-conversation re-routing
- **4-stage graceful degradation**: Grace Period → Semantic → LLM → Manual
  - Ensures users are never blocked, even if routing systems fail

#### 🎓 Training Mode
- **Interactive confirmations** for new users learning the system
- **Visual feedback** showing routing decisions and confidence scores
- **Disable when ready**: Toggle off once familiar with routing behavior

#### 🛠️ CLI Commands for Control
- `/router-status` - View current routing state, active triad, and grace period status
- `/switch-triad` - Manually override automatic routing to specific triad
- `/router-reset` - Clear routing state and restart with fresh context
- `/router-training` - Toggle training mode on/off
- `/router-stats` - View routing performance metrics and decision history

### 📊 Quality Improvements

#### Code Health: 8.3 → 9.1/10 (+0.8)
- **Eliminated 83% duplication** in router utilities:
  - Consolidated 7 timestamp implementations into `timestamp_utils.py`
  - Consolidated 5 path construction implementations into `router_paths.py`
- **Added 16 utility tests** for consolidated functions
- **Zero regressions** from refactoring (validated by comprehensive test suite)

#### Test Coverage
- **241 total tests** across 13 test modules
- **240 passing** (99.6% pass rate)
- **80% code coverage** overall
- **94-100% coverage** for router core modules

### ⚡ Performance

- **Routing latency**: 15-20ms P95 (semantic mode)
- **Semantic hit rate**: >65% (validated in integration testing)
- **Graceful degradation**: Ensures <100ms worst-case fallback to manual

### 📦 What's Included

**15 implementation modules** (3,447 lines):
- State management, configuration, telemetry
- Semantic routing with embeddings
- LLM disambiguation via Claude API
- Grace period enforcement
- Manual selection fallback
- Training mode with user guidance
- CLI command handlers

**11 test modules** (3,219 lines):
- Unit tests for all router components
- Integration tests for end-to-end workflows
- Performance benchmarks
- Edge case coverage

**5 CLI commands**:
- Status, switch, reset, training, stats

**Configuration files**:
- `.claude/router/config.json` - Router behavior
- `.claude/router/triad_routes.json` - Triad definitions

### 🔧 Installation

```bash
pip install triads==0.2.0
```

Or upgrade from earlier version:

```bash
pip install --upgrade triads
```

### 📚 Usage Example

```python
from triads.router import Router

# Initialize router
router = Router()

# Automatic routing based on user input
user_prompt = "Analyze the authentication system"
triad = router.route(user_prompt)  # Returns "discovery" triad

# Manual override if needed
router.switch_triad("design")

# Check routing status
status = router.get_status()
print(f"Active triad: {status['active_triad']}")
print(f"Grace period: {status['grace_period_active']}")
```

### 🔍 How It Works

1. **User enters prompt** (e.g., "Analyze the auth system")
2. **Grace period check**: If recently routed, stay in current triad
3. **Semantic routing**: Compute embedding similarity against triad examples
4. **LLM fallback**: If semantic confidence <85%, ask Claude API to disambiguate
5. **Manual fallback**: If LLM fails, prompt user to select triad manually
6. **Notification**: User sees which triad was selected and why (in training mode)

### 🛡️ Constitutional Compliance

All router components follow TRUST framework:
- **T**horough: Multi-stage verification before routing decisions
- **R**equire evidence: Confidence scores and reasoning for all decisions
- **U**ncertainty escalation: LLM disambiguation when semantic confidence low
- **S**how all work: Telemetry logs all routing decisions with rationale
- **T**est assumptions: Comprehensive test suite validates routing logic

### 🐛 Bug Fixes

No bug fixes in this release - this is a pure feature addition with quality improvements.

### 💡 Migration Guide

**From v0.0.x to v0.2.0**:

No breaking changes! The router is an additive feature. Existing workflows continue to work.

**To enable auto-routing**:
1. Install v0.2.0: `pip install --upgrade triads`
2. Configure triads in `.claude/router/triad_routes.json`
3. Start using natural language prompts without "Start {Triad}:" prefix

**To disable auto-routing**:
- Continue using explicit "Start {Triad}:" commands
- Router only activates for natural language prompts

### 📖 Documentation

- **README.md** - Updated with router usage guide
- **CHANGELOG.md** - Complete version history
- **Architecture docs** - Router design and implementation details

### 🙏 Acknowledgments

Special thanks to the Garden Tending triad for the quality improvements that made this release production-ready.

---

**Full Changelog**: [v0.0.4...v0.2.0](https://github.com/reliable-agents-ai/triads/compare/v0.0.4...v0.2.0)

**Questions?** Open an [issue](https://github.com/reliable-agents-ai/triads/issues) or [discussion](https://github.com/reliable-agents-ai/triads/discussions)
