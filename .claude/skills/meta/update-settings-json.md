---
name: update-settings-json
description: Update Claude Code settings.json configuration file for hooks triads agents and project settings. Use when configuring hooks, registering triads, enabling agents, updating settings, JSON configuration, hook registration, triad registration, agent configuration, settings validation, JSON merge strategies, configuration management, settings file updates, hook priorities, agent discovery, triad metadata, settings best practices, JSON syntax, configuration validation, settings documentation, project configuration, hook enable disable, triad versioning, settings structure, configuration patterns
---

# Update Settings JSON Configuration

**Purpose**: Update `.claude/settings.json` to register hooks, triads, and configure Claude Code behavior.

**Authority**: Meta-level (manages Claude Code configuration)

**Based on**: Claude Code configuration patterns and hook/agent registration requirements

---

## 📋 When to Invoke

**Invoke this skill when**:
- Registering new hooks
- Registering new triads
- Enabling/disabling features
- Configuring agent discovery
- Updating project settings
- Validating JSON configuration

**Keywords that trigger this skill**:
- "update settings.json"
- "register hook"
- "register triad"
- "configure settings"
- ".claude/settings.json"

---

## 🎯 Settings.json Structure

### File Location

**Path**: `.claude/settings.json`

### Top-Level Structure

```json
{
  "hooks": {
    "pre_tool_use": [...],
    "post_tool_use": [...],
    "notification": [...],
    "user_prompt_submit": [...],
    "stop": [...],
    "subagent_stop": [...],
    "pre_compact": [...],
    "session_start": [...],
    "session_end": [...]
  },
  "triads": {
    "triad_name": {...}
  },
  "project": {
    "name": "Project Name",
    "version": "1.0.0",
    "description": "Project description"
  }
}
```

---

## 📋 Skill Procedure

### Step 1: Read Existing Settings

**Load current configuration**:

```bash
# Check if file exists
if [ -f .claude/settings.json ]; then
  cat .claude/settings.json
else
  echo "File does not exist - will create new"
fi
```

**Parse JSON** (validation):

```bash
# Validate JSON syntax
python3 -m json.tool .claude/settings.json > /dev/null
if [ $? -eq 0 ]; then
  echo "✅ Valid JSON"
else
  echo "❌ Invalid JSON - fix syntax errors"
fi
```

---

### Step 2: Determine Update Type

**Update types**:

1. **Add hook registration**
2. **Remove hook registration**
3. **Update hook priority/enabled status**
4. **Add triad registration**
5. **Update triad metadata**
6. **Update project settings**

---

### Step 3: Hook Registration

#### Hook Entry Structure

```json
{
  "hooks": {
    "pre_tool_use": [
      {
        "script": ".claude/hooks/pre_tool_use/validate-read-access.py",
        "enabled": true,
        "priority": 10
      }
    ]
  }
}
```

**Fields**:
- `script`: Path to hook file (relative to project root)
- `enabled`: `true` | `false` (disable without deleting)
- `priority`: Number (higher = runs first, optional)

#### Adding Hook

**Before**:
```json
{
  "hooks": {
    "pre_tool_use": []
  }
}
```

**After**:
```json
{
  "hooks": {
    "pre_tool_use": [
      {
        "script": ".claude/hooks/pre_tool_use/validate-read-access.py",
        "enabled": true,
        "priority": 10
      }
    ]
  }
}
```

#### Multiple Hooks (Same Event)

```json
{
  "hooks": {
    "pre_tool_use": [
      {
        "script": ".claude/hooks/pre_tool_use/validate-read-access.py",
        "enabled": true,
        "priority": 10
      },
      {
        "script": ".claude/hooks/pre_tool_use/log-tool-calls.py",
        "enabled": true,
        "priority": 5
      }
    ]
  }
}
```

**Execution order**: priority 10 runs before priority 5

#### Disabling Hook (Don't Delete)

```json
{
  "script": ".claude/hooks/pre_tool_use/validate-read-access.py",
  "enabled": false,  // Disabled but preserved
  "priority": 10
}
```

---

### Step 4: Triad Registration

#### Triad Entry Structure

