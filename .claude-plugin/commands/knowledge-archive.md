# Archive Draft Knowledge

You are archiving a draft process knowledge node (marking it as a false positive).

## Arguments

- `<node_id>`: The ID of the draft node to archive (e.g., `process_user_correction_20251017_141530`)

## Your Task

1. **Parse the node_id** from the command
   - User will invoke: `/knowledge-archive <node_id>`
   - Extract the node_id parameter

2. **Find the node** across all knowledge graphs:
   - Search `.claude/graphs/*_graph.json` for node with matching ID
   - Verify the node has `status: "draft"`

3. **Validate before archiving**:
   - Check node exists
   - Check status is currently "draft"
   - If node not found or already archived, show error
   - Warn if trying to archive an active lesson

4. **Update the node**:
   - Change `status: "draft"` to `status: "archived"`
   - Add `archived_at: <timestamp>`
   - Add `archived_by: "user"`
   - Add `archive_reason: "false_positive"` (or ask user for reason)
   - Keep all other fields for audit trail

5. **Save the updated graph**:
   - Write the modified graph back to the same file
   - Preserve JSON formatting and structure

6. **Confirm to user**:
   - Show what was archived
   - Explain that this node won't appear in reviews anymore
   - Explain it's kept for audit purposes

## Example

**User runs**: `/knowledge-archive process_repeated_mistake_20251017_141830`

**You should**:
1. Find node `process_repeated_mistake_20251017_141830`
2. Change status from "draft" to "archived"
3. Add archived_at timestamp and archive_reason
4. Save the graph
5. Respond:

```markdown
🗄️ **Knowledge Archived**

**Node**: process_repeated_mistake_20251017_141830
**Label**: Repeated Issue: marketplace.json
**Triad**: deployment
**Status**: draft → **archived**
**Reason**: false_positive

This lesson has been archived and will not:
- Appear in `/knowledge-review-drafts`
- Be shown at SessionStart
- Be injected by PreToolUse hooks

The node is retained in the graph for audit purposes. If this was archived by mistake, you can manually edit the graph file to restore it.
```

## Optional: Ask for Archive Reason

Before archiving, you may optionally ask the user why they're archiving this lesson:

```markdown
**Why are you archiving this lesson?**
1. False positive (detected incorrectly)
2. No longer relevant
3. Duplicate of existing knowledge
4. Other reason

[Ask user to select or provide custom reason]
```

Then include their reason in `archive_reason` field.

## Error Handling

- **Node not found**: "❌ Error: Node `<node_id>` not found in any graph"
- **Already archived**: "ℹ️  Node `<node_id>` is already archived"
- **Active lesson warning**: "⚠️  Warning: This is an active lesson. Are you sure you want to archive it? This will stop it from appearing in hooks."
- **File write error**: Show helpful error message

## Implementation Notes

- Use the Edit tool to modify the graph JSON file
- Preserve all other nodes and graph structure
- Update graph metadata (updated_at timestamp)
- Archived nodes are NOT deleted, only status changes
- This allows for audit trail and potential restoration
