"""MCP tool entrypoints for generator tools.

Provides 1 MCP-compliant tool for agent generation.

CRITICAL: This tool returns MCP Resources (agent .md files), not text!
"""

from triads.tools.shared import ToolResult
from triads.tools.generator.bootstrap import bootstrap_generator_service

import logging

logger = logging.getLogger(__name__)



class GeneratorTools:
    """MCP tool entrypoints for generator operations.

    All methods return ToolResult in MCP-compliant format.
    """

    @staticmethod
    def generate_agents(workflow_type: str, domain: str) -> ToolResult:
        """Generate agent definitions for a workflow.

        MCP Tool: generate_agents

        Generates agent markdown files for the specified workflow type
        and domain. Returns agents as MCP Resources (not text).

        Args:
            workflow_type: Type of workflow (e.g., "debugging", "software-development")
            domain: Domain description for context

        Returns:
            ToolResult with resource content (agent .md files)

        Example:
            >>> result = GeneratorTools.generate_agents("debugging", "Python")
            >>> result.success
            True
            >>> result.content[0]["type"]
            'resource'
            >>> result.content[0]["resource"]["uri"]
            'triads://agents/debugging/investigator.md'

        Note:
            This tool returns MCP Resources, not text. Each resource represents
            an agent .md file with:
            - uri: triads://agents/{triad_id}/{agent_name}.md
            - mimeType: text/markdown
            - text: Full agent markdown content
        """
        service = bootstrap_generator_service()

        try:
            agents = service.generate_agents(workflow_type, domain)

            # Convert AgentDefinitions to MCP Resources
            resources = []
            for agent in agents:
                resource_uri = f"triads://agents/{agent.triad_id}/{agent.name}.md"
                resources.append({
                    "type": "resource",
                    "resource": {
                        "uri": resource_uri,
                        "mimeType": "text/markdown",
                        "text": agent.content
                    }
                })

            return ToolResult(success=True, content=resources)

        except Exception as e:
            return ToolResult(success=False, content=[], error=str(e))
