"""Agent upgrade orchestration.

This module orchestrates the agent upgrade workflow with multi-gate safety:
1. Scan agents to identify outdated versions
2. Backup agents before modification
3. Show diffs for user review
4. Validate new content structure
5. Apply upgrades atomically

Security features:
- Path traversal protection
- Atomic file operations (temp → rename)
- Validation gates before modification
- Backup before every change
"""

import difflib
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from triads.templates.agent_templates import AGENT_TEMPLATE_VERSION
from triads.utils.file_operations import atomic_read_text, atomic_write_text

from .exceptions import (
    AgentNotFoundError,
    InvalidAgentError,
    UpgradeIOError,
    UpgradeSecurityError,
)

logger = logging.getLogger(__name__)


@dataclass
class UpgradeCandidate:
    """Agent identified for potential upgrade.

    Attributes:
        agent_path: Path to agent markdown file
        current_version: Current template version (or "unknown")
        latest_version: Latest available template version
        triad_name: Name of triad this agent belongs to
        agent_name: Name of the agent (without .md extension)
        has_customizations: Whether agent has custom sections (Phase 3 feature)
    """
    agent_path: Path
    current_version: str
    latest_version: str
    triad_name: str
    agent_name: str
    has_customizations: bool = False

    @property
    def needs_upgrade(self) -> bool:
        """Check if version is outdated.

        Returns:
            True if current version differs from latest version
        """
        return self.current_version != self.latest_version

    def __str__(self) -> str:
        """Human-readable representation."""
        status = "⚠️ NEEDS UPGRADE" if self.needs_upgrade else "✓ UP TO DATE"
        return f"{self.triad_name}/{self.agent_name} ({self.current_version} → {self.latest_version}) {status}"


