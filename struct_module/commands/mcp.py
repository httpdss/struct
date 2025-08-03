import asyncio
import logging
from struct_module.commands import Command
from struct_module.mcp_server import StructMCPServer


# MCP command class for starting the MCP server
class MCPCommand(Command):
    def __init__(self, parser):
        super().__init__(parser)
        parser.add_argument('--server', action='store_true',
                          help='Start the MCP server for stdio communication')
        parser.set_defaults(func=self.execute)

    def execute(self, args):
        if args.server:
            self.logger.info("Starting MCP server for struct tool")
            asyncio.run(self._start_mcp_server())
        else:
            print("MCP (Model Context Protocol) support for struct tool")
            print("\nAvailable options:")
            print("  --server    Start the MCP server for stdio communication")
            print("\nMCP tools available:")
            print("  - list_structures: List all available structure definitions")
            print("  - get_structure_info: Get detailed information about a structure")
            print("  - generate_structure: Generate structures with various options")
            print("  - validate_structure: Validate structure configuration files")
            print("\nTo integrate with MCP clients, use: struct mcp --server")

    async def _start_mcp_server(self):
        """Start the MCP server."""
        try:
            server = StructMCPServer()
            await server.run()
        except Exception as e:
            self.logger.error(f"Error starting MCP server: {e}")
            raise
