# Server-Hosted Triads Architecture

**Status**: Design Proposal
**Created**: 2025-10-19
**Authors**: Design discussion with Claude
**Target**: v0.8.0 (Server Mode)

---

## Executive Summary

### Problem Statement

Current triads system operates exclusively as a Claude Code plugin, limiting usage to:
- Local development environments only
- Single-user, single-machine workflows
- Requires Claude Code CLI installation
- No programmatic API access
- State tied to local filesystem

**Users need**: Server-hosted triads accessible via API, supporting remote access, team collaboration, and programmatic integration while maintaining the same agent behavior as local mode.

### Proposed Solution

Deploy triads as a **serverless Cloud Run service** that:
1. Accepts user-specified Git repository URLs via API
2. Clones repos ephemerally to in-memory storage
3. Uses **Claude Agent SDK** to execute existing `.claude/` agent configurations
4. Creates Pull Requests with changes via GitHub API
5. Scales automatically with zero ops overhead

**Key Innovation**: The `.claude/` directory becomes a **portable agent configuration bundle** that works identically in both local Claude Code and server-hosted environments.

### Key Architectural Decisions

| Decision | Rationale |
|----------|-----------|
| **Claude Agent SDK** | Official SDK provides agent execution, context management, session handling - eliminates 12+ weeks of custom development |
| **Google Cloud Run** | Serverless, auto-scaling, no infrastructure management, pay-per-use |
| **Ephemeral Git Clones** | Stateless request model, simpler than persistent workspaces, natural cleanup |
| **In-Memory Volumes** | Size-limited storage prevents crashes, faster than Cloud Storage FUSE |
| **Same .claude/ Format** | Single source of truth, no translation layer, generator works for both modes |
| **Git Integration** | Server creates PRs instead of direct file writes, fits Git workflow |

---

## Architecture Overview

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│  USERS                                                            │
│  ├─ Developer (API requests from CLI/SDK)                        │
│  ├─ CI/CD (Programmatic integration)                             │
│  └─ Web UI (Interactive interface) [Future]                      │
└────────────────────────┬─────────────────────────────────────────┘
                         │ HTTPS/WebSocket
┌────────────────────────▼─────────────────────────────────────────┐
│  GOOGLE CLOUD RUN (Serverless Container)                         │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ FastAPI Application                                        │  │
│  │ ├─ POST /api/v1/execute (main endpoint)                    │  │
│  │ ├─ GET /api/v1/status/{request_id}                         │  │
│  │ └─ WebSocket /ws/stream (streaming) [Future]               │  │
│  └────────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ Request Handler                                            │  │
│  │ 1. Validate & authenticate request                         │  │
│  │ 2. Clone Git repo to /workspaces/{request_id}/             │  │
│  │ 3. Inject .claude/ if not present                          │  │
│  │ 4. Initialize Claude Agent SDK                             │  │
│  │ 5. Execute agent workflow                                  │  │
│  │ 6. Create PR with changes                                  │  │
│  │ 7. Cleanup workspace                                       │  │
│  └────────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ Claude Agent SDK (Official)                                │  │
│  │ ├─ Agent execution engine                                  │  │
│  │ ├─ Context management & compaction                         │  │
│  │ ├─ Tool calling (Read, Write, Edit, Bash, etc.)           │  │
│  │ ├─ Session persistence                                     │  │
│  │ └─ Loads .claude/ config automatically                     │  │
│  └────────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ In-Memory Volume (Gen2)                                    │  │
│  │ /workspaces/ (2Gi size limit)                              │  │
│  │   └─ {request_id}/                                         │  │
│  │       ├─ .git/                                             │  │
│  │       ├─ .claude/                                          │  │
│  │       │   ├─ agents/                                       │  │
│  │       │   ├─ graphs/                                       │  │
│  │       │   └─ settings.json                                 │  │
│  │       └─ [project files]                                   │  │
│  └────────────────────────────────────────────────────────────┘  │
└────────────────────────┬─────────────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────────────┐
│  EXTERNAL SERVICES                                                │
│  ├─ GitHub API (clone repos, create PRs)                         │
│  ├─ Cloud Storage (bundled .claude/ templates) [Optional]        │
│  ├─ Cloud SQL (knowledge graph persistence) [Future]             │
│  └─ Secret Manager (API keys, GitHub tokens)                     │
└──────────────────────────────────────────────────────────────────┘
```

### Request Flow

```
1. User Request
   POST /api/v1/execute
   {
     "repo_url": "https://github.com/user/project.git",
     "prompt": "Start Implementation: Add OAuth",
     "github_token": "ghp_xxx",
     "triad_config": "default"
   }