```json
{
  "triads": {
    "implementation_triad": {
      "version": "1.0.0",
      "agents": [
        "design-bridge",
        "senior-developer",
        "test-engineer"
      ],
      "purpose": "Write production code, create tests, ensure quality",
      "status": "ready",
      "note": "Implementation triad for software development"
    }
  }
}
```

**Fields**:
- `version`: Semantic version (e.g., "1.0.0")
- `agents`: Array of agent names (order matters - workflow sequence)
- `purpose`: Brief description of triad function
- `status`: `"ready"` | `"beta"` | `"deprecated"`
- `note`: Optional additional context

#### Adding Triad

**Before**:
```json
{
  "triads": {}
}
```

**After**:
```json
{
  "triads": {
    "system_upgrade_triad": {
      "version": "1.0.0",
      "agents": [
        "gap-analyzer",
        "upgrade-executor",
        "upgrade-bridge"
      ],
      "purpose": "Intelligently upgrade existing projects to template system",
      "status": "ready",
      "note": "Meta-level agents for project migration. Invoke with /upgrade-to-templates"
    }
  }
}
```

#### Multiple Triads

```json
{
  "triads": {
    "idea_validation_triad": {
      "version": "1.0.0",
      "agents": ["research-analyst", "community-researcher", "validation-synthesizer"],
      "purpose": "Research ideas, validate community need, prioritize features",
      "status": "ready"
    },
    "design_triad": {
      "version": "1.0.0",
      "agents": ["validation-synthesizer", "solution-architect", "design-bridge"],
      "purpose": "Create architecture, make decisions, write ADRs",
      "status": "ready"
    },
    "implementation_triad": {
      "version": "1.0.0",
      "agents": ["design-bridge", "senior-developer", "test-engineer"],
      "purpose": "Write code, create tests, ensure quality",
      "status": "ready"
    }
  }
}
```

#### Updating Triad Version

**Scenario**: Triad updated, increment version

**Before**:
```json
{
  "implementation_triad": {
    "version": "1.0.0",
    "agents": ["design-bridge", "senior-developer", "test-engineer"]
  }
}
```

**After**:
```json
{
  "implementation_triad": {
    "version": "1.1.0",  // Incremented
    "agents": ["design-bridge", "senior-developer", "test-engineer"],
    "changelog": "Added security-scan skill to test-engineer"
  }
}
```

---

### Step 5: Project Settings

#### Project Metadata Structure

```json
{
  "project": {
    "name": "Triads Plugin",
    "version": "0.9.0-alpha.1",
    "description": "Claude Code plugin for generating custom triad workflows",
    "domain": "software-development",
    "template_version": "1.0.0",
    "constitutional_architecture": true
  }
}
```

**Fields**:
- `name`: Project name
- `version`: Semantic version
- `description`: Brief project description
- `domain`: Domain classification (software-development, research, content, etc.)
- `template_version`: Which template system version used
- `constitutional_architecture`: Uses constitutional principles

---

### Step 6: Merge Strategy

**When updating settings.json, use merge (not replace)**:

#### Safe Merge Pattern (Python)

```python
import json

def merge_settings(existing, updates):
    """Merge updates into existing settings without losing data."""

    # Deep copy to avoid mutation
    import copy
    result = copy.deepcopy(existing)

    # Merge hooks
    if "hooks" in updates:
        if "hooks" not in result:
            result["hooks"] = {}

        for event_type, hooks in updates["hooks"].items():
            if event_type not in result["hooks"]:
                result["hooks"][event_type] = []

            # Add new hooks (avoid duplicates by script path)
            existing_scripts = {h["script"] for h in result["hooks"][event_type]}
            for hook in hooks:
                if hook["script"] not in existing_scripts:
                    result["hooks"][event_type].append(hook)

    # Merge triads
    if "triads" in updates:
        if "triads" not in result:
            result["triads"] = {}

        result["triads"].update(updates["triads"])

    # Merge project settings
    if "project" in updates:
        if "project" not in result:
            result["project"] = {}

        result["project"].update(updates["project"])

    return result

# Usage
with open('.claude/settings.json', 'r') as f:
    existing = json.load(f)

updates = {
    "hooks": {
        "pre_tool_use": [
            {
                "script": ".claude/hooks/pre_tool_use/new-hook.py",
                "enabled": true,
                "priority": 5
            }
        ]
    }
}

merged = merge_settings(existing, updates)

with open('.claude/settings.json', 'w') as f:
    json.dump(merged, f, indent=2)
```

