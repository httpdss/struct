import pytest
from unittest.mock import patch, MagicMock
from struct_module.file_item import FileItem

@pytest.fixture
def file_item():
    properties = {
        "name": "test.txt",
        "content": "file content",
        "config_variables": [],
        "input_store": "/tmp/input.json"
    }
    return FileItem(properties)

def test_file_creation(file_item):
    with patch('builtins.open', patch.mock_open()) as mock_file:
        file_item.create("/tmp", dry_run=True)
        mock_file.assert_called_once_with("/tmp/test.txt", 'w')

def test_apply_template_variables(file_item):
    template_vars = {"var1": "value1"}
    file_item.apply_template_variables(template_vars)
    assert file_item.content == "file content"

def test_fetch_content(file_item):
    with patch('struct_module.content_fetcher.ContentFetcher.fetch_content') as mock_fetch:
        mock_fetch.return_value = "fetched content"
        file_item.fetch_content()
        assert file_item.content == "fetched content"
