class ChoicesCompleter(object):
    def __init__(self, choices):
        self.choices = choices

    def __call__(self, **kwargs):
        return self.choices


log_level_completer = ChoicesCompleter(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
file_strategy_completer = ChoicesCompleter(['overwrite', 'skip', 'append', 'rename', 'backup'])
