import os
import yaml
import logging
import argparse
import shutil
import requests
from string import Template

def fetch_remote_content(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def apply_template_variables(content, template_vars):
    if template_vars:
        template = Template(content)
        content = template.substitute(template_vars)
    return content

def validate_configuration(structure):
    if not isinstance(structure, list):
        raise ValueError("The 'structure' key must be a list.")
    for item in structure:
        if not isinstance(item, dict):
            raise ValueError("Each item in the 'structure' list must be a dictionary.")
        for name, content in item.items():
            if not isinstance(name, str):
                raise ValueError("Each name in the 'structure' item must be a string.")
            if isinstance(content, dict):
                if 'content' not in content and 'file' not in content:
                    raise ValueError(f"Dictionary item '{name}' must contain either 'content' or 'file' key.")
                if 'file' in content and not isinstance(content['file'], str):
                    raise ValueError(f"The 'file' value for '{name}' must be a string.")
                if 'permissions' in content and not isinstance(content['permissions'], str):
                    raise ValueError(f"The 'permissions' value for '{name}' must be a string.")
            elif not isinstance(content, str):
                raise ValueError(f"The content of '{name}' must be a string or dictionary.")
    logging.info("Configuration validation passed.")

def create_structure(base_path, structure, dry_run=False, template_vars=None, backup_path=None, file_strategy='overwrite'):
    for item in structure:
        logging.debug(f"Processing item: {item}")
        for name, content in item.items():
            logging.debug(f"Processing name: {name}, content: {content}")
            if isinstance(content, dict):
                if 'file' in content:
                    # Fetch content from a remote file
                    remote_content = fetch_remote_content(content['file'])
                    remote_content = apply_template_variables(remote_content, template_vars)
                    file_path = os.path.join(base_path, name)
                    handle_file_creation(file_path, remote_content, content, dry_run, backup_path, file_strategy)
                else:
                    # It's a directory
                    dir_path = os.path.join(base_path, name)
                    if dry_run:
                        logging.info(f"[DRY RUN] Would create directory: {dir_path}")
                    else:
                        os.makedirs(dir_path, exist_ok=True)
                        logging.info(f"Created directory: {dir_path}")
                    create_structure(dir_path, content.values(), dry_run, template_vars, backup_path, file_strategy)
            elif isinstance(content, str):
                # It's a file with inline content
                file_path = os.path.join(base_path, name)
                content = apply_template_variables(content, template_vars)
                handle_file_creation(file_path, content, content, dry_run, backup_path, file_strategy)

def handle_file_creation(file_path, content, file_config, dry_run, backup_path, file_strategy):
    if dry_run:
        logging.info(f"[DRY RUN] Would create file: {file_path} with content: {content}")
    else:
        if os.path.exists(file_path):
            if file_strategy == 'backup' and backup_path:
                backup_file_path = os.path.join(backup_path, os.path.basename(file_path))
                shutil.copy2(file_path, backup_file_path)
                logging.info(f"Backed up existing file: {file_path} to {backup_file_path}")
            elif file_strategy == 'skip':
                logging.info(f"Skipped existing file: {file_path}")
                return
            elif file_strategy == 'append':
                with open(file_path, 'a') as f:
                    f.write(content)
                logging.info(f"Appended to existing file: {file_path}")
                return
            elif file_strategy == 'rename':
                new_name = f"{file_path}.{int(time.time())}"
                os.rename(file_path, new_name)
                logging.info(f"Renamed existing file: {file_path} to {new_name}")

        with open(file_path, 'w') as f:
            f.write(content)
        logging.info(f"Created file: {file_path} with content: {content}")

        if isinstance(file_config, dict) and 'permissions' in file_config:
            permissions = file_config['permissions']
            os.chmod(file_path, int(permissions, 8))
            logging.info(f"Set permissions {permissions} for file: {file_path}")

def main():
    parser = argparse.ArgumentParser(description="Generate project structure from YAML configuration.")
    parser.add_argument('yaml_file', type=str, help='Path to the YAML configuration file')
    parser.add_argument('base_path', type=str, help='Base path where the structure will be created')
    parser.add_argument('--log', type=str, default='INFO', help='Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
    parser.add_argument('--dry-run', action='store_true', help='Perform a dry run without creating any files or directories')
    parser.add_argument('--vars', type=str, help='Template variables in the format KEY1=value1,KEY2=value2')
    parser.add_argument('--backup', type=str, help='Path to the backup folder')
    parser.add_argument('--file-strategy', type=str, choices=['overwrite', 'skip', 'append', 'rename', 'backup'], default='overwrite', help='Strategy for handling existing files')
    parser.add_argument('--log-file', type=str, help='Path to a log file')

    args = parser.parse_args()

    logging_level = getattr(logging, args.log.upper(), logging.INFO)
    template_vars = dict(item.split('=') for item in args.vars.split(',')) if args.vars else None
    backup_path = args.backup

    if backup_path and not os.path.exists(backup_path):
        os.makedirs(backup_path)

    logging.info(f"Starting to create project structure from {args.yaml_file} in {args.base_path}")
    logging.debug(f"YAML file path: {args.yaml_file}, Base path: {args.base_path}, Dry run: {args.dry_run}, Template vars: {template_vars}, Backup path: {backup_path}")
    main(args.yaml_file, args.base_path, logging_level, args.dry_run, template_vars, backup_path, args.file_strategy, args.log_file)
    logging.info("Finished creating project structure")

if __name__ == "__main__":
    main()
