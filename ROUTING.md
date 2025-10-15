# ⚡ TRIAD ROUTING SYSTEM

**CRITICAL DIRECTIVE**: When user describes work (not questions), suggest the appropriate triad.

## Routing Recognition Patterns

| User Intent Pattern | Suggest This |
|-------------------|--------------|
| "I have an idea..." / "What if we..." / "Should we add..." | `Start Idea Validation: [idea]` |
| "How should we architect..." / "Design approach for..." | `Start Design: [feature]` |
| "Let's build..." / "Implement..." / "Create..." | `Start Implementation: [feature]` |
| "Code needs cleanup" / "Refactor..." / "Maintenance..." | `Start Garden Tending: [scope]` |
| "Ready to release" / "Deploy..." / "Publish..." | `Start Deployment: [version]` |

## Critical Routing Rules

1. **Suggest, don't auto-execute**: Always ask for user confirmation
2. **Work vs Questions**: Only suggest routing for work requests, NOT informational questions
3. **Context awareness**: If deep in implementation discussion, don't interrupt with routing suggestions
4. **Explicit commands**: When user types exact "Start TriadName: ..." syntax, invoke immediately

## Routing Examples

**Example 1: Feature Idea**
```
User: "I'm thinking about adding AI-powered code suggestions"

You: "This sounds like **Idea Validation** work - we should research demand
     and technical feasibility. Would you like me to
     `Start Idea Validation: AI-powered code suggestions`?"
```

**Example 2: Architecture Question**
```
User: "How should we structure the plugin system for extensibility?"

You: "This is **Design** work - we need to architect the solution.
     Would you like me to `Start Design: Plugin system architecture`?"
```

**Example 3: Q&A (NO ROUTING)**
```
User: "What's the difference between a bridge agent and a regular agent?"

You: [Answer the question directly - this is Q&A, NOT a work request.
     Do not suggest routing.]

Bridge agents serve two roles: they complete work in the source triad
AND compress context for the target triad...
```

**Example 4: Implementation Work**
```
User: "Let's build the OAuth2 integration"

You: "This sounds like **Implementation** work - building a feature.
     Would you like me to `Start Implementation: OAuth2 integration`?"
```

**Example 5: Maintenance Request**
```
User: "Is there any maintenance work needed?"

You: "This sounds like **Garden Tending** work - scanning for quality
     improvements. Would you like me to
     `Start Garden Tending: Codebase maintenance scan`?"
```

**Example 6: Release Work**
```
User: "We're ready to release v0.3.0"

You: "This is **Deployment** work. Would you like me to
     `Start Deployment: v0.3.0`?"
```

## Dynamic Triad Discovery

**Important**: This routing guide provides default patterns. Actual triads
in the current project may differ based on custom generation.

When suggesting routing:
1. Check if project has `.claude/agents/` directory
2. Look for triad names in subdirectories
3. Suggest based on actual project structure
4. Fall back to these generic patterns if no custom triads found

---

**Note**: This routing context is injected automatically at session start by
the triads plugin. Custom project routing (if exists in `.claude/ROUTING.md`)
takes precedence over these defaults.
