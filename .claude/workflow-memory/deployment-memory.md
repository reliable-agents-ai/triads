# Deployment Workflow - Context Memory

**Workflow**: Deployment
**Domain**: {{DOMAIN_TYPE}}
**Started**: {{START_DATE}}
**Status**: {{STATUS}}

This file captures context for deployment workflows (releases, documentation, publishing), ensuring continuity across gardener-bridge → release-manager → documentation-updater.

---

## 🎯 WORKFLOW PURPOSE

**Objective**: Create releases, update documentation, publish packages, prepare for deployment.

**Success Criteria**:
- [ ] Version bumped correctly (semantic versioning)
- [ ] CHANGELOG updated with all changes
- [ ] Documentation updated (README, guides)
- [ ] Release created (GitHub/GitLab)
- [ ] Package published (PyPI, npm, etc.)
- [ ] Installation verified

---

## 📊 FROM GARDEN TENDING

### Pre-Deployment State

```yaml
from_garden_tending:
  code_quality:
    tests_passing: "{{COUNT}}/{{TOTAL}}"
    test_coverage: "{{PERCENTAGE}}%"
    linting_status: "{{PASSED|FAILED}}"
    security_scan: "{{PASSED|FAILED}}"

  refactoring_summary:
    refactorings_applied: {{COUNT}}
    quality_improvements:
      - "{{IMPROVEMENT_1}}"
      - "{{IMPROVEMENT_2}}"

  ready_for_deployment: "{{YES|NO}}"
```

---

## 📋 RELEASE MANAGER WORK

### Version Information

```yaml
version:
  current: "{{CURRENT_VERSION}}"  # e.g., "0.8.0"
  new: "{{NEW_VERSION}}"          # e.g., "0.9.0"
  bump_type: "{{MAJOR|MINOR|PATCH}}"

  rationale: |
    {{WHY_THIS_VERSION_NUMBER}}

semantic_versioning:
  major: "Breaking changes"       # Incompatible API changes
  minor: "New features"           # Backward-compatible features
  patch: "Bug fixes"              # Backward-compatible bug fixes

  decision:
    breaking_changes: "{{YES|NO}}"
    new_features: "{{YES|NO}}"
    bug_fixes: "{{YES|NO}}"
    → bump_type: "{{MAJOR|MINOR|PATCH}}"
```

**Example**:
```yaml
version:
  current: "0.8.0"
  new: "0.9.0"
  bump_type: "MINOR"

  rationale: |
    New feature: AI-powered code suggestions (backward-compatible).
    No breaking changes.
    → Bump MINOR version: 0.8.0 → 0.9.0

semantic_versioning_decision:
  breaking_changes: "NO"
  new_features: "YES" # AI code suggestions
  bug_fixes: "YES"    # Also fixed 3 bugs
  → bump_type: "MINOR"
```

### CHANGELOG Generation

```yaml
changelog:
  version: "{{NEW_VERSION}}"
  date: "{{RELEASE_DATE}}"

  sections:
    added:
      - "{{FEATURE_1}}"
      - "{{FEATURE_2}}"

    changed:
      - "{{CHANGE_1}}"
      - "{{CHANGE_2}}"

    deprecated:
      - "{{DEPRECATED_1}}"

    removed:
      - "{{REMOVED_1}}"

    fixed:
      - "{{BUG_FIX_1}}"
      - "{{BUG_FIX_2}}"

    security:
      - "{{SECURITY_FIX_1}}"
```

**Example (Following Keep a Changelog)**:
```yaml
changelog:
  version: "0.9.0"
  date: "2024-10-28"

  sections:
    added:
      - "AI-powered code suggestions via Claude API"
      - "Context indexing with semantic search (ChromaDB)"
      - "Redis caching layer to reduce API costs"
      - "User settings for budget cap and privacy mode"

    changed:
      - "Improved suggestion latency from 150ms to 85ms with caching"
      - "Refactored API endpoints for better testability"
      - "Updated editor plugin to use async API calls"

    deprecated:
      - "Legacy suggest_v1 endpoint (will be removed in v1.0.0)"

    removed:
      - "Experimental local LLM mode (replaced with Claude API)"

    fixed:
      - "Fixed memory leak in Context Indexer (#45)"
      - "Fixed cache invalidation bug (#52)"
      - "Fixed editor freeze when network offline (#58)"

    security:
      - "Added user consent dialog before sending code to API"
      - "Implemented API key encryption in settings"
```

### Release Artifacts

