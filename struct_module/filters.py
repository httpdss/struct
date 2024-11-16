import os
import re
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

def get_default_branch(repo_name):
    token = os.getenv('GITHUB_TOKEN')

    if token:
        g = Github(token)
    else:
        g = Github()

    try:
        repo = g.get_repo(repo_name)
        return repo.default_branch
    except Exception:
        return "DEFAULT_BRANCH_ERROR"

def slugify(value):
    # Convert to lowercase
    value = value.lower()
    # Replace spaces with hyphens
    value = re.sub(r'\s+', '-', value)
    # Remove any non-alphanumeric characters (except hyphens)
    value = re.sub(r'[^a-z0-9-]', '', value)
    return value
