# User Memory - Claude Code Configuration

**Owner**: {{USER_NAME}}
**Created**: {{CREATION_DATE}}
**Last Updated**: {{LAST_UPDATED}}
**Location**: `~/.claude/USER_MEMORY.md`

This file stores user-level preferences, context, and patterns that persist across all projects. Claude Code reads this file to understand your working style, preferences, and common patterns.

---

## 🎯 PURPOSE

**What This File Does**:
- Stores your personal preferences for how Claude Code should work
- Captures your common patterns and workflows
- Documents your domain expertise and knowledge areas
- Defines your quality standards and expectations
- Tracks your project history and context

**What This File Does NOT Do**:
- Store project-specific information (that goes in project's CLAUDE.md)
- Store secrets or credentials (use environment variables)
- Override constitutional principles (those are absolute)

---

## 📋 SECTION 1: USER PROFILE

### Basic Information

```yaml
user:
  name: {{USER_NAME}}
  role: {{USER_ROLE}}  # e.g., "Senior Software Engineer", "Researcher", "Content Creator"
  organization: {{ORGANIZATION}}  # Optional
  location: {{TIMEZONE}}  # e.g., "America/Los_Angeles" (for scheduling context)
  primary_domains:
    - {{DOMAIN_1}}  # e.g., "software-development"
    - {{DOMAIN_2}}  # e.g., "content-creation"
  secondary_domains:
    - {{DOMAIN_3}}  # Areas of secondary expertise
```

### Working Hours and Availability

```yaml
working_hours:
  timezone: {{TIMEZONE}}
  typical_hours:
    monday: "9:00-17:00"
    tuesday: "9:00-17:00"
    wednesday: "9:00-17:00"
    thursday: "9:00-17:00"
    friday: "9:00-17:00"
    saturday: "off"
    sunday: "off"

  notes:
    - "Prefer async communication"
    - "No interruptions during focus blocks (10:00-12:00, 14:00-16:00)"
    - "Available for urgent issues via Slack"
```

**Usage**: Claude Code can use this to understand when you're likely to be available, but this is informational only.

---

## 📋 SECTION 2: COMMUNICATION PREFERENCES

### Response Style

```yaml
communication:
  verbosity: {{VERBOSITY_LEVEL}}  # "concise" | "moderate" | "detailed"
  # concise: Short responses, bullet points, minimal explanation
  # moderate: Balanced responses, some explanation, key details
  # detailed: Comprehensive responses, full explanations, all context

  technical_level: {{TECHNICAL_LEVEL}}  # "beginner" | "intermediate" | "expert"
  # beginner: Explain concepts, provide context, avoid jargon
  # intermediate: Assume basic knowledge, explain advanced concepts
  # expert: Assume deep knowledge, focus on nuances and edge cases

  preferred_format: {{FORMAT}}  # "markdown" | "code-first" | "visual"
  # markdown: Formatted text with headings, lists, code blocks
  # code-first: Lead with code examples, minimal text
  # visual: Diagrams, ASCII art, visual representations when possible
```

**Example - Concise + Expert**:
```markdown
❌ BAD (too verbose for concise+expert):
"Let me explain what a closure is. In JavaScript, a closure is a function that has access to variables in its outer scope, even after the outer function has returned. This is a powerful feature that allows for data encapsulation and functional programming patterns. Here's how it works..."

✅ GOOD (concise+expert):
"Closure pattern for data encapsulation:
```javascript
const counter = (() => {
  let count = 0;
  return { inc: () => ++count, get: () => count };
})();
```
Lexical scope preserves `count` - standard closure pattern."
```

**Example - Detailed + Beginner**:
```markdown
❌ BAD (too concise for detailed+beginner):
"Use closure for encapsulation."

✅ GOOD (detailed+beginner):
"I'll explain closures, which help keep data private.

**What is a closure?**
A closure is a function that 'remembers' variables from where it was created, even after that outer function has finished running.

**Why use closures?**
They let you create private data that can't be accessed from outside.

**Example**:
```javascript
function createCounter() {
  let count = 0;  // This is private

  return {
    increment: function() { count++; },
    getValue: function() { return count; }
  };
}

const counter = createCounter();
counter.increment();
console.log(counter.getValue());  // 1
console.log(counter.count);  // undefined (private!)
```

**What's happening**:
1. `createCounter` creates a variable `count`
2. It returns an object with two functions
3. Those functions can still access `count` even after `createCounter` finishes
4. But code outside can't access `count` directly - it's private!"
```

### Question Answering Preferences

```yaml
questions:
  ask_before_proceeding:
    - major_architectural_decisions  # Always ask before choosing architecture
    - destructive_operations  # Always ask before deleting files, dropping databases, etc.
    - external_service_calls  # Ask before calling APIs, sending emails, etc.
    - spending_resources  # Ask before operations that cost money

  proceed_without_asking:
    - minor_refactoring  # Proceed with safe refactoring (within same file)
    - formatting_changes  # Proceed with code formatting (black, prettier, etc.)
    - test_writing  # Proceed with writing tests
    - documentation_updates  # Proceed with updating docs

  uncertainty_threshold: {{THRESHOLD}}  # 90 (default) | 85 (more conservative) | 95 (less interruptions)
  # If confidence < threshold, escalate to user
```

**Example**:
```yaml
# Conservative user (prefers to be asked)
uncertainty_threshold: 95
ask_before_proceeding:
  - major_architectural_decisions
  - destructive_operations
  - external_service_calls
  - spending_resources
  - database_schema_changes
  - dependency_updates

# Autonomous user (prefers fewer interruptions)
uncertainty_threshold: 85
ask_before_proceeding:
  - destructive_operations
  - spending_resources
proceed_without_asking:
  - minor_refactoring
  - formatting_changes
  - test_writing
  - documentation_updates
  - minor_dependency_updates
```

---

## 📋 SECTION 3: TECHNICAL PREFERENCES

### Programming Languages and Frameworks

```yaml
programming:
  primary_languages:
    - language: {{LANGUAGE_1}}  # e.g., "Python"
      proficiency: {{PROFICIENCY}}  # "beginner" | "intermediate" | "expert"
      preferred_version: {{VERSION}}  # e.g., "3.11+"
      style_guide: {{STYLE}}  # e.g., "PEP 8", "Black", "Google Style Guide"

    - language: {{LANGUAGE_2}}  # e.g., "JavaScript"
      proficiency: {{PROFICIENCY}}
      preferred_version: {{VERSION}}  # e.g., "ES2022+"
      style_guide: {{STYLE}}  # e.g., "Airbnb", "Standard"

  frameworks:
    - name: {{FRAMEWORK_1}}  # e.g., "FastAPI"
      proficiency: {{PROFICIENCY}}
      version: {{VERSION}}

    - name: {{FRAMEWORK_2}}  # e.g., "React"
      proficiency: {{PROFICIENCY}}
      version: {{VERSION}}
```

### Tool Preferences

```yaml
tools:
  editor: {{EDITOR}}  # e.g., "VS Code", "Vim", "PyCharm"
  terminal: {{TERMINAL}}  # e.g., "zsh", "bash", "fish"
  package_manager:
    python: {{PYTHON_PKG}}  # e.g., "pip", "poetry", "conda"
    javascript: {{JS_PKG}}  # e.g., "npm", "yarn", "pnpm"

  version_control:
    preferred_workflow: {{GIT_WORKFLOW}}  # e.g., "GitHub Flow", "Git Flow", "Trunk-Based"
    commit_message_format: {{COMMIT_FORMAT}}  # e.g., "Conventional Commits", "Semantic"

  testing:
    python: {{PYTHON_TEST}}  # e.g., "pytest", "unittest"
    javascript: {{JS_TEST}}  # e.g., "Jest", "Vitest", "Mocha"

  formatting:
    python: {{PYTHON_FMT}}  # e.g., "black", "autopep8", "yapf"
    javascript: {{JS_FMT}}  # e.g., "prettier", "eslint"
```

### Code Quality Standards

```yaml
quality:
  test_coverage_minimum: {{COVERAGE}}  # e.g., 80 (%)

  code_review_checklist:
    - item: "All functions have docstrings"
      required: {{BOOLEAN}}
    - item: "Type hints on all function signatures"
      required: {{BOOLEAN}}
    - item: "No code duplication (DRY)"
      required: {{BOOLEAN}}
    - item: "Functions <20 lines"
      required: {{BOOLEAN}}
    - item: "No magic numbers (use named constants)"
      required: {{BOOLEAN}}

  documentation_requirements:
    - "README with installation instructions"
    - "API documentation (generated from docstrings)"
    - "CHANGELOG following Keep a Changelog"
    - "Examples in docs/ directory"
```

**Example - Python Expert**:
```yaml
programming:
  primary_languages:
    - language: "Python"
      proficiency: "expert"
      preferred_version: "3.11+"
      style_guide: "Black + Google Style Guide"

tools:
  package_manager:
    python: "poetry"
  testing:
    python: "pytest"
  formatting:
    python: "black + isort + mypy"

quality:
  test_coverage_minimum: 90
  code_review_checklist:
    - item: "Type hints on all function signatures"
      required: true
    - item: "Docstrings in Google format"
      required: true
    - item: "No code >10 cyclomatic complexity"
      required: true
```

---

## 📋 SECTION 4: DOMAIN EXPERTISE

### Software Development

```yaml
software_expertise:
  specializations:
    - {{SPECIALIZATION_1}}  # e.g., "Backend API development"
    - {{SPECIALIZATION_2}}  # e.g., "Database optimization"
    - {{SPECIALIZATION_3}}  # e.g., "DevOps and CI/CD"

  architectural_patterns:
    familiar_with:
      - {{PATTERN_1}}  # e.g., "Microservices"
      - {{PATTERN_2}}  # e.g., "Event-driven architecture"
    prefer:
      - {{PATTERN_3}}  # e.g., "Modular monolith"
    avoid:
      - {{PATTERN_4}}  # e.g., "Overly complex abstractions"

  security_focus_areas:
    - {{SECURITY_1}}  # e.g., "OWASP Top 10"
    - {{SECURITY_2}}  # e.g., "API security"
```

### Research

```yaml
research_expertise:
  methodologies:
    - {{METHOD_1}}  # e.g., "Quantitative analysis"
    - {{METHOD_2}}  # e.g., "Systematic reviews"

  statistical_tools:
    - {{TOOL_1}}  # e.g., "R", "SPSS", "Python (scipy/statsmodels)"

  citation_style: {{STYLE}}  # e.g., "APA 7th edition"

  preferred_journals:
    - {{JOURNAL_1}}
    - {{JOURNAL_2}}
```

### Content Creation

```yaml
content_expertise:
  content_types:
    - {{TYPE_1}}  # e.g., "Technical blog posts"
    - {{TYPE_2}}  # e.g., "Documentation"
    - {{TYPE_3}}  # e.g., "Marketing copy"

  seo_proficiency: {{LEVEL}}  # "beginner" | "intermediate" | "expert"

  style_preferences:
    voice: {{VOICE}}  # e.g., "Professional but approachable"
    tone: {{TONE}}  # e.g., "Helpful, clear, confident"
    person: {{PERSON}}  # e.g., "First person plural (we)", "Second person (you)"
```

### Business Analysis

```yaml
business_expertise:
  frameworks:
    - {{FRAMEWORK_1}}  # e.g., "SWOT analysis"
    - {{FRAMEWORK_2}}  # e.g., "Porter's Five Forces"

  financial_modeling:
    - {{SKILL_1}}  # e.g., "DCF valuation"
    - {{SKILL_2}}  # e.g., "Scenario planning"

  industries:
    - {{INDUSTRY_1}}  # e.g., "SaaS"
    - {{INDUSTRY_2}}  # e.g., "E-commerce"
```

---

## 📋 SECTION 5: PROJECT PATTERNS

### Common Project Types

```yaml
project_patterns:
  - pattern_name: "Python CLI Tool"
    description: "Command-line tool in Python"
    typical_structure:
      - "src/{project_name}/__init__.py"
      - "src/{project_name}/cli.py"
      - "src/{project_name}/core.py"
      - "tests/test_cli.py"
      - "pyproject.toml"
      - "README.md"
    typical_dependencies:
      - "click (CLI framework)"
      - "pytest (testing)"
      - "black (formatting)"
    typical_workflow:
      - "poetry install"
      - "poetry run pytest"
      - "poetry run black src tests"

  - pattern_name: "FastAPI Backend"
    description: "REST API using FastAPI"
    typical_structure:
      - "app/main.py"
      - "app/api/routes/"
      - "app/models/"
      - "app/schemas/"
      - "app/services/"
      - "app/db/database.py"
      - "tests/"
      - "alembic/"
    typical_dependencies:
      - "fastapi"
      - "uvicorn"
      - "sqlalchemy"
      - "alembic"
      - "pydantic"
    typical_workflow:
      - "uvicorn app.main:app --reload"
      - "pytest tests/"
      - "alembic upgrade head"
```

### Common Workflows

```yaml
workflows:
  - workflow_name: "New Feature Development"
    steps:
      - step: "Create feature branch"
        command: "git checkout -b feature/{feature-name}"
      - step: "Write failing tests (TDD RED)"
        command: "pytest tests/test_{feature}.py"
      - step: "Implement feature (TDD GREEN)"
        files: "src/{module}/{feature}.py"
      - step: "Refactor (TDD BLUE)"
        checklist:
          - "DRY - no duplication"
          - "Functions <20 lines"
          - "Clear names"
      - step: "Run quality checks"
        command: "black src && mypy src && pytest"
      - step: "Commit"
        command: "git commit -m 'feat: {description}'"
      - step: "Push and create PR"
        command: "git push -u origin feature/{feature-name}"

  - workflow_name: "Bug Fix"
    steps:
      - step: "Reproduce bug"
        action: "Create failing test that demonstrates bug"
      - step: "Fix bug"
        action: "Make minimal change to fix issue"
      - step: "Verify fix"
        action: "Test passes + no regressions"
      - step: "Commit"
        command: "git commit -m 'fix: {bug-description}'"
```

---

## 📋 SECTION 6: LEARNING AND GROWTH

### Knowledge Gaps and Learning Goals

```yaml
learning:
  currently_learning:
    - topic: {{TOPIC_1}}  # e.g., "Rust programming"
      proficiency: {{CURRENT_LEVEL}}  # e.g., "beginner"
      goal_proficiency: {{GOAL_LEVEL}}  # e.g., "intermediate"
      notes: "Focus on ownership and borrowing concepts"

    - topic: {{TOPIC_2}}  # e.g., "Kubernetes"
      proficiency: {{CURRENT_LEVEL}}
      goal_proficiency: {{GOAL_LEVEL}}
      notes: "Need to learn Helm charts and operators"

  want_to_learn:
    - {{TOPIC_3}}  # e.g., "WebAssembly"
    - {{TOPIC_4}}  # e.g., "GraphQL"

  teach_me_about:
    - category: "Concepts I struggle with"
      items:
        - {{CONCEPT_1}}  # e.g., "Async/await internals"
        - {{CONCEPT_2}}  # e.g., "Database indexing strategies"

    - category: "Explain when I use"
      items:
        - {{PATTERN_1}}  # e.g., "When I use Observer pattern, explain the tradeoffs"
        - {{PATTERN_2}}  # e.g., "When I use Redis, explain caching strategies"
```

**Usage Example**:
```yaml
learning:
  currently_learning:
    - topic: "Rust programming"
      proficiency: "beginner"
      goal_proficiency: "intermediate"
      notes: "Focus on ownership and borrowing - explain these concepts when I write Rust code"
```

When user writes Rust code, Claude Code will:
- Explain ownership and borrowing when relevant
- Point out common mistakes beginners make
- Suggest idiomatic Rust patterns
- Provide learning resources

---

## 📋 SECTION 7: CONTEXT AND HISTORY

### Active Projects

```yaml
active_projects:
  - name: {{PROJECT_1}}
    path: {{PROJECT_PATH}}
    domain: {{DOMAIN}}
    status: {{STATUS}}  # "active" | "maintenance" | "archived"
    last_worked: {{DATE}}
    notes: |
      {{PROJECT_NOTES}}

  - name: {{PROJECT_2}}
    path: {{PROJECT_PATH}}
    domain: {{DOMAIN}}
    status: {{STATUS}}
    last_worked: {{DATE}}
    notes: |
      {{PROJECT_NOTES}}
```

**Example**:
```yaml
active_projects:
  - name: "triads-generator"
    path: "~/code/triads"
    domain: "software-development"
    status: "active"
    last_worked: "2024-10-27"
    notes: |
      Constitutional workflow generator for Claude Code.
      Currently implementing template system with domain-aware generation.
      Uses Handlebars for templates, enforces constitutional principles.

  - name: "personal-blog"
    path: "~/code/blog"
    domain: "content-creation"
    status: "maintenance"
    last_worked: "2024-10-15"
    notes: |
      Hugo-based blog. Publishing workflow: write → review → publish.
      SEO focused. Target keyword difficulty <30.
```

### Common Issues and Solutions

```yaml
common_issues:
  - issue: "Poetry install fails on M1 Mac"
    solution: "Use: arch -x86_64 poetry install"
    context: "Some packages don't have ARM builds yet"

  - issue: "Docker build slow on macOS"
    solution: "Use BuildKit: DOCKER_BUILDKIT=1 docker build ."
    context: "BuildKit enables caching and parallel builds"

  - issue: "Import errors in tests"
    solution: "Add empty __init__.py to tests/ directory"
    context: "pytest needs package structure"
```

### Frequently Referenced Resources

```yaml
resources:
  documentation:
    - name: "FastAPI docs"
      url: "https://fastapi.tiangolo.com"
      notes: "Refer to this for FastAPI patterns and best practices"

    - name: "Python Type Hints"
      url: "https://docs.python.org/3/library/typing.html"
      notes: "Reference for complex type annotations"

  repositories:
    - name: "Clean Code Python"
      url: "https://github.com/zedr/clean-code-python"
      notes: "Code quality reference"

  articles:
    - title: "The Twelve-Factor App"
      url: "https://12factor.net"
      notes: "Architecture principles for SaaS applications"
```

---

## 🔧 USAGE EXAMPLES

### Example 1: Concise Expert Python Developer

```yaml
user:
  name: "Alex Chen"
  role: "Senior Backend Engineer"
  primary_domains: ["software-development"]

communication:
  verbosity: "concise"
  technical_level: "expert"
  preferred_format: "code-first"

programming:
  primary_languages:
    - language: "Python"
      proficiency: "expert"
      preferred_version: "3.11+"
      style_guide: "Black + Ruff"

quality:
  test_coverage_minimum: 90
  code_review_checklist:
    - item: "Type hints on all signatures"
      required: true
    - item: "Docstrings in Google format"
      required: true

software_expertise:
  specializations:
    - "High-performance APIs"
    - "Database optimization"
  architectural_patterns:
    prefer: ["Modular monolith", "CQRS"]
    avoid: ["Overly complex abstractions"]
```

**Result**: Claude Code will:
- Provide code-first responses with minimal explanation
- Assume deep Python knowledge
- Focus on performance and optimization
- Enforce strict type hints and 90% coverage
- Prefer simple, pragmatic architectures

---

### Example 2: Detailed Beginner Content Creator

```yaml
user:
  name: "Jordan Lee"
  role: "Content Writer"
  primary_domains: ["content-creation"]

communication:
  verbosity: "detailed"
  technical_level: "beginner"
  preferred_format: "markdown"

content_expertise:
  content_types:
    - "Blog posts"
    - "Social media"
  seo_proficiency: "intermediate"
  style_preferences:
    voice: "Friendly and approachable"
    tone: "Helpful and encouraging"
    person: "Second person (you)"

learning:
  currently_learning:
    - topic: "Technical SEO"
      proficiency: "beginner"
      goal_proficiency: "intermediate"
      notes: "Explain schema markup and Core Web Vitals when relevant"
```

**Result**: Claude Code will:
- Provide detailed explanations with examples
- Explain technical concepts like SEO in simple terms
- Use friendly, encouraging tone
- Teach technical SEO concepts when they come up
- Format responses with clear headings and structure

---

### Example 3: Research Scientist

```yaml
user:
  name: "Dr. Sarah Martinez"
  role: "Research Scientist"
  primary_domains: ["research"]

communication:
  verbosity: "detailed"
  technical_level: "expert"
  preferred_format: "markdown"

research_expertise:
  methodologies:
    - "Quantitative analysis"
    - "Meta-analysis"
  statistical_tools:
    - "R"
    - "Python (scipy/pandas)"
  citation_style: "APA 7th edition"

quality:
  code_review_checklist:
    - item: "Statistical assumptions documented"
      required: true
    - item: "Effect sizes reported"
      required: true
    - item: "Reproducible analysis (seed set)"
      required: true

common_issues:
  - issue: "P-values without effect sizes"
    solution: "Always report effect sizes (Cohen's d, r, η²)"
    context: "Statistical significance ≠ practical significance"
```

**Result**: Claude Code will:
- Provide detailed statistical analysis
- Enforce APA 7th citation style
- Always include effect sizes with p-values
- Document statistical assumptions
- Ensure reproducible analysis

---

## 🚨 IMPORTANT NOTES

### What This File Does NOT Override

**Constitutional Principles** (ABSOLUTE - cannot be overridden):
- Evidence-based claims
- Uncertainty escalation (< 90% confidence)
- Multi-method verification
- Complete transparency
- Assumption auditing
- Communication standards

**Example**:
```yaml
# ❌ THIS DOES NOT WORK
communication:
  uncertainty_threshold: 50  # Try to reduce escalations

# Constitutional principle requires 90% threshold
# User preference cannot override this
# Claude Code will still escalate at 90% threshold
```

### Privacy and Security

**DO NOT store in this file**:
- ❌ Passwords, API keys, tokens
- ❌ Personal identifying information (SSN, credit cards)
- ❌ Proprietary business information
- ❌ Credentials for services

**DO store**:
- ✅ Preferences and working style
- ✅ Tool and framework preferences
- ✅ Learning goals
- ✅ Project patterns
- ✅ Public resource links

### Synchronization

**Location**: `~/.claude/USER_MEMORY.md`

**Backup**: Recommended to version control this file (without secrets):
```bash
# Optional: Track user memory in personal dotfiles repo
cd ~/.claude
git init
git add USER_MEMORY.md
git commit -m "init: User memory configuration"
git remote add origin git@github.com:username/claude-config.git
git push -u origin main
```

**Updates**: This file is read at session start. To reload:
- Restart Claude Code session, OR
- Say "Reload user memory" to force refresh

---

## 📚 INTEGRATION WITH PROJECT MEMORY

### Relationship to CLAUDE.md

```
User Memory (~/.claude/USER_MEMORY.md)
    ↓
    Personal preferences, domain expertise, common patterns

Project Memory (project/.claude/CLAUDE.md)
    ↓
    Project-specific context, team standards, workflow design

Constitutional Principles (.claude/constitutional/*.md)
    ↓
    ABSOLUTE standards that cannot be overridden
```

**Authority Hierarchy**:
1. **Constitutional Principles**: ABSOLUTE (cannot be overridden)
2. **Project Memory**: HIGH (project-specific standards)
3. **User Memory**: MEDIUM (user preferences)
4. **Default Behavior**: LOW (Claude Code defaults)

**Example Conflict Resolution**:
```yaml
# User Memory says:
communication:
  verbosity: "concise"

# Project CLAUDE.md says:
communication:
  require_detailed_explanations: true

# RESULT: Project memory wins (higher authority)
# Claude Code provides detailed explanations for this project
# But uses concise style in other projects
```

---

## 🎓 LEARNING RESOURCES

### Understanding This File

**Sections Explained**:
1. **User Profile**: Who you are, when you work
2. **Communication Preferences**: How you like responses
3. **Technical Preferences**: Tools, languages, quality standards
4. **Domain Expertise**: Your specializations and preferences
5. **Project Patterns**: Common project structures and workflows
6. **Learning and Growth**: What you're learning, what to teach
7. **Context and History**: Active projects, common issues, resources

### Getting Started

**Minimal Configuration** (just 3 fields to start):
```yaml
user:
  name: "Your Name"
  primary_domains: ["software-development"]

communication:
  verbosity: "moderate"
  technical_level: "intermediate"
```

**Recommended Configuration** (add these for better experience):
```yaml
programming:
  primary_languages:
    - language: "Python"  # Or your language
      proficiency: "intermediate"

quality:
  test_coverage_minimum: 80
```

**Advanced Configuration** (add as you discover preferences):
- Project patterns (your common project structures)
- Learning goals (what you want to learn)
- Common issues (problems you encounter frequently)
- Resources (documentation you reference often)

---

## 🔄 MAINTENANCE

### When to Update This File

**Update when**:
- ✅ You discover a new preference
- ✅ Your expertise level changes
- ✅ You start learning something new
- ✅ You solve a common issue
- ✅ You find a useful resource

**Review periodically**:
- 📅 **Monthly**: Review active projects, update status
- 📅 **Quarterly**: Review learning goals, update proficiency
- 📅 **Yearly**: Full review of all sections

### Version History

```yaml
version_history:
  - version: "1.0.0"
    date: "2024-10-27"
    changes:
      - "Initial user memory configuration"

  - version: "1.1.0"
    date: "2024-11-15"
    changes:
      - "Added Rust to learning goals"
      - "Updated Python proficiency to expert"
      - "Added FastAPI project pattern"
```

---

## 💡 TIPS AND BEST PRACTICES

### Start Small, Grow Incrementally

**Week 1**: Just fill in User Profile and Communication Preferences
**Week 2**: Add Technical Preferences as you discover them
**Week 3**: Add Domain Expertise
**Month 2**: Add Project Patterns and Workflows
**Month 3**: Add Learning Goals and Common Issues

### Use Comments for Context

```yaml
quality:
  test_coverage_minimum: 90  # Strict for production code
  # For experimental projects, 70% is acceptable
```

### Document Your "Why"

```yaml
tools:
  package_manager:
    python: "poetry"
    # Why: Better dependency resolution than pip
    # Why: Lock file ensures reproducible installs
    # Why: Virtual env management built-in
```

### Keep It Updated

Set a reminder:
```bash
# Add to crontab (monthly review)
0 9 1 * * echo "Review ~/.claude/USER_MEMORY.md" | mail -s "User Memory Review" you@email.com
```

---

## ✅ TEMPLATE CHECKLIST

Before using this template, customize:

- [ ] **Section 1: User Profile**
  - [ ] Fill in name, role, domains
  - [ ] Set working hours and timezone
  - [ ] Define availability preferences

- [ ] **Section 2: Communication Preferences**
  - [ ] Choose verbosity level (concise/moderate/detailed)
  - [ ] Set technical level (beginner/intermediate/expert)
  - [ ] Define when to ask vs. proceed

- [ ] **Section 3: Technical Preferences**
  - [ ] List primary languages and proficiency
  - [ ] Specify preferred tools
  - [ ] Define quality standards

- [ ] **Section 4: Domain Expertise**
  - [ ] Document specializations
  - [ ] List architectural patterns you prefer/avoid
  - [ ] Define domain-specific standards

- [ ] **Section 5: Project Patterns** (Optional)
  - [ ] Add common project structures
  - [ ] Document typical workflows

- [ ] **Section 6: Learning and Growth** (Optional)
  - [ ] List current learning topics
  - [ ] Document knowledge gaps

- [ ] **Section 7: Context and History** (Optional)
  - [ ] List active projects
  - [ ] Document common issues and solutions
  - [ ] Add frequently referenced resources

---

**Ready to use**? Copy this template to `~/.claude/USER_MEMORY.md` and customize it with your preferences!

**Questions**? See [Claude Code Documentation](https://docs.claude.com/en/docs/claude-code) for more information.

---

*This user memory template was generated by Triads Generator to capture user preferences and context across all Claude Code projects.*

**Template Version**: v1.0.0
**Last Updated**: {{LAST_UPDATED}}
