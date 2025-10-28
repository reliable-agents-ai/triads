# Idea Validation Workflow - Context Memory

**Workflow**: Idea Validation
**Domain**: {{DOMAIN_TYPE}}
**Started**: {{START_DATE}}
**Status**: {{STATUS}}

This file captures context for idea validation workflows, ensuring continuity across validation-analyst → community-researcher → validation-synthesizer.

---

## 🎯 WORKFLOW PURPOSE

**Objective**: Validate feature ideas by researching community need, gathering evidence, and making PROCEED/DEFER/REJECT decisions.

**Success Criteria**:
- [ ] Community need quantified with evidence
- [ ] Technical feasibility assessed
- [ ] Priority score calculated (0-100)
- [ ] Clear decision made (PROCEED/DEFER/REJECT)
- [ ] Reasoning documented with citations

---

## 📊 IDEA BEING VALIDATED

### Core Idea

```yaml
idea:
  name: "{{IDEA_NAME}}"
  description: |
    {{IDEA_DESCRIPTION}}

  proposed_by: "{{PROPOSER}}"
  proposed_date: "{{PROPOSAL_DATE}}"

  category: "{{CATEGORY}}"  # feature | enhancement | fix | optimization

  problem_statement: |
    {{WHAT_PROBLEM_DOES_THIS_SOLVE}}

  proposed_solution: |
    {{HOW_WOULD_THIS_SOLVE_IT}}
```

**Example**:
```yaml
idea:
  name: "AI-powered code suggestions"
  description: |
    Add AI-powered code completion and suggestions to the editor,
    similar to GitHub Copilot but integrated with project context.

  proposed_by: "User"
  proposed_date: "2024-10-27"

  category: "feature"

  problem_statement: |
    Developers spend significant time writing boilerplate code and
    looking up API documentation. Context-aware suggestions could
    significantly improve productivity.

  proposed_solution: |
    Integrate an LLM (Claude or GPT-4) to provide inline code suggestions
    based on:
    - Current file context
    - Project structure and dependencies
    - Recent code patterns
    - Documentation and comments
```

---

## 📋 VALIDATION AGENT WORK

### Research Questions

**Questions to Answer**:
1. Is this a real problem? (Evidence of pain points)
2. How big is the problem? (Quantify impact)
3. Are users asking for this? (Community demand)
4. Do alternatives exist? (Competitive analysis)
5. Is this technically feasible? (Technical assessment)

### Research Conducted

```yaml
research:
  - method: "{{METHOD}}"  # web_search | github_issues | discussions | documentation
    query: "{{SEARCH_QUERY}}"
    date: "{{DATE}}"
    findings: |
      {{FINDINGS}}
    evidence_quality: "{{TIER}}"  # Tier 1-5
    confidence: "{{CONFIDENCE}}"  # 0-100%

  - method: "{{METHOD}}"
    query: "{{SEARCH_QUERY}}"
    date: "{{DATE}}"
    findings: |
      {{FINDINGS}}
    evidence_quality: "{{TIER}}"
    confidence: "{{CONFIDENCE}}"
```

**Example**:
```yaml
research:
  - method: "web_search"
    query: "AI code completion tools adoption rates"
    date: "2024-10-27"
    findings: |
      - GitHub Copilot: 1M+ users (GitHub blog, 2023)
      - Tabnine: 500K+ active users (Tabnine website, 2024)
      - Growing market: 35% CAGR (Gartner, 2024)
    evidence_quality: "Tier 2"  # Public data, reputable sources
    confidence: "85%"

  - method: "github_issues"
    query: "code completion feature requests in similar projects"
    date: "2024-10-27"
    findings: |
      - VS Code: 1,500+ issues mentioning "autocomplete" or "suggestions"
      - JetBrains: 800+ feature requests for AI assistance
      - High demand signals from developer community
    evidence_quality: "Tier 1"  # Direct observation
    confidence: "95%"
```

### Key Findings

```yaml
findings:
  - finding_id: "F001"
    category: "{{CATEGORY}}"  # problem_validation | demand | feasibility | competition
    description: |
      {{FINDING_DESCRIPTION}}
    evidence: |
      {{EVIDENCE_WITH_CITATIONS}}
    confidence: "{{CONFIDENCE}}"
    impact: "{{IMPACT}}"  # high | medium | low

  - finding_id: "F002"
    category: "{{CATEGORY}}"
    description: |
      {{FINDING_DESCRIPTION}}"
    evidence: |
      {{EVIDENCE}}"
    confidence: "{{CONFIDENCE}}"
    impact: "{{IMPACT}}"
```

