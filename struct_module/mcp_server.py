"""
MCP Server implementation for the struct tool.

This module provides MCP (Model Context Protocol) support for:
1. Listing available structures
2. Getting detailed information about structures
3. Generating structures with various options
4. Validating structure configurations
"""
import asyncio
import json
import logging
import os
import sys
import yaml
from typing import Any, Dict, List, Optional, Sequence

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    TextContent,
    Tool,
)

from struct_module.commands.generate import GenerateCommand
from struct_module.commands.validate import ValidateCommand
from struct_module.commands.info import InfoCommand
from struct_module.commands.list import ListCommand


class StructMCPServer:
    """MCP Server for struct tool operations."""

    def __init__(self):
        self.server = Server("struct-mcp-server")
        self.logger = logging.getLogger(__name__)

        # Register MCP tools
        self.register_tools()

    def register_tools(self):
        """Register all available MCP tools."""

        @self.server.list_tools()
        async def handle_list_tools(request: ListToolsRequest) -> List[Tool]:
            """List all available MCP tools."""
            return [
                Tool(
                    name="list_structures",
                    description="List all available structure definitions",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "structures_path": {
                                "type": "string",
                                "description": "Optional custom path to structure definitions",
                            }
                        },
                    },
                ),
                Tool(
                    name="get_structure_info",
                    description="Get detailed information about a specific structure",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "structure_name": {
                                "type": "string",
                                "description": "Name of the structure to get info about",
                            },
                            "structures_path": {
                                "type": "string",
                                "description": "Optional custom path to structure definitions",
                            }
                        },
                        "required": ["structure_name"],
                    },
                ),
                Tool(
                    name="generate_structure",
                    description="Generate a project structure using specified definition and options",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "structure_definition": {
                                "type": "string",
                                "description": "Name or path to the structure definition",
                            },
                            "base_path": {
                                "type": "string",
                                "description": "Base path where the structure should be generated",
                            },
                            "output": {
                                "type": "string",
                                "enum": ["console", "files"],
                                "description": "Output mode: console for stdout or files for actual generation",
                                "default": "files"
                            },
                            "dry_run": {
                                "type": "boolean",
                                "description": "Perform a dry run without creating actual files",
                                "default": False
                            },
                            "mappings": {
                                "type": "object",
                                "description": "Variable mappings for template substitution",
                                "additionalProperties": {"type": "string"}
                            },
                            "structures_path": {
                                "type": "string",
                                "description": "Optional custom path to structure definitions",
                            }
                        },
                        "required": ["structure_definition", "base_path"],
                    },
                ),
                Tool(
                    name="validate_structure",
                    description="Validate a structure configuration YAML file",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "yaml_file": {
                                "type": "string",
                                "description": "Path to the YAML configuration file to validate",
                            }
                        },
                        "required": ["yaml_file"],
                    },
                ),
            ]

        @self.server.call_tool()
        async def handle_call_tool(request: CallToolRequest) -> CallToolResult:
            """Handle MCP tool calls."""
            try:
                if request.name == "list_structures":
                    return await self._handle_list_structures(request.arguments or {})
                elif request.name == "get_structure_info":
                    return await self._handle_get_structure_info(request.arguments or {})
                elif request.name == "generate_structure":
                    return await self._handle_generate_structure(request.arguments or {})
                elif request.name == "validate_structure":
                    return await self._handle_validate_structure(request.arguments or {})
                else:
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=f"Unknown tool: {request.name}"
                            )
                        ]
                    )
            except Exception as e:
                self.logger.error(f"Error handling tool call {request.name}: {e}")
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Error: {str(e)}"
                        )
                    ]
                )

    async def _handle_list_structures(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle list_structures tool call."""
        try:
            # Mock an ArgumentParser-like object
            class MockArgs:
                def __init__(self, structures_path: Optional[str] = None):
                    self.structures_path = structures_path

            args = MockArgs(arguments.get("structures_path"))

            # Get the list of structures by using the ListCommand logic directly
            # We'll implement the logic inline since we can't create a command without a parser

            # Capture the structures list
            this_file = os.path.dirname(os.path.realpath(__file__))
            contribs_path = os.path.join(this_file, "contribs")

            if args.structures_path:
                final_path = args.structures_path
                paths_to_list = [final_path, contribs_path]
            else:
                paths_to_list = [contribs_path]

            all_structures = set()
            for path in paths_to_list:
                if os.path.exists(path):
                    for root, _, files in os.walk(path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            rel_path = os.path.relpath(file_path, path)
                            if file.endswith(".yaml"):
                                rel_path = rel_path[:-5]
                                if path != contribs_path:
                                    rel_path = f"+ {rel_path}"
                                all_structures.add(rel_path)

            sorted_list = sorted(all_structures)

            result_text = "📃 Available structures:\n\n"
            for structure in sorted_list:
                result_text += f" - {structure}\n"

            result_text += "\nNote: Structures with '+' sign are custom structures"

            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=result_text
                    )
                ]
            )
        except Exception as e:
            self.logger.error(f"Error in list_structures: {e}")
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Error listing structures: {str(e)}"
                    )
                ]
            )

    async def _handle_get_structure_info(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle get_structure_info tool call."""
        try:
            structure_name = arguments.get("structure_name")
            structures_path = arguments.get("structures_path")

            if not structure_name:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text="Error: structure_name is required"
                        )
                    ]
                )

            # Load the structure configuration
            if structure_name.startswith("file://") and structure_name.endswith(".yaml"):
                file_path = structure_name[7:]
            else:
                if structures_path is None:
                    this_file = os.path.dirname(os.path.realpath(__file__))
                    file_path = os.path.join(this_file, "contribs", f"{structure_name}.yaml")
                else:
                    file_path = os.path.join(structures_path, f"{structure_name}.yaml")

            if not os.path.exists(file_path):
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"❗ Structure not found: {file_path}"
                        )
                    ]
                )

            with open(file_path, 'r') as f:
                config = yaml.safe_load(f)

            result_text = "📒 Structure definition\n\n"
            result_text += f"   📌 Name: {structure_name}\n\n"
            result_text += f"   📌 Description: {config.get('description', 'No description')}\n\n"

            if config.get('files'):
                result_text += "   📌 Files:\n"
                for item in config.get('files', []):
                    for name, content in item.items():
                        result_text += f"       - {name}\n"

            if config.get('folders'):
                result_text += "   📌 Folders:\n"
                for folder in config.get('folders', []):
                    result_text += f"     - {folder}\n"

            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=result_text
                    )
                ]
            )
        except Exception as e:
            self.logger.error(f"Error in get_structure_info: {e}")
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Error getting structure info: {str(e)}"
                    )
                ]
            )

    async def _handle_generate_structure(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle generate_structure tool call."""
        try:
            structure_definition = arguments.get("structure_definition")
            base_path = arguments.get("base_path")
            output_mode = arguments.get("output", "files")
            dry_run = arguments.get("dry_run", False)
            mappings = arguments.get("mappings", {})
            structures_path = arguments.get("structures_path")

            if not structure_definition or not base_path:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text="Error: structure_definition and base_path are required"
                        )
                    ]
                )

            # Mock an ArgumentParser-like object
            class MockArgs:
                def __init__(self):
                    self.structure_definition = structure_definition
                    self.base_path = base_path
                    self.output = output_mode
                    self.dry_run = dry_run
                    self.structures_path = structures_path
                    self.mappings = mappings if mappings else None
                    self.log = "INFO"
                    self.config_file = None
                    self.log_file = None

            args = MockArgs()

            # Capture stdout for console output mode
            if output_mode == "console":
                from io import StringIO
                captured_output = StringIO()
                old_stdout = sys.stdout
                sys.stdout = captured_output

                try:
                    # Use the GenerateCommand to generate the structure
                    generate_cmd = GenerateCommand(None)
                    generate_cmd.execute(args)

                    result_text = captured_output.getvalue()
                    if not result_text.strip():
                        result_text = "Structure generation completed successfully"

                finally:
                    sys.stdout = old_stdout
            else:
                # Generate files normally
                generate_cmd = GenerateCommand(None)
                generate_cmd.execute(args)

                if dry_run:
                    result_text = f"Dry run completed for structure '{structure_definition}' at '{base_path}'"
                else:
                    result_text = f"Structure '{structure_definition}' generated successfully at '{base_path}'"

            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=result_text
                    )
                ]
            )
        except Exception as e:
            self.logger.error(f"Error in generate_structure: {e}")
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Error generating structure: {str(e)}"
                    )
                ]
            )

    async def _handle_validate_structure(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle validate_structure tool call."""
        try:
            yaml_file = arguments.get("yaml_file")

            if not yaml_file:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text="Error: yaml_file is required"
                        )
                    ]
                )

            # Mock an ArgumentParser-like object
            class MockArgs:
                def __init__(self):
                    self.yaml_file = yaml_file
                    self.log = "INFO"
                    self.config_file = None
                    self.log_file = None

            args = MockArgs()

            # Capture stdout for validation output
            from io import StringIO
            captured_output = StringIO()
            old_stdout = sys.stdout
            sys.stdout = captured_output

            try:
                # Use the ValidateCommand to validate
                validate_cmd = ValidateCommand(None)
                validate_cmd.execute(args)

                result_text = captured_output.getvalue()
                if not result_text.strip():
                    result_text = f"✅ YAML file '{yaml_file}' is valid"

            finally:
                sys.stdout = old_stdout

            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=result_text
                    )
                ]
            )
        except Exception as e:
            self.logger.error(f"Error in validate_structure: {e}")
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"❌ Validation error: {str(e)}"
                    )
                ]
            )

    async def run(self):
        """Run the MCP server using stdio transport."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="struct-mcp-server",
                    server_version="1.0.0",
                    capabilities={}
                )
            )


async def main():
    """Main entry point for the MCP server."""
    logging.basicConfig(level=logging.INFO)
    server = StructMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
