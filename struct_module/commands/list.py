from struct_module.commands import Command
import os
import yaml
from struct_module.file_item import FileItem

# List command class
class ListCommand(Command):
  def __init__(self, parser):
    super().__init__(parser)
    parser.set_defaults(func=self.execute)

  def execute(self, args):
    self.logger.info(f"Listing available structures")
    self._list_structures()

  def _list_structures(self):
    print("Listing available structures")
    sorted_list = [structure for structure in os.listdir('contribs') if structure.endswith('.yaml')]
    sorted_list.sort()
    for structure in sorted_list:
      print(f" - {structure[:-5]}")
