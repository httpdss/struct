import pytest
from struct_module.completers import log_level_completer, file_strategy_completer

def test_log_level_completer():
    completer = log_level_completer()
    assert 'DEBUG' in completer
    assert 'INFO' in completer
    assert 'WARNING' in completer
    assert 'ERROR' in completer
    assert 'CRITICAL' in completer

def test_file_strategy_completer():
    completer = file_strategy_completer()
    assert 'overwrite' in completer
    assert 'skip' in completer
    assert 'append' in completer
    assert 'rename' in completer
    assert 'backup' in completer