2. Server Processing
   ├─ Authenticate request
   ├─ Clone repo to /workspaces/{request_id}/
   ├─ Check for .claude/ directory
   │   ├─ If exists: Use as-is
   │   └─ If missing: Inject from template
   ├─ Initialize Claude Agent SDK
   │   └─ SDK loads .claude/agents/, settings.json, graphs/
   ├─ Execute agent
   │   ├─ Agent reads/writes files
   │   ├─ Updates knowledge graphs
   │   └─ Follows triad workflow
   ├─ Detect git changes
   └─ Create PR via GitHub API

3. Response
   {
     "status": "success",
     "request_id": "550e8400-...",
     "pr_url": "https://github.com/user/project/pull/42",
     "changes_made": true,
     "messages": [...]
   }

4. Cleanup
   └─ Delete /workspaces/{request_id}/ (background task)
```

---

## Storage Strategy

### Decision: In-Memory Volumes (Gen2)

Cloud Run Gen2 supports three storage options:

| Option | Use Case | Pros | Cons |
|--------|----------|------|------|
| **Default /tmp** | POC, tiny repos (<100MB) | No config needed | No size limit → crash risk |
| **In-Memory Volume** ✅ | Production git clones | Size-limited, crash-safe | Requires Gen2 |
| **Cloud Storage FUSE** | Persistent cache | Persistent across requests | Slower, FUSE overhead |

**Recommendation**: **In-Memory Volumes** for Phase 1-2

### Why In-Memory Volumes?

```yaml
# Cloud Run Service Configuration
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: triads-server
spec:
  template:
    metadata:
      annotations:
        run.googleapis.com/execution-environment: gen2  # Required!
    spec:
      containers:
      - image: gcr.io/PROJECT/triads-server
        resources:
          limits:
            memory: 4Gi
            cpu: 2
        volumeMounts:
        - name: workspace-storage
          mountPath: /workspaces  # Git clones here
      volumes:
      - name: workspace-storage
        emptyDir:
          medium: Memory
          sizeLimit: 2Gi  # Prevents crash if repo too large!
```

**Benefits**:
- **Crash protection**: Size limit prevents OOM crashes
- **Graceful errors**: Write fails when full (not crash)
- **Fast**: In-memory performance
- **Clean**: Auto-cleanup on container shutdown

**Trade-offs**:
- Requires Gen2 execution environment
- Slightly more complex deployment
- Not persistent (but we want ephemeral for stateless design)

### Size Recommendations

| Container Memory | Volume Size | Supported Repo Size |
|------------------|-------------|---------------------|
| 2 Gi | 1 Gi | Small repos (<500MB) |
| 4 Gi ✅ | 2 Gi | Medium repos (<1GB) |
| 8 Gi | 4 Gi | Large repos (<2GB) |

**Default**: 4Gi container, 2Gi volume

---

## Claude Agent SDK Integration

### Why Claude Agent SDK?

Claude Agent SDK is the **official agent execution framework** from Anthropic, powering Claude Code itself.

**What it provides** (out of the box):
- ✅ Agent execution engine
- ✅ Automatic context management & compaction
- ✅ Session persistence and resumption
- ✅ Tool calling framework (Read, Write, Edit, Bash, Grep, Glob)
- ✅ Custom tool/hook support (Python functions)
- ✅ Streaming API
- ✅ Error handling and retry logic
- ✅ **Loads .claude/ configuration automatically**

**Time savings**: ~12-16 weeks of development eliminated

### The Key Insight: .claude/ as Portable Config

The Claude Agent SDK can load the **exact same .claude/ directory** that works in Claude Code:

```python
from claude_agent_sdk import query, ClaudeAgentOptions

