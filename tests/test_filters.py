from unittest.mock import patch, MagicMock
from struct_module.filters import get_latest_release, stringify

@patch('struct_module.filters.Github')
@patch('struct_module.filters.os.getenv')
def test_get_latest_release(mock_getenv, mock_github):
    # Mock the environment variable
    mock_getenv.return_value = 'fake_token'

    # Mock the Github object and its methods
    mock_repo = MagicMock()
    mock_repo.get_latest_release.return_value.tag_name = 'v1.0.0'
    mock_repo.default_branch = 'main'

    mock_github.return_value.get_repo.return_value = mock_repo

    # Test with a valid release
    assert get_latest_release('fake/repo') == 'v1.0.0'

    # Test with an exception in get_latest_release
    mock_repo.get_latest_release.side_effect = Exception()
    assert get_latest_release('fake/repo') == 'main'

    # Test with an exception in default_branch
    mock_repo.default_branch = None
    mock_repo.get_latest_release.side_effect = Exception()
    mock_repo.default_branch.side_effect = Exception()
    assert get_latest_release('fake/repo') == 'LATEST_RELEASE_ERROR'

def test_stringify():
    assert stringify('Hello World') == 'hello-world'
    assert stringify('Python 3.8') == 'python-3-8'
    assert stringify('Special_Characters!@#') == 'special_characters'
