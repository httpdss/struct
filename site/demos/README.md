# Demo Images

This directory contains placeholder images for the STRUCT static site demos. In a production environment, these would be replaced with actual animated GIFs or videos showcasing the tool's capabilities.

## Image Specifications

- **Format**: GIF or MP4 for animations
- **Resolution**: 800x450px (16:9 aspect ratio)
- **Duration**: 10-30 seconds for GIFs
- **File Size**: Under 2MB per file for optimal loading

## Required Demo Images

1. `basic-usage.gif` - Shows basic project generation workflow
2. `yaml-config.gif` - Demonstrates YAML configuration creation
3. `mappings-demo.gif` - Shows external mappings usage
4. `remote-content.gif` - Demonstrates remote content fetching
5. `advanced-features.gif` - Shows hooks, validation, and dry-run

## Creating Demo Images

These images should be generated using [VHS](https://github.com/charmbracelet/vhs) tapes located in `/docs/vhs/` directory.

```bash
# Generate all demo GIFs
vhs docs/vhs/basic-usage.tape
vhs docs/vhs/yaml-config.tape
vhs docs/vhs/mappings-demo.tape
vhs docs/vhs/remote-content.tape
vhs docs/vhs/advanced-features.tape

# Move to demos directory
mv *.gif site/demos/
```

## Placeholder Content

Until real demos are generated, the site will gracefully handle missing images with loading states and fallback content.
