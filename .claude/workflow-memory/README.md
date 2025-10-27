# Workflow-Specific Memory Templates

This directory contains memory templates for the 5 standard triads workflows. These templates capture context and maintain continuity across multi-agent workflows.

---

## 🎯 Purpose

**Workflow memory templates** ensure:
- **Context preservation** across agent handoffs
- **Progress tracking** throughout workflow execution
- **Knowledge capture** for future reference
- **Quality verification** at each stage
- **Handoff summaries** for next triad

---

## 📋 Available Templates

### 1. Idea Validation Memory (`idea-validation-memory.md`)

**Workflow**: validation-analyst → community-researcher → validation-synthesizer

**Captures**:
- Idea being validated
- Research conducted (web search, GitHub issues, discussions)
- Community evidence (pain points, user demand)
- Priority score calculation (0-100)
- Decision (PROCEED/DEFER/REJECT) with reasoning
- Handoff to Design triad

**Key Sections**:
- Validation agent research questions and findings
- Community researcher evidence (GitHub, Stack Overflow)
- Validation synthesizer priority scoring
- Decision with confidence level
- Handoff summary

**Use When**: Validating new feature ideas before design/implementation

---

### 2. Design Memory (`design-memory.md`)

**Workflow**: validation-synthesizer → solution-architect → design-bridge

**Captures**:
- Feature requirements from idea validation
- Architecture overview (components, data flow, integration points)
- Alternative solutions evaluated (with trade-offs)
- Architecture Decision Records (ADRs)
- Implementation plan (phases, effort estimates, risks)
- HITL gate: User approval required
- Handoff to Implementation triad

**Key Sections**:
- Solution architect work (architecture, alternatives, ADRs)
- Design bridge compression (critical decisions, implementation order)
- User approval checklist
- Handoff to implementation

**Use When**: Designing technical solutions before implementation

---

### 3. Implementation Memory (`implementation-memory.md`)

**Workflow**: design-bridge → senior-developer → test-engineer

**Captures**:
- Design specifications to implement
- TDD cycle tracking (RED → GREEN → BLUE → VERIFY → COMMIT)
- Implementation progress by feature/file
- Test strategy and coverage
- Edge cases, security tests, performance tests
- Quality metrics
- Handoff to Garden Tending

**Key Sections**:
- Senior developer TDD iterations
- Test engineer test cases and coverage
- Quality verification (automated + manual)
- Handoff summary

**Use When**: Implementing designed features with TDD

---

### 4. Garden Tending Memory (`garden-tending-memory.md`)

**Workflow**: cultivator → pruner → gardener-bridge

**Captures**:
- Initial quality baseline
- Growth opportunities identified
- Beneficial patterns found
- Consolidation opportunities (DRY, merge, extract)
- Refactoring execution (following 5 Safe Refactoring Rules)
- Duplication removed
- Quality improvement metrics
- Handoff to Deployment

**Key Sections**:
- Cultivator growth opportunity identification
- Pruner refactoring log (one at a time, tests green)
- Gardener bridge quality summary
- Improvement patterns for Design triad
- Pre-deployment checklist

**Use When**: Refactoring code, reducing technical debt, improving quality

---

### 5. Deployment Memory (`deployment-memory.md`)

**Workflow**: gardener-bridge → release-manager → documentation-updater

**Captures**:
- Version information (semantic versioning)
- CHANGELOG generation (Keep a Changelog format)
- Release notes
- Documentation updates (README, guides, etc.)
- Build and publish process
- Installation verification
- Post-deployment tasks

**Key Sections**:
- Release manager version bumping and changelog
- Documentation updater file updates
- Publishing workflow
- Post-deployment verification
- Communication and monitoring

**Use When**: Creating releases, publishing packages, updating docs

---

## 🔄 Workflow Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│                   User Request                              │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ↓
┌────────────────────────────────────────────────────────────┐
│  IDEA VALIDATION                                            │
│  - Research idea                                            │
│  - Gather evidence                                          │
│  - Calculate priority score                                 │
│  - DECIDE: PROCEED / DEFER / REJECT                         │
└────────────────┬────────────────────────────────────────────┘
                 │ (if PROCEED)
                 ↓
