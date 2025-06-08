# YAML Schema

A JSON schema is provided to help validate your configuration and provide autocompletion in supported editors.

## Configuring VSCode

1. Install the [YAML extension](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml).
2. Add the following to your `.vscode/settings.json`:

```json
{
  "yaml.schemas": {
    "https://raw.githubusercontent.com/httpdss/struct/main/extras/schema.json": ".struct.yaml"
  }
}
```

This associates the schema with all `.struct.yaml` files in the workspace.