---

## 📋 COMMUNITY RESEARCHER WORK

### Community Evidence

```yaml
community_evidence:
  github_issues:
    total_searched: {{COUNT}}
    relevant_issues: {{COUNT}}
    top_issues:
      - url: "{{URL}}"
        title: "{{TITLE}}"
        reactions: {{COUNT}}  # thumbs up
        comments: {{COUNT}}
        created: "{{DATE}}"
        excerpt: |
          {{RELEVANT_EXCERPT}}

  discussions:
    total_searched: {{COUNT}}
    relevant_discussions: {{COUNT}}
    top_discussions:
      - url: "{{URL}}"
        title: "{{TITLE}}"
        upvotes: {{COUNT}}
        replies: {{COUNT}}
        created: "{{DATE}}"
        excerpt: |
          {{RELEVANT_EXCERPT}}

  stack_overflow:
    total_searched: {{COUNT}}
    relevant_questions: {{COUNT}}
    top_questions:
      - url: "{{URL}}"
        title: "{{TITLE}}"
        views: {{COUNT}}
        score: {{COUNT}}
        answers: {{COUNT}}
        excerpt: |
          {{RELEVANT_EXCERPT}}
```

**Example**:
```yaml
community_evidence:
  github_issues:
    total_searched: 50
    relevant_issues: 12
    top_issues:
      - url: "https://github.com/microsoft/vscode/issues/12345"
        title: "Feature request: AI-powered code completion"
        reactions: 450
        comments: 78
        created: "2023-06-15"
        excerpt: |
          "As a developer, I spend too much time writing boilerplate.
          AI suggestions would save hours per week."

  discussions:
    total_searched: 30
    relevant_discussions: 8
    top_discussions:
      - url: "https://github.com/community/discussions/54321"
        title: "What features would make you more productive?"
        upvotes: 320
        replies: 145
        created: "2024-01-20"
        excerpt: |
          "Top request: Intelligent code completion that understands
          project context, not just syntax."
```

### User Pain Points

```yaml
pain_points:
  - pain_point: "{{DESCRIPTION}}"
    frequency: "{{COUNT}} mentions"
    severity: "{{HIGH/MEDIUM/LOW}}"
    evidence: |
      {{CITATIONS}}

  - pain_point: "{{DESCRIPTION}}"
    frequency: "{{COUNT}} mentions"
    severity: "{{SEVERITY}}"
    evidence: |
      {{CITATIONS}}
```

**Example**:
```yaml
pain_points:
  - pain_point: "Time spent on boilerplate code"
    frequency: "23 mentions across issues and discussions"
    severity: "HIGH"
    evidence: |
      - "Spend 30% of time on repetitive code" (Issue #12345, 450 👍)
      - "Boilerplate is biggest productivity killer" (Discussion #54321, 320 ⬆️)
      - "Would pay for tool that reduces boilerplate" (StackOverflow, 2.3K views)

  - pain_point: "Context switching to documentation"
    frequency: "18 mentions"
    severity: "MEDIUM"
    evidence: |
      - "Constantly switching between code and docs" (Issue #23456, 280 👍)
      - "Documentation lookup breaks flow state" (Discussion #65432, 190 ⬆️)
```

---

## 📋 VALIDATION SYNTHESIZER WORK

### Priority Score Calculation

```yaml
priority_scoring:
  # Community Need (0-30 points)
  community_need:
    github_reactions: {{COUNT}}  # ≥100 = 10pts, ≥50 = 5pts, <50 = 0pts
    discussion_engagement: {{COUNT}}  # ≥100 = 10pts, ≥50 = 5pts, <50 = 0pts
    pain_point_severity: "{{SEVERITY}}"  # HIGH = 10pts, MED = 5pts, LOW = 0pts
    subtotal: {{POINTS}} / 30

  # Technical Feasibility (0-25 points)
  technical_feasibility:
    complexity: "{{COMPLEXITY}}"  # Low = 15pts, Med = 10pts, High = 5pts
    dependencies: "{{DEPENDENCIES}}"  # None = 10pts, Few = 5pts, Many = 0pts
    subtotal: {{POINTS}} / 25

  # Strategic Alignment (0-25 points)
  strategic_alignment:
    roadmap_fit: "{{FIT}}"  # Perfect = 15pts, Good = 10pts, Neutral = 5pts, Poor = 0pts
    user_segment: "{{SEGMENT}}"  # Core = 10pts, Important = 5pts, Niche = 0pts
    subtotal: {{POINTS}} / 25

  # Competitive Advantage (0-20 points)
  competitive_advantage:
    differentiation: "{{LEVEL}}"  # Unique = 15pts, Better = 10pts, Parity = 5pts, Behind = 0pts
    market_gap: "{{GAP}}"  # Yes = 5pts, No = 0pts
    subtotal: {{POINTS}} / 20

  # TOTAL SCORE: {{TOTAL}} / 100
```

