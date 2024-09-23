from struct_module.commands import Command
import os
import yaml
import argparse
from struct_module.file_item import FileItem
from struct_module.completers import file_strategy_completer
from struct_module.utils import project_path

# Generate command class
class GenerateCommand(Command):
  def __init__(self, parser):
    super().__init__(parser)
    parser.add_argument('structure_definition', type=str, help='Path to the YAML configuration file')
    parser.add_argument('base_path', type=str, help='Base path where the structure will be created')
    parser.add_argument('-s', '--structures-path', type=str, help='Path to structure definitions')
    parser.add_argument('-d', '--dry-run', action='store_true', help='Perform a dry run without creating any files or directories')
    parser.add_argument('-v', '--vars', type=str, help='Template variables in the format KEY1=value1,KEY2=value2')
    parser.add_argument('-b', '--backup', type=str, help='Path to the backup folder')
    parser.add_argument('-f', '--file-strategy', type=str, choices=['overwrite', 'skip', 'append', 'rename', 'backup'], default='overwrite', help='Strategy for handling existing files').completer = file_strategy_completer
    parser.add_argument('-p', '--global-system-prompt', type=str, help='Global system prompt for OpenAI')
    parser.set_defaults(func=self.execute)

  def execute(self, args):
    self.logger.info(f"Generating structure at {args.base_path} with config {args.structure_definition}")

    if args.backup and not os.path.exists(args.backup):
      os.makedirs(args.backup)

    if args.base_path and not os.path.exists(args.base_path):
      self.logger.info(f"Creating base path: {args.base_path}")
      os.makedirs(args.base_path)

    self._create_structure(args)


  def _create_structure(self, args):
    if isinstance(args, dict):
        args = argparse.Namespace(**args)
    if args.structure_definition.startswith("file://") and args.structure_definition.endswith(".yaml"):
      with open(args.structure_definition[7:], 'r') as f:
        config = yaml.safe_load(f)
    else:
      if args.structures_path is None:
        this_file = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(project_path, "contribs", f"{args.structure_definition}.yaml")
      else:
        file_path = os.path.join(args.structures_path, f"{args.structure_definition}.yaml")
      # show error if file is not found
      if not os.path.exists(file_path):
        self.logger.error(f"File not found: {file_path}")
        return
      with open(file_path, 'r') as f:
        config = yaml.safe_load(f)

    template_vars = dict(item.split('=') for item in args.vars.split(',')) if args.vars else None
    config_structure = config.get('structure', [])
    config_folders = config.get('folders', [])
    config_variables = config.get('variables', [])

    for item in config_structure:
      self.logger.debug(f"Processing item: {item}")
      for name, content in item.items():
        self.logger.debug(f"Processing name: {name}, content: {content}")
        if isinstance(content, dict):
          content["name"] = name
          content["global_system_prompt"] = args.global_system_prompt
          content["config_variables"] = config_variables
          file_item = FileItem(content)
          file_item.fetch_content()
        elif isinstance(content, str):
          file_item = FileItem(
            {"name": name,
             "content": content,
             "config_variables": config_variables,
            }
          )

        file_item.apply_template_variables(template_vars)
        file_item.process_prompt(args.dry_run)

        file_item.create(
          args.base_path,
          args.dry_run or False,
          args.backup or None,
          args.file_strategy or 'overwrite'
        )

    for item in config_folders:
      for folder, content in item.items():
        folder_path = os.path.join(args.base_path, folder)
        if args.dry_run:
          self.logger.info(f"[DRY RUN] Would create folder: {folder_path}")
          continue
        os.makedirs(folder_path, exist_ok=True)
        self.logger.info(f"Created folder: {folder_path}")

        # check if content has struct value
        if 'struct' in content:
          self.logger.info(f"Generating structure in folder: {folder} with struct {content['struct']}")
          if isinstance(content['struct'], str):

            self._create_structure({
              'structure_definition': content['struct'],
              'base_path': folder_path,
              'structures_path': args.structures_path,
              'dry_run': args.dry_run,
              'vars': args.vars,
              'backup': args.backup,
              'file_strategy': args.file_strategy,
              'global_system_prompt': args.global_system_prompt,
            })
          elif isinstance(content['struct'], list):
            for struct in content['struct']:
              self._create_structure({
                'structure_definition': struct,
                'base_path': folder_path,
                'structures_path': args.structures_path,
                'dry_run': args.dry_run,
                'vars': args.vars,
                'backup': args.backup,
                'file_strategy': args.file_strategy,
                'global_system_prompt': args.global_system_prompt,
              })
        else:
          self.logger.warning(f"Unsupported content in folder: {folder}")
