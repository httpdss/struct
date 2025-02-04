# FILE: content_fetcher.py
import os
import re
import requests
import subprocess
from pathlib import Path
import hashlib
import logging

try:
  import boto3
  from botocore.exceptions import NoCredentialsError, ClientError
  boto3_available = True
except ImportError:
  boto3_available = False

try:
  from google.cloud import storage
  from google.api_core.exceptions import GoogleAPIError
  gcs_available = True
except ImportError:
  gcs_available = False

class ContentFetcher:
  def __init__(self, cache_dir=None):
    self.logger = logging.getLogger(__name__)
    self.cache_dir = Path(cache_dir or os.path.expanduser("~/.struct/cache"))
    self.cache_dir.mkdir(parents=True, exist_ok=True)

  def fetch_content(self, content_location):
    """
    Fetch content from a given location. Supported protocols:
    - Local file (file://)
    - HTTP/HTTPS (https://)
    - GitHub repository (github://owner/repo/branch/file_path)
    - GitHub HTTPS (githubhttps://owner/repo/branch/file_path)
    - GitHub SSH (githubssh://owner/repo/branch/file_path)
    - S3 bucket (s3://bucket_name/key)
    - Google Cloud Storage (gs://bucket_name/key)
    """
    protocol_map = {
      "file://": self._fetch_local_file,
      "https://": self._fetch_http_url,
      "github://": self._fetch_github_file,
      "githubhttps://": self._fetch_github_https_file,
      "githubssh://": self._fetch_github_ssh_file,
    }

    if boto3_available:
      protocol_map["s3://"] = self._fetch_s3_file
    if gcs_available:
      protocol_map["gs://"] = self._fetch_gcs_file

    for prefix, method in protocol_map.items():
      if content_location.startswith(prefix):
        if content_location.startswith("http"):
          return method(content_location)
        else:
          return method(content_location[len(prefix):])

    raise ValueError(f"Unsupported content location: {content_location}")

  def _fetch_local_file(self, file_path):
    self.logger.debug(f"Fetching content from local file: {file_path}")
    file_path = Path(file_path)
    with file_path.open('r') as file:
      return file.read()

  def _fetch_http_url(self, url):
    self.logger.debug(f"Fetching content from URL: {url}")
    # Create a hash of the URL to use as a cache key
    cache_key = hashlib.md5(url.encode()).hexdigest()
    cache_file_path = self.cache_dir / cache_key

    if cache_file_path.exists():
      self.logger.debug(f"Loading content from cache: {cache_file_path}")
      with cache_file_path.open('r') as file:
        return file.read()

    response = requests.get(url)
    response.raise_for_status()
    with cache_file_path.open('w') as file:
      file.write(response.text)

    return response.text

  def _fetch_github_file(self, github_url):
    """
    Fetch a file from a GitHub repository using HTTPS.
    Expected format: github://owner/repo/branch/file_path
    """
    self.logger.debug(f"Fetching content from GitHub: {github_url}")
    match = re.match(r"github://([^/]+)/([^/]+)/([^/]+)/(.+)", github_url)
    if not match:
      raise ValueError("Invalid GitHub URL format. Expected github://owner/repo/branch/file_path")

    owner, repo, branch, file_path = match.groups()
    return self._clone_or_fetch_github(owner, repo, branch, file_path, https=True)

  def _fetch_github_https_file(self, github_url):
    """
    Fetch a file from a GitHub repository using HTTPS.
    Expected format: githubhttps://owner/repo/branch/file_path
    """
    self.logger.debug(f"Fetching content from GitHub (HTTPS): {github_url}")
    match = re.match(r"githubhttps://([^/]+)/([^/]+)/([^/]+)/(.+)", github_url)
    if not match:
      raise ValueError("Invalid GitHub URL format. Expected githubhttps://owner/repo/branch/file_path")

    owner, repo, branch, file_path = match.groups()
    return self._clone_or_fetch_github(owner, repo, branch, file_path, https=True)

  def _fetch_github_ssh_file(self, github_url):
    """
    Fetch a file from a GitHub repository using SSH.
    Expected format: githubssh://owner/repo/branch/file_path
    """
    self.logger.debug(f"Fetching content from GitHub (SSH): {github_url}")
    match = re.match(r"githubssh://([^/]+)/([^/]+)/([^/]+)/(.+)", github_url)
    if not match:
      raise ValueError("Invalid GitHub URL format. Expected githubssh://owner/repo/branch/file_path")

    owner, repo, branch, file_path = match.groups()
    return self._clone_or_fetch_github(owner, repo, branch, file_path, https=False)

  def _clone_or_fetch_github(self, owner, repo, branch, file_path, https=True):
    repo_cache_path = self.cache_dir / f"{owner}_{repo}_{branch}"
    clone_url = f"https://github.com/{owner}/{repo}.git" if https else f"git@github.com:{owner}/{repo}.git"

    # Clone or fetch the repository
    if not repo_cache_path.exists():
      self.logger.debug(f"Cloning repository: {owner}/{repo} (branch: {branch})")
      subprocess.run(["git", "clone", "-b", branch, clone_url, str(repo_cache_path)], check=True)
    else:
      self.logger.debug(f"Repository already cloned. Pulling latest changes for: {repo_cache_path}")
      subprocess.run(["git", "-C", str(repo_cache_path), "pull"], check=True)

    # Read the requested file
    file_full_path = repo_cache_path / file_path
    if not file_full_path.exists():
      raise FileNotFoundError(f"File {file_path} not found in repository {owner}/{repo} on branch {branch}")

    with file_full_path.open('r') as file:
      return file.read()

  def _fetch_s3_file(self, s3_url):
    """
    Fetch a file from an S3 bucket.
    Expected format: s3://bucket_name/key
    """
    if not boto3_available:
      raise ImportError("boto3 is not installed. Please install it to use S3 fetching.")

    self.logger.debug(f"Fetching content from S3: {s3_url}")
    match = re.match(r"s3://([^/]+)/(.+)", s3_url)
    if not match:
      raise ValueError("Invalid S3 URL format. Expected s3://bucket_name/key")

    bucket_name, key = match.groups()
    local_file_path = self.cache_dir / Path(key).name

    try:
      session = boto3.Session()  # Create a new session
      s3_client = session.client("s3")
      s3_client.download_file(bucket_name, key, str(local_file_path))
      self.logger.debug(f"Downloaded S3 file to: {local_file_path}")
    except NoCredentialsError:
      raise RuntimeError("AWS credentials not found. Ensure that your credentials are configured properly.")
    except ClientError as e:
      error_code = e.response.get("Error", {}).get("Code")
      if error_code == "404":
        raise FileNotFoundError(f"The specified S3 key does not exist: {key}")
      else:
        raise RuntimeError(f"Failed to download S3 file: {e}")

    with local_file_path.open('r') as file:
      return file.read()

  def _fetch_gcs_file(self, gcs_url):
    """
    Fetch a file from Google Cloud Storage.
    Expected format: gs://bucket_name/key
    """
    if not gcs_available:
      raise ImportError("google-cloud-storage is not installed. Please install it to use GCS fetching.")

    self.logger.debug(f"Fetching content from GCS: {gcs_url}")
    match = re.match(r"gs://([^/]+)/(.+)", gcs_url)
    if not match:
      raise ValueError("Invalid GCS URL format. Expected gs://bucket_name/key")

    bucket_name, key = match.groups()
    local_file_path = self.cache_dir / Path(key).name

    try:
      gcs_client = storage.Client()
      bucket = gcs_client.bucket(bucket_name)
      blob = bucket.blob(key)
      blob.download_to_filename(str(local_file_path))
      self.logger.debug(f"Downloaded GCS file to: {local_file_path}")
    except GoogleAPIError as e:
      raise RuntimeError(f"Failed to download GCS file: {e}")

    with local_file_path.open('r') as file:
      return file.read()
