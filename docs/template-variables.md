# Template Variables

Template variables allow you to create dynamic content in your STRUCT configurations. This page covers all aspects of working with variables.

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
- End block: `%@}`

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

STRUCT provides these built-in variables:

- `file_name`: The name of the file being processed
- `file_directory`: The directory containing the file being processed

## Interactive Variables

Define variables that prompt users for input:

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

### Variable Types

- `string`: Text values
- `integer`: Numeric values
- `number`: Floating-point values
- `boolean`: True/false values

### Validation and Defaults

Interactive enum selection: when a variable defines `enum` and you are in interactive mode, STRUCT will display numbered choices and accept either the number or the exact value. Press Enter to accept the default (if any).

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

## Custom Jinja2 Filters

STRUCT includes custom filters for common tasks:

### `latest_release`

Fetch the latest release version from GitHub:

```yaml
files:
  - Dockerfile:
      content: |
        FROM node:{{@ "nodejs/node" | latest_release @}}
```

**Requirements**: Set `GITHUB_TOKEN` environment variable for private repos.

### `slugify`

Convert strings to URL-friendly slugs:

```yaml
files:
  - "{{@ project_name | slugify @}}.conf":
      content: |
        server_name {{@ project_name | slugify @}};
```

**Options**: Optional separator character (default: `-`)

### `default_branch`

Get the default branch name of a GitHub repository:

```yaml
files:
  - .github/workflows/ci.yml:
      content: |
        on:
          push:
            branches: [ {{@ "httpdss/struct" | default_branch @}} ]
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
