import os
import subprocess
from unittest.mock import patch, MagicMock
from struct_module.utils import read_config_file, merge_configs, get_current_repo

def test_read_config_file(tmp_path):
    config_content = """
    key1: value1
    key2: value2
    """
    config_file = tmp_path / "config.yaml"
    config_file.write_text(config_content)

    result = read_config_file(config_file)
    assert result == {"key1": "value1", "key2": "value2"}

def test_merge_configs():
    file_config = {"key1": "value1", "key2": "value2"}
    args = MagicMock()
    args.key1 = None
    args.key2 = "existing_value"
    args.key3 = "value3"

    result = merge_configs(file_config, args)
    assert result == {"key1": "value1", "key2": "existing_value", "key3": "value3"}

@patch('subprocess.check_output')
def test_get_current_repo_https(mock_check_output):
    mock_check_output.return_value = b"https://github.com/owner/repo.git"
    result = get_current_repo()
    assert result == "owner/repo"

@patch('subprocess.check_output')
def test_get_current_repo_ssh(mock_check_output):
    mock_check_output.return_value = b"git@github.com:owner/repo.git"
    result = get_current_repo()
    assert result == "owner/repo"

@patch('subprocess.check_output')
def test_get_current_repo_error(mock_check_output):
    mock_check_output.side_effect = subprocess.CalledProcessError(1, 'git')
    result = get_current_repo()
    assert result == "Error: Not a Git repository or no remote URL set"
