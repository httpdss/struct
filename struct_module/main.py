import requests
import os
import shutil
import logging
from string import Template
import time
import yaml
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
openai_model = os.getenv("OPENAI_MODEL")

if not openai_api_key:
    logging.warning("OpenAI API key not found. Skipping processing prompt.")

class FileItem:
    def __init__(self, properties):
        self.name = properties.get("name")
        self.content = properties.get("content")
        self.remote_location = properties.get("file")
        self.permissions = properties.get("permissions")

        self.system_prompt = properties.get("system_prompt")
        self.user_prompt = properties.get("user_prompt")
        self.openai_client = OpenAI(
            api_key=openai_api_key
        )

        if not openai_model:
            logging.info("OpenAI model not found. Using default model.")
            self.openai_model = "gpt-3.5-turbo"
        else:
            logging.debug(f"Using OpenAI model: {openai_model}")
            self.openai_model = openai_model

    def process_prompt(self, dry_run=False):
        if self.user_prompt:
            logging.debug(f"Using user prompt: {self.user_prompt}")

            if not openai_api_key:
                logging.warning("Skipping processing prompt as OpenAI API key is not set.")
                return

            if not self.system_prompt:
                system_prompt = "You are a software developer working on a project. You need to create a file with the following content:"
            else:
                system_prompt = self.system_prompt

            if dry_run:
                logging.info("[DRY RUN] Would generate content using OpenAI API.")
                self.content = "[DRY RUN] Generating content using OpenAI"
                return

            completion = self.openai_client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": self.user_prompt}
                ]
            )

            self.content = completion.choices[0].message.content
            logging.debug(f"Generated content: {self.content}")

    def fetch_content(self):
        if self.remote_location:
            logging.debug(f"Fetching content from: {self.remote_location}")
            response = requests.get(self.remote_location)
            logging.debug(f"Response status code: {response.status_code}")
            response.raise_for_status()
            self.content = response.text
            logging.debug(f"Fetched content: {self.content}")

    def apply_template_variables(self, template_vars):
        if self.content and template_vars:
            logging.debug(f"Applying template variables: {template_vars}")
            template = Template(self.content)
            self.content = template.substitute(template_vars)

    def create(self, base_path, dry_run=False, backup_path=None, file_strategy='overwrite'):
        file_path = os.path.join(base_path, self.name)
        if dry_run:
            logging.info(f"[DRY RUN] Would create file: {file_path} with content: {self.content}")
            return

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
                    f.write(self.content)
                logging.info(f"Appended to existing file: {file_path}")
                return
            elif file_strategy == 'rename':
                new_name = f"{file_path}.{int(time.time())}"
                os.rename(file_path, new_name)
                logging.info(f"Renamed existing file: {file_path} to {new_name}")

        with open(file_path, 'w') as f:
            f.write(self.content)
        logging.info(f"Created file: {file_path} with content: {self.content}")

        if self.permissions:
            os.chmod(file_path, int(self.permissions, 8))
            logging.info(f"Set permissions {self.permissions} for file: {file_path}")

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
                # Check that any of the keys 'content', 'file' or 'prompt' is present
                if 'content' not in content and 'file' not in content and 'user_prompt' not in content:
                    raise ValueError(f"Dictionary item '{name}' must contain either 'content' or 'file' or 'user_prompt' key.")
                # Check if 'file' key is present and its value is a string
                if 'file' in content and not isinstance(content['file'], str):
                    raise ValueError(f"The 'file' value for '{name}' must be a string.")
                # Check if 'permissions' key is present and its value is a string
                if 'permissions' in content and not isinstance(content['permissions'], str):
                    raise ValueError(f"The 'permissions' value for '{name}' must be a string.")
                # Check if 'prompt' key is present and its value is a string
                if 'prompt' in content and not isinstance(content['prompt'], str):
                    raise ValueError(f"The 'prompt' value for '{name}' must be a string.")
                # Check if 'prompt' key is present but no OpenAI API key is found
                if 'prompt' in content and not openai_api_key:
                    raise ValueError("Using prompt property and no OpenAI API key was found. Please set it in the .env file.")
            elif not isinstance(content, str):
                raise ValueError(f"The content of '{name}' must be a string or dictionary.")
    logging.info("Configuration validation passed.")

def create_structure(base_path, structure, dry_run=False, template_vars=None, backup_path=None, file_strategy='overwrite'):
    for item in structure:
        logging.debug(f"Processing item: {item}")
        for name, content in item.items():
            logging.debug(f"Processing name: {name}, content: {content}")
            if isinstance(content, dict):
                content["name"] = name
                file_item = FileItem(content)
                file_item.fetch_content()
            elif isinstance(content, str):
                file_item = FileItem({"name": name, "content": content})

            file_item.apply_template_variables(template_vars)
            file_item.process_prompt(dry_run)
            file_item.create(base_path, dry_run, backup_path, file_strategy)

def main():
    import argparse

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

    logging.basicConfig(
        level=logging_level,
        filename=args.log_file,
        format='%(levelname)s:struct:%(message)s',
    )
    logging.info(f"Starting to create project structure from {args.yaml_file} in {args.base_path}")
    logging.debug(f"YAML file path: {args.yaml_file}, Base path: {args.base_path}, Dry run: {args.dry_run}, Template vars: {template_vars}, Backup path: {backup_path}")

    with open(args.yaml_file, 'r') as f:
        config = yaml.safe_load(f)

    validate_configuration(config.get('structure', []))
    create_structure(args.base_path, config.get('structure', []), args.dry_run, template_vars, backup_path, args.file_strategy)

    logging.info("Finished creating project structure")

if __name__ == "__main__":
    main()
