---
name: create-release
description: Automate full release process - version bump, changelog, git tag, GitHub release. Keywords - release, deploy, publish, version, bump, changelog, tag, deployment
category: automation
domain: software-development
allowed_tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob", "Task"]
---

# Create Release Skill

**Purpose**: Fully automate the release process including version bumping, changelog generation, git tagging, and GitHub release creation.

---

## Skill Procedure

### Phase 1: DETERMINE VERSION

**Objective**: Analyze changes since last release to determine semantic version bump.

**Actions**:
1. Get current version from plugin.json
2. Get commits since last tag
3. Analyze commit types:
   - `feat:` → MINOR bump
   - `fix:` → PATCH bump
   - `BREAKING CHANGE:` → MAJOR bump
   - Multiple types → highest takes precedence

**Example**:
```bash
# Current version
current_version=$(jq -r .version .claude-plugin/plugin.json)

# Get commits since last tag
git log $(git describe --tags --abbrev=0)..HEAD --oneline

# Analyze commit types
if grep "BREAKING CHANGE" commits.txt; then
  bump_type="major"
elif grep "^feat:" commits.txt; then
  bump_type="minor"
else
  bump_type="patch"
fi
```

---

### Phase 2: UPDATE VERSION FILES

**Objective**: Update version in all required files per Version Bump Checklist.

**CRITICAL CHECKLIST** (from knowledge graph):
- [ ] `.claude-plugin/plugin.json` - Update `version` field
- [ ] `.claude-plugin/marketplace.json` - Update `plugins[].version`
- [ ] `pyproject.toml` - Update `project.version`
- [ ] `CHANGELOG.md` - Add new version entry

**Additional Files** (if they exist):
- [ ] `package.json` - Update `version` field
- [ ] `setup.py` - Update `version` parameter
- [ ] `VERSION` file - Update version string
- [ ] Any `__version__` in Python files

**Action Template**:
```python
files_to_update = [
    {
        "path": ".claude-plugin/plugin.json",
        "type": "json",
        "field": "version",
        "required": True
    },
    {
        "path": ".claude-plugin/marketplace.json",
        "type": "json",
        "field": "plugins[0].version",
        "required": True
    },
    {
        "path": "pyproject.toml",
        "type": "toml",
        "field": "project.version",
        "required": True
    },
    {
        "path": "package.json",
        "type": "json",
        "field": "version",
        "required": False
    }
]

for file in files_to_update:
    if file["required"] or os.path.exists(file["path"]):
        update_version_in_file(file, new_version)
```

---

### Phase 3: GENERATE CHANGELOG

**Objective**: Create comprehensive changelog from commits.

**Format**:
```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New features (from feat: commits)

### Changed
- Improvements (from refactor: commits)

### Fixed
- Bug fixes (from fix: commits)

### Security
- Security fixes (if any)

### Breaking Changes
- Breaking changes (if any)
```

**Action**:
1. Parse commits by type
2. Group into categories
3. Generate user-friendly descriptions
4. Update CHANGELOG.md with new section

---

### Phase 4: RUN TESTS

**Objective**: Ensure all tests pass before release.

**Actions**:
```bash
# Python tests
if [ -f "pytest.ini" ] || [ -d "tests" ]; then
    pytest --tb=short
fi

# JavaScript tests
if [ -f "package.json" ]; then
    npm test
fi

# Verify version files updated correctly
for file in plugin.json marketplace.json pyproject.toml; do
    grep -q "$new_version" "$file" || exit 1
done
```

---

### Phase 5: COMMIT AND TAG

**Objective**: Create git commit and annotated tag.

**Actions**:
```bash
# Stage all version files
git add .claude-plugin/plugin.json
git add .claude-plugin/marketplace.json
git add pyproject.toml
git add CHANGELOG.md
git add package.json setup.py VERSION  # if they exist

# Commit with conventional message
git commit -m "chore: Release v${new_version}

- Updated version to ${new_version}
- Generated changelog
- All tests passing"

# Create annotated tag
git tag -a "v${new_version}" -m "Release v${new_version}

${changelog_summary}"

# Push changes and tag
git push origin main
git push origin "v${new_version}"
```

