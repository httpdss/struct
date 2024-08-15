import requests
import os
import shutil
import logging
from string import Template
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
openai_model = os.getenv("OPENAI_MODEL")


class FileItem:
    def __init__(self, properties):
        self.name = properties.get("name")
        self.content = properties.get("content")
        self.remote_location = properties.get("file")
        self.permissions = properties.get("permissions")

        self.system_prompt = properties.get("system_prompt") or properties.get("global_system_prompt")
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
            logging.info(f"[DRY RUN] Would create file: {file_path} with content: \n\n{self.content}")
            return

        # Create the directory if it does not exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

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
