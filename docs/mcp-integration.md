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

To start the MCP server for stdio communication:

```bash
struct mcp --server
```

### Command Line Integration

The existing `list` and `info` commands now support an optional `--mcp` flag:

```bash
# List structures with MCP support
struct list --mcp

# Get structure info with MCP support
struct info project/python --mcp
```

## MCP Client Integration

### Claude Desktop Integration

Add the following to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**Linux**: `~/.config/claude/claude_desktop_config.json`

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

### Cline/Continue Integration

For Cline (VS Code extension), add to your `.cline_mcp_settings.json`:

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

### Custom MCP Client Integration

For any MCP-compatible client, use these connection parameters:

```javascript
// Node.js example
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
# Python example
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
pip install struct[mcp]  # or pip install struct && pip install mcp
```

### Step 2: Test MCP server
```bash
# Test that MCP server starts correctly
struct mcp --server
# Should show: Starting MCP server...
# Press Ctrl+C to stop
```

### Step 3: Configure your MCP client
Add the configuration to your MCP client (see examples above).

### Step 4: Start using MCP tools
Once connected, you can use these tools:
- `list_structures` - Get all available structures
- `get_structure_info` - Get details about a specific structure
- `generate_structure` - Generate project structures
- `validate_structure` - Validate YAML configuration files

## Troubleshooting

### Common Issues

1. **"Command not found: struct"**
   - Solution: Ensure struct is installed and in your PATH
   - Alternative: Use full path to Python executable

2. **MCP server won't start**
   - Check if `mcp` package is installed: `pip show mcp`
   - Try running with verbose logging: `struct mcp --server --log DEBUG`

3. **Client can't connect**
   - Verify the command and args in your client configuration
   - Test MCP server manually first
   - Check working directory and environment variables

4. **Structures not found**
   - Set `STRUCT_STRUCTURES_PATH` environment variable
   - Use absolute paths in configuration
   - Verify structure files exist and are readable

### Debug Mode
```bash
# Run with debug logging
STRUCT_LOG_LEVEL=DEBUG struct mcp --server
```

## Benefits

1. **Automation**: Programmatic access to all struct tool functionality
2. **Integration**: Easy integration with other development tools
3. **AI Workflows**: Enhanced support for AI-assisted development processes
4. **Consistency**: Same underlying logic as CLI commands
5. **Flexibility**: Support for custom paths, mappings, and output modes

## Backward Compatibility

All existing struct tool functionality remains unchanged. The MCP integration is additive and does not affect existing workflows or commands.
