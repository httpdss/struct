# GitHub Trigger Script

The `github-trigger.py` utility triggers the `run-struct` workflow for every private repository in a GitHub organisation that matches certain criteria.

## Features

- Filter repositories by topic (for example `struct-enabled`).
- Check for the presence of a `.struct.yaml` file in the default branch.
- Ensure the `run-struct` workflow file exists.
- Dispatch the workflow for eligible repositories.

## Usage

Set a personal access token as `GITHUB_TOKEN` and run:

```sh
python3 scripts/github-trigger.py <organization> <topic>
```

### Arguments

- `<organization>` – GitHub organization name.
- `<topic>` – repository topic to search for.

### Example

```sh
export GITHUB_TOKEN=your_personal_access_token
python3 scripts/github-trigger.py my-org struct-enabled
```
