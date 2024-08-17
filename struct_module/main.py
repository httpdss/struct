import os
import logging
from dotenv import load_dotenv
from struct_module.utils import read_config_file, merge_configs
from struct_module.commands.generate import GenerateCommand
from struct_module.commands.info import InfoCommand
from struct_module.commands.validate import ValidateCommand

import argparse

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
openai_model = os.getenv("OPENAI_MODEL")

if not openai_api_key:
    logging.warning("OpenAI API key not found. Skipping processing prompt.")


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

    logging.basicConfig(
        level=logging_level,
        filename=args.log_file,
        format='[%(asctime)s][%(levelname)s][struct] >>> %(message)s',
    )

    args.func(args)

if __name__ == "__main__":
    main()
