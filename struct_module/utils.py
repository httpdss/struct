import logging
import os
from .file_item import FileItem
from dotenv import load_dotenv
import yaml

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
openai_model = os.getenv("OPENAI_MODEL")

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

def create_structure(base_path, structure, dry_run=False, template_vars=None, backup_path=None, file_strategy='overwrite', global_system_prompt=None):
    for item in structure:
        logging.debug(f"Processing item: {item}")
        for name, content in item.items():
            logging.debug(f"Processing name: {name}, content: {content}")
            if isinstance(content, dict):
                content["name"] = name
                content["global_system_prompt"] = global_system_prompt
                file_item = FileItem(content)
                file_item.fetch_content()
            elif isinstance(content, str):
                file_item = FileItem({"name": name, "content": content})

            file_item.apply_template_variables(template_vars)
            file_item.process_prompt(dry_run)
            file_item.create(base_path, dry_run, backup_path, file_strategy)

def read_config_file(file_path):
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)

def merge_configs(file_config, args):
    args_dict = vars(args)
    for key, value in file_config.items():
        if key in args_dict and args_dict[key] is None:
            args_dict[key] = value
    return args_dict
