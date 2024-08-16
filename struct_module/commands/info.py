from struct_module.commands import Command
# Info command class
class InfoCommand(Command):
    def __init__(self, parser):
        super().__init__(parser)
        parser.set_defaults(func=self.execute)

    def execute(self, args):
        print("Info about the package")