**Example**:
```yaml
priority_scoring:
  # Community Need (0-30 points)
  community_need:
    github_reactions: 450  # ≥100 = 10pts
    discussion_engagement: 320  # ≥100 = 10pts
    pain_point_severity: "HIGH"  # HIGH = 10pts
    subtotal: 30 / 30

  # Technical Feasibility (0-25 points)
  technical_feasibility:
    complexity: "Medium"  # Med = 10pts
    dependencies: "Claude API (existing)"  # Few = 5pts
    subtotal: 15 / 25

  # Strategic Alignment (0-25 points)
  strategic_alignment:
    roadmap_fit: "Perfect"  # Aligns with AI-first strategy = 15pts
    user_segment: "Core"  # All developers = 10pts
    subtotal: 25 / 25

  # Competitive Advantage (0-20 points)
  competitive_advantage:
    differentiation: "Better"  # Project-aware (vs generic Copilot) = 10pts
    market_gap: "Yes"  # No project-aware AI completion exists = 5pts
    subtotal: 15 / 20

  # TOTAL SCORE: 85 / 100
```

### Decision

```yaml
decision:
  outcome: "{{PROCEED|DEFER|REJECT}}"
  confidence: "{{CONFIDENCE}}"  # 0-100%

  reasoning: |
    {{DETAILED_REASONING}}

  conditions:  # If PROCEED or DEFER
    - "{{CONDITION_1}}"
    - "{{CONDITION_2}}"

  next_steps:
    - action: "{{ACTION}}"
      owner: "{{AGENT/USER}}"
      deadline: "{{DATE}}"
```

**Example - PROCEED**:
```yaml
decision:
  outcome: "PROCEED"
  confidence: "90%"

  reasoning: |
    **Community Need**: Extremely strong (30/30 points)
    - 450+ GitHub reactions, 320+ discussion upvotes
    - HIGH severity pain point (23 mentions of "time spent on boilerplate")
    - Clear demand signal from developer community

    **Technical Feasibility**: Moderate (15/25 points)
    - Medium complexity (LLM integration well-understood)
    - Existing Claude API dependency reduces risk
    - Similar implementations exist (Copilot, Tabnine) proving feasibility

    **Strategic Alignment**: Perfect (25/25 points)
    - Aligns with AI-first product strategy
    - Serves core user segment (all developers)
    - Differentiates from existing tools with project awareness

    **Competitive Advantage**: Strong (15/20 points)
    - Better than generic Copilot (project-aware suggestions)
    - Fills market gap (no project-aware AI completion exists)

    **Total Score**: 85/100 → PROCEED threshold (≥70)

  conditions:
    - "Must maintain 90%+ test coverage during implementation"
    - "Must not slow down editor (< 100ms latency requirement)"
    - "Must respect user privacy (local processing preferred)"

  next_steps:
    - action: "Design architecture for AI suggestions system"
      owner: "Design Triad (solution-architect)"
      deadline: "2024-11-03"
    - action: "Create ADR for LLM selection (Claude vs GPT-4)"
      owner: "Design Triad (solution-architect)"
      deadline: "2024-11-03"
    - action: "Prototype basic completion endpoint"
      owner: "Implementation Triad (senior-developer)"
      deadline: "2024-11-10"
```

**Example - DEFER**:
```yaml
decision:
  outcome: "DEFER"
  confidence: "85%"

  reasoning: |
    **Community Need**: Moderate (15/30 points)
    - Only 30 GitHub reactions, limited discussion engagement
    - LOW severity pain point (only 3 mentions)
    - Nice-to-have, not critical

    **Technical Feasibility**: Low (5/25 points)
    - High complexity (requires major refactor)
    - Many external dependencies (3 new services)
    - No similar implementations to reference

    **Strategic Alignment**: Poor (5/25 points)
    - Does not align with current roadmap
    - Serves niche user segment (<5% of users)

    **Competitive Advantage**: None (0/20 points)
    - Already solved by existing tools
    - No differentiation opportunity

    **Total Score**: 25/100 → DEFER threshold (<40)

    **Recommendation**: Defer until Q2 2025 after core features complete.

  conditions:
    - "Re-evaluate if community demand increases (>100 reactions)"
    - "Re-evaluate if strategic priority changes"
    - "Consider again after Q1 2025 roadmap completion"

  next_steps:
    - action: "Add to backlog for Q2 2025 consideration"
      owner: "Product Owner"
      deadline: "2024-11-01"
    - action: "Monitor community demand (set alert for >100 reactions)"
      owner: "Community Researcher"
      deadline: "Ongoing"
```

