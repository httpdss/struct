# Command-Line Auto-Completion

STRUCT provides intelligent auto-completion for commands, options, and **structure names** using [argcomplete](https://kislyuk.github.io/argcomplete/). This makes discovering and using available structures much faster and more user-friendly.

!!! tip "New Feature: Structure Name Completion"
    STRUCT now automatically completes structure names when using `struct generate`, showing all 47+ available structures from both built-in and custom paths!

## Quick Setup

The easiest way is to ask struct to print the exact commands for your shell:

```sh
# Auto-detect current shell and print install steps
struct completion install

# Or specify explicitly
struct completion install zsh
struct completion install bash
struct completion install fish
```

You can still follow the manual steps below if you prefer.

For most users, this simple setup will enable full completion:

```sh
# Install (if not already installed)
pip install argcomplete

# Enable completion for current session
eval "$(register-python-argcomplete struct)"

# Make permanent - add to your ~/.zshrc or ~/.bashrc
echo 'eval "$(register-python-argcomplete struct)"' >> ~/.zshrc
```

## Detailed Installation

### 1. Install argcomplete

```sh
pip install argcomplete
```

### 2. Enable Global Completion (Optional)

This step is optional but can be done once per system:

```sh
activate-global-python-argcomplete
```

This command sets up global completion for all Python scripts that use argcomplete.

### 3. Register the Script

Add the following line to your shell's configuration file:

**For Bash** (`.bashrc` or `.bash_profile`):

```sh
eval "$(register-python-argcomplete struct)"
```

**For Zsh** (`.zshrc`):

```sh
eval "$(register-python-argcomplete struct)"
```

**For Fish** (`.config/fish/config.fish`):

```fish
register-python-argcomplete --shell fish struct | source
```

### 4. Reload Your Shell

```sh
# For Bash
source ~/.bashrc

# For Zsh
source ~/.zshrc

# For Fish
source ~/.config/fish/config.fish
```

## Usage

After completing the setup, you can use auto-completion by typing part of a command and pressing `Tab`:

### Command Completion
```sh
struct <Tab>
# Shows: generate, generate-schema, validate, info, list
```

### Structure Name Completion ✨
```sh
# Complete structure names - shows all available structures!
struct generate <Tab>
# Shows: ansible-playbook, docker-files, github/workflows/codeql, project/nodejs, etc.

# Partial completion works too
struct generate git<Tab>
# Shows: git-hooks, github/workflows/codeql, github/templates, etc.

# Works with nested structures
struct generate github/<Tab>
# Shows: github/workflows/codeql, github/templates, github/prompts/generic, etc.
```

### Custom Structure Paths
```sh
# Completion works with custom structure paths
struct generate --structures-path /custom/path <Tab>
# Shows structures from both custom path and built-in structures
```

### Option Completion
```sh
struct generate --<Tab>
# Shows: --log, --dry-run, --backup, --file-strategy, --structures-path, etc.

struct generate --log <Tab>
# Shows: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## Advanced Configuration

### Per-Project Completion

If you only want completion for specific projects, you can add completion to your project's virtual environment activation script:

```sh
# In your .venv/bin/activate file, add:
eval "$(register-python-argcomplete struct)"
```

### Custom Completion

You can create custom completion functions for specific use cases:

```sh
# Custom completion for structure names
_struct_structures() {
    local structures=$(struct list --names-only 2>/dev/null)
    COMPREPLY=($(compgen -W "$structures" -- "${COMP_WORDS[COMP_CWORD]}"))
}

# Register custom completion
complete -F _struct_structures struct-generate
```

## Troubleshooting

### Completion Not Working

1. **Check argcomplete installation**:

   ```sh
   python -c "import argcomplete; print('OK')"
   ```

2. **Verify global activation**:

   ```sh
   activate-global-python-argcomplete --user
   ```

3. **Check shell configuration**:
   Make sure the eval statement is in the correct shell configuration file.

4. **Restart your shell**:
   Sometimes you need to completely restart your terminal.

### Slow Completion

If completion is slow, you can enable caching:

```sh
export ARGCOMPLETE_USE_TEMPFILES=1
```

Add this to your shell configuration file for persistent caching.

### Debug Completion

Enable debug mode to troubleshoot completion issues:

```sh
export _ARGCOMPLETE_DEBUG=1
struct <Tab>
```

## Platform-Specific Notes

### macOS

On macOS, you might need to install bash-completion first:

```sh
# Using Homebrew
brew install bash-completion

# Then add to ~/.bash_profile:
[[ -r "/usr/local/etc/profile.d/bash_completion.sh" ]] && . "/usr/local/etc/profile.d/bash_completion.sh"
```

### Windows

For Windows users using Git Bash or WSL, follow the same steps as Linux. For PowerShell, argcomplete support is limited.

### Docker

When running STRUCT in Docker, completion won't work directly. However, you can create a wrapper script:

```sh
#!/bin/bash
# struct-wrapper.sh
docker run --rm -v $(pwd):/workdir ghcr.io/httpdss/struct:main "$@"
```

Then set up completion for the wrapper:

```sh
eval "$(register-python-argcomplete struct-wrapper.sh)"
```

## Benefits of Auto-Completion

- **Faster typing**: Quickly complete command names and options
- **Discoverability**: See available commands and options
- **Accuracy**: Reduce typos and errors
- **Productivity**: Spend less time looking up command syntax

## Supported Completions

STRUCT provides intelligent completion for:

- **Commands**: `generate`, `validate`, `list`, `info`, `generate-schema`
- **Options**: `--log`, `--dry-run`, `--backup`, `--file-strategy`, `--structures-path`, etc.
- **Structure names**: All 47+ available built-in and custom structures
  - Built-in structures: `ansible-playbook`, `docker-files`, `helm-chart`, etc.
  - Nested structures: `github/workflows/codeql`, `project/nodejs`, `terraform/apps/generic`, etc.
  - Custom structures: From `--structures-path` directories
- **File paths**: Local files and directories
- **Enum values**: Log levels (`DEBUG`, `INFO`, etc.), file strategies (`overwrite`, `skip`, etc.)

## How Structure Completion Works

The structure name completion feature:

1. **Dynamically discovers** all available structure files (`.yaml` files)
2. **Scans multiple locations**:
   - Built-in structures in `struct_module/contribs/`
   - Custom structures from `--structures-path` if specified
3. **Returns clean names** without `.yaml` extensions
4. **Supports nested directories** like `github/workflows/codeql`
5. **Updates automatically** when new structures are added

## Example Session

```sh
# Command completion
$ struct <Tab>
generate        generate-schema info           list           validate

# Structure name completion (NEW!)
$ struct generate <Tab>
ansible-playbook     configs/codeowners    github/workflows/codeql  project/nodejs
chef-cookbook        docker-files          helm-chart               terraform/apps/generic
ci-cd-pipelines      git-hooks            kubernetes-manifests      vagrant-files

# Partial completion
$ struct generate proj<Tab>
project/custom-structures  project/go      project/nodejs  project/ruby
project/generic           project/java    project/python  project/rust

# Nested structure completion
$ struct generate github/<Tab>
github/chatmodes/plan       github/prompts/react-form    github/workflows/codeql
github/instructions/generic github/prompts/security-api  github/workflows/labeler
github/prompts/generic      github/workflows/pre-commit  github/workflows/stale

# Option completion
$ struct generate --<Tab>
--backup        --dry-run       --file-strategy --log
--log-file      --mappings-file --structures-path --vars

# Enum value completion
$ struct generate --log <Tab>
DEBUG    ERROR    INFO     WARNING  CRITICAL

$ struct generate --file-strategy <Tab>
append    backup    overwrite    rename    skip
```

This makes working with STRUCT much more efficient and user-friendly!
