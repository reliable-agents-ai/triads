---
description: Generate a custom workflow when gap detected (organic mode)
---

# Generate Workflow Command

Generate a custom workflow when the supervisor detects a gap (user request doesn't match existing workflows).

## Usage

```bash
/generate-workflow <workflow-description>
```

## Organic Mode

**What is Organic Mode?**

Organic mode is a streamlined workflow generation process triggered when:
1. User makes a work request
2. Headless classifier returns no match (gap detected)
3. User approves generating a custom workflow

**How it differs from normal generation:**
- ⚡ **Fast**: 5-10 minutes (vs 30-60 min full interview)
- 🎯 **Focused**: Skip broad domain research
- 📋 **Context-driven**: Use user's specific request as starting point
- 🔄 **Iterative**: Can refine based on user feedback

## Process

### 1. Supervisor Detects Gap

```
User: "Migrate database from PostgreSQL to MongoDB"

Supervisor: [Classifies using headless mode]
            → Result: None (confidence 0.0)

            🔍 Workflow Gap Detected

            This appears to be database migration work.
            Would you like me to generate a migration workflow?

User: "Yes please"
```

### 2. Invoke Generator with Organic Mode

The supervisor invokes the generator triad with workflow context:

```python
# Workflow context passed to generator
context = {
    "user_request": "Migrate database from PostgreSQL to MongoDB",
    "classified_type": None,  # No match found
    "gap_description": "database migration",
    "suggested_workflow_name": "database-migration",
    "organic_mode": True
}
```

### 3. Generator Triad Execution

**Generator Sequence** (organic mode):

**Phase 1: Workflow Analyst** (MODIFIED)
- Skip: Broad domain research
- Do: Analyze user's specific request
- Do: Identify key workflow steps
- Output: Workflow structure proposal

**Phase 2: Triad Architect**
- Design triad sequence for this workflow
- Map steps to existing triads
- Define entry/exit conditions
- Output: Workflow YAML

**Phase 3: Save & Notify**
- Save workflow to `.claude/workflows/<name>.yaml`
- Notify user of completion
- Remind user to restart session

### 4. Session Restart

```
Workflow generated: .claude/workflows/database-migration.yaml

Please restart your Claude Code session to load the new workflow.

After restart, you can use:
"Migrate database from PostgreSQL to MongoDB"
→ Will now match database-migration workflow
```

## Example

```bash
/generate-workflow database migration from PostgreSQL to MongoDB
```

**Output:**
```yaml
# .claude/workflows/database-migration.yaml

name: database-migration
description: Migrate database from one system to another

keywords:
  - migrate
  - migration
  - database
  - postgres
  - mongodb
  - data transfer

triad_sequence:
  - name: investigation
    description: Analyze current database and plan migration
    agents:
      - research-analyst
      - community-researcher
      - validation-synthesizer
    deliverables:
      - Database schema analysis
      - Data volume assessment
      - Migration strategy

  - name: design
    description: Design migration approach
    agents:
      - validation-synthesizer
      - solution-architect
      - design-bridge
    deliverables:
      - Migration architecture
      - Data transformation plan
      - Rollback strategy (ADR)

  - name: implementation
    description: Execute migration
    agents:
      - design-bridge
      - senior-developer
      - test-engineer
    deliverables:
      - Migration scripts
      - Data validation tests
      - Rollback procedures

  - name: garden-tending
    description: Cleanup and verification
    agents:
      - cultivator
      - pruner
      - gardener-bridge
    deliverables:
      - Migration verification
      - Performance testing
      - Documentation

entry_conditions:
  - Database migration needed
  - System migration required
  - Data transfer between platforms

success_criteria:
  - All data migrated successfully
  - No data loss
  - Performance acceptable
  - Rollback tested

estimated_duration: 1-2 weeks

metadata:
  version: "1.0"
  created: "2025-10-21"
  generated_by: organic-mode
  category: infrastructure
```

## Implementation Details

**File Location**: `.claude/workflows/<workflow-name>.yaml`

**Workflow Name Rules**:
- Lowercase with hyphens
- Descriptive (2-3 words)
- Unique (no conflicts with existing workflows)

**Post-Generation**:
1. Workflow saved to `.claude/workflows/`
2. User notified of completion
3. Session restart required for workflow to become available
4. Headless classifier will detect new workflow after restart

## Options

```bash
# Basic generation
/generate-workflow security audit workflow

# With specific details
/generate-workflow API versioning and deprecation workflow

# With urgency
/generate-workflow --fast incident response workflow
```

## Training Mode

During Phase 2 rollout:
- Supervisor suggests generation (doesn't auto-execute)
- User approves each generation
- After 5 successful generations → can enable auto-suggest

## Related

- `/workflows list` - View all workflows
- Supervisor gap detection - Automatic detection
- Headless classifier - Workflow matching

## Support

- [Organic Generation Design](../../docs/adrs/ADR-015.md)
- [GitHub Issues](https://github.com/reliable-agents-ai/triads/issues)
