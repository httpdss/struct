# FILE: file_item.py
import requests
import os
import shutil
import logging
import time
from dotenv import load_dotenv
from struct_module.template_renderer import TemplateRenderer
from struct_module.content_fetcher import ContentFetcher
from struct_module.model_wrapper import ModelWrapper

load_dotenv()

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
      self.non_interactive = properties.get("non_interactive")
      self.skip = properties.get("skip", False)
      self.skip_if_exists = properties.get("skip_if_exists", False)

      self.content_fetcher = ContentFetcher()

      self.system_prompt = properties.get("system_prompt") or properties.get("global_system_prompt")
      self.user_prompt = properties.get("user_prompt")
      self.mappings = properties.get("mappings", {})

      self.model_wrapper = ModelWrapper(self.logger)

      self.template_renderer = TemplateRenderer(
          self.config_variables,
          self.input_store,
          self.non_interactive,
          self.mappings
      )

    def _get_file_directory(self):
        return os.path.dirname(self.name)

    def process_prompt(self, dry_run=False, existing_content=None):
      if self.user_prompt:

        if not self.system_prompt:
          system_prompt = "You are a software developer working on a project. You need to create a file with the following content:"
        else:
          system_prompt = self.system_prompt

        user_prompt = self.user_prompt
        if existing_content:
          user_prompt += f"\n\nCurrent file content (if any):\n```\n{existing_content}\n```\n\nPlease modify existing content so that it meets the new requirements. Your output should be plain text, without any code blocks or formatting. Do not include any explanations or comments. Just provide the final content of the file."

        self.logger.debug(f"Using system prompt: {system_prompt}")
        self.logger.debug(f"Using user prompt: {user_prompt}")

        self.content = self.model_wrapper.generate_content(
            system_prompt,
            user_prompt,
            dry_run=dry_run
        )
        self.logger.debug(f"Generated content: \n\n{self.content}")

    def fetch_content(self):
      if self.content_location:
        self.logger.debug(f"Fetching content from: {self.content_location}")
        try:
          raw_content = self.content_fetcher.fetch_content(
              self.content_location)
          self.logger.debug(f"Fetched content: {raw_content}")
          # Render the fetched content using the template renderer
          template_vars = self._merge_default_template_vars(
              self.config_variables)
          missing_vars = self.template_renderer.prompt_for_missing_vars(
              raw_content, template_vars)
          template_vars.update(missing_vars)
          self.content = self.template_renderer.render_template(
              raw_content, template_vars)
          self.logger.debug(f"Rendered content: {self.content}")
        except Exception as e:
          self.logger.error(f"❗ Failed to fetch content from {self.content_location}: {e}")

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

      self.vars = vars
      self.logger.debug(f"Final template variables: {self.vars}")

      self.content = self.template_renderer.render_template(self.content, vars)

    def create(self, base_path, dry_run=False, backup_path=None, file_strategy='overwrite'):
      file_path = os.path.join(base_path, self.name)

      file_path = self.template_renderer.render_template(file_path, self.vars)

      if self.skip:
        self.logger.info(f"skip is set to true. skipping creation.")
        return

      if dry_run:
        self.logger.info(f"[DRY RUN] Would create file: {file_path} with content: \n\n{self.content}")
        return

      if self.skip_if_exists and os.path.exists(file_path):
        self.logger.info(f"    skip_if_exists is set to true and file already exists. skipping creation.")
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
              f.write(f"{self.content}\n")
          self.logger.info(f"✅ Appended to existing file: {file_path}")
          return
        elif file_strategy == 'rename':
          new_name = f"{file_path}.{int(time.time())}"
          os.rename(file_path, new_name)
          self.logger.info(f"Renamed existing file: {file_path} to {new_name}")

      with open(file_path, 'w') as f:
        f.write(f"{self.content}\n")
      self.logger.info(f"✅ Created file with content")
      self.logger.info(f"     File path: {file_path}")
      self.logger.debug(f"     Content: \n\n{self.content}")

      if self.permissions:
        os.chmod(file_path, int(self.permissions, 8))
        self.logger.info(f"🔐 Set permissions to file")
        self.logger.info(f"     File path: {file_path}")
        self.logger.info(f"     Permissions: {self.permissions}")
