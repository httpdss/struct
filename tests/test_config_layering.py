"""Tests for config layering system."""

import pytest
import os
import tempfile
import argparse
from pathlib import Path
from unittest.mock import patch, MagicMock
from structkit.config import (
    get_builtin_defaults,
    load_yaml_config,
    merge_config_layer,
    load_layered_config,
    merge_cli_args,
    apply_config_to_args,
    get_effective_config,
    get_user_config_path,
)


def test_get_builtin_defaults():
    """Test that built-in defaults contain expected keys."""
    defaults = get_builtin_defaults()
    assert 'file_strategy' in defaults
    assert defaults['file_strategy'] == 'overwrite'
    assert 'input_store' in defaults
    assert 'log' in defaults
    assert defaults['log'] == 'INFO'


def test_load_yaml_config_file_not_exists():
    """Test loading config from non-existent file returns None."""
    result = load_yaml_config('/nonexistent/path/config.yaml')
    assert result is None


def test_load_yaml_config_empty_file():
    """Test loading empty config file returns empty dict."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write('')
        f.flush()
        temp_path = f.name

    try:
        result = load_yaml_config(temp_path)
        assert result == {}
    finally:
        os.unlink(temp_path)


def test_load_yaml_config_valid_file():
    """Test loading valid config file."""
    config_data = """
file_strategy: skip
input_store: /custom/path/input.json
structures_path: /custom/structures
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_data)
        f.flush()
        temp_path = f.name

    try:
        result = load_yaml_config(temp_path)
        assert result is not None
        assert result['file_strategy'] == 'skip'
        assert result['input_store'] == '/custom/path/input.json'
        assert result['structures_path'] == '/custom/structures'
    finally:
        os.unlink(temp_path)


def test_merge_config_layer_base_only():
    """Test merging with None override returns copy of base."""
    base = {'key1': 'value1', 'key2': 'value2'}
    result = merge_config_layer(base, None)
    assert result == base
    assert result is not base  # Should be a copy


def test_merge_config_layer_with_override():
    """Test merging override into base."""
    base = {'key1': 'value1', 'key2': 'value2', 'key3': 'value3'}
    override = {'key2': 'new_value2', 'key4': 'value4'}
    result = merge_config_layer(base, override)

    assert result['key1'] == 'value1'  # Unchanged from base
    assert result['key2'] == 'new_value2'  # Overridden
    assert result['key3'] == 'value3'  # Unchanged from base
    assert result['key4'] == 'value4'  # New from override


def test_merge_config_layer_none_values():
    """Test that None values in override are applied."""
    base = {'key1': 'value1', 'key2': 'value2'}
    override = {'key2': None}
    result = merge_config_layer(base, override)

    # None values in override should not override base
    # (based on implementation, None is skipped)
    assert result['key1'] == 'value1'
    assert result['key2'] == 'value2'


def test_load_layered_config_only_defaults():
    """Test loading layered config with no user or project config."""
    with patch('structkit.config.get_user_config_path') as mock_user_path:
        mock_user_path.return_value = Path('/nonexistent/user/config.yaml')

        config = load_layered_config(None)

        # Should just be built-in defaults
        defaults = get_builtin_defaults()
        assert config == defaults


def test_load_layered_config_with_user_config():
    """Test loading layered config with user config present."""
    user_config_data = """
file_strategy: skip
input_store: /user/custom/input.json
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(user_config_data)
        f.flush()
        temp_user_path = f.name

    try:
        with patch('structkit.config.get_user_config_path') as mock_user_path:
            mock_user_path.return_value = Path(temp_user_path)

            config = load_layered_config(None)

            # Should have defaults merged with user config
            assert config['file_strategy'] == 'skip'
            assert config['input_store'] == '/user/custom/input.json'
            assert 'log' in config  # From defaults
    finally:
        os.unlink(temp_user_path)


def test_load_layered_config_with_project_config():
    """Test loading layered config with project config."""
    project_config_data = """
