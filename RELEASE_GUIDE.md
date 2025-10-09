# Release Guide

Guide for creating and publishing releases of Triad Generator.

---

## Overview

The repository is now configured with:
- ✅ GitHub Actions for automated releases
- ✅ Quick-install script for one-liner installation
- ✅ Version tracking (VERSION file)
- ✅ Git repository initialized with remote
- ✅ Issue and PR templates
- ✅ Validation workflow for CI/CD

Repository: https://github.com/reliable-agents-ai/triads

---

## First Time Setup

### 1. Push to GitHub

```bash
# Stage all files
git add .

# Commit
git commit -m "Initial commit - Triad Generator v0.0.1

- Self-discovering multi-agent system
- Generator triad (meta-level)
- TRUST framework enforcement
- Knowledge graph system
- Complete documentation
- GitHub Actions for releases"

# Push to main branch
git push -u origin main
```

### 2. Enable GitHub Actions

1. Go to: https://github.com/reliable-agents-ai/triads/settings/actions
2. Enable: "Allow all actions and reusable workflows"
3. Save

### 3. Set Up GitHub Pages (Optional)

For documentation hosting:
1. Go to: https://github.com/reliable-agents-ai/triads/settings/pages
2. Source: "Deploy from a branch"
3. Branch: "main" / "docs"
4. Save

---

## Creating a Release

### Automated Release (Recommended)

The GitHub Actions workflow automatically creates releases when you push a version tag:

```bash
# 1. Update VERSION file
echo "0.0.2" > VERSION

# 2. Commit changes
git add VERSION
git commit -m "Bump version to 0.0.2"
git push

# 3. Create and push tag
git tag v0.0.2
git push origin v0.0.2
```

**What happens automatically:**
1. ✅ GitHub Actions triggers on the v0.0.2 tag
2. ✅ Creates release tarball with all files
3. ✅ Generates SHA256 checksum
4. ✅ Creates GitHub Release with changelog
5. ✅ Attaches downloadable assets
6. ✅ Updates "latest" tag (for stable releases)

**Release will be available at:**
- https://github.com/reliable-agents-ai/triads/releases/tag/v0.0.2
- https://github.com/reliable-agents-ai/triads/releases/latest (for stable)

### Manual Release (Alternative)

If you need to create a release manually:

```bash
# 1. Run the release script
./create-release.sh 0.0.2

# 2. Upload to GitHub
# Go to: https://github.com/reliable-agents-ai/triads/releases/new
# - Tag: v0.0.2
# - Upload: releases/triad-generator-v0.0.2.tar.gz
# - Upload: releases/triad-generator-v0.0.2.tar.gz.sha256
```

---

## Version Numbering

Follow semantic versioning: `MAJOR.MINOR.PATCH`

### Pre-1.0.0 (Current Phase)
- **0.0.x**: Early development, testing
- **0.x.0**: Beta releases with significant features
- Breaking changes are expected

### Post-1.0.0
- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

### Pre-release Tags
- **v0.0.2-alpha**: Alpha release
- **v0.0.2-beta**: Beta release
- **v0.0.2-rc1**: Release candidate

Pre-release tags automatically marked as "Pre-release" on GitHub.

---

## Release Checklist

Before creating a release:

- [ ] All tests pass locally
- [ ] Documentation is up to date
- [ ] CHANGELOG or release notes prepared
- [ ] VERSION file updated
- [ ] Tested installation on clean system
- [ ] Tested on macOS and Linux (if applicable)
- [ ] Python 3.10, 3.11, 3.12 tested
- [ ] Breaking changes documented
- [ ] Migration guide provided (if needed)

---

## Testing a Release

### Test Quick Install

```bash
# Test the quick-install script
curl -sSL https://raw.githubusercontent.com/reliable-agents-ai/triads/main/quick-install.sh | bash
```

### Test Download Install

```bash
# Test release download
curl -LO https://github.com/reliable-agents-ai/triads/releases/download/v0.0.1/triad-generator-v0.0.1.tar.gz
tar -xzf triad-generator-v0.0.1.tar.gz
cd triad-generator-v0.0.1
./install-triads.sh --dry-run
```

### Verify Checksum

```bash
curl -LO https://github.com/reliable-agents-ai/triads/releases/download/v0.0.1/triad-generator-v0.0.1.tar.gz.sha256
sha256sum -c triad-generator-v0.0.1.tar.gz.sha256
```

---

## Hotfix Process

For urgent fixes to released versions:

```bash
# 1. Create hotfix branch from tag
git checkout -b hotfix/0.0.1-fix v0.0.1

# 2. Make fixes
# ... edit files ...

# 3. Update VERSION (patch increment)
echo "0.0.2" > VERSION

# 4. Commit and tag
git add .
git commit -m "Hotfix: Fix critical issue"
git tag v0.0.2
git push origin hotfix/0.0.1-fix
git push origin v0.0.2

# 5. Merge back to main
git checkout main
git merge hotfix/0.0.1-fix
git push origin main
```

---

## Troubleshooting Releases

### GitHub Actions Not Running

1. Check: https://github.com/reliable-agents-ai/triads/actions
2. Verify Actions are enabled in settings
3. Check workflow file syntax:
   ```bash
   # Validate YAML
   python3 -c "import yaml; yaml.safe_load(open('.github/workflows/release.yml'))"
   ```

### Release Failed

1. Check Actions logs: https://github.com/reliable-agents-ai/triads/actions
2. Common issues:
   - Missing files in bundle
   - Permission issues
   - Invalid tag format

### Fix and Re-run

```bash
# Delete failed tag
git tag -d v0.0.2
git push origin :refs/tags/v0.0.2

# Fix issues
# ... make changes ...

# Re-create tag
git tag v0.0.2
git push origin v0.0.2
```

---

## Download Statistics

View release download stats at:
https://github.com/reliable-agents-ai/triads/releases

Or via API:
```bash
curl https://api.github.com/repos/reliable-agents-ai/triads/releases/latest
```

---

## Communication

### Announcing Releases

**GitHub Release Notes**: Automatically generated from commits

**Additional Channels** (when ready):
- Twitter/X
- Blog post
- Newsletter
- Community forums

### Release Template

```markdown
## Triad Generator v0.0.2

### What's New
- Feature 1
- Feature 2
- Bug fix for issue #123

### Breaking Changes
- None (or list if applicable)

### Installation
\`\`\`bash
curl -sSL https://raw.githubusercontent.com/reliable-agents-ai/triads/main/quick-install.sh | bash
\`\`\`

### Full Changelog
https://github.com/reliable-agents-ai/triads/compare/v0.0.1...v0.0.2
```

---

## Next Steps After Release

1. Monitor issues for bug reports
2. Update documentation if needed
3. Plan next release features
4. Update project board/roadmap

---

**For more information:**
- [Contributing Guide](CONTRIBUTING.md)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Semantic Versioning](https://semver.org/)
