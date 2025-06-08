# YAML Configuration

STRUCT reads a YAML file that describes the files and directories to create. Below are the available keys and options.

## Configuration properties

- **skip** – skip creation of a file or folder.
- **skip_if_exists** – only create if the path does not already exist.
- **permissions** – set custom file permissions (e.g. `'0777'`).
- **content** – inline file content.
- **file** – path or URL of a file to include. Supported protocols include `file://`, `http://`, `https://`, `github://`, `githubhttps://`, `githubssh://`, `s3://` and `gs://`.

Example configuration:

```yaml
files:
  - README.md:
      skip: true
      content: |
        # {{@ project_name @}}
        This is a template repository.
  - script.sh:
      skip_if_exists: true
      permissions: '0777'
      content: |
        #!/bin/bash
        echo "Hello, {{@ author_name @}}!"
  - LICENSE:
      file: https://raw.githubusercontent.com/nishanths/license/master/LICENSE
  - remote_file.txt:
      file: file:///path/to/local/file.txt
  - github_file.py:
      file: github://owner/repo/branch/path/to/file.py
  - github_https_file.py:
      file: githubhttps://owner/repo/branch/path/to/file.py
  - github_ssh_file.py:
      file: githubssh://owner/repo/branch/path/to/file.py
  - s3_file.txt:
      file: s3://bucket_name/key
  - gcs_file.txt:
      file: gs://bucket_name/key
  - src/main.py:
      content: |
        print("Hello, World!")
folders:
  - .devops/modules/mod1:
      struct: terraform/module
  - .devops/modules/mod2:
      struct: terraform/module
      with:
        module_name: mymod2
  - ./:
      struct:
        - docker-files
        - project/go
variables:
  - project_name:
      description: "The name of the project"
      default: "MyProject"
      type: string
  - author_name:
      description: "The name of the author"
      type: string
      default: "John Doe"
```

## Template variables

Template variables are enclosed in `{{@` and `@}}` and are replaced at runtime. If a variable does not have a default value you will be prompted interactively.

### Default variables

- `file_name` – name of the file being processed.
- `file_directory` – directory of the file being processed.

### Custom Jinja2 filters

`struct` ships a few helper filters.

- **latest_release** – fetch the latest GitHub release.
- **slugify** – convert a string into a slug.
- **default_branch** – return the default branch of a GitHub repository.

```yaml
files:
  - README.md:
      content: |
        Latest release: {{@ "httpdss/struct" | latest_release @}}
```

If a filter fails, a placeholder value is inserted.

### `with` clause

Nested structures can receive extra variables using the `with` clause. These values are merged with the global variables.

```yaml
folders:
  - .devops/modules/mod2:
      struct: terraform/module
      with:
        module_name: mymod2
```
