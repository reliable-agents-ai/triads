# Military Organizational Patterns for Triad Architecture

**Research Date**: 2025-10-20
**Purpose**: Document military organizational principles that inform the Supervisor-first multi-workflow triad architecture
**Status**: Reference Documentation

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Military Squad Organization (9 Soldiers)](#military-squad-organization-9-soldiers)
3. [Special Forces ODA (12 Soldiers)](#special-forces-oda-12-soldiers)
4. [Military Task Organization Doctrine](#military-task-organization-doctrine)
5. [Optimal Team Size Research](#optimal-team-size-research)
6. [Mapping to Triad Architecture](#mapping-to-triad-architecture)
7. [Architectural Implications](#architectural-implications)
8. [References](#references)

---

## Executive Summary

This document captures military organizational research that informed the design of the Supervisor-first multi-workflow architecture. Key findings:

- **Optimal team size**: 9-12 personnel for task-focused operations
- **Atomic unit principle**: Fire teams (4 soldiers) never decomposed → Triads (3 agents) never decomposed
- **Coordination role**: Squad leader coordinates but doesn't execute → Supervisor routes but doesn't implement
- **Task organization**: Intact units composed for mission-specific needs → Atomic triads composed into workflows

These patterns provide battle-tested organizational principles that directly map to software development workflows.

---

## Military Squad Organization (9 Soldiers)

### Structure

```
Squad (9 soldiers)
├── Fire Team Alpha (4 soldiers)
│   ├── Team Leader
│   ├── Automatic Rifleman
│   ├── Grenadier
│   └── Rifleman
├── Fire Team Bravo (4 soldiers)
│   ├── Team Leader
│   ├── Automatic Rifleman
│   ├── Grenadier
│   └── Rifleman
└── Squad Leader (1 soldier)
```

### Key Principles

1. **Fire Team Atomicity**
   - Fire teams are the smallest tactical unit
   - Never decomposed into individual soldiers for task assignment
   - Each fire team has internal coherence and balanced capabilities
   - Teams work internally to complete assigned objectives

2. **Squad Leader Role**
   - Coordinates between fire teams
   - Makes tactical decisions
   - Communicates with higher command
   - Does NOT execute fire team actions directly
   - Maintains situational awareness across all teams

3. **Operational Characteristics**
   - Fire teams can operate semi-independently
   - Clear handoff points between team objectives
   - Squad leader monitors progress and adapts plan
   - Proven in combat operations across multiple conflicts

### Mapping to Triads

| Military Concept | Triad Architecture |
|-----------------|-------------------|
| Fire Team (4) | Triad (3 agents) |
| Squad Leader | Supervisor Agent |
| Fire Team atomicity | Triad atomicity principle |
| Squad coordination | Workflow orchestration |
| 9 soldiers total | 3 triads + Supervisor |

**Workflow Pattern**: Bug fix, performance optimization, refactoring workflows (9 agents)

---

## Special Forces ODA (12 Soldiers)

### Structure

```
ODA Team (12 soldiers)
├── Detachment Commander (Officer)
├── Detachment Technician (Warrant Officer)
├── Operations Sergeant (Team Sergeant)
├── Assistant Operations Sergeant
├── Intelligence Sergeant × 2 (paired)
├── Weapons Sergeant × 2 (paired)
├── Engineer Sergeant × 2 (paired)
├── Medical Sergeant × 2 (paired)
└── Communications Sergeant × 2 (paired)
```

### Key Principles

1. **Paired Specialists**
   - Each specialty has 2 personnel
   - Enables team split into 2×6-person elements
   - Maintains capability in both elements
   - Redundancy for critical functions

2. **Complex Operations**
   - Handles multi-phase missions
   - Can execute split operations simultaneously
   - Higher specialization than standard squads
   - Self-sufficient for extended periods

3. **Command Structure**
   - Commander coordinates overall mission
   - Team Sergeant manages operations
   - Specialists work in their domains
   - Clear authority and responsibility

### Mapping to Triads

| Military Concept | Triad Architecture |
|-----------------|-------------------|
| ODA (12) | 4 triads + Supervisor |
| Paired specialists | Triad specialization |
| Split operations | Sequential triad execution |
| Self-sufficiency | Complete workflow autonomy |

**Workflow Pattern**: Full feature development (idea-validation → design → implementation → garden-tending)

---

## Military Task Organization Doctrine

### Core Principle

**Task organization** is the practice of composing intact units into mission-specific configurations without decomposing them into individual components.

### Doctrine Elements

1. **Unit Integrity**
   - Units maintain their internal structure
   - No decomposition into sub-unit components
   - Same unit used in different task organizations
   - Unit coherence preserved across missions

2. **Mission-Specific Composition**
   - Different missions require different unit combinations
   - Units selected based on mission requirements
   - Composition changes, units don't
   - Proven patterns for common mission types

3. **Command Relationships**
   - Clear authority for each unit
   - Coordinated by task force commander
   - Units report completion and status
   - Handoffs between sequential phases

### Examples

**Assault Mission**:
- 2× Infantry Squads (fire and maneuver)
- 1× Weapons Squad (support)
- 1× Engineer Squad (breach)

**Reconnaissance Mission**:
- 1× Scout Squad (recon)
- 1× Sniper Team (overwatch)

**Defense Mission**:
- 3× Infantry Squads (positions)
- 1× Weapons Squad (heavy fire)
- 1× Mortar Section (indirect fire)

### Mapping to Workflows

| Military Concept | Triad Architecture |
|-----------------|-------------------|
| Task organization | Workflow composition |
| Unit integrity | Triad atomicity |
| Mission types | Problem types (bug, feature, etc.) |
| Unit combinations | Triad sequences |
| Commander coordination | Supervisor routing |

**Key Insight**: Same triads used in different workflows, just like same squads used in different task organizations.

---

## Optimal Team Size Research

### Military Research Findings

Across multiple militaries and historical periods, task-focused teams consistently optimize around 9-12 personnel.

#### Below 9 Personnel
- ❌ Insufficient capability diversity
- ❌ Single point of failure for specialties
- ❌ Difficulty sustaining operations (no rest rotation)
- ❌ Limited operational flexibility

#### 9-12 Personnel (Sweet Spot)
- ✅ Sufficient specialization
- ✅ Manageable coordination overhead
- ✅ Operational resilience (redundancy)
- ✅ Effective communication (everyone knows everyone)
- ✅ Can split into sub-elements if needed

#### Above 12 Personnel
- ❌ Coordination overhead increases exponentially
- ❌ Communication becomes difficult
- ❌ Requires hierarchical sub-structure
- ❌ Loss of cohesion and situational awareness

### Supporting Research

1. **Historical Evidence**
   - Roman contubernium: 8 soldiers
   - Medieval lance: 10-12 soldiers
   - Modern squad: 9-13 soldiers (varies by nation)
   - Special forces team: 12 soldiers

2. **Organizational Psychology**
   - Dunbar's number derivatives
   - Communication channel growth: n(n-1)/2
   - Coordination complexity increases superlinearly
   - Trust and cohesion degrade above ~15

3. **Combat Operations Research**
   - Small unit actions analysis
   - Mission success rates by team size
   - Casualty rates and team effectiveness
   - Decision-making speed vs. team size

### Mapping to Workflows

**Workflow Size Recommendations**:

- **2 triads (6 agents)**: Investigation, quick fixes
  - Minimal but sufficient
  - Fast execution
  - Limited scope problems

- **3 triads (9 agents)**: Bug fix, performance, refactoring
  - Matches military squad
  - Balanced capability and coordination
  - Most common workflow size

- **4 triads (12 agents)**: Feature development
  - Matches Special Forces ODA
  - Complex multi-phase operations
  - Idea → Design → Implementation → Garden Tending

- **5 triads (15 agents)**: Upper limit
  - Complex features with deployment
  - Coordination overhead starts increasing
  - Should be rare

---

## Mapping to Triad Architecture

### Direct Parallels

| Military | Triad System | Rationale |
|----------|-------------|-----------|
| Fire team | Triad | Atomic unit, never decomposed |
| Squad leader | Supervisor | Coordinates, doesn't execute |
| Squad (9) | 3 triads + Supervisor | Standard workflow size |
| ODA (12) | 4 triads + Supervisor | Complex workflow size |
| Task organization | Workflow composition | Mission-specific unit combinations |
| Unit integrity | Triad atomicity | Same unit/triad in multiple contexts |
| Mission types | Problem types | Different problems need different workflows |

### Architectural Decisions Informed

1. **Triad Atomicity Principle** (ADR-006)
   - Inspired by: Fire team atomicity
   - Decision: Triads never decomposed
   - Rationale: Maintains internal coherence, proven pattern

2. **Supervisor Role Definition**
   - Inspired by: Squad leader coordination role
   - Decision: Supervisor routes, doesn't execute
   - Rationale: Separation of coordination and execution

3. **Workflow Size Ranges**
   - Inspired by: 9-12 optimal team size
   - Decision: 2-5 triads per workflow (6-15 agents)
   - Rationale: Matches proven organizational patterns

4. **Workflow Library Approach**
   - Inspired by: Task organization doctrine
   - Decision: Predefined workflows + generation capability
   - Rationale: Common patterns + flexibility for novel problems

5. **Sequential Execution**
   - Inspired by: Phase-based military operations
   - Decision: Triads execute sequentially with handoffs
   - Rationale: Clear coordination, manageable complexity

---

## Architectural Implications

### 1. Triad Design

**DO**:
- Design triads as self-contained 3-agent units
- Give each triad clear, complete responsibility
- Ensure internal agent coherence
- Design for reusability across workflows

**DON'T**:
- Extract individual agents for reassignment
- Create dependencies on external agents
- Design triads expecting decomposition
- Make triads too specialized (limits reuse)

### 2. Workflow Design

**DO**:
- Compose workflows from intact triads
- Define clear handoff points between triads
- Use proven patterns for common problems
- Keep workflows 2-5 triads when possible

**DON'T**:
- Decompose triads into individual agents
- Create workflows >5 triads (coordination overhead)
- Skip handoff documentation
- Reinvent wheels (use proven patterns first)

### 3. Supervisor Design

**DO**:
- Handle all user interaction (Q&A and routing)
- Monitor workflow execution
- Learn from outcomes
- Maintain emergency bypass capability

**DON'T**:
- Execute work directly (that's what triads do)
- Micromanage internal triad operations
- Block users from direct access (allow `/direct`)
- Require Supervisor for every operation (allow fallback)

### 4. Context Handoffs

**DO**:
- Define standard handoff format
- Include all context needed for next triad
- Preserve decision rationale
- Document assumptions and constraints

**DON'T**:
- Assume next triad has implicit knowledge
- Pass incomplete context
- Skip handoff validation
- Lose information between triads

---

## References

### Military Doctrine

1. **U.S. Army FM 3-0 (Operations)**
   - Task organization principles
   - Unit integrity doctrine
   - Command relationships

2. **U.S. Army Infantry Squad Field Manuals**
   - Squad organization
   - Fire team structure and roles
   - Small unit tactics

3. **U.S. Army Special Forces Doctrine**
   - ODA organization
   - Paired specialist model
   - Split team operations

4. **NATO Standardization Agreements (STANAGs)**
   - International military organization patterns
   - Cross-nation team size consistency

### Organizational Research

1. **Dunbar, R. (1992)**
   - "Neocortex size as a constraint on group size in primates"
   - Cognitive limits on social group size

2. **Hackman, J.R. (2002)**
   - "Leading Teams: Setting the Stage for Great Performances"
   - Team size and effectiveness research

3. **Military Small Unit Operations Research**
   - Historical analysis of team sizes across cultures
   - Combat effectiveness by unit size
   - Coordination overhead studies

### Triad System Context

- **User Requirement (2025-10-20)**: "triads themselves are atomic, they should not be decomposed, they should work within themselves until they're complete, then hand off to another set of agents in a triad"
- **Design ADR-006**: Triad Atomicity Principle
- **Supervisor Architecture ADR**: docs/adrs/ADR-SUPERVISOR-ARCHITECTURE.md

---

## Document History

- **2025-10-20**: Initial documentation (Phase 0 of Supervisor implementation)
- Research findings documented in `.claude/graphs/design_graph.json` (nodes: military_squad_organization, military_oda_organization, military_task_organization_doctrine, optimal_team_size_finding, triad_atomicity_principle)

---

**Next Steps**: See ADR-SUPERVISOR-ARCHITECTURE.md for architectural decisions based on these patterns.
