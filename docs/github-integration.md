# GitHub Integration

STRUCT can seamlessly integrate with GitHub to automate the generation of project structures across repositories. This documentation explains how to set up and use the GitHub trigger script.

## GitHub Trigger Script

The `github-trigger.py` script is a utility designed to trigger the `run-struct` workflow for all private repositories in a GitHub organization that meet specific criteria. This script is particularly useful for automating tasks across multiple repositories.

### Features

- Filters repositories by a specific topic (e.g., `struct-enabled`).
- Checks for the existence of a `.struct.yaml` file in the repository's default branch.
- Verifies the presence of the `run-struct` workflow file in `.github/workflows/`.
- Triggers the workflow dispatch event for eligible repositories.

### Usage

To use the script, ensure you have the following prerequisites:

1. A valid GitHub Personal Access Token with the necessary permissions (set as the `GITHUB_TOKEN` environment variable).
2. The `PyGithub` library installed (`pip install PyGithub`).

Run the script with the following command:

```sh
python3 scripts/github-trigger.py <organization> <topic>
```

#### Arguments

- `<organization>`: The name of the GitHub organization.
- `<topic>`: The topic to filter repositories by (e.g., `struct-enabled`).

#### Example

```sh
export GITHUB_TOKEN=your_personal_access_token
python3 scripts/github-trigger.py my-org struct-enabled
```

### How It Works

1. The script connects to the GitHub API using the provided token.
2. It iterates through all private repositories in the specified organization.
3. For each repository:
   - Checks if the repository has the specified topic.
   - Verifies the existence of a `.struct.yaml` file in the default branch.
   - Confirms the presence of the `run-struct` workflow file.
   - Triggers the workflow dispatch event if all conditions are met.

### Notes

- Ensure the `GITHUB_TOKEN` environment variable is set before running the script.
- The token must have sufficient permissions to access private repositories and trigger workflows.
- Errors during execution (e.g., missing files or insufficient permissions) will be logged to the console.

### Advanced Usage

Add additional parameters to customize the script's behavior:

- `--dry-run`: Simulate the script actions without executing any API calls.
- `--verbose`: Enable verbose output for debugging purposes.

Example:

```sh
python3 scripts/github-trigger.py my-org struct-enabled --dry-run --verbose
```

### Troubleshooting

- **Unauthorized Error**: Make sure your token has the appropriate permissions.
- **Repository Not Found**: Ensure the organization name is correct and the token has access.
- **Missing Files**: Verify that the `.struct.yaml` and workflow files exist in each repository.

## Automating STRUCT

Combine GitHub Actions with STRUCT to automate project structure generation in CI/CD pipelines. Trigger the process manually or automatically based on events like pull requests or pushes.

Example Workflow:

```yaml
name: run-struct

on:
  workflow_dispatch:

jobs:
  generate:
    uses: httpdss/struct/.github/workflows/struct-generate.yaml@main
    secrets:
      token: ${{ secrets.STRUCT_RUN_TOKEN }}
```

## Best Practices

1. **Secure Your Token**: Store GitHub tokens in secrets management tools.
2. **Use Topics for Filtering**: Organize repositories with topics to efficiently manage workflows.
3. **Test Locally First**: Simulate script actions with `--dry-run` before executing in a CI/CD environment.
4. **Combine with Other Tools**: Use STRUCT with Terraform, Ansible, or Docker for comprehensive project management.

## FAQs

### Why use a GitHub Integration?

Using GitHub integration allows you to leverage STRUCT's automation capabilities in a version-controlled environment, enabling consistent and repeatable project structures.

### Can I customize the GitHub Action?

Yes, you can tailor the GitHub Action to your specific needs, including custom triggers, different environments, and additional dependencies.