# Initialize SDK pointing at workspace
options = ClaudeAgentOptions(
    setting_sources=["project"],  # ← Load .claude/ config!
    cwd="/workspaces/abc123/",     # Repo location
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    allowed_tools=["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
)

# Execute - SDK automatically:
# 1. Loads .claude/agents/*.md files
# 2. Loads .claude/settings.json (hooks)
# 3. Injects .claude/graphs/*.json context
# 4. Executes agent with full Claude Code behavior

async for message in query(prompt, options):
    print(message)
```

**This means**:
- ✅ Generator creates ONE .claude/ directory
- ✅ Works in Claude Code locally
- ✅ Works in server mode remotely
- ✅ No translation or conversion needed
- ✅ Agents behave identically in both environments

---

## Git Integration Strategy

### Server-Side File Operations Challenge

**Problem**: Triad agents (especially Implementation and Garden Tending) use file tools:
- `Read(file_path)` - Read files
- `Write(file_path, content)` - Create/overwrite files
- `Edit(file_path, old, new)` - Modify files
- `Bash(command)` - Run commands

In local Claude Code, these operate on the user's filesystem directly.

In server mode, there's no user filesystem!

### Solution: Git Clone + PR Workflow

```
1. Clone user's repo to /workspaces/{request_id}/
   └─ Full git repository with .git/ directory

2. Agent executes, modifies files
   ├─ Write() creates new files
   ├─ Edit() modifies existing files
   └─ Files tracked by git

3. Detect changes via git status
   └─ git status --porcelain

4. Create feature branch
   └─ git checkout -b triads/{request_id}

5. Commit changes
   └─ git commit -am "Triads: {prompt}"

6. Push to GitHub
   └─ git push origin triads/{request_id}

7. Create PR via GitHub API
   └─ gh api repos/{owner}/{repo}/pulls
```

**Benefits**:
- ✅ Agents work on real files (SDK sees normal filesystem)
- ✅ Changes reviewable via PR
- ✅ Fits Git workflow
- ✅ User controls merge

**Trade-offs**:
- Every execution creates a PR (could be noisy)
- Requires GitHub API access
- Needs authentication (GitHub token)

---

## API Design

### Phase 1: Execute Endpoint

```http
POST /api/v1/execute
Content-Type: application/json
Authorization: Bearer {api_key}

{
  "repo_url": "https://github.com/user/project.git",
  "prompt": "Start Implementation: Add OAuth login",
  "github_token": "ghp_xxx",         // Optional for private repos
  "triad_config": "default",         // Which .claude/ template
  "base_branch": "main",             // Branch to clone
  "create_pr": true                  // Auto-create PR if changes
}
```

**Response**:
```json
{
  "status": "success",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "repo_size_mb": 234,
  "execution_time_ms": 45230,
  "changes_made": true,
  "pr_url": "https://github.com/user/project/pull/42",
  "files_changed": [
    "src/auth/oauth.py",
    "tests/test_oauth.py",
    ".claude/graphs/implementation_graph.json"
  ],
  "messages": [
    {"type": "agent_output", "content": "Analyzing codebase..."},
    {"type": "tool_call", "tool": "Read", "args": {"file": "src/auth.py"}},
    {"type": "agent_output", "content": "Implementing OAuth..."}
  ]
}
```

### Phase 2: Status Endpoint

```http
GET /api/v1/status/{request_id}
Authorization: Bearer {api_key}
```

**Response**:
```json
{
  "request_id": "550e8400-...",
  "status": "running",  // pending, running, completed, failed
  "progress": {
    "current_agent": "senior-developer",
    "triad": "implementation",
    "step": "Writing code"
  },
  "started_at": "2025-10-19T12:34:56Z",
  "estimated_completion": "2025-10-19T12:36:30Z"
}
```

### Phase 3: WebSocket Streaming (Future)

```javascript
const ws = new WebSocket('wss://triads.example.com/ws/stream');

ws.send(JSON.stringify({
  repo_url: "https://github.com/user/project.git",
  prompt: "Start Implementation: OAuth",
  github_token: "ghp_xxx"
}));

ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  // { type: "agent_output", content: "..." }
  // { type: "tool_call", tool: "Read", args: {...} }
  // { type: "complete", pr_url: "..." }
};
```

---

## Deployment Configuration

### Dockerfile

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY main.py .

# Optional: Bundle default .claude/ templates
COPY triad-templates/ /app/triad-templates/

# Run server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### requirements.txt

```
# Core
claude-agent-sdk>=1.0.0
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
pydantic>=2.0.0

# Git integration
PyGithub>=2.1.0

