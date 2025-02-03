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
    args = parser.parse_args(['structure.yaml', 'base_path'])
    with patch.object(command, '_create_structure') as mock_create_structure:
        command.execute(args)
        mock_create_structure.assert_called_once()

def test_info_command(parser):
    command = InfoCommand(parser)
    args = parser.parse_args([])
    with patch('builtins.print') as mock_print:
        command.execute(args)
        mock_print.assert_called()

def test_validate_command(parser):
    command = ValidateCommand(parser)
    args = parser.parse_args(['config.yaml'])
    with patch('builtins.open', patch.mock_open(read_data="structure: []")):
        with patch('yaml.safe_load', return_value={'structure': []}):
            with patch.object(command, '_validate_structure_config') as mock_validate_structure:
                with patch.object(command, '_validate_folders_config') as mock_validate_folders:
                    with patch.object(command, '_validate_variables_config') as mock_validate_variables:
                        command.execute(args)
                        mock_validate_structure.assert_called_once()
                        mock_validate_folders.assert_called_once()
                        mock_validate_variables.assert_called_once()

def test_list_command(parser):
    command = ListCommand(parser)
    args = parser.parse_args([])
    with patch('os.walk', return_value=[('root', [], ['file.yaml'])]):
        with patch('builtins.print') as mock_print:
            command.execute(args)
            mock_print.assert_called()
