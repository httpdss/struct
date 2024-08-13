import os
import logging
import yaml
from dotenv import load_dotenv
from .utils import read_config_file, merge_configs, validate_configuration, create_structure

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
openai_model = os.getenv("OPENAI_MODEL")

if not openai_api_key:
    logging.warning("OpenAI API key not found. Skipping processing prompt.")

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate project structure from YAML configuration.",
        prog="struct",
        epilog="Thanks for using %(prog)s! :)",

    )
    parser.add_argument('yaml_file', type=str, help='Path to the YAML configuration file')
    parser.add_argument('base_path', type=str, help='Base path where the structure will be created')
    parser.add_argument('-c', '--config-file', type=str, help='Path to a configuration file')
    parser.add_argument('-l', '--log', type=str, default='INFO', help='Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
    parser.add_argument('-d', '--dry-run', action='store_true', help='Perform a dry run without creating any files or directories')
    parser.add_argument('-v', '--vars', type=str, help='Template variables in the format KEY1=value1,KEY2=value2')
    parser.add_argument('-b', '--backup', type=str, help='Path to the backup folder')
    parser.add_argument('-f', '--file-strategy', type=str, choices=['overwrite', 'skip', 'append', 'rename', 'backup'], default='overwrite', help='Strategy for handling existing files')
    parser.add_argument('-i', '--log-file', type=str, help='Path to a log file')
    parser.add_argument('-p', '--global-system-prompt', type=str, help='Global system prompt for OpenAI')

    args = parser.parse_args()

    # Read config file if provided
    if args.config_file:
        file_config = read_config_file(args.config_file)
        args = argparse.Namespace(**merge_configs(file_config, args))

    logging_level = getattr(logging, args.log.upper(), logging.INFO)
    template_vars = dict(item.split('=') for item in args.vars.split(',')) if args.vars else None
    backup_path = args.backup

    if backup_path and not os.path.exists(backup_path):
        os.makedirs(backup_path)

    if args.base_path and not os.path.exists(args.base_path):
        logging.info(f"Creating base path: {args.base_path}")
        os.makedirs(args.base_path)

    logging.basicConfig(
        level=logging_level,
        filename=args.log_file,
        format='[%(asctime)s][%(levelname)s][struct] >>> %(message)s',
    )
    logging.info(f"Starting to create project structure from {args.yaml_file} in {args.base_path}")
    logging.debug(f"YAML file path: {args.yaml_file}, Base path: {args.base_path}, Dry run: {args.dry_run}, Template vars: {template_vars}, Backup path: {backup_path}")

    with open(args.yaml_file, 'r') as f:
        config = yaml.safe_load(f)

    validate_configuration(config.get('structure', []))
    create_structure(args.base_path, config.get('structure', []), args.dry_run, template_vars, backup_path, args.file_strategy, args.global_system_prompt)

    logging.info("Finished creating project structure")

if __name__ == "__main__":
    main()