class UpgradeOrchestrator:
    """Orchestrate agent upgrade workflow.

    This class manages the complete upgrade process with safety gates:
    - Scanning for outdated agents
    - Creating backups before modification
    - Showing diffs for user review
    - Validating content structure
    - Applying upgrades atomically

    Example:
        >>> orchestrator = UpgradeOrchestrator(dry_run=True)
        >>> candidates = orchestrator.scan_agents()
        >>> for candidate in candidates:
        ...     if candidate.needs_upgrade:
        ...         print(candidate)
        >>>
        >>> # Review and apply
        >>> orchestrator.dry_run = False
        >>> new_content = generate_upgraded_content(candidate)
        >>> success = orchestrator.apply_upgrade(candidate, new_content)
    """

    def __init__(self, dry_run: bool = False, force: bool = False):
        """Initialize orchestrator.

        Args:
            dry_run: Preview changes without applying (default: False)
            force: Skip confirmation prompts - use with caution (default: False)
        """
        self.dry_run = dry_run
        self.force = force
        self.agents_dir = Path(".claude/agents")
        self.latest_version = AGENT_TEMPLATE_VERSION

        # Validate agents directory exists
        if not self.agents_dir.exists():
            logger.error("Agents directory not found: %s", self.agents_dir.absolute())
            raise AgentNotFoundError(
                f"Agents directory not found: {self.agents_dir.absolute()}"
            )

    def scan_agents(
        self,
        agent_names: Optional[List[str]] = None,
        triad_name: Optional[str] = None
    ) -> List[UpgradeCandidate]:
        """Scan for agents needing upgrade.

        Searches .claude/agents/ directory for agent files and checks their
        template versions against the latest version.

        Args:
            agent_names: Specific agent names to check (None = all agents)
            triad_name: Limit to specific triad (None = all triads)

        Returns:
            List of UpgradeCandidate objects (includes both outdated and current)

        Example:
            >>> # Scan all agents
            >>> candidates = orchestrator.scan_agents()
            >>>
            >>> # Scan specific triad
            >>> candidates = orchestrator.scan_agents(triad_name="implementation")
            >>>
            >>> # Scan specific agents
            >>> candidates = orchestrator.scan_agents(
            ...     agent_names=["senior-developer", "test-engineer"]
            ... )
        """
        candidates = []

        # Build glob pattern based on filters
        if triad_name:
            # Security: Validate triad name to prevent path traversal
            if not self._is_safe_path_component(triad_name):
                logger.error("Invalid triad name (security): %s", triad_name)
                raise UpgradeSecurityError(triad_name, "Invalid triad name (path traversal attempt)")
            pattern = f"{triad_name}/*.md"
        else:
            pattern = "**/*.md"

        logger.info("Scanning agents with pattern: %s, filters: triad=%s, names=%s",
                   pattern, triad_name, agent_names)

        # Find all matching agent files
        agent_files = sorted(self.agents_dir.glob(pattern))

        for agent_path in agent_files:
            # Security: Validate path is within agents directory
            if not self._is_safe_agent_path(agent_path):
                logger.warning("Skipping unsafe agent path (security): %s", agent_path)
                continue

            # Filter by agent_names if specified
            agent_name = agent_path.stem
            if agent_names and agent_name not in agent_names:
                continue

            # Extract triad name from path
            # Path structure: .claude/agents/{triad}/{agent}.md
            try:
                relative_path = agent_path.relative_to(self.agents_dir)
                current_triad = relative_path.parent.name
            except ValueError:
                # Path not relative to agents_dir - skip
                continue

            # Parse template version from frontmatter
            current_version = self._parse_template_version(agent_path)

            # Create candidate
            candidate = UpgradeCandidate(
                agent_path=agent_path,
                current_version=current_version,
                latest_version=self.latest_version,
                triad_name=current_triad,
                agent_name=agent_name
            )

            candidates.append(candidate)

        return candidates

    def _parse_template_version(self, agent_path: Path) -> str:
        """Extract template_version from agent frontmatter.

        Args:
            agent_path: Path to agent markdown file

        Returns:
            Version string, or "unknown" if not found

        Note:
            This parsing is intentionally simple and defensive.
            Complex YAML parsing with PyYAML would be overkill and add dependencies.
        """
        try:
            content = atomic_read_text(agent_path)
        except Exception as e:
            return "unknown"

        # Parse YAML frontmatter between --- markers
        # Pattern: Start of file, ---, content, ---
        match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL | re.MULTILINE)
        if not match:
            return "unknown"

        frontmatter = match.group(1)

        # Extract template_version field
        # Pattern: template_version: {value}
        version_match = re.search(
            r'^template_version:\s*(.+)$',
            frontmatter,
            re.MULTILINE
        )
        if version_match:
            return version_match.group(1).strip()

        return "unknown"

    def backup_agent(self, agent_path: Path) -> Path:
        """Create timestamped backup of agent file.

        Backups are stored in .claude/agents/backups/ with format:
        {agent_name}_{timestamp}.md.backup

        Args:
            agent_path: Path to agent file to back up

        Returns:
            Path to created backup file

        Raises:
            IOError: If backup creation fails

        Example:
            >>> backup_path = orchestrator.backup_agent(
            ...     Path(".claude/agents/implementation/senior-developer.md")
            ... )
            >>> print(backup_path)
            .claude/agents/backups/senior-developer_20251020_143022.md.backup
        """
        # Create backups directory if needed
        backup_dir = self.agents_dir / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)

        # Timestamped backup name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{agent_path.stem}_{timestamp}.md.backup"
        backup_path = backup_dir / backup_name

        # Copy content using centralized file operations
        try:
            content = atomic_read_text(agent_path)
            atomic_write_text(backup_path, content)
        except Exception as e:
            raise UpgradeIOError("backup_creation", str(agent_path), e) from e

        return backup_path

    def show_diff(
        self,
        current_content: str,
        proposed_content: str,
        agent_name: str = ""
    ) -> str:
        """Generate unified diff between current and proposed content.

        Creates a human-readable diff in unified format (like git diff).

        Args:
            current_content: Current agent content
            proposed_content: Proposed upgraded content
            agent_name: Agent name for display in diff header

        Returns:
            Formatted unified diff string

        Example:
            >>> diff = orchestrator.show_diff(
            ...     current_content=old_content,
            ...     proposed_content=new_content,
            ...     agent_name="senior-developer"
            ... )
            >>> print(diff)
            --- current/senior-developer
            +++ proposed/senior-developer
            @@ -1,5 +1,5 @@
             ---
             name: senior-developer
            -template_version: 0.7.0
            +template_version: 0.8.0
        """
        # Split into lines for difflib
        current_lines = current_content.splitlines(keepends=True)
        proposed_lines = proposed_content.splitlines(keepends=True)

        # Generate unified diff
        diff_lines = difflib.unified_diff(
            current_lines,
            proposed_lines,
            fromfile=f"current/{agent_name}" if agent_name else "current",
            tofile=f"proposed/{agent_name}" if agent_name else "proposed",
            lineterm=""
        )

        return "".join(diff_lines)

    def apply_upgrade(
        self,
        candidate: UpgradeCandidate,
        new_content: str
    ) -> bool:
        """Apply upgrade to agent file.

        This implements the multi-gate safety process:
        1. Create backup
        2. Validate new content structure
        3. Atomic write (temp file → rename)

        Args:
            candidate: Upgrade candidate to process
            new_content: New agent content to write

        Returns:
            True if successful, False otherwise

        Example:
            >>> candidate = candidates[0]
            >>> new_content = generate_upgraded_content(candidate)
            >>> success = orchestrator.apply_upgrade(candidate, new_content)
            >>> if success:
            ...     print(f"✓ Upgraded {candidate.agent_name}")
        """
        if self.dry_run:
            logger.info("Dry-run mode: Would upgrade %s", candidate.agent_path)
            print(f"[DRY-RUN] Would upgrade {candidate.agent_path}")
            return True

        try:
            # Gate 1: Create backup
            backup_path = self.backup_agent(candidate.agent_path)
            logger.info("Created backup: %s for agent %s", backup_path.name, candidate.agent_name)
            print(f"  ✓ Backed up to {backup_path.name}")

            # Gate 2: Validate new content
            if not self._validate_agent_content(new_content):
                logger.warning("Validation failed for agent %s, backup preserved at %s",
                             candidate.agent_name, backup_path)
                print(f"  ✗ Validation failed for {candidate.agent_name}")
                print(f"    Backup preserved at: {backup_path}")
                return False

            # Gate 3: Atomic write using centralized file operations
            # This ensures we never have a partially-written agent file
            try:
                atomic_write_text(candidate.agent_path, new_content)
            except Exception as e:
                raise UpgradeIOError("atomic_write", str(candidate.agent_path), e) from e

            logger.info("Successfully upgraded agent: %s from %s to %s",
                       candidate.agent_name, candidate.current_version, self.latest_version)
            print(f"  ✓ Upgraded {candidate.agent_name}")
            return True

        except Exception as e:
            logger.error("Error upgrading agent %s: %s", candidate.agent_name, e, exc_info=True)
            print(f"  ✗ Error upgrading {candidate.agent_name}: {e}")
            return False

    def _validate_agent_content(self, content: str) -> bool:
        """Validate agent content structure.

        Performs basic structural validation:
        - Has valid YAML frontmatter (starts with ---, ends with ---)
        - Required fields present (name, triad, role, template_version)

        Args:
            content: Agent content to validate

        Returns:
            True if valid, False otherwise

        Note:
            This is intentionally permissive. We validate structure, not semantics.
            The goal is to prevent obviously broken files, not enforce perfection.
        """
        # Check for frontmatter
        if not content.startswith('---\n'):
            return False

        # Extract frontmatter
        match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL | re.MULTILINE)
        if not match:
            return False

        frontmatter = match.group(1)

        # Check required fields (colon indicates YAML field)
        required_fields = ['name:', 'triad:', 'role:', 'template_version:']
        for field in required_fields:
            if field not in frontmatter:
                return False

        return True

    def _is_safe_path_component(self, component: str) -> bool:
        """Validate path component for security.

        Prevents path traversal attacks by rejecting:
        - Path separators (/, \\)
        - Parent directory references (..)
        - Null bytes

        Args:
            component: Path component to validate

        Returns:
            True if safe, False otherwise
        """
        if not component:
            return False

        # Block path traversal attempts
        dangerous_chars = ['/', '\\', '..', '\0']
        return not any(char in component for char in dangerous_chars)

    def _is_safe_agent_path(self, agent_path: Path) -> bool:
        """Validate agent path is within agents directory.

        Security check to prevent path traversal vulnerabilities.

        Args:
            agent_path: Path to validate

        Returns:
            True if path is safe (within agents_dir), False otherwise
        """
        try:
            # Resolve both paths to absolute
            agent_abs = agent_path.resolve()
            agents_abs = self.agents_dir.resolve()

            # Check agent path is relative to agents directory
            agent_abs.relative_to(agents_abs)
            return True
        except ValueError:
            # relative_to() raises ValueError if not relative
            return False

    def generate_upgraded_content(
        self,
        candidate: UpgradeCandidate,
        preserve_customizations: bool = True
    ) -> str:
        """Generate upgraded agent content.

        Applies template updates while preserving existing content and
        user customizations. Uses smart merge strategy to add new sections.

        Args:
            candidate: Agent to upgrade
            preserve_customizations: Whether to preserve custom sections (default: True)

        Returns:
            Upgraded agent content with new template features

        Example:
            >>> candidate = candidates[0]
            >>> upgraded = orchestrator.generate_upgraded_content(candidate)
            >>> # upgraded now has latest template sections while preserving content
        """
        current_content = atomic_read_text(candidate.agent_path)

        # Parse current agent into frontmatter + body
        frontmatter, body = self._parse_agent_file(current_content)

        # Update frontmatter version
        frontmatter['template_version'] = self.latest_version

        # Identify new sections in latest template
        new_sections = self._identify_new_sections(self.latest_version)

        # Merge: Add new sections while preserving existing content
        upgraded_body = self._merge_sections(body, new_sections, preserve_customizations)

        # Reconstruct agent file
        return self._format_agent_file(frontmatter, upgraded_body)

    def _parse_agent_file(self, content: str) -> tuple[dict, str]:
        """Parse agent file into frontmatter dict and body.

        Args:
            content: Full agent file content

        Returns:
            Tuple of (frontmatter_dict, body_string)
        """
        # Extract frontmatter
        match = re.search(r'^---\s*\n(.*?)\n---\s*\n(.*)', content, re.DOTALL | re.MULTILINE)
        if not match:
            raise InvalidAgentError("agent_file", "Could not parse agent frontmatter")

        frontmatter_text = match.group(1)
        body = match.group(2)

        # Parse frontmatter into dict
        frontmatter = {}
        for line in frontmatter_text.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip()

        return frontmatter, body

    def _identify_new_sections(self, version: str) -> List[str]:
        """Identify new sections added in this template version.

        For v0.8.0, this is the Knowledge Graph Protocol section.

        Args:
            version: Template version

        Returns:
            List of section names added in this version
        """
        if version == "0.8.0":
            return ["🧠 Knowledge Graph Protocol"]
        return []

    def _merge_sections(
        self,
        current_body: str,
        new_sections: List[str],
        preserve_custom: bool
    ) -> str:
        """Merge new template sections into existing agent body.

        Strategy:
        - Find insertion point (after Constitutional Principles section)
        - Insert new sections
        - Preserve all existing content

        Args:
            current_body: Current agent body text
            new_sections: List of section names to add
            preserve_custom: Whether to preserve customizations

        Returns:
            Merged body content
        """
        # For v0.8.0: Insert Knowledge Graph Protocol
        if "🧠 Knowledge Graph Protocol" in new_sections:
            if "🧠 Knowledge Graph Protocol" in current_body:
                # Already has it, skip
                return current_body

            # Get the Knowledge Graph Protocol section from template
            kg_protocol = self._get_kg_protocol_section()

            # Find insertion point (after Constitutional Principles, before next section)
            lines = current_body.split('\n')
            insert_idx = None

            # Strategy: Find "Constitutional Principles" section, then find next ## heading
            in_constitutional = False
            for i, line in enumerate(lines):
                if '## Constitutional Principles' in line:
                    in_constitutional = True
                elif in_constitutional and line.startswith('## ') and 'Constitutional' not in line:
                    # Found next section after Constitutional Principles
                    insert_idx = i
                    break

            if insert_idx is None:
                # Fallback: insert after frontmatter/first section
                # Find first ## after identity section
                for i, line in enumerate(lines):
                    if line.startswith('## ') and i > 10:  # Skip early sections
                        insert_idx = i
                        break

            if insert_idx is None:
                # Last resort: append to end
                insert_idx = len(lines)

            # Insert the new section with proper spacing
            lines.insert(insert_idx, "")  # Blank line after previous section
            lines.insert(insert_idx + 1, kg_protocol)
            lines.insert(insert_idx + 2, "")  # Blank line before next section

            return '\n'.join(lines)

        return current_body

    def _get_kg_protocol_section(self) -> str:
        """Get Knowledge Graph Protocol section from template.

        Returns the full section text to insert into agents.

        Returns:
            Knowledge Graph Protocol section markdown
        """
        # Import template
        from triads.templates.agent_templates import AGENT_TEMPLATE

        # Extract the KG Protocol section using regex
        # Pattern: ## 🧠 Knowledge Graph Protocol ... up to next ## or end
        match = re.search(
            r'(## 🧠 Knowledge Graph Protocol.*?)(?=\n##[^#]|\Z)',
            AGENT_TEMPLATE,
            re.DOTALL
        )

        if match:
            section = match.group(1).strip()
            # Replace template variables with placeholders
            # The triad_name will vary per agent
            section = section.replace('{triad_name}', '{triad_name}')
            return section

        # Fallback if not found (should not happen)
        return """## 🧠 Knowledge Graph Protocol (MANDATORY)

**Knowledge Graph Location**: `.claude/graphs/{triad_name}_graph.json`

### Before Starting ANY Work

You MUST query your knowledge graph, display findings, and apply them as canon.
See agent template for full protocol.

---"""

    def _format_agent_file(self, frontmatter: dict, body: str) -> str:
        """Reconstruct agent file from frontmatter and body.

        Args:
            frontmatter: Dict of frontmatter fields
            body: Agent body content

        Returns:
            Complete agent file content
        """
        # Build frontmatter
        fm_lines = ["---"]
        for key, value in frontmatter.items():
            fm_lines.append(f"{key}: {value}")
        fm_lines.append("---")
        fm_lines.append("")  # Blank line after frontmatter

        frontmatter_text = '\n'.join(fm_lines)

        # Combine
        return frontmatter_text + body

    def upgrade_agent(
        self,
        candidate: UpgradeCandidate,
        show_diff_first: bool = True,
        require_confirmation: bool = True
    ) -> bool:
        """Complete upgrade workflow for a single agent.

        Orchestrates the full upgrade process:
        1. Generate upgraded content
        2. Show diff for review
        3. Get user confirmation
        4. Apply upgrade with safety gates

        Args:
            candidate: Agent to upgrade
            show_diff_first: Show diff before applying (default: True)
            require_confirmation: Ask user to confirm (default: True)

        Returns:
            True if upgrade successful, False otherwise

        Example:
            >>> # Interactive upgrade
            >>> success = orchestrator.upgrade_agent(candidate)
            >>>
            >>> # Force upgrade (no confirmation)
            >>> orchestrator.force = True
            >>> success = orchestrator.upgrade_agent(candidate, require_confirmation=False)
        """
        print(f"\n📦 Upgrading {candidate.agent_name}")
        print(f"   Current version: {candidate.current_version}")
        print(f"   Target version: {candidate.latest_version}")

        # Generate upgraded content
        try:
            new_content = self.generate_upgraded_content(candidate)
        except Exception as e:
            logger.error("Error generating upgrade for %s: %s", candidate.agent_name, e, exc_info=True)
            print(f"❌ Error generating upgrade: {e}")
            return False

        # Show diff if requested
        if show_diff_first:
            current_content = atomic_read_text(candidate.agent_path)
            diff = self.show_diff(current_content, new_content, candidate.agent_name)
            print("\n📊 Proposed changes:")
            print(diff)

        # Confirm if needed
        if require_confirmation and not self.force:
            response = input("\n❓ Apply this upgrade? [y/N/d(iff)/s(kip)]: ").lower()

            if response == 'd':
                # Show diff again
                current_content = atomic_read_text(candidate.agent_path)
                diff = self.show_diff(current_content, new_content, candidate.agent_name)
                print("\n📊 Proposed changes:")
                print(diff)
                response = input("❓ Apply upgrade? [y/N]: ").lower()

            if response == 's':
                print("⏭️  Skipped")
                return False

            if response != 'y':
                print("❌ Cancelled")
                return False

        # Apply upgrade
        success = self.apply_upgrade(candidate, new_content)

        if success:
            print(f"✅ Upgraded {candidate.agent_name} to v{self.latest_version}")

        return success

    def upgrade_all(
        self,
        agent_names: Optional[List[str]] = None,
        triad_name: Optional[str] = None
    ) -> dict:
        """Upgrade multiple agents.

        Scans for candidates and upgrades them with user confirmation.

        Args:
            agent_names: Specific agents to upgrade (None = all)
            triad_name: Limit to specific triad (None = all)

        Returns:
            Statistics dict: {'total': N, 'upgraded': M, 'skipped': K, 'failed': L}

        Example:
            >>> # Upgrade all agents
            >>> stats = orchestrator.upgrade_all()
            >>>
            >>> # Upgrade specific triad
            >>> stats = orchestrator.upgrade_all(triad_name="implementation")
            >>>
            >>> # Upgrade specific agents
            >>> stats = orchestrator.upgrade_all(
            ...     agent_names=["senior-developer", "test-engineer"]
            ... )
        """
        stats = {'total': 0, 'upgraded': 0, 'skipped': 0, 'failed': 0}

        # Scan for candidates
        candidates = self.scan_agents(agent_names=agent_names, triad_name=triad_name)

        # Filter to only those needing upgrade
        candidates = [c for c in candidates if c.needs_upgrade]

        stats['total'] = len(candidates)

        if stats['total'] == 0:
            print("✅ All agents are up to date!")
            return stats

        print(f"\n📋 Found {stats['total']} agents needing upgrade\n")

        # Upgrade each
        for candidate in candidates:
            success = self.upgrade_agent(candidate)

            if success:
                stats['upgraded'] += 1
            elif self.dry_run:
                stats['skipped'] += 1
            else:
                stats['failed'] += 1

        # Summary
        print("\n" + "="*60)
        print("📊 UPGRADE SUMMARY")
        print("="*60)
        print(f"Total agents scanned: {stats['total']}")
        print(f"Successfully upgraded: {stats['upgraded']}")
        print(f"Skipped: {stats['skipped']}")
        print(f"Failed: {stats['failed']}")

        return stats
