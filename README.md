[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/httpdss/struct/blob/master/README.md) [![es](https://img.shields.io/badge/lang-es-yellow.svg)](https://github.com/httpdss/struct/blob/master/README.es.md)

# 🚀 STRUCT: Automated Project Structure Generator

![Struct Banner](extras/banner.png)

> ⚠️ **Warning:** This project is still in development and may contain bugs. Use it at your own risk.

## 📄 Table of Contents

- [Introduction](#-introduction)
- [Features](#-features)
- [Installation](#-installation)
  - [Using pip](#using-pip)
  - [From Source](#from-source)
  - [Using Docker](#using-docker)
- [Quick Start](#-quick-start)
- [Usage](#-usage)
- [YAML Configuration](#-yaml-configuration)
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
- **Template Variables**: Use placeholders in your configuration and replace them with actual values at runtime.
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

Alternatively, you can clone the repository and install it locally. See the [Development](#development) section for more details.

### Using Docker

You can use the Docker image to run the script without installing it on your system. See the [Quick Start](#quick-start) section for more details.

## 🐳 Quick Start

### Using Docker

1. Create a YAML configuration file for your project structure. See sample configuration [here](./example/structure.yaml).
2. Run the following command to generate the project structure:

```sh
docker run \
  -v $(pwd):/workdir \
  -e OPENAI_API_KEY=your-key \
  -u $(id -u):$(id -g) \
  ghcr.io/httpdss/struct:main \
  /workdir/example/structure.yaml \
  /workdir/example_output
```

Replace `your-key` with your OpenAI API key and adjust the paths as needed. If you are not using prompts inside your structure, you can set the `OPENAI_API_KEY` to any value. There is a known issue with the script that requires the `OPENAI_API_KEY` to be set. See [Known Issues](#known-issues) for more details.

### Using Docker Alpine

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
export OPENAI_API_KEY=something
struct structure.yaml .
```

## 📝 Usage

Run the script with the following command:

```sh
usage: struct [-h] [--log LOG] [--dry-run] [--vars VARS] [--backup BACKUP] [--file-strategy {overwrite,skip,append,rename,backup}] [--log-file LOG_FILE] yaml_file base_path
```

### Options

- `-h` or `--help`: Show help and exit
- `--log`: Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Default is INFO.
- `--dry-run`: Perform a dry run without creating any files or directories.
- `--vars`: Template variables in the format `KEY1=value1,KEY2=value2`.
- `--backup`: Path to the backup folder.
- `--file-strategy`: Strategy for handling existing files (overwrite, skip, append, rename, backup). Default is overwrite.
- `--log-file`: Path to a log file.

### Simple Example

```sh
struct /path/to/your/structure.yaml /path/to/your/output/directory
```

### More Complete Example

```sh
struct \
  --log=DEBUG \
  --dry-run \
  --vars="project_name=MyProject,author_name=JohnDoe" \
  --backup=/path/to/backup \
  --file-strategy=rename \
  --log-file=/path/to/logfile.log \
  /path/to/your/structure.yaml \
  /path/to/your/output/directory
```

## 📄 YAML Configuration

Here is an example of a YAML configuration file:

```yaml
structure:
  - README.md:
      content: |
        # ${project_name}
        This is a template repository.
  - script.sh:
      permissions: '0777'
      content: |
        #!/bin/bash
        echo "Hello, ${author_name}!"
  - LICENSE:
      file: https://raw.githubusercontent.com/nishanths/license/master/LICENSE
  - src/main.py:
      content: |
        print("Hello, World!")
```

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

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 💰 Funding

If you find this project helpful, please consider supporting it through donations: [patreon/structproject](https://patreon.com/structproject)

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## 🙏 Acknowledgments

Special thanks to all the contributors who helped make this project possible.

## 🐞 Known Issues

- It is mandatory to set the `OPENAI_API_KEY` environment variable before running the script. If you are not using GPT properties, you can set it to any value. Issue [#3](https://github.com/httpdss/struct/issues/3)
