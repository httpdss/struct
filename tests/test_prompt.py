import pytest
import os
import tempfile
import requests
import logging
from unittest.mock import patch, MagicMock
from struct_module.main import FileItem, validate_configuration, create_structure

# Mock the OpenAI API response
@patch('struct_module.openai.Completion.create')
def test_process_prompt(mock_openai_create):
    mock_openai_create.return_value = MagicMock(choices=[MagicMock(text='Generated content from prompt')])

    file_item = FileItem({"name": "generated_file.txt", "prompt": "Write a short story about a dragon."})
    file_item.process_prompt()

    assert file_item.content == 'Generated content from prompt'
    mock_openai_create.assert_called_once_with(
        engine="davinci",
        prompt="Write a short story about a dragon.",
        max_tokens=100
    )

# Test for validate_configuration with prompt
def test_validate_configuration_with_prompt():
    valid_structure = [
        {
            "story.txt": {
                "prompt": "Write a short story about a dragon."
            }
        }
    ]
    invalid_structure = [
        {
            "story.txt": {
                "prompt": 12345  # Invalid type
            }
        }
    ]

    validate_configuration(valid_structure)

    with pytest.raises(ValueError):
        validate_configuration(invalid_structure)

# Test for creating a file with prompt content
@patch('struct_module.openai.Completion.create')
def test_create_structure_with_prompt(mock_openai_create):
    mock_openai_create.return_value = MagicMock(choices=[MagicMock(text='Generated content from prompt')])

    structure = [
        {
            "story.txt": {
                "prompt": "Write a short story about a dragon."
            }
        }
    ]

    with tempfile.TemporaryDirectory() as tmpdirname:
        create_structure(tmpdirname, structure)

        story_path = os.path.join(tmpdirname, "story.txt")
        assert os.path.exists(story_path)
        with open(story_path, 'r') as f:
            assert f.read() == 'Generated content from prompt'

# Test for dry run with prompt
@patch('struct_module.openai.Completion.create')
def test_dry_run_with_prompt(mock_openai_create, caplog):
    mock_openai_create.return_value = MagicMock(choices=[MagicMock(text='Generated content from prompt')])

    structure = [
        {
            "story.txt": {
                "prompt": "Write a short story about a dragon."
            }
        }
    ]

    with tempfile.TemporaryDirectory() as tmpdirname:
        with caplog.at_level(logging.INFO):
            create_structure(tmpdirname, structure, dry_run=True)

        assert not os.path.exists(os.path.join(tmpdirname, "story.txt"))
        assert any("[DRY RUN] Would create file:" in message for message in caplog.messages)
        assert any("Generated content from prompt" in message for message in caplog.messages)

# Mocking requests.get for testing fetch_remote_content within create_structure with prompt
@patch('struct_module.requests.get')
@patch('struct_module.openai.Completion.create')
def test_create_structure_with_remote_content_and_prompt(mock_openai_create, mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = "Remote content"
    mock_openai_create.return_value = MagicMock(choices=[MagicMock(text='Generated content from prompt')])

    structure = [
        {
            "LICENSE": {
                "file": "https://example.com/mock"
            }
        },
        {
            "story.txt": {
                "prompt": "Write a short story about a dragon."
            }
        }
    ]

    with tempfile.TemporaryDirectory() as tmpdirname:
        create_structure(tmpdirname, structure)

        license_path = os.path.join(tmpdirname, "LICENSE")
        story_path = os.path.join(tmpdirname, "story.txt")

        assert os.path.exists(license_path)
        assert os.path.exists(story_path)

        with open(license_path, 'r') as f:
            assert f.read() == "Remote content"

        with open(story_path, 'r') as f:
            assert f.read() == 'Generated content from prompt'
