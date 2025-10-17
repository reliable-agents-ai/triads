# Promote Draft Knowledge

You are promoting a draft process knowledge node to **active** status.

## Arguments

- `<node_id>`: The ID of the draft node to promote (e.g., `process_user_correction_20251017_141530`)

## Your Task

1. **Parse the node_id** from the command
   - User will invoke: `/knowledge-promote <node_id>`
   - Extract the node_id parameter

2. **Find the node** across all knowledge graphs:
   - Search `.claude/graphs/*_graph.json` for node with matching ID
   - Verify the node has `status: "draft"`

3. **Validate before promoting**:
   - Check node exists
   - Check status is currently "draft"
   - If node not found or already active, show error

4. **Update the node**:
   - Change `status: "draft"` to `status: "active"`
   - Add `promoted_at: <timestamp>`
   - Add `promoted_by: "user"`
   - Keep all other fields unchanged (priority, content, trigger_conditions, etc.)

5. **Save the updated graph**:
   - Write the modified graph back to the same file
   - Preserve JSON formatting and structure

6. **Confirm to user**:
   - Show what was promoted
   - Explain that this knowledge is now active
   - Note: It will now appear in PreToolUse hooks when relevant

## Example

**User runs**: `/knowledge-promote process_user_correction_20251017_141530`

**You should**:
1. Find node `process_user_correction_20251017_141530` in deployment_graph.json
2. Change status from "draft" to "active"
3. Add promoted_at timestamp
4. Save the graph
5. Respond:

```markdown
✅ **Knowledge Promoted**

**Node**: process_user_correction_20251017_141530
**Label**: Remember: marketplace.json
**Triad**: deployment
**Status**: draft → **active**

This lesson is now active and will be injected by PreToolUse hooks when:
- Using tools: Write, Edit
- Working with files matching: **/marketplace.json
- Keywords detected: marketplace

The lesson will help prevent this mistake from happening again.
```

## Error Handling

- **Node not found**: "❌ Error: Node `<node_id>` not found in any graph"
- **Already active**: "ℹ️  Node `<node_id>` is already active (status: active)"
- **Already archived**: "❌ Error: Cannot promote archived node. Use `/knowledge-review-drafts` to see active drafts"
- **File write error**: Show helpful error message

## Implementation Notes

- Use the Edit tool to modify the graph JSON file
- Preserve all other nodes and graph structure
- Update graph metadata (updated_at timestamp)
- Be careful with JSON formatting (use proper indentation)