```yaml
release_artifacts:
  - type: "{{SOURCE_CODE|BINARY|DOCKER_IMAGE}}"
    name: "{{ARTIFACT_NAME}}"
    location: "{{PATH_OR_URL}}"
    checksum: "{{SHA256_CHECKSUM}}"

  - type: "SOURCE_CODE"
    name: "triads-v0.9.0.tar.gz"
    location: "https://github.com/user/triads/archive/v0.9.0.tar.gz"
    checksum: "sha256:abc123..."

  - type: "WHEEL"
    name: "triads-0.9.0-py3-none-any.whl"
    location: "dist/triads-0.9.0-py3-none-any.whl"
    checksum: "sha256:def456..."
```

### Release Notes

```markdown
# Release v0.9.0 - AI-Powered Code Suggestions

**Release Date**: 2024-10-28

## 🎉 Highlights

{{MAJOR_FEATURE_HIGHLIGHTS}}

## ✨ What's New

{{FEATURES_AND_IMPROVEMENTS}}

## 🐛 Bug Fixes

{{BUG_FIXES_LIST}}

## 🔒 Security

{{SECURITY_FIXES}}

## 📦 Installation

{{INSTALLATION_INSTRUCTIONS}}

## 🔄 Upgrade Guide

{{MIGRATION_INSTRUCTIONS_IF_BREAKING_CHANGES}}

## 📊 Metrics

- Test coverage: {{COVERAGE}}%
- Tests passing: {{COUNT}}/{{TOTAL}}
- Performance: {{METRIC}}

## 🙏 Contributors

{{CONTRIBUTOR_LIST}}
```

**Example**:
```markdown
# Release v0.9.0 - AI-Powered Code Suggestions

**Release Date**: 2024-10-28

## 🎉 Highlights

- **AI-Powered Code Suggestions**: Inline code completion using Claude API with project context
- **50% Faster**: Improved suggestion latency from 150ms to 85ms with intelligent caching
- **Privacy-First**: User consent required, local processing option available

## ✨ What's New

### AI Code Suggestions
- Inline suggestions based on cursor context and project files
- Semantic search finds relevant code examples from your project
- 70%+ acceptance rate in beta testing
- Budget cap enforcement to control API costs

### Performance Improvements
- Redis caching layer reduces API calls by 70%
- Async processing eliminates editor freezing
- Latency improved from 150ms to 85ms (p95)

### Privacy & Security
- User consent dialog before first API call
- API key encryption in settings
- Opt-in mode for code sharing

## 🐛 Bug Fixes

- Fixed memory leak in Context Indexer (#45) - indexing large projects no longer causes OOM
- Fixed cache invalidation bug (#52) - suggestions now update when files change
- Fixed editor freeze when network offline (#58) - graceful degradation with error message

## 🔒 Security

- Added user consent dialog before sending code to Claude API
- Implemented API key encryption using system keychain
- Updated dependencies to patch known vulnerabilities

## 📦 Installation

**Via pip**:
```bash
pip install triads==0.9.0
```

**Via source**:
```bash
git clone https://github.com/user/triads.git
cd triads
git checkout v0.9.0
pip install -e .
```

**VS Code Extension**:
- Install from marketplace: [Triads Code Suggestions](https://marketplace.visualstudio.com/items?itemName=user.triads)
- Or: `code --install-extension user.triads-0.9.0.vsix`

## 🔄 Upgrade Guide

### From v0.8.x

No breaking changes - upgrade is seamless:
```bash
pip install --upgrade triads
```

**New settings** (optional):
- `triads.apiKey`: Your Claude API key (encrypted in keychain)
- `triads.budgetCap`: Monthly budget limit (default: $50)
- `triads.privacyMode`: Require consent per session (default: true)

## 📊 Metrics

- Test coverage: 92%
- Tests passing: 247/247
- Performance: 85ms p95 latency (vs 100ms requirement)
- Cache hit rate: 71% (target: 70%)

## 🙏 Contributors

- @user - Design and implementation
- @contributor1 - Testing and feedback
- @contributor2 - Documentation improvements

**Full Changelog**: https://github.com/user/triads/blob/main/CHANGELOG.md
```

---

## 📋 DOCUMENTATION UPDATER WORK

### Documentation Updates

```yaml
documentation_updates:
  files_to_update:
    - file: "README.md"
      sections:
        - section: "Installation"
          changes: "{{WHAT_CHANGED}}"
          status: "{{UPDATED|PENDING}}"

        - section: "Features"
          changes: "Added AI code suggestions section"
          status: "UPDATED"

    - file: "docs/INSTALLATION.md"
      sections:
        - section: "Prerequisites"
          changes: "Added Redis requirement"
          status: "UPDATED"

        - section: "Configuration"
          changes: "Added API key setup instructions"
          status: "UPDATED"

    - file: "CHANGELOG.md"
      sections:
        - section: "v0.9.0"
          changes: "Added full changelog for v0.9.0"
          status: "UPDATED"

    - file: "docs/guides/ai-suggestions.md"
      sections:
        - section: "New guide"
          changes: "Created comprehensive guide for AI suggestions feature"
          status: "CREATED"
```

