from struct_module.commands import Command
import os
import yaml
from struct_module.file_item import FileItem
from struct_module.utils import project_path

# List command class
class ListCommand(Command):
  def __init__(self, parser):
    super().__init__(parser)
    parser.add_argument('-s', '--structures-path', type=str, help='Path to structure definitions')
    parser.set_defaults(func=self.execute)

  def execute(self, args):
    self.logger.info(f"Listing available structures")
    self._list_structures(args)

  def _list_structures(self, args):
    this_file = os.path.dirname(os.path.realpath(__file__))
    contribs_path = os.path.join(this_file, "..", "contribs")

    if args.structures_path:
      final_path = args.structures_path
      paths_to_list = [final_path, contribs_path]
    else:
      paths_to_list = [contribs_path]

    print("Listing available structures")
    all_structures = set()
    for path in paths_to_list:
      for root, _, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, path)
            if file.endswith(".yaml"):
              all_structures.add(rel_path)

    sorted_list = sorted(all_structures)
    for structure in sorted_list:
      print(f" - {structure[:-5]}")
