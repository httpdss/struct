import argparse, argcomplete
import logging
from dotenv import load_dotenv
from struct_module.utils import read_config_file, merge_configs
from struct_module.commands.generate import GenerateCommand
from struct_module.commands.info import InfoCommand
from struct_module.commands.validate import ValidateCommand
from struct_module.commands.list import ListCommand



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

    logging.basicConfig(
      level=logging_level,
      filename=args.log_file,
      format='[%(asctime)s][%(levelname)s][struct] >>> %(message)s',
    )

    args.func(args)

    # Use an official Python runtime as a parent image
    FROM python:3.12.4-slim

    # Set the working directory in the container
    WORKDIR /app

    # Copy the requirements.txt file into the container at /app
    COPY requirements.txt .

    # Install any needed packages specified in requirements.txt
    RUN pip install --no-cache-dir -r requirements.txt

    # Install argcomplete and activate global completion
    RUN pip install argcomplete && \
        activate-global-python-argcomplete

    # Copy the rest of the working directory contents into the container at /app
    COPY . .

    # Register the script for auto-completion
    RUN echo 'eval "$(register-python-argcomplete struct)"' >> /etc/bash.bashrc

    # Run your script when the container launches
    ENTRYPOINT ["python", "struct_module/main.py"]

if __name__ == "__main__":
    main()
