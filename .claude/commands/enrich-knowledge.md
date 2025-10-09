---
description: Manually enrich sparse entities in knowledge graphs
---

# Enrich Knowledge Command

You are manually enriching sparse entities in the knowledge graph system.

## Your Task

1. **Load KM Queue**: Read `.claude/km_queue.json` to find sparse entities
2. **Select Target**: Either:
   - Use entity specified by user (if they provided node_id or label)
   - Show user the list of sparse entities and ask which to enrich
3. **Research and Enrich**: Act as the research-agent
4. **Output [GRAPH_UPDATE]**: Update the node with enriched properties

## Process

### Step 1: Load and Display Sparse Entities

```
Reading .claude/km_queue.json...

Found 3 sparse entities:

1. **PyJWT Library** (`pyjwt_lib`) in discovery triad
   - Current properties: 1
   - Needs: Research on JWT library capabilities

2. **Redis Cache** (`redis_cache`) in discovery triad
   - Current properties: 2
   - Needs: Configuration and usage details

3. **Microservices Pattern** (`microservices_concept`) in design triad
   - Current properties: 1
   - Needs: Definition, trade-offs, best practices

Which would you like me to enrich? (Enter number or node_id, or "all")
```

### Step 2: Research

Follow research-agent guidelines (see `.claude/agents/system/research-agent.md`):

1. **Understand Context**: Check which triad, read current properties
2. **Gather Information**:
   - For code entities: Use Grep/Read tools to find implementation
   - For concepts: Web search for authoritative sources
   - For tools: Official docs, package info
3. **Extract Properties**: Find 3+ meaningful properties
4. **Cite Evidence**: Specific file:line, URLs, commit hashes

### Step 3: Output [GRAPH_UPDATE]

```
[GRAPH_UPDATE]
type: update_node
node_id: {entity_id}
properties: {
  "property1": "value1",
  "property2": "value2",
  "property3": "value3",
  ...
}
confidence: 0.95
evidence: {detailed_evidence_with_citations}
[/GRAPH_UPDATE]
```

### Step 4: Verify Enrichment

After outputting [GRAPH_UPDATE]:
- Confirm the entity now has 3+ meaningful properties
- Verify evidence is comprehensive
- Note that the entity will be removed from km_queue.json on next graph update

## Example: Enriching PyJWT Library

**Step 1: Load**
```
Found sparse entity: PyJWT Library (pyjwt_lib)
Current state:
- Type: Entity
- Label: PyJWT
- Properties: {"name": "PyJWT"} (only 1 property)
- Triad: discovery
```

**Step 2: Research**
```
Let me research PyJWT...

1. Checking pyproject.toml for version:
   - Found: PyJWT==2.8.0 at line 23

2. Searching for usage in codebase:
   - src/auth/jwt.py imports PyJWT
   - src/auth/tokens.py uses jwt.encode()
   - src/middleware/auth.py uses jwt.decode()

3. Checking PyJWT documentation:
   - Official docs: https://pyjwt.readthedocs.io/
   - Capabilities: Encode/decode JWT, supports multiple algorithms
   - Used for: Stateless authentication tokens

4. Checking security:
   - Algorithm: RS256 (from config/jwt.yml:12)
   - No known vulnerabilities in 2.8.0
```

**Step 3: Output Update**
```
[GRAPH_UPDATE]
type: update_node
node_id: pyjwt_lib
properties: {
  "version": "2.8.0",
  "package_name": "PyJWT",
  "purpose": "JWT token encoding and decoding for stateless authentication",
  "algorithm": "RS256",
  "usage_files": ["src/auth/jwt.py", "src/auth/tokens.py", "src/middleware/auth.py"],
  "documentation_url": "https://pyjwt.readthedocs.io/en/stable/",
  "capabilities": ["encode", "decode", "verify signature", "validate expiration"],
  "install_location": "pyproject.toml:23"
}
confidence: 0.95
evidence: Version 2.8.0 found in pyproject.toml:23. Usage confirmed in src/auth/jwt.py:5 (import), src/auth/tokens.py:45 (jwt.encode), src/middleware/auth.py:32 (jwt.decode). Algorithm RS256 specified in config/jwt.yml:12. Official documentation at https://pyjwt.readthedocs.io/. Verified no security issues with version 2.8.0.
[/GRAPH_UPDATE]
```

**Step 4: Verify**
```
✅ Enrichment complete!

PyJWT Library now has 8 properties:
- version: 2.8.0
- package_name: PyJWT
- purpose: JWT token encoding and decoding for stateless authentication
- algorithm: RS256
- usage_files: [3 files]
- documentation_url: https://pyjwt.readthedocs.io/en/stable/
- capabilities: [4 capabilities]
- install_location: pyproject.toml:23

Confidence: 0.95
Evidence: Comprehensive citations provided

The entity will be removed from km_queue.json on next graph update.
```

## Constitutional Compliance

### R - Require Evidence
**CRITICAL**: Every property must have verifiable evidence.
- ✅ Good: "version: 2.8.0 (from pyproject.toml:23)"
- ❌ Bad: "version: probably 2.x (looks recent)"

### T - Thorough over Fast
Take time to research properly. Better to spend 3 minutes and add 5 solid properties than rush with 3 weak ones.

### R - Respect Uncertainty
If you cannot find information, add an Uncertainty node rather than guessing.

## User Arguments

If user provides specific target:
```
/enrich-knowledge pyjwt_lib
/enrich-knowledge "PyJWT Library"
/enrich-knowledge all
```

## Error Handling

- **No sparse entities found**: Report "No sparse entities in queue. Run /km-status to check for other issues."
- **Node not found**: "Node '{id}' not found in queue. Available: [list]"
- **Cannot find information**: Create Uncertainty node instead of guessing

## Related Commands

- `/km-status` - View all KM issues
- `/validate-knowledge` - Add evidence to low-confidence nodes

Begin enrichment now. If no target specified, load and display the list.
