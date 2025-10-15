#!/bin/bash

# Triads Plugin Installation Script
# Installs the triads plugin locally for development/testing

set -e

echo "========================================"
echo " Triads Plugin Installation"
echo "========================================"
echo ""

# Check if claude command exists
if ! command -v claude &> /dev/null; then
    echo "❌ Error: claude command not found"
    echo "   Please install Claude Code first"
    exit 1
fi

echo "📦 Installing triads plugin from current directory..."
echo ""

# Install plugin from current directory
claude plugin install .

echo ""
echo "========================================"
echo " ✅ Plugin Installed Successfully!"
echo "========================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Navigate to a project:"
echo "   cd ~/your-project"
echo ""
echo "2. Start Claude Code:"
echo "   claude code"
echo ""
echo "3. Generate custom workflow:"
echo "   > /generate-triads"
echo ""
echo "4. Restart session to load agents:"
echo "   exit"
echo "   claude code"
echo ""
echo "5. Use your workflow:"
echo "   > Start [TriadName]: [task]"
echo ""
echo "========================================"
echo ""
echo "📚 Documentation:"
echo "   - User Guide: docs/USER_GUIDE.md"
echo "   - Architecture: docs/ARCHITECTURE_DECISIONS.md"
echo ""
echo "🐛 Issues: https://github.com/reliable-agents-ai/triads/issues"
echo ""
