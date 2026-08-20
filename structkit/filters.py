import os
import re
import json
from uuid import uuid4
from datetime import datetime, timezone
from typing import Any

import yaml
from github import Github
from cachetools import TTLCache, cached

cache = TTLCache(maxsize=100, ttl=600)


def _is_git_object_id(value):
    return (
        isinstance(value, str)
        and re.fullmatch(r"(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})", value) is not None
    )


def _resolve_commit_sha(repo, git_object, peel_tags=True, max_depth=10):
    """Resolve a GitHub Git object to its commit object ID."""
    seen = set()

    for _ in range(max_depth):
        object_type = getattr(git_object, "type", None)
        sha = getattr(git_object, "sha", None)
        if not isinstance(object_type, str) or not _is_git_object_id(sha):
            raise ValueError("Malformed Git object")

        if object_type == "commit":
            return sha
        if object_type != "tag" or not peel_tags or sha in seen:
            raise ValueError("Git object does not resolve to a commit")

        seen.add(sha)
        git_tag = repo.get_git_tag(sha)
        git_object = getattr(git_tag, "object", None)

    raise ValueError("Annotated tag nesting limit exceeded")


def _resolve_tag_sha(repo, tag_name):
    if not isinstance(tag_name, str) or not tag_name:
        raise ValueError("Malformed release tag name")
    git_ref = repo.get_git_ref(f"tags/{tag_name}")
    return _resolve_commit_sha(repo, getattr(git_ref, "object", None))


def _resolve_branch_sha(repo, branch_name):
    if not isinstance(branch_name, str) or not branch_name:
        raise ValueError("Malformed default branch name")
    git_ref = repo.get_git_ref(f"heads/{branch_name}")
    return _resolve_commit_sha(repo, getattr(git_ref, "object", None), peel_tags=False)


@cached(cache)
def get_latest_release(repo_name, strip_v=False, return_sha=False):
    token = os.getenv("GITHUB_TOKEN")

    # Use the token if available, otherwise proceed without authentication
    if token:
        g = Github(token)
    else:
        g = Github()

    repo = None
    try:
        # Get the repository object
        repo = g.get_repo(repo_name)
        # Get the latest release
        latest_release = repo.get_latest_release()
    except Exception:
        # If an error occurs, return the default branch name
        try:
            if repo is None:
                raise ValueError("Repository lookup failed")
            default_branch = repo.default_branch
            if return_sha:
                return _resolve_branch_sha(repo, default_branch)
            return default_branch
        except Exception as e:
            print(f"Error getting default branch: {e}")
            return "LATEST_RELEASE_ERROR"

    try:
        tag_name = getattr(latest_release, "tag_name", None)
    except Exception:
        return "LATEST_RELEASE_ERROR"
    if not isinstance(tag_name, str) or not tag_name:
        return "LATEST_RELEASE_ERROR"

    if return_sha:
        try:
            return _resolve_tag_sha(repo, tag_name)
        except Exception:
            return "LATEST_RELEASE_ERROR"

    if strip_v and tag_name.startswith("v"):
        return tag_name[1:]
    return tag_name


@cached(cache)
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

# -----------------------------
# Additional helpers/filters
# -----------------------------


def gen_uuid() -> str:
    return str(uuid4())


def now_iso() -> str:
    # UTC ISO8601 string
    return datetime.now(timezone.utc).isoformat()


def env(name: str, default: str = "") -> str:
    return os.getenv(name, default)


def read_file(path: str, encoding: str = "utf-8") -> str:
    try:
        with open(path, "r", encoding=encoding) as f:
            return f.read()
    except Exception:
        return ""


def to_yaml(obj: Any) -> str:
    try:
        return yaml.safe_dump(obj, sort_keys=False)
    except Exception:
        return ""


def from_yaml(s: str) -> Any:
    try:
        return yaml.safe_load(s)
    except Exception:
        return None


def to_json(obj: Any, indent: int | None = None) -> str:
    try:
        return json.dumps(obj, indent=indent)
    except Exception:
        return ""


def from_json(s: str) -> Any:
    try:
        return json.loads(s)
    except Exception:
        return None
