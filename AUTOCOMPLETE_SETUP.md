# Struct Autocomplete Setup

This document explains the autocomplete functionality that has been implemented for the `struct` tool's positional arguments.

## What was implemented

### 1. Dynamic Structure Completer (`struct_module/completers.py`)

A new `StructuresCompleter` class was added that:

- Dynamically discovers available structure names from the `contribs` directory
- Supports custom structure paths via the `--structures-path` argument
- Returns structure names without the `.yaml` extension
- Handles nested directory structures (e.g., `github/workflows/codeql`)

### 2. Integration with Generate Command

The `GenerateCommand` class in `struct_module/commands/generate.py` now:

- Imports the `structures_completer`
- Assigns it to the `structure_definition` positional argument
- Enables autocomplete for structure names when using `struct generate`

### 3. Test Coverage

Added comprehensive tests in `tests/test_completers.py`:

- Test basic structure completion functionality
- Test completion with custom structure paths
- Verify integration with argparse

## How to enable autocomplete

### For Zsh users (current shell):

1. Make sure your virtual environment is activated:
   ```bash
   source .venv/bin/activate
   ```

2. Install the package in development mode (if not already done):
   ```bash
   pip install -e .
   ```

3. Enable completion for the current session:
   ```bash
   eval "$(register-python-argcomplete struct)"
   ```

4. To make it permanent, add this line to your `~/.zshrc`:
   ```bash
   eval "$(register-python-argcomplete struct)"
   ```

### For Bash users:

Follow the same steps as above - the `register-python-argcomplete` command works for both bash and zsh.

## How it works

1. When you type `struct generate ` and press Tab, argcomplete intercepts the completion request
2. The `StructuresCompleter` scans the available structure files in:
   - `struct_module/contribs/` (built-in structures)
   - Custom path specified via `--structures-path` (if provided)
3. It returns a list of structure names (without `.yaml` extension)
4. Your shell displays these as completion options

## Example Usage

Once autocomplete is enabled, you can:

```bash
# Tab completion for structure names
struct generate <TAB>
# Shows: ansible-playbook, chef-cookbook, ci-cd-pipelines, etc.

# Partial completion
struct generate git<TAB>
# Shows: git-hooks, github/workflows/codeql, etc.

# With custom structures path
struct generate --structures-path /path/to/custom <TAB>
# Shows structures from both custom path and built-in contribs
```

## Available Structures

The completer will show all structures available in your installation, including:

- `ansible-playbook`
- `docker-files`
- `helm-chart`
- `github/workflows/codeql`
- `project/nodejs`
- `terraform/apps/generic`
- And many more...

## Testing

To verify the autocomplete functionality is working:

1. Run the tests: `python -m pytest tests/test_completers.py -v`
2. Test manually: `python -c "from struct_module.completers import structures_completer; import argparse; print(structures_completer('', argparse.Namespace(structures_path=None)))"`

## Troubleshooting

- **Completion not working**: Make sure argcomplete is installed and the completion is registered
- **Missing structures**: Verify that structure files exist in `struct_module/contribs/`
- **Custom paths not working**: Ensure the `--structures-path` argument is specified before the positional argument