# Google Cloud (optional)
google-cloud-storage>=2.10.0
google-cloud-secret-manager>=2.16.0

# Utilities
python-multipart>=0.0.6
aiofiles>=23.0.0
```

### Cloud Run Deployment

```bash
# Build and deploy
gcloud run deploy triads-server \
    --source . \
    --region us-central1 \
    --execution-environment=gen2 \
    --memory=4Gi \
    --cpu=2 \
    --timeout=600s \
    --max-instances=10 \
    --min-instances=0 \
    --allow-unauthenticated \
    --set-env-vars="ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}" \
    --set-secrets="GITHUB_TOKEN=github-token:latest"
```

### Service Configuration (service.yaml)

```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: triads-server
spec:
  template:
    metadata:
      annotations:
        run.googleapis.com/execution-environment: gen2
        autoscaling.knative.dev/maxScale: '10'
        autoscaling.knative.dev/minScale: '0'
    spec:
      containerConcurrency: 5
      timeoutSeconds: 600
      containers:
      - image: gcr.io/PROJECT_ID/triads-server:latest
        resources:
          limits:
            memory: 4Gi
            cpu: '2'
        env:
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: anthropic-api-key
              key: latest
        - name: ENVIRONMENT
          value: production
        volumeMounts:
        - name: workspace-storage
          mountPath: /workspaces
      volumes:
      - name: workspace-storage
        emptyDir:
          medium: Memory
          sizeLimit: 2Gi