**Example - REJECT**:
```yaml
decision:
  outcome: "REJECT"
  confidence: "95%"

  reasoning: |
    **Community Need**: None (0/30 points)
    - Zero GitHub reactions or discussion engagement
    - No evidence of pain point
    - No user demand

    **Technical Feasibility**: Infeasible (0/25 points)
    - Requires technology that doesn't exist yet
    - Would break core functionality
    - No path to implementation

    **Strategic Alignment**: Misaligned (0/25 points)
    - Contradicts product vision
    - Serves no user segment
    - Diverts resources from strategic goals

    **Competitive Advantage**: Negative (0/20 points)
    - Puts us behind competitors
    - Creates technical debt
    - No market demand

    **Total Score**: 0/100 → REJECT threshold (<20)

    **Recommendation**: Reject permanently. No conditions for reconsideration.

  conditions: []  # No conditions - rejected outright

  next_steps:
    - action: "Document rejection reasoning for future reference"
      owner: "Validation Synthesizer"
      deadline: "2024-10-27"
    - action: "Close related GitHub issues with explanation"
      owner: "Product Owner"
      deadline: "2024-10-28"
```

---

## 📊 KNOWLEDGE GRAPH UPDATES

### Nodes Created

```yaml
knowledge_nodes:
  - node_id: "{{NODE_ID}}"
    node_type: "{{TYPE}}"  # Finding | Decision | Requirement | Uncertainty
    label: "{{LABEL}}"
    description: |
      {{DESCRIPTION}}
    confidence: {{CONFIDENCE}}
    evidence: |
      {{EVIDENCE}}
    created_by: "{{AGENT_NAME}}"
    created_at: "{{TIMESTAMP}}"

  - node_id: "{{NODE_ID}}"
    node_type: "{{TYPE}}"
    label: "{{LABEL}}"
    description: |
      {{DESCRIPTION}}
    confidence: {{CONFIDENCE}}
    evidence: |
      {{EVIDENCE}}
    created_by: "{{AGENT_NAME}}"
    created_at: "{{TIMESTAMP}}"
```

---

## 🔗 HANDOFF TO DESIGN TRIAD

### Context Summary

```yaml
handoff:
  decision: "{{PROCEED|DEFER|REJECT}}"
  priority_score: {{SCORE}} / 100

  key_findings:
    - "{{FINDING_1}}"
    - "{{FINDING_2}}"
    - "{{FINDING_3}}"

  critical_requirements:
    - "{{REQUIREMENT_1}}"
    - "{{REQUIREMENT_2}}"

  constraints:
    - "{{CONSTRAINT_1}}"
    - "{{CONSTRAINT_2}}"

  questions_for_design:
    - "{{QUESTION_1}}"
    - "{{QUESTION_2}}"

  recommended_next_steps:
    - "{{STEP_1}}"
    - "{{STEP_2}}"
```

**Example**:
```yaml
handoff:
  decision: "PROCEED"
  priority_score: 85 / 100

  key_findings:
    - "Strong community demand (450+ reactions, 23 pain point mentions)"
    - "Technical feasibility confirmed (similar to existing Copilot/Tabnine implementations)"
    - "Strategic fit: Aligns with AI-first product vision"
    - "Competitive advantage: Project-aware suggestions (vs generic Copilot)"

  critical_requirements:
    - "Latency: <100ms for suggestions (user expectation from research)"
    - "Privacy: Local processing preferred (15 mentions of privacy concerns)"
    - "Accuracy: ≥70% acceptance rate (benchmark from Copilot data)"
    - "Test coverage: ≥90% (maintain project standard)"

  constraints:
    - "Must use existing Claude API (no new dependencies)"
    - "Must not slow down editor (<100ms latency requirement)"
    - "Budget: Maximum $50/month per user for API costs"

  questions_for_design:
    - "Which LLM? Claude 3.5 Sonnet vs GPT-4 (cost vs quality tradeoff)"
    - "Architecture: Client-side processing vs server-side? (latency vs privacy)"
    - "Context window: How much project context to include? (quality vs token cost)"
    - "Caching strategy: Cache embeddings or re-process each time?"

  recommended_next_steps:
    - "Create ADR for LLM selection (Claude vs GPT-4)"
    - "Design system architecture (client vs server processing)"
    - "Define API contract for suggestions endpoint"
    - "Prototype basic completion with 10-file context window"
```

