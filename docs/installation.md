# Installation Guide

## Using pip

Install STRUCT with pip:

```sh
pip install git+https://github.com/httpdss/struct.git
```

## From Source

Clone the repository and install locally. See the [Development](development.md) page for details.

## Using Docker

Run STRUCT without installing, using Docker:

```sh
docker run -v $(pwd):/workdir -u $(id -u):$(id -g) ghcr.io/httpdss/struct:main generate /workdir/example/structure.yaml /workdir/example_output
```

Refer to the [Quick Start](quickstart.md) guide for more options.