#### Safe Merge Pattern (Bash + jq)

```bash
#!/bin/bash

# Add hook to settings.json using jq
jq '.hooks.pre_tool_use += [{
  "script": ".claude/hooks/pre_tool_use/new-hook.py",
  "enabled": true,
  "priority": 5
}]' .claude/settings.json > .claude/settings.json.tmp

mv .claude/settings.json.tmp .claude/settings.json
```

---

### Step 7: Validate Updated Settings

**Validation checklist**:

```bash
# 1. JSON syntax valid
python3 -m json.tool .claude/settings.json > /dev/null
echo "JSON syntax: $?"

# 2. All hook scripts exist
jq -r '.hooks | to_entries[] | .value[] | .script' .claude/settings.json | while read script; do
  if [ -f "$script" ]; then
    echo "✅ $script"
  else
    echo "❌ MISSING: $script"
  fi
done

# 3. All triad agents exist
jq -r '.triads | to_entries[] | .value.agents[]' .claude/settings.json | while read agent; do
  if [ -f ".claude/agents/**/$agent.md" ]; then
    echo "✅ Agent: $agent"
  else
    echo "⚠️ Agent not found: $agent"
  fi
done

# 4. No duplicate hook scripts
jq -r '.hooks | to_entries[] | .value[] | .script' .claude/settings.json | sort | uniq -d
# (empty output = no duplicates)
```

---

## 📊 Output Format

```yaml
settings_updated:
  path: ".claude/settings.json"
  changes:
    - type: "{{hook|triad|project}}"
      action: "{{add|update|remove}}"
      details: "{{description}}"
  validation:
    json_syntax: "{{PASS|FAIL}}"
    hook_scripts_exist: "{{PASS|FAIL}}"
    triad_agents_exist: "{{PASS|FAIL}}"
    no_duplicates: "{{PASS|FAIL}}"
  hooks_registered: {{COUNT}}
  triads_registered: {{COUNT}}
```

---

## 💡 Complete Settings.json Examples

### Example 1: Software Development Project

**File**: `.claude/settings.json`

```json
{
  "hooks": {
    "pre_tool_use": [
      {
        "script": ".claude/hooks/pre_tool_use/validate-read-access.py",
        "enabled": true,
        "priority": 10
      }
    ],
    "post_tool_use": [
      {
        "script": ".claude/hooks/post_tool_use/log-tool-usage.sh",
        "enabled": true,
        "priority": 5
      }
    ],
    "user_prompt_submit": [
      {
        "script": ".claude/hooks/user_prompt_submit/inject-context.py",
        "enabled": true
      }
    ],
    "stop": [
      {
        "script": ".claude/hooks/stop/validate-completion.py",
        "enabled": true,
        "priority": 5
      }
    ]
  },
  "triads": {
    "idea_validation_triad": {
      "version": "1.0.0",
      "agents": [
        "research-analyst",
        "community-researcher",
        "validation-synthesizer"
      ],
      "purpose": "Research ideas, validate community need, prioritize features",
      "status": "ready"
    },
    "design_triad": {
      "version": "1.0.0",
      "agents": [
        "validation-synthesizer",
        "solution-architect",
        "design-bridge"
      ],
      "purpose": "Create architecture, make decisions, write ADRs",
      "status": "ready"
    },
    "implementation_triad": {
      "version": "1.0.0",
      "agents": [
        "design-bridge",
        "senior-developer",
        "test-engineer"
      ],
      "purpose": "Write production code, create tests, ensure quality",
      "status": "ready"
    },
    "garden_tending_triad": {
      "version": "1.0.0",
      "agents": [
        "cultivator",
        "pruner",
        "gardener-bridge"
      ],
      "purpose": "Refactor, reduce technical debt, improve code quality",
      "status": "ready"
    },
    "deployment_triad": {
      "version": "1.0.0",
      "agents": [
        "gardener-bridge",
        "release-manager",
        "documentation-updater"
      ],
      "purpose": "Create releases, update docs, publish packages",
      "status": "ready"
    },
    "system_upgrade_triad": {
      "version": "1.0.0",
      "agents": [
        "gap-analyzer",
        "upgrade-executor",
        "upgrade-bridge"
      ],
      "purpose": "Intelligently upgrade existing projects to template system",
      "status": "ready",
      "note": "Meta-level agents that upgrade projects to template architecture. Invoke with /upgrade-to-templates"
    }
  },
  "project": {
    "name": "Triads Plugin",
    "version": "0.9.0-alpha.1",
    "description": "Claude Code plugin for generating custom triad workflows",
    "domain": "software-development",
    "template_version": "1.0.0",
    "constitutional_architecture": true,
    "triads_count": 6,
    "agents_count": 18
  }
}
```

