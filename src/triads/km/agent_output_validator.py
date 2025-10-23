"""Agent output validation.

This module parses and validates [GRAPH_UPDATE] blocks from agent outputs
BEFORE they're applied to knowledge graphs. Prevents corrupted agent output
from reaching graph files.

Validates:
- Block structure (proper [GRAPH_UPDATE]...[/GRAPH_UPDATE] tags)
- YAML-like content parsing
- Required fields (node_id, node_type, label, etc.)
- Field types and values (confidence in [0.0, 1.0], valid node types)
- Integration with schema validator for consistency
"""

from __future__ import annotations

import logging
import re
from typing import Any

from triads.km.schema_validator import VALID_NODE_TYPES

# Initialize module logger
logger = logging.getLogger(__name__)


# ============================================================================
# Exceptions
# ============================================================================


class ParseError(Exception):
    """Raised when parsing [GRAPH_UPDATE] block fails."""

    pass


class ValidationError(Exception):
    """Raised when validating [GRAPH_UPDATE] block fails."""

    pass


# ============================================================================
# Data Models
# ============================================================================


class GraphUpdateBlock:
    """Represents a parsed [GRAPH_UPDATE] block from agent output."""

    def __init__(self, raw_content: str, parsed_data: dict[str, Any]) -> None:
        self.raw_content = raw_content
        self.parsed_data = parsed_data
        self.is_valid = False

        # Expose common fields as attributes for convenience
        self.type = parsed_data.get("type")
        self.node_id = parsed_data.get("node_id")
        self.node_type = parsed_data.get("node_type")
        self.label = parsed_data.get("label")
        self.confidence = parsed_data.get("confidence")
        self.source = parsed_data.get("source")
        self.target = parsed_data.get("target")

    def to_node_dict(self) -> dict[str, Any]:
        """Convert block to node dictionary for graph insertion.

        Returns:
            Node dictionary with normalized field names (lowercase type)
        """
        node = {
            "id": self.node_id,
            "label": self.label,
            "type": self.node_type.lower() if self.node_type else None,
        }

        # Add optional fields if present
        if "description" in self.parsed_data:
            node["description"] = self.parsed_data["description"]
        if "confidence" in self.parsed_data:
            node["confidence"] = self.parsed_data["confidence"]
        if "file_path" in self.parsed_data:
            node["file_path"] = self.parsed_data["file_path"]
        if "lines" in self.parsed_data:
            node["lines"] = self.parsed_data["lines"]
        if "implements" in self.parsed_data:
            node["implements"] = self.parsed_data["implements"]
        if "created_by" in self.parsed_data:
            node["created_by"] = self.parsed_data["created_by"]

        return node

    def to_edge_dict(self) -> dict[str, Any]:
        """Convert block to edge dictionary for graph insertion.

        Returns:
            Edge dictionary with source, target, and optional fields
        """
        edge = {
            "source": self.source,
            "target": self.target,
        }

        # Add optional fields if present
        if "key" in self.parsed_data:
            edge["key"] = self.parsed_data["key"]
        if "rationale" in self.parsed_data:
            edge["rationale"] = self.parsed_data["rationale"]
        if "confidence" in self.parsed_data:
            edge["confidence"] = self.parsed_data["confidence"]
        if "created_by" in self.parsed_data:
            edge["created_by"] = self.parsed_data["created_by"]

        return edge


# ============================================================================
# AgentOutputValidator: Parse and validate agent outputs
# ============================================================================