---

## 🚨 ISSUES AND UNCERTAINTIES

### Unresolved Questions

```yaml
uncertainties:
  - question: "{{QUESTION}}"
    confidence: "{{CONFIDENCE}}"  # <90% = needs resolution
    impact: "{{IMPACT}}"  # blocks_design | blocks_implementation | informational
    research_needed: |
      {{WHAT_RESEARCH_WOULD_RESOLVE_THIS}}

  - question: "{{QUESTION}}"
    confidence: "{{CONFIDENCE}}"
    impact: "{{IMPACT}}"
    research_needed: |
      {{RESEARCH_NEEDED}}
```

**Example**:
```yaml
uncertainties:
  - question: "Will Claude API costs be sustainable at scale?"
    confidence: "65%"  # Below 90% threshold
    impact: "blocks_implementation"
    research_needed: |
      - Get Claude API pricing for high-volume usage
      - Calculate cost per suggestion (tokens used)
      - Benchmark against Copilot pricing ($10/month)
      - Determine if caching/optimization can reduce costs

  - question: "Do users want inline suggestions or sidebar suggestions?"
    confidence: "75%"
    impact: "blocks_design"
    research_needed: |
      - Survey 20 target users on preference
      - Run A/B test with prototype
      - Review Copilot vs Tabnine UX patterns
```

---

## 📋 CONSTITUTIONAL COMPLIANCE

### Evidence Quality Audit

```yaml
evidence_audit:
  total_claims: {{COUNT}}
  tier_1_evidence: {{COUNT}}  # Direct observation, primary sources
  tier_2_evidence: {{COUNT}}  # Reputable secondary sources
  tier_3_evidence: {{COUNT}}  # Estimates, calculations
  tier_4_evidence: {{COUNT}}  # Unverified claims
  tier_5_evidence: {{COUNT}}  # Speculation

  minimum_confidence: {{PERCENTAGE}}%  # Should be ≥85%
  average_confidence: {{PERCENTAGE}}%

  verification_methods:
    single_source: {{COUNT}}
    multi_method: {{COUNT}}  # Should be majority
```

### Assumptions Validated

```yaml
assumptions:
  - assumption: "{{STATEMENT}}"
    validation: "{{HOW_VALIDATED}}"
    status: "✅ VERIFIED | ⚠️ UNVERIFIED | ❌ INVALID"
    confidence: "{{CONFIDENCE}}"

  - assumption: "{{STATEMENT}}"
    validation: "{{HOW_VALIDATED}}"
    status: "{{STATUS}}"
    confidence: "{{CONFIDENCE}}"
```

---

## 📚 RESOURCES

### Research Sources

```yaml
sources:
  - title: "{{TITLE}}"
    url: "{{URL}}"
    type: "{{TYPE}}"  # documentation | github_issue | discussion | article | paper
    accessed: "{{DATE}}"
    relevance: "{{RELEVANCE}}"  # high | medium | low
    notes: |
      {{NOTES}}

  - title: "{{TITLE}}"
    url: "{{URL}}"
    type: "{{TYPE}}"
    accessed: "{{DATE}}"
    relevance: "{{RELEVANCE}}"
    notes: |
      {{NOTES}}
```

---

## 🎯 SUCCESS METRICS

```yaml
success_metrics:
  validation_complete:
    - criterion: "Community need quantified"
      status: "{{✅ COMPLETE | ⏳ IN PROGRESS | ❌ NOT STARTED}}"
    - criterion: "Technical feasibility assessed"
      status: "{{STATUS}}"
    - criterion: "Priority score calculated"
      status: "{{STATUS}}"
    - criterion: "Decision made (PROCEED/DEFER/REJECT)"
      status: "{{STATUS}}"
    - criterion: "Evidence meets constitutional standards"
      status: "{{STATUS}}"

  quality_gates:
    - gate: "All findings have ≥85% confidence"
      status: "{{✅ PASSED | ❌ FAILED}}"
    - gate: "All claims have Tier 1-3 evidence"
      status: "{{STATUS}}"
    - gate: "Decision reasoning documented with citations"
      status: "{{STATUS}}"
```

---

*This context memory ensures continuity and quality across the Idea Validation workflow.*

**Template Version**: v1.0.0
**Last Updated**: {{LAST_UPDATED}}
