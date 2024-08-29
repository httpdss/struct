from struct_module.commands import Command
# Info command class
class InfoCommand(Command):
    def __init__(self, parser):
      super().__init__(parser)
      parser.set_defaults(func=self.execute)

    def execute(self, args):
      print("STRUCT 1.0.0")
      print("")
      print("Generate project structure from YAML configuration.")
      print("Commands:")
      print("  generate    Generate the project structure")
      print("  validate    Validate the YAML configuration file")
      print("  info        Show information about the package")
