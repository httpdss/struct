# MCP (Model Context Protocol) Integration

The struct tool now supports MCP (Model Context Protocol) integration, providing a programmable interface to interact with structure definitions. This enables automation and integration with other tools, particularly AI-assisted development workflows.

## Available MCP Tools

### 1. list_structures
Lists all available structure definitions.

```json
{
  "name": "list_structures",
  "arguments": {
    "structures_path": "/path/to/custom/structures"  // optional
  }
}
```

**Parameters:**
- `structures_path` (optional): Custom path to structure definitions

### 2. get_structure_info
Get detailed information about a specific structure.

```json
{
  "name": "get_structure_info",
  "arguments": {
    "structure_name": "project/python",
    "structures_path": "/path/to/custom/structures"  // optional
  }
}
```

**Parameters:**
- `structure_name` (required): Name of the structure to get info about
- `structures_path` (optional): Custom path to structure definitions

### 3. generate_structure
Generate a project structure using specified definition and options.

```json
{
  "name": "generate_structure",
  "arguments": {
    "structure_definition": "project/python",
    "base_path": "/tmp/myproject",
    "output": "console",  // "console" or "files"
    "dry_run": false,
    "mappings": {
      "project_name": "MyProject",
      "author": "John Doe"
    },
    "structures_path": "/path/to/custom/structures"  // optional
  }
}
```

**Parameters:**
- `structure_definition` (required): Name or path to the structure definition
- `base_path` (required): Base path where the structure should be generated
- `output` (optional): Output mode - "console" for stdout or "files" for actual generation (default: "files")
- `dry_run` (optional): Perform a dry run without creating actual files (default: false)
- `mappings` (optional): Variable mappings for template substitution
- `structures_path` (optional): Custom path to structure definitions

### 4. validate_structure
Validate a structure configuration YAML file.

```json
{
  "name": "validate_structure",
  "arguments": {
    "yaml_file": "/path/to/structure.yaml"
  }
}
```

**Parameters:**
- `yaml_file` (required): Path to the YAML configuration file to validate

## Usage

### Starting the MCP Server

The struct tool supports both stdio and HTTP transports for MCP:

#### stdio Transport (Default)
```bash
struct mcp --server
# or explicitly
struct mcp --server --transport stdio
```

#### HTTP Transport (Recommended)
```bash
# Start HTTP server on default port 8000
struct mcp --server --transport http

# Start HTTP server on custom port
struct mcp --server --transport http --port 8001

# Start HTTP server on all interfaces
struct mcp --server --transport http --host 0.0.0.0
```

**HTTP Transport Benefits:**
- ✅ More reliable connection handling
- ✅ Better error reporting and debugging
- ✅ Support for multiple concurrent clients
- ✅ REST API endpoints for health checks
- ✅ Swagger documentation at `/docs`

### HTTP Endpoints (HTTP Transport)

When using HTTP transport, the following endpoints are available:

- **MCP Endpoint**: `http://localhost:8000/mcp` (JSON-RPC)
- **API Documentation**: `http://localhost:8000/docs` (Swagger UI)
- **Health Check**: `http://localhost:8000/health`
- **Server Info**: `http://localhost:8000/`

## MCP Client Integration

### HTTP Client Integration (Recommended)

For HTTP transport, you can use any HTTP client to interact with the MCP server:

```python
# Python example using httpx
import httpx
import asyncio

async def call_mcp_tool(tool_name, arguments):
    async with httpx.AsyncClient() as client:
        response = await client.post('http://localhost:8000/mcp', json={
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'tools/call',
            'params': {
                'name': tool_name,
                'arguments': arguments
            }
        })
        result = response.json()
        if 'result' in result and 'content' in result['result']:
            for content in result['result']['content']:
                if content.get('type') == 'text':
                    return content['text']
        return str(result)

# Example usage
result = asyncio.run(call_mcp_tool('list_structures', {}))
print(result)
```

### Claude Desktop Integration

**stdio Transport Configuration:**
```json
{
  "mcpServers": {
    "struct": {
      "command": "struct",
      "args": ["mcp", "--server"],
      "cwd": "/path/to/your/project"
    }
  }
}
```

**HTTP Transport Configuration** (if your MCP client supports HTTP):
```json
{
  "mcpServers": {
    "struct": {
      "url": "http://localhost:8000/mcp",
      "transport": "http"
    }
  }
}
```

### Cline/Continue Integration

**stdio Transport:**
```json
{
  "mcpServers": {
    "struct": {
      "command": "struct",
      "args": ["mcp", "--server"]
    }
  }
}
```

