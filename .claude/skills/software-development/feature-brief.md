---
name: feature-brief
description: Transform vague feature request into complete FeatureBrief specification with user stories, acceptance criteria, technical requirements, and success metrics. Use when user requests new features, enhancements, capabilities, or functionality. Discovers via keywords - feature, add, new, enhancement, improvement, capability, functionality, user story, requirement, want, need, would like, can we, implement, build, create, develop, support, enable, allow, provide, include, integrate, extend
category: brief
domain: software-development
generated_by: upgrade-executor
generated_at: 2025-10-28T17:45:00Z
allowed_tools: ["Grep", "Read", "AskUserQuestion", "WebSearch"]
---

# Feature Brief Skill

## Purpose

Transform vague feature request into complete FeatureBrief specification.

**What users say**: "add dark mode", "we need X", "can you make it do Y", "users want Z"

**What this skill creates**: Complete feature specification with:
- User stories (As a... I want... So that...)
- Acceptance criteria
- Technical requirements
- Success metrics
- Dependencies and constraints

## Keywords for Discovery

feature, add, new, enhancement, improvement, capability, functionality, user story, requirement, want, need, would like, can we, implement, build, create, develop, support, enable, allow, provide, include, integrate, extend, modify, change, update, upgrade, expand, introduce, request, suggestion, proposal, idea, innovation, addition, augmentation

## When to Invoke This Skill

Invoke when user requests new functionality like:
- "Add dark mode"
- "We need a search feature"
- "Can you make it support OAuth?"
- "Users want to export data"
- "I'd like to integrate with Stripe"
- "Can we add email notifications?"
- "Support for multiple languages"
- "Let users customize their dashboard"

## Skill Procedure

### Step 1: Clarify Input with Questions

Use AskUserQuestion to gather missing information:

**Questions for feature requests**:
1. Who will use this feature? (Target users)
2. What problem does this solve? (User need/pain point)
3. What should the feature do? (Core functionality)
4. How will users access it? (UI/API/CLI)
5. What does success look like? (Metrics/outcomes)
6. Are there any constraints? (Timeline, budget, technical limits)

---

### Step 2: Gather Context Using Tools

**Use Grep to find related code**:
```bash
# Search for related features
Grep pattern="{feature_keyword}" path=.
Grep pattern="{related_module}" path=.
```

**Use Read to examine existing implementations**:
```bash
# Read similar features for consistency
Read file_path="{related_feature_file}"
```

**Use WebSearch for best practices**:
```bash
# Research industry standards
WebSearch query="{feature_name} best practices implementation"
WebSearch query="{feature_name} user experience patterns"
```

**Analyze for**:
- Existing similar features
- Architecture patterns used
- Database schema requirements
- API design consistency
- UI/UX patterns

---

### Step 3: Create FeatureBrief Knowledge Graph Node

Based on gathered information, create structured specification:

