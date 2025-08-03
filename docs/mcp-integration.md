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

### Client Configuration
To integrate with MCP clients, configure the client to execute:
```bash
struct mcp --server
```

## Benefits

1. **Automation**: Programmatic access to all struct tool functionality
2. **Integration**: Easy integration with other development tools
3. **AI Workflows**: Enhanced support for AI-assisted development processes
4. **Consistency**: Same underlying logic as CLI commands
5. **Flexibility**: Support for custom paths, mappings, and output modes

## Backward Compatibility

All existing struct tool functionality remains unchanged. The MCP integration is additive and does not affect existing workflows or commands.
