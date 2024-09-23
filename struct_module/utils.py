import yaml
import os

def read_config_file(file_path):
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)


def merge_configs(file_config, args):
    args_dict = vars(args)
    for key, value in file_config.items():
        if key in args_dict and args_dict[key] is None:
            args_dict[key] = value
    return args_dict

project_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")
