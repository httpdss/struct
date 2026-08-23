import pytest
from unittest.mock import patch, MagicMock, call, mock_open
from structkit.commands.generate import GenerateCommand
import argparse
import os

@pytest.fixture
def parser():
    return argparse.ArgumentParser()

def make_args(tmp_path, pre=None, post=None):
    # Create a minimal YAML config file
    config = {
        'files': [
            {'test.txt': {'content': 'hello'}}
        ]
    }
    if pre:
        config['pre_hooks'] = pre
    if post:
        config['post_hooks'] = post
    yaml_path = tmp_path / 'struct.yaml'
    import yaml as _yaml
    with open(yaml_path, 'w') as f:
        _yaml.safe_dump(config, f)
    return yaml_path

def make_allowlist(tmp_path, commands):
    """Create a hooks allowlist file."""
    allowlist_path = tmp_path / '.struct-hooks-allowlist'
    with open(allowlist_path, 'w') as f:
        for cmd in commands:
            f.write(f"{cmd}\n")
    return allowlist_path

def test_no_hooks_runs_ok(tmp_path, parser):
    yaml_path = make_args(tmp_path)
    command = GenerateCommand(parser)
    args = parser.parse_args([f'file://{yaml_path}', str(tmp_path)])
    with patch.object(command, '_create_structure') as mock_create_structure, \
         patch.object(command, '_run_hooks', wraps=command._run_hooks) as mock_run_hooks:
        command.execute(args)
        # _run_hooks should be called for pre and post, but both are no-op
        assert mock_run_hooks.call_count == 2
        mock_create_structure.assert_called_once()

def test_pre_hook_runs_and_blocks_on_failure(tmp_path, parser):
    yaml_path = make_args(tmp_path, pre=['exit 1'])
    command = GenerateCommand(parser)
    args = parser.parse_args([f'file://{yaml_path}', str(tmp_path), '--non-interactive'])
    with patch('subprocess.run', side_effect=__import__('subprocess').CalledProcessError(1, 'exit 1')) as mock_subproc, \
         patch.object(command, '_create_structure') as mock_create_structure:
        command.execute(args)
        mock_subproc.assert_called_once()
        mock_create_structure.assert_not_called()

def test_post_hook_runs_and_blocks_on_failure(tmp_path, parser):
    yaml_path = make_args(tmp_path, post=['exit 1'])
    command = GenerateCommand(parser)
    args = parser.parse_args([f'file://{yaml_path}', str(tmp_path), '--non-interactive'])
    with patch('subprocess.run', side_effect=__import__('subprocess').CalledProcessError(1, 'exit 1')) as mock_subproc, \
         patch.object(command, '_create_structure') as mock_create_structure:
        command.execute(args)
        # Only post-hook should run, so only one call
        mock_subproc.assert_called_once()
        mock_create_structure.assert_called_once()

def test_hooks_order(tmp_path, parser):
    yaml_path = make_args(tmp_path, pre=['echo pre'], post=['echo post'])
    command = GenerateCommand(parser)
    args = parser.parse_args([f'file://{yaml_path}', str(tmp_path), '--non-interactive'])
    with patch('subprocess.run') as mock_subproc, \
         patch.object(command, '_create_structure') as mock_create_structure:
        command.execute(args)
        # Should call pre first, then post
        assert mock_subproc.call_args_list[0][0][0] == 'echo pre'
        assert mock_subproc.call_args_list[1][0][0] == 'echo post'
        mock_create_structure.assert_called_once()

def test_no_hooks_flag(tmp_path, parser):
    """Test that --no-hooks skips all hooks."""
    yaml_path = make_args(tmp_path, pre=['echo pre'], post=['echo post'])
    command = GenerateCommand(parser)
    args = parser.parse_args([f'file://{yaml_path}', str(tmp_path), '--no-hooks'])
    with patch('subprocess.run') as mock_subproc, \
         patch.object(command, '_create_structure') as mock_create_structure:
        command.execute(args)
        # No hooks should run
        mock_subproc.assert_not_called()
        mock_create_structure.assert_called_once()

