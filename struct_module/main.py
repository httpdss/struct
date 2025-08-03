import argparse, argcomplete
import logging
from dotenv import load_dotenv
from struct_module.utils import read_config_file, merge_configs
from struct_module.commands.generate import GenerateCommand
from struct_module.commands.info import InfoCommand
from struct_module.commands.validate import ValidateCommand
from struct_module.commands.list import ListCommand
from struct_module.commands.generate_schema import GenerateSchemaCommand
from struct_module.commands.mcp import MCPCommand
from struct_module.logging_config import configure_logging



load_dotenv()

def main():
    parser = argparse.ArgumentParser(
      description="Generate project structure from YAML configuration.",
      prog="struct",
      epilog="Thanks for using %(prog)s! :)",
    )

    # Create subparsers
    subparsers = parser.add_subparsers()

    InfoCommand(subparsers.add_parser('info', help='Show information about the package'))
    ValidateCommand(subparsers.add_parser('validate', help='Validate the YAML configuration file'))
    GenerateCommand(subparsers.add_parser('generate', help='Generate the project structure'))
    ListCommand(subparsers.add_parser('list', help='List available structures'))
    GenerateSchemaCommand(subparsers.add_parser('generate-schema', help='Generate JSON schema for available structures'))
    MCPCommand(subparsers.add_parser('mcp', help='MCP (Model Context Protocol) support'))

    argcomplete.autocomplete(parser)

    args = parser.parse_args()

    # Check if a subcommand was provided
    if not hasattr(args, 'func'):
      parser.print_help()
      parser.exit()

    # Read config file if provided
    if args.config_file:
      file_config = read_config_file(args.config_file)
      args = argparse.Namespace(**merge_configs(file_config, args))

    logging_level = getattr(logging, args.log.upper(), logging.INFO)

    configure_logging(level=logging_level, log_file=args.log_file)


    args.func(args)

if __name__ == "__main__":
    main()