**HTTP Transport:**
```json
{
  "mcpServers": {
    "struct": {
      "command": "struct",
      "args": ["mcp", "--server", "--transport", "http", "--port", "8000"]
    }
  }
}
```

### Custom MCP Client Integration

#### HTTP Transport (Recommended)

```python
# Python HTTP client example
import asyncio
import httpx

class StructMCPClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()

    async def call_tool(self, tool_name, arguments):
        response = await self.client.post(f"{self.base_url}/mcp", json={
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'tools/call',
            'params': {'name': tool_name, 'arguments': arguments}
        })
        return response.json()

    async def list_tools(self):
        response = await self.client.post(f"{self.base_url}/mcp", json={
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'tools/list',
            'params': {}
        })
        return response.json()

    async def close(self):
        await self.client.aclose()

# Example usage
async def main():
    client = StructMCPClient()
    try:
        # List available tools
        tools = await client.list_tools()
        print(f"Available tools: {tools}")

        # Call a tool
        result = await client.call_tool("list_structures", {})
        print(result)
    finally:
        await client.close()

asyncio.run(main())
```

#### stdio Transport

```javascript
// Node.js stdio example
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import { Client } from '@modelcontextprotocol/sdk/client/index.js';

const transport = new StdioClientTransport({
  command: 'struct',
  args: ['mcp', '--server']
});

const client = new Client(
  {
    name: "struct-client",
    version: "1.0.0"
  },
  {
    capabilities: {}
  }
);

await client.connect(transport);
```

```python
# Python stdio example
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    server_params = StdioServerParameters(
        command="struct",
        args=["mcp", "--server"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List available tools
            tools = await session.list_tools()
            print(f"Available tools: {[tool.name for tool in tools.tools]}")

            # Call a tool
            result = await session.call_tool("list_structures", {})
            print(result.content[0].text)

if __name__ == "__main__":
    asyncio.run(main())
```

## AI-Assisted Development Workflows

The MCP integration is particularly powerful for AI-assisted development workflows:

### Console Output Mode
Using `output: "console"` with `generate_structure` allows piping structure content to stdout for subsequent AI prompts:

```bash
# Generate structure content to console for AI review
struct mcp --server | ai-tool "Review this project structure"
```

### Chaining Operations
The MCP tools can be chained together for complex workflows:

1. List available structures
2. Get detailed info about a specific structure
3. Generate the structure with custom mappings
4. Validate any custom configurations

### Integration Examples

**Example 1: Generate and Review**
```json
// 1. Generate structure to console
{
  "name": "generate_structure",
  "arguments": {
    "structure_definition": "project/python",
    "base_path": "/tmp/review",
    "output": "console"
  }
}

// 2. Use output as context for AI code review
```

**Example 2: Custom Structure Validation**
```json
// 1. Validate custom structure
{
  "name": "validate_structure",
  "arguments": {
    "yaml_file": "/path/to/custom-structure.yaml"
  }
}

// 2. If valid, generate using the custom structure
{
  "name": "generate_structure",
  "arguments": {
    "structure_definition": "file:///path/to/custom-structure.yaml",
    "base_path": "/tmp/project"
  }
}
```

## Configuration

### Environment Variables
The MCP server respects the same environment variables as the regular struct tool:
- `STRUCT_STRUCTURES_PATH`: Default path for structure definitions
- Any mapping variables used in templates

### Client Configuration Examples

#### 1. Basic Configuration
```json
{
  "command": "struct",
  "args": ["mcp", "--server"]
}
```

#### 2. With Custom Structures Path
```json
{
  "command": "struct",
  "args": ["mcp", "--server"],
  "env": {
    "STRUCT_STRUCTURES_PATH": "/path/to/custom/structures"
  }
}
```

#### 3. With Python Virtual Environment
```json
{
  "command": "/path/to/venv/bin/python",
  "args": ["-m", "struct_module.main", "mcp", "--server"],
  "cwd": "/path/to/struct/project"
}
```

#### 4. Using Shell Script Wrapper
Create a shell script `struct-mcp.sh`:
```bash
#!/bin/bash
cd /path/to/your/project
source .venv/bin/activate
struct mcp --server
```

Then configure your MCP client:
```json
{
  "command": "/path/to/struct-mcp.sh",
  "args": []
}
```

## Quick Start Guide

### Step 1: Install struct with MCP support
```bash
pip install struct
# MCP dependencies are included in requirements.txt
```

### Step 2: Test MCP server

