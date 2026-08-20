# Template Variables

Template variables allow you to create dynamic content in your StructKit configurations. This page covers all aspects of working with variables.

## Custom Delimiters (StructKit)

StructKit uses custom Jinja2 delimiters to avoid conflicts with YAML and other content:

- Variables: `{{@` and `@}}`
- Blocks: `{%@` and `@%}`
- Comments: `{#@` and `@#}`

Examples are shown below and throughout this page.

## Basic Syntax

Use template variables by enclosing them in `{{@` and `@}}`:

```yaml
files:
  - README.md:
      content: |
        # {{@ project_name @}}
        Welcome to {{@ project_name @}}!
```

## Block Syntax

For control structures, use block notation:

- Start block: `{%@`
- End block: `@%}`

```yaml
files:
  - config.yaml:
      content: |
        {%@ if environment == "production" @%}
        debug: false
        {%@ else @%}
        debug: true
        {%@ endif @%}
```

## Comments

Use comment notation to document your templates:

- Start comment: `{#@`
- End comment: `@#}`

```yaml
files:
  - app.py:
      content: |
        {#@ This is a template comment @#}
        app_name = "{{@ project_name @}}"
```

## Default Variables

StructKit provides these built-in variables:

- `file_name`: The name of the file being processed
- `file_directory`: The directory containing the file being processed

## Interactive Variables

Define variables that prompt users for input. When running in interactive mode, StructKit will display the variable's description to help users understand what value is expected:

```yaml
variables:
  - project_name:
      description: "The name of your project"
      type: string
      default: "MyProject"
  - author_name:
      description: "Your name"
      type: string
      # No default = interactive prompt
  - port:
      description: "Application port"
      type: integer
      default: 8080
```

When prompted interactively, variables with descriptions will display with contextual icons, **bold variable names**, and clean formatting:

```
🚀 project_name: The name of your project
   Enter value [MyProject]:

🌍 environment: Target deployment environment
   Options: (1) dev, (2) staging, (3) prod
   Enter value [dev]:
```

For variables without descriptions, a more compact format is used:

```
🔧 author_name []:
⚡ enable_logging [true]:
```

**Note**: Variable names appear in **bold** in actual terminal output for better readability.

**Contextual Icons**: StructKit automatically selects appropriate icons based on variable names and types:
- 🚀 Project/app names
- 🌍 Environment/deployment variables
- 🔌 Ports/network settings
- 🗄️ Database configurations
- ⚡ Boolean/toggle options
- 🔐 Authentication/secrets
- 🏷️ Versions/tags
- 📁 Paths/directories
- 🔧 General variables

**Note**: The `description` field is displayed in interactive mode only. You can also use the legacy `help` field which works the same way.

### Variable Types

- `string`: Text values
- `integer`: Numeric values
- `number`: Floating-point values
- `boolean`: True/false values

### Validation and Defaults

Interactive enum selection: when a variable defines `enum` and you are in interactive mode, StructKit will display numbered choices and accept either the number or the exact value. Press Enter to accept the default (if any).

Example prompt:

```
❓ Enter value for ENV [dev] (1) dev, (2) prod:
# Typing `2` selects `prod`, typing `prod` also works.
```

You can now enforce types and validations in your variables schema:

- `required: true` to require a value (non-interactive runs will error if missing)
- `enum: [...]` to restrict values to a set
- `regex`/`pattern` to validate string format
- `min`/`max` to bound numeric values
- `env` or `default_from_env` to set defaults from environment variables

Example:

```yaml
variables:
  - IS_ENABLED:
      type: boolean
      required: true
  - RETRY:
      type: integer
      min: 1
      max: 5
  - ENV:
      type: string
      enum: [dev, prod]
  - TOKEN:
      type: string
      env: MY_TOKEN
```

## Custom Jinja2 Filters and Globals

StructKit includes custom filters for common tasks:

### `uuid()` (global)

Generate a random UUID v4 string.

```yaml
files:
  - id.txt:
      content: |
        id: {{@ uuid() @}}
```

### `now()` (global)

Return the current UTC time in ISO 8601 format.

```yaml
files:
  - stamp.txt:
      content: |
        generated_at: {{@ now() @}}
```

!!! warning "`uuid()` and `now()` are non-deterministic"
    A file containing either produces different content on every run, so it always
    appears in `structkit generate --dry-run --diff` output. That removes the diff's
    value as a drift check. Confine them to files marked `skip_if_exists: true`, or
    avoid them in anything you regenerate.

### `env(name, default="")` (global)

Read an environment variable with an optional default.

```yaml
files:
  - .env.example:
      content: |
        TOKEN={{@ env("TOKEN", "changeme") @}}
```

### `read_file(path)` (global)

Read the contents of a file on disk. Returns empty string on error.

```yaml
files:
  - README.md:
      content: |
        {{@ read_file("INTRO.md") @}}
```

