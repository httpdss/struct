import pytest
from unittest.mock import patch, MagicMock
from struct_module.commands.generate import GenerateCommand
from struct_module.commands.info import InfoCommand
from struct_module.commands.validate import ValidateCommand
from struct_module.commands.list import ListCommand
from struct_module.commands.generate_schema import GenerateSchemaCommand
import argparse
import json
import os

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

def test_with_value_renders_jinja2_with_mappings():
    from struct_module.template_renderer import TemplateRenderer
    config_variables = []
    input_store = "/tmp/input.json"
    non_interactive = True
    mappings = {
        "teams": {
            "devops": "devops-team"
        }
    }
    # Simulate a 'with' dict as in the folder struct logic
    with_dict = {"team": "{{@ mappings.teams.devops @}}"}
    template_vars = {}
    renderer = TemplateRenderer(
        config_variables, input_store, non_interactive, mappings)
    rendered_with = {}
    for k, v in with_dict.items():
        context = template_vars.copy() if template_vars else {}
        context['mappings'] = mappings or {}
        rendered_with[k] = renderer.render_template(str(v), context)
    assert rendered_with["team"] == "devops-team"


# Tests for GenerateSchemaCommand
def test_generate_schema_command_init(parser):
    """Test that GenerateSchemaCommand initializes correctly with proper arguments."""
    command = GenerateSchemaCommand(parser)

    # Check that arguments were added
    actions = {action.dest: action for action in parser._actions}
    assert 'structures_path' in actions
    assert 'output' in actions

    # Check help text
    assert actions['structures_path'].help == 'Path to structure definitions'
    assert actions['output'].help == 'Output file path for the schema (default: stdout)'


def test_generate_schema_command_execute_calls_generate_schema(parser):
    """Test that execute method calls _generate_schema."""
    command = GenerateSchemaCommand(parser)
    args = MagicMock()

    with patch.object(command, '_generate_schema') as mock_generate_schema:
        command.execute(args)
        mock_generate_schema.assert_called_once_with(args)


def test_generate_schema_stdout_output(parser):
    """Test generate schema command outputs to stdout when no output file specified."""
    command = GenerateSchemaCommand(parser)
    args = MagicMock()
    args.structures_path = None
    args.output = None

    # Mock the file system to simulate contribs directory with YAML files
    mock_walk_data = [
        ('/path/to/contribs', [], ['terraform-module.yaml', 'docker-files.yaml']),
        ('/path/to/contribs/subdir', [], ['nested-struct.yaml'])
    ]

    with patch('os.path.dirname') as mock_dirname, \
            patch('os.path.realpath') as mock_realpath, \
            patch('os.path.join') as mock_join, \
            patch('os.path.exists', return_value=True), \
            patch('os.walk', return_value=mock_walk_data), \
            patch('os.path.relpath', side_effect=['terraform-module', 'docker-files', 'subdir/nested-struct']), \
            patch('builtins.print') as mock_print:

        mock_dirname.return_value = '/path/to/commands'
        mock_realpath.return_value = '/path/to/commands'
        mock_join.return_value = '/path/to/contribs'

        command._generate_schema(args)

        # Verify print was called with JSON output
        mock_print.assert_called_once()
        printed_output = mock_print.call_args[0][0]

        # Parse the JSON to verify structure
        schema = json.loads(printed_output)
        assert 'definitions' in schema
        assert 'PluginList' in schema['definitions']
        assert 'enum' in schema['definitions']['PluginList']

        # Check that structures are sorted and include expected files
        structures = schema['definitions']['PluginList']['enum']
        assert 'docker-files' in structures
        assert 'subdir/nested-struct' in structures
        assert 'terraform-module' in structures
        assert structures == sorted(structures)  # Verify sorted order


def test_generate_schema_file_output(parser):
    """Test generate schema command writes to file when output path specified."""
    command = GenerateSchemaCommand(parser)
    args = MagicMock()
    args.structures_path = None
    args.output = '/output/schema.json'

    mock_walk_data = [
        ('/path/to/contribs', [], ['test-struct.yaml'])
    ]

    mock_file = MagicMock()

    with patch('os.path.dirname') as mock_dirname, \
            patch('os.path.realpath') as mock_realpath, \
            patch('os.path.join') as mock_join, \
            patch('os.path.exists', return_value=True), \
            patch('os.walk', return_value=mock_walk_data), \
            patch('os.path.relpath', return_value='test-struct'), \
            patch('os.makedirs') as mock_makedirs, \
            patch('builtins.open', return_value=mock_file) as mock_open, \
            patch('builtins.print') as mock_print:

        mock_dirname.side_effect = ['/path/to/commands', '/output']
        mock_realpath.return_value = '/path/to/commands'
        mock_join.return_value = '/path/to/contribs'
        mock_file.__enter__.return_value = mock_file

        command._generate_schema(args)

        # Verify file operations
        mock_makedirs.assert_called_once_with('/output')
        mock_open.assert_called_once_with('/output/schema.json', 'w')
        mock_file.write.assert_called_once()

        # Verify success message
        mock_print.assert_called_once_with(
            '✅ Schema successfully generated at: /output/schema.json')

        # Verify JSON content written to file
        written_content = mock_file.write.call_args[0][0]
        schema = json.loads(written_content)
        assert 'definitions' in schema
        assert 'PluginList' in schema['definitions']
        assert 'test-struct' in schema['definitions']['PluginList']['enum']