### README Updates

```yaml
readme_updates:
  version_badge: "Updated to v0.9.0"
  features_section:
    added:
      - "🤖 AI-powered code suggestions"
      - "🔍 Semantic code search"
      - "⚡ Intelligent caching"

  installation_section:
    updated: "Added pip install triads==0.9.0"

  configuration_section:
    added: "API key setup instructions"

  examples_section:
    added: "AI suggestions usage example"
```

### Link Verification

```yaml
link_verification:
  total_links: {{COUNT}}
  checked: {{COUNT}}
  broken: {{COUNT}}

  broken_links:
    - url: "{{BROKEN_LINK_1}}"
      location: "{{FILE}}:{{LINE}}"
      status: "{{HTTP_STATUS}}"
      fix: "{{CORRECTED_URL}}"
```

---

## 📋 PUBLISHING WORKFLOW

### Pre-Publish Checklist

```yaml
pre_publish:
  code_quality:
    - criterion: "All tests pass"
      status: "{{✅ PASSED | ❌ FAILED}}"
    - criterion: "Coverage ≥{{TARGET}}%"
      status: "{{PASSED|FAILED}}"
    - criterion: "No linting errors"
      status: "{{PASSED|FAILED}}"

  versioning:
    - criterion: "Version bumped in all files"
      status: "{{COMPLETE|INCOMPLETE}}"
      files:
        - "pyproject.toml: {{UPDATED|PENDING}}"
        - "package.json: {{UPDATED|PENDING}}"
        - "__version__.py: {{UPDATED|PENDING}}"

  documentation:
    - criterion: "CHANGELOG updated"
      status: "{{UPDATED|PENDING}}"
    - criterion: "README updated"
      status: "{{UPDATED|PENDING}}"
    - criterion: "All links verified"
      status: "{{VERIFIED|FAILED}}"

  git:
    - criterion: "Working directory clean"
      status: "{{CLEAN|DIRTY}}"
    - criterion: "On main branch"
      status: "{{YES|NO}}"
    - criterion: "Synced with remote"
      status: "{{SYNCED|DIVERGED}}"
```

### Build and Publish

```yaml
build_process:
  - step: "Build package"
    command: "{{BUILD_COMMAND}}"  # e.g., "python -m build"
    output: "{{OUTPUT_SUMMARY}}"
    status: "{{SUCCESS|FAILED}}"

  - step: "Run package checks"
    command: "{{CHECK_COMMAND}}"  # e.g., "twine check dist/*"
    output: "{{OUTPUT}}"
    status: "{{SUCCESS|FAILED}}"

  - step: "Publish to registry"
    command: "{{PUBLISH_COMMAND}}"  # e.g., "twine upload dist/*"
    registry: "{{REGISTRY_URL}}"    # e.g., "https://pypi.org"
    output: "{{OUTPUT}}"
    status: "{{SUCCESS|FAILED}}"

  - step: "Create git tag"
    command: "git tag v{{VERSION}}"
    status: "{{SUCCESS|FAILED}}"

  - step: "Push tag to remote"
    command: "git push origin v{{VERSION}}"
    status: "{{SUCCESS|FAILED}}"

  - step: "Create GitHub release"
    command: "gh release create v{{VERSION}} --notes-file RELEASE_NOTES.md"
    status: "{{SUCCESS|FAILED}}"
    url: "{{RELEASE_URL}}"
```

**Example**:
```yaml
build_process:
  - step: "Build package"
    command: "python -m build"
    output: |
      Successfully built triads-0.9.0.tar.gz
      Successfully built triads-0.9.0-py3-none-any.whl
    status: "SUCCESS"

  - step: "Run package checks"
    command: "twine check dist/*"
    output: "Checking dist/triads-0.9.0.tar.gz: PASSED\nChecking dist/triads-0.9.0-py3-none-any.whl: PASSED"
    status: "SUCCESS"

  - step: "Publish to PyPI"
    command: "twine upload dist/*"
    registry: "https://pypi.org"
    output: "Uploading triads-0.9.0... 100%\nView at: https://pypi.org/project/triads/0.9.0/"
    status: "SUCCESS"

  - step: "Create git tag"
    command: "git tag v0.9.0"
    status: "SUCCESS"

  - step: "Push tag to remote"
    command: "git push origin v0.9.0"
    status: "SUCCESS"

  - step: "Create GitHub release"
    command: "gh release create v0.9.0 --notes-file RELEASE_NOTES.md dist/*"
    status: "SUCCESS"
    url: "https://github.com/user/triads/releases/tag/v0.9.0"
```

