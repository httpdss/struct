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

    if args.structures_path is None:
      this_file = os.path.dirname(os.path.realpath(__file__))
      final_path = os.path.join(project_path, "contribs")
    else:
      final_path = os.path.join(args.structures_path)

    print("Listing available structures")
    sorted_list = [structure for structure in os.listdir(final_path) if structure.endswith('.yaml')]
    sorted_list.sort()
    for structure in sorted_list:
      print(f" - {structure[:-5]}")
