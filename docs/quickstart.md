# Quick Start

## Quick Start Using Docker

1. Create a YAML configuration file for your project structure. [See sample configuration here](../example/structure.yaml).
2. Run the following command to generate the project structure:

```sh
docker run \
  -v $(pwd):/workdir \
  -u $(id -u):$(id -g) \
  ghcr.io/httpdss/struct:main generate \
  file:///workdir/example/structure.yaml \
  /workdir/example_output
```

## Quick Start Using Docker Alpine

```sh
docker run \
  -v $(pwd):/workdir \
  -u $(id -u):$(id -g) \
  ghcr.io/httpdss/struct:alpine generate \
  file:///workdir/example/structure.yaml \
  /workdir/example_output
```

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

> **Note**: The `file://` protocol is automatically added for `.yaml` files, so `structure.yaml` and `file://structure.yaml` work identically.

## First Example

After installing STRUCT, try this simple example:

```sh
struct generate terraform-module ./my-terraform-module
```

This will create a new terraform module structure in the `./my-terraform-module` directory.

## Next Steps

- Learn about [YAML Configuration](configuration.md)
- Explore [Template Variables](template-variables.md)
- Check out [Usage Examples](usage.md)