---

### Phase 6: CREATE GITHUB RELEASE

**Objective**: Create GitHub release with artifacts.

**Actions**:
```bash
# Create release notes file
cat > RELEASE_NOTES.md << EEOF
${changelog_content}

## Installation

\`\`\`bash
# Claude Code plugin
claude plugin install triads@${new_version}

# Python package
pip install triads==${new_version}
\`\`\`

## Verification

\`\`\`bash
# Verify installation
claude plugin list | grep triads
\`\`\`
EEOF

# Create GitHub release
gh release create "v${new_version}" \
  --title "v${new_version}: ${release_title}" \
  --notes-file RELEASE_NOTES.md \
  --verify-tag
```

---

### Phase 7: DEPLOY PACKAGES

**Objective**: Publish to package registries (if applicable).

**Actions**:
```bash
# Publish to npm (if package.json exists)
if [ -f "package.json" ]; then
    npm publish
fi

# Build and publish to PyPI (if setup.py exists)
if [ -f "setup.py" ] || [ -f "pyproject.toml" ]; then
    python -m build
    python -m twine upload dist/*
fi

# Update marketplace (if applicable)
if [ -f ".claude-plugin/marketplace.json" ]; then
    echo "Remember to PR marketplace.json to central registry"
fi
```

---

## Error Handling

### Version Conflict
- **Symptom**: Version already exists
- **Response**: Check if tag was already created, suggest next version

### Test Failures
- **Symptom**: Tests fail during Phase 4
- **Response**: Abort release, show failing tests, suggest fixes

### Missing Required Files
- **Symptom**: Required version file missing
- **Response**: List missing files, abort with clear error

### Git State Issues
- **Symptom**: Uncommitted changes or not on main branch
- **Response**: Show git status, suggest stashing or switching branches

---

## Usage Examples

### Example 1: Patch Release
```
User: "Create release for the bug fixes"

Skill:
1. Analyzes commits → finds only fix: commits
2. Bumps patch version: 0.14.0 → 0.14.1
3. Updates all 4 required files + any optional ones
4. Generates changelog with Fixed section
5. Runs tests → all pass
6. Creates commit and tag
7. Creates GitHub release
```

### Example 2: Minor Release
```
User: "Release the new workspace features"

Skill:
1. Analyzes commits → finds feat: commits
2. Bumps minor version: 0.14.1 → 0.15.0
3. Updates all version files
4. Generates changelog with Added section
5. Tests, commits, tags, releases
```

### Example 3: Emergency Patch
```
User: "Emergency release for security fix"

Skill:
1. Detects security fix needed
2. Suggests patch bump with Security section
3. Fast-tracks through process
4. Highlights security fix in release notes
```

---

## Integration Points

### With Release Manager Agent
This skill can invoke the release-manager agent for complex deployments:
```
Task(
    subagent_type="agent:deployment:release-manager",
    description="Handle deployment",
    prompt="Deploy version {new_version} after release created"
)
```

### With Garden Tending
Ensures code quality before release:
- Checks if Garden Tending was run recently
- Suggests running if many changes accumulated

### With Knowledge Graph
Updates deployment graph with release information:
```markdown
[GRAPH_UPDATE]
type: add_node
node_id: release_v{version}
node_type: Entity
label: Release v{version}
[/GRAPH_UPDATE]
```

---

## Constitutional Compliance

- **Evidence-Based**: Shows all commits analyzed for version decision
- **Thoroughness**: Updates ALL required files from checklist
- **Transparency**: Shows each step of release process
- **Verification**: Tests must pass before release
- **No Ambiguity**: Clear version bump rules

---

## Invocation

This skill is triggered by:
- "Create release"
- "Bump version"
- "Deploy new version"
- "Publish release"
- "Generate changelog"
- "Tag release"

Or programmatically:
```python
from triads.skills import invoke_skill

result = invoke_skill(
    "create-release",
    version_type="patch",  # or "minor", "major", "auto"
    dry_run=False
)
```

---

*Generated by release-skill-generator v1.0.0*
*Created: 2024-11-03*
*Last Updated: 2024-11-03*
