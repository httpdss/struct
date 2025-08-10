import hashlib
from unittest.mock import patch, MagicMock
import tempfile
from pathlib import Path
from struct_module.content_fetcher import ContentFetcher
import argparse
from struct_module.commands.cache import CacheCommand


def _mock_response(text):
    mock = MagicMock()
    mock.text = text
    mock.raise_for_status = MagicMock()
    return mock


def test_cache_policy_always():
    with tempfile.TemporaryDirectory() as tmpdir:
        fetcher = ContentFetcher(cache_dir=tmpdir, cache_policy="always")
        url = "https://example.com/data"
        with patch("requests.get", return_value=_mock_response("first")) as mock_get:
            assert fetcher.fetch_content(url) == "first"
            assert mock_get.call_count == 1
        with patch("requests.get", return_value=_mock_response("second")) as mock_get:
            assert fetcher.fetch_content(url) == "first"
            mock_get.assert_not_called()


def test_cache_policy_never(tmp_path):
    fetcher = ContentFetcher(cache_dir=tmp_path, cache_policy="never")
    url = "https://example.com/data"
    with patch("requests.get", side_effect=[_mock_response("a"), _mock_response("b")]) as mock_get:
        assert fetcher.fetch_content(url) == "a"
        assert fetcher.fetch_content(url) == "b"
        assert mock_get.call_count == 2
    cache_key = hashlib.md5(url.encode()).hexdigest()
    assert not (tmp_path / cache_key).exists()


def test_cache_policy_refresh(tmp_path):
    fetcher = ContentFetcher(cache_dir=tmp_path, cache_policy="refresh")
    url = "https://example.com/data"
    with patch("requests.get", side_effect=[_mock_response("old"), _mock_response("new")]) as mock_get:
        assert fetcher.fetch_content(url) == "old"
        assert fetcher.fetch_content(url) == "new"
        assert mock_get.call_count == 2
    cache_key = hashlib.md5(url.encode()).hexdigest()
    with open(tmp_path / cache_key, "r") as f:
        assert f.read() == "new"


def test_cache_command_clear(tmp_path, capsys):
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    (cache_dir / "file.txt").write_text("data")
    parser = argparse.ArgumentParser()
    cmd = CacheCommand(parser)
    args = parser.parse_args(["clear", "--cache-dir", str(cache_dir)])
    cmd.execute(args)
    assert not any(cache_dir.iterdir())
    captured = capsys.readouterr()
    assert "Cache cleared." in captured.out
