"""Config command for displaying effective configuration."""

from structkit.commands import Command
import yaml
import json
from structkit.config import get_effective_config, get_user_config_path, get_builtin_defaults


class ConfigCommand(Command):
    def __init__(self, parser):
        # Don't call super().__init__() yet - we need to set up subparsers first
        self.parser = parser
        import logging
        self.logger = logging.getLogger(__name__)

        parser.description = "Display and manage structkit configuration"

        # Create subparsers for config subcommands
        subparsers = parser.add_subparsers(dest='config_subcommand', help='Config subcommand')

        # print subcommand
        print_parser = subparsers.add_parser('print', help='Print the effective configuration')
        print_parser.add_argument(
            '--format',
            type=str,
            choices=['yaml', 'json'],
            default='yaml',
            help='Output format (default: yaml)'
        )
        print_parser.set_defaults(config_func=self.print_config)

        # Add common arguments to the main parser and all subparsers
        for p in [parser, print_parser]:
            self._add_common_args(p)

        parser.set_defaults(func=self.execute)

    def _add_common_args(self, parser):
        """Add common arguments to a parser (replicating Command base class)."""
        from structkit.completers import log_level_completer
        parser.add_argument('-l', '--log', type=str, default='INFO', help='Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)').completer = log_level_completer
        parser.add_argument('-c', '--config-file', type=str, help='Path to a configuration file')
        parser.add_argument('-i', '--log-file', type=str, help='Path to a log file')

    def execute(self, args):
        """Execute the config command."""
        # If no subcommand is provided, show help
        if not hasattr(args, 'config_func'):
            self.parser.print_help()
            return

        # Execute the subcommand
        args.config_func(args)

    def print_config(self, args):
        """Print the effective configuration after all layers are merged.

        This shows the final configuration that structkit would use,
        combining built-in defaults, user config, project config, and CLI args.
        """
        # Get effective config
        effective_config = get_effective_config(args)

        # Format and print
        if args.format == 'json':
            output = json.dumps(effective_config, indent=2, sort_keys=True)
        else:  # yaml
            output = yaml.dump(effective_config, default_flow_style=False, sort_keys=True)

        print(output.rstrip())

        # Show config sources
        user_config_path = get_user_config_path()
        self.logger.info("")
        self.logger.info("Configuration sources:")
        self.logger.info("  1. Built-in defaults: always loaded")
        self.logger.info(f"  2. User config: {user_config_path} {'(exists)' if user_config_path.exists() else '(not found)'}")
        if hasattr(args, 'config_file') and args.config_file:
            self.logger.info(f"  3. Project config: {args.config_file}")
        else:
            self.logger.info("  3. Project config: none specified")
        self.logger.info("  4. CLI arguments: highest priority")
