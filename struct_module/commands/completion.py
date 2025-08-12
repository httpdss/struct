from struct_module.commands import Command
import os

SUPPORTED_SHELLS = ["bash", "zsh", "fish"]

class CompletionCommand(Command):
  def __init__(self, parser):
    super().__init__(parser)
    parser.description = "Manage CLI shell completions for struct (argcomplete)"
    sub = parser.add_subparsers(dest="action")

    install = sub.add_parser("install", help="Print the commands to enable completion for your shell")
    install.add_argument("shell", nargs="?", choices=SUPPORTED_SHELLS, help="Shell type (auto-detected if omitted)")
    install.set_defaults(func=self._install)

  def _detect_shell(self):
    shell = os.environ.get("SHELL", "")
    if shell:
      basename = os.path.basename(shell)
      if basename in SUPPORTED_SHELLS:
        return basename
    # Fallback to zsh if running zsh, else bash
    if os.environ.get("ZSH_NAME") or os.environ.get("ZDOTDIR"):
      return "zsh"
    return "bash"

  def _install(self, args):
    shell = args.shell or self._detect_shell()
    print(f"Detected shell: {shell}")

    if shell == "bash":
      print("\n# One-time dependency (if not installed):")
      print("python -m pip install argcomplete")
      print("\n# Enable completion for 'struct' in bash (append to ~/.bashrc):")
      print('echo "eval \"$(register-python-argcomplete struct)\"" >> ~/.bashrc')
      print("\n# Apply now:")
      print("source ~/.bashrc")

    elif shell == "zsh":
      print("\n# One-time dependency (if not installed):")
      print("python -m pip install argcomplete")
      print("\n# Enable completion for 'struct' in zsh (append to ~/.zshrc):")
      print('echo "eval \"$(register-python-argcomplete --shell zsh struct)\"" >> ~/.zshrc')
      print("\n# Apply now:")
      print("source ~/.zshrc")

    elif shell == "fish":
      print("\n# One-time dependency (if not installed):")
      print("python -m pip install argcomplete")
      print("\n# Install fish completion file for 'struct':")
      print('mkdir -p ~/.config/fish/completions')
      print('register-python-argcomplete --shell fish struct > ~/.config/fish/completions/struct.fish')
      print("\n# Apply now:")
      print("fish -c 'source ~/.config/fish/completions/struct.fish'")

    else:
      self.logger.error(f"Unsupported shell: {shell}. Supported: {', '.join(SUPPORTED_SHELLS)}")
      return

    print("\nTip: If 'register-python-argcomplete' is not found, try:\n  python -m argcomplete.shellintegration <shell>")
