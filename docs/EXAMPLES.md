# Examples

Real-world examples of using the Triad Generator system across different domains.

---

## Table of Contents

- [Software Development](#software-development)
- [RFP/Bid Writing](#rfpbid-writing)
- [Lead Generation](#lead-generation)
- [Data Analysis](#data-analysis)
- [Content Creation](#content-creation)
- [Research Projects](#research-projects)

---

## Software Development

### Scenario

You're a software developer working on adding OAuth2 authentication to an existing web application.

### Generation Session

```
> /generate-triads

Domain Researcher:
"What type of work do you need help with?"

You:
"I build features for a Python/Flask web application. My typical workflow is:
1. Analyze existing code and requirements
2. Design the solution architecture
3. Implement the code
4. Review and test

I often lose track of requirements when coding, and sometimes miss
security considerations during design."

Domain Researcher:
🔍 Researching software development workflows...

📚 Findings:
• Standard SDLC: Requirements → Design → Implementation → Testing
• Common issue: Requirements loss during coding (you mentioned this!)
• Critical: Security review in design phase

Follow-up questions:
1. Scale: Typical feature size? → "3-5 days usually"
2. Team: Solo or collaborative? → "Solo, but code reviewed"
3. Languages: → "Python, Flask, SQLAlchemy, React"
4. Security: How critical? → "Very - handles user data"
5. Testing: Level needed? → "Unit tests required"

Workflow Analyst:
Based on your software development workflow, here are 2 options:

OPTION A: 3 Triads (Streamlined)
━━━━━━━━━━━━━━━━━━━━━━━━━━

Discovery Triad
  • Codebase Analyst - Explores existing code
  • Requirements Gatherer - Documents needs
  • Knowledge Synthesizer [BRIDGE] - Integrates findings

Design Triad
  • Knowledge Synthesizer [BRIDGE] - Carries requirements
  • Solution Architect [BRIDGE] - Plans solution
  • Security Analyst - Reviews for vulnerabilities

Implementation Triad
  • Solution Architect [BRIDGE] - Carries design
  • Senior Developer - Implements code
  • Code Reviewer - Validates quality

Which fits better?

You: "Option A looks good"

Triad Architect:
✅ Generated 9 agents, 3 hooks, TRUST framework docs

Ready to use!
```

### Using the Generated System

#### Phase 1: Discovery

```
> Start Discovery: analyze the authentication system for OAuth2 integration

[Discovery Triad activates]

Codebase Analyst:
🔍 Analyzing authentication system...

Explored:
├─ src/auth/login.py - Current JWT authentication
├─ src/auth/models.py - User model structure
├─ src/auth/decorators.py - @login_required decorator
└─ config/settings.py - Auth configuration

Key findings:
• JWT tokens stored in httpOnly cookies
• User model has email, password_hash fields
• No OAuth support currently
• Session management via Flask-Login

[GRAPH_UPDATE]
type: add_node
node_type: Entity
node_id: current_auth_system
label: "JWT-based authentication"
description: "Located in src/auth/, uses JWT tokens in httpOnly cookies"
confidence: 0.95
evidence: "Direct code analysis of src/auth/ files"
created_by: codebase-analyst
[/GRAPH_UPDATE]

Requirements Gatherer:
📋 Documenting OAuth2 requirements...

Requirements identified:
1. Support Google and GitHub OAuth2 providers
2. Link OAuth accounts to existing users by email
3. Handle new user creation from OAuth
4. Maintain existing JWT auth alongside OAuth
5. Secure token storage and refresh logic

[GRAPH_UPDATE]
type: add_node
node_type: Concept
node_id: req_oauth2_providers
label: "Support Google and GitHub OAuth2"
description: "Users should be able to sign in with Google or GitHub accounts"
confidence: 1.0
evidence: "Requirements document section 3.2"
created_by: requirements-gatherer
[/GRAPH_UPDATE]

Knowledge Synthesizer:
🧠 Synthesizing discovery findings...

Integration points identified:
• OAuth flow must work with existing User model
• Need new OAuthAccount model to link providers
• JWT generation code can be reused
• Consider security: CSRF protection, state parameter

Critical context for design phase:
1. Existing auth uses src/auth/login.py - extend here
2. User model needs relationship to OAuthAccount
3. Security requirement: httpOnly cookies + CSRF protection

[GRAPH_UPDATE]
type: add_node
node_type: Decision
node_id: decision_extend_existing
label: "Extend existing auth rather than replace"
description: "OAuth should integrate with current JWT system"
rationale: "Maintains backward compatibility, reuses tested code"
confidence: 0.88
created_by: knowledge-synthesizer
[/GRAPH_UPDATE]

✅ Discovery complete
Knowledge graph: .claude/graphs/discovery_graph.json (42 nodes)
```

#### Phase 2: Design

```
> Start Design: plan OAuth2 integration architecture

[Design Triad activates]

Knowledge Synthesizer [BRIDGE]:
🌉 Loading Discovery context...
Compressed 42 nodes → 20 critical nodes + neighbors

Carrying forward:
• Current auth system structure
• OAuth2 provider requirements (Google, GitHub)
• Decision to extend existing system
• Security constraints (httpOnly, CSRF)

Solution Architect:
🏗️ Designing OAuth2 integration architecture...

With full Discovery context in mind, here's the design:

Architecture:
┌─────────────────┐
│ OAuth2 Routes   │  /auth/oauth/{provider}
└────────┬────────┘
         │
┌────────▼────────┐
│ OAuth Handler   │  Manages OAuth flow
└────────┬────────┘
         │
┌────────▼────────┐
│ Provider Config │  Google, GitHub credentials
└────────┬────────┘
         │
┌────────▼────────┐
│ OAuthAccount    │  New model linking User to providers
└─────────────────┘

Database changes:
• New table: oauth_accounts (user_id, provider, provider_user_id, tokens)
• User model: relationship to oauth_accounts

Libraries:
• Authlib - Well-maintained OAuth2 client library
• Provides: state validation, token refresh, PKCE support

[GRAPH_UPDATE]
type: add_node
node_type: Decision
node_id: decision_use_authlib
label: "Use Authlib for OAuth2 client"
description: "Adopt Authlib library for OAuth2 implementation"
rationale: "Secure, maintained, handles state/PKCE/refresh automatically"
confidence: 0.9
evidence: "Authlib docs, security audit reports, active maintenance"
created_by: solution-architect
[/GRAPH_UPDATE]

Security Analyst:
🔒 Security review of OAuth2 design...

Reviewing design with Discovery context (CSRF requirement noted):

Security considerations:
✅ State parameter: Authlib provides CSRF protection
✅ PKCE: Use for authorization code flow
✅ Token storage: Store in database, encrypted at rest
⚠️  Token refresh: Need refresh token rotation
⚠️  Scope minimization: Request only necessary scopes

Recommendations:
1. Enable PKCE in Authlib config
2. Implement refresh token rotation
3. Minimal scopes: Google (profile, email), GitHub (user:email)
4. Rate limiting on OAuth endpoints
5. Audit logging for OAuth events

[GRAPH_UPDATE]
type: add_node
node_type: Finding
node_id: security_token_rotation
label: "Implement refresh token rotation"
description: "OAuth refresh tokens should rotate on use to prevent replay attacks"
confidence: 0.92
evidence: "OAuth2 Security Best Practices RFC 6819 section 5.2.2"
created_by: security-analyst
[/GRAPH_UPDATE]

✅ Design complete
Knowledge graph: .claude/graphs/design_graph.json (38 nodes)
Bridge context preserved from Discovery
```

#### Phase 3: Implementation

```
> Start Implementation: build OAuth2 authentication flow

[Implementation Triad activates]

Solution Architect [BRIDGE]:
🌉 Loading Design context...

Carrying forward complete architecture:
• Authlib library decision
• OAuthAccount model specification
• Security requirements (PKCE, rotation, scopes)
• Integration points with existing auth

Senior Developer:
💻 Implementing OAuth2 flow...

With full architecture from Design phase:

Step 1: Install and configure Authlib
```bash
pip install Authlib
```

Step 2: Create OAuthAccount model
```python
# src/auth/models.py

from sqlalchemy.orm import relationship
from src.database import db
import json

class OAuthAccount(db.Model):
    __tablename__ = 'oauth_accounts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    provider = db.Column(db.String(50), nullable=False)  # 'google' or 'github'
    provider_user_id = db.Column(db.String(255), nullable=False)
    access_token = db.Column(db.Text, nullable=False)  # Encrypted
    refresh_token = db.Column(db.Text)  # Encrypted
    expires_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = relationship('User', back_populates='oauth_accounts')

    __table_args__ = (
        db.UniqueConstraint('provider', 'provider_user_id', name='provider_user_unique'),
    )

# Update User model
class User(db.Model):
    # ... existing fields ...
    oauth_accounts = relationship('OAuthAccount', back_populates='user', cascade='all, delete-orphan')
```

Step 3: Configure OAuth2 providers
```python
# src/auth/oauth.py

from authlib.integrations.flask_client import OAuth

oauth = OAuth()

def init_oauth(app):
    # Google OAuth2
    oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid profile email'}  # Minimal scopes per security review
    )

    # GitHub OAuth2
    oauth.register(
        name='github',
        client_id=app.config['GITHUB_CLIENT_ID'],
        client_secret=app.config['GITHUB_CLIENT_SECRET'],
        access_token_url='https://github.com/login/oauth/access_token',
        authorize_url='https://github.com/login/oauth/authorize',
        client_kwargs={'scope': 'user:email'}  # Minimal scopes
    )
```

Step 4: Implement OAuth routes
```python
# src/auth/oauth_routes.py

from flask import Blueprint, redirect, url_for, session
from src.auth.oauth import oauth
from src.auth.models import User, OAuthAccount
from src.auth.jwt_utils import generate_jwt  # Reuse existing JWT code

oauth_bp = Blueprint('oauth', __name__, url_prefix='/auth/oauth')

@oauth_bp.route('/<provider>')
def oauth_login(provider):
    """Initiate OAuth flow"""
    if provider not in ['google', 'github']:
        return {'error': 'Invalid provider'}, 400

    client = oauth.create_client(provider)
    redirect_uri = url_for('oauth.oauth_callback', provider=provider, _external=True)

    # PKCE enabled automatically by Authlib
    return client.authorize_redirect(redirect_uri)

@oauth_bp.route('/<provider>/callback')
def oauth_callback(provider):
    """Handle OAuth callback"""
    client = oauth.create_client(provider)

    # Get access token (includes state validation)
    token = client.authorize_access_token()

    # Get user info from provider
    if provider == 'google':
        user_info = client.get('https://www.googleapis.com/oauth2/v3/userinfo').json()
        provider_user_id = user_info['sub']
        email = user_info['email']
        name = user_info.get('name')
    elif provider == 'github':
        user_info = client.get('https://api.github.com/user').json()
        provider_user_id = str(user_info['id'])
        email = user_info['email']
        name = user_info.get('name')

    # Find or create user
    oauth_account = OAuthAccount.query.filter_by(
        provider=provider,
        provider_user_id=provider_user_id
    ).first()

    if oauth_account:
        user = oauth_account.user
    else:
        # Try to find existing user by email
        user = User.query.filter_by(email=email).first()
        if not user:
            # Create new user
            user = User(email=email, name=name)
            db.session.add(user)

        # Create OAuth account link
        oauth_account = OAuthAccount(
            user_id=user.id,
            provider=provider,
            provider_user_id=provider_user_id,
            access_token=encrypt(token['access_token']),  # Encrypt before storage
            refresh_token=encrypt(token.get('refresh_token')),
            expires_at=datetime.utcnow() + timedelta(seconds=token['expires_in'])
        )
        db.session.add(oauth_account)

    db.session.commit()

    # Generate JWT (reusing existing code per Discovery findings)
    jwt_token = generate_jwt(user.id)

    # Set httpOnly cookie (matching existing auth per Security review)
    response = redirect(url_for('dashboard'))
    response.set_cookie(
        'auth_token',
        jwt_token,
        httponly=True,
        secure=True,
        samesite='Lax'
    )

    return response
```

Step 5: Token refresh logic
```python
# src/auth/oauth_refresh.py

def refresh_oauth_token(oauth_account):
    """Refresh OAuth token with rotation per security requirements"""
    client = oauth.create_client(oauth_account.provider)

    # Use refresh token
    token = client.fetch_access_token(
        refresh_token=decrypt(oauth_account.refresh_token)
    )

    # Rotate tokens (security requirement from design phase)
    oauth_account.access_token = encrypt(token['access_token'])
    if 'refresh_token' in token:
        oauth_account.refresh_token = encrypt(token['refresh_token'])
    oauth_account.expires_at = datetime.utcnow() + timedelta(seconds=token['expires_in'])

    db.session.commit()
```

[GRAPH_UPDATE]
type: add_node
node_type: Entity
node_id: impl_oauth_routes
label: "OAuth routes implementation"
description: "Complete OAuth flow with login, callback, token refresh"
confidence: 0.95
evidence: "Code in src/auth/oauth_routes.py, src/auth/oauth_refresh.py"
created_by: senior-developer
[/GRAPH_UPDATE]

Code Reviewer:
✅ Code review...

Reviewing implementation against Design specifications:

✅ Authlib library used as specified
✅ OAuthAccount model matches design
✅ PKCE enabled (Authlib default)
✅ Minimal scopes (profile+email for Google, user:email for GitHub)
✅ Token encryption before storage
✅ Refresh token rotation implemented
✅ httpOnly cookies match existing auth
✅ Reuses JWT generation code
✅ Error handling present

Suggestions:
1. Add rate limiting to oauth routes (use Flask-Limiter)
2. Add audit logging for OAuth events
3. Add unit tests for token refresh logic
4. Document OAuth setup in README

[GRAPH_UPDATE]
type: add_node
node_type: Task
node_id: task_add_tests
label: "Add unit tests for OAuth flow"
description: "Test token refresh, user creation, account linking"
confidence: 1.0
created_by: code-reviewer
[/GRAPH_UPDATE]

✅ Implementation complete
All security requirements from Design phase satisfied
All integration points from Discovery phase addressed
```

### Result

**Complete OAuth2 integration** built with:
- ✅ Zero context loss (bridge agents preserved requirements and design)
- ✅ Security requirements met (PKCE, rotation, minimal scopes, encryption)
- ✅ Architectural consistency (extended existing system as decided in Discovery)
- ✅ Quality assurance (TRUST principles enforced)

**Knowledge graphs captured**:
- Discovery: Current system structure, requirements, integration points
- Design: Architecture decisions, security considerations, library choices
- Implementation: Code structure, review findings, follow-up tasks

---

## RFP/Bid Writing

### Scenario

You write proposals in response to RFPs for government contracts.

### Generation Session (Abbreviated)

```
> /generate-triads

You: "I write RFP responses. My workflow:
1. Analyze RFP requirements and compliance matrix
2. Research competitors and develop win themes
3. Write technical approach and management sections
4. Validate compliance and finalize pricing

I often lose compliance requirements between analysis and writing."

[Generator Triad designs 4-triad system]

Analysis Triad
  • RFP Analyst - Extracts requirements
  • Compliance Checker - Creates compliance matrix
  • Requirements Synthesizer [BRIDGE]

Strategy Triad
  • Requirements Synthesizer [BRIDGE]
  • Win Theme Developer [BRIDGE]
  • Competitive Researcher

Writing Triad
  • Win Theme Developer [BRIDGE]
  • Technical Writer [BRIDGE]
  • Management Writer

Validation Triad
  • Technical Writer [BRIDGE]
  • Compliance Validator
  • Pricing Analyst
```

### Usage Example

```
> Start Analysis: review RFP for cloud migration services (rfp_document.pdf)

[Analysis Triad extracts all requirements, builds compliance matrix]
Identified: 47 mandatory requirements, 23 evaluation criteria
Graph: analysis_graph.json

> Start Strategy: develop win themes for cloud migration proposal

[Requirements Synthesizer bridges compliance requirements forward]
[Strategy Triad develops 3 win themes based on requirements]
Win themes: (1) Zero downtime migration, (2) Cost optimization, (3) Federal security compliance
Graph: strategy_graph.json (includes compliance context)

> Start Writing: draft technical approach section

[Win Theme Developer bridges themes and requirements forward]
[Writing Triad drafts technical approach aligned with win themes]
Technical approach: 15 pages addressing all 47 requirements
Graph: writing_graph.json

> Start Validation: check compliance and finalize pricing

[Technical Writer bridges draft content forward]
[Validation Triad checks all requirements addressed]
Compliance: 47/47 requirements addressed ✅
Pricing: Competitive within budget ceiling
```

**Result**: Compliant proposal with zero missed requirements, consistent win themes throughout, delivered on time.

---

## Lead Generation

### Scenario

You generate and qualify leads for a B2B SaaS company.

### Generated System

```
Prospecting Triad
  • Company Researcher - Finds prospects via WebSearch
  • Qualification Analyst - Scores leads
  • Lead Synthesizer [BRIDGE]

Enrichment Triad
  • Lead Synthesizer [BRIDGE]
  • Profile Builder [BRIDGE]
  • Contact Finder

Outreach Prep Triad
  • Profile Builder [BRIDGE]
  • Messaging Specialist
  • Sequence Designer
```

### Usage Example

```
> Start Prospecting: find 50 SaaS companies in fintech with 50-200 employees

[Prospecting Triad searches, qualifies, scores prospects]
Found: 73 companies meeting criteria
Qualified: 52 companies (71% qualification rate)
Top 20 by score saved
Graph: prospecting_graph.json

> Start Enrichment: build detailed profiles for top 20 prospects

[Lead Synthesizer bridges qualification criteria and scores]
[Enrichment Triad builds comprehensive profiles]
Profiles include: Tech stack, recent funding, pain points, decision makers
Graph: enrichment_graph.json

> Start Outreach: create personalized messaging for top 20

[Profile Builder bridges full profiles forward]
[Outreach Prep creates personalized sequences]
Output: 20 personalized email sequences, 5-email each
Personalization based on: pain points, tech stack, recent news
```

**Result**: Highly qualified leads with personalized outreach, significantly higher response rates.

---

## Data Analysis

### Scenario

You analyze sales data to identify trends and make recommendations.

### Generated System

```
Collection Triad
  • Data Gatherer - Collects from sources
  • Data Cleaner - Cleans and validates
  • Data Synthesizer [BRIDGE]

Analysis Triad
  • Data Synthesizer [BRIDGE]
  • Statistical Analyst [BRIDGE]
  • Visualization Specialist

Insights Triad
  • Statistical Analyst [BRIDGE]
  • Insight Generator
  • Recommendation Writer
```

### Usage Example

```
> Start Collection: gather Q4 sales data from CRM and financial systems

[Collection Triad gathers, cleans, validates data]
Collected: 47,382 transactions
Cleaned: Removed 127 duplicates, filled 43 missing values
Ready for analysis
Graph: collection_graph.json (includes data quality metrics)

> Start Analysis: analyze Q4 sales trends and patterns

[Data Synthesizer bridges data quality context]
[Analysis Triad performs statistical analysis]
Key findings: 23% increase in enterprise segment, 15% churn in SMB
Visualizations: 12 charts created
Graph: analysis_graph.json

> Start Insights: generate actionable recommendations

[Statistical Analyst bridges findings and statistical context]
[Insights Triad generates recommendations]
Recommendations:
1. Double down on enterprise sales (highest growth)
2. SMB churn intervention needed (high-risk accounts identified)
3. Pricing optimization opportunity in mid-market
```

**Result**: Data-driven recommendations with full statistical backing and clear action items.

---

## Content Creation

### Scenario

You create technical blog posts for a developer audience.

### Generated System

```
Research Triad
  • Topic Researcher - Researches subject matter
  • Audience Analyzer - Understands target readers
  • Content Strategist [BRIDGE]

Writing Triad
  • Content Strategist [BRIDGE]
  • Technical Writer [BRIDGE]
  • Code Example Developer

Polish Triad
  • Technical Writer [BRIDGE]
  • Editor
  • SEO Specialist
```

### Usage Example

```
> Start Research: research "Kubernetes autoscaling best practices" for DevOps engineers

[Research Triad researches topic, analyzes audience]
Findings: Current pain points, common mistakes, trending solutions
Audience: DevOps engineers, intermediate level, need practical examples
Strategy: Hands-on tutorial format with code examples
Graph: research_graph.json

> Start Writing: draft Kubernetes autoscaling tutorial

[Content Strategist bridges strategy and audience insights]
[Writing Triad creates tutorial with code examples]
Draft: 2,500 words, 8 code examples, 3 diagrams
Covers: HPA, VPA, Cluster Autoscaler with real configs
Graph: writing_graph.json

> Start Polish: edit and optimize for SEO

[Technical Writer bridges draft content]
[Polish Triad edits, optimizes]
Final: 2,700 words, improved clarity, SEO optimized
Title, meta description, headings optimized for "kubernetes autoscaling"
Images alt text added
```

**Result**: High-quality technical content, audience-appropriate, SEO-optimized, ready to publish.

---

## Research Projects

### Scenario

You conduct research projects that require literature review, data collection, analysis, and writing.

### Generated System

```
Literature Review Triad
  • Paper Searcher - Finds relevant papers
  • Paper Analyzer - Reads and extracts key points
  • Literature Synthesizer [BRIDGE]

Methodology Triad
  • Literature Synthesizer [BRIDGE]
  • Methodology Designer [BRIDGE]
  • Ethics Reviewer

Execution Triad
  • Methodology Designer [BRIDGE]
  • Data Collector [BRIDGE]
  • Data Analyst

Writing Triad
  • Data Collector [BRIDGE]
  • Academic Writer
  • Citation Manager
```

### Usage Example

```
> Start Literature Review: review papers on machine learning interpretability

[Literature Review Triad searches, analyzes papers]
Found: 87 relevant papers (2019-2024)
Analyzed: 32 high-impact papers
Key themes: SHAP, LIME, attention mechanisms, counterfactual explanations
Gaps identified: Limited work on interpretability for multimodal models
Graph: literature_graph.json

> Start Methodology: design study on interpretability for vision-language models

[Literature Synthesizer bridges research findings and gaps]
[Methodology Triad designs study]
Study design: Comparative analysis of SHAP vs attention for VLMs
Dataset: COCO captions (5,000 samples)
Metrics: Faithfulness, stability, comprehensibility
Ethics: No human subjects, using public dataset
Graph: methodology_graph.json

> Start Execution: collect data and run experiments

[Methodology Designer bridges complete study design]
[Execution Triad runs experiments]
Experiments: 3 VLMs tested (CLIP, BLIP, LLaVA)
Data: 5,000 samples processed
Results: SHAP more faithful (0.87 vs 0.73), attention more stable
Graph: execution_graph.json

> Start Writing: write research paper

[Data Collector bridges experimental results and context]
[Writing Triad writes academic paper]
Paper: 8,000 words, 6 figures, 4 tables
Sections: Abstract, Intro, Related Work, Methodology, Results, Discussion
Citations: 45 references properly formatted (ACL style)
Ready for submission
```

**Result**: Complete research paper with solid methodology, rigorous execution, proper citations.

---

## Common Patterns Across Examples

### Context Preservation

All examples show **zero context loss** between phases:
- Requirements carry forward to implementation
- Compliance criteria never forgotten
- Qualification criteria inform outreach
- Data quality metrics inform analysis
- Research findings guide methodology

### Quality Through TRUST Principles

All examples enforce the TRUST framework:
- **T (Thorough over fast)**: Complete analysis, no shortcuts
- **R (Require evidence)**: All findings cited with sources
- **U (Uncertainty escalation)**: Unknowns flagged explicitly
- **S (Show all work)**: All reasoning transparent
- **T (Test assumptions)**: Assumptions validated

### Knowledge Graphs Capture Learning

All examples build knowledge graphs that:
- Document decisions with rationale
- Track uncertainties and their resolution
- Link related entities and concepts
- Preserve provenance and confidence scores
- Enable review and auditing

---

## Creating Your Own Example

**Steps**:
1. Run `/generate-triads`
2. Describe your workflow honestly
3. Answer follow-up questions
4. Review proposed structure
5. Let system generate
6. Start using: `Start {Triad}: {task}`

**Tips**:
- Be specific about where you lose context
- Mention critical quality areas (security, compliance, etc.)
- Describe typical scale (hours/days/weeks)
- Note any domain-specific constraints

**The system will adapt to YOUR needs** - these examples show the pattern, but your generated system will be unique to your workflow.

---

**Ready to try it? See [Usage Guide](USAGE.md) for detailed instructions.**
