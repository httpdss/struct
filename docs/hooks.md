# Pre-Generation and Post-Generation Hooks

You can run shell commands before and after structure generation using `pre_hooks` and `post_hooks` in your configuration.

- **pre_hooks** – commands executed before generation. If any command returns a non-zero exit code the process stops.
- **post_hooks** – commands executed after generation completes. If any command fails an error is shown.

Example:

```yaml
pre_hooks:
  - echo "Preparing environment..."
  - ./scripts/prep.sh

post_hooks:
  - echo "Generation complete!"
  - ./scripts/cleanup.sh
files:
  - README.md:
      content: |
        # My Project
```

Output from hooks is shown in the terminal.
