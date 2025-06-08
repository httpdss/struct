# 🚀 STRUCT: Automated Project Structure Generator

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/httpdss/struct/blob/master/README.md)
[![es](https://img.shields.io/badge/lang-es-yellow.svg)](https://github.com/httpdss/struct/blob/master/README.es.md)

![Struct Banner](extras/banner.png)

STRUCT automates the creation of project structures from YAML templates. It helps developers and DevOps teams scaffold projects quickly and reproducibly.

## Features 🎯

- Define project layouts using YAML
- Template variables with interactive prompts
- Custom file permissions
- Remote file inclusion (HTTP/GitHub/S3/GCS)
- Multiple strategies for existing files
- Dry-run mode and configuration validation
- Verbose logging

## Quick Start ⚡

Install using pip:

```sh
pip install git+https://github.com/httpdss/struct.git
```

Or run the Docker image:

```sh
docker run \
  -v $(pwd):/workdir \
  -u $(id -u):$(id -g) \
  ghcr.io/httpdss/struct:main generate \
  /workdir/example/structure.yaml \
  /workdir/example_output
```

## Documentation 📚

See the detailed docs in [`docs/en`](docs/en) or the Spanish version in [`docs/es`](docs/es).

- [Installation](docs/en/installation.md)
- [Usage](docs/en/usage.md)
- [YAML configuration reference](docs/en/configuration.md)
- [YAML schema](docs/en/yaml_schema.md)
- [GitHub trigger script](docs/en/github_trigger_script.md)
- [Development](docs/en/development.md)
- [Command-line completion](docs/en/completion.md)
- [Hooks](docs/en/hooks.md)
- [Articles](docs/en/articles.md)
- [Available structures](docs/en/structures.md)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Funding

If you find this project helpful, please consider supporting it through donations: [patreon/structproject](https://patreon.com/structproject)

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Acknowledgments

Special thanks to all the contributors who helped make this project possible.

## Known Issues

- [ ] TBD
