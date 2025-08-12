# FILE: template_renderer.py
import logging
import os
import sys
from jinja2 import Environment, meta
from struct_module.filters import (
  get_latest_release,
  slugify,
  get_default_branch,
  gen_uuid,
  now_iso,
  env as env_get,
  read_file,
  to_yaml,
  from_yaml,
  to_json,
  from_json,
)
from struct_module.input_store import InputStore
from struct_module.utils import get_current_repo

class TemplateRenderer:
    def __init__(self, config_variables, input_store, non_interactive, mappings=None):
      self.config_variables = config_variables
      self.non_interactive = non_interactive
      self.mappings = mappings or {}

      self.env = Environment(
        trim_blocks=True,
        block_start_string='{%@',
        block_end_string='@%}',
        variable_start_string='{{@',
        variable_end_string='@}}',
        comment_start_string='{#@',
        comment_end_string='@#}'
      )

      self.logger = logging.getLogger(__name__)

      custom_filters = {
        'latest_release': get_latest_release,
        'slugify': slugify,
        'default_branch': get_default_branch,
        'to_yaml': to_yaml,
        'from_yaml': from_yaml,
        'to_json': to_json,
        'from_json': from_json,
      }

      globals = {
        'current_repo': get_current_repo,
        'uuid': gen_uuid,
        'now': now_iso,
        'env': env_get,
        'read_file': read_file,
      }

      self.env.globals.update(globals)
      self.env.filters.update(custom_filters)
      self.input_store = InputStore(input_store)
      self.input_store.load()
      self.input_data = self.input_store.get_data()

    # Get the config variables from the list and create a dictionary that has
    # variable name and their default value
    #
    # Example:
    # variables:
    #   - session_name:
    #       type: string
    #       default: my_session
    #   - project_name:
    #       type: string
    #       default: my_project
    #       help: The name of the project
    #
    # Returns:
    #   {'session_name': 'my_session', 'project_name': 'my_project'}
    def get_defaults_from_config(self):
      self.logger.debug(f"Config variables: {self.config_variables}")
      defaults = {}
      for item in self.config_variables:
        for name, content in item.items():
          # Explicit default value
          if 'default' in content:
            defaults[name] = content.get('default')
          # Default from environment variable (env or default_from_env)
          env_key = content.get('env') or content.get('default_from_env')
          if env_key and os.environ.get(env_key) is not None:
            defaults[name] = os.environ.get(env_key)
      return defaults


    def render_template(self, content, vars):
      # Inject mappings into the template context
      if self.mappings:
        vars = vars.copy() if vars else {}
        vars['mappings'] = self.mappings
      template = self.env.from_string(content)
      return template.render(vars)

    def prompt_for_missing_vars(self, content, vars):
      parsed_content = self.env.parse(content)
      undeclared_variables = meta.find_undeclared_variables(parsed_content)
      self.logger.debug(f"Undeclared variables: {undeclared_variables}")

      # Build schema lookup
      schema = {}
      for item in (self.config_variables or []):
        for name, conf in item.items():
          schema[name] = conf or {}

      # Prompt the user for any missing variables
      # Suggest a default from the config if available
      default_values = self.get_defaults_from_config()
      self.logger.debug(f"Default values from config: {default_values}")

      for var in undeclared_variables:
        if var not in vars:
          conf = schema.get(var, {})
          required = conf.get('required', False)
          default = self.input_data.get(var, default_values.get(var, ""))
          if self.non_interactive:
            if required and (default is None or default == ""):
              raise ValueError(f"Missing required variable '{var}' in non-interactive mode")
            user_input = default
          else:
            # Interactive prompt with enum support (choose by value or index)
            enum = conf.get('enum')
            if enum:
              # Build options list string like "(1) dev, (2) prod)"
              options = ", ".join([f"({i+1}) {val}" for i, val in enumerate(enum)])
              while True:
                raw = input(f"❓ Enter value for {var} [{default}] {options}: ")
                raw = raw.strip()
                if raw == "":
                  user_input = default
                elif raw.isdigit() and 1 <= int(raw) <= len(enum):
                  user_input = enum[int(raw) - 1]
                else:
                  # accept exact match from enum
                  if raw in enum:
                    user_input = raw
                  else:
                    print(f"Invalid choice. Please enter one of: {options} or a valid value.")
                    continue
                break
            else:
              user_input = input(f"❓ Enter value for {var} [{default}]: ") or default
          # Coerce and validate according to schema
          coerced = self._coerce_and_validate(var, user_input, conf)
          self.input_store.set_value(var, coerced)
          vars[var] = coerced
      self.input_store.save()
      return vars

    def _coerce_and_validate(self, name, value, conf):
      # Type coercion
      vtype = (conf.get('type') or 'string').lower()
      original = value
      try:
        if vtype == 'boolean' or vtype == 'bool':
          if isinstance(value, bool):
            coerced = value
          elif isinstance(value, str):
            coerced = value.strip().lower() in ['1', 'true', 'yes', 'y', 'on']
          else:
            coerced = bool(value)
        elif vtype == 'number' or vtype == 'float':
          coerced = float(value) if value != '' and value is not None else None
        elif vtype == 'integer' or vtype == 'int':
          coerced = int(value) if value not in (None, '') else None
        else:
          coerced = '' if value is None else str(value)
      except Exception:
        raise ValueError(f"Variable '{name}' could not be coerced to {vtype} (value: {original})")

      # Enum validation
      enum = conf.get('enum')
      if enum is not None and coerced not in enum:
        raise ValueError(f"Variable '{name}' must be one of {enum}, got: {coerced}")

      # Regex validation (only for strings)
      pattern = conf.get('regex') or conf.get('pattern')
      if pattern and isinstance(coerced, str):
        import re as _re
        if _re.fullmatch(pattern, coerced) is None:
          raise ValueError(f"Variable '{name}' does not match required pattern: {pattern}")

      # Min/Max validation
      def _as_num(x):
        try:
          return float(x)
        except Exception:
          return None
      minv = conf.get('min')
      maxv = conf.get('max')
      if minv is not None:
        cv = _as_num(coerced)
        if cv is not None and cv < float(minv):
          raise ValueError(f"Variable '{name}' must be >= {minv}, got {coerced}")
      if maxv is not None:
        cv = _as_num(coerced)
        if cv is not None and cv > float(maxv):
          raise ValueError(f"Variable '{name}' must be <= {maxv}, got {coerced}")

      return coerced