def test_interactive_confirmation_declined(tmp_path, parser):
    """Test that declining hook confirmation aborts generation."""
    yaml_path = make_args(tmp_path, pre=['echo pre'])
    command = GenerateCommand(parser)
    args = parser.parse_args([f'file://{yaml_path}', str(tmp_path)])
    with patch('subprocess.run') as mock_subproc, \
         patch.object(command, '_create_structure') as mock_create_structure, \
         patch('builtins.input', return_value='n'):
        command.execute(args)
        # No hooks should run
        mock_subproc.assert_not_called()
        # Structure should not be created
        mock_create_structure.assert_not_called()

def test_interactive_confirmation_accepted(tmp_path, parser):
    """Test that accepting hook confirmation runs hooks."""
    yaml_path = make_args(tmp_path, pre=['echo pre'])
    command = GenerateCommand(parser)
    args = parser.parse_args([f'file://{yaml_path}', str(tmp_path)])
    with patch('subprocess.run') as mock_subproc, \
         patch.object(command, '_create_structure') as mock_create_structure, \
         patch('builtins.input', return_value='y'):
        command.execute(args)
        # Hooks should run
        mock_subproc.assert_called_once()
        mock_create_structure.assert_called_once()

def test_non_interactive_mode(tmp_path, parser):
    """Test that --non-interactive skips confirmation."""
    yaml_path = make_args(tmp_path, pre=['echo pre'])
    command = GenerateCommand(parser)
    args = parser.parse_args([f'file://{yaml_path}', str(tmp_path), '--non-interactive'])
    with patch('subprocess.run') as mock_subproc, \
         patch.object(command, '_create_structure') as mock_create_structure, \
         patch('builtins.input') as mock_input:
        command.execute(args)
        # No prompt should appear
        mock_input.assert_not_called()
        # Hooks should run
        mock_subproc.assert_called_once()
        mock_create_structure.assert_called_once()

def test_allowlist_blocks_unlisted_command(tmp_path, parser):
    """Test that allowlist blocks commands not in the list."""
    yaml_path = make_args(tmp_path, pre=['dangerous-command'])
    make_allowlist(tmp_path, ['echo', 'git'])
    command = GenerateCommand(parser)
    args = parser.parse_args([
        f'file://{yaml_path}',
        str(tmp_path),
        '--non-interactive',
        '--hooks-allowlist', str(tmp_path / '.struct-hooks-allowlist')
    ])
    with patch('subprocess.run') as mock_subproc, \
         patch.object(command, '_create_structure') as mock_create_structure:
        command.execute(args)
        # Hook should be blocked
        mock_subproc.assert_not_called()
        # Structure should not be created
        mock_create_structure.assert_not_called()

def test_allowlist_allows_listed_command(tmp_path, parser):
    """Test that allowlist allows commands in the list."""
    yaml_path = make_args(tmp_path, pre=['echo test'])
    make_allowlist(tmp_path, ['echo', 'git'])
    command = GenerateCommand(parser)
    args = parser.parse_args([
        f'file://{yaml_path}',
        str(tmp_path),
        '--non-interactive',
        '--hooks-allowlist', str(tmp_path / '.struct-hooks-allowlist')
    ])
    with patch('subprocess.run') as mock_subproc, \
         patch.object(command, '_create_structure') as mock_create_structure:
        command.execute(args)
        # Hook should run
        mock_subproc.assert_called_once()
        mock_create_structure.assert_called_once()

def test_allowlist_exact_match(tmp_path, parser):
    """Test that allowlist supports exact command matching."""
    yaml_path = make_args(tmp_path, pre=['./scripts/prep.sh'])
    make_allowlist(tmp_path, ['./scripts/prep.sh', 'echo'])
    command = GenerateCommand(parser)
    args = parser.parse_args([
        f'file://{yaml_path}',
        str(tmp_path),
        '--non-interactive',
        '--hooks-allowlist', str(tmp_path / '.struct-hooks-allowlist')
    ])
    with patch('subprocess.run') as mock_subproc, \
         patch.object(command, '_create_structure') as mock_create_structure:
        command.execute(args)
        # Hook should run
        mock_subproc.assert_called_once()
        mock_create_structure.assert_called_once()

