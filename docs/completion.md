# Command-Line Auto-Completion

This project uses [argcomplete](https://kislyuk.github.io/argcomplete/) to provide command-line auto-completion for the `struct` script. Follow these steps to enable auto-completion:

## Installation

### 1. Install argcomplete

```sh
pip install argcomplete
```

### 2. Enable Global Completion

This step is usually done once per system:

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

```sh
struct <Tab>
# Shows: generate, generate-schema, validate, info, list

struct generate <Tab>
# Shows available structure names and options

struct generate --<Tab>
# Shows: --log, --dry-run, --backup, --file-strategy, etc.
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

STRUCT provides completion for:

- **Commands**: `generate`, `validate`, `list`, etc.
- **Options**: `--log`, `--dry-run`, `--backup`, etc.
- **Structure names**: All available built-in and custom structures
- **File paths**: Local files and directories
- **Enum values**: Log levels, file strategies, etc.

## Example Session

```sh
$ struct <Tab>
generate        generate-schema info           list           validate

$ struct generate <Tab>
configs/        docker-files    project/       terraform/

$ struct generate terraform/<Tab>
terraform/app   terraform/module

$ struct generate --<Tab>
--backup        --dry-run       --file-strategy --log
--log-file      --mappings-file --structures-path

$ struct generate --log <Tab>
DEBUG    ERROR    INFO     WARNING
```

This makes working with STRUCT much more efficient and user-friendly!
