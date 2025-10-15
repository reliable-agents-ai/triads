# Triads Marketplace Setup

## ✅ v0.3.0 Pushed to GitHub

The plugin is now live at:
- **Repository**: https://github.com/reliable-agents-ai/triads
- **Tag**: v0.3.0
- **Commit**: https://github.com/reliable-agents-ai/triads/commit/59c99ec

---

## 📦 Create GitHub Marketplace

### Step 1: Create Marketplace Repository

```bash
# On GitHub, create new repository:
# Name: triads-marketplace
# Owner: reliable-agents-ai
# Description: Marketplace for triads Claude Code plugin
# Public: Yes
```

### Step 2: Initialize Marketplace

```bash
# Clone the new repository
cd ~/Documents/repos
git clone https://github.com/reliable-agents-ai/triads-marketplace.git
cd triads-marketplace

# Create plugin manifest
mkdir -p .claude-plugin
```

### Step 3: Create Marketplace Manifest

Create `.claude-plugin/marketplace.json`:

```json
{
  "name": "triads-marketplace",
  "version": "1.0.0",
  "description": "Official marketplace for the triads Claude Code plugin - workflow system for organizing complex work",
  "owner": {
    "name": "Reliable Agents AI",
    "url": "https://github.com/reliable-agents-ai"
  },
  "plugins": [
    {
      "name": "triads",
      "source": "github:reliable-agents-ai/triads",
      "description": "Triad workflow system - organize complex work into phases with specialized agents and automatic knowledge management",
      "version": "0.3.0"
    }
  ]
}
```

### Step 4: Create README

Create `README.md`:

```markdown
# Triads Marketplace

Official marketplace for the [triads](https://github.com/reliable-agents-ai/triads) Claude Code plugin.

## What is Triads?

Triads helps you organize complex work into phases (called "triads"). Each triad has specialized agents that work together and automatically hand off context to the next phase.

## Installation

\`\`\`bash
# Add marketplace
/plugin marketplace add github:reliable-agents-ai/triads-marketplace

# Install triads plugin
/plugin install triads
\`\`\`

## Usage

\`\`\`bash
# In any project
cd ~/your-project
claude code

# Generate custom workflow
> /generate-triads

# Restart session
exit
claude code

# Use your workflow
> Start [TriadName]: [task]
\`\`\`

## Documentation

- [User Guide](https://github.com/reliable-agents-ai/triads/blob/main/docs/USER_GUIDE.md)
- [Architecture Decisions](https://github.com/reliable-agents-ai/triads/blob/main/docs/ARCHITECTURE_DECISIONS.md)
- [Release Notes](https://github.com/reliable-agents-ai/triads/blob/main/RELEASE_NOTES_v0.3.0.md)

## Support

- [Issues](https://github.com/reliable-agents-ai/triads/issues)
- [Discussions](https://github.com/reliable-agents-ai/triads/discussions)
```

### Step 5: Commit and Push

```bash
git add .
git commit -m "Initial marketplace setup for triads v0.3.0"
git push origin main
```

---

## 🧪 Test Installation

Once the marketplace is pushed:

```bash
# Add marketplace
/plugin marketplace add github:reliable-agents-ai/triads-marketplace

# List available plugins
/plugin list

# Install triads
/plugin install triads

# Verify installation
/plugin list installed
```

---

## 🔄 Updating Plugin Versions

When you release a new version of triads:

1. **Update triads repo** with new version
2. **Tag the release** (e.g., `v0.4.0`)
3. **Update marketplace** `.claude-plugin/marketplace.json`:
   ```json
   {
     "plugins": [
       {
         "name": "triads",
         "version": "0.4.0"  // <-- Update this
       }
     ]
   }
   ```
4. **Commit and push** marketplace changes

Users can then update:
```bash
/plugin update triads
```

---

## 📚 Files Created

```
triads-marketplace/
├── .claude-plugin/
│   └── marketplace.json     # Plugin registry
└── README.md                # Installation instructions
```

---

## ✅ Next Steps

1. Create `triads-marketplace` repository on GitHub
2. Clone and add the files above
3. Push to GitHub
4. Test installation with `/plugin marketplace add`

Once done, anyone can install triads with:
```bash
/plugin marketplace add github:reliable-agents-ai/triads-marketplace
/plugin install triads
```

---

**Achievement**: 🎯 Plugin published to GitHub, ready for distribution!