def test_allowlist_base_command_match(tmp_path, parser):
    """Test that allowlist matches base command (first word)."""
    yaml_path = make_args(tmp_path, pre=['git add .'])
    make_allowlist(tmp_path, ['git', 'echo'])
    command = GenerateCommand(parser)
    args = parser.parse_args([
        f'file://{yaml_path}',
        str(tmp_path),
        '--non-interactive',
        '--hooks-allowlist', str(tmp_path / '.struct-hooks-allowlist')
    ])
    with patch('subprocess.run') as mock_subproc, \
         patch.object(command, '_create_structure') as mock_create_structure:
        command.execute(args)
        # Hook should run (base command 'git' is allowed)
        mock_subproc.assert_called_once()
        mock_create_structure.assert_called_once()

def test_allowlist_with_comments(tmp_path, parser):
    """Test that allowlist ignores comments and empty lines."""
    yaml_path = make_args(tmp_path, pre=['echo test'])
    allowlist_path = tmp_path / '.struct-hooks-allowlist'
    with open(allowlist_path, 'w') as f:
        f.write("# This is a comment\n")
        f.write("\n")
        f.write("echo\n")
        f.write("# Another comment\n")
        f.write("git\n")
    command = GenerateCommand(parser)
    args = parser.parse_args([
        f'file://{yaml_path}',
        str(tmp_path),
        '--non-interactive',
        '--hooks-allowlist', str(allowlist_path)
    ])
    with patch('subprocess.run') as mock_subproc, \
         patch.object(command, '_create_structure') as mock_create_structure:
        command.execute(args)
        # Hook should run
        mock_subproc.assert_called_once()
        mock_create_structure.assert_called_once()

def test_default_allowlist_detection(tmp_path, parser):
    """Test that .struct-hooks-allowlist is auto-detected in current directory."""
    yaml_path = make_args(tmp_path, pre=['echo test'])
    allowlist_path = tmp_path / '.struct-hooks-allowlist'
    with open(allowlist_path, 'w') as f:
        f.write("echo\n")
    command = GenerateCommand(parser)
    args = parser.parse_args([
        f'file://{yaml_path}',
        str(tmp_path),
        '--non-interactive'
    ])
    # Change to tmp_path so default allowlist is found
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        with patch('subprocess.run') as mock_subproc, \
             patch.object(command, '_create_structure') as mock_create_structure:
            command.execute(args)
            # Hook should run (allowlist auto-detected)
            mock_subproc.assert_called_once()
            mock_create_structure.assert_called_once()
    finally:
        os.chdir(original_cwd)

def test_post_hooks_confirmation(tmp_path, parser):
    """Test that post-hooks also require confirmation."""
    yaml_path = make_args(tmp_path, post=['echo post'])
    command = GenerateCommand(parser)
    args = parser.parse_args([f'file://{yaml_path}', str(tmp_path)])
    with patch('subprocess.run') as mock_subproc, \
         patch.object(command, '_create_structure') as mock_create_structure, \
         patch('builtins.input', return_value='n'):
        command.execute(args)
        # Structure should be created
        mock_create_structure.assert_called_once()
        # Post-hooks should not run
        mock_subproc.assert_not_called()

def test_allowlist_blocks_post_hooks(tmp_path, parser):
    """Test that allowlist blocks post-hooks too."""
    yaml_path = make_args(tmp_path, post=['dangerous-post-command'])
    make_allowlist(tmp_path, ['echo', 'git'])
    command = GenerateCommand(parser)
    args = parser.parse_args([
        f'file://{yaml_path}',
        str(tmp_path),
        '--non-interactive',
        '--hooks-allowlist', str(tmp_path / '.struct-hooks-allowlist')
    ])
    with patch('subprocess.run') as mock_subproc, \
         patch.object(command, '_create_structure') as mock_create_structure:
        command.execute(args)
        # Structure should be created
        mock_create_structure.assert_called_once()
        # Post-hook should be blocked
        mock_subproc.assert_not_called()