---

## 📋 POST-DEPLOYMENT VERIFICATION

### Installation Testing

```yaml
installation_tests:
  - environment: "{{ENV_DESCRIPTION}}"  # e.g., "Fresh Python 3.11 venv"
    install_command: "pip install triads==0.9.0"
    status: "{{SUCCESS|FAILED}}"
    verification:
      - check: "{{WHAT_TO_VERIFY}}"
        command: "{{COMMAND}}"
        result: "{{RESULT}}"

  - environment: "Fresh Python 3.11 virtual environment (Ubuntu 22.04)"
    install_command: "pip install triads==0.9.0"
    status: "SUCCESS"
    verification:
      - check: "Package installed"
        command: "pip show triads"
        result: "Name: triads\nVersion: 0.9.0 ✅"

      - check: "CLI works"
        command: "triads --version"
        result: "triads v0.9.0 ✅"

      - check: "Import works"
        command: "python -c 'import triads; print(triads.__version__)'"
        result: "0.9.0 ✅"

  - environment: "Upgrade from v0.8.0 (macOS, Python 3.12)"
    install_command: "pip install --upgrade triads"
    status: "SUCCESS"
    verification:
      - check: "Upgrade successful"
        command: "pip show triads"
        result: "Version: 0.9.0 ✅"

      - check: "Settings preserved"
        command: "triads config show"
        result: "Previous settings intact ✅"
```

---

## 📊 KNOWLEDGE GRAPH UPDATES

```yaml
knowledge_nodes:
  - node_id: "RELEASE_{{VERSION}}_{{TIMESTAMP}}"
    node_type: "Release"
    label: "Released v{{VERSION}}"
    description: |
      Released version {{VERSION}} with {{FEATURE_COUNT}} new features.
      Published to {{REGISTRY}}.
      Installation verified on {{PLATFORM_COUNT}} platforms.
    confidence: 1.0
    evidence: |
      - Published: {{REGISTRY_URL}}/project/{{PROJECT}}/{{VERSION}}
      - GitHub release: {{GITHUB_RELEASE_URL}}
      - Installation tests: {{PASSED}}/{{TOTAL}} passed
      - Documentation updated: README, CHANGELOG, guides
    created_by: "release-manager"
    created_at: "{{TIMESTAMP}}"
```

---

## 🚨 ISSUES ENCOUNTERED

```yaml
issues:
  - issue_id: "DEP001"
    description: "{{WHAT_WENT_WRONG}}"
    impact: "{{IMPACT}}"
    resolution: "{{HOW_RESOLVED}}"

  - issue_id: "DEP002"
    description: "PyPI upload failed - API token expired"
    impact: "Could not publish package"
    resolution: "Generated new API token from PyPI settings, re-ran twine upload"
    prevention: "Set calendar reminder to rotate token before expiry"
```

---

## 🎯 SUCCESS METRICS

```yaml
success_metrics:
  deployment_complete:
    - criterion: "Version bumped correctly"
      status: "{{✅ COMPLETE | ⏳ IN PROGRESS}}"
    - criterion: "CHANGELOG updated"
      status: "{{STATUS}}"
    - criterion: "Documentation updated"
      status: "{{STATUS}}"
    - criterion: "Package published"
      status: "{{STATUS}}"
    - criterion: "Release created (GitHub)"
      status: "{{STATUS}}"
    - criterion: "Installation verified"
      status: "{{STATUS}}"

  quality_gates:
    - gate: "All pre-publish checks passed"
      status: "{{✅ PASSED | ❌ FAILED}}"
    - gate: "Installation successful on ≥3 platforms"
      status: "{{STATUS}}"
    - gate: "All documentation links valid"
      status: "{{STATUS}}"
```

---

## 📚 POST-DEPLOYMENT TASKS

```yaml
post_deployment:
  communication:
    - task: "Announce release on Twitter/X"
      status: "{{DONE|PENDING}}"
      link: "{{TWEET_URL}}"

    - task: "Post to Discord/Slack community"
      status: "{{DONE|PENDING}}"

    - task: "Update project website"
      status: "{{DONE|PENDING}}"

  monitoring:
    - task: "Monitor PyPI download stats"
      status: "{{MONITORING}}"
      metric: "{{COUNT}} downloads in first 24h"

    - task: "Watch for bug reports"
      status: "{{MONITORING}}"
      issues_filed: {{COUNT}}

  next_steps:
    - "{{NEXT_STEP_1}}"
    - "{{NEXT_STEP_2}}"
```

---

*This context memory ensures continuity and quality across the Deployment workflow.*

**Template Version**: v1.0.0
**Last Updated**: {{LAST_UPDATED}}
