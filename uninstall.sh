#!/bin/bash
set -e

# Triad Generator - Safe Uninstaller
# Removes generator components while preserving user's custom work

BACKUP_DIR=".claude.uninstall-backup.$(date +%Y%m%d_%H%M%S)"
CLAUDE_DIR=".claude"

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
Triad Generator Uninstaller

Usage: $0 [OPTIONS]

Options:
  --complete    Remove everything including generated agents
  --dry-run     Show what would be removed without actually removing
  --no-backup   Skip creating backup (not recommended)
  --help        Show this help message

Default behavior (no flags):
  - Removes generator meta-agents
  - Removes generator templates
  - Removes slash command
  - PRESERVES your custom agents
  - PRESERVES knowledge graphs
  - PRESERVES settings
  - Creates backup before removal

Examples:
  $0                  # Safe uninstall (preserves custom work)
  $0 --dry-run        # See what would be removed
  $0 --complete       # Remove everything (clean slate)

EOF
}

# Parse arguments
COMPLETE_REMOVAL=false
DRY_RUN=false
CREATE_BACKUP=true

while [[ $# -gt 0 ]]; do
    case $1 in
        --complete)
            COMPLETE_REMOVAL=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --no-backup)
            CREATE_BACKUP=false
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
echo "   Triad Generator Uninstaller"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if .claude directory exists
if [ ! -d "$CLAUDE_DIR" ]; then
    print_error ".claude/ directory not found"
    print_info "Nothing to uninstall"
    exit 0
fi

# Show what will be done
echo "Uninstall mode: $( [ "$COMPLETE_REMOVAL" = true ] && echo "COMPLETE" || echo "SAFE" )"
echo "Dry run: $( [ "$DRY_RUN" = true ] && echo "YES" || echo "NO" )"
echo "Create backup: $( [ "$CREATE_BACKUP" = true ] && echo "YES" || echo "NO" )"
echo ""

if [ "$COMPLETE_REMOVAL" = true ]; then
    print_warning "COMPLETE REMOVAL will delete:"
    echo "  • All generator components"
    echo "  • All generated agents"
    echo "  • All knowledge graphs"
    echo "  • All settings and configuration"
    echo "  • Everything in .claude/"
    echo ""
    print_warning "This cannot be undone (except from backup)"
else
    print_info "SAFE REMOVAL will delete:"
    echo "  • Generator meta-agents (.claude/generator/)"
    echo "  • Slash command (.claude/commands/generate-triads.md)"
    echo "  • Generator knowledge graph (.claude/graphs/generator_graph.json)"
    echo ""
    print_success "SAFE REMOVAL will PRESERVE:"
    echo "  • Your custom agents (.claude/agents/)"
    echo "  • Knowledge graphs (.claude/graphs/*_graph.json)"
    echo "  • Constitutional principles (.claude/constitutional/)"
    echo "  • Settings (.claude/settings.json)"
    echo "  • Custom documentation"
fi

echo ""

# Confirm unless dry-run
if [ "$DRY_RUN" = false ]; then
    read -r -p "Continue with uninstallation? (yes/no): " CONFIRM
    if [ "$CONFIRM" != "yes" ]; then
        print_info "Uninstallation cancelled"
        exit 0
    fi
fi

echo ""

# Create backup
if [ "$CREATE_BACKUP" = true ] && [ "$DRY_RUN" = false ]; then
    print_info "Creating backup..."
    cp -r "$CLAUDE_DIR" "$BACKUP_DIR"
    print_success "Backup created: $BACKUP_DIR"
    echo ""
fi

# Function to remove file/directory
remove_item() {
    local item=$1
    local description=$2

    if [ -e "$item" ]; then
        if [ "$DRY_RUN" = true ]; then
            print_info "[DRY RUN] Would remove: $description"
        else
            rm -rf "$item"
            print_success "Removed: $description"
        fi
    else
        if [ "$DRY_RUN" = true ]; then
            print_info "[DRY RUN] Not found (would skip): $description"
        fi
    fi
}

# Perform removal
print_info "Removing Triad Generator components..."
echo ""

if [ "$COMPLETE_REMOVAL" = true ]; then
    # Complete removal
    remove_item "$CLAUDE_DIR" "Entire .claude/ directory"
else
    # Safe removal - only generator components
    remove_item "$CLAUDE_DIR/generator" "Generator meta-agents"
    remove_item "$CLAUDE_DIR/commands/generate-triads.md" "Generate-triads slash command"
    remove_item "$CLAUDE_DIR/graphs/generator_graph.json" "Generator knowledge graph"

    # Check if commands directory is now empty
    if [ -d "$CLAUDE_DIR/commands" ]; then
        if [ -z "$(ls -A $CLAUDE_DIR/commands)" ]; then
            remove_item "$CLAUDE_DIR/commands" "Empty commands directory"
        fi
    fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "$DRY_RUN" = true ]; then
    echo ""
    print_success "DRY RUN COMPLETE"
    echo ""
    print_info "No changes were made"
    print_info "Run without --dry-run to actually uninstall"
elif [ "$COMPLETE_REMOVAL" = true ]; then
    echo ""
    print_success "COMPLETE REMOVAL FINISHED"
    echo ""
    print_info "All Triad Generator components removed"

    if [ "$CREATE_BACKUP" = true ]; then
        print_info "Backup available at: $BACKUP_DIR"
        echo ""
        echo "To restore:"
        echo "  mv $BACKUP_DIR .claude"
    fi
else
    echo ""
    print_success "SAFE UNINSTALLATION COMPLETE"
    echo ""
    print_info "Generator components removed"
    print_success "Your custom work preserved:"
    echo ""

    # Show what's preserved
    if [ -d "$CLAUDE_DIR/agents" ]; then
        echo "  ✓ Custom agents: $CLAUDE_DIR/agents/"
    fi

    if [ -d "$CLAUDE_DIR/graphs" ]; then
        GRAPH_COUNT=$(find "$CLAUDE_DIR/graphs" -name '*.json' 2>/dev/null | wc -l)
        echo "  ✓ Knowledge graphs: $GRAPH_COUNT files"
    fi

    if [ -f "$CLAUDE_DIR/settings.json" ]; then
        echo "  ✓ Settings: $CLAUDE_DIR/settings.json"
    fi

    if [ -d "$CLAUDE_DIR/constitutional" ]; then
        echo "  ✓ Constitutional principles: $CLAUDE_DIR/constitutional/"
    fi

    echo ""
    if [ "$CREATE_BACKUP" = true ]; then
        print_info "Backup available at: $BACKUP_DIR"
        echo ""
        echo "To restore generator:"
        echo "  cp -r $BACKUP_DIR/generator .claude/"
        echo "  cp -r $BACKUP_DIR/commands/generate-triads.md .claude/commands/"
    fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ "$DRY_RUN" = false ] && [ "$COMPLETE_REMOVAL" = false ]; then
    print_info "Your generated triads still work!"
    print_info "You can still use: Start {Triad}: [task]"
    echo ""
    print_info "To reinstall the generator:"
    echo "  ./setup-complete.sh"
    echo "  claude code"
    echo "  > /generate-triads"
fi

exit 0
