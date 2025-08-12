# CLI Reference

This document provides a reference for the `struct` command-line interface (CLI).

## Overview

The `struct` CLI allows you to generate project structures from YAML configuration files. It supports both built-in structure definitions and custom structures.

**Basic Usage:**

```sh
struct {info,validate,generate,list,generate-schema,mcp,completion} ...
```

## Global Options

These options are available for all commands:

- `-h, --help`: Show the help message and exit.
- `-l LOG, --log LOG`: Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
- `-c CONFIG_FILE, --config-file CONFIG_FILE`: Path to a configuration file.
- `-i LOG_FILE, --log-file LOG_FILE`: Path to a log file.

## Commands

### `info`

Show information about a structure definition.

**Usage:**

```sh
struct info [-h] [-l LOG] [-c CONFIG_FILE] [-i LOG_FILE] [-s STRUCTURES_PATH] structure_definition
```

**Arguments:**

- `structure_definition`: Name of the structure definition.
- `-s STRUCTURES_PATH, --structures-path STRUCTURES_PATH`: Path to structure definitions.

### `validate`

Validate the YAML configuration file.

**Usage:**

```sh
struct validate [-h] [-l LOG] [-c CONFIG_FILE] [-i LOG_FILE] yaml_file
```

**Arguments:**

- `yaml_file`: Path to the YAML configuration file.

### `generate`

Generate the project structure.

**Usage:**

```sh
struct generate [-h] [-l LOG] [-c CONFIG_FILE] [-i LOG_FILE] [-s STRUCTURES_PATH] [-n INPUT_STORE] [-d] [--diff] [-v VARS] [-b BACKUP] [-f {overwrite,skip,append,rename,backup}] [-p GLOBAL_SYSTEM_PROMPT] [--non-interactive] [--mappings-file MAPPINGS_FILE] [-o {console,file}] structure_definition base_path
```

**Arguments:**

- `structure_definition`: Path to the YAML configuration file.
- `base_path`: Base path where the structure will be created.
- `-s STRUCTURES_PATH, --structures-path STRUCTURES_PATH`: Path to structure definitions.
- `-n INPUT_STORE, --input-store INPUT_STORE`: Path to the input store.
- `-d, --dry-run`: Perform a dry run without creating any files or directories.
- `--diff`: Show unified diffs for files that would be created/modified (works with `--dry-run` and in `-o console` mode).
- `-v VARS, --vars VARS`: Template variables in the format KEY1=value1,KEY2=value2.
- `-b BACKUP, --backup BACKUP`: Path to the backup folder.
- `-f {overwrite,skip,append,rename,backup}, --file-strategy {overwrite,skip,append,rename,backup}`: Strategy for handling existing files.
- `-p GLOBAL_SYSTEM_PROMPT, --global-system-prompt GLOBAL_SYSTEM_PROMPT`: Global system prompt for OpenAI.
- `--non-interactive`: Run the command in non-interactive mode.
- `--mappings-file MAPPINGS_FILE`: Path to a YAML file containing mappings to be used in templates (can be specified multiple times).
- `-o {console,file}, --output {console,file}`: Output mode.

### `list`

List available structures.

**Usage:**

```sh
struct list [-h] [-l LOG] [-c CONFIG_FILE] [-i LOG_FILE] [-s STRUCTURES_PATH]
```

**Arguments:**

- `-s STRUCTURES_PATH, --structures-path STRUCTURES_PATH`: Path to structure definitions.

### `generate-schema`

Generate JSON schema for available structures.

**Usage:**

```sh
struct generate-schema [-h] [-l LOG] [-c CONFIG_FILE] [-i LOG_FILE] [-s STRUCTURES_PATH] [-o OUTPUT]
```

**Arguments:**

- `-s STRUCTURES_PATH, --structures-path STRUCTURES_PATH`: Path to structure definitions.
- `-o OUTPUT, --output OUTPUT`: Output file path for the schema (default: stdout).

### `completion`

Manage shell completions for struct.

Usage:

```sh
struct completion install [bash|zsh|fish]
```

- If no shell is provided, the command attempts to auto-detect your current shell and prints the exact commands to enable argcomplete-based completion for struct.
- This does not modify your shell configuration; it only prints the commands you can copy-paste.

## Examples

### Basic Structure Generation

Generate a structure using a built-in definition:

```sh
struct generate python-basic ./my-project
```

Generate from a custom YAML file:

```sh
struct generate file://my-structure.yaml ./output-dir
```

### Using Custom Structures

Generate with custom structure path:

```sh
struct generate -s ~/custom-structures python-api ./my-api
```

### Template Variables

Pass template variables to the structure:

```sh
struct generate -v "project_name=MyApp,author=John Doe" file://structure.yaml ./output
```

### Dry Run

Test structure generation without creating files:

```sh
struct generate -d file://structure.yaml ./output
```

### File Strategies

Handle existing files with different strategies:

```sh
# Skip existing files
struct generate -f skip file://structure.yaml ./output

# Backup existing files
struct generate -f backup -b ./backup file://structure.yaml ./output
```

### Console Output

Output to console instead of creating files:

```sh
struct generate -o console file://structure.yaml ./output
```

### Validation

Validate a YAML configuration before generation:

```sh
struct validate my-structure.yaml
```

### List Available Structures

List all built-in structures:

```sh
struct list
```

List structures from custom path:

```sh
struct list -s ~/custom-structures
```

### Get Structure Information

Get detailed information about a structure:

```sh
struct info python-basic
```

### Generate Schema

Generate JSON schema and save to file:

```sh
struct generate-schema -o schema.json
```
