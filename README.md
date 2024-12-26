# 🚀 STRUCT: Automated Project Structure Generator

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/httpdss/struct/blob/master/README.md) [![es](https://img.shields.io/badge/lang-es-yellow.svg)](https://github.com/httpdss/struct/blob/master/README.es.md)

![Struct Banner](extras/banner.png)

> [!WARNING]
> This project is still in development and may contain bugs. Use it at your own risk.

## 📄 Table of Contents

- [Introduction](#-introduction)
- [Features](#-features)
- [Installation](#installation)
  - [Using pip](#using-pip)
  - [From Source](#from-source)
  - [Using Docker](#using-docker)
- [Quick Start](#-quick-start)
- [Usage](#-usage)
- [YAML Configuration](#-yaml-configuration)
- [YAML Schema](#-yaml-schema)
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
- `validate`: Validate the YAML configuration file.
- `info`: Display information about the script and its dependencies.
- `list`: List the available structs

For more information, run the script with the `-h` or `--help` option (this is also available for each subcommand):

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

## 📝 YAML Configuration

Here is an example of a YAML configuration file:

```yaml
structure:
  - README.md:
      content: |
        # {{@ project_name @}}
        This is a template repository.
  - script.sh:
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
structure:
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
structure:
  - README.md:
      content: |
        # {{@ project_name @}}
        This is a template repository.
        slugify project_name: {{@ project_name | slugify @}}
```

##### `default_branch`

This filter fetches the default branch name of a GitHub repository. It takes the repository name as an argument.

```yaml
structure:
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
