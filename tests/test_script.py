import pytest
import logging
import os
import tempfile
import shutil
import requests
import time
from unittest.mock import patch, MagicMock

from struct_module.main import FileItem, validate_configuration, create_structure

# Test for FileItem.fetch_content
@patch('struct_module.requests.get')
def test_fetch_remote_content(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = "Mocked content"

    file_item = FileItem(name="LICENSE", remote_location="https://example.com/mock")
    file_item.fetch_content()

    assert file_item.content == "Mocked content"
    mock_get.assert_called_once_with("https://example.com/mock")

# Test for FileItem.apply_template_variables
def test_apply_template_variables():
    file_item = FileItem(name="README.md", content="Hello, ${name}!")
    template_vars = {"name": "World"}

    file_item.apply_template_variables(template_vars)

    assert file_item.content == "Hello, World!"

# Test for validate_configuration
def test_validate_configuration():
    valid_structure = [
        {
            "README.md": {
                "content": "This is a README file."
            }
        }
    ]
    invalid_structure = [
        {
            "README.md": {
                "invalid_key": "This should cause validation to fail."
            }
        }
    ]

    validate_configuration(valid_structure)

    with pytest.raises(ValueError):
        validate_configuration(invalid_structure)

# Test for FileItem.create with different strategies
def test_create_file():
    structure = [
        {
            "README.md": {
                "content": "This is a README file."
            }
        },
        {
            "script.sh": {
                "permissions": '0777',
                "content": "#!/bin/bash\necho 'Hello, World!'"
            }
        }
    ]

    with tempfile.TemporaryDirectory() as tmpdirname:
        create_structure(tmpdirname, structure)

        # Check if README.md was created with correct content
        readme_path = os.path.join(tmpdirname, "README.md")
        assert os.path.exists(readme_path)
        with open(readme_path, 'r') as f:
            assert f.read() == "This is a README file."

        # Check if script.sh was created with correct content and permissions
        script_path = os.path.join(tmpdirname, "script.sh")
        assert os.path.exists(script_path)
        with open(script_path, 'r') as f:
            assert f.read() == "#!/bin/bash\necho 'Hello, World!'"
        assert oct(os.stat(script_path).st_mode)[-3:] == '777'

# # Test for dry run
def test_dry_run(caplog):
    structure = [
        {
            "README.md": {
                "content": "This is a README file."
            }
        }
    ]

    with tempfile.TemporaryDirectory() as tmpdirname:
        with caplog.at_level(logging.INFO):
            create_structure(tmpdirname, structure, dry_run=True)

        assert not os.path.exists(os.path.join(tmpdirname, "README.md"))
        assert any("[DRY RUN] Would create file:" in message for message in caplog.messages)

# Mocking requests.get for testing fetch_remote_content within create_structure
@patch('struct_module.requests.get')
def test_create_structure_with_remote_content(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = "Remote content"

    structure = [
        {
            "LICENSE": {
                "file": "https://example.com/mock"
            }
        }
    ]

    with tempfile.TemporaryDirectory() as tmpdirname:
        create_structure(tmpdirname, structure)

        license_path = os.path.join(tmpdirname, "LICENSE")
        assert os.path.exists(license_path)
        with open(license_path, 'r') as f:
            assert f.read() == "Remote content"

# Test for backup strategy
def test_backup_strategy():
    structure = [
        {
            "README.md": {
                "content": "This is a README file."
            }
        }
    ]

    with tempfile.TemporaryDirectory() as tmpdirname:
        readme_path = os.path.join(tmpdirname, "README.md")
        with open(readme_path, 'w') as f:
            f.write("Existing content")

        backup_path = os.path.join(tmpdirname, "backup")
        os.makedirs(backup_path)

        create_structure(tmpdirname, structure, backup_path=backup_path, file_strategy='backup')

        assert os.path.exists(os.path.join(backup_path, "README.md"))
        with open(readme_path, 'r') as f:
            assert f.read() == "This is a README file."

# Test for skip strategy
def test_skip_strategy():
    structure = [
        {
            "README.md": {
                "content": "This is a README file."
            }
        }
    ]

    with tempfile.TemporaryDirectory() as tmpdirname:
        readme_path = os.path.join(tmpdirname, "README.md")
        with open(readme_path, 'w') as f:
            f.write("Existing content")

        create_structure(tmpdirname, structure, file_strategy='skip')

        with open(readme_path, 'r') as f:
            assert f.read() == "Existing content"

# Test for append strategy
def test_append_strategy():
    structure = [
        {
            "README.md": {
                "content": " Appended content."
            }
        }
    ]

    with tempfile.TemporaryDirectory() as tmpdirname:
        readme_path = os.path.join(tmpdirname, "README.md")
        with open(readme_path, 'w') as f:
            f.write("Existing content.")

        create_structure(tmpdirname, structure, file_strategy='append')

        with open(readme_path, 'r') as f:
            assert f.read() == "Existing content. Appended content."

# Test for rename strategy
def test_rename_strategy():
    structure = [
        {
            "README.md": {
                "content": "This is a new README file."
            }
        }
    ]

    with tempfile.TemporaryDirectory() as tmpdirname:
        readme_path = os.path.join(tmpdirname, "README.md")
        with open(readme_path, 'w') as f:
            f.write("Existing content")

        create_structure(tmpdirname, structure, file_strategy='rename')

        new_name = f"{readme_path}.{int(time.time())}"
        assert os.path.exists(new_name)
        with open(readme_path, 'r') as f:
            assert f.read() == "This is a new README file."

