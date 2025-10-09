#!/bin/bash
# Triad Generator - Enhanced Installer
# Creates the Generator Triad system with safety features

set -e

BACKUP_DIR=".claude.backup.$(date +%Y%m%d_%H%M%S)"
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
Triad Generator Installer

Usage: $0 [OPTIONS]

Options:
  --dry-run        Show what would be installed without making changes
  --force          Skip safety checks and overwrite existing files
  --no-backup      Skip creating backup of existing .claude/ folder
  --components=X   Install only specific components (comma-separated)
                   Options: generator,command,hooks,graphs,constitutional,all
  --help           Show this help message

Examples:
  $0                          # Interactive installation with safety checks
  $0 --dry-run                # Preview what would be installed
  $0 --force                  # Overwrite without prompts
  $0 --components=generator   # Install only generator meta-agents
  $0 --no-backup              # Skip backup (not recommended)

Safety Features:
  - Detects existing .claude/ setup
  - Creates backup before overwriting
  - Prompts for confirmation on conflicts
  - Validates dependencies before installation
  - Dry-run mode to preview changes

EOF
}

# Parse arguments
DRY_RUN=false
FORCE=false
CREATE_BACKUP=true
COMPONENTS="all"

while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        --no-backup)
            CREATE_BACKUP=false
            shift
            ;;
        --components=*)
            COMPONENTS="${1#*=}"
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
echo "   Triad Generator Installer"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Pre-flight checks
print_info "Running pre-flight checks..."
echo ""

# Check Python version
print_info "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 not found"
    print_info "Please install Python 3.10+ and try again"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')

if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" 2>/dev/null; then
    print_error "Python $PYTHON_VERSION found, but 3.10+ required"
    print_info "Please upgrade Python and try again"
    exit 1
fi

print_success "Python $PYTHON_VERSION found"

# Check for existing .claude directory
EXISTING_SETUP=false
CUSTOM_AGENTS=false
EXISTING_GRAPHS=false

if [ -d "$CLAUDE_DIR" ]; then
    EXISTING_SETUP=true
    print_warning "Existing .claude/ directory detected"

    # Check for custom agents (not generator)
    if [ -d "$CLAUDE_DIR/agents" ] && [ -n "$(find "$CLAUDE_DIR/agents" -mindepth 1 -maxdepth 1 2>/dev/null)" ]; then
        CUSTOM_AGENTS=true
        print_warning "Custom agents detected in .claude/agents/"
    fi

    # Check for existing graphs
    if [ -d "$CLAUDE_DIR/graphs" ] && [ -n "$(find "$CLAUDE_DIR/graphs" -name '*.json' 2>/dev/null)" ]; then
        EXISTING_GRAPHS=true
        print_warning "Existing knowledge graphs detected"
    fi

    # Check for generator already installed
    if [ -d "$CLAUDE_DIR/generator" ]; then
        print_info "Generator already installed (will be updated)"
    fi
fi

echo ""

# Handle existing setup
if [ "$EXISTING_SETUP" = true ] && [ "$FORCE" = false ]; then
    print_warning "Installation options:"
    echo ""
    echo "  1. Backup and proceed (recommended)"
    echo "  2. Skip installation"
    echo "  3. Proceed without backup (not recommended)"
    echo "  4. Show what would change (dry-run)"
    echo ""

    if [ "$DRY_RUN" = false ]; then
        read -r -p "Choose option (1-4): " CHOICE

        case $CHOICE in
            1)
                CREATE_BACKUP=true
                print_info "Will create backup before proceeding"
                ;;
            2)
                print_info "Installation cancelled"
                exit 0
                ;;
            3)
                CREATE_BACKUP=false
                print_warning "Proceeding without backup"
                ;;
            4)
                DRY_RUN=true
                print_info "Dry-run mode activated"
                ;;
            *)
                print_error "Invalid choice"
                exit 1
                ;;
        esac
        echo ""
    fi
fi

# Create backup if needed
if [ "$EXISTING_SETUP" = true ] && [ "$CREATE_BACKUP" = true ] && [ "$DRY_RUN" = false ]; then
    print_info "Creating backup..."
    cp -r "$CLAUDE_DIR" "$BACKUP_DIR"
    print_success "Backup created: $BACKUP_DIR"
    echo ""
fi

# Check NetworkX
print_info "Checking NetworkX..."
if ! python3 -c "import networkx" 2>/dev/null; then
    if [ "$DRY_RUN" = true ]; then
        print_info "[DRY RUN] Would install NetworkX"
    else
        print_info "Installing NetworkX..."
        pip3 install networkx --quiet || pip3 install --user networkx --quiet
        print_success "NetworkX installed"
    fi
else
    print_success "NetworkX already installed"
fi

echo ""

# Determine what to install
INSTALL_GENERATOR=false
INSTALL_COMMAND=false
INSTALL_HOOKS=false
INSTALL_GRAPHS=false
INSTALL_CONSTITUTIONAL=false

if [ "$COMPONENTS" = "all" ]; then
    INSTALL_GENERATOR=true
    INSTALL_COMMAND=true
    INSTALL_HOOKS=true
    INSTALL_GRAPHS=true
    INSTALL_CONSTITUTIONAL=true
else
    # Parse comma-separated component list
    IFS=',' read -ra COMPONENT_ARRAY <<< "$COMPONENTS"
    for component in "${COMPONENT_ARRAY[@]}"; do
        case $component in
            generator)
                INSTALL_GENERATOR=true
                ;;
            command)
                INSTALL_COMMAND=true
                ;;
            hooks)
                INSTALL_HOOKS=true
                ;;
            graphs)
                INSTALL_GRAPHS=true
                ;;
            constitutional)
                INSTALL_CONSTITUTIONAL=true
                ;;
            *)
                print_warning "Unknown component: $component"
                ;;
        esac
    done