### `current_repo()` (global)

Return `owner/repo` for the Git repository in the current working directory, read from
`remote.origin.url`. Both HTTPS and SSH remotes are supported; a non-GitHub remote
returns an error string.

```yaml
files:
  - README.md:
      content: |
        [![CI](https://github.com/{{@ current_repo() @}}/actions/workflows/ci.yml/badge.svg)](https://github.com/{{@ current_repo() @}}/actions)
```

### `to_yaml` / `from_yaml` (filters)

Serialize and parse YAML.

```yaml
files:
  - data.yml:
      content: |
        {{@ some_dict | to_yaml @}}
```

```yaml
# Assume str_var holds YAML string
{%@ set obj = str_var | from_yaml @%}
```

### `to_json` / `from_json` (filters)

Serialize and parse JSON. to_json accepts an optional indent argument.

```yaml
files:
  - data.json:
      content: |
        {{@ some_dict | to_json(indent=2) @}}
```

```yaml
# Assume str_var holds JSON string
{%@ set obj = str_var | from_json @%}
```

### `latest_release`

Select the latest GitHub release with the following filter signature:

```python
latest_release(repo_name: str, strip_v: bool = False, return_sha: bool = False) -> str
```

- `strip_v` removes exactly one leading lowercase `v` from a release tag. It defaults to `false`; uppercase `V` and tags without `v` are unchanged.
- `return_sha` returns the commit SHA identified by the release tag instead of its name. It defaults to `false`.
- When both are `true`, `return_sha` takes precedence and `strip_v` has no effect.

For a release tagged `v22.0.0`:

```yaml
files:
  - release-info.txt:
      content: |
        Version: {{@ "nodejs/node" | latest_release @}}                       # v22.0.0
        Version without v: {{@ "nodejs/node" | latest_release(strip_v=true) @}} # 22.0.0
        Commit: {{@ "nodejs/node" | latest_release(return_sha=true) @}}        # full commit SHA
```

Calls that omit the new options remain unchanged. If repository lookup succeeds but latest-release lookup fails, version mode returns the default branch name and SHA mode returns that branch's head commit SHA; `strip_v` does not alter a fallback branch name. Repository lookup, fallback-resolution, or selected-release SHA-resolution failures return `LATEST_RELEASE_ERROR`.

SHA mode supports lightweight and annotated tags. Resolution examines at most 10 Git objects, so no more than nine annotated-tag hops may precede the final commit. A tag must ultimately resolve to a commit with a full 40-character SHA-1 or 64-character SHA-256 hexadecimal object ID. A malformed, cyclic, over-nested, missing, or non-commit tag target returns `LATEST_RELEASE_ERROR`; it does not fall back to a different revision after a release has already been selected.

**Requirements**: Set the `GITHUB_TOKEN` environment variable for private repositories and authenticated API rate limits.

### `slugify`

Convert strings to URL-friendly slugs:

```yaml
files:
  - "{{@ project_name | slugify @}}.conf":
      content: |
        server_name {{@ project_name | slugify @}};
```

**Options**: None. The value is lowercased, runs of whitespace become a single hyphen, and any character that is not `a-z`, `0-9`, or `-` is removed.

Note that underscores are removed rather than converted, so `My_Project` becomes `myproject`. To produce a different separator, chain Jinja2's built-in `replace` filter:

```yaml
files:
  - src/{{@ project_name | slugify | replace("-", "_") @}}/__init__.py:
      content: ""
```

### `default_branch`

Get the default branch name of a GitHub repository:

```yaml
files:
  - .github/workflows/ci.yml:
      content: |
        on:
          push:
            branches: [ {{@ "httpdss/structkit" | default_branch @}} ]
```

## The `with` Clause

Pass additional variables to nested structures:

```yaml
folders:
  - frontend/:
      struct: project/react
      with:
        app_name: "{{@ project_name @}}-frontend"
        port: 3000
  - backend/:
      struct: project/node
      with:
        app_name: "{{@ project_name @}}-backend"
        port: 8000
```

Variables defined in `with` are merged with global variables and take precedence.

## Advanced Examples

### Conditional File Creation

```yaml
files:
  - docker-compose.yml:
      skip: "{{@ not use_docker @}}"
      content: |
        version: '3.8'
        services:
          app:
            image: {{@ project_name | slugify @}}:latest
```

### Dynamic File Names

```yaml
files:
  - "src/{{@ module_name @}}/index.js":
      content: |
        // {{@ module_name @}} module
        export default {};
```

### Environment-Specific Content

```yaml
files:
  - config/{{@ environment @}}.yml:
      content: |
        {%@ if environment == "production" @%}
        database_url: {{@ production_db_url @}}
        {%@ else @%}
        database_url: sqlite:///dev.db
        {%@ endif @%}
```
