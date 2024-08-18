import os
from github import Github

def get_latest_release(repo_name):
    token = os.getenv('GITHUB_TOKEN')

    # Use the token if available, otherwise proceed without authentication
    if token:
        g = Github(token)
    else:
        g = Github()

    try:
        # Get the repository object
        repo = g.get_repo(repo_name)
        # Get the latest release
        latest_release = repo.get_latest_release()
        return latest_release.tag_name
    except Exception:
        # If an error occurs, return the default branch name
        try:
            default_branch = repo.default_branch
            return default_branch
        except Exception as e:
            return "LATEST_RELEASE_ERROR"
