# Installation Guide

## Using pip

Install STRUCT with pip:

```sh
pip install git+https://github.com/httpdss/struct.git
```

!!! tip "Enable Auto-Completion"
    After installation, enable command-line auto-completion for better productivity:
    ```sh
    eval "$(register-python-argcomplete struct)"
    ```
    For permanent setup, see the [Command-Line Completion](completion.md) guide.

## From Source

Clone the repository and install locally. See the [Development](development.md) page for details.

## Using Docker

Run STRUCT without installing, using Docker:

```sh
docker run -v $(pwd):/workdir -u $(id -u):$(id -g) ghcr.io/httpdss/struct:main generate file:///workdir/example/structure.yaml /workdir/example_output
```

Refer to the [Quick Start](quickstart.md) guide for more options.