class AgentOutputValidator:
    """Parse and validate [GRAPH_UPDATE] blocks from agent outputs.

    Security:
        - Validates all fields before applying to graphs
        - Prevents malformed data from corrupting graphs
        - Atomic updates (all or nothing)

    Example:
        validator = AgentOutputValidator()
        blocks = validator.parse_and_validate(agent_output)
        validator.apply_updates(blocks, loader, "triad_name")
    """

    # Pattern to find [GRAPH_UPDATE] blocks
    BLOCK_PATTERN = re.compile(
        r"\[GRAPH_UPDATE\](.*?)\[/GRAPH_UPDATE\]",
        re.DOTALL,
    )

    # Pattern to parse key: value lines (simple YAML-like)
    LINE_PATTERN = re.compile(r"^(\w+):\s*(.*)$")

    def __init__(self) -> None:
        pass

    def _parse_block_content(self, content: str) -> dict[str, Any]:
        """Parse YAML-like content from a [GRAPH_UPDATE] block.

        Args:
            content: Raw block content between tags

        Returns:
            Dictionary of parsed key-value pairs

        Raises:
            ParseError: If content cannot be parsed
        """
        content = content.strip()
        if not content:
            raise ParseError("Block content is empty")

        parsed = {}
        for line in content.split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            match = self.LINE_PATTERN.match(line)
            if not match:
                raise ParseError(f"Invalid line format (expected 'key: value'): {line}")

            key, value = match.groups()
            value = value.strip()

            # Parse numeric values (only if ALL characters are numeric)
            # Don't parse things like "1-150" or "auth-system" as numbers
            try:
                if "." in value:
                    # Try parsing as float
                    parsed[key] = float(value)
                elif value.isdigit() or (value.startswith("-") and value[1:].isdigit()):
                    # Try parsing as int
                    parsed[key] = int(value)
                else:
                    # Keep as string
                    parsed[key] = value
            except ValueError:
                # If parsing fails, keep as string
                parsed[key] = value

        return parsed

    def parse_update_blocks(self, agent_output: str) -> list[GraphUpdateBlock]:
        """Parse [GRAPH_UPDATE] blocks from agent output.

        Args:
            agent_output: Full agent output text

        Returns:
            List of parsed GraphUpdateBlock objects

        Raises:
            ParseError: If block structure is malformed
        """
        blocks = []

        # Check for unclosed blocks
        open_count = agent_output.count("[GRAPH_UPDATE]")
        close_count = agent_output.count("[/GRAPH_UPDATE]")
        if open_count != close_count:
            raise ParseError(
                f"Malformed blocks: {open_count} opening tags but {close_count} closing tags (missing closing tag)"
            )

        # Find and parse all blocks
        for match in self.BLOCK_PATTERN.finditer(agent_output):
            raw_content = match.group(1)
            try:
                parsed_data = self._parse_block_content(raw_content)
                block = GraphUpdateBlock(raw_content, parsed_data)
                blocks.append(block)
            except ParseError:
                # Re-raise parse errors with context
                raise

        return blocks

    def _validate_block(self, block: GraphUpdateBlock) -> None:
        """Validate a GraphUpdateBlock.

        Args:
            block: Block to validate

        Raises:
            ValidationError: If validation fails
        """
        # Check update type
        if block.type not in ["add_node", "add_edge"]:
            raise ValidationError(
                f"Invalid update type '{block.type}'. Must be 'add_node' or 'add_edge'"
            )

        if block.type == "add_node":
            self._validate_node_block(block)
        elif block.type == "add_edge":
            self._validate_edge_block(block)

    def _validate_node_block(self, block: GraphUpdateBlock) -> None:
        """Validate an add_node block.

        Args:
            block: Block to validate

        Raises:
            ValidationError: If validation fails
        """
        # Required fields
        if not block.node_id:
            raise ValidationError("Missing required field 'node_id' for add_node")
        if not block.node_type:
            raise ValidationError("Missing required field 'node_type' for add_node")
        if not block.label:
            raise ValidationError("Missing required field 'label' for add_node")

        # Validate node_type
        if block.node_type.lower() not in VALID_NODE_TYPES:
            valid_types = ", ".join(sorted(VALID_NODE_TYPES))
            raise ValidationError(
                f"Invalid node_type '{block.node_type}'. Valid types: {valid_types}"
            )

        # Validate confidence if present
        if block.confidence is not None:
            if not isinstance(block.confidence, (int, float)):
                raise ValidationError(
                    f"Confidence must be numeric, got {type(block.confidence).__name__}"
                )
            if block.confidence < 0.0 or block.confidence > 1.0:
                raise ValidationError(
                    f"Confidence {block.confidence} outside valid range [0.0, 1.0]"
                )

    def _validate_edge_block(self, block: GraphUpdateBlock) -> None:
        """Validate an add_edge block.

        Args:
            block: Block to validate

        Raises:
            ValidationError: If validation fails
        """
        # Required fields
        if not block.source:
            raise ValidationError("Missing required field 'source' for add_edge")
        if not block.target:
            raise ValidationError("Missing required field 'target' for add_edge")

        # Validate confidence if present
        if block.confidence is not None:
            if not isinstance(block.confidence, (int, float)):
                raise ValidationError(
                    f"Confidence must be numeric, got {type(block.confidence).__name__}"
                )
            if block.confidence < 0.0 or block.confidence > 1.0:
                raise ValidationError(
                    f"Confidence {block.confidence} outside valid range [0.0, 1.0]"
                )

    def parse_and_validate(self, agent_output: str) -> list[GraphUpdateBlock]:
        """Parse and validate [GRAPH_UPDATE] blocks.

        Args:
            agent_output: Full agent output text

        Returns:
            List of validated GraphUpdateBlock objects

        Raises:
            ParseError: If block structure is malformed
            ValidationError: If block content is invalid
        """
        blocks = self.parse_update_blocks(agent_output)

        # Validate each block
        for block in blocks:
            self._validate_block(block)
            block.is_valid = True

        return blocks

    def apply_updates(
        self,
        blocks: list[GraphUpdateBlock],
        loader: Any,
        triad: str,
    ) -> bool:
        """Apply validated updates to graph.

        Args:
            blocks: List of validated GraphUpdateBlock objects
            loader: GraphLoader instance
            triad: Triad name to update

        Returns:
            True if all updates applied successfully

        Raises:
            ValidationError: If any update is invalid
        """
        # Verify all blocks are validated
        for block in blocks:
            if not block.is_valid:
                raise ValidationError(
                    "Cannot apply unvalidated block. Call parse_and_validate first."
                )

        # Load existing graph
        try:
            graph = loader.load_graph(triad)
        except Exception:
            # Create new graph if doesn't exist
            graph = {"nodes": [], "edges": []}

        # Apply updates atomically (build new graph, save at end)
        for block in blocks:
            if block.type == "add_node":
                node = block.to_node_dict()
                graph["nodes"].append(node)
            elif block.type == "add_edge":
                edge = block.to_edge_dict()
                graph["edges"].append(edge)

        # Save updated graph (with validation in save_graph)
        success = loader.save_graph(triad, graph)
        if not success:
            raise ValidationError("Failed to save updated graph")

        logger.info(
            "Applied %d updates to graph '%s'",
            len(blocks),
            triad,
        )

        return True