**HTTP Transport (Recommended):**
```bash
# Test HTTP server
struct mcp --server --transport http
# Should show: 🚀 Starting Struct HTTP MCP Server on http://localhost:8000
# Open http://localhost:8000/docs in browser to see API documentation
# Press Ctrl+C to stop
```

**stdio Transport:**
```bash
# Test stdio server
struct mcp --server
# Should show: Starting MCP server with stdio transport
# Press Ctrl+C to stop
```

### Step 3: Test MCP tools

**Using HTTP client:**
```bash
# In another terminal, test with curl
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {}
  }'
```

### Step 4: Configure your MCP client
Add the configuration to your MCP client (see examples above).

### Step 5: Available MCP tools
Once connected, you can use these **fully functional** tools:
- ✅ `list_structures` - Get all available structures
- ✅ `get_structure_info` - Get details about a specific structure
- ✅ `generate_structure` - Generate project structures (**Fixed: ArgumentParser issues resolved**)
- ✅ `validate_structure` - Validate YAML configuration files (**Fixed: ArgumentParser issues resolved**)

## Troubleshooting

### Transport Comparison

| Feature | stdio Transport | HTTP Transport |
|---------|----------------|----------------|
| Connection Reliability | ⚠️ Can have issues | ✅ Very reliable |
| Multiple Clients | ❌ Single client only | ✅ Multiple concurrent |
| Debugging | ⚠️ Limited | ✅ Easy with browser/curl |
| Health Checks | ❌ Not available | ✅ `/health` endpoint |
| API Documentation | ❌ Not available | ✅ `/docs` endpoint |
| Error Reporting | ⚠️ Basic | ✅ Detailed HTTP responses |

**Recommendation:** Use HTTP transport for production and development.

### Common Issues

1. **"Command not found: struct"**
   - Solution: Ensure struct is installed and in your PATH
   - Alternative: Use full path to Python executable

2. **MCP server won't start**
   - Check if dependencies are installed: `pip show mcp fastapi uvicorn`
   - Try HTTP transport: `struct mcp --server --transport http`
   - Check for port conflicts: `lsof -i :8000`

3. **Client can't connect (stdio)**
   - Verify the command and args in your client configuration
   - Test MCP server manually first
   - Check working directory and environment variables
   - **Solution:** Switch to HTTP transport for better reliability

4. **Client can't connect (HTTP)**
   - Check if server is running: `curl http://localhost:8000/health`
   - Verify port number in client configuration
   - Check firewall settings if accessing remotely

5. **Structures not found**
   - Set `STRUCT_STRUCTURES_PATH` environment variable
   - Use absolute paths in configuration
   - Verify structure files exist and are readable

6. **ArgumentParser errors (Fixed in latest version)**
   - Update to the latest version of struct
   - These errors with `generate_structure` and `validate_structure` have been resolved

### Debug Mode

**HTTP Transport:**
```bash
# Run with debug logging
struct mcp --server --transport http --log-level DEBUG

# Check server health
curl http://localhost:8000/health

# View API documentation
open http://localhost:8000/docs
```

**stdio Transport:**
```bash
# Run with debug logging
STRUCT_LOG_LEVEL=DEBUG struct mcp --server
```

### Testing MCP Tools

**Test all tools with HTTP:**
```bash
# Start server
struct mcp --server --transport http &
SERVER_PID=$!

# Test list_structures
curl -X POST http://localhost:8000/mcp -H "Content-Type: application/json" -d '{
  "jsonrpc": "2.0", "id": 1, "method": "tools/call",
  "params": {"name": "list_structures", "arguments": {}}
}'

# Test get_structure_info
curl -X POST http://localhost:8000/mcp -H "Content-Type: application/json" -d '{
  "jsonrpc": "2.0", "id": 2, "method": "tools/call",
  "params": {"name": "get_structure_info", "arguments": {"structure_name": "project/python"}}
}'

# Test validate_structure
curl -X POST http://localhost:8000/mcp -H "Content-Type: application/json" -d '{
  "jsonrpc": "2.0", "id": 3, "method": "tools/call",
  "params": {"name": "validate_structure", "arguments": {"yaml_file": "/path/to/structure.yaml"}}
}'

# Clean up
kill $SERVER_PID
```

## Benefits

1. **Automation**: Programmatic access to all struct tool functionality
2. **Integration**: Easy integration with other development tools
3. **AI Workflows**: Enhanced support for AI-assisted development processes
4. **Consistency**: Same underlying logic as CLI commands
5. **Flexibility**: Support for custom paths, mappings, and output modes

## Backward Compatibility

All existing struct tool functionality remains unchanged. The MCP integration is additive and does not affect existing workflows or commands.
