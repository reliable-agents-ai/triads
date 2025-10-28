"""Test upgrade-executor.md integration with Steps 6.9 and 6.10."""

import pytest
from pathlib import Path


def test_upgrade_executor_has_steps_6_9_and_6_10():
    """Test upgrade-executor.md contains new steps in correct order."""
    executor_path = Path(".claude/agents/system-upgrade/upgrade-executor.md")
    assert executor_path.exists(), "upgrade-executor.md not found"

    content = executor_path.read_text()

    # Assert Step 6.9 exists
    assert "### Step 6.9: Analyze Entry Points" in content, "Step 6.9 heading not found"
    assert "python triads/entry_point_analyzer.py" in content, "Step 6.9 command not found"
    assert "routing_decision_table.yaml" in content, "Step 6.9 output not mentioned"

    # Assert Step 6.10 exists
    assert "### Step 6.10: Generate Coordination Skills" in content, "Step 6.10 heading not found"
    assert "python triads/coordination_skill_generator.py" in content, "Step 6.10 command not found"
    assert "coordinate-{work_type}.md" in content, "Step 6.10 output pattern not mentioned"

    # Assert steps are in correct order
    step_6_9_pos = content.find("### Step 6.9")
    step_6_10_pos = content.find("### Step 6.10")
    step_7_pos = content.find("### Step 7")

    assert step_6_9_pos > 0, "Step 6.9 not found"
    assert step_6_10_pos > 0, "Step 6.10 not found"
    assert step_7_pos > 0, "Step 7 not found"

    assert step_6_9_pos < step_6_10_pos, "Step 6.9 must come before Step 6.10"
    assert step_6_10_pos < step_7_pos, "Step 6.10 must come before Step 7"


def test_step_6_9_has_all_required_sections():
    """Test Step 6.9 has all required sections."""
    executor_path = Path(".claude/agents/system-upgrade/upgrade-executor.md")
    content = executor_path.read_text()

    # Extract Step 6.9 section
    step_6_9_start = content.find("### Step 6.9: Analyze Entry Points")
    step_6_10_start = content.find("### Step 6.10: Generate Coordination Skills")
    step_6_9_content = content[step_6_9_start:step_6_10_start]

    # Check required sections
    assert "**Objective**:" in step_6_9_content, "Step 6.9 missing Objective"
    assert "**Purpose**:" in step_6_9_content, "Step 6.9 missing Purpose"
    assert "**Prerequisites**:" in step_6_9_content, "Step 6.9 missing Prerequisites"
    assert "**Command**:" in step_6_9_content, "Step 6.9 missing Command"
    assert "**What This Does**:" in step_6_9_content, "Step 6.9 missing What This Does"
    assert "**Validation Steps**:" in step_6_9_content, "Step 6.9 missing Validation Steps"
    assert "**Expected Output**:" in step_6_9_content, "Step 6.9 missing Expected Output"
    assert "**Example Output Structure**:" in step_6_9_content, "Step 6.9 missing Example Output"
    assert "**Error Handling**:" in step_6_9_content, "Step 6.9 missing Error Handling"

    # Check validation checkboxes
    assert "- [ ] Check `.claude/routing_decision_table.yaml` was created" in step_6_9_content
    assert "- [ ] File contains `routing_decisions` section" in step_6_9_content
    assert "- [ ] File contains `fallback` section" in step_6_9_content
    assert "- [ ] File contains `ambiguity_resolution` section" in step_6_9_content


def test_step_6_10_has_all_required_sections():
    """Test Step 6.10 has all required sections."""
    executor_path = Path(".claude/agents/system-upgrade/upgrade-executor.md")
    content = executor_path.read_text()

    # Extract Step 6.10 section
    step_6_10_start = content.find("### Step 6.10: Generate Coordination Skills")
    step_7_start = content.find("### Step 7: Update CLAUDE.md with @imports")
    step_6_10_content = content[step_6_10_start:step_7_start]

    # Check required sections
    assert "**Objective**:" in step_6_10_content, "Step 6.10 missing Objective"
    assert "**Purpose**:" in step_6_10_content, "Step 6.10 missing Purpose"
    assert "**Prerequisites**:" in step_6_10_content, "Step 6.10 missing Prerequisites"
    assert "**Command**:" in step_6_10_content, "Step 6.10 missing Command"
    assert "**What This Does**:" in step_6_10_content, "Step 6.10 missing What This Does"
    assert "**Validation Steps**:" in step_6_10_content, "Step 6.10 missing Validation Steps"
    assert "**Expected Output**:" in step_6_10_content, "Step 6.10 missing Expected Output"
    assert "**Example Filenames**:" in step_6_10_content, "Step 6.10 missing Example Filenames"
    assert "**Example Skill Structure" in step_6_10_content, "Step 6.10 missing Example Structure"
    assert "**Error Handling**:" in step_6_10_content, "Step 6.10 missing Error Handling"

    # Check validation checkboxes
    assert "- [ ] One coordination skill generated per work type" in step_6_10_content
    assert "- [ ] Skills placed in `.claude/skills/{domain}/` directory" in step_6_10_content
    assert "- [ ] Each skill has filename pattern: `coordinate-{work_type}.md`" in step_6_10_content
    assert "- [ ] Each skill has valid frontmatter" in step_6_10_content
    assert "- [ ] Each skill contains 4-phase workflow:" in step_6_10_content