---

### Example 2: Minimal Settings (New Project)

**File**: `.claude/settings.json`

```json
{
  "hooks": {},
  "triads": {},
  "project": {
    "name": "My Project",
    "version": "0.1.0",
    "domain": "software-development"
  }
}
```

---

### Example 3: Research Project Settings

**File**: `.claude/settings.json`

```json
{
  "hooks": {
    "pre_tool_use": [
      {
        "script": ".claude/hooks/pre_tool_use/validate-data-access.py",
        "enabled": true,
        "priority": 10
      }
    ],
    "stop": [
      {
        "script": ".claude/hooks/stop/validate-citations.py",
        "enabled": true,
        "priority": 5
      }
    ]
  },
  "triads": {
    "literature_review_triad": {
      "version": "1.0.0",
      "agents": [
        "search-coordinator",
        "paper-analyzer",
        "synthesis-writer"
      ],
      "purpose": "Search literature, analyze papers, synthesize findings",
      "status": "ready"
    },
    "analysis_triad": {
      "version": "1.0.0",
      "agents": [
        "data-validator",
        "statistical-analyst",
        "results-interpreter"
      ],
      "purpose": "Validate data, run statistical tests, interpret results",
      "status": "ready"
    }
  },
  "project": {
    "name": "Research Study",
    "version": "1.0.0",
    "domain": "research",
    "irb_protocol": "IRB-2024-001",
    "template_version": "1.0.0",
    "constitutional_architecture": true
  }
}
```

---

## 🎯 Settings Best Practices

### 1. Version Everything

```json
{
  "project": {
    "version": "1.2.3",
    "template_version": "1.0.0"
  },
  "triads": {
    "my_triad": {
      "version": "2.0.1"
    }
  }
}
```

**Why**: Track changes, support migrations

---

### 2. Document Status

```json
{
  "triads": {
    "experimental_triad": {
      "status": "beta",
      "note": "Under active development, may change"
    },
    "deprecated_triad": {
      "status": "deprecated",
      "note": "Use new_triad instead. Will be removed in v2.0.0"
    }
  }
}
```

**Why**: Clear communication about stability

---

### 3. Use Descriptive Names

```json
{
  "triads": {
    "system_upgrade_triad": {  // ✅ GOOD - clear purpose
      "purpose": "..."
    }
  }
}

// ❌ BAD
{
  "triads": {
    "triad1": {  // ❌ Not descriptive
      "purpose": "..."
    }
  }
}
```

---

### 4. Maintain Hook Priority Order

```json
{
  "hooks": {
    "pre_tool_use": [
      {
        "script": "validate-access.py",
        "priority": 10  // Runs first (authentication)
      },
      {
        "script": "log-request.py",
        "priority": 5   // Runs second (logging)
      }
    ]
  }
}
```

**Why**: Dependencies between hooks may exist

---

### 5. Comment Complex Configurations

```json
{
  "triads": {
    "custom_workflow": {
      "version": "1.0.0",
      "agents": ["agent-a", "agent-b", "agent-c"],
      "purpose": "Custom workflow for XYZ use case",
      "note": "Agent-B must run before Agent-C due to dependency on intermediate knowledge graph state. See docs/workflows/custom.md for details."
    }
  }
}
```

---

### 6. Backup Before Major Changes

```bash
# Backup settings before update
cp .claude/settings.json .claude/settings.json.backup

# Make changes
...

# Restore if needed
mv .claude/settings.json.backup .claude/settings.json
```

---

## 🎯 Common Update Patterns

### Pattern 1: Add New Hook

