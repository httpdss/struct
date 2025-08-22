import asyncio
import logging
from struct_module.commands import Command
from struct_module.mcp_server import StructMCPServer


# MCP command class for starting the MCP server
class MCPCommand(Command):
    def __init__(self, parser):
        super().__init__(parser)
        parser.description = "MCP (Model Context Protocol) support for struct tool"
        parser.add_argument('--server', action='store_true',
                          help='Start the MCP server')
        parser.add_argument('--transport', choices=['stdio', 'http'], default='stdio',
                          help='Transport protocol to use (default: stdio)')
        parser.add_argument('--host', default='localhost',
                          help='Host to bind HTTP server to (default: localhost)')
        parser.add_argument('--port', type=int, default=8000,
                          help='Port to bind HTTP server to (default: 8000)')
        parser.set_defaults(func=self.execute)

    def execute(self, args):
        if args.server:
            self.logger.info(f"Starting MCP server with {args.transport} transport")
            asyncio.run(self._start_mcp_server(args))
        else:
            print("MCP (Model Context Protocol) support for struct tool")
            print("\nAvailable options:")
            print("  --server              Start the MCP server")
            print("  --transport PROTO     Transport protocol: stdio (default) or http")
            print("  --host HOST           Host for HTTP server (default: localhost)")
            print("  --port PORT           Port for HTTP server (default: 8000)")
            print("\nMCP tools available:")
            print("  - list_structures: List all available structure definitions")
            print("  - get_structure_info: Get detailed information about a structure")
            print("  - generate_structure: Generate structures with various options")
            print("  - validate_structure: Validate structure configuration files")
            print("\nExamples:")
            print("  struct mcp --server                           # stdio transport")
            print("  struct mcp --server --transport http          # HTTP transport")
            print("  struct mcp --server --transport http --port 8001  # HTTP on custom port")

    async def _start_mcp_server(self, args):
        """Start the MCP server with the specified transport."""
        try:
            if args.transport == 'stdio':
                # Use the existing stdio-based MCP server
                server = StructMCPServer()
                await server.run()
            elif args.transport == 'http':
                # Use the HTTP-based MCP server
                await self._start_http_server(args.host, args.port)
        except Exception as e:
            self.logger.error(f"Error starting MCP server: {e}")
            raise

    async def _start_http_server(self, host: str, port: int):
        """Start the HTTP MCP server."""
        # Import HTTP server components
        from fastapi import FastAPI, HTTPException
        from pydantic import BaseModel
        import uvicorn

        # Create a reference to the MCP server instance
        struct_server = StructMCPServer()

        app = FastAPI(
            title="Struct MCP Server",
            description="HTTP-based MCP server for the Struct tool",
            version="1.0.0"
        )

        class MCPRequest(BaseModel):
            jsonrpc: str = "2.0"
            id: int
            method: str
            params: dict = {}

        @app.post("/mcp")
        async def handle_mcp_request(request: MCPRequest):
            """Handle MCP JSON-RPC requests."""
            try:
                if request.method == "tools/list":
                    # Get tools list
                    tools_response = await self._get_tools_list()
                    return {
                        "jsonrpc": "2.0",
                        "id": request.id,
                        "result": {"tools": tools_response}
                    }

                elif request.method == "tools/call":
                    tool_name = request.params.get("name")
                    arguments = request.params.get("arguments", {})

                    if not tool_name:
                        raise HTTPException(status_code=400, detail="Tool name is required")

                    # Call the tool using existing server logic
                    result = await self._handle_tool_call(struct_server, tool_name, arguments)
                    return {
                        "jsonrpc": "2.0",
                        "id": request.id,
                        "result": result
                    }

                else:
                    return {
                        "jsonrpc": "2.0",
                        "id": request.id,
                        "error": {
                            "code": -32601,
                            "message": f"Method not found: {request.method}"
                        }
                    }

            except Exception as e:
                self.logger.error(f"Error handling MCP request: {e}")
                return {
                    "jsonrpc": "2.0",
                    "id": request.id,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }

        @app.get("/")
        async def root():
            return {"message": "Struct MCP Server", "version": "1.0.0"}

        @app.get("/health")
        async def health():
            return {"status": "healthy"}

        # Configure uvicorn
        config = uvicorn.Config(
            app=app,
            host=host,
            port=port,
            log_level="info"
        )

        server = uvicorn.Server(config)

        print(f"🚀 Starting Struct HTTP MCP Server on http://{host}:{port}")
        print(f"📋 MCP endpoint: http://{host}:{port}/mcp")
        print(f"📖 API docs: http://{host}:{port}/docs")
        print(f"🩺 Health check: http://{host}:{port}/health")
        print("Press Ctrl+C to stop the server")

        await server.serve()

    async def _get_tools_list(self):
        """Get the list of available MCP tools."""
        return [
            {
                "name": "list_structures",
                "description": "List all available structure definitions",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "structures_path": {
                            "type": "string",
                            "description": "Optional custom path to structure definitions",
                        }
                    },
                },
            },
            {
                "name": "get_structure_info",
                "description": "Get detailed information about a specific structure",
                "inputSchema": {
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
            },
            {
                "name": "generate_structure",
                "description": "Generate a project structure using specified definition and options",
                "inputSchema": {
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
            },
            {
                "name": "validate_structure",
                "description": "Validate a structure configuration YAML file",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "yaml_file": {
                            "type": "string",
                            "description": "Path to the YAML configuration file to validate",
                        }
                    },
                    "required": ["yaml_file"],
                },
            },
        ]

    async def _handle_tool_call(self, struct_server, tool_name: str, arguments: dict):
        """Handle tool call and return result in MCP format."""
        try:
            # Use the updated struct_server methods that have ArgumentParser fixes
            if tool_name == "list_structures":
                result = await struct_server._handle_list_structures(arguments)
            elif tool_name == "get_structure_info":
                result = await struct_server._handle_get_structure_info(arguments)
            elif tool_name == "generate_structure":
                result = await struct_server._handle_generate_structure(arguments)
            elif tool_name == "validate_structure":
                result = await struct_server._handle_validate_structure(arguments)
            else:
                return {
                    "content": [{
                        "type": "text",
                        "text": f"Unknown tool: {tool_name}"
                    }]
                }

            # Convert CallToolResult to dict format
            content_list = []
            if result.content:
                for content in result.content:
                    if hasattr(content, 'text'):
                        content_list.append({
                            "type": "text",
                            "text": content.text
                        })

            return {"content": content_list}

        except Exception as e:
            self.logger.error(f"Error in tool call {tool_name}: {e}")
            return {
                "content": [{
                    "type": "text",
                    "text": f"Error: {str(e)}"
                }]
            }
