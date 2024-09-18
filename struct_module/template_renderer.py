# FILE: template_renderer.py
import logging
from jinja2 import Environment, meta
from struct_module.filters import get_latest_release, stringify

class TemplateRenderer:
    def __init__(self, config_variables):
      self.config_variables = config_variables
      self.env = Environment(
        trim_blocks=True,
        block_start_string='{%@',
        block_end_string='@%}',
        variable_start_string='{{@',
        variable_end_string='@}}',
        comment_start_string='{#@',
        comment_end_string='@#}'
      )

      custom_filters = {
        'latest_release': get_latest_release,
        'stringify': stringify,
      }
      self.env.filters.update(custom_filters)
      self.logger = logging.getLogger(__name__)

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
      for name, content in self.config_variables.items():
        if 'default' in content:
          defaults[name] = content.get('default')
      self.logger.debug(f"Defaults: {defaults}")
      return defaults


    def render_template(self, content, vars):
      template = self.env.from_string(content)
      return template.render(vars)

    def prompt_for_missing_vars(self, content, vars):
      parsed_content = self.env.parse(content)
      undeclared_variables = meta.find_undeclared_variables(parsed_content)
      self.logger.debug(f"Undeclared variables: {undeclared_variables}")

      # Prompt the user for any missing variables
      # Suggest a default from the config if available
      default_values = self.get_defaults_from_config()
      self.logger.debug(f"Default values from config: {default_values}")

      for var in undeclared_variables:
        if var not in vars:
          default = default_values.get(var, "")
          user_input = input(f"Enter value for {var} [{default}]: ")
          if not user_input:
            user_input = default
          vars[var] = user_input
      return vars
