"""Tests for the config command."""

import pytest
import argparse
import tempfile
import os
import yaml
import json
from unittest.mock import patch, MagicMock
from pathlib import Path
from structkit.commands.config import ConfigCommand


@pytest.fixture
def parser():
    return argparse.ArgumentParser()


@pytest.fixture
def config_command(parser):
    return ConfigCommand(parser)


def test_config_command_no_subcommand(parser, capsys):
    """Test config command without subcommand shows help."""
    command = ConfigCommand(parser)
    args = parser.parse_args([])

    command.execute(args)

    captured = capsys.readouterr()
    assert 'usage:' in captured.out or 'Display and manage structkit configuration' in captured.out


def test_config_print_yaml_format(parser):
    """Test config print command with YAML format."""
    command = ConfigCommand(parser)

    # Create a temporary config file
    config_data = """
file_strategy: skip
input_store: /custom/input.json
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_data)
        f.flush()
        temp_path = f.name

    try:
        with patch('structkit.config.get_user_config_path') as mock_user_path:
            mock_user_path.return_value = Path('/nonexistent/user/config.yaml')

            args = parser.parse_args(['print', '--format', 'yaml', '-c', temp_path])
            args.config_file = temp_path

            with patch('builtins.print') as mock_print:
                command.execute(args)
                mock_print.assert_called()

                # Get the printed output
                printed_output = mock_print.call_args[0][0]

                # Parse the YAML output
                printed_config = yaml.safe_load(printed_output)

                # Check that config was merged correctly
                assert printed_config['file_strategy'] == 'skip'
                assert printed_config['input_store'] == '/custom/input.json'
    finally:
        os.unlink(temp_path)


def test_config_print_json_format(parser):
    """Test config print command with JSON format."""
    command = ConfigCommand(parser)

    # Create a temporary config file
    config_data = """
file_strategy: backup
structures_path: /custom/structures
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_data)
        f.flush()
        temp_path = f.name

    try:
        with patch('structkit.config.get_user_config_path') as mock_user_path:
            mock_user_path.return_value = Path('/nonexistent/user/config.yaml')

            args = parser.parse_args(['print', '--format', 'json', '-c', temp_path])
            args.config_file = temp_path

            with patch('builtins.print') as mock_print:
                command.execute(args)
                mock_print.assert_called()

                # Get the printed output
                printed_output = mock_print.call_args[0][0]

                # Parse the JSON output
                printed_config = json.loads(printed_output)

                # Check that config was merged correctly
                assert printed_config['file_strategy'] == 'backup'
                assert printed_config['structures_path'] == '/custom/structures'
    finally:
        os.unlink(temp_path)


def test_config_print_with_cli_override(parser):
    """Test that CLI args override config file values in print output."""
    command = ConfigCommand(parser)

    # Create a temporary config file
    config_data = """
file_strategy: skip
log: WARNING
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_data)
        f.flush()
        temp_path = f.name

    try:
        with patch('structkit.config.get_user_config_path') as mock_user_path:
            mock_user_path.return_value = Path('/nonexistent/user/config.yaml')

            # Simulate CLI args that override config
            args = parser.parse_args(['print', '-c', temp_path, '--log', 'DEBUG'])
            args.config_file = temp_path

            with patch('builtins.print') as mock_print:
                command.execute(args)

                # Get the printed output
                printed_output = mock_print.call_args[0][0]
                printed_config = yaml.safe_load(printed_output)

                # CLI arg should override config file
                assert printed_config['log'] == 'DEBUG'
    finally:
        os.unlink(temp_path)


def test_config_print_default_format(parser):
    """Test that config print defaults to YAML format."""
    command = ConfigCommand(parser)

    with patch('structkit.config.get_user_config_path') as mock_user_path:
        mock_user_path.return_value = Path('/nonexistent/user/config.yaml')

        args = parser.parse_args(['print'])

        with patch('builtins.print') as mock_print:
            command.execute(args)
            mock_print.assert_called()

            # Get the printed output
            printed_output = mock_print.call_args[0][0]

            # Should be valid YAML
            printed_config = yaml.safe_load(printed_output)
            assert isinstance(printed_config, dict)
            assert 'file_strategy' in printed_config


def test_config_print_shows_all_layers(parser):
    """Test that config print merges all config layers."""
    command = ConfigCommand(parser)

    user_config_data = """
input_store: /user/input.json
file_strategy: skip
"""
    project_config_data = """
file_strategy: backup
structures_path: /project/structures
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as user_f, \
         tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as project_f:
        user_f.write(user_config_data)
        user_f.flush()
        temp_user_path = user_f.name

        project_f.write(project_config_data)
        project_f.flush()
        temp_project_path = project_f.name

        try:
            with patch('structkit.config.get_user_config_path') as mock_user_path:
                mock_user_path.return_value = Path(temp_user_path)

                args = parser.parse_args(['print', '-c', temp_project_path])
                args.config_file = temp_project_path

                with patch('builtins.print') as mock_print:
                    command.execute(args)

                    # Get the printed output
                    printed_output = mock_print.call_args[0][0]
                    printed_config = yaml.safe_load(printed_output)

                    # Project config should override user config
                    assert printed_config['file_strategy'] == 'backup'  # From project
                    assert printed_config['input_store'] == '/user/input.json'  # From user
                    assert printed_config['structures_path'] == '/project/structures'  # From project
                    # Should also have built-in defaults
                    assert 'log' in printed_config
        finally:
            os.unlink(temp_user_path)
            os.unlink(temp_project_path)