```markdown
[GRAPH_UPDATE]
type: add_node
node_id: feature_brief_{sanitized_name}_{timestamp}
node_type: FeatureBrief

metadata:
  created_by: feature-brief-skill
  created_at: {ISO 8601 timestamp}
  confidence: {0.85-1.0 based on information completeness}
  domain: software-development
  output_type: "brief"

data:
  feature_name: "{Feature name}"
  summary: "{One-sentence feature description}"

  user_stories:
    - role: "{User type: end-user, admin, developer, etc.}"
      want: "{What they want to do}"
      so_that: "{Why they want it / benefit}"
      priority: "{MUST|SHOULD|COULD|WON'T}"
    - role: "{Another user type}"
      want: "{Capability}"
      so_that: "{Benefit}"
      priority: "{Priority}"

  problem_statement:
    current_situation: "{What users do now}"
    pain_points:
      - "{Pain point 1}"
      - "{Pain point 2}"
    desired_outcome: "{What users want to achieve}"

  acceptance_criteria:
    - "{Testable criterion 1}"
    - "{Testable criterion 2}"
    - "{Testable criterion 3}"
    - "Performance: {response time, throughput, etc.}"
    - "Security: {authentication, authorization requirements}"
    - "Accessibility: {WCAG compliance, screen reader support}"

  technical_requirements:
    frontend:
      - "{UI component requirements}"
      - "{User interaction flow}"
    backend:
      - "{API endpoints needed}"
      - "{Business logic requirements}"
    database:
      - "{Schema changes: new tables, columns, indexes}"
      - "{Data migration needed: yes/no}"
    integration:
      - "{Third-party services: API name, purpose}"
      - "{Authentication: OAuth, API keys, etc.}"

  success_metrics:
    - metric: "{e.g., User adoption rate}"
      target: "{e.g., 40% of users within 30 days}"
      measurement: "{How to measure: analytics, surveys}"
    - metric: "{e.g., Task completion time}"
      target: "{e.g., Reduce from 5 min to 2 min}"
      measurement: "{User testing, analytics}"

  dependencies:
    - type: "feature"
      description: "{Feature X must exist first}"
    - type: "technical"
      description: "{Library Y must be installed}"
    - type: "external"
      description: "{Third-party API must be available}"

  constraints:
    timeline: "{Deadline or sprint}"
    budget: "{Cost limits if applicable}"
    technical: "{Technology restrictions}"
    compatibility: "{Browser, OS, device requirements}"

  risks:
    - risk: "{Potential issue}"
      likelihood: "{HIGH|MEDIUM|LOW}"
      impact: "{HIGH|MEDIUM|LOW}"
      mitigation: "{How to address}"

  alternatives_considered:
    - option: "{Alternative approach 1}"
      pros: ["{Pro 1}", "{Pro 2}"]
      cons: ["{Con 1}", "{Con 2}"]
      why_rejected: "{Reason}"
    - option: "{Alternative approach 2}"
      pros: ["{Pro 1}"]
      cons: ["{Con 1}"]
      why_rejected: "{Reason}"

handoff:
  ready_for_next: true
  next_stage: "design-triad"
  required_fields: ["feature_name", "user_stories", "acceptance_criteria", "technical_requirements"]
  optional_fields: ["success_metrics", "dependencies", "constraints", "risks", "alternatives_considered"]

lineage:
  created_from_node: null
  consumed_by_nodes: []
[/GRAPH_UPDATE]
```

---

### Step 4: Return Standard OUTPUT Envelope

Return lightweight handoff with node reference:

```markdown
OUTPUT:
  _meta:
    output_type: "brief"
    created_by: "feature-brief"
    domain: "software-development"
    timestamp: "{ISO 8601}"
    confidence: {0.85-1.0}

  _handoff:
    next_stage: "design-triad"
    graph_node: "feature_brief_{sanitized_name}_{timestamp}"
    required_fields: ["feature_name", "user_stories", "acceptance_criteria", "technical_requirements"]
    optional_fields: ["success_metrics", "dependencies", "constraints"]
```

---

## Output Format

Returns:
- **Knowledge graph node** with complete feature specification (stored in graph)
- **Standard OUTPUT envelope** with node reference (lightweight handoff)

**User sees**:
```markdown
✅ Created FeatureBrief specification: feature_brief_dark_mode_20251028_173045

**Feature**: Dark Mode Theme

**User Story**: As a user, I want to switch to dark mode, so that I can reduce eye strain when using the app at night.

**Acceptance Criteria**:
- Theme toggle available in settings
- All UI components render correctly in dark mode
- User preference persisted across sessions
- System theme detection (auto-switch based on OS preference)

**Technical Requirements**:
- CSS variables for theme colors
- LocalStorage for preference persistence
- useTheme React hook for theme state
- Dark mode variants for all components

**Success Metrics**:
- 30% of users enable dark mode within 14 days
- No increase in UI-related bug reports

**Next Stage**: design-triad

View full specification in knowledge graph: feature_brief_dark_mode_20251028_173045
```

---

## Example Usage

**User Input**: "add dark mode"