```

---

## Implementation Phases

### Phase 1: Proof of Concept (Weeks 1-2)

**Goal**: Validate core architecture with minimal features

**Scope**:
- ✅ FastAPI server on Cloud Run
- ✅ Claude Agent SDK integration
- ✅ Public repo cloning only
- ✅ Single agent execution
- ✅ In-memory volumes
- ✅ No PR creation (just show changes)

**Deliverables**:
- Working `/api/v1/execute` endpoint
- Can clone public repo, run single agent
- Returns agent output and file changes
- Deployed to Cloud Run

**Validation Criteria**:
- Clone small public repo (<100MB)
- Execute research-analyst agent
- Verify .claude/ config loads correctly
- Verify file operations work
- Response time <2 minutes

### Phase 2: Git Integration (Weeks 3-4)

**Goal**: Complete Git workflow with PR creation

**Scope**:
- ✅ GitHub token authentication
- ✅ Private repo support
- ✅ Branch creation
- ✅ Commit changes
- ✅ PR creation via GitHub API
- ✅ Error handling

**Deliverables**:
- Private repo cloning
- Automated PR creation
- GitHub API integration
- Error recovery

**Validation Criteria**:
- Clone private repo with token
- Execute implementation agent
- Verify PR created with changes
- Verify PR description accurate
- Handle git conflicts gracefully

### Phase 3: Production Readiness (Weeks 5-6)

**Goal**: Security, monitoring, knowledge graph persistence

**Scope**:
- ✅ GitHub App authentication (replace PATs)
- ✅ Request authentication/authorization
- ✅ Knowledge graph persistence (Cloud Storage or SQL)
- ✅ Logging and monitoring
- ✅ Cost optimization
- ✅ Rate limiting

**Deliverables**:
- GitHub App integration
- API key management
- Knowledge graph sync to Cloud Storage
- Cloud Logging integration
- Documentation

**Validation Criteria**:
- GitHub App auth works
- Knowledge graphs persist across requests
- Logs accessible in Cloud Console
- Cost per request measured
- Security audit passes

### Phase 4: Advanced Features (Weeks 7-8+)

**Goal**: Enhanced UX, performance, team features

**Scope**:
- ✅ WebSocket streaming
- ✅ Repo clone caching (Cloud Storage FUSE)
- ✅ Multi-user workspaces
- ✅ Hybrid knowledge graph scoping
- ✅ .claude/ generation API
- ✅ Web UI

**Out of Scope** (for now):
- ❌ Real-time collaboration
- ❌ LangGraph integration
- ❌ Graph database (use Postgres JSON)
- ❌ Custom LLM providers (Anthropic only)

---

## Trade-offs and Design Decisions

### Decision 1: Claude Agent SDK vs. Custom Implementation

**Options Considered**:
1. Build custom agent interpreter
2. Use LangGraph
3. Use Claude Agent SDK ✅

**Decision**: Claude Agent SDK

**Rationale**:
- Eliminates 12-16 weeks of development
- Official, maintained by Anthropic
- Battle-tested (powers Claude Code)
- Automatic .claude/ config loading
- Context management built-in

**Trade-offs**:
- ⚠️ Dependency on Anthropic's SDK
- ⚠️ Limited to Anthropic's design decisions
- ⚠️ SDK is relatively new (potential bugs)

### Decision 2: Ephemeral vs. Persistent Workspaces

**Options Considered**:
1. Persistent workspaces (Cloud Storage FUSE)
2. Ephemeral clones ✅
3. Hybrid (cache in Cloud Storage)

**Decision**: Ephemeral clones for Phase 1-2

**Rationale**:
- Simpler implementation
- Stateless (better for serverless)
- Auto-cleanup (no disk management)
- Lower cost (no persistent storage)

**Trade-offs**:
- ⚠️ Clone latency on every request
- ⚠️ No clone reuse
- ⚠️ Higher bandwidth usage

**Future**: Add Cloud Storage caching in Phase 4

### Decision 3: Git Integration vs. Direct File Access

**Options Considered**:
1. Direct file writes to Cloud Storage
2. Git clone + PR workflow ✅
3. Containerized filesystem per workspace

**Decision**: Git clone + PR workflow

**Rationale**:
- Fits developer workflow (PRs)
- Changes are reviewable
- User controls merge
- Integrates with existing tools

**Trade-offs**:
- ⚠️ Creates PR for every execution (could be noisy)
- ⚠️ Requires GitHub API access
- ⚠️ More complex than direct writes

### Decision 4: In-Memory Volumes vs. Default /tmp

**Options Considered**:
1. Default /tmp (no config)
2. In-memory volumes ✅
3. Cloud Storage FUSE

**Decision**: In-memory volumes (Gen2)

**Rationale**:
- Size limits prevent crashes
- Graceful errors when full
- Still fast (in-memory)
- Production-safe

**Trade-offs**:
- ⚠️ Requires Gen2 (more complex config)
- ⚠️ Size limits require estimation

### Decision 5: Authentication Strategy

**Phase 1**: User-provided GitHub tokens
**Phase 2**: GitHub App installation
**Phase 3**: OAuth + workspace management

**Rationale**: Progressive enhancement
- Phase 1: Simple, works immediately
- Phase 2: Secure, production-ready
- Phase 3: Enterprise-grade

---

## Open Questions

### 1. Knowledge Graph Persistence

**Question**: How should knowledge graphs persist across requests?

**Options**:
- **A**: Include in PR (graphs committed to repo)
  - ✅ Self-contained
  - ❌ PR spam
- **B**: External storage (Cloud Storage/SQL keyed by repo_url)
  - ✅ No PR noise
  - ❌ Separate storage system
- **C**: Hybrid (commit periodically, cache in storage)
  - ✅ Best of both
  - ❌ Most complex

**Current thinking**: Option B for Phase 3

### 2. Multi-User Isolation

**Question**: How to handle multiple users working on same repo?

**Options**:
- **A**: Per-user graphs (isolated)
- **B**: Shared team graphs (collaborative)
- **C**: Hybrid scoping (user/team/global)

**Current thinking**: Option C (hybrid) but needs design work

### 3. Clone Caching Strategy

**Question**: Should we cache clones to avoid re-cloning?

**When to cache**:
- Same repo, same user, within 1 hour?
- Same repo, any user (shared cache)?

**Cache invalidation**:
- Time-based TTL?
- Webhook on repo push?
- User-initiated refresh?

**Current thinking**: Phase 4 feature, needs usage data first

### 4. Cost Management

**Question**: How to prevent abuse and manage costs?

**Concerns**:
- Large repos (>1GB) are expensive to clone
- Long-running agents consume compute
- Anthropic API costs scale with usage

**Mitigations**:
- Rate limiting per user/API key
- Repo size limits (reject >1GB)
- Timeout enforcement (10 min max)
- Usage quotas

**Current thinking**: Implement in Phase 3

### 5. Error Handling Strategy

**Question**: What happens when things fail?

**Failure modes**:
- Repo clone fails (auth, size, timeout)
- Agent execution fails (LLM error, tool error)
- PR creation fails (permissions, conflicts)

**Recovery**:
- Retry logic?
- Partial results?
- Graceful degradation?

**Current thinking**: Fail fast with clear errors, no retries in Phase 1

---

## Success Metrics

### Phase 1 (POC)

- [ ] Successfully clone and execute on 5 different public repos
- [ ] Response time <2 minutes for small repos
- [ ] Zero container crashes
- [ ] .claude/ config loads correctly 100% of time

### Phase 2 (Production)

- [ ] Private repo support working
- [ ] PR creation success rate >95%
- [ ] 10+ active users
- [ ] Cost per execution <$2

### Phase 3 (Scale)

- [ ] 100+ executions/day
- [ ] Knowledge graph persistence working
- [ ] GitHub App auth deployed
- [ ] Monitoring dashboard operational

---

## References

### Documentation

- [Claude Agent SDK](https://docs.claude.com/en/api/agent-sdk/overview)
- [Cloud Run Gen2](https://cloud.google.com/run/docs/about-execution-environments)
- [Cloud Run Volumes](https://cloud.google.com/run/docs/configuring/services/in-memory-volume-mounts)
- [GitHub API - PRs](https://docs.github.com/en/rest/pulls/pulls)

### Related ADRs

- ADR-001: Workflow State Storage Location
- ADR-003: Blocking Mechanism Implementation
- [Future] ADR-XXX: Server-Hosted Execution Environment

### Code References

- Current triads generator: `src/triads/generator/`
- Knowledge graph system: `src/triads/km/`
- Workflow enforcement: `src/triads/workflow_enforcement/`

---

## Appendix: Example Implementation

### Minimal Server (main.py)

```python
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from claude_agent_sdk import query, ClaudeAgentOptions
import subprocess
from pathlib import Path
import shutil
import uuid
import os

