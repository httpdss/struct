from struct_module.commands import Command
import os
import yaml
from struct_module.file_item import FileItem

# Generate command class
class GenerateCommand(Command):
  def __init__(self, parser):
    super().__init__(parser)
    parser.add_argument('yaml_file', type=str, help='Path to the YAML configuration file')
    parser.add_argument('base_path', type=str, help='Base path where the structure will be created')
    parser.add_argument('-d', '--dry-run', action='store_true', help='Perform a dry run without creating any files or directories')
    parser.add_argument('-v', '--vars', type=str, help='Template variables in the format KEY1=value1,KEY2=value2')
    parser.add_argument('-b', '--backup', type=str, help='Path to the backup folder')
    parser.add_argument('-f', '--file-strategy', type=str, choices=['overwrite', 'skip', 'append', 'rename', 'backup'], default='overwrite', help='Strategy for handling existing files')
    parser.add_argument('-p', '--global-system-prompt', type=str, help='Global system prompt for OpenAI')
    parser.set_defaults(func=self.execute)

  def execute(self, args):
    self.logger.info(f"Generating structure at {args.base_path} with config {args.yaml_file}")

    if args.backup and not os.path.exists(args.backup):
      os.makedirs(args.backup)

    if args.base_path and not os.path.exists(args.base_path):
      self.logger.info(f"Creating base path: {args.base_path}")
      os.makedirs(args.base_path)

    self._create_structure(args)


  def _create_structure(self, args):
    with open(args.yaml_file, 'r') as f:
      config = yaml.safe_load(f)

    template_vars = dict(item.split('=') for item in args.vars.split(',')) if args.vars else None
    structure = config.get('structure', [])

    for item in structure:
      self.logger.debug(f"Processing item: {item}")
      for name, content in item.items():
        self.logger.debug(f"Processing name: {name}, content: {content}")
        if isinstance(content, dict):
          content["name"] = name
          content["global_system_prompt"] = args.global_system_prompt
          file_item = FileItem(content)
          file_item.fetch_content()
        elif isinstance(content, str):
          file_item = FileItem({"name": name, "content": content})

          file_item.apply_template_variables(template_vars)
          file_item.process_prompt(args.dry_run)
          file_item.create(
            args.base_path,
            args.dry_run or False,
            args.backup_path or None,
            args.file_strategy or 'overwrite'
          )
