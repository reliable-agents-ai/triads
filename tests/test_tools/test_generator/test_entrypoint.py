"""Tests for generator tools MCP entrypoints."""

import pytest
from unittest.mock import Mock, patch

from triads.tools.generator.entrypoint import GeneratorTools
from triads.tools.shared import ToolResult


class TestGenerateAgents:
    """Tests for generate_agents MCP tool."""

    def test_generate_agents_returns_mcp_compliant_result(self):
        """generate_agents returns ToolResult in MCP format."""
        result = GeneratorTools.generate_agents("debugging", "Python")

        assert isinstance(result, ToolResult)
        assert result.success is True
        assert len(result.content) > 0

    def test_generate_agents_returns_resources_not_text(self):
        """generate_agents returns resources, not text content."""
        result = GeneratorTools.generate_agents("debugging", "Python")

        assert result.success is True
        # All content items should be resources
        for item in result.content:
            assert item["type"] == "resource"
            assert "resource" in item

    def test_generate_agents_resource_has_required_fields(self):
        """generate_agents resources have uri, mimeType, and text."""
        result = GeneratorTools.generate_agents("debugging", "Python")

        assert result.success is True
        for item in result.content:
            resource = item["resource"]
            assert "uri" in resource
            assert "mimeType" in resource
            assert "text" in resource

    def test_generate_agents_resource_uri_format(self):
        """generate_agents resources use correct URI format."""
        result = GeneratorTools.generate_agents("debugging", "Python")

        assert result.success is True
        for item in result.content:
            uri = item["resource"]["uri"]
            # URI should be: triads://agents/{triad_id}/{agent_name}.md
            assert uri.startswith("triads://agents/")
            assert uri.endswith(".md")
            assert "debugging" in uri

    def test_generate_agents_resource_mimetype(self):
        """generate_agents resources have correct MIME type."""
        result = GeneratorTools.generate_agents("debugging", "Python")

        assert result.success is True
        for item in result.content:
            mime_type = item["resource"]["mimeType"]
            assert mime_type == "text/markdown"

    def test_generate_agents_resource_content(self):
        """generate_agents resources contain agent markdown content."""
        result = GeneratorTools.generate_agents("debugging", "Python")

        assert result.success is True
        assert len(result.content) >= 1

        # Check first resource has valid markdown
        first_resource = result.content[0]["resource"]
        text = first_resource["text"]
        assert "---" in text  # YAML frontmatter
        assert "name:" in text
        assert "role:" in text
        assert "tools:" in text

    def test_generate_agents_debugging_workflow(self):
        """generate_agents creates debugging workflow agents."""
        result = GeneratorTools.generate_agents("debugging", "Python Application")

        assert result.success is True
        assert len(result.content) == 3  # investigator, fixer, verifier

        agent_names = [item["resource"]["uri"].split("/")[-1].replace(".md", "")
                       for item in result.content]
        assert "investigator" in agent_names
        assert "fixer" in agent_names
        assert "verifier" in agent_names

    def test_generate_agents_software_development_workflow(self):
        """generate_agents creates software development workflow agents."""
        result = GeneratorTools.generate_agents("software-development", "Web App")

        assert result.success is True
        assert len(result.content) >= 1

        # Should have at least designer agent
        uris = [item["resource"]["uri"] for item in result.content]
        assert any("designer" in uri for uri in uris)

    def test_generate_agents_includes_domain_in_content(self):
        """generate_agents includes domain context in agent content."""
        result = GeneratorTools.generate_agents("debugging", "Python Microservice")

        assert result.success is True

        # Domain should appear in at least one agent's content
        domain_found = False
        for item in result.content:
            if "Python Microservice" in item["resource"]["text"]:
                domain_found = True
                break

        assert domain_found, "Domain not found in any agent content"

    def test_generate_agents_error_returns_proper_format(self):
        """generate_agents returns error in MCP format when generation fails."""
        with patch(
            "triads.tools.generator.entrypoint.bootstrap_generator_service"
        ) as mock_bootstrap:
            from triads.tools.generator.repository import GeneratorRepositoryError

            mock_service = Mock()
            mock_service.generate_agents.side_effect = GeneratorRepositoryError(
                "Invalid workflow_type"
            )
            mock_bootstrap.return_value = mock_service

            result = GeneratorTools.generate_agents("", "test domain")

            assert isinstance(result, ToolResult)
            assert result.success is False
            assert result.error is not None

    def test_generate_agents_multiple_resources(self):
        """generate_agents can return multiple agent resources."""
        result = GeneratorTools.generate_agents("debugging", "Python")

        assert result.success is True
        assert len(result.content) > 1  # Multiple agents

        # Each should be a separate resource
        uris = [item["resource"]["uri"] for item in result.content]
        assert len(uris) == len(set(uris))  # All URIs unique


class TestToolSignatures:
    """Tests for MCP tool signatures."""

    def test_generate_agents_has_proper_signature(self):
        """generate_agents tool exists with proper signature."""
        assert hasattr(GeneratorTools, "generate_agents")
        assert callable(GeneratorTools.generate_agents)

    def test_generate_agents_accepts_required_parameters(self):
        """generate_agents accepts workflow_type and domain parameters."""
        # Should not raise
        result = GeneratorTools.generate_agents("debugging", "Python")
        assert isinstance(result, ToolResult)


class TestResourceFormatValidation:
    """Tests specifically for MCP Resource format compliance."""

    def test_resource_format_matches_mcp_spec(self):
        """Resources match MCP specification format."""
        result = GeneratorTools.generate_agents("debugging", "Python")

        assert result.success is True

        for item in result.content:
            # Top-level structure
            assert "type" in item
            assert item["type"] == "resource"
            assert "resource" in item

            # Resource structure
            resource = item["resource"]
            assert isinstance(resource, dict)
            assert "uri" in resource
            assert "mimeType" in resource
            assert "text" in resource

            # Field types
            assert isinstance(resource["uri"], str)
            assert isinstance(resource["mimeType"], str)
            assert isinstance(resource["text"], str)

    def test_resource_text_is_non_empty(self):
        """Resource text field is non-empty."""
        result = GeneratorTools.generate_agents("debugging", "Python")

        assert result.success is True
        for item in result.content:
            text = item["resource"]["text"]
            assert len(text) > 0
            assert text.strip() != ""

    def test_no_text_type_content_returned(self):
        """generate_agents does NOT return text-type content."""
        result = GeneratorTools.generate_agents("debugging", "Python")

        assert result.success is True
        # All content should be resources, not text
        for item in result.content:
            assert item["type"] != "text"
            assert item["type"] == "resource"
