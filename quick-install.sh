#!/bin/bash
# Triad Generator - Quick Installer
# Downloads and installs the latest release from GitHub

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${BLUE}ℹ${NC}  $1"
}

print_success() {
    echo -e "${GREEN}✓${NC}  $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC}  $1"
}

print_error() {
    echo -e "${RED}✗${NC}  $1"
}

# Configuration
REPO="reliable-agents-ai/triads"
VERSION="${TRIAD_VERSION:-latest}"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   Triad Generator Quick Install"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check prerequisites
print_info "Checking prerequisites..."

# Check for curl or wget
if command -v curl &> /dev/null; then
    DOWNLOAD_CMD="curl -fsSL"
    DOWNLOAD_OUTPUT_FLAG="-o"
elif command -v wget &> /dev/null; then
    DOWNLOAD_CMD="wget -qO"
    DOWNLOAD_OUTPUT_FLAG=""
else
    print_error "Neither curl nor wget found. Please install one of them."
    exit 1
fi

# Check for tar
if ! command -v tar &> /dev/null; then
    print_error "tar not found. Please install tar."
    exit 1
fi

# Check Python version
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 not found. Please install Python 3.10+"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
print_success "Python $PYTHON_VERSION found"

if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" 2>/dev/null; then
    print_error "Python 3.10+ required, found Python $PYTHON_VERSION"
    exit 1
fi

echo ""

# Determine download URL
if [ "$VERSION" = "latest" ]; then
    print_info "Fetching latest release information..."

    # Get latest release info from GitHub API
    RELEASE_INFO=$($DOWNLOAD_CMD https://api.github.com/repos/$REPO/releases/latest)

    # Extract version and download URL
    VERSION=$(echo "$RELEASE_INFO" | grep -o '"tag_name": *"[^"]*"' | sed 's/"tag_name": *"\(.*\)"/\1/' | sed 's/^v//')
    DOWNLOAD_URL=$(echo "$RELEASE_INFO" | grep -o '"browser_download_url": *"[^"]*tar\.gz"' | head -1 | sed 's/"browser_download_url": *"\(.*\)"/\1/')

    if [ -z "$DOWNLOAD_URL" ]; then
        print_error "Could not find latest release download URL"
        print_info "Trying direct download..."
        DOWNLOAD_URL="https://github.com/$REPO/releases/latest/download/triad-generator-latest.tar.gz"
    fi
else
    # Specific version requested
    DOWNLOAD_URL="https://github.com/$REPO/releases/download/v$VERSION/triad-generator-v$VERSION.tar.gz"
fi

print_info "Version: $VERSION"
print_info "Download URL: $DOWNLOAD_URL"
echo ""

# Create temporary directory
TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT

cd "$TEMP_DIR"

# Download release
print_info "Downloading Triad Generator v$VERSION..."

if [ -n "$DOWNLOAD_OUTPUT_FLAG" ]; then
    $DOWNLOAD_CMD $DOWNLOAD_OUTPUT_FLAG "triad-generator.tar.gz" "$DOWNLOAD_URL" || {
        print_error "Download failed"
        exit 1
    }
else
    $DOWNLOAD_CMD "triad-generator.tar.gz" "$DOWNLOAD_URL" || {
        print_error "Download failed"
        exit 1
    }
fi

print_success "Downloaded successfully"

# Download checksum if available
CHECKSUM_URL="${DOWNLOAD_URL}.sha256"
if $DOWNLOAD_CMD $DOWNLOAD_OUTPUT_FLAG "triad-generator.tar.gz.sha256" "$CHECKSUM_URL" 2>/dev/null; then
    print_info "Verifying checksum..."

    if command -v sha256sum &> /dev/null; then
        if sha256sum -c "triad-generator.tar.gz.sha256" 2>/dev/null; then
            print_success "Checksum verified"
        else
            print_warning "Checksum verification failed"
            read -r -p "Continue anyway? (yes/no): " CONTINUE
            if [ "$CONTINUE" != "yes" ]; then
                print_error "Installation cancelled"
                exit 1
            fi
        fi
    else
        print_warning "sha256sum not found, skipping checksum verification"
    fi
fi

echo ""

# Extract archive
print_info "Extracting..."
tar -xzf "triad-generator.tar.gz" || {
    print_error "Extraction failed"
    exit 1
}

# Find extracted directory
EXTRACTED_DIR=$(find . -maxdepth 1 -type d -name "triad-generator-*" | head -1)

if [ -z "$EXTRACTED_DIR" ]; then
    print_error "Could not find extracted directory"
    exit 1
fi

cd "$EXTRACTED_DIR"

print_success "Extracted successfully"
echo ""

# Run installer
print_info "Running installer..."
echo ""

chmod +x install-triads.sh

# Pass through any arguments
./install-triads.sh "$@"

INSTALL_EXIT_CODE=$?

if [ $INSTALL_EXIT_CODE -eq 0 ]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    print_success "QUICK INSTALL COMPLETE!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    print_info "Next steps:"
    echo ""
    echo "  1. Launch Claude Code:"
    echo "     claude code"
    echo ""
    echo "  2. Generate your custom triad system:"
    echo "     > /generate-triads"
    echo ""
    echo "  3. Answer questions about your workflow"
    echo ""
    echo "  4. Start using your triads!"
    echo ""
    print_info "Documentation: https://github.com/$REPO"
    echo ""
else
    echo ""
    print_error "Installation failed with exit code $INSTALL_EXIT_CODE"
    echo ""
    print_info "For help:"
    echo "  • Check logs above"
    echo "  • Visit: https://github.com/$REPO/issues"
    echo "  • See: https://github.com/$REPO/blob/main/docs/TROUBLESHOOTING.md"
    echo ""
    exit $INSTALL_EXIT_CODE
fi