app = FastAPI(title="Triads Server", version="0.8.0")

class ExecuteRequest(BaseModel):
    repo_url: str
    prompt: str
    github_token: str | None = None
    triad_config: str = "default"
    base_branch: str = "main"
    create_pr: bool = True

@app.post("/api/v1/execute")
async def execute_triad(
    request: ExecuteRequest,
    background_tasks: BackgroundTasks
):
    request_id = str(uuid.uuid4())
    workspace = Path(f"/workspaces/{request_id}")

    try:
        # 1. Clone repo
        workspace.mkdir(parents=True, exist_ok=True)
        clone_repo(request.repo_url, workspace, request.github_token)

        # 2. Inject .claude/ if needed
        if not (workspace / ".claude").exists():
            inject_claude_config(workspace, request.triad_config)

        # 3. Execute with Claude Agent SDK
        options = ClaudeAgentOptions(
            setting_sources=["project"],
            cwd=str(workspace),
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            allowed_tools=["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
        )

        messages = []
        async for msg in query(request.prompt, options):
            messages.append({"type": msg.type, "content": msg.content})

        # 4. Create PR if changes
        pr_url = None
        if has_changes(workspace) and request.create_pr:
            pr_url = create_pull_request(
                workspace, request.repo_url,
                request.github_token, request_id
            )

        return {
            "status": "success",
            "request_id": request_id,
            "pr_url": pr_url,
            "messages": messages
        }

    finally:
        background_tasks.add_task(shutil.rmtree, workspace, ignore_errors=True)

def clone_repo(url: str, dest: Path, token: str | None):
    auth_url = url.replace("https://", f"https://{token}@") if token else url
    subprocess.run(
        ["git", "clone", "--depth", "1", auth_url, str(dest)],
        check=True, capture_output=True
    )

def inject_claude_config(workspace: Path, config: str):
    # Copy bundled template or generate
    template = Path(f"/app/triad-templates/{config}")
    if template.exists():
        shutil.copytree(template, workspace / ".claude")

def has_changes(workspace: Path) -> bool:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=workspace, capture_output=True, text=True
    )
    return bool(result.stdout.strip())

def create_pull_request(
    workspace: Path, repo_url: str, token: str, branch: str
) -> str:
    # Create branch, commit, push, create PR via GitHub API
    # Implementation omitted for brevity
    pass
```

---

**End of Design Document**

This design serves as the foundation for implementing server-hosted triads. Implementation will follow the phased approach, with each phase building on the previous one while maintaining the core architectural principles.
