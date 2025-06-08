# Usage

STRUCT exposes a command called `struct` with a set of subcommands:

- `generate` – generate a project structure from a YAML file.
- `validate` – validate a configuration file.
- `info` – display information about the tool and its dependencies.
- `list` – list available structures shipped with the project.

For help on any command run:

```sh
struct -h
```

## Simple example

```sh
struct generate terraform-module ./my-terraform-module
```

## More complete example

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

The [configuration](configuration.md) file controls what files and folders are created.
