#!/usr/bin/env python3
import os
import sys
import argparse
from github import Github, GithubException

def main():
    parser = argparse.ArgumentParser(
        description="Trigger the 'run-struct' workflow for all private repos in an organization that have a .struct.yaml file and the specified topic."
    )
    parser.add_argument("org", help="Name of the GitHub organization")
    parser.add_argument("topic", help="Repository topic to filter by (e.g., 'struct-enabled')")
    args = parser.parse_args()

    # Ensure that the GitHub token is set in the environment
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        sys.exit("Error: Please set the GITHUB_TOKEN environment variable.")

    # Connect to GitHub
    g = Github(token)

    try:
        org = g.get_organization(args.org)
    except GithubException as e:
        sys.exit(f"Error getting organization '{args.org}': {e}")

    # Iterate over all repositories in the organization
    for repo in org.get_repos():
        # Filter for private repositories only
        if not repo.private:
            continue

        # Check if the repository has the specified topic
        try:
            topics = repo.get_topics()
        except GithubException as e:
            print(f"Could not retrieve topics for repo {repo.full_name}: {e}")
            continue

        if args.topic not in topics:
            continue

        print(f"\nProcessing repository: {repo.full_name}")

        # Check for the existence of .struct.yaml file (in the repo's default branch)
        try:
            _ = repo.get_contents(".struct.yaml", ref=repo.default_branch)
        except GithubException as e:
            if e.status == 404:
                print("  .struct.yaml file not found. Skipping.")
            else:
                print(f"  Error retrieving .struct.yaml: {e}")
            continue

        print("  Found .struct.yaml file.")

        # Check if the workflow file exists at .github/workflows/run-struct.yaml
        try:
            _ = repo.get_contents(".github/workflows/run-struct.yaml", ref=repo.default_branch)
        except GithubException as e:
            if e.status == 404:
                print("  Workflow file .github/workflows/run-struct.yaml not found. Skipping workflow trigger.")
            else:
                print(f"  Error retrieving workflow file: {e}")
            continue

        print("  Found workflow file .github/workflows/run-struct.yaml.")

        # Retrieve the workflow object (using the file name as identifier)
        try:
            workflow = repo.get_workflow("run-struct.yaml")
        except GithubException as e:
            print(f"  Error retrieving workflow object: {e}")
            continue

        # Trigger a workflow dispatch event on the default branch
        try:
            workflow.create_dispatch(ref=repo.default_branch)
            print("  Triggered run-struct workflow successfully.")
        except GithubException as e:
            print(f"  Error triggering workflow: {e}")

if __name__ == "__main__":
    main()
