"""Repository layer for generator tools.

Abstracts access to agent generation functionality.
"""

from abc import ABC, abstractmethod
from typing import List

from triads.tools.generator.domain import AgentDefinition

import logging

logger = logging.getLogger(__name__)



class GeneratorRepositoryError(Exception):
    """Base exception for generator repository errors."""
    pass


class AbstractGeneratorRepository(ABC):
    """Abstract interface for generator repositories.

    Defines the contract for accessing agent generation functionality.
    """

    @abstractmethod
    def generate_agents(self, workflow_type: str, domain: str) -> List[AgentDefinition]:
        """Generate agent definitions for a workflow.

        Args:
            workflow_type: Type of workflow (e.g., "debugging", "software-development")
            domain: Domain description for context

        Returns:
            List of AgentDefinition objects

        Raises:
            GeneratorRepositoryError: If generation fails
        """
        pass


class InMemoryGeneratorRepository(AbstractGeneratorRepository):
    """In-memory generator repository for testing.

    Provides simplified agent generation without external dependencies.
    Used for unit testing.
    """

    def generate_agents(self, workflow_type: str, domain: str) -> List[AgentDefinition]:
        """Generate sample agent definitions.

        Args:
            workflow_type: Type of workflow
            domain: Domain description

        Returns:
            List of AgentDefinition objects with sample content

        Raises:
            GeneratorRepositoryError: If workflow_type or domain is invalid
        """
        if not workflow_type or not isinstance(workflow_type, str):
            raise GeneratorRepositoryError(
                "Valid workflow_type required (must be non-empty string)"
            )

        if not domain or not isinstance(domain, str):
            raise GeneratorRepositoryError(
                "Valid domain required (must be non-empty string)"
            )

        # Generate sample agents based on workflow type
        if workflow_type == "debugging":
            return self._generate_debugging_agents(domain)
        elif workflow_type == "software-development":
            return self._generate_software_development_agents(domain)
        else:
            # Generic workflow - generate basic triad
            return self._generate_generic_agents(workflow_type, domain)

    def _generate_debugging_agents(self, domain: str) -> List[AgentDefinition]:
        """Generate agents for debugging workflow."""
        investigator_content = f"""---
name: investigator
role: Lead Investigator
tools: [Read, Grep, Bash]
---

# Lead Investigator

You are the **Lead Investigator** in the debugging triad.

Domain: {domain}

## Responsibilities

- Analyze error messages and stack traces
- Investigate root causes of bugs
- Identify affected components
- Document findings

## Tools Available

- Read: Examine source files
- Grep: Search for patterns
- Bash: Run diagnostic commands
"""

        fixer_content = f"""---
name: fixer
role: Bug Fixer
tools: [Read, Edit, Bash]
---

# Bug Fixer

You are the **Bug Fixer** in the debugging triad.

Domain: {domain}

## Responsibilities

- Implement fixes based on investigator findings
- Write tests to prevent regressions
- Validate fixes work correctly

## Tools Available

- Read: Review code
- Edit: Make changes
- Bash: Run tests
"""

        verifier_content = f"""---
name: verifier
role: Verification Bridge
tools: [Bash, Read]
---

# Verification Bridge

You are the **Verification Bridge** in the debugging triad.

Domain: {domain}

## Responsibilities

- Verify fixes resolve the issue
- Ensure no new bugs introduced
- Confirm tests pass
- Handoff to next phase

## Tools Available

- Bash: Run test suites
- Read: Review changes
"""

        return [
            AgentDefinition(
                name="investigator",
                role="Lead Investigator",
                tools=["Read", "Grep", "Bash"],
                content=investigator_content,
                triad_id="debugging"
            ),
            AgentDefinition(
                name="fixer",
                role="Bug Fixer",
                tools=["Read", "Edit", "Bash"],
                content=fixer_content,
                triad_id="debugging"
            ),
            AgentDefinition(
                name="verifier",
                role="Verification Bridge",
                tools=["Bash", "Read"],
                content=verifier_content,
                triad_id="debugging"
            )
        ]

    def _generate_software_development_agents(self, domain: str) -> List[AgentDefinition]:
        """Generate agents for software development workflow."""
        designer_content = f"""---
name: designer
role: Solution Architect
tools: [Read, Grep, Write]
---

# Solution Architect

Domain: {domain}

Design and architect software solutions.
"""

        return [
            AgentDefinition(
                name="designer",
                role="Solution Architect",
                tools=["Read", "Grep", "Write"],
                content=designer_content,
                triad_id="design"
            )
        ]

    def _generate_generic_agents(self, workflow_type: str, domain: str) -> List[AgentDefinition]:
        """Generate generic agents for unknown workflow types."""
        agent_content = f"""---
name: agent
role: Generic Agent
tools: [Read, Write, Bash]
---

# Generic Agent

Workflow: {workflow_type}
Domain: {domain}

General-purpose agent for {workflow_type} workflow.
"""

        return [
            AgentDefinition(
                name="agent",
                role="Generic Agent",
                tools=["Read", "Write", "Bash"],
                content=agent_content,
                triad_id=workflow_type
            )
        ]