**Skill Process**:
1. ✅ Keyword match: "add" triggers feature-brief skill
2. ✅ Asked clarifying questions via AskUserQuestion
   - Who: All users (end-users)
   - Why: Reduce eye strain at night
   - How: Toggle in settings
   - Success: 30% adoption in 14 days
3. ✅ Searched codebase with Grep for "theme" and "settings"
   - Found: components/Settings.tsx, styles/theme.css
4. ✅ Read existing theme implementation
   - Discovered: CSS variables already used for colors
5. ✅ Searched web for "dark mode best practices"
   - Found: System theme detection, WCAG contrast requirements
6. ✅ Created FeatureBrief knowledge graph node with complete specification
7. ✅ Returned OUTPUT envelope with node reference

**Output**: Complete feature specification ready for design triad

---

## Integration with Standard Output Protocol

This skill follows the standard output protocol (`.claude/protocols/standard-output.md`):
- Creates knowledge graph node (full data storage)
- Returns OUTPUT envelope (lightweight handoff)
- Downstream agents load node by reference

**Node structure** follows `.claude/protocols/node-types.md` → FeatureBrief definition.

---

## Why This Skill Matters

**Before**:
- User: "add dark mode"
- Developer: "Where? How? What colors? System detection? When needed?"
- [Multiple meetings, spec documents, revisions]
- [Finally enough detail to design]
- [Months later, feature doesn't match user needs]

**After**:
- User: "add dark mode"
- feature-brief skill activates automatically
- Asks structured questions once
- Researches best practices automatically
- Creates complete specification with user stories, acceptance criteria
- Design triad receives structured brief and creates architecture immediately
- Feature matches user needs on first iteration

**Time saved**: ~2-3 weeks of requirements gathering
**Quality improvement**: Comprehensive specification prevents rework

---

## User Story Template

All user stories follow this format:

```
As a [role],
I want [capability],
So that [benefit].
```

**Examples**:

```
As a content creator,
I want to schedule posts in advance,
So that I can maintain consistent publishing without manual effort.

As an administrator,
I want to bulk import users from CSV,
So that I can onboard large teams efficiently.

As a developer,
I want API rate limit information in response headers,
So that I can implement proper backoff strategies.
```

---

## Acceptance Criteria Checklist

All acceptance criteria must be:
- [ ] Testable (can verify pass/fail)
- [ ] Specific (no ambiguity)
- [ ] User-focused (describes behavior, not implementation)
- [ ] Complete (covers happy path + edge cases)
- [ ] Measurable (has quantifiable success)

**Example - Good Acceptance Criteria**:
```
✅ User can toggle dark mode in settings page
✅ Theme change applies immediately (no page refresh)
✅ Theme preference persists across browser sessions
✅ All UI components meet WCAG AAA contrast ratio (7:1)
✅ Theme auto-switches when OS theme changes (if preference = "auto")
✅ Performance: Theme change completes in <100ms
```

**Example - Bad Acceptance Criteria**:
```
❌ Dark mode works (not testable - what does "works" mean?)
❌ User can change theme (not specific - how?)
❌ App looks good in dark mode (not measurable - what's "good"?)
❌ CSS updated for dark mode (implementation detail, not user-facing)
```

---

## Constitutional Integration

This skill enforces constitutional principles:

- **Evidence-Based Claims**: All requirements cite user research, best practices, existing code patterns
- **Multi-Method Verification**: Uses Grep (codebase) + Read (existing features) + WebSearch (industry standards)
- **Complete Transparency**: Shows reasoning from vague request → user stories → technical requirements
- **Uncertainty Escalation**: If confidence < 85%, flags missing information (e.g., unclear user need)
- **Assumption Auditing**: Documents assumptions (e.g., "Assuming CSS variables already used" based on code inspection)
- **No Hyperbole**: Uses objective language (target metrics, not "amazing feature")
- **Critical Thinking**: Considers alternatives, evaluates pros/cons, explains why chosen

**This skill transforms vague ideas into actionable specifications with constitutional rigor.**