```python
import json

with open('.claude/settings.json', 'r') as f:
    settings = json.load(f)

# Add hook to pre_tool_use
if 'hooks' not in settings:
    settings['hooks'] = {}

if 'pre_tool_use' not in settings['hooks']:
    settings['hooks']['pre_tool_use'] = []

settings['hooks']['pre_tool_use'].append({
    "script": ".claude/hooks/pre_tool_use/new-hook.py",
    "enabled": True,
    "priority": 10
})

with open('.claude/settings.json', 'w') as f:
    json.dump(settings, f, indent=2)
```

---

### Pattern 2: Disable Hook (Don't Delete)

```python
import json

with open('.claude/settings.json', 'r') as f:
    settings = json.load(f)

# Find and disable hook
for hook in settings['hooks']['pre_tool_use']:
    if hook['script'] == '.claude/hooks/pre_tool_use/validate-read-access.py':
        hook['enabled'] = False
        break

with open('.claude/settings.json', 'w') as f:
    json.dump(settings, f, indent=2)
```

---

### Pattern 3: Add New Triad

```python
import json

with open('.claude/settings.json', 'r') as f:
    settings = json.load(f)

# Add triad
if 'triads' not in settings:
    settings['triads'] = {}

settings['triads']['new_triad'] = {
    "version": "1.0.0",
    "agents": ["agent-1", "agent-2", "agent-3"],
    "purpose": "Triad purpose description",
    "status": "ready"
}

with open('.claude/settings.json', 'w') as f:
    json.dump(settings, f, indent=2)
```

---

### Pattern 4: Update Project Version

```python
import json

with open('.claude/settings.json', 'r') as f:
    settings = json.load(f)

# Increment version (assuming semantic versioning)
current = settings['project']['version']
major, minor, patch = map(int, current.split('.'))
patch += 1  # Increment patch version

settings['project']['version'] = f"{major}.{minor}.{patch}"

with open('.claude/settings.json', 'w') as f:
    json.dump(settings, f, indent=2)
```

---

## 🎯 Validation Script

**File**: `.claude/scripts/validate-settings.py`

```python
#!/usr/bin/env python3
"""
Validate .claude/settings.json configuration.
"""

import json
import sys
import os
from pathlib import Path

def validate_settings(settings_path='.claude/settings.json'):
    """Validate settings.json structure and references."""

    print(f"Validating {settings_path}...")

    # Check file exists
    if not os.path.exists(settings_path):
        print(f"❌ File not found: {settings_path}")
        return False

    # Load and validate JSON
    try:
        with open(settings_path, 'r') as f:
            settings = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return False

    print("✅ Valid JSON syntax")

    # Validate hook scripts exist
    if 'hooks' in settings:
        for event_type, hooks in settings['hooks'].items():
            for hook in hooks:
                script = hook.get('script')
                if script and not os.path.exists(script):
                    print(f"❌ Hook script not found: {script}")
                    return False
                elif script:
                    print(f"✅ Hook script exists: {script}")

    # Validate triad agents exist
    if 'triads' in settings:
        for triad_name, triad_config in settings['triads'].items():
            agents = triad_config.get('agents', [])
            for agent in agents:
                # Check in .claude/agents/**/*.md
                agent_files = list(Path('.claude/agents').rglob(f'{agent}.md'))
                if not agent_files:
                    print(f"⚠️ Agent file not found: {agent}")
                else:
                    print(f"✅ Agent exists: {agent}")

    print("\n✅ Validation complete")
    return True

if __name__ == "__main__":
    success = validate_settings()
    sys.exit(0 if success else 1)
```

**Usage**:
```bash
chmod +x .claude/scripts/validate-settings.py
.claude/scripts/validate-settings.py
```

---

## 🎯 Success Criteria

- [ ] `.claude/settings.json` file exists
- [ ] JSON syntax is valid
- [ ] All hook scripts exist at specified paths
- [ ] All triad agents referenced exist
- [ ] No duplicate hook registrations
- [ ] Hook priorities are logical
- [ ] Triad versions follow semantic versioning
- [ ] Project metadata is complete
- [ ] Validation script passes

---

**This skill updates `.claude/settings.json` configuration following Claude Code patterns.**

**Version**: 1.0.0
**Last Updated**: 2025-10-27
**Source**: Claude Code configuration patterns