def test_generate_schema_with_custom_structures_path(parser):
    """Test generate schema command with custom structures path."""
    command = GenerateSchemaCommand(parser)
    args = MagicMock()
    args.structures_path = '/custom/structures'
    args.output = None

    # Mock two separate walk calls for custom path and contribs
    def mock_walk_side_effect(path):
        if '/custom/structures' in path:
            return [('/custom/structures', [], ['custom-struct.yaml'])]
        else:  # contribs path
            return [('/path/to/contribs', [], ['builtin-struct.yaml'])]

    def mock_relpath_side_effect(file_path, base_path):
        if 'custom-struct' in file_path:
            return 'custom-struct'
        else:
            return 'builtin-struct'

    with patch('os.path.dirname') as mock_dirname, \
            patch('os.path.realpath') as mock_realpath, \
            patch('os.path.join') as mock_join, \
            patch('os.path.exists', return_value=True), \
            patch('os.walk', side_effect=mock_walk_side_effect), \
            patch('os.path.relpath', side_effect=mock_relpath_side_effect), \
            patch('builtins.print') as mock_print:

        mock_dirname.return_value = '/path/to/commands'
        mock_realpath.return_value = '/path/to/commands'
        mock_join.return_value = '/path/to/contribs'

        command._generate_schema(args)

        # Verify print was called
        mock_print.assert_called_once()
        printed_output = mock_print.call_args[0][0]

        # Parse and verify both custom and builtin structures are included
        schema = json.loads(printed_output)
        structures = schema['definitions']['PluginList']['enum']
        assert 'custom-struct' in structures
        assert 'builtin-struct' in structures


def test_generate_schema_no_output_directory_creation(parser):
    """Test that output directory is not created when it already exists."""
    command = GenerateSchemaCommand(parser)
    args = MagicMock()
    args.structures_path = None
    args.output = '/existing/dir/schema.json'

    mock_walk_data = [('/path/to/contribs', [], ['test.yaml'])]
    mock_file = MagicMock()

    with patch('os.path.dirname') as mock_dirname, \
            patch('os.path.realpath') as mock_realpath, \
            patch('os.path.join') as mock_join, \
            patch('os.path.exists', side_effect=lambda path: True), \
            patch('os.walk', return_value=mock_walk_data), \
            patch('os.path.relpath', return_value='test'), \
            patch('os.makedirs') as mock_makedirs, \
            patch('builtins.open', return_value=mock_file) as mock_open, \
            patch('builtins.print'):

        mock_dirname.side_effect = ['/path/to/commands', '/existing/dir']
        mock_realpath.return_value = '/path/to/commands'
        mock_join.return_value = '/path/to/contribs'
        mock_file.__enter__.return_value = mock_file

        command._generate_schema(args)

        # Verify makedirs was not called since directory exists
        mock_makedirs.assert_not_called()


def test_generate_schema_empty_directory(parser):
    """Test generate schema command with directory containing no YAML files."""
    command = GenerateSchemaCommand(parser)
    args = MagicMock()
    args.structures_path = None
    args.output = None

    # Empty directory
    mock_walk_data = [('/path/to/contribs', [], [])]

    with patch('os.path.dirname') as mock_dirname, \
            patch('os.path.realpath') as mock_realpath, \
            patch('os.path.join') as mock_join, \
            patch('os.path.exists', return_value=True), \
            patch('os.walk', return_value=mock_walk_data), \
            patch('builtins.print') as mock_print:

        mock_dirname.return_value = '/path/to/commands'
        mock_realpath.return_value = '/path/to/commands'
        mock_join.return_value = '/path/to/contribs'

        command._generate_schema(args)

        # Verify empty enum is generated
        printed_output = mock_print.call_args[0][0]
        schema = json.loads(printed_output)
        assert schema['definitions']['PluginList']['enum'] == []


def test_generate_schema_nonexistent_path(parser):
    """Test generate schema command with nonexistent path."""
    command = GenerateSchemaCommand(parser)
    args = MagicMock()
    args.structures_path = '/nonexistent/path'
    args.output = None

    # Mock contribs path with some files
    def mock_walk_side_effect(path):
        if '/nonexistent/path' in path:
            return []  # No files for nonexistent path
        else:  # contribs path
            return [('/path/to/contribs', [], ['builtin.yaml'])]

    def mock_exists_side_effect(path):
        return '/nonexistent/path' not in path

    with patch('os.path.dirname') as mock_dirname, \
            patch('os.path.realpath') as mock_realpath, \
            patch('os.path.join') as mock_join, \
            patch('os.path.exists', side_effect=mock_exists_side_effect), \
            patch('os.walk', side_effect=mock_walk_side_effect), \
            patch('os.path.relpath', return_value='builtin'), \
            patch('builtins.print') as mock_print:

        mock_dirname.return_value = '/path/to/commands'
        mock_realpath.return_value = '/path/to/commands'
        mock_join.return_value = '/path/to/contribs'

        command._generate_schema(args)

        # Should only include builtin structures, not fail
        printed_output = mock_print.call_args[0][0]
        schema = json.loads(printed_output)
        structures = schema['definitions']['PluginList']['enum']
        assert 'builtin' in structures
        assert len(structures) == 1
