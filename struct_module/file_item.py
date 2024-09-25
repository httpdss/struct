# FILE: file_item.py
import requests
import os
import shutil
import logging
import time
from openai import OpenAI
from dotenv import load_dotenv
from struct_module.template_renderer import TemplateRenderer

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
openai_model = os.getenv("OPENAI_MODEL")

class FileItem:
    def __init__(self, properties):
      self.logger = logging.getLogger(__name__)
      self.name = properties.get("name")
      self.file_directory = self._get_file_directory()
      self.content = properties.get("content")
      self.config_variables = properties.get("config_variables")
      self.content_location = properties.get("file")
      self.permissions = properties.get("permissions")
      self.input_store = properties.get("input_store")

      self.system_prompt = properties.get("system_prompt") or properties.get("global_system_prompt")
      self.user_prompt = properties.get("user_prompt")
      self.openai_client = None

      if openai_api_key:
        self._configure_openai()

      self.template_renderer = TemplateRenderer(self.config_variables, self.input_store)

    def _configure_openai(self):
      self.openai_client = OpenAI(api_key=openai_api_key)
      if not openai_model:
        self.logger.debug("OpenAI model not found. Using default model.")
        self.openai_model = "gpt-3.5-turbo"
      else:
        self.logger.debug(f"Using OpenAI model: {openai_model}")
        self.openai_model = openai_model

    def _get_file_directory(self):
        return os.path.dirname(self.name)

    def process_prompt(self, dry_run=False):
      if self.user_prompt:
        self.logger.debug(f"Using user prompt: {self.user_prompt}")

        if not self.openai_client or not openai_api_key:
          self.logger.warning("Skipping processing prompt as OpenAI API key is not set.")
          return

        if not self.system_prompt:
          system_prompt = "You are a software developer working on a project. You need to create a file with the following content:"
        else:
          system_prompt = self.system_prompt

        if dry_run:
          self.logger.info("[DRY RUN] Would generate content using OpenAI API.")
          self.content = "[DRY RUN] Generating content using OpenAI"
          return

        if not self.openai_client or not openai_api_key:
          completion = self.openai_client.chat.completions.create(
            model=self.openai_model,
            messages=[
              {"role": "system", "content": system_prompt},
              {"role": "user", "content": self.user_prompt}
            ]
          )

          self.content = completion.choices[0].message.content
        else:
          self.content = "OpenAI API key not found. Skipping content generation."
          self.logger.warning("Skipping processing prompt as OpenAI API key is not set.")
        self.logger.debug(f"Generated content: \n\n{self.content}")

    def fetch_content(self):
      if self.content_location:
        self.logger.debug(f"Fetching content from: {self.content_location}")

        if self.content_location.startswith("file://"):
          file_path = self.content_location[len("file://"):]
          with open(file_path, 'r') as file:
            self.content = file.read()
          self.logger.debug(f"Fetched content from local file: {self.content}")

        elif self.content_location.startswith("https://"):
          response = requests.get(self.content_location)
          self.logger.debug(f"Response status code: {response.status_code}")
          response.raise_for_status()
          self.content = response.text
          self.logger.debug(f"Fetched content from URL: {self.content}")

        else:
          self.logger.warning(f"Unsupported protocol in content_location: {self.content_location}")

    def _merge_default_template_vars(self, template_vars):
      default_vars = {
        "file_name": self.name,
        "file_directory": self.file_directory,
      }
      if not template_vars:
        return default_vars
      return {**default_vars, **template_vars}

    def apply_template_variables(self, template_vars):
      vars = self._merge_default_template_vars(template_vars)
      self.logger.debug(f"Applying template variables: {vars}")

      missing_vars = self.template_renderer.prompt_for_missing_vars(self.content, vars)
      vars.update(missing_vars)

      self.content = self.template_renderer.render_template(self.content, vars)

    def create(self, base_path, dry_run=False, backup_path=None, file_strategy='overwrite'):
      file_path = os.path.join(base_path, self.name)
      if dry_run:
        self.logger.info(f"[DRY RUN] Would create file: {file_path} with content: \n\n{self.content}")
        return

      # Create the directory if it does not exist
      os.makedirs(os.path.dirname(file_path), exist_ok=True)

      if os.path.exists(file_path):
        if file_strategy == 'backup' and backup_path:
          backup_file_path = os.path.join(backup_path, os.path.basename(file_path))
          shutil.copy2(file_path, backup_file_path)
          self.logger.info(f"Backed up existing file: {file_path} to {backup_file_path}")
        elif file_strategy == 'skip':
          self.logger.info(f"Skipped existing file: {file_path}")
          return
        elif file_strategy == 'append':
          with open(file_path, 'a') as f:
              f.write(self.content)
          self.logger.info(f"Appended to existing file: {file_path}")
          return
        elif file_strategy == 'rename':
          new_name = f"{file_path}.{int(time.time())}"
          os.rename(file_path, new_name)
          self.logger.info(f"Renamed existing file: {file_path} to {new_name}")

      with open(file_path, 'w') as f:
        f.write(self.content)
      self.logger.debug(f"Created file: {file_path} with content: \n\n{self.content}")

      if self.permissions:
        os.chmod(file_path, int(self.permissions, 8))
        self.logger.info(f"Set permissions {self.permissions} for file: {file_path}")
