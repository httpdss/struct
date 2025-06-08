# Installation

## Using pip

You can install STRUCT using pip:

```sh
pip install git+https://github.com/httpdss/struct.git
```

## From Source

Alternatively, clone the repository and install it locally:

```sh
git clone https://github.com/httpdss/struct.git
cd struct
pip install -r requirements.txt
```

## Using Docker

The Docker image lets you run the script without installing anything locally. See the [Quick Start](#quick-start) below for an example.

## Quick Start

### Generate a project from a local YAML file

```sh
docker run \
  -v $(pwd):/workdir \
  -u $(id -u):$(id -g) \
  ghcr.io/httpdss/struct:main generate \
  /workdir/example/structure.yaml \
  /workdir/example_output
```

### Quick Start Using Docker Alpine

For testing you can start a minimal Alpine container and install STRUCT inside it:

```sh
docker run -it --entrypoint="" python:3.10-alpine sh -l
```

Inside the container install the tool and run it:

```sh
apk add python-pip git vim
pip install git+https://github.com/httpdss/struct.git
mkdir example
cd example
cp /workdir/example/structure.yaml .
struct generate structure.yaml .
```
