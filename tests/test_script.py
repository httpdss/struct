import pytest
import os
import tempfile
import shutil
import requests
import sys
from unittest.mock import patch
from script import fetch_remote_content, apply_template_variables, validate_configuration, create_structure

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Test for fetch_remote_content
def test_fetch_remote_content():
    url = "https://raw.githubusercontent.com/nishanths/license/master/LICENSE"
    content = fetch_remote_content(url)
    assert "MIT License" in content

# Test for apply_template_variables
def test_apply_template_variables():
    content = "Hello, ${name}!"
    template_vars = {"name": "World"}
    result = apply_template_variables(content, template_vars)
    assert result == "Hello, World!"

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

# Test for create_structure
def test_create_structure():
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

# Mocking requests.get for testing fetch_remote_content
@patch('script.requests.get')
def test_fetch_remote_content_mock(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = "Mocked content"

    url = "https://example.com/mock"
    content = fetch_remote_content(url)
    assert content == "Mocked content"
