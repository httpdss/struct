# Command-Line Auto-Completion

STRUCT uses [argcomplete](https://kislyuk.github.io/argcomplete/) to provide auto-completion.

1. Install `argcomplete`:

```sh
pip install argcomplete
```

2. Enable global completion (usually done once):

```sh
activate-global-python-argcomplete
```

3. Register the script in your shell configuration (e.g. `.bashrc` or `.zshrc`):

```sh
eval "$(register-python-argcomplete struct)"
```

4. Reload your shell configuration:

```sh
source ~/.bashrc  # or ~/.zshrc for Zsh
```