fi

# Show installation plan
echo "Installation plan:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Mode: $( [ "$DRY_RUN" = true ] && echo "DRY RUN" || echo "INSTALL" )"
echo "Backup: $( [ "$CREATE_BACKUP" = true ] && echo "YES ($BACKUP_DIR)" || echo "NO" )"
echo ""
echo "Components to install:"
[ "$INSTALL_GENERATOR" = true ] && echo "  ✓ Generator meta-agents"
[ "$INSTALL_COMMAND" = true ] && echo "  ✓ Slash command (/generate-triads)"
[ "$INSTALL_HOOKS" = true ] && echo "  ✓ Lifecycle hooks"
[ "$INSTALL_GRAPHS" = true ] && echo "  ✓ Graph infrastructure"
[ "$INSTALL_CONSTITUTIONAL" = true ] && echo "  ✓ Constitutional framework"
echo ""

if [ "$CUSTOM_AGENTS" = true ]; then
    print_success "Your custom agents will be preserved"
fi

if [ "$EXISTING_GRAPHS" = true ]; then
    print_success "Your knowledge graphs will be preserved"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Confirm unless dry-run or force
if [ "$DRY_RUN" = false ] && [ "$FORCE" = false ]; then
    read -r -p "Proceed with installation? (yes/no): " CONFIRM
    if [ "$CONFIRM" != "yes" ]; then
        print_info "Installation cancelled"
        exit 0
    fi
    echo ""
fi

# Function to create directory
create_dir() {
    local dir=$1
    local description=$2

    if [ "$DRY_RUN" = true ]; then
        if [ ! -d "$dir" ]; then
            print_info "[DRY RUN] Would create: $description"
        else
            print_info "[DRY RUN] Already exists: $description"
        fi
    else
        mkdir -p "$dir"
        print_success "Created: $description"
    fi
}

# Create directory structure
print_info "Creating directory structure..."
echo ""

create_dir "$CLAUDE_DIR" ".claude/ root directory"

if [ "$INSTALL_GENERATOR" = true ]; then
    create_dir "$CLAUDE_DIR/generator" "Generator folder"
    create_dir "$CLAUDE_DIR/generator/agents" "Generator agents folder"
    create_dir "$CLAUDE_DIR/generator/lib" "Generator templates library"
fi

if [ "$INSTALL_COMMAND" = true ]; then
    create_dir "$CLAUDE_DIR/commands" "Commands folder"
fi

if [ "$INSTALL_HOOKS" = true ]; then
    create_dir "$CLAUDE_DIR/hooks" "Hooks folder"
fi

if [ "$INSTALL_GRAPHS" = true ]; then
    create_dir "$CLAUDE_DIR/graphs" "Graphs folder"
fi

if [ "$INSTALL_CONSTITUTIONAL" = true ]; then
    create_dir "$CLAUDE_DIR/constitutional" "Constitutional folder"
fi

echo ""

# Check if setup-complete.sh exists
if [ ! -f "setup-complete.sh" ]; then
    print_error "setup-complete.sh not found in current directory"
    print_info "This script must be run from the triad-generator root directory"
    exit 1
fi

# Run setup-complete.sh
if [ "$DRY_RUN" = true ]; then
    print_info "[DRY RUN] Would run setup-complete.sh to create files"
    print_info "[DRY RUN] Files that would be created:"
    echo ""
    [ "$INSTALL_GENERATOR" = true ] && echo "  • domain-researcher.md"
    [ "$INSTALL_GENERATOR" = true ] && echo "  • workflow-analyst.md"
    [ "$INSTALL_GENERATOR" = true ] && echo "  • triad-architect.md"
    [ "$INSTALL_GENERATOR" = true ] && echo "  • templates.py"
    [ "$INSTALL_COMMAND" = true ] && echo "  • generate-triads.md"
    [ "$INSTALL_CONSTITUTIONAL" = true ] && echo "  • checkpoints.json"
    [ "$INSTALL_CONSTITUTIONAL" = true ] && echo "  • violations.json"
    [ "$INSTALL_GRAPHS" = true ] && echo "  • generator_graph.json"
    echo "  • settings.json"
    echo "  • README.md"
else
    print_info "Running setup-complete.sh..."
    echo ""
    ./setup-complete.sh
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "$DRY_RUN" = true ]; then
    echo ""
    print_success "DRY RUN COMPLETE"
    echo ""
    print_info "No changes were made"
    print_info "Run without --dry-run to actually install"
    echo ""
    print_info "To install:"
    echo "  $0"
else
    echo ""
    print_success "INSTALLATION COMPLETE!"
    echo ""

    if [ "$CREATE_BACKUP" = true ] && [ "$EXISTING_SETUP" = true ]; then
        print_info "Backup saved: $BACKUP_DIR"
        echo ""
        echo "To restore backup:"
        echo "  rm -rf .claude && mv $BACKUP_DIR .claude"
        echo ""
    fi

    print_success "Next steps:"
    echo ""
    echo "  1. Launch Claude Code:"
    echo "     claude code"
    echo ""
    echo "  2. Generate your custom triad system:"
    echo "     > /generate-triads"
    echo ""
    echo "  3. Answer questions about your workflow"
    echo ""
    echo "  4. Get a custom multi-agent system designed for you!"
    echo ""

    print_info "Documentation:"
    echo "  • System overview: .claude/README.md"
    echo "  • Quick reference: QUICK_REFERENCE.md"
    echo "  • Full docs: docs/"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

exit 0
