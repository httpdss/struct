# 🚀 STRUCT: Automated Project Structure Generator

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/httpdss/struct/blob/master/README.md) [![es](https://img.shields.io/badge/lang-es-yellow.svg)](https://github.com/httpdss/struct/blob/master/README.es.md)

![Struct Banner](extras/banner.png)

## 📄 Table of Contents

- [Introduction](#-introduction)
- [Features](#-features)
- [Installation](#️-installation)
- [Quick Start](#-quick-start)
- [Usage](#-usage)
- [YAML Configuration](#-yaml-configuration)
- [YAML Schema](#-yaml-schema)
- [GitHub Trigger Script](#-github-trigger-script)
- [Development](#-development)
- [License](#-license)
- [Funding](#-funding)
- [Contributing](#-contributing)
- [Acknowledgments](#-acknowledgments)
- [Known Issues](#-known-issues)

## 📦 Introduction

STRUCT is a powerful and flexible script designed to automate the creation of project structures based on YAML configurations. It supports template variables, custom file permissions, remote content fetching, and multiple file handling strategies to streamline your development setup process.

This is targeted towards developers, DevOps engineers, and anyone who wants to automate the creation of project structures. It can be used to generate boilerplate code, configuration files, documentation, and more.

## ✨ Features

- **YAML Configuration**: Define your project structure in a simple YAML file.
- **Template Variables**: Use placeholders in your configuration and replace them with actual values at runtime. Also supports custom Jinja2 filters and interactive mode to fill in the variables.
- **Custom File Permissions**: Set custom permissions for your files directly from the YAML configuration.
- **Remote Content Fetching**: Include content from remote files by specifying their URLs.
- **File Handling Strategies**: Choose from multiple strategies (overwrite, skip, append, rename, backup) to manage existing files.
- **Dry Run**: Preview the actions without making any changes to your file system.
- **Configuration Validation**: Ensure your YAML configuration is valid before executing the script.
- **Verbose Logging**: Get detailed logs of the script's actions for easy debugging and monitoring.

## 🛠️ Installation

### Using pip

You can install STRUCT using pip:

```sh
pip install git+https://github.com/httpdss/struct.git
```

### From Source

Alternatively, you can clone the repository and install it locally. See the [Development](#-development) section for more details.

### Using Docker

You can use the Docker image to run the script without installing it on your system. See the [Quick Start](#-quick-start) section for more details.

## 🐳 Quick Start

### Quick Start Using Docker

1. Create a YAML configuration file for your project structure. See sample configuration [here](./example/structure.yaml).
2. Run the following command to generate the project structure:

```sh
docker run \
  -v $(pwd):/workdir \
  -u $(id -u):$(id -g) \
  ghcr.io/httpdss/struct:main generate \
  /workdir/example/structure.yaml \
  /workdir/example_output
```

### Quick Start Using Docker Alpine

For testing, you can run an alpine Docker container and install the script inside it:

```sh
docker run -it --entrypoint="" python:3.10-alpine sh -l
```

Inside the container:

```sh
apk add python-pip git vim
pip install git+https://github.com/httpdss/struct.git
mkdir example
cd example/
touch structure.yaml
vim structure.yaml # copy the content from the example folder
struct generate structure.yaml .
```

## 📝 Usage

Run the script with the following command using one of the following subcommands:

- `generate`: Generate the project structure based on the YAML configuration.
- `generate-schema`: Generate JSON schema for available structure templates.
- `validate`: Validate the YAML configuration file.
- `info`: Display information about the script and its dependencies.
- `list`: List the available structs

For more information, run the script with the `-h` or `--help` option (this is also available for each subcommand):

![Struct List](./docs/vhs/usage.gif)

```sh
struct -h
```

### Simple Example

```sh
struct generate terraform-module ./my-terraform-module
```

### More Complete Example

```sh
struct generate \
  --log=DEBUG \
  --dry-run \
  --backup=/path/to/backup \
  --file-strategy=rename \
  --log-file=/path/to/logfile.log \
  terraform-module \
  ./my-terraform-module
```

### Generate Schema Command

The `generate-schema` command creates JSON schema definitions for available structure templates, making it easier for tools and IDEs to provide autocompletion and validation.

#### Basic Usage

```sh
# Generate schema to stdout
struct generate-schema

# Generate schema with custom structures path
struct generate-schema -s /path/to/custom/structures

# Save schema to file
struct generate-schema -o schema.json

# Combine custom path and output file
struct generate-schema -s /path/to/custom/structures -o schema.json
```

#### Command Options

- `-s, --structures-path`: Path to additional structure definitions (optional)
- `-o, --output`: Output file path for the schema (default: stdout)

The generated schema includes all available structures from both the built-in contribs directory and any custom structures path you specify. This is useful for:

- IDE autocompletion when writing `.struct.yaml` files
- Validation of structure references in your configurations
- Programmatic discovery of available templates

## 📝 YAML Configuration

### Configuration Properties

When defining your project structure in the YAML configuration file, you can use various properties to control the behavior of the script. Here are the available properties:

- **skip**: If set to `true`, the file or folder will be skipped and not created.
- **skip_if_exists**: If set to `true`, the file or folder will be skipped if it already exists.
- **permissions**: Set custom file permissions using a string representation of the octal value (e.g., `'0777'`).
- **content**: Define the content of the file directly in the YAML configuration.
- **file**: Specify a local or remote file to include. Supported protocols include `file://`, `http://`, `https://`, `github://`, `githubhttps://`, `githubssh://`, `s3://`, and `gs://`.

Example:

```yaml
files:
  - README.md:
      skip: true
      content: |
        # {{@ project_name @}}
        This is a template repository.
  - script.sh:
      skip_if_exists: true
      permissions: '0777'
      content: |
        #!/bin/bash
        echo "Hello, {{@ author_name @}}!"
  - LICENSE:
      file: https://raw.githubusercontent.com/nishanths/license/master/LICENSE
  - remote_file.txt:
      file: file:///path/to/local/file.txt
  - github_file.py:
      file: github://owner/repo/branch/path/to/file.py
  - github_https_file.py:
      file: githubhttps://owner/repo/branch/path/to/file.py
  - github_ssh_file.py:
      file: githubssh://owner/repo/branch/path/to/file.py
  - s3_file.txt:
      file: s3://bucket_name/key
  - gcs_file.txt:
      file: gs://bucket_name/key
  - src/main.py:
      content: |
        print("Hello, World!")
folders:
  - .devops/modules/mod1:
      struct: terraform/module
  - .devops/modules/mod2:
      struct: terraform/module
      with:
        module_name: mymod2
  - ./:
      struct:
        - docker-files
        - project/go
variables:
  - project_name:
      description: "The name of the project"
      default: "MyProject"
      type: string
  - author_name:
      description: "The name of the author"
      type: string
      default: "John Doe"
```

These properties allow you to customize the behavior and content of the files and folders generated by the script, providing flexibility and control over your project structure.

### Template variables

You can use template variables in your configuration file by enclosing them in `{{@` and `@}}`. For example, `{{@ project_name @}}` will be replaced with the value of the `project_name` variable at runtime. If this are not set when running the script, it will prompt you to enter the value interactively.

If you need to define blocks you can use starting block notation `{%@` and end block notation `%@}`.

To define comments you can use the comment start notation `{#@` and end comment notation `@#}`.

#### Default template variables

- `file_name`: The name of the file being processed.
- `file_directory`: The name of the directory of file that is being processed.

#### Interactive template variables

If you don't provide a default value for a variable, the script will prompt you to enter the value interactively.

The struct defined should define the variable on a specific section of the YAML file. For example:

```yaml
variables:
  - author_name:
      description: "The name of the author"
      type: string
      default: "John Doe"
```

as you can see, the `author_name` variable is defined on the `variables` section of the YAML file. it includes a `description`, `type` and `default` value which is used if the user doesn't provide a value interactively.

#### Custom Jinja2 filters

##### `latest_release`

This filter fetches the latest release version of a GitHub repository. It takes the repository name as an argument.

```yaml
files:
  - README.md:
      content: |
        # MyProject
        Latest release: {{@ "httpdss/struct" | latest_release @}}
```

This uses PyGithub to fetch the latest release of the repository so setting the `GITHUB_TOKEN` environment variable will give you access to private repositories.

If there is an error in the process, the filter will return `LATEST_RELEASE_ERROR`.

NOTE: you can use this filter to get the latest release for a terraform provider. For example, to get the latest release of the `aws` provider, you can use `{{@ "hashicorp/terraform-provider-aws" | latest_release @}}` or datadog provider `{{@ "DataDog/terraform-provider-datadog" | latest_release @}}`.

##### `slugify`

This filter converts a string into a slug. It takes an optional argument to specify the separator character (default is `-`).

```yaml
files:
  - README.md:
      content: |
        # {{@ project_name @}}
        This is a template repository.
        slugify project_name: {{@ project_name | slugify @}}
```

##### `default_branch`

This filter fetches the default branch name of a GitHub repository. It takes the repository name as an argument.

```yaml
files:
  - README.md:
      content: |
        # MyProject
        Default branch: {{@ "httpdss/struct" | default_branch @}}
```

### `with` Clause

The `with` clause allows you to pass additional variables to nested structures. These variables will be merged with the global variables and can be used within the nested structure.

Example:

```yaml
folders:
  - .devops/modules/mod1:
      struct: terraform/module
  - .devops/modules/mod2:
      struct: terraform/module
      with:
        module_name: mymod2
```

## 📝 YAML Schema

To ensure your YAML configuration files adhere to the expected structure, you can use the provided JSON schema. This helps in validating your YAML files and provides autocompletion in supported editors like VSCode.

### Configuring VSCode

1. Install the [YAML extension](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml) for VSCode.
2. Add the following configuration to your workspace settings (`.vscode/settings.json`):

```json
{
  "yaml.schemas": {
    "https://raw.githubusercontent.com/httpdss/struct/main/extras/schema.json": ".struct.yaml"
  }
}
```

This configuration will associate the JSON schema with all .struct.yaml files in your workspace, providing validation and autocompletion.

## 🔄 GitHub Trigger Script

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

## 👩‍💻 Development

To get started with development, follow these steps:

- Clone the repository
- Create a virtual environment

```sh
python3 -m venv .venv
source .venv/bin/activate
```

- Install the dependencies

```sh
pip install -r requirements.txt
pip install -r requirements.dev.txt
```

## 🛠️ Command-Line Auto-Completion

This project uses [argcomplete](https://kislyuk.github.io/argcomplete/) to provide command-line auto-completion for the `struct` script. Follow these steps to enable auto-completion:

1. **Install `argcomplete`**:

    ```sh
    pip install argcomplete
    ```

2. **Enable global completion** for your shell. This step is usually done once:

    ```sh
    activate-global-python-argcomplete
    ```

3. **Register the script for auto-completion**. Add the following line to your shell's configuration file (e.g., `.bashrc`, `.zshrc`):

    ```sh
    eval "$(register-python-argcomplete struct)"
    ```

4. **Reload your shell configuration**:

    ```sh
    source ~/.bashrc  # or source ~/.zshrc for Zsh users
    ```

After completing these steps, you should have auto-completion enabled for the `struct` script. You can test it by typing part of a command and pressing `Tab` to see the available options.

```sh
struct <Tab>
```

## Articles

- [**Defining User Prompts on STRUCT: Harnessing GPT-4.1 for Scalable Project Scaffolding**](https://medium.com/@httpdss/defining-user-prompts-on-struct-harnessing-gpt-4-1-for-scalable-project-scaffolding-e6d3b4ec4701)
- [**Unlocking Developer Productivity with STRUCT: The Ultimate Open-Source Tool for Automated Project Structures**](https://blog.devops.dev/unlocking-developer-productivity-with-struct-the-ultimate-open-source-tool-for-automated-project-8bca9b5f40f9)
- [**Automating Project Structures with STRUCT and GitHub Actions**](https://medium.com/@httpdss/automating-project-structures-with-struct-and-github-actions-64e09c40c11e)
- [**Advanced STRUCT Tips: Working with Template Variables and Jinja2 Filters**](https://medium.com/@httpdss/advanced-struct-tips-working-with-template-variables-and-jinja2-filters-b239bf3145e4)

## 🪝 Pre-generation and Post-generation Hooks

You can define shell commands to run before and after structure generation using the `pre_hooks` and `post_hooks` keys in your YAML configuration. These are optional and allow you to automate setup or cleanup steps.

- **pre_hooks**: List of shell commands to run before generation. If any command fails (non-zero exit), generation is aborted.
- **post_hooks**: List of shell commands to run after generation completes. If any command fails, an error is shown.

Example:

```yaml
pre_hooks:
  - echo "Preparing environment..."
  - ./scripts/prep.sh

post_hooks:
  - echo "Generation complete!"
  - ./scripts/cleanup.sh
files:
  - README.md:
      content: |
        # My Project
```

**Notes:**

- Output from hooks (stdout and stderr) is shown in the terminal.
- If a pre-hook fails, generation is halted.
- If no hooks are defined, nothing extra happens.

## 🗺️ Mappings Support

You can provide a mappings YAML file to inject key-value maps into your templates. This is useful for referencing environment-specific values, IDs, or any other mapping you want to use in your generated files.

### Example mappings file

```yaml
mappings:
  teams:
    devops: devops-team
  aws_account_ids:
    myenv-non-prod: 123456789
    myenv-prod: 987654321
```

### Usage in templates

You can reference mapping values in your templates using the `mappings` variable:

```jinja
{{@ mappings.aws_account_ids['myenv-prod'] @}}
```

This will render as:

```text
987654321
```

### Using mappings in the `with` clause

You can also assign a value from a mapping directly in the `with` clause for folder struct calls. For example:

```yaml
folders:
  - ./:
      struct:
        - configs/codeowners
    with:
      team: {{@ mappings.teams.devops @}}
      account_id: {{@ mappings.aws_account_ids['myenv-prod'] @}}
```

This will assign the value `devops-team` to the variable `team` and `987654321` to `account_id` in the struct, using the values from your mappings file.

### Passing the mappings file

Use the `--mappings-file` argument with the `generate` command:

```sh
struct generate --mappings-file ./mymap.yaml my-struct.yaml .
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 💰 Funding

If you find this project helpful, please consider supporting it through donations: [patreon/structproject](https://patreon.com/structproject)

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## 🙏 Acknowledgments

Special thanks to all the contributors who helped make this project possible.

## 🐞 Known Issues

- [ ] TBD