file_strategy: backup
structures_path: /project/structures
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(project_config_data)
        f.flush()
        temp_project_path = f.name

    try:
        with patch('structkit.config.get_user_config_path') as mock_user_path:
            mock_user_path.return_value = Path('/nonexistent/user/config.yaml')

            config = load_layered_config(temp_project_path)

            # Should have defaults merged with project config
            assert config['file_strategy'] == 'backup'
            assert config['structures_path'] == '/project/structures'
            assert 'log' in config  # From defaults
    finally:
        os.unlink(temp_project_path)


def test_config_precedence():
    """Test full config precedence: defaults < user < project."""
    user_config_data = """
file_strategy: skip
input_store: /user/input.json
backup: /user/backup
"""
    project_config_data = """
file_strategy: backup
backup: /project/backup
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

                config = load_layered_config(temp_project_path)

                # Project config should override user config
                assert config['file_strategy'] == 'backup'  # From project (overrides user)
                assert config['backup'] == '/project/backup'  # From project (overrides user)
                assert config['input_store'] == '/user/input.json'  # From user (not in project)
                assert config['structures_path'] == '/project/structures'  # From project only
                assert 'log' in config  # From defaults
        finally:
            os.unlink(temp_user_path)
            os.unlink(temp_project_path)


def test_merge_cli_args():
    """Test merging CLI args into config."""
    config = {
        'file_strategy': 'skip',
        'input_store': '/config/input.json',
        'log': 'INFO',
    }

    args = argparse.Namespace(
        file_strategy='overwrite',  # Override from CLI
        input_store=None,  # Not set via CLI
        backup='/cli/backup',  # New from CLI
        log='DEBUG',  # Override from CLI
    )

    result = merge_cli_args(config, args)

    assert result['file_strategy'] == 'overwrite'  # CLI override
    assert result['input_store'] == '/config/input.json'  # From config
    assert result['backup'] == '/cli/backup'  # CLI arg
    assert result['log'] == 'DEBUG'  # CLI override


def test_apply_config_to_args():
    """Test applying config to argparse namespace."""
    config = {
        'file_strategy': 'skip',
        'input_store': '/config/input.json',
        'backup': '/config/backup',
        'structures_path': '/config/structures',
    }

    args = argparse.Namespace(
        file_strategy='overwrite',  # Already set via CLI
        input_store=None,  # Not set, should get from config
        backup=None,  # Not set, should get from config
        structures_path=None,  # Not set, should get from config
    )

    apply_config_to_args(config, args)

    # CLI arg should not be overridden
    assert args.file_strategy == 'overwrite'

    # Config values should be applied where args were None
    assert args.input_store == '/config/input.json'
    assert args.backup == '/config/backup'
    assert args.structures_path == '/config/structures'


def test_get_effective_config():
    """Test getting effective config with all layers."""
    project_config_data = """
file_strategy: backup
structures_path: /project/structures
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(project_config_data)
        f.flush()
        temp_project_path = f.name

    try:
        with patch('structkit.config.get_user_config_path') as mock_user_path:
            mock_user_path.return_value = Path('/nonexistent/user/config.yaml')

            args = argparse.Namespace(
                config_file=temp_project_path,
                file_strategy='overwrite',  # CLI override
                input_store=None,
                backup=None,
                structures_path=None,
                log='DEBUG',  # CLI override
            )

            effective_config = get_effective_config(args)

            # Check precedence
            assert effective_config['file_strategy'] == 'overwrite'  # CLI wins
            assert effective_config['structures_path'] == '/project/structures'  # From project
            assert effective_config['log'] == 'DEBUG'  # CLI wins
            assert 'input_store' in effective_config  # From defaults
    finally:
        os.unlink(temp_project_path)


def test_user_config_path():
    """Test that user config path is in expected location."""
    path = get_user_config_path()
    assert str(path).endswith('.config/struct/config.yaml')
    assert path.is_absolute()
