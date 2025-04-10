import os
from github import Github
import argparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_repositories_with_topic(org_name, topic):
    """Fetch all repositories in an organization with a specific topic."""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise EnvironmentError("GITHUB_TOKEN environment variable is not set.")

    github = Github(token)
    org = github.get_organization(org_name)
    repos_with_topic = []

    for repo in org.get_repos():
        if topic in repo.get_topics():
            repos_with_topic.append(repo)

    return repos_with_topic

def trigger_workflow(repo):
    """Trigger the 'run-struct.yaml' workflow for a given repository."""
    workflows = repo.get_workflows()
    for workflow in workflows:
        if workflow.path.endswith("run-struct.yaml"):
            workflow.create_dispatch(ref=repo.default_branch)
            logging.info(f"Triggered workflow for repository: {repo.full_name}")
            return

    logging.warning(f"No 'run-struct.yaml' workflow found in repository: {repo.full_name}")

def main():
    parser = argparse.ArgumentParser(description="Trigger 'run-struct.yaml' workflow for repositories with a specific topic.")
    parser.add_argument("--org", required=True, help="The GitHub organization name.")
    parser.add_argument("--topic", required=True, help="The topic to filter repositories by.")

    args = parser.parse_args()

    org_name = args.org
    topic = args.topic

    try:
        repos = get_repositories_with_topic(org_name, topic)
        logging.info(f"Found {len(repos)} repositories with topic '{topic}'.")

        for repo in repos:
            trigger_workflow(repo)

    except Exception as e:
        logging.error(f"Error: {e}")

if __name__ == "__main__":
    main()
