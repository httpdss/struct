Output docs/vhs/multiple-mappings.gif

Set Theme "Monokai Vivid"
Set FontSize 14
Set TypingSpeed 40ms
Set WindowBar Colorful
Set BorderRadius 8
Set Margin 0
Set Padding 10
Set Width 1400
Set Height 800
Set Shell "bash"

Type "# Create base mappings file" Enter
Type "cat > base-mappings.yaml << 'EOF'" Enter
Type "mappings:" Enter
Type "  common:" Enter
Type "    app_name: 'MyApp'" Enter
Type "    version: '1.0.0'" Enter
Type "  environments:" Enter
Type "    dev:" Enter
Type "      replicas: 1" Enter
Type "EOF" Enter
Sleep 2
Type "" Enter
Type "# Create environment-specific overrides" Enter
Type "cat > prod-mappings.yaml << 'EOF'" Enter
Type "mappings:" Enter
Type "  environments:" Enter
Type "    dev:" Enter
Type "      debug: true" Enter
Type "    prod:" Enter
Type "      replicas: 3" Enter
Type "      debug: false" Enter
Type "EOF" Enter
Sleep 2
Type "" Enter
Type "# Create deployment template" Enter
Type "cat > deployment.yaml << 'EOF'" Enter
Type "files:" Enter
Type "  - k8s/deployment.yaml:" Enter
Type "      content: |" Enter
Type "        apiVersion: apps/v1" Enter
Type "        kind: Deployment" Enter
Type "        metadata:" Enter
Type "          name: {{@ mappings.common.app_name @}}" Enter
Type "        spec:" Enter
Type "          replicas: {{@ mappings.environments[env].replicas @}}" Enter
Type "variables:" Enter
Type "  - env:" Enter
Type "      description: 'Target environment'" Enter
Type "      default: 'dev'" Enter
Type "EOF" Enter
Sleep 3
Type "" Enter
Type "# Generate with multiple mappings files (deep merge)" Enter
Type "struct generate \\" Enter
Type "  --mappings-file base-mappings.yaml \\" Enter
Type "  --mappings-file prod-mappings.yaml \\" Enter
Type "  deployment.yaml ./k8s-output" Enter
Sleep 5
Type "" Enter
Type "# Check the merged result" Enter
Type "cat k8s-output/k8s/deployment.yaml" Enter
Sleep 3
