# Maintainer Quick Reference

Quick reference for common maintainer tasks.

---

## 🚀 Creating a Release

### Automated Release (Recommended)

```bash
# 1. Update version
echo "0.0.2" > VERSION

# 2. Commit
git add VERSION
git commit -m "Bump version to 0.0.2"
git push

# 3. Tag and push (triggers GitHub Action)
git tag v0.0.2
git push origin v0.0.2
```

**What happens automatically:**
- ✅ Builds release tarball
- ✅ Generates SHA256 checksum
- ✅ Creates GitHub Release
- ✅ Attaches downloadable assets
- ✅ Generates changelog

**Monitor:** https://github.com/reliable-agents-ai/triads/actions

---

## 📋 Pre-Release Checklist

Before creating a release:

- [ ] All tests passing locally
- [ ] GitHub Actions validation passing
- [ ] Documentation updated
- [ ] VERSION file updated
- [ ] Tested on clean system
- [ ] Tested installation methods:
  - [ ] Quick install script
  - [ ] Download release (from previous version)
  - [ ] Clone repo install
- [ ] Breaking changes documented (if any)
- [ ] Migration guide written (if needed)

---

## 🏷️ Version Numbering

**Current phase (pre-1.0.0):**
- `0.0.x` - Early development, testing
- `0.x.0` - Beta releases, significant features

**Semantic Versioning:**
- `MAJOR.MINOR.PATCH`
- Breaking changes expected before 1.0.0

**Pre-release tags:**
- `v0.0.2-alpha` - Alpha release
- `v0.0.2-beta` - Beta release
- `v0.0.2-rc1` - Release candidate

---

## 🧪 Testing Releases

### Test Quick Install
```bash
curl -sSL https://raw.githubusercontent.com/reliable-agents-ai/triads/main/quick-install.sh | bash
```

### Test Release Download
```bash
VERSION="0.0.1"
curl -LO https://github.com/reliable-agents-ai/triads/releases/download/v${VERSION}/triad-generator-v${VERSION}.tar.gz
tar -xzf triad-generator-v${VERSION}.tar.gz
cd triad-generator-v${VERSION}
./install-triads.sh --dry-run
```

### Verify Checksum
```bash
curl -LO https://github.com/reliable-agents-ai/triads/releases/download/v${VERSION}/triad-generator-v${VERSION}.tar.gz.sha256
sha256sum -c triad-generator-v${VERSION}.tar.gz.sha256
```

---

## 🐛 Hotfix Process

For urgent fixes:

```bash
# 1. Checkout tag
git checkout -b hotfix/0.0.1-fix v0.0.1

# 2. Make fixes
# ... edit files ...

# 3. Update version (patch increment)
echo "0.0.2" > VERSION

# 4. Commit and tag
git add .
git commit -m "Hotfix: [description]"
git tag v0.0.2
git push origin hotfix/0.0.1-fix
git push origin v0.0.2

# 5. Merge to main
git checkout main
git merge hotfix/0.0.1-fix
git push origin main
```

---

## 🔧 Common Tasks

### Viewing Release Stats
```bash
curl https://api.github.com/repos/reliable-agents-ai/triads/releases/latest
```

### Deleting a Failed Release
```bash
# Delete tag locally and remotely
git tag -d v0.0.2
git push origin :refs/tags/v0.0.2

# Delete release via GitHub UI or:
gh release delete v0.0.2  # Requires GitHub CLI
```

### Re-running Failed GitHub Action
1. Go to: https://github.com/reliable-agents-ai/triads/actions
2. Click on the failed workflow
3. Click "Re-run jobs" → "Re-run all jobs"

---

## 📊 Monitoring

### GitHub Actions Status
https://github.com/reliable-agents-ai/triads/actions

### Releases
https://github.com/reliable-agents-ai/triads/releases

### Issues
https://github.com/reliable-agents-ai/triads/issues

### Pull Requests
https://github.com/reliable-agents-ai/triads/pulls

---

## 📚 Documentation

### Main Docs
- [RELEASE_GUIDE.md](../RELEASE_GUIDE.md) - Complete release process
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contributor guidelines
- [README.md](../README.md) - Main documentation

### User Docs
- [docs/INSTALLATION.md](../docs/INSTALLATION.md)
- [docs/USAGE.md](../docs/USAGE.md)
- [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md)
- [docs/TROUBLESHOOTING.md](../docs/TROUBLESHOOTING.md)

---

## 🆘 Troubleshooting

### GitHub Action Not Running
1. Check Actions enabled: Settings → Actions → General
2. Verify workflow file syntax:
   ```bash
   python3 -c "import yaml; yaml.safe_load(open('.github/workflows/release.yml'))"
   ```

### Release Build Failed
1. Check logs: https://github.com/reliable-agents-ai/triads/actions
2. Common issues:
   - Missing files
   - Permission issues
   - Invalid tag format (must be `vX.Y.Z`)

### Users Can't Install
1. Check release assets uploaded
2. Verify quick-install.sh syntax:
   ```bash
   shellcheck quick-install.sh
   ```
3. Test installation in clean environment

---

## 📞 Support

For questions or issues:
- **Internal**: Check this file and RELEASE_GUIDE.md
- **Community**: GitHub Discussions
- **Urgent**: Direct message other maintainers

---

**Remember:** All releases trigger automatically from version tags. Always test locally before pushing tags!
