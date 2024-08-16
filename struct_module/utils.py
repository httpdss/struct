import logging
import os
from .file_item import FileItem
from dotenv import load_dotenv
import yaml

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
openai_model = os.getenv("OPENAI_MODEL")








def read_config_file(file_path):
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)


def merge_configs(file_config, args):
    args_dict = vars(args)
    for key, value in file_config.items():
        if key in args_dict and args_dict[key] is None:
            args_dict[key] = value
    return args_dict
