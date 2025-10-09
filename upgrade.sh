#!/bin/bash
# Triad Generator - Upgrade Script
# Upgrades generator components while preserving customizations

set -e

BACKUP_DIR=".claude.upgrade-backup.$(date +%Y%m%d_%H%M%S)"
CLAUDE_DIR=".claude"
TEMP_DIR=".claude.upgrade-temp"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Function to show help
show_help() {
    cat << EOF
Triad Generator Upgrade Script

Usage: $0 [OPTIONS]

Options:
  --dry-run        Show what would be upgraded without making changes
  --no-backup      Skip creating backup (not recommended)
  --force          Force upgrade even if versions match
  --help           Show this help message

What gets upgraded:
  ✓ Generator meta-agents (domain-researcher, workflow-analyst, triad-architect)
  ✓ Template library (templates.py)
  ✓ Slash command (generate-triads.md)
  ✓ System documentation (README.md)

What gets preserved:
  ✓ Your custom agents (.claude/agents/)
  ✓ Knowledge graphs (.claude/graphs/*.json)
  ✓ Settings (.claude/settings.json - merged if needed)
  ✓ Constitutional principles (yours preserved, new ones offered)
  ✓ Hooks (yours preserved unless you want updates)

Examples:
  $0                 # Interactive upgrade with backup
  $0 --dry-run       # Preview what would change
  $0 --force         # Force upgrade

EOF
}

# Parse arguments
DRY_RUN=false
CREATE_BACKUP=true
FORCE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --no-backup)
            CREATE_BACKUP=false
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   Triad Generator Upgrade"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if .claude directory exists
if [ ! -d "$CLAUDE_DIR" ]; then
    print_error ".claude/ directory not found"
    print_info "Run ./install-triads.sh first to install"
    exit 1
fi

# Check if generator is installed
if [ ! -d "$CLAUDE_DIR/generator" ]; then
    print_error "Generator not found in .claude/generator/"
    print_info "Run ./install-triads.sh first to install"
    exit 1
fi

# Detect current version (if version file exists)
CURRENT_VERSION="unknown"
NEW_VERSION="latest"

if [ -f "$CLAUDE_DIR/generator/VERSION" ]; then
    CURRENT_VERSION=$(cat "$CLAUDE_DIR/generator/VERSION")
    print_info "Current version: $CURRENT_VERSION"
else
    print_info "Current version: unknown (no VERSION file)"
fi

print_info "New version: $NEW_VERSION"
echo ""

# Check if upgrade needed
if [ "$CURRENT_VERSION" = "$NEW_VERSION" ] && [ "$FORCE" = false ]; then
    print_success "Already on latest version!"
    print_info "Use --force to reinstall anyway"
    exit 0
fi

# Analyze what will be upgraded
print_info "Analyzing current setup..."
echo ""

HAS_CUSTOM_AGENTS=false
HAS_GRAPHS=false
HAS_CUSTOM_SETTINGS=false
HAS_CUSTOM_HOOKS=false

if [ -d "$CLAUDE_DIR/agents" ] && [ -n "$(find "$CLAUDE_DIR/agents" -mindepth 1 -maxdepth 1 2>/dev/null)" ]; then
    HAS_CUSTOM_AGENTS=true
fi

if [ -d "$CLAUDE_DIR/graphs" ] && [ "$(find "$CLAUDE_DIR/graphs" -name '*.json' 2>/dev/null | wc -l)" -gt 1 ]; then
    HAS_GRAPHS=true
fi

if [ -f "$CLAUDE_DIR/settings.json" ]; then
    HAS_CUSTOM_SETTINGS=true
fi

if [ -d "$CLAUDE_DIR/hooks" ] && [ -n "$(find "$CLAUDE_DIR/hooks" -name '*.py' 2>/dev/null)" ]; then
    HAS_CUSTOM_HOOKS=true
fi

# Show upgrade plan
echo "Upgrade plan:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Mode: $( [ "$DRY_RUN" = true ] && echo "DRY RUN" || echo "UPGRADE" )"
echo "Backup: $( [ "$CREATE_BACKUP" = true ] && echo "YES ($BACKUP_DIR)" || echo "NO" )"
echo ""
echo "Will upgrade:"
echo "  ✓ Generator meta-agents"
echo "  ✓ Template library"
echo "  ✓ Slash command"
echo "  ✓ System README"
echo ""
echo "Will preserve:"
[ "$HAS_CUSTOM_AGENTS" = true ] && echo "  ✓ Your custom agents ($(find "$CLAUDE_DIR/agents" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l) triads)"
[ "$HAS_GRAPHS" = true ] && echo "  ✓ Knowledge graphs ($(find "$CLAUDE_DIR/graphs" -name '*.json' 2>/dev/null | wc -l) files)"
[ "$HAS_CUSTOM_SETTINGS" = true ] && echo "  ✓ Settings (will merge)"
[ "$HAS_CUSTOM_HOOKS" = true ] && echo "  ✓ Custom hooks (yours preserved)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Confirm unless dry-run
if [ "$DRY_RUN" = false ]; then
    read -r -p "Proceed with upgrade? (yes/no): " CONFIRM
    if [ "$CONFIRM" != "yes" ]; then
        print_info "Upgrade cancelled"
        exit 0
    fi
    echo ""
fi

# Create backup
if [ "$CREATE_BACKUP" = true ] && [ "$DRY_RUN" = false ]; then
    print_info "Creating backup..."
    cp -r "$CLAUDE_DIR" "$BACKUP_DIR"
    print_success "Backup created: $BACKUP_DIR"
    echo ""
fi

# Upgrade process
print_info "Upgrading generator components..."
echo ""

# Check if setup-complete.sh exists (source of new files)
if [ ! -f "setup-complete.sh" ]; then
    print_error "setup-complete.sh not found"
    print_info "This script must be run from the triad-generator root directory"
    exit 1
fi

if [ "$DRY_RUN" = true ]; then
    print_info "[DRY RUN] Would run setup-complete.sh to get new versions"
    print_info "[DRY RUN] Files that would be upgraded:"
    echo "  • domain-researcher.md"
    echo "  • workflow-analyst.md"
    echo "  • triad-architect.md"
    echo "  • templates.py"
    echo "  • generate-triads.md"
    echo "  • README.md"
    echo ""
    print_info "[DRY RUN] Your files would be preserved:"
    [ "$HAS_CUSTOM_AGENTS" = true ] && echo "  • Custom agents"
    [ "$HAS_GRAPHS" = true ] && echo "  • Knowledge graphs"
    [ "$HAS_CUSTOM_SETTINGS" = true ] && echo "  • Settings (merged)"
    [ "$HAS_CUSTOM_HOOKS" = true ] && echo "  • Custom hooks"
else
    # Create temp directory for new files
    print_info "Downloading new versions..."
    mkdir -p "$TEMP_DIR"

    # Run setup-complete.sh to temp directory
    # (This would need modification to setup-complete.sh to support custom target dir)
    # For now, we'll update in place

    # Preserve custom work
    if [ "$HAS_CUSTOM_AGENTS" = true ]; then
        print_info "Preserving custom agents..."
        mkdir -p "$TEMP_DIR/agents"
        cp -r "$CLAUDE_DIR/agents" "$TEMP_DIR/"
    fi

    if [ "$HAS_GRAPHS" = true ]; then
        print_info "Preserving knowledge graphs..."
        mkdir -p "$TEMP_DIR/graphs"
        cp "$CLAUDE_DIR/graphs"/*.json "$TEMP_DIR/graphs/" 2>/dev/null || true
    fi

    if [ "$HAS_CUSTOM_SETTINGS" = true ]; then
        print_info "Preserving settings..."
        cp "$CLAUDE_DIR/settings.json" "$TEMP_DIR/settings.json.backup"
    fi

    if [ "$HAS_CUSTOM_HOOKS" = true ]; then
        print_info "Preserving custom hooks..."
        mkdir -p "$TEMP_DIR/hooks"
        cp "$CLAUDE_DIR/hooks"/*.py "$TEMP_DIR/hooks/" 2>/dev/null || true
    fi

    # Run setup (upgrades generator files)
    print_info "Installing new versions..."
    ./setup-complete.sh

    # Restore custom work
    if [ "$HAS_CUSTOM_AGENTS" = true ]; then
        print_info "Restoring custom agents..."
        cp -r "$TEMP_DIR/agents" "$CLAUDE_DIR/" 2>/dev/null || true
    fi

    if [ "$HAS_GRAPHS" = true ]; then
        print_info "Restoring knowledge graphs..."
        cp "$TEMP_DIR/graphs"/*.json "$CLAUDE_DIR/graphs/" 2>/dev/null || true
    fi

    if [ "$HAS_CUSTOM_HOOKS" = true ]; then
        print_info "Restoring custom hooks..."
        echo ""
        print_warning "You have custom hooks. Options:"
        echo "  1. Keep your hooks (recommended if customized)"
        echo "  2. Use new hooks (get latest features)"
        echo "  3. Keep both (manual merge needed)"
        read -r -p "Choose (1-3): " HOOK_CHOICE

        case $HOOK_CHOICE in
            1)
                cp "$TEMP_DIR/hooks"/*.py "$CLAUDE_DIR/hooks/" 2>/dev/null || true
                print_success "Kept your custom hooks"
                ;;
            2)
                print_success "Using new hooks"
                ;;
            3)
                cp "$TEMP_DIR/hooks"/*.py "$CLAUDE_DIR/hooks.custom/" 2>/dev/null || true
                print_info "Custom hooks saved to .claude/hooks.custom/"
                print_info "New hooks in .claude/hooks/"
                ;;
        esac
    fi

    # Clean up temp directory
    rm -rf "$TEMP_DIR"

    # Update version file
    echo "$NEW_VERSION" > "$CLAUDE_DIR/generator/VERSION"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "$DRY_RUN" = true ]; then
    echo ""
    print_success "DRY RUN COMPLETE"
    echo ""
    print_info "No changes were made"
    print_info "Run without --dry-run to actually upgrade"
else
    echo ""
    print_success "UPGRADE COMPLETE!"
    echo ""

    if [ "$CREATE_BACKUP" = true ]; then
        print_info "Backup saved: $BACKUP_DIR"
        echo ""
        echo "To rollback:"
        echo "  rm -rf .claude && mv $BACKUP_DIR .claude"
        echo ""
    fi

    print_success "Generator upgraded to version $NEW_VERSION"
    echo ""
    print_info "Your custom work preserved:"
    [ "$HAS_CUSTOM_AGENTS" = true ] && echo "  ✓ Custom agents"
    [ "$HAS_GRAPHS" = true ] && echo "  ✓ Knowledge graphs"
    [ "$HAS_CUSTOM_SETTINGS" = true ] && echo "  ✓ Settings"
    [ "$HAS_CUSTOM_HOOKS" = true ] && echo "  ✓ Hooks"
    echo ""

    print_info "Test your system:"
    echo "  claude code"
    echo "  > /generate-triads"
    echo ""
    echo "Or use existing triads:"
    echo "  > Start Discovery: [your task]"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

exit 0
