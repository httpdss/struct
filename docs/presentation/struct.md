<!-- >

# Struct

![](struct-banner.png)

Automated Project Structure Generator

<!-- end_slide -->

# What is Struct?

Struct automates project structure creation from YAML configurations.

- YAML-based configurations for reproducible scaffolding
- Jinja2 templating and interactive prompts for dynamic content
- Remote content sources (GitHub, HTTP/HTTPS, S3, GCS)
- Smart file handling (overwrite, skip, append, rename, backup)
- Hooks (pre/post) to automate tasks around generation
- Dry-run and diff preview before applying changes
- Validation and JSON schema generation
- MCP (Model Context Protocol) integration

<!-- end_slide -->

# Install

Option 1 — pip (from GitHub):

```sh
pip install git+https://github.com/httpdss/struct.git
```

Option 2 — Docker:

```sh
docker run -v $(pwd):/workdir ghcr.io/httpdss/struct:main generate my-config.yaml ./output
```

Option 3 — From source with venv:

```sh
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install .
```

<!-- end_slide -->

# Basic Commands

- struct list — List available structures
- struct generate — Generate a project from a structure or YAML file
- struct validate — Validate a YAML configuration
- struct generate-schema — Emit JSON schema for available structures
- struct init — Create a minimal .struct.yaml in a directory
- struct info — Show details about a structure definition
- struct completion install — Install shell completions
- struct mcp --server — Start MCP server

```sh
struct --help
```

<!-- end_slide -->

# List Structures

See all available structures:

```sh
struct list
```

Include custom structure directories:

```sh
struct list -s ~/custom-structures
```

Tip (with shell completion enabled):

```sh
struct generate <Tab>   # shows available structures
```

<!-- end_slide -->

# Generate: Quick Start

Use defaults (.struct.yaml in current dir, generate into current dir):

```sh
struct generate
```

Generate a Terraform module (example):

```sh
struct generate terraform/modules/generic ./my-terraform-module
```

Generate from a YAML file:

```sh
struct generate my-config.yaml ./output
# or
struct generate file://my-config.yaml ./output
```

<!-- end_slide -->

# Generate: Variables & Paths

Pass template variables:

```sh
struct generate -v "project_name=MyApp,author=John Doe" file://structure.yaml ./output
```

Use additional custom structures path:

```sh
struct generate -s ~/custom-structures python-api ./my-api
```

<!-- end_slide -->

# Generate: Dry Run & Diff

Preview without creating files and show diffs:

```sh
struct generate --dry-run --diff file://structure.yaml ./output
```

Other helpful options:
- --log=DEBUG
- --mappings-file path.yaml (can be repeated)
- --output {console,file}

<!-- end_slide -->

# Handling Existing Files

Skip existing files:

```sh
struct generate -f skip file://structure.yaml ./output
```

Backup before overwriting:

```sh
struct generate -f backup -b ./backup file://structure.yaml ./output
```

Other strategies: overwrite, append, rename

<!-- end_slide -->

# Multiple Use Cases

- Infrastructure as Code: Terraform modules, Kubernetes manifests
- Application Scaffolding: microservices, APIs, frontends
- DevOps Automation: CI/CD pipelines, configuration management
- Documentation: consistent project docs and compliance templates

<!-- end_slide -->

# Extras

Initialize a starter configuration:

```sh
struct init
```

Validate a configuration:

```sh
struct validate my-structure.yaml
```

Generate JSON schema:

```sh
struct generate-schema -o schema.json
```

Shell completion (auto-detect shell):

```sh
struct completion install
```

MCP integration:

```sh
struct mcp --server
```

<!-- end_slide -->

# End
