import os
import yaml
from dotenv import load_dotenv
from struct_module.commands import Command

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
openai_model = os.getenv("OPENAI_MODEL")

# Validate command class
class ValidateCommand(Command):
    def __init__(self, parser):
        super().__init__(parser)
        parser.add_argument('yaml_file', type=str, help='Path to the YAML configuration file')
        parser.set_defaults(func=self.execute)

    def execute(self, args):
        self.logger.info(f"Validating {args.yaml_file}")

        with open(args.yaml_file, 'r') as f:
            config = yaml.safe_load(f)

        self._validate_configuration(config.get('structure', []))


    def _validate_configuration(self, structure):
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
        self.logger.info("Configuration validation passed.")
