Output docs/vhs/yaml-config.gif

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

Type "# Create a custom YAML configuration" Enter
Type "cat > my-project.yaml << 'EOF'" Enter
Type "files:" Enter
Type "  - README.md:" Enter
Type "      content: |" Enter
Type "        # {{@ project_name @}}" Enter
Type "        Welcome to my awesome project!" Enter
Type "  - src/main.py:" Enter
Type "      content: |" Enter
Type "        print('Hello from {{@ project_name @}}!')" Enter
Type "" Enter
Type "variables:" Enter
Type "  - project_name:" Enter
Type "      description: 'Name of your project'" Enter
Type "      type: string" Enter
Type "      default: 'MyProject'" Enter
Type "EOF" Enter
Sleep 2
Type "" Enter
Type "# Generate structure from YAML (note: file:// is automatic)" Enter
Type "struct generate my-project.yaml ./output" Enter
Sleep 5
Type "" Enter
Type "# Check the generated files" Enter
Type "tree output && echo && cat output/README.md" Enter
Sleep 5
