#!/bin/bash
# Create release bundle for Triad Generator

set -e

VERSION="${1:-latest}"
RELEASE_NAME="triad-generator-${VERSION}"
RELEASE_DIR="releases"

echo "Creating release bundle: ${RELEASE_NAME}"
echo ""

# Create release directory
mkdir -p "${RELEASE_DIR}"

# Create temporary directory for bundle
TEMP_DIR=$(mktemp -d)
BUNDLE_DIR="${TEMP_DIR}/${RELEASE_NAME}"
mkdir -p "${BUNDLE_DIR}"

# Copy essential files
echo "Copying files..."
cp -r .claude "${BUNDLE_DIR}/"
cp install-triads.sh "${BUNDLE_DIR}/"
cp setup-complete.sh "${BUNDLE_DIR}/"
cp uninstall.sh "${BUNDLE_DIR}/"
cp upgrade.sh "${BUNDLE_DIR}/"
cp README.md "${BUNDLE_DIR}/"
cp CLAUDE.md "${BUNDLE_DIR}/"
cp LICENSE "${BUNDLE_DIR}/"
cp CONTRIBUTING.md "${BUNDLE_DIR}/"
cp -r docs "${BUNDLE_DIR}/"

# Copy KM system components to .claude/km/ for self-contained distribution
echo "Bundling KM system into .claude/km/..."
mkdir -p "${BUNDLE_DIR}/.claude/km"
cp src/triads/km/*.py "${BUNDLE_DIR}/.claude/km/"

# Copy tests (for verification)
echo "Copying tests..."
cp -r tests "${BUNDLE_DIR}/"

# Copy project configuration
echo "Copying configuration..."
cp pyproject.toml "${BUNDLE_DIR}/"

# Make scripts executable
chmod +x "${BUNDLE_DIR}"/*.sh

# Remove any runtime files
rm -rf "${BUNDLE_DIR}/.claude/graphs"/*.json 2>/dev/null || true
mkdir -p "${BUNDLE_DIR}/.claude/graphs"
touch "${BUNDLE_DIR}/.claude/graphs/.gitkeep"

# Create tarball
echo "Creating tarball..."
cd "${TEMP_DIR}"
tar -czf "${RELEASE_NAME}.tar.gz" "${RELEASE_NAME}"
cd - > /dev/null

# Move to releases directory
mv "${TEMP_DIR}/${RELEASE_NAME}.tar.gz" "${RELEASE_DIR}/"

# Create checksum
cd "${RELEASE_DIR}"
shasum -a 256 "${RELEASE_NAME}.tar.gz" > "${RELEASE_NAME}.tar.gz.sha256"
cd - > /dev/null

# Cleanup
rm -rf "${TEMP_DIR}"

echo ""
echo "✅ Release bundle created:"
echo "   ${RELEASE_DIR}/${RELEASE_NAME}.tar.gz"
echo ""
echo "📋 Checksum:"
cat "${RELEASE_DIR}/${RELEASE_NAME}.tar.gz.sha256"
echo ""
echo "📤 Upload to GitHub Releases:"
echo "   1. Go to: https://github.com/YOUR_USERNAME/triad-generator/releases/new"
echo "   2. Create tag: v${VERSION}"
echo "   3. Upload: ${RELEASE_DIR}/${RELEASE_NAME}.tar.gz"
echo "   4. Upload: ${RELEASE_DIR}/${RELEASE_NAME}.tar.gz.sha256"
echo ""
echo "Users can then install with:"
echo "   curl -LO https://github.com/YOUR_USERNAME/triad-generator/releases/download/v${VERSION}/${RELEASE_NAME}.tar.gz"
echo "   tar -xzf ${RELEASE_NAME}.tar.gz"
echo "   cd ${RELEASE_NAME}"
echo "   ./install-triads.sh"