┌────────────────────────────────────────────────────────────┐
│  DESIGN                                                     │
│  - Design architecture                                      │
│  - Evaluate alternatives                                    │
│  - Create ADRs                                              │
│  - HITL GATE: User approval required                        │
└────────────────┬────────────────────────────────────────────┘
                 │ (if APPROVED)
                 ↓
┌────────────────────────────────────────────────────────────┐
│  IMPLEMENTATION                                             │
│  - Follow TDD (RED → GREEN → BLUE → VERIFY → COMMIT)       │
│  - Write tests (≥80% coverage)                              │
│  - Ensure quality gates pass                                │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ↓
┌────────────────────────────────────────────────────────────┐
│  GARDEN TENDING                                             │
│  - Identify growth opportunities                            │
│  - Refactor (5 Safe Refactoring Rules)                      │
│  - Improve quality, reduce debt                             │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ↓
┌────────────────────────────────────────────────────────────┐
│  DEPLOYMENT                                                 │
│  - Bump version (semantic versioning)                       │
│  - Update CHANGELOG and docs                                │
│  - Publish package                                          │
│  - Create release                                           │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ↓
               DONE ✅
```

---

## 📐 Template Structure

Each workflow memory template follows this structure:

### 1. Header
```yaml
**Workflow**: {{WORKFLOW_NAME}}
**Domain**: {{DOMAIN_TYPE}}
**Started**: {{START_DATE}}
**Status**: {{STATUS}}
```

### 2. Purpose and Success Criteria
- Clear objective statement
- Measurable success criteria (checklist)

### 3. From Previous Triad
- Context summary from handoff
- Key information needed to start work

### 4. Agent-Specific Work Sections
- One section per agent in the triad
- Structured data capture (YAML format)
- Progress tracking
- Evidence and citations

### 5. Handoff to Next Triad
- Compressed context summary
- Critical information only
- Clear next steps

### 6. Knowledge Graph Updates
- Nodes created during workflow
- Evidence and confidence levels

### 7. Issues and Metrics
- Problems encountered and resolutions
- Success criteria checklist
- Quality gates

---

## 🎨 Usage Examples

### Example 1: Starting Idea Validation

**User**: "I want to add AI-powered code suggestions"

**Process**:
1. Create new instance of `idea-validation-memory.md`
2. Fill in "Core Idea" section:
   ```yaml
   idea:
     name: "AI-powered code suggestions"
     description: "Add inline code completion using LLM"
     problem_statement: "Developers spend 30% of time on boilerplate"
     proposed_solution: "Context-aware AI suggestions"
   ```
3. Agents fill in their sections as they work
4. At end, handoff summary populated for Design triad

---

### Example 2: Tracking Implementation Progress

**Process**:
1. Create new instance of `implementation-memory.md`
2. Copy design summary from design-memory handoff
3. Senior developer fills in TDD cycle tracking:
   ```yaml
   red_phase:
     test_file: "tests/test_suggest.py"
     test_name: "test_suggest_with_context"
     result: "FAILED ❌"
     verified: "YES"
   ```
4. Test engineer fills in test strategy and coverage
5. At end, quality metrics for Garden Tending

---

### Example 3: Refactoring with Garden Tending

**Process**:
1. Create new instance of `garden-tending-memory.md`
2. Cultivator identifies growth opportunities:
   ```yaml
   growth_opportunities:
     - opportunity_id: "GROW001"
       type: "Extract method"
       location: "src/api/suggest.py:45-78"
       description: "34-line function does multiple things"
       priority: "HIGH"
   ```
3. Pruner refactors following 5 Safe Rules
4. Gardener bridge summarizes quality improvements

---

## 🔗 Integration with Project Memory

### Relationship to CLAUDE.md

```
Project CLAUDE.md
    ↓
Imports all constitutional principles and methodologies

Workflow Memory (this directory)
    ↓
