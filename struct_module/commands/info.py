import os
import yaml

from struct_module.commands import Command

# Info command class for exposing information about the structure
class InfoCommand(Command):
    def __init__(self, parser):
      super().__init__(parser)
      parser.add_argument('structure_definition', type=str, help='Name of the structure definition')
      parser.add_argument('-s', '--structures-path', type=str, help='Path to structure definitions')

      parser.set_defaults(func=self.execute)

    def execute(self, args):
      self.logger.info(f"Getting info for structure {args.structure_definition}")

      self._get_info(args)

    def _get_info(self, args):
      if args.structure_definition.startswith("file://") and args.structure_definition.endswith(".yaml"):
        with open(args.structure_definition[7:], 'r') as f:
          config = yaml.safe_load(f)
      else:
        if args.structures_path is None:
          this_file = os.path.dirname(os.path.realpath(__file__))
          file_path = os.path.join(this_file, "..", "contribs", f"{args.structure_definition}.yaml")
        else:
          file_path = os.path.join(args.structures_path, f"{args.structure_definition}.yaml")
        # show error if file is not found
        if not os.path.exists(file_path):
          self.logger.error(f"❗ File not found: {file_path}")
          return
        with open(file_path, 'r') as f:
          config = yaml.safe_load(f)

      print("📒 Structure definition\n")
      print(f"   📌 Name: {args.structure_definition}\n")
      print(f"   📌 Description: {config.get('description', 'No description')}\n")

      if config.get('files'):
        print(f"   📌 Files:")
        for item in config.get('files', []):
          for name, content in item.items():
            print(f"       - {name} ")
            # indent all lines of content
            # for line in content.get('content', content.get('file', 'Not defined')).split('\n'):
            #   print(f"       {line}")

      if config.get('folders'):
        print(f"   📌 Folders:")
        for folder in config.get('folders', []):
          print(f"     - {folder}")
          # print(f"     - {folder}: {folder.get('struct', 'No structure')}")
