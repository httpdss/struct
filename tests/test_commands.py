import pytest
from unittest.mock import patch, MagicMock
from struct_module.commands.generate import GenerateCommand
from struct_module.commands.info import InfoCommand
from struct_module.commands.validate import ValidateCommand
from struct_module.commands.list import ListCommand
import argparse

@pytest.fixture
def parser():
    return argparse.ArgumentParser()

def test_generate_command(parser):
    command = GenerateCommand(parser)
    # Patch os.path.exists to always return True for the config file, and patch open/yaml.safe_load to return a minimal config
    with patch('os.path.exists', return_value=True), \
         patch('builtins.open', new_callable=MagicMock) as mock_open, \
         patch('yaml.safe_load', return_value={'files': []}), \
         patch.object(command, '_create_structure') as mock_create_structure:
        args = parser.parse_args(['structure.yaml', 'base_path'])
        command.execute(args)
        mock_create_structure.assert_called_once()

def test_info_command(parser):
    command = InfoCommand(parser)
    args = parser.parse_args(["github/workflows/pre-commit"])
    with patch('builtins.print') as mock_print:
        command.execute(args)
        mock_print.assert_called()

def test_list_command(parser):
    command = ListCommand(parser)
    args = parser.parse_args([])
    with patch('os.walk', return_value=[('root', [], ['file.yaml'])]):
        with patch('builtins.print') as mock_print:
            command.execute(args)
            mock_print.assert_called()

def test_validate_command(parser):
    command = ValidateCommand(parser)
    args = parser.parse_args(['config.yaml'])
    with patch.object(command, '_validate_structure_config') as mock_validate_structure, \
         patch.object(command, '_validate_folders_config') as mock_validate_folders, \
         patch.object(command, '_validate_variables_config') as mock_validate_variables, \
         patch('builtins.open', new_callable=MagicMock) as mock_open, \
         patch('yaml.safe_load', return_value={
             'structure': [],
             'folders': [],
             'variables': []
         }):
        command.execute(args)
        mock_validate_structure.assert_called_once()
        mock_validate_folders.assert_called_once()
        mock_validate_variables.assert_called_once()