Captures context for specific workflow execution
Persists knowledge to graph
Generates handoff summaries
```

**CLAUDE.md** = Static configuration (principles, methodologies)
**Workflow Memory** = Dynamic execution context (progress, decisions, findings)

---

## 📊 Handlebars Variables

Templates use Handlebars syntax for variable substitution:

**Common Variables**:
- `{{WORKFLOW_NAME}}` - Name of workflow
- `{{DOMAIN_TYPE}}` - software-development | research | content-creation | business-analysis
- `{{START_DATE}}` - ISO 8601 timestamp
- `{{STATUS}}` - pending | in_progress | complete
- `{{FEATURE_NAME}}` - Feature being worked on
- `{{VERSION}}` - Version number (for deployment)

**Agent-Specific Variables**:
- `{{AGENT_NAME}}` - Name of agent (e.g., "validation-analyst")
- `{{TIMESTAMP}}` - Current timestamp
- `{{EVIDENCE}}` - Evidence supporting claim
- `{{CONFIDENCE}}` - Confidence level (0-100%)

**Conditionals**:
```handlebars
{{#if_software}}
  Software-specific content
{{/if_software}}

{{#if_research}}
  Research-specific content
{{/if_research}}
```

---

## 🛠️ Customization

### Adding Domain-Specific Sections

To add domain-specific sections to templates:

1. Identify domain-specific patterns (e.g., research methodologies, SEO requirements)
2. Add conditional sections:
   ```handlebars
   {{#if_research}}
   ### Research-Specific Section

   ```yaml
   statistical_tests:
     - test: "{{TEST_NAME}}"
       result: "{{RESULT}}"
   ```
   {{/if_research}}
   ```
3. Update Triad Architect to populate these sections

---

### Extending Workflows

To create custom workflow memory templates:

1. Copy closest existing template (e.g., `implementation-memory.md`)
2. Modify sections to match your workflow
3. Ensure consistent structure:
   - Purpose and success criteria
   - Agent-specific sections
   - Handoff summary
   - Knowledge graph updates
4. Add to generator configuration

---

## 📚 Best Practices

### 1. Progressive Filling
- Don't fill entire template at start
- Each agent fills their section as they work
- Update handoff summary at end

### 2. Evidence-Based
- All claims require evidence
- Cite sources with file:line or URLs
- Include confidence levels

### 3. Handoff Summaries
- Keep concise (top-N most important items)
- Critical information only
- Clear next steps for next triad

### 4. Knowledge Graph Updates
- Create nodes for key findings and decisions
- Include evidence and verification methods
- Maintain confidence scores

### 5. Metrics Tracking
- Track progress against success criteria
- Record quality gates (PASSED/FAILED)
- Measure improvements (before/after)

---

## 🎯 Success Criteria

Each workflow memory template should enable:

✅ **Context Preservation**: Next agent understands previous work
✅ **Progress Tracking**: Clear status of work in progress
✅ **Quality Verification**: Evidence that standards were met
✅ **Knowledge Capture**: Findings/decisions recorded in graph
✅ **Handoff Clarity**: Next triad knows exactly what to do

---

## 📖 References

### Keep a Changelog Format
- https://keepachangelog.com
- Used in Deployment workflow

### Semantic Versioning
- https://semver.org
- MAJOR.MINOR.PATCH versioning
- Used in Deployment workflow

### TDD Cycle
- RED → GREEN → BLUE → VERIFY → COMMIT
- Used in Implementation workflow

### 5 Safe Refactoring Rules
- Tests exist and pass BEFORE refactoring
- ONE refactoring at a time
- Run tests AFTER each refactoring
- Commit AFTER each successful refactoring
- NEVER change behavior, only structure
- Used in Garden Tending workflow

---

## 🔍 Troubleshooting

### Problem: Handoff summary too large

**Solution**: Use bridge-compress skill to select top-N nodes
```
Top-10 most important items for next triad
Use importance scoring algorithm (confidence + type + recency)
```

### Problem: Uncertainty about what to capture

**Solution**: Follow template structure
- Each section has examples
- Use YAML format for structured data
- When in doubt, capture more (can compress later)

### Problem: Too much manual work to fill template

**Solution**: Agents auto-populate their sections
- Senior developer fills TDD cycle tracking automatically
- Test engineer fills coverage metrics from tool output
- Release manager generates CHANGELOG from git log

---

**These workflow memory templates ensure high-quality, traceable, and well-documented work across all triads.**

**Template Version**: v1.0.0
**Created**: 2024-10-27
**Status**: Complete (5/5 workflow templates)