def test_step_6_9_command_syntax():
    """Test Step 6.9 command has correct syntax."""
    executor_path = Path(".claude/agents/system-upgrade/upgrade-executor.md")
    content = executor_path.read_text()

    # Check entry_point_analyzer.py command
    assert "python triads/entry_point_analyzer.py" in content
    assert "--settings .claude/settings.json" in content
    assert "--skills-dir .claude/skills/" in content
    assert "--output .claude/routing_decision_table.yaml" in content


def test_step_6_10_command_syntax():
    """Test Step 6.10 command has correct syntax."""
    executor_path = Path(".claude/agents/system-upgrade/upgrade-executor.md")
    content = executor_path.read_text()

    # Check coordination_skill_generator.py command
    assert "python triads/coordination_skill_generator.py" in content
    assert "--routing-table .claude/routing_decision_table.yaml" in content
    assert "--output-dir .claude/skills/" in content


def test_step_6_9_example_output_valid_yaml():
    """Test Step 6.9 example output is valid YAML structure."""
    executor_path = Path(".claude/agents/system-upgrade/upgrade-executor.md")
    content = executor_path.read_text()

    # Check example YAML structure
    assert "version: 1.0.0" in content
    assert "domain: software-development" in content
    assert "routing_decisions:" in content
    assert "target_triad:" in content
    assert "entry_agent:" in content
    assert "brief_skill:" in content
    assert "confidence:" in content
    assert "fallback:" in content
    assert "ambiguity_resolution:" in content


def test_step_6_10_example_skill_structure():
    """Test Step 6.10 includes example skill structure."""
    executor_path = Path(".claude/agents/system-upgrade/upgrade-executor.md")
    content = executor_path.read_text()

    # Check coordinate-feature.md example
    assert "coordinate-feature.md" in content
    assert "name: coordinate-feature" in content
    assert "category: coordination" in content
    assert "domain: software-development" in content
    assert "allowed_tools:" in content

    # Check 4-phase workflow
    assert "### Phase 1: CREATE BRIEF" in content
    assert "### Phase 2: ROUTE TO TRIAD" in content
    assert "### Phase 3: INVOKE TRIAD" in content
    assert "### Phase 4: MONITOR EXECUTION" in content


def test_steps_reference_correct_tools():
    """Test steps reference the correct Python tools."""
    executor_path = Path(".claude/agents/system-upgrade/upgrade-executor.md")
    content = executor_path.read_text()

    # Check Step 6.9 references entry_point_analyzer.py
    step_6_9_start = content.find("### Step 6.9")
    step_6_10_start = content.find("### Step 6.10")
    step_6_9_section = content[step_6_9_start:step_6_10_start]

    assert "entry_point_analyzer.py" in step_6_9_section

    # Check Step 6.10 references coordination_skill_generator.py
    step_7_start = content.find("### Step 7")
    step_6_10_section = content[step_6_10_start:step_7_start]

    assert "coordination_skill_generator.py" in step_6_10_section


def test_formatting_consistency():
    """Test formatting is consistent with existing steps."""
    executor_path = Path(".claude/agents/system-upgrade/upgrade-executor.md")
    content = executor_path.read_text()

    # Check markdown formatting
    assert "### Step 6.9: Analyze Entry Points\n" in content
    assert "### Step 6.10: Generate Coordination Skills\n" in content
    assert "### Step 7: Update CLAUDE.md with @imports\n" in content

    # Check separator lines
    step_6_9_section = content[content.find("### Step 6.9"):content.find("### Step 6.10")]
    step_6_10_section = content[content.find("### Step 6.10"):content.find("### Step 7")]

    # Each step should end with ---
    assert "---\n" in step_6_9_section
    assert "---\n" in step_6_10_section
