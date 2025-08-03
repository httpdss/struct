"""
Tests for MCP (Model Context Protocol) integration.
"""
import asyncio
import json
import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock
import yaml

from struct_module.mcp_server import StructMCPServer
from mcp.types import CallToolRequest, TextContent


class TestMCPIntegration(unittest.TestCase):
    """Test cases for MCP integration."""

    def setUp(self):
        """Set up test fixtures."""
        self.server = StructMCPServer()

    def test_server_initialization(self):
        """Test that MCP server initializes correctly."""
        self.assertIsNotNone(self.server)
        self.assertIsNotNone(self.server.server)
        self.assertEqual(self.server.server.name, "struct-mcp-server")

    def test_list_structures_tool(self):
        """Test the list_structures MCP tool."""
        async def run_test():
            request = CallToolRequest(
                method="tools/call",
                params={
                    "name": "list_structures",
                    "arguments": {}
                }
            )
            request.name = "list_structures"
            request.arguments = {}

            result = await self.server._handle_list_structures({})

            self.assertIsNotNone(result)
            self.assertEqual(len(result.content), 1)
            self.assertIsInstance(result.content[0], TextContent)
            self.assertIn("Available structures", result.content[0].text)

        asyncio.run(run_test())

    def test_get_structure_info_tool(self):
        """Test the get_structure_info MCP tool."""
        async def run_test():
            # Test with missing structure_name
            result = await self.server._handle_get_structure_info({})
            self.assertIn("Error: structure_name is required", result.content[0].text)

            # Test with non-existent structure
            result = await self.server._handle_get_structure_info({
                "structure_name": "non_existent_structure"
            })
            self.assertIn("Structure not found", result.content[0].text)

        asyncio.run(run_test())

    def test_generate_structure_tool(self):
        """Test the generate_structure MCP tool."""
        async def run_test():
            # Test with missing required parameters
            result = await self.server._handle_generate_structure({})
            self.assertIn("structure_definition and base_path are required", result.content[0].text)

            # Test with valid parameters but non-existent structure
            with tempfile.TemporaryDirectory() as temp_dir:
                result = await self.server._handle_generate_structure({
                    "structure_definition": "non_existent",
                    "base_path": temp_dir,
                    "output": "console"
                })
                # Should handle gracefully, even if structure doesn't exist

        asyncio.run(run_test())

    def test_validate_structure_tool(self):
        """Test the validate_structure MCP tool."""
        async def run_test():
            # Test with missing yaml_file
            result = await self.server._handle_validate_structure({})
            self.assertIn("Error: yaml_file is required", result.content[0].text)

            # Test with valid YAML file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump({
                    'files': [
                        {'test.txt': {'content': 'Hello World'}}
                    ],
                    'description': 'Test structure'
                }, f)
                f.flush()

                try:
                    result = await self.server._handle_validate_structure({
                        "yaml_file": f.name
                    })
                    # Should validate successfully or provide validation feedback
                    self.assertIsNotNone(result.content[0].text)
                finally:
                    os.unlink(f.name)

        asyncio.run(run_test())

    def test_run_async_methods(self):
        """Test that async methods can be called."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            # Test list_structures
            result = loop.run_until_complete(
                self.server._handle_list_structures({})
            )
            self.assertIsNotNone(result)

            # Test get_structure_info with error case
            result = loop.run_until_complete(
                self.server._handle_get_structure_info({})
            )
            self.assertIsNotNone(result)

        finally:
            loop.close()


class TestMCPCommands(unittest.TestCase):
    """Test MCP command line integration."""

    def test_mcp_command_import(self):
        """Test that MCP command can be imported."""
        from struct_module.commands.mcp import MCPCommand
        self.assertIsNotNone(MCPCommand)

    def test_list_command_mcp_option(self):
        """Test that list command has MCP option."""
        from struct_module.commands.list import ListCommand
        import argparse

        parser = argparse.ArgumentParser()
        subparser = parser.add_subparsers()
        list_parser = subparser.add_parser('list')

        list_cmd = ListCommand(list_parser)

        # Parse args with MCP flag
        args = parser.parse_args(['list', '--mcp'])
        self.assertTrue(hasattr(args, 'mcp'))

    def test_info_command_mcp_option(self):
        """Test that info command has MCP option."""
        from struct_module.commands.info import InfoCommand
        import argparse

        parser = argparse.ArgumentParser()
        subparser = parser.add_subparsers()
        info_parser = subparser.add_parser('info')

        info_cmd = InfoCommand(info_parser)

        # Parse args with MCP flag
        args = parser.parse_args(['info', 'test_structure', '--mcp'])
        self.assertTrue(hasattr(args, 'mcp'))
        self.assertEqual(args.structure_definition, 'test_structure')


if __name__ == '__main__':
    unittest.main()
