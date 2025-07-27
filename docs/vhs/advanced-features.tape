Output docs/vhs/advanced-features.gif

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

Type "# Create a test structure" Enter
Type "mkdir -p existing-project && echo 'old content' > existing-project/README.md" Enter
Sleep 1
Type "" Enter
Type "# Use dry-run to preview changes" Enter
Type "struct generate --dry-run terraform/module ./existing-project" Enter
Sleep 5
Type "" Enter
Type "# Validate a YAML configuration" Enter
Type "cat > test-config.yaml << 'EOF'" Enter
Type "files:" Enter
Type "  - test.txt:" Enter
Type "      content: 'Hello World'" Enter
Type "EOF" Enter
Sleep 2
Type "struct validate test-config.yaml" Enter
Sleep 3
Type "" Enter
Type "# Generate with backup strategy" Enter
Type "struct generate --file-strategy=backup --backup=./backups terraform/module ./existing-project" Enter
Sleep 5
Type "" Enter
Type "# Check backup was created" Enter
Type "ls -la backups/ && echo && echo 'New content:' && head existing-project/README.md" Enter
Sleep 3
