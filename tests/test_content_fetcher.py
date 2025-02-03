import pytest
from unittest.mock import patch, MagicMock
from struct_module.content_fetcher import ContentFetcher

@pytest.fixture
def fetcher():
    return ContentFetcher()

def test_fetch_local_file(fetcher):
    with patch('builtins.open', patch.mock_open(read_data="file content")):
        content = fetcher._fetch_local_file('file://test.txt')
        assert content == "file content"

def test_fetch_http_url(fetcher):
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = "http content"
        content = fetcher._fetch_http_url('https://example.com')
        assert content == "http content"

def test_fetch_github_file(fetcher):
    with patch('subprocess.run') as mock_run:
        with patch('builtins.open', patch.mock_open(read_data="github content")):
            content = fetcher._fetch_github_file('github://owner/repo/branch/file.txt')
            assert content == "github content"

def test_fetch_s3_file(fetcher):
    with patch('boto3.Session') as mock_session:
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client
        mock_client.download_file = MagicMock()
        with patch('builtins.open', patch.mock_open(read_data="s3 content")):
            content = fetcher._fetch_s3_file('s3://bucket/key')
            assert content == "s3 content"

def test_fetch_gcs_file(fetcher):
    with patch('google.cloud.storage.Client') as mock_client:
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_blob.download_to_filename = MagicMock()
        with patch('builtins.open', patch.mock_open(read_data="gcs content")):
            content = fetcher._fetch_gcs_file('gs://bucket/key')
            assert content == "gcs content"
