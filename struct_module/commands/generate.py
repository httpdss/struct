from struct_module.commands import Command
import os
import yaml
import argparse
from struct_module.file_item import FileItem
from struct_module.completers import file_strategy_completer
from struct_module.utils import project_path
import subprocess

# Generate command class
class GenerateCommand(Command):
  def __init__(self, parser):
    super().__init__(parser)
    parser.add_argument('structure_definition', type=str, help='Path to the YAML configuration file')
    parser.add_argument('base_path', type=str, help='Base path where the structure will be created')
    parser.add_argument('-s', '--structures-path', type=str, help='Path to structure definitions')
    parser.add_argument('-n', '--input-store', type=str, help='Path to the input store', default='/tmp/struct/input.json')
    parser.add_argument('-d', '--dry-run', action='store_true', help='Perform a dry run without creating any files or directories')
    parser.add_argument('-v', '--vars', type=str, help='Template variables in the format KEY1=value1,KEY2=value2')
    parser.add_argument('-b', '--backup', type=str, help='Path to the backup folder')
    parser.add_argument('-f', '--file-strategy', type=str, choices=['overwrite', 'skip', 'append', 'rename', 'backup'], default='overwrite', help='Strategy for handling existing files').completer = file_strategy_completer
    parser.add_argument('-p', '--global-system-prompt', type=str, help='Global system prompt for OpenAI')
    parser.add_argument('--non-interactive', action='store_true', help='Run the command in non-interactive mode')
    parser.add_argument('--mappings-file', type=str,
                        help='Path to a YAML file containing mappings to be used in templates')
    parser.set_defaults(func=self.execute)

  def _run_hooks(self, hooks, hook_type="pre"):  # helper for running hooks
    if not hooks:
      return True
    for cmd in hooks:
      self.logger.info(f"Running {hook_type}-hook: {cmd}")
      try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
          self.logger.info(f"{hook_type}-hook stdout: {result.stdout.strip()}")
        if result.stderr:
          self.logger.info(f"{hook_type}-hook stderr: {result.stderr.strip()}")
      except subprocess.CalledProcessError as e:
        self.logger.error(f"{hook_type}-hook failed: {cmd}")
        self.logger.error(f"Return code: {e.returncode}")
        if e.stdout:
          self.logger.error(f"stdout: {e.stdout.strip()}")
        if e.stderr:
          self.logger.error(f"stderr: {e.stderr.strip()}")
        return False
    return True

  def _load_yaml_config(self, structure_definition, structures_path):
    if structure_definition.startswith("file://") and structure_definition.endswith(".yaml"):
      with open(structure_definition[7:], 'r') as f:
        return yaml.safe_load(f)
    else:
      this_file = os.path.dirname(os.path.realpath(__file__))
      contribs_path = os.path.join(this_file, "..", "contribs")
      file_path = os.path.join(contribs_path, f"{structure_definition}.yaml")
      if structures_path:
        file_path = os.path.join(structures_path, f"{structure_definition}.yaml")
      if not os.path.exists(file_path):
        file_path = os.path.join(contribs_path, f"{structure_definition}.yaml")
      if not os.path.exists(file_path):
        self.logger.error(f"❗ File not found: {file_path}")
        return None
      with open(file_path, 'r') as f:
        return yaml.safe_load(f)

  def execute(self, args):
    self.logger.info(f"Generating structure")
    self.logger.info(f"  Structure definition: {args.structure_definition}")
    self.logger.info(f"  Base path: {args.base_path}")

    # Load mappings if provided
    mappings = {}
    if getattr(args, 'mappings_file', None):
      if os.path.exists(args.mappings_file):
        with open(args.mappings_file, 'r') as mf:
          try:
            mappings = yaml.safe_load(mf) or {}
          except Exception as e:
            self.logger.error(f"Failed to load mappings file: {e}")
      else:
        self.logger.error(f"Mappings file not found: {args.mappings_file}")

    if args.backup and not os.path.exists(args.backup):
      os.makedirs(args.backup)

    if args.base_path and not os.path.exists(args.base_path):
      self.logger.info(f"Creating base path: {args.base_path}")
      os.makedirs(args.base_path)

    # Load config to check for hooks
    config = None
    config = self._load_yaml_config(args.structure_definition, args.structures_path)
    if config is None:
      return

    pre_hooks = config.get('pre_hooks', [])
    post_hooks = config.get('post_hooks', [])

    # Run pre-hooks
    if not self._run_hooks(pre_hooks, hook_type="pre"):
      self.logger.error("Aborting generation due to pre-hook failure.")
      return

    # Actually generate structure
    self._create_structure(args, mappings)

    # Run post-hooks
    if not self._run_hooks(post_hooks, hook_type="post"):
      self.logger.error("Post-hook failed.")
      return

  def _create_structure(self, args, mappings=None):
    if isinstance(args, dict):
        args = argparse.Namespace(**args)
    this_file = os.path.dirname(os.path.realpath(__file__))
    contribs_path = os.path.join(this_file, "..", "contribs")

    config = self._load_yaml_config(args.structure_definition, args.structures_path)
    if config is None:
      return

    template_vars = dict(item.split('=') for item in args.vars.split(',')) if args.vars else None
    config_structure = config.get('files', config.get('structure', []))
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
          content["input_store"] = args.input_store
          content["non_interactive"] = args.non_interactive
          content["mappings"] = mappings or {}
          file_item = FileItem(content)
          file_item.fetch_content()
        elif isinstance(content, str):
          file_item = FileItem(
            {
              "name": name,
              "content": content,
              "config_variables": config_variables,
              "input_store": args.input_store,
              "non_interactive": args.non_interactive,
              "mappings": mappings or {},
            }
          )

        # Determine the full file path
        file_path_to_create = os.path.join(args.base_path, name)
        existing_content = None
        if os.path.exists(file_path_to_create):
          self.logger.warning(f"⚠️ File already exists: {file_path_to_create}")
          with open(file_path_to_create, 'r') as existing_file:
            existing_content = existing_file.read()

        file_item.process_prompt(
          args.dry_run,
          existing_content=existing_content
        )
        file_item.apply_template_variables(template_vars)

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
        self.logger.info(f"Created folder")
        self.logger.info(f"  Folder: {folder_path}")

        # check if content has struct value
        if 'struct' in content:
          self.logger.info(f"Generating structure")
          self.logger.info(f"  Folder: {folder}")
          self.logger.info(f"  Struct:")
          if isinstance(content['struct'], list):
            # iterate over the list of structures
            for struct in content['struct']:
              self.logger.info(f"    - {struct}")
          if isinstance(content['struct'], str):
            self.logger.info(f"    - {content['struct']}")

          # get vars from with param. this will be a dict of key value pairs
          merged_vars = ""

          # dict to comma separated string
          if 'with' in content:
            if isinstance(content['with'], dict):
              merged_vars = ",".join([f"{k}={v}" for k, v in content['with'].items()])

          if args.vars:
            merged_vars = args.vars + "," + merged_vars

          if isinstance(content['struct'], str):
            self._create_structure({
              'structure_definition': content['struct'],
              'base_path': folder_path,
              'structures_path': args.structures_path,
              'dry_run': args.dry_run,
              'vars': merged_vars,
              'backup': args.backup,
              'file_strategy': args.file_strategy,
              'global_system_prompt': args.global_system_prompt,
              'input_store': args.input_store,
              'non_interactive': args.non_interactive,
            })
          elif isinstance(content['struct'], list):
            for struct in content['struct']:
              self._create_structure({
                'structure_definition': struct,
                'base_path': folder_path,
                'structures_path': args.structures_path,
                'dry_run': args.dry_run,
                'vars': merged_vars,
                'backup': args.backup,
                'file_strategy': args.file_strategy,
                'global_system_prompt': args.global_system_prompt,
                'input_store': args.input_store,
                'non_interactive': args.non_interactive,
              })
        else:
          self.logger.warning(f"Unsupported content in folder: {folder}")
