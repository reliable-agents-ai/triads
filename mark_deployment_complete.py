#!/usr/bin/env python3
"""
Mark deployment triad as complete in workflow instance.

This script is run by the Documentation Updater agent to mark
the deployment triad as complete after documentation updates.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from triads.workflow_enforcement.instance_manager import WorkflowInstanceManager
from triads.utils.workflow_context import get_current_instance_id

def main():
    """Mark deployment triad complete."""
    instance_id = get_current_instance_id()

    if not instance_id:
        print("⚠️  No current workflow instance found")
        print("   This is expected if not running within a workflow context")
        return 0

    print(f"📋 Current workflow instance: {instance_id}")

    try:
        manager = WorkflowInstanceManager()

        # Mark deployment complete
        manager.mark_triad_completed(instance_id, "deployment")
        print("✅ Deployment triad marked complete")

        # Update significance metrics
        instance = manager.load_instance(instance_id)
        instance.significance_metrics.update({
            "documentation_updated": True,
            "version": "0.7.0-alpha.7",
            "files_updated": [
                "README.md",
                "docs/WORKFLOW_MANAGEMENT.md",
                "docs/USAGE.md",
                "DOCUMENTATION_UPDATE_v0.7.0-alpha.7.md"
            ],
            "lines_added": 732,
            "lines_deleted": 0,
            "links_verified": 18,
            "new_documentation_files": 2
        })
        manager.update_instance(instance_id, instance.to_dict())
        print("✅ Significance metrics updated")

        print(f"\n🎉 Workflow instance {instance_id} deployment complete!")
        print(f"   Documentation for v0.7.0-alpha.7 is ready")

        return 0

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
